#!/usr/bin/python
import sys
import json
from collections import OrderedDict

paper = None
current_paper = None
current_paper_info = dict()

key_order = ['id', 'title', 'publicationDate', 'referenceCount',
             'citationCount', 'estimatedCitationCount']

for line in sys.stdin:
    paper, paper_info = line.strip().split('\t', 1)
    paper_info = json.loads(paper_info)

    if current_paper == paper:
        current_paper_info.update(paper_info)

    else:
        if current_paper:
            current_paper_info.update({'id': current_paper})
            ordered_paper_info = OrderedDict()
            for key in key_order:
                if key in current_paper_info:
                    ordered_paper_info[key] = current_paper_info[key]

            print(json.dumps(ordered_paper_info))

        current_paper = paper
        current_paper_info = paper_info

# last paper
if current_paper == paper:
    current_paper_info.update({'id': current_paper})
    ordered_paper_info = OrderedDict()
    for key in key_order:
        if key in current_paper_info:
            ordered_paper_info[key] = current_paper_info[key]

    print(json.dumps(ordered_paper_info))
