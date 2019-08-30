import re
import json
import string
import requests
import time
import nltk
import spacy 
import langid
import pycountry
nlp = spacy.load('en_core_web_sm')
import lxml.html as lh
import urllib.robotparser
from xml.etree import ElementTree
from  bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse,unquote
from langdetect import detect 
from nameparser import HumanName
import dateutil.parser as date_parser
from datetime import datetime
from sklearn.feature_extraction.text import CountVectorizer
from bibmatch.clean_data import strip_accents,clean_name,clean_articles,clean_unicode_characters,detect_lang_and_retrieve,is_date




from lxml.html import HtmlElement
#method  for matching text in xpath using regex and binding it to HtmlElement Class
def re_xpath(self, path):
    return self.xpath(path, namespaces={
        're': 'http://exslt.org/regular-expressions'})
HtmlElement.re_xpath = re_xpath




def check_valid_date(date_string):
    '''Check if the string is valid date and return date in words if so'''
    try:
        dte = date_parser.parse(date_string);
    except  ValueError:
        return None
    try:
        datet=datetime.strftime(datetime.strptime(date_string, '%Y-%m-%d'),'%b %d, %Y')
        return datet
    except ValueError:
        datet=datetime.strftime(datetime.strptime(date_string, '%Y'),'%Y')
        return datet

def filter_none(s):
    if s:
        return list(filter(lambda p:p if p and is_not_blank(p) else None,s))
    else:
        return [] 
def unknown_key(d, k, default_response = ''):
        try:
            return d[k]
        except KeyError:
            return default_response
def is_not_blank(x):
    return bool(x and x.strip())
def is_valid_name(s):
    if is_not_blank(s):
        r = re.compile("^[a-zA-Z\s\'\.\-]*$")
        if r.match:
            return True
    return False
def in_list(extra_list,person_name):
    if any(each_word in person_name for each_word in extra_list)==True:
        return True
    return False


#to checkness politenss policy and canonicalization of url
def ispolite(absolute_url):
    #print("at ispolite")
    scheme, netloc_host, path, params, query, fragment = urlparse(absolute_url)
    url = scheme + "://" + netloc_host
    robotUrl = url + "/robots.txt"
    try:
        if robotUrl not in robot_dict:
   # print("r",robotUrl)
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robotUrl)
            rp.read()
            robot_dict[robotUrl] = rp
        r=robot_dict[robotUrl]
        return r.can_fetch("*", absolute_url)
    except Exception:
        return True
def normalize_slashes(url):
    url=str(url)
    segments=url.split('/')
    correct_segments=list()
    for each_seg in segments:
        if each_seg!='':
            correct_segments.append(each_seg)
    first_seg=str(correct_segments[0])
    if(first_seg.find('http')==-1):
        correct_segments=['http:']+correct_segments
    correct_segments[0]=correct_segments[0]+'/'
    normalized_url='/'.join(correct_segments)
    return normalized_url

def urlCanonicalization(url, base_url=None):
    #url = url.lower()
    if not url.startswith("http"):
        url = urljoin(base_url, url)
    if url.startswith("http") and url.endswith(":80"):
        url = url[:-3]
    if url.startswith("https") and url.endswith(":443"):
        url = url[:-4]
    url=normalize_slashes(url)
    url = url.rsplit('#', 1)[0]
    url=url.rsplit('?', 1)[0]
    return url




#get alma_institution/affliations from winner wiki page
def parse_institutions(institution_page):
    time.sleep(1)
    insitution_name=None
    page = requests.get(institution_page)
    raw_html = page.content
    doc = lh.fromstring(page.content)
    first_heading=doc.xpath('//*[@id="firstHeading"]')
    if first_heading:
        institute_name=first_heading[0].text_content()
        if institute_name!=None:
            institute_name=re.sub(' +', ' ', re.sub(' at |,',' ', strip_accents(institute_name)).strip()).strip()
            return (institute_name)
    return None



