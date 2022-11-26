def get_minutes(cooking_time: str) -> int:
    words = cooking_time.strip().split(' ')
    if len(words) == 2:
        if words[-1] in ['минута', 'минут', 'минуты']:
            return int(words[0])
        elif words[-1] in ['час', 'часов', 'часа']:
            return int(words[0]) * 60
    elif len(words) == 4:
        return int(words[0]) * int(words[2])


def get_float(value: str) -> float:
    try:
        value = value.strip()
        if value == '½':
            return 0.5
        elif value == '¼':
            return 0.25
        elif value == '1 ¼':
            return 1.25
        elif value == '1 ½':
            return 1.5
        try:
            return float(value)
        except ValueError:
            digits = value.split('/')
            try:
                return round(float(digits[0].replace(',', '.')) / float(digits[1].replace(',', '.')), 2)
            except IndexError:
                return float(value.replace(',', '.'))
    except ValueError:
        pass


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