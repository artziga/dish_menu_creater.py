import re
from database.data_structure import MeasureUnit, IngredientValue


def get_minutes(cooking_time: str) -> int:
    words = cooking_time.strip().split(' ')
    if len(words) == 2:
        if re.search('минут', words[-1]):
            return int(words[0])
        elif re.search('час', words[-1]):
            return int(words[0]) * 60
    elif len(words) == 4:
        return int(words[0]) * int(words[2])


def get_digital_ingredient_value(value: str, mul: int) -> float | None:
    if value:
        value = value.replace(' ', '')
        if value in ['¼', r'1\4']:
            return 0.25 * mul
        elif value in ['1/3', '1/3-1/2']:
            return 0.33 * mul
        elif value in ['½', r'1\2', r'от 1/2', '1/2-1', ')0,5']:
            return 0.5 * mul
        elif value in ['¾']:
            return 0.75 * mul
        elif value in ['от1']:
            return 1 * mul
        elif value in ['1 ¼']:
            return 1.25 * mul
        elif value in ['1 1/3', '1\xa01/3']:
            return 1.33 * mul
        elif value in ['1 ½', '1 1/2', '1,3-1,6', '1½', '1и1/2']:
            return 1.5 * mul
        elif value == '1 3/4':
            return 1.75 * mul
        elif value in ['2 ½', '2½']:
            return 2.5 * mul
        elif value == '3 столовых ложки':
            return 3 * mul
        elif value == '3 1/2':
            return 3.5 * mul
        elif value == '4 1/2':
            return 4.5 * mul
        elif value == '2 2/3':
            return 2.66 * mul
        try:
            return float(value) * mul
        except ValueError:
            if r'\\' in value:
                digits = value.split(r'\\')
            else:
                digits = value.split('/')
            try:
                return round(float(digits[0].replace(',', '.')) / float(digits[1].replace(',', '.')), 2) * mul
            except IndexError:
                return float(value.replace(',', '.')) * mul
            except ValueError:
                return float(value.split('-')[0].replace(',', '.'))

    return None


def types_normalization(starting_type: str) -> MeasureUnit:
    match = re.search(r'(?P<g>(^|\s)гр?\.?\s)(?P<note>.*)', starting_type)
    if match:
        return MeasureUnit(multiplier=1, unit='г', note=match['note'])
    match = re.search(r'(?P<kg>(^|\s)кг\.?\s)(?P<note>.*)', starting_type)
    if match:
        return MeasureUnit(multiplier=1000, unit='г', note=match['note'])
    match = re.search(r'(?P<ml>(^|\s)мл\.?\s)(?P<note>.*)', starting_type)
    if match:
        return MeasureUnit(multiplier=1, unit='мл', note=match['note'])
    match = re.search(r'(?P<l>(^|\s)л\.?\s)(?P<note>.*)', starting_type)
    if match:
        return MeasureUnit(multiplier=1000, unit='мл', note=match['note'])
    match = re.search(r'(?P<some>(^|\s)\w\w\.\w?\.?\s)(?P<note>.*)', starting_type)
    if match:
        return MeasureUnit(multiplier=1, unit=match['some'], note=match['note'])
    return MeasureUnit(multiplier=1, unit=starting_type, note=None)


def ingredient_value(value: str, measure: str) -> IngredientValue:
    mul, new_type, note = types_normalization(measure.lower())
    value = get_digital_ingredient_value(value=value, mul=mul)
    if not value:
        value = new_type
        new_type = None
    return IngredientValue(value=value, measure_unit=new_type, note=note)


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
