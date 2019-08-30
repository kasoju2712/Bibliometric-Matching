import string
import sys
import re
import langid
import urllib
import unicodedata
from nameparser import HumanName
from unidecode import  unidecode
from langdetect import detect 
from dateutil.parser import parse
from urllib.parse import unquote


# from fuzzy-wuzzy string processing
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
    elif isinstance(strlist, set):
        return [_sort_process(s) for s in strlist]
    else:
        return False

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

#to detect language of titles(articles)
def detect_lang_and_retrieve(article):
    print(article)
    match=re.search(r'\((.*?)\)',article)
    #print(match.groups(1))
    if match and len(match.groups())==1:
        x=re.sub(r'\(.*\)', '', article)
        #print(x)
    
        if x!='' and detect(x)!='en':
            #print("hehe")
            if is_date(match.group(1))==False and  detect(match.group(1))=='en':
                return (match.group(1))
    return article

#check if string is valid date
def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False
    
def clean_unicode_characters(article_title):
    article_title=strip_accents(article_title)
    article_title=article_title.replace("+"," ").replace("%3A"," ").replace("%2C",",").replace("%2F","/").replace("%27","'").replace("%28","(").replace("%29",")").replace("%3F","?").replace("%CF%88","ψ").replace("%E2%80%94","-").replace("%E2%80%93","-").replace("%E2%88%92","−")
    return article_title

def clean_articles(article_title):
    #remove invalid titles
    if re.search('^(?=.*\d)(?=.*[a-z])(?=.*[\/])(?=.*[\.])[a-z0-9\.\/]+$',article_title) or re.search('^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[\.])[a-z0-9A-Z\.]+$',article_title):
        return None
    article_title=re.sub('\s+', ' ', re.sub('\([\s\d\-]+\)|\d+$', '',article_title)).strip()
    if not re.match("^[A-Z0-9/\.\-]+$",article_title) and article_title!='':
        article_title=detect_lang_and_retrieve(article_title)
        return unquote(article_title)


def check_name(name):
    if ',' in name:
        if len(str(name.split(',')[-1]))==2 or len(str(name.split(',')[-1]))==3:
            first=name.split(',')[-1]
            final_name=" ".join(list(first)) +" "+str(name.split(',')[0])
        else:
            final_name=str(name.split(',')[-1]) +" "+str(name.split(',')[0])
        return final_name
    else:
        return name
    
roman = ['I', 'V' , 'X', 'III','II','IV' ]
def clean_roman(name):
    roman_exists= [each_roman_literal for each_roman_literal in roman if(each_roman_literal in name)]
    #based on assumption that roman letter occurs towards end on the name
    if len(roman_exists)>0:
        name=re.sub(r"\s+"+sorted(roman_exists, key=len,reverse=True)[0]+r"$",'',name)
        # substitute all tabs, newlines and other "whitespace-like" characters.
    name=re.sub('\s+', ' ', name).strip()
    return name

def clean_name(name,return_human_name=True):
    name = strip_accents(name)
    name_str=HumanName(name)
    name = name.replace(name_str.title,'')
    name = re.sub(r'[\(|\"]%s[\)|\"]'% name_str.nickname,'',name).strip()
    name = clean_roman(name)
    name = re.sub('Jr\.$', '', name)
    name = name.lower()
    name = remove_science_labels(name)
    name = name.replace('.', ' ')
    name = name.replace("(",'"').replace(")",'"').replace("-"," ").replace('"','')
    name = name.strip("\n").strip("\t").strip(" ")
    name = re.sub('\s+', ' ', name)
    name = check_name(name)
    if return_human_name:
        return HumanName(name)
    else :
        return name

def agg_stringlist_with_delim(string_list,delimiter=" | "):
    """return list of co_authors for a Author ID"""
    result = set()
    for each_string in string_list:
        result.update(set(each_string.split(delimiter)))
    return list(filter(None, result))



