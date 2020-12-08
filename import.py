from elasticsearch import Elasticsearch
from elasticsearch import helpers
from os import listdir
import json
import html

BULK_SIZE = 3000
INDEX = 'authors'


def get_actions_from_line(line: dict) -> list:
    if 'name' not in line:
        return list()

    author_id = line['id']
    papers = list()

    if 'papers' in line:
        for paper in line['papers']:
            new_paper = {
                'title': html.unescape(paper['title']),

                'fields_of_study': (
                    [{'name': field}
                     for field in paper['fieldsOfStudy']
                     ] if 'fieldsOfStudy' in paper else None),

                'coauthors': (
                    [{'name': html.unescape(coauthor)}
                     for coauthor in paper['coauthors']
                     ] if 'coauthors' in paper else None)
            }

            if new_paper['coauthors']:
                new_paper['coauthors'] = new_paper['coauthors']

            papers.append(new_paper)

    author = {
        'name': html.unescape(line['name']),
        'other_names': None,
        'papers': papers or None
    }

    actions = [{
        '_index': INDEX,
        '_id': author_id,
        '_source': author
    }]

    return actions


def main():
    es = Elasticsearch()

    files = listdir('./data/out')

    for i, file in enumerate(files):
        print('Processing file {} ({}/{})'.format(file, i + 1, len(files)))

        with open('./data/out/{}'.format(file)) as f:
            line_count = 0
            bulk_actions = list()

            # process line, when the bulk contains more than 3000 authors add
            # those authors to the index
            for line in f:
                line = json.loads(line)
                bulk_actions += get_actions_from_line(line)
                line_count += 1

                if len(bulk_actions) >= BULK_SIZE:
                    print('Bulk after line {}, bulk size: {}'.format(
                        line_count, len(bulk_actions)))

                    helpers.bulk(es, bulk_actions)
                    bulk_actions.clear()

            # add last bulk which is probably smaller than 3000
            if bulk_actions:
                print('Bulk after line {}, bulk size: {}'.format(
                    line_count, len(bulk_actions)))
                helpers.bulk(es, bulk_actions)


if __name__ == '__main__':
    main()
