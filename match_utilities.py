#!/usr/bin/env python
# coding: utf-8

# In[43]:


import re
from nameparser import HumanName
import pandas as pd
import itertools
from itertools import chain,product
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import clean_data as clean_data
import enchant
d = enchant.Dict('en_US')


# In[38]:


get_ipython().run_cell_magic('bash', '', 'jupyter nbconvert match_utilities.ipynb --to script')


# In[44]:


#creating dataframe to store author information based on last name candidates for crawled authors
def get_wos_records(nobel_winner_wiki_information,author_df):
    author_new_df=None
    count=0    
    for crawled_file,v in nobel_winner_wiki_information.items():
        preferred_name=v['preferred_name']
        print(preferred_name)
        personality_name=clean_data.strip_accents(preferred_name)
        name=HumanName(personality_name)
        if (name.title):
            personality_name = personality_name.replace(name.title,'')
        personality_name=personality_name.replace(",","")
        personality_name = re.sub('Jr\.$', '', personality_name)
        personality_name=personality_name.replace("(",'"').replace(")",'"')
        personality_name=personality_name.strip("\n").strip("\t").strip(" ")
        last_word=personality_name.split(" ")[-1]
        first_name=personality_name.split(" ")[0] 
        if "-" in last_word:
            last_words=last_word.split("-")
            last_word=last_words[-1]     
        a=None
        b=None
        c=None 
        if last_word==name.last:
            b=author_df.loc[(author_df['LastName'] == name.last) | (author_df['LastName'] == name.last.upper())   ][['FullName','AuthorDAIS','AuthorOrder','ArticleID','LastName','FirstName']]  
        else:
            b=author_df.loc[(author_df['LastName'] == name.last) | (author_df['LastName'] == name.last.upper())|(author_df['LastName'] == last_word)| (author_df['LastName'] == last_word.upper())][['FullName','AuthorDAIS','AuthorOrder','ArticleID','LastName','FirstName']]  
        if b.empty:
            if not d.check(personality_name):
                b=author_df.loc[(author_df['LastName'] == first_name)][['FullName','AuthorDAIS','AuthorOrder','ArticleID','LastName','FirstName']]
        if count==0:
            author_new_df=b
        else :
            author_new_df=pd.concat([author_new_df,b])
        count=count+1
    return author_new_df


# In[45]:


def check_if_initial(firstmiddleparts,crawled_firstmidlleparts):
    first_name=firstmiddleparts[0]
#     print(first_name)
    if len(first_name)==1:
        return False  
    if len(crawled_firstmidlleparts)==len(first_name):
        for i in range(0,len(first_name)):
            if not crawled_firstmidlleparts[i][0]==first_name[i]:
                break
        else:
            return True
        return False
    else:
        return False  


# In[46]:


