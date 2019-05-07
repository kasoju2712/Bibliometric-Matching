
from bibmatch.fast_string_compare import sort_process_strings
import bibmatch.clean_data as clean_data


class author(object):

    def __init__(self, authorobj = None):
        self.prefered_name = ''
        self.all_names = set([])
        self.coauthor_list = []
        self.article_titles = []
        self.institutions = set([])
        self.authorID = None

        self.full_last_names = None
        self.full_middle_names = None
        self.full_first_names = None
        self.first_initials = None
        self.middle_initials = None

        if isinstance(authorobj, dict):
            self.from_dict(authorobj)
        elif isinstance(authorobj, str):
            self.from_string(authorobj)

    def _uknown_key(d, k, default_response = ''):
        try:
            return d[k]
        except KeyError:
            return default_response

    def _process_nameset(nameset):
        nameset = list(map(clean_data.clean_name, map(str.lower, nameset)))
        for name in nameset:
            if len(name.first) == 2 and len(name.middle) == 0:
                name.middle = name.first[1]
        firstnames = set([name.first for name in nameset if len(name.first) > 0] + [name.first[0] for name in nameset if len(name.first) > 0])
        middlenames = set([mname for name in nameset for mname in name.middle.split(' ') if len(mname) > 0])
        # for last names, take the human last name and the last name by spacing
        lastnames = set([name.last for name in nameset if len(name.last) > 0] + [name.last.split(' ')[-1] for name in nameset if name.last.contains(' ')])
        return firstnames, middlenames, lastnames

    def from_dict(self, author_dict):
        self.prefered_name = _uknown_key(author_dict, 'prefered_name', '')
        self.all_names = _uknown_key(author_dict, 'all_names', set([]))
        self.coauthor_list = _uknown_key(author_dict, 'co_authors', [])
        self.article_titles = _uknown_key(author_dict, 'article_titles', [])
        self.institutions = _uknown_key(author_dict, 'institutions', set([]))

    def from_string(self, author_string):
        self.prefered_name = author_string
        self.all_names = [author_string]

    def update_coauthors(self, coauthor_list):
        self.coauthor_list = coauthor_list

    def process_author(self):
        # process all of the information associated with an author entry
        firstnames, middlenames, lastnames = _process_nameset(nameset)

        self.full_last_names = set([n for n in lastnames if len(n) > 1])
        self.full_first_names = set([n for n in firstnames if len(n) > 1])
        self.full_middle_names = set([n for n in middlenames if len(n) > 1])
        self.first_initials = set([n for n in firstnames if len(n) == 1])
        self.middle_initials = set([n for n in middlenames if len(n) == 1])

        # clean these objects in preparation for fuzzy matching
        self.article_titles = sort_process_strings(self.article_titles)
        self.institutions = sort_process_strings(self.institutions)

        # process the co-author list
        new_coauthor_list = []
        for a in self.co_authors:
            if isinstance(a, author):
                new_coauthor_list.append(a.process_author())
            elif isinstance(a, str) or isinstance(a, dict):
                new_coauthor_list.append(author(a).process_author())
        self.co_authors = new_coauthor_list

        return self


