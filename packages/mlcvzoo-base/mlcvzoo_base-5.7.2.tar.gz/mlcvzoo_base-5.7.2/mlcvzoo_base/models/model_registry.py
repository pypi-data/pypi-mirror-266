# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""Module to provide a registry for model and configuration constructors"""

import copy
import inspect
import logging
from typing import Any, Dict, List, Optional, Type

from config_builder import BaseConfigClass

from mlcvzoo_base.api.model import ConfigurationType, DataType, Model, PredictionType
from mlcvzoo_base.api.registry import MLCVZooRegistry
from mlcvzoo_base.configuration.config_registry import ConfigRegistry
from mlcvzoo_base.configuration.model_config import ModelConfig
from mlcvzoo_base.configuration.replacement_config import (
    STRING_REPLACEMENT_MAP_KEY,
    ReplacementConfig,
)
from mlcvzoo_base.models.read_from_file.configuration import ReadFromFileConfig
from mlcvzoo_base.models.read_from_file.model import (
    ReadFromFileClassificationModel,
    ReadFromFileObjectDetectionModel,
    ReadFromFileSegmentationModel,
)

logger = logging.getLogger(__name__)


class ModelRegistry(MLCVZooRegistry[Type[Model[PredictionType, ConfigurationType, DataType]]]):
    """
    Class to provide a registry for model and configuration constructors
    """

    def __init__(self) -> None:
        MLCVZooRegistry.__init__(self)

        # =================================================
        # Init and fill ConfigRegistry
        self._config_registry = ConfigRegistry()

        self._config_registry.register_module(
            module_type_name="read_from_file_config", module_constructor=ReadFromFileConfig
        )

        self._config_registry.register_external_module(
            module_type_name="yolox_config",
            module_constructor="YOLOXConfig",
            package_name="mlcvzoo_yolox.configuration",
        )

        self._config_registry.register_external_module(
            module_type_name="tf_classification_xception_config",
            module_constructor="XceptionConfig",
            package_name="mlcvzoo_tf_classification.xception.configuration",
        )

        self._config_registry.register_external_module(
            module_type_name="tf_classification_custom_block_config",
            module_constructor="CustomBlockConfig",
            package_name="mlcvzoo_tf_classification.custom_block.configuration",
        )

        self._config_registry.register_external_module(
            module_type_name="mmocr_config",
            module_constructor="MMOCRConfig",
            package_name="mlcvzoo_mmocr.configuration",
        )

        self._config_registry.register_external_module(
            module_type_name="mmdet_config",
            module_constructor="MMDetectionConfig",
            package_name="mlcvzoo_mmdetection.configuration",
        )
        self._config_registry.register_external_module(
            module_type_name="darknet_config",
            module_constructor="DarknetConfig",
            package_name="mlcvzoo_darknet.configuration",
        )

        # =================================================
        # Fill ModelRegistry
        self.register_model(
            model_type_name="read_from_file_classification",
            model_constructor=ReadFromFileClassificationModel,
        )
        self.register_model(
            model_type_name="read_from_file_object_detection",
            model_constructor=ReadFromFileObjectDetectionModel,
        )
        self.register_model(
            model_type_name="read_from_file_segmentation",
            model_constructor=ReadFromFileSegmentationModel,
        )
        self.register_external_model(
            model_type_name="yolox",
            model_constructor="YOLOXModel",
            package_name="mlcvzoo_yolox.model",
        )
        # TODO: Add deprecation?
        self.register_external_model(
            model_type_name="yolov4_darknet",
            model_constructor="DarknetDetectionModel",
            package_name="mlcvzoo_darknet.model",
        )
        self.register_external_model(
            model_type_name="darknet_object_detection",
            model_constructor="DarknetDetectionModel",
            package_name="mlcvzoo_darknet.model",
        )
        self.register_external_model(
            model_type_name="mmdetection_object_detection",
            model_constructor="MMObjectDetectionModel",
            package_name="mlcvzoo_mmdetection.object_detection_model",
        )
        self.register_external_model(
            model_type_name="mmocr_text_detection",
            model_constructor="MMOCRTextDetectionModel",
            package_name="mlcvzoo_mmocr.text_detection_model",
        )
        self.register_external_model(
            model_type_name="mmocr_text_recognition",
            model_constructor="MMOCRTextRecognitionModel",
            package_name="mlcvzoo_mmocr.text_recognition_model",
        )
        self.register_external_model(
            model_type_name="tf_classification_custom_block",
            model_constructor="CustomBlockModel",
            package_name="mlcvzoo_tf_classification.custom_block.model",
        )
        self.register_external_model(
            model_type_name="tf_classification_xception",
            model_constructor="XceptionModel",
            package_name="mlcvzoo_tf_classification.xception.model",
        )

        self._model_to_config_dict: Dict[str, str] = {
            "read_from_file_classification": "read_from_file_config",
            "read_from_file_object_detection": "read_from_file_config",
            "read_from_file_segmentation": "read_from_file_config",
            "yolox": "yolox_config",
            "yolov4_darknet": "darknet_config",
            "darknet_object_detection": "darknet_config",
            "mmdetection_object_detection": "mmdet_config",
            "mmocr_text_detection": "mmocr_config",
            "mmocr_text_recognition": "mmocr_config",
            "tf_classification_custom_block": "tf_classification_custom_block_config",
            "tf_classification_xception": "tf_classification_xception_config",
        }

    @property
    def model_registry(
        self,
    ) -> Dict[str, Type[Model[PredictionType, ConfigurationType, DataType]]]:
        return self._registry

    @property
    def config_registry(self) -> Dict[str, Type[BaseConfigClass]]:
        return self._config_registry._registry

    def determine_config_class(self, model_type_name: str) -> Type[BaseConfigClass]:
        return self.config_registry[self._model_to_config_dict[model_type_name]]

    def determine_config_class_name(self, model_type_name: str) -> str:
        return self._model_to_config_dict[model_type_name]

    def register_external_model(
        self, model_type_name: str, model_constructor: str, package_name: str
    ) -> None:
        """
        Register an external model
        Args:
            model_type_name: name of the model to register
            model_constructor: name of the constructor of the model to register
            package_name: the full package to import to call the constructor

        Returns:
            Nothing
        """
        self.register_external_module(
            module_type_name=model_type_name,
            module_constructor=model_constructor,
            package_name=package_name,
        )

    def get_registered_models(
        self,
    ) -> Dict[str, Type[Model[PredictionType, ConfigurationType, DataType]]]:
        return copy.deepcopy(self._registry)

    def get_model_type(
        self, class_type: str
    ) -> Optional[Type[Model[PredictionType, ConfigurationType, DataType]]]:
        if class_type in self._registry:
            return self._registry[class_type]

        return None

    def register_model(
        self, model_type_name: str, model_constructor: Any, force: bool = False
    ) -> None:
        self.register_module(
            module_type_name=model_type_name, module_constructor=model_constructor, force=force
        )

    def init_model(
        self,
        model_config: ModelConfig,
        string_replacement_map: Optional[Dict[str, str]] = None,
    ) -> Model[PredictionType, ConfigurationType, DataType]:
        """
        Generic method for instantiating any model that is registered in the model-registry

        Args:
            model_config: The model configuration defining which model should be initialized
            string_replacement_map: (Optional) A dictionary that defines placeholders which can
                                    be used while parsing a configuration file. They can be
                                    understood as variables that can be used to define configs
                                    that are valid across multiple devices.

                                    If no string_replacement_map a default map based on the
                                    ReplacementConfig will be created and used. This allows
                                    to use the attributes of the ReplacementConfig to be
                                    replaced by os environment variables.

        Returns:
            The created model instance
        """

        model_type = self.get_model_type(class_type=model_config.class_type)
        if model_type is not None:
            model: Model[PredictionType, ConfigurationType, DataType]

            init_params: List[Any] = list(inspect.getfullargspec(model_type.__init__).args)
            # We don't need self as parameter in the configuration
            init_params.remove("self")

            if (
                STRING_REPLACEMENT_MAP_KEY not in model_config.constructor_parameters
                and STRING_REPLACEMENT_MAP_KEY in init_params
            ):
                if string_replacement_map is None:
                    string_replacement_map = ReplacementConfig().to_dict()
                model_config.constructor_parameters[
                    STRING_REPLACEMENT_MAP_KEY
                ] = string_replacement_map

            try:
                model = model_type(**model_config.constructor_parameters)  # type: ignore[arg-type]
            except TypeError as e:
                logger.error(
                    "Please provide the parameters " "%s, as specified for %s",
                    init_params,
                    model_type,
                )
                raise e
        else:
            message = (
                f"The model '{model_config.class_type}' is not registered! \n"
                f"The registered models are: {self._registry.keys()}"
            )

            logger.error(message)
            raise ValueError(message)

        return model
