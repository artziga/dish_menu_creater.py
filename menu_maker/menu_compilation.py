import peewee
from peewee import fn, JOIN
from database.menu_models import Dish, Ingredient, Eating as EatingTable, Recipe, LnkDishTag, LnkEatingTag, Tag
from database.data_structure import EatingSet
import random

METABOLISM = 1900
i = 1


class DayMenu:
    def __init__(self, target: str = ''):
        self._breakfast = Eating(metabolism=METABOLISM, cooking_time=20, category='breakfast')
        self._lunch = Lunch(metabolism=METABOLISM, cooking_time=30)
        self._dinner = Eating(metabolism=METABOLISM, cooking_time=20, category='second_dish', alias='dinner')
        self.day_menu_variants = self.get_menu(100)

    def get_menu(self, limit):
        breakfast = self._breakfast.dish
        lunch = self._lunch.dish
        dinner = self._dinner.dish
        day_menu = (Dish
                    .select(Dish.dish_name,
                            Dish.href,
                            lunch.c.dish_name.alias('lunch_name'),
                            lunch.c.href.alias('lunch_href'),
                            dinner.c.dish_name.alias('dinner_name'),
                            dinner.c.href.alias('dinner_href'),
                            ((Dish.calories + lunch.c.calories + dinner.c.calories) * 3.5).alias('sum'))
                    .join(breakfast, on=(Dish.dish_name == lunch.alias('breakfast').c.dish_name))
                    .join(lunch, JOIN.CROSS)
                    .join(dinner, JOIN.CROSS)
                    .where(((breakfast.c.calories + lunch.c.calories + dinner.c.calories) * 3.5)
                           .between(METABOLISM * 0.99, METABOLISM * 1.01))
                    .order_by(fn.random())
                    .limit(limit))
        print(day_menu)
        return day_menu


class Eating:

    def __init__(self,
                 metabolism: int,
                 cooking_time: int = 30,
                 serving_size: int = 350,
                 hysteresis: float = 0.15,
                 part_from_daily_calories: float = 0.33,
                 category: str = None,
                 alias: str = None):
        self.dish_set: EatingSet | None = None
        self._high_hysteresis = 1 + hysteresis  # ???????????? ???????????????????? ?????????????? ???? ???????????????? ???????????????? ??????????
        self._low_hysteresis = 1 - hysteresis  # ???????????? ???????????????????? ?????????????? ???? ???????????????? ???????????????? ????????
        self._serving_size = serving_size  # ???????????? ???????????? ?? ??
        self._calories_needed = metabolism * part_from_daily_calories  # ?????????????? ???????????????????? ?????????????? ???? ???????? ?????????? ????????
        self._cooking_time = cooking_time  # ???????????????????????? ?????????? ??????????????
        self._low_calories = self._calories_needed * self._low_hysteresis
        self._high_calories = self._calories_needed * self._high_hysteresis
        if category is None:
            self._category = random.choice(['breakfast', 'second_dish', 'soup', 'salad', 'dessert', 'snack'])
        else:
            self._category = category
        self.dish = self.get_dish(category=self._category, alias=alias)

    def get_dish(self, category: str = None, alias: str = None, low_calories=None, high_calories=None, limit=100):
        """?????????????? ???????????????? ???? ???? ?????????????????? ??????????, ???????????????????? ???? ?????????????????? ????????????????"""
        if low_calories is None:
            low_calories = self._low_calories
        if high_calories is None:
            high_calories = self._high_calories
        if alias is None:
            alias = category
        calories_in_portion = (Dish.alias(alias)
                               .calories * self._serving_size) / 100  # ?????????? ???? 100 ??.??. ?????????????? ?????? 100?? ??????????
        limitation = ((EatingTable.eating_name == category)
                      &
                      (calories_in_portion.between(low_calories, high_calories))
                      & (Dish.alias(alias).active_cooking_time <= self._cooking_time))
        dish_variants = (Dish.alias(alias).select(Dish.alias(alias).id,
                                                  Dish.alias(alias).dish_name,
                                                  Dish.alias(alias).href,
                                                  Dish.alias(alias).calories)
                         .join(LnkDishTag)
                         .join(Tag)
                         .join(LnkEatingTag)
                         .join(EatingTable)
                         .where(limitation)
                         .alias(alias)
                         .order_by(fn.random())
                         .limit(limit)
                         .distinct())
        return dish_variants


class Lunch(Eating):
    def __init__(self,
                 metabolism: int,
                 cooking_time: int = 30,
                 serving_size: int = 350,
                 hysteresis: float = 0.15,
                 part_from_daily_calories: float = 0.35,
                 ):
        super().__init__(metabolism,
                         cooking_time,
                         serving_size,
                         hysteresis,
                         part_from_daily_calories)

    def get_dish(self, category: str = None, alias: str = None, low_calories=None, high_calories=None, limit=100):
        second_dishes = super().get_dish('second_dish', low_calories=0, high_calories=1000)
        soups = super().get_dish(category='soup', low_calories=0, high_calories=1000)
        second_dishes_only = super().get_dish('second_dish', limit=70)
        soups_with_second_dishes = (Dish.select(Dish.id,
                                                soups.c.dish_name.concat('||').concat(Dish.dish_name).alias(
                                                    'dish_name'),
                                                (soups.c.href.concat(' || ').concat(Dish.href)).alias('href'),
                                                (soups.c.calories + Dish.calories).alias('calories'),
                                                )
                                    .join(second_dishes, on=(Dish.id == second_dishes.c.id))
                                    .join(soups, JOIN.CROSS)
                                    .where(((soups.c.calories + second_dishes.c.calories) * self._serving_size / 100)
                                           .between(self._low_calories, self._high_calories)
                                           & (soups.c.dish_name != second_dishes.c.dish_name))
                                    .order_by(fn.random())
                                    .limit(30))

        union = second_dishes_only | soups_with_second_dishes
        # print(union)
        # print(union.count())
        dice = random.randint(1, 100)
        if dice > 30:
            return second_dishes_only
        return soups_with_second_dishes


# e = Eating(metabolism=METABOLISM, category='salad')
a = DayMenu()

# for i in a.get_menu(7):
#     print(f'??????????????: {i.dish_name}, ????????: {i.lunch_name}, ????????: {i.dinner_name}, ?????????????? ???? ????????: {i.sum}')

el = Lunch(metabolism=METABOLISM)
# el.get_lunch_variants()
days = ['??????????????????????', '??????????????', '??????????', '??????????????', '??????????????', '??????????????', '??????????????????????']
for day in days:
    print(day)
    a = DayMenu()
    menu = a.day_menu_variants.get()
    print(f'??????????????: {menu.dish_name}  {menu.href}, '
          f'????????: {menu.lunch_name}  {menu.lunch_href}, '
          f'????????: {menu.dinner_name}  {menu.dinner_href}, '
          f'???????????????? ???? ????????: {menu.sum}')



