#!/usr/bin/env python
# coding: utf-8
import os
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
    a.process_names()
    return a

def parse_wos_authors(full_df, groupby_col='AuthorDAIS'):
    alist = [adf2author(aid, adf) for aid, adf in full_df.groupby(groupby_col)]
    return alist

def load_wos_data(name = 'article', year_list = None, columns = None,
          duplicate_subset = ['ArticleID'], path2rawdata = '',
          dropna = None, isindict = None, verbose = False):

  if year_list is None:
    year_list = [1900] + list(range(1945, 2017))
  year_list = map(str, year_list)

  file_df_list = []
  ifile = 0
  for year in year_list:
    for df_file in os.listdir(os.path.join(path2rawdata, name)):
      if "WR_" + year in df_file:

        fname = os.path.join(path2rawdata, name, df_file)
        subdf = pd.read_hdf(fname, mode = 'r')

        if type(columns) is list:
          subdf = subdf[columns]

        if type(dropna) is list:
          subdf.dropna(subset = dropna, inplace = True, how = 'any')

        if type(isindict) is dict:
          for isinkey, isinlist in isindict.items():
            subdf = subdf[isin_sorted(subdf[isinkey], isinlist)]

        # date tag to keep most recent entry
        filetag = df_file.split('_')[2]
        subdf['filetag'] = filetag

        file_df_list.append(subdf)
        ifile += 1
        if verbose and ifile % verbose == 0:
          print(ifile)

  df = pd.concat(file_df_list)

  # take most recent entries according to filetag
  df.sort_values(by = 'filetag', inplace = True)
  df.drop_duplicates(subset = duplicate_subset, keep = 'last', inplace = True)
  del df['filetag']

  if verbose:
    print("Final DF Shape", df.shape)

  return df

def isin_sorted(values2check, masterlist):
  index = np.searchsorted(masterlist, values2check, side = 'left')
  index[index >= masterlist.shape[0]] = masterlist.shape[0] - 1
  return values2check == masterlist[index]