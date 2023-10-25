import os
from components.pfp.job_config.deployments.aws_managed_flink import AMFStreamingJobApplicationConfig, \
    load_amf_streaming_job_application_config

if __name__ == "__main__":
    properties_file_path: str = os.environ.get("LOCAL_PROPERTIES_FILE") if os.environ.get("LOCAL_PROPERTIES_FILE") \
        else "/etc/flink/application_properties.json"
    config: AMFStreamingJobApplicationConfig = load_amf_streaming_job_application_config(
        properties_file_path=properties_file_path
    )
    print(f"Running pipeline {config.application_config.name}")
