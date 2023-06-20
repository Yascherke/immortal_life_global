import logging
import os
from aiogram import Bot, Dispatcher, types, executor
from pymongo import MongoClient
from dotenv import load_dotenv

from profile import ProfileCommand
from system import CultivateCommand
from user import UserRegistration, ChangeNameCommand


load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
MONGODB_URI = os.getenv('MONGODB_URI')

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Включение логгирования
logging.basicConfig(level=logging.INFO)

# Подключение к MongoDB
client = MongoClient(MONGODB_URI)
db = client['Life']
players_collection = db['players']


# Создание экземпляра класса UserRegistration
user_registration = UserRegistration(bot, players_collection)

# Создание экземпляра класса ChangeNameCommand
change_name_command = ChangeNameCommand(bot, players_collection)

# Создание экземпляра класса ProfileCommand
profile_command = ProfileCommand(bot, players_collection)

# Создание экземпляра класса HuntCommand
work_command = CultivateCommand(bot, players_collection)

# Обработчик команды /help
@dp.message_handler(commands=['help'])
async def handle_help(message: types.Message):
    await message.answer("""
    
Вывод профиля: Профиль
    
Смена имени: /name Ваше имя
    """)

# Обработчики сообщений
@dp.message_handler(commands=['start'])
async def handle_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    profile_button = types.KeyboardButton(text="Профиль")
    keyboard.add(profile_button)
    await message.answer("Добро пожаловать!", reply_markup=keyboard)
    await user_registration.start(message)

# Обработчик команды изменения имени
@dp.message_handler(commands=['name'])
async def handle_change_name(message: types.Message):
    await change_name_command.execute(message)

# Обработчик команды /work
@dp.message_handler(commands=['meditate'])
async def handle_hunt(message: types.Message):
    await work_command.execute(message)


@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_message(message: types.Message):
    if message.text.lower() == "профиль":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        profile_button = types.KeyboardButton(text="Профиль")
        work_button = types.KeyboardButton(text="Медитировать")
        keyboard.add(profile_button, work_button)
        await message.answer('Ваш профиль', reply_markup=keyboard)
        await profile_command.execute(message)

    if message.text.lower() == "медитировать":
        await work_command.execute(message)

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
