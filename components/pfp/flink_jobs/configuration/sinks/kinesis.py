from typing import Optional

from pydantic import Field

from pfp.flink_jobs.configuration.schema_registry import SchemaRegistryConfig
from pfp.flink_jobs.configuration.sinks.core import BaseSinkConfig


class KinesisSinkConfig(BaseSinkConfig):
    stream_name: str = Field(
        description="The name of the Kinesis stream to emit results to",
    )
    aws_region: str = Field(
        default=...,
        description="The AWS region in which the output stream is defined"
    )
    aws_endpoint: Optional[str] = Field(
        default=...,
        description="AN optional endpoint to be used by the aws client"
    )
    fail_on_error: Optional[bool] = Field(
        default=None,
        description="If set to true, the job will fail if en error is encountered while emitting records to the sink"
    )
    schema_registry_config: Optional[SchemaRegistryConfig] = Field(
        default=None,
        description="Optional configuration for the schema registry from where to fetch the Avro schema. If set, a "
                    "schema registry client will be created to fetch the corresponding Avro schema from the registry"
    )
