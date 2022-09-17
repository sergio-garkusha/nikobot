import configparser
from datetime import datetime
import pytz
import traceback
import re
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from pymongo import DESCENDING, MongoClient
from pymongo.server_api import ServerApi

from src.helpers.auth import is_permitted
from src.helpers.bday import parse_dob
from src.helpers.msg_parser import parse_msg_for_record
from src.helpers.project_root import project_root

"""
[Commands]:

start - Знайомство
create_order - Створити заявку
find_by_phone - Шукати за номером телефону
find_by_name - Шукати за ім'ям
find_by_dob - Шукати за датою народження
find_by_address - Шукати за адресою
find_by_order - Шукати за номером заяви
help - Докладний перелік можливостей
"""

TOKEN = None
DB = None

STATE = 0

ORD_NUM = 5
NAME = 10
PHONE = 20
DOB = 30
ADDRESS = 40
CREATE = 50


def reset_state():
    global STATE
    STATE = None


def find_by_order(update, context):
    global STATE
    user = update.message.chat.username
    if is_permitted(user):
        STATE = ORD_NUM
        update.message.reply_text("Введіть номер заяви:")


def find_by_phone(update, context):
    global STATE
    user = update.message.chat.username
    if is_permitted(user):
        STATE = PHONE
        update.message.reply_text("Введіть номер телефону:")


def find_by_dob(update, context):
    global STATE
    user = update.message.chat.username
    if is_permitted(user):
        STATE = DOB
        update.message.reply_text("Введіть дату народження:")


def find_by_name(update, context):
    global STATE
    user = update.message.chat.username
    if is_permitted(user):
        STATE = NAME
        update.message.reply_text("Введіть ім'я:")


def find_by_address(update, context):
    global STATE
    user = update.message.chat.username
    if is_permitted(user):
        STATE = ADDRESS
        update.message.reply_text("Введіть адресу:")


def create_order(update, context):
    global STATE
    user = update.message.chat.username
    if is_permitted(user):
        STATE = CREATE
        update.message.reply_text("Введіть заявку, ось вам шаблон:")
        update.message.reply_text(
            f"#️⃣ Нумер\n"
            + "👤 Ім'ячко\n"
            + "🎈 Хеппібьоздей\n"
            + "📫 Домівка\n"
            + "📲 Телехвончик\n"
            + "👵🏻 Категорія громадян\n"
            + "🚗 Самовивіз (як є)\n\n"
            + "=== Тіло Заявки ===")
        update.message.reply_text(
            "Копіюємо шаблон, редагуємо його, надсилаємо мені готову сюди")
        update.message.reply_text(
            f'Якщо заявка збереглася\n'
            + 'копіюємо її до каналу\n'
            + '🚑 Задачи NikoVolunteers')


def reply_for_search(reply, **kvargs):
    reply(
        f"#️⃣ {kvargs['num']}\n"
        + f"👤 {kvargs['name']}\n"
        + f"🎈 {kvargs['bday']}\n"
        + f"📫 {kvargs['addr']}\n"
        + f"📲 {kvargs['phone']}\n"
        + f"👵🏻 {kvargs['cats']}\n\n"
        + f"=== «Сира» Заявка ===\n\n"
        + f"```\n{kvargs['msg']}```")


def get_ordnum(num):
    query = DB.orders.find({"OrderNumber": num}).sort("Date", DESCENDING)
    try:
        query = query.next()
    except:
        pass
    return query


def get_phone(phone):
    query = DB.orders.find({"Phone": phone}).sort("Date", DESCENDING)
    try:
        query = query.next()
    except:
        pass
    return query


def get_dob(bday):
    query = DB.orders.find({"Bday": bday}).sort("Date", DESCENDING)
    try:
        query = query.next()
    except:
        pass
    return query


def get_address(addr):
    query = DB.orders.find(
        {"Address": {"$regex": re.compile(f'{addr}', re.I)}}).sort("Date", DESCENDING)
    try:
        query = query.next()
    except:
        pass
    return query


def get_name(name):
    query = DB.orders.find({"PIB": {"$all": name}}).sort("Date", DESCENDING)
    try:
        query = query.next()
    except:
        pass
    return query


def compute_date_delta(date):
    # EET  - Estern European Time
    # EEST - summertime, can be ignore since we care only about days
    UATZ = pytz.timezone('EET')

    today = datetime.now(UATZ)
    date = datetime.fromisoformat(date)
    delta = today - date

    return delta.days


