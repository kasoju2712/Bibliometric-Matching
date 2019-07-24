

from bibmatch.clean_data import clean_name,sort_process_strings


class author(object):

    def __init__(self, authorobj = None):
        self.preferred_name = ''
        self.all_names = set([])
        self.coauthor_list = []
        self.article_titles = []
        self.institutions = set([])
        self.authorID = None
        self.other_info = None
        self.full_last_names = set([])
        self.full_middle_names = set([])
        self.full_first_names = set([])
        self.first_initials = set([])
        self.middle_initials = set([])

        if isinstance(authorobj, dict):
            self.from_dict(authorobj)
        elif isinstance(authorobj, str):
            self.from_string(authorobj)

    def _unknown_key(self, d, k, default_response = ''):
        try:
            return d[k]
        except KeyError:
            return default_response

    def _process_nameset(self, nameset):
        nameset = list(map(clean_name,nameset))
        firstnames = set([name.first for name in nameset if len(name.first) > 0] + [name.first[0] for name in nameset if len(name.first) > 0])
        middlenames=set([name.middle for name in nameset if len(name.middle) > 0])
        # for last names, take the human last name and the last name by spacing
        lastnames = set([name.last for name in nameset if len(name.last) > 0] + [(name.last.split(' '))[-1] for name in nameset if ' ' in name.last])
        return firstnames, middlenames, lastnames

    def from_dict(self, author_dict):
        self.preferred_name = self._unknown_key(author_dict, 'preferred_name', '')
        self.all_names = self._unknown_key(author_dict, 'all_names', set([]))
        self.coauthor_list = self._unknown_key(author_dict, 'co_authors', [])
        self.article_titles = self._unknown_key(author_dict, 'article_titles', [])
        self.institutions = self._unknown_key(author_dict, 'institutions', set([]))

    def from_string(self, author_string):
        self.preferred_name = author_string
        self.all_names = [author_string]

    def set_id(self, aid):
        self.authorID = aid
        
    def update_articles(self, article_titles):
        self.article_titles = sort_process_strings(article_titles)
        
    def update_institutions(self, institutions):
        self.institutions = sort_process_strings(institutions)
        
    def update_coauthor_list(self, coauthor_list):
        new_coauthor_list = []
        for a in coauthor_list:
            if isinstance(a, author):
                new_coauthor_list.append(a.process_names())
            elif isinstance(a, str) or isinstance(a, dict):
                new_coauthor_list.append(author(a).process_names())
        self.coauthor_list = new_coauthor_list

    def process_names(self):
        # process all of the information associated with an author entry
        firstnames, middlenames, lastnames = self._process_nameset(self.all_names)
        if lastnames:
            self.full_last_names = set([n for n in lastnames if len(n) > 1])
        if firstnames:
            self.full_first_names = set([n for n in firstnames if len(n) > 1])
        if middlenames:
            self.full_middle_names = set([n for n in middlenames if len(n) > 1])
        if firstnames:
            self.first_initials = set([n for n in firstnames if len(n) >= 1])
        if middlenames:
            self.middle_initials = set([n for n in middlenames if len(n) >= 1] + [n[0] for n in middlenames if len(n) >= 1])
        return self
        
    def process_metadata(self):
        # process all of the information associated with an author entry
        self=self.process_names()

        # clean these objects in preparation for fuzzy matching
        self.article_titles = sort_process_strings(self.article_titles)
        self.institutions = sort_process_strings(self.institutions)

        # process the co-author list
        new_coauthor_list = []
        for a in self.coauthor_list:
            if isinstance(a, author):
                new_coauthor_list.append(a.process_names())
            elif isinstance(a, str) or isinstance(a, dict):
                new_coauthor_list.append(author(a).process_names())
        self.coauthor_list = new_coauthor_list

        return self








