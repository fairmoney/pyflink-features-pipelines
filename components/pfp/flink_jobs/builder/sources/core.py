from pfp.flink_jobs.configuration.sources import SourceConfig
from typing import Union
from abc import ABC, abstractmethod
from pyflink.datastream import SourceFunction
from pyflink.datastream.connectors import Source


class FlinkJobSourceBuilder(ABC):

    config: SourceConfig

    def __init__(self, config: SourceConfig):
        self.config = config

    @abstractmethod
    def build(self) -> Union[Source, SourceFunction]:
        pass
