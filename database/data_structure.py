from typing import NamedTuple


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

