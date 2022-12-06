import requests
from bs4 import BeautifulSoup
from database.data_structure import Nutrient

cookies = {
    '_ym_uid': '1669124732148791181',
    '_ym_d': '1669124732',
    '_ym_isad': '1',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    # Requests sorts cookies= alphabetically
    # 'Cookie': '_ym_uid=1669124732148791181; _ym_d=1669124732; _ym_isad=1',
    'Referer': 'https://health-diet.ru/table_calorie/',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}


def get_categories() -> list[str]:
    response = requests.get(
        'https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie',
        cookies=cookies,
        headers=headers
    )
    soup = BeautifulSoup(response.text, 'lxml')
    categories_html = soup.find('div', class_='uk-grid uk-grid-medium')\
        .find_all('div', class_='uk-flex mzr-tc-group-item')
    categories_urls = ['https://health-diet.ru' + category.find('a').get('href') for category in categories_html]
    return categories_urls


def get_prods_nutrients(soup) -> list[dict]:
    products = soup.find('div', class_='uk-overflow-container').find_all('tr')
    prods = []
    for prod in products[1:]:
        nutrients = prod.find_all('td')
        nutrients = Nutrient(name=nutrients[0].text.lower().strip(),
                             calories=nutrients[1].text.strip().split(' ')[0],
                             protein=nutrients[2].text.strip().split(' ')[0],
                             fats=nutrients[3].text.strip().split(' ')[0],
                             carbohydrates=nutrients[4].text.strip().split(' ')[0])
        prods.append(nutrients._asdict())
    return prods


def get_cat_nutrients(category: str):
    response = requests.get(
        category,
        cookies=cookies,
        headers=headers
    )
    soup = BeautifulSoup(response.text, 'lxml')
    nutrs = get_prods_nutrients(soup)
    return nutrs


def get_nutrients():
    categories = get_categories()
    for category in categories:
        nutrs = get_cat_nutrients(category=category)
        yield nutrs

