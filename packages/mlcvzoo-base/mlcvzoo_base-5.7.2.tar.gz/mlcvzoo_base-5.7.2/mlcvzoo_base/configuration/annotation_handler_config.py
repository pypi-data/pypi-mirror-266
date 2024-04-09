# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""
Module for parsing information from yaml in python accessible attributes for the
AnnotationHandler class.
"""
import logging
import os
from typing import List, Optional

import related
from attr import define
from config_builder import BaseConfigClass

from mlcvzoo_base.configuration.class_mapping_config import ClassMappingConfig
from mlcvzoo_base.configuration.reduction_mapping_config import ReductionMappingConfig
from mlcvzoo_base.data_preparation.structs import (
    CSVOutputStringFormats,
    MOTChallengeFormats,
)

logger = logging.getLogger(__name__)


@define
class AnnotationHandlerPASCALVOCInputDataConfig(BaseConfigClass):
    """Class for parsing information of PASCAL VOC input format"""

    __related_strict__ = True

    input_image_dir: str = related.StringField()
    input_xml_dir: str = related.StringField()
    input_sub_dirs: List[str] = related.SequenceField(str)

    image_format: str = related.StringField()
    use_difficult: bool = related.BooleanField(default=True)
    ignore_missing_images: bool = related.BooleanField(default=False)
    use_occluded: bool = related.BooleanField(default=True)
    use_background: bool = related.BooleanField(default=True)


@define
class AnnotationHandlerMOTInputDataConfig(BaseConfigClass):
    """Class for parsing MOT information of input data"""

    __related_strict__ = True

    # Path to the annotation file
    annotation_path: str = related.StringField()
    # Root directory which fits to the relative directory in the given annotation file
    image_dir: str = related.StringField()
    # considered image file format
    image_format: str = related.StringField(required=False, default=".jpg")
    # specifies which format of which challenge/year should be used
    mot_format: str = related.StringField(required=False, default=MOTChallengeFormats.MOT20.value)
    # specifies how to interpret confidence scores in annotations
    ground_truth: bool = related.BooleanField(required=False, default=True)
    # path to the files where the MOT labels are specified
    label_path: Optional[str] = related.ChildField(cls=str, required=False, default=None)

    def check_values(self) -> bool:
        return self.mot_format in [f.value for f in MOTChallengeFormats]


@define
class AnnotationHandlerLabelStudioInputDataConfig(BaseConfigClass):
    """Class for parsing information of input data"""

    input_image_dir: str = related.StringField()
    input_annotation_dir: str = related.StringField()

    image_format: str = related.StringField()
    # TODO: don't set defaults here?
    # TODO: Implement functionality
    use_difficult: bool = related.BooleanField(default=True)
    ignore_missing_images: bool = related.BooleanField(default=False)


@define
class AnnotationHandlerSingleFileInputDataConfig(BaseConfigClass):
    """Class for parsing information of input data"""

    __related_strict__ = True

    # Path to the annotation file
    input_path: str = related.StringField()
    # Root directory which fits to the relative directory in the given annotation file
    # TODO: Optional?
    input_root_dir: str = related.StringField()

    # TODO: don't set defaults here?
    use_difficult: bool = related.BooleanField(default=True)
    use_occluded: bool = related.BooleanField(default=True)
    use_background: bool = related.BooleanField(default=True)


@define
class AnnotationHandlerWriteOutputCSVAnnotationConfig(BaseConfigClass):
    """Class for parsing information of output format when writing CSV annotations"""

    __related_strict__ = True

    csv_dir: str = related.StringField()
    csv_base_file_name: str = related.StringField(default="")

    csv_split_0_file_name: str = related.StringField(default="")
    csv_split_1_file_name: str = related.StringField(default="")

    # TODO: add hint for file-name replacement? Add specific config class?
    timestamp_format: str = related.StringField(default="%Y-%m-%d")
    include_surrounding_bboxes: bool = related.BooleanField(default=True)
    output_string_format: str = related.StringField(default=CSVOutputStringFormats.BASE)

    def check_values(self) -> bool:
        if not os.path.isdir(self.csv_dir):
            # Note: this is not necessarily required or
            #       already existing when config is read (see test)
            logger.info("Class='%s', specify correct output_dir'%s'", type(self), self.csv_dir)

        return self.output_string_format in CSVOutputStringFormats.get_values_as_list(
            class_type=CSVOutputStringFormats
        )


@define
class AnnotationHandlerWriteOutputDarknetAnnotationConfig(BaseConfigClass):
    """Class for parsing information of output format when writing Darknet annotations"""

    __related_strict__ = True

    train_data_set_dir: str = related.StringField()
    base_file_name: str = related.StringField(default="")
    write_as_symlink: bool = related.BooleanField(default=False)

    def get_train_file_path(self) -> str:
        return os.path.join(self.train_data_set_dir, f"{self.base_file_name}_train.txt")

    def get_test_file_path(self) -> str:
        return os.path.join(self.train_data_set_dir, f"{self.base_file_name}_test.txt")


@define
class AnnotationHandlerWriteOutputBoxSnippetsConfig(BaseConfigClass):
    """Class for parsing information of output directory when writing annotations"""

    __related_strict__ = True

    output_dir: str = related.StringField()


@define
class AnnotationHandlerWriteOutputConfig(BaseConfigClass):
    """Class for parsing information of output format when writing annotations"""

    __related_strict__ = True

    use_cross_val: bool = related.BooleanField()
    number_splits: int = related.IntegerField()
    split_size: int = related.FloatField()

    csv_annotation: Optional[AnnotationHandlerWriteOutputCSVAnnotationConfig] = related.ChildField(
        cls=AnnotationHandlerWriteOutputCSVAnnotationConfig,
        required=False,
        default=None,
    )

    darknet_train_set: Optional[
        AnnotationHandlerWriteOutputDarknetAnnotationConfig
    ] = related.ChildField(
        cls=AnnotationHandlerWriteOutputDarknetAnnotationConfig,
        required=False,
        default=None,
    )
    darknet_annotation: AnnotationHandlerWriteOutputDarknetAnnotationConfig = related.ChildField(
        cls=AnnotationHandlerWriteOutputDarknetAnnotationConfig,
        required=False,
        default=None,
    )
    use_difficult: bool = related.BooleanField(default=True)
    use_occluded: bool = related.BooleanField(default=True)

    bbox_snippets: Optional[AnnotationHandlerWriteOutputBoxSnippetsConfig] = related.ChildField(
        AnnotationHandlerWriteOutputBoxSnippetsConfig, required=False, default=None
    )

    random_state: Optional[int] = related.ChildField(cls=int, default=None, required=False)


@define
class AnnotationHandlerConfig(BaseConfigClass):
    """Class for parsing information from yaml in respective hierarchy"""

    __related_strict__ = True

    class_mapping: Optional[ClassMappingConfig] = related.ChildField(
        cls=ClassMappingConfig, required=False, default=None
    )

    pascal_voc_input_data: List[AnnotationHandlerPASCALVOCInputDataConfig] = related.SequenceField(
        AnnotationHandlerPASCALVOCInputDataConfig, default=[]
    )

    coco_input_data: List[AnnotationHandlerSingleFileInputDataConfig] = related.SequenceField(
        AnnotationHandlerSingleFileInputDataConfig, default=[]
    )

    cvat_input_data: List[AnnotationHandlerSingleFileInputDataConfig] = related.SequenceField(
        AnnotationHandlerSingleFileInputDataConfig, default=[]
    )

    label_studio_input_data: List[
        AnnotationHandlerLabelStudioInputDataConfig
    ] = related.SequenceField(AnnotationHandlerLabelStudioInputDataConfig, default=[])

    write_output: Optional[AnnotationHandlerWriteOutputConfig] = related.ChildField(
        AnnotationHandlerWriteOutputConfig, required=False, default=None
    )

    reduction_class_mapping: Optional[ReductionMappingConfig] = related.ChildField(
        cls=ReductionMappingConfig, required=False, default=None
    )

    mot_input_data: List[AnnotationHandlerMOTInputDataConfig] = related.SequenceField(
        AnnotationHandlerMOTInputDataConfig, default=[]
    )
