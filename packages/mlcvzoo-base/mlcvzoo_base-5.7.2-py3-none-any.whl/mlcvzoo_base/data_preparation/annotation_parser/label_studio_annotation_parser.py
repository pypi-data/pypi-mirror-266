# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""Module for parsing Label Studio formatted annotations"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, cast

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper
from mlcvzoo_base.api.data.annotation_parser import AnnotationParser
from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.api.data.box import Box
from mlcvzoo_base.api.data.class_identifier import ClassIdentifier
from mlcvzoo_base.api.exceptions import ClassMappingNotFoundError, ForbiddenClassError
from mlcvzoo_base.configuration.annotation_handler_config import (
    AnnotationHandlerLabelStudioInputDataConfig,
)
from mlcvzoo_base.configuration.structs import ObjectDetectionBBoxFormats
from mlcvzoo_base.utils import get_file_list

logger = logging.getLogger(__name__)


class LabelStudioAnnotationParser(AnnotationParser):
    """
    Parser for the Label Studio json format.

    REMARK:
    For now only Bounding Boxes are supported
    """

    def __init__(
        self,
        mapper: AnnotationClassMapper,
        label_studio_input_data: List[AnnotationHandlerLabelStudioInputDataConfig],
    ):
        AnnotationParser.__init__(self, mapper=mapper)

        self.label_studio_input_data = label_studio_input_data

    @staticmethod
    def __get_label_studio_annotation_dict(
        label_studio_annotation_path: str,
    ) -> Optional[Dict[str, Any]]:
        with open(label_studio_annotation_path, "r") as label_studio_file:
            try:
                return cast(Dict[str, Any], json.load(label_studio_file))
            except json.decoder.JSONDecodeError as json_error:
                logger.exception(
                    msg="Could not parse annotation file '%s'. Annotation will be skipped."
                    % label_studio_annotation_path,
                    exc_info=json_error,
                )

        return None

    def parse(self) -> List[BaseAnnotation]:
        annotations: List[BaseAnnotation] = []

        for dataset_count, input_data in enumerate(self.label_studio_input_data):
            input_image_types = input_data.image_format.split("|")

            input_image_paths: List[str] = []
            for input_image_type in input_image_types:
                input_image_paths.extend(
                    get_file_list(
                        input_dir=input_data.input_image_dir,
                        search_subfolders=True,
                        file_extension=input_image_type,
                    )
                )

            image_file_dict = {os.path.basename(p): p for p in input_image_paths}
            label_studio_annotation_paths = [
                str(p) for p in Path(input_data.input_annotation_dir).glob("**/*")
            ]

            for label_studio_annotation_path in label_studio_annotation_paths:
                label_studio_dict = LabelStudioAnnotationParser.__get_label_studio_annotation_dict(
                    label_studio_annotation_path=label_studio_annotation_path
                )
                if label_studio_dict is None:
                    continue

                try:
                    label_studio_image_name = os.path.basename(
                        label_studio_dict["task"]["data"]["image"]
                    )

                    if label_studio_image_name in image_file_dict:
                        image_path = image_file_dict[label_studio_image_name]
                    else:
                        logger.warning(
                            "Label Studio annotation contains non-existing image: '%s', "
                            "Annotation will be skipped." % label_studio_image_name
                        )
                        continue

                    image_shape: Optional[Tuple[int, int]] = None
                    bounding_boxes: List[BoundingBox] = []
                    for result in label_studio_dict["result"]:
                        if image_shape is None:
                            image_shape = (result["original_height"], result["original_width"])

                        if result["type"] == "rectanglelabels" and image_shape is not None:
                            try:
                                bounding_box: Optional[BoundingBox] = self.__parse_bounding_box(
                                    label_studio_value=result["value"], image_shape=image_shape
                                )
                                if bounding_box is not None:
                                    bounding_boxes.append(bounding_box)

                            except (ValueError, ForbiddenClassError) as error:
                                logger.warning("%s, annotation will be skipped" % str(error))
                                continue

                    if image_shape is not None:
                        annotations.append(
                            BaseAnnotation(
                                image_path=image_path,
                                annotation_path=label_studio_annotation_path,
                                image_shape=image_shape,
                                classifications=[],
                                bounding_boxes=bounding_boxes,
                                segmentations=[],
                                image_dir=os.path.dirname(image_path),
                                annotation_dir=os.path.dirname(label_studio_annotation_path),
                                # TODO: How to set this?
                                replacement_string="",
                            )
                        )
                except KeyError as index_error:
                    logger.exception(
                        msg="Could not parse annotation file '%s'. Annotation will be skipped."
                        % label_studio_annotation_path,
                        exc_info=index_error,
                    )

        return annotations

    def __parse_bounding_box(
        self, label_studio_value: Dict[str, Any], image_shape: Tuple[int, int]
    ) -> Optional[BoundingBox]:
        label_studio_class_name: str = label_studio_value["rectanglelabels"][0]

        try:
            class_name = self.mapper.map_annotation_class_name_to_model_class_name(
                class_name=label_studio_class_name
            )
            class_id = self.mapper.map_annotation_class_name_to_model_class_id(
                class_name=label_studio_class_name
            )

            return BoundingBox(
                class_identifier=ClassIdentifier(
                    class_id=class_id,
                    class_name=class_name,
                ),
                score=1.0,
                difficult=False,
                occluded=False,
                content="",
                box=Box.init_format_based(
                    box_list=(
                        int(image_shape[1] * label_studio_value["x"] / 100),
                        int(image_shape[0] * label_studio_value["y"] / 100),
                        int(image_shape[1] * label_studio_value["width"] / 100),
                        int(image_shape[0] * label_studio_value["height"] / 100),
                    ),
                    box_format=ObjectDetectionBBoxFormats.XYWH,
                ),
            )

        except ClassMappingNotFoundError:
            logger.debug(
                "Could not find a valid class-mapping for class-name '%s'. "
                "BoundingBox will be skipped",
                label_studio_class_name,
            )
            return None
