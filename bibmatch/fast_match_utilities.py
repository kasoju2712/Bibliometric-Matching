#!/usr/bin/env python
# coding: utf-8

import numpy as np
from itertools import product
from bibmatch.fast_string_compare import ratio

def author_matching_vector(author1, author2):

    vector = np.zeros(7, dtype=int)

    # 1. Do the first names match?
    vector[0] = int(len(author1.full_first_names.intersection(author2.full_first_names)) > 0)

    # 2. Does a first and middle name match?
    vector[1] = int(np.logical_or(len(author1.full_middle_names.intersection(author2.full_first_names)) > 0,
                    len(author1.full_first_names.intersection(author2.full_middle_names)) > 0))

    # 3 Do the middle names match?
    vector[2] = int(len(author1.full_middle_names.intersection(author2.full_middle_names)) > 0)

    # 4 both 1 and 3
    vector[3] = int(np.logical_and(vector[0], vector[2]))

    # 5 Do the first initials match?
    vector[4] = int(len(author1.first_initials.intersection(author2.first_initials)) > 0)

    # 6 Does a first and middle initial match?
    vector[5] = int(np.logical_or(len(author1.middle_initials.intersection(author2.first_initials)) > 0,
                    len(author1.first_initials.intersection(author2.middle_initials)) > 0))

    # 7
    vector[6] = -int(np.logical_nand(vector[0], vector[1]))
    return vector



def matching_articles(author1, author2, match_threshold=0.75):
    '''
    use Sorted Levenshtein distance to determine if at least one article title is similar
    '''
    for a1, a2 in product(author1.article_titles, author2.article_titles):
        if ratio(a1, a2) >= match_threshold:
            return True
    return False

def matching_coauthors(author1, author2, match_threshold=0.75):
    '''
    use LastNames and the decision vector to determine if at least one co-author is similar
    '''
    for a1, a2 in product(author1.coauthor_list, author2.coauthor_list):
        # first check the last names
        if len(a1.full_last_names.intersection(a2.full_last_names)) > 0:
            # then use the decision vector
            if author_matching_vector(a1, a2).sum() >= 1:
                return True
    return False

def matching_affiliations(author1, author2, match_threshold=0.75):
    '''
    use Sorted Levenshtein distance to determine if at least one affiliation is similar
    '''
    for a1, a2 in product(author1.institutions, author2.institutions):
        if ratio(a1, a2) >= match_threshold:
            return True
    return False

