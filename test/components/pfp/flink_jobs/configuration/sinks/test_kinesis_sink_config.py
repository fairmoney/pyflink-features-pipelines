import os
import unittest
import tempfile
import json

from pfp.flink_jobs.configuration import LocalSchemaRegistryConfig, AwsGlueAvroSchemaRegistryConfig
from pfp.flink_jobs.configuration.sinks.kinesis import *
import itertools


class KinesisSinkConfigTestCases(unittest.TestCase):
    """
    KinesisSinkConfig
    """

    def test_should_serialize_and_deserialize(self):
        """
        should successfully serialise configuration objects to json and deserialize them back to objects
        """
        local_schema_registry_config = LocalSchemaRegistryConfig(avro_file_path="test_path")
        glue_schema_registry_config = AwsGlueAvroSchemaRegistryConfig(
            schema_arn="test_schema_arn",
            schema_version_id=1
        )
        aws_endpoint_options = ["test_endpoint", None]
        fail_on_error_options = [True, False, None]
        schema_registry_config_options = [None, local_schema_registry_config, glue_schema_registry_config]

        with tempfile.TemporaryDirectory() as d:
            for i, v in enumerate(itertools.product(aws_endpoint_options, fail_on_error_options, schema_registry_config_options)):
                target_file_name: str = os.path.join(d, f"sink_config_{i}.json")
                config: KinesisSinkConfig = KinesisSinkConfig(
                    sink_name="test_sink",
                    sink_description="A test sink",
                    stream_name="test_stream",
                    aws_region="test_region",
                    aws_endpoint=v[0],
                    fail_on_error=v[1],
                    schema_registry_config=v[2]
                )
                with open(target_file_name, "w") as out_file:
                    json.dump(config.dict(), out_file)
                deserialized_config = KinesisSinkConfig.parse_file(target_file_name)
                self.assertEqual(deserialized_config, config, f"Difference in deserialized config for sample {i}: "
                                                              f"{deserialized_config} | {config}")






