import sqlite3
from typing import List, Optional
from models import Team, Player, Match, PlayerStat, User

class TeamRepository:
    """Репозиторий для управления командами (CRUD)"""
    def __init__(self, db_path: str):
        self.db_path = db_path

    def add(self, team: Team) -> int:
        """C - Создать команду"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Teams (название) VALUES (?)", 
                (team.name,)
            )
            conn.commit()
            return cursor.lastrowid

    def get_by_id(self, id_teams: int) -> Optional[Team]:
        """R - Прочитать команду по ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_команды, название FROM Teams WHERE id_команды = ?", (id_teams,))
            row = cursor.fetchone()
            if row:
                return Team(id_teams=row[0], name=row[1])
            return None

    def get_all(self) -> List[Team]:
        """R - Получить все команды"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_команды, название FROM Teams")
            return [Team(id_teams=row[0], name=row[1]) for row in cursor.fetchall()]

    def delete(self, id_teams: int) -> None:
        """D - Удалить команду"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute("DELETE FROM Teams WHERE id_команды = ?", (id_teams,))
            conn.commit()


class PlayerRepository:
    """Репозиторий для управления игроками (CRUD)"""
    def __init__(self, db_path: str):
        self.db_path = db_path

    def add(self, player: Player) -> int:
        """C - Добавить игрока"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Players (id_команды, фио, игровой_номер, позиция) VALUES (?, ?, ?, ?)",
                (player.id_teams, player.fio, player.number, player.position)
            )
            conn.commit()
            return cursor.lastrowid

    def get_all_by_team(self, id_teams: int) -> List[Player]:
        """R - Получить игроков конкретной команды"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_игрока, id_команды, фио, игровой_номер, позиция FROM Players WHERE id_команды = ?", 
                (id_teams,)
            )
            return [Player(id_players=row[0], id_teams=row[1], fio=row[2], number=row[3], position=row[4]) 
                    for row in cursor.fetchall()]

    def delete(self, id_players: int) -> None:
        """D - Удалить игрока"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Players WHERE id_игрока = ?", (id_players,))
            conn.commit()


class MatchRepository:
    """Репозиторий для управления расписанием матчей"""
    def __init__(self, db_path: str):
        self.db_path = db_path

    def add(self, match: Match) -> int:
        """C - Добавить матч в расписание"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Matches (id_домашней_команды, id_гостевой_команды, дата_время) VALUES (?, ?, ?)",
                (match.id_home_team, match.id_away_team, match.date_time)
            )
            conn.commit()
            return cursor.lastrowid

    def get_all(self) -> List[Match]:
        """R - Получить все матчи"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_матча, id_домашней_команды, id_гостевой_команды, дата_время FROM Matches")
            return [Match(id_matches=row[0], id_home_team=row[1], id_away_team=row[2], date_time=row[3]) 
                    for row in cursor.fetchall()]


class StatRepository:
    """Репозиторий для управления голами и нарушениями (PlayerStats)"""
    def __init__(self, db_path: str):
        self.db_path = db_path

    def add_event(self, stat: PlayerStat) -> int:
        """C - Записать гол или карточку игрока в матче"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO PlayerStats (id_матча, id_игрока, забитые_мячи, желтые_карточки, красные_карточки) VALUES (?, ?, ?, ?, ?)",
                (stat.id_matches, stat.id_players, stat.goals, stat.yellow_cards, stat.red_cards)
            )
            conn.commit()
            return cursor.lastrowid
            
    def get_stats_by_match(self, id_matches: int) -> List[PlayerStat]:
        """R - Получить всю статистику по конкретному матчу"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_записи, id_матча, id_игрока, забитые_мячи, желтые_карточки, красные_карточки FROM PlayerStats WHERE id_матча = ?",
                (id_matches,)
            )
            return [PlayerStat(id_stat=row[0], id_matches=row[1], id_players=row[2], goals=row[3], yellow_cards=row[4], red_cards=row[5])
                    for row in cursor.fetchall()]
class UserRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_user_by_login(self, login: str) -> Optional[User]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_пользователя, логин, пароль FROM Users WHERE логин = ?", 
                (login,)
            )
            row = cursor.fetchone()
            if row:
                return User(id_пользователя=row[0], логин=row[1], пароль=row[2])
            return None


