from api.models import Mail, TrackedMailSender, User
from api.serializers import (
    EmailSenderSerializer,
    ExcludedMailFieldsSerializer,
    MailSerializer,
    SenderSerializer,
    UserSerializer,
)
from django.conf import settings
from django.http import QueryDict
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from .base import AbstractUserService
from .provider import ProviderService


class UserService(AbstractUserService):
    """
    Класс, представляющий сервис для работы с пользователями.

    Реализует основные методы -
    `create_user()`,
    `get_user()`,
    `get_senders()`,
    `get_mails()`,
    `connect_sender()`,
    `disconnect_sender()`
    унаследованные от абстрактного базового класса `AbstractUserService`.
    """

    def _authenticate_user(self, request: Request) -> int:
        """
        Аутентифицирует пользователя по id в телеграм, переданному в заголовке.

        :param request: Объект запроса, содержащий заголовки.
        :return: Целое число, представляющее токен пользователя.
        :raises: NotAuthenticated, если токен не передан.
        """
        token = request.headers.get("tg-id")
        if not token:
            raise NotAuthenticated

        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        request.data["tg_id"] = int(token)
        return token

    def _get_user(self, token: int) -> User:
        """
        Получает объект пользователя по его id в телеграм.

        :param token: Целое число, представляющее токен пользователя.
        :return: Объект пользователя.
        """
        return get_object_or_404(User, tg_id=token)

    def create_user(self, request: Request) -> Response:
        """
        Создает нового пользователя.

        :param request: Объект запроса, содержащий информацию о новом пользователе.
        :return: Объект ответа.
        """
        if self._authenticate_user(request):
            serialized_user = UserSerializer(data=request.data)
            return serialized_user.user_create()

    def get_user(self, request: Request) -> Response:
        """
        Получает информацию о пользователе по его id в телеграм.

        :param request: Объект запроса.
        :return: Объект ответа.
        """
        if token := self._authenticate_user(request):
            user = self._get_user(token)
            serialized_user = UserSerializer(user)
            return Response(serialized_user.data, status=status.HTTP_200_OK)

    def _setup_paginator(self) -> PageNumberPagination:
        """
        Создает и настраивает объект пагинации.

        :return: Объект пагинации.
        """
        paginator = PageNumberPagination()
        paginator.page_size = settings.PAGINATION_SIZE
        return paginator

    def _paginate(self, request: Request, db_model, serializer) -> Response:
        """
        Выполняет пагинацию и сериализацию списка объектов модели.

        :param request: Объект запроса.
        :param db_model: Модель базы данных,
        объекты которой нужно сериализовать и отображать на страницах.
        :param serializer: Сериализатор, преобразующий объекты модели в словари.
        :return: Объект ответа.
        """
        if token := self._authenticate_user(request):
            user = self._get_user(token)
            mailboxes = db_model.objects.filter(user_id=user.pk).order_by("id")
            paginator = self._setup_paginator()
            page = paginator.paginate_queryset(mailboxes, request)
            serializer = serializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

    def get_senders(self, request: Request) -> Response:
        """
        Возвращает список отправителей с постраничным выводом.

        :param request: Объект запроса.
        :return: Список отправителей в виде JSON-объекта с метаданными пагинации.
        """
        response = self._paginate(request, TrackedMailSender, SenderSerializer)
        return response

    def get_mails(self, request: Request) -> Response:
        """
        Возвращает список писем с постраничным выводом.

        :param request: Объект запроса.
        :return: Список писем в виде JSON-объекта с метаданными пагинации.
        """
        response = self._paginate(request, Mail, ExcludedMailFieldsSerializer)
        return response

    def connect_sender(self, request: Request, email: str) -> Response:
        """
        Привязывает отправителя к аккаунту пользователя
        для дальнейшего отслеживания писем.

        :param request: Объект запроса.
        :param email: Почтовый адрес отправителя для отслеживания.
        :return: Объект ответа.
        """
        if token := self._authenticate_user(request):
            if user := self._get_user(token):
                data = dict(user=user.pk, email=email)
                serialized_sender_email = EmailSenderSerializer(data=data)
                return serialized_sender_email.link()

    def disconnect_sender(self, request: Request, email: str) -> Response:
        """
        Отвязывает отправителя от аккаунта пользователя.

        :param request: Объект запроса.
        :param email: Почтовый адрес отправителя для отслеживания.
        :return: Объект ответа.
        """
        if token := self._authenticate_user(request):
            if user := self._get_user(token):
                sender_email = get_object_or_404(
                    TrackedMailSender, email=email, user=user.pk
                )
                sender_email.delete()
                return Response(
                    {
                        "detail": "Отслеживаемая почта отвязана.",
                        "email": sender_email.email,
                    },
                    status=status.HTTP_200_OK,
                )

    def connect_email(self, request: Request, email: str) -> Response:
        """
        Привязывает почту к аккаунту пользователя.

        :param request: Объект запроса.
        :param email: Почтовый адрес для привязывания.
        :return: Объект ответа.
        """
        if token := self._authenticate_user(request):
            if user := self._get_user(token):
                provider_id = request.data.get("provider")
                if provider_id:
                    request.data.update(user=user.pk, email=email)
                    serialized_mail = MailSerializer(data=request.data)
                    return serialized_mail.link_to_user()
                else:
                    provider_service = ProviderService()
                    provider = provider_service.create_provider(email)
                    if provider:
                        request.data.update(
                            provider=provider.pk, user=user.pk, email=email
                        )
                        serialized_mail = MailSerializer(data=request.data)
                        return serialized_mail.link_to_user()
                    else:
                        return Response(
                            {
                                "detail": [
                                    "Найти подходящий почтовый сервис не удалось, "
                                    "Проверьте еще раз, нет ли нужного вам провайдера в списке "
                                    "или обратитесь к администратору"
                                ]
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

    def disconnect_email(self, request: Request, email: str) -> Response:
        """
        Отвязывает почту от аккаунта пользователя.

        :param request: Объект запроса.
        :param email: Почтовый адрес для привязывания.
        :return: Объект ответа.
        """
        if token := self._authenticate_user(request):
            if user := self._get_user(token):
                mail = get_object_or_404(Mail, user=user.pk, email=email)
                mail.delete()
                return Response(
                    {"detail": "Почта отвязана", "email": mail.email},
                    status=status.HTTP_200_OK,
                )
