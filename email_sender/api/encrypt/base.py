import abc


class AbstractEncryptionService(abc.ABC):
    """
    Абстрактный базовый класс для сервисов шифрования.

    Определяет два абстрактных метода, которые должны быть реализованы в подклассах:
    decrypt() и encrypt().
    """

    @abc.abstractmethod
    def decrypt(self, password: bytes) -> str:
        """
        Расшифровывает пароль и возвращает его в виде строки.

        :param password: Объект bytes, представляющий зашифрованный пароль.
        :return: Строка, представляющая расшифрованный пароль.
        """

    @abc.abstractmethod
    def encrypt(self, password: str) -> str:
        """
        Шифрует пароль и возвращает его в виде объекта bytes.

        :param password: Строка, представляющая пароль в открытом виде.
        :return: Объект str, представляющий зашифрованный пароль.
        """
