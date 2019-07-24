

import pandas as pd
import sys
import pyarrow as pa
import pyarrow.parquet as pq
import pickle 
from nameparser import HumanName
from bibmatch.authorclass import author
from bibmatch.fast_match_utilities import author_matching_vector,combine_match_result
from bibmatch.clean_data import clean_name,agg_stringlist_with_delim

path=str(sys.argv[1])

#loading data
full_df = pq.read_table(path+'{}.parquet'.format(str(sys.argv[2]))).to_pandas()

#loading wikipedia information
with open(path+'{}.pickle'.format(str(sys.argv[3])), 'rb') as handle:
    winner_wiki_information = pickle.load(handle)

print("Required Data Loaded")

def get_wos_records(winner_wiki_information,full_df):
    author_new_df=None
    count=0
    for crawled_file,v in winner_wiki_information.items():
        preferred_name=v['preferred_name']
        wiki_a=author(v)
        wiki_a=wiki_a.process_names()
        b=full_df[(full_df.Lower.isin(wiki_a.full_last_names))][['FullName','AuthorDAIS','AuthorOrder','ArticleID','LastName','Organization','Title','CoAuthors','Lower']]  
        if not b.empty:
            b.dropna(subset=['AuthorDAIS'],inplace=True)
            if count==0:
                author_new_df=b
            else :
                author_new_df=pd.concat([author_new_df,b])          
        count=count+1
    return author_new_df

full_df['Lower']=full_df['LastName'].astype(str).str.lower()
winner_df=get_wos_records(winner_wiki_information,full_df)


print("Subset selection done")


def get_author (l):
    """returns the author object for a Author ID"""
    author_dict={}
    author_dict['all_names'] = set(l)
    a = author(author_dict)
    a.process_names()
    return a

def process_match(organization,title,articleid,fullnames,wiki_a,co_authors):
    """to process and combine match results of all attributes"""
    author_dict={}
    author_dict['institutions'] = set(list(filter(None, organization)))
    author_dict['article_titles'] = set(list(filter(None, title)))
    author_dict['co_authors']=co_authors
    wos_a = author(author_dict)
    wos_a =  wos_a.process_metadata()
    s=combine_match_result(wos_a, wiki_a)
    return s


#find best match based on criteria for all the authors
def find_best_match(winner_df,winner_wiki_information):
    missed_match_co_authors_set=set()
    count=0
    for k,v in winner_wiki_information.items():
        count=count+1
        v=winner_wiki_information[k]
        personality_last_names= [clean_name(each_name).last for each_name in v['all_names']]
        co_authors= [each_coauthor for each_coauthor in v['co_authors'] if clean_name(each_coauthor).last not in personality_last_names]
        v['co_authors']=co_authors
        wikipedia_a = author(v)
        if count%50==0:
            print("50 done")
        wikipedia_a =  wikipedia_a.process_metadata()
        list_of_wiki_institutions,list_of_wiki_titles,list_of_wiki_coauthors=wikipedia_a.institutions,wikipedia_a.article_titles,wikipedia_a.coauthor_list
        b=winner_df[(winner_df.Lower.isin(wikipedia_a.full_last_names))]  
        b.dropna(subset=['AuthorDAIS'],inplace=True)
        grouped_df = b.groupby('AuthorDAIS').agg({'FullName':lambda x: list(x.unique()),'LastName':lambda x: list(x.unique()),'ArticleID':lambda x: list(x.unique()),'Organization':lambda x: list(x.unique()),'Title':lambda x: list(x.unique()),'CoAuthors':agg_stringlist_with_delim})
        grouped_df['score']=grouped_df['FullName'].apply(lambda x: author_matching_vector(wikipedia_a,get_author (list(set(x)))))
        grouped_df = grouped_df.drop(grouped_df[grouped_df.score < 0].index)
        grouped_df = grouped_df.reset_index()
        if not grouped_df.empty:
            applied_df = grouped_df.apply(lambda x:process_match(x.Organization,x.Title,x.ArticleID,x.FullName,wikipedia_a,x.CoAuthors),axis=1,result_type='expand')
            grouped_df = pd.concat([grouped_df, applied_df], axis='columns')
            grouped_df.rename(columns={0: 'coauthors_match', 1:'org_match',2:'title_match'}, inplace=True)
            grouped_df.sort_values(by=['score','title_match','coauthors_match'],ascending=False,inplace=True)
            grouped_df['total_score']=grouped_df['score']+grouped_df['org_match']
            title_grouped_df = grouped_df[(grouped_df['title_match'] > 0)]
            if not title_grouped_df.empty:
                winner_wiki_information[k].update({"wos_author_id":title_grouped_df.iloc[0].AuthorDAIS})
                if len(title_grouped_df[(title_grouped_df['coauthors_match']>0)])>0:
                        missed_match_co_authors_set.add(k)
            elif len(grouped_df[grouped_df['coauthors_match']>0])>0:
                coauthor_grouped_df=grouped_df[grouped_df['coauthors_match']==grouped_df['coauthors_match'].max()]
                winner_wiki_information[k].update({"wos_author_id":coauthor_grouped_df.iloc[0].AuthorDAIS})
            else:   
                score_grouped_df=grouped_df[grouped_df['total_score']==grouped_df['total_score'].max()]
                if len(score_grouped_df)>=1:
                    winner_wiki_information[k].update({"wos_author_id":score_grouped_df.iloc[0].AuthorDAIS})
        else:
            winner_wiki_information[k].update({"wos_author_id":None})

    return winner_wiki_information

winner_wiki_information=find_best_match(winner_df,winner_wiki_information)

with open(path+'{}_updated.pickle'.format(str(sys.argv[3])), 'wb') as handle:
    pickle.dump(winner_wiki_information, handle, protocol=pickle.HIGHEST_PROTOCOL)

print("Matching Completed")



