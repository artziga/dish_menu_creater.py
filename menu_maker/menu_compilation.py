import peewee
from peewee import fn
from database.menu_models import Dish, Ingredient, Eating as EatingTable, Recipe, LnkDishTag, LnkEatingTag, Tag
import random


class Menu:

    def __int__(self, persons: list, target: str):
        pass


class Eating:

    def __init__(self, metabolism, cooking_time=30, serving_size=350,
                 hysteresis=0.1, part_from_daily_calories=0.33, category=None):
        self.high_hysteresis = 1 + hysteresis  # допуск отклонения калорий от целевого значения вверх
        self.low_hysteresis = 1 - hysteresis  # допуск отклонения калорий от целевого значения вниз
        self.serving_size = serving_size   # размер порции в г
        self.calories_needed = metabolism * part_from_daily_calories  # целевое количество калорий на один приём пищи
        self.cooking_time = cooking_time  # максимальное время готовки
        self.category = category
        if category is None:
            self.category = random.choice(['breakfast', 'second_dish', 'soup', 'salad', 'dessert', 'snack'])

    def get_dish(self):
        """Функция забирает из БД случайное блюдо, подходящие по указанным фильтрам"""
        low_calories = self.low_hysteresis * self.calories_needed
        high_calories = self.high_hysteresis * self.calories_needed
        calories_in_portion = Dish.calories * self.serving_size / 100  # делим на 100 т.к. калории для 100г блюда
        dish = (Dish.select(Dish.dish_name, Dish.calories, Dish.href, EatingTable.eating_name)
                .join(LnkDishTag, attr='a')
                .join(Tag, attr='b')
                .join(LnkEatingTag, attr='c')
                .join(EatingTable, attr='d')
                .where((EatingTable.eating_name == self.category)
                       &
                       (Dish.active_cooking_time <= self.cooking_time)
                       &
                       (calories_in_portion.between(low_calories, high_calories))
                       &
                       (Dish.portions_value.is_null(False)))
                .order_by(fn.random()).get())

        print(dish.dish_name)
        return dish


class Lunch(Eating):
    def __init__(self,
                 metabolism,
                 cooking_time=30,
                 serving_size=350,
                 hysteresis=0.1,
                 part_from_daily_calories=0.35,
                 ):
        super().__init__(metabolism, cooking_time, serving_size, hysteresis, part_from_daily_calories)
        self.category = 'soup' if random.randint(1, 100) < 30 else 'second_dish'
        self.low_hysteresis = 1 - hysteresis * 3

    def is_calories_enough(self, dish):
        if dish.calories * self.serving_size / 100 >= self.calories_needed * 0.85:
            return True
        return False

    def get_dish(self):
        self.low_hysteresis *= 0.8
        first_dish = super().get_dish()
        if self.is_calories_enough(first_dish):
            return first_dish
        else:
            self.category = 'second_dish' if self.category == 'soup' else 'soup'
            self.calories_needed = self.calories_needed - first_dish.calories
            self.low_hysteresis = 0.9
            self.high_hysteresis = 1.1
            second_dish = super().get_dish()
        return [first_dish, second_dish]


b = Lunch(metabolism=1900, cooking_time=30)
a = b.get_dish()
if type(a) != list:
    print(a.dish_name)
else:
    print([i.dish_name for i in a])


days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']


