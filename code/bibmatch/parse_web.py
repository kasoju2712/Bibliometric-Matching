#!/usr/bin/env python
# coding: utf-8




from urllib.parse import urljoin, urlparse
from lxml import html
import urllib.robotparser
import string
import json
from itertools import chain
from xml.etree import ElementTree
from unidecode import  unidecode
from urllib.parse import unquote
import time
import bibmatch.clean_data as clean_data
import requests
import lxml.html as lh
import re
from xml.etree import ElementTree
from langdetect import detect 
from nameparser import HumanName
from dateutil.parser import parse
import langid





#get_ipython().run_cell_magic('bash', '', 'jupyter nbconvert parse_web.ipynb --to script')





#to checkness politenss policy and canonicalization of url
def ispolite(absolute_url):
    scheme, netloc_host, path, params, query, fragment = urlparse(absolute_url)
    url = scheme + "://" + netloc_host
    robotUrl = url + "/robots.txt"
    try:
        if robotUrl not in robot_dict:
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
        #print("here",institute_name)
        if institute_name!=None:
            institute_name=clean_data.strip_accents( institute_name)
            institute_name=re.sub(' +', ' ', re.sub('at|,','', institute_name).strip()).strip()
            return (institute_name.lower())
    return None



#get articles/publication information from known page(infobox card) of winner wiki page
def parse_known_for(known_for_page,list_of_names):
    time.sleep(1)
    author_au_regex=re.compile('(?<=au\=)[\w%+\d\.]+(?=\&)')
    author_title_regex=re.compile('(?<=atitle\=)[\w%+\d\.\-]+(?=\&)')
    book_title_regex=re.compile('(?<=btitle\=)[\w%+\d\.\-]+(?=\&)')
    page = requests.get(known_for_page)
    raw_html = page.content
    doc = lh.fromstring(page.content)
    extra_words=[each_x.lower() for each_x in ['Biographical Memoirs','Biography','Obituary','Centennial','Birth Centennial','Nobel Foundation','lectures on','PhRvL','physrev','PhRv','RevModPhys']]
    extra_words.extend(list_of_names)
    extra_words=[each_x.lower() for each_x in  extra_words]
    all_articles=set()
    journal_elements=doc.xpath('//*[@class="citation journal"]/following-sibling::span[1]/@title')
    if not journal_elements:return all_articles
    for each_elem in journal_elements:
        if re.search(author_title_regex,each_elem):
            title=clean_data.clean_unicode_characters(re.findall(author_title_regex,each_elem)[0])
            if 'span' in title  and 'style' in title:
                    title=re.sub('span(.*)(span(?!.*span))',' ',title)
            all_articles.add(title)
        else:
            if re.search(book_title_regex,each_elem):
                title=clean_data.clean_unicode_characters(re.findall(book_title_regex,each_elem)[0])
                if 'span' in title and 'style' in title:
                    title=re.sub('span(.*)(span(?!.*span))',' ',title)
                all_articles.add(title)
    all_articles=[clean_data.strip_accents(each_article) for each_article in all_articles]
    new_articles=[each_article for each_article in all_articles if not any(t in each_article.lower() for t in extra_words)] 
    #removing extra whitespaces/tabs and those articles with only spaces-numbers-hyphen-block_letters
    new_articles=[re.sub('\s+', ' ', re.sub('\([\s\d\-]+\)|\d+$', '',each_article)).strip() for each_article in new_articles] 
    new_articles=[each_article for each_article in new_articles if not re.match("^[A-Z0-9/\.\-]+$",each_article) and each_article!='']
    return new_articles





#check if string is valid date
def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False





#to detect language of titles(articles)
def detect_lang_and_retrieve(article):
    match=re.search(r'\((.*?)\)',article)
    if match and len(match.groups())==1:
        x=re.sub(r'\(.*\)', '', article)
        if x!='' and detect(x)!='en':
            if is_date(match.group(1))==False and  detect(match.group(1))=='en':
                return (match.group(1))
    return article





