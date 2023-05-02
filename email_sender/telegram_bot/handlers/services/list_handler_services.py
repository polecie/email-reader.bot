from abc import ABC, abstractmethod
from functools import lru_cache

from aiogram import types
from aiogram.dispatcher import FSMContext
from telegram_bot.keyboards.list_kb import create_list_kb
from telegram_bot.services.api_request_service import get_api_requests
from telegram_bot.services.message import get_bot_message
from telegram_bot.services.notification import CustomResponse, get_notification_requests
from telegram_bot.states.states import AskCreds, ListChoiceWait


class BaseListService(ABC):
    """
    Абстрактный класс для работы со списковым представлением
    """

    list_state = ListChoiceWait.element_choice.state

    def __init__(self):
        self.api_requests = get_api_requests()
        self.notification_service = get_notification_requests()
        self.bot_message_service = get_bot_message()

    @abstractmethod
    async def list_api_request(
        self, id: int | None = None, url: str | None = None
    ) -> CustomResponse:
        """
        Обращение к Api для получения списка данных
        """

    @abstractmethod
    async def list_button_press(
        self, call: types.CallbackQuery, state: FSMContext
    ) -> None:
        """
        Обработка нажатия на кнопку выдачи списка
        """

    @abstractmethod
    async def list_elem_button_press(
        self, call: types.CallbackQuery, callback_data: dict, state: FSMContext
    ) -> None:
        """
        Обработка нажатия кнопки с элементом списка
        """

    @abstractmethod
    async def list_service_button_press(
        self, call: types.CallbackQuery, callback_data: dict, state: FSMContext
    ) -> None:
        """
        Обработка нажатия сервисной кнопки списк (вперед/назад)
        """


class MailListService(BaseListService):
    action: str = "list_mails"

    async def list_api_request(
        self, id: int | None = None, url: str | None = None
    ) -> CustomResponse:
        response = await self.api_requests.get_mails_list_request(id, url)
        customized_response = await self.notification_service.get_mails(response)
        return customized_response

    async def delete_api_request(self, id: int, main_value: str) -> CustomResponse:
        """
        Обращение к API с запросом на удлаение выбранного объекта списка
        """
        response = await self.api_requests.delete_mail_request(id, main_value)
        customized_response = await self.notification_service.delete_email(response)
        return customized_response

    async def list_button_press(self, call: types.CallbackQuery, state: FSMContext):
        customized_response = await self.list_api_request(call.from_user.id)
        if customized_response.status:
            new_kb = await create_list_kb(customized_response.data, self.action)
            await state.set_state(self.list_state)
            message = await call.message.answer(
                customized_response.message,
                reply_markup=new_kb,
            )
            await state.update_data(message=message)
            await state.update_data(list_service=self)
        else:
            await call.message.answer(
                customized_response.message,
            )

    async def list_elem_button_press(
        self, call: types.CallbackQuery, callback_data: dict, state: FSMContext
    ):
        main_value: str = callback_data["main_value"]
        customized_response = await self.delete_api_request(
            call.from_user.id, main_value
        )

        await state.finish()
        await call.message.answer(customized_response.message)

    async def list_service_button_press(
        self, call: types.CallbackQuery, callback_data: dict, state: FSMContext
    ):
        state_data = await state.get_data()
        url: str = callback_data["url"]
        message_with_list: types.Message = state_data.get("message")

        customized_response = await self.list_api_request(call.from_user.id, url)
        if customized_response.status:
            new_kb = await create_list_kb(customized_response.data, self.action)
            await message_with_list.edit_text(
                message_with_list.text, reply_markup=new_kb
            )
        else:
            await state.finish()
            await message_with_list.edit_text(message_with_list.text)


class SenderListService(MailListService):
    action: str = "list_senders"

    async def list_api_request(
        self, id: int | None = None, url: str | None = None
    ) -> CustomResponse:
        response = await self.api_requests.get_senders_list_request(id, url)
        customized_response = await self.notification_service.get_senders(response)
        return customized_response

    async def delete_api_request(self, id: int, main_value: str) -> CustomResponse:
        response = await self.api_requests.delete_sender_request(id, main_value)
        customized_response = await self.notification_service.delete_sender(response)
        return customized_response


class ProviderListService(MailListService):
    action: str = "link_mail"

    async def _ask_email(
        self, call: types.CallbackQuery, callback_data: dict, state: FSMContext
    ):
        """
        Обработчик кнопки с привязкой почты пользователя
        """
        bot_answer = await self.bot_message_service.ask_email()
        await call.message.answer(bot_answer.message)
        await state.set_state(AskCreds.waiting_for_email.state)
        provider_id: int = callback_data["id"]
        await state.update_data(provider_id=provider_id)

    async def list_api_request(
        self, id: int | None = None, url: str | None = None
    ) -> CustomResponse:
        response = await self.api_requests.get_providers_list_request(url)
        customized_response = await self.notification_service.get_providers(response)
        return customized_response

    async def list_elem_button_press(
        self, call: types.CallbackQuery, callback_data: dict, state: FSMContext
    ):
        await state.finish()
        await self._ask_email(call, callback_data, state)


@lru_cache
def get_mail_list_service() -> MailListService:
    return MailListService()


@lru_cache
def get_sender_list_service() -> SenderListService:
    return SenderListService()


@lru_cache
def get_provider_list_service() -> ProviderListService:
    return ProviderListService()
