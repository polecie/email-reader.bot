from unittest.mock import AsyncMock

import pytest
from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from telegram_bot.handlers.list import (
    list_button_press,
    list_elem_button_press,
    list_service_button_press,
)
from telegram_bot.tests.mock_service.api_service import ApiRequestsMock
from telegram_bot.tests.mock_service.list_mock_services import (
    MailListServiceMock,
    SenderListServiceMock,
)


@pytest.mark.asyncio
class TestListHandler:
    async def test_email_list_button_press(self):
        callback_mock = AsyncMock()
        callback_mock.data = "list_mails"
        state_mock = AsyncMock(spec=FSMContext)

        data = dict(
            count=2,
            next=None,
            previous=None,
            results=[
                {"id": 1, "email": "test@mail.ru"},
                {"id": 2, "email": "test2@mail.ru"},
            ],
        )

        await list_button_press(
            callback_mock,
            state_mock,
            MailListServiceMock(ApiRequestsMock(200, data=data)),  # type: ignore
            SenderListServiceMock(ApiRequestsMock(200, data=data)),  # type: ignore
        )

        callback_mock.message.answer.assert_called_once_with(
            "Ниже список ваших email-адресов, которые я отслеживаю.\n"
            "<u><strong>ВНИМАНИЕ:</strong></u> Если вы желаете прервать отслеживание какой либо вашей почты, "
            "просто нажмите на кнопку с нужным email-адресом.",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        {
                            "text": "test@mail.ru",
                            "callback_data": "list_elem:list_mails:1:test@mail.ru",
                        },
                        {
                            "text": "test2@mail.ru",
                            "callback_data": "list_elem:list_mails:2:test2@mail.ru",
                        },
                    ]
                ]
            ),
        )

    async def test_email_list_button_with_empty_list(self):
        callback_mock = AsyncMock()
        callback_mock.data = "list_mails"
        state_mock = AsyncMock(spec=FSMContext)

        data = dict(count=0, next=None, previous=None, results=[])

        await list_button_press(
            callback_mock,
            state_mock,
            MailListServiceMock(ApiRequestsMock(200, data=data)),  # type: ignore
            SenderListServiceMock(ApiRequestsMock(200, data=data)),  # type: ignore
        )

        callback_mock.message.answer.assert_called_once_with(
            "Вы пока еще не отслеживаете ни одного своего email-адреса. "
            "Добавьте пожалуйста ваш email, чтобы я смог начать работу с Вами."
        )

    async def test_sender_list_button_press(self):
        callback_mock = AsyncMock()
        callback_mock.data = "list_senders"
        state_mock = AsyncMock(spec=FSMContext)

        data = dict(
            count=1,
            next=None,
            previous=None,
            results=[{"id": 1, "email": "test@mail.ru"}],
        )

        await list_button_press(
            callback_mock,
            state_mock,
            MailListServiceMock(ApiRequestsMock(200, data=data)),  # type: ignore
            SenderListServiceMock(ApiRequestsMock(200, data=data)),  # type: ignore
        )

        callback_mock.message.answer.assert_called_once_with(
            "Ниже список отслеживаемых вами отправителей.\n"
            "<u><strong>ВНИМАНИЕ:</strong></u> Если вы желаете удалить отправителя из отслеживаемых, "
            "просто нажмите на кнопку с его email-адресом.",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        {
                            "text": "test@mail.ru",
                            "callback_data": "list_elem:list_senders:1:test@mail.ru",
                        }
                    ]
                ]
            ),
        )

    async def test_list_elem_button_press(self):
        testing_mail = "test@test.ru"

        callback_mock = AsyncMock()
        state_mock = FSMContext(MemoryStorage(), chat=123, user=123)

        await state_mock.update_data(
            {
                "list_service": MailListServiceMock(
                    ApiRequestsMock(200, data={"email": testing_mail})
                )
            }
        )

        await list_elem_button_press(callback_mock, {"main_value": "test"}, state_mock)

        callback_mock.message.answer.assert_called_once_with(
            f"Почта {testing_mail} успешно удалена из списка отслеживаемых!"
        )

    async def test_list_service_button_press(self):
        callback_mock = AsyncMock()
        state_mock = FSMContext(MemoryStorage(), chat=123, user=123)

        data = dict(
            count=2,
            next=None,
            previous=None,
            results=[
                {"id": 1, "email": "test@mail.ru"},
                {"id": 2, "email": "test2@mail.ru"},
            ],
        )

        msg_mock = AsyncMock(spec=types.Message)
        await state_mock.update_data(
            {
                "list_service": MailListServiceMock(ApiRequestsMock(200, data=data)),
                "message": msg_mock,
            }
        )

        await list_service_button_press(
            callback_mock, {"main_value": "test", "url": "some_test_url"}, state_mock
        )

        msg_mock.assert_not_awaited()
        callback_mock.assert_not_awaited()

    async def test_(self):
        pass
