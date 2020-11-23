#!/usr/bin/python
import sys
import re
import json

infile = sys.stdin

for line in infile:
    matched_line = re.search('^<.*/([0-9]+?)> <.*/name> "(.+?)"\^\^<.*>', line)

    if matched_line:
        field = matched_line.group(1)
        field_info = {'name': matched_line.group(2)}
        print(field + '\t' + json.dumps(field_info))
