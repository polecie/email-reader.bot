from httpx import Response


class ApiRequestsMock:
    """
    Сервис для отправки запросов к API
    """

    def __init__(self, status_code: int = 200, data: dict | None = None):
        self.status_code = status_code
        self.data = data

    async def post_user_request(self, *args, **kwargs) -> Response:
        """
        Отправляет запрос к API на создание пользователя
        """
        return Response(status_code=self.status_code, json=self.data)

    async def post_mail_creds_request(self, *args, **kwargs) -> Response:
        """
        Отправляет запрос в API на добавление почтовых данных
        """
        return Response(status_code=self.status_code, json=self.data)

    async def post_sender_mail(self, *args, **kwargs) -> Response:
        """
        Отправляет запрос к API на добавление почты отправителя
        """
        return Response(status_code=self.status_code, json=self.data)

    async def get_mails_list_request(self, *args, **kwargs) -> Response:
        """
        Отправляет запрос к API на получение списка привязанных почт
        """
        return Response(status_code=self.status_code, json=self.data)

    async def get_senders_list_request(self, *args, **kwargs) -> Response:
        """
        Отправляет запрос к API на получение списка привязанных почт
        """
        return Response(status_code=self.status_code, json=self.data)

    async def get_providers_list_request(self, *args, **kwargs) -> Response:
        return Response(status_code=self.status_code, json=self.data)

    async def delete_mail_request(self, *args, **kwargs) -> Response:
        return Response(status_code=self.status_code, json=self.data)

    async def delete_sender_request(self, *args, **kwargs) -> Response:
        return Response(status_code=self.status_code, json=self.data)
