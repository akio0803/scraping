# coding:utf-8

from urllib2 import Request, urlopen, URLError, HTTPError
import requests
from bs4 import BeautifulSoup
import re
import csv
import time


def create_root_url_list(start, stop, root_url):
    tmp_list = range(start, stop)
    root_url_list = [root_url + str(x) for x in tmp_list]

    return root_url_list


def get_first_links_androider(url_list):

    def get_first_link(url):
        soup = get_html(url)
        tmp_url_list = [x.a.get('href') for x in soup.find_all('p', class_='appliName')]

        return tmp_url_list

    tmp = [get_first_link(url) for url in url_list]

    res = [url for x in tmp for url in x]

    return res


def get_secound_links_androider(url_list):

    def get_secound_link(url):
        soup = get_html(url)

        return soup.find('div', class_='dl_gp_btn').a.get('href')

    res = map(get_secound_link, url_list)

    return res


def scraping_androider(start, stop):
    root_url = 'https://androider.jp/official/applist/'

    root_url_list = create_root_url_list(start, stop, root_url)
    links_1 = get_first_links_androider(root_url_list)
    googleplay_url = get_secound_links_androider(links_1)

    return googleplay_url


def androider(start, stop):
    googleplay_url = scraping_androider(start, stop)
    target_info = extract_from_googleplay(googleplay_url)

    return target_info


def get_first_links_ketchapp(url_list):

    def get_first_link(url):
        soup = get_html(url)
        url_list = [x.a.get('href') for x in soup.find_all('div', class_='rev_list_area')]
        return url_list

    tmp = [get_first_link(url) for url in url_list]
    res = [url for x in tmp for url in x]

    return res


def get_secound_links_ketchapp(url_list):

    def get_secound_links(url):
        soup = get_html(url)
        itunes_url = ''
        googleplay_url = ''

        for target in  soup.find_all('div', 'rev_button_area'):
            if target.find('a', class_='button_iphone') is not None:
                itunes_url = target.find('a', class_='button_iphone').get('href')
            if target.find('a', class_='button_andmkt') is not None:
                googleplay_url = target.find('a', class_='button_andmkt').get('href')

        return [googleplay_url, itunes_url]

    googleplay_url_list = []
    itunes_url_list = []
    for url in url_list:
        googleplay_url, itunes_url = get_secound_links(url)
        if googleplay_url:
            googleplay_url_list.append(googleplay_url)
        if itunes_url:
            itunes_url_list.append(itunes_url)

    return [googleplay_url_list, itunes_url_list]


def scraping_ketchapp(start, stop):
    root_url = 'http://ketchapp.jp/app/page/'

    root_url_list = create_root_url_list(start, stop, root_url)
    links_1 =  get_first_links_ketchapp(root_url_list)
    googleplay_url, itunes_url = get_secound_links_ketchapp(links_1)

    return [googleplay_url, itunes_url]


def ketchapp(start, stop):
    googleplay_url, itunes_url = scraping_ketchapp(start, stop)
    tmp1 = extract_from_googleplay(googleplay_url)
    tmp2 = extract_from_itues(itunes_url)
    target_info = tmp1 + tmp2

    return target_info


def get_html(url):
    html = urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')
    return soup


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


def extract_from_itues(url_list):

    def extract_info(url):
        try:
            soup = get_html(url)

            name = soup.find('div', class_='intro').h1.string
            tmp1 = soup.find('div', class_='intro').h2.string
            provider = tmp1[tmp1.find(':') + 2:]
            category = soup.find('span', itemprop='applicationCategory').string
            address = ''

            return [name, provider, category, address, url]
        except:
            # print 'open error:' + url
            return None

    res = [x for x in map(extract_info, url_list) if x is not None]

    return res


def init_csv():
    title_array = [[u'name', u'developer', u'category', u'mail address', u'url']]
    output_csv(title_array, 'w')


def output_csv(info, mode):
    f = open('applist.csv', mode)

    writer = csv.writer(f, lineterminator='\n')
    writer.writerows(info)

    f.close()


def focus_page(loop):
    get_per_loop = 2
    start = get_per_loop * loop + 1
    stop = start + get_per_loop

    return [start, stop]


if __name__ == '__main__':
    t_s = time.time()

    loop_num = 10

    init_csv()

    for i in range(loop_num):
        try:
            start, stop = focus_page(i)
            # target_info = androider(start, stop)
            target_info = ketchapp(start, stop)
        except:
            continue
        else:
            output_csv(target_info, 'a')

        print 'loop_count:' + str(i)

    t = time.time() - t_s

    print "extraction finished!!\n" + "time: " + str(t)
