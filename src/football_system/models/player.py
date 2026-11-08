from dataclasses import dataclass
from typing import Optional


@dataclass
class Player:
    """Модель игрока."""

    id_players: Optional[int]
    id_teams: int  # Ссылка на команду (FK)
    fio: str
    number: int
    position: str
