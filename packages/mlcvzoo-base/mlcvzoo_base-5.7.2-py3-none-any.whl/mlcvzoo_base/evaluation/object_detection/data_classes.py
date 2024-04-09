# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""
Module for storing data classes and complex type definitions that are used in the context of the
mlcvzoo_base.evaluation.object_detection package
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Final, List, Optional

import numpy as np

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.bounding_box import BoundingBox

# 3D List containing of the following:
#   1) One entry per data items / image
#   2) One entry per call of classes
#   3) One entry per annotation Annotations the matches the image (1) and the class (2)
# This is a list of BaseAnnotations in order to carry information about the image
# instead of just bounding boxes
EVALUATION_LIST_TYPE = List[List[List[BaseAnnotation]]]  # pylint: disable=invalid-name

CONFUSION_MATRIX_TYPE = List[List[int]]
CONFUSION_MATRIX_DICT_TYPE = Dict[str, Dict[str, int]]  # pylint: disable=invalid-name

DEFAULT_INT_VALUE: Final[int] = 0
DEFAULT_FLOAT_VALUE: Final[float] = 0.0


# NOTE: Since this are the main Object Detection metrics, it's okay to have more instance
#       attributes
@dataclass
class ODMetrics:  # pylint: disable=too-many-instance-attributes
    """
    Dataclass for storing the main metrics that are computed for object detection algorithms
    """

    # TODO: rename to lower case, disable pylint only temporary!
    TP: int = DEFAULT_INT_VALUE  # pylint: disable=invalid-name
    FP: int = DEFAULT_INT_VALUE  # pylint: disable=invalid-name
    FN: int = DEFAULT_INT_VALUE  # pylint: disable=invalid-name
    PR: float = DEFAULT_FLOAT_VALUE  # pylint: disable=invalid-name
    RC: float = DEFAULT_FLOAT_VALUE  # pylint: disable=invalid-name
    F1: float = DEFAULT_FLOAT_VALUE  # pylint: disable=invalid-name
    AP: float = DEFAULT_FLOAT_VALUE  # pylint: disable=invalid-name
    COUNT: int = DEFAULT_INT_VALUE  # pylint: disable=invalid-name

    @staticmethod
    def from_dict(input_dict: Dict[str, Any]) -> ODMetrics:
        return ODMetrics(**input_dict)

    def __repr__(self):  # type: ignore
        return (
            f"TP: {self.TP}, "
            f"FP: {self.FP}, "
            f"FN: {self.FN}, "
            f"PR: {self.PR}, "
            f"RC: {self.RC}, "
            f"F1: {self.F1}, "
            f"AP: {self.AP}, "
            f"COUNT: {self.COUNT}"
        )

    def __str__(self):  # type: ignore
        return self.__repr__()


@dataclass
class MetricImageInfo:
    """
    Dataclass to store information about false positives and false negatives in the
    form of BaseAnnotation objects. This to have a exact relation between an image
    and the according false positive / false negative bounding boxes. The ground
    truth data is added to be able to visualize the expected bounding boxes.
    """

    ground_truth_annotation: Optional[BaseAnnotation] = None
    false_negative_annotation: Optional[BaseAnnotation] = None
    false_positive_annotation: Optional[BaseAnnotation] = None
    false_negative_matched_false_positive_annotation: Optional[BaseAnnotation] = None


# 1st key: Class Identifier as string
# 2nd key: Image Path
# 2nd value: The MetricImageInfo for this class name and image path
METRIC_IMAGE_INFO_TYPE = Dict[str, Dict[str, MetricImageInfo]]  # pylint: disable=invalid-name


# 1st key: iou-threshold
# 2nd key: Type of the size of the bounding-box => Any of BBoxSizeTypes.BBOX_SIZE_TYPE
# 3rd key: Class Identifier as string
# value: The computed metrics of type ODMetrics
METRIC_DICT_TYPE = Dict[float, Dict[str, Dict[str, ODMetrics]]]  # pylint: disable=invalid-name


def build_metric_dict_from_dict(
    input_dict: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]]
) -> METRIC_DICT_TYPE:
    metric_dict: METRIC_DICT_TYPE = {}

    for key_0, value_0 in input_dict.items():
        metric_dict[float(key_0)] = {}
        for key_1, value_1 in value_0.items():
            metric_dict[float(key_0)][key_1] = {}
            for key_2, od_metrics_dict in value_1.items():
                metric_dict[float(key_0)][key_1][key_2] = ODMetrics.from_dict(
                    input_dict=od_metrics_dict
                )

    return metric_dict


@dataclass
class ODModelEvaluationMetrics:
    """
    Dataclass for storing the output of an object detection evaluation.
    The metrics_dict stores the actual computed metrics, while the metrics_image_info_dict
    stores debugging information to be able to analyze false positives and false negatives.

    The model_specifier indicates for which model the metrics have been computed.
    """

    model_specifier: str
    metrics_dict: METRIC_DICT_TYPE = field(default_factory=lambda: {})
    metrics_image_info_dict: METRIC_IMAGE_INFO_TYPE = field(default_factory=lambda: {})


@dataclass
class ODEvaluationComputingData:
    """
    Dataclass for storing data structures that are needed to computed object detection metrics
    """

    # 1st key: Type of the size of the bounding-box => Any of BBoxSizeTypes.BBOX_SIZE_TYPE
    # 2nd key: Class Identifier as string
    # value: The number of ground truth boxes for the combination of keys
    gt_counter_dict: Dict[str, Dict[str, int]] = field(default_factory=lambda: {})

    # 1st key: iou-threshold
    # 2nd key: Type of the size of the bounding-box => Any of BBoxSizeTypes.BBOX_SIZE_TYPE
    # Cumulative array indicating the false positives of the dataset
    false_positives_dict: Dict[float, Dict[str, np.ndarray]] = field(  # type: ignore[type-arg]
        default_factory=lambda: {}
    )

    # 1st key: iou-threshold
    # 2nd key: Type of the size of the bounding-box => Any of BBoxSizeTypes.BBOX_SIZE_TYPE
    # Cumulative array indicating the true positives of the dataset
    true_positives_dict: Dict[float, Dict[str, np.ndarray]] = field(  # type: ignore[type-arg]
        default_factory=lambda: {}
    )

    # 1st key: iou-threshold
    # 2nd key: Type of the size of the bounding-box => Any of BBoxSizeTypes.BBOX_SIZE_TYPE
    # value: Array indicating the score for each data item
    scores: Dict[float, Dict[str, np.ndarray]] = field(  # type: ignore[type-arg]
        default_factory=lambda: {}
    )

    # key: iou-threshold
    detected_annotations: Dict[float, List[BoundingBox]] = field(default_factory=lambda: {})

    # TODO: Is this needed?! => Remove at next major version update
    # 1st key: iou-threshold
    # 2nd key: Type of the size of the bounding-box => Any of BBoxSizeTypes.BBOX_SIZE_TYPE
    # List indicating the AP metrics that have been computed correctly
    valid_precisions: Dict[float, Dict[str, List[float]]] = field(default_factory=lambda: {})
