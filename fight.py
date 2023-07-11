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


# Функция для выполнения атаки
def battle(attacker_id, defender_id):

    # Получение профилей атакующего и защищающегося из базы данных
    attacker_profile = players_collection.find_one({"user_id": attacker_id})
    defender_profile = players_collection.find_one({"user_id": defender_id})
    # Проверка наличия профилей в базе данных

    # Получение статистики и навыков атакующего и защищающегося
    attacker_stats = attacker_profile["stats"]
    defender_stats = defender_profile['stats']
    attacker_skills = attacker_profile['skills']
    defender_skills = defender_profile['skills']
    attacker_ma = attacker_profile['material_art']
    defender_ma = defender_profile['material_art']

    # Расчет урона атаки
    attack_damage = attacker_stats['strength'] + attacker_stats['agility'] + attacker_stats['intelligence']
    def_damage = defender_stats['strength'] + defender_stats['agility'] + defender_stats['intelligence']

    # Награда
    win_attack = round(defender_profile['money'] / 2)
    win_def = round(attacker_profile['money'] / 2)

    # Боевое искусство

    # Бой
    while attacker_stats['health'] > 0 or defender_stats['health'] > 0:

        if attacker_stats['agility'] >= defender_stats['agility']:
            defender_stats['health'] -= attack_damage
            attacker_stats['health'] -= def_damage
        else:
            attacker_stats['health'] -= def_damage
            defender_stats['health'] -= attack_damage

        if defender_stats['health'] <= 0:
            players_collection.update_one({"user_id": attacker_id}, {"$unset": {"hunt_end_time": ""}, "$inc": {
                "money": win_attack
            }})
            return [1, win_attack]
        if attacker_stats['health'] <= 0:
            players_collection.update_one({"user_id": defender_id}, {"$unset": {"hunt_end_time": ""}, "$inc": {
                "money": win_def
            }})
            return [2, win_def]
