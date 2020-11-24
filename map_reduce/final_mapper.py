#!/usr/bin/python
import sys
import json
import copy

infile = sys.stdin

for line in infile:
    line = json.loads(line)

    for i, author in enumerate(line['authors']):
        author_id = author['id']
        print(author_id + '\t' + json.dumps(author))

        line_copy = copy.deepcopy(line)
        del line_copy['authors'][i]

        coauthors = [x['name'] for x in line_copy['authors']]
        del line_copy['authors']

        line_copy['coauthors'] = coauthors
        print(author_id + '-\t' + json.dumps(line_copy))
