from random import randint

import schedule

import googletrans
from googletrans import Translator

import pymorphy2

from datetime import datetime

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

from config import TOKEN
from config import API_KEY

import requests
from bs4 import BeautifulSoup
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

import pandas as pd
cols = [1,2,3,4]
user_base = pd.read_excel('user_base.xlsx',usecols=cols)
user_base.head()

@dp.message_handler(commands="dice")
async def cmd_random(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="бросить кубик", callback_data="random_value"))
    await message.answer("Нажмите на кнопку, чтобы бот бросил кубик", reply_markup=keyboard)
@dp.callback_query_handler(text="random_value")
async def send_random_value(call: types.CallbackQuery):
    await call.message.answer(str(randint(1, 6)))

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    global user_base
    user_id = message.from_user.id
    user_id_base = user_base['id'].tolist()
    user_name_base = user_base['name'].tolist()

    if (user_id in user_id_base) == False:
        await bot.send_message(message.from_user.id, 'Здавствуй пользователь я бот Grek, как я вижу ты здесь впервые укажи пожалуйста в следующем сообщении как мне к тебе обращаться\n')
        time_update(user_id = user_id)

    else:
        log = -1
        while log == -1:
            for index in range (len(user_base)):
                if user_id_base[index] == user_id:
                    log = index
                    await bot.send_message(message.from_user.id,"Приветствую " + user_name_base[index] + " чем я могу вам помочь ? \nДля получения справки ввидите команду /help")
                    time_update(user_id=user_id)

    return user_id_base , user_name_base
def time_update (user_id):
    global user_base
    user_id_base = user_base['id'].tolist()
    log = -1
    while log == -1:
        for index in range(len(user_base)):
            if user_id_base[index] == user_id:
                log = index
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                user_base.at[index, 'last call'] = current_time
                user_base.at[index, 'status'] = "Online"
                user_base.to_excel("user_base.xlsx")
@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Вот что я умею:\nотвечать на ваше приветсттвие\nПоказывать погоду в указаном вами городе\nБросать кубик через команду /dice")
    user_id = message.from_user.id
    time_update(user_id=user_id)

def multiple_replace(page, dictionary):
        for i, j in dictionary.items():
            page = page.replace(i, j)
        return page
@dp.message_handler()
async def processing_message(message: types.Message):
    global user_base ,user_name_base
    user_id_base = user_base['id'].tolist()
    user_name_base = user_base['name'].tolist()
    user_id = message.from_user.id
    pas = 0
    if (user_id in user_id_base) == False:
        new_user = {'id':[user_id],'name':[message.text]}
        df = pd.DataFrame(new_user,columns=['id','name'])
        user_base = pd.concat([user_base,df], ignore_index=True, sort=False)
        user_base.to_excel("user_base.xlsx")
        await bot.send_message(message.from_user.id,"Отлично я успешно внёс вас в баззу данных")
        time_update(user_id=user_id)
        pas = 1
    elif message.text == "Привет":
        status_base = user_base['status'].tolist()
        log = -1
        while log == -1:
            for index in range (len(user_base)):
                if user_id_base[index] == user_id:
                    log = index
                    status_base = user_base['status'].tolist()
                    if status_base[index] == 'Online':
                        await bot.send_message(message.from_user.id, 'Привет ' + user_name_base[index])
                    else:
                        await bot.send_message(message.from_user.id, 'Привет ' + user_name_base[index] + 'давно не виделись')
                    time_update(user_id=user_id)
    elif "Погода в" in message.text:
       a =  message.text[9:len(message.text)]
       morph = pymorphy2.MorphAnalyzer()
       a = morph.parse(a)[0].normal_form
       params = {"q": a,"appid":API_KEY,"units":"metric"}
       res = requests.get('https://api.openweathermap.org/data/2.5/weather',params = params)
       list = res.text
       time_update(user_id=user_id)
       if list != '{"cod":"404","message":"city not found"}':
            translator = Translator()
            f1 = translator.translate( list[(list.find("main") + 6):(list.find("description")-2)], src='en', dest='ru')
            f2 = translator.translate( list[(list.find("temp") + 6):(list.find("pressure")-57)],  src='en', dest='ru')
            f3 = translator.translate( list[(list.find("wind") + 7):(list.find("deg")-2)],  src='en', dest='ru')
            res = "Погода:" + f1.text  + "\nТемпература:" + f2.text + "\nВетер:" + f3.text
            await bot.send_message(message.from_user.id,res)
       else:
           await bot.send_message(message.from_user.id, "Город не найден")
    elif "Какой сегодня день" in message.text:
        time_update(user_id=user_id)
        url = 'https://my-calend.ru/holidays/'
        response = requests.get(url)
        page = BeautifulSoup(response.text, "lxml")
        # page = page.find_all('holiday-items')
        page = page.text
        page = page[(page.find('Праздники сегодня ') + 22):page.find('Именины отмечают')]
        dictionary = {"\xa0": "", "  ": "", " 0": "\n", " 1": "\n", " 2": "\n", " 3": "\n", " 4": "\n", " 5": "\n",
                      " 6": "\n", " 7": "\n", " 8": "\n", " 9": "\n", "0": "", "1": "", "2": "", "3": "", "4": "",
                      "5": "", "6": "", "7": "", "8": "", "9": ""}
        page = multiple_replace(page, dictionary)
        await bot.send_message(message.from_user.id, "Сегодня: \n" + page)
    elif pas == 1 :
        await bot.send_message(message.from_user.id, 'непонял вас')
        time_update(user_id=user_id)
def status_chek():
    t_1 = 0  # минуты
    t_2 = 0  # часы
    now = datetime.now()
    current_time_m = int(now.strftime("%M"))
    current_time_h = int(now.strftime("%H"))
    global user_base
    time_base = user_base['last call'].tolist()
    for index in range(len(time_base)):
        t_1 = int((time_base[index][3]) + (time_base[index][4]))
        t_2 = int((time_base[index][0]) + (time_base[index][1]))
        current_time = now.strftime("%H:%M:%S")
        if t_1 < current_time_m:
            if (current_time_m - t_1 >= 30):
                user_base.at[index, 'status'] = "offline"
                user_base.to_excel("user_base.xlsx")
        elif t_2 < current_time_h:
            if (current_time_h - t_1 >= 1):
                user_base.at[index, 'status'] = "offline"
                user_base.to_excel("user_base.xlsx")

def starter_status_chek():
    schedule.every(5).second.do(status_chek())
    print("status_chek started")

if __name__ == '__main__':
    executor.start_polling(dp)