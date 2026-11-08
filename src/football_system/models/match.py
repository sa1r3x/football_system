from dataclasses import dataclass
from typing import Optional


@dataclass
class Match:
    """Модель матча."""

    id_matches: Optional[int]
    id_home_team: int  # Ссылка на домашнюю команду (FK)
    id_away_team: int  # Ссылка на гостевую команду (FK)
    date_time: str
    score: Optional[str] = None  # Счёт может быть не выставлен (NULL)
