from typing import List, Optional

from src.football_system.models import Team
from src.football_system.repositories import TeamRepository


class TeamService:
    """Бизнес-логика работы с командами."""

    def __init__(self, team_repo: TeamRepository):
        self.team_repo = team_repo

    def register_team(self, name: str) -> int:
        """Регистрирует новую команду с проверкой названия."""
        name = name.strip()
        if not name:
            raise ValueError("Название команды не может быть пустым!")

        team = Team(id_teams=None, name=name)
        return self.team_repo.add(team)

    def get_all_teams(self) -> List[Team]:
        return self.team_repo.get_all()

    def get_team(self, id_teams: int) -> Optional[Team]:
        return self.team_repo.get_by_id(id_teams)
