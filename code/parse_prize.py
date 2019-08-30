import re
import requests
import lxml.html as lh
import pandas as pd
import pickle
from queue import Queue, Empty
from urllib.parse import urljoin, urlparse
from lxml import html
import numpy as np
import parse_web  as parse_web
from bibmatch.clean_data import strip_accents
import string
from string import punctuation
paranthesis_text=re.compile(r'\((.*?)\)')
r = re.compile(r'[\s{}]+'.format(re.escape(punctuation)))
paranthesis=re.compile(r'\(.*\)')



# def copytofile(raw_html,filename):
#     with open(filename, 'wb') as outfile:
#         outfile.write(raw_html)


#retrieve nobel prize lauarates from main WIKI page
nobel_prize_page='https://en.wikipedia.org/wiki/List_of_Nobel_laureates_in_Chemistry'
page = requests.get(nobel_prize_page)
doc = lh.fromstring(page.content)
list_of_nobel_prize_winners=[]
tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table[1]/tbody/tr')
prev=None
prev_purpose=None
for each_tr_element in tr_elements:
    winner_href=None
    winner_title=None
    year=None
    purpose=None
    td_elements=each_tr_element.xpath('.//td')
    th_elements=each_tr_element.xpath('.//th')
    if td_elements:
        if len(td_elements)+ len(th_elements)<=2:
            continue
        last_td=td_elements[len(td_elements)-1]
        if td_elements[0].xpath('boolean(.//a[contains(@class,"image")])') is False and td_elements[0].xpath('boolean(.//a)') is False:
            year=td_elements[0].text
            year=year.strip("\n")
            # for shared prices in a year
            if year == '' or year == '–':
                year=prev
            prev=year
            if last_td.xpath('boolean(.//sup[contains(@class,"reference")])') is True:
                updated_list=td_elements[:-1]
                if len(updated_list)>2:
                    purpose=(updated_list[-1].text_content()).replace('"','').replace("\n","")
                    prev_purpose=purpose
                else:
                    purpose=prev_purpose
            else:
                purpose=prev_purpose          
        else:
            year=prev
            if last_td.xpath('boolean(.//sup[contains(@class,"reference")])') is True:
                updated_list=td_elements[:-1]
                if len(updated_list)>2:
                    purpose=(updated_list[-1].text_content()).replace('"','').replace("\n","")
                    prev_purpose=purpose
                else:
                    purpose=prev_purpose
            else:
                purpose=prev_purpose
    if th_elements:
        winner_href=th_elements[0].xpath('./a/@href')
        winner_title=th_elements[0].xpath('./a/@title')

        if winner_href and winner_title:
            list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),re.sub("[\[].*?[\]]", "",purpose)])

#retrieve nobel prize lauarates from main WIKI page
# nobel_prize_page='https://en.wikipedia.org/wiki/List_of_Nobel_laureates_in_Physics'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table[1]/tbody/tr')
# prev=None
# prev_purpose=None
# #print(tr_elements)
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     td_elements=each_tr_element.xpath('.//td')
#     th_elements=each_tr_element.xpath('.//th')
#     if td_elements:
#         if len(td_elements)+ len(th_elements)<=2:
#             continue
#         last_td=td_elements[len(td_elements)-1]
#         if td_elements[0].xpath('boolean(.//a[contains(@class,"image")])') is False and td_elements[0].xpath('boolean(.//a)') is False:
#             year=td_elements[0].text
#             year=year.strip("\n")
#             # for shared prices in a year
#             if year == '' or year == '–':
#                 year=prev
#             prev=year
#             if last_td.xpath('boolean(.//sup[contains(@class,"reference")])') is True:
#                 updated_list=td_elements[:-1]
#                 if len(updated_list)>2:
#                     purpose=(updated_list[-1].text_content()).replace('"','').replace("\n","")
#                     prev_purpose=purpose
#                 else:
#                     purpose=prev_purpose
#             else:
#                 purpose=prev_purpose          
#         else:
#             year=prev
#             if last_td.xpath('boolean(.//sup[contains(@class,"reference")])') is True:
#                 updated_list=td_elements[:-1]
#                 if len(updated_list)>2:
#                     purpose=(updated_list[-1].text_content()).replace('"','').replace("\n","")
#                     prev_purpose=purpose
#                 else:
#                     purpose=prev_purpose
#             else:
#                 purpose=prev_purpose
#     if th_elements:
#         winner_href=th_elements[0].xpath('./a/@href')
#         winner_title=th_elements[0].xpath('./a/@title')
#         if winner_href and winner_title:
#             list_of_nobel_prize_winners.append([int(year),re.sub(r"\(chemist\)|\(physicist\)",'',strip_accents(winner_title[0])),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose.replace("[",'').replace("]",'')])
            
#retrieve nobel prize lauarates from main WIKI page
# nobel_prize_page='https://en.wikipedia.org/wiki/Lorentz_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table/tbody/tr')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# for curr_elem in tr_elements:
#     td_elements=curr_elem.xpath('.//td')
#     if td_elements:
#         year=td_elements[0].xpath("./text()")[0].strip(" ") 
#         for x_elem in td_elements[-1].xpath('.//a'):
#             winner_href=x_elem.xpath('./@href')
#             winner_title=x_elem.xpath('./@title')
#         #if winner_title and 'page does not exist' in winner_title[0]:continue
#             if winner_title and 'page does not exist' in winner_title[0]:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),"Page does not exist",purpose])
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])  

#retrieve nobel prize lauarates from main WIKI page
# nobel_prize_page='https://en.wikipedia.org/wiki/List_of_Nobel_laureates_in_Physiology_or_Medicine'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table[1]/tbody/tr')
# prev=None
# prev_purpose=None
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     td_elements=each_tr_element.xpath('.//td')
#    # print(each_tr_element)
#     if td_elements:
#         last_td=td_elements[-1]
#         if len(td_elements)<=2:
#             continue
#         if  td_elements[0].xpath('boolean(.//a)') is False:
#             year=td_elements[0].text
#             year=year.strip("\n")
#             if year == '' or year == '–':
#                 year=prev
#             prev=year
#             #purpose=(td_elements[4].text_content()).replace('"','').replace("\n","")
#             #prev_purpose=purpose
#         else:
#             year=prev
#         if len(td_elements)>5:
#             purpose=(td_elements[-2].text_content()).replace('"','').replace("\n","")
#             prev_purpose=purpose
#         else:
#             purpose=prev_purpose
#         x_elements=each_tr_element.xpath('.//a[not(contains(@class,"image"))]/parent::td[1]')
#         if x_elements:
#             winner_href=x_elements[0].xpath('./a/@href')
#             winner_title=x_elements[0].xpath('./a/@title')
#             if winner_title and 'page does not exist' in winner_title[0]:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),"Page does not exist",purpose])  
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(r"\(chemist\)|\(physicist\)|\(economist\)|\(neuroscientist\)|\(scientist\)",'',strip_accents(winner_title[0])),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),re.sub("[\[].*?[\]]", "",purpose)])
                
#hughes prize
# hughes_prize_page='https://en.wikipedia.org/wiki/Hughes_Medal'
# page = requests.get(hughes_prize_page)
# doc = lh.fromstring(page.content)
# list_of_hughes_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table/tbody/tr')
# #print(tr_elements)
# prev=None
# prev_purpose=None
# for each_tr_element in tr_elements:
#     td_elements=each_tr_element.xpath('.//td')
#    # print(td_elements)
#     #list_of_winner_elem=[]
#     if td_elements:  
#         if len(td_elements)>3:
#             purpose=(td_elements[-2].text_content()).replace('"','').replace("\n","")
#             #print(purpose)
#             prev_purpose=purpose
#         else:
#             purpose=prev_purpose
#         year=td_elements[0].text
#         winner_href=each_tr_element.xpath('.//td[2]//a/@href')
#         winner_title=each_tr_element.xpath('.//td[2]//a/@title')
#         if winner_href and winner_title:
#             list_of_hughes_prize_winners.append([int(year),re.sub(r"\(chemist\)|\(physicist\)|\(economist\)|\(neuroscientist\)|\(scientist\)",'',strip_accents(winner_title[0])),winner_href[0],parse_web.urlCanonicalization(winner_href[0], base_url=hughes_prize_page),re.sub("[\[].*?[\]]", "",purpose)])
            
# #retrieve nobel prize lauarates from main WIKI page
# nobel_prize_page='https://en.wikipedia.org/wiki/Matteucci_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/div[1]/ul/li')
# for curr_elem in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     year=curr_elem.xpath('./text()')[0].strip(" ")
#     winner_href=curr_elem.xpath('./a/@href')
#     winner_title=curr_elem.xpath('./a/@title')
#     if winner_title and 'page does not exist' in winner_title[0]:continue
#     if winner_href and winner_title:
#             list_of_nobel_prize_winners.append([int(year),re.sub(r"\(chemist\)|\(physicist\)|\(economist\)|\(neuroscientist\)|\(scientist\)",'',strip_accents(winner_title[0])),winner_href[0],parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])  
# nobel_prize_page='https://en.wikipedia.org/wiki/List_of_Nobel_laureates_in_Literature'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table[1]/tbody/tr')
# prev=None
# prev_purpose=None
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     td_elements=each_tr_element.xpath('.//td')
#    # print(each_tr_element)
#     if td_elements:
#         last_td=td_elements[-1]
#         if len(td_elements)<=2:
#             continue
#         if td_elements[0].xpath('boolean(.//a[contains(@class,"image")])') is False and td_elements[0].xpath('boolean(.//a)') is False:
#             year=td_elements[0].text
#             year=year.strip("\n")
#             if year == '' or year == '–':
#                 year=prev
#             prev=year
#         else:
#             year=prev
#         if last_td.xpath('boolean(.//sup[contains(@class,"reference")])') is True:
#             updated_list=td_elements[:-1]
#         else:
#             updated_list=td_elements
#         if len(updated_list)>2:
#             purpose=(updated_list[-2].text_content()).replace('"','').replace("\n","")
#         x_elements=each_tr_element.xpath('.//a[not(contains(@class,"image"))]/parent::td[1]')
#         if x_elements:
#             winner_href=x_elements[0].xpath('./a/@href')
#             winner_title=x_elements[0].xpath('./a/@title')
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(r"\(chemist\)|\(physicist\)",'',strip_accents(winner_title[0])),winner_href[0],parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),re.sub("[\[].*?[\]]", "",purpose)])
# hughes_prize_page='https://en.wikipedia.org/wiki/Enrico_Fermi_Prize'
# page = requests.get(hughes_prize_page)
# doc = lh.fromstring(page.content)
# list_of_hughes_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table/tbody/tr')
# #print(tr_elements)
# prev=None
# prev_purpose=None
# for each_tr_element in tr_elements:
#     td_elements=each_tr_element.xpath('.//td')
#     if td_elements:  
#         if len(td_elements)>=2:
#             purpose=(td_elements[-1].text_content()).replace('"','').replace("\n","")
#             #print(purpose)
#             prev_purpose=purpose
#         else:
#             purpose=prev_purpose
#         if td_elements[0].xpath('boolean(.//a)') is False:
#             year=td_elements[0].text
#             year=year.strip("\n")
#             if year == '' or year == '–':
#                 year=prev
#             prev=year
#             #purpose=(td_elements[4].text_content()).replace('"','').replace("\n","")
#             #prev_purpose=purpose
#         else:
#             year=prev
#         x_elements=each_tr_element.xpath('.//a/parent::td[1]|.//span[a]')
#         if x_elements:
#             winner_href=x_elements[0].xpath('./a/@href')
#             winner_title=x_elements[0].xpath('./a/@title')
#             #print(winner_title)
#             if winner_title and 'page does not exist' in winner_title[0]:continue
#             if winner_href and winner_title:
#            # winner_info=list(zip(winner_title,winner_href))
#             #for each_winner_info in winner_info:
#                 list_of_hughes_prize_winners.append([int(year),re.sub(r"\(chemist\)|\(physicist\)",'',strip_accents(winner_title[0])),winner_href[0],parse_web.urlCanonicalization(winner_href[0], base_url=hughes_prize_page),re.sub("[\[].*?[\]]", "",purpose)]) 

