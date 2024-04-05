import random
import numpy as np
import torch
import shutil
import os
import pickle
import torch
from typing import List, Union
from .custom_ops import custom_scaled_dot_product_attention
from PIL import Image
import requests
from optimum.onnxruntime import ORTModel
import json
import logging
from easydict import EasyDict
from transformers import AutoConfig
import torch.nn.functional as F  ## hm
from copy import deepcopy
import torch.nn as nn


logger = logging.getLogger(__name__)


def sample_stratified(df, n_samples_per_label, problem_type):
    """
    Returns a stratified sample of rows from the dataframe, ensuring that each 'label' value is
    equally represented according to n_samples_per_label.

    Parameters:
    - df: DataFrame to sample from.
    - n_samples_per_label: Number of samples to draw for each label.

    Returns:
    - Stratified sample of the dataframe.
    """
    # Group by 'label' and sample n_samples_per_label from each group
    df_copy = df.copy()
    if problem_type == "multi_label_classification":
        # select random label in label_list
        df_copy["label"] = df_copy["label"].apply(lambda x: random.choice(x))
    sampled_df = df_copy.groupby("label", group_keys=False).apply(
        lambda x: x.sample(min(len(x), n_samples_per_label))
    )

    return sampled_df


def set_seed(seed: int):
    """
    Helper function for reproducible behavior to set the seed in `random`, `numpy`, `torch` and/or `tf` (if installed).

    Args:
        seed (`int`): The seed to set.
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def model_save(model_type: str, save_dir: str, ckpt_path: str, device: str = "gpu"):
    """
    Save model backbone with huggingface format if possible, and classifier to onnx.
    Exporting backbone to onnx has to be done outside the trainer class, due to the large memory usage.
    Refer to the export_onnx function in trainer_util.py

    Args:
        model_type (str): model type, e.g. 'TextClassifier', 'ImageClassifier', 'ImageTextClassifier'
        save_dir (str): Directory to save the model
        ckpt_path (str): trained model checkpoint path
        device (str): device name, e.g. 'cpu', 'gpu'
    """
    if model_type == "TextClassifier":
        from .text_classifier import TextClassifierModule

        classifier_module = TextClassifierModule
    elif model_type == "ImageClassifier":
        from .image_classifier import ImageClassifierModule

        classifier_module = ImageClassifierModule
    elif model_type == "ImageTextClassifier":
        from .image_text_classifier import ImageTextClassifierModule

        classifier_module = ImageTextClassifierModule
    else:
        raise ValueError(f"Not supported model type: {model_type}")

    if device == "gpu":
        device = torch.device("cuda")
    elif device == "cpu":
        device = torch.device("cpu")
    else:
        raise ValueError(
            f"Not supported device type: {device}, choose in ['cpu', 'gpu']."
        )

    if model_type == "ImageTextClassifier":
        os.makedirs(os.path.join(save_dir, "image"), exist_ok=True)
        os.makedirs(os.path.join(save_dir, "text"), exist_ok=True)
    else:
        os.makedirs(save_dir, exist_ok=True)

    # Load pretrained model
    logger.info(f"Loading the checkpoint from {ckpt_path}")
    print(f"Loading the checkpoint from {ckpt_path}")
    train_module = classifier_module.load_from_checkpoint(
        ckpt_path, map_location=device
    )
    train_module.eval()

    # Contiguous for save_pretrained
    for param in train_module.parameters():
        param.data = param.data.contiguous()

    # For torch pipeline
    shutil.copy(ckpt_path, os.path.join(save_dir, "model.ckpt"))

    if model_type == "ImageTextClassifier":
        ### Image backbone to onnx
        image_backbone_save_module = train_module.image_backbone
        # Only for huggingface transformers
        if not train_module.train_config.image_timm:
            # TransformerWrapper
            image_backbone_save_module = image_backbone_save_module.model
            # When model is trained with LORA, we have to merge the lora weight with backbone.
            if train_module.train_config.image_lora:
                image_backbone_save_module = (
                    image_backbone_save_module.merge_and_unload()
                )
            image_backbone_save_module.save_pretrained(os.path.join(save_dir, "image"))
        ### Text backbone to onnx
        text_backbone_save_module = train_module.text_backbone
        # When model is trained with LORA, we have to merge the lora weight with backbone.
        if train_module.train_config.text_lora:
            text_backbone_save_module = text_backbone_save_module.merge_and_unload()
        # ONly for huggingface transformers
        assert (
            train_module.train_config.text_timm == False
        ), "Not supported timm model for text backbone."
        text_backbone_save_module.save_pretrained(os.path.join(save_dir, "text"))
        # Save Tokenizer
        train_module.tokenizer.save_pretrained(os.path.join(save_dir, "text"))
        train_module.text_initial_config.save_pretrained(os.path.join(save_dir, "text"))

        # with open(os.path.join(save_dir, "image", "config.json"), "w") as f:
        #     json.dump(train_module.image_initial_config, f)

        if train_module.image_initial_config is not None:
            train_module.image_initial_config.save_pretrained(save_dir)

        # Save validation transform with pickle
        with open(os.path.join(save_dir, "image", "val_transforms.pkl"), "wb") as f:
            pickle.dump(train_module.val_transforms, f)

    else:
        ### Backbone to onnx
        backbone_save_module = train_module.backbone
        # Only for huggingface transformers
        if not train_module.train_config.timm:
            # TransformerWrapper
            if model_type == "ImageClassifier":
                backbone_save_module = backbone_save_module.model
            # When model is trained with LORA, we have to merge the lora weight with backbone.
            if train_module.train_config.lora:
                backbone_save_module = backbone_save_module.merge_and_unload()
            backbone_save_module.save_pretrained(save_dir)

        if model_type == "TextClassifier":
            # Save Tokenizer
            train_module.tokenizer.save_pretrained(save_dir)
            train_module.initial_config.save_pretrained(save_dir)
        # ImageClassifier
        else:
            ### timm flag False
            if train_module.initial_config is not None:
                train_module.initial_config.save_pretrained(save_dir)
            # with open(os.path.join(save_dir, "config.json"), "w") as f:
            #     json.dump(train_module.initial_config, f)
            # Save validation transform with pickle
            with open(os.path.join(save_dir, "val_transforms.pkl"), "wb") as f:
                pickle.dump(train_module.val_transforms, f)

    # Save train config
    with open(os.path.join(save_dir, "train_config.json"), "w", encoding="utf-8") as f:
        json.dump(train_module.train_config.to_dict(), f, ensure_ascii=False, indent=4)

    ### Classifier save to onnx
    classifier_head_save_module = train_module.classifier_head
    dummy_input = torch.randn([1, train_module.embedding_size], device=device)
    torch.onnx.export(
        classifier_head_save_module,
        dummy_input,
        os.path.join(save_dir, "classifier_head.onnx"),
        input_names=["embeddings"],
        output_names=["logits"],
        dynamic_axes={"embeddings": {0: "batch_size"}, "logits": {0: "batch_size"}},
    )

    ## Classifier save to ckpt

    torch.save(
        classifier_head_save_module, os.path.join(save_dir, "classifier_head.ckpt")
    )


def export_onnx(model_type: str, save_dir: str, device: str = "gpu"):
    """
    Export Huggingface backbone model to onnx format.
    Args:
        model_type (`str`): Model type string, e.g. "TextClassifier", "ImageClassifier", "ImageTextClassifier"
        save_dir (`str`): Saved model directory, containing pytorch_model.bin or model.ckpt
        device (`str`): Device type for exporting onnx, no related with pipeline device  "cpu" or "gpu"
    """
    if device == "gpu":
        device = torch.device("cuda")
    elif device == "cpu":
        device = torch.device("cpu")
    else:
        raise ValueError(
            f"Not supported device type: {device}, choose in ['cpu', 'gpu']."
        )

    with open(os.path.join(save_dir, "train_config.json"), "r", encoding="utf-8") as f:
        train_config = EasyDict(json.load(f))

    if model_type == "TextClassifier":
        assert train_config.timm == False, "timm is not supported for TextClassifier"
        logger.info("Exporting torch pt model to onnx...")
        model = ORTModel.from_pretrained(save_dir, export=True)
        # Saved with model.onnx
        logger.info("Saving onnx file...")
        model.save_pretrained(save_dir)
    elif model_type == "ImageClassifier":
        from .image_classifier import ImageClassifierModule

        if train_config.timm:
            train_module = ImageClassifierModule.load_from_checkpoint(
                os.path.join(save_dir, "model.ckpt"), map_location=device
            )

            backbone_save_module = train_module.backbone
            from transformers import CLIPModel

            if isinstance(train_module.backbone, CLIPModel):
                backbone_save_module = backbone_save_module.vision_model

            if train_module.train_config.lora:
                backbone_save_module = backbone_save_module.merge_and_unload()

            torch.onnx.register_custom_op_symbolic(
                symbolic_name="aten::scaled_dot_product_attention",
                symbolic_fn=custom_scaled_dot_product_attention,
                opset_version=17,
            )

            # Custom operation registered, we can produce our onnx model

            dummy_input = torch.randn(
                train_module.data_config["input_size"], device=device
            ).unsqueeze(0)
            torch.onnx.export(
                backbone_save_module,
                dummy_input,
                os.path.join(save_dir, "model.onnx"),
                custom_opsets={"onnx-script": 17},
                opset_version=17,
                input_names=["inputs"],
                output_names=["embeddings"],
                dynamic_axes={
                    "inputs": {0: "batch_size"},
                    "embeddings": {0: "batch_size"},
                },
            )
        # Case for using huggingface transformers
        else:
            logger.info("Exporting torch pt model to onnx...")
            model = ORTModel.from_pretrained(save_dir, export=True)
            # Saved with model.onnx
            logger.info("Saving onnx file...")
            model.save_pretrained(save_dir)

    elif model_type == "ImageTextClassifier":
        from .image_text_classifier import ImageTextClassifierModule

        assert (
            train_config.text_timm == False
        ), "timm is not supported for TextClassifier"
        logger.info("Exporting torch pt text model to onnx...")
        text_model = ORTModel.from_pretrained(
            os.path.join(save_dir, "text"), export=True
        )
        # Saved with model.onnx
        logger.info("Saving onnx file...")
        text_model.save_pretrained(os.path.join(save_dir, "text"))

        logger.info("Exporting torch pt image model to onnx...")
        # huggingface transformers
        if not train_config.image_timm:
            image_model = ORTModel.from_pretrained(
                os.path.join(save_dir, "image"), export=True
            )
            # Saved with model.onnx
            logger.info("Saving onnx file...")
            image_model.save_pretrained(os.path.join(save_dir, "image"))
        # timm
        else:
            train_module = ImageTextClassifierModule.load_from_checkpoint(
                os.path.join(save_dir, "model.ckpt"), map_location=device
            )
            from transformers import CLIPModel

            if isinstance(train_module.image_backbone, CLIPModel):
                image_backbone_save_module = (
                    train_module.image_backbone.model.vision_model
                )
            else:
                image_backbone_save_module = train_module.image_backbone

            # image_backbone_save_module = train_module.image_backbone.model
            if train_module.train_config.image_lora:
                image_backbone_save_module = (
                    image_backbone_save_module.merge_and_unload()
                )

            torch.onnx.register_custom_op_symbolic(
                symbolic_name="aten::scaled_dot_product_attention",
                symbolic_fn=custom_scaled_dot_product_attention,
                opset_version=17,
            )
            # Custom operation registered, we can produce our onnx model

            dummy_image_input = torch.randn(
                train_module.image_data_config["input_size"], device=device
            ).unsqueeze(0)
            torch.onnx.export(
                image_backbone_save_module,
                dummy_image_input,
                os.path.join(save_dir, "image/model.onnx"),
                custom_opsets={"onnx-script": 17},
                opset_version=17,
                input_names=["inputs"],
                output_names=["embeddings"],
                dynamic_axes={
                    "inputs": {0: "batch_size"},
                    "embeddings": {0: "batch_size"},
                },
            )

    else:
        raise ValueError(f"Model type {model_type} not supported.")


def export_onnx_optimization(save_dir: str, optimization_level: int = 2):
    """
    export optimized onnx model using onnxruntime

    Args:
        save_dir (str): directory to save the optimized onnx model
        optimization_level (int, optional): optimization level. Defaults to 2. Can be 1, 2, 3, 4
    """
    from optimum.onnxruntime import ORTOptimizer, AutoOptimizationConfig

    optimization_config_dict = {
        1: AutoOptimizationConfig.O1(),
        2: AutoOptimizationConfig.O2(),
        3: AutoOptimizationConfig.O3(),
        4: AutoOptimizationConfig.O4(),
    }

    if optimization_level not in optimization_config_dict.keys():
        raise ValueError(f"Not supported optimization level {optimization_level}")
    optimization_config = optimization_config_dict[optimization_level]
    # Need to export onnx model first using export_onnx
    optimizer = ORTOptimizer.from_pretrained(save_dir, file_names="model.onnx")
    # saved with model_optimized.onnx
    optimizer.optimize(save_dir=save_dir, optimization_config=optimization_config)


def export_onnx_quantization(save_dir: str, cpu_architecture: str = "avx512"):
    """
    export quantized onnx model using onnxruntime

    Args:
        save_dir (str): directory to save the quantized onnx model
        cpu_architecture (str, optional): cpu architecture. Defaults to "avx512". Can be "arm64", "avx2", "avx512", "avx512_vnni", "tensorrt"
    """
    from optimum.onnxruntime import ORTQuantizer
    from optimum.onnxruntime.configuration import AutoQuantizationConfig

    supported_architectures = ["arm64", "avx2", "avx512", "avx512_vnni", "tensorrt"]
    if cpu_architecture not in supported_architectures:
        raise ValueError(
            f"Not supported quantization cpu architecture {cpu_architecture}"
        )
    # Need to export onnx model first using export_onnx
    quantizer = ORTQuantizer.from_pretrained(save_dir, file_name="model.onnx")
    # Use dynamic quantization, not using calibration dataset.
    dqconfig = getattr(AutoQuantizationConfig, cpu_architecture)(
        is_static=False, per_channel=False
    )
    # saved with model_quantized.onnx
    model_quantized_path = quantizer.quantize(
        save_dir=save_dir, quantization_config=dqconfig
    )


def ImageClassifierInputPreprocess(
    input_img_paths: List[str], device: torch.device, transforms
):
    """
    Preprocess input images for image classifier.

    Args:
        input_img_paths (List[str]): list of image paths
        device (torch.device): device to use
        transforms (torchvision.transforms): torchvision transforms
    """
    inputs = []
    # PIL open image then preprocess with augmentation.
    for img_path in input_img_paths:
        if type(img_path) == str:
            try:
                if img_path.startswith("https:"):
                    input_img = Image.open(
                        requests.get(img_path, stream=True).raw
                    ).convert("RGB")
                else:
                    input_img = Image.open(img_path).convert("RGB")
            except:
                logger.warning(
                    f"Cannot open image {img_path}, use zero padding image instead"
                )
                input_img = Image.fromarray(np.zeros((224, 224, 3), dtype=np.uint8))
        ### 보통 inference할 때만 사용. -> pil image 자체가 input인 경우.
        elif isinstance(img_path, Image.Image):
            input_img = img_path.convert("RGB")
        else:
            raise TypeError(
                "Not supported input type for image classifier. Only support img path or pil image."
            )
        input_tensor = transforms(input_img).to(device)
        inputs.append(input_tensor)

    return torch.stack(inputs)


def TextClassifierInputPreprocess(
    input_texts: List[str], text_prompt: str, device: torch.device, tokenizer
):
    """
    Preprocess input texts for text classifier, including prompt and tokenizer.

    Args:
        input_texts (List[str]): list of input texts
        text_prompt (str): text prompt
        device (torch.device): device to use
        tokenizer (transformers.tokenizer): tokenizer
    """
    # Prompting and apply tokenizer.
    prompted_input_texts = list(map(lambda x: text_prompt.format(x), input_texts))

    inputs = tokenizer(
        prompted_input_texts, padding=True, truncation=True, return_tensors="pt"
    ).to(device)

    return inputs


def TextClassifierSelectToken(
    backbone_outputs: torch.Tensor, inputs: dict, configs: AutoConfig
):
    """
    Selecting the proper token for text classifier.
    Can be different for each model_type, so we need to handle it separately.
    Currently only implemented for gpt_neox.

    Args:
        backbone_outputs (torch.tensor): backbone outputs
        inputs (dict): model inputs
        configs (AutoConfig): model configs
    """
    # For classificaiton, model use the last token as other causal models (e.g. GPT-1) do. We utilize attention mask to know the position of the last token.
    if configs.model_type == "gpt_neox":
        last_hidden_state = backbone_outputs[0]
        if type(last_hidden_state) == np.ndarray:
            selected_tokens = last_hidden_state[
                np.arange(last_hidden_state.shape[0]),
                inputs["attention_mask"].sum(axis=-1) - 1,
            ]
            selected_tokens = torch.from_numpy(selected_tokens)
        else:
            selected_tokens = last_hidden_state[
                torch.arange(last_hidden_state.shape[0]),
                inputs["attention_mask"].sum(axis=-1) - 1,
            ]

        return selected_tokens

    elif (
        configs.model_type == "roberta"
        or configs.model_type == "xlm-roberta"
        or configs.model_type == "electra"
        or configs.model_type == "bert"
    ):
        last_hidden_state = backbone_outputs[0]
        if type(last_hidden_state) == np.ndarray:
            last_hidden_state = torch.from_numpy(last_hidden_state)
        selected_tokens = last_hidden_state[:, 0]

        return selected_tokens
    ##  hm
    elif configs.model_type == "mpnet":
        # print('============= you are here =============')
        def mean_pooling(model_output, attention_mask):
            token_embeddings = model_output[0]
            input_mask_expanded = (
                attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
            )
            return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
                input_mask_expanded.sum(1), min=1e-9
            )

        attention_mask = inputs["attention_mask"]

        if type(backbone_outputs) == np.ndarray:
            backbone_outputs = torch.from_numpy(backbone_outputs)

        selected_tokens = mean_pooling(backbone_outputs, attention_mask)
        selected_tokens = F.normalize(selected_tokens, p=2, dim=1)

        return selected_tokens

    else:
        raise NotImplementedError(
            f"{configs.model_type} selecting token method is not implemented."
        )


def is_parallel(model):
    """check if model is in parallel mode."""

    parallel_type = (
        nn.parallel.DataParallel,
        nn.parallel.DistributedDataParallel,
    )
    return isinstance(model, parallel_type)


def copy_attr(a, b, include=(), exclude=()):
    # Copy attributes from b to a, options to only include [...] and to exclude [...]
    for k, v in b.__dict__.items():
        if (len(include) and k not in include) or k.startswith("_") or k in exclude:
            continue
        else:
            setattr(a, k, v)


class ModelEMA:
    """
    Model Exponential Moving Average from https://github.com/rwightman/pytorch-image-models
    Keep a moving average of everything in the model state_dict (parameters and buffers).
    This is intended to allow functionality like
    https://www.tensorflow.org/api_docs/python/tf/train/ExponentialMovingAverage
    A smoothed version of the weights is necessary for some training schemes to perform well.
    This class is sensitive where it is initialized in the sequence of model init,
    GPU assignment and distributed training wrappers.
    """

    def __init__(self, models, decay=0.9999, updates=0):
        """
        Args:
            models (tuple of nn.Module): model list to apply EMA.
            decay (float): ema decay reate.
            updates (int): counter of EMA updates.
        """
        # Create EMA(FP32)
        self.ema = ()
        self.updates = ()
        self.decay = decay
        for model in models:
            ema = deepcopy(model.module if is_parallel(model) else model).eval()
            self.ema = self.ema + (ema,)
            # decay exponential ramp (to help early epochs)
            # self.decay = lambda x: decay * (1 - math.exp(-x / 2000))
            for p in ema.parameters():
                p.requires_grad_(False)

        self.updates = (updates,) * len(models)

    def update(self, models):
        # Update EMA parameters
        self.updates += 1
        for idx, model in enumerate(models):
            with torch.no_grad():
                # d = self.decay(self.updates)
                d = self.decay
                msd = (
                    model.module.state_dict()
                    if is_parallel(model)
                    else model.state_dict()
                )  # model state_dict
                for k, v in self.ema[idx].state_dict().items():
                    if v.dtype.is_floating_point:
                        v *= d
                        v += (1.0 - d) * msd[k].detach()

    @staticmethod
    def update_attr(
        updating_models,
        cand_models,
        include=(),
        exclude=("process_group", "reducer", "training"),
    ):
        for updating_model, cand_model in zip(updating_models, cand_models):
            # Update EMA attributes
            copy_attr(updating_model, cand_model, include, exclude)


def find_indices_based_on_max_and_label(tensor, labels, threshold):
    # 각 행의 최대값과 그 인덱스를 계산
    max_values, max_indices = torch.max(tensor, dim=1)

    # 조건 1: 최대값이 threshold보다 큰 경우
    condition1 = max_values > threshold

    # 조건 2: 최대값의 인덱스가 labels와 일치하는 경우
    condition2 = max_indices == labels

    # 두 조건을 모두 만족하는 경우
    valid_indices = torch.where(condition1 & condition2)[0]

    # 두 조건 중 하나라도 만족하지 않는 경우
    invalid_indices = torch.where(~(condition1 & condition2))[0]

    return valid_indices, invalid_indices
