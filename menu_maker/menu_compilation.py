from peewee import fn, JOIN
from database.menu_models import Dish, Ingredient, Eating as EatingTable, Recipe, LnkDishTag, LnkEatingTag, Tag
from database.data_structure import EatingSet
import random
from itertools import product

METABOLISM = 1900
i = 1


class DayMenu:
    def __init__(self, target: str = '', breakfast_to_use_id=None, lunch_to_use_id=None, dinner_to_use_id=None):
        self._breakfast = Eating(metabolism=METABOLISM, cooking_time=20, category='breakfast', alias='breakfast',
                                 dish_to_use_id=breakfast_to_use_id)
        self._lunch = Lunch(metabolism=METABOLISM, cooking_time=30)
        self._dinner = Eating(metabolism=METABOLISM, cooking_time=20, category='second_dish', alias='dinner',
                              dish_to_use_id=dinner_to_use_id)
        self.day_menu_variants = self.get_menu(100)

    def get_menu(self, limit):
        breakfast = self._breakfast.dish
        lunch = self._lunch.dish
        dinner = self._dinner.dish
        day_menu = (Dish
                    .select(Dish.id,
                            Dish.dish_name,
                            Dish.href,
                            lunch.c.id.alias('lunch_id'),
                            lunch.c.dish_name.alias('lunch_name'),
                            lunch.c.href.alias('lunch_href'),
                            dinner.c.id.alias('dinner_id'),
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
        return day_menu


class WeekMenu:
    def __init__(self, left_dishes: dict[str, dict[int, int]] = None):
        if left_dishes is not None:
            self.left_dishes = left_dishes
        else:
            self.left_dishes = {
                'breakfast': None,
                'lunch': None,
                'dinner': None
            }
        self.is_soup_allowed = True
        self.menu = []
        self.combinations: list[set] = []
        self.combination_variants: list[set] = []

    def get_combinations_by_day(self, day_menu):
        day_combinations = set()
        for eating in list(day_menu):
            day_combinations.add(day_menu[eating].id)
        self.combinations.append(day_combinations)

    def get_possible_combination_variants(self):
        self.combination_variants.clear()
        for eating_category in self.left_dishes:
            left_dishes = list(self.left_dishes).copy()
            left_dishes.remove(eating_category)
            variants = (product
                        (*[list(self.left_dishes[dish_vars])
                           for dish_vars in left_dishes if self.left_dishes[dish_vars]]))
            for variant in variants:
                variant = set(variant)
                if variant not in self.combination_variants and len(variant) > 1:
                    self.combination_variants.append(variant)

    def get_dishes_to_use(self):
        valid_combinations = []
        for combination in self.combinations:
            for variant in self.combination_variants:
                if len(combination.intersection(variant)) <= 1:
                    valid_combinations.append(variant)
        if not valid_combinations:
            left_dishes = self.left_dishes.copy()
            while True:
                if not left_dishes:
                    dish_to_use = {
                        'breakfast': None,
                        'lunch': None,
                        'dinner': None
                    }
                    break
                random_eating = random.choice(list(left_dishes))
                if left_dishes[random_eating]:
                    dish_to_use = random.choice(list(self.left_dishes[random_eating]))
                    dish_to_use = {random_eating: dish_to_use}
                    break
                else:
                    left_dishes.pop(random_eating)
        else:
            dish_to_use = {}
            dtu = random.choice(valid_combinations)
            for dish in dtu:
                for eating in self.left_dishes:
                    dishes: dict | None = self.left_dishes.get(eating)
                    if dishes and dishes.get(dish):
                        dish_to_use[eating] = dish

        # print('d_t_u', d_t_u)
        dishes_to_use = {}
        not_can_be_together = True
        eatings_to_use = list(self.left_dishes)
        if len(list(self.left_dishes)) > 1:
            eating_except = random.choice(eatings_to_use)
            eatings_to_use.remove(eating_except)
        for eating in eatings_to_use:
            if self.left_dishes[eating]:
                dishes_to_use[eating] = random.choice(list(self.left_dishes[eating]))

        return dish_to_use

    def update_left_dishes(self, daily_menu: dict):
        for eating in daily_menu:
            try:
                if not self.left_dishes.get(eating) or (daily_menu[eating].id not in self.left_dishes[
                    eating].keys()  # проверить как работает это условие (проходят блюда где 2 порции)
                                                        and daily_menu[eating].portions_count > 2):
                    self.left_dishes[eating] = {daily_menu[eating].id: daily_menu[eating].portions_count - 2}
                elif self.left_dishes[eating][daily_menu[eating].id] <= 2:
                    self.left_dishes[eating].pop(daily_menu[eating].id)
                else:
                    self.left_dishes[eating][daily_menu[eating].id] -= 2
            except KeyError:
                pass

    def get_next_day_menu(self):
        dishes_to_use = self.get_dishes_to_use()
        if dishes_to_use:
            breakfast_to_use = dishes_to_use.get('breakfast', None)
            lunch_to_use = dishes_to_use.get('lunch', None)
            dinner_to_use = dishes_to_use.get('dinner', None)
        else:
            breakfast_to_use = None
            lunch_to_use = None
            dinner_to_use = None
        day_menu = DayMenu(breakfast_to_use_id=breakfast_to_use, dinner_to_use_id=dinner_to_use).day_menu_variants.get()
        daily_menu = {
            'breakfast': (Dish.select(Dish.id, Dish.dish_name, Dish.href, Dish.calories, Dish.portions_count)
                          .where(Dish.id == day_menu.id).get()),
            'lunch': (Dish.select(Dish.id, Dish.dish_name, Dish.href, Dish.calories, Dish.portions_count)
                      .where(Dish.id == day_menu.lunch_id).get()),
            'dinner': (Dish.select(Dish.id, Dish.dish_name, Dish.href, Dish.calories, Dish.portions_count)
                       .where(Dish.id == day_menu.dinner_id).get())
        }
        self.update_left_dishes(daily_menu=daily_menu)
        self.get_combinations_by_day(day_menu=daily_menu)
        self.get_possible_combination_variants()
        return daily_menu

    def week_menu(self):
        while len(self.menu) < 7:
            self.menu.append(self.get_next_day_menu())
            # self.is_can_be_together()

        return self.menu


class Eating:

    def __init__(self,
                 metabolism: int,
                 cooking_time: int = 30,
                 serving_size: int = 350,
                 hysteresis: float = 0.15,
                 part_from_daily_calories: float = 0.33,
                 category: str = None,
                 alias: str = None,
                 dish_to_use_id=None):
        self.dish_set: EatingSet | None = None
        self._high_hysteresis = 1 + hysteresis  # допуск отклонения калорий от целевого значения вверх
        self._low_hysteresis = 1 - hysteresis  # допуск отклонения калорий от целевого значения вниз
        self._serving_size = serving_size  # размер порции в г
        self._calories_needed = metabolism * part_from_daily_calories  # целевое количество калорий на один приём пищи
        self._cooking_time = cooking_time  # максимальное время готовки
        self._low_calories = self._calories_needed * self._low_hysteresis
        self._high_calories = self._calories_needed * self._high_hysteresis
        self._dish_to_use_id = dish_to_use_id
        if category is None:
            self._category = random.choice(['breakfast', 'second_dish', 'soup', 'salad', 'dessert', 'snack'])
        else:
            self._category = category
        self.dish = self.get_dish(category=self._category, alias=alias)

    def get_dish(self, category: str = None, alias: str = None, low_calories=None, high_calories=None, limit=100):
        """Функция забирает из БД варианты блюд, подходящих по указанным фильтрам"""
        if self._dish_to_use_id is not None:
            return (Dish.alias(alias).select(Dish.alias(alias).id,
                                             Dish.alias(alias).dish_name,
                                             Dish.alias(alias).href,
                                             Dish.alias(alias).calories)
                    .where(Dish.alias(alias).id == self._dish_to_use_id)
                    .alias(alias))
        if low_calories is None:
            low_calories = self._low_calories
        if high_calories is None:
            high_calories = self._high_calories
        if alias is None:
            alias = category
        calories_in_portion = (Dish.alias(alias)
                               .calories * self._serving_size) / 100  # делим на 100 т.к. калории для 100г блюда
        limitation = ((EatingTable.eating_name == category)
                      &
                      (calories_in_portion.between(low_calories, high_calories))
                      &
                      (Dish.alias(alias).active_cooking_time <= self._cooking_time)
                      &
                      (Dish.alias(alias).portions_count.between(2, 6)))
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
        soups_with_second_dishes = (Dish.select(Dish.id.alias('second_dish_id'),
                                                Dish.dish_name.alias('second_dish_name'),
                                                Dish.href.alias('second_dish_href'),
                                                soups.c.id.alias('soup_id'),
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

        dice = random.randint(1, 100)
        if dice > 0:
            return second_dishes_only
        return soups_with_second_dishes


def main() -> list[dict[str, Dish]]:
    week_menu = WeekMenu()
    wmenu = week_menu.week_menu()
    return wmenu


if __name__ == '__main__':
    for i in main():
        print(type(i['lunch']))
