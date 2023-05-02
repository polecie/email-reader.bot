from aiogram import types
from telegram_bot.services.message import get_bot_message

bot_message_service = get_bot_message()


async def info_button_press(call: types.CallbackQuery):
    """
    Обработчик кнопки запроса информации
    """
    bot_answer = await bot_message_service.get_about_message()
    await call.message.answer(bot_answer.message)
