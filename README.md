Bibliometric Matching

Code to uniquely match  every famous personality(prize_winners in science,art,literature) to Web of Science Data.To do so,we  build a knowledge graph with features from information obtained through their wikipedia, which includes publications/journal articles , affiliations/institutions associated , co-authors/collaborators ,including their  specializations .

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
- Spacy
- NLTK


Modules
-----------
bibmatch 
	
	
	1) authorclass - Functions defined to and process author attributes .

	2) clean_data - Functions defined to clean data before matching 

	3) fast_match_utilities - Functions defined to match co-authors,organizations and full_names of authors from Wikipedia to Web of Science

	4) parse_wos - Functions defined to parse information from Web of Science such as articles,affiliations and co-authors

	5) load_data - Functions and utilities load appropriate dataframes from Web of Science



Execution
---------

Part 1  - Execute parse_prize,parse_prize_winner  scripts to extract winner information from various prizes and store in a proper format
 
Part 2  - Use the information to uniquely match personality in Web of Science.

Once the required data is available (WOS Data and Wikipedia Information), execute the run_match.py by providing command line arguments .

Eg: python <name-of-program> <path-to-data> <data1-without-extension> <data2-without-extension>
	python run_match.py /home/apoorva_kasoju2712/wos_samplecode/ full_df nobel_chemistry_win
	
