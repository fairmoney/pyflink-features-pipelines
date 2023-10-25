from typing import Union, Any
from pfp.flink_jobs.configuration.sinks.kinesis import KinesisSinkConfig

SinkConfig = Union[
    KinesisSinkConfig
]

__all__ = [
    "SinkConfig",
    "KinesisSinkConfig"
]