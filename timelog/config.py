import os

TIMELOG_FILE = '~/vimwiki/timelog.txt'
CLIENTS_FILE = 'projects.txt'
HTML_TEMPLATE = 'bar_report.html'
DURATION_FORMAT = r'%d h %d min'
DATE_FORMAT = r'^(\d+)/(\d+)/(\d+)$'
DATETIME_FORMAT = r'^(\d+)-(\d+)-(\d+) (\d+):(\d+)$'
TASKS_FORMAT = r'^\* \[[\.oOX]\]'
TIMELOG_SEPARATION_FORMAT = r': '   # This is the separation between the
                                    # datetime and the tag/client
SLACK_FORMAT = r'\w+\*\*$'          # the format of the log entries that aren't
                                    # counted as work
SITE = os.path.join(os.path.dirname(__file__), '../reports')

