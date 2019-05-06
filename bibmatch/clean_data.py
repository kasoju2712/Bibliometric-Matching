#!/usr/bin/env python
# coding: utf-8

# In[1]:


import string
from nameparser import HumanName
import re
from unidecode import  unidecode
import unicodedata





#get_ipython().run_cell_magic('bash', '', 'jupyter nbconvert clean_data.ipynb --to script')





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




def strip_accents(text):
    try:
        text = unicode(text, 'utf-8')
    except (TypeError, NameError): # unicode is a default on python 3 
        pass
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)





def clean_unicode_characters(article_title):
    article_title=strip_accents(article_title)
    return (article_title.replace("+"," ").replace("%3A"," ").replace("%2C",",").replace("%2F","/").replace("%27","'").replace("%28","(").replace("%29",")").replace("%3F","?").replace("%CF%88","ψ").replace("%E2%80%94","-").replace("%E2%80%93","-").replace("%E2%88%92","−"))

