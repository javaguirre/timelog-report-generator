# -*- coding: utf-8 -*-

from collections import defaultdict
import os
import re
import functools
import datetime
import codecs
import json
import calendar

from jinja2 import Environment, FileSystemLoader

from timelog import dateutils
from timelog.config import *


'''
    Timelog generator report tools
'''
# Entry fields
DATE = 0
CLIENT = 1
DURATION = 2
TASKS = 3


class TimelogReport():
    def __init__(self, args):
        for prop in ['client', 'tasks', 'html', 'month', 'year']:
            setattr(self, prop, getattr(args, prop))

        if self.year:
            self.year = int(self.year)
        else:
            self.year = datetime.date.today().year

        if self.month:
            self.month = int(self.month)
        else:
            self.month = 1

        self.start_date = datetime.datetime(
            self.year, self.month, 1,
            0, 0, 0
        )
        self.end_date = datetime.datetime(
            self.year, self.month,
            calendar.monthrange(self.year, self.month)[1],
            23, 59, 59
        )

    def get_task(self, line, no_progress):
        task_line = None

        if re.match(TASKS_FORMAT, line):
            task_line = line.replace('\n', '')

            if no_progress:
                task_line = re.sub(TASKS_FORMAT, '', task_line)

        return task_line

    def calculate_report(self, no_progress=False):
        entries = []
        last_datetime = None
        tasks = set()

        with codecs.open(os.path.expanduser(TIMELOG_FILE),
                         encoding='utf-8') as filed:
            for line in filed:
                try:
                    time, entry = line.split(TIMELOG_SEPARATION_FORMAT, 1)
                    entry = entry.replace('\n', '')
                    entry_time = dateutils.parse_datetime(time)
                except ValueError:
                    entry_time = None
                    task_entry = self.get_task(line, no_progress)

                    if task_entry:
                        tasks.add(task_entry)

                    continue

                if entry_time >= self.start_date and entry_time <= self.end_date:
                    if not re.match(SLACK_FORMAT, entry):
                        if not self.client or self.client == entry:
                            duration = dateutils.set_duration(entry_time, last_datetime)
                            entries.append([entry_time.date(), entry, duration, tasks])
                    last_datetime = entry_time
                    tasks = set()
        return entries

    def report_group_by(self, entries):
        new_entries = {}
        last_value = None

        if not entries:
            return False

        for date_work, client, duration, tasks in entries:
            if last_value == date_work:
                if client in new_entries[date_work]:
                    new_entries[date_work][client][DURATION] += duration
                    new_entries[date_work][client][TASKS] = new_entries[date_work][client][3] | tasks
                else:
                    new_entries[date_work][client] = [date_work, client,
                                                      duration, tasks]
            else:
                new_entries[date_work] = {client: [date_work, client,
                                                   duration, tasks]}
            last_value = date_work

        return new_entries

    def set_json_entry(self, item):
        return {
            'x': key,
            'y': item[DURATION].seconds/(3600),
            'size': len(item[TASKS]),
            'id': '-'.join(['id', str(key)])
        }

    def set_json_output(entries):
        if self.client:
            result_output = [{'key': self.client, 'values': entries}]
        else:
            result_output = [{'key': client_key, 'values': items}
                             for client_key, items in entries.items()]
        return result_output

    def generate_json_output(self, entries):
        result_output = []
        entries_json = []
        entries_multiple_clients = defaultdict(list)

        for key, entry in entries.items():
            if self.client:
                entries_json.append(self.set_json_entry(key, entry[self.client]))
            else:
                for client, item in entry.items():
                    entries_multiple_clients[client].append(self.set_json_entry(key, item))

        return json.dumps(set_json_output(entries_json or entries_multiple_clients))

    def generate_html_output(self, entries, total=0):
        loader = FileSystemLoader(os.path.join(os.path.dirname(__file__),
                                               'templates'))

        total_time = 0
        directory = self.client or 'admin'
        path = os.path.join(SITE, directory, '%s_%s.html' % (self.start_date.month, self.start_date.year))
        entries_json = self.generate_json_output(entries)

        try:
            os.mkdir(os.path.join(SITE, self.client or 'admin'))
        except FileExistsError:
            pass

        if self.client:
            total_time = dateutils.get_hours(total[self.client])

        env = Environment(loader=loader)
        template = env.get_template(HTML_TEMPLATE)
        template_content = template.render(
            entries=entries,
            entries_json=entries_json,
            client=self.client,
            total=total_time
        )
        new_file = open(path, 'w')
        new_file.write(template_content)
        new_file.close()

    def get_content(self, data):
        content = []

        for client, client_info in data.items():
            content.append('%s:%s%s' % (client.capitalize(),
                                        ' ' * (COLUMN_WIDTH - len(client)),
                                        dateutils.format_duration(client_info[DURATION])))
            if client_info[TASKS] and self.tasks:
                content.append('\n%s' % ''.join(client_info[TASKS]))

        return content

    def get_total_sum(self, data):
        return functools.reduce(
                lambda x, y: x + y,
                [value[DURATION] for value in data.values()]
        )

    def get_result(self, data_report):
        TOTAL = 'Total time'
        result = []
        entry_dates = [elem for elem in data_report.keys()]
        entry_dates.sort()
        general_total = datetime.timedelta(0)

        for entry_date in entry_dates:
            current_data = data_report[entry_date]
            total_time = self.get_total_sum(current_data)
            general_total += total_time

            result.append('\n# %s\n' % entry_date.strftime('%d/%m/%Y'))
            result = result + self.get_content(current_data)
            result.append('\n%s:%s%s' % (
                TOTAL,
                ' ' * (COLUMN_WIDTH - len(TOTAL)),
                dateutils.format_duration(total_time)
            ))

        general_total = dateutils.format_duration(general_total)
        result.append('\nTOTAL: %s' % general_total)

        return result

    def run(self):
        entries = self.calculate_report(self.html)

        if not entries:
            return 'There are no entries'

        entries = self.report_group_by(entries)

        if self.html:
            self.generate_html_output(entries)

        result = self.get_result(entries)

        return '\n'.join(result)
