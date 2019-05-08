#!/usr/bin/env python
# coding: utf-8
import numpy as np
import pandas as pd
from bibmatch.authorclass import author

def adf2author(aid, adf):
    author_dict = {}
    author_dict['all_names'] = set(adf['FullName'])
    author_dict['prefered_name'] = sorted(author_dict['all_names'], key = len)[-1]
    author_dict['articles'] = set([t for t in adf['Title'].dropna()])
    author_dict['co_authors'] = set([name.strip() for namelist in adf['CoAuthors'].dropna() for name in namelist.split('|') if len(name.strip()) > 0])
    author_dict['institutions'] = set([t for t in adf['Organization'].dropna()])
    a = author(author_dict)
    a.set_id(aid)
    a.process_author()
    return a

def parse_wos_authors(full_df, groupby_col='AuthorDAIS'):
    alist = [adf2author(aid, adf) for aid, adf in full_df.groupby(groupby_col)]
    return alist

