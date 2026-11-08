from dataclasses import dataclass
from typing import Optional


@dataclass
class PlayerStat:
    """Модель статистики игрока в конкретном матче."""

    id_stat: Optional[int]
    id_matches: int  # Ссылка на матч (FK)
    id_players: int  # Ссылка на игрока (FK)
    goals: int = 0
    yellow_cards: int = 0
    red_cards: int = 0
