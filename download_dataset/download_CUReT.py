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
    soup = get_html("http://www.cs.columbia.edu/CAVE/software/curet/html/download.html")
    target_list = soup.find_all('a')[:-1]

    root_url = 'http://www.cs.columbia.edu/CAVE/'

    url_list = [root_url + re.sub(r'(\.\.\/)+', '/', x.get('href')) for x in target_list]

    map(wget.download, url_list)