def received_address(update, context):
    try:
        addr = update.message.text.strip()
        recs_qty = DB.orders.count_documents(
            {"Address": {"$regex": re.compile(f'{addr}', re.I)}})

        if recs_qty:
            res = get_address(addr)
            num = res["OrderNumber"]
            name = ' '.join(res["PIB"])
            bday = res["Bday"]
            addr = res["Address"]
            msg = res["RawMessage"]
            delt = compute_date_delta(res["Date"])
            phone = '0' + str(res["Phone"])

            cats = ' '.join(res["Categories"]) if len(
                res["Categories"]) > 0 else None

            if recs_qty > 1:
                update.message.reply_text(f"Всього заявок: {recs_qty}")
            if recs_qty > 9:
                update.message.reply_text(f"⚠️ Занадто загальний запрос ⚠️")
            update.message.reply_text(f"Днів з останньої заявки: {delt}")
            reply_for_search(update.message.reply_markdown,
                             num=num, name=name, bday=bday,
                             addr=addr, phone=phone, cats=cats,
                             msg=msg)
            reset_state()
        else:
            update.message.reply_text(f"Записів немає")
    except Exception as e:
        update.message.reply_text("Невірний формат імені")
        print(f"\n{e}")
        traceback.print_exc()


def received_name(update, context):
    try:
        name = update.message.text.strip()
        if name.__contains__("‘"):
            name = name.replace("‘", "'")
        name = name.split(' ')
        length = len(name)

        q = [""]
        if length == 1:  # Last name
            # DB.orders.find({"PIB": {$all: ["Сочоран"]}}).pretty()
            q = [f"{name[0]}"]
        elif length == 2:  # First name + Last name
            # DB.orders.find({"PIB": {$all: ["Сочоран", "Владимир"]}}).pretty()
            q = [f"{name[0]}", f"{name[1]}"]
        elif length == 3:  # First name + Last name + Father's name
            # DB.orders.find({"PIB": {$all: ["Сочоран", "Владимир", "Индигович"]}}).pretty()
            q = [f"{name[0]}", f"{name[1]}", f"{name[2]}"]

        recs_qty = DB.orders.count_documents({"PIB": {"$all": q}})

        if recs_qty:
            res = get_name(q)
            num = res["OrderNumber"]
            name = ' '.join(res["PIB"])
            bday = res["Bday"]
            addr = res["Address"]
            msg = res["RawMessage"]
            delt = compute_date_delta(res["Date"])
            phone = '0' + str(res["Phone"])

            cats = ' '.join(res["Categories"]) if len(
                res["Categories"]) > 0 else None

            if recs_qty > 1:
                update.message.reply_text(f"Всього заявок: {recs_qty}")
            update.message.reply_text(
                f"Днів з останньої заявки: {delt}")
            reply_for_search(update.message.reply_markdown,
                             num=num, name=name, bday=bday,
                             addr=addr, phone=phone, cats=cats,
                             msg=msg)
            reset_state()
        else:
            update.message.reply_text(f"Записів немає")
    except Exception as e:
        update.message.reply_text("Невірний формат імені")
        print(f"\n{e}")
        traceback.print_exc()


def received_dob(update, context):
    try:
        bday = parse_dob(update.message.text.strip())
        recs_qty = DB.orders.count_documents({"Bday": bday})

        if recs_qty:
            rec = get_dob(bday)
            num = rec["OrderNumber"]
            name = ' '.join(word for word in rec["PIB"] if type(word) == str)
            bday = rec["Bday"]
            addr = rec["Address"]
            msg = rec["RawMessage"]
            delt = compute_date_delta(rec["Date"])
            phone = '0' + str(rec["Phone"])

            cats = ' '.join(rec["Categories"]) if len(
                rec["Categories"]) > 0 else None

            if recs_qty > 1:
                update.message.reply_text(f"Всього заявок: {recs_qty}")
            update.message.reply_text(
                f"Днів з останньої заявки: {delt}")
            reply_for_search(update.message.reply_markdown,
                             num=num, name=name, bday=bday,
                             addr=addr, phone=phone, cats=cats,
                             msg=msg)
            reset_state()
        else:
            update.message.reply_text(f"Записів немає")
    except Exception as e:
        update.message.reply_text("Невірний формат дати")
        print(f"\n{e}")
        traceback.print_exc()


def received_create(update, context):
    try:
        to_record = parse_msg_for_record(update.message)
        recorded = DB.orders.insert_one(to_record)

        if recorded and recorded.inserted_id:
            update.message.reply_text(f"Успішно збережено!")
            update.message.reply_text(
                f'Можна копіювати до каналу\n'
                + '🚑 Задачи NikoVolunteers')
            reset_state()
        else:
            update.message.reply_text(f"Заявку неможливо зберегти :(")
    except Exception as e:
        update.message.reply_text("Щось пішло не так :(")
        print(f"\n{e}")
        traceback.print_exc()


