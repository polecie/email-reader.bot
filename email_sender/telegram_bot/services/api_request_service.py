import logging
from functools import lru_cache

from httpx import AsyncClient, Headers, Response
from telegram_bot.config.config import get_bot_config


class ApiRequests:
    """
    Сервис для отправки запросов к API
    """

    def __init__(self):
        self.config = get_bot_config()

    async def _make_headers(self, tg_id: int) -> Headers:
        """
        Создает объект headers с tg_id
        """
        headers = {"tg_id": str(tg_id)}
        return Headers(headers)

    async def _get_request(self, url: str, headers: Headers = None) -> Response | None:
        """
        Посылает get запрос к API
        """
        try:
            async with AsyncClient() as client:
                response: Response = await client.get(
                    url,
                    headers=headers,
                )
                return response
        except Exception as err:
            logging.error(msg="Error when connect to API", exc_info=err)
            return None

    async def _post_request(
        self, url: str, data: dict | None = None, headers: Headers = None
    ) -> Response | None:
        """
        Посылает post запрос к API
        """
        try:
            async with AsyncClient() as client:
                response: Response = await client.post(
                    url,
                    json=data,
                    headers=headers,
                )
                return response
        except Exception as err:
            logging.error(msg="Error when connect to API", exc_info=err)
            return None

    async def _delete_request(
        self, url: str, headers: Headers = None
    ) -> Response | None:
        """
        Посылаетв delete запрос к API
        """
        try:
            async with AsyncClient() as client:
                response: Response = await client.delete(
                    url,
                    headers=headers,
                )
                return response
        except Exception as err:
            logging.error(msg="Error when connect to API", exc_info=err)
            return None

    async def post_user_request(
        self, tg_id: int, first_name: str, last_name: str
    ) -> Response | None:
        """
        Отправляет запрос к API на создание пользователя
        """
        user_data = {
            "first_name": first_name,
            "last_name": last_name,
        }
        headers = await self._make_headers(tg_id)
        response = await self._post_request(self.config.USERS_URL, user_data, headers)
        return response

    async def post_mail_creds_request(
        self, tg_id: int, provider_id: int, email: str, password: str
    ) -> Response | None:
        """
        Отправляет запрос в API на добавление почтовых данных
        """
        provider_id = int(provider_id)
        mail_data = {
            "password": password,
        }
        if provider_id:
            mail_data.setdefault(
                "provider",
                provider_id,  # type: ignore
            )

        headers = await self._make_headers(tg_id)
        response = await self._post_request(
            self.config.LINK_MAIL_URL.format(email), mail_data, headers
        )
        return response

    async def post_sender_mail(self, tg_id: int, email: str) -> Response | None:
        """
        Отправляет запрос к API на добавление почты отправителя
        """
        headers = await self._make_headers(tg_id)
        response = await self._post_request(
            self.config.LINK_SENDER_URL.format(email), headers=headers
        )
        return response

    async def get_mails_list_request(
        self, tg_id: int, url: str | None = None
    ) -> Response | None:
        """
        Отправляет запрос к API на получение списка привязанных почт
        """
        if url:
            list_url = url
        else:
            list_url = self.config.LIST_MAILS_URL

        headers = await self._make_headers(tg_id)
        response = await self._get_request(list_url, headers=headers)
        return response

    async def get_senders_list_request(
        self, tg_id: int, url: str | None = None
    ) -> Response | None:
        """
        Отправляет запрос к API на получение списка привязанных почт
        """
        if url:
            list_url = url
        else:
            list_url = self.config.LIST_SENDERS_URL
        headers = await self._make_headers(tg_id)
        response = await self._get_request(list_url, headers=headers)
        return response

    async def get_providers_list_request(
        self, url: str | None = None
    ) -> Response | None:
        """
        Отправляет запрос к API на получение списка доступных почтовых сервисов
        """
        if url:
            list_url = url
        else:
            list_url = self.config.LIST_PROVIDERS_URL
        response = await self._get_request(list_url)
        return response

    async def delete_mail_request(self, tg_id: int, email: str) -> Response | None:
        """
        Отправляет запрос к API на удаление привязанной почты (отвязка)
        """
        headers = await self._make_headers(tg_id)
        response = await self._delete_request(
            self.config.LINK_MAIL_URL.format(email), headers=headers
        )
        return response

    async def delete_sender_request(self, tg_id: int, email: str) -> Response | None:
        """
        Отправляет запрос к API на удаление привязанного отправителя (отвязка)
        """
        headers = await self._make_headers(tg_id)
        response = await self._delete_request(
            self.config.LINK_SENDER_URL.format(email), headers=headers
        )
        return response


@lru_cache
def get_api_requests() -> ApiRequests:
    return ApiRequests()
