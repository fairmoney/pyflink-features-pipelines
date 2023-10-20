import datetime as dt


def to_seconds_since_epoch(ts: dt.datetime) -> int:
    return int(ts.timestamp())


def to_milliseconds_since_epoch(ts: dt.datetime) -> int:
    return int(ts.timestamp() * 1e3)


def to_microseconds_since_epoch(ts: dt.datetime) -> int:
    return int(ts.timestamp() * 1e6)
