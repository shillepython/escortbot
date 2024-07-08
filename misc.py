import logging
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3
from aiogram import Bot, Dispatcher
import configparser

config = configparser.ConfigParser()
config.read('addons/config.ini')


conn = sqlite3.connect("database.sqlite3", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("PRAGMA journal_mode = WAL")
cursor.execute("PRAGMA wal_autocheckpoint = 1")

bot = Bot(token=config["Bot"]["token"])
memory_storage = MemoryStorage()
dispatcher = Dispatcher(bot, storage=memory_storage)
logging.basicConfig(level=logging.INFO)

