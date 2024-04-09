# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""Module for enumerating options of formats"""
from enum import Enum

from mlcvzoo_base.configuration.structs import BaseType


class CSVOutputStringFormats(BaseType):
    BASE = "BASE"
    YOLO = "YOLO"


class MOTChallengeFormats(Enum):
    MOT15 = "mot15"
    MOT1617 = "mot1617"
    MOT20 = "mot20"