def received_ordnum(update, context):
    try:
        patt = r'\d*'
        num = update.message.text.strip()
        num = re.search(patt, num)
        num = num.group() if num else None

        if not num:
            update.message.reply_text("Помилка вводу")
            return

        print(num)
        recs_qty = DB.orders.count_documents({"OrderNumber": int(num)})
        if recs_qty:
            rec = get_ordnum(int(num))

            num = rec["OrderNumber"]
            name = ' '.join(word for word in rec["PIB"] if type(word) == str)
            bday = rec["Bday"]
            addr = rec["Address"]
            msg = rec["RawMessage"]
            delt = compute_date_delta(rec["Date"])
            phone = '0' + str(rec["Phone"])

            cats = ' '.join(rec["Categories"]) if len(
                rec["Categories"]) > 0 else None

            if recs_qty > 1:
                update.message.reply_text(f"Всього заявок: {recs_qty}")
            update.message.reply_text(
                f"Днів з останньої заявки: {delt}")
            reply_for_search(update.message.reply_markdown,
                             num=num, name=name, bday=bday,
                             addr=addr, phone=phone, cats=cats,
                             msg=msg)
            reset_state()
        else:
            update.message.reply_text("Записів немає")
    except Exception as e:
        update.message.reply_text("Невірно введений номер")
        print(f"\nPhone exception: {e}")
        traceback.print_exc()


def received_phone(update, context):
    try:
        # 097 262 31 68  # 10 digits, starts with 0
        phone = update.message.text.strip()
        phone = ''.join(e for e in phone if e.isnumeric())
        phone = phone[2:] if len(phone) == 12 else phone
        patt = r'\d{9,10}'
        phone = re.search(patt, phone)
        phone = phone.group() if phone else None

        if not phone:
            update.message.reply_text("Помилка вводу")
            return

        recs_qty = DB.orders.count_documents({"Phone": int(phone)})
        if recs_qty:
            rec = get_phone(int(phone))

            num = rec["OrderNumber"]
            name = ' '.join(word for word in rec["PIB"] if type(word) == str)
            bday = rec["Bday"]
            addr = rec["Address"]
            msg = rec["RawMessage"]
            delt = compute_date_delta(rec["Date"])
            phone = '0' + str(rec["Phone"])

            cats = ' '.join(rec["Categories"]) if len(
                rec["Categories"]) > 0 else None

            if recs_qty > 1:
                update.message.reply_text(f"Всього заявок: {recs_qty}")
            update.message.reply_text(
                f"Днів з останньої заявки: {delt}")
            reply_for_search(update.message.reply_markdown,
                             num=num, name=name, bday=bday,
                             addr=addr, phone=phone, cats=cats,
                             msg=msg)
            reset_state()
        else:
            update.message.reply_text("Записів немає")
    except Exception as e:
        update.message.reply_text("Невірно введений номер")
        print(f"\nPhone exception: {e}")
        traceback.print_exc()


def start(update, context):
    # function to handle the /start command
    user = update.message.chat.username
    if is_permitted(user):
        first_name = update.message.chat.first_name
        update.message.reply_text(
            f"Вітаю {first_name}, я @nikovolunteerbot!\n"
            + "(a-ka Adjutant)\n"
            + "Твій персональний помічник.\n")
        update.message.reply_text(
            "Я вмію шукати заявки за критеріями.\n"
            + "А також допомагати тобі в їх створенні.")
        update.message.reply_text(
            "Використовуй меню зліва\n"
            + "щоб обрати команду зі списку.")
        update.message.reply_text(
            "Або обирай /help для продовження знайомства.")
    else:
        update.message.reply_text("Я той що автоматизує.\n"
                                  + "Нехай Щастить!")


