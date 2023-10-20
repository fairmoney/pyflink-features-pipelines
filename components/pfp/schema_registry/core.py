from abc import ABCMeta, ABC, abstractmethod
from typing import Union
from importlib.abc import Traversable
import json
import fastavro


class SchemaRegistryClient(ABC):

    @abstractmethod
    def fetch_avro_schema(self, address: Union[str, Traversable]) -> dict:
        """
        Loads an Avro schema given its name (for remote schema registries implementations), or its path (for local
        schema registry implementation).
        :param address: The name, arn or path to the avsc file describing the avro schema
        :return: a dictionary with the contents of the avro schema
        """

    def fetch_avro_schema_string(self, address: Union[str, Traversable]) -> str:
        """
        Loads an Avro schema string given its name (for remote schema registries implementations), or its path (for local
        schema registry implementation).
        :param address: The name, arn or path to the avsc file describing the avro schema
        :return: a dictionary with the contents of the avro schema
        """
        return json.dumps(self.fetch_avro_schema(address=address))


class LocalSchemaRegistryClient(SchemaRegistryClient):

    _local_folder_path: str

    def fetch_avro_schema(self, address: str) -> dict:
        if isinstance(address, Traversable):
            with address.open("r") as f:
                return fastavro.parse_schema(json.load(f))
        elif isinstance(address, str):
            with open(address, "r") as f:
                return fastavro.parse_schema(json.load(f))
        else:
            raise Exception("schema_path should be either string or Traversable")


class AwsGlueSchemaRegistryClient(SchemaRegistryClient):

    def fetch_avro_schema(self, address: Union[str, Traversable]) -> dict:
        raise NotImplementedError("AwsGlueSchemaRegistryClient is not yet implemented")


class AivenKafkaSchemaRegistryClient(SchemaRegistryClient):

    def fetch_avro_schema(self, address: Union[str, Traversable]) -> dict:
        raise NotImplementedError("AivenKafkaSchemaRegistryClient is not yet implemented")
