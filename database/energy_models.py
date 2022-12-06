from peewee import SqliteDatabase, Model, CharField, IntegerField, FloatField, IntegrityError
from parsing.pars_energy import pars_energy
from parsing.health import get_nutrients

db = SqliteDatabase(r'..\database\menu.db')


class Energy(Model):
    name = CharField(unique=True)
    protein = FloatField()
    fats = FloatField()
    carbohydrates = FloatField()
    calories = IntegerField()

    class Meta:
        database = db


Energy.create_table()


def fill_energy(energies):
    for en in energies:
        try:
            Energy.insert(en).execute()
        except IntegrityError:
            print(en)


if __name__ == '__main__':
    energies = get_nutrients()
    for energy in energies:
        fill_energy(energy)
