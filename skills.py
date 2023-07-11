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
techniques = db['techniques']

# Уникальные техники обычных боевых культиваторов
techniques = [

    {
        'type': 'divine',
        'name': 'Покров Божества',
        'desc': 'Блокирует весь урона за счёт ци',
    },
    {
        'type': 'divine',
        'name': 'Божественное просветление',
        'desc': 'Получение дополнительного опыта в бою с противником.',
    },
    {
        'type': 'demonic',
        'name': 'Клинок бессмертия',
        'desc': 'Впитывает жизенные силы противника',
    },
    {
        'type': 'demonic',
        'name': 'Укрощение Мощи',
        'desc': 'Кража силы противника',
    },
    {
        'type': 'demonic',
        'name': 'Эссенция Улитки',
        'desc': 'Кража ловкости противника',
    },
    {
        'type': 'demonic',
        'name': 'Манипуляция Сущностью',
        'desc': 'Кража живучести противника',
    },
    {
        'type': 'demonic',
        'name': 'Тик-Ток',
        'desc': 'Кража интеллекта у противника. Превращает человека в дауна.',
    },
    {
        'type': 'demonic',
        'name': 'Апокалипсический Взрыв',
        'desc': 'Наносит урон пропорционально имеющейся ци',
    },
]

    # Запись уникальных техник в коллекции 'unique_techniques' с указанием владельцев
db.techniques.insert_many(techniques)

