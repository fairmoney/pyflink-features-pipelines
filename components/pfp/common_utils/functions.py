import importlib
import inspect
from dataclasses import dataclass, field
from typing import Callable, Optional
from inspect import FullArgSpec


@dataclass
class FlinkJobTransformationSpec:

    _python_module: str = field(metadata={"doc": "The fully qualified name of the python module hosting the function"})
    _function_name: str = field(metadata={"doc": "The name of the Python function within its module"})
    _function: Optional[Callable] = field(default=None, metadata={"doc": "The loaded python function"})

    _datastream_str_type: str = "<class 'pyflink.datastream.data_stream.DataStream'>"

    def __init__(self, python_module: str, function_name: str):
        self._python_module = python_module
        self._function_name = function_name

    @property
    def function(self) -> Callable:
        if self._function is None:
            self._load_function()
        return self._function

    @staticmethod
    def from_fully_qualified_function_address(fn_address: str) -> 'FlinkJobTransformationSpec':
        (*module_args, function_name) = fn_address.split(".")
        module = ".".join(module_args)
        return FlinkJobTransformationSpec(
            python_module=module,
            function_name=function_name
        )

    def _load_function(self):
        module = importlib.import_module(name=self._python_module)
        function = getattr(module, self._function_name)
        self._function = function

    @property
    def arg_specs(self) -> FullArgSpec:
        if self.function is None:
            raise Exception("Function has not been loaded properly")
        return inspect.getfullargspec(self._function)

    def validate(self, expected_input_names: list[str]) -> None:
        full_arg_specs: FullArgSpec = self.arg_specs
        try:
            annotations = full_arg_specs.annotations
        except AttributeError:
            raise Exception(f"No annotations found for function {self._function_name}, please define your function "
                            f"with annotated types for inputs and output")
        try:
            output_type = annotations.pop("return")
        except KeyError:
            raise Exception(f"Output type for function {self._function_name} is not annotated, please add the "
                            f"output type using python annotations")
        if not str(output_type) == self._datastream_str_type:
            raise Exception(f"Output type for transformation {self._function_name} should be "
                            f"pyflink.datastream.data_stream.DataStream")
        for input_name, input_type in annotations.items():
            if not str(input_type) == self._datastream_str_type:
                raise Exception(f"Type for {self._function_name} input {input_name} should be "
                                f"pyflink.datastream.data_stream.DataStream")
            if not input_name in expected_input_names:
                raise Exception(f"Cannot find argument '{input_name}' in expected inputs {expected_input_names}")


