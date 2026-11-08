import sys
from pathlib import Path

# Позволяет запускать файл напрямую: python src/football_system/main.py
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.football_system.database.database import DB_PATH
from src.football_system.menu import Menu
from src.football_system.repositories import (
    MatchRepository,
    PlayerRepository,
    StatRepository,
    TeamRepository,
    UserRepository,
)
from src.football_system.services import (
    AuthService,
    ExporterService,
    MatchService,
    PlayerService,
    StatService,
    TeamService,
    TournamentService,
)


def main() -> None:
    """Инициализирует зависимости и запускает консольное меню."""
    team_repo = TeamRepository(db_path=DB_PATH)
    player_repo = PlayerRepository(db_path=DB_PATH)
    match_repo = MatchRepository(db_path=DB_PATH)
    stat_repo = StatRepository(db_path=DB_PATH)
    user_repo = UserRepository(db_path=DB_PATH)

    menu = Menu(
        auth_service=AuthService(user_repo),
        team_service=TeamService(team_repo),
        player_service=PlayerService(player_repo, team_repo),
        match_service=MatchService(
            match_repo,
            team_repo,
            player_repo,
            stat_repo,
        ),
        stat_service=StatService(
            stat_repo,
            match_repo,
            player_repo,
            team_repo,
        ),
        tournament_service=TournamentService(
            team_repo,
            player_repo,
            match_repo,
            stat_repo,
        ),
        exporter_service=ExporterService(player_repo),
    )
    menu.run()


if __name__ == "__main__":
    main()
