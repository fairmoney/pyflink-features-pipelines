import boto3
from pfp.flink_jobs.configuration.schema_registry import SchemaRegistryConfig, LocalSchemaRegistryConfig, \
    AwsGlueAvroSchemaRegistryConfig
from pfp.schema_registry.core import AwsGlueSchemaRegistryClient, LocalSchemaRegistryClient


def fetch_avro_schema(config: SchemaRegistryConfig) -> str:
    if type(config) == AwsGlueAvroSchemaRegistryConfig:
        return AwsGlueSchemaRegistryClient(boto3_client=boto3.client("glue"))\
            .fetch_avro_schema_string(
                address=config.schema_address,
                version=config.schema_version_id
            )
    elif type(config) == LocalSchemaRegistryConfig:
        return LocalSchemaRegistryClient()\
            .fetch_avro_schema_string(
                address=config.schema_address,
                version=None
            )
    else:
        raise NotImplementedError(f"No implementation for {type(config)} schema registry")
