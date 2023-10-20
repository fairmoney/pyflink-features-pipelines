from pyflink.datastream.functions import MapFunction


class AddOne(MapFunction):

    def map(self, value: int) -> int:
        return value + 1
