from random import randint
import asyncio
import os

import psycopg2

from googletrans import Translator

import pymorphy2

from datetime import datetime

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher

from config import TOKEN
from config import API_KEY
from config import ADMIN_PASS

import requests
from bs4 import BeautifulSoup

bot_loop = asyncio.new_event_loop()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

import pandas as pd

cols_user_base = [1, 2, 3, 4, 5, 6, 7]
cols_ip_base = [1, 2]
global ch_log, con_adm_rig, ip_list, element
ch_log = 0
con_adm_rig = 0
Im_sear = 0
user_base = pd.read_excel("User_base.xlsx", usecols=cols_user_base)
user_base.head()
ip_base = pd.read_excel('ip_base.xlsx', usecols=cols_ip_base)
user_base.head()
ip = ip_base['number_ip'].tolist()
element = int(ip[0])
ip_list = ip_base['ip_list'].tolist()

@dp.message_handler(commands="dice")
async def cmd_random(message: types.Message):
    user_id = message.from_user.id
    if ban_chek(user_id) != 1:
        time_update(user_id=user_id)
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="бросить кубик", callback_data="random_value"))
        await message.answer("Нажмите на кнопку, чтобы бот бросил кубик", reply_markup=keyboard)
        count_of_message(user_id)


@dp.callback_query_handler(text="random_value")
async def send_random_value(call: types.CallbackQuery):
    await call.message.answer(str(randint(1, 6))), await call.message.answer("/start\n/help\n/dice\n/func_menu")

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    global user_base
    user_id_base = user_base['id'].tolist()
    user_id = message.from_user.id
    if ban_chek(user_id) != 1 or (user_id in user_id_base) == False:
        user_name_base = user_base['name'].tolist()
        if (user_id in user_id_base) == False:
            await bot.send_message(message.from_user.id,'Здавствуй пользователь я бот Grek, как я вижу ты здесь впервые укажи пожалуйста в следующем сообщении как мне к тебе обращаться\n')
        else:
            boolean_variable = -1
            while boolean_variable == -1:
                boolean_variable = [index for index in range(len(user_base)) if user_id_base[index] == user_id], await bot.send_message(message.from_user.id,f"Приветствую {user_name_base[boolean_variable]} чем я могу вам помочь ? \nДля получения справки ввидите команду /help"), time_update(user_id=user_id), await bot.send_message(message.from_user.id, "/start\n/help\n/dice\n/func_menu")
            count_of_message(user_id)
        return user_id_base, user_name_base


def time_update(user_id):
    global user_base
    user_id_base = user_base['id'].tolist()
    boolean_variable = -1
    if (user_id in user_id_base) == True:
        while boolean_variable == -1:
            boolean_variable = [index for index in range(len(user_base)) if user_id_base[index] == user_id]
            now = datetime.now()
            current_time = now.strftime("%d:%H:%M:%S")
            user_base.at[boolean_variable[0], 'last call'] = current_time
            user_base.at[boolean_variable[0], 'status'] = "Online"
            user_base.to_excel("User_base.xlsx")
    count_of_message(user_id)

@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    user_id = message.from_user.id
    if ban_chek(user_id) != 1:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Получить справку о функциональности бота", callback_data="feature list"))
        keyboard.add(types.InlineKeyboardButton(text="Сменить свой ник", callback_data="Change nickname"))
        await message.answer("Выберите один из следующих пунктов", reply_markup=keyboard)
        user_id = message.from_user.id
        time_update(user_id=user_id)
        count_of_message(user_id)

