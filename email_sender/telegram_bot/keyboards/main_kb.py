from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram_bot.keyboards.link_mail_kb import info_button, link_mail_button
from telegram_bot.keyboards.link_sender_kb import link_sender_button
from telegram_bot.keyboards.list_kb import list_mails_button, list_senders_button

menu_button_text = "Меню"
main_kb = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
main_kb.insert(KeyboardButton(text=menu_button_text))

menu_kb = InlineKeyboardMarkup(row_width=2)
menu_kb.insert(link_mail_button)
menu_kb.insert(link_sender_button)
menu_kb.insert(list_mails_button)
menu_kb.insert(list_senders_button)
menu_kb.add(info_button)
