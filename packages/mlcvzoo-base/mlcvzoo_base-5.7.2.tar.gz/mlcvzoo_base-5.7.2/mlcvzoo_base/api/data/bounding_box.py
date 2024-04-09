# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

""" Class for Bounding Box Annotation"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from mlcvzoo_base.api.data.annotation_attributes import AnnotationAttributes
from mlcvzoo_base.api.data.box import Box
from mlcvzoo_base.api.data.class_identifier import ClassIdentifier
from mlcvzoo_base.api.data.classification import Classification


class BoundingBox(AnnotationAttributes, Classification):
    """
    A class for defining the data object consumed by ObjectDetection models.
    It is mainly described by the box attribute, which covers an rectangular
    area of an image and is associated with a certain class
    """

    def __init__(
        self,
        box: Box,
        class_identifier: ClassIdentifier,
        score: float,
        difficult: bool = False,
        occluded: bool = False,
        content: str = "",
        model_class_identifier: Optional[ClassIdentifier] = None,
        background: bool = False,
    ):
        Classification.__init__(
            self,
            class_identifier=class_identifier,
            model_class_identifier=model_class_identifier,
            score=score,
        )
        AnnotationAttributes.__init__(
            self, difficult=difficult, occluded=occluded, content=content, background=background
        )
        self.__box = box

    def to_dict(self, raw_type: bool = False, reduced: bool = False) -> Dict[str, Any]:
        if reduced:
            return {
                "box": self.box if raw_type else self.box.to_dict(),
                "class_id": self.class_id,
                "class_name": self.class_name,
                "model_class_id": self.model_class_identifier.class_id,
                "model_class_name": self.model_class_identifier.class_name,
                "score": self.score,
            }
        else:
            return {
                "box": self.box if raw_type else self.box.to_dict(),
                "class_identifier": (
                    self.class_identifier if raw_type else self.class_identifier.to_dict()
                ),
                "model_class_identifier": (
                    self.model_class_identifier
                    if raw_type
                    else self.model_class_identifier.to_dict()
                ),
                "score": self.score,
                "difficult": self.difficult,
                "occluded": self.occluded,
                "background": self.background,
                "content": self.content,
            }

    @staticmethod
    def from_dict(input_dict: Dict[str, Any], reduced: bool = False) -> BoundingBox:
        # fmt: off
        if reduced:
            return BoundingBox(**{
                "box": Box(**input_dict["box"]),
                "class_identifier": ClassIdentifier(**{
                    "class_id": input_dict["class_id"],
                    "class_name": input_dict["class_name"],
                }),
                "model_class_identifier": ClassIdentifier(**{
                    "class_id": input_dict["model_class_id"],
                    "class_name": input_dict["model_class_name"],
                }),
                "score": input_dict["score"],
                "difficult": False,
                "occluded": False,
                "background": False,
                "content": "",
            })
        else:
            return BoundingBox(**{
                "box": Box(**input_dict["box"]),
                "class_identifier": ClassIdentifier(
                    **input_dict["class_identifier"]
                ),
                "model_class_identifier": ClassIdentifier(
                    **input_dict["model_class_identifier"]
                ),
                "score": input_dict["score"],
                "difficult": input_dict["difficult"],
                "occluded": input_dict["occluded"],
                "background": input_dict["background"],
                "content": input_dict["content"],
            })
        # fmt: on

    def to_json(self) -> Any:
        return self.to_dict(raw_type=False)

    @property
    def box(self) -> Box:
        return self.__box

    def __eq__(self, other: BoundingBox):  # type: ignore
        # NOTE: Since floats may very for different systems, don't check the score for equality,
        #       but allow it to be in a reasonable range
        return (
            self.box == other.box
            and self.class_identifier.class_id == other.class_identifier.class_id
            and self.class_identifier.class_name == other.class_identifier.class_name
            and self.model_class_identifier.class_id == other.model_class_identifier.class_id
            and self.model_class_identifier.class_name == other.model_class_identifier.class_name
            and self.occluded == other.occluded
            and self.difficult == other.difficult
            and self.background == other.background
            and self.content == other.content
            and math.isclose(a=self.score, b=other.score, abs_tol=0.005)
        )

    def __repr__(self):  # type: ignore
        return (
            f"BoundingBox: "
            f"class-id={self.class_id}, "
            f"class-name={self.class_name}: "
            f"model-class-id={self.model_class_identifier.class_id}, "
            f"model-class-name={self.model_class_identifier.class_name}: "
            f"Box={self.box}, "
            f"score={self.score}, "
            f"difficult={self.difficult}, "
            f"occluded={self.occluded}, "
            f"background={self.background}, "
            f"content='{self.content}'"
        )

    def to_list(self) -> List[int]:
        """
        Transforms the BoundingBox object to a list of its coordinates.

        Returns:
            A 1x4 list of the objects coordinates [xmin, ymin, xmax, ymax]
        """
        return [self.box.xmin, self.box.ymin, self.box.xmax, self.box.ymax]

    def copy_bounding_box(self, class_identifier: ClassIdentifier) -> BoundingBox:
        return BoundingBox(
            box=self.box,
            class_identifier=class_identifier,
            score=self.score,
            difficult=self.difficult,
            occluded=self.occluded,
            background=self.background,
            content=self.content,
            model_class_identifier=self.model_class_identifier,
        )
