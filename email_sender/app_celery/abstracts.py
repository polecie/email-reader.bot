from abc import ABC, abstractmethod


class AbstractMailService(ABC):
    """
    Абстрактный базовый класс для почтовых сервисов.

    Определяет следующие абстрактные методы, которые должны быть реализованы в подклассах:
    - check_new_mails()
    - get_mails(msg_id, mail)
    - generate_screenshot()
    - run()
    """

    @abstractmethod
    def __init__(self, mails: list, senders: list) -> None:
        self.mail = mails
        self.senders = senders

    @abstractmethod
    async def check_new_mails(self) -> None:
        """
        Метод проверки новых писем.
        """

    @abstractmethod
    async def get_mail(self, msg_id: int, sender: str, to_email: str) -> None:
        """
        Метод получения содержимого письма

        :param msg_id: аргумент типа int, представляющий id или uid письма.
        :param sender: аргумент типа str, email отправителя.
        :param to_email: аргумент типа str, email получателя.
        """

    @abstractmethod
    async def generate_screenshot(
        self, content: str, folder_name: str, msg_id: int
    ) -> None:
        """
        Метод получения скриншота сообщений

        :param content: Тело сообщения в виде html-страницы для визуализации в браузере
        :param folder_name: имя директории в виде email-адреса получателя, куда будут сохраняться скриншоты
        :param msg_id: int - id сообщения для скриншота
        """

    @abstractmethod
    def run(self) -> None:
        """
        Метод для запуска сервиса
        """
