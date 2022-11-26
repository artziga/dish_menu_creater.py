import requests
from bs4 import BeautifulSoup

url = 'https://calorizator.ru/product/all'


def pars_energy() -> dict:
    for page in range(80):
        print(f'Собирается страница: {page + 1}')
        params = {'page': page}
        r = requests.get(url, params=params)
        if not r:
            break
        soup = BeautifulSoup(r.text, 'lxml')
        page += 1
        for elem in soup.find('tbody').find_all('tr'):
            prod = {}
            i = elem.find_all('td')
            prod['name'] = i[1].text.lower().strip()
            prod['prot'] = i[2].text.strip()
            prod['fats'] = i[3].text.strip()
            prod['carbohydrates'] = i[4].text.strip()
            prod['calories'] = i[5].text.strip()
            yield prod


