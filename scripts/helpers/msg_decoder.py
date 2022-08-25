# import collections
# from ast import keyword
# from gc import collect
import json
# from operator import add
import re
# from tokenize import Number
# from unittest import result

raw_records_counter = 1

PHONES = []
PHONES_SET = {}

CATS = [
    ["Людина з інвалідністю", {"инвалид", "інвалід"}],
    ["Переселенці", {"переселенці", "впо"}],
    ["Багатодітна родина", {"многодетная", "багатодітна"}],
    ["Родини, що втратили годувальника",
     {"втратили годувальника"}],
    ["Один годувальник", {"один годувальник"}],
    ["Мати-одиначка", {"мама-одиночка", "мати-одиначка"}],
    ["Літні люди (75+)", {"літні люди (75+)"}],
    ["Пенсіонер", {"пенсіонер", "пенсионер"}]
]


def find_categories(t):
    if len(t) > 0:
        categories = []
        for cat in CATS:
            for word in cat[1]:
                if t.lower().__contains__(word):
                    categories.append(cat[0])
                    break
        return categories
    return []


def is_selfpick(t):
    """"""
    keywords = ["самовивіз", "самовывоз"]
    for word in keywords:
        if t.lower().__contains__(word):
            return True

    return False


def find_phone(t):
    phone = r'(\+?\d{12})|\d{10}'
    result = re.search(phone, t)

    """
    +380971525053
       0971525053
    """
    if result:
        r = result.group()
        if len(r) > 10:
            r = r[2:]
        return int(r)
    return None


def find_address(t):
    """
    Patterns:
        [See comments below]

        [Won't match]
            1-я Госпитальная, 18
            6 слободская, 5а, кв.19
    """

    """
        Too generic, so words like match as well, which is wrong.
        But too cool to be simply forgotten

        📫 вул. Лазурна, 50А
        📫 ул. Вільна, 58
        📫 ул. Велика Морська, 58
        вул. Фаліївська, 40
        пров. Зоряний, 13
        пер. Рейдовый 9А
        вулиця Металургів, 15
        ул. Московська 50 квартира 13
        Очаковская 15
        Заречная, 54
        Московська 55 квартира 12
        Озерна 1 А кв 17
        Крылова, 38 б, кв.3
        6 слободская, 5а, кв.19
        Варваровка улица Партизанская дом 41
        Мастерская, 60/3, кв. 2
        вул. Героїв України, 18 кв. 36
        Миколаїв, Курортна 19, 24
    """
    addr = r'\n(📫{1} ?)?([а-яїієґ]+)?,? ?(((в?ул.?)|(пров.?)|(пер.?)|(вулиця)|(улица)) ?)?(\d{1,2})? ?[а-яїієґ]+( ?[а-яїієґ]+)?,? ?\d{1,4}(\/\d{1,2})? ?[абвгд]?(,? ?(квартира|кв.?)? ?\d{1,4})?'
    result = re.search(addr, t, flags=re.IGNORECASE)

    """
        📫 вул. Лазурна, 50А
        📫 ул. Вільна, 58
        📫 ул. Велика Морська, 58
        вул. Фаліївська, 40
        пров. Зоряний, 13
        пер. Рейдовый 9А
        пр. Мира 9а
        Пр.Богоявленський  26-А
        вулиця Металургів, 15
        ул. Московська 50 квартира 13
        Варваровка улица Партизанская дом 41
        вул. Героїв України, 18 кв. 36
        ул. Арх. Старова, 6б кв65
    """
    # ул/вул is required
    # addr = r'\n(📫{1} ?)?([а-яїієґ]+)?,? ?(((в?ул.?)|(пров.?)|(пер.?)|(вулиця)|(улица)) ?)(\d{1,3})? ?[а-яїієґ]+( ?[а-яїієґ]+)?,? ?\d{1,3}(\/\d{1,2})? ?[абвгд]?(,? ?(квартира|кв.?)? ?\d{1,3})?'

    # without the first word
    addr = r'\n(📫{1} ?)?,? ?(((в?ул.?)|(пров.?)|(пер.?)|(пр.?)|(вулиця)|(улица)) ?)(\d{1,3})? ?[а-яїієґ]+\.?( ?[а-яїієґ]+)?,? {1,}?\d{1,3}(\/\d{1,2})?( |-)?[абвгд]?(,? ?(квартира|кв.?)? ?\d{1,3})?'
    result = re.search(addr, t, flags=re.IGNORECASE)

    if not result:
        """
            вулиця Металургів, 15
            Очаковская 15
            Заречная, 54
            Московська 55 квартира 12
            Озерна 1 А кв 17
            Крылова, 38 б, кв.3
            Мастерская, 60/3, кв. 2
            Миколаїв, Курортна 19, 24
            Потемкинська, 129в
        """
        # 143 chars
        addr = r'\n(📫{1} ?)?([а-яїієґ]+)?,? ?((\d{1,2}\bw)?(-[а|я])?) ?[а-яїієґ]+( ?[а-яїієґ]+)?,? ?\d{1,3}(\/\d{1,2})? ?[абвгд]?(,? ?(квартира|кв.?)? ?\d{1,3})?'
        result = re.search(addr, t, flags=re.IGNORECASE)

    if result:
        return result.group().replace("📫", "").lstrip()
    return None


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


