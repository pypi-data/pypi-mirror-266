# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""
Module for parsing information from yaml in python accessible attributes for different
configuration classes and also for the ModelRegistry class.
"""

from inspect import getfullargspec
from typing import Any, Dict, List, Optional, Type, Union, cast, get_args

import related
from attr import define
from config_builder import BaseConfigClass

from mlcvzoo_base.configuration.utils import str2bool

INIT_FOR_INFERENCE_PARAMETER = "init_for_inference"


@define
class ModelConfig(BaseConfigClass):
    __related_strict__ = True

    class_type: str = related.StringField()
    constructor_parameters: Dict[
        str, Union[int, bool, str, float, List[Any], Dict[str, Any]]
    ] = related.ChildField(
        cls=dict,
    )

    def update_class_type(self, args_dict: Dict[str, Optional[str]]) -> None:
        if "class_type" in args_dict and args_dict["class_type"] is not None:
            self.class_type = args_dict["class_type"]

    def update_constructor_parameters(
        self, args_dict: Dict[str, Optional[str]], model_type: Type[Any]
    ) -> None:
        model_arg_spec = getfullargspec(model_type.__init__)

        if (
            "constructor_parameters" in args_dict
            and args_dict["constructor_parameters"] is not None
        ):
            constructor_parameters = {}
            for constructor_parameters_dict in args_dict["constructor_parameters"]:
                constructor_parameters.update(cast(Dict[str, Any], constructor_parameters_dict))

            for (
                constructor_parameter_key,
                constructor_parameter_value,
            ) in constructor_parameters.items():
                if constructor_parameter_key in model_arg_spec.annotations.keys():
                    type_arg = model_arg_spec.annotations[constructor_parameter_key]

                    # In case of a "typing.Optional" parameter type, the casting_type
                    # has to be determined by utilizing "typing.get_args"
                    if len(get_args(type_arg)) == 0:
                        casting_type = type_arg
                    else:
                        casting_type = get_args(type_arg)[0]

                    # bool types have to be handled by str2bool
                    if casting_type is bool:
                        self.constructor_parameters[constructor_parameter_key] = str2bool(
                            constructor_parameter_value
                        )
                    else:
                        self.constructor_parameters[constructor_parameter_key] = casting_type(
                            constructor_parameter_value
                        )

    def is_inference(self) -> bool:
        return INIT_FOR_INFERENCE_PARAMETER in self.constructor_parameters

    def set_inference(self, inference: bool) -> None:
        self.constructor_parameters[INIT_FOR_INFERENCE_PARAMETER] = inference
