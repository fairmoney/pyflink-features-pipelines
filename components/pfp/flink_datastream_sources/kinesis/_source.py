from pyflink.datastream.connectors.kinesis import FlinkKinesisConsumer
from pyflink.datastream.functions import SourceFunction
from pyflink.datastream.formats.avro import AvroRowDeserializationSchema

from pfp.flink_datastream_sources.kinesis._config import KinesisSourceConfig


def read_from_kinesis_avro(
        stream_name: str,
        deserializer: AvroRowDeserializationSchema,
        config: KinesisSourceConfig
) -> SourceFunction:
    consumer_config_props: dict = config.dict(exclude_none=True, by_alias=True, exclude_unset=True)
    return FlinkKinesisConsumer(
        streams=stream_name,
        deserializer=deserializer,
        config_props=consumer_config_props
    )