stop_words=[each_x.lower() for each_x in ['Biographical Memoirs','Biography','Centennial','Obituary','Birth Centennial','Nobel Foundation','lectures on','PhRvL','physrev','PhRv','RevModPhys']]
author_last_regex=re.compile('(?<=aulast\=)[\w%+\d\.]+(?=\&)')
author_au_regex=re.compile('(?<=au\=)[\w%+\d\.]+(?=\&)')
title_regex=re.compile('(?<=title\=)(?<!jtitle\=)[\w%+\d\.\-]+(?=\&)')
def detect_regex_and_process(article_elements):
   # print(article_elements)
    all_articles=set()
    for each_elem in article_elements:
        if re.search(title_regex,each_elem):
            title=clean_unicode_characters(re.findall(title_regex,each_elem)[0])
            if 'span' in title and 'style' in title:
                    title=re.sub('span(.*)(span(?!.*span))',' ',title)
        all_articles.add(title)
    return all_articles
  


gender_pronoun_vocabulary=['he','his','himself','her','hers','herself','she']
def cleanMe(page_text):
    """retrieve cleaned text from html page"""
    soup = BeautifulSoup(page_text,"lxml") # create a new bs4 object from the html data loaded
    for script in soup(["script", "style"]): # remove all javascript and stylesheet code
        script.extract()
    # get text
    text = soup.get_text()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = ' '.join(chunk for chunk in chunks if chunk)
    return text.lower()
def process_gender_significance(page_text):
    """count pronoun occurences in html page"""
    doc1=cleanMe(page_text)
    doc_set=[doc1]
    gender_significance,male_pronouns,female_pronouns=None,None,None
    vectorizer = CountVectorizer( vocabulary=gender_pronoun_vocabulary)
    tf = vectorizer.fit_transform(doc_set) 
    tf_array=tf.toarray().sum(axis=0)
    male_pronouns=sum(tf_array[:3])
    female_pronouns=sum(tf_array[3:])  
    gender_significance='M' if male_pronouns > female_pronouns else 'F'
    return (gender_significance,male_pronouns,female_pronouns)



def parse_articles(list_of_names,doc,personality_page=True):
    """parse article title from different sections of author's wiki page"""
    extra_words=stop_words
    all_articles=set()
    if personality_page:
        #patents
        patent_elements=doc.xpath('(//span[contains(@id,"patents")]/parent::*)/following-sibling::ul[1]|(//span[contains(@id,"patents") ]/parent::*)/following-sibling::*/ul')
        if patent_elements:
            for each_elem in patent_elements:
                if each_elem.xpath('.//li/i'):
                    all_articles.update(set(each_elem.xpath('.//li/i/text()'))) 
        #publications
        p_elements=doc.xpath('(//*[@id="Publications" or @id="Selected_bibliography" or  @id="Popular_articles" or @id="Bibliography" ]/parent::*)/following-sibling::ul[1]|(//*[@id="Selected_bibliography" or @id="Publications" or   @id="Popular_articles" or @id="Bibliography"]/parent::*)/following-sibling::*/ul')
        if p_elements:
            for each_elem in p_elements:
                if not each_elem.xpath('.//a[@rel="nofollow"]/@href'):
                    all_articles.update(set([clean_unicode_characters(x) for x in each_elem.xpath('.//li/i/text()')]))
                    all_articles.update(set([clean_unicode_characters(re.findall(r'"([^"]*)"', each_text.strip("\n"))[0] if re.search(r'"([^"]*)"', each_text.strip("\n")) else '') for each_text in each_elem.xpath('.//li[not(i)]/text()')  or [] ])) 
                else:
                    all_articles.update(set([clean_unicode_characters(each_y.strip('"')) for each_y in each_elem.xpath('.//a[@rel="nofollow"]/text()')]))
    journal_elements=doc.xpath('//*[@class="citation journal" or @class="citation" or @class="citation thesis"]/following-sibling::span[1]/@title')
    if not journal_elements:return all_articles
    else:
        all_articles.update(detect_regex_and_process(journal_elements)) 
    reference_text=doc.xpath('.//*[contains(@class,"reference-text")]/text()')
    if reference_text:
        reference_articles=set()
        for each_text in reference_text:
            reference_articles.update(re.findall(r'"([^"]*)"', each_text.strip("\n")))
        reference_articles= [each_article.strip(":").strip(" ") for each_article in reference_articles]
        all_articles.update(reference_articles)
    new_articles=[clean_articles(each_article) for each_article in all_articles if not in_list(extra_words,each_article.lower())] 
    new_articles = list(filter(lambda p:p if p not in list_of_names else None, filter_none(new_articles)))
    return new_articles


