# coding:utf-8

from urllib2 import urlopen
from bs4 import BeautifulSoup
import re
import wget


def get_html(url):
    html = urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')
    return soup

if __name__ == '__main__':
    soup = get_html("http://www.cb.uu.se/~gustaf/texture/data/with-rotations-zip/")

    target_list = [x.find('a').get('href') for x in soup.find_all('tr')[4:-1]]

    root_url = 'http://www.cb.uu.se/~gustaf/texture/data/with-rotations-zip/'

    url_list = [root_url + x for x in target_list]

    map(wget.download, url_list)
