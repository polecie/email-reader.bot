from abc import ABC, abstractmethod
from typing import Any


class AbstractMailSender(ABC):
    """
    Базовый класс для создания сервиса отправки сообщений пользователям

    Должны быть реализованы минимум два метода:
    - send_photo(screenshot)
    - send_warning(data)
    """

    @abstractmethod
    def __init__(self, user_id: Any) -> None:
        self.user_id = user_id

    @abstractmethod
    async def send_photo(self, screenshot: Any) -> bool:
        """
        Метод для отправки скриншота получателю(target)

        :param screenshot: any - скриншот в заданном формате
        :return: bool - результат отправки(True/False)
        """

    @abstractmethod
    async def send_warning(self, data: dict) -> bool:
        """
        Метод для отправки предупреждений и уведомлений в случае
        необходимости

        :param data: dict - информация для обработки и отправки
        :return: bool - результат отправки(True/False)
        """
