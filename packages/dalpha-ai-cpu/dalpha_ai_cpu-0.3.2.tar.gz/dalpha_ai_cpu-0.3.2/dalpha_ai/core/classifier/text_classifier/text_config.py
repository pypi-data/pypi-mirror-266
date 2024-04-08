import torch
import logging
from ..base_config import BaseClassifierConfig

logger = logging.getLogger(__name__)


class TextClassifierConfig(BaseClassifierConfig):
    """
    Text Classifier Config.

    Args:
        text_prompt (str): Text prompt for the task, default: "{}의 상품 종류는?".
        backbone_name (str): Name of the backbone model, default: "EleutherAI/polyglot-ko-1.3b".
        classifier_learning_rate (float): Learning rate for the classifier, default: 1e-3.
        backbone_learning_rate (float): Learning rate for the backbone, default: 3e-4.
        freeze (bool): Whether to freeze the backbone, default: False.
        lora (bool): Whether to use LoRA for the backbonㄷ, default: True.
        lora_r (int): LoRA r parameter, default: 16.
        lora_alpha (int): LoRA alpha parameter, default: 16.
        lora_target_modules (list): LoRA target modules, default: ["query_key_value"].
        lora_dropout (float): LoRA dropout, default: 0.1.
    """

    def __init__(
        self,
        text_prompt: str = "{}의 상품 종류는?",
        backbone_name: str = "EleutherAI/polyglot-ko-1.3b",
        classifier_learning_rate: float = 1e-3,
        backbone_learning_rate: float = 3e-4,
        freeze: bool = False,
        lora: bool = True,
        lora_r: int = 16,
        lora_alpha: int = 16,
        lora_target_modules: list = None,
        lora_dropout: float = 0.1,
        **kwargs
    ):
        super().__init__(**kwargs)
        # 태스크에 맞게 text prompt 수정 필수!
        self.text_prompt = text_prompt
        self.backbone_name = backbone_name
        self.classifier_learning_rate = classifier_learning_rate
        self.backbone_learning_rate = backbone_learning_rate

        self.freeze = freeze
        self.lora = lora
        if self.freeze and self.lora:
            raise ValueError(
                "freezing backbone and using lora cannot be True at the same time"
            )

        self.lora_r = lora_r
        self.lora_alpha = lora_alpha
        if lora_target_modules is None:
            self.lora_target_modules = ["query_key_value"]
        else:
            self.lora_target_modules = lora_target_modules
        self.lora_dropout = lora_dropout
        # Boolean to check if the model is loaded from transformers or timm, default value is False for TextClassifier
        self.timm = False