def vector_for_match_names(set_of_wos_names,set_of_wiki_names):
    vector=[]
    set_wiki_first_middle=[]
    for personality_name in set_of_wiki_names:
        personality_name=personality_name.lower()
        crawled_full_name_splits=personality_name.split(" ")
        if len(crawled_full_name_splits)==1:
            set_wiki_first_middle.append(crawled_full_name_splits)
        else:
            name=HumanName(personality_name)
            if name.last!=crawled_full_name_splits[-1]:
                l=[x for x in name[1:3] if x != '']
                set_wiki_first_middle.append(l)
                for x in l:
                    if "-" in x:
                        set_wiki_first_middle.append(x.split("-"))
                
            else:
                crawled_lastname=crawled_full_name_splits[-1]
                crawled_firstmiddleparts=crawled_full_name_splits[:-1]
                set_wiki_first_middle.append(crawled_firstmiddleparts)
                for x in crawled_firstmiddleparts:
                    if "-" in x:
                        set_wiki_first_middle.append(x.split("-"))
    set_wiki_first_middle.sort()
    set_wiki_first_middle=list(set_wiki_first_middle for set_wiki_first_middle,_ in itertools.groupby(set_wiki_first_middle))
    set_wiki_first_middle= [x for x in set_wiki_first_middle if x != []]
    set_wos_first_middle=[]
    for retrieved_name in set_of_wos_names:
        retrieved_name=re.sub(r'(?<=\w)[\.](?=\w)', r' ',str(re.sub(r'(?<=\.)\-', r' ',str(re.sub(r'(\.)$', r'', str(re.sub(r'(\.)[\s\-]+', r' ', retrieved_name)))))))
        retrieved_name=retrieved_name.rstrip(" ")
        retrieved_name=retrieved_name.lstrip(" ")
        retrieved_name=retrieved_name.lower()
        retrieved_lastname,firstandmiddlename=retrieved_name.split(",")[0].strip(" "),retrieved_name.split(",")[1].strip(" ")
        firstmiddleparts=firstandmiddlename.split(" ")
        if '' in firstmiddleparts:
            firstmiddleparts.remove('')
        if len(firstmiddleparts)==1:
            for crawled_firstmiddleparts in set_wiki_first_middle:
                if check_if_initial(firstmiddleparts,crawled_firstmiddleparts)==True:
                    set_wos_first_middle.append(list(firstmiddleparts[0]))
                    break
            else:
                set_wos_first_middle.append(firstmiddleparts)
        else:
            set_wos_first_middle.append(firstmiddleparts)
    set_wos_first_middle.sort()
    set_wos_first_middle=list(set_wos_first_middle for set_wos_first_middle,_ in itertools.groupby(set_wos_first_middle))
    set_wos_first_middle = [x for x in set_wos_first_middle if x != []]
   # print("wos",set_wos_first_middle)
   # char 1 -> If First_name(WOS)==First_name(Wikipedia)
    vector.append(0 if len(set([each_first_middle[0] for each_first_middle in set_wiki_first_middle]).intersection(set([each_first_middle[0] for each_first_middle in set_wos_first_middle])))==0 else 1)
   #char 2 -> If First_name(WOS)==Middle_name(Wikipedia) or Middle_name(WOS)==First_name(Wikipedia)
    vector.append(0 if len(set([each_first_middle[1] for each_first_middle in set_wiki_first_middle if len(each_first_middle)>1]).intersection(set([each_first_middle[0] for each_first_middle in set_wos_first_middle])))==0 else 1                or 0 if len(set([each_first_middle[1] for each_first_middle in set_wos_first_middle if len(each_first_middle)>1]).intersection(set([each_first_middle[0] for each_first_middle in set_wiki_first_middle])))==0 else 1 )
   #char 3 -> If Middle_name(WOS)==Middle_name(Wikipedia)
    vector.append(0 if len(set([each_first_middle[1] for each_first_middle in set_wiki_first_middle if len(each_first_middle)>1]).intersection(set([each_first_middle[1] for each_first_middle in set_wos_first_middle if len(each_first_middle)>1])))==0 else 1)
   #char 4-> 1 and 3 
    vector.append(vector[0] and vector[2])
    #char 5 -> If 1st char of First_name(WOS)==1st char of First_name(Wikipedia)
    vector.append(0 if len(set([each_first_middle[0][0] for each_first_middle in set_wiki_first_middle]).intersection(set([each_first_middle[0][0] for each_first_middle in set_wos_first_middle])))==0 else 1)
    #char 6 -> If 1st char of First_name(WOS)==1st char of Middle_name(Wikipedia) or if 1st char of Middle_name(WOS)==1st char of First_name(Wiki)
    vector.append(0 if len(set([each_first_middle[1][0] for each_first_middle in set_wiki_first_middle if len(each_first_middle)>1]).intersection(set([each_first_middle[0][0] for each_first_middle in set_wos_first_middle])))==0 else 1                or 0 if len(set([each_first_middle[1][0] for each_first_middle in set_wos_first_middle if len(each_first_middle)>1]).intersection(set([each_first_middle[0][0] for each_first_middle in set_wiki_first_middle])))==0 else 1 )
    #--exclusions
    #char 7 -> Not (First_name(WOS)==First_name(Wikipedia) or First_name(WOS)==Middle_name(Wikipedia)) 
    vector.append(1 if any(True for x in set([each_first_middle[0] for each_first_middle in set_wos_first_middle if len(each_first_middle[0])>1]) if x  not in list(set([each_first_middle[0] for each_first_middle in set_wiki_first_middle if len(each_first_middle[0])>1])))==True else 0 )
    return ''.join(map(str,vector))


# In[50]:


