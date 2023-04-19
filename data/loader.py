from telebot import TeleBot
from config import TOKEN
from database.database import MainManager
manager = MainManager()

bot = TeleBot(TOKEN)

