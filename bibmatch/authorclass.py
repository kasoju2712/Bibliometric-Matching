
import bibmatch.clean_data as clean_data


class author(object):

    def __init__(self, authorobj = None):
        self.prefered_name = ''
        self.all_names = set([])
        self.coauthor_list = []
        self.article_titles = []
        self.institutions = set([])
        self.authorID = None
        self.other_info = {}


        self.full_last_names = None
        self.full_middle_names = None
        self.full_first_names = None
        self.last_initials  = None
        self.first_initials = None
        self.middle_initials = None

        self.processed_article_titles = None
        self.processed_institutions = None

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
        nameset = list(map(clean_data.clean_name, map(str.lower, nameset)))
        for name in nameset:
            if len(name.middle) == 0:
                if len(name.first) == 2:
                    name.middle = name.first[1]
                elif len(name.first) == 3:
                    name.middle = name.first[1] + ' ' + name.first[2]

        firstnames = set([name.first for name in nameset if len(name.first) > 0] + [name.first[0] for name in nameset if len(name.first) > 0])
        middlenames = set([mname for name in nameset for mname in name.middle.split(' ') if len(mname) > 0])
        # for last names, take the human last name and the last name by spacing
        lastnames = set([name.last for name in nameset if len(name.last) > 0] + [name.last.split(' ')[-1] for name in nameset if ' ' in name.last])
        return firstnames, middlenames, lastnames

    def from_dict(self, author_dict):
        self.prefered_name = self._unknown_key(author_dict, 'prefered_name', '')
        self.all_names = self._unknown_key(author_dict, 'all_names', set([]))
        self.coauthor_list = self._unknown_key(author_dict, 'co_authors', [])
        self.article_titles = self._unknown_key(author_dict, 'article_titles', [])
        self.institutions = self._unknown_key(author_dict, 'institutions', set([]))

    def from_string(self, author_string):
        self.prefered_name = author_string
        self.all_names = [author_string]

    def set_id(self, aid):
        self.authorID = aid

    def update_coauthors(self, coauthor_list):
        self.coauthor_list = coauthor_list

    def process_names(self):
        firstnames, middlenames, lastnames = self._process_nameset(self.all_names)

        self.full_last_names = set([n for n in lastnames if len(n) > 1])
        self.full_first_names = set([n for n in firstnames if len(n) > 1])
        self.full_middle_names = set([n for n in middlenames if len(n) > 1])
        self.last_initials = set([n[0] for n in lastnames if len(n) >= 1])
        self.first_initials = set([n for n in firstnames if len(n) == 1])
        self.middle_initials = set([n for n in middlenames if len(n) == 1])

    def process_metadata(self):
        # process all of the information associated with an author entry
        self.process_names()

        # clean these objects in preparation for fuzzy matching
        self.processed_article_titles = clean_data.sort_process_strings(self.article_titles)
        self.processed_institutions = clean_data.sort_process_strings(self.institutions)

        # process the co-author list
        new_coauthor_list = []
        for a in self.coauthor_list:
            if isinstance(a, author):
                new_coauthor_list.append(a.process_author())
            elif isinstance(a, str) or isinstance(a, dict):
                new_coauthor_list.append(author(a).process_names())
        self.coauthor_list = new_coauthor_list

        return self

    def author2dict(self):
        authordict = copy.deepcopy(self.__dict__)
        if 'coauthor_list' in authordict.keys():
            authordict['coauthor_list'] = [a.prefered_name for p in authordict['coauthor_list']]
        return authordict

    def print_author(self, list_articles=False):
        print(self.prefered_name)
        print("All Names: ", self.all_names)
        print('Institutions:' , self.institutions)
        print('Co-authors:' , [a.prefered_name if isinstance(a,author) else a for a in self.coauthor_list])
        if list_articles:
            print("Articles")
            for title in self.article_titles:
                print(title)