@dp.message_handler(commands=['func_menu'])
async def func_menu(message: types.Message):
    user_id = message.from_user.id
    admin_base = user_base['admin'].tolist()
    if ban_chek(user_id) != 1:
        user_id_base = user_base['id'].tolist()
        time_update(user_id=user_id)
        boolean_variable = -1
        while boolean_variable == -1:
            boolean_variable = [index for index in range(len(user_base)) if user_id_base[index] == user_id]
        if admin_base[boolean_variable[0]] == "NO":
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text="Какой сегодня день", callback_data="What day is today"))
            keyboard.add(types.InlineKeyboardButton(text="Подключить права администратора",callback_data="Connect administrator rights"))
            keyboard.add(types.InlineKeyboardButton(text="Подобрать фон для рабочего стола", callback_data="Image search"))
            await message.answer("Выберите одну из следующих функций", reply_markup=keyboard)
        elif admin_base[boolean_variable[0]] == "YES":
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text="Просмотреть базу данных о пользвателях", callback_data="view database"))
            keyboard.add(types.InlineKeyboardButton(text="Какой сегодня день", callback_data="What day is today"))
            keyboard.add(types.InlineKeyboardButton(text="Подобрать фон для рабочего стола", callback_data="Image search"))
            await message.answer("Выберите одну из следующих функций", reply_markup=keyboard), time_update(user_id=user_id)
        count_of_message(user_id)

@dp.callback_query_handler(text="What day is today")
async def What_day_is_today(call: types.CallbackQuery):
    user_id = call.from_user.id
    if ban_chek(user_id) != 1:
        time_update(user_id=user_id)
        url = 'https://my-calend.ru/holidays/'
        response = requests.get(url)
        page = BeautifulSoup(response.text, "lxml").text
        page = page[(page.find('Праздники сегодня ') + 22):page.find('Именины отмечают')]
        dictionary = {"\xa0": "", "   ": "\n", "    ": "\n", "0": "", "1": "", "2": "", "3": "", "4": "","5": "", "6": "", "7": "", "8": "", "9": "", "  ": "", "\n ": "\n" , " день": "" }
        page = multiple_replace(page, dictionary)
        await call.message.answer(f"Сегодня: \n {page}"), await call.message.answer("/start\n/help\n/dice\n/func_menu"), time_update(user_id=user_id)
        count_of_message(user_id)

@dp.callback_query_handler(text="view database")
async def view_database(call: types.CallbackQuery):
    user_id = call.from_user.id
    if ban_chek(user_id) != 1:
        await call.message.answer(user_base), await call.message.answer("/start\n/help\n/dice\n/func_menu")


@dp.callback_query_handler(text="Connect administrator rights")
async def Connect_administrator_rights(call: types.CallbackQuery):
    user_id = call.from_user.id
    if ban_chek(user_id) != 1:
        await call.message.answer("Укажите пароль для получения прав Администратора")
        global con_adm_rig
        con_adm_rig = 1


@dp.callback_query_handler(text="feature list")
async def feature_list(call: types.CallbackQuery):
    user_id = call.from_user.id
    if ban_chek(user_id) != 1:
        await call.message.answer("Вот что я умею:\nотвечать на ваше приветсттвие\nПоказывать погоду в указаном вами городе\nБросать кубик через команду /dice\nРассказывать какой сегодня день\nПодбирать Обои для вашего рабочего стола"), await call.message.answer("/start\n/help\n/dice\n/func_menu")


@dp.callback_query_handler(text="Change nickname")
async def Change_nickname(call: types.CallbackQuery):
    user_id = call.from_user.id
    if ban_chek(user_id) != 1:
        await call.message.answer("В следующем сообщении укажите свой новый ник")
        global ch_log
        ch_log = 1


@dp.callback_query_handler(text="Image search")
async def Image_search(call: types.CallbackQuery):
    user_id = call.from_user.id
    if ban_chek(user_id) != 1:
        await call.message.answer("В следующем сообщении укажите ключевое слово по которому будет производиться поиск")
        global Im_sear
        Im_sear = 1


def multiple_replace(page, dictionary):
    for i, j in dictionary.items():
        page = page.replace(i, j)
    return page


