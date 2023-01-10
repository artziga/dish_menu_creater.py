from database.data_structure import User


def get_user() -> User:
    name = input('Введите ваше имя: ')
    age = int(input('Введите ваш возраст: '))
    gender = input('Выберите пол (М/Ж)').lower()
    while gender not in ['м', 'ж']:
        gender = input('Выберите пол (М/Ж)').lower()
    if gender == 'м':
        gender = True
    else:
        gender = False
    weight = int(input('Введите ваш вес: '))
    height = int(input('Введите ваш рост: '))
    physical_activity = int((input('Выберете уровень вашей физической активности, где:\n'
                                   '1 - Минимальные нагрузки (сидячая работа)\n'
                                   '2 - Необременительные тренировки 3 раза в неделю\n'
                                   '3 - Тренировки 5 раз в неделю (работа средней тяжести)\n'
                                   '4 - Интенсивные тренировки 5 раз в неделю\n'
                                   '5 - Ежедневные тренировки\n'
                                   '6 - Ежедневные интенсивные тренировки или занятия 2 раза в день\n'
                                   '7 - Тяжелая физическая работа или интенсивные тренировки 2 раза в день\n')))
    user = User(name=name,
                age=age,
                gender=gender,
                weight=weight,
                height=height,
                physical_activity=physical_activity
                )
    return user


if __name__ == '__main__':
    user = get_user()
    print(user)
