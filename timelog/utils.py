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


class TimelogReport():
    def __init__(self, args):
        self.timelog_src = args.timelog_src
        self.start_date = args.start_date
        self.end_date = args.end_date
        self.client = args.client
        self.order_by = args.order_by or 'day'
        self.tasks = args.tasks
        self.client = args.client
        self.client_file = args.clients_file
        self.price = args.price
        self.tasks = args.tasks

    def as_minutes(self, duration):
        """Convert a datetime.timedelta to an integer number of minutes."""
        return duration.days * 24 * 60 + duration.seconds // 60

    def format_duration(self, duration):
        """Format a datetime.timedelta with minute precision."""
        h, m = divmod(self.as_minutes(duration), 60)
        return DURATION_FORMAT % (h, m)

    def parse_date(self, dt):
        m = re.match(DATE_FORMAT, dt)
        if not m:
            raise ValueError('bad date time: ', dt)
        day, month, year = map(int, m.groups())
        return datetime.datetime(year, month, day)

    def parse_datetime(self, dt):
        m = re.match(DATETIME_FORMAT, dt)
        if not m:
            raise ValueError('bad date time: ', dt)
        year, month, day, hour, min = map(int, m.groups())
        return datetime.datetime(year, month, day, hour, min)

    def set_duration(self, current, last):
        if last and current.day == last.day:
            return current - last
        else:
            return datetime.timedelta(0)

    def calculate_report(self):
        entries = []
        start = self.parse_date(self.start_date)
        end = self.parse_date(self.end_date)
        last_datetime = None
        tasks = []

        with codecs.open(os.path.expanduser(self.timelog_src), encoding='utf-8') as filed:
            for line in filed:
                try:
                    time, entry = line.split(TIMELOG_SEPARATION_FORMAT, 1)
                    entry = entry.replace('\n', '')
                    dt = self.parse_datetime(time)
                except ValueError:
                    dt = None
                    if re.match(TASKS_FORMAT, line):
                        tasks.append(line)
                    continue
                if dt is not None and dt > start and dt < end:
                    if not re.match(SLACK_FORMAT, entry):
                        if not self.client or self.client == entry:
                            duration = self.set_duration(dt, last_datetime)
                            entries.append([dt, entry, duration, tasks])
                    last_datetime = dt
                    tasks = []
        return entries

    def report_group_by(self, entries):
        new_entries = {}
        last_value = None

        if not entries:
            return False

        for date_work, client, duration, tasks in entries:
            if self.order_by == 'week':
                date_value = date_work.isocalendar()[1]
            else:
                date_value = getattr(date_work, self.order_by)

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

    def get_price(self, total_time):
        with open(self.client_file, 'r') as f:
            for line in f:
                if line.startswith(self.client):
                    client_info = line.split(':')
                    if client_info[0] == self.client:
                        hours = (total_time.total_seconds()*1.0)/3600
                        return '%.2f' % round(float(client_info[2])*float(hours),
                                              2)
        return 0

    def get_header(self, order_value):
        return '\n====== %s %s =======\n' % (self.order_by.capitalize(), str(order_value))

    def get_content(self, data):
        content = []
        for client, client_info in data.items():
            content.append('%s : %s' % (client.capitalize(),
                                        self.format_duration(client_info[2])))
            if client_info[3] and self.tasks:
                content.append('\n%s' % ''.join(client_info[3]))
        return content

    def get_result(self, data_report):
        result = []
        for order_value, data in data_report.items():
            result.append(self.get_header(order_value))
            result = result + self.get_content(data)
            total_time = reduce(lambda x, y: x + y,
                                [value[2] for value in data.values()])
            result.append('\nTotal time: %s' % self.format_duration(total_time))

            if self.price and self.client:
                total_price = self.get_price(total_time)
                result.append('\nTotal amount: %s' % total_price)
        return result

    def run(self):
        entries = self.calculate_report()
        if not entries:
            return 'Error: No entries'

        if self.order_by in ('day', 'week', 'month'):
            entries = self.report_group_by(entries)
        else:
            return 'Error: You need to provide a good order, the options are day, week, month'

        result = self.get_result(entries)
        return '\n'.join(result)
