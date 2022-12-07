from database.data_structure import User, Metabolism
from database.user_models import User as UserTable
from interface.console import get_user


def get_basic_metabolism(user: User) -> Metabolism:
    physical_activity_coefficients = {1: 1.2, 2: 1.375, 3: 1.4625, 4: 1.55, 5: 1.6375, 6: 1.725, 7: 1.9}
    k = 5 if user.gender else -161
    basic_metabolism = 10 * user.weight + 6.25 * user.height - 5 * user.age + k
    daily_metabolism = basic_metabolism * physical_activity_coefficients[user.physical_activity]
    metabolism = Metabolism(basic_metabolism=basic_metabolism, daily_metabolism=daily_metabolism)
    return metabolism


def fill_user():
    user = get_user()
    metabolism = get_basic_metabolism(user=user)
    UserTable.create(**user._asdict(), daily_metabolism=metabolism.daily_metabolism)


if __name__ == '__main__':
    fill_user()
