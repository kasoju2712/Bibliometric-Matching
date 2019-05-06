#!/usr/bin/env python
# coding: utf-8




#get_ipython().magic('load_ext autoreload')
#get_ipython().magic('reload_ext autoreload')




import requests
import lxml.html as hl
from xml.etree import ElementTree
import pandas as pd
import numpy as np

from bs4 import BeautifulSoup
from queue import Queue, Empty
from urllib.parse import urljoin, urlparse
import urllib.robotparser

import string
import json
import pickle
import re
import unicodedata
from unidecode import  unidecode

from itertools import chain
from collections import Counter

from urllib.parse import unquote
import operator
from matplotlib import pyplot as plt


import math
import statistics

import WOSutilities as wosutil
from nameparser import HumanName
import name_tools



import enchant
d=enchant.Dict('en_US')
import imp


#import load_data as load_data





get_ipython().run_cell_magic('bash', '', 'jupyter nbconvert Nobel_prize_crawl.ipynb --to script')




def strip_accents(text):
    """
    Strip accents from input String.

    :param text: The input string.
    :type text: String.

    :returns: The processed String.
    :rtype: String.
    """
    try:
        text = unicode(text, 'utf-8')
    except (TypeError, NameError): # unicode is a default on python 3 
        pass
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)





def copytofile(raw_html,filename):
    with open(filename, 'wb') as outfile:
        outfile.write(raw_html)





#retrieve nobel prize lauarates from main WIKI page
nobel_prize_page='https://en.wikipedia.org/wiki/List_of_Nobel_laureates_in_Physics'
page = requests.get(nobel_prize_page)
doc = lh.fromstring(page.content)
list_of_nobel_prize_winners=[]
tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table[1]/tbody/tr')
prev=None
#print(tr_elements)
for each_tr_element in tr_elements:
    winner_href=None
    winner_title=None
    year=None
    #print(each_tr_element)
    td_elements=each_tr_element.xpath('.//td')
    if td_elements:
        if td_elements[0].xpath('boolean(.//a[contains(@class,"image")])') is False:
            year=td_elements[0].text
            year=year.strip("\n")
            # for shared prices in a year
            if year == '' or year == '–':
                year=prev
            prev=year
        else:
            year=prev
    th_elements=each_tr_element.xpath('.//th')
    if th_elements:
        winner_href=th_elements[0].xpath('./a/@href')
        winner_title=th_elements[0].xpath('./a/@title')
        if winner_href and winner_title:
            list_of_nobel_prize_winners.append([int(year),re.sub(r"\(chemist\)|\(physicist\)",'',clean_data.strip_accents(winner_title[0])),winner_href[0],parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page)])





#creating dataframe with winners,year they were awarded and url of the winner page
nobel_prize_winners=pd.DataFrame(list_of_nobel_prize_winners,columns=['Year','Name','Url','Cannonicalized_Url'])





#to retrieve all information relevant information available in the winner page in WIKI
def update_winner_information(prize_type,prize_winners_dataframe,path_to_store_crawled_info):
    winner_wiki_information={}
    doc_num=0
    count=0
    visited_seed=set()
    for index,row in prize_winners_dataframe.iterrows():
        count=count+1
        url=row['Cannonicalized_Url']
        if  url in visited_seed or not parse_web.ispolite(url):
            continue
        print(row['Name'])
        visited_seed.add(url)
        page = requests.get(url)
        doc_num=doc_num+1
        raw_html=page.content
        doc = lh.fromstring(page.content)
        path=path_to_store_crawled_info+'/'+prize_type+'-document-{0}'
        copytofile(raw_html,path.format(doc_num))
        winner_wiki_information.update(parse_web.get_wiki_information(prize_type,doc_num,doc))
    return winner_wiki_information





nobel_winner_wiki_information=update_winner_information('nobel',nobel_prize_winners,'/home/apoorva_kasoju2712/nobel_crawled_data')





 #store nobel_winner_wiki_information as pickled file
with open('/home/apoorva_kasoju2712/wos_samplecode/nobel_winner_wiki_p.pickle', 'wb') as handle:
    pickle.dump(nobel_winner_wiki_information, handle, protocol=pickle.HIGHEST_PROTOCOL)




#retrieve stored nobel_winner_wiki_information
with open('/home/apoorva_kasoju2712/wos_samplecode/nobel_winner_wiki_p.pickle', 'rb') as handle:
    nobel_winner_wiki_information = pickle.load(handle)





path2rawdata='/home/apoorva_kasoju2712/WOS_data'

#loading article_df
article_df=load_data.load_article_data(path2rawdata)
#converting author_df from hdf5 
article_df.to_hdf('/home/apoorva_kasoju2712/wos_samplecode/article_df_data.h5','article_df',mode='w',format='table',complevel=9,complib ='blosc')
#or use loaded article_df
#article_df=pd.read_hdf('/home/apoorva_kasoju2712/wos_samplecode/article_df_data.h5','article_df')

#loading author df
author_df=load_data.load_author_data(path2rawdata)
#converting author_df from hdf5 
author_df.to_hdf('/home/apoorva_kasoju2712/wos_samplecode/author_df_data_full.h5','author_df_full',mode='w',format='table',complevel=9,complib ='blosc')
#or use loaded article_df
author_df=pd.read_hdf('/home/apoorva_kasoju2712/wos_samplecode/author_df_data_full.h5','author_df_full')

