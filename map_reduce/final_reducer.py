#!/usr/bin/python
import sys
import json
from collections import OrderedDict

author = None
current_author = None
current_author_info = dict()

author_key_order = ['id', 'name', 'paperCount', 'citationCount', 'papers']
paper_key_order = ['id', 'title', 'publicationDate', 'referenceCount',
                   'citationCount', 'estimatedCitationCount', 'fieldsOfStudy',
                   'coauthors']

for line in sys.stdin:
    author, type, info = line.strip().split('\t', 2)
    info = json.loads(info)

    if current_author == author:
        if 'name' in info:
            # there are as many lines with purely author info as there are
            # papers written by that author so as soon as we get 1st author
            # info all the others (which are the same) can be ignored
            continue

        if 'papers' not in current_author_info:
            current_author_info['papers'] = list()

        ordered_paper_info = OrderedDict()
        for key in paper_key_order:
            if key in info:
                ordered_paper_info[key] = info[key]

        current_author_info['papers'].append(ordered_paper_info)

    else:
        if current_author:
            ordered_author_info = OrderedDict()
            for key in author_key_order:
                if key in current_author_info:
                    ordered_author_info[key] = current_author_info[key]

            print(json.dumps(ordered_author_info))

        current_author = author
        current_author_info = info

# last author
if current_author == author:
    ordered_author_info = OrderedDict()
    for key in author_key_order:
        if key in current_author_info:
            ordered_author_info[key] = current_author_info[key]

    print(json.dumps(ordered_author_info))