@dp.message_handler()
async def processing_message(message: types.Message):
    global user_base, user_name_base, ch_log, con_adm_rig, Im_sear
    user_id = message.from_user.id
    user_id_base = user_base['id'].tolist()
    if ban_chek(user_id) != 1 or (user_id in user_id_base) == False:
        user_id_base = user_base['id'].tolist()
        user_name_base = user_base['name'].tolist()
        user_id = message.from_user.id
        index = [index for index in range(len(user_base)) if user_id_base[index] == user_id]
        if (user_id in user_id_base) == False:
            new_user = {'id': [user_id], 'name': [message.text], 'admin': ["NO"], 'message in 5 seconds': [0], 'ban': ["NO"]}
            df = pd.DataFrame(new_user, columns=['id', 'name', 'admin'])
            user_base = pd.concat([user_base, df], ignore_index=True, sort=False)
            user_base.to_excel("User_base.xlsx")
            await bot.send_message(message.from_user.id, "Отлично я успешно внёс вас в базу данных"), await bot.send_message(message.from_user.id, "/start\n/help\n/dice\n/func_menu"), time_update(user_id=user_id)
            count_of_message(user_id)
        elif ch_log == 1:
            user_base.at[index[0], 'name'] = message.text
            user_base.to_excel("User_base.xlsx")
            await bot.send_message(message.from_user.id, f"Отлично я успешно сменил ваш ник на {message.text}"), await bot.send_message(message.from_user.id, "/start\n/help\n/dice\n/func_menu")
            ch_log = 0
            count_of_message(user_id)
        elif con_adm_rig == 1:
            time_update(user_id=user_id)
            if message.text == ADMIN_PASS:
                user_base.at[index[0], 'admin'] = 'YES', user_base.to_excel("User_base.xlsx")
                await bot.send_message(message.from_user.id,"Вы успешно получили права администратора"), await bot.send_message(message.from_user.id, "/start\n/help\n/dice\n/func_menu")
            else: await bot.send_message(message.from_user.id, "Неверный пароль")
            con_adm_rig = 0, time_update(user_id=user_id)
            count_of_message(user_id)
        elif Im_sear == 1:
            user_base.at[index[0], 'ban'] = "YES"
            time_update(user_id=user_id)
            images = 0
            switch = 1
            num_page = 1
            keyword = message.text
            ip = await ip_database_manager()
            proxies = {'http': f'http://{ip}'}
            await bot.send_message(message.from_user.id, "Начинаю искать подходящие картинки")
            while switch >= 1 and images != 10:
                link = f'https://zastavok.net'
                request = f'/search/{keyword}'
                url = f'{link}/{request}/{num_page}/'
                response = requests.get(url, proxies=proxies).text
                if ('ничего не найдено' in response) == False:
                    page = BeautifulSoup(response, "lxml")
                    block = page.find('div', class_='main')
                    num = page.find('div', id='clsLink3')
                    maximum_number_of_pages = num.find_all('a').__str__()
                    if maximum_number_of_pages[(maximum_number_of_pages.rfind("</a>,")) - 2] == '>':
                        maximum_number_of_pages = [int(maximum_number_of_pages[(maximum_number_of_pages.rfind("</a>,")) - 1]) if maximum_number_of_pages != '[]' else 1]
                    else:
                        maximum_number_of_pages = [int(maximum_number_of_pages[(maximum_number_of_pages.rfind("</a>,")) - 2:(maximum_number_of_pages.rfind("</a>,"))]) if maximum_number_of_pages != '[]' else 1]
                    Pictures = block.find_all('div', class_='short_full')
                    for image in Pictures:
                        chek = image.find('img').get('alt')
                        if ((f'{keyword} ' in chek) or (f'{keyword.lower()} ' in chek) or (keyword == chek) or (keyword.lower() == chek)):
                            switch += 1
                            break
                    if switch == 1:
                        switch = 0
                    if switch > 0:
                        if images == 0:
                            await bot.send_message(message.from_user.id, "Нашёл несколько интересных изображений по вашему запросу, сейчас перешлю вам")
                        for image in Pictures:
                            if images == 10:
                                break
                            chek = image.find('img').get('alt')
                            if ((f'{keyword} ' in chek) or (f'{keyword.lower()} ' in chek) or (keyword == chek) or (keyword.lower() == chek)) and images != 11:
                                image_link = image.find('a').get('href')
                                download = requests.get(f'{link}{image_link}').text
                                download_page = BeautifulSoup(download, 'lxml')
                                download_blok = download_page.find('div', class_='image_data').find('div', class_='block_down')
                                download_link = download_blok.find('a').get('href')
                                image_bytes = requests.get(f'{link}{download_link}').content
                                with open(f'picture/{chek}.jpg', 'wb') as file:
                                    file.write(image_bytes)
                                with open(f'picture/{chek}.jpg', 'rb') as photo:
                                    await bot.send_photo(chat_id=message.chat.id, photo=photo)
                                os.remove(f'picture/{chek}.jpg')
                                images += 1
                        if maximum_number_of_pages[0] == num_page:index = 0
                        else:num_page += 1
                    else:
                        await bot.send_message(message.from_user.id, "По вашему запросу ничего не найдено")
                        switch = 0
                else:
                    await bot.send_message(message.from_user.id, "По вашему запросу ничего не найдено")
                    switch = 0
            user_base.at[index[0], 'ban'] = "NO"
            user_base.to_excel("User_base.xlsx")
            await bot.send_message(message.from_user.id, "/start\n/help\n/dice\n/func_menu")
            count_of_message(user_id)
            Im_sear == 0
        elif message.text == "Привет" or message.text == "привет":
            status_base = user_base['status'].tolist()
            if status_base[index[0]] == 'Online':
                await bot.send_message(message.from_user.id, f"Привет {user_name_base[index[0]]}"), await bot.send_message(message.from_user.id, "/start\n/help\n/dice\n/func_menu")
            else:await bot.send_message(message.from_user.id,f"Привет {user_name_base[index[0]]} давно не виделись"),await bot.send_message(message.from_user.id, "/start\n/help\n/dice\n/func_menu"), time_update(user_id=user_id)
            count_of_message(user_id)
        elif "Погода в" in message.text:
            a = message.text[9:len(message.text)]
            morph = pymorphy2.MorphAnalyzer()
            a = morph.parse(a)[0].normal_form
            params = {"q": a, "appid": API_KEY, "units": "metric"}
            result = requests.get('https://api.openweathermap.org/data/2.5/weather', params=params)
            list = result.text
            time_update(user_id=user_id)
            if list != '{"cod":"404","message":"city not found"}':
                translator = Translator()
                description = translator.translate(list[(list.find("main") + 6):(list.find("description") - 2)], src='en',dest='ru')
                temp = translator.translate((list[(list.find("temp") + 5):(list.find("feels_like") - 2)]), src='en',dest='ru')
                wind = translator.translate(list[(list.find("wind") + 7):(list.find("deg") - 2)], src='en', dest='ru')
                result = f"Погода: {description.text}  \nТемпература: {temp.text} C \nВетер:{wind.text} м/с"
                await bot.send_message(message.from_user.id, result), await bot.send_message(message.from_user.id, "/start\n/help\n/dice\n/func_menu")
            else:
                await bot.send_message(message.from_user.id, "Город не найден"), await bot.send_message(message.from_user.id, "/start\n/help\n/dice\n/func_menu")
            count_of_message(user_id)
        elif message.text == ADMIN_PASS:
            return 1
            count_of_message(user_id)
        elif (user_id in user_id_base) != False:
            await bot.send_message(message.from_user.id, 'непонял вас'), await bot.send_message(message.from_user.id, "/start\n/help\n/dice\n/func_menu"), time_update(user_id=user_id)
            count_of_message(user_id)


