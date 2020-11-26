#!/usr/bin/python
import sys
import json
from collections import OrderedDict

field = None
current_field = None
current_field_info = dict()

key_order = ['paperId', 'fieldId', 'fieldName']

for line in sys.stdin:
    field, type, info = line.strip().split('\t', 2)

    if current_field == field:
        if not info.isdigit():
            # it should never get to this part of code
            info = json.loads(info)
            current_field_info = {'fieldId': field, 'fieldName': info['name']}

        else:
            output_dict = OrderedDict()
            output_dict['paperId'] = info
            output_dict['fieldId'] = current_field_info['fieldId']
            output_dict['fieldName'] = current_field_info['fieldName']
            print(json.dumps(output_dict))

    else:
        if not info.isdigit():
            current_field = field
            info = json.loads(info)
            current_field_info = {'fieldId': field, 'fieldName': info['name']}
