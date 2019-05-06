#!/usr/bin/env python
# coding: utf-8




import pandas as pd
import numpy as np
from collections import Counter
import itertools
import WOSutilities as wosutil
path2rawdata='/home/apoorva_kasoju2712/WOS_data'





def load_author_data():
    #['ArticleID', 'AuthorOrder', 'AuthorDAIS', 'FullName', 'LastName', 'FirstName', 'Email']
    author_df_1 = wosutil.load_wos_data(name = 'authorship',path2rawdata = path2rawdata,year_list = [1900] + list(range(1945, 1955)),columns=['ArticleID','AuthorOrder','AuthorDAIS','FullName','LastName','FirstName'],
                       duplicate_subset = None,dropna = ['ArticleID','FullName', 'LastName','FirstName'],     verbose = 50)
    author_df_2 = wosutil.load_wos_data(name = 'authorship',path2rawdata = path2rawdata,year_list =  list(range(1955, 1965)),columns=['ArticleID','AuthorOrder','AuthorDAIS','FullName','LastName','FirstName'],
                            duplicate_subset = None,dropna = ['ArticleID','FullName', 'LastName','FirstName'],    verbose = 50)
    author_df_3 = wosutil.load_wos_data(name = 'authorship',path2rawdata = path2rawdata,year_list =  list(range(1965, 1975)),columns=['ArticleID','AuthorOrder','AuthorDAIS','FullName','LastName','FirstName'],
                          duplicate_subset = None, dropna = ['ArticleID','FullName', 'LastName','FirstName'],     verbose = 50)
    author_df_4 = wosutil.load_wos_data(name = 'authorship',path2rawdata = path2rawdata,year_list =  list(range(1975, 1990)),columns=['ArticleID','AuthorOrder','AuthorDAIS','FullName','LastName','FirstName'],
                          duplicate_subset = None, dropna = ['ArticleID','FullName', 'LastName','FirstName'],     verbose = 50)
    author_df_5 = wosutil.load_wos_data(name = 'authorship',path2rawdata = path2rawdata,year_list =  list(range(1990, 2005)),columns=['ArticleID','AuthorOrder','AuthorDAIS','FullName','LastName','FirstName'],
                           duplicate_subset = None,dropna = ['ArticleID','FullName', 'LastName','FirstName'],     verbose = 50)
    author_df_6 = wosutil.load_wos_data(name = 'authorship',path2rawdata = path2rawdata,year_list =  list(range(2005, 2016)),columns=['ArticleID','AuthorOrder','AuthorDAIS','FullName','LastName','FirstName'],
                          duplicate_subset = None,dropna = ['ArticleID','FullName', 'LastName','FirstName'],     verbose = 50)
    author_df_12=pd.concat([author_df_1, author_df_2], ignore_index=True)
    del author_df_1
    del author_df_2
    author_df_34=pd.concat([author_df_3, author_df_4], ignore_index=True)
    del author_df_3
    del author_df_4
    author_df_56=pd.concat([author_df_5, author_df_6], ignore_index=True)
    del author_df_5
    del author_df_6
    author_df=pd.concat([author_df_12,author_df_34,author_df_56],ignore_index=True)
    del author_df_12
    del author_df_34
    del author_df_56
    print(author_df.shape)
    return author_df





