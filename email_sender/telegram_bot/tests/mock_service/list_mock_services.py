from aiogram import types
from aiogram.dispatcher import FSMContext
from telegram_bot.keyboards.list_kb import create_list_kb
from telegram_bot.services.message import get_bot_message
from telegram_bot.services.notification import CustomResponse, get_notification_requests
from telegram_bot.states.states import ListChoiceWait


class BaseListServiceMock:
    list_state = ListChoiceWait.element_choice.state

    def __init__(self, api_service):
        self.api_requests = api_service
        self.noticitaion_service = get_notification_requests()
        self.bot_message_service = get_bot_message()


class MailListServiceMock(BaseListServiceMock):
    """Mocked сервис для получения списка почт пользователя"""

    action: str = "list_mails"

    async def list_api_request(
        self, id: int | None = None, url: str | None = None
    ) -> CustomResponse:
        response = await self.api_requests.get_mails_list_request(id, url)
        customized_response = await self.noticitaion_service.get_mails(response)
        return customized_response

    async def delete_api_request(self, id: int, main_value: str) -> CustomResponse:
        response = await self.api_requests.delete_mail_request(id, main_value)
        customized_response = await self.noticitaion_service.delete_email(response)
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


class SenderListServiceMock(MailListServiceMock):
    """Mocked сервис для получения списка отслеживаемых почт пользователя"""

    action: str = "list_senders"

    async def list_api_request(
        self, id: int | None = None, url: str | None = None
    ) -> CustomResponse:
        response = await self.api_requests.get_senders_list_request(id, url)
        customized_response = await self.noticitaion_service.get_senders(response)
        return customized_response

    async def delete_api_request(self, id: int, main_value: str) -> CustomResponse:
        response = await self.api_requests.delete_sender_request(id, main_value)
        customized_response = await self.noticitaion_service.delete_sender(response)
        return customized_response
