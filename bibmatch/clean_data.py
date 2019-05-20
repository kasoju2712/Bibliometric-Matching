#!/usr/bin/env python
# coding: utf-8

# In[1]:

import sys
import string
from nameparser import HumanName
import re
from unidecode import  unidecode
import unicodedata

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


def remove_punctuation(personality_name):
    personality_name=personality_name.replace("-"," ")
    name=HumanName(personality_name)
    if name.nickname:
        personality_name=re.sub(r'\"'+name.nickname+r'\"','',personality_name)
    personality_name=personality_name.replace(".","")
    #capitalize first letters of words
    personality_name=string.capwords(personality_name)
    # substitute all tabs, newlines and other "whitespace-like" characters.
    personality_name=re.sub('\s+', ' ', personality_name).strip()
    return personality_name





def remove_roman_and_period(personality_name):
    roman = ['I', 'V' , 'X', 'III','II','IV' ]
    roman_exists= [each_roman_literal for each_roman_literal in roman if(each_roman_literal in personality_name)]
    #based on assumption that roman letter occurs towards end on the name
    if len(roman_exists)>0:
        personality_name=re.sub(r"\s+"+sorted(roman_exists, key=len,reverse=True)[0]+r"$",'',personality_name)
    if re.findall(re.compile(r'(?<=\w)[\'](?=[\w])'),personality_name):
        personality_name = re.sub(r'(?<=\w)[\'](?=\w)', "", personality_name)
    personality_name = re.sub(r'(\s)+[\'](?=\w)', "'", personality_name)
    if "physicist" in personality_name:
        personality_name=re.sub('\"physicist\"','',personality_name)
    # substitute all tabs, newlines and other "whitespace-like" characters.
    personality_name=re.sub('\s+', ' ', personality_name).strip()
    return personality_name


types_of_scientists = ['\"physicist\"', r"\(physicist\)", '\"chemist\"', r"\(chemist\)", '\"biologist\"', r"\(biologist\)",
    '\"botanist\"', r"\(botanist\)", '\"astronomer\"', r"\(astronomer\)", '\"geologist\"', r"\(geologist\)"]
def remove_science_labels(name):
    for label in types_of_scientists:
        name = re.sub(label,'',name)
    return name


def strip_accents(text):
    try:
        text = unicode(text, 'utf-8')
    except (TypeError, NameError): # unicode is a default on python 3
        pass
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)

def clean_name(name):
    if isinstance(name, str):
        name = strip_accents(name)
        name = clean_roman(name)
        name = remove_science_labels(name)
        name = name.replace('.', ' ')
        name = name.replace("(",'"').replace(")",'"')
        name = name.strip("\n").strip("\t").strip(" ")
    else:
        name = ''
    return HumanName(name)

roman = ['I', 'V' , 'X', 'III','II','IV' ]
def clean_roman(name):
    roman_exists= [each_roman_literal for each_roman_literal in roman if(each_roman_literal in name)]
    #based on assumption that roman letter occurs towards end on the name
    if len(roman_exists)>0:
        name=re.sub(r"\s+"+sorted(roman_exists, key=len,reverse=True)[0]+r"$",'',name)
    return name

def clean_unicode_characters(article_title):
    article_title=strip_accents(article_title)
    return (article_title.replace("+"," ").replace("%3A"," ").replace("%2C",",").replace("%2F","/").replace("%27","'").replace("%28","(").replace("%29",")").replace("%3F","?").replace("%CF%88","ψ").replace("%E2%80%94","-").replace("%E2%80%93","-").replace("%E2%88%92","−"))

