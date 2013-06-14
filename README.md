Timelog
=======

This project is a text report generator for the gtimelog
text format.

We should be able to generate weekly, monthly or daily reports
using your timelog.txt file and generate it from vimwiki, which is the one I am using
for the timetrack.

Example:

    python2 timelog.py --start-date 1/1/2013 --end-date 30/6/2013 --order-by week --tasks

Output:

    ====== Week 17 =======

    Project1 : 9 h 30 min

    * [X] Task completed


    Total time: 9 h 30 min
    ====== Week 18 =======

    Project3 : 0 h 30 min
    Project2 : 3 h 36 min

    * [.] Task started


    Total time: 4 h 6 min


TODO
----

- [ ] Make easier configuration, move it to a config file
- [ ] Create a Python package
