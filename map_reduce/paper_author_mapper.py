#!/usr/bin/python
import sys
import json

infile = sys.stdin

for line in infile:
    line = json.loads(line)

    if 'paperId' in line:
        paper = line['paperId']
        author = line.copy()
        author['id'] = author['authorId']
        del author['paperId']
        del author['authorId']
        print(paper + '\t1\t' + json.dumps(author))

    else:
        paper = line['id']
        paper_info = line
        print(paper + '\t0\t' + json.dumps(paper_info))
