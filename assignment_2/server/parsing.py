import re
import requests

from bs4 import BeautifulSoup


def parse_tomshardware_website():
    html = requests.get('https://www.tomshardware.com/reviews/gpu-hierarchy,4388.html').content
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find_all('table')[0]
    rows = table.find('tbody').find_all('tr')
    headers = ['name', 'score', 'gpu', 'boost_freq', 'memory', 'power', 'buy_link']
    for row in rows:
        cells = row.find_all('td')
        current_item = {}
        for header, cell in zip(headers, cells):
            if header == 'score':
                current_item[header] = cell.text[:-1]
            elif cell.a is not None:
                current_item[header] = cell.a['href']
            else:
                current_item[header] = cell.text
        del current_item['gpu']
        yield current_item


def parse_pcgamer_website():
    html = requests.get('https://www.pcgamer.com/gpu-hierarchy-2019-ranking-the-graphics-cards-you-can-buy/').content
    soup = BeautifulSoup(html, 'html.parser')
    headers = ['boost_freq', 'memory', 'cuda_cores']
    article = soup.select('#article-body')[0]
    descriptions = article.find_all('p', class_='specs__container')
    names = article.find_all('h3')
    for name, desc in zip(names, descriptions):
        item = {'name': re.search('. (.*)', name.text).group(1),
                'buy_link': name.a['href'] if name.a is not None else ''}
        for header, feature in zip(headers, desc.text.split('|')):
            feature = feature.replace(',', '')
            item[header] = re.search(': (.*) ', feature).group(1)
            if header == 'cuda_cores':
                item[header] = int(item[header])
        yield item
