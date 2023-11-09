import os

from pfp.flink_jobs.builder.core import FlinkJobBuilder
from pfp.flink_jobs.configuration import LocalSchemaRegistryConfig
from pfp.flink_jobs.configuration.job import FlinkJobConfig, FlinkEnvironmentSetting, FlinkExecutionMode
from pfp.flink_jobs.configuration.sources import KinesisAvroSourceConfig
from pfp.flink_jobs.configuration.sources.kinesis import KinesisStreamInitPosition

if __name__ == "__main__":
    jars_folder = os.path.join(os.getcwd(), "jars")
    avro_folder = os.path.join(os.getcwd(), "development", "avro")

    job_config: FlinkJobConfig = FlinkJobConfig(
        job_name="sample_branch_events_job",
        environment_settings=FlinkEnvironmentSetting(
            execution_mode=FlinkExecutionMode.STREAMING,
            jars_paths=[
                f"file://{jars_folder}/flink-sql-avro-1.15.4.jar",
                f"file://{jars_folder}/flink-sql-connector-kinesis-1.15.4.jar",
            ]
        ),
        sources_configs=[
            KinesisAvroSourceConfig(
                source_name="kinesis_branch_events",
                stream_name="branch-events",
                aws_region="eu-west-1",
                stream_init_pos=KinesisStreamInitPosition.LATEST,
                schema_registry_config=LocalSchemaRegistryConfig(
                    avro_file_path=os.path.join(avro_folder, "branch-event.avsc")
                ),
                transformation_function_arg_name="ds"
            ),
            # KinesisAvroSourceConfig(
            #     source_name="kinesis_lendmate_application_updated",
            #     stream_name="lendmate-application-updated",
            #     aws_region="eu-west-1",
            #     stream_init_pos=KinesisStreamInitPosition.TRIM_HORIZON,
            #     schema_registry_config=LocalSchemaRegistryConfig(
            #         avro_file_path=os.path.join(avro_folder, "lendmate-application-updated.avsc")
            #     ),
            #     transformation_function_arg_name="ds"
            # ),
            KinesisAvroSourceConfig(
                source_name="kinesis_loan_data_updated",
                stream_name="loan-data-updated",
                aws_region="eu-west-1",
                stream_init_pos=KinesisStreamInitPosition.LATEST,
                schema_registry_config=LocalSchemaRegistryConfig(
                    avro_file_path=os.path.join(avro_folder, "loan-data-updated.avsc")
                ),
                transformation_function_arg_name="ds"
            )
        ],
        transformation_function="pfp.sample_flink_transformations.identity"
    )
    job_builder = FlinkJobBuilder(config=job_config)
    job_builder.build()
    job_builder.run()
