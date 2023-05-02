from unittest.mock import AsyncMock

import pytest
from aiogram import types
from telegram_bot.handlers.link_mail import mail_inputed, password_inputed
from telegram_bot.keyboards.link_mail_kb import link_mail_kb
from telegram_bot.keyboards.link_sender_kb import link_sender_kb
from telegram_bot.services.message import get_bot_message
from telegram_bot.services.notification import get_notification_requests
from telegram_bot.templates import messages
from telegram_bot.tests.mock_service.api_service import ApiRequestsMock


class TestMailHandler:
    @pytest.mark.asyncio
    async def test_mail_inputed(
        self,
    ):
        mock_state = AsyncMock()
        mock_state.update_data = AsyncMock()
        message_mock = AsyncMock(spec=types.Message)
        await mail_inputed(
            message=message_mock, messages_service=get_bot_message(), state=mock_state
        )
        message_mock.answer.assert_called_once_with(" ".join(messages.ask_password))

    @pytest.mark.asyncio
    async def test_password_inputed_201(
        self,
    ):
        mock_state = AsyncMock()
        mock_state.update_data = AsyncMock()
        message_mock = AsyncMock(spec=types.Message)
        await password_inputed(
            message=message_mock,
            api_service=ApiRequestsMock(  # type: ignore
                status_code=201,
                data={
                    "user_id": 123456,
                    "provider_id": 1,
                    "email": {"email": "example@test.com"},
                    "password": "password",
                },
            ),
            notification_service=get_notification_requests(),
            state=mock_state,
        )
        message_mock.answer.assert_called_once_with(
            "{}".join(messages.email_connected).format("example@test.com"),
            reply_markup=link_sender_kb,
        )

    @pytest.mark.asyncio
    async def test_password_inputed_500(
        self,
    ):
        mock_state = AsyncMock()
        mock_state.update_data = AsyncMock()
        message_mock = AsyncMock(spec=types.Message)

        await password_inputed(
            message=message_mock,
            api_service=ApiRequestsMock(status_code=500),  # type: ignore
            notification_service=get_notification_requests(),
            state=mock_state,
        )
        message_mock.answer.assert_called_once_with(
            " ".join(messages.connecting_failed), reply_markup=link_mail_kb
        )

    @pytest.mark.asyncio
    async def test_password_inputed_400_wrong_email(
        self,
    ):
        mock_state = AsyncMock()
        mock_state.update_data = AsyncMock()
        message_mock = AsyncMock(spec=types.Message)

        await password_inputed(
            message=message_mock,
            api_service=ApiRequestsMock(  # type: ignore
                status_code=400,
                data={"email": ["Введите правильный адрес электронной почты."]},
            ),
            notification_service=get_notification_requests(),
            state=mock_state,
        )
        error = "email: Введите правильный адрес электронной почты."
        message_mock.answer.assert_called_once_with(error, reply_markup=link_mail_kb)

    @pytest.mark.asyncio
    async def test_password_inputed_400_email_exist(
        self,
    ):
        mock_state = AsyncMock()
        mock_state.update_data = AsyncMock()
        message_mock = AsyncMock(spec=types.Message)

        await password_inputed(
            message=message_mock,
            api_service=ApiRequestsMock(  # type: ignore
                status_code=400,
                data={"email": ["Почта с таким Электронный адрес уже существует."]},
            ),
            notification_service=get_notification_requests(),
            state=mock_state,
        )
        error = "email: Почта с таким Электронный адрес уже существует."
        message_mock.answer.assert_called_once_with(error, reply_markup=link_mail_kb)

    @pytest.mark.asyncio
    async def test_password_inputed_400_provider_not_found(
        self,
    ):
        mock_state = AsyncMock()
        mock_state.update_data = AsyncMock()
        message_mock = AsyncMock(spec=types.Message)

        await password_inputed(
            message=message_mock,
            api_service=ApiRequestsMock(  # type: ignore
                status_code=400,
                data={
                    "detail": [
                        "Найти подходящий почтовый сервис не удалось, "
                        "Проверьте еще раз, нет ли нужного вам провайдера в списке или обратитесь к администратору"
                    ]
                },
            ),
            notification_service=get_notification_requests(),
            state=mock_state,
        )
        error = (
            "detail: Найти подходящий почтовый сервис не удалось, "
            "Проверьте еще раз, нет ли нужного вам провайдера в списке или обратитесь к администратору"
        )
        message_mock.answer.assert_called_once_with(error, reply_markup=link_mail_kb)
