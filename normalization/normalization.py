import re
def get_minutes\
                (cooking_time: str) -> int:
    words = cooking_time.strip().split(' ')
    if len(words) == 2:
        if re.search('минут', words[-1]):
            return int(words[0])
        elif re.search('час', words[-1]):
            return int(words[0]) * 60
    elif len(words) == 4:
        return int(words[0]) * int(words[2])


def get_digital_ingredient_value(value: str, mul: int) -> float:
    try:
        value = value.strip()
        if value == '½':
            return 0.5 * mul
        elif value == '¼':
            return 0.25 * mul
        elif value == '1 ¼':
            return 1.25 * mul
        elif value == '1 ½':
            return 1.5 * mul
        try:
            return float(value) * mul
        except ValueError:
            digits = value.split('/')
            try:
                return round(float(digits[0].replace(',', '.')) / float(digits[1].replace(',', '.')), 2) * mul
            except IndexError:
                return float(value.replace(',', '.')) * mul
    except ValueError as err:
        print(err)


def types_normalization(starting_type: str) -> tuple[int, str]:
    if re.search(r'\sг\s', starting_type) or re.search(r'^г\s', starting_type.replace('.',' ')):
        return 1, 'г'
    if re.search(r'\sкг\s', starting_type) or re.search(r'^кг\s', starting_type.replace('.',' ')):
        return 1000, 'г'
    if re.search(r'\sмл\s', starting_type) or re.search(r'^мл\s', starting_type.replace('.',' ')):
        return 1, 'мл'
    if re.search(r'\sл\s', starting_type) or re.search(r'^л\s', starting_type.replace('.',' ')):
        return 1000, 'мл'
    return 1, starting_type


def ingredient_value(value: str, measure: str) -> tuple[float, str]:
    mul, new_type = types_normalization(measure.lower())
    value = get_digital_ingredient_value(value=value, mul=mul)
    return value, new_type


def get_ing_name(name: str) -> str:
    goods = {
        ('кальмары',): 'кальмар',
        ('крахмал',): 'крахмал картофельный',
        ('разрыхлитель теста',): 'разрыхлитель',
        ('сыр плавленный',): 'сыр плавленый',
        ('тортилья лепешка',): 'тортилья',
        ('цукини',): 'цуккини',
        ('яйцо', 'яйца'): 'яйцо куриное',
        ('персики',): 'персик',
        ('масло растительное',): 'масло подсолнечное',
        ('черные оливки',): 'маслины',
        ('макаронные изделия',): 'макароны',
        ('лук', 'лук-порей', 'лук красный', 'лук белый', 'лук-шалот'): 'лук репчатый',
        ('бульон или вода',): 'бульон',
        ('булка',): 'батон',
        ('базилик сушеный',): 'базилик'
    }
    bad_goods = []
    for good in goods:
        for i in good:
            bad_goods.append(i)
    if name not in bad_goods:
        return name
    for bg in goods:
        if name in bg:
            return goods[bg]