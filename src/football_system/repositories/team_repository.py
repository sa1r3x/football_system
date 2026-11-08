from contextlib import closing
from pathlib import Path
from typing import List, Optional

from src.football_system.database.database import DB_PATH, get_connection
from src.football_system.models import Team


class TeamRepository:
    """Репозиторий для управления командами (CRUD)."""

    def __init__(self, db_path: str | Path = DB_PATH):
        self.db_path = db_path

    def add(self, team: Team) -> int:
        """C - Создать команду."""
        with closing(get_connection(self.db_path)) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO Teams (название) VALUES (?)",
                (team.name,),
            )
            connection.commit()
            return cursor.lastrowid

    def get_by_id(self, id_teams: int) -> Optional[Team]:
        """R - Прочитать команду по ID."""
        with closing(get_connection(self.db_path)) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id_команды, название FROM Teams WHERE id_команды = ?",
                (id_teams,),
            )
            row = cursor.fetchone()
            if row:
                return Team(id_teams=row[0], name=row[1])
            return None

    def get_all(self) -> List[Team]:
        """R - Получить все команды."""
        with closing(get_connection(self.db_path)) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id_команды, название FROM Teams")
            return [
                Team(id_teams=row[0], name=row[1])
                for row in cursor.fetchall()
            ]

    def delete(self, id_teams: int) -> None:
        """D - Удалить команду."""
        with closing(get_connection(self.db_path)) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM Teams WHERE id_команды = ?",
                (id_teams,),
            )
            connection.commit()
