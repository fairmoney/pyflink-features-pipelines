import importlib
from typing import Optional, Callable

from pyflink.datastream import DataStream
from pyflink.testing.test_case_utils import PyFlinkUTTestCase

from pfp.test_utils.pipelines.specs import TransformationFunctionIntegrationTestCaseSpec, \
    TransformationFunctionIntegrationTestSuiteSpec, PythonFunctionSpec


class PyFlinkDataStreamUTTestCase(PyFlinkUTTestCase):

    def assertUnsortedDataStreamEqual(self, ds_1: DataStream, ds_2: DataStream, message: Optional[str] = None):
        ds_1_values = list(sorted(ds_1.execute_and_collect()))
        ds_2_values = list(sorted(ds_2.execute_and_collect()))
        self.assertListEqual(ds_1_values, ds_2_values, message)


class PyFlinkDataStreamTransformationTestCase(PyFlinkDataStreamUTTestCase):

    def _build_transformation_inputs_kwargs(self, spec) -> dict[str, DataStream]:
        results = {}
        for inputs_spec in spec.input_spec:
            data_stream = self.env.from_collection(inputs_spec.values)
            results[inputs_spec.arg_name] = data_stream
        return results

    @staticmethod
    def _build_test_case(test_transform: Callable, spec: TransformationFunctionIntegrationTestCaseSpec):
        def _exec_transform_test(self):
            inputs_kwargs = self._build_transformation_inputs_kwargs(spec)
            outputs = test_transform(**inputs_kwargs)
            self.assertUnsortedDataStreamEqual(outputs, self.env.from_collection(spec.output_spec.values))
        return _exec_transform_test


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
    tests_specs: TransformationFunctionIntegrationTestSuiteSpec = TransformationFunctionIntegrationTestSuiteSpec\
        .parse_file(file_path)
    return generate_transform_tests(test_specs=tests_specs)
