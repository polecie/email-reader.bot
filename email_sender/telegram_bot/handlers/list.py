from aiogram import types
from aiogram.dispatcher import FSMContext
from telegram_bot.handlers.services.list_handler_services import (
    BaseListService,
    MailListService,
    SenderListService,
)


async def list_button_press(
    call: types.CallbackQuery,
    state: FSMContext,
    mail_list_service: MailListService,
    sender_list_service: SenderListService,
):
    """
    Обработчик кнопики списка привязанных почт
    """
    list_service: BaseListService = sender_list_service

    if call.data == "list_mails":
        list_service = mail_list_service

    await list_service.list_button_press(call, state)


async def list_elem_button_press(
    call: types.CallbackQuery, callback_data: dict, state: FSMContext
):
    """
    Обработчик кнопки - элемента списка привязанных почт
    """
    state_data = await state.get_data()
    list_service: BaseListService = state_data.get("list_service")

    await list_service.list_elem_button_press(call, callback_data, state)


async def list_service_button_press(
    call: types.CallbackQuery, callback_data: dict, state: FSMContext
):
    """
    Обработчик сервисных кнопок спискового представления почт (вперед/назад)
    """
    state_data = await state.get_data()
    list_service: BaseListService = state_data.get("list_service")

    await list_service.list_service_button_press(call, callback_data, state)
