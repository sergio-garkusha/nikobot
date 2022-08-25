import re

ru = ["янв", "фев", "мар", "апр", "мая", "июн",
      "июл", "авг", "сен", "окт", "ноя", "дек"]
ua = ["січ", "лют", "бер", "квіт", "трав", "черв",
      "лип", "серп", "вер", "жов", "лист", "груд"]
_ua = ["січ", "лют", "бер", "кві", "тра", "чер",
       "лип", "сер", "вер", "жов", "лис", "гру"]


def parse_year(t):
    """
    returns:
        str<YYYY> || False
    """
    y = r'\d{4}'
    y = re.search(y, t)
    if not y:
        return False
    y = y.group()
    # y = int(y) if y.is_numeric() else False
    if not y:
        return False

    return y


def parse_dob(t):
    """
    returns:
        str<DD Mon YYYY> || str<YYYY> || None
    """
    if not t:
        return None
    year = parse_year(t)
    if not year:
        return None

    t = t.split(year)

    for item in t:
        if not item:
            continue
        t = item
        break

    if t.__contains__('.'):
        # numeric
        t = t.strip().strip('.').split('.')

        if len(t) != 2:
            t = t[0].split(' ')

        day = int(t[0])
        mon = int(t[1])
        return f'{day} {ua[mon - 1]} {year}'
    else:
        # num + word || year only
        valid = set(t)
        if not valid.pop():
            # year only
            return f'{year}'

        num = r'\d{1,2}'
        num = re.search(num, t)
        if num:
            num = num.group()
        else:
            return None

        delim = len(num)
        day = int(t[:delim].strip())
        mon = t[delim:].strip()[:3]

        if mon in _ua:
            return f'{day} {ua[_ua.index(mon)]} {year}'
        if mon in ru:
            return f'{day} {ua[ru.index(mon)]} {year}'
