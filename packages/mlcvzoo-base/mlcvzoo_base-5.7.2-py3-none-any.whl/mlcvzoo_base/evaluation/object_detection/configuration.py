# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

import logging
from typing import List, Optional

import related
from attr import define
from config_builder import BaseConfigClass

from mlcvzoo_base.configuration.annotation_handler_config import AnnotationHandlerConfig
from mlcvzoo_base.configuration.mlfow_config import MLFlowConfig
from mlcvzoo_base.configuration.model_config import ModelConfig
from mlcvzoo_base.configuration.visualization_config import VisualizationConfig

logger = logging.getLogger(__name__)


@define
class ODEvaluationInputDataConfig(BaseConfigClass):
    # path to the csv file, where the annotation data should be parsed from
    csv_file_path: str = related.StringField()


@define
class TensorboardLoggingConfig(BaseConfigClass):
    tensorboard_dir: str = related.StringField()
    false_positive_image_size: int = related.IntegerField(default=650)


@define
class ODEvaluationConfig(BaseConfigClass):
    iou_thresholds: List[float] = related.SequenceField(float)

    mlflow_config: Optional[MLFlowConfig] = related.ChildField(
        cls=MLFlowConfig, required=False, default=None
    )

    tensorboard_logging: Optional[TensorboardLoggingConfig] = related.ChildField(
        cls=TensorboardLoggingConfig, required=False, default=None
    )

    visualization: VisualizationConfig = related.ChildField(
        cls=VisualizationConfig, default=VisualizationConfig()
    )

    model_configs: Optional[List[ModelConfig]] = related.SequenceField(
        cls=ModelConfig, required=False, default=None
    )

    input_data: Optional[List[ODEvaluationInputDataConfig]] = related.SequenceField(
        cls=ODEvaluationInputDataConfig, required=False, default=None
    )

    annotation_handler_config: Optional[AnnotationHandlerConfig] = related.ChildField(
        cls=AnnotationHandlerConfig, required=False, default=None
    )

    def check_values(self) -> bool:
        logger.warning(
            "DEPRECATED: The class ODEvaluationConfig is deprecated and will"
            "be removed in future versions"
        )
        return True