def load_article_data():
    article_df_1 = wosutil.load_wos_data(name = 'article', path2rawdata = path2rawdata,
                                   year_list = [1900] + list(range(1945, 1955)), 
                          columns = ['ArticleID','Title', 'PubYear','Doctypes'], 
                          dropna = ['ArticleID', 'PubYear'], 
                           duplicate_subset = ['ArticleID'],
                          isindict = {'Doctypes':np.sort(['Article','Letter','Review','Note'])}, 
                        verbose = 50)
    del article_df_1['Doctypes']
    #print("Completed in %f" % (time.time() - st))

    article_df_2 = wosutil.load_wos_data(name = 'article', path2rawdata = path2rawdata,
                                   year_list = list(range(1955, 1965)), 
                          columns = ['ArticleID','Title','PubYear','Doctypes'], 
                          dropna = ['ArticleID', 'PubYear'], 
                           duplicate_subset = ['ArticleID'],
                          isindict = {'Doctypes':np.sort(['Article','Letter','Review','Note'])}, 
                        verbose = 50)
    del article_df_2['Doctypes']
    article_df_3 = wosutil.load_wos_data(name = 'article', path2rawdata = path2rawdata,
                                   year_list = list(range(1965, 1975)), 
                          columns = ['ArticleID', 'Title','PubYear','Doctypes'], 
                          dropna = ['ArticleID', 'PubYear'], 
                           duplicate_subset = ['ArticleID'],
                          isindict = {'Doctypes':np.sort(['Article','Letter','Review','Note'])}, 
                        verbose = 50)
    del article_df_3['Doctypes']
    article_df_4 = wosutil.load_wos_data(name = 'article', path2rawdata = path2rawdata,
                                   year_list = list(range(1975, 1990)), 
                          columns = ['ArticleID', 'Title','PubYear','Doctypes'], 
                          dropna = ['ArticleID', 'PubYear'], 
                           duplicate_subset = ['ArticleID'],
                          isindict = {'Doctypes':np.sort(['Article','Letter','Review','Note'])}, 
                        verbose = 50)
    del article_df_4['Doctypes']
    article_df_5 = wosutil.load_wos_data(name = 'article', path2rawdata = path2rawdata,
                                   year_list = list(range(1990, 2005)), 
                          columns = ['ArticleID','Title', 'PubYear','Doctypes'], 
                          dropna = ['ArticleID', 'PubYear'], 
                           duplicate_subset = ['ArticleID'],
                          isindict = {'Doctypes':np.sort(['Article','Letter','Review','Note'])}, 
                        verbose = 50)
    del article_df_5['Doctypes']
    article_df_6 = wosutil.load_wos_data(name = 'article', path2rawdata = path2rawdata,
                                   year_list = list(range(2005, 2016)), 
                          columns = ['ArticleID', 'Title','PubYear','Doctypes'], 
                          dropna = ['ArticleID', 'PubYear'], 
                           duplicate_subset = ['ArticleID'],
                          isindict = {'Doctypes':np.sort(['Article','Letter','Review','Note'])}, 
                        verbose = 50)
    del article_df_6['Doctypes']
    article_df_12=pd.concat([article_df_1, article_df_2], ignore_index=True)
    del article_df_1
    del article_df_2
    article_df_34=pd.concat([article_df_3, article_df_4], ignore_index=True)
    del article_df_3
    del article_df_4
    article_df_56=pd.concat([article_df_5, article_df_6], ignore_index=True)
    del article_df_5
    del article_df_6
    article_df=pd.concat([article_df_12,article_df_34,article_df_56],ignore_index=True)
    del article_df_12
    del article_df_34
    del article_df_56
    return article_df





