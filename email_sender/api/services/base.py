import abc

from rest_framework.request import Request
from rest_framework.response import Response


class AbstractUserService(abc.ABC):
    """
    Абстрактный класс, предоставляющий интерфейс для работы с пользователем.

    Определяет абстрактные методы, которые должны быть реализованы в подклассах:
    `get_user()`,
    `create_user()`,
    `get_senders()`,
    `get_mails()`,
    `connect_sender()`,
    `disconnect_sender()`
    """

    @abc.abstractmethod
    def get_user(self, request: Request) -> Response:
        """
        Получает пользователя по запросу.

        :param request: Объект запроса.
        :return: Объект ответа.
        """

    @abc.abstractmethod
    def create_user(self, request: Request) -> Response:
        """
        Создает нового пользователя.

        :param request: Объект запроса, содержащий информацию о новом пользователе.
        :return: Объект ответа.
        """

    @abc.abstractmethod
    def get_senders(self, request: Request) -> Response:
        """
        Возвращает список отправителей.

        :param request: Объект запроса.
        :return: Объект ответа.
        """

    @abc.abstractmethod
    def get_mails(self, request: Request) -> Response:
        """
        Возвращает список писем.

        :param request: Объект запроса.
        :return: Объект ответа.
        """

    @abc.abstractmethod
    def connect_sender(self, request: Request, email: str) -> Response:
        """
        Привязывает отправителя к аккаунту пользователя.

        :param request: Объект запроса.
        :param email: Почтовый адрес отправителя для отслеживания.
        :return: Объект ответа.
        """

    @abc.abstractmethod
    def disconnect_sender(self, request: Request, email: str) -> Response:
        """
        Отвязывает отправителя от аккаунта пользователя.

        :param request: Объект запроса.
        :param email: Почтовый адрес отправителя для отслеживания.
        :return: Объект ответа.
        """

    @abc.abstractmethod
    def connect_email(self, request: Request, email: str) -> Response:
        """
        Привязывает почту к аккаунту пользователя.

        :param request: Объект запроса.
        :param email: Почтовый адрес для привязывания.
        :return: Объект ответа.
        """

    @abc.abstractmethod
    def disconnect_email(self, request: Request, email: str) -> Response:
        """
        Отвязывает почту от аккаунта пользователя.

        :param request: Объект запроса.
        :param email: Почтовый адрес для привязывания.
        :return: Объект ответа.
        """
