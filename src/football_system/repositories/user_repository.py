from contextlib import closing
from pathlib import Path
from typing import Optional

from src.football_system.database.database import DB_PATH, get_connection
from src.football_system.models import User


class UserRepository:
    """Репозиторий для работы с пользователями системы."""

    def __init__(self, db_path: str | Path = DB_PATH):
        self.db_path = db_path

    def get_user_by_login(self, login: str) -> Optional[User]:
        """R - Найти пользователя по логину."""
        with closing(get_connection(self.db_path)) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id_пользователя, логин, пароль FROM Users "
                "WHERE логин = ?",
                (login,),
            )
            row = cursor.fetchone()
            if row:
                return User(
                    id_пользователя=row[0],
                    логин=row[1],
                    пароль=row[2],
                )
            return None
