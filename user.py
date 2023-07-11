import os
import random

from aiogram import Bot, Dispatcher, types, executor
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
MONGODB_URI = os.getenv('MONGODB_URI')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Подключение к MongoDB
client = MongoClient(MONGODB_URI)
db = client['Life']
players_collection = db['players']


class UserRegistration:
    def __init__(self, bot, collection):
        self.bot = bot
        self.collection = collection

    async def start(self, message):
        user_id = message.from_user.id
        username = message.from_user.first_name

        def get_potential():
            potentials = ['F', 'E', 'D', 'C', 'B', 'A', 'S']
            return random.choice(potentials)

        if self.is_user_registered(user_id):
            await message.answer("Вы уже зарегистрированы!")
        else:

        # Сохраняем данные пользователя в базе данных
            player_data = {
                "user_id": user_id,
                "username": username,

                'sect': 'Свободный культиватор',

                'material_art': 'Отсутствует',

                "money": 0,

                "potential": "S",
                #"potential": get_potential(),

                'lvl': 1,
                'experience': {
                    'current': 0,
                    'total': 1000
                },

                'stats': {
                    'health': 100,
                    'strength': 1,
                    'agility': 1,
                    'vitality': 1,
                    'intelligence': 1,

                    'qi': 0,

                    'points': 0
                },
                'skills': [

                ],
                'equipment': {
                    'weapon': 'Пусто',
                    'armor': 'Пусто',
                    "eq1": 'Пусто',
                    "eq2": 'Пусто',
                    "eq3": 'Пусто',
                    "eq4": 'Пусто',
                    "eq5": 'Пусто',
                },
                'inventory': [

                ],
                'quests': [

                ],
                'achievements': [

                ],

                'location': 'Город Лотоса',

                'isAdmin': False,

            }

            self.collection.insert_one(player_data)

            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            profile_button = types.KeyboardButton(text="Профиль")
            keyboard.add(profile_button)
            await message.answer("""
    Вы создали персонажа. Самое время начать свой путь в Immortal Life.
    Желаю вам успехов!
                """, reply_markup=keyboard)


    def is_user_registered(self, user_id):
        return self.collection.find_one({"user_id": user_id}) is not None


class ChangeNameCommand:
    def __init__(self, bot, collection):
        self.bot = bot
        self.collection = collection

    async def execute(self, message):
        user_id = message.from_user.id
        new_name = message.get_args()

        if new_name:
            self.update_user_name(user_id, new_name)
            await message.answer(f"Имя пользователя успешно изменено на: {new_name}")
        else:
            await message.answer("Укажите новое имя пользователя после команды /name")

    def update_user_name(self, user_id, new_name):
        self.collection.update_one({"user_id": user_id}, {"$set": {"username": new_name}})
