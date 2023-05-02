from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from telegram_bot.keyboards.info import info_button

link_mail_cb = CallbackData("link_mail")

link_mail_kb = InlineKeyboardMarkup()
link_mail_button = InlineKeyboardButton(
    text="Добавить новый email", callback_data=link_mail_cb.new()
)


link_mail_kb.add(link_mail_button, info_button)
