import configparser
from datetime import datetime
from src.helpers.bday import parse_dob
import pytz
import traceback
import re
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from pymongo import MongoClient

"""
[Commands]:

start - Знайомство
save_order - Створити заявку
find_by_phone - Шукати за номером телефону
find_by_name - Шукати за ім'ям
find_by_dob - Шукати за датою народження
find_by_address - Шукати за адресою
help - Докладний перелік можливостей

[@TODO]:

    0. !!!!! Check that user belongs to NikoVoluneers !!!!!

    Search by address is far from ideal based on data we have.
    So it is most realistic to search by street names with $regex.
    That will generate many results (20 +)
    
    1. Create mechanism for this < Вулиця + 16 + кв 5 >
        1. Searches within prev results
            result = search (Вулиця):
                        # narrower
                        search (16):
                            # narrower
                            search (кв 5):
                                # exact
        2. OR Add InlineKeyboard to create choosable address cards
            a) Update to latest version:
               pip install python-telegram-bot==v20.0a2
            b) Revrite the WHOLE APP accordingly :(
    2. Add search by name chunks, e.g. Захарче Володим Алекс
    3. Add CANCEL
    ...
    7. PROFIT!!!111
"""

STATE = 0
NAME = 10
PHONE = 20
DOB = 30
ADDRESS = 40
SAVE = 50


def reset_state():
    global STATE
    STATE = None


client = MongoClient("mongodb://localhost:27017")
db = client.nikovolunteers


def find_by_phone(update, context):
    global STATE
    STATE = PHONE
    update.message.reply_text("Введіть номер телефону:")


def find_by_dob(update, context):
    global STATE
    STATE = DOB
    update.message.reply_text("Введіть дату народження:")


def find_by_name(update, context):
    global STATE
    STATE = NAME
    update.message.reply_text("Введіть ім'я:")


def find_by_address(update, context):
    global STATE
    STATE = ADDRESS
    update.message.reply_text("Введіть адресу:")


def save_order(update, context):
    global STATE
    STATE = SAVE
    update.message.reply_text("Введіть заявку, ось вам шаблон:")
    update.message.reply_text(
        f"👤 Ім'ячко\n🎈 Хеппібьоздей\n📫 Домівка\n📲 Телехвончик\n👨‍👩‍👧‍👦 Категорія громадян\n\n=== Тіло Заявки ===")
    update.message.reply_text(
        "Копіюємо шаблон, редагуємо його, надсилаємо готове мені")
    update.message.reply_text(
        "Я скажу чи заявка збереглася успішно\nПересилай ії до каналу Задач")


def get_phone(phone):
    query = db.orders.find({"Phone": phone})
    query = query.next()
    print(query)
    return query


def get_dob(bday):
    query = db.orders.find({"Bday": bday})
    query = query.next()
    print(query)
    return query


def get_address(addr):
    query = db.orders.find(
        {"Address": {"$regex": re.compile(f'{addr}', re.I)}})
    while True:
        try:
            query = query.next()
        except:
            break
    print(query)
    return query


def get_name(name):
    query = db.orders.find({"PIB": {"$all": name}})
    while True:
        try:
            query = query.next()
        except:
            break
    print(query)
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
        recs_qty = db.orders.count_documents(
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
            update.message.reply_text(
                f"Заявка № {num}\nДнів з останньої заявки: {delt}")
            update.message.reply_text(
                f"👤 {name}\n🎈 {bday}\n📫 {addr}\n📲 {phone}\n👨‍👩‍👧‍👦 {cats}")
            update.message.reply_markdown_v2(f"```\n{msg}```")
            reset_state()
        else:
            update.message.reply_text(f"Записів немає")
    except Exception as e:
        update.message.reply_text("Невірний формат імені")
        print(f"\n{e}")


def received_name(update, context):
    try:
        name = update.message.text.strip()
        name = name.split(' ')
        length = len(name)

        if length == 1:  # Last name
            # db.orders.find({"PIB": {$all: ["Сорочан"]}}).pretty()
            q = [f"{name[0]}"]
        elif length == 2:  # First name + Last name
            # db.orders.find({"PIB": {$all: ["Сорочан", "Владимир"]}}).pretty()
            q = [f"{name[0]}", f"{name[1]}"]
        elif length == 3:  # First name + Last name + Father's name
            # db.orders.find({"PIB": {$all: ["Сорочан", "Владимир", "Васильевич"]}}).pretty()
            q = [f"{name[0]}", f"{name[1]}", f"{name[2]}"]

        recs_qty = db.orders.count_documents({"PIB": {"$all": q}})

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
                f"Заявка № {num}\nДнів з останньої заявки: {delt}")
            update.message.reply_text(
                f"👤 {name}\n🎈 {bday}\n📫 {addr}\n📲 {phone}\n👨‍👩‍👧‍👦 {cats}")
            update.message.reply_markdown_v2(f"```\n{msg}```")
            reset_state()
        else:
            update.message.reply_text(f"Записів немає")
    except Exception as e:
        update.message.reply_text("Невірний формат імені")
        print(f"\n{e}")


