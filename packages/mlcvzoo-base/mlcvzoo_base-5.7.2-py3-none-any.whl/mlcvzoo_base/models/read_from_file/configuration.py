# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""
Module for configuring the parsing of information from yaml in python
accessible attributes for the ReadFromFileModel class
"""
from typing import Optional

import related
from attr import define

from mlcvzoo_base.api.configuration import ModelConfiguration
from mlcvzoo_base.configuration.annotation_handler_config import AnnotationHandlerConfig
from mlcvzoo_base.configuration.class_mapping_config import ClassMappingConfig
from mlcvzoo_base.configuration.reduction_mapping_config import ReductionMappingConfig


@define
class ReadFromFileConfig(ModelConfiguration):
    """
    Class for parsing information from yaml in respective hierarchy

    Attributes:
        class_mapping (ClassMappingConfig):
        annotation_handler_config:
        use_image_name_hash:
        include_segmentations:
        reduction_class_mapping:
    """

    class_mapping: ClassMappingConfig = related.ChildField(ClassMappingConfig)

    annotation_handler_config: AnnotationHandlerConfig = related.ChildField(
        cls=AnnotationHandlerConfig
    )

    use_image_name_hash: bool = related.BooleanField(default=False)

    include_segmentations: bool = related.BooleanField(default=False)

    reduction_class_mapping: Optional[ReductionMappingConfig] = related.ChildField(
        cls=ReductionMappingConfig, required=False, default=None
    )
