import bs4
import peewee
import requests
from bs4 import BeautifulSoup
import time
from database.menu_models import Dish as DishTable,\
    Recipe as RecipeTable,\
    Ingredient as IngredientTable, \
    Tag as TagTable, \
    LnkDishTag as LnkDishTagTable
from normalization import normalization as norm
from database.data_structure import Dish, DishPage, Ingredient, DishInfo
from logger_create import init_logger
import logging

init_logger('app')
logger = logging.getLogger('app.parsing.pars_menu')


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
            logger.debug('----------------------------')
            break
        logger.debug(f'Собирается страница {page}')
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
                    except ValueError as err:
                        logger.warning(err, name, href)
                        total_duration = 0
                    try:
                        active_duration = norm.get_minutes(dur[1].text)
                    except ValueError as err:
                        logger.warning(err, name, href)
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
        logger.debug(er, dish.dish_name)


def get_dish_pages(table: type[DishTable]) -> list[str]:
    hrefs = table.select(table.href).where(table.id == 2599)
    return [h.href for h in hrefs]


def get_dish_html(dish_url) -> DishPage:
    return DishPage(url=dish_url, html=requests.get(dish_url).text)


def get_ingredients(
        ingredient_names: bs4.element.ResultSet,
        ingredients_value: bs4.element.ResultSet,
        ingredients_type: bs4.element.ResultSet) -> list[Ingredient]:
    ingredients = []
    for name, value, unit in zip(ingredient_names, ingredients_value, ingredients_type):
        try:
            val, unit, note = norm.ingredient_value(value.text, unit.text)
        except ValueError as err:
            logger.warning(err)
            raise ValueError
        ingredients.append(Ingredient(
            ingredient_name=name.text.strip().lower(),
            value=val,
            measure_units=unit,
            note=note))
    return ingredients


def parse_dish_page(href) -> DishInfo:
    dish = get_dish_html(dish_url=href)
    soup = BeautifulSoup(dish.html, 'lxml')
    try:
        portions_value = soup.find('span', class_='yield').text
    except AttributeError:
        portions_value = None
        logger.debug(f'У блюда нет  количества порций {dish.url}')
    ingredients_list = soup.find('ul', class_='ingredients-lst')
    ingredient_names = ingredients_list.find_all('span', class_='name')
    ingredients_value = ingredients_list.find_all('span', class_='value')
    ingredients_type = ingredients_list.find_all('span', class_='type')
    ingredients = get_ingredients(ingredient_names, ingredients_value, ingredients_type)
    categories = [i.text for i in soup.find('div', class_='catg').find_all('a', rel='category tag')]
    return DishInfo(ingredients=ingredients, portions_value=portions_value, categories=categories)


def fill_ingredients(ingredients: list[Ingredient], dish) -> None:
    for ingredient in ingredients:
        try:
            ing = IngredientTable.create(ingredient_name=ingredient.ingredient_name)
        except peewee.IntegrityError as err:
            ing = IngredientTable.get(ingredient_name=ingredient.ingredient_name)
            #logger.debug(f'{ingredient.ingredient_name} уже есть в базе')
        RecipeTable.create(
            quantity=ingredient.value,
            measure_unit=ingredient.measure_units,
            dish_name_id=dish,
            ingredient_name_id=ing,
            note=ingredient.note)


def fill_categories(dish, categories: list) -> None:
    for category in categories:
        try:
            cat = TagTable.create(tag_name=category)
        except peewee.IntegrityError as err:
            cat = TagTable.get(tag_name=category)
            #logger.debug(f'Категория {category} уже есть в добавлена')
        LnkDishTagTable.create(dish_name_id=dish, tag_name_id=cat)


def fill_recipes_info(num):
    dishes = DishTable.select(DishTable.id, DishTable.dish_name, DishTable.href).order_by(DishTable.id)
    for dish in dishes:
        logger.debug(f'собирается блюдо {dish.dish_name}\n{dish.id} из {len(dishes)}, {round(dish.id/len(dishes)*100, 2)}%')
        if not RecipeTable.select(RecipeTable.dish_name_id).where(RecipeTable.dish_name_id == dish.id):
            try:
                dish_info = parse_dish_page(dish.href)
            except AttributeError or ValueError:
                logger.warning(f'Не удалось собрать данные для блюда {dish.dish_name} {dish.href}')
                continue
            DishTable.portions_value = dish_info.portions_value
            fill_ingredients(dish=dish, ingredients=dish_info.ingredients)
            fill_categories(dish=dish, categories=dish_info.categories)
            time.sleep(1)

if __name__ == '__main__':
    fill_recipes_info(6)