# nobel_prize_page='https://en.wikipedia.org/wiki/Comstock_Prize_in_Physics'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table/tbody/tr')
# #print(tr_elements)
# prev=None
# prev_purpose=None
# for each_tr_element in tr_elements:
#     td_elements=each_tr_element.xpath('.//td')
#     if td_elements:  
#         if len(td_elements)>=2:
#             purpose=(td_elements[-1].text_content()).replace('"','').replace("\n","")
#             if len(purpose)<5:
#                 purpose=None
#             prev_purpose=purpose
#         else:
#             purpose=prev_purpose
#         if td_elements[0].xpath('boolean(.//a)') is False:
#             year=td_elements[0].text
#             year=year.strip("\n")
#             if year == '' or year == '–':
#                 year=prev
#             prev=year
#         else:
#             year=prev
#         x_elements=each_tr_element.xpath('.//a[not(contains(@class,"image"))]/parent::td[1]')
#         if x_elements:
#             for x_elem in x_elements:
#                 a_elem=x_elem.xpath('.//a')
#                 count=0
#                 for each_elem in a_elem:
#                     winner_href=each_elem.xpath('./@href')
#                     winner_title=each_elem.xpath('./@title')
#                     if winner_title and 'page does not exist' in winner_title[0]:
#                         list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),"Page does not exist",purpose])
#                         continue
#                     if winner_title and 'Silicon photonics' in winner_title[0]:
#                         continue
#                     if winner_href and winner_title:
#                         list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])
                    
#retrieve nobel prize lauarates from main WIKI page
# paranthesis=re.compile(r'\(.*\)')
# nobel_prize_page='https://en.wikipedia.org/wiki/CAP-CRM_Prize_in_Theoretical_and_Mathematical_Physics'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/div[1]/ul/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# for curr_elem in tr_elements:
#     year=curr_elem.xpath("./text()")[0].strip(" ")  
#     each_a_elem=curr_elem.xpath(".//a[1]")
#     if each_a_elem:
#         winner_href=each_a_elem[0].xpath('./@href')
#         winner_title=each_a_elem[0].xpath('./@title')
#         if winner_title and 'page does not exist' in winner_title[0]:
#             list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),"Page does not exist",purpose])
#             continue
#         if winner_title and 'Université de Montréal' in winner_title[0]:continue
# #                 print(winner_title)
#         if winner_href and winner_title:
#             list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose]) 

# #retrieve nobel prize lauarates from main WIKI page
# paranthesis=re.compile(r'\(.*\)')
# nobel_prize_page='https://en.wikipedia.org/wiki/Boltzmann_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul[1]/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# for curr_elem in tr_elements:
#     year=curr_elem.xpath("./text()")[0].strip(" ")  
#     a_elem=curr_elem.xpath(".//a")
#     if a_elem:
#         len_elem=len(a_elem)
#         count=0
#         for each_a_elem in a_elem:
#             if count%2==0:
#                 winner_href=each_a_elem.xpath('./@href')
#                 winner_title=each_a_elem.xpath('./@title')
#                 if winner_title and 'page does not exist' in winner_title[0]:
#                     count=count+1
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),"Page does not exist",purpose])
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose]) 
#             count=count+1             
#retrieve nobel prize lauarates from main WIKI page


# nobel_prize_page='https://en.wikipedia.org/wiki/Dirac_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/div[3]/ul/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# for curr_elem in tr_elements:
#     year=curr_elem.xpath("./text()")[0].strip(" ")  
#     #print(year)
#     a_elem=curr_elem.xpath(".//a")
#     #print(a_elem)
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('./@title')
#             if winner_title and 'page does not exist' in winner_title[0]:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),"Page does not exist",purpose])    
#                 count=count+1
#                 continue
#             #print(winner_title)
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    
#retrieve nobel prize lauarates from main WIKI page
# nobel_prize_page='https://en.wikipedia.org/wiki/Lorentz_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table/tbody/tr')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# for curr_elem in tr_elements:
#     td_elements=curr_elem.xpath('.//td')
#     if td_elements:
#         year=td_elements[0].xpath("./text()")[0].strip(" ") 
#         for x_elem in td_elements[-1].xpath('.//a'):
#             winner_href=x_elem.xpath('./@href')
#             winner_title=x_elem.xpath('./@title')
#         #if winner_title and 'page does not exist' in winner_title[0]:continue
#             if winner_title and 'page does not exist' in winner_title[0]:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),"Page does not exist",purpose])
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])  
 #retrieve nobel prize lauarates from main WIKI page
# nobel_prize_page='https://en.wikipedia.org/wiki/Batchelor_Prize'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul[1]/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# for curr_elem in tr_elements:
#     year=curr_elem.xpath("./text()")[0].strip(":").strip(" ").strip(":") 
#     #print(year)
#     a_elem=curr_elem.xpath(".//a[1]")
#     #print(a_elem)
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('./@title')
#             if winner_title and 'page does not exist' in winner_title[0]:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),"Page does not exist",purpose])    
#                 count=count+1
#                 continue
#             #print(winner_title)
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    
# import re
# from string import punctuation
# paranthesis_text=re.compile(r'\((.*?)\)')
# r = re.compile(r'[\s{}]+'.format(re.escape(punctuation)))
# nobel_prize_page='https://en.wikipedia.org/wiki/Bogolyubov_Prize_(NASU)'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul[1]/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     year=curr_elem.xpath("./text()")[0].strip(":").strip(" ").strip(":") 
#     #print(year)
#     a_elem=curr_elem.xpath(".//a")
#     text=' '.join(curr_elem.xpath(".//descendant::text()"))
#     if re.search(paranthesis_text,text):
#         country=re.findall('\((.*?)\)',text)
#     l= [ x for x in ['for his','for her','for their','for a'] if x in text] 
#     if l:
#         index_pos=text.find(l[0])
#         purpose=text[index_pos:]  
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('./@title')
#             if winner_title and winner_title[0]:
#                 if purpose and winner_title[0].lower() in purpose:
#                     continue
#                 if country and any (True for each_country in country if re.sub('\(country\)','',winner_title[0]) in each_country)==True:
#                     continue
#             if winner_title and 'page does not exist' in winner_title[0]:
#                 years=year.split("–")
#                 for each_year in years:
#                     list_of_nobel_prize_winners.append([int(each_year),re.sub(paranthesis,'',strip_accents(winner_title[0])),"Page does not exist",purpose])    
#                 continue
#             #print(winner_title)
#             if winner_href and winner_title:
#                 years=year.split("–")
#                 for each_year in years:
#                     list_of_nobel_prize_winners.append([int(each_year),re.sub(paranthesis,'',strip_accents(winner_title[0])),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    

# nobel_prize_page='https://en.wikipedia.org/wiki/Niels_Bohr_International_Gold_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul[1]/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# for curr_elem in tr_elements:
#     year=curr_elem.xpath("./text()")[0].strip(":").strip(" ").strip(":").strip(",")
#     #print(year)
#     a_elem=curr_elem.xpath(".//a")
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('./@title')
#             if winner_title and 'page does not exist' in winner_title[0]:
#                 years=year.split("–")
#                 for each_year in years:
#                     list_of_nobel_prize_winners.append([int(each_year),re.sub(paranthesis,'',strip_accents(winner_title[0])),"Page does not exist",purpose])    
#                     count=count+1
#                 continue
#             #print(winner_title)
#             if winner_href and winner_title:
#                 years=year.split("–")
#                 for each_year in years:
#                     list_of_nobel_prize_winners.append([int(each_year),re.sub(paranthesis,'',strip_accents(winner_title[0])),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    



    

# nobel_prize_page='https://en.wikipedia.org/wiki/Bogolyubov_Prize'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul[1]/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# for curr_elem in tr_elements:
#     year=curr_elem.xpath("./text()")[0].strip(":").strip(" ").strip(":") 
#     #print(year)
#     a_elem=curr_elem.xpath(".//a")
#     text=' '.join(curr_elem.xpath(".//descendant::text()"))
#     if re.search(paranthesis_text,text):
#         country=re.findall('\((.*?)\)',text)
#     l= [ x for x in ['for his','for her','for their','for a'] if x in text] 
#     if l:
#         index_pos=text.find(l[0])
#         purpose=text[index_pos:]  
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('./@title')
#             if winner_title and winner_title[0]:
#                 if purpose and winner_title[0].lower() in purpose:
#                     continue
#                 if country and any (True for each_country in country if re.sub('\(country\)','',winner_title[0]) in each_country)==True:
#                     continue
#             if winner_title and 'page does not exist' in winner_title[0]:
#                 years=year.split("–")
#                 for each_year in years:
#                     list_of_nobel_prize_winners.append([int(each_year),re.sub(paranthesis,'',strip_accents(winner_title[0])),"Page does not exist",purpose])    
                   
#                 continue
#             #print(winner_title)
#             if winner_href and winner_title:
#                 years=year.split("–")
#                 for each_year in years:
#                     list_of_nobel_prize_winners.append([int(each_year),re.sub(paranthesis,'',strip_accents(winner_title[0])),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    
# nobel_prize_page='https://en.wikipedia.org/wiki/Boltzmann_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul[1]/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     year=curr_elem.xpath("./text()")[0].strip(":").strip(" ").strip(":") 
#     #print(year)
#     a_elem=curr_elem.xpath(".//a")
#     text=' '.join(curr_elem.xpath(".//descendant::text()"))
#     if re.search(paranthesis_text,text):
#         country=re.findall('\((.*?)\)',text)
#     l= [ x for x in ['for his','for her','for their','for a'] if x in text] 
#     if l:
#         index_pos=text.find(l[0])
#         purpose=text[index_pos:]  
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('./@title')
#             if winner_title and winner_title[0]:
#                 if purpose and winner_title[0].lower() in purpose:
#                     continue
#                 if country and any (True for each_country in country if re.sub('\(country\)','',winner_title[0]) in each_country)==True:
#                     continue
#             if winner_title and 'page does not exist' in winner_title[0]:
#                 years=year.split("–")
#                 for each_year in years:
#                     list_of_nobel_prize_winners.append([int(each_year),re.sub(paranthesis,'',strip_accents(winner_title[0])),"Page does not exist",purpose])    
                    
