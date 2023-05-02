from aiogram import types
from aiogram.dispatcher import FSMContext
from telegram_bot.keyboards.link_sender_kb import link_sender_kb
from telegram_bot.keyboards.main_kb import main_kb
from telegram_bot.services.api_request_service import ApiRequests
from telegram_bot.services.message import BotMessageService
from telegram_bot.services.notification import BotNotificationService
from telegram_bot.states.states import AskSender


async def ask_sender_email(
    call: types.CallbackQuery, state: FSMContext, messages_service: BotMessageService
):
    """
    Обработчик нажатия кнопки привязки отправителя
    """
    bot_answer = await messages_service.ask_sender()
    await call.message.answer(bot_answer.message)
    await state.set_state(AskSender.ask_email.state)


async def sender_email_inputed(
    message: types.Message,
    state: FSMContext,
    api_service: ApiRequests,
    notification_service: BotNotificationService,
):
    """
    Обработчик введенной почты отправителя
    """
    response = await api_service.post_sender_mail(message.from_user.id, message.text)
    customized_response = await notification_service.connect_sender(response)
    await state.finish()

    if customized_response.status:
        await message.answer(customized_response.message, reply_markup=main_kb)
    else:
        await message.answer(customized_response.message, reply_markup=link_sender_kb)