def help(update, context):
    # function to handle the /help command
    user = update.message.chat.username
    if is_permitted(user):
        update.message.reply_text(f"Ось що я вмію:\n\n"
                                  + f"/start - Знайомство\n"
                                  + f"/create_order - Створити заявку\n"
                                  + f"/find_by_phone - Шукати за номером телефону\n"
                                  + f"/find_by_name - Шукати за ім'ям\n"
                                  + f"/find_by_dob - Шукати за датою народження\n"
                                  + f"/find_by_address - Шукати за адресою\n"
                                  + "/find_by_order - Шукати за номером заяви\n"
                                  + f"/help - Докладний перелік можливостей")
        update.message.reply_text("/find_by_phone - Пошук за номером телефону\n\n"
                                  + "Номер наступного вигляду: 0972623168\n"
                                  + "UPD: тепер в будь-якому форматі\n\n"
                                  + "Варіанти запросів: \n\n"
                                  + "+380 (97) 262 31 68\n"
                                  + "+38097 262 31 68\n"
                                  + "+380972623168\n"
                                  + "0972623168\n"
                                  + "972623168\n"
                                  + "Номери в інших форматах неприпустимі.")
        update.message.reply_text("/find_by_name - Пошук за ім'ям\n\n"
                                  + "Варіанти запросів:\n\n"
                                  + "За прізвищем:\n"
                                  + "      В'юн\n\n"
                                  + "За прізвищем та ім'ям:\n"
                                  + "      В'юн В'ячеслав\n\n"
                                  + "За повним ім'ям:\n"
                                  + "      В'юн В'ячеслав Дем'янович\n\n"
                                  + "За ім'ям та по-батькові (можливі співпадіння):\n"
                                  + "      В'ячеслав Дем'янович\n\n"
                                  + "В майбутньому будуть і часткові імена, наприклад:\n\n"
                                  + "Захарч Волод Олекс або В'юн В Д")
        update.message.reply_text("/find_by_dob - Пошук за датою народження\n\n"
                                  + "Формат: число місяць рік\n\n"
                                  + "Варіанти запросів:\n\n"
                                  + "21.10.1962\n"
                                  + "21 жов 1962\n"
                                  + "21 жов 1962\n"
                                  + "21 окт 1962\n"
                                  + "21 октября 1962\n")
        update.message.reply_text("/find_by_address - Пошук за адресою\n\n"
                                  + "Найскладніший вид пошуку\n\n"
                                  + "На сьогодні він вміє шукати за точними адресами:\n"
                                  + "так, як вони були записані в заявках.\n\n"
                                  + "В майбутньому буде реалізовано більш гнучкий варіант.\n\n"
                                  + "Варіанти запросів:\n\n"
                                  + "Крилова\n"
                                  + "Крилова 12\n"
                                  + "Крилова, 12\n")
        update.message.reply_text("/find_by_order - Шукати за номером заяви\n\n"
                                  + "Варіант запросу:\n\n"
                                  + "5111\n")
        update.message.reply_text("/create_order - Механізм створення та збереження заявок\n\n"
                                  + "Надважливо зберігати заявки в базу!!!\n")
    else:
        update.message.reply_text("Допомога вже близько.\n"
                                  + "Нехай Щастить!")


def error(update, context):
    # function to handle errors occured in the dispatcher
    update.message.reply_text('Якась невідома хрєнь')


def text_handler(update, context):
    # function to handle normal text
    global STATE
    user = update.message.chat.username
    if is_permitted(user):
        if STATE == ORD_NUM:
            return received_ordnum(update, context)

        if STATE == PHONE:
            return received_phone(update, context)

        if STATE == DOB:
            return received_dob(update, context)

        if STATE == NAME:
            return received_name(update, context)

        if STATE == ADDRESS:
            return received_address(update, context)

        if STATE == CREATE:
            return received_create(update, context)
    else:
        update.message.reply_text("Ви не авторизовані")


def main():
    global CONFIG
    global DB

    config = configparser.ConfigParser()
    config.read(f"{project_root()}/../.nikobot.ini")
    CONFIG = config["NikoBot"]
    TOKEN = CONFIG["TOKEN"]
    mongodb = CONFIG["mongodb"]
    cert = CONFIG["cert"]

    # create the updater, that will automatically create also a dispatcher and a queue to
    # make them dialoge
    updater = Updater(TOKEN, use_context=True)
    # BOT = updater.bot
    dispatcher = updater.dispatcher

    # os = platform.system()
    with MongoClient(mongodb,
                     tls=True,
                     tlsCertificateKeyFile=cert,
                     server_api=ServerApi('1')) as client:
        DB = client.nikovolunteers

        # handlers for start and help commands
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", help))

        # handlers for search commands
        dispatcher.add_handler(CommandHandler("find_by_name", find_by_name))
        dispatcher.add_handler(CommandHandler(
            "find_by_order", find_by_order))
        dispatcher.add_handler(CommandHandler("find_by_phone", find_by_phone))
        dispatcher.add_handler(CommandHandler("find_by_dob", find_by_dob))
        dispatcher.add_handler(CommandHandler(
            "find_by_address", find_by_address))

        # handler for save command
        dispatcher.add_handler(CommandHandler("create_order", create_order))

        # handler for normal text (not commands)
        dispatcher.add_handler(MessageHandler(Filters.text, text_handler))

        # handler for errors
        dispatcher.add_error_handler(error)

        # start your shiny new bot
        updater.start_polling()

        # run the bot until Ctrl-C
        updater.idle()


if __name__ == '__main__':
    main()