#                 continue
#             #print(winner_title)
#             if winner_href and winner_title:
#                 years=year.split("–")
#                 for each_year in years:
#                     list_of_nobel_prize_winners.append([int(each_year),re.sub(paranthesis,'',strip_accents(winner_title[0])),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    


                    
# nobel_prize_page='https://en.wikipedia.org/wiki/Ludwig_Boltzmann_Prize'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table/tbody/tr/td/ul/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     a_elem=curr_elem.xpath(".//a[1]")
#     if a_elem:
#         year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#         more_authors=curr_elem.xpath("./text()")[0].replace(year," ").replace("-","").strip("-")
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('./@title')
#             if winner_title and 'page does not exist' in winner_title[0]:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    
#     else:
#         text=' '.join(curr_elem.xpath(".//text()"))
#         index_pos = re.search('(\d{4})', text)
#         if index_pos:
#             index=index_pos.start()
#             prize_year=text[index:index+4]
#             prize_name=re.sub(prize_year,'',text).strip("-").strip(" ")
#             if prize_year and prize_name and prize_name!=' ':
#                 if ' and ' in prize_name:
#                     prize_names=prize_name.split(' and ')
#                     for each_name in prize_names:
#                         list_of_nobel_prize_winners.append([int(prize_year),re.sub(paranthesis,'',strip_accents(each_name.strip("-"))),"Page does not exist",purpose])    
#                 else:
#                     list_of_nobel_prize_winners.append([int(prize_year),re.sub(paranthesis,'',strip_accents(prize_name.strip("-"))),"Page does not exist",purpose])    


#retrieve nobel prize lauarates from main WIKI page
import re
from string import punctuation
# paranthesis_text=re.compile(r'\((.*?)\)')
# nobel_prize_page='https://en.wikipedia.org/wiki/Breakthrough_Prize_in_Fundamental_Physics'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr')
# prev=None
# extra=['LIGO','ATLAS','Observation of Gravitational Waves from a Binary Black Hole Merger','Super-Kamiokande','Sudbury Neutrino Observatory','K2K','T2K',' KamLAND']
# prev_purpose=None
# #print(tr_elements)
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     country=None
#     #print(each_tr_element)
#     td_elements=each_tr_element.xpath('.//td')
#     th_elements=each_tr_element.xpath('.//th')
#     if td_elements:
#         if len(td_elements)+ len(th_elements)<=2:
#             continue
#         last_td=td_elements[len(td_elements)-1]
#         if td_elements[0].xpath('boolean(.//a[contains(@class,"image")])') is False and td_elements[0].xpath('boolean(.//a)') is False:
#             #print(len(td_elements))
#             year=td_elements[0].text
#             year=year.strip("\n")
#             # for shared prices in a year
#             if year == '' or year == '–':
#                 year=prev
#             prev=year
#             td_elem=td_elements[1]
#             if len(td_elements)>3:
#                 purpose=(td_elements[2].text_content()).replace('"','').replace("\n","")
#                 prev_purpose=purpose
#             else:
#                 purpose=prev_purpose         
#         else:
#             year=prev
#             td_elem=td_elements[0]
#             if len(td_elements)>3:
#                 purpose=(td_elements[1].text_content()).replace('"','').replace("\n","")
#                 prev_purpose=purpose
#             else:
#                 purpose=prev_purpose
#     if not purpose:
#         purpose=prev_purpose
#     if year:
#         year=re.sub(paranthesis,'',year)
#     if td_elements:
#         a_elem=td_elem.xpath('.//a')
#         text=' '.join(td_elem.xpath('.//descendant::text()'))
#         if re.search(paranthesis_text,text):
#             country=re.findall('\((.*?)\)',text)
#         for each_elem in a_elem:
#             winner_href=each_elem.xpath('./@href')
  
#             winner_title=each_elem.xpath('./text()')

#             if winner_title and winner_title[0]:
#                 if country and any (True for each_country in country if re.sub('\(country\)','',winner_title[0]) in each_country)==True:
#                     continue
#             if winner_title and winner_title[0]:
#                 if winner_title[0] in extra or re.search(re.compile(r'\d+'),winner_title[0]):
#                     continue
#             if winner_title and 'page does not exist' in winner_title[0]:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),"Page does not exist",purpose])    
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])

# paranthesis_text=re.compile(r'\((.*?)\)')
# nobel_prize_page='https://en.wikipedia.org/wiki/Harold_Brown_Award'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('///*[@id="mw-content-text"]/div/table/tbody/tr')
# prev=None
# prev_purpose=None
# #print(tr_elements)
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     purpose_text=None
#     country=None
#     #print(each_tr_element)
#     th_elements=each_tr_element.xpath('.//th')
#     td_elements=each_tr_element.xpath('.//td')
#     if td_elements:
#         if len(td_elements)+ len(th_elements)<=2:
#             continue
#         last_td=td_elements[len(td_elements)-1]
#         if td_elements[0].xpath('boolean(.//a[contains(@class,"image")])') is False and td_elements[0].xpath('boolean(.//a)') is False:
#             #print(len(td_elements))
#             year=td_elements[0].text
#             year=year.strip("\n")
#     if year:
#         year=re.sub(paranthesis,'',year)
#     if td_elements:
#         purpose_text=' '.join(td_elements[2].xpath('.//descendant::text()'))
#         if purpose_text:
#             l= [x for x in ['for ','For ']  if x in  purpose_text ]
#             if l:
#                 index_pos=purpose_text.find(l[0])
#                 purpose=purpose_text[index_pos:].strip("\n")
            
#         a_elem=td_elements[1].xpath('.//a')
#         text=' '.join(td_elements[1].xpath('.//descendant::text()'))
#         if re.search(paranthesis_text,text):
#             country=re.findall('\((.*?)\)',text)
#         if a_elem:
#             for each_elem in a_elem:
#                 winner_href=each_elem.xpath('./@href')
#                 winner_title=each_elem.xpath('./text()')
#                 if winner_title and winner_title[0]:
#                     if country and any (True for each_country in country if re.sub('\(country\)','',winner_title[0]) in each_country)==True:
#                         continue
#                 if winner_title and 'page does not exist' in winner_title[0]:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),"Page does not exist",purpose])    
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])
#         else:
#             list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(td_elements[1].xpath('.//text()')[0])).strip("\n"),"Page does not exist",purpose])

# nobel_prize_page='https://en.wikipedia.org/wiki/Eddington_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/div[2]/ul/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
# #     year=re.findall('\d{4}',curr_elem.xpath(".//text"))[0]
#     a_elem=curr_elem.xpath(".//a")
#     if a_elem:
#         year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
# #         more_authors=curr_elem.xpath("./text()")[0].replace(year," ").replace("-","").strip("-")
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('./@title')
#             if winner_title and 'page does not exist' in winner_title[0]:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    

# nobel_prize_page='https://en.wikipedia.org/wiki/Einstein_Prize_for_Laser_Science'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('///*[@id="mw-content-text"]/div/ul[1]/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
# #     year=re.findall('\d{4}',curr_elem.xpath(".//text"))[0]
#     a_elem=curr_elem.xpath(".//a")
#     if a_elem:
#         year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
# #         more_authors=curr_elem.xpath("./text()")[0].replace(year," ").replace("-","").strip("-")
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('./@title')
#             if winner_title and 'page does not exist' in winner_title[0]:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    


# nobel_prize_page='https://en.wikipedia.org/wiki/Albert_Einstein_Award'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table/tbody/tr')
# prev=None
# prev_purpose=None
# #print(tr_elements)
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     purpose_text=None
#     country=None
#     #print(each_tr_element)
#     th_elements=each_tr_element.xpath('.//th')
#     td_elements=each_tr_element.xpath('.//td')
#     if td_elements:
#         if len(td_elements)+ len(th_elements)<=2:
#             continue
#         last_td=td_elements[len(td_elements)-1]
#         if td_elements[0].xpath('boolean(.//a[contains(@class,"image")])') is False and td_elements[0].xpath('boolean(.//a)') is False:
#             #print(len(td_elements))
#             year=td_elements[0].text
#             year=year.strip("\n")  
#     if year:
#         year=re.sub(paranthesis,'',year)
#     if td_elements:
            
#         a_elem=td_elements[1].xpath('.//a')
#         if a_elem:
#             for each_elem in a_elem:
#                 winner_href=each_elem.xpath('./@href')
#                 winner_title=each_elem.xpath('./text()')
#                 if winner_title and 'page does not exist' in winner_title[0]:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),"Page does not exist",purpose])    
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])


# nobel_prize_page='https://en.wikipedia.org/wiki/Albert_Einstein_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/div[2]/ul/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
# #     year=re.findall('\d{4}',curr_elem.xpath(".//text"))[0]
#     a_elem=curr_elem.xpath(".//a")
#     if a_elem:
#         year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
# #         more_authors=curr_elem.xpath("./text()")[0].replace(year," ").replace("-","").strip("-")
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('./@title')
#             if winner_title and 'page does not exist' in winner_title[0]:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    

#     else:
#         year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#         list_of_nobel_prize_winners.append([int(year),re.sub(year,''," ".join(curr_elem.xpath("./text()"))).strip("\n").strip(":"),"Page does not exist",purpose])

# nobel_prize_page='https://en.wikipedia.org/wiki/Enrico_Fermi_Award'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table[1]/tbody/tr/td/ul/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
# #     year=re.findall('\d{4}',curr_elem.xpath(".//text"))[0]
#     a_elem=curr_elem.xpath(".//a")
#     if a_elem:
#         year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
# #         more_authors=curr_elem.xpath("./text()")[0].replace(year," ").replace("-","").strip("-")
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('./@title')
#             if winner_title and 'page does not exist' in winner_title[0]:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    


# nobel_prize_page='https://en.wikipedia.org/wiki/Friedmann_Prize'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table[1]/tbody/tr')
# prev=None
# prev_purpose=None
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     purpose_text=None
#     country=None
#     td_elements=each_tr_element.xpath('.//td')
#     if td_elements:
#         last_td=td_elements[len(td_elements)-1]
#         if td_elements[0].xpath('boolean(.//a[contains(@class,"image")])') is False and td_elements[0].xpath('boolean(.//a)') is False and td_elements[0].xpath('boolean(.//span)') is False:
#             year=td_elements[0].text
#             year=year.strip("\n")  
#             if year == '' or year == '–':
#                 year=prev
#             prev=year
#             td_elem=td_elements[1]
#             if len(td_elements)>2:
#                 purpose=' '.join(td_elements[2].xpath(".//descendant::text()")).strip("\n").strip("\t")
#                 prev_purpose=purpose
#             else:
#                 purpose=prev_purpose
#         else:
            
#             year=prev
#             td_elem=td_elements[0]
#             purpose=prev_purpose
#     if year:
#         year=re.sub(paranthesis,'',year)
#     if td_elements:           
#         a_elem=td_elem.xpath('.//a[1]')
#         if not td_elem:
#             a_elem=td_elem.xpath('.//span/a[1]')
#         if a_elem:
#             for each_elem in a_elem:
#                 winner_href=each_elem.xpath('./@href')
#                 winner_title=each_elem.xpath('./text()')
#                 if winner_title and 'page does not exist' in winner_title[0]:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),"Page does not exist",purpose])    
#                     continue
#                 if winner_title and 'ru' in each_elem.xpath(".//text()"):continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])


# nobel_prize_page='https://en.wikipedia.org/wiki/Friedmann_Prize'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table[1]/tbody/tr')
# prev=None
# prev_purpose=None
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     purpose_text=None
#     country=None
#     td_elements=each_tr_element.xpath('.//td')
#     if td_elements:
#         last_td=td_elements[len(td_elements)-1]
#         if td_elements[0].xpath('boolean(.//a[contains(@class,"image")])') is False and td_elements[0].xpath('boolean(.//a)') is False and td_elements[0].xpath('boolean(.//span)') is False:
#             year=td_elements[0].text
#             year=year.strip("\n")  
#             if year == '' or year == '–':
#                 year=prev
#             prev=year
#             td_elem=td_elements[1]
#             if len(td_elements)>2:
#                 purpose=' '.join(td_elements[2].xpath(".//descendant::text()")).strip("\n").strip("\t")
#                 prev_purpose=purpose
#             else:
#                 purpose=prev_purpose
#         else:
            
