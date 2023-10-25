from pfp.flink_jobs.builder.sinks.core import FlinkJobSinkBuilder
from pfp.flink_jobs.builder.sinks.kinesis import FlinkJobKinesisSinkBuilder
from pfp.flink_jobs.configuration.sinks import KinesisSinkConfig, SinkConfig


def get_sink_builder(config: SinkConfig) -> FlinkJobSinkBuilder:
    if isinstance(config, KinesisSinkConfig):
        return FlinkJobKinesisSinkBuilder(config=config)
    else:
        raise NotImplementedError(f"No builder found for source config of type {type(config)}")


__all__ = [
    "FlinkJobSinkBuilder",
    "get_sink_builder"
]
