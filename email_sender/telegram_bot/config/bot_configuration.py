import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.filters import OrFilter
from aiogram.types import BotCommand
from telegram_bot.handlers.commands import cmd_cancel, start_bot
from telegram_bot.handlers.info import info_button_press
from telegram_bot.handlers.link_mail import ask_provider, mail_inputed, password_inputed
from telegram_bot.handlers.link_sender_mail import (
    ask_sender_email,
    sender_email_inputed,
)
from telegram_bot.handlers.list import (
    list_button_press,
    list_elem_button_press,
    list_service_button_press,
)
from telegram_bot.handlers.menu import menu_button_press
from telegram_bot.keyboards.info import info_cb
from telegram_bot.keyboards.link_mail_kb import link_mail_cb
from telegram_bot.keyboards.link_sender_kb import link_sender_cb
from telegram_bot.keyboards.list_kb import (
    list_elem_cb,
    list_mails_cb,
    list_senders_cb,
    list_service_cb,
)
from telegram_bot.keyboards.main_kb import menu_button_text
from telegram_bot.states.states import AskCreds, AskSender, ListChoiceWait

from ..middlewares.services import ServicesMiddleware
from .config import get_bot_config


class EmailReaderBot:
    """
    Класс для настройки бота: переключение режимов, регистрации хэнделров, устанвовки команд
    """

    def __init__(self):
        self.config = get_bot_config()

        if self.config.LOGGING_ON:
            logging.basicConfig(level=logging.INFO)

        self.bot = Bot(token=self.config.API_TOKEN, parse_mode=types.ParseMode.HTML)
        self.dispatcher = Dispatcher(self.bot, storage=MemoryStorage())

    async def _register_handlers(
        self,
    ) -> None:
        """
        Регистраци всех обработчиков
        """
        await self.__register_commands_handlers()
        await self.__register_link_mail_handlers()
        await self.__register_link_sender_mail_handlers()
        await self.__register_list_handlers()
        await self.__register_menu_handlers()
        await self.__register_info_handlers()

    async def __register_commands_handlers(
        self,
    ) -> None:
        """
        Регистрация обработчиков команд
        """

        self.dispatcher.register_message_handler(start_bot, commands=["start"])
        self.dispatcher.register_message_handler(
            cmd_cancel, commands="cancel", state="*"
        )

    async def __register_link_mail_handlers(
        self,
    ) -> None:
        """
        Регистрация обработчиков кнопок привязки почты
        """
        self.dispatcher.register_callback_query_handler(
            ask_provider, link_mail_cb.filter()
        )

        self.dispatcher.register_message_handler(
            mail_inputed, state=AskCreds.waiting_for_email
        )
        self.dispatcher.register_message_handler(
            password_inputed, state=AskCreds.ask_password
        )

    async def __register_link_sender_mail_handlers(
        self,
    ) -> None:
        """
        Регистрация обработчиков кнопок привязки отправителей
        """

        self.dispatcher.register_callback_query_handler(
            ask_sender_email, link_sender_cb.filter()
        )
        self.dispatcher.register_message_handler(
            sender_email_inputed, state=AskSender.ask_email
        )

    async def __register_list_handlers(
        self,
    ) -> None:
        """
        Регистрация обработчиков кнопок списка
        """
        self.dispatcher.register_callback_query_handler(
            list_button_press,
            OrFilter(list_senders_cb.filter(), list_mails_cb.filter()),
        )

        self.dispatcher.register_callback_query_handler(
            list_elem_button_press,
            list_elem_cb.filter(),
            state=ListChoiceWait.element_choice,
        )

        self.dispatcher.register_callback_query_handler(
            list_service_button_press,
            list_service_cb.filter(),
            state=ListChoiceWait.element_choice,
        )

    async def __register_menu_handlers(self) -> None:
        """
        Регистрация обработчика кнопок меню
        """
        self.dispatcher.register_message_handler(
            menu_button_press, Text(equals=menu_button_text)
        )

    async def __register_info_handlers(self) -> None:
        """
        Регистрация обработчиков кнопок с информацией
        """
        self.dispatcher.register_callback_query_handler(
            info_button_press, info_cb.filter()
        )

    def _register_middlewares(self):
        self.dispatcher.setup_middleware(ServicesMiddleware())

    async def _set_commands(
        self,
    ):
        """
        Добавление своих команд в бот
        """
        commands = [
            BotCommand(command="/cancel", description="Прервать текущее действие")
        ]
        await self.dispatcher.bot.set_my_commands(commands)

    async def _configure(
        self,
    ) -> None:
        """
        Настройка бота
        """
        if self.config.SKIP_UPDATES:
            await self.dispatcher.skip_updates()

        self._register_middlewares()
        await self._register_handlers()
        await self._set_commands()

    async def run(
        self,
    ) -> None:
        """
        Запуск бота
        """
        await self._configure()
        await self.dispatcher.start_polling()
