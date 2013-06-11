# -*- coding: utf-8 -*-

import os
import re
import datetime
import codecs

'''
    Timelog generator report tools
'''


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


def calculate_report(filepath, start_date, end_date, order_by, client=None):
    entries = []
    start = parse_date(start_date)
    end = parse_date(end_date)
    with codecs.open(os.path.expanduser(filepath), encoding='utf-8') as filed:
        for line in filed:
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
                        entries.append([dt, entry])
    return entries


def report_group_by(data, order_by):
    if not data:
        return False

    if order_by is 'month':
        start = data[0][0].month
    elif order_by is 'week':
        start = data[0][0].isocalendar()[1]
    else:
        start = data[0][0]



def get_price(entry, duration, clients_file, with_price=False):
    if with_price:
        with codecs.open(clients_file, encoding='utf-8') as f:
            for line in f:
                if line.startswith(entry.lower()):
                    client_info = line.split(':')
                    if client_info[0] == entry.lower():
                        if client_info[1] == 'hour':
                            hours = '%.2f' % round((duration.total_seconds()*1.0)/3600, 2)
                            return '%s Euros' % str(int(client_info[2])*float(hours))
                        elif client_info[1] == 'day':
                            days = '%.2f' % round(((duration.total_seconds()*1.0)/3600)/8, 2)
                            return '%s Euros' % str(int(client_info[2])*float(days))
    return ''


def print_result(data_report, filepath=None):
    # TODO If filepath
    for item in data_report:
        print(item)


def run_timelog(args):
    filepath = args.timelog_src
    filepath_dst = None

    data_report = calculate_report(filepath,
                                   args.start_date, args.end_date,
                                   args.order_by, args.client)
    if args.order_by and args.order_by in ('day', 'week', 'month'):
        report_group_by(data_report, args.order_by)

    print_result(data_report, filepath_dst)
