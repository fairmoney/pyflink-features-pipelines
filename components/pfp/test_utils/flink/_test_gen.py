import importlib

from typing import Any, Optional

from pydantic import BaseModel, Field


class InputSpec(BaseModel):
    arg_name: str = Field(
        default=...,
        description="The name of the argument in the transformation to be tested"
    )
    values: list[Any] = Field(
        default=...,
        description="The values to be passed to the transformation to be tested"
    )


class OutputSpec(BaseModel):
    values: list[Any] = Field(
        default=...,
        description="The expected outputs from the transformation to be tested"
    )


class PythonFunctionSpec(BaseModel):
    module: str = Field(
        default=...,
        description="The python module holding the function"
    )
    function_name: str = Field(
        default=...,
        description="The name of the python function within its parent module"
    )


class TransformationFunctionIntegrationTestCaseSpec(BaseModel):
    description: str = Field(
        default=...,
        description="A description of what this test achieves"
    )
    input_spec: list[InputSpec] = Field(
        default=...,
        description="The specifications for inputs to be passed to the transformation being tested"
    )
    output_spec: OutputSpec = Field(
        default=...,
        description="The expected outputs from the transformation being tested"
    )


class TransformationFunctionIntegrationTestSuiteSpec(BaseModel):
    description: Optional[str] = Field(
        default=None,
        description="The high level description of the test suite. If not provided, a high level description will be "
                    "inferred from the tested transformation function"
    )
    transformation_function: str = Field(
        default=...,
        description="The fully qualified name of the transformation function to be tested, including namespace"
    )
    test_cases_specs: list[TransformationFunctionIntegrationTestCaseSpec] = Field(
        default=...,
        description="List of integration tests cases for the transformation being tested"
    )

    @property
    def transformation_pyfunction_specs(self) -> PythonFunctionSpec:
        (*module_args, function_name) = self.transformation_function.split(".")
        module = ".".join(module_args)
        return PythonFunctionSpec(
            module=module,
            function_name=function_name
        )


def generate_transform_tests(test_specs: TransformationFunctionIntegrationTestSuiteSpec):
    transformation_pyfunction_specs: PythonFunctionSpec = test_specs.transformation_pyfunction_specs
    transformation_module = importlib.import_module(name=transformation_pyfunction_specs.module)
    transformation_fn = getattr(transformation_module, transformation_pyfunction_specs.function_name)

    def _set_test_cases(cls):
        for i, spec in enumerate(test_specs.test_cases_specs):
            test_id: int = i + 1
            test_fn_name = f"test_{transformation_fn.__name__}_{test_id}"
            _test_fn = cls._build_test_case(transformation_fn, spec)
            _test_fn.__doc__ = spec.description
            setattr(cls, test_fn_name, _test_fn)
        suite_description = test_specs.description if test_specs.description is not None else f"{transformation_fn.__name__} tests suite"
        setattr(cls, "__doc__", suite_description)
        return cls

    return _set_test_cases


def generate_transform_tests_from_spec_file(file_path: str):
    tests_specs: TransformationFunctionIntegrationTestSuiteSpec = TransformationFunctionIntegrationTestSuiteSpec \
        .parse_file(file_path)
    return generate_transform_tests(test_specs=tests_specs)