# coding:utf-8

import argparse
from urllib2 import urlopen
from bs4 import BeautifulSoup
import re
import csv
import time

parser = argparse.ArgumentParser(description='scraping from androrank.com')
parser.add_argument('--filter',
                    help='choose filter types (select {org, pic, upd, sal, new} for parameter m; default: m=org)',
                    default='org')
parser.add_argument('--price',
                    help='choose price types (select {0:all, 1:free, 2:paid} for parameter s; default: s=1)',
                    default=1,
                    type=int)
parser.add_argument('--category',
                    help='choose categories (default: c=all)',
                    default='all')
parser.add_argument('--start_page',
                    help='select start page number (default: 1)',
                    default=1,
                    type=int)
parser.add_argument('--end_page',
                    help='select end page number (default: 0(all pages))',
                    default=0,
                    type=int)

args = parser.parse_args()

root_url = "http://androrank.com/"


def get_html(url):
    html = urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def search_last_page_num(url):
    soup = get_html(url)
    last_page = soup.find('div', id='page-list').find_all('li')[-2].string

    return int(last_page)


class CsvWriter:
    def __init__(self, out_path):
        self.out_path = out_path
        title_array = [[u'name', u'developer', u'category', u'mail address', u'url']]
        self.output_csv(title_array, 'w')

    def output_csv(self, out_info, mode):
        with open(self.out_path, mode) as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows(out_info)



def initialize():
    c_value = args.category
    m_value = args.filter
    s_value = args.price

    raw_target_url = root_url + "?c=%s&m=%s&s=%s" % (c_value, m_value, s_value)

    start_page = args.start_page
    if args.end_page is 0:
        end_page = search_last_page_num(raw_target_url)
    else:
        end_page = args.end_page

    csv_out_path = 'androrank_c_%s_m_%s_s_%s_sp_%s_ep_%s.csv' % (c_value, m_value, s_value, start_page, end_page)
    csv_writer_instance = CsvWriter(csv_out_path)

    return raw_target_url, start_page, end_page, csv_writer_instance

def get_first_links(url):
    soup = get_html(url)
    candidates = soup.find('table', id='main-list').find_all('a', id='name-l')
    result_url_list = list(set([root_url + element.get('href') for element in candidates]))

    return result_url_list

def get_googleplay_links(url_list):

    def get_googleplay_link(url):
        try:
            soup = get_html(url)
            return soup.find("div", id='url-d').find_all('a', target="_blank")[1].get('href')
        except:
            return None

    result_url_list =[get_googleplay_link(url) for url in url_list]
    result_url_list = [x for x in result_url_list if x is not None]

    return result_url_list


def scrape(url):
    internal_links_1 = get_first_links(url)
    googleplay_links = get_googleplay_links(internal_links_1)
    target_info = extract_from_googleplay(googleplay_links)

    return target_info

def extract_from_googleplay(url_list):

    def extract_info(url):
        try:
            soup = get_html(url)

            name = soup.find('div', class_='id-app-title').string
            provider = soup.find('a', class_='document-subtitle primary').find('span').string
            category = soup.find('a', class_='document-subtitle category').find('span').string
            tmp = soup.find('div', class_='content contains-text-link').find('a', href=re.compile('^mailto')).string
            address = tmp[tmp.find(':') + 2:]

            return [name, provider, category, address, url]
        except:
            # print 'open eroor: ' + url
            return None


    res = [x for x in map(extract_info, url_list) if x is not None]

    return res

if __name__ == '__main__':
    ts = time.time()
    raw_target_url, start_page, end_page, csv_writer_instance = initialize()

    for p in xrange(start_page, end_page+1):
        try:
            target_url = raw_target_url + '&p=%s' % p
            result = scrape(target_url)
        except:
            print 'some error occured!!'
        else:
            csv_writer_instance.output_csv(result, 'a')

        print 'page_count: %s' % p

    elapsed_time = time.time() - ts

    print "finish all process!!\n time: %s" % elapsed_time