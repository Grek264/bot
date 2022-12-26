from random import randint
import asyncio
import os
import threading
from multiprocessing import Process
from threading import Thread, Lock

import time

import psycopg2

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
from config import ADMIN_PASS

import requests
from bs4 import BeautifulSoup
bot_loop = asyncio.new_event_loop()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

import pandas as pd
cols = [1,2,3,4,5]
global ch_log , con_adm_rig
ch_log = 0
con_adm_rig = 0
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
    await call.message.answer( "/start\n/help\n/dice\n/func_menu")

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
    await bot.send_message(message.from_user.id,"/start\n/help\n/dice\n/func_menu")
    return user_id_base , user_name_base
def time_update (user_id):
    global user_base
    user_id_base = user_base['id'].tolist()
    log = -1
    if (user_id in user_id_base) == True:
        while log == -1:
            for index in range(len(user_base)):
                if user_id_base[index] == user_id:
                    log = index
                    now = datetime.now()
                    current_time = now.strftime("%d:%H:%M:%S")
                    user_base.at[index, 'last call'] = current_time
                    user_base.at[index, 'status'] = "Online"
                    user_base.to_excel("user_base.xlsx")
@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Получить справку о функциональности бота", callback_data="feature list"))
    keyboard.add(types.InlineKeyboardButton(text="Сменить свой ник", callback_data="Change nickname" ))
    await message.answer("Выберите один из следующих пунктов", reply_markup=keyboard)
    user_id = message.from_user.id
    time_update(user_id=user_id)

@dp.message_handler(commands=['func_menu'])
async def func_menu(message: types.Message):
    user_id = message.from_user.id
    user_id_base = user_base['id'].tolist()
    time_update(user_id=user_id)
    log = -1
    while log == -1:
        for index in range(len(user_base)):
            if user_id_base[index] == user_id:
                log = index
    admin_base = user_base['admin'].tolist()
    if admin_base[index] == "NO":
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Какой сегодня день", callback_data="What day is today"))
        keyboard.add(types.InlineKeyboardButton(text="Подключить права администратора", callback_data="Connect administrator rights" ))
        await message.answer("Выберите одну из следующих функций", reply_markup=keyboard)
    elif admin_base[index] == "YES":
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Просмотреть базу данных о пользвателях", callback_data="view database"))
        keyboard.add(types.InlineKeyboardButton(text="Какой сегодня день", callback_data="What day is today"))
        await message.answer("Выберите одну из следующих функций", reply_markup=keyboard)

@dp.callback_query_handler(text="What day is today")
async def What_day_is_today(call: types.CallbackQuery):
    user_id = call.from_user.id
    time_update(user_id=user_id)
    url = 'https://my-calend.ru/holidays/'
    response = requests.get(url)
    page = BeautifulSoup(response.text, "lxml")
    page = page.text
    page = page[(page.find('Праздники сегодня ') + 22):page.find('Именины отмечают')]
    dictionary = {"\xa0": "", "   ": "\n", "    ": "\n", "0": "", "1": " ", "2": "", "3": "", "4": "",
                  "5": "", "6": "", "7": "", "8": "", "9": "", "  ": "", "\n ": "\n"}
    page = multiple_replace(page, dictionary)
    await call.message.answer( "Сегодня: \n" + page)
    await call.message.answer("/start\n/help\n/dice\n/func_menu")

@dp.callback_query_handler(text="view database")
async def view_database(call: types.CallbackQuery):
    await call.message.answer(user_base)
    await call.message.answer("/start\n/help\n/dice\n/func_menu")

@dp.callback_query_handler(text="Connect administrator rights")
async def Connect_administrator_rights(call: types.CallbackQuery):
    await call.message.answer("Укажите пароль для получения прав Администратора")
    global con_adm_rig
    con_adm_rig = 1

@dp.callback_query_handler(text="feature list")
async def feature_list(call: types.CallbackQuery):
    await call.message.answer("Вот что я умею:\nотвечать на ваше приветсттвие\nПоказывать погоду в указаном вами городе\nБросать кубик через команду /dice\nРассказывать какой сегодня день")
    await call.message.answer("/start\n/help\n/dice\n/func_menu")

@dp.callback_query_handler(text="Change nickname")
async def Change_nickname(call: types.CallbackQuery):
    await call.message.answer("В следующем сообщении укажите свой новый ник")
    global ch_log
    ch_log = 1
def multiple_replace(page, dictionary):
        for i, j in dictionary.items():
            page = page.replace(i, j)
        return page
