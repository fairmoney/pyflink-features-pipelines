from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field

from pfp.common_utils.functions import FlinkJobTransformationSpec
from pfp.flink_jobs.configuration.sinks import SinkConfig
from pfp.flink_jobs.configuration.sources import SourceConfig


class FlinkExecutionMode(Enum):
    BATCH: str = "batch"
    STREAMING: str = "streaming"


class FlinkEnvironmentSetting(BaseModel):
    execution_mode: FlinkExecutionMode = Field(
        description="The execution mode for the job's environment"
    )
    jars_paths: Optional[List[str]] = Field(
        default=None,
        description="Optional list of extra jars to be added to Flink runtime environment"
    )


class FlinkJobConfig(BaseModel):
    job_name: str = Field(
        default=...,
        description="A description of what the job is computing."
    )
    environment_settings: FlinkEnvironmentSetting = Field(
        default=...,
        description="Configuration for the Flink environment"
    )
    sources_configs: List[SourceConfig] = Field(
        default=...,
        description="A list of source configurations that defines the inputs of the job"
    )

    transformation_function: str = Field(
        default=...,
        description="The fully qualified name of the transformation to be applied to inputs"
    )

    sinks_configs: Optional[List[SinkConfig]] = Field(
        default=None,
        description="An optional list of sink configs to emit results of the job. If no sink config is provided, "
                    "a PrintSink will be instantiated to print the results of the pipeline to the console."
    )

    @property
    def transformation_pyfunction_specs(self) -> FlinkJobTransformationSpec:
        return FlinkJobTransformationSpec \
            .from_fully_qualified_function_address(fn_address=self.transformation_function)
