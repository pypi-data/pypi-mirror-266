# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

from typing import Optional

import related
from attr import define
from config_builder import BaseConfigClass

from mlcvzoo_base.configuration.structs import DeviceQueryTypes


@define
class ModelTimerDeviceQueryConfig(BaseConfigClass):
    device_index: Optional[int] = related.ChildField(cls=int)
    query_type: str = related.StringField()

    def check_values(self) -> bool:
        return (
            self.device_index is None
            or isinstance(self.device_index, int)
            and self.query_type in [d.value.upper() for d in DeviceQueryTypes]
        )
