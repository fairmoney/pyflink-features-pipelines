import os

from pfp.test_utils.core import run_slow_tests
from pfp.test_utils.flink import generate_transform_tests_from_spec_file, PyFlinkDataStreamTransformationTestCase


def full_test_file_path(file_name: str) -> str:
    return f"{os.getcwd()}/test/bases/pfp/sample_flink_transformations/test_files/{file_name}"


@generate_transform_tests_from_spec_file(file_path=full_test_file_path("add_one_specs.json"))
class AddOneTransformationITTesCase(PyFlinkDataStreamTransformationTestCase):

    def setUp(self) -> None:
        if not run_slow_tests():
            self.skipTest(reason="Skip slow tests")
        super().setUp()

    def tearDown(self) -> None:
        if not run_slow_tests():
            self.skipTest(reason="Skip slow tests")
        super().tearDown()


@generate_transform_tests_from_spec_file(file_path=full_test_file_path("add_one_withmapfunction_specs.json"))
class AddOneWithMapFunctionTransformationITTesCase(PyFlinkDataStreamTransformationTestCase):

    def setUp(self) -> None:
        if not run_slow_tests():
            self.skipTest(reason="Skip slow tests")
        super().setUp()

    def tearDown(self) -> None:
        if not run_slow_tests():
            self.skipTest(reason="Skip slow tests")
        super().tearDown()
