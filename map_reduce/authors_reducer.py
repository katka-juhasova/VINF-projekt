#!/usr/bin/python
import sys
import json
from collections import OrderedDict

author = None
current_author = None
current_author_info = dict()

key_order = ['id', 'name', 'paperCount', 'citationCount']

for line in sys.stdin:
    author, author_info = line.strip().split('\t', 1)
    author_info = json.loads(author_info)

    if current_author == author:
        current_author_info.update(author_info)

    else:
        if current_author:
            current_author_info.update({'id': current_author})
            ordered_author_info = OrderedDict()
            for key in key_order:
                if key in current_author_info:
                    ordered_author_info[key] = current_author_info[key]

            print(json.dumps(ordered_author_info))

        current_author = author
        current_author_info = author_info

# last author
if current_author == author:
    current_author_info.update({'id': current_author})
    ordered_author_info = OrderedDict()
    for key in key_order:
        if key in current_author_info:
            ordered_author_info[key] = current_author_info[key]

    print(json.dumps(ordered_author_info))
