from abc import ABC, abstractmethod
from typing import Union

from pydantic import BaseModel, Field


class BaseSchemaRegistryConfig(ABC):

    @property
    @abstractmethod
    def schema_address(self) -> str:
        pass


class LocalSchemaRegistryConfig(BaseSchemaRegistryConfig, BaseModel):
    avro_file_path: str = Field(
        default=...,
        description="The local path of the avsc file defining the Avro schema"
    )

    @property
    def schema_address(self) -> str:
        return self.avro_file_path


class AwsGlueAvroSchemaRegistryConfig(BaseSchemaRegistryConfig, BaseModel):
    schema_arn: str = Field(
        default=...,
        description="The ARN of the schema to be fetched from Glue schema registry"
    )
    schema_version_id: str = Field(
        default=...,
        description="The id of the schema's version to fetch"
    )

    @property
    def schema_address(self) -> str:
        return self.schema_arn


SchemaRegistryConfig = Union[
    LocalSchemaRegistryConfig,
    AwsGlueAvroSchemaRegistryConfig
]