#             year=prev
#             td_elem=td_elements[0]
#             purpose=prev_purpose
#     if year:
#         year=re.sub(paranthesis,'',year)
#     if td_elements:           
#         a_elem=td_elem.xpath('.//a[1]')
#         if not td_elem:
#             a_elem=td_elem.xpath('.//span/a[1]')
#         if a_elem:
#             for each_elem in a_elem:
#                 winner_href=each_elem.xpath('./@href')
#                 winner_title=each_elem.xpath('./@title')
#                 if winner_title and 'page does not exist' in winner_title[0]:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),"Page does not exist",purpose])    
#                     continue
#                 if winner_title and 'ru' in each_elem.xpath(".//text()"):continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])


# nobel_prize_page='https://en.wikipedia.org/wiki/List_of_Fritz_London_Memorial_Prizes'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul[1]/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
# #     year=re.findall('\d{4}',curr_elem.xpath(".//text"))[0]
#     a_elem=curr_elem.xpath(".//a")
#     if a_elem:
#         year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
# #         more_authors=curr_elem.xpath("./text()")[0].replace(year," ").replace("-","").strip("-")
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('.//text()')
#             if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    

# nobel_prize_page='https://en.wikipedia.org/wiki/Günther_Laukien_Prize'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     a_elem=curr_elem.xpath(".//a")
#     year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if a_elem:
# #         more_authors=curr_elem.xpath("./text()")[0].replace(year," ").replace("-","").strip("-")
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('.//text()')
#             if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    
#     text=" ".join(curr_elem.xpath("./text()"))
#     text=re.sub(year,'',text).replace(' and ',',')
#     names=text.split(',')
#     names=list(filter(None,names))
#     names=[each_name for each_name in names if each_name!=', ' and each_name!=' ' and each_name!='  ']   
#     if names!=[]:
#         for each_name in names:
#             list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(each_name)).strip(":").strip(" "),"Page does not exist",purpose]) 


# nobel_prize_page='https://en.wikipedia.org/wiki/H._C._Ørsted_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul[not(contains(./li/a/@class,"external text"))]/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     a_elem=curr_elem.xpath(".//a")
#     year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('.//text()')
#             if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    



square_braces=re.compile(r'\[.*\]')
# nobel_prize_page='https://en.wikipedia.org/wiki/Haitinger_Prize'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul/li[not(contains(.//descendant::cite/@class,"citation journal"))]|//*[@id="mw-content-text"]/div/dl')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     if curr_elem.xpath('name()')=='li':
#         a_elem=curr_elem.xpath(".//a[not(parent::sup)]")
#         text=" ".join(curr_elem.xpath("./text()"))
#         if not text:continue
#         year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#         prev_year=year
#         if a_elem:
#             for each_a_elem in a_elem:
#                 winner_href=each_a_elem.xpath('./@href')
#                 winner_title=each_a_elem.xpath('.//text()')
#                 if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    
#     if curr_elem.xpath('name()')=='dl':
#         a_elem=curr_elem.xpath('.//a[not(parent::sup)]')
#         year=prev_year
#         if a_elem:
#             for each_a_elem in a_elem:
#                 winner_href=each_a_elem.xpath('./@href')
#                 winner_title=each_a_elem.xpath('.//text()')
#                 if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(square_braces,"",re.sub(paranthesis,'',strip_accents(winner_title[0]))).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    

#         else:
#             list_of_nobel_prize_winners.append([int(year),re.sub(square_braces,"",re.sub(paranthesis,'',' '.join(curr_elem.xpath('.//descendant::text()')))).strip(":"),"Page does not exist",purpose]) 

# nobel_prize_page='https://en.wikipedia.org/wiki/Hector_Memorial_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table/tbody/tr')
# prev=None
# prev_purpose=None
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     purpose_text=None
#     country=None
#     td_elements=each_tr_element.xpath('.//td')
#     if td_elements:
#         last_td=td_elements[len(td_elements)-1]
#         if td_elements[0].xpath('boolean(.//a[contains(@class,"image")])') is False and td_elements[0].xpath('boolean(.//a)') is False and td_elements[0].xpath('boolean(.//span)') is False:
#             year=td_elements[0].text
#             year=year.strip("\n")  
#     if year:
#         year=re.sub(paranthesis,'',year)
#     if td_elements:           
#         a_elem=td_elements[1].xpath('.//a[1]')
# #         if not td_elem:
# #             a_elem=td_elem.xpath('.//span/a[1]')
#         if a_elem:
#             for each_elem in a_elem:
#                 winner_href=each_elem.xpath('./@href')
#                 winner_title=each_elem.xpath('./@title')
#                 if winner_title and 'page does not exist' in winner_title[0]:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),"Page does not exist",purpose])    
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])

                    

# nobel_prize_page='https://en.wikipedia.org/wiki/IEEE_Heinrich_Hertz_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul[1]/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     marked=False
#     text=' '.join (curr_elem.xpath(".//descendant::text()"))
#     index_pos = re.search('(\d{4})', text)
#     if index_pos:
#         index=index_pos.start()
#         year=text[index:index+4]
#         purpose=text[text.find(')')+1:]
#     if re.search(paranthesis_text,text):
#         country=re.findall('\((.*?)\)',text)
#     a_elem=curr_elem.xpath(".//a") 
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('.//text()')
#             if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:
#                 marked=True
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_title and winner_title[0]:
#                 if purpose and winner_title[0].lower() in purpose:
#                     continue
#                 if country and any (True for each_country in country if re.sub('\(country\)','',winner_title[0]) in each_country)==True:
#                     continue    
#             if winner_href and winner_title:
#                 marked=True
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    
      
#     if not marked:
#         name=text[index+4:text.find('(')]
#         list_of_nobel_prize_winners.append([int(year),name.strip(":").strip(" "),"Page does not exist",purpose])

 


# nobel_prize_page='https://en.wikipedia.org/wiki/Henri_Poincaré_Prize'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr')
# prev=None
# prev_purpose=None
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     purpose_text=None
#     country=None
#     td_elements=each_tr_element.xpath('.//td')
#     if td_elements:
#         last_td=td_elements[len(td_elements)-1]
#         if td_elements[0].xpath('boolean(.//a[contains(@class,"image")])') is False and td_elements[0].xpath('boolean(.//a)') is False and td_elements[0].xpath('boolean(.//span)') is False:
#             year=td_elements[0].text
#             year=year.strip("\n")  
#     if year:
#         year=re.sub(paranthesis,'',year)
#     if td_elements:           
#         a_elem=td_elements[2].xpath('.//a')
#         if a_elem:
#             for each_elem in a_elem:
#                 winner_href=each_elem.xpath('./@href')
#                 winner_title=each_elem.xpath('./@title')
#                 if winner_title and 'page does not exist' in winner_title[0]:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),"Page does not exist",purpose])    
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])


# nobel_prize_page='https://en.wikipedia.org/wiki/Infosys_Prize'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr')
# prev=None
# prev_purpose=None
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     purpose_text=None
#     country=None
#     td_elements=each_tr_element.xpath('.//td')
#     year=each_tr_element.xpath("./th/text()")[0].strip("\n") 
#     if year:
#         year=re.sub(paranthesis,'',year)
#     if td_elements:   
#         a_elem=td_elements[0].xpath('.//a')
#         if a_elem:
#             for each_elem in a_elem:
#                 winner_href=each_elem.xpath('./@href')
#                 winner_title=each_elem.xpath('./@title')
#                 if winner_title and 'page does not exist' in winner_title[0]:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),"Page does not exist",purpose])    
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])


# square_braces=re.compile(r'\[.*\]')
# nobel_prize_page='https://en.wikipedia.org/wiki/International_Dennis_Gabor_Award#2010'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/h3|//*[@id="mw-content-text"]/div/ul/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     if curr_elem.xpath('name()')=='h3':
#         year=curr_elem.xpath("./span[1]/text()")[0].strip(":").strip(" ").strip(":").strip("-")
#         prev_year=year
#     if curr_elem.xpath('name()')=='li':       
#         text=" ".join(curr_elem.xpath("./text()[not(parent::sup)]"))
#         index_pos=text.find('for')
#         if index_pos==-1:
#             purpose=None
#         if index_pos!=-1:
#             purpose=text[index_pos:]
#         a_elem=curr_elem.xpath('.//a[not(parent::sup)]')
#         year=prev_year
#         if a_elem:
#             for each_a_elem in a_elem:
#                 winner_href=each_a_elem.xpath('./@href')
#                 winner_title=each_a_elem.xpath('.//text()')
#                 if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(square_braces,"",re.sub(paranthesis,'',strip_accents(winner_title[0]))).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    

#         else:
#             list_of_nobel_prize_winners.append([int(year),re.sub(square_braces,"",re.sub(paranthesis,'',' '.join(curr_elem.xpath('.//descendant::text()')))).strip(":"),"Page does not exist",purpose]) 


# nobel_prize_page='https://en.wikipedia.org/wiki/J._Robert_Oppenheimer_Memorial_Prize'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     a_elem=curr_elem.xpath(".//a[not(parent::sup)]")
#     year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('.//text()')
#             if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    


# nobel_prize_page='https://en.wikipedia.org/wiki/Jacques_Herbrand_Prize'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul[1]/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     text=" ".join(curr_elem.xpath(".//text()"))
    
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span)]")
#     if re.search(paranthesis_text,text):
#         country=re.findall('\((.*?)\)',text)
#     year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('.//text()')
#             if winner_title and winner_title[0]:
#                 if country and any (True for each_country in country if re.sub('\(country\)','',winner_title[0]) in each_country)==True:
#                     continue
#             if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    


# nobel_prize_page='https://en.wikipedia.org/wiki/John_Price_Wetherill_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     text=" ".join(curr_elem.xpath(".//text()")) 
#     year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")


#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span)]")
#     if re.search(paranthesis_text,text):
#         country=re.findall('\((.*?)\)',text)
#     year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('.//text()')
#             if winner_title and winner_title[0]:
#                 if country and any (True for each_country in country if re.sub('\(country\)','',winner_title[0]) in each_country)==True:
#                     continue
#             if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    


# nobel_prize_page='https://en.wikipedia.org/wiki/Oskar_Klein_Memorial_Lecture'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/div/ul/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     text=" ".join(curr_elem.xpath(".//text()")) 
#     year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span)]")
#     if re.search(paranthesis_text,text):
#         country=re.findall('\((.*?)\)',text)
#     year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('.//text()')
#             if winner_title and winner_title[0]:
#                 if country and any (True for each_country in country if re.sub('\(country\)','',winner_title[0]) in each_country)==True:
#                     continue
#             if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    

#     else:
#         name=text[text.find('-')+1:text.find(',')-1]
#         list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',name).strip(":"),"Page does not exist",purpose])    

