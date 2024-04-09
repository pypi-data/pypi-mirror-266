# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""
Module for storing types that are shared across the mlcvzoo
"""
from typing import Literal

import numpy as np
from numpy.typing import NDArray
from typing_extensions import Annotated

ImageType = Annotated[NDArray[np.int_], Literal["Height", "Width", 3]]