def received_dob(update, context):
    try:
        bday = parse_dob(update.message.text.strip())
        recs_qty = db.orders.count_documents({"Bday": bday})

        if recs_qty:
            rec = get_dob(bday)
            num = rec["OrderNumber"]
            name = ' '.join(rec["PIB"])
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
                f"Заявка № {num}\nДнів з останньої заявки: {delt}")
            update.message.reply_text(
                f"👤 {name}\n🎈 {bday}\n📫 {addr}\n📲 {phone}\n👨‍👩‍👧‍👦 {cats}")
            update.message.reply_markdown_v2(f"```\n{msg}```")
            reset_state()
        else:
            update.message.reply_text(f"Записів немає")
    except Exception as e:
        update.message.reply_text("Невірний формат дати")
        print(f"\n{e}")


def received_save(update, context):
    try:
        update.message.reply_text(
            "Ще в розробці, спробуй пошук - він спрощує життя вже сьогодні")
        reset_state()
    except Exception as e:
        update.message.reply_text("Щось пішло не так :(")
        print(f"\n{e}")


def received_phone(update, context):
    try:
        # 097 262 31 68  # 10 digits, starts with 0
        patt = r'\d{9,10}'
        phone = update.message.text.strip()
        phone = re.search(patt, phone).group()

        recs_qty = db.orders.count_documents({"Phone": int(phone)})
        if recs_qty:
            rec = get_phone(int(phone))

            # context.user_data['current_record'] = rec

            num = rec["OrderNumber"]
            name = ' '.join(rec["PIB"])
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
                f"Заявка № {num}\nДнів з останньої заявки: {delt}")
            update.message.reply_text(
                f"👤 {name}\n🎈 {bday}\n📫 {addr}\n📲 {phone}\n👨‍👩‍👧‍👦 {cats}")
            update.message.reply_markdown_v2(f"```\n{msg}```")
            reset_state()
        else:
            update.message.reply_text(f"Записів немає")
    except Exception as e:
        update.message.reply_text("Невірно введений номер")
        print(f"\nPhone exception: {e}")
        traceback.print_exc()


def start(update, context):
    # function to handle the /start command
    first_name = update.message.chat.first_name
    update.message.reply_text(
        f"Вітаю {first_name}, я ваш ад'ютант, попрацюємо?\nВикористовуй меню для пошуку та створення")


def help(update, context):
    # function to handle the /help commazxnd
    update.message.reply_text('Всі інструкції згодом')


def error(update, context):
    # function to handle errors occured in the dispatcher
    update.message.reply_text('Якась нєвєдома хрєнь')

# function to handle normal text


def text(update, context):
    global STATE

    if STATE == PHONE:
        return received_phone(update, context)

    if STATE == DOB:
        return received_dob(update, context)

    if STATE == NAME:
        return received_name(update, context)

    if STATE == ADDRESS:
        return received_address(update, context)

    if STATE == SAVE:
        return received_save(update, context)

# This function is called when the /biorhythm command is issued


def main():
    config = configparser.ConfigParser()
    config.read(".nikobot.ini")
    TOKEN = config["NikoBot"]["TOKEN"]

    # create the updater, that will automatically create also a dispatcher and a queue to
    # make them dialoge
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # add handlers for start and help commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))

    #
    dispatcher.add_handler(CommandHandler("find_by_name", find_by_name))
    dispatcher.add_handler(CommandHandler("find_by_phone", find_by_phone))
    dispatcher.add_handler(CommandHandler("find_by_dob", find_by_dob))
    dispatcher.add_handler(CommandHandler("find_by_address", find_by_address))

    dispatcher.add_handler(CommandHandler("save_order", save_order))

    # add an handler for normal text (not commands)
    dispatcher.add_handler(MessageHandler(Filters.text, text))

    # add an handler for errors
    dispatcher.add_error_handler(error)

    # start your shiny new bot
    updater.start_polling()

    # run the bot until Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()
