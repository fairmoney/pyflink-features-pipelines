import os
import json
import tempfile
import unittest

from pfp.flink_jobs.configuration import LocalSchemaRegistryConfig, AwsGlueAvroSchemaRegistryConfig


class LocalSchemaRegistryConfigTestCase(unittest.TestCase):
    """
    LocalSchemaRegistryConfig
    """
    test_avro_path = "test_path"

    def test_serde(self):
        """
        should successfully serialise configuration objects to json and deserialize them back to objects
        """
        with tempfile.TemporaryDirectory() as d:
            target_file_name: str = os.path.join(d, "config.json")
            config: LocalSchemaRegistryConfig = LocalSchemaRegistryConfig(avro_file_path=self.test_avro_path)
            with open(target_file_name, "w") as out_file:
                json.dump(config.dict(), out_file)
            deserialized_config = LocalSchemaRegistryConfig.parse_file(target_file_name)
            self.assertEqual(deserialized_config, config, f"Difference in deserialized config: "
                                                          f"{deserialized_config} | {config}")

    def test_address_should_return_correct_value(self):
        """
        should have `schema_address` property return the avro file path
        """
        config: LocalSchemaRegistryConfig = LocalSchemaRegistryConfig(avro_file_path=self.test_avro_path)
        self.assertEqual(config.avro_file_path, config.schema_address)


class AwsGlueSchemaRegistryConfigTestCase(unittest.TestCase):
    """
    AwsGlueAvroSchemaRegistryConfig
    """
    test_schema_arn = "test_arn"
    test_schema_version_id = 1

    def test_serde(self):
        """
        should successfully serialise configuration objects to json and deserialize them back to objects
        """
        with tempfile.TemporaryDirectory() as d:
            target_file_name: str = os.path.join(d, "config.json")
            config: AwsGlueAvroSchemaRegistryConfig = AwsGlueAvroSchemaRegistryConfig(
                schema_arn=self.test_schema_arn,
                schema_version_id=self.test_schema_version_id
            )
            with open(target_file_name, "w") as out_file:
                json.dump(config.dict(), out_file)
            deserialized_config = AwsGlueAvroSchemaRegistryConfig.parse_file(target_file_name)
            self.assertEqual(deserialized_config, config, f"Difference in deserialized config: "
                                                          f"{deserialized_config} | {config}")

    def test_address_should_return_correct_value(self):
        """
        should have `schema_address` property return the schema arn
        """
        config: AwsGlueAvroSchemaRegistryConfig = AwsGlueAvroSchemaRegistryConfig(
            schema_arn=self.test_schema_arn,
            schema_version_id=self.test_schema_version_id
        )
        self.assertEqual(config.schema_arn, config.schema_address)
