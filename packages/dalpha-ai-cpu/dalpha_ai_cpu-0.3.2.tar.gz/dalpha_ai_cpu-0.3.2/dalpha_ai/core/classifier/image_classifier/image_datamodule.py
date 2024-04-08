from pytorch_lightning import LightningDataModule
import pandas as pd
from torch.utils.data import Dataset
from typing import Optional
import torch
from .image_config import ImageClassifierConfig
from ..base_datamodule import BaseDataModule


class ImageClassifierDataset(Dataset):
    """
    Image Classifier Dataset.

    Args:
        data (pd.DataFrame): Dataframe containing image path and label.
        problem_type (str): Problem type, either "single_label_classification" or "multi_label_classification".
        num_class (int): Number of classes.
    """

    def __init__(self, data: pd.DataFrame, problem_type: str, num_class: int):
        super().__init__()
        self.img_path_list = data["img_path"].tolist()
        self.label_list = data["label"].tolist()
        self.problem_type = problem_type
        self.num_class = num_class

    def __getitem__(self, idx):
        input_img_path = self.img_path_list[idx]
        label = self.label_list[idx]

        if self.problem_type == "multi_label_classification":
            target = torch.zeros(self.num_class)
            # Case for single label, but want to use multi-label loss (e.g. BCE)
            if type(label) != list:
                label = [label]
            for lab in label:
                # negative sample
                if lab == -1:
                    continue
                target[lab] = 1

            return input_img_path, target
        # single label classification
        else:
            return input_img_path, label

    def __len__(self):
        return len(self.label_list)


class ImageClassifierDataModule(BaseDataModule):
    """
    Image Classifier Data Module.

    Args:
        train_dataset (pd.DataFrame): Training dataset.
        val_dataset (pd.DataFrame): Validation dataset.
        test_dataset (pd.DataFrame): Test dataset.
        train_config (ImageClassifierConfig): ImageClassifierConfig.
    """

    def __init__(
        self,
        train_dataset: pd.DataFrame,
        val_dataset: pd.DataFrame,
        test_dataset: pd.DataFrame,
        train_config: ImageClassifierConfig,
    ):
        super().__init__(train_dataset, val_dataset, test_dataset, train_config)


    def setup(self, stage: Optional[str] = None):
        self.trainset = ImageClassifierDataset(
            self.train_dataset, self.problem_type, self.num_class
        )
        self.valset = ImageClassifierDataset(
            self.val_dataset, self.problem_type, self.num_class
        )
        self.testset = ImageClassifierDataset(
            self.test_dataset, self.problem_type, self.num_class
        )


class FeedbackImageClassifierDataset(Dataset):
    """
    Feedback Image Classifier Dataset.

    Args:
        data (pd.DataFrame): Dataframe containing image path and label.
        problem_type (str): Problem type, either "single_label_classification" or "multi_label_classification".
        num_class (int): Number of classes.
    """

    def __init__(self, data: pd.DataFrame, problem_type: str, num_class: int):
        super().__init__()
        self.img_path_list = data["img_path"].tolist()
        self.label_list = data["label"].tolist()
        self.feedback_flag_list = data["feedback_flag"].tolist()
        self.problem_type = problem_type
        self.num_class = num_class

    def __getitem__(self, idx):
        input_img_path = self.img_path_list[idx]
        label = self.label_list[idx]
        feedback_flag = self.feedback_flag_list[idx]

        if self.problem_type == "multi_label_classification":
            target = torch.zeros(self.num_class)
            # Case for single label, but want to use multi-label loss (e.g. BCE)
            if type(label) != list:
                label = [label]
            for lab in label:
                # negative sample
                if lab == -1:
                    continue
                target[lab] = 1

            return input_img_path, target, feedback_flag
        # single label classification
        else:
            return input_img_path, label, feedback_flag

    def __len__(self):
        return len(self.label_list)



class FeedbackImageClassifierDataModule(BaseDataModule):
    """
    Feedback Image Classifier Data Module.

    Args:
        train_dataset (pd.DataFrame): Training dataset (containing original train data and feedback data).
        val_dataset (pd.DataFrame): Validation dataset.
        test_dataset (pd.DataFrame): Test dataset.
        train_config (ImageClassifierConfig): ImageClassifierConfig.
    """

    def __init__(
        self,
        train_dataset: pd.DataFrame,
        val_dataset: pd.DataFrame,
        test_dataset: pd.DataFrame,
        train_config: ImageClassifierConfig,
    ):
        super().__init__(train_dataset, val_dataset, test_dataset, train_config)

    def setup(self, stage: Optional[str] = None):
        self.trainset = FeedbackImageClassifierDataset(
            self.train_dataset, self.problem_type, self.num_class
        )
        # Use same dataset for validation with and without feedback
        self.valset = ImageClassifierDataset(
            self.val_dataset, self.problem_type, self.num_class
        )
        # Use same dataset for test with and without feedback
        self.testset = ImageClassifierDataset(
            self.test_dataset, self.problem_type, self.num_class
        )