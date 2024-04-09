# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""
Module for configuring the visualization of model outputs
"""

import related
from attr import define
from config_builder import BaseConfigClass


@define
class VisualizationConfig(BaseConfigClass):
    """Class for parsing information for visualization"""

    show_image: bool = related.BooleanField(default=True)
    font_path: str = related.StringField(default="")
    output_shape: int = related.IntegerField(default=500)
