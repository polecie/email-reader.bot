import random
from dataclasses import dataclass
from functools import lru_cache

from rest_framework import status
from rest_framework.response import Response
from telegram_bot.templates import messages as answer


@dataclass
class CustomResponse:
    status: bool
    message: str
    data: dict | None = None


class BotNotificationService:
    message_200: str = ""
    message_201: str = ""
    message_500: str = random.choice(answer.server_error)
    message_400: str = ""

    def _make_response(
        self,
        response: Response,
    ) -> CustomResponse:
        if response.status_code == status.HTTP_200_OK:
            return CustomResponse(True, self.message_200)
        if response.status_code == status.HTTP_201_CREATED:
            return CustomResponse(True, self.message_201)
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            if len(self.message_400) == 0:
                values = [
                    f"{key}: {value[0]}" for key, value in response.json().items()
                ]
                self.message_400 = " ".join(values)
                return CustomResponse(False, self.message_400)
            return CustomResponse(False, self.message_400)
        return CustomResponse(False, self.message_500)

    @staticmethod
    async def _no_response_check(response: Response | None) -> bool:
        """
        Проверка, что есть объект ответа
        """
        if response is None:
            return True
        else:
            return False

    def _get_message(self, messages: list) -> str:
        return random.choice(messages)

    async def create_user(self, response: Response) -> CustomResponse:
        if await self._no_response_check(response):
            return CustomResponse(False, self._get_message(answer.server_unavailable))

        self.message_400 = self._get_message(answer.user_greeting)
        self.message_201 = self._get_message(answer.new_user_greeting)
        return self._make_response(response)

    async def connect_email(self, response: Response) -> CustomResponse:
        if await self._no_response_check(response):
            return CustomResponse(False, self._get_message(answer.server_unavailable))
        user_email = ""
        if response.status_code == status.HTTP_201_CREATED:
            user_email = response.json()["email"]["email"]
        self.message_400 = ""
        self.message_201 = self._get_message(answer.email_connected).format(user_email)
        self.message_500 = self._get_message(answer.connecting_failed)
        return self._make_response(response)

    async def connect_sender(self, response: Response) -> CustomResponse:
        if await self._no_response_check(response):
            return CustomResponse(False, self._get_message(answer.server_unavailable))
        sender_email = ""
        if response.status_code == status.HTTP_201_CREATED:
            sender_email = response.json()["sender"]["email"]
        self.message_400 = ""
        self.message_201 = self._get_message(answer.sender_connected).format(
            sender_email
        )
        self.message_500 = self._get_message(answer.connecting_failed)
        return self._make_response(response)

    async def delete_sender(self, response: Response) -> CustomResponse:
        if await self._no_response_check(response):
            return CustomResponse(False, self._get_message(answer.server_unavailable))
        sender_email = ""
        if response.status_code == status.HTTP_200_OK:
            sender_email = response.json()["email"]
        self.message_400 = ""
        self.message_200 = self._get_message(answer.delete_sender).format(sender_email)
        self.message_500 = self._get_message(answer.disconnecting_failed)
        return self._make_response(response)

    async def delete_email(self, response: Response) -> CustomResponse:
        if await self._no_response_check(response):
            return CustomResponse(False, self._get_message(answer.server_unavailable))
        user_email = ""
        if response.status_code == status.HTTP_200_OK:
            user_email = response.json()["email"]
        self.message_400 = ""
        self.message_200 = self._get_message(answer.delete_email).format(user_email)
        self.message_500 = self._get_message(answer.disconnecting_failed)
        return self._make_response(response)

    async def get_senders(self, response: Response) -> CustomResponse:
        if await self._no_response_check(response):
            return CustomResponse(False, self._get_message(answer.server_unavailable))
        empty = self._get_message(answer.senders_empty)
        if response.status_code == status.HTTP_200_OK:
            if len(response.json()["results"]) > 0:
                return CustomResponse(
                    True, self._get_message(answer.senders), response.json()
                )
            else:
                return CustomResponse(False, empty, response.json())
        else:
            return CustomResponse(False, empty, response.json())

    async def get_mails(self, response: Response) -> CustomResponse:
        if await self._no_response_check(response):
            return CustomResponse(False, self._get_message(answer.server_unavailable))
        empty = self._get_message(answer.emails_empty)
        if response.status_code == status.HTTP_200_OK:
            if len(response.json()["results"]) > 0:
                return CustomResponse(
                    True, self._get_message(answer.emails), response.json()
                )
            else:
                return CustomResponse(False, empty, response.json())
        else:
            return CustomResponse(False, empty, response.json())

    async def get_providers(self, response: Response) -> CustomResponse:
        if await self._no_response_check(response):
            return CustomResponse(False, self._get_message(answer.server_unavailable))
        if response.status_code == status.HTTP_200_OK:
            return CustomResponse(
                True,
                self._get_message(answer.provider_choice_msg),
                response.json(),
            )
        else:
            return CustomResponse(
                False,
                self._get_message(answer.unknown_error_msg),
                response.json(),
            )


@lru_cache
def get_notification_requests() -> BotNotificationService:
    return BotNotificationService()
