from random import randint

import googletrans
from googletrans import Translator

import pymorphy2

import psycopg2
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
cols = [0,1]
user_base = pd.read_excel('C:/Users/grish\OneDrive/Рабочий стол/бот/user_base.xlsx',usecols=cols)
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
    user_id = message.from_user.id
    user_id_base = user_base['id'].tolist()
    user_name_base = user_base['name'].tolist()
    if (user_id in user_id_base) == False:
        await bot.send_message(message.from_user.id, 'Здавствуй пользователь я бот Grek, как я вижу ты здесь впервые укажи пожалуйста в следующем сообщении как мне к тебе обращаться\n')

    else:
        index = 1
        while user_id_base[index] != user_id:
            index += 1
        await bot.send_message(message.from_user.id,"Приветствую " + user_name_base[index] + " чем я могу вам помочь ? \nДля получения справки ввидите команду /help")

@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Вот что я умею:\nотвечать на ваше приветсттвие\nПоказывать погоду в указаном вами городе\nБросать кубик через команду /dice")

@dp.message_handler()
async def processing_message(message: types.Message):
    global user_base , user_id_base
    # user_id = message.from_user.id
    # log = 0
    # if (user_id in user_base['id']) == False:
    #     new_user = pd.DataFrame([user_id,message.text])
    #     user_base.append(new_user,ignore_index=True)
    #     await message.reply(message.from_user.id,"Отлично я успешно внёс вас в баззу данных" + message.text )
    #     log = 1
    if message.text == "Привет":
        await bot.send_message(message.from_user.id,'Привет')
    elif "Погода в" in message.text:
       a =  message.text[9:len(message.text)]
       morph = pymorphy2.MorphAnalyzer()
       a = morph.parse(a)[0].normal_form
       params = {"q": a,"appid":API_KEY,"units":"metric"}
       res = requests.get('https://api.openweathermap.org/data/2.5/weather',params = params)
       list = res.text
       if list != '{"cod":"404","message":"city not found"}':
            translator = Translator()
            f1 = translator.translate( list[(list.find("main") + 6):(list.find("description")-2)], src='en', dest='ru')
            f2 = translator.translate( list[(list.find("temp") + 7):(list.find("pressure")-57)],  src='en', dest='ru')
            f3 = translator.translate( list[(list.find("wind") + 7):(list.find("deg")-2)],  src='en', dest='ru')
            res = "Погода:" + f1.text  + "\nТемпература:" + f2.text + "\nВетер:" + f3.text
            await bot.send_message(message.from_user.id,res)
       else:
           await bot.send_message(message.from_user.id, "Город не найден")
    elif log == 1 :
        await bot.send_message(message.from_user.id, 'непонял вас')
        await message.reply(message.from_user.id, log)

if __name__ == '__main__':
    executor.start_polling(dp)
    # executor.start_polling(dp, skip_updates=True)