def parse_co_authors_from_articles(doc):
    """parse authors from publications,notes and bibliograpghy of wiki page"""
    regexp = re.compile('[\w]{2,}[,]\s[\w]{1}\.\s[\w]{1}\.|[\w]{2,}[,]\s[\w]{1}\.[\w]{1}\.|[\w]{2,}[,]\s[\w]{1}\.')
    regexp_2=re.compile('[\w]{1}\.\s[\w]{1}\.\s[\w]{2,}|[\w]{1}\.\s[\w]{2,}')
    author_name_regex=re.compile('[\w]{2,}[,]\s[\w]{1}\.\s[\w]{1}\.|[\w]{2,}[,]\s[\w]{1}\.[\w]{1}\.|[\w]{2,}[,]\s[\w]{1}\.|[\w]{1}\.\s[\w]{1}\.\s[\w]{2,}|[\w]{1}\.[\w]{1}\.\s[\w]{2,}|[\w]{1}\.\s[\w]{2,}')
    co_authors,s,l=[],[],[]
    title_elements=doc.xpath('(//span[contains(@id,"Publications") or contains(@id,"Selected_publications") or contains(@id,"Further_reading") or contains(@id,"Books") or contains(@id,"Articles")]/parent::*)/following-sibling::ul[1]|(//span[contains(@id,"Publications") or contains(@id,"Selected_publications") or contains(@id,"Further_reading") or contains(@id,"Books") or contains(@id,"Articles")]/parent::*)/following-sibling::*/ul')
    if title_elements:
        for each_elem in title_elements:
            m=each_elem.xpath('.//li/text()[1]')
            m=[re.sub('et al\.$', '', re.sub("[\(\[].*?[\)\]]", "", x).strip()) for x in m]
            for each_m in m:
                    s.extend(re.split('(?<=\s)[,](?=\s)|and|&', each_m))
            s=[x.strip() for x in s]
            for each_str in s:
                if not ',' in each_str:
                    l.append(each_str)
                elif regexp_2.search(each_str):
                    l.extend(re.split('(?<=\w)[,](?=\s)', each_str))
                elif regexp.search(each_str):
                    l.extend(re.split('(?<!\w)[,](?=\s)', each_str))
    if l:
        l=list(set(l))
        for each_elem in l:
            if re.search(author_name_regex,each_elem):
                 co_authors.append(re.findall(author_name_regex,each_elem)[0])
    co_authors=set([strip_accents(each_co_author) for each_co_author in co_authors if not re.search('[\d\\\\]', each_co_author)  ])
    new_co_authors=[]
    for each_coauthor in set(co_authors):
        if regexp_2.search(each_coauthor):
            name=HumanName(each_coauthor)
            new_co_authors.append((name.last+', '+name.first+' '+name.middle).strip(" "))
        else:
            new_co_authors.append(each_coauthor) 
    return(set(new_co_authors))




def get_from_spacy(sentence,person_name):
    """retrieve person label from a sentence"""
    doc = nlp(sentence) 
    for ent in [ent for ent in doc.ents if ent.label_=='PERSON' and  person_name in ent.text]: 
        return (ent.text).split(" ")
    return []





