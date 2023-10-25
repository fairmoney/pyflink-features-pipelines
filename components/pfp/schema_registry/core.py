from abc import ABCMeta, ABC, abstractmethod
from typing import Union, Optional, Any
from importlib.abc import Traversable
import json
import fastavro
import boto3


class SchemaRegistryClient(ABC):

    @abstractmethod
    def fetch_avro_schema_string(
            self,
            address: Union[str, Traversable],
            version: Optional[str]
    ) -> str:
        pass

    def fetch_avro_schema(
            self,
            address: Union[str, Traversable],
            version: Optional[str]
    ) -> dict:
        avro_schema_string: str = self.fetch_avro_schema_string(address=address, version=version)
        return fastavro.parse_schema(json.loads(avro_schema_string))


class LocalSchemaRegistryClient(SchemaRegistryClient):

    def fetch_avro_schema_string(
            self,
            address: str,
            version: Optional[str]
    ) -> str:
        if version is not None:
            raise Exception("Local schema registry does not support schema versioning")
        if isinstance(address, Traversable):
            with address.open("r") as f:
                return f.read()
        elif isinstance(address, str):
            with open(address, "r") as f:
                return f.read()
        else:
            raise Exception("schema_path should be either string or Traversable")


class AwsGlueSchemaRegistryClient(SchemaRegistryClient):

    _client: Any

    def __init__(self, boto3_client: Any):
        self._client = boto3.client("kinesis")

    def fetch_avro_schema_string(
            self,
            address: str,
            version: Optional[str]
    ) -> str:
        raise NotImplementedError("AwsGlueSchemaRegistryClient is not yet implemented")