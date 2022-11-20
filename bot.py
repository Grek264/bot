from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from config import TOKEN


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет!")

@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("я могу: отвечать на ваше приветсттвие")

@dp.message_handler()
async def hello_message(message: types.Message):
    if message.text == "Привет":
      await bot.send_message(message.from_user.id,'Привет')
    else:
        await bot.send_message(message.from_user.id, 'непонял вас')


if __name__ == '__main__':
    executor.start_polling(dp)