#to get publication/articles titles from winner wiki page
def parse_articles(list_of_names,doc):
    extra_words=[each_x.lower() for each_x in ['Biographical Memoirs','Biography','Centennial','Obituary','Birth Centennial','Nobel Foundation','lectures on','PhRvL','physrev','PhRv','RevModPhys']]
    author_last_regex=re.compile('(?<=aulast\=)[\w%+\d\.]+(?=\&)')
    author_au_regex=re.compile('(?<=au\=)[\w%+\d\.]+(?=\&)')
    author_title_regex=re.compile('(?<=atitle\=)[\w%+\d\.\-]+(?=\&)')
    book_title_regex=re.compile('(?<=btitle\=)[\w%+\d\.\-]+(?=\&)')
    list_of_names=[clean_data.strip_accents(each_name) for each_name in list_of_names]
    extra_words.extend(list_of_names)
    extra_words=[each_x.lower() for each_x in  extra_words]
    all_articles=set()
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
                all_articles.update(set(each_elem.xpath('.//li/i/text()'))) 
            else:
                all_articles.update(set([each_y.strip('"') for each_y in each_elem.xpath('.//a[@rel="nofollow"]/text()')]))
    #journals
    journal_elements=doc.xpath('//*[@class="citation journal" or @class="citation" or @class="citation thesis"]/following-sibling::span[1]/@title')
    for each_elem in journal_elements:
        if re.search(author_title_regex,each_elem):
            title=clean_data.clean_unicode_characters(re.findall(author_title_regex,each_elem)[0])
            if 'span' in title and 'style' in title:
                    title=re.sub('span(.*)(span(?!.*span))',' ',title)
            all_articles.add(title)
        else:
            if re.search(book_title_regex,each_elem):
                title=clean_data.clean_unicode_characters(re.findall(book_title_regex,each_elem)[0])
                if 'span' in title and 'style' in title:
                    title=re.sub('span(.*)(span(?!.*span))',' ',title)
                all_articles.add(title)
    new_articles=[clean_data.clean_unicode_characters(each_article) for each_article in all_articles if not any(t in each_article.lower() for t in extra_words)] 
    new_articles=[re.sub('\s+', ' ', re.sub('\([\s\d\-]+\)|\d+$', '',each_article)).strip() for each_article in new_articles] 
    new_articles=[each_article for each_article in new_articles if not re.match("^[A-Z0-9/\.\-]+$",each_article) and each_article!='']
    new_articles=[detect_lang_and_retrieve(article) for article in new_articles]
    return new_articles





#to get co-authors(doctoral advisors/students from infobox) and colloborators from author's original publications
def parse_co_authors_from_articles(doc):
    regexp = re.compile('[\w]{2,}[,]\s[\w]{1}\.\s[\w]{1}\.|[\w]{2,}[,]\s[\w]{1}\.[\w]{1}\.|[\w]{2,}[,]\s[\w]{1}\.')
    regexp_2=re.compile('[\w]{1}\.\s[\w]{1}\.\s[\w]{2,}|[\w]{1}\.\s[\w]{2,}')
    author_name_regex=re.compile('[\w]{2,}[,]\s[\w]{1}\.\s[\w]{1}\.|[\w]{2,}[,]\s[\w]{1}\.[\w]{1}\.|[\w]{2,}[,]\s[\w]{1}\.|[\w]{1}\.\s[\w]{1}\.\s[\w]{2,}|[\w]{1}\.[\w]{1}\.\s[\w]{2,}|[\w]{1}\.\s[\w]{2,}')
    co_authors=[]
    s=[]
    l=[]
    title_elements=doc.xpath('(//span[contains(@id,"Publications") or contains(@id,"Selected_publications") or contains(@id,"Further_reading") or contains(@id,"Books") or contains(@id,"Articles")]/parent::*)/following-sibling::ul[1]|(//span[contains(@id,"Publications") or contains(@id,"Selected_publications") or contains(@id,"Further_reading") or contains(@id,"Books") or contains(@id,"Articles")]/parent::*)/following-sibling::*/ul')
    if title_elements:
        for each_elem in title_elements:
            #each_elem.xpath('.//li/text()[1]')
            m=each_elem.xpath('.//li/text()[1]')
            m=[re.sub('et al\.$', '', re.sub("[\(\[].*?[\)\]]", "", x).strip("\t").strip(" ")) for x in m]
            for each_m in m:
                    s.extend(re.split('(?<=\s)[,](?=\s)|and|&', each_m))
            s=[x.strip("\t").strip(" ") for x in s]
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
    co_authors=set([clean_data.strip_accents(each_co_author) for each_co_author in co_authors if not re.search('[\d\\\\]', each_co_author)  ])
    new_co_authors=[]
    for each_coauthor in set(co_authors):
        if regexp_2.search(each_coauthor):
            name=HumanName(each_coauthor)
            new_co_authors.append((name.last+', '+name.first+' '+name.middle).strip(" "))
        else:
            new_co_authors.append(each_coauthor) 
    return(set(new_co_authors))




