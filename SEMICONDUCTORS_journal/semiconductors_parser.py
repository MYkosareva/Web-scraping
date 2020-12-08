from bs4 import BeautifulSoup
from tqdm import tqdm
import requests
import json
import re


def save_file(path, data):
    with open(path, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False)


def soup_(link):
    request = requests.get(link)
    soup = BeautifulSoup(request.text, 'lxml')
    return soup


main_page_link = "https://journals.ioffe.ru/issues/2024"
all_links = ['https://journals.ioffe.ru' + elem['href'] for elem in soup_(main_page_link).select('.issue_menu_item a')]


res = {'title': [], 'author': [], 'year': [], 'volume': [], 'issue': [], 'journal': []}
titles = []


for page in tqdm(all_links):
    temp_soup = soup_(page)
    titles = [elem.get_text() for elem in temp_soup.select('.issue_art_title a')]
    res['title'] += titles
    len_titles = len(titles)
    years = [elem.get_text() for elem in temp_soup.select('.issue_title')]
    res['author'] += [elem.get_text() for elem in temp_soup.find_all('div', class_='issue_art_authors')]
    res['year'] += [(re.findall('\d+', years[0])[0]) for _ in range(len_titles)]
    res['volume'] += [(re.findall('\d+', years[0])[1]) for _ in range(len_titles)]
    res['issue'] += [re.findall('\d+', years[0])[2] for _ in range(len_titles)]
    res['journal'] += [re.split('\d+', years[0])[0] for _ in range(len_titles)]


path_to_save = ''               # path to file
save_file(path_to_save, res)