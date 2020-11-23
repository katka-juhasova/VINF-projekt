#!/usr/bin/python
import sys
import re
import json

current_paper = None
previous_paper = None
paper_info = dict()

paper_attr = ['title', 'publicationDate', 'referenceCount',
              'citationCount', 'estimatedCitationCount']

infile = sys.stdin

for line in infile:
    matched_line = re.search(
        '^<.*/([0-9]+?)> <.*/([a-z, A-Z]+?)> "(.+?)"\^\^<.*>', line
    )

    if matched_line:
        if matched_line.group(2) not in paper_attr:
            continue

        current_paper = matched_line.group(1)

        if previous_paper != current_paper:
            if previous_paper:
                print(previous_paper + '\t' + json.dumps(paper_info))

            previous_paper = current_paper
            paper_info = {matched_line.group(2): matched_line.group(3)}

        else:
            paper_info.update({matched_line.group(2): matched_line.group(3)})

# print last paper
if previous_paper == current_paper:
    print(current_paper + '\t' + json.dumps(paper_info))
