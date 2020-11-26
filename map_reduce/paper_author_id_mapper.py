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
        author = matched_pair.group(2)
        print(author + '\t1\t' + paper)

    else:
        author = json.loads(line)
        author_id = author['id']
        del author['id']
        print(author_id + '\t0\t' + json.dumps(author))
