from dataclasses import dataclass
from typing import Optional


@dataclass
class Team:
    """Модель команды."""

    id_teams: Optional[int]
    name: str
    faculty: Optional[str] = None  # None для новых команд, которые еще не в базе
