from api.models import Mail, MailProvider, TrackedMailSender, User
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITransactionTestCase


class UserApiTest(APITransactionTestCase):
    """Тесты для апи вьюшки пользователя."""

    url = reverse("users_view")
    headers = {"HTTP_tg-id": 123123}

    def test_user_not_found(self):
        """Тестируем что пользователя нет и возвращается верный статус код."""
        response = self.client.get(reverse("users_view"), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_user(self):
        """Тестируем создание пользователя через апи."""
        data = dict(first_name="test_name")

        response = self.client.post(self.url, data, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().first_name, "test_name")

    def test_get_user_detail(self):
        """Тестируем получение несуществующего пользователя после чего создаем его и повторяем получение."""
        headers = {"HTTP_tg-id": 1}

        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.post(self.url, {"first_name": "user"}, **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().first_name, "user")

        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_without_headers(self):
        """Тестируем что без идентификатора пользователя в заголовках выдается верный статус код."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserMailsPaginatingTest(APITransactionTestCase):
    """Тесты для получения списка почт и отслеживаемых почт пользователя."""

    mail_url = reverse("users_mails_list_view")
    mail_sender_url = reverse("users_mail_senders_list_view")
    headers = {"HTTP_tg-id": 123123}

    def setUp(self) -> None:
        """Создание пользователя, провайдера и нужный почтовых данных."""
        user = User.objects.create(tg_id=123123, first_name="test_name")
        provider = MailProvider.objects.create(server="imap.mail.ru", port=1111)

        for index in range(settings.PAGINATION_SIZE + 1):
            """Создаем  элементов PAGINATION_SIZE + 1 для того, чтобы у нас было 2 страницы элементов"""
            Mail.objects.create(
                email=f"test{index}@test.com",
                password="123",
                user=user,
                provider=provider,
            )
            TrackedMailSender.objects.create(
                email=f"tracking{index}@mail.com", user=user
            )

    def test_mail_list(self):
        """Получаем список почт пользователя и проверяем количество, то что нет предыдущей страницы
        (так как это первая, запрос без параметров page) и то что есть результат со следующей страницей
        """
        response = self.client.get(self.mail_url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("count"), Mail.objects.count())
        self.assertIsNone(response.data.get("previous"))
        self.assertIsNotNone(response.data.get("results"))
        self.assertIsNotNone(response.data.get("next"))

    def test_mail_senders_list(self):
        """Получаем список привязанных почт с параметром page и так же проверяем количество, результат
        и предыдущую страницу, так же проверяем что это последняя страница так как
        создали PAGINATION_SIZE + 1 элементов"""
        response = self.client.get(
            "?".join([self.mail_sender_url, "page=2"]), **self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("count"), TrackedMailSender.objects.count())
        self.assertIsNotNone(response.data.get("previous"))
        self.assertIsNotNone(response.data.get("results"))
        self.assertIsNone(response.data.get("next"))

    def test_without_headers(self):
        """Тестируем что без идентификатора пользователя в заголовках выдается верный статус код."""
        response_mail = self.client.get(self.mail_url)
        response_sender = self.client.get(self.mail_sender_url)

        self.assertEqual(response_mail.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_sender.status_code, status.HTTP_403_FORBIDDEN)


class UserMailLinkTest(APITransactionTestCase):
    """Тесты для проверки корректной привязки и отвязки почтовых данные пользователя."""

    url = reverse("users_mails_view", kwargs={"email": "test@mail.ru"})
    headers = {"HTTP_tg-id": 123123}

    def setUp(self) -> None:
        """Создание пользователя и почтового провайдера."""
        User.objects.create(tg_id=123123, first_name="test_name")
        self.provider = MailProvider.objects.create(server="imap.mail.ru", port=1111)

    def test_mail_linking(self):
        """Тестируем отвязку не привязанной почты, привязываем и проверяем успешность."""
        response = self.client.delete(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        data = dict(password="123123", provider=self.provider.pk)
        response = self.client.post(self.url, data, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Mail.objects.count(), 0)

    def test_mail_unlinking(self):
        """Тестируем успешную отвязку почты изначально привязав ее к пользователю."""
        data = dict(password="123123", provider=self.provider.pk)
        response = self.client.post(self.url, data, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Mail.objects.count(), 0)

        response = self.client.delete(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_mail_user_not_found(self):
        """Тестируем что без идентификатора пользователя в заголовках выдается верный статус код."""
        data = dict(password="123123", provider=self.provider.pk)

        response_link = self.client.post(self.url, data)
        response_unlink = self.client.delete(self.url)

        self.assertEqual(response_link.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_unlink.status_code, status.HTTP_403_FORBIDDEN)


class UserMailSenderTest(APITransactionTestCase):
    """Тесты для проверки корректной привязки и отвязки отслеживаемых почт пользователя."""

    url = reverse("users_mail_senders_view", kwargs={"email": "test@mail.ru"})
    headers = {"HTTP_tg-id": 123123}

    def setUp(self) -> None:
        """Создание пользователя."""
        User.objects.create(tg_id=123123, first_name="test_name")

    def test_mail_linking(self):
        """Тестируем отвязку непривязанного отправителя, привязываем и проверяем успешность."""
        response = self.client.delete(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.post(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TrackedMailSender.objects.count(), 1)

    def test_mail_unlinking(self):
        """Тестируем успешную привязку отправителя и отвязываем проверяя успешность."""
        response = self.client.post(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TrackedMailSender.objects.count(), 1)

        response = self.client.delete(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(TrackedMailSender.objects.count(), 0)

    def test_mail_user_not_found(self):
        """Тестируем что без идентификатора пользователя в заголовках выдается верный статус код."""
        response_link = self.client.post(self.url)
        response_unlink = self.client.delete(self.url)

        self.assertEqual(response_link.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_unlink.status_code, status.HTTP_403_FORBIDDEN)


class ProviderApiViewTest(APITransactionTestCase):
    def test_providers_list(self):
        url = reverse("providers_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("count"), MailProvider.objects.count())
        self.assertIsNone(response.data.get("previous"))
        self.assertIsNotNone(response.data.get("results"))
