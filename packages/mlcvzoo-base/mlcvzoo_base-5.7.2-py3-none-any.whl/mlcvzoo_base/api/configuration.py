# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""Module for configuring machine learning models"""

from abc import ABC
from typing import Optional

import related
from attr import define
from config_builder import BaseConfigClass


@define
class ModelConfiguration(BaseConfigClass, ABC):
    """
    A model configuration.
    Typically, subclasses of a configuration parser implement
    this class to provide a mechanism to feed parameters into models or training.
    """

    unique_name: str = related.StringField()


@define
class InferenceConfig(BaseConfigClass):
    """
    Overall inference config that defines parameters that
    are valid for every model that is performing an inference.
    """

    config_path: Optional[str] = related.ChildField(cls=str)
    checkpoint_path: str = related.StringField()
    score_threshold: float = related.FloatField()
