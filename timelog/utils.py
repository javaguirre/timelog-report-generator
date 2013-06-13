# -*- coding: utf-8 -*-

import os
import re
import datetime
import codecs

'''
    Timelog generator report tools
'''

DURATION_FORMAT = r'%d h %d min'
DATE_FORMAT = r'^(\d+)/(\d+)/(\d+)$'
DATETIME_FORMAT = r'^(\d+)-(\d+)-(\d+) (\d+):(\d+)$'
TASKS_FORMAT = r'^\* \[[\.oOX]\]'
TIMELOG_SEPARATION_FORMAT = r': '   # This is the separation between the
                                    # datetime and the tag/client
SLACK_FORMAT = r'\w+\*\*$'          # the format of the log entries that aren't
                                    # counted as work


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


def calculate_report(filepath, start_date, end_date, client=None):
    entries = []
    start = parse_date(start_date)
    end = parse_date(end_date)
    last_datetime = None
    tasks = []

    with codecs.open(os.path.expanduser(filepath), encoding='utf-8') as filed:
        for line in filed:
            try:
                time, entry = line.split(TIMELOG_SEPARATION_FORMAT, 1)
                entry = entry.replace('\n', '')
                dt = parse_datetime(time)
            except ValueError:
                dt = None
                if re.match(TASKS_FORMAT, line):
                    tasks.append(line)
                continue
            if dt is not None and dt > start and dt < end:
                if not re.match(SLACK_FORMAT, entry):
                    if not client or client == entry:
                        duration = set_duration(dt, last_datetime)
                        entries.append([dt, entry, duration, tasks])
                last_datetime = dt
                tasks = []
    return entries


def report_group_by(entries, order_by):
    new_entries = {}
    last_value = None

    if not entries:
        return False

    for date_work, client, duration, tasks in entries:
        if order_by == 'week':
            date_value = date_work.isocalendar()[1]
        else:
            date_value = getattr(date_work, order_by)

        if last_value == date_value:
            if client in new_entries[date_value]:
                new_entries[date_value][client][2] += duration
                new_entries[date_value][client][3] += tasks
            else:
                new_entries[date_value][client] = [date_work, client,
                                                   duration, tasks]
        else:
            new_entries[date_value] = {client: [date_work, client,
                                                duration, tasks]}
        last_value = date_value
    return new_entries


def get_price(client, total_time, client_file):
    with open(client_file, 'r') as f:
        for line in f:
            if line.startswith(client):
                client_info = line.split(':')
                if client_info[0] == client:
                    hours = '%.2f' % round((total_time.total_seconds()*1.0)/3600, 2)
                    return int(client_info[2])*float(hours)
    return 0


def print_header(order_value, order_by):
    return '====== %s %s =======\n' % (order_by.capitalize(), str(order_value))


def print_content(data, with_tasks):
    for client, client_info in data.items():
        print('%s : %s' % (client.capitalize(),
                           format_duration(client_info[2])))
        if client_info[3] and with_tasks:
            print('\n%s' % ''.join(client_info[3]))


def print_result(data_report, with_tasks, order_by=None, client=None,
                 filepath=None, client_file=None, with_price=False):
    # TODO If filepath, save to the file instead of stdout
    for order_value, data in data_report.items():
        print(print_header(order_value, order_by))
        print_content(data, with_tasks)
        total_time = reduce(lambda x, y: x + y,
                            [value[2] for value in data.values()])
        print('\nTotal time: %s' % total_time)

        if with_price:
            total_price = get_price(client, total_time, client_file)
            print('\nTotal amount: %s' % total_price)


def run_timelog(args):
    order = args.order_by or 'day'
    entries = calculate_report(args.timelog_src,
                               args.start_date, args.end_date,
                               args.client)
    if not entries:
        print('Error: No entries')
        return False

    if order in ('day', 'week', 'month'):
        entries = report_group_by(entries, order)
    else:
        print('Error: You need to provide a good order, the options are day, week, month')
        return False

    print_result(entries, args.tasks, order, args.client,
                 os.path.expanduser(args.timelog_src),
                 os.path.expanduser(args.clients_file),
                 args.price)
