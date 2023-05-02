from aiogram import types
from aiogram.dispatcher import FSMContext
from telegram_bot.keyboards.link_mail_kb import link_mail_kb
from telegram_bot.keyboards.main_kb import main_kb
from telegram_bot.services.api_request_service import ApiRequests
from telegram_bot.services.notification import BotNotificationService, CustomResponse


async def start_bot(
    message: types.Message,
    api_service: ApiRequests,
    notification_service: BotNotificationService,
):
    """
    Обработчик команды /start - запуска бота
    """
    from_user = message.from_user

    response = await api_service.post_user_request(
        from_user.id, from_user.first_name, from_user.last_name
    )
    customized_response: CustomResponse = await notification_service.create_user(
        response
    )

    if customized_response.status:
        # todo: Возможно добавить проверки на наличие, хотя бы одной почты и адресата
        await message.reply(
            customized_response.message,
            reply_markup=link_mail_kb,
        )
    else:
        await message.reply(customized_response.message, reply_markup=main_kb)


async def cmd_cancel(message: types.Message, state: FSMContext):
    """
    Обработчик команды /cancel - прерывание действия
    """
    await state.finish()
    await message.answer("Действие прервано")
