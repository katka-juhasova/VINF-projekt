#!/usr/bin/python3
import json
import bz2
import re


def get_author_ids():
    with open('data/parsed_papers_1000.json') as papers_file:
        papers = json.load(papers_file)

    author_ids = list()

    with bz2.open('data/PaperAuthorAffiliations.nt.bz2', 'rt') as f:
        for line in f:
            matched_line = re.match(
                '^<.*/([0-9]+?)> <.*> <.*/([0-9]+?)>', line
            )

            if matched_line.group(1) in papers:
                print('got paper {} and adding author {}'.format(
                    matched_line.group(1), matched_line.group(2)))
                author_ids.append(matched_line.group(2))

    with open('data/author_ids_1000.txt', 'w') as f:
        f.write(json.dumps(author_ids))


def get_authors():
    with open('data/author_ids.txt', 'r') as f:
        author_ids = json.loads(f.read())

    author_lines = list()

    with bz2.open('Authors.nt.bz2', 'rt') as f:
        for line in f:
            matched_line = re.match('^<.*/([0-9]+?)> <.*> .$', line)

            if matched_line and matched_line.group(1) in author_ids:
                print('appending author {}'.format(matched_line.group(1)))
                author_lines.append(line)

    with open('data/authors_selection_v2.nt', 'w') as outfile:
        outfile.write(''.join(author_lines))


def get_1000_authors():
    with open('data/author_ids_1000.txt') as authors_file:
        author_ids = json.load(authors_file)

    author_lines = list()

    with bz2.open('data/Authors.nt.bz2', 'rt') as f:
        for line in f:
            matched_line = re.match('^<.*/([0-9]+?)> <.*> .$', line)

            if matched_line and matched_line.group(1) in author_ids:
                print('appending author {}'.format(matched_line.group(1)))
                author_lines.append(line)

    with open('data/authors_selection_1000.nt', 'w') as outfile:
        outfile.write(''.join(author_lines))


def get_1000_papers():
    with open('data/parsed_papers_v2.json') as papers_file:
        papers = json.load(papers_file)

    papers_1000 = dict()
    count = 0

    for key, value in papers.items():
        papers_1000[key] = value
        count += 1
        print(count)
        if count > 1000:
            break

    with open('data/parsed_papers_1000.json', 'w') as outfile:
        json.dump(papers_1000, outfile, indent=4)
