from pyflink.datastream import DataStream

from pfp.sample_flink_transformations.map_functions import AddOne


def add_one(inputs: DataStream) -> DataStream:
    return inputs.map(lambda x: x+1)


def add_one_with_mapfunction(inputs: DataStream, ) -> DataStream:
    return inputs.map(AddOne())

