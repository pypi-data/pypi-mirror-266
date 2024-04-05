import pandas as pd
from torch.utils.data import Dataset
from typing import Optional
import torch
from pytorch_lightning import LightningDataModule
from typing import Union


class BaseDataModule(LightningDataModule):
    """
    Base DataModule for all classification tasks
    Args:
        train_dataset (pd.DataFrame): training dataset
        val_dataset (pd.DataFrame): validation dataset
        test_dataset (pd.DataFrame): test dataset
        train_config: train_config
    """

    def __init__(
        self,
        train_dataset: pd.DataFrame,
        val_dataset: pd.DataFrame,
        test_dataset: pd.DataFrame,
        train_config,
        feedback_dataset: Union[pd.DataFrame, None] = None,
    ):
        super().__init__()
        self.train_dataset = train_dataset
        self.val_dataset = val_dataset
        self.feedback_dataset = feedback_dataset
        self.test_dataset = test_dataset
        self.batch_size = train_config.batch_size
        self.num_workers = train_config.num_workers
        self.problem_type = train_config.problem_type
        self.num_class = train_config.num_class

    def train_dataloader(self):
        dataloader_kwargs = {
            "num_workers": self.num_workers,
            "pin_memory": True,
            "drop_last": True,
            "shuffle": True,
        }
        dataloader_kwargs["batch_size"] = self.batch_size

        return torch.utils.data.DataLoader(self.trainset, **dataloader_kwargs)

    def val_dataloader(self):
        dataloader_kwargs = {"num_workers": self.num_workers, "pin_memory": True}
        dataloader_kwargs["batch_size"] = self.batch_size

        return torch.utils.data.DataLoader(self.valset, **dataloader_kwargs)

    def test_dataloader(self):
        dataloader_kwargs = {
            "num_workers": self.num_workers,
            "pin_memory": True,
        }
        dataloader_kwargs["batch_size"] = self.batch_size

        return torch.utils.data.DataLoader(self.testset, **dataloader_kwargs)
