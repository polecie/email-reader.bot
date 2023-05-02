import random
from dataclasses import dataclass
from functools import lru_cache

from telegram_bot.templates import messages


@dataclass
class BotMessage:
    message: str


class BotMessageService:
    def _get_message(self, messages: list) -> str:
        return random.choice(messages)

    async def ask_sender(self) -> BotMessage:
        return BotMessage(self._get_message(messages.ask_sender))

    async def ask_password(self) -> BotMessage:
        return BotMessage(self._get_message(messages.ask_password))

    async def ask_email(self) -> BotMessage:
        return BotMessage(self._get_message(messages.ask_email))

    async def get_about_message(self) -> BotMessage:
        return BotMessage(self._get_message(messages.useful_info))


@lru_cache
def get_bot_message() -> BotMessageService:
    return BotMessageService()
