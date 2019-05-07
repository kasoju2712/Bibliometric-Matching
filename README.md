Biblipometric Matching

Code for matching Nobel Prize in Physics winner information from Wikipedia to Web of Science Data.To uniquely identify a personality , we build a knowledge graph with features from information obtained through their wikipedia, which includes publications/journal articles , affiliations/institutions associated , co-authors/collaborators and also information from specializations of the personality.

A decision vector is built for matching names of co-authors and authors themselves , including penalization for mismatch.
For matching organizations , articles string matching algorithms like fuzz match score has been used.
 

Success
Code author
-----------
Apoorva Kasoju

Installation
------------

- Python 3.6
- Numpy
- Enchant


Modules
-----------
1) clean_data -> Functions defined to clean data before matching 

2) match_utilities -> Consists of functions to match co-authors,organizations and full_names of authors from Wikipedia to Web of Science

3) parse_web -> Functions defined to parse information from Wikipedia such as articles,affiliations and co-authors

4) load_data -> Functions and utilities load appropriate dataframes from Web of Science

Execution
---------
1) Execute Nobel_prize_crawl with required modules imported.

 -> First part of the execution deals with crawling laureate's wiki page and extracting relevant information
 
 -> Second part of the execution deals with with using the crawled information to uniquely identify laureate in Web of Science.
