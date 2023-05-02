from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

link_sender_cb = CallbackData("link_sender")

link_sender_kb = InlineKeyboardMarkup(row_width=2)
link_sender_button = InlineKeyboardButton(
    text="Добавить email отправителя", callback_data=link_sender_cb.new()
)
link_sender_kb.add(link_sender_button)
