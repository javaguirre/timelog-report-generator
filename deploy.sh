#!/bin/bash
rsync -rav timelog/reports --delete -e ssh gigas:taikoa_reports
rsync -rav timelog/static --delete -e ssh gigas:taikoa_reports
