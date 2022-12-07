from peewee import SqliteDatabase, Model, CharField, IntegerField, ForeignKeyField, FloatField


class BaseModel(Model):
    class Meta:
        database = SqliteDatabase(r'..\database\menu.db')


class User(BaseModel):
    name = CharField(unique=True)
    age = IntegerField()
    weight = IntegerField()
    height = IntegerField()
    gender = IntegerField()
    physical_activity = IntegerField()
    daily_metabolism = FloatField()


User.create_table()
