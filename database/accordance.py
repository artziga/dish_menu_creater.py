import random
from peewee import fn, DoesNotExist
from energy_models import Energy
from menu_models import Ingredient, Recipe, Weight, OldIngredient, Tag, Eating, LnkEatingTag, OldWeight
from data_structure import Nutrient
from fuzzywuzzy import fuzz, process
from urllib.parse import quote
from pprint import pprint


def get_data():
    '''собирает названия ингридиентов из рецептов
     и из базы с калориями'''
    ingredients = set()
    energies = set()
    for ing in Ingredient.select():
        ingredients.add(ing.ingredient_name)
    for en in Energy.select():
        energies.add(en.name)
    return ingredients, energies


def get_ing_without_energy(ingredients, energies):
    dif = ingredients.difference(energies)
    same = ingredients.intersection(energies)
    return same, dif


def upd_same_en(same):
    for element in same:
        gbzu = Energy.get(Energy.name == element)
        ingred = Ingredient.get(Ingredient.ingredient_name == element)
        ingred.protein_value = gbzu.protein
        ingred.fats_value = gbzu.fats
        ingred.carbohydrates_value = gbzu.carbohydrates
        ingred.energy_value = gbzu.calories
        ingred.save()


def get_updown_en(ener: set, ingred: set):
    un_ings = list(ener.difference(ingred))
    ens = list(ingred.difference(ener))
    accord = {}
    for ing in un_ings:
        for en in ens:
            if fuzz.token_sort_ratio(ing, en) >= 95:
                accord[ing] = en
                un_ings.remove(ing)
                ens.remove(en)
    return accord


def get_empty_ings(ens):
    final_accord = {}
    q = Ingredient.select().where(Ingredient.energy_value.is_null()).order_by(fn.Random())
    remains = len(q)
    for ing in q:
        print(f'Осталось {remains} продуктов')
        ing = ing.ingredient_name
        var = process.extract(ing, ens, limit=7)
        print(ing)
        for i, j in enumerate(var):
            print(i + 1, j)
        ind = int(input('Введите соответствие: ')) - 1
        if ind == -1:
            continue
        gbzu = Energy.get(Energy.name == var[ind][0])
        ingred = Ingredient.get(Ingredient.ingredient_name == ing)
        ingred.protein_value = gbzu.protein
        ingred.fats_value = gbzu.fats
        ingred.carbohydrates_value = gbzu.carbohydrates
        ingred.energy_value = gbzu.calories
        ingred.save()
        remains -= 1


def upd_updown_en(ac: dict):
    for el in ac:
        gbzu = Energy.get(Energy.name == ac[el])
        ingred = Ingredient.get(Ingredient.ingredient_name == el)
        ingred.protein_value = gbzu.protein
        ingred.fats_value = gbzu.fats
        ingred.carbohydrates_value = gbzu.carbohydrates
        ingred.energy_value = gbzu.calories
        ingred.save()


def get_piece_products():
    piece_ingredients = []
    r = (Ingredient.select(Ingredient.ingredient_name)
         .join(Recipe)
         .where(Recipe.measure_unit.contains('шт')).distinct())
    for p_p in r:
        if p_p.ingredient_name:
            piece_ingredients.append(p_p.ingredient_name)
    return piece_ingredients


def get_old_weight(name):
    r = (OldWeight.select(OldWeight.weight)
         .join(OldIngredient)
         .where(OldIngredient.ingredient_name == name).get())
    return r.weight


def fill_from_old_weight():
    piece_ingredients = get_piece_products()
    print(len(piece_ingredients))
    for p_p in piece_ingredients:
        ingredient_id = Ingredient.get(Ingredient.ingredient_name == p_p)
        try:
            weight = get_old_weight(p_p)
        except DoesNotExist:
            Weight.create(ingredient_id=ingredient_id, weight=None)
            continue
        Weight.create(ingredient_id=ingredient_id, weight=weight)


