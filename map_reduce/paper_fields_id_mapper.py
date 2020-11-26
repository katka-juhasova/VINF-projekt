#!/usr/bin/python
import sys
import re
import json

infile = sys.stdin

for line in infile:
    matched_pair = re.search(
        '^<.*/([0-9]+?)> <.*> <.*/([0-9]+?)>', line
    )

    if matched_pair:
        paper = matched_pair.group(1)
        field = matched_pair.group(2)
        print(field + '\t1\t' + paper)

    else:
        field = json.loads(line)
        field_id = field['id']
        del field['id']
        print(field_id + '\t0\t' + json.dumps(field))
