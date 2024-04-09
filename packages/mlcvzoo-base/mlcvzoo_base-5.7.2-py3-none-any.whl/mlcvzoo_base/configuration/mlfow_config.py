# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""
Module for parsing information from yaml in python accessible attributes for using mlflow.
"""
from typing import List, Optional

import related
from attr import define
from config_builder import BaseConfigClass


@define
class MLFlowPostgresSQLConfig(BaseConfigClass):
    """Class for parsing information about a SQL sever used for storing experiment information"""

    database_user: str = related.StringField()
    database_pw: str = related.StringField()
    database_port: str = related.StringField(default=5432)
    database_name: str = related.StringField(default="mlflowdb")


@define
class MLFlowFileConfig(BaseConfigClass):
    """Class for parsing information about a directory used for storing experiment information"""

    logging_dir: str = related.StringField()


@define
class MLFlowConfig(BaseConfigClass):
    """
    Class for parsing general information about path handling and also further
    configuration information in respective hierarchy
    """

    artifact_location: str = related.StringField()

    mlflow_postgressql_config: Optional[MLFlowPostgresSQLConfig] = related.ChildField(
        cls=MLFlowPostgresSQLConfig, required=False, default=None
    )

    mlflow_file_config: Optional[MLFlowFileConfig] = related.ChildField(
        cls=MLFlowFileConfig, required=False, default=None
    )

    @property
    def _mutual_attributes(self) -> List[str]:
        return [
            "mlflow_postgressql_config",
            "mlflow_file_config",
        ]
