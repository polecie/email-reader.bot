from django.db import models

__all__ = ("User", "MailProvider", "Mail", "TrackedMailSender")


class User(models.Model):
    """Модель пользователя."""

    tg_id = models.BigIntegerField(unique=True, verbose_name="Идентификатор в телеграм")
    first_name = models.CharField(max_length=150, verbose_name="Имя")
    second_name = models.CharField(
        max_length=150, null=True, blank=True, verbose_name="Фамилия"
    )
    registered_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата регистрации"
    )

    def __str__(self) -> str:
        return f"{self.tg_id}"

    class Meta:
        verbose_name_plural = "Пользователи"
        verbose_name = "Пользователь"


class MailProvider(models.Model):
    """Модель почтового провайдера."""

    name = models.CharField(max_length=30, unique=True, verbose_name="Название")
    server = models.TextField(verbose_name="Адрес сервера")
    port = models.IntegerField(verbose_name="Порт")

    def __str__(self) -> str:
        return f"{self.server}:{self.port}"

    class Meta:
        verbose_name_plural = "Провайдеры"
        verbose_name = "Провайдер"

    def to_json(self) -> dict:
        return {"host": self.server, "port": self.port}


class Mail(models.Model):
    """Модель почты."""

    email = models.EmailField(
        max_length=256, unique=True, verbose_name="Электронный адрес"
    )
    password = models.TextField(verbose_name="Пароль для приложений")
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    provider = models.ForeignKey("MailProvider", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return str(self.email)

    class Meta:
        verbose_name_plural = "Почты"
        verbose_name = "Почта"

    def to_json(self) -> dict:
        return {
            "email": self.email,
            "password": self.password,
            "provider": self.provider.to_json(),
        }


class TrackedMailSender(models.Model):
    """Модель отправителя."""

    email = models.EmailField(max_length=256, verbose_name="Электронный адрес")
    user = models.ForeignKey("User", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return str(self.email)

    class Meta:
        verbose_name_plural = "Отправители"
        verbose_name = "Отправитель"
