from abc import ABC, abstractmethod
from typing import Union

from pyflink.datastream import SinkFunction
from pyflink.datastream.connectors import Sink

from pfp.flink_jobs.configuration.sinks import SinkConfig


class FlinkJobSinkBuilder(ABC):

    config: SinkConfig

    def __init__(self, config: SinkConfig):
        self.config = config

    @abstractmethod
    def build(self) -> Union[SinkFunction, Sink]:
        pass
