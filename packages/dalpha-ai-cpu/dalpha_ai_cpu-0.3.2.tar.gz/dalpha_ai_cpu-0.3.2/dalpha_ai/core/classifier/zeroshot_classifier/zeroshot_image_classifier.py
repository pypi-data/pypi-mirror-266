import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"
import copy
import torch

torch.backends.cudnn.benchmark = False
import logging
from typing import List, Union

import pandas as pd
from PIL import Image
import requests

# for test
from tqdm import tqdm
import time
from .zeroshot_image_datamodule import TextDataset, ImageDataset, ImageClassifierDataset
from .zeroshot_image_config import ZeroshotImageClassifierConfig
import torch.nn.functional as F
from torch.utils.data import DataLoader

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class ZeroshotImageClassifier:
    """
    Zeroshot Image Classifier.

    Args:
        test_dataset (Union[pd.DataFrame, List[List]]): Test dataset, optional.
        label_name_list (List[str]): List of label names, optional.
        label_embeddings (torch.Tensor): Label embeddings, optional.
        config (ZeroshotImageClassifierConfig): ZeroshotImageClassifierConfig, optional.
        device (str): Device, optional.
    """

    def __init__(
        self,
        test_dataset: Union[pd.DataFrame, List[List]] = None,
        label_name_list: List[str] = None,
        label_embeddings: torch.Tensor = None,
        config: ZeroshotImageClassifierConfig = None,
        device: str = None,
    ):
        # Initial starting without loading from checkpoint
        if config is None:
            output_dir = "tmp_classifier"
            logger.info(
                f"No `ZeroshotImageClassifierConfig` passed, using `output_dir={output_dir}`."
            )
            train_config = ZeroshotImageClassifierConfig(output_dir=output_dir)

        self.train_config = config

        if device is None:
            self.device = self.train_config.device
        else:
            self.device = device

        test_dataset = copy.deepcopy(test_dataset)
        # Dataset Setting

        if test_dataset is not None:
            logger.info(
                "Test dataset is provided, you can inference test dataset with ZeroshotImageClassifier().test()"
            )
            if type(test_dataset) == pd.DataFrame:
                if len(test_dataset.columns) != 2:
                    raise ValueError(
                        f"When the test dataset data type is DataFrame, length of the column has to fixed with 2."
                    )
                if test_dataset.columns[0] != "img_path":
                    logger.warning(
                        f"When the test dataset data type is DataFrame, first column name has to be 'img_path', assuming '{test_dataset.columns[0]}' means 'img_path' column."
                    )
                    test_dataset.rename(
                        columns={test_dataset.columns[0]: "img_path"}, inplace=True
                    )
                if test_dataset.columns[1] != "label":
                    logger.warning(
                        f"When the test dataset data type is DataFrame, first column name has to be 'label', assuming '{test_dataset.columns[1]}' means 'label' column."
                    )
                    test_dataset.rename(
                        columns={test_dataset.columns[1]: "label"}, inplace=True
                    )

            elif type(test_dataset) == list:
                if len(test_dataset) != 2:
                    raise ValueError(
                        f"When the test dataset data type is List, length of the list has to fixed with 2."
                    )
                else:
                    logger.warning(
                        "When the test dataset data type is List, we assume that the first component of list means 'img_path', and the second component of list means 'label'."
                    )
                # test_dataset = pd.DataFrame(test_dataset, columns=["img_path", "label"])
                test_dataset = pd.DataFrame(
                    {"img_path": test_dataset[0], "label": test_dataset[1]}
                )

            else:
                raise TypeError(
                    f"Not supported test dataset type, {type(test_dataset)}"
                )

            if test_dataset["label"].dtype != "int":
                raise TypeError(
                    f"Expect int datatype for test dataset label, but get {test_dataset['label'].dtype}"
                )

        if self.train_config.backbone_name == "clip":
            from transformers import AutoModel, AutoProcessor, AutoTokenizer

            name = self.train_config.model_name
            self.model = AutoModel.from_pretrained(name).to(self.device)
            self.processor = AutoProcessor.from_pretrained(name)
            self.tokenizer = AutoTokenizer.from_pretrained(name)

        else:
            raise ValueError(
                "This backbone is not currently supported. Supported backbone list are ['clip']."
            )

        if label_embeddings is None:
            if label_name_list is None:
                raise ValueError(
                    f"You must enter either 'label_name_list' or 'label_embeddings'."
                )
            else:
                logger.info("Make label embeddings with label name list.")
                dataset = TextDataset(label_name_list)
                dataloader = DataLoader(dataset=dataset, batch_size=1)
                text_embeddings = []
                success_text = []
                with torch.no_grad():
                    for batch in dataloader:
                        try:
                            inputs = self.tokenizer(
                                batch, padding=True, return_tensors="pt"
                            ).to(self.device)
                            emb = self.model.get_text_features(**inputs)
                            text_embeddings.append(emb)
                            success_text.append(batch)
                        except:
                            logger.warning(f"Cannot tokenize text, {batch}")
                    label_embeddings = torch.cat(text_embeddings).to(self.device)

        self.label_name_list = success_text
        self.label_embeddings = label_embeddings.to(self.device)

        # Check number of class when training config num class value is default value.
        if label_name_list is not None:
            if label_embeddings is not None:
                if label_embeddings.size()[0] != len(label_name_list):
                    raise ValueError(
                        f"The length of the label_name_list and size of the label_embeddings are different. Please check the size."
                    )

            logger.info("Get number of class with the length of label name list.")
            self.train_config.num_class = len(label_name_list)
            self.train_config.label_name_list = label_name_list
        else:
            if label_embeddings is not None:
                logger.info(
                    "Get number of class with the length of label embeddings tensor."
                )
                self.train_config.num_class = label_embeddings.size[0]
            else:
                raise ValueError(
                    f"You must enter either 'label_name_list' or 'label_embeddings'."
                )

        if test_dataset is not None:
            self.test_dataset = test_dataset

    def make_embedding(self, text: List[str] = None, image_path: List[str] = None):
        """
        Make embedding with text or image.

        Args:
            text (List[str], optional): List of text. Defaults to None.
            image_path (List[str], optional): List of image path. Defaults to None.
        """
        if text is None and image_path is None:
            raise ValueError("You must enter text or image_path.")
        if text is not None and image_path is not None:
            raise ValueError("Please enter either an text or image_path.")

        if image_path:
            dataset = ImageDataset(image_path)
            dataloader = DataLoader(dataset=dataset, batch_size=1)
            image_embeddings = []
            process_data = []
            with torch.no_grad():
                for batch in dataloader:
                    path = batch[0]
                    try:
                        if path[:4] == "http":
                            image = Image.open(requests.get(path, stream=True).raw)
                        else:
                            image = Image.open(path)

                        inputs = self.processor(images=image, return_tensors="pt").to(
                            self.device
                        )
                        emb = self.model.get_image_features(**inputs)
                        image_embeddings.append(emb)
                        process_data.extend(batch)
                    except:
                        logger.warning(f"Cannot processing image, {path}")
                result = torch.cat(image_embeddings).to(self.device)

        if text:
            dataset = TextDataset(text)
            dataloader = DataLoader(dataset=dataset, batch_size=1)
            text_embeddings = []
            process_data = []
            with torch.no_grad():
                for batch in dataloader:
                    try:
                        inputs = self.tokenizer(
                            batch, padding=True, return_tensors="pt"
                        ).to(self.device)
                        emb = self.model.get_text_features(**inputs)
                        text_embeddings.append(emb)
                        process_data.extend(batch)
                    except:
                        logger.warning(f"Cannot tokenize text, '{batch[0]}'")
                result = torch.cat(text_embeddings).to(self.device)

        return result, process_data

    def top_cos_sim(self, query, corpus, k):
        cos_sim = F.normalize(query) @ F.normalize(corpus).T
        similarity, indices = torch.topk(cos_sim, k)
        return similarity.cpu(), indices.cpu()

    def test(self):
        """
        Test model with test dataset.
        """
        print("Start testing")
        start_time = time.time()
        topk_list = self.train_config.print_topk_list
        if max(topk_list) > self.train_config.num_class:
            logger.warning(f"max of the topk is bigger than the number of class")
            topk_list = [i for i in topk_list if i <= self.train_config.num_class]

        test_dataset = ImageClassifierDataset(self.test_dataset)
        dataloader = DataLoader(dataset=test_dataset, batch_size=1)

        process_data = []

        total_num = 0
        topk_count = [0] * len(topk_list)
        # pred = []

        with torch.no_grad():
            for img_path, label in tqdm(dataloader):
                path = img_path[0]
                label = label[0].item()

                try:
                    if path[:4] == "http":
                        image = Image.open(requests.get(path, stream=True).raw)
                    else:
                        image = Image.open(path)

                    inputs = self.processor(images=image, return_tensors="pt").to(
                        self.device
                    )
                    emb = self.model.get_image_features(**inputs)
                    process_data.extend(img_path)

                    cos_sim, cos_ids = self.top_cos_sim(
                        emb, self.label_embeddings, max(topk_list)
                    )
                    # pred.append(cos_ids[0].tolist())

                    total_num += 1
                    for topk_idx, topk in enumerate(topk_list):
                        if label in cos_ids[0][:topk]:
                            topk_count[topk_idx] += 1

                except:
                    logger.warning(f"Cannot processing image, {path}")

        topk_acc = [round(i / total_num, 4) for i in topk_count]
        for acc, topk in zip(topk_acc, topk_list):
            print(f"Top {topk} accuracy: {acc}")
            logger.info(f"Top {topk} accuracy: {acc}")

        end_time = time.time()
        print(f"Total testing time: {end_time - start_time} seconds")

    def inference(self, input_image_path, topk=5):
        print("Start testing")
        start_time = time.time()
        if topk > self.train_config.num_class:
            topk = self.train_config.num_class
            logger.warning(
                f"topk is bigger than the number of class. topk is set to the number of classes '{topk}'"
            )

        test_dataset = ImageClassifierDataset(self.test_dataset)
        dataloader = DataLoader(dataset=test_dataset, batch_size=1)

        process_image_path = []
        pred = []

        with torch.no_grad():
            for path in input_image_path:
                try:
                    if path[:4] == "http":
                        image = Image.open(requests.get(path, stream=True).raw)
                    else:
                        image = Image.open(path)

                    inputs = self.processor(images=image, return_tensors="pt").to(
                        self.device
                    )
                    emb = self.model.get_image_features(**inputs)
                    process_image_path.append(path)

                    cos_sim, cos_ids = self.top_cos_sim(
                        emb, self.label_embeddings, topk
                    )

                    pred_index = cos_ids[0].tolist()
                    pred_category = [self.label_name_list[i] for i in pred_index]

                    pred.append(pred_category)

                except:
                    logger.warning(f"Cannot processing image, {path}")

        end_time = time.time()
        print(f"Total inference number: {len(process_image_path)} images")
        print(f"Total inference time: {end_time - start_time} seconds")
        return process_image_path, pred

    """
    Save model backbone with huggingface format, and classifier to onnx. 
    Exporting backbone to onnx has to be done outside the trainer class, due to the large memory usage. 
    Refer to the export_onnx function in trainer_util.py 
    """
