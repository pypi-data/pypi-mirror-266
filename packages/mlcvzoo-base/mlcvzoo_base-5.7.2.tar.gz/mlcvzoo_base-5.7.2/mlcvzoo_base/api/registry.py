# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""
Module for defining a component that enables to create registries for generic class types
"""

import importlib
import logging
from typing import Dict, Generic, TypeVar

ClassType = TypeVar("ClassType")

logger = logging.getLogger(__name__)


class MLCVZooRegistry(Generic[ClassType]):
    """
    Basis class that enables to create registries for generic class types
    """

    def __init__(self) -> None:
        self._registry: Dict[str, ClassType] = {}

    def register_module(
        self, module_type_name: str, module_constructor: ClassType, force: bool = False
    ) -> None:
        """
        Directly register an module constructor

        Args:
            module_type_name: Name of the model to register
            module_constructor: The reference to the model constructor
            force: Overwrite an existing entry

        Returns:
            None
        """

        if not force and module_type_name in self._registry:
            raise KeyError(
                f"{module_type_name} is already registered model registry" f"in {self._registry}"
            )

        self._registry[module_type_name] = module_constructor

    def register_external_module(
        self, module_type_name: str, module_constructor: str, package_name: str
    ) -> None:
        """
        Register an external model

        Args:
            module_type_name: Name of the model to register
            module_constructor: Name of the constructor of the model to register as string
            package_name: The full package to import to call the constructor

        Returns:
            None
        """
        try:
            # pylint: disable=c0415
            module = importlib.import_module(package_name)
            self.register_module(
                module_type_name=module_type_name,
                module_constructor=module.__dict__[module_constructor],
            )
        except ImportError as error:
            logger.error(
                "Optional module '%s' (%s.%s) not available: %s",
                module_type_name,
                package_name,
                module_constructor,
                error,
            )
        except Exception as error:  # pylint: disable=W0718
            logger.error(
                "Error while registering module '%s' (%s.%s): %s",
                module_type_name,
                package_name,
                module_constructor,
                error,
            )