#method to get all relevant information(articles/publications,co-authors,institutions) for a winner from WIKI
def get_wiki_information(prize_type,doc_num,doc):
    n=doc.xpath('//link[@rel="canonical"]/@href')
    base_url=n[0]
    all_articles=set()
    name_set=set()
    nickname=None
    tr_elements = doc.xpath('//div[@class="mw-parser-output"]/table[@class="infobox biography vcard"]/tbody/tr')
    if tr_elements:
        for each_id in tr_elements[0].iterchildren(): 
            if each_id.tag=='th':
                parts = ([each_id.text] + list(chain(*([c.text, c.tail] for c in each_id.getchildren()))) + [each_id.tail])
                cell_data_text=''.join(filter(None, parts))
                personality_name=cell_data_text
        if personality_name and langid.classify(personality_name)[0]!='zh':
            name_set.add(clean_data.strip_accents(personality_name))
    full_name_tag=doc.xpath('//*[@class="mw-parser-output"]/p[not(@class ="mw-empty-elt")][1]/b')
    if full_name_tag:
        full_name=full_name_tag[0].text
        if full_name is not None:
            full_name=clean_data.strip_accents(full_name.split(',', 1)[0])
            name_set.add(full_name) 
    first_heading_tag=doc.xpath('//*[@id="firstHeading"]')
    if first_heading_tag:
        first_heading_name=first_heading_tag[0].text
        if first_heading_name is not None:
            first_heading_name=clean_data.strip_accents(first_heading_name.split(',', 1)[0])
            name_set.add(first_heading_name)  
    new_name_set=set()
    for each_name in name_set:
        nick_name=None
        name=HumanName(each_name)
        if (name.title):
            each_name = each_name.replace(name.title,'').replace('"','')
        each_name=each_name.replace("(",'"').replace(")",'"')
        if (name.nickname):
            nick_name=name.nickname
            each_name =each_name.replace('\"'+name.nickname+'\"','')
        each_name=each_name.replace(",","").replace('"','')
        each_name = re.sub('Jr\.$', '', each_name)
        #each_name=each_name.strip("(physicist)").strip("(chemist)")
        each_name=each_name.replace("\n", "").strip("\n").strip("\t").strip(" ")
        if "physicist" in each_name:
            each_name=re.sub('\"physicist\"','',each_name)
            each_name=re.sub(r"\(physicist\)",'',each_name)
        if "chemist" in each_name:
            each_name=re.sub('\"chemist\"','',each_name)
            each_name=re.sub(r"\(chemist\)",'',each_name)
        each_name=re.sub('\s+', ' ', each_name).strip()
        if ' '==each_name or ''==each_name:
            continue
        each_name=clean_data.remove_roman_and_period(each_name)
        new_name_set.add(each_name)
        if nick_name:
            new_name_set.add(nick_name+" "+each_name.split(" ")[-1])
    #if physicist in set of names , choose second longest name
    if any('physicist' in k for k in new_name_set):
        final_personality_name=sorted(list(new_name_set), key=len)[-2]
    else:
        final_personality_name=max(new_name_set, key=len)
    #print(final_personality_name)
    co_author_elements=doc.xpath('//th[contains(.//text(),"advisor") or contains(.//text(),"student")]/following-sibling::td[1]')
    co_authors=[]
    if co_author_elements:
        for each_elem in co_author_elements:
            co_author_elem=each_elem.xpath(".//a/@title")
            if co_author_elem:
                co_authors.extend(co_author_elem)
            co_author_elem2=each_elem.xpath(".//text()")
            if co_author_elem2:
                co_authors.extend(co_author_elem2)
        co_authors=[re.sub("[\(\[].*?[\)\]]", "", x) for x in co_authors]
        co_authors=[each_l for each_l in co_authors if any( not(("A" <= char and char <= "Z") or ("a" <= char and char <= "z") or (char == " ") or (char=='.')) for char in each_l) is False  and each_l!='' ]
        co_authors=set(co_authors)
    article_co_authors=parse_co_authors_from_articles(doc)
    institutions=set()
    institution_element=doc.xpath('//th[text()="Institutions"]/parent::tr')
    alma_mater=doc.xpath('//th[contains(text(),"Alma")]/parent::tr')