def base_call(id, message):
    conn = psycopg2.connect(user="bot",password="7961dee7X1",database="postgres_db", host='localhost')
    print("Database opened successfully")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM airport LIMIT 10')
    records = cursor.fetchall()
    print(records)
    cursor.close()
    conn.close()


def ban_chek(id):
    global user_base
    user_id_base = user_base['id'].tolist()
    if (id in user_id_base) == True:
        ban_base = user_base['ban'].tolist()
        boolean_variable = [index for index in range(len(user_base)) if user_id_base[index] == id]
        if ban_base[boolean_variable[0]] != "YES":return 0
        else:return 1
    else:return 0
def count_of_message (id):
    global user_base
    user_id_base = user_base['id'].tolist()
    boolean_variable = [index for index in range(len(user_base)) if user_id_base[index] == id]
    user_base.at[boolean_variable[0], 'message in 5 seconds'] += 1
    user_base.to_excel("User_base.xlsx")


async def spam_chek ():
    global user_base
    while True:
        speed = user_base['message in 5 seconds'].tolist()
        ban_list = user_base['ban'].tolist()
        id_list = user_base['id'].tolist()
        for index in range(len(speed)):
            if ban_list[index] != "YES":
                if speed[index] >= 15:
                    user_base.at[index, 'ban'] = "YES"
                    await send_message(id_list[index], "Вы получили бан , бот с вами больше не общается")
                    user_base.at[index, 'message in 5 seconds'] = 0
                    user_base.to_excel("User_base.xlsx")
                else:
                    user_base.at[index, 'message in 5 seconds'] = 0
                    user_base.to_excel("User_base.xlsx")
        await asyncio.sleep(5)



