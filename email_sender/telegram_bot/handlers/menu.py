from aiogram import types
from telegram_bot.keyboards.main_kb import menu_kb


async def menu_button_press(message: types.Message):
    """
    Обработчик кнопки menu
    """
    await message.reply("Доступные действия", reply_markup=menu_kb)