def load_address_data():
    #loading address
    #[ArticleID,AuthorOrder,AddressOrder,Organization,SubOrganization]
    address_df_1 = wosutil.load_wos_data(name = 'address', path2rawdata = path2rawdata,
                                   year_list =[1900]+list(range(1945, 1955)), 
                           columns = ['ArticleID','AuthorOrder','AddressOrder','Organization','SubOrganization'], 
                           duplicate_subset = None, 
                           verbose = 50)
    address_df_2 = wosutil.load_wos_data(name = 'address', path2rawdata = path2rawdata,
                                   year_list =list(range(1955, 1965)), 
                           columns = ['ArticleID','AuthorOrder','AddressOrder','Organization','SubOrganization'], 
                           duplicate_subset = None, 
                           verbose = 50)
    address_df_3 = wosutil.load_wos_data(name = 'address', path2rawdata = path2rawdata,
                                   year_list =list(range(1965, 1975)), 
                           columns = ['ArticleID','AuthorOrder','AddressOrder','Organization','SubOrganization'], 
                           duplicate_subset = None, 
                           verbose = 50)
    address_df_4 = wosutil.load_wos_data(name = 'address', path2rawdata = path2rawdata,
                                   year_list =list(range(1975, 1990)), 
                           columns = ['ArticleID','AuthorOrder','AddressOrder','Organization','SubOrganization'], 
                           duplicate_subset = None, 
                           verbose = 50)
    address_df_5 = wosutil.load_wos_data(name = 'address', path2rawdata = path2rawdata,
                                   year_list =list(range(1990, 2005)), 
                           columns = ['ArticleID','AuthorOrder','AddressOrder','Organization','SubOrganization'], 
                           duplicate_subset = None, 
                           verbose = 50)
    address_df_6 = wosutil.load_wos_data(name = 'address', path2rawdata = path2rawdata,
                                   year_list =list(range(2005, 2016)), 
                           columns = ['ArticleID','AuthorOrder','AddressOrder','Organization','SubOrganization'], 
                           duplicate_subset = None, 
                           verbose = 50)
    address_df_12=pd.concat([address_df_1, address_df_2], ignore_index=True)
    del address_df_1
    del address_df_2
    address_df_34=pd.concat([address_df_3, address_df_4], ignore_index=True)
    del address_df_3
    del address_df_4
    address_df_56=pd.concat([address_df_5, address_df_6], ignore_index=True)
    del address_df_5
    del address_df_6
    address_df=pd.concat([address_df_12,address_df_34,address_df_56],ignore_index=True)
    del address_df_12
    del address_df_34
    del address_df_56
    return address_df





def load_paper_address_data():
    #loading paper address
    #[ArticleID,AddressOrder,Organization,SubOrganization]
    paper_address_df_1 = wosutil.load_wos_data(name = 'paper-address', path2rawdata = path2rawdata,
                                   year_list =[1900]+list(range(1945, 1955)), 
                           columns = ['ArticleID','AddressOrder','Organization','SubOrganization'], 
                           duplicate_subset = None, 
                           verbose = 50)
    paper_address_df_2 = wosutil.load_wos_data(name = 'paper-address', path2rawdata = path2rawdata,
                                   year_list =list(range(1955, 1965)), 
                           columns = ['ArticleID','AddressOrder','Organization','SubOrganization'], 
                           duplicate_subset = None, 
                           verbose = 50)
    paper_address_df_3 = wosutil.load_wos_data(name = 'paper-address', path2rawdata = path2rawdata,
                                   year_list =list(range(1965, 1975)), 
                           columns = ['ArticleID','AddressOrder','Organization','SubOrganization'], 
                           duplicate_subset = None, 
                           verbose = 50)
    paper_address_df_4 = wosutil.load_wos_data(name = 'paper-address', path2rawdata = path2rawdata,
                                   year_list =list(range(1975, 1990)), 
                           columns = ['ArticleID','AddressOrder','Organization','SubOrganization'], 
                           duplicate_subset = None, 
                           verbose = 50)
    paper_address_df_5 = wosutil.load_wos_data(name = 'paper-address', path2rawdata = path2rawdata,
                                   year_list =list(range(1990, 2005)), 
                           columns = ['ArticleID','AddressOrder','Organization','SubOrganization'], 
                           duplicate_subset = None, 
                           verbose = 50)

    paper_address_df_6 = wosutil.load_wos_data(name = 'paper-address', path2rawdata = path2rawdata,
                                   year_list =list(range(2005, 2016)), 
                           columns = ['ArticleID','AddressOrder','Organization','SubOrganization'], 
                           duplicate_subset = None, 
                           verbose = 50)
    paper_address_df_12=pd.concat([paper_address_df_1, paper_address_df_2], ignore_index=True)
    del paper_address_df_1
    del paper_address_df_2
    paper_address_df_34=pd.concat([paper_address_df_3, paper_address_df_4], ignore_index=True)
    del paper_address_df_3
    del paper_address_df_4
    paper_address_df_56=pd.concat([paper_address_df_5, paper_address_df_6], ignore_index=True)
    del paper_address_df_5
    del paper_address_df_6
    paper_address_df=pd.concat([paper_address_df_12,paper_address_df_34,paper_address_df_56],ignore_index=True)
    del paper_address_df_12
    del paper_address_df_34
    del paper_address_df_56
    return paper_address_df


