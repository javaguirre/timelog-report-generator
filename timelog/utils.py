# -*- coding: utf-8 -*-

import os
import re
import datetime
import codecs

'''
    Timelog generator report tools
'''


def as_minutes(duration):
    """Convert a datetime.timedelta to an integer number of minutes."""
    return duration.days * 24 * 60 + duration.seconds // 60


def format_duration(duration):
    """Format a datetime.timedelta with minute precision."""
    h, m = divmod(as_minutes(duration), 60)
    return '%d h %d min' % (h, m)


def parse_date(dt):
    m = re.match(r'^(\d+)/(\d+)/(\d+)$', dt)
    if not m:
        raise ValueError('bad date time: ', dt)
    day, month, year = map(int, m.groups())
    return datetime.datetime(year, month, day)


def parse_datetime(dt):
    """Parse a datetime instance from 'YYYY-MM-DD HH:MM' formatted string."""
    m = re.match(r'^(\d+)-(\d+)-(\d+) (\d+):(\d+)$', dt)
    if not m:
        raise ValueError('bad date time: ', dt)
    year, month, day, hour, min = map(int, m.groups())
    return datetime.datetime(year, month, day, hour, min)


def set_duration(current, last):
    if last and current.day == last.day:
        return current - last
    else:
        return datetime.timedelta(0)


def calculate_report(filepath, start_date, end_date, order_by, client=None):
    entries = []
    start = parse_date(start_date)
    end = parse_date(end_date)
    last_datetime = None

    with codecs.open(os.path.expanduser(filepath), encoding='utf-8') as filed:
        for line in filed:
            # TODO Tasks
            try:
                time, entry = line.split(': ', 1)
                entry = entry.replace('\n', '')
                dt = parse_datetime(time)
            except ValueError:
                dt = None
                continue
            if dt is not None and dt > start and dt < end:
                if not entry.endswith('**'):
                    if not client or client == entry:
                        duration = set_duration(dt, last_datetime)
                        entries.append([dt, entry, duration])
                last_datetime = dt
    return entries


def report_group_by(entries, order_by):
    new_entries = {}
    last_value = None

    if not entries:
        return False

    if order_by in ('week', 'month', 'day'):
        for date_work, client, duration in entries:
            if order_by == 'week':
                date_value = date_work.isocalendar()[1]
            else:
                date_value = getattr(date_work, order_by)

            if last_value == date_value:
                if client in new_entries[date_value]:
                    new_entries[date_value][client][2] += duration
                else:
                    new_entries[date_value][client] = [date_work, client, duration]
            else:
                new_entries[date_value] = {client: [date_work, client, duration]}

            last_value = date_value
    else:
        # FIXME This is not good because in this case new_entries is a list
        new_entries = entries

    return new_entries


def print_header(order_value, order_by):
    return '====== %s %s =======\n' % (order_by.capitalize(), str(order_value))


def print_content(data):
    for client, client_info in data.items():
        print('%s : %s' % (client.capitalize(),
                           format_duration(client_info[2])))


def print_result(data_report, order_by=None, filepath=None):
    # TODO If filepath
    if not order_by:
        # TODO Think what to do with the default
        for item in data_report:
            print('%s %s %s' % (item[0], item[1], format_duration(item[2])))
    else:
        for order_value, data in data_report.items():
            print(print_header(order_value, order_by))
            print_content(data)


def run_timelog(args):
    filepath = args.timelog_src
    filepath_dst = None

    entries = calculate_report(filepath,
                               args.start_date, args.end_date,
                               args.order_by, args.client)
    if args.order_by and args.order_by in ('day', 'week', 'month'):
        entries = report_group_by(entries, args.order_by)

    print_result(entries, args.order_by, filepath_dst)
