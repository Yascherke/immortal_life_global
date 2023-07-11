import logging
import os
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from pymongo import MongoClient
from dotenv import load_dotenv

from profile import ProfileCommand
from system import CultivateCommand, HuntCommand
from user import UserRegistration, ChangeNameCommand

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
MONGODB_URI = os.getenv('MONGODB_URI')

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

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

hunt_command = HuntCommand(bot, players_collection)


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


@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_message(message: types.Message, state: FSMContext):
    if message.text.lower() == "профиль":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        profile_button = types.KeyboardButton(text="Профиль")
        work_button = types.KeyboardButton(text="Медитировать")
        hunt_button = types.KeyboardButton(text="Охота")
        stats_button = types.KeyboardButton(text="Характеристики")
        loc_button = types.KeyboardButton(text="Локации")
        keyboard.add(profile_button, stats_button, work_button, hunt_button, loc_button)
        await message.answer('Ваш профиль', reply_markup=keyboard)
        await profile_command.execute(message)

    if message.text.lower() == "медитировать":
        await work_command.execute(message)

    if message.text.lower() == "охота":
        await hunt_command.execute(message)

    if message.text.lower() == "характеристики":

        await message.answer("Какой стат вы хотите повысить?")
        await state.set_state(States.START)

    if message.text.lower() == "локации":
        user_id = message.from_user.id
        player_loc = players_collection.find_one({'user_id': user_id})

        loc_keyb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        loc1 = types.KeyboardButton(text="Рисовые поля Лонг-Це")
        loc2 = types.KeyboardButton(text="Медитировать")
        loc3 = types.KeyboardButton(text="Охота")
        loc4 = types.KeyboardButton(text="Характеристики")
        city = types.KeyboardButton(text="Город Лотоса")
        back = types.KeyboardButton(text="Профиль")
        if player_loc["location"] == "Город Лотоса":
            loc_keyb.add(loc1, back)
        if player_loc["location"] == "Рисовые поля Лонг-Це":
            loc_keyb.add(loc1, back)

        await message.answer(f'Вы находитесь в локации: {player_loc["location"]}. Чтобы отправиться в другую локацию выберите один из доступных вариантов.', reply_markup=loc_keyb)

    if message.text == "Рисовые поля Лонг-Це":
        user_id = message.from_user.id
        player_loc = players_collection.find_one({'user_id': user_id})

        loc_keyb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        loc1 = types.KeyboardButton(text="Рисовые поля Лонг-Це")
        loc2 = types.KeyboardButton(text="Медитировать")
        loc3 = types.KeyboardButton(text="Охота")
        loc4 = types.KeyboardButton(text="Характеристики")
        back = types.KeyboardButton(text="Профиль")
        loc_keyb.add(loc1, back)

        players_collection.update_one({"user_id": user_id}, {'$set': {'location': "Рисовые поля Лонг-Це"}})
        await message.answer(
                f'Вы отправились в локацию: Рисовые поля Лонг-Це. Эта локацию для начинающих свой путь культиваторов. \n\nСложность: Низкая. \nПлотность энергии: Низкая. \nШанс встретить врага: 25%',
                reply_markup=loc_keyb)

    if message.text == "Город Лотоса":
        user_id = message.from_user.id
        player_loc = players_collection.find_one({'user_id': user_id})

        loc_keyb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        city = types.KeyboardButton(text="Город Лотоса")
        loc2 = types.KeyboardButton(text="Медитировать")
        loc3 = types.KeyboardButton(text="Охота")
        loc4 = types.KeyboardButton(text="Характеристики")
        back = types.KeyboardButton(text="Профиль")
        loc_keyb.add(city, back)

        players_collection.update_one({"user_id": user_id}, {'$set': {'location': "Город Лотоса"}})
        await message.answer(
                f'Вы отправились в локацию: Город Лотоса. Портовый город и отправная точка в пути становления бессмертным. \n\nПлотность энергии: Очень низкая',
                reply_markup=loc_keyb)


class States:
    START = "start"

    strength = "str"
    agility = "agi"
    vitality = "vit"
    intelligence = "int"



@dp.message_handler(state=States.START)
async def process_start_state(message: types.Message, state: FSMContext):
    # Логика обработки сообщений и переходы между состояниями
    if message.text.lower() == "сила":
        await state.set_state(States.strength)
        await message.answer("На сколько очков вы хотите повысить силу?")


    elif message.text.lower() == "ловкость":
        await state.set_state(States.agility)

    elif message.text.lower() == "выносливость":
        await state.set_state(States.vitality)

    elif message.text.lower() == "интеллект":
        await state.set_state(States.intelligence)
    else:
        await message.answer("Некорректный выбор.")


@dp.message_handler(state=States.strength)
async def process_state_a(message: types.Message, state: FSMContext):

    user_id = message.from_user.id
    character_profile = players_collection.find_one({"user_id": user_id})
    points = character_profile.get("stats").get("points")
    msg = message.text

    if int(msg) <= points:
        players_collection.update_one({"user_id": user_id},
                                      {"$inc": {"stats.strength": int(msg), "stats.points": -int(msg)}})
        await message.answer("Вы увеличили силу")
        await state.finish()
    else:
        await message.answer("Не хватает поинтов")

@dp.message_handler(state=States.agility)
async def process_state_a(message: types.Message, state: FSMContext):

    user_id = message.from_user.id
    character_profile = players_collection.find_one({"user_id": user_id})
    points = character_profile.get("stats").get("points")
    msg = message.text

    if int(msg) <= points:
        players_collection.update_one({"user_id": user_id},
                                      {"$inc": {"stats.agility": int(msg), "stats.points": -int(msg)}})
        await message.answer("Вы увеличили ловкость")
        await state.finish()
    else:
        await message.answer("Не хватает поинтов")

@dp.message_handler(state=States.vitality)
async def process_state_a(message: types.Message, state: FSMContext):

    user_id = message.from_user.id
    character_profile = players_collection.find_one({"user_id": user_id})
    points = character_profile.get("stats").get("points")
    msg = message.text

    if int(msg) <= points:
        players_collection.update_one({"user_id": user_id},
                                      {"$inc": {"stats.vitality": int(msg), "stats.points": -int(msg), "stats.health": 10 * int(msg)}})
        await message.answer("Вы увеличили выносливость")
        await state.finish()
    else:
        await message.answer("Не хватает поинтов")

@dp.message_handler(state=States.intelligence)
async def process_state_a(message: types.Message, state: FSMContext):

    user_id = message.from_user.id
    character_profile = players_collection.find_one({"user_id": user_id})
    points = character_profile.get("stats").get("points")
    msg = message.text

    if int(msg) <= points:
        players_collection.update_one({"user_id": user_id},
                                      {"$inc": {"stats.intelligence": int(msg), "stats.points": -int(msg), "stats.qi": 10 * int(msg)}})
        await message.answer("Вы увеличили интеллект")
        await state.finish()
    else:
        await message.answer("Не хватает поинтов")




# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
