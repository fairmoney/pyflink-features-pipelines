from pyflink.datastream import DataStream


def identity(ds: DataStream) -> DataStream:
    return ds
