from unittest.mock import AsyncMock

import pytest
from aiogram import types
from telegram_bot.handlers.commands import start_bot
from telegram_bot.keyboards.link_mail_kb import link_mail_kb
from telegram_bot.keyboards.main_kb import main_kb
from telegram_bot.services.notification import get_notification_requests
from telegram_bot.templates import messages
from telegram_bot.tests.mock_service.api_service import ApiRequestsMock


@pytest.mark.asyncio
class TestStartHandler:
    async def test_start_bot_201(
        self,
    ):
        message_mock = AsyncMock(spec=types.Message)
        message_mock.from_user = types.User(
            id=123456, first_name="qwerty", last_name=None
        )

        await start_bot(
            message=message_mock,
            api_service=ApiRequestsMock(status_code=201),  # type: ignore
            notification_service=get_notification_requests(),
        )
        message_mock.reply.assert_called_once_with(
            " ".join(messages.new_user_greeting), reply_markup=link_mail_kb
        )

    async def test_start_bot_500(
        self,
    ):
        message_mock = AsyncMock(spec=types.Message)
        message_mock.from_user = types.User(
            id=123456, first_name="qwerty", last_name=None
        )

        await start_bot(
            message=message_mock,
            api_service=ApiRequestsMock(status_code=500),  # type: ignore
            notification_service=get_notification_requests(),
        )
        message_mock.reply.assert_called_once_with(
            " ".join(messages.connecting_failed),
            # server_error or connecting_failed
            reply_markup=main_kb,
        )

    async def test_start_bot_400(
        self,
    ):
        message_mock = AsyncMock(spec=types.Message)
        message_mock.from_user = types.User(
            id=123456, first_name="qwerty", last_name=None
        )

        await start_bot(
            message=message_mock,
            api_service=ApiRequestsMock(status_code=400),  # type: ignore
            notification_service=get_notification_requests(),
        )
        message_mock.reply.assert_called_once_with(
            " ".join(messages.user_greeting), reply_markup=main_kb
        )
