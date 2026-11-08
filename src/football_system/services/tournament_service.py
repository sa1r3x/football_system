from typing import Any, Dict, List

from src.football_system.repositories import (
    MatchRepository,
    PlayerRepository,
    StatRepository,
    TeamRepository,
)
from src.football_system.services.match_service import MatchService


class TournamentService:
    """Расчёт турнирной таблицы и сводной статистики игроков."""

    def __init__(
        self,
        team_repo: TeamRepository,
        player_repo: PlayerRepository,
        match_repo: MatchRepository,
        stat_repo: StatRepository,
    ):
        self.team_repo = team_repo
        self.player_repo = player_repo
        self.match_repo = match_repo
        self.stat_repo = stat_repo
        self.match_service = MatchService(
            match_repo,
            team_repo,
            player_repo,
            stat_repo,
        )

    def generate_tournament_table(self) -> List[Dict[str, Any]]:
        """Строит турнирную таблицу на основе всех матчей."""
        teams = self.team_repo.get_all()
        matches = self.match_repo.get_all()

        table = {
            team.id_teams: {
                "Название": team.name,
                "Игр": 0,
                "Побед": 0,
                "Ничьих": 0,
                "Поражений": 0,
                "Очки": 0,
            }
            for team in teams
        }

        for match in matches:
            score = self.match_service.get_calculated_match_score(
                match.id_matches
            )
            goals_home, goals_away = map(int, score.split(":"))

            if (
                match.id_home_team not in table
                or match.id_away_team not in table
            ):
                continue

            table[match.id_home_team]["Игр"] += 1
            table[match.id_away_team]["Игр"] += 1

            if goals_home > goals_away:
                table[match.id_home_team]["Побед"] += 1
                table[match.id_home_team]["Очки"] += 3
                table[match.id_away_team]["Поражений"] += 1
            elif goals_away > goals_home:
                table[match.id_away_team]["Побед"] += 1
                table[match.id_away_team]["Очки"] += 3
                table[match.id_home_team]["Поражений"] += 1
            else:
                table[match.id_home_team]["Ничьих"] += 1
                table[match.id_home_team]["Очки"] += 1
                table[match.id_away_team]["Ничьих"] += 1
                table[match.id_away_team]["Очки"] += 1

        return sorted(
            table.values(),
            key=lambda row: row["Очки"],
            reverse=True,
        )

    def get_all_players_statistics(self) -> List[Dict[str, Any]]:
        """Собирает сводную статистику по всем игрокам турнира."""
        teams = self.team_repo.get_all()
        all_stats = self.stat_repo.get_all()
        stats_report: List[Dict[str, Any]] = []

        for team in teams:
            players = self.player_repo.get_all_by_team(team.id_teams)
            for player in players:
                player_events = [
                    stat
                    for stat in all_stats
                    if stat.id_players == player.id_players
                ]

                stats_report.append(
                    {
                        "ФИО": player.fio,
                        "Команда": team.name,
                        "Номер": player.number,
                        "Позиция": player.position,
                        "Голы": sum(stat.goals for stat in player_events),
                        "ЖК": sum(
                            stat.yellow_cards for stat in player_events
                        ),
                        "КК": sum(
                            stat.red_cards for stat in player_events
                        ),
                    }
                )

        return sorted(
            stats_report,
            key=lambda row: row["Голы"],
            reverse=True,
        )
