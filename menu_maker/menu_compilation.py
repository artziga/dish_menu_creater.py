import peewee
from peewee import fn
from database.menu_models import Dish, Ingredient, Eating, Recipe
import random

days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']


def get_bf_or_din(eating: str, tt: int, at: int) -> peewee.ModelSelect:
    foods = Dish.select(Dish.dish_name, Dish.href). \
        join(Eating) \
        .where((Eating.eating_name == eating)
               & (Dish.active_cooking_time < tt)
               & (Dish.total_cooking_time < at)) \
        .order_by(fn.Random()).limit(7)
    return foods

def get_energy_value(foods: list):
    foods = {}
    for food in foods:
        Ingredient.get()


def get_lunchs(tt: int, at: int) -> list:
    foods = []
    for day in days:
        if random.randint(1, 100) > 70:
            eating = 'soup'
        else:
            eating = 'second_dish'
        food = Dish.select(Dish.dish_name, Dish.href). \
            join(Eating)\
            .where((Eating.eating_name == eating)
                   & (Dish.active_cooking_time < tt)
                   & (Dish.total_cooking_time < at))\
            .order_by(fn.Random()).get()
        foods.append(food)
    return foods


def get_dish_list():
    bf = [food for food in get_bf_or_din('breakfast', 15, 30)]
    second_dish = get_lunchs(30, 60)
    dinner = [food for food in get_bf_or_din('second_dish', 20, 40)]
    for day, b, l, d in zip(days, bf, second_dish, dinner):
        print(f'{day}\nЗавтрак: {b.dish_name},'
              f' Обед: {l.dish_name}, '
              f'Ужин: {d.dish_name}')


get_dish_list()

