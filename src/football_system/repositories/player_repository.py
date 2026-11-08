from contextlib import closing
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.football_system.database.database import DB_PATH, get_connection
from src.football_system.models import Player


class PlayerRepository:
    """Репозиторий для управления игроками (CRUD)."""

    def __init__(self, db_path: str | Path = DB_PATH):
        self.db_path = db_path

    def add(self, player: Player) -> int:
        """C - Добавить игрока."""
        with closing(get_connection(self.db_path)) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO Players (id_команды, фио, игровой_номер, позиция) "
                "VALUES (?, ?, ?, ?)",
                (player.id_teams, player.fio, player.number, player.position),
            )
            connection.commit()
            return cursor.lastrowid

    def get_by_id(self, id_players: int) -> Optional[Player]:
        """R - Прочитать игрока по ID."""
        with closing(get_connection(self.db_path)) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id_игрока, id_команды, фио, игровой_номер, позиция "
                "FROM Players WHERE id_игрока = ?",
                (id_players,),
            )
            row = cursor.fetchone()
            if row:
                return Player(
                    id_players=row[0],
                    id_teams=row[1],
                    fio=row[2],
                    number=row[3],
                    position=row[4],
                )
            return None

    def get_all(self) -> List[Player]:
        """R - Получить всех игроков."""
        with closing(get_connection(self.db_path)) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id_игрока, id_команды, фио, игровой_номер, позиция "
                "FROM Players"
            )
            return [
                Player(
                    id_players=row[0],
                    id_teams=row[1],
                    fio=row[2],
                    number=row[3],
                    position=row[4],
                )
                for row in cursor.fetchall()
            ]

    def get_all_with_team_name(self) -> List[Dict[str, Any]]:
        """R - Получить игроков вместе с названиями их команд (JOIN)."""
        with closing(get_connection(self.db_path)) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT p.id_игрока AS id_players, "
                "p.фио AS fio, "
                "p.игровой_номер AS number, "
                "p.позиция AS position, "
                "t.название AS team_name "
                "FROM Players AS p "
                "JOIN Teams AS t ON t.id_команды = p.id_команды "
                "ORDER BY p.id_игрока"
            )
            columns = [
                description[0] for description in cursor.description
            ]
            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]

    def get_all_by_team(self, id_teams: int) -> List[Player]:
        """R - Получить игроков конкретной команды."""
        with closing(get_connection(self.db_path)) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id_игрока, id_команды, фио, игровой_номер, позиция "
                "FROM Players WHERE id_команды = ?",
                (id_teams,),
            )
            return [
                Player(
                    id_players=row[0],
                    id_teams=row[1],
                    fio=row[2],
                    number=row[3],
                    position=row[4],
                )
                for row in cursor.fetchall()
            ]

    def delete(self, id_players: int) -> None:
        """D - Удалить игрока."""
        with closing(get_connection(self.db_path)) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM Players WHERE id_игрока = ?",
                (id_players,),
            )
            connection.commit()
