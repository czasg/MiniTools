import re
import calendar

from datetime import datetime, timedelta

__all__ = ('to_datetime', 'timekiller')

RE_SEARCH_D4_D2 = re.compile("(\d{4})[^\d]*(\d{2})[^\d]*(\d{0,2})[^\d]*(\d{0,2})[^\d]*(\d{0,2})[^\d]*(\d{0,2})").search


def str2datetime(string):
    d4d2 = RE_SEARCH_D4_D2(string)
    if not d4d2: return None

    lower_limit = [1000, 1, 1, 0, 0, 0]  # Using the lower limit as the default time
    upper_limit = [9999, 12, 31, 23, 59, 59]

    for index in range(6):
        match_key = int(d4d2.group(index + 1) or 0)
        if match_key and lower_limit[index] < match_key < upper_limit[index]:
            lower_limit[index] = match_key

    return datetime(*lower_limit)


def to_datetime(obj):
    if isinstance(obj, datetime):
        return obj
    elif isinstance(obj, str):
        return str2datetime(obj)
    else:
        raise NotImplemented(f"No func process {type(obj)} to datetime")


class _DateTimeKiller:

    @classmethod
    def split(cls, dateObj: datetime = None):
        dateObj = dateObj or cls.get_today()
        return dateObj.year, dateObj.month, dateObj.day, dateObj.hour, dateObj.minute, dateObj.second

    @classmethod
    def datetimeStr(cls, dateObj: datetime, dateStr="%y-%m-%d %H:%M:%S"):
        return dateObj.strftime(dateStr)

    @classmethod
    def create(cls, *args):
        return datetime(*args)

    @classmethod
    def get_now(cls):
        return datetime.now()

    @classmethod
    def get_today(cls):
        now = cls.get_now()
        return datetime(now.year, now.month, now.day)

    @classmethod
    def get_past_day(cls, days):
        today = cls.get_today()
        return today - timedelta(days=days)

    @classmethod
    def get_yesterday(cls):
        return cls.get_past_day(1)

    @classmethod
    def get_tomorrow(cls):
        return cls.get_past_day(-1)

    @classmethod
    def get_len_of_month(cls, _datetime):
        return calendar.monthlen(_datetime.year, _datetime.month)

    @classmethod
    def get_len_of_current_month(cls):
        return cls.get_len_of_month(cls.get_now())

    @classmethod
    def head_and_tail_of_month(cls, _datetime):
        return cls.create(_datetime.year, _datetime.month, 1), \
               cls.create(_datetime.year, _datetime.month, cls.get_len_of_month(_datetime))


timekiller = _DateTimeKiller
