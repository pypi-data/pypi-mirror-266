import logging
from ..base_config import BaseClassifierConfig

logger = logging.getLogger(__name__)


class ImageTextClassifierConfig(BaseClassifierConfig):
    """
    ImageText Classifier Config.

    Args:
        text_prompt (str): Text prompt for text classification, default: "{}의 상품 종류는?".
        image_backbone_name (str): Image backbone name, default: "eva_large_patch14_196.in22k_ft_in22k_in1k".
        text_backbone_name (str): Text backboname, default: "EleutherAI/polyglot-ko-1.3b".
        classifier_learning_reate (float): Classifier learning rate, default: 1e-3.
        image_backbone_learning_rate (float): Image backbone learning rate, default: 4e-5.
        text_backbone_learning_rate (float): Text backbone learning rate, default: 3e-4.
        image_freeze (bool): Freeze image backbone, default: False.
        text_freeze (bool): Freeze text backbone, default: False.
        image_lora (bool): Use LoRA for image backbone, default: True.
        text_lora (bool): Use LoRA for text backbone, default: True.
        image_lora_r (int): LoRA r for image backbone, default: 16.
        text_lora_r (int): LoRA r for text backbone, default: 16.
        image_lora_alpha (int): LoRA alpha for image backbone, default: 16.
        text_lora_alpha (int): LoRA alpha for text backbone, default: 16.
        image_lora_target_modules (list): LoRA target modules for image backbone, default: ["qkv"].
        text_lora_target_modules (list): LoRA target modules for text backbone, default: ["query_key_value"].
        image_lora_dropout (float): LoRA dropout for image backbone, default: 0.1.
        text_lora_dropout (float): LoRA dropout for text backbone, default: 0.1.
        auto_augment (str): Auto augment for image backbone, default: "rand-m9-mstd0.5-inc1".
        crop_ratio (float): Minimum crop ratio for image backbone when augmentation image, default: 0.9.
    """

    def __init__(
        self,
        text_prompt: str = "{}의 상품 종류는?",
        image_backbone_name: str = "eva_large_patch14_196.in22k_ft_in22k_in1k",
        text_backbone_name: str = "EleutherAI/polyglot-ko-1.3b",
        classifier_learning_rate: float = 1e-3,
        image_backbone_learning_rate: float = 4e-5,
        text_backbone_learning_rate: float = 3e-4,
        image_freeze: bool = False,
        text_freeze: bool = False,
        image_lora: bool = True,
        text_lora: bool = True,
        image_lora_r: int = 16,
        text_lora_r: int = 16,
        image_lora_alpha: int = 16,
        text_lora_alpha: int = 16,
        image_lora_target_modules: list = None,
        text_lora_target_modules: list = None,
        image_lora_dropout: float = 0.1,
        text_lora_dropout: float = 0.1,
        auto_augment: str = "rand-n3-mstd1",
        crop_ratio: float = 0.9,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.text_prompt = text_prompt
        self.image_backbone_name = image_backbone_name
        self.text_backbone_name = text_backbone_name
        self.classifier_learning_rate = classifier_learning_rate
        self.image_backbone_learning_rate = image_backbone_learning_rate
        self.text_backbone_learning_rate = text_backbone_learning_rate

        # Training Config
        self.image_freeze = image_freeze
        self.text_freeze = text_freeze
        self.image_lora = image_lora
        self.text_lora = text_lora
        if self.image_freeze and self.image_lora:
            raise ValueError(
                "freezing backbone and using lora for image backbone cannot be True at the same time"
            )
        if self.text_freeze and self.text_lora:
            raise ValueError(
                "freezing backbone and using lora for text backbone cannot be True at the same time"
            )

        self.image_lora_r = image_lora_r
        self.text_lora_r = text_lora_r
        self.image_lora_alpha = image_lora_alpha
        self.text_lora_alpha = text_lora_alpha
        if image_lora_target_modules is None:
            self.image_lora_target_modules = ["qkv"]
        else:
            self.image_lora_target_modules = image_lora_target_modules
        if text_lora_target_modules is None:
            self.text_lora_target_modules = ["query_key_value"]
        else:
            self.text_lora_target_modules = text_lora_target_modules
        self.image_lora_dropout = image_lora_dropout
        self.text_lora_dropout = text_lora_dropout
        # Image Augmentation
        self.auto_augment = auto_augment
        self.crop_ratio = crop_ratio

        # Boolean to check if the model is loaded from transformers or timm, will be set in trainer
        self.text_timm = False
        self.image_timm = None