#loading address df
address_df=load_data.load_address_data(path2rawdata)
#converting address df to hdf5 and store 
address_df.to_hdf('/home/apoorva_kasoju2712/wos_samplecode/address_df_data.h5','address_df',mode='w',format='table',complevel=9,complib ='blosc')
#or use loaded  address_df 
#address_df=pd.read_hdf('/home/apoorva_kasoju2712/wos_samplecode/address_df_data.h5','address_df',mode='w',format='table',complevel=9,complib ='blosc')

#loading paper_address df
paper_address_df=load_data.load_paper_address_data(path2rawdata)
#converting paper_address df to hdf5 and store 
paper_address_df.to_hdf('/home/apoorva_kasoju2712/wos_samplecode/paper_address_df_data.h5','paper_address_df',mode='w',format='table',complevel=9,complib ='blosc')
#or use loaded paper_address_df 
paper_address_df=pd.read_hdf('/home/apoorva_kasoju2712/wos_samplecode/paper_address_df_data.h5','paper_address_df')



#merge paper_address and address_df
address_df_merged=pd.merge(paper_address_df[['ArticleID','AddressOrder','Organization','SubOrganization']], address_df[['ArticleID','AuthorOrder','AddressOrder']],  how='inner', on=['ArticleID','AddressOrder'])
address_df_merged["AddressOrder"]=address_df_merged["AddressOrder"].astype('int64') 
address_df_merged["AuthorOrder"]=address_df_merged["AuthorOrder"].astype('int64')
address_df_merged.sort_values(by = ['AuthorOrder','AddressOrder'], inplace = True)
address_df_merged.dropna(subset=['AuthorOrder','ArticleID'], inplace=True)

#prepare author_address
author_address=pd.merge(author_df[['ArticleID','FullName', 'LastName', 'FirstName','AuthorDAIS','AuthorOrder']],address_df_merged[['ArticleID','AuthorOrder','Organization']],on=['ArticleID','AuthorOrder'], how='inner')
#or use loaded author_address 
author_address=pd.read_hdf('/home/apoorva_kasoju2712/wos_samplecode/author_address_data.h5','author_address')





#getting relevant records for nobel prize winners matching in the WOS
nobel_author_df=match_utilities.get_wos_records(nobel_winner_wiki_information,author_df)





#storing the relevant data to hdf5 
prize_type='nobel'
nobel_author_df.to_hdf('/home/apoorva_kasoju2712/wos_samplecode/'+prize_type+'_author_df_data.h5',prize_type+'_author_df',mode='w',format='table',complevel=9,complib ='blosc')


# In[7]:


#loading nobel_author_df
prize_type='nobel'
nobel_author_df=pd.read_hdf('/home/apoorva_kasoju2712/wos_samplecode/'+prize_type+'_author_df_data.h5',prize_type+'_author_df')





#retrieving co-authors for the articles in nobel_author_df
nobel_article_co_author_temp=pd.merge(author_df[['ArticleID','FullName','LastName']],nobel_author_df[['ArticleID']],how='inner',on=['ArticleID'])
nobel_article_co_author=nobel_article_co_author_temp.groupby(['ArticleID']).agg({'LastName':lambda x: list(x.unique()),'FullName':lambda x: list(x.unique())}).reset_index()
nobel_article_co_author.to_pickle("/home/apoorva_kasoju2712/wos_samplecode/nobel_article_co_author_df.pkl")
#loading nobel_article_co_author as pandas Dataframe
#nobel_article_co_author=pd.read_pickle("/home/apoorva_kasoju2712/wos_samplecode/nobel_article_co_author_df.pkl")





#retrieving nobel_author_df articles from article_df  
nobel_author_article=pd.merge(article_df[['ArticleID','Title']],nobel_author_df[['ArticleID','AuthorOrder','AuthorDAIS','FullName','LastName']],on=['ArticleID'],how='inner')
nobel_author_article.dropna(subset=['AuthorDAIS'],inplace=True)





#retrieving address information(organization) for authors in nobel_author_df 
nobel_author_address=pd.merge(nobel_author_df[['ArticleID','FullName', 'LastName', 'FirstName','AuthorDAIS','AuthorOrder']],author_address[['ArticleID','AuthorOrder','Organization']],on=['ArticleID'], how='left')
nobel_author_address.dropna(subset=['AuthorDAIS'],inplace=True)

#merging  address information(organization) and article information for authors in nobel_author_df 
nobel_author_address_article=pd.merge(nobel_author_address[['ArticleID','FullName', 'LastName', 'FirstName','Organization','AuthorDAIS']],nobel_author_article[['ArticleID','Title','AuthorDAIS']],on=['AuthorDAIS','ArticleID'], how='left')





#finding best match for authors in nobel_author_df from WOS using organization,co_authorships,decision_vector(author full_names) features retrieved from WIKIPEDIA
match_title_dict,high_score_dict,match_co_author_dict,no_match_dict,tie_match_dict=match_utilities.find_best_match(nobel_winner_wiki_information,nobel_author_address_article,nobel_article_co_author)





#update winner information with their WOS ID matched
for k,v in match_title_dict:
    nobel_winner_wiki_information[k].update({'wos_author_id':v[0]})
for k,v in high_score_dict:
    nobel_winner_wiki_information[k].update({'wos_author_id':v[0]})
for k,v in match_co_author_dict:
    nobel_winner_wiki_information[k].update({'wos_author_id':v[0]})
for k,v in tie_match_dict:
    nobel_winner_wiki_information[k].update({'wos_author_id':None})
for k,v in no_match_dict:
    nobel_winner_wiki_information[k].update({'wos_author_id':None})

