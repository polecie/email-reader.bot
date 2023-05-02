from adrf.views import APIView
from adrf.viewsets import ViewSet
from api.serializers import (
    ExcludedMailFieldsSerializer,
    MailCreateSerializer,
    MailSerializer,
)
from api.services import user_service
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request


class MailsListView(APIView):
    pagination_class = PageNumberPagination

    @extend_schema(responses=ExcludedMailFieldsSerializer(many=True))
    async def get(self, request: Request):
        """
        Список привязанных почтовых данных пользователя.
        :param request: Объект запроса.
        :return: Объект ответа.
        """
        return user_service.get_mails(request)


class UserMailViewSet(ViewSet):
    @extend_schema(request=MailCreateSerializer, responses=MailSerializer)
    async def create(self, request: Request, email: str):
        """
        Привязка почты пользователя к его аккаунту.

        :param email: Почта для привязки.
        :param request: Объект запроса.
        :return: Объект ответа.
        """
        return user_service.connect_email(request, email)

    @extend_schema(
        responses={status.HTTP_200_OK: dict},
        examples=[
            OpenApiExample(
                "Example 1",
                status_codes=[status.HTTP_200_OK],
                value={"detail": "Почта отвязана", "email": "example@gmail.com"},
            ),
        ],
    )
    async def destroy(self, request: Request, email: str):
        """
        Отвязка почты пользователя от его аккаунта.

        :param email: Почта для привязки.
        :param request: Объект запроса.
        :return: Объект ответа.
        """
        return user_service.disconnect_email(request, email)