def get_weight():
    prods = Weight.select(Weight.ingredient_id.alias('i_id'), Ingredient.ingredient_name) \
        .join(Ingredient) \
        .where(Weight.weight.is_null())
    rem = len(prods)
    for prod in prods:
        print(f'{prod.i_id} Осталось {rem} продуктов')
        name = prod.ingredient_id.ingredient_name
        weight = input(f'{name}\nhttps://www.google.com/search?q=%D0%B2%D0%B5%D1%81+{quote(name)}'
                       f'\nВведите вес: ')
        Weight.update({Weight.weight: weight}) \
            .where(Weight.ingredient_id == prod.i_id).execute()
        rem -= 1


def connect_weight():
    weight = OldWeight.select(OldWeight.weight, OldIngredient.ingredient_name) \
        .join(OldIngredient, attr='ingr') \
        .where(OldWeight.weight.is_null(False))
    for i in weight:
        if i:
            print(i.weight, i.ingr.ingredient_name)
    # prods = Weight.select(Weight.ingredient_id.alias('i_id'), Ingredient.ingredient_name) \
    #     .join(Ingredient) \
    #     .where(Weight.weight.is_null())


def fill_from_old_db():
    ingredients_to_fill = Ingredient.select().where(Ingredient.fats_value.is_null())
    print(len(ingredients_to_fill))
    for ingredient in ingredients_to_fill:
        try:
            old_ingredient = OldIngredient.get(OldIngredient.ingredient_name == ingredient.ingredient_name)
        except DoesNotExist:
            continue
        ingredient.energy_value = old_ingredient.energy_value
        ingredient.fats_value = old_ingredient.fats_value
        ingredient.protein_value = old_ingredient.protein_value
        ingredient.carbohydrates_value = old_ingredient.carbohydrates_value
        ingredient.save()


def connect_tags():
    tags = Tag.select(Tag.id, Tag.tag_name)
    for tag in tags:
        if 'завтрак' in tag.tag_name.lower().strip():
            eating_id = Eating.select(Eating.id).where(Eating.eating_name == 'breakfast').get()
            link = LnkEatingTag.create(eating_name_id=eating_id, tag_name_id=tag.id)
            link.save()
        if 'салат' in tag.tag_name.lower().strip():
            eating_id = Eating.select(Eating.id).where(Eating.eating_name == 'salad').get()
            link = LnkEatingTag.create(eating_name_id=eating_id, tag_name_id=tag.id)
            link.save()
        if 'обед' in tag.tag_name.lower().strip():
            eating_id = Eating.select(Eating.id).where(Eating.eating_name == 'second_dish').get()
            link = LnkEatingTag.create(eating_name_id=eating_id, tag_name_id=tag.id)
            link.save()
        if 'суп' in tag.tag_name.lower().strip():
            eating_id = Eating.select(Eating.id).where(Eating.eating_name == 'soup').get()
            link = LnkEatingTag.create(eating_name_id=eating_id, tag_name_id=tag.id)
            link.save()
        if 'десерт' in tag.tag_name.lower().strip() \
                or 'торт' in tag.tag_name.lower().strip() \
                or 'печенье' in tag.tag_name.lower().strip() \
                or 'пирожн' in tag.tag_name.lower().strip():
            eating_id = Eating.select(Eating.id).where(Eating.eating_name == 'dessert').get()
            link = LnkEatingTag.create(eating_name_id=eating_id, tag_name_id=tag.id)
            link.save()


if __name__ == '__main__':
    # get_weight()
    i, e = get_data()  # собираем данные из базы данных
    # sames, difs = get_ing_without_energy(i, e) # определяем продукты котрые есть и в ингридиентах и в базе калорий, а так же те ктоторые отличаются
    # upd_same_en(sames) # записываем калории для идентичных продуктов
    # ac = get_updown_en(i, e) # определяем продукты названия котрых отличаются только порядком слов
    # upd_updown_en(ac) # записываем в базу продукты названия котрых отличаются только порядком слов
    # fill_from_old_db()
    # get_empty_ings(e)  # запускаем ручное заполнение
    connect_tags()
    # fill_from_old_weight()
    # connect_weight()
# upd_updown_en(ac)


# f_a = get_empty_ings(e)
# upd_updown_en(f_a)


# un_ings, ens = get_ing_without_energy()
