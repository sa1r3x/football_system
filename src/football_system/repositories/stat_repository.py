from contextlib import closing
from pathlib import Path
from typing import List

from src.football_system.database.database import DB_PATH, get_connection
from src.football_system.models import PlayerStat


class StatRepository:
    """Репозиторий для управления голами и нарушениями (PlayerStats)."""

    def __init__(self, db_path: str | Path = DB_PATH):
        self.db_path = db_path

    def add_event(self, stat: PlayerStat) -> int:
        """C - Записать гол или карточку игрока в матче."""
        with closing(get_connection(self.db_path)) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO PlayerStats "
                "(id_матча, id_игрока, забитые_мячи, желтые_карточки, "
                "красные_карточки) VALUES (?, ?, ?, ?, ?)",
                (
                    stat.id_matches,
                    stat.id_players,
                    stat.goals,
                    stat.yellow_cards,
                    stat.red_cards,
                ),
            )
            connection.commit()
            return cursor.lastrowid

    def get_stats_by_match(self, id_matches: int) -> List[PlayerStat]:
        """R - Получить всю статистику по конкретному матчу."""
        with closing(get_connection(self.db_path)) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id_записи, id_матча, id_игрока, забитые_мячи, "
                "желтые_карточки, красные_карточки FROM PlayerStats "
                "WHERE id_матча = ?",
                (id_matches,),
            )
            return [
                PlayerStat(
                    id_stat=row[0],
                    id_matches=row[1],
                    id_players=row[2],
                    goals=row[3],
                    yellow_cards=row[4],
                    red_cards=row[5],
                )
                for row in cursor.fetchall()
            ]

    def get_all(self) -> List[PlayerStat]:
        """R - Получить всю статистику игроков."""
        with closing(get_connection(self.db_path)) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id_записи, id_матча, id_игрока, забитые_мячи, "
                "желтые_карточки, красные_карточки FROM PlayerStats"
            )
            return [
                PlayerStat(
                    id_stat=row[0],
                    id_matches=row[1],
                    id_players=row[2],
                    goals=row[3],
                    yellow_cards=row[4],
                    red_cards=row[5],
                )
                for row in cursor.fetchall()
            ]
