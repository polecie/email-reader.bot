import os
from unittest.mock import AsyncMock

import pytest
from aiogram import types
from telegram_bot.handlers.info import info_button_press
from telegram_bot.handlers.menu import menu_button_press
from telegram_bot.keyboards.main_kb import menu_kb


@pytest.mark.asyncio
async def test_menu_button_press():
    message_mock = AsyncMock(spec=types.Message)
    await menu_button_press(message=message_mock)
    message_mock.reply.assert_called_once_with(
        "Доступные действия", reply_markup=menu_kb
    )


@pytest.mark.asyncio
async def test_info_button_press():
    mock_bot_message_service = AsyncMock()
    mock_bot_message_service.get_about_message = AsyncMock()
    mock_bot_message = AsyncMock()
    mock_bot_message.message = (
        "Данный бот предназначен и разработан с целью отслеживания сообщений"
        " с указанных email-адресов от добавленных Вами отправителей. "
        "Воспользуйтесь кнопкой <strong>МЕНЮ</strong> для вызова меню доступных команд. "
        "В случае если вы хотите отменить текущее действие, введите команду /cancel.\n"
        "По всем вопросам работы сервиса Вы можете обратиться к администрации, "
        f"написав письмо по адресу <u>{os.environ.get('DJANGO_SUPERUSER_EMAIL')}</u>"
    )
    mock_bot_message_service.get_about_message.return_value = mock_bot_message
    mock_callback_query = AsyncMock()
    mock_message = AsyncMock()
    mock_callback_query.message = mock_message

    info_button_press.bot_answer = await mock_bot_message_service.get_about_message()
    await info_button_press(mock_callback_query)

    mock_bot_message_service.get_about_message.assert_called_once()
    mock_callback_query.message.answer.assert_called_once_with(mock_bot_message.message)
