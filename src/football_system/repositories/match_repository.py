from contextlib import closing
from pathlib import Path
from typing import List, Optional

from src.football_system.database.database import DB_PATH, get_connection
from src.football_system.models import Match


class MatchRepository:
    """Репозиторий для управления расписанием матчей."""

    def __init__(self, db_path: str | Path = DB_PATH):
        self.db_path = db_path

    def add(self, match: Match) -> int:
        """C - Добавить матч в расписание."""
        with closing(get_connection(self.db_path)) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO Matches "
                "(id_домашней_команды, id_гостевой_команды, дата_время) "
                "VALUES (?, ?, ?)",
                (match.id_home_team, match.id_away_team, match.date_time),
            )
            connection.commit()
            return cursor.lastrowid

    def get_by_id(self, id_matches: int) -> Optional[Match]:
        """R - Прочитать матч по ID."""
        with closing(get_connection(self.db_path)) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id_матча, id_домашней_команды, id_гостевой_команды, "
                "дата_время, итоговый_счет FROM Matches WHERE id_матча = ?",
                (id_matches,),
            )
            row = cursor.fetchone()
            if row:
                return Match(
                    id_matches=row[0],
                    id_home_team=row[1],
                    id_away_team=row[2],
                    date_time=row[3],
                    score=row[4],
                )
            return None

    def get_all(self) -> List[Match]:
        """R - Получить все матчи."""
        with closing(get_connection(self.db_path)) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id_матча, id_домашней_команды, id_гостевой_команды, "
                "дата_время, итоговый_счет FROM Matches"
            )
            return [
                Match(
                    id_matches=row[0],
                    id_home_team=row[1],
                    id_away_team=row[2],
                    date_time=row[3],
                    score=row[4],
                )
                for row in cursor.fetchall()
            ]
