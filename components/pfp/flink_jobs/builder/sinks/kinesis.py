from typing import Union

from pyflink.datastream import SinkFunction
from pyflink.datastream.connectors import Sink
from pyflink.datastream.connectors.kinesis import KinesisStreamsSink
from pyflink.datastream.formats.avro import AvroRowSerializationSchema

from pfp.flink_jobs.builder.schema_registry import fetch_avro_schema
from pfp.flink_jobs.builder.sinks.core import FlinkJobSinkBuilder
from pfp.flink_jobs.configuration.sinks import SinkConfig


class FlinkJobKinesisSinkBuilder(FlinkJobSinkBuilder):

    def __init__(self, config: SinkConfig):
        super().__init__(config)

    def build(self) -> Union[SinkFunction, Sink]:
        kinesis_client_properties = {
            "aws.region": self.config.aws_region
        }
        if self.config.aws_endpoint is not None:
            kinesis_client_properties.update({"aws.endpoint": self.config.aws_endpoint})
        builder = KinesisStreamsSink \
            .builder() \
            .set_kinesis_client_properties(kinesis_client_properties=kinesis_client_properties) \
            .set_stream_name(stream_name=self.config.stream_name)

        if self.config.fail_on_error is not None:
            builder = builder.set_fail_on_error(fail_on_error=True)

        if self.config.schema_registry_config is not None:
            avro_schema_str: str = fetch_avro_schema(config=self.config.schema_registry_config)
            serializer: AvroRowSerializationSchema = AvroRowSerializationSchema(avro_schema_string=avro_schema_str)
            builder = builder.set_serialization_schema(serialization_schema=serializer)
        return builder.build()
