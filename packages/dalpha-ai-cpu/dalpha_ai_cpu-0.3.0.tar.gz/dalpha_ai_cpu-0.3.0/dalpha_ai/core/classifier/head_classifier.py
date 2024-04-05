import torch.nn as nn
import torch.nn.functional as F


class Base2LinearClassifier(nn.Module):
    """
    Head Classifier with 2 Linear Layers and relu, dropout 0.5 in between
    """

    def __init__(self, embedding_size, num_class):
        super().__init__()
        self.fc_layer1 = nn.Linear(embedding_size, embedding_size)
        self.fc_layer2 = nn.Linear(embedding_size, num_class)
        self.bn1 = nn.BatchNorm1d(embedding_size)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = self.fc_layer1(x)
        x = self.bn1(x)
        x = F.relu(x)
        x = self.dropout(x)
        x = self.fc_layer2(x)

        return x


class BaseLinearClassifier(nn.Module):
    """
    Head Classifier with 1 Linear Layer
    """

    def __init__(self, embedding_size, num_class):
        super().__init__()
        self.fc_layer1 = nn.Linear(embedding_size, num_class)

    def forward(self, x):
        x = self.fc_layer1(x)

        return x


class ElectraClassifier(nn.Module):
    """
    Classifier for Electra Model (following huggingface)
    """

    def __init__(self, embedding_size, num_class):
        super().__init__()
        self.fc_layer1 = nn.Linear(embedding_size, embedding_size)
        self.dropout = nn.Dropout(0.1)
        self.fc_layer2 = nn.Linear(embedding_size, num_class)

    def forward(self, x):
        x = self.dropout(x)
        x = self.fc_layer1(x)
        x = F.gelu(x)
        x = self.dropout(x)
        x = self.fc_layer2(x)

        return x
