import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Iterable

from pyflink.common.typeinfo import Types
from pyflink.common.watermark_strategy import TimestampAssigner, WatermarkStrategy, Duration
from pyflink.datastream import DataStream
from pyflink.datastream import window
from pyflink.datastream.functions import MapFunction, RuntimeContext, AggregateFunction, ProcessWindowFunction
from pyflink.datastream.state import ValueStateDescriptor, ValueState
from pyflink.datastream.window import SlidingEventTimeWindows
from pyflink.datastream.window import Time

from pfp.common_utils.date import to_milliseconds_since_epoch


class ActionType(Enum):
    LOGIN: str = "login"
    DO_SOMETHING: str = "do_something"
    LOGOUT: str = "logout"


@dataclass
class UserActionIn:
    """
    An internal model representing a user action
    """
    user_id: str
    action_time: dt.datetime
    action_type: ActionType


@dataclass
class UserActionCount:
    """
    An internal model representing the count of user actions
    """
    user_id: str
    last_action_time: dt.datetime
    actions_count: int


@dataclass
class UserActionWindowedCount:
    """
    An internal model representing the count of user actions over a time window
    """
    user_id: str
    window_start: dt.datetime
    window_end: dt.datetime
    actions_count: int


class ActionsCountFunction(MapFunction):

    actions_count: Optional[ValueState]

    def __init__(self):
        self.actions_count = None

    def open(self, runtime_context: RuntimeContext):
        actions_counter_descriptor = ValueStateDescriptor(
            name="actions_counter",
            value_type_info=Types.INT()
        )
        self.actions_count = runtime_context.get_state(state_descriptor=actions_counter_descriptor)

    def map(self, value: UserActionIn):

        # Access state value
        current_actions_count: int = self.actions_count.value()
        if current_actions_count is None:
            current_actions_count = 0

        # Update state value
        updated_actions_count: int = current_actions_count + 1
        self.actions_count.update(value=updated_actions_count)

        # Emit results
        return UserActionCount(
            user_id=value.user_id,
            last_action_time=value.action_time,
            actions_count=updated_actions_count
        )


def count_all_user_actions(actions_stream: DataStream, action_type: Optional[ActionType]=None) -> DataStream:
    """
    A transformation function that receives a stream of user actions and emits a count of actions per user.
    :param actions_stream: A DataStream or user actions
    :param action_type: An optional filter to consider only actions of a certain type
    :return: A Datastream emitting the count of actions per user
    """
    def _filter(user_action: UserActionIn) -> bool:
        return user_action.action_type.value == action_type.value
    inputs: DataStream = actions_stream if action_type is None else actions_stream.filter(_filter)
    return inputs\
        .key_by(lambda e: e.user_id)\
        .map(ActionsCountFunction())


class WindowedActionCountFunction(AggregateFunction):
    """
    The accumulator is used to keep a running count of user actions over a window.
    It can be combined with a WindowProcessFunction - so that intermediary window aggregates are being passed to the
    WindowProcessFunction, instead of all elements from the window.
    """
    def create_accumulator(self) -> int:
        return 0

    def add(self, value: UserActionIn, accumulator: int) -> int:
        return accumulator + 1

    def get_result(self, accumulator: int) -> int:
        return accumulator

    def merge(self, acc_a: int, acc_b: int) -> int:
        return acc_a + acc_b


class ActionsCountProcessWindowFunction(ProcessWindowFunction):

    def process(
            self,
            key: str,
            context: 'ProcessWindowFunction.Context',
            counts: Iterable[int]
    ) -> Iterable[UserActionWindowedCount]:
        """
        This function is here only to get window context as the WindowedActionCountFunction doesn't have it.
        :param key: The user_id - as the incoming DataStream is keyed by user_id
        :param context: The current context of the window being triggered
        :param counts: an iterable of integers - representing intermediary results from the aggregation function
        :return: an element of type UserActionCount for the current window
        """
        current_window = context.window()
        current_window_count = next(iter(counts))

        yield UserActionWindowedCount(
            user_id=key,
            window_start=current_window.start,
            window_end=current_window.end,
            actions_count=current_window_count
        )


class UserActionTimestampAssigner(TimestampAssigner):
    def extract_timestamp(self, value: UserActionIn, record_timestamp):
        return to_milliseconds_since_epoch(value.action_time)


def count_all_user_actions_last_x_seconds_every_y_seconds(
        actions_stream: DataStream,
        window_size_seconds: int,
        window_slide_seconds: int
) -> DataStream:
    """
    A transformation function that receives a stream of user actions and emits a count of actions per user over the
    last x seconds.
    :param actions_stream: A DataStream or user actions
    :param window_size_seconds: The size of the window to consider, in seconds
    :param window_slide_seconds: The interval between 2 windows trigger
    :return: A Datastream emitting the count of actions per user over the last x seconds
    """
    watermark_strategy: WatermarkStrategy = WatermarkStrategy\
        .for_bounded_out_of_orderness(max_out_of_orderness=Duration.of_seconds(1))\
        .with_timestamp_assigner(UserActionTimestampAssigner())
    sliding_window: SlidingEventTimeWindows = window.SlidingEventTimeWindows.of(
        size=Time.seconds(window_size_seconds),
        slide=Time.seconds(window_slide_seconds)
    )
    return actions_stream \
        .assign_timestamps_and_watermarks(watermark_strategy) \
        .key_by(lambda e: e.user_id) \
        .window(sliding_window) \
        .aggregate(
            aggregate_function=WindowedActionCountFunction(),
            window_function=ActionsCountProcessWindowFunction()
        )
