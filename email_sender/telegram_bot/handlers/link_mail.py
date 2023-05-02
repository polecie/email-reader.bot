from aiogram import types
from aiogram.dispatcher import FSMContext
from telegram_bot.handlers.services.list_handler_services import ProviderListService
from telegram_bot.keyboards.link_mail_kb import link_mail_kb
from telegram_bot.keyboards.link_sender_kb import link_sender_kb
from telegram_bot.services.api_request_service import ApiRequests
from telegram_bot.services.message import BotMessageService
from telegram_bot.services.notification import BotNotificationService
from telegram_bot.states.states import AskCreds


async def ask_provider(
    call: types.CallbackQuery,
    state: FSMContext,
    provider_list_service: ProviderListService,
):
    await provider_list_service.list_button_press(call, state)


async def mail_inputed(
    message: types.Message, state: FSMContext, messages_service: BotMessageService
):
    """
    Обработчик ввода пароля привязываемой почты
    """
    await state.update_data(email=message.text)
    await state.set_state(AskCreds.ask_password.state)
    bot_answer = await messages_service.ask_password()
    await message.answer(bot_answer.message)


async def password_inputed(
    message: types.Message,
    state: FSMContext,
    api_service: ApiRequests,
    notification_service: BotNotificationService,
):
    """
    Обработчик полученных данных почты от пользователя
    """
    user_data = await state.get_data()
    mail = user_data.get("email")
    provider_id = user_data.get("provider_id")
    password = message.text
    user_id = message.from_user.id
    response = await api_service.post_mail_creds_request(
        user_id, provider_id, mail, password
    )
    customized_response = await notification_service.connect_email(response)

    await state.finish()
    if customized_response.status:
        await message.answer(
            customized_response.message,
            reply_markup=link_sender_kb,
        )
        await message.delete()
    else:
        await message.answer(customized_response.message, reply_markup=link_mail_kb)
