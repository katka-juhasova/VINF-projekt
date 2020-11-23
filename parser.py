import re
import json
import bz2
from itertools import permutations
from whoswho import who


def parse_authors(infile: str, outfile: str):
    authors = dict()
    author_attr = ['name', 'paperCount', 'citationCount']

    with open(infile, 'r') as f:
        for line in f.readlines():
            matched_line = re.search(
                '^<.*/([0-9]+?)> <.*/([a-z, A-Z]+?)> "(.+?)"\^\^<.*>', line
            )

            # TODO: maybe convert id, paperCount and citationCount to int
            if matched_line:
                if matched_line.group(2) not in author_attr:
                    continue

                if matched_line.group(1) not in authors:
                    authors[matched_line.group(1)] = dict()
                    # authors[matched_line.group(1)]['papers'] = list()
                authors[matched_line.group(1)][matched_line.group(2)] = (
                    matched_line.group(3)
                )

    with open(outfile, 'w') as f:
        json.dump(authors, f, indent=4)

    print('Successfully parsed {} authors'.format(len(authors)))


def parse_papers(infile: str, outfile: str):
    papers = dict()
    paper_attr = ['title', 'publicationDate', 'referenceCount',
                  'citationCount', 'estimatedCitationCount']

    with open(infile, 'r') as f:
        for line in f.readlines():
            matched_line = re.search(
                '^<.*/([0-9]+?)> <.*/([a-z, A-Z]+?)> "(.+?)"\^\^<.*>', line
            )

            # TODO: maybe convert id and counts to int
            if matched_line:
                if matched_line.group(2) not in paper_attr:
                    continue

                if matched_line.group(1) not in papers:
                    papers[matched_line.group(1)] = dict()
                papers[matched_line.group(1)][matched_line.group(2)] = (
                    matched_line.group(3)
                )

    with open(outfile, 'w') as f:
        json.dump(papers, f, indent=4)

    print('Successfully parsed {} papers'.format(len(papers)))


def parse_fields_of_study():
    fields = dict()
    fields_attr = ['name', 'level']

    with open('data/FieldsOfStudy.nt.bz2', 'r') as f:
        for line in f.readlines():

            matched_line = re.search(
                '^<.*/([0-9]+?)> <.*/([a-z, A-Z]+?)> "(.+?)"\^\^<.*>', line
            )

            # TODO: maybe convert id and level to int
            if matched_line:
                if matched_line.group(2) not in fields_attr:
                    continue

                if matched_line.group(1) not in fields:
                    fields[matched_line.group(1)] = dict()
                    fields[matched_line.group(1)]['parentFields'] = list()
                fields[matched_line.group(1)][matched_line.group(2)] = (
                    matched_line.group(3)
                )

    with open('data/parsed_fields_of_study.json', 'w') as f:
        json.dump(fields, f, indent=4)

    print('Successfully parsed {} fields of study'.format(len(fields)))


def build_fields_hierarchy() -> dict:
    hierarchy = dict()

    with bz2.open('data/FieldOfStudyChildren.nt.bz2', 'rt') as f:
        for line in f:

            matched_line = re.search(
                '^<.*/([0-9]+?)> <.*> <.*/([0-9]+?)>', line
            )

            # TODO: maybe convert id to int
            if matched_line:
                if matched_line.group(2) not in hierarchy:
                    hierarchy[matched_line.group(2)] = list()

                if matched_line.group(1) not in hierarchy:
                    hierarchy[matched_line.group(1)] = list()

                # child has link to its parent
                hierarchy[matched_line.group(1)].append(matched_line.group(2))

    return hierarchy


def add_parents(child, parents, hierarchy, fields):
    # it's ok even for the root fields, they have empty list of parents so
    # the loop would be executed 0 times
    for parent in parents:
        fields[child]['parentFields'].append(fields[parent]['name'])

        # all fields are contained in hierarchy, the ones without parent simply
        # have empty list as value
        if hierarchy[parent]:
            add_parents(child, hierarchy[parent], hierarchy, fields)


def parse_fields_of_study_children():
    with open('data/parsed_fields_of_study.json', 'r') as f:
        fields = json.load(f)

    hierarchy = build_fields_hierarchy()

    for child, parents in hierarchy.items():
        add_parents(child, parents, hierarchy, fields)

    for field_id, field in fields.items():
        field['parentFields'] = list(set(field['parentFields']))

    with open('data/parsed_fields_of_study.json', 'w') as outfile:
        json.dump(fields, outfile, indent=4)

    print('Successfully parsed fields of study children')


def match_papers_and_fields_of_study(infile: str, outfile: str):
    with open(infile, 'r') as f:
        papers = json.load(f)

    with open('data/parsed_fields_of_study.json') as f:
        fields = json.load(f)

    with bz2.open('data/PaperFieldsOfStudy.nt.bz2', 'rt') as bzf:
        for line in bzf:
            matched_line = re.match(
                '^<.*/([0-9]+?)> <.*> <.*/([0-9]+?)>', line
            )

            if matched_line.group(1) in papers:
                if 'fieldsOfStudy' not in papers[matched_line.group(1)]:
                    papers[matched_line.group(1)]['fieldsOfStudy'] = list()

                papers[matched_line.group(1)]['fieldsOfStudy'].append(
                    fields[matched_line.group(2)]['name']
                )

                print(matched_line.group(1), matched_line.group(2))

    with open(outfile, 'w') as f:
        json.dump(papers, f, indent=4)

    print('Successfully matched papers and fields of study')


