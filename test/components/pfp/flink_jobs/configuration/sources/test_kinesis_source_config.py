import os
import unittest
import tempfile
import json
from pfp.flink_jobs.configuration.sources.kinesis import *


class KinesisSourceConfigTestCases(unittest.TestCase):
    """
    KinesisSourceConfig
    """
    test_files_folder: str = "test/components/pfp/flink_jobs/configuration/sources/test_config_files"

    def test_should_serialize_and_deserialize(self):
        """
        should successfully serialise configuration objects to json and deserialize them back to objects
        """
        config_values = [
            (KinesisStreamInitPosition.TRIM_HORIZON, None, None),
            (KinesisStreamInitPosition.LATEST, None, None),
            (KinesisStreamInitPosition.TRIM_HORIZON, KinesisRecordPublisherType.POLLING, None),
            (KinesisStreamInitPosition.TRIM_HORIZON, KinesisRecordPublisherType.EFO, "test-consumer-name"),
        ]

        with tempfile.TemporaryDirectory() as d:
            for i, v in enumerate(config_values):
                target_file_name = os.path.join(d, f"test_file_{i}.json")
                config: KinesisSourceConfig = KinesisSourceConfig(
                    source_name="kinesis_source_test_stream",
                    transformation_function_arg_name="test_arg",
                    stream_name="test_stream",
                    aws_region="test_region",
                    stream_init_pos=v[0],
                    record_publisher_type=v[1],
                    efo_consumer_name=v[2]
                )
                with open(target_file_name, "w") as out_file:
                    json.dump(config.dict(), out_file)
                deserialized_config = KinesisSourceConfig.parse_file(target_file_name)
                self.assertEqual(deserialized_config, config, f"Difference in deserialized config for sample {i}: "
                                                              f"{deserialized_config} | {config}")

    def test_validation_should_fail_1(self):
        """
        should fail at validation step if record_publisher_type is set to EFO and efo_consumer_name is not set
        """
        from pydantic import ValidationError
        with self.assertRaises(ValidationError) as context:
            _ = KinesisSourceConfig(
                source_name="kinesis_source_test_stream",
                transformation_function_arg_name="test_arg",
                stream_name="test_stream",
                aws_region="test_region",
                stream_init_pos=KinesisStreamInitPosition.LATEST,
                record_publisher_type=KinesisRecordPublisherType.EFO
            )
            self.assertTrue("record_publisher_type is set to EFO but efo_consumer_name is not set" in context.exception)

    def test_validation_should_fail_2(self):
        """
        should fail at validation step if record_publisher_type is set to POLLING and efo_consumer_name is set
        """
        from pydantic import ValidationError
        with self.assertRaises(ValidationError) as context:
            _ = KinesisSourceConfig(
                source_name="kinesis_source_test_stream",
                transformation_function_arg_name="test_arg",
                stream_name="test_stream",
                aws_region="test_region",
                stream_init_pos=KinesisStreamInitPosition.LATEST,
                record_publisher_type=KinesisRecordPublisherType.POLLING,
                efo_consumer_name="test_consumer"
            )
            self.assertTrue("record_publisher_type is set to POLLING but efo_consumer_name is set" in context.exception)

    def test_validation_should_fail_3(self):
        """
        should fail at validation step if record_publisher_type is not set and efo_consumer_name is set
        """
        from pydantic import ValidationError
        with self.assertRaises(ValidationError) as context:
            _ = KinesisSourceConfig(
                source_name="kinesis_source_test_stream",
                transformation_function_arg_name="test_arg",
                stream_name="test_stream",
                aws_region="test_region",
                stream_init_pos=KinesisStreamInitPosition.LATEST,
                efo_consumer_name="test_consumer"
            )
            self.assertTrue("record_publisher_type is not set but efo_consumer_name is set" in context.exception)