# nobel_prize_page='https://en.wikipedia.org/wiki/Klopsteg_Memorial_Award'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody/tr')
# prev=None
# prev_purpose=None
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     purpose_text=None
#     country=None
#     td_elements=each_tr_element.xpath('.//td')
#     year=each_tr_element.xpath("./th/text()")[0].strip("\n") 
#     if year:
#         year=re.sub(paranthesis,'',year)
#     if td_elements:   
#         a_elem=td_elements[0].xpath('.//a')
#         if a_elem:
#             for each_elem in a_elem:
#                 winner_href=each_elem.xpath('./@href')
#                 winner_title=each_elem.xpath('./@title')
#                 if winner_title and 'page does not exist' in winner_title[0]:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),"Page does not exist",purpose])    
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])
#         else:
#             name=each_tr_element.xpath("./td[1]/text()")[0].strip("\n") 
#             list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',name).strip(":"),"Page does not exist",purpose])    


# nobel_prize_page='https://en.wikipedia.org/wiki/Klung_Wilhelmy_Science_Award'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table/tbody/tr')
# prev=None
# prev_purpose=None
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     purpose_text=None
#     country=None
#     td_elements=each_tr_element.xpath('.//td')
#     if td_elements:   
#         for each_td in td_elements:
#             year=re.findall('(\d{4})'," ".join(each_td.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#             a_elem=each_td.xpath('.//a[not(parent::span) and not(parent::sup)]')
#             text=" ".join(each_td.xpath('.//descendant::text()'))
#             index_pos=text.find('for')

#             if index_pos and index_pos==-1:
#                 purpose=None
#             if index_pos and index_pos!=-1:
#                 purpose=text[index_pos:]   
#             if a_elem:
#                 for each_elem in a_elem:
#                     winner_href=each_elem.xpath('./@href')
#                     winner_title=each_elem.xpath('./@title')
#                     if 'Nobel Prize' in winner_title[0]:continue
#                     if winner_title and 'page does not exist' in winner_title[0]:
#                         list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),"Page does not exist",purpose])    
#                         continue
#                     if winner_href and winner_title:
#                         list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])

# nobel_prize_page='https://en.wikipedia.org/wiki/Kotcherlakota_Rangadhama_Rao_Memorial_Lecture_Award'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr')
# prev=None
# prev_purpose=None
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     purpose_text=None
#     country=None
#     td_elements=each_tr_element.xpath('.//td')
#     if td_elements:   
#         year=td_elements[3].xpath(".//text()")[0].strip(" ")
#         purpose= td_elements[4].xpath(".//text()")[0].strip(" ").strip("\n")
#         if purpose==" " or purpose=="":
#             purpose=None
            
#         a_elem=td_elements[1].xpath('.//a[not(parent::span) and not(parent::sup)]')
#         if a_elem:  
#             for each_elem in a_elem:
#                 winner_href=each_elem.xpath('./@href')
#                 winner_title=each_elem.xpath('./@title')
#                 if 'Nobel Prize' in winner_title[0]:continue
#                 if winner_title and 'page does not exist' in winner_title[0]:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),"Page does not exist",purpose])    
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])



# nobel_prize_page='https://en.wikipedia.org/wiki/Kurchatov_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul/li[not(contains(./a/@class,"external text")) and not(contains(./a/@class,"mw-redirect"))]')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     text=" ".join(curr_elem.xpath(".//text()"))   
#     year=re.findall('(\d{4})',text)[0].strip(":").strip(" ").strip(":").strip("-")
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))]")
#     if re.search(paranthesis_text,text):
#         country=re.findall('\((.*?)\)',text)
#     year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('.//text()')
#             if winner_title and winner_title[0]:
#                 if country and any (True for each_country in country if re.sub('\(country\)','',winner_title[0]) in each_country)==True:
#                     continue
#             if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    

# nobel_prize_page='https://en.wikipedia.org/wiki/Landau_Gold_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul[1]/li[not(contains(./a/@class,"external text")) and not(contains(./a/@class,"mw-redirect"))]')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))]")
#     year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('.//text()')
#             if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    
#     text=" ".join(curr_elem.xpath("./text()"))
#     text=re.sub(year,'',text).replace(' and ',',').replace("-","")
#     text=re.sub("\s+"," ",text)
#     names=text.split(',')    
#     names=list(filter(None,names))
#     names=[each_name for each_name in names if each_name!=', ' and each_name!=' ' and each_name!='  '] 
#     if names!=[]:
#         for each_name in names:
#             list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(each_name)).strip(":").strip(" "),"Page does not exist",purpose]) 

                  
# nobel_prize_page='https://en.wikipedia.org/wiki/Leconte_Prize'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul/li[not(contains(./a/@class,"external text")) and not(contains(./a/@class,"mw-redirect"))]')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     full_text=" ".join(curr_elem.xpath("./descendant::text()"))
#     if 'No award' in full_text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))]")
#     year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('.//text()')
#             if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:
            
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       
#     text=curr_elem.xpath(".//text()")[0]
#     text=re.sub(year,'',text).replace(' and ',';').replace("-","").replace(":","")
#     text=re.sub("\s+"," ",text)
#     names=text.split(';')    
#     names=list(filter(None,names))
#     names=[each_name for each_name in names if each_name!=', ' and each_name!=' ' and each_name!='  ']
#     if names!=[]:
#         for each_name in names:
#             list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(each_name)).strip(":").strip(" "),"Page does not exist",purpose]) 


# nobel_prize_page='https://en.wikipedia.org/wiki/Lieben_Prize'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul/li[not(contains(./a/@class,"external text")) and not(contains(./a/@class,"mw-redirect"))]')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     full_text=" ".join(curr_elem.xpath("./descendant::text()"))
#     if 'Not award' in full_text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))]")
#     year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('.//text()')
#             if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:
            
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       

# nobel_prize_page='https://en.wikipedia.org/wiki/Lise_Meitner_Distinguished_Lecture'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     full_text=" ".join(curr_elem.xpath("./descendant::text()"))
#     if 'Not award' in full_text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))]")
#     year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('.//text()')
#             if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:          
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       

# nobel_prize_page='https://en.wikipedia.org/wiki/Lorentz_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table/tbody/tr')
# prev=None
# prev_purpose=None
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     purpose_text=None
#     country=None
#     td_elements=each_tr_element.xpath('.//td')
#     if td_elements:   
#         year=td_elements[0].xpath(".//text()")[0].strip(" ")
#         a_elem=td_elements[1].xpath('.//a[not(parent::span) and not(parent::sup)]')
#         if a_elem:  
#             for each_elem in a_elem:
#                 winner_href=each_elem.xpath('./@href')
#                 winner_title=each_elem.xpath('./@title')
#                 if winner_title and 'page does not exist' in winner_title[0]:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),"Page does not exist",purpose])    
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])


# nobel_prize_page='https://en.wikipedia.org/wiki/Thomas_Ranken_Lyle_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table/tbody/tr')
# prev=None
# prev_purpose=None
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     purpose_text=None
#     country=None
#     td_elements=each_tr_element.xpath('.//td')
#     if td_elements:  
#         year=td_elements[0].xpath(".//text()")[0].strip(" ")
#         a_elem=td_elements[1].xpath('.//a[not(parent::sup)]')
#         if a_elem:  
#             for each_elem in a_elem:
#                 winner_href=each_elem.xpath('./@href')
#                 winner_title=each_elem.xpath('./@title')
#                 if winner_title and 'page does not exist' in winner_title[0]:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),"Page does not exist",purpose])    
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])


# nobel_prize_page='https://en.wikipedia.org/wiki/Medard_W._Welch_Award'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table/tbody/tr')
# prev=None
# prev_purpose=None
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     purpose_text=None
#     country=None
#     td_elements=each_tr_element.xpath('.//td')
#     if td_elements:  
#         year=re.findall('(\d{4})'," ".join(td_elements[0].xpath(".//text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#         a_elem=td_elements[1].xpath('.//a[not(parent::sup)]')
#         purpose=td_elements[2].xpath('.//text()')[0]
#         if a_elem:  
#             for each_elem in a_elem:
#                 winner_href=each_elem.xpath('./@href')
#                 winner_title=each_elem.xpath('./@title')
#                 if winner_title and 'page does not exist' in winner_title[0]:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),"Page does not exist",purpose])    
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])
#         else:
#             name=td_elements[1].xpath('.//text()')[0].strip("\n")
#             list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',name).strip("\n"),"Page does not exist",purpose])


# nobel_prize_page='https://en.wikipedia.org/wiki/Luigi_G._Napolitano_Award'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul[1]/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     full_text=" ".join(curr_elem.xpath(".//text()[not(parent::a)]"))
#     if 'Not award' in full_text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))]")
#     year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     name=re.sub(year,'',full_text).strip("\n").strip(" ")
#     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',name).strip(":"),"Page does not exist",purpose])       

# nobel_prize_page='https://en.wikipedia.org/wiki/National_Prize_for_Exact_Sciences_(Chile)'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul[1]/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     full_text=" ".join(curr_elem.xpath(".//text()"))
#     if 'Not award' in full_text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))]")
#     year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('.//text()')
#             if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:          
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       
#     text=curr_elem.xpath(".//text()")[0]
#     text=re.sub(paranthesis,'',text)
#     text=re.sub(year,'',text).replace(' and ',';').replace("-","").replace(":","")
#     text=re.sub("\s+"," ",text)
#     names=text.split(';')    
#     names=list(filter(None,names))
#     names=[each_name for each_name in names if each_name!=', ' and each_name!=' ' and each_name!='  ']
#     if names!=[]:
#         for each_name in names:
#             list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(each_name)).strip(":").strip(" ").strip(","),"Page does not exist",purpose]) 


# nobel_prize_page='https://en.wikipedia.org/wiki/Louis_Néel_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/div[1]/ul/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     full_text=" ".join(curr_elem.xpath(".//text()"))
#     if 'Not award' in full_text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))]")
#     year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('.//text()')
#             if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:          
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       


# nobel_prize_page='https://en.wikipedia.org/wiki/Niels_Bohr_Institute'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul[1]/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     full_text=" ".join(curr_elem.xpath(".//text()"))
#     if 'Not award' in full_text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))]")
#     year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('.//text()')
#             if each_a_elem.xpath('./@title') and 'Glacio' in each_a_elem.xpath('./@title')[0] :continue
#             if each_a_elem.xpath('./@title') and 'Astrophysicist' in each_a_elem.xpath('./@title')[0]:continue
#             if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:          
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       

# nobel_prize_page='https://en.wikipedia.org/wiki/Nishina_Memorial_Prize'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul/li[not(contains(./a/@class,"external text")) and not(contains(./a/@class,"mw-redirect"))]')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     text=' '.join(curr_elem.xpath(".//descendant::text()"))
#     if re.search(paranthesis_text,text):
#         country=re.findall('\((.*?)\)',text)
#     if 'Not award' in text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))]")
#     year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('.//text()')
#             if country and any (True for each_country in country if re.sub('\(country\)','',winner_title[0]) in each_country)==True:
#                     continue
#             if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:          
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       

# nobel_prize_page='https://en.wikipedia.org/wiki/Giuseppe_Occhialini_Medal_and_Prize'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table[1]/tbody/tr')
# prev=None
# prev_purpose=None
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     purpose_text=None
#     country=None
#     td_elements=each_tr_element.xpath('.//td')
#     if td_elements:  
#         year=re.findall('(\d{4})'," ".join(td_elements[0].xpath(".//text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#         a_elem=td_elements[1].xpath('.//a[not(parent::sup) and not(parent::span)]')
#         purpose=td_elements[3].xpath('.//text()')[0]
#         if a_elem:  
#             for each_elem in a_elem:
#                 winner_href=each_elem.xpath('./@href')
#                 winner_title=each_elem.xpath('./@title')
#                 if winner_title and 'page does not exist' in winner_title[0]:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),"Page does not exist",purpose])    
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])


