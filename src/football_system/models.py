from dataclasses import dataclass
from typing import Optional

@dataclass
class Team:
    """Модель команды"""
    id_teams: Optional[int]  
    name: str
    faculty: Optional[str] = None  # None для новых команд, которые еще не в базе


@dataclass
class Player:
    """Модель игрока"""
    id_players: Optional[int]
    id_teams: int            # Ссылка на команду (FK)
    fio: str
    number: int
    position: str


@dataclass
class Match:
    """Модель матча"""
    id_matches: Optional[int]
    id_home_team: int        # Ссылка на домашнюю команду (FK)
    id_away_team: int        # Ссылка на гостевую команду (FK)
    date_time: str
    score: Optional[str] = None  # Счёт может быть не выставлен (NULL)


@dataclass
class PlayerStat:
    """Модель статистики игрока в конкретном матче"""
    id_stat: Optional[int]
    id_matches: int          # Ссылка на матч (FK)
    id_players: int          # Ссылка на игрока (FK)
    goals: int = 0
    yellow_cards: int = 0
    red_cards: int = 0
