from dataclasses import dataclass


@dataclass
class Mail:
    """Класс почтового ящика"""

    email: str
    password: bytes | str
    provider: dict
