import configparser
from src.helpers.project_root import project_root

# https://www.mongodb.com/developer/languages/python/python-quickstart-fle/
# https://python.gotrained.com/adding-telegram-members-to-your-groups-telethon-python/
# https://www.google.com/search?q=how+to+check+if+user+belongs+to+a+channel+programmaticaly+telegram

# BOT should be a group admin
# BOT.getClient('channel_id - .ini tasks_channel'message.chat.id)
config = configparser.ConfigParser()
config.read(f"{project_root()}/../.nikobot.ini")
config = config["NikoBot"]
users = config["users"]
users = users.replace(' ', '').split(',')
users = set(users)


def is_permitted(user):
    return users.__contains__(user)
