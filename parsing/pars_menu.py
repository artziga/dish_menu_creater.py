import bs4
import peewee
import requests
from bs4 import BeautifulSoup
from typing import NamedTuple
import time
from database.menu_models import Dish as DishTable, Ingredient, Tag, LnkDishTag
from normalization import normalization as norm


class Dish(NamedTuple):
    dish_name: str
    href: str
    total_cooking_time: int
    active_cooking_time: int


class Ingredient(NamedTuple):
    ingredient_name: str
    value: float
    measure_units: str


def get_category_urls() -> list[str]:
    html = requests.get('https://menunedeli.ru/2014/12/katalog-receptov-i-statej-opublikovannyx-na-sajte/')
    soup = BeautifulSoup(html.text, 'lxml')\
        .find_all('ul', class_='catg row no-gutters')[4]\
        .find_all('li', class_='col item')
    urls = get_hrefs_from_page(soup=soup)
    return urls


def get_hrefs_from_page(soup: bs4.element.ResultSet) -> list:
    urls = []
    for i in soup:
        e = i.find('li')
        if e:
            url = e.find('a').get('href')
            if 'https://menunedeli.ru' in url:
                urls.append(url)
            else:
                urls.append('https://menunedeli.ru' + url)
    return urls


def get_page(url: str) -> bs4.element.ResultSet:
    page = 1
    url = url + 'page/'
    while True:
        html = requests.get(url + str(page))
        time.sleep(1)
        if not html:
            print('----------------------------')
            break
        print(f'Собирается страница {page}')
        soup = BeautifulSoup(html.text, 'lxml').find_all('div', class_='info col')
        yield soup
        page += 1


def get_dishes(fc: bs4.element.ResultSet) -> list[dict[Dish, Ingredient]]:
    dishes = []
    for card in fc:
        dish = {}
        dish_name = card.find('h5', class_='hdr').text
        href = card.find('a').get('href')
        dur = card.find_all('span', class_='duration')
        if dur:
            total_duration = norm.get_minutes(dur[0].text)
            active_duration = norm.get_minutes(dur[1].text)
        else:
            total_duration = 0
            active_duration = 0
        ingredients_list = card.find_all('ul', class_="ingredients-lst")
        for ingredient in ingredients_list:
            names = [norm.get_ing_name(name.text.lower().strip()) for name in ingredient.find_all('span', class_="name")
                     if name.text]
            values = [norm.get_digital_ingredient_value(value.text) for value in ingredient.find_all('span', class_="value")]
            measure_units = [measure_unit.text.strip().lower() for measure_unit in ingredient.find_all('span', class_="type")]
            dish[Dish(
                dish_name=dish_name,
                href=href,
                active_cooking_time=active_duration,
                total_cooking_time=total_duration
            )] = Ingredient(
                ingredient_names=names,
                values=values,
                measure_units=measure_units)
        if dish:
            dishes.append(dish)
    return dishes


def get_dish_urls(cat_urls: list[str]) -> list[Dish]:
    for cat_url in cat_urls:
        dish_page = get_page(cat_url)
        for cards in dish_page:
            for card in cards:
                name = card.find('h5', class_='hdr').text
                href = card.find('a').get('href')
                dur = card.find_all('span', class_='duration')
                if dur:
                    try:
                        total_duration = norm.get_minutes(dur[0].text)
                    except ValueError:
                        print(name, href)
                        total_duration = 0
                    try:
                        active_duration = norm.get_minutes(dur[1].text)
                    except ValueError:
                        print(name, href)
                        active_duration = 0
                else:
                    total_duration = active_duration = 0
                yield Dish(
                    dish_name=name,
                    href=href,
                    active_cooking_time=active_duration,
                    total_cooking_time=total_duration
                )


def fill_dish_table(dish: Dish):
    try:
        DishTable.create(**dish._asdict())
    except peewee.IntegrityError as er:
        print(er, dish.dish_name)


def get_dish_pages(table: type[DishTable]) -> list[str]:
    hrefs = table.select(table.href).where(table.id < 10)
    return [h.href for h in hrefs]


def get_dish_html():
    for dish_url in get_dish_pages(DishTable):
        print('_________')
        yield requests.get(dish_url).text


def get_ingredients(
        ingredient_names: bs4.element.ResultSet,
        ingredients_value: bs4.element.ResultSet,
        ingredients_type: bs4.element.ResultSet) -> list:
    ingredients = []
    for name, value, unit in zip(ingredient_names, ingredients_value, ingredients_type):
        val, unit, note = norm.ingredient_value(value.text, unit.text)
        if note:
            ingredients.append((Ingredient(
                ingredient_name=name.text.strip().lower(),
                value=val,
                measure_units=unit), note))
        else:
            ingredients.append(Ingredient(
                ingredient_name=name.text.strip().lower(),
                value=val,
                measure_units=unit))

    return ingredients


def parse_dish_page():
    for dish in get_dish_html():
        soup = BeautifulSoup(dish, 'lxml')
        try:
            portions_value = soup.find('span', class_='yield').text
        except AttributeError:
            with open('1.html', 'w', encoding='utf-8') as f:
                f.write(dish)

        ingredients_list = soup.find('ul', class_='ingredients-lst')
        ingredient_names = ingredients_list.find_all('span', class_='name')
        ingredients_value = ingredients_list.find_all('span', class_='value')
        ingredients_type = ingredients_list.find_all('span', class_='type')
        ingredients = get_ingredients(ingredient_names, ingredients_value, ingredients_type)
        categories = soup.find('div', class_='catg').find_all('a', rel='category tag')
        cats = [i.text for i in categories]
        for i in ingredients:
            print(i)


def get_cooking_time(url: str):
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'lxml').find_all('div', class_='info col')
    for times in soup:
        dur = times.find_all('span', class_='duration')
        if dur:
            total_time = dur[0].text
            active_time = dur[1].text
            print(f'Общее время: {total_time} / Активное время: {active_time}')
        # print(dur.text)


if __name__ == '__main__':
    parse_dish_page()





