import os
from functools import lru_cache

from dotenv import find_dotenv, load_dotenv


class BotConfig:
    """
    Класс для получения переменных конфигураций бота из окужения
    """

    def __init__(self):
        load_dotenv(find_dotenv(".env.dev"))
        self.API_TOKEN = os.getenv("API_TOKEN")

        self.SKIP_UPDATES = os.getenv("SKIP_UPDATES", True)
        self.LOGGING_ON = os.getenv("LOGGING_ON", True)

        self.USERS_URL = os.getenv("USERS_URL")
        self.LINK_MAIL_URL = os.getenv("LINK_MAIL_URL")
        self.LINK_SENDER_URL = os.getenv("LINK_SENDER_URL")
        self.LIST_MAILS_URL = os.getenv("LIST_MAILS_URL")
        self.LIST_SENDERS_URL = os.getenv("LIST_SENDERS_URL")
        self.LIST_PROVIDERS_URL = os.getenv("LIST_PROVIDERS_URL")


@lru_cache
def get_bot_config() -> BotConfig:
    return BotConfig()
