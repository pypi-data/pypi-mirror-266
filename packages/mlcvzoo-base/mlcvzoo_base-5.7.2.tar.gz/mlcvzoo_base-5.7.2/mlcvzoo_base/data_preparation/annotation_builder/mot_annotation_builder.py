# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""Module for building MOT formatted annotations."""
import logging
from typing import Dict, List, Tuple

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.annotation_builder import AnnotationBuilder
from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper
from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.api.data.box import Box
from mlcvzoo_base.api.data.class_identifier import ClassIdentifier
from mlcvzoo_base.api.exceptions import ClassMappingNotFoundError
from mlcvzoo_base.configuration.structs import ObjectDetectionBBoxFormats
from mlcvzoo_base.data_preparation.structs import MOTChallengeFormats
from mlcvzoo_base.data_preparation.utils import ensure_abspath

logger = logging.getLogger(__name__)


class MOTAnnotationBuilder(AnnotationBuilder):
    """
    Class for defining the methods that are needed to build a BaseAnnotation
    object from an MOT annotation file (.txt).

    REMARK: The MOT Challenge only considers BoundingBoxes.
    """

    def __init__(
        self,
        image_shape: Tuple[int, int],  # HEIGHT, WIDTH
        image_id: int,
        annotation_line_dict: Dict[int, List[str]],
        mapper: AnnotationClassMapper,
        mot_class_mapper: AnnotationClassMapper,
        mot_format: str,
        ground_truth: bool,
    ) -> None:
        AnnotationBuilder.__init__(self)

        self.image_shape = image_shape
        self.image_id = image_id
        self.annotation_line_dict = annotation_line_dict
        self.mapper = mapper
        self.mot_class_mapper = mot_class_mapper
        self.mot_format = mot_format
        self.ground_truth = ground_truth

    def build(
        self,
        image_path: str,
        annotation_path: str,
        image_dir: str,
        annotation_dir: str,
        replacement_string: str,
    ) -> BaseAnnotation:
        """
        Build an annotation from the given annotation lines of the annotation_line_dict
        attribute, which have been extracted form an MOT annotation file.

        Args:
            image_path: String, points to an annotated image
            annotation_path: String, points to the respective annotation
            image_dir: String, points to the dir where the annotated image is stored
            annotation_dir: String, points to the dir where the respective annotation is stored
            replacement_string: String, part of the paths that is a placeholder

        Returns:
            A BaseAnnotation object
        """

        bounding_boxes = self.__parse_bounding_boxes()

        annotation: BaseAnnotation = BaseAnnotation(
            image_path=image_path,
            annotation_path=annotation_path,
            image_shape=self.image_shape,
            classifications=[],
            bounding_boxes=bounding_boxes,
            image_dir=image_dir,
            annotation_dir=annotation_dir,
            replacement_string=replacement_string,
        )

        annotation = ensure_abspath(annotation=annotation)

        try:
            AnnotationBuilder._check_annotation(annotation=annotation)
        except ValueError as value_error:
            logger.exception(
                "%s, in a future version, the whole annotation will be skipped!", value_error
            )

        return annotation

    def __parse_bounding_boxes(
        self,
    ) -> List[BoundingBox]:
        """
        Parse bounding boxes from all annotation lines that are associated with the
        image-id attribute ob this MOTAnnotationBuilder instance.

        Format for MOT2015 is:
        <frame>, <id>, <bb_left>, <bb_top>, <bb_width>, <bb_height>, <conf>, <3D-X>, <3D-Y>, <3D-Z>

        Format for MOT201617 and MOT2020 is:
        <frame>, <id>, <bb_left>, <bb_top>, <bb_width>, <bb_height>, <conf>, <class>, <visibility>

        Explanation of fields, from the respective papers:
        - frame: Number of the frame in the image sequence
        - id: bounding box ID in a trajectory
        - confidence score: in ground truth data handled as a flag (0/1) for consideration of boxed
        - 3D world coordinates: describe the position of a pedestrian's feet, "in the case of
                                2D tracking, these values will be ignored and can be left at -1"
        - class id: introduced in MOT201617, before only pedestrians were considered
        - visibility: indicates the degree of visibility of an object

        Note from the instruction page at https://motchallenge.net/instructions/ :
        "All frame numbers, target IDs and bounding boxes are 1-based"

        REMARK: <id> field is not used in object detection tasks. In case you want to
                pursue tracking this functionality needs to be added.

        Details about the annotation format can be found here:

        Documentation regarding the MOT challenge submission format:
        https://motchallenge.net/instructions/

        The format for the MOT challenge 2015:
        https://arxiv.org/pdf/1504.01942.pdf (section 3.4 "Data Format")

        The format for the MOT challenge 2016:
        https://arxiv.org/pdf/1603.00831.pdf (section 3.4 "Data Format")

        Returns:
            A list of BoundingBox objects for image of the MOTAnnotationBuilder instance

        Raises:
            ClassMappingNotFoundError: when the class_name can not be mapped to a model class
            name.
        """

        bounding_boxes: List[BoundingBox] = []

        if self.image_id not in self.annotation_line_dict:
            return bounding_boxes

        for mot_annotation_line in self.annotation_line_dict[self.image_id]:
            # Note: annotation is given in a .txt file where each line equals to one bounding box.
            # These lines are contained in self.mot_annotations as a list of strings.
            # So each line has to be read out, split along the ",", filtered by image_id
            # and the corresponding bounding box values parsed to integer values.
            mot_annotation_elements = mot_annotation_line.split(",")

            # The mot class mapping is static. Therefore, first translate the given
            # class-id to a mot class-name and then map this class-name to the according
            # class-id and class-name of the model.
            if self.mot_format == MOTChallengeFormats.MOT15.value:
                mot_class_id = 1
            else:
                mot_class_id = int(mot_annotation_elements[7])

            mot_class_name = self.mot_class_mapper.map_annotation_class_id_to_model_class_name(
                class_id=mot_class_id
            )

            try:
                class_id = self.mapper.map_annotation_class_name_to_model_class_id(
                    class_name=mot_class_name
                )
                class_name = self.mapper.map_annotation_class_name_to_model_class_name(
                    class_name=mot_class_name
                )
            except ClassMappingNotFoundError:
                logger.debug(
                    "Could not find a valid class-mapping for class-name '%s'. "
                    "BndBox will be skipped, mot-line= '%s'",
                    mot_class_name,
                    mot_annotation_line,
                )
                continue

            # Note:
            #  - in GT data "confidence score" indicates whether an entry is considered for
            #    training
            #  - Whereas in pre-annotated data it indicates how confident the detector was
            #    that this instance is of the specified class [1,100]
            score = float(mot_annotation_elements[6])
            if self.ground_truth and score == 0.0:
                # Skip annotation line if mot annotation file contains ground truth data.
                # Then score value serves as flag for considering an annotation during
                # training (1=yes) or not (0=no).
                continue

            bounding_boxes.append(
                BoundingBox(
                    class_identifier=ClassIdentifier(
                        class_id=class_id,
                        class_name=class_name,
                    ),
                    score=score,
                    difficult=False,
                    occluded=False,
                    content="",
                    box=Box.init_format_based(  # NOTE: MOT bbox is format XYWH
                        box_list=(
                            int(float(mot_annotation_elements[2])),
                            int(float(mot_annotation_elements[3])),
                            int(float(mot_annotation_elements[4])),
                            int(float(mot_annotation_elements[5])),
                        ),
                        box_format=ObjectDetectionBBoxFormats.XYWH,
                        src_shape=self.image_shape,
                    ),
                )
            )
        return bounding_boxes