remove_words=['college','research','reproduced','advanced']
def get_human_names(text,base_url,doc,personality_last_names,doctoral_co_authors):
    """retrieve human names from text"""
    extra_words=personality_last_names+remove_words
    all_coauthors_list,text_co_authors,person_list = set(),set(),set()
    person_names=person_list
    sent = nltk.sent_tokenize(text)
    for each_sent in sent:
        if any(x in each_sent for x in  ['staff','worked','colleagues','colloborated','working','developed','developing','assistant','colleague',"their contributions"]):
            tokens = nltk.tokenize.word_tokenize(each_sent.strip())
            pos = nltk.pos_tag(tokens)
            sentt = nltk.ne_chunk(pos, binary = False)
            person,name = [],""
            for subtree in sentt.subtrees(filter=lambda t: t.label() == 'PERSON'):
                for leaf in subtree.leaves():
                    person.append(leaf[0])
                if len(person)==1:# to address cases where just first names is labelled as PERSON
                    person=get_from_spacy(each_sent,person[0])
                if len(person) > 1: #avoid grabbing lone surnames
                    for part in person:
                        name += part + ' '
                    if name[:-1] not in person_list:
                        person_list.add(name[:-1])
                    name = ''
                person=[]
    if person_list:
        person_list=[each_coauthor for each_coauthor in person_list if not in_list(extra_words,each_coauthor.lower())]
        person_list=[each_person for each_person in person_list if is_valid_name(each_person)]
        if doctoral_co_authors:
            text_co_authors=set([each_co_author for each_co_author in person_list if  any(True for x in doctoral_co_authors if x!=each_co_author and not each_co_author in x )==True])
        #retrieve all possible names of co-author by scraping his web page if exists
        for each_person in person_list:
            next_elem=doc.re_xpath('//a[re:match(@title,"%s")][1]/@href'%each_person)
            if next_elem:                   
                cannonicalised_url=urlCanonicalization(next_elem[0],base_url)
                if not ispolite(cannonicalised_url):
                    continue
                else:
                    time.sleep(1)
                    page = requests.get(cannonicalised_url)
                    raw_html = page.content
                    doc1 = lh.fromstring(page.content)
                    all_coauthors_list.update(extract_all_names(doc1,each_person))      
    return all_coauthors_list,text_co_authors





def extract_all_names(doc,personality_name):
    """retrieve names of the personality from their wiki page-heading,infobox"""
    name_set=set()
    tr_elements = doc.xpath('//div[@class="mw-parser-output"]/table[@class="infobox biography vcard"]/tbody/tr')
    if tr_elements:
        for each_id in tr_elements[0].iterchildren(): 
            if each_id.tag=='th':
                parts = ([each_id.text] + list(chain(*([c.text, c.tail] for c in each_id.getchildren()))) + [each_id.tail])
                personality_name=''.join(filter(None, parts))
        if personality_name and langid.classify(personality_name)[0]!='zh':
            name_set.add(strip_accents(personality_name))
    full_name_tag=doc.xpath('//*[@class="mw-parser-output"]/p[not(@class ="mw-empty-elt")][1]/b')
    if full_name_tag and full_name_tag[0].text is not None:
        name_set.add(strip_accents(full_name_tag[0].text.split(',', 1)[0])) 
    first_heading_tag=doc.xpath('//*[@id="firstHeading"]')
    if first_heading_tag and first_heading_tag[0].text is not None:
        name_set.add(strip_accents(first_heading_tag[0].text.split(',', 1)[0])) 
    cleaned_names = list(map(lambda p: clean_name(p,False),name_set))
    cleaned_names=filter_none(cleaned_names)
    return set([name.title() for name in cleaned_names])