@dp.message_handler()
async def processing_message(message: types.Message):
    global user_base ,user_name_base ,ch_log , con_adm_rig
    user_id_base = user_base['id'].tolist()
    user_name_base = user_base['name'].tolist()
    user_id = message.from_user.id
    if (user_id in user_id_base) == False:
        new_user = {'id':[user_id],'name':[message.text],'admin':["NO"]}
        df = pd.DataFrame(new_user,columns=['id','name','admin'])
        user_base = pd.concat([user_base,df], ignore_index=True, sort=False)
        user_base.to_excel("user_base.xlsx")
        await bot.send_message(message.from_user.id,"Отлично я успешно внёс вас в базу данных")
        await bot.send_message(message.from_user.id, "/start\n/help\n/dice\n/func_menu")
        time_update(user_id=user_id)
    elif ch_log == 1:
        user_id = message.from_user.id
        user_id_base = user_base['id'].tolist()
        log = -1
        while log == -1:
            for index in range(len(user_base)):
                if user_id_base[index] == user_id:
                    log = index
                    user_base.at[index, 'name'] = message.text
                    user_base.to_excel("user_base.xlsx")
                    await bot.send_message(message.from_user.id, "Отлично я успешно сменил ваш ник на " + message.text)
                    await bot.send_message(message.from_user.id, "/start\n/help\n/dice\n/func_menu")
                    ch_log = 0
    elif con_adm_rig == 1:
        time_update(user_id=user_id)
        if message.text == ADMIN_PASS:
            log = -1
            while log == -1:
                for index in range(len(user_base)):
                    if user_id_base[index] == user_id:
                        log = index
                        user_base.at[index, 'admin'] = "YES"
                        user_base.to_excel("user_base.xlsx")
                        await bot.send_message(message.from_user.id,"Вы успешно получили права администратора")
                        await bot.send_message(message.from_user.id, "/start\n/help\n/dice\n/func_menu")
        else:
            await bot.send_message(message.from_user.id,"Неверный пароль")
        con_adm_rig = 0
    elif message.text == "Привет" or message.text == "привет":
        status_base = user_base['status'].tolist()
        log = -1
        while log == -1:
            for index in range (len(user_base)):
                if user_id_base[index] == user_id:
                    log = index
                    if status_base[index] == 'Online':
                        await bot.send_message(message.from_user.id, 'Привет ' + user_name_base[index])
                        await bot.send_message(message.from_user.id,"/start\n/help\n/dice\n/func_menu")
                    else:
                        await bot.send_message(message.from_user.id, 'Привет ' + user_name_base[index] + ' давно не виделись')
                        await bot.send_message(message.from_user.id, "/start\n/help\n/dice\n/func_menu")
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
            # print(list)
            f1 = translator.translate( list[(list.find("main") + 6):(list.find("description")-2)], src='en', dest='ru')
            f2 = translator.translate( (list[(list.find("temp") + 5):(list.find("feels_like")-2)]),  src='en', dest='ru')
            f3 = translator.translate( list[(list.find("wind") + 7):(list.find("deg")-2)],  src='en', dest='ru')
            res = "Погода:" + f1.text  + "\nТемпература:" + f2.text+ " C" + "\nВетер:" + f3.text + "м/с"
            await bot.send_message(message.from_user.id,res)
            await bot.send_message(message.from_user.id, "/start\n/help\n/dice\n/func_menu")
       else:
           await bot.send_message(message.from_user.id, "Город не найден")
           await bot.send_message(message.from_user.id, "/start\n/help\n/dice\n/func_menu")
    elif message.text == ADMIN_PASS:
        return 1
    elif (user_id in user_id_base) != False:
        await bot.send_message(message.from_user.id, 'непонял вас')
        await bot.send_message(message.from_user.id, "/start\n/help\n/dice\n/func_menu")
        time_update(user_id=user_id)

def base_call(id , message):
    conn = psycopg2.connect(user="bot",
                password="7961dee7X1",
                database="postgres_db", host='localhost')
    print("Database opened successfully")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM airport LIMIT 10')
    records = cursor.fetchall()
    print(records)
    cursor.close()
    conn.close()
async def send_message(id ,message):
    await bot.send_message(id,message)

async def status_chek():
    print('start')
    while True:
        now = datetime.now()
        print("status_chek started:"+str(now))
        current_time_m = int(now.strftime("%M"))
        current_time_h = int(now.strftime("%H"))
        current_time_d = int(now.strftime("%d"))
        global user_base
        time_base = user_base['last call'].tolist()
        for index in range(len(time_base)):
            t_1 = int((time_base[index][6]) + (time_base[index][7]))
            t_2 = int((time_base[index][3]) + (time_base[index][4]))
            t_3 = int((time_base[index][0]) + (time_base[index][1]))
            if t_3 < current_time_d:
                user_base.at[index, 'status'] = "offline"
                user_base.to_excel("user_base.xlsx")
            elif t_1 < current_time_m:
                if (current_time_m - t_1 >= 30):
                    user_base.at[index, 'status'] = "offline"
                    user_base.to_excel("user_base.xlsx")
                elif t_2 < current_time_h:
                    if (current_time_h - t_2 >= 1):
                        user_base.at[index, 'status'] = "offline"
                        user_base.to_excel("user_base.xlsx")
                else:
                    user_base.at[index, 'status'] = "Online"
                    user_base.to_excel("user_base.xlsx")
        # await send_message(1258306656,"status_chek completed:" + str(now))
        now = datetime.now()
        print("status_chek completed:" + str(now))
        await asyncio.sleep(60*30)

#threading.Thread(target=status_chek,args=(),daemon=True).start()

if __name__ == '__main__':
    myloop = asyncio.new_event_loop()
    myloop.create_task(status_chek())
    myloop.create_task(dp.start_polling())
    myloop.run_forever()