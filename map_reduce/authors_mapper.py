#!/usr/bin/python
import sys
import re
import json

current_author = None
previous_author = None
author_info = dict()

author_attr = ['name', 'paperCount', 'citationCount']

infile = sys.stdin

for line in infile:
    matched_line = re.search(
        '^<.*/([0-9]+?)> <.*/([a-z, A-Z]+?)> "(.+?)"\^\^<.*>', line
    )

    if matched_line:
        if matched_line.group(2) not in author_attr:
            continue

        current_author = matched_line.group(1)

        if previous_author != current_author:
            if previous_author:
                print(previous_author + '\t' + json.dumps(author_info))

            previous_author = current_author
            author_info = {matched_line.group(2): matched_line.group(3)}

        else:
            author_info.update({matched_line.group(2): matched_line.group(3)})

# print last author
if previous_author == current_author:
    print(current_author + '\t' + json.dumps(author_info))
