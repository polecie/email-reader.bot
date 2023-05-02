from adrf.views import APIView
from adrf.viewsets import ViewSet
from api.serializers import EmailSenderSerializer, SenderSerializer
from api.services import user_service
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response


class SendersListView(APIView):
    pagination_class = PageNumberPagination

    @extend_schema(
        responses=SenderSerializer(many=True),
    )
    async def get(self, request: Request):
        """
        Список отслеживаемых отправителей пользователя.
        :param request: Объект запроса.
        :return: Объект ответа.
        """
        return user_service.get_senders(request)


class UserMailSendersViewSet(ViewSet):
    @extend_schema(request=None, responses=EmailSenderSerializer)
    async def create(self, request: Request, email: str) -> Response:
        """
        Привязка отслеживаемой почты пользователя к его аккаунту.

        :param email: Отслеживаемая почта для привязки.
        :param request: Объект запроса.
        :return: Объект ответа.
        """
        return user_service.connect_sender(request, email)

    @extend_schema(
        responses={status.HTTP_200_OK: dict},
        examples=[
            OpenApiExample(
                "Response example 1",
                status_codes=[status.HTTP_200_OK],
                value={
                    "detail": "Отслеживаемая почта отвязана.",
                    "email": "example@gmail.com",
                },
            ),
        ],
    )
    async def destroy(self, request: Request, email: str):
        """
        Отвязка отслеживаемой почты пользователя к его аккаунту.

        :param email: Отслеживаемая почта для отвязки.
        :param request: Объект запроса.
        :return: Объект ответа.
        """
        return user_service.disconnect_sender(request, email)
