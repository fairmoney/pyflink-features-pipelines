from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class KinesisStreamInitPosition(Enum):
    TRIM_HORIZON: str = "TRIM_HORIZON"
    AT_TIMESTAMP: str = "AT_TIMESTAMP"
    LATEST: str = "LATEST"


class KinesisRecordPublisherType(Enum):
    EFO: str = "EFO"
    POLLING: str = "POLLING"


class KinesisSourceConfig(BaseModel):
    aws_region: str = Field(
        default=...,
        description="The AWS region in which the Kinesis stream is defined",
        alias="aws.region"
    )
    stream_init_pos: KinesisStreamInitPosition = Field(
        default=...,
        description="The initial position in the Kinesis stream to read from",
        alias="flink.stream.initpos"
    )
    record_publisher_type: Optional[KinesisRecordPublisherType] = Field(
        default=KinesisRecordPublisherType.POLLING,
        description="Determines whether to use EFO or POLLING. The default RecordPublisher is POLLING.",
        alias="flink.stream.recordpublisher"
    )
    efo_consumer_name: Optional[str] = Field(
        default=None,
        description="A name to identify the consumer. For a given Kinesis data stream, each consumer must have a "
                    "unique name. However, consumer names do not have to be unique across data streams. Reusing a "
                    "consumer name will result in existing subscriptions being terminated.",
        alias="flink.stream.efo.consumername"
    )

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True


