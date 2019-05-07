#!/usr/bin/env python
# coding: utf-8

import sys
import re
from Levenshtein import ratio, distance

# from fuzzy wuzzy string processing
PY3 = sys.version_info[0] == 3
bad_chars = str("").join([chr(i) for i in range(128, 256)])  # ascii dammit!
if PY3:
    translation_table = dict((ord(c), None) for c in bad_chars)
    unicode = str

def asciionly(s):
    if PY3:
        return s.translate(translation_table)
    else:
        return s.translate(None, bad_chars)


def asciidammit(s):
    if type(s) is str:
        return asciionly(s)
    elif type(s) is unicode:
        return asciionly(s.encode('ascii', 'ignore'))
    else:
        return asciidammit(unicode(s))

regex = re.compile(r"(?ui)\W")


def _sort_process(s):
    # remove non-ascii, lowercase, remove all but letters and numbers, remove whitespace
    s = regex.sub(" ", asciidammit(s).lower()).strip()
    return u" ".join(sorted(s.split(' '))).strip()

def sort_process_strings(strlist):
    if isinstance(strlist, str):
        return _sort_process(strlist)
    elif isinstance(strlist, list):
        return [_sort_process(s) for s in strlist]
    else:
        return False


def sort_ratio_similarity(s1,s2):
    # str.lower, str.strip
    s1, s2 = sort_process_strings([s1,s2])
    return  (s1,s2)



