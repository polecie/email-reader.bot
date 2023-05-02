from api.models import Mail, MailProvider, TrackedMailSender, User
from app_celery.schemes import Mail as MailScheme
from app_celery.services import MailService
from rest_framework import serializers, status
from rest_framework.fields import CharField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer


class UserSerializer(ModelSerializer):
    """
    Сериализатор объектов класса `User`.
    """

    class Meta:
        model = User
        fields = ("id", "tg_id", "first_name", "second_name")

    def _get_user_second_name(self, user: User) -> bool:
        """
        Функция для проверки наличия `second_name` у пользователя.
        """
        if user.second_name:
            return True
        return False

    def to_representation(self, instance) -> dict:
        """
        Преобразует объект `User` в словарь,
        возвращает `second_name` пользователя, если оно установлено.
        """
        representation = super().to_representation(instance)
        if not self._get_user_second_name(instance):
            del representation["second_name"]
            del representation["tg_id"]
            return representation
        representation["first_name"] = instance.first_name
        representation["second_name"] = instance.second_name
        del representation["tg_id"]
        return representation

    def user_create(self) -> Response:
        """
        Создание пользователя в базе данных если данные валидны и пользователь не существует.

        :return: Объект ответа.
        """
        if self.is_valid():
            self.save()

            return Response(
                {"detail": "Пользователь успешно создан.", "user": self.data},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            self.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class MailSerializer(ModelSerializer):
    """
    Сериализатор для привязки почты.
    """

    provider = PrimaryKeyRelatedField(
        queryset=MailProvider.objects.all(), required=False
    )

    class Meta:
        model = Mail
        fields = ("id", "email", "password", "user", "provider")

    def validate(self, data):
        """
            Валидация путем аутентификация на imap сервере
        :param data: входные данные сериализатора
        :return: данные
        """
        mail_creds = MailScheme(
            email=data["email"],
            password=data["password"],
            provider=data["provider"].to_json(),
        )
        if not MailService.validate_mail(mail_creds):
            raise serializers.ValidationError(
                "Почтовые данные не подошли, проверьть логин, пароль и выбранный почтовый сервер"
            )
        return data

    def link_to_user(self) -> Response:
        """
        Привязка почтовых данные к пользователю.

        :return: Объект ответа
        """
        if self.is_valid():
            self.save()

            return Response(
                {"detail": "Почта привязана", "email": self.data},
                status=status.HTTP_201_CREATED,
            )

        return Response(self.errors, status=status.HTTP_400_BAD_REQUEST)


class ExcludedMailFieldsSerializer(MailSerializer):
    """
    Сериализатор для объектов класса `Mail`,
    исключающий поле "password", "user", "provider".
    """

    class Meta:
        model = Mail
        fields = (
            "id",
            "email",
        )


class SenderSerializer(ModelSerializer):
    """
    Сериализатор для объектов класса `TrackedMailSender`.
    """

    class Meta:
        model = TrackedMailSender
        fields = ("id", "email")


class EmailSenderSerializer(ModelSerializer):
    """
    Сериализатор для объектов класса `TrackedMailSender`.
    Включающий все поля
    """

    class Meta:
        model = TrackedMailSender
        fields = ("email", "user")

    def link(self):
        """
        Привязка отслеживаемых почтовых адресов к пользователю если данные валидны.

        :return: Объект ответа.
        """
        if self.is_valid():
            is_exists = TrackedMailSender.objects.filter(
                email=self.validated_data.get("email"),
                user=self.validated_data.get("user"),
            ).first()
            if is_exists:
                return Response(
                    {"email": ["Почта уже привязана"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not is_exists:
                self.save()

                return Response(
                    {"detail": "Отслеживаемая почта привязана.", "sender": self.data},
                    status=status.HTTP_201_CREATED,
                )

        return Response(self.errors, status=status.HTTP_400_BAD_REQUEST)


class ProviderSerializer(ModelSerializer):
    """
    Сериализатор объекта почтового сервиса MailProvider
    """

    class Meta:
        model = MailProvider
        fields = "__all__"
        read_only_fields = ["id"]


class UserCreateSerializer(ModelSerializer):
    """
    Сериализатор объектов класса `User`.
    """

    second_name = CharField(required=False)

    class Meta:
        model = User
        fields = ("first_name", "second_name")


class MailCreateSerializer(MailSerializer):
    class Meta:
        model = Mail
        fields = (
            "password",
            "provider",
        )
