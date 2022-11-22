from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from config import TOKEN
from config import API_KEY

import requests
from bs4 import BeautifulSoup

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Приветствую я бот Grek чем я могу вам помочь ? \n Для получения справки ввидите команду \help ")

@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Вот что я умею:\nотвечать на ваше приветсттвие")

@dp.message_handler()
async def processing_message(message: types.Message):
    if message.text == "Привет":
      await bot.send_message(message.from_user.id,'Привет')
    elif "Погода в" in message.text:
       a =  message.text[9:len(message.text)]
       params = {"q": a,"appid":API_KEY,"units":"metric"}
       res = requests.get('https://api.openweathermap.org/data/2.5/weather',params = params)
       list = res.text
       #await bot.send_message(message.from_user.id, list)
       if list != '{"cod":"404","message":"city not found"}':
        res = "Погода:" + list[(list.find("main") + 6):(list.find("description")-2)] + "\nТемпература:" + list[(list.find("temp") + 7):(list.find("pressure")-2)] + "\nВетер:"+ list[(list.find("wind") + 7):(list.find("deg")+8)]
        await bot.send_message(message.from_user.id,res)
       else:
           await bot.send_message(message.from_user.id, "Город не найден")
    else:
        await bot.send_message(message.from_user.id, 'непонял вас')

if __name__ == '__main__':
    executor.start_polling(dp)