# nobel_prize_page='https://en.wikipedia.org/wiki/Oersted_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/div[2]/ul/li[not(contains(./a/@class,"external text")) and not(contains(./a/@class,"mw-redirect"))]')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     text=' '.join(curr_elem.xpath(".//descendant::text()"))
#     if re.search(paranthesis_text,text):
#         country=re.findall('\((.*?)\)',text)
#     if 'not award' in text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))]")
#     year=re.findall('(\d{4})',text)[0].strip(":").strip(" ").strip(":").strip("-")
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('.//text()')
#             if country and any (True for each_country in country if re.sub('\(country\)','',winner_title[0]) in each_country)==True:
#                     continue
#             if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:          
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       

# nobel_prize_page='https://en.wikipedia.org/wiki/Om_Prakash_Bhasin_Award'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table[5]/tbody/tr')
# prev=None
# prev_purpose=None
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     purpose_text=None
#     country=None
#     td_elements=each_tr_element.xpath('.//td')
#     if td_elements:  
#         year=re.findall('(\d{4})'," ".join(td_elements[0].xpath(".//text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#         a_elem=td_elements[1].xpath('.//a[not(parent::sup) and not(parent::span)]')
# #         purpose=td_elements[3].xpath('.//text()')[0]
#         if a_elem:  
#             for each_elem in a_elem:
#                 winner_href=each_elem.xpath('./@href')
#                 winner_title=each_elem.xpath('./@title')
#                 if winner_title and 'page does not exist' in winner_title[0]:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),"Page does not exist",purpose])    
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])
#         else:
#             name=td_elements[1].xpath('.//text()')[0].strip("\n")
#             list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',name).strip("\n"),"Page does not exist",purpose])

                    
# nobel_prize_page='https://en.wikipedia.org/wiki/Pawsey_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table/tbody/tr')
# prev=None
# prev_purpose=None
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     purpose_text=None
#     country=None
#     td_elements=each_tr_element.xpath('.//td')
#     if td_elements:  
#         year=re.findall('(\d{4})'," ".join(td_elements[0].xpath(".//text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#         a_elem=td_elements[1].xpath('.//a[not(parent::sup) and not(parent::span)]')
#         if a_elem:  
#             for each_elem in a_elem:
#                 winner_href=each_elem.xpath('./@href')
#                 winner_title=each_elem.xpath('./@title')
#                 if winner_title and 'page does not exist' in winner_title[0]:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),"Page does not exist",purpose])    
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])
#         else:
#             name=td_elements[1].xpath('.//text()')[0].strip("\n")
#             list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',name).strip("\n"),"Page does not exist",purpose])

# nobel_prize_page='https://en.wikipedia.org/wiki/Peter_Mark_Memorial_award'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr')
# prev=None
# prev_purpose=None
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     purpose_text=None
#     country=None
#     td_elements=each_tr_element.xpath('.//td')
#     if td_elements:  
#         year=re.findall('(\d{4})'," ".join(td_elements[0].xpath(".//text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#         a_elem=td_elements[1].xpath('.//a[not(parent::sup) and not(parent::span)]')
#         purpose=td_elements[3].xpath('.//text()')[0].strip("\n").strip(" ")
#         if purpose==' ' or purpose=='':
#             purpose=None
#         if a_elem:  
#             for each_elem in a_elem:
#                 winner_href=each_elem.xpath('./@href')
#                 winner_title=each_elem.xpath('./@title')
#                 if winner_title and 'page does not exist' in winner_title[0]:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),"Page does not exist",purpose])    
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])
        
#         else:
#             name=td_elements[1].xpath('.//text()')[0].strip("\n")
#             list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',name).strip("\n"),"Page does not exist",purpose])

# nobel_prize_page='https://en.wikipedia.org/wiki/Pomeranchuk_Prize'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul[1]/li[not(contains(./a/@class,"external text")) and not(contains(./a/@class,"mw-redirect"))]')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     text=' '.join(curr_elem.xpath(".//descendant::text()"))
#     if re.search(paranthesis_text,text):
#         country=re.findall('\((.*?)\)',text)
#     if 'not award' in text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))]")
#     year=re.findall('(\d{4})',text)[0].strip(":").strip(" ").strip(":").strip("-")
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('.//text()')
#             if country and any (True for each_country in country if re.sub('\(country\)','',winner_title[0]) in each_country)==True:
#                     continue
#             if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:          
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       
 


# nobel_prize_page='https://en.wikipedia.org/wiki/Ampère_Prize'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/div[2]/ul/li[not(contains(./a/@class,"external text")) and not(contains(./a/@class,"mw-redirect"))]')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     text=' '.join(curr_elem.xpath(".//descendant::text()"))
#     if re.search(paranthesis_text,text):
#         country=re.findall('\((.*?)\)',text)
#     if 'not award' in text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))]")
#     year=re.findall('(\d{4})',text)[0].strip(":").strip(" ").strip(":").strip("-")
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('.//text()')
#             if country and any (True for each_country in country if re.sub('\(country\)','',winner_title[0]) in each_country)==True:
#                     continue
#             if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:          
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       
 

# nobel_prize_page='https://en.wikipedia.org/wiki/Rayleigh_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/div[1]/ul/li[not(contains(./a/@class,"external text")) and not(contains(./a/@class,"mw-redirect"))]')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     text=' '.join(curr_elem.xpath(".//descendant::text()"))
#     if re.search(paranthesis_text,text):
#         country=re.findall('\((.*?)\)',text)
#     if 'not award' in text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))]")
#     year=re.findall('(\d{4})',text)[0].strip(":").strip(" ").strip(":").strip("-")
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('.//text()')
#             if country and any (True for each_country in country if re.sub('\(country\)','',winner_title[0]) in each_country)==True:
#                     continue
#             if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:          
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       


# nobel_prize_page='https://en.wikipedia.org/wiki/Richtmyer_Memorial_Award'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul/li[not(contains(./a/@class,"external text")) and not(contains(./a/@class,"mw-redirect"))]')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     text=' '.join(curr_elem.xpath(".//descendant::text()"))
#     if re.search(paranthesis_text,text):
#         country=re.findall('\((.*?)\)',text)
#     if 'not award' in text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))][1]")
#     year=re.findall('(\d{4})',text)[0].strip(":").strip(" ").strip(":").strip("-")
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('.//text()')
#             if country and any (True for each_country in country if re.sub('\(country\)','',winner_title[0]) in each_country)==True:
#                     continue
#             if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:          
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       


# nobel_prize_page='https://en.wikipedia.org/wiki/Robert_A._Millikan_award'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr')
# prev=None
# prev_purpose=None
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     purpose_text=None
#     country=None
#     td_elements=each_tr_element.xpath('.//td')
#     if td_elements:  
#         year=re.findall('(\d{4})'," ".join(td_elements[0].xpath(".//text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#         a_elem=td_elements[1].xpath('.//a[not(parent::sup) and not(parent::span)]')
#         #purpose=td_elements[3].xpath('.//text()')[0].strip("\n").strip(" ")
#         if purpose==' ' or purpose=='':
#             purpose=None
#         if a_elem:  
#             for each_elem in a_elem:
#                 winner_href=each_elem.xpath('./@href')
#                 winner_title=each_elem.xpath('./@title')
#                 if winner_title and 'page does not exist' in winner_title[0]:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),"Page does not exist",purpose])    
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])
        
#         else:
#             name=td_elements[1].xpath('.//text()')[0].strip("\n")
#             list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',name).strip("\n"),"Page does not exist",purpose])

# nobel_prize_page='https://en.wikipedia.org/wiki/Russell_Varian_Prize'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul[1]/li[not(contains(./a/@class,"external text")) and not(contains(./a/@class,"mw-redirect"))]')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     text=' '.join(curr_elem.xpath(".//descendant::text()"))
#     if 'not award' in text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))][1]")
#     year=re.findall('(\d{4})',text)[0].strip(":").strip(" ").strip(":").strip("-")
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('./@title')
#             if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:          
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       
 


# nobel_prize_page='https://en.wikipedia.org/wiki/Rutherford_Medal_(Royal_Society_of_New_Zealand)'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul[1]/li[not(contains(./a/@class,"external text")) and not(contains(./a/@class,"mw-redirect"))]')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     text=' '.join(curr_elem.xpath(".//descendant::text()"))
#     if not re.findall('(\d{4})',text):continue

#     if 'No award' in text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))][1]")
#     year=re.findall('(\d{4})',' '.join(curr_elem.xpath(".//text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if year:
#         if a_elem:
#             for each_a_elem in a_elem:
#                 winner_href=each_a_elem.xpath('./@href')
#                 winner_title=each_a_elem.xpath('./@title')
#                 if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:          
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       
#         else:
#             name=re.sub(year,"",text)
#             name=re.sub(r'\,.*','',name)

#             list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',name).strip("\n").strip(":"),"Page does not exist",purpose])


# nobel_prize_page='https://en.wikipedia.org/wiki/Abdus_Salam_Award'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul/li[not(contains(./a/@class,"external text")) and not(contains(./a/@class,"mw-redirect"))]')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     text=' '.join(curr_elem.xpath(".//descendant::text()"))
#     if not re.findall('(\d{4})',text):continue
#     if 'No award' in text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))][1]")
#     year=re.findall('(\d{4})',' '.join(curr_elem.xpath(".//text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if year:
#         if a_elem:
#             for each_a_elem in a_elem:
#                 winner_href=each_a_elem.xpath('./@href')
#                 winner_title=each_a_elem.xpath('./@title')
#                 if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:          
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       
#         else:
#             name=re.sub(year,"",text)
#             name=re.sub(paranthesis,'',name)
#             name=re.sub(r'\,.*','',name).replace("–",'').replace("-","")

#             list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',name).strip("\n").strip(":"),"Page does not exist",purpose])


            
# nobel_prize_page='https://en.wikipedia.org/wiki/R_W_B_Stephens_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/div[1]/ul/li[not(contains(./a/@class,"external text")) and not(contains(./a/@class,"mw-redirect"))]')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     text=' '.join(curr_elem.xpath(".//descendant::text()"))
#     if not re.findall('(\d{4})',text):continue
#     if 'No award' in text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))][1]")
#     year=re.findall('(\d{4})',' '.join(curr_elem.xpath(".//text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if year:
#         if a_elem:
#             for each_a_elem in a_elem:
#                 winner_href=each_a_elem.xpath('./@href')
#                 winner_title=each_a_elem.xpath('./@title')
#                 if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:          
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       
#         else:
#             name=re.sub(year,"",text)
#             name=re.sub(paranthesis,'',name)
#             name=re.sub(r'\,.*','',name).replace("–",'').replace("-","")

#             list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',name).strip("\n").strip(":"),"Page does not exist",purpose])


# nobel_prize_page='https://en.wikipedia.org/wiki/Three_Physicists_Prize'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/div[1]/ul/li[not(contains(./a/@class,"external text")) and not(contains(./a/@class,"mw-redirect"))]')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     text=' '.join(curr_elem.xpath(".//descendant::text()"))
#     if not re.findall('(\d{4})',text):continue
#     if 'No award' in text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))][1]")
#     year=re.findall('(\d{4})',' '.join(curr_elem.xpath(".//text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if year:
#         if a_elem:
#             for each_a_elem in a_elem:
#                 winner_href=each_a_elem.xpath('./@href')
#                 winner_title=each_a_elem.xpath('./@title')
#                 if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:          
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       
             
# nobel_prize_page='https://en.wikipedia.org/wiki/Tomassoni_awards'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul/li[not(contains(./a/@class,"external text")) and not(contains(./a/@class,"mw-redirect"))]')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     text=' '.join(curr_elem.xpath(".//descendant::text()"))
#     if not re.findall('(\d{4})',text):continue
#     if 'No award' in text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))][1]")
#     year=re.findall('(\d{4})',' '.join(curr_elem.xpath(".//text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if year:
#         if a_elem:
#             for each_a_elem in a_elem:
#                 winner_href=each_a_elem.xpath('./@href')
#                 winner_title=each_a_elem.xpath('./@title')
#                 if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:          
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       


# nobel_prize_page='https://en.wikipedia.org/wiki/Henri_Poincaré_Prize'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr')
# prev=None
# prev_purpose=None
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     purpose_text=None
#     country=None
#     td_elements=each_tr_element.xpath('.//td')
#     if td_elements:
#         last_td=td_elements[len(td_elements)-1]
#         if td_elements[0].xpath('boolean(.//a[contains(@class,"image")])') is False and td_elements[0].xpath('boolean(.//a)') is False and td_elements[0].xpath('boolean(.//span)') is False:
#             year=td_elements[0].text
#             year=year.strip("\n")  
#     if year:
#         year=re.sub(paranthesis,'',year)
#     if td_elements:           
#         a_elem=td_elements[2].xpath('.//a')
#         if a_elem:
#             for each_elem in a_elem:
#                 winner_href=each_elem.xpath('./@href')
#                 winner_title=each_elem.xpath('./@title')
#                 if winner_title and 'page does not exist' in winner_title[0]:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),"Page does not exist",purpose])    
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])

# nobel_prize_page='https://en.wikipedia.org/wiki/Walter_Boas_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul[1]/li[not(contains(./a/@class,"external text")) and not(contains(./a/@class,"mw-redirect"))]')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     text=' '.join(curr_elem.xpath(".//descendant::text()"))
#     if not re.findall('(\d{4})',text):continue
#     if 'No medal award' in text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))][1]")
#     year=re.findall('(\d{4})',' '.join(curr_elem.xpath(".//text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if year:
#         if a_elem:
#             for each_a_elem in a_elem:
#                 winner_href=each_a_elem.xpath('./@href')
#                 winner_title=each_a_elem.xpath('./@title')
#                 if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:          
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       

#         else:
#             name=re.sub(year,"",text)
#             name=re.sub(paranthesis,'',name)
#             name=re.sub(r'\,.*','',name).replace("–",'').replace("-","")
#             list_of_nobel_prize_winners.append([int(year),re.sub(square_braces,'',re.sub(paranthesis,'',name)).strip("\n").strip(":"),"Page does not exist",purpose])


# nobel_prize_page='https://en.wikipedia.org/wiki/Wigner_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul[1]/li[not(contains(./a/@class,"external text")) and not(contains(./a/@class,"mw-redirect"))]')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     text=' '.join(curr_elem.xpath(".//descendant::text()"))
#     if not re.findall('(\d{4})',text):continue
#     if 'not award' in text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))][1]")
#     year=re.findall('(\d{4})',' '.join(curr_elem.xpath(".//text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if year:
#         if a_elem:
#             for each_a_elem in a_elem:
#                 winner_href=each_a_elem.xpath('./@href')
#                 winner_title=each_a_elem.xpath('./@title')
#                 if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:          
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       

# nobel_prize_page='https://en.wikipedia.org/wiki/A_B_Wood_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/div[1]/ul/li[not(contains(./a/@class,"external text")) and not(contains(./a/@class,"mw-redirect"))]')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     text=' '.join(curr_elem.xpath(".//descendant::text()"))
#     if not re.findall('(\d{4})',text):continue
#     if 'not award' in text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))][1]")
#     year=re.findall('(\d{4})',' '.join(curr_elem.xpath(".//text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if year:
#         if a_elem:
#             for each_a_elem in a_elem:
#                 winner_href=each_a_elem.xpath('./@href')
#                 winner_title=each_a_elem.xpath('./@title')
#                 if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:          
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       
#         else:
#             name=re.sub(year,"",text)
#             name=re.sub(paranthesis,'',name)
#             name=re.sub(r'\,.*','',name).replace("–",'').replace("-","")
#             list_of_nobel_prize_winners.append([int(year),re.sub(square_braces,'',re.sub(paranthesis,'',name)).strip("\n").strip(":"),"Page does not exist",purpose])


# nobel_prize_page='https://en.wikipedia.org/wiki/Tyndall_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/div[1]/ul/li[not(contains(./a/@class,"external text")) and not(contains(./a/@class,"mw-redirect"))]')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     text=' '.join(curr_elem.xpath(".//descendant::text()"))
#     if not re.findall('(\d{4})',text):continue
#     if 'not award' in text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span) and not(contains(@rel,'nofollow'))][1]")
#     year=re.findall('(\d{4})',' '.join(curr_elem.xpath(".//text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if year:
#         if a_elem:
#             for each_a_elem in a_elem:
#                 winner_href=each_a_elem.xpath('./@href')
#                 winner_title=each_a_elem.xpath('./@title')
#                 if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:          
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       
#         else:
#             name=re.sub(year,"",text)
#             name=re.sub(paranthesis,'',name)
#             name=re.sub(r'\,.*','',name).replace("–",'').replace("-","")
#             list_of_nobel_prize_winners.append([int(year),re.sub(square_braces,'',re.sub(paranthesis,'',name)).strip("\n").strip(":"),"Page does not exist",purpose])



# nobel_prize_page='https://en.wikipedia.org/wiki/Albert_Einstein_World_Award_of_Science'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr')
# prev=None
# prev_purpose=None
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     purpose_text=None
#     country=None
#     td_elements=each_tr_element.xpath('.//td')
#     if td_elements:  
#         text=' '.join(td_elements[1].xpath(".//text()"))
#         if 'no award' in text:
#             continue
#         if td_elements[0].xpath('boolean(.//a[contains(@class,"image")])') is False and td_elements[0].xpath('boolean(.//a)') is False:
#             #print(len(td_elements))
#             year=td_elements[0].text
#             year=year.strip("\n")
#         a_elem=td_elements[1].xpath('.//a[not(parent::sup) and not(parent::span)]')
#         if a_elem:  
#             for each_elem in a_elem:
#                 winner_href=each_elem.xpath('./@href')
#                 winner_title=each_elem.xpath('./@title')
#                 if winner_title and 'page does not exist' in winner_title[0]:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),"Page does not exist",purpose])    
#                     continue
#                 if winner_href and winner_title:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])

# square_braces=re.compile(r'\[.*\]')
# nobel_prize_page='https://en.wikipedia.org/wiki/Alexander_Hollaender_Award_in_Biophysics'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul/li[not(contains(.//descendant::cite/@class,"citation journal"))]|//*[@id="mw-content-text"]/div/dl')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     if curr_elem.xpath('name()')=='li':
#         a_elem=curr_elem.xpath(".//a[not(parent::sup)]")
#         text=" ".join(curr_elem.xpath("./text()"))
#         if not text:continue
#         year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#         prev_year=year
#         if a_elem:
#             for each_a_elem in a_elem:
#                 winner_href=each_a_elem.xpath('./@href')
#                 winner_title=each_a_elem.xpath('.//text()')
#                 if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                     continue
#     if curr_elem.xpath('name()')=='dl':
#         purpose=' '.join(curr_elem.xpath('.//descendant::text()')).strip('"')
#         if winner_href and winner_title:
#             list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    
 

# nobel_prize_page='https://en.wikipedia.org/wiki/H._C._Ørsted_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul[not(contains(./li/a/@class,"external text"))]/li')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     a_elem=curr_elem.xpath(".//a")
#     year=re.findall('(\d{4})'," ".join(curr_elem.xpath("./text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if a_elem:
#         for each_a_elem in a_elem:
#             winner_href=each_a_elem.xpath('./@href')
#             winner_title=each_a_elem.xpath('.//text()')
#             if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                 continue
#             if winner_href and winner_title:
#                 list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])    

#hughes prize
# nobel_prize_page='https://en.wikipedia.org/wiki/Hughes_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table/tbody/tr')
# #print(tr_elements)
# purpose=None
# for each_tr_element in tr_elements:
#     td_elements=each_tr_element.xpath('.//td')
#    # print(td_elements)
#     #list_of_winner_elem=[]
#     if td_elements:  
#         year=td_elements[0].text
#         winner_href=each_tr_element.xpath('.//td[2]//a/@href')
#         winner_title=each_tr_element.xpath('.//td[2]//a/@title')
#         if winner_href and winner_title:
#             winner_info=list(zip(winner_title,winner_href))
#             for each_winner_info in winner_info:
#                 list_of_nobel_prize_winners.append([year,re.sub(paranthesis,'',strip_accents(each_winner_info[0])),parse_web.urlCanonicalization(each_winner_info[1], base_url=nobel_prize_page),purpose])
            
# nobel_prize_page='https://en.wikipedia.org/wiki/Gregori_Aminoff_Prize'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr')
# #print(tr_elements)
# for each_tr_element in tr_elements:
#     td_elements=each_tr_element.xpath('.//td')
#     if td_elements:
#         text=' '.join(td_elements[1].xpath(".//text()"))
#         if 'no prize award' in text:
#             continue
#         year=td_elements[0].text
#         purpose=' '.join(td_elements[2].xpath('.//descendant::text()')).strip("\n").strip(" ").strip('"')
#         if purpose==" " or purpose=="":
#             purpose=None
#         a_elem=td_elements[1].xpath('.//a[not(parent::sup) and not(parent::span)]')
#         if a_elem:
#             for each_elem in a_elem:
#                 winner_href=each_elem.xpath('./@href')
#                 winner_title=each_elem.xpath('./@title')
#                 if winner_title and 'page does not exist' in winner_title[0]:
#                         list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),"Page does not exist",purpose])    
#                         continue
#                 if winner_href and winner_title:
#                         list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip("\n"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])


# square_braces=re.compile(r'\[.*\]')
# nobel_prize_page='https://en.wikipedia.org/wiki/I._I._Rabi_Award'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul[1]/li[not(contains(./a/@class,"mw-redirect"))]')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     marked=None
#     text=' '.join(curr_elem.xpath(".//descendant::text()"))
#     if not re.findall('(\d{4})',text):continue
#     if 'not award' in text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span)][1]")
#     year=re.findall('(\d{4})',' '.join(curr_elem.xpath(".//descendant::text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if year:
#         if a_elem:
#             for each_a_elem in a_elem:
#                 winner_href=each_a_elem.xpath('./@href')
#                 winner_title=each_a_elem.xpath('./text()')
#                 if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:          
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                     continue
#                 if winner_title and 'http' in winner_title[0]:
                    
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents('Ulrich L. Rohde')).strip(":"),winner_href[0],purpose])       
#                     continue
#                 if winner_href and winner_title:
#                     marked=True
#                     text=text.replace(winner_title[0],'')
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       
#         name=re.sub(year,"",text)
#         name=re.sub(paranthesis,'',name)
#         name=re.sub(r'\,.*','',name).replace("–",'').replace("-","")
#         if 'http' in name:continue
#         name=name.replace('and',":").strip(" ")
#         person_names=name.split(":")
#         person_names=[x for x in person_names if x!='']
#         if person_names!=[]:
#             for each_name in person_names:
#                     list_of_nobel_prize_winners.append([int(year),re.sub(square_braces,'',re.sub(paranthesis,'',each_name)).strip("\n").strip(":"),"Page does not exist",purpose])


