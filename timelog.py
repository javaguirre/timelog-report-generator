#!/user/bin/env python

import argparse

from timelog.utils import TimelogReport

TIMELOG_FILE = 'timelog.txt'
CLIENTS_FILE = 'projects.txt'


def main():
    parser = argparse.ArgumentParser(description='Timelog - Report generator for gtimelog format')
    parser.add_argument('--timelog-src',
                        help='Source file for the timelog',
                        default=TIMELOG_FILE)
    parser.add_argument('--clients-file',
                        help='Source file for the clients',
                        default=CLIENTS_FILE)
    parser.add_argument('--start-date',
                        help='Start date report'
                        )
    parser.add_argument('--end-date',
                        help='End date report'
                        )
    parser.add_argument('--order-by',
                        help='Order by month week day',
                        default=False
                        )
    parser.add_argument('--price',
                        help='With price or not, boolean',
                        action='store_true',
                        default=False)
    parser.add_argument('--tasks',
                        help='With tasks or not, boolean',
                        action='store_true',
                        default=False)
    parser.add_argument('--generate-timelog',
                        help='With a format */*/2013',
                        default='*')
    parser.add_argument('--client',
                        help='The client in case you want a client report',
                        default=None)

    arguments = parser.parse_args()
    timelog_report = TimelogReport(arguments)
    result = timelog_report.run()

    # TODO Or write it to a file
    print(result)


if __name__ == '__main__':
    main()
