import io
import logging
import os

from aiogram import Bot, types
from app_celery.mailsender_service.base import AbstractMailSender


class MailSender(AbstractMailSender):
    """
    Сервис отправки уведомлений и сообщений пользователю.
    Основное использование в параметрах почтового сервиса

    Имеет два метода:
     - send_photo(screenshot) - метод для отправки скриншота письма
     - send_warning(data) - метод для отправки уведомлений о сбое в работе системы
    """

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        self.bot_token = os.environ.get("API_TOKEN")
        self.screenshot_filename: str = "mail_screenshot.png"

    async def send_photo(self, screenshot: bytes) -> bool:
        """
        Метод для отправки сгенерированных скриншотов пользователю бота.

        :param screenshot: Список скриншот в виде байтовой строки.
        :return: bool - результат отправки(True/False)
        """
        success: bool = True
        bot = Bot(self.bot_token)

        try:
            await bot.send_document(
                chat_id=self.user_id,
                document=types.InputFile(
                    io.BytesIO(screenshot), self.screenshot_filename
                ),
            )
        except Exception as e:
            logging.error(
                "Ошибка при отправке скриншота письма пользователю {} - {}".format(
                    self.user_id, e.__str__()
                )
            )
            success = False
        finally:
            bot_session = await bot.get_session()
            await bot_session.close()

        return success

    async def send_warning(self, data: dict) -> bool:
        """
        Метод для отправки уведомлений пользователю бота.

        :param data: dict - Данные для формирования сообщения
        :return: bool - результат отправки(True/False)
        """
        success: bool = True
        bot = Bot(self.bot_token)

        try:
            await bot.send_message(
                chat_id=self.user_id,
                text=data.get(
                    "msg",
                    "Возникла непредвиденная ошибка при отправке скриншота письма.\n"
                    "Возможно письмо слишком большое. Рекомендуется проверить письмо напрямую",
                ),
            )
        except Exception as e:
            logging.error(
                "Ошибка при отправке скриншота письма пользователю {} - {}".format(
                    self.user_id, e.__str__()
                )
            )
            success = False
        finally:
            bot_session = await bot.get_session()
            await bot_session.close()

        return success
