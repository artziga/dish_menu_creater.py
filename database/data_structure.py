from typing import NamedTuple
from database.menu_models import Dish as DishTable

class Dish(NamedTuple):
    dish_name: str
    href: str
    total_cooking_time: int
    active_cooking_time: int


class DishPage(NamedTuple):
    url: str
    html: str


class Ingredient(NamedTuple):
    ingredient_name: str
    value: float
    measure_units: str | None
    note: str | None


class MeasureUnit(NamedTuple):
    multiplier: int
    unit: str
    note: str or None


class IngredientValue(NamedTuple):
    value: float
    measure_unit: str | None
    note: str | None


class DishInfo(NamedTuple):
    ingredients: list[Ingredient]
    portions_value: int | None
    categories: list[str]
    calories: int | None

class Nutrient(NamedTuple):
    name: str
    calories: int
    protein: float
    fats: float
    carbohydrates: float


class User(NamedTuple):
    name: str
    age: int
    weight: int
    height: int
    gender: bool
    physical_activity: int


class Metabolism(NamedTuple):
    basic_metabolism: float
    daily_metabolism: float


class EatingSet(NamedTuple):
    dish: DishTable
    second_dish: DishTable = None


class OnlyLunch(NamedTuple):
    dish: DishTable