def match_papers_and_authors(papers_infile: str, authors_infile: str,
                             outfile: str):

    with open(authors_infile, 'r') as f:
        authors = json.load(f)

    with open(papers_infile, 'r') as f:
        papers = json.load(f)

    print('Successfully loaded parsed files')

    with bz2.open('data/PaperAuthorAffiliations.nt.bz2', 'rt') as bzf:
        for line in bzf:
            match = re.match('^<.*/([0-9]+?)> <.*> <.*/([0-9]+?)>', line)

            if match.group(1) in papers and match.group(2) in authors:
                print('pair found with author {} and paper {}'.format(
                    match.group(2), match.group(1)))

                if 'papers' not in authors[match.group(2)]:
                    authors[match.group(2)]['papers'] = list()

                authors[match.group(2)]['papers'].append(
                    papers[match.group(1)])

    with open(outfile, 'w') as f:
        json.dump(authors, f, indent=4)

    print('Successfully matched papers and authors')


def match_authors(author1: dict, author2: dict) -> bool:
    # NOTE: all the attributes are ascii encoded
    # TODO: decide whether I wanna deal with degrees, e.g. remove titles while
    #  comparing the names

    if author1['name'] == author2['name']:
        print('matching same {} ({}) and {} ({})'.format(
            author1['id'], author1['name'], author2['id'], author2['name']))
        return True

    # match according to the package whoswho
    # case insensitive
    # different name formats
    # handles excess dots and commas
    if who.match(author1['name'], author2['name']):
        print('matching on whoswho {} ({}) and {} ({})'.format(
            author1['id'], author1['name'], author2['id'], author2['name']))
        return True

    # remove excess spaces, separating dots and commas
    mod_author1 = author1['name'].lower().split()
    mod_author1 = ' '.join(
        filter(None, [x.strip('.,') for x in mod_author1])
    )
    mod_author2 = author2['name'].lower().split()
    mod_author2 = ' '.join(
        filter(None, [x.strip('.,') for x in mod_author2])
    )

    # match after removing dots and commas
    if mod_author1 == mod_author2:
        print('matching on strip/split {} ({}) and {} ({})'.format(
            author1['id'], author1['name'], author2['id'], author2['name']))
        return True

    # at this point both names split into lists must be of same length
    if len(mod_author1) != len(mod_author2):
        return False

    # match permutations
    author1_perm = permutations(mod_author1.split())
    author1_perm = [' '.join(x) for x in author1_perm]
    if mod_author2 in author1_perm:
        print('matching on permutation {} ({}) and {} ({})'.format(
            author1['id'], author1['name'], author2['id'], author2['name']))
        return True

    return False


def merge_authors(infile: str, outfile: str):
    with open(infile, 'r') as f:
        authors_dict = json.load(f)

    authors_list = list()
    for index, author in authors_dict.items():
        authors_list.append({'id': index,
                             'name': author['name'],
                             'paperCount': author['paperCount'],
                             'citationCount': author['citationCount'],
                             'papers': author['papers'],
                             'other_ids': list(),
                             'other_names': list(),
                             'other_paperCount': list(),
                             'other_citationCount': list()
                             })

    i = 0
    while i < len(authors_list) - 1:
        print('trying to match {} ({})'.format(
            authors_list[i]['id'], authors_list[i]['name']))

        j = i + 1
        while j < len(authors_list) - 1:
            match = match_authors(authors_list[i], authors_list[j])
            if match:
                fields1 = list()
                for paper in authors_list[i]['papers']:
                    fields1 += paper['fieldsOfStudy']

                fields2 = list()
                for paper in authors_list[j]['papers']:
                    fields2 += paper['fieldsOfStudy']

                matched_fields = list(set(fields1).intersection(fields2))
                if matched_fields:
                    authors_list[i]['other_ids'].append(authors_list[j]['id'])
                    authors_list[i]['other_names'].append(
                        authors_list[j]['name'])
                    authors_list[i]['papers'] += authors_list[j]['papers']
                    authors_list[i]['other_paperCount'].append(
                        authors_list[j]['paperCount'])
                    authors_list[i]['other_citationCount'].append(
                        authors_list[j]['citationCount'])
                    del authors_list[j]
                else:
                    j += 1

            else:
                j += 1

        print('==================================================')
        i += 1

    new_dict = dict()
    for author in authors_list:
        new_dict[author['id']] = {
            'otherId': author['other_ids'],
            'name': author['name'],
            'otherNames': author['other_names'],
            'paperCount': author['paperCount'],
            'otherPaperCount': author['other_paperCount'],
            'citationCount': author['citationCount'],
            'otherCitationCount': author['other_citationCount'],
            'papers': author['papers']
        }

    with open(outfile, 'w') as f:
        json.dump(new_dict, f, indent=4)


def main():
    # TODO: save save the parsed data as .jsonlines and .bz

    merge_authors('data/parsed_authors_v2_1000.json',
                  'data/parsed_authors_v3_1000.json')

    # TODO: update parse_papers() or add function so that each paper contains
    #  ids of authors
    # TODO: remove parentFieldsOfStudy
    # TODO: parse all papers written by authors from author_ids_1000.txt
    # TODO: merge those papers with authors from parsed_authors_v2_1000.json
    # TODO: merge that new authors file
    # TODO: convert that file to jsonlines
    # TODO: handle duplicate papers
    # TODO: add matching on same author groups
    # TODO: clean up the repository
    # TODO: create index for searching in data                             
