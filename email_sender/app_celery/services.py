import asyncio
import datetime
import imaplib
import logging
import re
import uuid
from asyncio import Task
from email.parser import BytesHeaderParser, BytesParser
from typing import Any

import aioimaplib
from api.encrypt import EncryptionService, encryption_service
from app_celery.abstracts import AbstractMailService
from app_celery.mailsender_service import MailSender
from app_celery.schemes import Mail
from app_celery.utils import MAIL_FOLDER, STATE_AUTH
from playwright.async_api import async_playwright

ID_HEADER_SET = {"From", "To", "Date"}
FETCH_MESSAGE_DATA_UID = re.compile(rb".*UID (?P<uid>\d+).*")
FETCH_MESSAGE_DATA_FLAGS = re.compile(rb".*FLAGS \((?P<flags>.*?)\).*")


class MailService(AbstractMailService):
    """
    Основной класс для работы с почтой.

    :param mails: список email адресов (объекты типа Mail),
    которые необходимо проверить на наличие новых писем
    :param senders: список отслеживаемых адресов отправителей
    :param save_screen: Булевое значение, определяющее метод сохранения скрина
    - изображение(True) или код(False). По умолчанию False
    :param date: Дата, определяющая фильтрацию проверки новых писем.
    По умолчанию None - будут включены все новые письма
    :param timeout: int, таймоут ожидания для подключения к серверу. По умолчанию 10 секунд
    :param send_method: any - Сервис отправки сообщения. Это может быть телеграм бот,
    SMTP совместимый сервис или любой другой пользовательский сервис, способный принимать входящие файлы
    """

    def __init__(
        self,
        mails: list[Mail],
        senders: list[str],
        save_screen: bool = False,
        date: datetime.datetime = datetime.datetime(year=2000, day=1, month=1),
        timeout: int = 10,
        encrypt_method: EncryptionService = encryption_service,
        send_method: Any = None,
    ) -> None:
        self.mails = mails
        self.senders = senders
        self.save_screen = save_screen
        self.date = date
        self.timeout = timeout
        self.encrypt_method = encrypt_method
        self.mail_list: list[Task] = list()
        self.imap_client: aioimaplib.IMAP4_SSL = None  # type: ignore
        if send_method is None:
            raise NotImplementedError
        else:
            self.mail_sender_service: MailSender = send_method  # type: ignore
        self.errors: dict = dict()

    @classmethod
    def validate_mail(cls, mail: Mail) -> bool:
        """
        Метод проверки валидности введенных email, пароля и провайдера.
        Возвращает булевое значение True если подключение прошло успешно, иначе False

        ::return: bool
        """
        try:
            imap_client = imaplib.IMAP4_SSL(
                host=mail.provider["host"], port=mail.provider["port"]
            )
            imap_client.login(mail.email, str(mail.password))
            return True
        except Exception:
            return False

    def _connect_imap(self, host: str, port: int) -> None:
        """
        Метод для подключения к imap-серверу

        :param host: строка вида imap.server.com, адрес почтового сервера
        :param port: int, порт сервера
        """
        self.imap_client = aioimaplib.IMAP4_SSL(
            host=host, port=port, timeout=self.timeout
        )

    async def check_new_mails(self) -> None:
        """
        Метод проверки новых писем на отслеживаемых почтовых ящиках.

        """
        for mail in self.mails:
            try:
                self._connect_imap(
                    host=mail.provider["host"], port=mail.provider["port"]
                )
                await self.imap_client.wait_hello_from_server()
            except TimeoutError:
                logging.warning(msg=f"Timeout connect to {mail.provider['host']}")
                self.errors.get("timeout", []).append(mail.email)
                continue
            except Exception as err:
                logging.error(msg="Unknown error", exc_info=err)
                continue

            password = self.encrypt_method.decrypt(mail.password.encode())  # type: ignore
            await self.imap_client.login(mail.email, password)
            state = self.imap_client.get_state()
            if state != STATE_AUTH:
                await self.mail_sender_service.send_warning(
                    data={
                        "msg": f"Не удалось подключиться к почтовому ящику {mail.email}. "
                        f"Возможно, вы изменили пароль."
                    }
                )
                continue
            await self.imap_client.select("INBOX")
            await self._fetch_messages_headers(mail.email)
            if self.mail_list:
                await asyncio.wait(self.mail_list)
            self.mail_list.clear()
            await self.imap_client.close()

    async def _fetch_messages_headers(self, to_email: str) -> None:
        """
        Вспомогательный метод для считывания и обработки заголовков письма
        """
        response: aioimaplib.Response = await self.imap_client.uid(
            "fetch",
            "1:*",
            f'(UID FLAGS BODY.PEEK[HEADER.FIELDS ({" ".join(ID_HEADER_SET)})])',
        )
        for i in range(0, len(response.lines) - 1, 3):
            fetch_command_without_literal = b"%s %s" % (
                response.lines[i],
                response.lines[i + 2],
            )
            uid: int = int(
                FETCH_MESSAGE_DATA_UID.match(fetch_command_without_literal).group("uid")  # type: ignore
            )
            flags: bytes = FETCH_MESSAGE_DATA_FLAGS.match(  # type: ignore
                fetch_command_without_literal
            ).group("flags")

            if b"\\Seen" not in flags:
                message_headers = BytesHeaderParser().parsebytes(response.lines[i + 1])
                mail_date = re.search(  # type: ignore
                    r"\d{1,2} \w{3} \d{4}", message_headers["Date"]
                ).group(0)
                from_date = datetime.datetime.strptime(mail_date, "%d %b %Y")
                for sender in self.senders:
                    if sender in message_headers["From"] and from_date >= self.date:
                        await self.get_mail(
                            msg_id=uid, sender=sender, to_email=to_email
                        )

    async def get_mail(self, msg_id: int, sender: str, to_email: str) -> None:
        """
        Метод получения письма с идентификатором uid с почтового ящика to_email,
        от отправителя sender. Метод формирует список отложенных задач self.mail_list
        для скриншотов писем.

        :param msg_id: int - идентификатор письма
        :param sender: str - адрес отправителя
        :param to_email: str - адрес получателя
        """
        res = await self.imap_client.uid("fetch", str(msg_id), "(RFC822)")
        msg = BytesParser().parsebytes(res.lines[1])
        template: str = ""

        for part in msg.walk():
            if (
                part.get_content_maintype() in {"text", "html"}
                and not part.get_filename()
            ):
                template = part.get_payload(decode=True).decode()

        content: str = "".join(
            [
                f"<strong>From: {sender}</strong><br><strong>To: {to_email}</strong><br>",
                template,
            ]
        )
        self.mail_list.append(
            asyncio.create_task(self.generate_screenshot(content, to_email, msg_id))
        )
        await self.imap_client.uid("STORE", str(msg_id), "+FLAGS", r"\Seen")

    async def generate_screenshot(
        self, content: str, filename: str, msg_id: int
    ) -> None:
        """
        Метод сохранения скриншота письма.

        :param content: str - контент содержимого для рендера страницы письма
        :param filename: str - имя директории, куда будут сохраненые скриншоты,
        если save_screen=True.
        :param msg_id: int - id сообщения для скриншота
        """
        async with async_playwright() as p:
            browser = await p.firefox.launch()
            page = await browser.new_page()
            await page.set_content(content)
            if self.save_screen:
                await page.screenshot(
                    path=f"{MAIL_FOLDER}/{filename}/{uuid.uuid4()}.png",
                    full_page=True,
                )
            else:
                result = await page.screenshot(full_page=True)
                flag: str = "+FLAGS"
                if not await self.mail_sender_service.send_photo(result):
                    flag = "-FLAGS"
                    await self.mail_sender_service.send_warning(
                        data={"msg": "Возникла ошибка при отправке скриншота."}
                    )
                await self.imap_client.uid("STORE", str(msg_id), flag, r"\Seen")
            await browser.close()

    @property
    def get_errors(self) -> dict:
        return self.errors

    def run(self) -> None:
        """
        Метод запуска сервиса
        """
        asyncio.new_event_loop().run_until_complete(self.check_new_mails())
