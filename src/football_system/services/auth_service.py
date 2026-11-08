from typing import Optional

from src.football_system.models import User
from src.football_system.repositories import UserRepository


class AuthService:
    """Авторизация пользователей системы."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def authenticate(self, login: str, password: str) -> Optional[User]:
        """Проверяет логин и пароль. Возвращает пользователя или None."""
        login = login.strip()
        if not login or not password:
            return None

        user = self.user_repo.get_user_by_login(login)
        if user and user.пароль == password:
            return user
        return None
