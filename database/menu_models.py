from peewee import SqliteDatabase, Model, CharField, IntegerField, ForeignKeyField, FloatField


class BaseModel(Model):
    class Meta:
        database = SqliteDatabase(r'/home/zai/PycharmProjects/dish_menu_creater/database/menu.db')


class Eating(BaseModel):
    eating_name = CharField()


class StoreDepartment(BaseModel):
    department_name = CharField(null=True)


class Dish(Model):
    dish_name = CharField(unique=False)
    href = CharField(unique=True)
    photo = CharField(unique=False, null=True)
    total_cooking_time = IntegerField(null=True)
    active_cooking_time = IntegerField(null=True)
    portions_count = IntegerField(null=True)
    calories = IntegerField(null=True)

    class Meta:
        database = SqliteDatabase(r'/home/zai/PycharmProjects/dish_menu_creater/database/menu.db')
        alias = 'dishes'






class Tag(BaseModel):
    tag_name = CharField(unique=True)


class LnkDishTag(BaseModel):
    dish_name_id = ForeignKeyField(Dish)
    tag_name_id = ForeignKeyField(Tag)


class LnkEatingTag(BaseModel):
    eating_name_id = ForeignKeyField(Eating)
    tag_name_id = ForeignKeyField(Tag)


class Ingredient(BaseModel):
    ingredient_name = CharField(unique=True)
    protein_value = IntegerField(null=True)
    fats_value = IntegerField(null=True)
    carbohydrates_value = IntegerField(null=True)
    energy_value = IntegerField(null=True)
    department_name_id = ForeignKeyField(StoreDepartment, null=True)


class OldIngredient(Model):
    ingredient_name = CharField(unique=True)
    protein_value = IntegerField(null=True)
    fats_value = IntegerField(null=True)
    carbohydrates_value = IntegerField(null=True)
    energy_value = IntegerField(null=True)
    department_name_id = ForeignKeyField(StoreDepartment, null=True)

    class Meta:
        database = SqliteDatabase(r'/home/zai/PycharmProjects/dish_menu_creater/database/архив/menu.db')
        table_name = 'ingredient'


class Recipe(BaseModel):
    dish_name_id = ForeignKeyField(Dish)
    ingredient_name_id = ForeignKeyField(Ingredient)
    quantity = FloatField()
    measure_unit = CharField(null=True)
    note = CharField(null=True)


class Weight(BaseModel):
    ingredient_id = ForeignKeyField(Ingredient)
    weight = FloatField(null=True)


class OldWeight(BaseModel):
    ingredient_id = ForeignKeyField(OldIngredient)
    weight = FloatField(null=True)

    class Meta:
        database = SqliteDatabase(r'/home/zai/PycharmProjects/dish_menu_creater/database/архив/menu.db')
        table_name = 'weight'


database = SqliteDatabase('/home/zai/PycharmProjects/food_site/foodsite/db.sqlite3')

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel1(Model):
    class Meta:
        database = database



class FoodDish(BaseModel1):
    active_cooking_time = IntegerField(null=True)
    calories = IntegerField(null=True)
    dish_name = CharField()
    photo = CharField(null=True)
    href = CharField(unique=True)
    portions_count = IntegerField(null=True)
    total_cooking_time = IntegerField(null=True)

    class Meta:
        table_name = 'food_dish'

class FoodTag(BaseModel1):
    tag_name = CharField(unique=True)

    class Meta:
        table_name = 'food_tag'

class FoodDishTags(BaseModel1):
    dish = ForeignKeyField(column_name='dish_id', field='id', model=FoodDish)
    tag = ForeignKeyField(column_name='tag_id', field='id', model=FoodTag)

    class Meta:
        table_name = 'food_dish_tags'
        indexes = (
            (('dish', 'tag'), True),
        )

class FoodStoredepartment(BaseModel1):
    department_name = CharField(null=True)

    class Meta:
        table_name = 'food_storedepartment'

class FoodIngredient(BaseModel1):
    carbohydrates_value = IntegerField(null=True)
    department = ForeignKeyField(column_name='department_id', field='id', model=FoodStoredepartment, null=True)
    energy_value = IntegerField(null=True)
    fats_value = IntegerField(null=True)
    ingredient_name = CharField(unique=True)
    protein_value = IntegerField(null=True)

    class Meta:
        table_name = 'food_ingredient'

class FoodMeal(BaseModel1):
    meal_name = CharField()

    class Meta:
        table_name = 'food_meal'

class FoodRecipe(BaseModel1):
    dish = ForeignKeyField(column_name='dish_id', field='id', model=FoodDish)
    ingredient_id = ForeignKeyField(column_name='ingredient_id', field='id', model=FoodIngredient)
    measure_unit = CharField(null=True)
    note = CharField(null=True)
    quantity = FloatField()

    class Meta:
        table_name = 'food_recipe'


class FoodTagMeal(BaseModel1):
    meal = ForeignKeyField(column_name='meal_id', field='id', model=FoodMeal)
    tag = ForeignKeyField(column_name='tag_id', field='id', model=FoodTag)

    class Meta:
        table_name = 'food_tag_meal'
        indexes = (
            (('tag', 'meal'), True),
        )

class FoodWeight(BaseModel1):
    ingredient = ForeignKeyField(column_name='ingredient_id', field='id', model=FoodIngredient)
    weight = FloatField(null=True)

    class Meta:
        table_name = 'food_weight'



# Eating.create_table()
# StoreDepartment.create_table()
# Dish.create_table()
# Ingredient.create_table()
# Recipe.create_table()
# Weight.create_table()
# Tag.create_table()
# LnkDishTag.create_table()
# LnkEatingTag.create_table()


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


def migrate_dish():
    table1 = Dish.select().dicts()
    table2 = FoodDish
    for dish in table1:
        table2.create(**dish)


def migrate_ingridients():
    table1 = Ingredient.select().dicts()
    table2 = FoodIngredient
    for dish in table1:
        # dish['dish_id'] = dish.pop('dish_name_id')
        # dish['tag_id'] = dish.pop('tag_name_id')
        print(dish)
        table2.create(**dish)


def migrate_recipe():
    table1 = Recipe.select().dicts()
    table2 = FoodRecipe
    for dish in table1:
        dish['dish_id'] = dish.pop('dish_name_id')
        dish['ingredient_id'] = dish.pop('ingredient_name_id')
        table2.create(**dish)


def migrate_tags():
    table1 = Tag.select().dicts()
    table2 = FoodTag
    for dish in table1:
        # dish['dish_id'] = dish.pop('dish_name_id')
        # dish['tag_id'] = dish.pop('tag_name_id')
        # print(dish.id)
        table2.create(**dish)


def migrate_dish_tags():
    table1 = LnkDishTag.select().dicts()
    table2 = FoodDishTags
    for dish in table1:
        print(dish)
        dish['dish_id'] = dish.pop('dish_name_id')
        dish['tag_id'] = dish.pop('tag_name_id')
        table2.create(**dish)


def make_migration():
    # migrate_dish()
    # migrate_ingridients()
    migrate_recipe()
    # migrate_dish_tags()
    # migrate_dish_tags()


def main():
    make_migration()


if __name__ == '__main__':
    make_migration()
    # Eating.create(eating_name='breakfast')
    # Eating.create(eating_name='second_dish')
    # Eating.create(eating_name='soup')
    # Eating.create(eating_name='salad')
    # Eating.create(eating_name='dessert')


