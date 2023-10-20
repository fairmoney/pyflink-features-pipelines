import unittest
import datetime as dt
from pfp.common_utils import date as date_utils
import pytz


class DateUtilTests(unittest.TestCase):
    """
    A set of unit tests to test date utility functions
    """
    _ref_date: dt.datetime = dt.datetime(2023, 10, 20, tzinfo=pytz.utc)
    _seconds_since_epoch = (_ref_date - dt.datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds()

    def test_to_seconds_since_epoch(self):
        """
        to_seconds_since_epoch should return valid number of seconds since 1970-01-01
        """
        seconds_since_epoch: int = date_utils.to_seconds_since_epoch(self._ref_date)
        self.assertEqual(seconds_since_epoch, int(self._seconds_since_epoch))

    def test_to_milliseconds_since_epoch(self):
        """
        to_milliseconds_since_epoch should return valid number of milliseconds since 1970-01-01
        """
        milliseconds_since_epoch: int = date_utils.to_milliseconds_since_epoch(self._ref_date)
        self.assertEqual(milliseconds_since_epoch, int(1e3 * self._seconds_since_epoch))

    def test_to_microseconds_since_epoch(self):
        """
        to_microseconds_since_epoch should return valid number of microseconds since 1970-01-01
        """
        microseconds_since_epoch: int = date_utils.to_microseconds_since_epoch(self._ref_date)
        self.assertEqual(microseconds_since_epoch, int(1e6 * self._seconds_since_epoch))
