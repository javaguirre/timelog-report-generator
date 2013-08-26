import unittest

from timelog.utils import TimelogReport


class ArgParseMock(object):
    def __init__(self,  **kwargs):
        self.timelog_src = 'timelog.txt'
        self.clients_file = 'projects.txt'
        for key, value in kwargs.items():
            setattr(self, key, value)


class TestTimelogFunctions(unittest.TestCase):
    def setUp(self):
        self.args = {'start_date': '1/5/2013',
                     'end_date': '30/6/2013',
                     'order_by': None,
                     'client': None,
                     'tasks': False,
                     'price': False,
                     'generate_html': False}

    def test_dates_empty(self):
        arguments = ArgParseMock(**self.args)
        timelog_report = TimelogReport(arguments)
        self.assertEqual(timelog_report.run(),
                         'Error: No entries')

    def test_dates_data(self):
        self.args['start_date'] = '20/4/2013'
        self.args['end_date'] = '28/4/2013'
        arguments = ArgParseMock(**self.args)
        timelog_report = TimelogReport(arguments)
        self.assertEqual('====== Day 24 =======' in timelog_report.run(),
                         True)

    def test_dates_price(self):
        self.args['start_date'] = '24/4/2013'
        self.args['end_date'] = '25/4/2013'
        self.args['price'] = True
        self.args['client'] = 'project1'
        arguments = ArgParseMock(**self.args)
        timelog_report = TimelogReport(arguments)
        self.assertEqual('Total amount: 180.00' in timelog_report.run(),
                         True)

    def test_dates_tasks(self):
        self.args['start_date'] = '26/4/2013'
        self.args['end_date'] = '27/4/2013'
        self.args['tasks'] = True
        self.args['client'] = 'project1'
        arguments = ArgParseMock(**self.args)
        timelog_report = TimelogReport(arguments)
        self.assertEqual('* [X] Task completed' in timelog_report.run(),
                         True)

if __name__ == '__main__':
    unittest.main()
