from typing import Union

from pyflink.datastream import SourceFunction
from pyflink.datastream.connectors import Source
from pyflink.datastream.connectors.kinesis import FlinkKinesisConsumer
from pyflink.datastream.formats.avro import AvroRowDeserializationSchema

from pfp.flink_jobs.builder.schema_registry import fetch_avro_schema
from pfp.flink_jobs.builder.sources.core import FlinkJobSourceBuilder
from pfp.flink_jobs.configuration.sources import SourceConfig


class FlinkJobKinesisAvroSourceBuilder(FlinkJobSourceBuilder):

    def __init__(self, config: SourceConfig):
        super().__init__(config)

    def build(self) -> Union[Source, SourceFunction]:
        consumer_config: dict = {
            "aws.region": self.config.aws_region,
            "flink.stream.initpos": self.config.stream_init_pos
        }
        if self.config.record_publisher_type is not None and self.config.efo_consumer_name is not None:
            consumer_config.update({
                "flink.stream.recordpublisher": self.config.record_publisher_type.value,
                "flink.stream.efo.consumername": self.config.efo_consumer_name
            })
        avro_schema_str: str = fetch_avro_schema(config=self.config.schema_registry_config)
        deserializer = AvroRowDeserializationSchema(avro_schema_string=avro_schema_str)
        return FlinkKinesisConsumer(
            streams=self.config.stream_name,
            deserializer=deserializer,
            config_props=consumer_config
        )