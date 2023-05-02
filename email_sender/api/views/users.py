from adrf.viewsets import ViewSet
from api.serializers import UserCreateSerializer, UserSerializer
from api.services import user_service
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request


class UsersViewSet(ViewSet):
    http_method_names = ("get", "post")

    @extend_schema(request=UserCreateSerializer, responses=UserSerializer)
    async def create(self, request: Request):
        """
        Метод для создания нового пользователя.
        :param request: Объект запроса.
        :return: Объект ответа.
        """
        return user_service.create_user(request)

    @extend_schema(responses=UserSerializer)
    async def retrieve(self, request: Request):
        """
        Метод для получения данных пользователя.
        :param request: Объект запроса.
        :return: Объект ответа.
        """
        return user_service.get_user(request)
