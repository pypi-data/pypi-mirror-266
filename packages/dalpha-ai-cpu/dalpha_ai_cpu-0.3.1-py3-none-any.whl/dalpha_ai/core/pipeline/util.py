import os
import json
import pickle
from typing import Union, List
import torch
import torch.nn.functional as F

import logging
import numpy as np

logger = logging.getLogger(__name__)


def postprocess(
    logits: torch.Tensor,
    topk: int,
    label_name_list: List[str],
    return_logits: bool,
    sigmoid: bool,
    temperature: float,
):
    """
    Postprocess logits to topk predictions.

    Args:
        logits (torch.Tensor): Logits from model.
        topk (int): Top k prediction.
        label_name_list (List[str]): List of label names.
        return_logits (bool): Return logits or not.
        sigmoid (bool): Apply sigmoid to logits or not.
    """
    _, predictions = logits.topk(topk, 1, True, True)
    predictions_index = predictions.cpu().detach().numpy()

    cat_list = []
    # In case when label name list is not defined in the training step, pipeline returns the category label index of prediction, instead of category name.
    if label_name_list is None:
        logger.warning(
            "Label name list is not defined in the training step, pipeline returns the category label index of prediction, instead of category name."
        )

        for pred_index in predictions_index:
            cat_list.append(
                list(
                    map(
                        lambda x: x,
                        pred_index,
                    )
                )
            )
    else:
        for pred_index in predictions_index:
            cat_list.append(
                list(
                    map(
                        lambda x: label_name_list[x],
                        pred_index,
                    )
                )
            )

    if return_logits:
        if type(logits) == np.ndarray:
            logits = torch.from_numpy(logits)
        if sigmoid:
            return F.sigmoid(logits.to(torch.float32)).cpu().detach().numpy(), cat_list
        else:
            return (
                F.softmax(logits.to(torch.float32) / temperature, dim=-1)
                .cpu()
                .detach()
                .numpy(),
                cat_list,
            )

    else:
        return cat_list
