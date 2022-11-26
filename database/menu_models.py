import peewee
from peewee import SqliteDatabase, Model, CharField, IntegerField, ForeignKeyField, FloatField
from parsing.pars_menu import get_category_urls, get_dish_urls, Dish as DishObj


class BaseModel(Model):
    class Meta:
        database = SqliteDatabase(r'..\database\menu.db')


class Eating(BaseModel):
    eating_name = CharField()


class StoreDepartment(BaseModel):
    department_name = CharField(null=True)


class Dish(BaseModel):
    dish_name = CharField(unique=False)
    href = CharField(unique=True)
    total_cooking_time = IntegerField(null=True)
    active_cooking_time = IntegerField(null=True)


class Ingredient(BaseModel):
    ingredient_name = CharField(unique=True)
    protein_value = IntegerField(null=True)
    fats_value = IntegerField(null=True)
    carbohydrates_value = IntegerField(null=True)
    energy_value = IntegerField(null=True)
    department_name_id = ForeignKeyField(StoreDepartment, null=True)


class Recipe(BaseModel):
    dish_name_id = ForeignKeyField(Dish)
    ingredient_name_id = ForeignKeyField(Ingredient)
    quantity = FloatField()
    measure_unit = CharField(null=True)


class Weight(BaseModel):
    ingredient_id = ForeignKeyField(Ingredient)
    weight = FloatField(null=True)


Eating.create_table()
StoreDepartment.create_table()
Dish.create_table()
Ingredient.create_table()
Recipe.create_table()
Weight.create_table()


def create_ears():
    breakfast = Eating.create(eating_name='breakfast')
    second_dish = Eating.create(eating_name='second_dish')
    soup = Eating.create(eating_name='soup')

    bread = StoreDepartment.create(department_name='bread')
    confectionery = StoreDepartment.create(department_name='confectionery')
    milk = StoreDepartment.create(department_name='milk')
    vegetables = StoreDepartment.create(department_name='vegetables')
    fruits = StoreDepartment.create(department_name='fruits')
    meat = StoreDepartment.create(department_name='meat')
    spices = StoreDepartment.create(department_name='spices')
    fish = StoreDepartment.create(department_name='fish')
    grocery = StoreDepartment.create(department_name='grocery')
    preserves = StoreDepartment.create(department_name='preserves')
    nuts = StoreDepartment.create(department_name='nuts')


def fill_dish_table(dish: DishObj):
    try:
        Dish.create(**dish._asdict())
    except peewee.IntegrityError as er:
        print(er, dish.dish_name)


def main():
    url = get_category_urls()
    for dish in get_dish_urls(cat_urls=url):
        fill_dish_table(dish)


if __name__ == '__main__':
    main()
