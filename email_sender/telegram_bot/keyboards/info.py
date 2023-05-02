from aiogram.types import InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

info_cb = CallbackData("info")
info_button = InlineKeyboardButton(text="Подсказки", callback_data=info_cb.new())
