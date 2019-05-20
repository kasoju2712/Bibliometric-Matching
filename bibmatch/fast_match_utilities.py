#!/usr/bin/env python
# coding: utf-8

import numpy as np
from itertools import product
from bibmatch.authorclass import author
from bibmatch.clean_data import asciidammit, sort_process_strings
from Levenshtein import ratio


def sort_ratio_similarity(s1,s2):
    # str.lower, str.strip
    s1, s2 = sort_process_strings([s1,s2])
    return  ratio(s1,s2)



def exact_lastname_match(a1, a2):
    return len(a1.full_last_names.intersection(a2.full_last_names)) > 0

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



def matching_articles(author1, author2, similarity_threshold=0.75, return_count = False):
    '''
    use Sorted Levenshtein distance to determine if at least one article title is similar
    '''
    count = 0
    for a1, a2 in product(author1.processed_article_titles, author2.processed_article_titles):
        if ratio(a1, a2) >= similarity_threshold:
            if return_count:
                count += 1
            else:
                return True
    return count

def matching_coauthors(author1, author2, return_count = False):
    '''
    use LastNames and the decision vector to determine if at least one co-author is similar
    '''
    count = 0
    for a1, a2 in product(author1.coauthor_list, author2.coauthor_list):
        # first check the last names and then use the decision vector
        if exact_lastname_match(a1, a2) and author_matching_vector(a1, a2).sum() >= 1:
            if return_count:
                count += 1
            else:
                return True
    return count

def matching_affiliations(author1, author2, similarity_threshold=0.75, return_count = False):
    '''
    use Sorted Levenshtein distance to determine if at least one affiliation is similar
    '''
    for a1, a2 in product(author1.processed_institutions, author2.processed_institutions):
        if ratio(a1, a2) >= similarity_threshold:
            if return_count:
                count += 1
            else:
                return True
    return count

def find_best_match(author_list1, author_list2, verbose = True):
    # check objects are author lists and not individual authors
    if isinstance(author_list1, author):
        author_list1 = [author_list1]
    if isinstance(author_list2, author):
        author_list2 = [author_list2]

    # now pick the shorter list
    if len(author_list1) >= len(author_list2):
        short_list, long_list = author_list2, author_list1
    else:
        short_list, long_list = author_list1, author_list2

    matches = {}
    for desired_author in short_list:
        if verbose: print("Starting: ", desired_author.prefered_name)
        # do a first pass based on last name
        first_pass =[a for a in long_list if exact_lastname_match(a, desired_author)]
        if verbose: print(len(first_pass), 'matches on last name')