async def send_message(id ,message):
    await bot.send_message(id,message)

async def get_new_ip_list():
    global ip_list
    request = 'https://free-proxy-list.net'
    response = requests.get(request).text
    ip_list_string = response[(response.find('UTC.\n') + 6):(response.find('</textarea>'))]
    for element in range(0, ip_list_string.count('\n')):
        ip_list.append(ip_list_string[0:ip_list_string.find('\n')])
        ip_base.at[element, 'ip_list'] = ip_list[element]
        print(ip_list[element])
        ip_list_string = ip_list_string[(ip_list_string.find('\n')) + 2:len(ip_list_string)]
    ip_base.to_excel("ip_base.xlsx")


async def ip_database_manager():
    global ip_list, element
    element += 1
    ip_base.at[0,'number_ip'] =element
    ip_base.to_excel("ip_base.xlsx")
    if ip_list[0] == -1 or element == len(ip_list):
        await get_new_ip_list()
        element = -1
        ip_base.at[0, 'number_ip'] = element
        ip_base.to_excel("ip_base.xlsx")
    return ip_list[element]


async def status_chek():
    while True:
        now = datetime.now()
        print(f"status_chek started:{str(now)}")
        current_time_minutes = int(now.strftime("%M"))
        current_time_hour = int(now.strftime("%H"))
        current_time_date = int(now.strftime("%d"))
        global user_base
        time_base = user_base['last call'].tolist()
        for index in range(len(time_base)):
            time_1 = int((time_base[index][6]) + (time_base[index][7]))
            time_2 = int((time_base[index][3]) + (time_base[index][4]))
            time_3 = int((time_base[index][0]) + (time_base[index][1]))
            if time_3 < current_time_date:
                user_base.at[index, 'status'] = "offline"
                user_base.to_excel("User_base.xlsx")
            elif time_1 < current_time_minutes:
                if (current_time_minutes - time_1 >= 30):
                    user_base.at[index, 'status'] = "offline"
                    user_base.to_excel("User_base.xlsx")
                elif time_2 < current_time_hour:
                    if (current_time_hour - time_2 >= 1):
                        user_base.at[index, 'status'] = "offline"
                        user_base.to_excel("User_base.xlsx")
                else:
                    user_base.at[index, 'status'] = "Online"
                    user_base.to_excel("User_base.xlsx")
        await send_message(1258306656, "status_chek completed:" + str(now))
        now = datetime.now()
        print(f"status_chek completed: {str(now)}")
        await asyncio.sleep(60 * 30)


if __name__ == '__main__':
    myloop = asyncio.new_event_loop()
    myloop.create_task(status_chek())
    myloop.create_task(spam_chek())
    myloop.create_task(dp.start_polling())
    myloop.run_forever()