def parse_infobox(doc,base_url,institutions_dict,prizes_dict,prize_type,country_info):
    """parse information from infobox section"""
    advisor_co_authors,student_co_authors,prizes=[],[],[]
    nationality_info,birth_date,birth_place=None,None,None
    institution_names,institution_hrefs=set(),set()
    #doctoral advisors
    advisor_co_author_elements=doc.xpath('//th[contains(descendant::text(),"advisor")]/following-sibling::td[1]')
    if advisor_co_author_elements:
        for each_elem in advisor_co_author_elements:
            advisor_co_authors.extend([strip_accents(re.sub("[\(\[].*?[\)\]]", "", x)) for x in each_elem.xpath(".//a/@title|.//text()")])
        advisor_co_authors=set([each_l for each_l in advisor_co_authors if any( not(("A" <= char and char <= "Z") or ("a" <= char and char <= "z") or (char == " ") or (char == "'") or (char == "-") or (char=='.')) for char in each_l) is False  and each_l!=''])
    #doctoral students
    student_co_author_elements=doc.xpath('//th[contains(descendant::text(),"student")]/following-sibling::td[1]')
    if student_co_author_elements:
        for each_elem in student_co_author_elements:
            student_co_authors.extend([strip_accents(re.sub("[\(\[].*?[\)\]]", "", x)) for x in each_elem.xpath(".//a/@title|.//text()")])
        student_co_authors=set([each_l for each_l in student_co_authors if any( not(("A" <= char and char <= "Z") or ("a" <= char and char <= "z") or (char == "-") or (char == " ") or (char == "'") or (char=='.')) for char in each_l) is False  and each_l!=''])
    #nationality
    nationality_element=doc.xpath('//th[contains(text(),"Nationality")]/following-sibling::td[1]')
    if nationality_element:
        nationality_info=re.split(' and |,|\n',nationality_element[0].xpath(".//text()")[0])
    birth_place_element=doc.xpath('//th[contains(text(),"Born")]/following-sibling::td[1]') 
    #birth place
    if birth_place_element:
        birth_place_text=[country for country in countries if country in  ' '.join(birth_place_element[0].xpath('.//text()')) ]
        if birth_place_text:
            birth_place=birth_place_text[0]
        else:
            country_info.add(' '.join(birth_place_element[0].xpath('.//text()')))
    #birthday
    birth_element=doc.xpath('.//span[contains(@class,"bday")]')
    if birth_element:
        birth_date=check_valid_date(birth_element[0].xpath('.//text()')[0].strip(" "))
   #institutions
    institution_element=doc.xpath('//th[text()="Institutions" or contains(text(),"Alma")]/following-sibling::td[1]/a')
    if institution_element:
        for a_elem in institution_element:
            institution_href=a_elem.xpath("./@href")[0]
            institution_title=a_elem.xpath(".//@title")[0] or a_elem.xpath("./text()")[0]
            if institution_title:
                    institution_title=re.sub(' +', ' ', re.sub(',','',strip_accents(institution_title)))
                    institution_names.add(institution_title)
            if institution_href and institution_title:
                institution_page=urlCanonicalization(institution_href,base_url)
                institution_hrefs.add(institution_page)
                if not ispolite(institution_page):continue
                if institution_page not in institutions_dict:
                    institutions_dict.update({institution_page:{institution_title}})
                else:
                    institutions_dict[institution_page].update({institution_title})
                m=parse_institutions(institution_page)
                if m:
                    institutions_dict[institution_page].update({m})
    #awards
    awards=doc.xpath('//th[contains(text(),"Awards")]/parent::tr')
    if awards:
        href_awards=awards[0].xpath(".//a[not(parent::sup)]")
        for each_award in href_awards:
            prize_name=prize_year=purpose=None
            p=each_award.text_content()+" "+str(each_award.tail if each_award.tail is not None else '')
            prize_name=re.sub(paranthesis, '', p).strip(" ").strip("\n")
            if prize_name==prize_type:
                continue
            if prize_name in ['National Academy of Sciences','American Physical Society','Royal Society']:
                prize_name='Fellow of  '+prize_name
            if re.search(paranthesis_text,p):
                prize_year=re.search(paranthesis_text,p).group(0)
            else:
                text_elem_index=int(each_award.re_xpath('count(./following-sibling::text()[re:match(.,"\(\d+\)")][1])'))
                br_elem_index=int(each_award.xpath('count(./following-sibling::br)'))
                if text_elem_index < br_elem_index:
                    next_elem=each_award.re_xpath('./following-sibling::text()[re:match(.,"\(\d+\)")][1]')
                    if next_elem:
                        prize_year=(re.search(paranthesis_text,next_elem[0]).group(0)) 
            if not prize_year:
                next_elem=each_award.re_xpath('./preceding-sibling::br[1]')
                if next_elem:
                    prize_year=str(next_elem[0].tail if next_elem[0].tail is not None else '')
            if not prize_year and each_award.re_xpath('./preceding-sibling::*[position()<2 and position()>0 and re:match(local-name(), "br")]')==[]:
                if not prize_year:
                    next_elem=each_award.re_xpath('./preceding-sibling::*[re:match(text(),"\d+")][1]')
                    if next_elem:
                        prize_year=(next_elem[0].xpath('./text()')[0])
                if not prize_year:
                        next_elem=each_award.re_xpath('preceding-sibling::text()[re:match(.,"\d+")][1]')
                        if next_elem:
                            prize_year=strip_accents(next_elem[0])
            if not prize_year:
                next_elem=each_award.re_xpath('./following-sibling::*/text()[re:match(.,"\(\d+\)")][1]')
                if next_elem:
                    prize_year=(re.search(paranthesis_text,next_elem[0]).group(0))
            prize_href=each_award.xpath('./@href')[0]
            if not prize_href in prizes_dict:
                prizes_dict.update({urlCanonicalization(prize_href,base_url):prize_name}) 
            if is_not_blank(prize_year):
                prize_year=prize_year.strip()
                prize_years=list(filter(None,list(filter(str.isdigit, r.split(prize_year)))))
                if len(prize_years)>1:  
                    for each_year in prize_years:
                        prizes.append({"href":prize_href,"Year":int(each_year),"Name":prize_name,"Purpose":purpose})
                else:
                    if re.findall(r'\d{4}', prize_year):
                        prizes.append({"href":urlCanonicalization(prize_href,base_url),"Name":prize_name,"Year":int(re.findall(r'\d{4}', prize_year)[0]),"Purpose":purpose})
        non_href_awards=awards[0].xpath("./td/descendant::text()[not(parent::a)]") 
        if non_href_awards:
            non_href_awards=list(filter(lambda p:p if p!=' ' and re.findall(number_regex,p)==[] else None ,non_href_awards))
            for each_award in non_href_awards:
                prize_year=purpose=None
                if is_not_blank(prize_name):
                    prizes.append({"href":None,"Name":prize_name,"Year":prize_year,"Purpose":purpose})
    if not awards:
        awards=doc.xpath('(//*[contains(@id,"Awards") or contains(@id,"awards") or contains(@id,"Prizes") or contains(@id,"prizes") or contains(@id,"Honor") or contains(@id,"honor")]/parent::*)/following-sibling::ul[1]|(//*[contains(@id,"Awards") or contains(@id,"awards") or contains(@id,"Honor") or contains(@id,"Prizes") or contains(@id,"prizes") or contains(@id,"honor")]/parent::*)/following-sibling::*/ul')
        if awards:
            li_elements=awards[0].xpath('.//li')
            for each_li in li_elements:
                award_href=prize_name=prize_year=purpose=prize_href=None
                s=' '.join(each_li.xpath(".//descendant::text()"))
                each_award=each_li.xpath('./a')
                if each_award: 
                    award_href=each_award[0].xpath('./@href')
                index_pos = re.search('(\d{4})', s)
                if index_pos:
                    index=index_pos.start()
                    if index==0:
                        index_pos2=re.search('.*(?:\D|^)(\d+)', s)
                        if index_pos2:
                            index_pos22=index_pos2.end()
                            prize_year,prize_name=s[0:index_pos22],s[index_pos22:].strip(" ")                          
                    else: 
                        prize_year,prize_name=s[index:],s[:index].strip(" ")
                    prize_name=re.sub(r'\".*\"','',prize_name).replace(":"," ").strip(" ").replace("\\s+","")
                    #retrieving purpose
                    l=[x for x in ['for his','for her','for their'] if x in prize_name]
                    if l:
                        index_of_purpose=s.find(l[0])
                        if index_of_purpose!=-1:
                            purpose=prize_name[index_of_purpose:]
                            prize_name=re.sub(purpose,'',prize_name)                       
                    if award_href:
                        prize_href=urlCanonicalization(award_href[0],base_url)
                        if award_href[0] not in prizes_dict:
                            prizes_dict.update({prize_href:prize_name})                                        
                    if "," in prize_year:
                        prize_years=prize_year.split(",")
                        for each_year in prize_years:
                            prizes.append({"href":prize_href,"Year":each_year.strip(")").strip("("),"Name":prize_name,"Purpose":purpose})
                    else:
                            prizes.append({"href":prize_href,"Year":prize_year.strip(")").strip("("),"Name":prize_name,"Purpose":purpose})

    return (advisor_co_authors,student_co_authors,prizes,nationality_info,birth_date,birth_place,institution_hrefs,institution_names,institutions_dict,prizes_dict,country_info)


