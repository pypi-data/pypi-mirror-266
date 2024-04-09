# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

""" Class for Bounding Box information"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import cv2

from mlcvzoo_base.api.data.types import ImageType
from mlcvzoo_base.configuration.structs import ObjectDetectionBBoxFormats

logger = logging.getLogger(__name__)


class Box:
    """
    Class for storing bounding box information.

    Box on an Image:
    |-----------------------|
    |(xmin, ymin)           |
    |                       |
    |                       |
    |                       |
    |                       |
    |                       |
    |           (xmax, ymax)|
    |-----------------------|
    """

    def __init__(self, xmin: int, ymin: int, xmax: int, ymax: int) -> None:
        if xmin >= xmax:
            raise ValueError(f"xmin={xmin} has to be < xmax={xmax}")

        if ymin >= ymax:
            raise ValueError(f"ymin={ymin} has to be < ymax={ymax}")

        # top left x coordinate
        self.__xmin: int = xmin
        # top left y coordinate
        self.__ymin: int = ymin
        # lover right x coordinate
        self.__xmax: int = xmax
        # lower right y coordinate
        self.__ymax: int = ymax

        self._center: Tuple[float, float] = self.__center()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Box):
            return (
                self.xmin == other.xmin
                and self.ymin == other.ymin
                and self.xmax == other.xmax
                and self.ymax == other.ymax
            )

        return False

    def __repr__(self):  # type: ignore
        return (
            f"Box("
            f"xmin={self.__xmin}, ymin={self.__ymin}, xmax={self.__xmax}, ymax={self.__ymax}"
            f")"
        )

    def to_dict(self) -> Dict[str, int]:
        return {
            "xmin": self.xmin,
            "ymin": self.ymin,
            "xmax": self.xmax,
            "ymax": self.ymax,
        }

    def to_json(self) -> Any:
        return self.to_dict()

    @property
    def xmin(self) -> int:
        return self.__xmin

    @property
    def ymin(self) -> int:
        return self.__ymin

    @property
    def xmax(self) -> int:
        return self.__xmax

    @property
    def ymax(self) -> int:
        return self.__ymax

    @property
    def width(self) -> int:
        return self.__xmax - self.__xmin

    @property
    def height(self) -> int:
        return self.__ymax - self.__ymin

    @staticmethod
    def init_format_based(
        box_format: str,
        box_list: Tuple[int, int, int, int],
        src_shape: Optional[Tuple[int, int]] = None,
        dst_shape: Optional[Tuple[int, int]] = None,
    ) -> Box:
        """
        Additional Constructor

        Args:
            box_format: specify the way for parsing the box argument
            box_list: object as 4D array containing bounding box information
            src_shape: shape of the original image as tuple (height, width)
            dst_shape: desired shape for creating the bounding boxes as tuple (height, width)

        Returns:
            A Box object
        """

        xmin = box_list[0]
        if xmin < 0:
            xmin = max(0, xmin)

        ymin = box_list[1]
        if ymin < 0:
            ymin = max(0, ymin)

        if box_format == ObjectDetectionBBoxFormats.XYWH:
            width = box_list[2]
            if width < 0:
                raise ValueError("Can not build a box with negative width")

            height = box_list[3]
            if height < 0:
                raise ValueError("Can not build a box with negative height")

            base_box = Box(
                xmin=int(xmin),
                ymin=int(ymin),
                xmax=int(xmin + width),
                ymax=int(ymin + height),
            )
        elif box_format == ObjectDetectionBBoxFormats.XYXY:
            base_box = Box(
                xmin=int(xmin),
                ymin=int(ymin),
                xmax=int(box_list[2]),
                ymax=int(box_list[3]),
            )
        else:
            valid_formats = ObjectDetectionBBoxFormats.get_values_as_list(
                class_type=ObjectDetectionBBoxFormats
            )
            raise ValueError(
                f"Format {box_format} is not supported. Please provide any of {valid_formats}"
            )

        if src_shape is not None:
            base_box.clamp(shape=src_shape)

        if src_shape is not None and dst_shape is not None:
            base_box.scale(src_shape=src_shape, dst_shape=dst_shape)

        return base_box

    def to_list(self, dst_type: Any = int) -> List[Any]:
        """
        Args:
            dst_type: destination type to transform the data to

        Returns:
            List of transformed polygons
        """

        return [
            dst_type(self.xmin),
            dst_type(self.ymin),
            dst_type(self.xmax),
            dst_type(self.ymax),
        ]

    def clamp(self, shape: Tuple[int, int]) -> None:
        """
        Clamps the bounding-box based on the given shape

        Args:
            shape: The shape to define the min and max coordinates
                   for the clamping, format in (y, x)

        Returns:
            None
        """
        self.__xmin = int(max(0, self.__xmin))
        self.__ymin = int(max(0, self.__ymin))

        self.__ymax = int(min(shape[0] - 1, self.__ymax))
        self.__xmax = int(min(shape[1] - 1, self.__xmax))

        self._center = self.__center()

    def scale(self, src_shape: Tuple[int, int], dst_shape: Tuple[int, int]) -> None:
        """
        Scale the Box according to the given shapes of the source and destination image

        Args:
            src_shape: shape of the original image as tuple (height, width)
            dst_shape: desired shape for creating the bounding boxes as tuple (height, width)

        Returns:
            None
        """
        if src_shape[0] < 0 or src_shape[1] < 0 or src_shape[0] > src_shape[1]:
            raise ValueError("Invalid source shape %s: ", src_shape)

        if dst_shape[0] < 0 or dst_shape[1] < 0 or dst_shape[0] > dst_shape[1]:
            raise ValueError("Invalid destination shape %s: ", dst_shape)

        height_scale_factor = dst_shape[0] / src_shape[0]
        width_scale_factor = dst_shape[1] / src_shape[1]

        self.__xmin = int(self.xmin * width_scale_factor)
        self.__xmax = int(self.xmax * width_scale_factor)

        self.__ymin = int(self.ymin * height_scale_factor)
        self.__ymax = int(self.ymax * height_scale_factor)

        self._center = self.__center()

    def as_array(self) -> List[int]:
        """
        Transforms the Box object to a list of coordinates

        Returns:
            A List of coordinates in the order [xmin, ymin, xmax, ymax]
        """
        return [self.xmin, self.ymin, self.xmax, self.ymax]

    def center(self) -> Tuple[float, float]:
        """
        Calculates the center coordinates of the Box

        Returns:
            A Tuple as the coordinates of the center
        """
        return self._center

    def __center(self) -> Tuple[float, float]:
        """
        Calculates the center coordinates of the Box

        Returns:
            A Tuple as the coordinates of the center
        """
        return (
            self.xmin + (self.xmax - self.xmin) * 0.5,
            self.ymin + (self.ymax - self.ymin) * 0.5,
        )

    def translation(self, x: int, y: int) -> None:
        """
        Shifts Box for x and y pixels in x and y direction respectively

        Args:
            x: int value for shift in x direction
            y: int value for shift in y direction

        Returns:
            None
        """
        self.__xmin += x
        self.__xmax += x
        self.__ymin += y
        self.__ymax += y

        self._center = self.__center()

    def new_center(self, x: int, y: int) -> None:
        """
        Shifts the Box based on a new center coordinate. Scale of Box is kept.

        Args:
            x: int value, x coordinate of the new center
            y: int value, y coordinate of the new center

        Returns:
            None
        """
        width = self.xmax - self.xmin
        height = self.ymax - self.ymin

        self.__xmin = round(x - width / 2)
        self.__xmax = round(x + width / 2)
        self.__ymin = round(y - height / 2)
        self.__ymax = round(y + height / 2)

        self._center = self.__center()

    def crop_img(
        self, frame: ImageType, margin_x: float = 0.0, margin_y: float = 0.0
    ) -> Optional[ImageType]:
        """
        Create a crop of the given frame based on the information of this box object
        and the given margins. The margin are used as scale factors based on the
        width (x direction) and height (y-direction)

        Args:
            frame: The frame to crop from
            margin_x: The margin around the box in x direction
            margin_y: The margin around the box in y direction

        Returns:
            The cropped image (if it could be computed)
        """

        if frame is None:
            return None

        xmin = int(self.xmin - int(round(margin_x * (self.xmax - self.xmin))))
        xmax = int(self.xmax + int(round(margin_x * (self.xmax - self.xmin))))
        ymin = int(self.ymin - int(round(margin_y * (self.ymax - self.ymin))))
        ymax = int(self.ymax + int(round(margin_y * (self.ymax - self.ymin))))

        margin_box = Box(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)
        margin_box.clamp(shape=(frame.shape[0], frame.shape[1]))

        cropped_image = frame[margin_box.ymin : margin_box.ymax, margin_box.xmin : margin_box.xmax]

        return cropped_image

    def color_hist(
        self,
        frame: ImageType,
        margin_x: float,
        margin_y: float,
    ) -> Optional[ImageType]:
        """
        Calculate the color history the for the Box. First a crop
        of the given image is created based on the box information
        of this object and the given margins. The margin are used
        as scale factors based on the width (x direction) and height
        (y-direction)Afterwards the histogram is computed for this crop.

        Args:
            frame: The frame to crop from
            margin_x: The margin around the box in x direction
            margin_y: The margin around the box in y direction

        Returns:
            Color histogram of the box
        """

        cropped_image = self.crop_img(frame=frame, margin_x=margin_x, margin_y=margin_y)

        if cropped_image is None:
            return None

        # Convert image to HSV (Hue, Saturation, Value)
        hsv_image: ImageType = cv2.cvtColor(  # pylint: disable=no-member
            cropped_image, cv2.COLOR_BGR2HSV  # pylint: disable=no-member
        )

        h_bins = 10
        s_bins = 10

        # hue varies from 0 to 179, saturation from 0 to 255
        h_ranges = [0, 180]
        s_ranges = [0, 256]

        # Use the 0-th and 1-st channels
        channels = [0, 1]
        color_hist: ImageType = cv2.calcHist(
            [hsv_image],
            channels,
            None,
            [h_bins, s_bins],
            h_ranges + s_ranges,
            accumulate=False,
        )
        cv2.normalize(color_hist, color_hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

        return color_hist


def compute_iou(box_1: Box, box_2: Box) -> float:
    """
    Determine the Intersection-over-Union (IoU) of two box objects

    Args:
        box_1: Box object 1
        box_2: Box object 2

    Returns:
        The IoU between box_1 and box_2
    """

    # Determine the coordinates of the intersection rectangle
    x_left = max(box_1.xmin, box_2.xmin)
    x_right = min(box_1.xmax, box_2.xmax)
    y_bottom = min(box_1.ymax, box_2.ymax)
    y_top = max(box_1.ymin, box_2.ymin)

    # Boxes don't overlap at all
    if x_right < x_left or y_bottom < y_top:
        return 0.0

    # The intersection of two axis-aligned bounding boxes
    # is always an axis-aligned bounding box => A(intersect)
    intersection_area = (x_right - x_left) * (y_bottom - y_top)

    # Compute the area of both boxes => A(box_1) and A(box_2(
    box_1_area = (box_1.xmax - box_1.xmin) * (box_1.ymax - box_1.ymin)
    box_2_area = (box_2.xmax - box_2.xmin) * (box_2.ymax - box_2.ymin)

    # Compute the intersection over union by taking the intersection
    # area and dividing it by the sum of box areas:
    # => iou = A(intersect) / ( A(box_1) + A(box_2))
    iou = intersection_area / float(box_1_area + box_2_area - intersection_area)

    # Clamp the iou value
    return max(min(iou, 1.0), 0.0)


def euclidean_distance(box_1: Box, box_2: Box) -> float:
    """
    Determine the euclidean distance between two Box objects

    Args:
        box_1: Box object 1
        box_2: Box object 2

    Returns:
        The euclidean distance between two Box objects
    """

    center1 = box_1.center()
    center2 = box_2.center()

    return float(((center2[0] - center1[0]) ** 2 + (center2[1] - center1[1]) ** 2) ** 0.5)
