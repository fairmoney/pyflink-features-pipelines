from pfp.flink_jobs.builder.sources.core import FlinkJobSourceBuilder
from pfp.flink_jobs.builder.sources.kinesis import FlinkJobKinesisAvroSourceBuilder
from pfp.flink_jobs.configuration.sources import SourceConfig, KinesisAvroSourceConfig


def get_source_builder(config: SourceConfig) -> FlinkJobSourceBuilder:
    if isinstance(config, KinesisAvroSourceConfig):
        return FlinkJobKinesisAvroSourceBuilder(config=config)
    else:
        raise NotImplementedError(f"No builder found for source config of type {type(config)}")


__all__ = [
    "FlinkJobSourceBuilder",
    "get_source_builder"
]
