from typing import Union, Callable

from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.datastream import SinkFunction
from pyflink.datastream import SourceFunction
from pyflink.datastream import StreamExecutionEnvironment, DataStream, DataStreamSink
from pyflink.datastream.connectors import Sink
from pyflink.datastream.connectors import Source

from pfp.flink_jobs.builder.sinks import get_sink_builder
from pfp.flink_jobs.builder.sinks.core import FlinkJobSinkBuilder
from pfp.flink_jobs.builder.sources import get_source_builder, FlinkJobSourceBuilder
from pfp.flink_jobs.configuration.job import FlinkJobConfig, FlinkExecutionMode
from pfp.flink_jobs.configuration.sinks import SinkConfig
from pfp.flink_jobs.configuration.sources import SourceConfig
from pyflink.datastream import RuntimeExecutionMode


class FlinkJobBuilder:

    _config: FlinkJobConfig
    _env: StreamExecutionEnvironment

    _sources: list[Union[SourceFunction, Source]]
    _sinks: list[Union[SinkFunction, Sink]]

    def __init__(self, config: FlinkJobConfig):
        self._config = config

    @staticmethod
    def _build_clean_uid(name: str) -> str:
        return name.strip().replace(" ", "").lower()

    def _build_environment(self):
        self._env = StreamExecutionEnvironment.get_execution_environment()
        env_exec_mode = self._config.environment_settings.execution_mode
        execution_mode: RuntimeExecutionMode
        if env_exec_mode == FlinkExecutionMode.STREAMING:
            execution_mode = RuntimeExecutionMode.STREAMING
        elif env_exec_mode == FlinkExecutionMode.BATCH:
            execution_mode = RuntimeExecutionMode.BATCH
        else:
            raise Exception(f"Unknown value {env_exec_mode} for Flink execution mode.")
        self._env.set_runtime_mode(execution_mode=execution_mode)
        if self._config.environment_settings.jars_paths is not None:
            self._env.add_jars(*self._config.environment_settings.jars_paths)
            self._env.add_classpaths(*self._config.environment_settings.jars_paths)

    def _build_source_datastream(self, config: SourceConfig) -> DataStream:
        builder: FlinkJobSourceBuilder = get_source_builder(config=config)
        source: Union[Source, SourceFunction] = builder.build()
        base_source_ds: DataStream
        if isinstance(source, SourceFunction):
            base_source_ds = self._env.add_source(source_name=config.source_name, source_func=source)
        elif isinstance(source, Source):
            # todo: add watermark_strategy_config in config
            base_source_ds = self._env.from_source(
                source=source,
                watermark_strategy=WatermarkStrategy.no_watermarks(),
                source_name=config.source_name
            )
        else:
            raise NotImplementedError(f"Unknown Flink source type {type(source)}")
        # todo: add configuration options for parallelism
        return base_source_ds\
            .name(config.source_name)\
            .uid(config.source_name.strip().replace(" ", "_"))

    @staticmethod
    def _build_datastream_sink(config: SinkConfig, ds: DataStream) -> DataStreamSink:
        builder: FlinkJobSinkBuilder = get_sink_builder(config)
        sink: Union[SinkFunction, Sink] = builder.build()
        base_ds_sink: DataStreamSink
        if isinstance(sink, SinkFunction):
            base_ds_sink = ds.add_sink(sink_func=sink)
        elif isinstance(sink, Sink):
            base_ds_sink = ds.sink_to(sink=sink)
        else:
            raise Exception(f"Unknown Flink sink type {type(sink)}")
        uid: str = FlinkJobBuilder._build_clean_uid(name=config.sink_name)
        description: str = config.sink_name if config.sink_description is not None else config.sink_name
        return base_ds_sink\
            .name(config.sink_name)\
            .uid(uid)\
            .set_description(description=description)

    def build(self):
        self._build_environment()
        transformation_function_inputs: dict[str, DataStream] = {}
        expected_transformation_function_input_args = [
            s.transformation_function_arg_name for s in self._config.sources_configs
        ]
        self._config.transformation_pyfunction_specs.validate(expected_transformation_function_input_args)
        transformation_function: Callable = self._config.transformation_pyfunction_specs.function
        for source_config in self._config.sources_configs:
            source_ds: DataStream = self._build_source_datastream(config=source_config)
            transformation_function_inputs[source_config.transformation_function_arg_name] = source_ds
        outputs: DataStream = transformation_function(**transformation_function_inputs)
        if self._config.sinks_configs is not None:
            for sink_config in self._config.sinks_configs:
                FlinkJobBuilder._build_datastream_sink(config=sink_config, ds=outputs)
        else:
            outputs.print(sink_identifier="Console sink")

    def run(self):
        self._env.execute(job_name=self._config.job_name)




