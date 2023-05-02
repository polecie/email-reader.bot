import imaplib

from api.models import MailProvider
from api.serializers import ProviderSerializer


class ProviderService:
    """
    Класс для работы с почтовыми серверами
    """

    def __server_exists(self, server: str) -> bool:
        """
        Проверка imap сервера на существование
        :param server:
        :return: Существует ли сервер
        """
        try:
            imaplib.IMAP4_SSL(server, timeout=1.5)
            return True
        except Exception:
            return False

    def __get_provider_name(self, mail: str) -> str:
        """
            Выделяем почтовый домен из почты
        :param mail: Почта
        :return: Почтовый домен
        """
        server = f'{mail.split(sep="@")[-1]}'
        return server

    def __get_imap_server(self, provider_name: str) -> str:
        """
        Формирует по домену, предполагаемый почтовый сервер
        :param provider_name:
        :return: почтовый сервер
        """
        return f"imap.{provider_name}"

    def create_provider(self, mail: str) -> MailProvider | None:
        """
        Если сформированный по почте сервер существует, то возращает объект провайдера
        Иначе None
        :param mail: почта
        :return: Объект почтового сервиса,если удалось создать иначе None
        """
        provider_name = self.__get_provider_name(mail)
        imap_server = self.__get_imap_server(provider_name)
        exists = self.__server_exists(imap_server)
        if exists:
            new_server = {
                "name": provider_name,
                "server": imap_server,
                "port": 993,
            }
            provider_serializer = ProviderSerializer(data=new_server)

            if provider_serializer.is_valid():
                provider = provider_serializer.save()
                return provider
            else:
                return None
        return None
