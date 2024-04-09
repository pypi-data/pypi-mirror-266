# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""Module for building Pascal VOC formatted annotations."""
import logging
import os
import xml.etree.ElementTree as ET_xml
from typing import Any, List, Tuple

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.annotation_builder import AnnotationBuilder
from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper
from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.api.data.box import Box
from mlcvzoo_base.api.data.class_identifier import ClassIdentifier
from mlcvzoo_base.api.exceptions import ClassMappingNotFoundError
from mlcvzoo_base.configuration.structs import ObjectDetectionBBoxFormats
from mlcvzoo_base.configuration.utils import str2bool
from mlcvzoo_base.data_preparation.utils import ensure_abspath

logger = logging.getLogger(__name__)


class PascalVOCAnnotationBuilder(AnnotationBuilder):
    """
    Super class for defining the methods that are needed to build a BaseAnnotation
    object from a Pascal VOC type XML file.
    """

    def __init__(
        self,
        mapper: AnnotationClassMapper,
        use_difficult: bool = True,
        use_occluded: bool = True,
        use_background: bool = True,
    ) -> None:
        AnnotationBuilder.__init__(self)

        self.mapper = mapper
        self.use_difficult = use_difficult
        self.use_occluded = use_occluded
        self.use_background = use_background

    def build(
        self,
        image_path: str,
        annotation_path: str,
        image_dir: str,
        annotation_dir: str,
        replacement_string: str,
    ) -> BaseAnnotation:
        (
            annotation_path,
            image_shape,
            bounding_boxes,
            source_image_filename,
        ) = self.__init_from_pascal_voc_xml(xml_file_path=annotation_path)

        if not os.path.isfile(image_path):
            image_path = source_image_filename

        annotation: BaseAnnotation = BaseAnnotation(
            image_path=image_path,
            annotation_path=annotation_path,
            image_shape=image_shape,
            classifications=[],
            bounding_boxes=bounding_boxes,
            segmentations=[],
            image_dir=image_dir,
            annotation_dir=annotation_dir,
            replacement_string=replacement_string,
        )

        try:
            AnnotationBuilder._check_annotation(annotation=annotation)
        except ValueError as value_error:
            logger.exception(
                f"{value_error}, in a future version, the whole annotation will be skipped!"
            )

        annotation = ensure_abspath(annotation=annotation)

        return annotation

    def __init_from_pascal_voc_xml(
        self,
        xml_file_path: str,
    ) -> Tuple[str, Tuple[int, int], List[BoundingBox], str]:
        """
        Parses and generates objects that are needed to build a BaseAnnotation

        Args:
            xml_file_path: Can either be a string to a XML-File or a File-Object of a XML-File
                in VOC-Format

        Returns: the given xml_file_path,
                the shape of the annotated image,
                a list of annotated bounding_boxes and
                the file path of the image, if available in xml file

        """

        bounding_boxes: List[BoundingBox] = list()

        tree = ET_xml.parse(xml_file_path)

        root = tree.getroot()

        width = int(root.find("size").find("width").text)  # type: ignore
        height = int(root.find("size").find("height").text)  # type: ignore
        image_shape = (height, width)

        source_image_filename = ""
        if root.find("path") is not None:
            source_image_filename = (
                root.find("path").text if root.find("path").text is not None else ""  # type: ignore
            )

        for element in root.findall("object"):
            annotation_class_name: str = element[0].text  # type: ignore

            try:
                # map the parsed "class_name" according to the mapping defined in the mapper class
                class_name = self.mapper.map_annotation_class_name_to_model_class_name(
                    class_name=annotation_class_name
                )

                class_id = self.mapper.map_annotation_class_name_to_model_class_id(
                    class_name=annotation_class_name
                )
            except ClassMappingNotFoundError:
                logger.debug(
                    "Could not find a valid class-mapping for class-name '%s'. "
                    "BndBox will be skipped, file = '%s'",
                    annotation_class_name,
                    xml_file_path,
                )
                continue

            box_tag = element.find("bndbox")

            if box_tag is None:
                continue

            difficult, occluded = self.__parse_default_attributes(element=element)
            background, content = self.__parse_attributes(element=element)

            bounding_box = BoundingBox(
                box=Box.init_format_based(
                    box_list=(
                        int(float(str(box_tag[0].text))),
                        int(float(str(box_tag[1].text))),
                        int(float(str(box_tag[2].text))),
                        int(float(str(box_tag[3].text))),
                    ),
                    box_format=ObjectDetectionBBoxFormats.XYXY,
                    src_shape=image_shape,
                ),
                class_identifier=ClassIdentifier(class_id=class_id, class_name=class_name),
                model_class_identifier=ClassIdentifier(class_id=class_id, class_name=class_name),
                difficult=difficult,
                background=background,
                occluded=occluded,
                content=content,
                score=1.0,
            )

            if difficult and not self.use_difficult:
                continue

            if occluded and not self.use_occluded:
                continue

            if background and not self.use_background:
                continue

            bounding_boxes.append(bounding_box)

        return xml_file_path, image_shape, bounding_boxes, source_image_filename

    @staticmethod
    def __parse_default_attributes(element: ET_xml.Element) -> Tuple[bool, bool]:
        difficult = False
        difficult_tag = element.find("difficult")
        if difficult_tag is not None and difficult_tag.text is not None:
            difficult = str2bool(difficult_tag.text)

        occluded = False
        occluded_tag = element.find("occluded")
        if occluded_tag is not None and occluded_tag.text is not None:
            occluded = str2bool(occluded_tag.text)

        return difficult, occluded

    @staticmethod
    def __parse_attributes(element: ET_xml.Element) -> Tuple[bool, str]:
        background = False
        content = ""
        attributes_tag = element.find("attributes")
        if attributes_tag is None:
            return background, content

        for attribute in attributes_tag:
            _attribute_name = attribute.find("name")

            if _attribute_name is not None:
                if _attribute_name.text == "background":
                    background = str2bool(
                        PascalVOCAnnotationBuilder.__parse_attribute_value(
                            attribute_element=attribute, default=False
                        )
                    )
                if _attribute_name.text == "content":
                    content = PascalVOCAnnotationBuilder.__parse_attribute_value(
                        attribute_element=attribute, default=""
                    )

        return background, content

    @staticmethod
    def __parse_attribute_value(attribute_element: ET_xml.Element, default: Any) -> Any:
        _attribute_value_element = attribute_element.find("value")
        if _attribute_value_element is not None:
            _attribute_value = _attribute_value_element.text

            if _attribute_value is not None:
                return _attribute_value

        return default
