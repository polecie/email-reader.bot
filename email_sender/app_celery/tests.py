import os
import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock

from aioimaplib import Response
from api.encrypt import EncryptionService
from app_celery.mailsender_service import AbstractMailSender
from app_celery.schemes import Mail
from app_celery.services import MailService
from app_celery.utils import MAIL_FOLDER, STATE_AUTH
from django.conf import settings


class TestResult:
    """
    Тестовый класс, имитирующий новые входящие письма
    """

    def __init__(self):
        self.lines = [
            b"1 FETCH (UID 1 FLAGS () BODY[HEADER.FIELDS (To Date From)] {1}",
            bytearray(
                b"From: test_sender1@example.com\r\nTo: test@example.com\r\n"
                b"Date: 1 Nov 2022 13:55:15 +0100\r\n\r\n"
            ),
            b")",
            b"1 FETCH (UID 2 FLAGS () BODY[HEADER.FIELDS (To Date From)] {2}",
            bytearray(
                b"From: test_sender3@example.com\r\nTo: test@example.com\r\n"
                b"Date: 1 Nov 2022 16:55:15 +0100\r\n\r\n"
            ),
            b")",
        ]


class FakeEncrypt(EncryptionService):
    """
    Фейковый сервис шифроыки паролей
    """

    def decrypt(self, password: str) -> str:  # type: ignore
        return password

    def encrypt(self, password: str) -> str:
        return password


class MockMailService(MailService):
    """
    Модифиуированный почтовый сервис с имитацией подключения к imap
    """

    def _connect_imap(self, host: str, port: int) -> None:
        pass


class FakeMailSender(AbstractMailSender):
    """
    Фейковый сервис отправки сообщений и уведомлений пользователю
    """

    def __init__(self, user_id: int = 1111) -> None:
        self.user_id = user_id

    async def send_photo(self, screenshot: bytes) -> bool:
        return True

    async def send_warning(self, data: dict) -> bool:
        return True


class TestMailService(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.test_content = "<html><body><p>Test content</p></body></html>"
        self.test_email = "test@example.com"
        self.test_msg_id = 1
        self.test_sender = "test_sender1@example.com"

        self.mock_imap_client = MagicMock("aioimaplib.IMAP_SSL")
        self.mock_imap_client.wait_hello_from_server = AsyncMock()
        self.mock_imap_client.login = AsyncMock(
            return_value=Response(result="OK", lines=[])
        )
        self.mock_imap_client.get_state = Mock(return_value=STATE_AUTH)
        self.mock_imap_client.select = AsyncMock()
        self.mock_imap_client.uid = AsyncMock(return_value=TestResult())
        self.mock_imap_client.wait_hello_from_server = AsyncMock()
        self.mock_imap_client.close = AsyncMock()

        self.mail_service = MailService(
            [], [], save_screen=False, date=datetime.now(), send_method=FakeMailSender()
        )
        self.mail_service.imap_client = self.mock_imap_client

    async def test_check_new_mails(self):
        """
        Интеграционный тест почтового сервиса
        """
        test_mails = [
            Mail(
                email="test@example.com",
                password="password",
                provider={"host": "imap.example.com", "port": 993},
            )
        ]
        test_senders = ["test_sender1@example.com", "test_sender2@example.com"]
        test_date = datetime(year=2000, month=1, day=1)
        mail_service = MockMailService(
            mails=test_mails,
            senders=test_senders,
            save_screen=False,
            date=test_date,
            encrypt_method=FakeEncrypt(),
            send_method=FakeMailSender(),
        )
        mail_service.imap_client = self.mock_imap_client
        await mail_service.check_new_mails()
        self.mock_imap_client.uid.assert_called_with("STORE", "1", "+FLAGS", r"\Seen")
        with self.assertRaises(AssertionError):
            self.mock_imap_client.uid.assert_called_with(
                "STORE", "2", "+FLAGS", r"\Seen"
            )

    async def test_get_mail(self):
        """
        Тестирование получения письма
        """
        await self.mail_service.get_mail(
            self.test_msg_id, self.test_sender, self.test_email
        )
        self.assertTrue(len(self.mail_service.mail_list) == 1)

    async def test_generate_screenshot_bytes(self):
        """
        Тестирование генерации скриншота в виде байтовой строки
        с последующей отправкой пользователю
        """
        await self.mail_service.generate_screenshot(
            self.test_content, self.test_email, self.test_msg_id
        )
        self.mock_imap_client.uid.assert_called_with("STORE", "1", "+FLAGS", r"\Seen")
        with self.assertRaises(AssertionError):
            self.mock_imap_client.uid.assert_called_with(
                "STORE", "2", "+FLAGS", r"\Seen"
            )

    async def test_generate_screenshot_png(self):
        """
        Тестирование генерации скриншота и сохранение как файла
        """
        self.mail_service.save_screen = True
        await self.mail_service.generate_screenshot(
            self.test_content, self.test_email, self.test_msg_id
        )
        self.assertTrue(
            os.path.exists(
                os.path.join(settings.BASE_DIR.parent, MAIL_FOLDER, self.test_email)
            )
            is True
        )

        for file in os.scandir(
            os.path.join(settings.BASE_DIR.parent, MAIL_FOLDER, self.test_email)
        ):
            os.remove(file.path)
        os.rmdir(os.path.join(settings.BASE_DIR.parent, MAIL_FOLDER, self.test_email))
        os.rmdir(os.path.join(settings.BASE_DIR.parent, MAIL_FOLDER))
