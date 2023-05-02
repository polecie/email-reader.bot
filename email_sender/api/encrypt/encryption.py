import base64

import rsa
from api.encrypt.base import AbstractEncryptionService
from django.conf import settings


class EncryptionService(AbstractEncryptionService):
    """
    Класс, представляющий сервис шифрования.

    Реализует два основных метода `encrypt()` и `decrypt()`,
    унаследованных от абстрактного базового класса `AbstractEncryptionService`.
    """

    @staticmethod
    def _format_key(key: str, prefix: str, suffix: str) -> bytes:
        """
        Форматирует ключ шифрования в соответствии с заданным префиксом и суффиксом.

        :param key: Строка, представляющая ключ шифрования.
        :param prefix: Строка, содержащая префикс для форматирования ключа.
        :param suffix: Строка, содержащая суффикс для форматирования ключа.
        :return: Объект bytes, представляющий отформатированный ключ шифрования.
        """
        formatted_key = f"{prefix}\n"
        formatted_key += "\n".join(
            key[i : i + 64] for i in range(0, len(key), 64)  # noqa: E203
        )
        formatted_key += f"\n{suffix}"
        return formatted_key.encode(settings.ENCRYPTION_ENCODING)

    @staticmethod
    def _encode(password: str) -> bytes:
        """
        Кодирует строку пароля в объект bytes.

        :param password: Строка, представляющая пароль в открытом виде.
        :return: Объект bytes, представляющий зашифрованный пароль.
        """
        return password.encode(settings.ENCRYPTION_ENCODING)

    @staticmethod
    def _decode(password: bytes) -> str:
        """
        Декодирует объект bytes, представляющий зашифрованный пароль, в строку.

        :param password: Объект bytes, представляющий зашифрованный пароль.
        :return: Строка, представляющая расшифрованный пароль.
        """
        return password.decode(settings.ENCRYPTION_ENCODING)

    def encrypt(self, password: str) -> str:
        """
        Шифрует пароль и возвращает его в виде строки-шифра.

        :param password: Строка, представляющая пароль в открытом виде.
        :return: Объект str, представляющий зашифрованный пароль.
        """
        key = self._format_key(
            key=settings.PUBLIC_KEY,
            prefix=settings.PUBLIC_KEY_PREFIX,
            suffix=settings.PUBLIC_KEY_SUFFIX,
        )
        password = self._encode(password)  # type: ignore
        public = rsa.PublicKey.load_pkcs1_openssl_pem(key)
        crypto = rsa.encrypt(password, public)
        return base64.b64encode(crypto).decode("utf-8")

    def decrypt(self, password: bytes) -> str:
        """
        Расшифровывает пароль и возвращает его в виде строки.

        :param password: Объект bytes, представляющий зашифрованный пароль.
        :return: Строка, представляющая расшифрованный пароль.
        """
        key = self._format_key(
            key=settings.PRIVATE_KEY,
            prefix=settings.PRIVATE_KEY_PREFIX,
            suffix=settings.PRIVATE_KEY_SUFFIX,
        )
        private = rsa.PrivateKey.load_pkcs1(key, format="PEM")
        crypto = base64.b64decode(password)
        password = rsa.decrypt(crypto, private)
        return self._decode(password)