paranthesis_text=re.compile(r'\(\d+\)')
paranthesis=re.compile(r'\(.*\)')
number_regex=re.compile(r'\d+')
from string import punctuation
r = re.compile(r'[\s{}]+'.format(re.escape(punctuation)))
countries=[country.name for country in pycountry.countries] +['U.S.','U.K.','Soviet Union'] 
#method to get all relevant information(articles/publications,co-authors,institutions) for a winner from WIKI
def get_wiki_information(prize_type,doc_num,page_content,institutions_dict,row_dict,prizes_dict,country_info):
    doc = lh.fromstring(page_content)
    gender_significance,male_pronouns,female_pronouns=process_gender_significance(page_content)
    n=doc.xpath('//link[@rel="canonical"]/@href')
    base_url=n[0]
    all_articles,co_authors=set(),set()
    prizes=[]
    personality_name,prize_purpose,prize_year = unknown_key(row_dict, 'Name', ''),unknown_key(row_dict, 'Purpose', ''),unknown_key(row_dict, 'Year', '')
    #print("personality",personality_name)
    name_set.add(personality_name)
    if is_not_blank(prize_type):
        prizes.append({"Name":prize_type,"Year":prize_year,"Purpose":prize_purpose})
    cleaned_names=extract_all_names(doc,personality_name)
    preferred_name = max(cleaned_names, key=len)
    if personality_name=='':
        personality_name=preferred_name
    personality_last_names= filter_none(set([clean_name(each_name).last for each_name in cleaned_names]))
    advisor_co_authors,student_co_authors,infobox_prizes,nationality_info,birth_date,birth_place,institution_hrefs,institution_names,institutions_dict,prizes_dict,country_info=parse_infobox(doc,base_url,institutions_dict,prizes_dict,prize_type,country_info)
    prizes.extend(infobox_prizes if infobox_prizes else [] )
    # coauthors
    doctoral_co_authors=advisor_co_authors.union(student_co_authors)
    co_authors.update(doctoral_co_authors.union(parse_co_authors_from_articles(doc)))
    co_authors_from_text=set()
    cleaned_text=doc.xpath('//*[@id="mw-content-text"]/div/p[not(contains(@id,"Personal")) and not(contains(@id,"Life")) and not(contains(@id,"Death")) and not(contains(@id,"External")) and not(contains(@class,"citation")) and not(contains(@class,"Publications")) and not(contains(@class,"Bibliography")) and not(contains(@class,"reflist"))]/descendant::text()[not(parent::sup) and not(ancestor::sup)]')
    if cleaned_text:
        text=" ".join(cleaned_text).replace('\n','').replace("\\", "")
        all_co_authors_from_text,co_authors_from_text=get_human_names(text,base_url,doc,personality_last_names,doctoral_co_authors)
        co_authors.update(all_co_authors_from_text if all_co_authors_from_text else set())
    #  articles
    all_articles.update(parse_articles(cleaned_names,doc))
    #scraping Known - for infobox biography vcard
    td_elem=doc.xpath('//*[@id="mw-content-text"]//table[contains(@class,"infobox biography vcard")]/tbody/tr/th[contains(text(),"Known")]/following-sibling::td')
    if td_elem:
        known_for_hrefs=td_elem[0].xpath('.//a/@href')
        known_for_text=td_elem[0].xpath('.//a/text()')
        if known_for_text:
            all_articles.add(known_for_text[0])
        for each_href in known_for_hrefs:
            known_for_page=urlCanonicalization(each_href,base_url)
            if not ispolite(known_for_page):continue
            time.sleep(1)
            known_for_doc = lh.fromstring(requests.get(known_for_page).content)
            m=parse_articles(cleaned_names,known_for_doc,False)
            if m:
                all_articles.update(m)
    all_articles=set([unquote(title) for title in all_articles]) if all_articles else set()
    return (country_info,base_url,institutions_dict,prizes_dict,{'personality':personality_name.title(),'preferred_name':preferred_name,"awards":prizes,'all_names':cleaned_names,"born":birth_date,"nationality":nationality_info,'birth_place':birth_place,"institution_names":institution_names,"institution_hrefs":institution_hrefs,'article_titles':all_articles,'students':student_co_authors,'advisors':advisor_co_authors,'co_authors':co_authors,"text_co_authors":co_authors_from_text,'gender_significance':gender_significance,'pronoun_count_male':male_pronouns,'pronoun_count_female':female_pronouns })

