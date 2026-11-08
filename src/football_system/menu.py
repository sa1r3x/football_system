import sys

from src.football_system.services import (
    AuthService,
    ExporterService,
    MatchService,
    PlayerService,
    StatService,
    TeamService,
    TournamentService,
)


class Menu:
    """Консольный интерфейс системы управления турниром."""

    def __init__(
        self,
        auth_service: AuthService,
        team_service: TeamService,
        player_service: PlayerService,
        match_service: MatchService,
        stat_service: StatService,
        tournament_service: TournamentService,
        exporter_service: ExporterService,
    ):
        self.auth_service = auth_service
        self.team_service = team_service
        self.player_service = player_service
        self.match_service = match_service
        self.stat_service = stat_service
        self.tournament_service = tournament_service
        self.exporter_service = exporter_service

    def run(self) -> None:
        """Запускает главное меню приложения."""
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")

        self._main_menu()

    # ------------------------------------------------------------------
    # Главное меню и авторизация
    # ------------------------------------------------------------------
    def _main_menu(self) -> None:
        while True:
            print("\n=============================================")
            print("ДОБРО ПОЖАЛОВАТЬ В СИСТЕМУ УПРАВЛЕНИЯ ТУРНИРОМ")
            print("=============================================")
            print("Выберите вашу роль в системе:")
            print("1. Войти как Болельщик (Только просмотр данных)")
            print(
                "2. Войти как Администратор / Судья "
                "(Полный доступ)"
            )
            print("0. Закрыть приложение")

            role = input("Введите номер роли: ")

            if role == "1":
                self._fan_menu()
            elif role == "2":
                self._login_admin()
            elif role == "0":
                print("Приложение закрыто. Удачи в турнире!")
                break
            else:
                print("Ошибка: выберите 1, 2 или 0.")

    def _login_admin(self) -> None:
        print("\n--- АВТОРИЗАЦИЯ АДМИНИСТРАТОРА ---")
        login = input("Введите логин: ")
        password = input("Введите пароль: ")

        user = self.auth_service.authenticate(login, password)

        if user:
            print(f"\n[✓] Успешный вход! Добро пожаловать, {login}.")
            self._admin_menu()
        else:
            print(
                "\n[X] Ошибка: Неверный логин или пароль! "
                "Доступ закрыт."
            )

    # ------------------------------------------------------------------
    # Меню болельщика
    # ------------------------------------------------------------------
    def _fan_menu(self) -> None:
        while True:
            print("\n--- МЕНЮ БОЛЕЛЬЩИКА ---")
            print("1. Посмотреть турнирную таблицу")
            print("2. Посмотреть расписание и результаты матчей")
            print(
                "3. Посмотреть общую статистику игроков "
                "(Бомбардиры/Штрафы)"
            )
            print("0. Выйти в главное меню выбора ролей")

            choice = input("Выберите действие: ")

            if choice == "1":
                self._display_tournament_table()
            elif choice == "2":
                self._display_matches()
            elif choice == "3":
                self._display_player_stats()
            elif choice == "0":
                break
            else:
                print("Неверный ввод, попробуйте снова.")

    # ------------------------------------------------------------------
    # Меню администратора
    # ------------------------------------------------------------------
    def _admin_menu(self) -> None:
        while True:
            print("\n--- МЕНЮ АДМИНИСТРАТОРА (СУДЬИ) ---")
            print("1. Зарегистрировать новую команду")
            print("2. Добавить футболиста в состав")
            print("3. Запланировать новый матч")
            print("4. Зафиксировать ГОЛ в матче")
            print("5. Зафиксировать КАРТОЧКУ (желтая/красная)")
            print("6. Экспорт данных в out/")
            print("0. Выйти в главное меню выбора ролей")

            choice = input("Выберите действие: ")

            try:
                if choice == "1":
                    self._register_team()
                elif choice == "2":
                    self._add_player()
                elif choice == "3":
                    self._schedule_match()
                elif choice == "4":
                    self._record_goal()
                elif choice == "5":
                    self._record_card()
                elif choice == "6":
                    self._export_data()
                elif choice == "0":
                    break
                else:
                    print("Неверный ввод.")
            except Exception as error:
                print(f"\n[ОШИБКА БИЗНЕС-ЛОГИКИ]: {error}")

    def _register_team(self) -> None:
        name = input("Введите название команды (института): ")
        new_id = self.team_service.register_team(name)
        print(f"Успешно! Команда '{name.strip()}' добавлена с ID: {new_id}")

    def _add_player(self) -> None:
        self._display_teams()
        id_team = int(
            input("Введите ID команды, куда добавить игрока: ")
        )
        fio = input("Введите ФИО футболиста: ")
        number = int(input("Введите игровой номер (1-99): "))
        position = input(
            "Введите позицию "
            "(Нападающий/Вратарь/Защитник/Универсал): "
        )

        new_player_id = self.player_service.add_player_to_team(
            id_team,
            fio,
            number,
            position,
        )
        print(
            f"Успешно! Игрок {fio.strip()} добавлен под ID: "
            f"{new_player_id}"
        )

    def _schedule_match(self) -> None:
        self._display_teams()
        id_home = int(input("Введите ID домашней команды: "))
        id_away = int(input("Введите ID гостевой команды: "))
        date_time = input("Введите дату и время матча: ")

        new_match_id = self.match_service.schedule_match(
            id_home,
            id_away,
            date_time,
        )
        print(
            f"Успешно! Матч №{new_match_id} добавлен в расписание."
        )

    def _record_goal(self) -> None:
        self._display_matches()
        id_match = int(input("Введите номер матча: "))
        fio = input("Введите ФИО игрока, забившего гол: ")

        player = self.player_service.find_by_fio(fio)
        if not player:
            print("Игрок с таким ФИО не найден в базе данных.")
            return

        self.stat_service.record_goal(id_match, player.id_players)
        print(
            f"Гол игрока {player.fio} успешно занесен в протокол!"
        )

    def _record_card(self) -> None:
        self._display_matches()
        id_match = int(input("Введите номер матча: "))
        fio = input("Введите ФИО нарушителя: ")
        card_type = input("Тип карточки (желтая/красная): ")

        player = self.player_service.find_by_fio(fio)
        if not player:
            print("Игрок с таким ФИО не найден.")
            return

        self.stat_service.record_card(
            id_match,
            player.id_players,
            card_type,
        )
        print(
            f"Карточка ({card_type}) игроку {player.fio} "
            "успешно добавлена."
        )

    def _export_data(self) -> None:
        paths = self.exporter_service.export_players()
        print("\nЭкспорт данных завершён:")
        for file_format, path in paths.items():
            print(f"  {file_format.upper()}: {path}")

    # ------------------------------------------------------------------
    # Отображение данных
    # ------------------------------------------------------------------
    def _display_teams(self) -> None:
        print("\nСписок доступных команд:")
        for team in self.team_service.get_all_teams():
            print(f"ID: {team.id_teams} | {team.name}")

    def _display_tournament_table(self) -> None:
        print("\n=== ТУРНИРНАЯ ТАБЛИЦА ===")
        table = self.tournament_service.generate_tournament_table()
        if not table:
            print("Команд пока нет в турнире.")
            return

        print(
            f"{'№':<3} | {'Команда':<20} | {'Игры':<6} | "
            f"{'Победы':<7} | {'Ничьи':<6} | {'Поражения':<9} | "
            f"{'Очки':<5}"
        )
        print("-" * 72)

        for index, row in enumerate(table, 1):
            print(
                f"{index:<3} | {row['Название']:<20} | "
                f"{row['Игр']:<6} | {row['Побед']:<7} | "
                f"{row['Ничьих']:<6} | {row['Поражений']:<9} | "
                f"{row['Очки']:<5}"
            )

    def _display_matches(self) -> None:
        print("\n=== РАСПИСАНИЕ И РЕЗУЛЬТАТЫ МАТЧЕЙ ===")
        matches = self.match_service.get_all_matches()
        if not matches:
            print("Матчей пока не запланировано.")
            return

        for match in matches:
            home_team = self.team_service.get_team(match.id_home_team)
            away_team = self.team_service.get_team(match.id_away_team)
            home_name = (
                home_team.name
                if home_team
                else f"ID {match.id_home_team}"
            )
            away_name = (
                away_team.name
                if away_team
                else f"ID {match.id_away_team}"
            )
            current_score = self.match_service.get_calculated_match_score(
                match.id_matches
            )
            print(
                f"Матч №{match.id_matches} | {match.date_time} | "
                f"{home_name} {current_score} {away_name}"
            )

    def _display_player_stats(self) -> None:
        print("\n=== СТАТИСТИКА ИГРОКОВ ТУРНИРА ===")
        stats = self.tournament_service.get_all_players_statistics()
        if not stats:
            print("Игроков или статистики пока нет в базе.")
            return

        print(
            f"{'ФИО':<20} | {'Команда':<15} | {'№':<3} | "
            f"{'Позиция':<12} | {'Голы':<5} | {'ЖК':<3} | {'КК':<3}"
        )
        print("-" * 75)

        for row in stats:
            print(
                f"{row['ФИО']:<20} | {row['Команда']:<15} | "
                f"{row['Номер']:<3} | {row['Позиция']:<12} | "
                f"{row['Голы']:<5} | {row['ЖК']:<3} | {row['КК']:<3}"
            )
