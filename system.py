import asyncio
import datetime
from pymongo import MongoClient
import os
import random

from aiogram import Bot, Dispatcher, types, executor
from pymongo import MongoClient
from dotenv import load_dotenv

from fight import battle

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
MONGODB_URI = os.getenv('MONGODB_URI')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Подключение к MongoDB
client = MongoClient(MONGODB_URI)
db = client['Life']
players_collection = db['players']


class CultivateCommand:
    def __init__(self, bot, collection):
        self.bot = bot
        self.collection = collection

    async def execute(self, message):
        user_id = message.from_user.id
        player_data = self.get_player_data(user_id)

        if player_data:
            player_name = player_data.get("username")

            if "hunt_end_time" not in player_data and "cult_end_time" in player_data:

                cult_end_time = player_data["cult_end_time"]
                remaining_time = cult_end_time - datetime.datetime.now().replace(microsecond=0)
                if remaining_time.total_seconds() <= 0:
                    await self.complete_hunt(user_id, player_name)
                else:
                    await message.answer(f"{player_name}, вы уже медитируете. Осталось времени: {remaining_time}")
            else:

                if "hunt_end_time" not in player_data:
                    cult_end_time = datetime.datetime.now() + datetime.timedelta(minutes=1)
                    self.update_hunt_time(user_id, cult_end_time)

                    funny_phrases = [
                        "Культивировать боевые искусства - это как пытаться скормить коту горячий перец. Он будет вас преследовать, но в конечном итоге получите огненные лапы!",
                        "Когда я начал культивацию боевых искусств, я думал, что стану непобедимым. А оказалось, что стал только неприятным для моих противников!",
                        "Моя культивация боевых искусств так быстро развивается, что мои противники начали тренироваться в беге от меня!",
                        "Культивировать боевые искусства - это как играть в шахматы с самим собой. В конце концов, я побеждаю и проигрываю одновременно!",
                        "Когда я культивирую боевые искусства, мои мышцы говорят: 'Стоп, хватит!' А мой разум говорит: 'Еще немного, только пара тысяч повторений!'",
                        "Моя культивация боевых искусств так эффективна, что мои противники иногда просто садятся и плачут, прежде чем со мной сражаться!",
                        "Если культивация боевых искусств была бы олимпийским видом спорта, я бы получил золотую медаль за самые странные позы!",
                        "Мои друзья думают, что я сумасшедший, потому что я культивирую боевые искусства во сне. Но я знаю, что я просто готов к любым ситуациям!",
                        "Культивация боевых искусств - это как поездка на американских горках. Иногда весело, иногда страшно, но всегда захватывающе!",
                        "Моя культивация боевых искусств дала мне невероятные рефлексы. Теперь я могу ловить летящие воздушные пирожки!"
                    ]

                    await message.answer(f"{random.choice(funny_phrases)}")
                else:
                    await message.answer(f"Вы не можете медитировать во время охоты")
        else:
            await message.answer("Ваш профиль не найден.")

    def get_player_data(self, user_id):
        return self.collection.find_one({"user_id": user_id})

    def update_hunt_time(self, user_id, cult_end_time):
        self.collection.update_one({"user_id": user_id}, {"$set": {"cult_end_time": cult_end_time}})

    async def complete_hunt(self, user_id, player_name):
        player_data = self.get_player_data(user_id)

        if player_data and "cult_end_time" in player_data:

            if player_data.get("location") == "Город Лотоса":
                experience = random.randint(10, 100)
                energy = random.randint(1, 50)

            if player_data.get("location") == "Рисовые поля Лонг-Це":
                experience = random.randint(50, 250)
                energy = random.randint(10, 100)

        # Обновляем профиль с полученным опытом
        self.collection.update_one({"user_id": user_id}, {"$unset": {"cult_end_time": ""}, "$inc": {
            "experience.current": experience, "stats.qi": energy
        }})
        await self.bot.send_message(user_id,
                                    f"{player_name}, вы закончили медитацию! Полученный опыт: {experience}\nПолученная ци: {energy}")


