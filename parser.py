#!/usr/bin/python3
import re
import json
import bz2


def parse_authors():
    authors = dict()
    author_attr = ['name', 'paperCount', 'citationCount']

    with open('data/authors_selection_1000.nt', 'r') as f:
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
                    authors[matched_line.group(1)]['papers'] = list()
                authors[matched_line.group(1)][matched_line.group(2)] = (
                    matched_line.group(3)
                )

    with open('data/parsed_authors_1000.json', 'w') as outfile:
        json.dump(authors, outfile, indent=4)

    print('Successfully parsed {} authors'.format(len(authors)))


def parse_papers():
    papers = dict()
    paper_attr = ['title', 'publicationDate', 'referenceCount',
                  'citationCount', 'estimatedCitationCount']

    with open('data/papers_selection.nt', 'r') as f:
        for line in f.readlines():
            matched_line = re.search(
                '^<.*/([0-9]+?)> <.*/([a-z, A-Z]+?)> "(.+?)"\^\^<.*>', line
            )

            # TODO: maybe convert id and counts to int
            if matched_line:
                if matched_line.group(2) not in paper_attr:
                    continue

                if matched_line.group(1) not in papers:
                    papers[matched_line.group(1)] = {
                        'fieldsOfStudy': list(),
                        'parentFieldsOfStudy': list()
                    }

                papers[matched_line.group(1)][matched_line.group(2)] = (
                    matched_line.group(3)
                )

    with open('data/parsed_papers.json', 'w') as outfile:
        json.dump(papers, outfile, indent=4)

    print('Successfully parsed {} papers'.format(len(papers)))


def parse_fields_of_study():
    fields = dict()
    fields_attr = ['name', 'level']

    with open('data/FieldsOfStudy.nt', 'r') as f:
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

    with open('data/parsed_fields_of_study.json', 'w') as outfile:
        json.dump(fields, outfile, indent=4)

    print('Successfully parsed {} fields of study'.format(len(fields)))


def build_fields_hierarchy():
    hierarchy = dict()

    with open('data/FieldOfStudyChildren.nt', 'r') as f:
        for line in f.readlines():

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
    with open('data/parsed_fields_of_study.json') as fields_file:
        fields = json.load(fields_file)

    hierarchy = build_fields_hierarchy()

    for child, parents in hierarchy.items():
        add_parents(child, parents, hierarchy, fields)

    for field_id, field in fields.items():
        field['parentFields'] = list(set(field['parentFields']))

    with open('data/parsed_fields_of_study.json', 'w') as outfile:
        json.dump(fields, outfile, indent=4)


def match_papers_and_fields_of_study():
    with open('data/parsed_papers.json') as papers_file:
        papers = json.load(papers_file)

    with open('data/parsed_fields_of_study.json') as fields_file:
        fields = json.load(fields_file)

    with bz2.open('data/PaperFieldsOfStudy.nt.bz2', 'rt') as f:
        for line in f:
            matched_line = re.match(
                '^<.*/([0-9]+?)> <.*> <.*/([0-9]+?)>', line
            )

            # TODO: fix parentFieldsOfStudy so that it contains only the fields
            #  which are not present in fieldsOfStudy
            if matched_line.group(1) in papers:
                papers[matched_line.group(1)]['fieldsOfStudy'].append(
                    fields[matched_line.group(2)]['name']
                )
                # papers[matched_line.group(1)]['parentFieldsOfStudy'] += (
                #     fields[matched_line.group(2)]['parentFields']
                # )

                # papers[matched_line.group(1)]['parentFieldsOfStudy'] = list(
                #     set(papers[matched_line.group(1)]['parentFieldsOfStudy'])
                # )

                print(matched_line.group(1), matched_line.group(2))

    with open('data/parsed_papers_v3.json', 'w') as outfile:
        json.dump(papers, outfile, indent=4)


def match_papers_and_authors():
    with open('data/parsed_authors_1000.json') as authors_file:
        authors = json.load(authors_file)

    with open('data/parsed_papers_1000.json') as papers_file:
        papers = json.load(papers_file)

    print('Successfully loaded parsed files')
    with bz2.open('data/PaperAuthorAffiliations.nt.bz2', 'rt') as f:
        for line in f:
            m = re.match('^<.*/([0-9]+?)> <.*> <.*/([0-9]+?)>', line)

            if m.group(1) in papers and m.group(2) in authors:
                print('pair found with author {} and paper {}'.format(
                    m.group(2), m.group(1)))

                authors[m.group(2)]['papers'].append(papers[m.group(1)])

    with open('data/parsed_authors_v2_1000.json', 'w') as outfile:
        json.dump(authors, outfile, indent=4)


if __name__ == '__main__':
    # TODO: save the parsed data as list of.json files or .txt instead of one
    #  large .json

    match_papers_and_authors()
