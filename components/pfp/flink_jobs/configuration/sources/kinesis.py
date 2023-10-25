from enum import Enum
from typing import Optional

from pydantic import Field, root_validator

from pfp.flink_jobs.configuration.schema_registry import SchemaRegistryConfig
from pfp.flink_jobs.configuration.sources.core import BaseSourceConfig


class KinesisStreamInitPosition(Enum):
    TRIM_HORIZON: str = "TRIM_HORIZON"
    # todo: add support for this option in KinesisSourceConfig
    # AT_TIMESTAMP: str = "AT_TIMESTAMP"
    LATEST: str = "LATEST"


class KinesisRecordPublisherType(Enum):
    EFO: str = "EFO"
    POLLING: str = "POLLING"


class KinesisSourceConfig(BaseSourceConfig):
    stream_name: str = Field(
        default=...,
        description="The name of the Kinesis stream to read from"
    )
    aws_region: str = Field(
        default=...,
        description="The AWS region in which the Kinesis stream is defined"
    )
    stream_init_pos: KinesisStreamInitPosition = Field(
        default=...,
        description="The initial position in the Kinesis stream to read from"
    )
    record_publisher_type: Optional[KinesisRecordPublisherType] = Field(
        default=None,
        description="Determines whether to use EFO or POLLING. The default RecordPublisher is POLLING."
    )
    efo_consumer_name: Optional[str] = Field(
        default=None,
        description="A name to identify the consumer. For a given Kinesis data stream, each consumer must have a "
                    "unique name. However, consumer names do not have to be unique across data streams. Reusing a "
                    "consumer name will result in existing subscriptions being terminated."
    )

    @root_validator(pre=True)
    def validate_publish_mode(cls, values: dict):
        record_publisher_type = values.get("record_publisher_type")
        efo_consumer_name = values.get("efo_consumer_name")
        if record_publisher_type == KinesisRecordPublisherType.EFO and efo_consumer_name is None:
            raise ValueError("record_publisher_type is set to EFO but efo_consumer_name is not set. Please provide a "
                             "value for efo_consumer_name.")
        if record_publisher_type == KinesisRecordPublisherType.POLLING and efo_consumer_name is not None:
            raise ValueError(f"record_publisher_type is set to POLLING but efo_consumer_name is set to "
                             f"{efo_consumer_name}. Please remove efo_consumer_name option.")
        if record_publisher_type is None and efo_consumer_name is not None:
            raise ValueError(f"record_publisher_type is not set but efo_consumer_name is set to "
                             f"{efo_consumer_name}. Please remove efo_consumer_name option.")
        return values


    class Config:
        use_enum_values = True
        allow_population_by_field_name = True


class KinesisAvroSourceConfig(KinesisSourceConfig):
    schema_registry_config: SchemaRegistryConfig = Field(
        default=...,
        description="Configuration for the schema registry from where to fetch the Avro schema"
    )


