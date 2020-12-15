from elasticsearch import Elasticsearch
from itertools import permutations
from whoswho import who

SEARCH_SIZE = 100
INDEX = 'authors'


def get_authors_body(search_after=None) -> dict:
    body = {
        'size': SEARCH_SIZE,
        'query': {
            'bool': {
                'must': [
                    {
                        'nested': {
                            'path': 'papers',
                            'query': {
                                'exists': {
                                    'field': 'papers'
                                }
                            }
                        }
                    }
                ]
            }
        },
        'sort': [
            {
                '_id': 'asc'
            }
        ]
    }

    if search_after:
        body['search_after'] = [search_after]

    return body


def match_authors_body(name: str, search_after=None):
    body = {
        'size': SEARCH_SIZE,
        "query": {
            "bool": {
                "must": [
                    {
                        "nested": {
                            "path": "papers",
                            "query": {
                                "exists": {
                                    "field": "papers"
                                }
                            }
                        }
                    }
                ],
                "filter": [
                    {
                        "match": {
                            "name": name
                        }
                    }
                ]
            }
        },
        'sort': [
            {
                '_id': 'asc'
            }
        ]
    }

    if search_after:
        body['search_after'] = [search_after]

    return body


def match_authors(author1: str, author2: str) -> bool:
    if author1 == author2:
        return True

    # match according to the package whoswho
    # case insensitive
    # different name formats
    # handles excess dots and commas
    if who.match(author1, author2):
        return True

    # handle the option when one of the names is just the last name
    if (len(author1.split()) == 1
            and len(author2.split()) == 2
            and (author2.lower().split()[1] == author1.lower()
                 or author2.lower().split(', ')[0] == author1.lower())):
        return True

    if (len(author2.split()) == 1
            and len(author1.split()) == 2
            and (author1.lower().split()[1] == author2.lower()
                 or author1.lower().split(', ')[0] == author2.lower())):
        return True

    # remove excess spaces, separating dots and commas
    mod_author1 = author1.lower().split()
    mod_author1 = ' '.join(
        filter(None, [x.strip('.,') for x in mod_author1])
    )
    mod_author2 = author2.lower().split()
    mod_author2 = ' '.join(
        filter(None, [x.strip('.,') for x in mod_author2])
    )

    # match after removing dots and commas
    if mod_author1 == mod_author2:
        return True

    # at this point both names split into lists must be of same length
    if len(mod_author1) != len(mod_author2):
        return False

    # match permutations
    author1_perm = permutations(mod_author1.split())
    author1_perm = [' '.join(x) for x in author1_perm]
    if mod_author2 in author1_perm:
        return True

    return False


def match_authors_list(authors1: list, authors2: list) -> bool:
    for author1 in authors1:
        for author2 in authors2:
            if match_authors(author1, author2):
                return True

    return False


def main():
    es = Elasticsearch()
    processed_authors = 0

    print('Getting initial authors batch...')
    authors = es.search(index=INDEX, body=get_authors_body())

    while authors['hits']['hits']:
        print('Processing authors from _id: {} to _id: {}'.format(
            authors['hits']['hits'][0]['sort'][0],
            authors['hits']['hits'][-1]['sort'][0]
        ))

        last_id = authors['hits']['hits'][-1]['sort'][0]
        last_match_id = None

        for author in authors['hits']['hits']:
            is_modified = False
            docs_to_delete = list()

            # get coauthors and fields of study for current author
            coauthors1 = list()
            fields1 = list()
            for paper in author['_source']['papers']:
                if paper['coauthors']:
                    coauthors1 += paper['coauthors'].split('\n')
                if paper['fields_of_study']:
                    fields1 += paper['fields_of_study'].split('\n')

            if not coauthors1 and not fields1:
                continue

            coauthors1 = list(set(coauthors1))
            fields1 = list(set(fields1))

            matched_authors = es.search(
                index=INDEX,
                body=match_authors_body(author['_source']['name'],
                                        last_match_id)
            )

            while matched_authors['hits']['hits']:
                last_match_id = matched_authors['hits']['hits'][-1]['sort'][0]

                for match in matched_authors['hits']['hits']:
                    if match['_id'] == author['_id']:
                        continue

                    is_match = match_authors(author['_source']['name'],
                                             match['_source']['name'])

                    if is_match:
                        # get all coauthors and fields of study
                        coauthors2 = list()
                        fields2 = list()
                        for paper in match['_source']['papers']:
                            if paper['coauthors']:
                                coauthors2 += paper['coauthors'].split('\n')
                            if paper['fields_of_study']:
                                fields2 += paper['fields_of_study'].split('\n')

                        if not coauthors2 and not fields2:
                            continue

                        matched_fields = list(
                            set(fields1).intersection(fields2)
                        )

                        matched_coauthors = list(
                            set(coauthors1).intersection(coauthors2)
                        )

                        if not matched_coauthors:
                            matched_coauthors = match_authors_list(coauthors1,
                                                                   coauthors2)

                        # match both coauthors and fields
                        # match fields and empty coauthors
                        # match coauthors and empty fields
                        if ((matched_coauthors and matched_fields)
                                or (matched_fields
                                    and (not coauthors1 or not coauthors2))
                                or (matched_coauthors
                                    and (not fields1 or not fields2))):

                            if not author['_source']['other_names']:
                                author['_source']['other_names'] = list()

                            author['_source']['other_names'].append(
                                {'name': match['_source']['name']})
                            author['_source']['papers'] += match['_source'][
                                'papers']

                            is_modified = True
                            docs_to_delete.append(match['_id'])

                matched_authors = es.search(
                    index=INDEX,
                    body=match_authors_body(author['_source']['name'],
                                            last_match_id)
                )

            # update author
            if is_modified:
                print('Updating document with _id: {}'.format(author['_id']))
                print('Deleting documents: {}'.format(docs_to_delete))
                es.index(index=INDEX, id=author['_id'], body=author['_source'])
                for doc in docs_to_delete:
                    es.delete(index=INDEX, id=doc)

        processed_authors += len(authors['hits']['hits'])
        print('Done processing authors {}/52847108'.format(processed_authors))
        print('Getting authors after _id: {}'.format(last_id))
        authors = es.search(index=INDEX,
                            body=get_authors_body(search_after=last_id))


if __name__ == '__main__':
    main()
