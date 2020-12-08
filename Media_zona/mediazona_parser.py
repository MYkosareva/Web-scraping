import re
import time
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


X_PATH_BUTTON = '/html/body/div/section/section/section/section/a'


def save_file(path, data_):
    """
        To save on Directory.
    """
    with open(path, 'w', encoding='utf-8') as outfile:
        json.dump(data_, outfile, ensure_ascii=False)


def get_url_data(link):
    """
        N_CLICK -  is the number of clicks on the button "MORE 25 articles"
        returns list of links: ['string','string'...'string']

    """
    driver = webdriver.Chrome()
    driver.get(link)
    time.sleep(3)
    try:
        for click in range(N_CLICK):
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, X_PATH_BUTTON))).click()
            time.sleep(3)
    except:
        pass
    soup = BeautifulSoup(driver.page_source, 'lxml')
    links = ['https://zona.media' + elem.get('href') for elem in
             soup.find_all('a', class_='mz-topnews-item__link-wrapper')]   #mz-material-item__link-wrapper
    try:
        links += ['https://zona.media' + elem.get('href') for elem in
                  soup.find_all('a', class_='mz-feature-item__link')]
    except:
        pass
    driver.quit()
    return links


def get_data(link):
    """
        Take all data about article (title, text, date of publication)
        return dictionary: {title': title, 'text': text, 'link': link, 'date': date}
    """
    request = requests.get(link)
    soup = BeautifulSoup(request.text, 'lxml')
    title = soup.find('title').get_text()

    text = ''
    try:
        announce_text = soup.find('div', class_='mz-publish__announce').get_text(' ')
        text += announce_text + ' '
    except:
        pass
    try:
        for elem in soup.find_all('section', class_='mz-publish__text'):
            text += ' ' + elem.get_text(' ')
    except:
        for elem in soup.find_all('div', class_='mz-publish__text__content'):
            text += ' ' + elem.get_text(' ')

    redundant_text = [elem.get_text(' ') for elem in soup.find_all('span', class_="mz-publish-context-cite__text")]
    if len(redundant_text) != 0:
        for redundant_t in redundant_text:
            text = re.sub(redundant_t, ' ', text)

    try:
        date = soup.find('div', 'mz-publish-meta__item').get_text()[:-7]
    except:
        date = soup.find('span', 'mz-content-meta-info__item').get_text()[:-7]

    ready = {'title': title, 'text': text, 'link': link, 'date': date}
    return ready


def media_zona_parser(link):
    """
        link - link for scraping
        N_CLICK  -  is the number of clicks on the button "MORE 25 articles
        function return [{data},{data}...{data}]

    """
    if link.startswith('https://zona.media'):
        r = requests.get(link)
        if r.status_code == 200:
            if link[19:24] == 'theme' or link.endswith('news') or link.endswith('chronicles'):
                links_lst = get_url_data(link)
                res = []
                for links in links_lst:
                    res += [get_data(links)]
                return res

            else:
                return get_data(link)
        else:
            return 'Please, check URL'
    else:
        return 'Incorrect link '


if __name__ == '__main__':
    url = ''                        #url for parsing
    N_CLICK = 3                     #number of clicks on the button "MORE 25 articles
    path_to_saving = ''             #path to empty json file
    data = media_zona_parser(url)   #data obtained
    save_file(path_to_saving, data) #saving data to json file