class HuntCommand:
    def __init__(self, bot, collection):
        self.bot = bot
        self.collection = collection

    async def execute(self, message):
        user_id = message.from_user.id
        player_data = self.get_player_data(user_id)

        if player_data:
            player_name = player_data.get("username")

            if "hunt_end_time" in player_data and "cult_end_time" not in player_data:

                hunt_end_time = player_data["hunt_end_time"]
                remaining_time = hunt_end_time - datetime.datetime.now().replace(microsecond=0)
                if remaining_time.total_seconds() <= 0:
                    await self.complete_hunt(user_id, player_name)
                else:
                    await message.answer(
                        f"{player_name}, вы уже охотитесь. Осталось времени: {remaining_time}")
            else:
                if "cult_end_time" not in player_data and player_data.get('location') != "Город Лотоса":
                    hunt_end_time = datetime.datetime.now() + datetime.timedelta(minutes=1)
                    self.update_hunt_time(user_id, hunt_end_time)

                    phrases = [
                        "С рёвом тигра и страшным криком 'Мяу!', отправляюсь на охоту за судьбой и рыбкой!",
                        "С шагами журавля и вилянием хвоста, преследую свою добычу, будь то мышь или сушняк!",
                        "В глубине леса слышится шорох... Эй, приключение, я готов схватить тебя за хвост!",
                        "Соединяюсь с природой и прикидываюсь кустом, чтобы подсмотреть за дичью незамеченным!",
                        "Сквозь туман леса пробиваюсь, в одной руке чай, в другой печенье - готов к бою и перекусу!",
                        "Взмах метлы, рассекающий воздух, отправляюсь на охоту, чтобы собрать нечестивые пылинки!",
                        "Следы добычи ведут меня по лабиринтам леса. Спокойно, охота, я пока выпью чашечку чая!",
                        "Слушаю шорох ветра и разговоры листьев. Лес готов открыть свои сокровища, но только после песни!",
                        "Тропинка ведёт меня в глубины дикой природы, где я смогу столкнуться с невероятной дичью и невероятными приключениями!",
                        "С силой взрывающегося пузыря, отправляюсь на охоту за приключениями и забавными моментами!"
                    ]

                    await message.answer(f"{random.choice(phrases)}")
                else:
                    await message.answer(f"Вы не можете охотиться в городе, либо вы заняты медитацией.")

        else:
            await message.answer("Ваш профиль не найден.")

    def get_player_data(self, user_id):
        return self.collection.find_one({"user_id": user_id})

    def update_hunt_time(self, user_id, hunt_end_time):
        self.collection.update_one({"user_id": user_id}, {"$set": {"hunt_end_time": hunt_end_time}})

    async def complete_hunt(self, user_id, player_name):
        player_data = self.get_player_data(user_id)

        if player_data and "hunt_end_time" in player_data:
            time_to_battle = random.randint(0, 100)
            if time_to_battle >= 25:

                if player_data.get("location") == "Рисовые поля Лонг-Це":
                    experience = random.randint(10, 100)
                    money = random.randint(100, 500)

                # Обновляем профиль с полученным опытом
                self.collection.update_one({"user_id": user_id}, {"$unset": {"cult_end_time": ""}, "$inc": {
                    "experience.current": experience, "money": money
                }})
                await self.bot.send_message(user_id,
                                            f"{player_name}, вы закончили охоту! Полученный опыт: {experience}\nДуховные камни: {money}")

            else:
                random_player = players_collection.aggregate([{'$sample': {'size': 1}}]).next()
                while random_player["user_id"] == user_id and random_player["location"] != "Город Лотоса":
                    random_player = players_collection.aggregate([{'$sample': {'size': 1}}]).next()
                res = battle(user_id, random_player['user_id'])

                if res[0] == 1:
                    await bot.send_message(chat_id=random_player['user_id'],
                                           text=f"На вас напал и избил {player_data['username']}. -{res[1]} духовных камней")
                    await bot.send_message(chat_id=user_id,
                                           text=f"Вы напали на {random_player['username']} и одолели его. +{res[1]} духовных камней")

                if res[0] == 2:
                    await bot.send_message(chat_id=user_id,
                                           text=f"Вы напали на {random_player['username']}, но проиграли. -{res[1]} духовных камней")
                    await bot.send_message(chat_id=random_player['user_id'],
                                           text=f"На вас напали, но вы отбили атаку {player_data['username']}. +{res[1]} духовных камней")