def match_co_authors(list_of_articleID,list_of_last_names,co_authors,title_co_authors,article_co_author):
    if not co_authors and not title_co_authors:
        return 0
    num_of_matches=set()
    list_of_wos_last_and_full=[]
    list_of_wos_last_names=[]
    personality_last_names=list_of_last_names
    personality_last_names=list(set(list_of_last_names))
    personality_last_names=[each_name.lower() for each_name in personality_last_names]
    list_of_wos_full_names=[]
    if co_authors:
        list_of_wiki_coauthors=list(co_authors)
        if 'citation needed' in list_of_wiki_coauthors:
            list_of_wiki_coauthors.remove('citation needed')
        list_of_wiki_last_names=[HumanName(name).last for name in list_of_wiki_coauthors]
        list_of_wiki_last_and_full=list(zip(list_of_wiki_last_names,list_of_wiki_coauthors))
        list_of_wiki_last_and_full=[(each_name[0].lower(),each_name[1].lower()) for each_name in list_of_wiki_last_and_full]
        list_of_wiki_last_names= [each_name.lower() for each_name in list_of_wiki_last_names]
        if len(list_of_wiki_last_names)>0:
            articleID_list=list_of_articleID
            list_of_wos_last_and_full=[]
            for index, row in (article_co_author.query("ArticleID in @articleID_list")[['LastName','FullName']]).iterrows():
                list_of_wos_last_and_full.extend(list(zip(row['LastName'], row['FullName'])))  
                #print("row",row['FullName'])
                list_of_wos_full_names.extend(row['FullName'])
            list_of_wos_last_and_full=[(each_name[0].lower(),each_name[1].lower()) for each_name in list_of_wos_last_and_full if not each_name[0].lower() in personality_last_names ]
            list_of_wos_last_and_full=list(set(list_of_wos_last_and_full))
        #print("list of wos last and full",list_of_wos_last_and_full)
            list_of_wos_last_names=[each[0] for each in list_of_wos_last_and_full]
            if  len(list_of_wos_last_names)>0:  
                for x in itertools.product(list_of_wos_last_names,list_of_wiki_last_names) :
                    if fuzz.token_sort_ratio(*x) >=90:
                  #  print("x is ",x)
                        wos_set=set()
                   # print("value at wos",list_of_wos_last_and_full[(list_of_wos_last_names.index(x[0]))][1])
                        wos_set.add(list_of_wos_last_and_full[(list_of_wos_last_names.index(x[0]))][1])
                        wiki_set=set()
                  #  print("value at wiki",list_of_wiki_last_and_full[(list_of_wiki_last_names.index(x[1]))][1])
                        wiki_set.add(list_of_wiki_last_and_full[(list_of_wiki_last_names.index(x[1]))][1])
                        score_vector=vector_for_match_names(wos_set,wiki_set) 
                        if sum(map(int,list(score_vector[:-1])) )-int(score_vector[-1]) >=1:
                          #  print("here",list_of_wos_last_and_full[(list_of_wos_last_names.index(x[0]))][1])
                            num_of_matches.add(list_of_wos_last_and_full[(list_of_wos_last_names.index(x[0]))][1])  
            
    if title_co_authors:
        title_co_authors=[re.sub(r'(?<=\w)[\.](?=\w)', r' ',str(re.sub(r'(?<=\.)\-', r' ',str(re.sub(r'(\.)$', r'', str(re.sub(r'(\.)[\s\-]+', r'', retrieved_name))))))) for retrieved_name in title_co_authors]
        k=[HumanName(name).last for name in list(title_co_authors) ]
        list_of_title_coauthor_names=[name.lower()  for name in list(title_co_authors) if (HumanName(name).last).lower() not in  personality_last_names]
        list_of_title_coauthor_last_names=[HumanName(name).last for name in list_of_title_coauthor_names]
        list_of_title_coauthor_last_and_full=list(zip(list_of_title_coauthor_last_names,list_of_title_coauthor_names))
        articleID_list=list_of_articleID
        if not list_of_wos_full_names:
            list_of_wos_full_names=list(chain.from_iterable((article_co_author.query("ArticleID in @articleID_list")['FullName']).tolist()))
        list_of_wos_full_names=[each_name.lower() for each_name in list_of_wos_full_names if (HumanName(each_name).last).lower() not in personality_last_names]
        list_of_wos_full_names=list(set(list_of_wos_full_names))
        if  len(list_of_wos_full_names)>0:  
            for x in itertools.product(list_of_wos_full_names,list_of_title_coauthor_names) :
                if fuzz.token_sort_ratio(*x) >=97:
                   # print(x[0],x[1],fuzz.token_sort_ratio(*x))
                    num_of_matches.add(x[0])
    return len(num_of_matches)    
def match_articles(list_of_wos_articles,list_of_wiki_articles):
    list_of_wos_articles=list(filter(lambda x:str(x)!='nan' ,list_of_wos_articles))
    list_of_wos_articles = [each_article.lower() for each_article in list_of_wos_articles]
    list_of_wiki_articles = [each_article.lower() for each_article in list_of_wiki_articles]
    list_of_wiki_articles =[each_article.strip('nobel lecture') for each_article in list_of_wiki_articles]
    if len(list_of_wos_articles)>0 and len(list_of_wiki_articles)>0:
        return len(set([x[0] for x in itertools.product(list_of_wos_articles,list_of_wiki_articles) if fuzz.token_sort_ratio(*x) >=75]))
    else:
        return 0
def match_organizations(list_of_wos_institutions,list_of_wiki_institutions):
    list_of_wos_institutions=list(filter(lambda x:str(x)!='nan' ,list_of_wos_institutions))
    if len(list_of_wos_institutions)>0:
        return len(set([x[0] for x in itertools.product(list_of_wos_institutions,list_of_wiki_institutions) if fuzz.token_sort_ratio(*x) > 85]))
    else:
        return 0



