import re
import datetime
from collections import defaultdict

from timelog.config import DATETIME_FORMAT, DATE_FORMAT, DURATION_FORMAT


def as_minutes(duration):
    """Convert a datetime.timedelta to an integer number of minutes."""
    return duration.days * 24 * 60 + duration.seconds // 60


def format_duration(duration):
    """Format a datetime.timedelta with minute precision."""
    h, m = divmod(as_minutes(duration), 60)

    return DURATION_FORMAT % (h, m)


def parse_date(dt):
    m = re.match(DATE_FORMAT, dt)

    if not m:
        raise ValueError('bad date time: ', dt)

    day, month, year = map(int, m.groups())

    return datetime.datetime(year, month, day)


def parse_datetime(dt):
    m = re.match(DATETIME_FORMAT, dt)

    if not m:
        raise ValueError('bad date time: ', dt)

    year, month, day, hour, min = map(int, m.groups())

    return datetime.datetime(year, month, day, hour, min)


def set_duration(current, last):
    if last and current.day == last.day:
        return current - last
    else:
        return datetime.timedelta(0)


def get_hours(total_time):
    return '%.2f' % ((total_time.total_seconds() * 1.0) / 3600)


def get_total_time(entries):
    total_times = defaultdict(int)

    for entry in entries:
        if entry[1] in total_times:
            total_times[entry[1]] += entry[2]

    return total_times
