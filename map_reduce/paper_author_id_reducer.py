#!/usr/bin/python
import sys
import json
from collections import OrderedDict

author = None
current_author = None
current_author_info = dict()

key_order = ['authorId', 'name', 'paperCount', 'citationCount']
# + 'paperId' in the beginning

for line in sys.stdin:
    author, type, info = line.strip().split('\t', 2)

    if current_author == author:
        if not info.isdigit():
            # the code should never get here but it's here just to make sure it
            # doesn't crash
            info = json.loads(info)
            current_author_info = {'authorId': author}
            current_author_info.update(info)

        else:
            output_dict = OrderedDict()
            output_dict['paperId'] = info
            for key in key_order:
                if key in current_author_info:
                    output_dict[key] = current_author_info[key]

            print(json.dumps(output_dict))

    else:
        if not info.isdigit():
            current_author = author
            info = json.loads(info)
            current_author_info = {'authorId': author}
            current_author_info.update(info)