# In[51]:


def find_best_match(author_wiki_information,author_address_article_new,article_co_author):
    match_title_dict={}
    missed_match_co_authors_set=set()
    match_co_author_dict={}
    high_score_dict={}
    tie_match_dict={}
    no_match_dict={}
    for k , v in author_wiki_information.items():
        x=k
        name,all_names,list_of_wiki_institutions,list_of_wiki_titles,list_of_wiki_coauthors,list_of_title_coauthors=author_wiki_information[x]['preferred_name'],author_wiki_information[x]['all_names'],author_wiki_information[x]['institutions'],author_wiki_information[x]['articles'],author_wiki_information[x]['co_authors'],author_wiki_information[x]['article_co_authors']
        co_authors=list_of_wiki_coauthors
        s=None
        first_name=None
        middle_name=None
        last_name=None
        personality_name=name
        print(personality_name)
        m=author_address_article_new
        last_name=personality_name.split(" ")[-1]
        first_name=personality_name.split(" ")[0] 
        if len(personality_name.split(" "))>2:
            middle_name=personality_name.split(" ")[1] 
        name=HumanName(personality_name)
        if last_name==name.last:
            s=m.groupby('LastName').filter(lambda x: any(x['LastName'] == last_name) | any(x['LastName'] == last_name.upper()))
        else:
            s=m.groupby('LastName').filter(lambda x:any(x['LastName'] == last_name) |any(x['LastName'] == last_name.upper()) | any(x['LastName'] == name.last.upper())| any(x['LastName'] == name.last))
        if s.empty:
            if not d.check(personality_name):
                s=m.groupby('LastName').filter(lambda x: any(x['LastName'] == first_name)| any(x['LastName'] == first_name.upper()))
        s.dropna(subset=['AuthorDAIS'],inplace=True)
        grouped_df = s.groupby('AuthorDAIS').agg({'FullName':lambda x: list(x.unique()),'LastName':lambda x: list(x.unique()),'ArticleID':lambda x: list(x.unique()),'Organization':lambda x: list(x.unique()),'Title':lambda x: list(x.unique())})
        grouped_df['article_num'] =s.groupby('AuthorDAIS')['ArticleID'].nunique().values
        grouped_df['vector']=grouped_df['FullName'].apply(lambda x : vector_for_match_names(x,set(all_names)))
        grouped_df['score']=grouped_df['vector'].apply(lambda x :sum(map(int,list(x[:-1])) )-int(x[-1]))
        grouped_df = grouped_df.drop(grouped_df[grouped_df.score < 0].index)
        grouped_df = grouped_df.reset_index()
        if not grouped_df.empty:
            grouped_df['match_co_author']=grouped_df.apply(lambda x: match_co_authors(x['ArticleID'], x['LastName'],co_authors,list_of_title_coauthors,article_co_author), axis=1)
            grouped_df['match_org']=grouped_df['Organization'].apply(lambda x:match_organizations(x,list_of_wiki_institutions) )
            grouped_df['match_title']=grouped_df['Title'].apply(lambda x:match_articles(x,list_of_wiki_titles) )
            grouped_df.drop(columns=['ArticleID'],inplace=True)
            grouped_df.sort_values(by=['score','match_title','match_co_author','article_num'],ascending=False,inplace=True)
            grouped_df['total_score']=grouped_df['score']+grouped_df['match_org']
            new_grouped_df = grouped_df[(grouped_df['match_title'] > 0)]
            if not new_grouped_df.empty:
                match_title_dict.update({k:[new_grouped_df.iloc[0].AuthorDAIS,author_wiki_information[k]['preferred_name']]})
                if len(new_grouped_df[(new_grouped_df['match_co_author']>0)])>0:
                    missed_match_co_authors_set.add(k)
            elif len(grouped_df[grouped_df['match_co_author']>0])>0:
                max_grouped_df=grouped_df[grouped_df['match_co_author']==grouped_df['match_co_author'].max()]
                match_co_author_dict.update({k:[max_grouped_df.iloc[0].AuthorDAIS,author_wiki_information[k]['preferred_name']]})
            else:   
                score_grouped_df=grouped_df[grouped_df['total_score']==grouped_df['total_score'].max()]
                if len(score_grouped_df)==1:
                    high_score_dict.update({k:[score_grouped_df.iloc[0].AuthorDAIS,author_wiki_information[k]['preferred_name']]})
                else:   
                    tie_match_dict.update({k:[score_grouped_df.iloc[0].AuthorDAIS,author_wiki_information[k]['preferred_name']]})
        else:
            no_match_dict.update({k:[None,author_wiki_information[k]['preferred_name']]})
    return match_title_dict,high_score_dict,match_co_author_dict,no_match_dict,tie_match_dict


# In[ ]:





# In[ ]:




