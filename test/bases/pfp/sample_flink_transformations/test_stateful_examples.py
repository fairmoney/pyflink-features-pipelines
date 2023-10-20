from pyflink.testing.test_case_utils import PyFlinkUTTestCase

from pfp.sample_flink_transformations.stateful_examples import *


class StatefulExampleUTTestCase(PyFlinkUTTestCase):
    """
    A set of unit tests to test stateful examples
    """

    def test_count_all_user_actions_1(self):
        """
        count_all_user_actions transformation should count all user actions when no filtering criteria is given
        """
        ref_timestamp = dt.datetime.utcnow()
        inputs = [
            UserActionIn(user_id="1", action_time=ref_timestamp, action_type=ActionType.LOGIN),
            UserActionIn(
                user_id="1",
                action_time=ref_timestamp + dt.timedelta(seconds=1),
                action_type=ActionType.DO_SOMETHING
            ),
            UserActionIn(
                user_id="1",
                action_time=ref_timestamp + dt.timedelta(seconds=2),
                action_type=ActionType.DO_SOMETHING
            ),
            UserActionIn(
                user_id="1",
                action_time=ref_timestamp + dt.timedelta(seconds=3),
                action_type=ActionType.LOGOUT
            )
        ]
        outputs_ds = count_all_user_actions(self.env.from_collection(inputs))
        outputs = list(outputs_ds.execute_and_collect())
        expected_outputs = [
            UserActionCount(user_id="1", last_action_time=ref_timestamp, actions_count=1),
            UserActionCount(user_id="1", last_action_time=ref_timestamp + dt.timedelta(seconds=1), actions_count=2),
            UserActionCount(user_id="1", last_action_time=ref_timestamp + dt.timedelta(seconds=2), actions_count=3),
            UserActionCount(user_id="1", last_action_time=ref_timestamp + dt.timedelta(seconds=3), actions_count=4),
        ]
        self.assertListEqual(outputs, expected_outputs)

    def test_count_all_user_actions_2(self):
        """
        count_all_user_actions transformation should count all login user actions when filtering criteria is set to
        login only
        """
        ref_timestamp = dt.datetime.utcnow()
        inputs = [
            UserActionIn(user_id="1", action_time=ref_timestamp, action_type=ActionType.LOGIN),
            UserActionIn(
                user_id="1",
                action_time=ref_timestamp + dt.timedelta(seconds=1),
                action_type=ActionType.DO_SOMETHING
            ),
            UserActionIn(
                user_id="1",
                action_time=ref_timestamp + dt.timedelta(seconds=2),
                action_type=ActionType.DO_SOMETHING
            ),
            UserActionIn(
                user_id="1",
                action_time=ref_timestamp + dt.timedelta(seconds=3),
                action_type=ActionType.LOGOUT
            )
        ]
        outputs_ds = count_all_user_actions(self.env.from_collection(inputs), action_type=ActionType.LOGIN)
        outputs = list(outputs_ds.execute_and_collect())
        expected_outputs = [
            UserActionCount(user_id="1", last_action_time=ref_timestamp, actions_count=1)
        ]
        self.assertListEqual(outputs, expected_outputs)

    def test_count_all_user_actions_last_x_seconds_1(self):
        """
        count_all_user_actions_last_x_seconds should emit counts over sliding windows of x seconds every y seconds
        """
        ref_timestamp = dt.datetime(year=2023, month=10, day=20, hour=12, minute=0, second=0)
        inputs = [
            UserActionIn(
                user_id="1",
                action_time=ref_timestamp,
                action_type=ActionType.LOGIN
            ),
            UserActionIn(
                user_id="1",
                action_time=ref_timestamp + dt.timedelta(seconds=7),
                action_type=ActionType.DO_SOMETHING
            ),
            UserActionIn(
                user_id="1",
                action_time=ref_timestamp + dt.timedelta(seconds=13),
                action_type=ActionType.DO_SOMETHING
            ),
            UserActionIn(
                user_id="1",
                action_time=ref_timestamp + dt.timedelta(seconds=24),
                action_type=ActionType.LOGOUT
            )
        ]
        window_size_seconds: int = 30
        window_slide_seconds: int = 5

        last_window_start = ref_timestamp + dt.timedelta(seconds=20)  #Flink will trigger windows at "rounded" timestamps. If the
        last_window_end = last_window_start + dt.timedelta(seconds=window_size_seconds)
        # slinding window has slide = 5 seconds, then Flink will start windows at seconds [0, 5, 10, 15, 20, 2, etc...]
        # as last event timestamp here has seconds value of 24 - closest window triggered will be 20 seconds
        first_window_end = ref_timestamp + dt.timedelta(seconds=5)  # Same logics applies here.
        first_window_start = first_window_end - dt.timedelta(seconds=window_size_seconds)
        expected_windows_count = int((last_window_start.timestamp() - first_window_start.timestamp()) / window_slide_seconds) + 1
        outputs_ds = count_all_user_actions_last_x_seconds_every_y_seconds(
            actions_stream=self.env.from_collection(inputs),
            window_size_seconds=window_size_seconds,
            window_slide_seconds=window_slide_seconds
        )
        outputs = list(outputs_ds.execute_and_collect())
        event_times = [i.action_time for i in inputs]
        max_event_time = max(event_times)
        min_event_time = min(event_times)
        print("==================")
        print(f"Min event time: {min_event_time.isoformat()} - Max event time: {max_event_time.isoformat()}")
        print(f"Expected windows count: {expected_windows_count}")
        for o in outputs:
            print(dict(
                window_start=dt.datetime.fromtimestamp(o.window_start / 1e3).isoformat(),
                window_end=dt.datetime.fromtimestamp(o.window_end / 1e3).isoformat(),
                actions_count=o.actions_count
            ))
        self.assertEquals(len(outputs), expected_windows_count)
