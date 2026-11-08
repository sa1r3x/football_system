from dataclasses import dataclass


@dataclass
class User:
    """Модель пользователя системы."""

    id_пользователя: int
    логин: str
    пароль: str
