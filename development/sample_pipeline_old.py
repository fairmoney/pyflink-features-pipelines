import os

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kinesis import FlinkKinesisConsumer
from pyflink.datastream.formats.avro import AvroRowDeserializationSchema

from pfp.flink_datastream_sources.kinesis import read_from_kinesis_avro, KinesisSourceConfig, KinesisStreamInitPosition
from pfp.schema_registry.core import LocalSchemaRegistryClient


def load_avro_schema(avsc_file_path: str) -> str:
    import json
    with open(avsc_file_path, "r") as avsc_file:
        dict = json.load(avsc_file)
        return json.dumps(dict)


def build_kinesis_source():
    avro_schema_string: str = load_avro_schema("./development/avro/lendmate-application-updated.avsc")
    deserializer = AvroRowDeserializationSchema(avro_schema_string=avro_schema_string)
    return FlinkKinesisConsumer(
        streams=["lendmate-application-updated"],
        deserializer=deserializer,
        config_props={
            "aws.region": "eu-west-1",
            "flink.stream.initpos": "TRIM_HORIZON"
        }
    )


if __name__ == "__main__":
    stream_env = StreamExecutionEnvironment.get_execution_environment()
    extra_jar_paths = [f"file://{os.getcwd()}/jars/{f}" for f in os.listdir("jars")]
    stream_env.add_jars(*extra_jar_paths)
    stream_env.add_classpaths(*extra_jar_paths)
    schema_registry_client: LocalSchemaRegistryClient = LocalSchemaRegistryClient()
    lendmate_application_updated_schema_string: str = schema_registry_client.fetch_avro_schema_string(
        address="avro/kinesis/fairmoney-tube/lendmate-application-updated.avsc"
    )
    deserializer = AvroRowDeserializationSchema(avro_schema_string=lendmate_application_updated_schema_string)
    kinesis_source_config = KinesisSourceConfig(
        aws_region="eu-west-1",
        stream_init_pos=KinesisStreamInitPosition.TRIM_HORIZON
    )
    events_source = read_from_kinesis_avro(
        stream_name="lendmate-application-updated",
        config=KinesisSourceConfig(
            aws_region="eu-west-1",
            stream_init_pos=KinesisStreamInitPosition.TRIM_HORIZON
        ),
        deserializer=deserializer
    )
    events_stream = stream_env.add_source(
        source_name="kinesis-lendmate-application-updated",
        source_func=events_source
    )
    events_stream.print()
    stream_env.execute("sample_pipeline")

