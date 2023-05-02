from unittest.mock import AsyncMock

import pytest
from aiogram import types
from telegram_bot.handlers.link_sender_mail import sender_email_inputed
from telegram_bot.keyboards.link_sender_kb import link_sender_kb
from telegram_bot.keyboards.main_kb import main_kb
from telegram_bot.services.notification import get_notification_requests
from telegram_bot.templates import messages
from telegram_bot.tests.mock_service.api_service import ApiRequestsMock


class TestSenderHandler:
    @pytest.mark.asyncio
    async def test_sender_email_inputed_201(
        self,
    ):
        mock_state = AsyncMock()
        mock_state.update_data = AsyncMock()
        message_mock = AsyncMock(spec=types.Message)
        await sender_email_inputed(
            message=message_mock,
            api_service=ApiRequestsMock(  # type: ignore
                status_code=201, data={"sender": {"email": "example@test.com"}}
            ),
            notification_service=get_notification_requests(),
            state=mock_state,
        )
        message_mock.answer.assert_called_once_with(
            "{}".join(messages.sender_connected).format("example@test.com"),
            reply_markup=main_kb,
        )

    @pytest.mark.asyncio
    async def test_sender_email_inputed_500(
        self,
    ):
        mock_state = AsyncMock()
        mock_state.update_data = AsyncMock()
        message_mock = AsyncMock(spec=types.Message)

        await sender_email_inputed(
            message=message_mock,
            api_service=ApiRequestsMock(status_code=500),  # type: ignore
            notification_service=get_notification_requests(),
            state=mock_state,
        )
        message_mock.answer.assert_called_once_with(
            " ".join(messages.connecting_failed), reply_markup=link_sender_kb
        )

    @pytest.mark.asyncio
    async def test_sender_email_inputed_400_email_exist(
        self,
    ):
        mock_state = AsyncMock()
        mock_state.ask_sender = AsyncMock()
        message_mock = AsyncMock(spec=types.Message)

        await sender_email_inputed(
            message=message_mock,
            api_service=ApiRequestsMock(  # type: ignore
                status_code=400, data={"email": ["Почта уже привязана"]}
            ),
            notification_service=get_notification_requests(),
            state=mock_state,
        )
        error = "email: Почта уже привязана"
        message_mock.answer.assert_called_once_with(error, reply_markup=link_sender_kb)

    @pytest.mark.asyncio
    async def test_sender_email_inputed_400_wrong_email(
        self,
    ):
        mock_state = AsyncMock()
        mock_state.ask_sender = AsyncMock()
        message_mock = AsyncMock(spec=types.Message)

        await sender_email_inputed(
            message=message_mock,
            api_service=ApiRequestsMock(  # type: ignore
                status_code=400,
                data={"email": ["Введите правильный адрес электронной почты."]},
            ),
            notification_service=get_notification_requests(),
            state=mock_state,
        )
        error = "email: Введите правильный адрес электронной почты."
        message_mock.answer.assert_called_once_with(error, reply_markup=link_sender_kb)