# square_braces=re.compile(r'\[.*\]')
# nobel_prize_page='https://en.wikipedia.org/wiki/Aryabhata_Award'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/div[1]/ul/li[not(contains(./a/@class,"mw-redirect"))]')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     marked=None
#     text=' '.join(curr_elem.xpath(".//descendant::text()"))
#     if not re.findall('(\d{4})',text):continue
#     if 'not award' in text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span)][1]")
#     year=re.findall('(\d{4})',' '.join(curr_elem.xpath(".//descendant::text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if year:
#         if a_elem:
#             for each_a_elem in a_elem:
#                 winner_href=each_a_elem.xpath('./@href')
#                 winner_title=each_a_elem.xpath('./text()')
#                 if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:          
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                     continue
#                 if winner_title and 'http' in winner_title[0]:
                    
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents('Ulrich L. Rohde')).strip(":"),winner_href[0],purpose])       
#                     continue
#                 if winner_href and winner_title:
#                     marked=True
#                     text=text.replace(winner_title[0],'')
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       
#         name=re.sub(year,"",text)
#         name=re.sub(paranthesis,'',name)
#         each_name=re.sub(r'\,.*','',name).replace("–",'').replace("-","")
#         list_of_nobel_prize_winners.append([int(year),re.sub(square_braces,'',re.sub(paranthesis,'',each_name)).strip("\n").strip(":"),"Page does not exist",purpose])


# square_braces=re.compile(r'\[.*\]')
# nobel_prize_page='https://en.wikipedia.org/wiki/Stern–Gerlach_Medal'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/ul[1]/li[not(contains(./a/@class,"mw-redirect"))] | //*[@id="mw-content-text"]/div/div/ul/li[not(contains(./a/@class,"mw-redirect"))]')
# winner_href=None
# winner_title=None
# year=None
# purpose=None
# country=None
# for curr_elem in tr_elements:
#     marked=None
#     text=' '.join(curr_elem.xpath(".//descendant::text()"))
#     if not re.findall('(\d{4})',text):continue
#     if 'not award' in text:
#         continue
#     a_elem=curr_elem.xpath(".//a[not(parent::sup) and not(parent::span)]")
#     year=re.findall('(\d{4})',' '.join(curr_elem.xpath(".//descendant::text()")))[0].strip(":").strip(" ").strip(":").strip("-")
#     if year:
#         if a_elem:
#             for each_a_elem in a_elem:
#                 winner_href=each_a_elem.xpath('./@href')
#                 winner_title=each_a_elem.xpath('./text()')
#                 if each_a_elem.xpath('./@title') and 'page does not exist' in each_a_elem.xpath('./@title')[0]:          
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),"Page does not exist",purpose]) 
#                     continue
#                 if winner_title and 'http' in winner_title[0]:
                    
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents('Ulrich L. Rohde')).strip(":"),winner_href[0],purpose])       
#                     continue
#                 if winner_href and winner_title:
#                     marked=True
#                     text=text.replace(winner_title[0],'')
#                     list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])).strip(":"),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose])       


#retrieve nobel prize lauarates from main WIKI page
# nobel_prize_page='https://en.wikipedia.org/wiki/List_of_Nobel_laureates_in_Physics'
# page = requests.get(nobel_prize_page)
# doc = lh.fromstring(page.content)
# list_of_nobel_prize_winners=[]
# tr_elements=doc.xpath('//*[@id="mw-content-text"]/div/table[1]/tbody/tr')
# prev=None
# prev_purpose=None
# #print(tr_elements)
# for each_tr_element in tr_elements:
#     winner_href=None
#     winner_title=None
#     year=None
#     purpose=None
#     #print(each_tr_element)
#     td_elements=each_tr_element.xpath('.//td')
#     th_elements=each_tr_element.xpath('.//th')
#     if td_elements:
#         if len(td_elements)+ len(th_elements)<=2:
#             continue
#         last_td=td_elements[len(td_elements)-1]
#         if td_elements[0].xpath('boolean(.//a[contains(@class,"image")])') is False and td_elements[0].xpath('boolean(.//a)') is False:
#             #print(len(td_elements))
#             year=td_elements[0].text
#             year=year.strip("\n")
#             # for shared prices in a year
#             if year == '' or year == '–':
#                 year=prev
#             prev=year
#             if last_td.xpath('boolean(.//sup[contains(@class,"reference")])') is True:
#                 updated_list=td_elements[:-1]
#                 if len(updated_list)>2:
#                     purpose=(updated_list[-1].text_content()).replace('"','').replace("\n","")
#                     prev_purpose=purpose
#                 else:
#                     purpose=prev_purpose
#             else:
#                 purpose=prev_purpose          
#         else:
#             year=prev
#            # print("year",year)
#             if last_td.xpath('boolean(.//sup[contains(@class,"reference")])') is True:
#                 updated_list=td_elements[:-1]
#                 if len(updated_list)>2:
#                     purpose=(updated_list[-1].text_content()).replace('"','').replace("\n","")
#                     prev_purpose=purpose
#                 else:
#                     purpose=prev_purpose
#             else:
#                 purpose=prev_purpose
    
#    # print(th_elements)
#     if th_elements:
#         winner_href=th_elements[0].xpath('./a/@href')
#         winner_title=th_elements[0].xpath('./a/@title')
#         if winner_href and winner_title:
#             list_of_nobel_prize_winners.append([int(year),re.sub(paranthesis,'',strip_accents(winner_title[0])),parse_web.urlCanonicalization(winner_href[0], base_url=nobel_prize_page),purpose.replace("[",'').replace("]",'')])
                                    

            
                    
#to retrieve all information relevant information available in the winner page in WIKI
# def update_winner_information(prize_type,prize_winners_dataframe,path_to_store_crawled_info,institutions_dict,prizes_dict):
#     winner_wiki_information={}
#     doc_num=0
#     count=0
#     visited_seed=set()
#     visited_personalities=[]
#     for index,row in prize_winners_dataframe.iterrows():
#         if row.Name=='Emil Theodor Kocher':continue
#         count=count+1
#         if count%50==0:
#             print("50 done")
#         url=row['Cannonicalized_Url']
#         if row.Cannonicalized_Url=='Page does not exist':
#             personality_url=row.Name+'Page does not exist'
#             winner_wiki_information.update({personality_url:{'personality':row.Name.title(),'preferred_name':row.Name,"awards":None,'all_names':[row.Name],"born":None,"nationality":None,'birth_place':None,"institution_names":None,"institution_hrefs":None,'articles':None,'students':None,'advisors':None,'co_authors':None,'gender_significance':None,'pronoun_count_male':None,'pronoun_count_female':None }})
#             continue
#         if not parse_web.ispolite(url):
#             continue
#         if  url in visited_seed:
#             continue
#         visited_seed.add(url)
#         page = requests.get(url)
#         doc_num=doc_num+1
#         raw_html=page.content
#         #doc = lh.fromstring(page.content)
#         path=path_to_store_crawled_info+'/'+str(prize_type.split(" ")[0])+'-document-{0}'
#         personality_url,institutions_dict,personality_dict=parse_web.get_wiki_information(prize_type,doc_num,raw_html,institutions_dict,row.to_dict(),prizes_dict)
# #         if personality_name in visited_personalities:      
# #             winner_wiki_information.update({personality_name+'_'+str(visited_personalities.count(personality_name)):personality_dict})
# #         else:
#         winner_wiki_information.update({personality_url:personality_dict})
#         #visited_personalities.append(personality_name)
#     return winner_wiki_information,institutions_dict,prizes_dict
#to retrieve all information relevant information available in the winner page in WIKI

# country_info=set()


#creating dataframe with winners,year they were awarded and url of the winner page
nobel_prize_winners=pd.DataFrame(list_of_nobel_prize_winners,columns=['Year','Name','Cannonicalized_Url','Purpose'])
with open('/home/apoorva_kasoju2712/wos_samplecode/prizes_directory_wiki.pickle', 'rb') as handle:
    prizes_dict=pickle.load(handle)
with open('/home/apoorva_kasoju2712/wos_samplecode/institutions_wiki.pickle', 'rb') as handle:
    institutions_dict = pickle.load(handle)
with open('/home/apoorva_kasoju2712/wos_samplecode/visited_set.pickle', 'rb') as handle:
    visited_set = pickle.load(handle)
with open('/home/apoorva_kasoju2712/wos_samplecode/country_info.pickle', 'rb') as handle:
    country_info = pickle.load(handle)

def update_winner_information(prize_type,prize_winners_dataframe,path_to_store_crawled_info,institutions_dict,prizes_dict,country_info,visited_set):
    winner_wiki_information={}
    doc_num=0
    count=0
    visited_personalities=[]
    for index,row in prize_winners_dataframe.iterrows():
        if row.Name=='Emil Theodor Kocher':continue
        count=count+1
        if count%50==0:
            print("50 done")
        url=row['Cannonicalized_Url']
        if row.Cannonicalized_Url=='Page does not exist':
            personality_url=row.Name+'Page does not exist'
            winner_wiki_information.update({personality_url:{'personality':row.Name.title(),'preferred_name':row.Name,"awards":None,'all_names':[row.Name],"born":None,"nationality":None,'birth_place':None,"institution_names":None,"institution_hrefs":None,'article_titles':None,'students':None,'advisors':None,'co_authors':None,'gender_significance':None,'pronoun_count_male':None,'pronoun_count_female':None }})
            continue
        if not parse_web.ispolite(url):
            continue
#         if  url in visited_set:
#             continue
#         visited_set.add(url)
        page = requests.get(url)
        doc_num=doc_num+1
        raw_html=page.content
        #path=path_to_store_crawled_info+'/'+str(prize_type.split(" ")[0])+'-document-{0}'
        country_info,personality_url,institutions_dict,prizes_dict,personality_dict=parse_web.get_wiki_information(prize_type,doc_num,raw_html,institutions_dict,row.to_dict(),prizes_dict,country_info)
        winner_wiki_information.update({personality_url:personality_dict})
    return winner_wiki_information,institutions_dict,prizes_dict,country_info,visited_set

winner_wiki_information,institutions_dict,prizes_dict,country_info,visited_set=update_winner_information(strip_accents('Nobel Prize in Chemistry'),nobel_prize_winners,'/home/apoorva_kasoju2712/nobel_crawled_data',institutions_dict,prizes_dict,country_info,visited_set)






with open('/home/apoorva_kasoju2712/wos_samplecode/nobel_chemistry_win.pickle', 'wb') as handle:
    pickle.dump(winner_wiki_information, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open('/home/apoorva_kasoju2712/wos_samplecode/institutions_wiki.pickle', 'wb') as handle:
    pickle.dump(institutions_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open('/home/apoorva_kasoju2712/wos_samplecode/prizes_directory_wiki.pickle', 'wb') as handle:
    pickle.dump(prizes_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open('/home/apoorva_kasoju2712/wos_samplecode/visited_set.pickle', 'wb') as handle:
    pickle.dump(visited_set, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open('/home/apoorva_kasoju2712/wos_samplecode/country_info.pickle', 'wb') as handle:
    pickle.dump(country_info, handle, protocol=pickle.HIGHEST_PROTOCOL)