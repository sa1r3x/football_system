from typing import List, Optional

from src.football_system.models import Player
from src.football_system.repositories import PlayerRepository, TeamRepository


class PlayerService:
    """Бизнес-логика работы с игроками и их валидацией."""

    MIN_NUMBER = 1
    MAX_NUMBER = 99

    def __init__(
        self,
        player_repo: PlayerRepository,
        team_repo: TeamRepository,
    ):
        self.player_repo = player_repo
        self.team_repo = team_repo

    def add_player_to_team(
        self,
        id_teams: int,
        fio: str,
        number: int,
        position: str,
    ) -> int:
        """Добавляет игрока в команду после проверки входных данных."""
        fio = fio.strip()
        position = position.strip()

        if not fio:
            raise ValueError("ФИО футболиста не может быть пустым!")

        if number < self.MIN_NUMBER or number > self.MAX_NUMBER:
            raise ValueError("Игровой номер футболиста должен быть от 1 до 99!")

        if not position:
            raise ValueError("Позиция футболиста не может быть пустой!")

        if self.team_repo.get_by_id(id_teams) is None:
            raise ValueError(f"Команда с ID {id_teams} не найдена!")

        player = Player(
            id_players=None,
            id_teams=id_teams,
            fio=fio,
            number=number,
            position=position,
        )
        return self.player_repo.add(player)

    def get_all_by_team(self, id_teams: int) -> List[Player]:
        return self.player_repo.get_all_by_team(id_teams)

    def find_by_fio(self, fio: str) -> Optional[Player]:
        """Ищет игрока по ФИО без учёта регистра."""
        search = fio.strip().casefold()
        if not search:
            return None

        for player in self.player_repo.get_all():
            if player.fio.casefold() == search:
                return player
        return None
