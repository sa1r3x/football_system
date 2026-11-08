from typing import List

from src.football_system.models import Match, PlayerStat
from src.football_system.repositories import (
    MatchRepository,
    PlayerRepository,
    StatRepository,
    TeamRepository,
)


class StatService:
    """Бизнес-логика фиксации голов, карточек и дисквалификаций."""

    def __init__(
        self,
        stat_repo: StatRepository,
        match_repo: MatchRepository,
        player_repo: PlayerRepository,
        team_repo: TeamRepository,
    ):
        self.stat_repo = stat_repo
        self.match_repo = match_repo
        self.player_repo = player_repo
        self.team_repo = team_repo

    def _get_player_team_matches(self, id_players: int) -> List[Match]:
        """Находит все матчи команды игрока в хронологическом порядке."""
        player = self.player_repo.get_by_id(id_players)
        if not player:
            return []

        team_matches = [
            match
            for match in self.match_repo.get_all()
            if match.id_home_team == player.id_teams
            or match.id_away_team == player.id_teams
        ]
        team_matches.sort(key=lambda match: match.id_matches)
        return team_matches

    def check_player_ban(self, id_matches: int, id_players: int) -> bool:
        """Проверяет, дисквалифицирован ли игрок на текущий матч."""
        team_matches = self._get_player_team_matches(id_players)

        current_index = next(
            (
                index
                for index, match in enumerate(team_matches)
                if match.id_matches == id_matches
            ),
            -1,
        )
        if current_index <= 0:
            return False

        previous_match = team_matches[current_index - 1]
        previous_stats = self.stat_repo.get_stats_by_match(
            previous_match.id_matches
        )
        player_previous_stats = [
            stat
            for stat in previous_stats
            if stat.id_players == id_players
        ]

        return any(stat.red_cards > 0 for stat in player_previous_stats)

    def record_goal(self, id_matches: int, id_players: int) -> None:
        """Фиксирует гол с проверкой дисквалификации игрока."""
        if self.check_player_ban(id_matches, id_players):
            raise ValueError(
                "Действие отклонено! Игрок дисквалифицирован "
                "(отрабатывает бан за красную карточку в прошлом матче)."
            )

        stat = PlayerStat(
            id_stat=None,
            id_matches=id_matches,
            id_players=id_players,
            goals=1,
        )
        self.stat_repo.add_event(stat)

    def record_card(
        self,
        id_matches: int,
        id_players: int,
        card_type: str,
    ) -> None:
        """Фиксирует карточку с учётом накопления и сброса жёлтых."""
        if self.check_player_ban(id_matches, id_players):
            raise ValueError(
                "Действие отклонено! Игрок дисквалифицирован "
                "из-за бана в прошлом матче."
            )

        card_type_lower = card_type.strip().lower()

        if card_type_lower == "красная":
            stat = PlayerStat(
                id_stat=None,
                id_matches=id_matches,
                id_players=id_players,
                red_cards=1,
            )
            self.stat_repo.add_event(stat)
            return

        if card_type_lower == "желтая":
            current_match_stats = self.stat_repo.get_stats_by_match(id_matches)
            current_match_yellows = sum(
                stat.yellow_cards
                for stat in current_match_stats
                if stat.id_players == id_players
            )

            if current_match_yellows >= 1:
                stat = PlayerStat(
                    id_stat=None,
                    id_matches=id_matches,
                    id_players=id_players,
                    yellow_cards=0,
                    red_cards=1,
                )
                self.stat_repo.add_event(stat)
                raise ValueError(
                    "Вторая желтая в одном матче! Карточки сброшены, "
                    "игрок получил КРАСНУЮ и удален."
                )

            team_matches = self._get_player_team_matches(id_players)
            current_index = next(
                (
                    index
                    for index, match in enumerate(team_matches)
                    if match.id_matches == id_matches
                ),
                -1,
            )

            if current_index > 0:
                previous_match = team_matches[current_index - 1]
                previous_match_stats = self.stat_repo.get_stats_by_match(
                    previous_match.id_matches
                )
                previous_yellows = sum(
                    stat.yellow_cards
                    for stat in previous_match_stats
                    if stat.id_players == id_players
                )
                previous_reds = sum(
                    stat.red_cards
                    for stat in previous_match_stats
                    if stat.id_players == id_players
                )

                if previous_yellows > 0 and previous_reds == 0:
                    stat = PlayerStat(
                        id_stat=None,
                        id_matches=id_matches,
                        id_players=id_players,
                        yellow_cards=0,
                        red_cards=1,
                    )
                    self.stat_repo.add_event(stat)
                    raise ValueError(
                        "Накопление! Игрок получил желтую карточку второй "
                        "матч подряд. Желтые сброшены, начислена КРАСНАЯ."
                    )

            stat = PlayerStat(
                id_stat=None,
                id_matches=id_matches,
                id_players=id_players,
                yellow_cards=1,
            )
            self.stat_repo.add_event(stat)
            return

        raise ValueError(
            "Неверный тип карточки! Должно быть 'желтая' или 'красная'"
        )

    def get_stats_by_match(self, id_matches: int) -> List[PlayerStat]:
        return self.stat_repo.get_stats_by_match(id_matches)