ru = ["янв", "фев", "мар", "апр", "мая", "июн",
      "июл", "авг", "сен", "окт", "ноя", "дек"]
ua = ["січ", "лют", "бер", "квіт", "трав", "черв",
      "лип", "серп", "вер", "жов", "лист", "груд"]
_ua = ["січ", "лют", "бер", "кві", "тра", "чер",
       "лип", "сер", "вер", "жов", "лис", "гру"]


def parse_dob(t):
    """
    returns:
        str<DD Mon YYYY> || None
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

    return None


def find_dob(t):
    """
    Patterns:
        <UA occurances>
         17 липня 1941
         01лютого1947
         26 серпня1958
         22листопада 1930

        <RU occurances>
         17 мая 1941
         01февраля1947
         26 августа1958
         22ноября 1930

        <DD.MM.YYYY>
         01.09.1970

        <YYYY.DD.MM>
         1985.13.04

        <D.MM.YYYY>
         1.09.1970

        <YYYY.DD.MM>
         1985.13.04

        <YYYY>
         1970
    Returns:
        None or [1936, 01.09.1970, ...]
    """
    # 01.09.1970 <DD.MM.YYYY>
    dob = r'(0[1-9]|[12][0-9]|3[01])[- \..](0[1-9]|1[012])[- \..](19|20)\d\d'
    result = re.search(dob, t)

    if not result:
        # 1.09.1970 <D.MM.YYYY>
        dob = r'([1-9]|[12][0-9]|3[01])[- \..](0[1-9]|1[012])[- \..](19|20)\d\d'
        result = re.search(dob, t)

    if not result:
        # 1985.13.04 <YYYY.DD.MM>
        dob = r'(19|20)\d\d\.(0[1-9]|[12][0-9]|3[01]).(0[1-9]|1[012])'
        result = re.search(dob, t)

    if not result:
        # RU text date <DD M YYYY> or <DDMYYYY>
        """ 17 мая 1941
            01февраля1947
            26 августа1958
            22ноября 1930
        """
        dob = r'(0?[1-9]|[12][0-9]|3[01]) ?(янв(?:аря)?|фев(?:раля)?|мар(?:та)?|апр(?:еля)?|мая|июн(?:я)?|июл(?:я)?|авг(?:уста)?|сен(?:тября)?|окт(?:ября)?|ноя(?:бря)?|дек(?:абря)?) ?(19|20)\d\d'
        result = re.search(dob, t)

    if not result:
        # UA text date <DD MM YYYY> or <DDMMYYYY>
        """ 17 липня 1941
            01лютого1947
            26 серпня1958
            22листопада 1930
        """
        dob = r'(0?[1-9]|[12][0-9]|3[01]) ?(січ(:?ня)?|лют(?:ого)?|бер(?:езня)?|квіт(?:ня)?|трав(?:ня)?|черв(?:ня)?|лип(?:ня)?|серп(?:ня)?|вер(?:есня)?|жовт(?:ня)?|груд(?:ня)?|лист(?:опада)?) ?(19|20)\d\d'
        result = re.search(dob, msg)

    if not result:
        # 1970 <YYYY>
        dob = r'(19|20)\d\d'
        result = re.search(dob, msg)

    if result:
        return result.group()
    return None


def find_pib(text):
    """
        ПІБ

        В'юн В'ячеслав Дем'янович
        Урова Олена Михайлівна
        ГЛУХИХ АННА АЛЕКСЕЕВНА
        Заяц А.О
    """
    text = str(text)
    text = text.replace('Ё', 'Е')
    text = text.replace('ё', 'е')
    text = re.sub(r'\s+', ' ', text)  # removes double spaces
    name = None

    # ЇІЄҐ' їієґ'
    pattern = r"((\b[А-ЯЇІЄҐ][^А-ЯЇІЄҐ\s\.\,][а-яїієґ']*)(\s+)([А-ЯЇІЄҐ][а-яїієґ']*)(\.+\s*|\s+)([А-ЯЇІЄҐ][а-яїієґ']*))"

    name = re.findall(pattern, text)
    if name:
        PIB = name[0][0].replace('.', ' ')
        PIB = re.sub(r'\s+', ' ', PIB).split(' ')
        if len(PIB) >= 3:
            return PIB[0], PIB[1], PIB[2]
        elif len(PIB) == 2:
            return PIB[0], PIB[1], None
        elif len(PIB) == 1:
            return PIB[0], None, None
    else:
        return None, None, None


collection = []

with open("./channel_messages.json", encoding='utf-8') as f:
    data = json.load(f)

    i = 1
    for raw_msg in data:
        if i < len(data):
            if not raw_msg.get("message", None):
                continue

            collection_item = {}
            date = raw_msg.get("date", None)

            order_no = 0  # Number(0001)
            pib = ()  # ("P", "I", "B")
            bday = ""
            phone = None  # Number, 10 digits
            address = ""
            self_pickup = ""
            categories = []

            msg = raw_msg.get("message", None)
            if msg and len(msg) > 0:
                msg = msg.split("№")
                if len(msg) > 1:
                    msg = msg[1]

                idx = 0
                for char in msg:
                    if char.isnumeric():
                        idx = idx + 1
                    else:
                        order_no = msg[0: idx]
                        break

                for char in msg[idx:]:
                    if char != "\n":
                        idx = idx + 1
                    else:
                        idx = idx + 1
                        break

                msg = msg[idx:]  # goes to DB like this

                if len(msg) > 0:
                    pib = find_pib(msg)
                    bday = parse_dob(find_dob(msg))
                    phone = find_phone(msg)
                    PHONES.append(phone)
                    address = find_address(msg)
                    categories = find_categories(msg)
                    self_pickup = is_selfpick(msg)

                    collection_item["Date"] = date
                    collection_item["Num"] = i
                    collection_item["OrderNumber"] = int(
                        order_no) if order_no.isnumeric() else -1
                    collection_item["PIB"] = pib
                    collection_item["Bday"] = bday
                    print(order_no)
                    collection_item["Phone"] = phone
                    collection_item["Address"] = address
                    collection_item["Categories"] = categories
                    collection_item["SelfPickup"] = self_pickup
                    collection_item["RawMessage"] = msg

                    # print("Date 🗓:", date)
                    # print("№:", i)
                    # print("Order #:", order_no)
                    # print("PIB 🪪:", pib)
                    # print("B-day 🎂:", bday)
                    # print("Phone ☎️:", phone)
                    # print("Address 📫:", address)
                    # print("Categories 👨‍👩‍👧‍👦:", categories)
                    # print()
                    # print("Self Pickup 🛻:", "✅" if self_pickup else "⛔️")
                    # print("___________________")
                    # print()
                    # print(msg)
                    # print("___________________\n\n")

                    i = i + 1
                    collection.append(collection_item)
                else:
                    pass
                    # print("Rec #:", raw_records_counter)
                    # print(msg)
                    # exit(0)
            raw_records_counter = raw_records_counter + 1
        else:
            #     print("Усього оброблено:", raw_records_counter - 1, "заявок")
            break

with open("parsed_results.json", "w", encoding='utf8') as outfile:
    json.dump(collection, outfile, ensure_ascii=False)

    print("Усього оброблено:", raw_records_counter - 1, "заявок")

# print(len(PHONES))
# PHONES_SET = set(PHONES)
# print(len(PHONES_SET))

# duplicated phone numbers
# l = [item for item, count in collections.Counter(PHONES).items() if count > 1]
# for i in l:
#     print(i)
