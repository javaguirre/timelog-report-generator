#!/user/bin/env python

import argparse

from timelog.utils import TimelogReport


def main():
    parser = argparse.ArgumentParser(description='Timelog - Report generator for gtimelog format')

    parser.add_argument('--month', help='Month of the report')
    parser.add_argument('--year', help='Year of the report')
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
    parser.add_argument('--html',
                        help='Generate HTML page with the stats',
                        action='store_true',
                        default=False)

    arguments = parser.parse_args()
    timelog_report = TimelogReport(arguments)
    result = timelog_report.run()

    # TODO Or write it to a file
    print(result)


if __name__ == '__main__':
    main()
