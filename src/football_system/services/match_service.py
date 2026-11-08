from typing import List, Optional

from src.football_system.models import Match
from src.football_system.repositories import (
    MatchRepository,
    PlayerRepository,
    StatRepository,
    TeamRepository,
)


class MatchService:
    """Бизнес-логика планирования матчей и расчёта счёта."""

    def __init__(
        self,
        match_repo: MatchRepository,
        team_repo: TeamRepository,
        player_repo: PlayerRepository,
        stat_repo: StatRepository,
    ):
        self.match_repo = match_repo
        self.team_repo = team_repo
        self.player_repo = player_repo
        self.stat_repo = stat_repo

    def schedule_match(
        self,
        id_home_team: int,
        id_away_team: int,
        date_time: str,
    ) -> int:
        """Планирует матч после проверки команд и даты."""
        date_time = date_time.strip()
        if not date_time:
            raise ValueError("Дата и время матча не могут быть пустыми!")

        if id_home_team == id_away_team:
            raise ValueError("Команда не может играть матч сама с собой!")

        if self.team_repo.get_by_id(id_home_team) is None:
            raise ValueError(f"Домашняя команда с ID {id_home_team} не найдена!")

        if self.team_repo.get_by_id(id_away_team) is None:
            raise ValueError(f"Гостевая команда с ID {id_away_team} не найдена!")

        match = Match(
            id_matches=None,
            id_home_team=id_home_team,
            id_away_team=id_away_team,
            date_time=date_time,
        )
        return self.match_repo.add(match)

    def get_all_matches(self) -> List[Match]:
        return self.match_repo.get_all()

    def get_match(self, id_matches: int) -> Optional[Match]:
        return self.match_repo.get_by_id(id_matches)

    def get_calculated_match_score(self, id_matches: int) -> str:
        """Считает счёт матча по записанным голам игроков."""
        current_match = self.match_repo.get_by_id(id_matches)
        if not current_match:
            return "0:0"

        home_players_ids = [
            player.id_players
            for player in self.player_repo.get_all_by_team(
                current_match.id_home_team
            )
        ]
        away_players_ids = [
            player.id_players
            for player in self.player_repo.get_all_by_team(
                current_match.id_away_team
            )
        ]

        match_stats = self.stat_repo.get_stats_by_match(id_matches)
        home_goals = sum(
            stat.goals
            for stat in match_stats
            if stat.id_players in home_players_ids
        )
        away_goals = sum(
            stat.goals
            for stat in match_stats
            if stat.id_players in away_players_ids
        )

        return f"{home_goals}:{away_goals}"
