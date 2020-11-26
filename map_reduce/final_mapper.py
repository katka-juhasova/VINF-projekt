#!/usr/bin/python
import sys
import json
import copy

infile = sys.stdin

for line in infile:
    line = json.loads(line)

    # line containing whole paper record
    if 'authors' in line and 'title' in line:
        for author in line['authors']:
            author_id = author['id']
            print(author_id + '\t0\t' + json.dumps(author))

            line_copy = copy.deepcopy(line)
            coauthors = [x['name'] for x in line['authors']]
            coauthors.remove(author['name'])
            if coauthors:
                line_copy['coauthors'] = coauthors
            del line_copy['authors']

            print(author_id + '\t1\t' + json.dumps(line_copy))

    # line containing author with no paper
    elif 'name' in line and 'title' not in line:
        author_id = line['id']
        print(author_id + '\t0\t' + json.dumps(line))
