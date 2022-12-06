import requests
from bs4 import BeautifulSoup
from database.data_structure import Nutrient

url = 'https://calorizator.ru/product/all'


def get_nutrients(soup):
    prods = []
    for prod in soup.find('tbody').find_all('tr'):
        nutrients = Nutrient(name=prod.find('td', class_='views-field views-field-title active').text.lower().strip(),
                             calories=prod.find('td', class_='views-field views-field-field-kcal-value').text.strip(),
                             protein=prod.find('td', class_='views-field views-field-field-protein-value').text.strip(),
                             fats=prod.find('td', class_='views-field views-field-field-fat-value').text.strip(),
                             carbohydrates=prod.find('td',
                                                     class_='views-field views-field-field-carbohydrate-value').text.strip())
        prods.append(nutrients._asdict())
    return prods


def pars_energy() -> list[dict]:
    for page in range(80):
        print(f'Собирается страница: {page + 1}')
        params = {'page': page}
        r = requests.get(url, params=params)
        if not r:
            break
        soup = BeautifulSoup(r.text, 'lxml')
        page += 1
        prods = get_nutrients(soup)
        yield prods


