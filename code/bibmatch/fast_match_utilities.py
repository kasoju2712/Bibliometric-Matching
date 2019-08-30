import numpy as np
import pandas as pd
from itertools import product
from Levenshtein import ratio


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


   # 7 Does any of the first names in the required set not exist in first names of matching set ?
    vector[6] = -int(1 if any(True for x in list(author2.full_first_names) if x not in list(author1.full_first_names))==True else 0)
    
    return (sum(vector))

def coauthor_matching_vector(author1, author2):

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

   # 7 Does any of the (first names+first initials) in the required set not exist in (first names+first initials) of matching set ?
    vector[6] = -int(1 if any(True for x in list(author2.full_first_names.union(author2.first_initials)) if x not in list(author1.full_first_names.union(author1.first_initials)))==True else 0)
    return (sum(vector))

def matching_articles(author1, author2, similarity_threshold=0.75, return_count = False):
    '''
    use Sorted Levenshtein distance to determine if at least one article title is similar
    '''
    count = 0
    if len(author1.article_titles)>0 and len(author2.article_titles)>0:
        for a1, a2 in product(author1.article_titles, author2.article_titles):
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
    matched_coauthors=[]
    if len(author1.coauthor_list)>0 and len(author2.coauthor_list)>0:
        for a1, a2 in product(author1.coauthor_list, author2.coauthor_list):
            # first check the last names
            if len(a1.full_last_names.intersection(a2.full_last_names)) > 0:
                # then use the decision vector
                if coauthor_matching_vector(a1, a2)>= 1:
                    if return_count:
                        matched_coauthors.append((a1.all_names)[0])
                    else:
                        return True
    return len(set(matched_coauthors))

def matching_affiliations(author1, author2, similarity_threshold=0.75, return_count = False):
    '''
    use Sorted Levenshtein distance to determine if at least one affiliation is similar
    '''
    count=0
    if len(author1.institutions)>0 and len(author2.institutions)>0:
        for a1, a2 in product(author1.institutions, author2.institutions):
            if ratio(a1, a2) >= similarity_threshold:
                if return_count:
                    count += 1
                else:
                    return True
    return count


def combine_match_result(author1, author2):
    return pd.Series((matching_coauthors(author1,author2,True),matching_affiliations(author1,author2,0.75,True),matching_articles(author1,author2,0.75,True)))



