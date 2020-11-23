#!/usr/bin/python
import sys
import json
from collections import OrderedDict

field = None
current_field = None
current_field_info = dict()

for line in sys.stdin:
    field, field_info = line.strip().split('\t', 1)
    field_info = json.loads(field_info)

    if current_field == field:
        current_field_info.update(field_info)

    else:
        if current_field:
            current_field_info.update({'id': current_field})
            ordered_field_info = OrderedDict(
                [(key, current_field_info[key]) for key in ['id', 'name']]
            )
            print(json.dumps(ordered_field_info))

        current_field = field
        current_field_info = field_info

# last field of study
if current_field == field:
    current_field_info.update({'id': current_field})
    ordered_field_info = OrderedDict(
        [(key, current_field_info[key]) for key in ['id', 'name']]
    )
    print(json.dumps(ordered_field_info))
