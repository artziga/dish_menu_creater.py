from peewee import SqliteDatabase, Model, CharField, IntegerField, FloatField
from parsing.pars_energy import pars_energy

db = SqliteDatabase(r'..\database\menu.db')


class Energy(Model):
    name = CharField(unique=True)
    prot = FloatField()
    fats = FloatField()
    carbohydrates = FloatField()
    calories = IntegerField()

    class Meta:
        database = db


Energy.create_table()


def get_energy():
    for en in pars_energy():
        Energy.insert(en).execute()


if __name__ == '__main__':
    get_energy()