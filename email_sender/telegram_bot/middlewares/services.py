from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from telegram_bot.handlers.services.list_handler_services import (
    get_mail_list_service,
    get_provider_list_service,
    get_sender_list_service,
)
from telegram_bot.services.api_request_service import get_api_requests
from telegram_bot.services.message import get_bot_message
from telegram_bot.services.notification import get_notification_requests


class ServicesMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    async def pre_process(self, obj, data, *args):
        data["api_service"] = get_api_requests()
        data["notification_service"] = get_notification_requests()
        data["messages_service"] = get_bot_message()
        data["mail_list_service"] = get_mail_list_service()
        data["sender_list_service"] = get_sender_list_service()
        data["provider_list_service"] = get_provider_list_service()
