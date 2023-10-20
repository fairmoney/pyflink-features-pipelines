import importlib
from typing import Optional, Callable

from pyflink.datastream import DataStream
from pyflink.testing.test_case_utils import PyFlinkUTTestCase

from pfp.test_utils.flink._test_gen import TransformationFunctionIntegrationTestCaseSpec


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



