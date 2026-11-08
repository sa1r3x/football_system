from typing import Any, Dict, List

from src.football_system.repositories import (
    MatchRepository,
    PlayerRepository,
    StatRepository,
    TeamRepository,
)
from src.football_system.services.match_service import MatchService
from src.football_system.services.player_service import PlayerService
from src.football_system.services.stat_service import StatService
from src.football_system.services.team_service import TeamService
from src.football_system.services.tournament_service import TournamentService


class LeagueService:
    """Фасад над предметными сервисами для обратной совместимости."""

    def __init__(
        self,
        team_repo: TeamRepository,
        player_repo: PlayerRepository,
        match_repo: MatchRepository,
        stat_repo: StatRepository,
    ):
        self.team_service = TeamService(team_repo)
        self.player_service = PlayerService(player_repo, team_repo)
        self.match_service = MatchService(
            match_repo,
            team_repo,
            player_repo,
            stat_repo,
        )
        self.stat_service = StatService(
            stat_repo,
            match_repo,
            player_repo,
            team_repo,
        )
        self.tournament_service = TournamentService(
            team_repo,
            player_repo,
            match_repo,
            stat_repo,
        )

    def register_team(self, name: str) -> int:
        return self.team_service.register_team(name)

    def add_player_to_team(
        self,
        id_teams: int,
        fio: str,
        number: int,
        position: str,
    ) -> int:
        return self.player_service.add_player_to_team(
            id_teams,
            fio,
            number,
            position,
        )

    def schedule_match(
        self,
        id_home_team: int,
        id_away_team: int,
        date_time: str,
    ) -> int:
        return self.match_service.schedule_match(
            id_home_team,
            id_away_team,
            date_time,
        )

    def check_player_ban(self, id_matches: int, id_players: int) -> bool:
        return self.stat_service.check_player_ban(id_matches, id_players)

    def record_goal(self, id_matches: int, id_players: int) -> None:
        self.stat_service.record_goal(id_matches, id_players)

    def record_card(
        self,
        id_matches: int,
        id_players: int,
        card_type: str,
    ) -> None:
        self.stat_service.record_card(id_matches, id_players, card_type)

    def get_calculated_match_score(self, id_matches: int) -> str:
        return self.match_service.get_calculated_match_score(id_matches)

    def generate_tournament_table(self) -> List[Dict[str, Any]]:
        return self.tournament_service.generate_tournament_table()

    def get_all_players_statistics(self) -> List[Dict[str, Any]]:
        return self.tournament_service.get_all_players_statistics()
