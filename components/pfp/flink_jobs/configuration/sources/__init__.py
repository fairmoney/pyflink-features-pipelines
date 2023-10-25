from typing import Union

from pfp.flink_jobs.configuration.sources.kinesis import KinesisSourceConfig, KinesisAvroSourceConfig

SourceConfig = Union[
    KinesisAvroSourceConfig,
    KinesisSourceConfig
]

__all__ = [
    "KinesisAvroSourceConfig",
    "KinesisSourceConfig",
    "SourceConfig"
]