import logging
import torch

from ..head_classifier import *
from .image_config import ImageClassifierConfig
from ..base_trainer import BaseClassifierModule
from ..base_feedback_trainer import FeedbackBaseClassifierModule

logger = logging.getLogger(__name__)


class ImageClassifierModule(BaseClassifierModule):
    """
    Image Classifier for training and inference.

    Args:
        train_config (ImageClassifierConfig): ImageClassifierConfig.
    """

    def __init__(self, train_config: ImageClassifierConfig):
        super().__init__(train_config)

        (
            self.backbone,
            self.train_transforms,
            self.val_transforms,
            self.data_config,
            self.train_config.timm,
            self.initial_config,
        ) = self.get_model()
        self.embedding_size = self.backbone.forward(
            torch.randn(self.data_config["input_size"]).unsqueeze(0)
        ).shape[-1]

        # Define classifier
        if type(self.train_config.fc_classifier) == str:
            classifier_class = globals()[self.train_config.fc_classifier]
            self.classifier_head = classifier_class(
                self.embedding_size, self.train_config.num_class
            )
        else:
            self.classifier_head = self.train_config.fc_classifier(
                self.embedding_size, self.train_config.num_class
            )

        self.save_hyperparameters()

    def get_model(self):
        """
        Get model, train transforms, val transforms, initial config, and timm flag.
        """
        return self.get_image_model(
            self.train_config.backbone_name,
            self.train_config.freeze,
            self.train_config.lora,
            self.train_config.lora_r,
            self.train_config.lora_alpha,
            self.train_config.lora_target_modules,
            self.train_config.lora_dropout,
        )

    # model forward
    def forward(
        self,
        input_img_paths,
        backbone=None,
        classifier_head=None,
        eval=False,
        classifier=True,
    ):
        if backbone is None:
            backbone = self.backbone
        if classifier_head is None:
            classifier_head = self.classifier_head
        return self.image_forward(
            input_img_paths,
            backbone,
            classifier_head,
            self.train_config.freeze,
            eval=eval,
            classifier=classifier,
        )

    def configure_optimizers(self):
        optimizer = self.classifier_head_optimizers()
        optimizer = self.add_optimizers(
            optimizer,
            self.backbone,
            self.train_config.freeze,
            self.train_config.lora,
            self.train_config.backbone_learning_rate,
        )

        lr_scheduler = self.get_lr_scheduler(optimizer, self.train_config.lr_scheduler)

        return [optimizer], [{"scheduler": lr_scheduler}]


class FeedbackImageClassifierModule(FeedbackBaseClassifierModule):
    """
    FeedbackImage Classifier for training and inference.

    Args:
        train_config (ImageClassifierConfig): ImageClassifierConfig.
    """

    def __init__(self, train_config: ImageClassifierConfig):
        super().__init__(train_config)

        (
            self.backbone,
            self.train_transforms,
            self.val_transforms,
            self.data_config,
            self.train_config.timm,
            self.initial_config,
        ) = self.get_model()
        self.embedding_size = self.backbone.forward(
            torch.randn(self.data_config["input_size"]).unsqueeze(0)
        ).shape[-1]

        # Define classifier
        if type(self.train_config.fc_classifier) == str:
            classifier_class = globals()[self.train_config.fc_classifier]
            self.classifier_head = classifier_class(
                self.embedding_size, self.train_config.num_class
            )
        else:
            self.classifier_head = self.train_config.fc_classifier(
                self.embedding_size, self.train_config.num_class
            )

        self.save_hyperparameters()

    def get_model(self):
        """
        Get model, train transforms, val transforms, initial config, and timm flag.
        """
        return self.get_image_model(
            self.train_config.backbone_name,
            self.train_config.freeze,
            self.train_config.lora,
            self.train_config.lora_r,
            self.train_config.lora_alpha,
            self.train_config.lora_target_modules,
            self.train_config.lora_dropout,
        )

    # model forward
    def forward(
        self,
        input_img_paths,
        backbone=None,
        classifier_head=None,
        eval=False,
        classifier=True,
    ):
        if backbone is None:
            if type(self.backbone) == nn.ModuleList:
                backbone = self.backbone[0]
            else:
                backbone = self.backbone
        if classifier_head is None:
            classifier_head = self.classifier_head
        return self.image_forward(
            input_img_paths,
            backbone,
            classifier_head,
            self.train_config.freeze,
            eval=eval,
            classifier=classifier,
        )

    def configure_optimizers(self):
        optimizer = self.classifier_head_optimizers()
        optimizer = self.add_optimizers(
            optimizer,
            self.backbone,
            self.train_config.freeze,
            self.train_config.lora,
            self.train_config.backbone_learning_rate,
        )

        lr_scheduler = self.get_lr_scheduler(optimizer, self.train_config.lr_scheduler)

        return [optimizer], [{"scheduler": lr_scheduler}]
