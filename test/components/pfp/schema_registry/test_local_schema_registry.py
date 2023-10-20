import os
from unittest import TestCase

from pfp.schema_registry.core import LocalSchemaRegistryClient


class LocalSchemaRegistryTestCase(TestCase):

    @staticmethod
    def _load_all_kinesis_schemas_paths() -> list[str]:
        res = []
        base_path: str = "avro/kinesis"
        for sub_folder in os.listdir(base_path):
            for avsc_file_name in os.listdir(f"{base_path}/{sub_folder}"):
                res.append(f"{base_path}/{sub_folder}/{avsc_file_name}")
        return res

    def test_load_all_kinesis_avro_schemas(self):
        client: LocalSchemaRegistryClient = LocalSchemaRegistryClient()
        local_kinesis_schemas_paths: list[str] = self._load_all_kinesis_schemas_paths()
        for p in local_kinesis_schemas_paths:
            schema = client.fetch_avro_schema(address=p)
            self.assertTrue(isinstance(schema, dict))



