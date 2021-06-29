from bs4 import BeautifulSoup
import requests
from multiprocessing import Pool
import json
import re


def save_file(path, data_):
    with open(path, 'w', encoding='utf-8') as outfile:
        json.dump(data_, outfile, ensure_ascii=False)


def get_html(url):
    request = requests.get(url)
    return request.text


def get_all_links(html):
    soup = BeautifulSoup(html, 'lxml')
    links_to_article_pages = ['https://journals.ioffe.ru' + elem['href'] for elem in soup.select('.issue_menu_item a')]
    return links_to_article_pages


def get_info_from_link(html):
    RES = {'title': [], 'author': [], 'year': [], 'volume': [], 'issue': [], 'journal': []}
    soup = BeautifulSoup(html, 'lxml')
    titles = [el.get_text().replace('\n', '') for el in soup.find_all(class_='issue_art_title')]
    RES['title'] += titles
    RES['author'] += [el.get_text().replace('\n\t', '') for el in soup.find_all('div', class_='issue_art_authors')]

    issue_info = [el.get_text() for el in soup.select('.issue_title')]
    issue_info_digits = re.findall('\d+', issue_info[0])
    count_of_articles = len(titles)

    RES['year'] += [int(issue_info_digits[0]) for _ in range(count_of_articles)]
    RES['volume'] += [int(issue_info_digits[1]) for _ in range(count_of_articles)]
    RES['issue'] += [int(issue_info_digits[2]) for _ in range(count_of_articles)]
    RES['journal'] += [re.split('\d+', issue_info[0])[0].replace('\n', '') for _ in range(count_of_articles)]
    return RES


def multi_run_wrapper(arg):
    return get_info_from_link(get_html(arg))


if __name__ == '__main__':
    url = "https://journals.ioffe.ru/issues/2024"  #url for scraping
    path_to_save = ''  # path to saving results

    all_links = get_all_links(get_html(url))
    pool = Pool(processes=30)
    data = pool.map(multi_run_wrapper, all_links)
    pool.close()
    pool.join()

    save_file(path_to_save, data)