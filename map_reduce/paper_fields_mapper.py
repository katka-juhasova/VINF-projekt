#!/usr/bin/python
import sys
import re
import json

infile = sys.stdin

for line in infile:
    line = json.loads(line)

    if 'paperId' in line:
        paper = line['paperId']
        field = {'field': line['fieldName']}
        print(paper + '\t' + json.dumps(field))

    else:
        paper = line['id']
        paper_info = line
        print(paper + '\t' + json.dumps(paper_info))
