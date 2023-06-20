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

def level_up(user_id):
    character_profile = players_collection.find_one({"user_id": user_id})

    if character_profile:
        current = character_profile.get("experience").get("current")
        total = character_profile.get("experience").get("total")
        potential = character_profile.get("potential")

        while current >= total:
            new_level = 1
            point = 1

            if potential == 'S':
                point = 12
            if potential == 'A':
                point = 10
            if potential == 'B':
                point = 8
            if potential == 'C':
                point = 6
            if potential == 'D':
                point = 4
            if potential == 'E':
                point = 2
            if potential == 'F':
                point = 1


            # Обновляем уровень и очки навыков персонажа в базе данных
            players_collection.update_one(
                {"user_id": user_id},
                {"$inc": {"lvl": new_level, "stats.points": point}},
                upsert=True
            )

            # Обновляем текущий опыт персонажа в базе данных
        players_collection.update_one(
            {"user_id": user_id},
            {"$set": {"experience.current": current}},
            upsert=True
        )


class ProfileCommand:
    def __init__(self, bot, collection):
        self.bot = bot
        self.collection = collection

    async def execute(self, message):
        user_id = message.from_user.id
        level_up(user_id)
        profile_data = self.get_profile_data(user_id)


        if profile_data:
            username = profile_data.get("username")
            lvl = profile_data.get("lvl")
            money = profile_data.get("money")
            potential = profile_data.get("potential")
            current = profile_data.get("experience").get("current")
            total = profile_data.get("experience").get("total")
            stats = profile_data.get("stats")


            await message.answer(f"""
Профиль:

Имя: {username}
Потенциал: {potential}

Уровель: {lvl}
Опыт: {current} из {total}

Деньги: {money} духовных камней(дк)


Характеристики:

Сила: {stats.get("strength")}
Ловкость: {stats.get("agility")}
Живучесть: {stats.get("vitality")}
Интеллект: {stats.get("intelligence")}
Ци: {stats.get("qi")}
Очки развития: {stats.get("points")}

            """)
        else:
            await message.answer("Ваш профиль не найден.")

    def get_profile_data(self, user_id):
        return self.collection.find_one({"user_id": user_id})

