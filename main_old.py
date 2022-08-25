from imaplib import Commands
import telebot
from pymongo import MongoClient

from datetime import datetime

# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
client = MongoClient("mongodb://localhost:27017")
db = client.nikovolunteers

# init the bot
adjutant = telebot.TeleBot('YOUR_TOKEN_HERE')


@adjutant.message_handler(commands=['start'])
def start(msg):
    resp = f'Salve, <u>{msg.from_user.first_name}</u> 🖖🏻 Що робимо далі?'
    # for arg in argv:
    print(msg)
    adjutant.send_message(msg.chat.id, resp, parse_mode='html')


@adjutant.message_handler(commands=['find'])
def find(msg):
    query = db.orders.find({"Phone": 680659203})
    prev = None
    delta = None
    while True:
        try:
            rec = query.next()
            date = datetime.fromisoformat(rec["Date"])
            if prev:
                delta = prev - date
                print("delta", delta.days)
            if not prev:
                prev = date
        except StopIteration:
            break
    resp = f'Маємо днів між датами заявок: <b>{delta.days}</b>'
    adjutant.send_message(msg.chat.id, msg, parse_mode='html')


# @
# def ge_che(lil):
#     adjutant.send_message(lil.chat.id, lil, parse_mode='html')


# adjutant.polling(non_stop=True)
