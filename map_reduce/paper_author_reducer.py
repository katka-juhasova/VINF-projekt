#!/usr/bin/python
import sys
import json
from collections import OrderedDict

paper = None
current_paper = None
current_paper_info = dict()

key_order = ['id', 'title', 'publicationDate', 'referenceCount',
             'citationCount', 'estimatedCitationCount', 'fieldsOfStudy',
             'authors']
authors_key_order = ['id', 'name', 'paperCount', 'citationCount']

for line in sys.stdin:
    paper, info = line.strip().split('\t', 1)
    paper = paper.strip('-')
    info = json.loads(info)

    if current_paper == paper:
        if 'title' in info:
            # NOTE: the code should never get here
            current_paper_info.update(info)

        else:
            if 'authors' not in current_paper_info:
                current_paper_info['authors'] = list()

            ordered_author_info = OrderedDict()
            for key in authors_key_order:
                if key in info:
                    ordered_author_info[key] = info[key]

            current_paper_info['authors'].append(ordered_author_info)

    else:
        if current_paper:
            ordered_paper_info = OrderedDict()
            for key in key_order:
                if key in current_paper_info:
                    ordered_paper_info[key] = current_paper_info[key]

            print(json.dumps(ordered_paper_info))

        current_paper = paper
        current_paper_info = info

# last paper
if current_paper == paper:
    ordered_paper_info = OrderedDict()
    for key in key_order:
        if key in current_paper_info:
            ordered_paper_info[key] = current_paper_info[key]

    print(json.dumps(ordered_paper_info))
