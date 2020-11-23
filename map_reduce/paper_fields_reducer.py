#!/usr/bin/python
import sys
import json
from collections import OrderedDict

paper = None
current_paper = None
current_paper_info = dict()

key_order = ['id', 'title', 'publicationDate', 'referenceCount',
             'citationCount', 'estimatedCitationCount', 'fieldsOfStudy']

for line in sys.stdin:
    paper, paper_info = line.strip().split('\t', 1)
    paper_info = json.loads(paper_info)

    if current_paper == paper:
        if len(paper_info) > 1:
            current_paper_info.update(paper_info)

        else:
            if 'fieldsOfStudy' not in current_paper_info:
                current_paper_info['fieldsOfStudy'] = list()

            current_paper_info['fieldsOfStudy'].append(paper_info['field'])

    else:
        if current_paper:
            ordered_paper_info = OrderedDict()
            for key in key_order:
                if key in current_paper_info:
                    ordered_paper_info[key] = current_paper_info[key]

            print(json.dumps(ordered_paper_info))

        current_paper = paper
        current_paper_info = paper_info

# last paper
if current_paper == paper:
    ordered_paper_info = OrderedDict()
    for key in key_order:
        if key in current_paper_info:
            ordered_paper_info[key] = current_paper_info[key]

    print(json.dumps(ordered_paper_info))

# NOTE: not all the papers have fields of study
