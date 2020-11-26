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
author_key_order = ['id', 'name', 'paperCount', 'citationCount']

# 0: paper
# 1: author
for line in sys.stdin:
    paper, type, info = line.strip().split('\t', 2)
    info = json.loads(info)

    if current_paper == paper:
        if 'title' in info:
            # NOTE: the code should never get here, if it does get here it just
            # multiple records for paper since the ids are matching
            continue

        else:
            if 'authors' not in current_paper_info:
                current_paper_info['authors'] = list()

            ordered_author_info = OrderedDict()
            for key in author_key_order:
                if key in info:
                    ordered_author_info[key] = info[key]

            current_paper_info['authors'].append(ordered_author_info)

    else:
        if current_paper:
            ordered_info = OrderedDict()
            # we have paper with or without authors
            if 'title' in current_paper_info:
                for key in key_order:
                    if key in current_paper_info:
                        ordered_info[key] = current_paper_info[key]

            # we have author which doesn't have any paper
            else:
                for key in author_key_order:
                    if key in current_paper_info:
                        ordered_info[key] = current_paper_info[key]
            print(json.dumps(ordered_info))

        current_paper = paper
        current_paper_info = info

# last paper
if current_paper == paper:
    ordered_info = OrderedDict()
    # we have paper with or without authors
    if 'title' in current_paper_info:
        for key in key_order:
            if key in current_paper_info:
                ordered_info[key] = current_paper_info[key]

    # we have author which doesn't have any paper
    else:
        for key in author_key_order:
            if key in current_paper_info:
                ordered_info[key] = current_paper_info[key]
    print(json.dumps(ordered_info))
