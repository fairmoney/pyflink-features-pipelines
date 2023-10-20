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