#     print(personality_name)
    if institution_element:
        affiliated_institutions=institution_element[0].xpath(".//a/@title")
        institution_hrefs=institution_element[0].xpath(".//a/@href")
       # print("href",institution_hrefs)
        if affiliated_institutions:
                affiliated_institutions=[clean_data.strip_accents(each_affliated_insitute) for  each_affliated_insitute in affiliated_institutions]
                affiliated_institutions=[re.sub(' +', ' ', re.sub(',','', each_affliated_insitute).strip()).strip() for  each_affliated_insitute in affiliated_institutions]
                affiliated_institutions=map(lambda x:x.lower(),affiliated_institutions)
                institutions.update(set(affiliated_institutions))
        if institution_hrefs:
            for each_href in institution_hrefs:
                institution_page=urlCanonicalization(each_href,base_url)
                if not ispolite(institution_page):continue
                m=parse_institutions(institution_page)
                if  m==None:
                    continue
                else:
                    institutions.add(m)
    if alma_mater:
        alma_institutions=alma_mater[0].xpath(".//a/@title")
        alma_hrefs=alma_mater[0].xpath(".//a/@href")
       # print("href",alma_hrefs)
        if alma_institutions:
                alma_institutions=[clean_data.strip_accents(each_affliated_insitute) for  each_affliated_insitute in alma_institutions]
                alma_institutions=[re.sub(' +', ' ', re.sub(',','', each_affliated_insitute).strip()).strip() for  each_affliated_insitute in alma_institutions]
                alma_institutions=map(lambda x:x.lower(),alma_institutions)
                institutions.update(set(alma_institutions))
        if alma_hrefs:
            for each_href in alma_hrefs:
                institution_page=urlCanonicalization(each_href,base_url)
                if not ispolite(institution_page):continue
                m=parse_institutions(institution_page)
                if  m==None:
                    continue
                else:
                    institutions.add(m)
    all_articles.update(parse_articles(new_name_set,doc))
    #scraping Known - for infobox biography vcard
    td_elem=doc.xpath('//*[@id="mw-content-text"]//table[contains(@class,"infobox biography vcard")]/tbody/tr/th[contains(text(),"Known")]/following-sibling::td')
    if not td_elem:
        return {prize_type+'-document-'+'{0}'.format(doc_num):{'preferred_name':final_personality_name,'all_names':new_name_set,'institutions':institutions,'articles':all_articles,'co_authors':set(co_authors),'article_co_authors':set(article_co_authors) }}
    known_for_hrefs=td_elem[0].xpath('.//a/@href')
    known_for_text=td_elem[0].xpath('.//a/text()')
    if known_for_text:
        all_articles.add(known_for_text[0])
    for each_href in known_for_hrefs:
        known_for_page=urlCanonicalization(each_href,base_url)
        if not ispolite(known_for_page):continue
        m=parse_known_for(known_for_page,new_name_set)
        if m==None:
            continue
        else:
            all_articles.update(m)
    return {prize_type+'-document-'+'{0}'.format(doc_num):{'preferred_name':final_personality_name,'all_names':new_name_set,'institutions':institutions,'articles':all_articles,'co_authors':set(co_authors),'article_co_authors':set(article_co_authors) }}






