from typing import List, Dict, Any
from models import Team, Player, Match, PlayerStat
from repositories import TeamRepository, PlayerRepository, MatchRepository, StatRepository

class LeagueService:
    """Мозги футбольной системы с накопительными желтыми картами и отработкой бана"""
    def __init__(
        self, 
        team_repo: TeamRepository, 
        player_repo: PlayerRepository, 
        match_repo: MatchRepository, 
        stat_repo: StatRepository
    ):
        self.team_repo = team_repo
        self.player_repo = player_repo
        self.match_repo = match_repo
        self.stat_repo = stat_repo

    # ЛОГИКА ДЛЯ КОМАНД И ИГРОКОВ 
    def register_team(self, name: str) -> int:
        if not name.strip():
            raise ValueError("Название команды не может быть пустым!")
        team = Team(id_teams=None, name=name)
        return self.team_repo.add(team)

    def add_player_to_team(self, id_teams: int, fio: str, number: int, position: str) -> int:
        if number < 1 or number > 99:
            raise ValueError("Игровой номер футболиста должен быть от 1 до 99!")
        player = Player(id_players=None, id_teams=id_teams, fio=fio, number=number, position=position)
        return self.player_repo.add(player)

    # СЛОЖНАЯ БИЗНЕС-ЛОГИКА: НАКОПЛЕНИЕ КАРТОЧЕК И БАНЫ 
    
    def _get_player_team_matches(self, id_players: int) -> List[Match]:
        """Вспомогательный метод: находит все матчи конкретной команды игрока, отсортированные по хронологии"""
        # Находим, в какой команде играет футболист
        all_players = []
        for team in self.team_repo.get_all():
            all_players.extend(self.player_repo.get_all_by_team(team.id_teams))
        
        player = next((p for p in all_players if p.id_players == id_players), None)
        if not player:
            return []
            
        # Находим все матчи этой команды
        team_matches = [
            m for m in self.match_repo.get_all() 
            if m.id_home_team == player.id_teams or m.id_away_team == player.id_teams
        ]
        # Сортируем по ID матча (хронология турнира)
        team_matches.sort(key=lambda m: m.id_matches)
        return team_matches

    def check_player_ban(self, id_matches: int, id_players: int) -> bool:
        """
        Проверяет, забанен ли игрок на текущий матч.
        Игрок забанен, если в ПРЕДЫДУЩЕМ матче своей команды он заработал красную карточку
        (напрямую или через накопительные желтые).
        """
        team_matches = self._get_player_team_matches(id_players)
        
        # Находим индекс текущего матча в истории команды
        current_index = next((i for i, m in enumerate(team_matches) if m.id_matches == id_matches), -1)
        if current_index <= 0:
            return False  # Это первый матч команды, банов быть не может

        # Берем самый последний прошедший матч этой команды
        prev_match = team_matches[current_index - 1]
        
        # Проверяем, были ли у игрока красные карточки в том матче
        prev_stats = self.stat_repo.get_stats_by_match(prev_match.id_matches)
        player_prev_stats = [s for s in prev_stats if s.id_players == id_players]
        
        # Если в предыдущей игре была хоть одна красная — сегодня игрок сидит на трибуне (бан)
        # Как только этот матч пройдет, в следующем матче (current_index + 1) prev_match уже сменится,
        # то есть красная автоматически «сбросится»
        for s in player_prev_stats:
            if s.red_cards > 0:
                return True
        return False

    def record_goal(self, id_matches: int, id_players: int) -> None:
        """Зафиксировать гол с проверкой бана"""
        if self.check_player_ban(id_matches, id_players):
            raise ValueError("Действие отклонено! Игрок дисквалифицирован (отрабатывает бан за красную карту в прошлом матче).")
        stat = PlayerStat(id_stat=None, id_matches=id_matches, id_players=id_players, goals=1)
        self.stat_repo.add_event(stat)

    def record_card(self, id_matches: int, id_players: int, card_type: str) -> None:
        """Зафиксировать карточку с проверкой межматчевого накопления и сброса"""
        if self.check_player_ban(id_matches, id_players):
            raise ValueError("Действие отклонено! Игрок дисквалифицирован из-за бана в прошлом матче.")
            
        card_type_lower = card_type.lower()
        
        if card_type_lower == "красная":
            # Прямое удаление с поля
            stat = PlayerStat(id_stat=None, id_matches=id_matches, id_players=id_players, red_cards=1)
            self.stat_repo.add_event(stat)
            return

        if card_type_lower == "желтая":
            # 1. Сначала проверяем классику: получил ли он ВТОРУЮ желтую в ЭТОМ ЖЕ матче
            current_match_stats = self.stat_repo.get_stats_by_match(id_matches)
            current_match_yellows = sum(s.yellow_cards for s in current_match_stats if s.id_players == id_players)
            
            if current_match_yellows >= 1:
                # Вторая желтая в одном матче -> желтые сгорают до 0, красная += 1, удаление!
                stat = PlayerStat(id_stat=None, id_matches=id_matches, id_players=id_players, yellow_cards=0, red_cards=1)
                self.stat_repo.add_event(stat)
                raise ValueError("Вторая желтая в одном матче! Карточки сброшены, игрок получил КРАСНУЮ и удален.")

            # 2. Если в этом матче желтых не было, проверяем НАКОПЛЕНИЕ с прошлого матча
            team_matches = self._get_player_team_matches(id_players)
            current_index = next((i for i, m in enumerate(team_matches) if m.id_matches == id_matches), -1)
            
            if current_index > 0:
                prev_match = team_matches[current_index - 1]
                prev_match_stats = self.stat_repo.get_stats_by_match(prev_match.id_matches)
                
                # Смотрим, получал ли он желтую в прошлом матче
                prev_yellows = sum(s.yellow_cards for s in prev_match_stats if s.id_players == id_players)
                # Проверяем, не было ли там при этом красной (если была красная, значит те желтые уже сгорели)
                prev_reds = sum(s.red_cards for s in prev_match_stats if s.id_players == id_players)
                
                if prev_yellows > 0 and prev_reds == 0:
                    # получил желтую подряд во втором матче -> желтые в 0, красная += 1!
                    stat = PlayerStat(id_stat=None, id_matches=id_matches, id_players=id_players, yellow_cards=0, red_cards=1)
                    self.stat_repo.add_event(stat)
                    raise ValueError("Накопление! Игрок получил желтую карточку второй матч подряд. Желтые сброшены, начислена КРАСНАЯ.")
            
            # 3. Если прошлый матч был чистым или это первая игра — просто записываем обычную желтую
            stat = PlayerStat(id_stat=None, id_matches=id_matches, id_players=id_players, yellow_cards=1)
            self.stat_repo.add_event(stat)
            
        else:
            raise ValueError("Неверный тип карточки! Должно быть 'желтая' или 'красная'")

    # ВЫЧИСЛЯЕМАЯ АВТОМАТИКА ДЛЯ ТАБЛИЦ 
    def get_calculated_match_score(self, id_matches: int) -> str:
        all_matches = self.match_repo.get_all()
        current_match = next((m for m in all_matches if m.id_matches == id_matches), None)
        if not current_match:
            return "0:0"

        home_players_ids = [p.id_players for p in self.player_repo.get_all_by_team(current_match.id_home_team)]
        away_players_ids = [p.id_players for p in self.player_repo.get_all_by_team(current_match.id_away_team)]

        match_stats = self.stat_repo.get_stats_by_match(id_matches)
        home_goals = sum(s.goals for s in match_stats if s.id_players in home_players_ids)
        away_goals = sum(s.goals for s in match_stats if s.id_players in away_players_ids)

        return f"{home_goals}:{away_goals}"

    def generate_tournament_table(self) -> List[Dict[str, Any]]:
        teams = self.team_repo.get_all()
        matches = self.match_repo.get_all()

        table = {t.id_teams: {"Название": t.name, "Игр": 0, "Побед": 0, "Ничьих": 0, "Поражений": 0, "Очки": 0} for t in teams}

        for m in matches:
            score_str = self.get_calculated_match_score(m.id_matches)
            g_home, g_away = map(int, score_str.split(":"))

            if m.id_home_team in table and m.id_away_team in table:
                # Если счет 0:0 и по нему нет записей голов вообще, считаем матч сыгранным, если он есть в расписании
                table[m.id_home_team]["Игр"] += 1
                table[m.id_away_team]["Игр"] += 1

                if g_home > g_away:
                    table[m.id_home_team]["Побед"] += 1
                    table[m.id_home_team]["Очки"] += 3
                    table[m.id_away_team]["Поражений"] += 1
                elif g_away > g_home:
                    table[m.id_away_team]["Побед"] += 1
                    table[m.id_away_team]["Очки"] += 3
                    table[m.id_home_team]["Поражений"] += 1
                else:
                    table[m.id_home_team]["Ничьих"] += 1
                    table[m.id_home_team]["Очки"] += 1
                    table[m.id_away_team]["Ничьих"] += 1
                    table[m.id_away_team]["Очки"] += 1

        sorted_table = sorted(table.values(), key=lambda x: x["Очки"], reverse=True)
        return sorted_table
    def get_all_players_statistics(self) -> List[Dict[str, Any]]:
        """Автоматический сбор общей статистики по всем игрокам турнира"""
        teams = self.team_repo.get_all()
        stats_report = []

        for team in teams:
            players = self.player_repo.get_all_by_team(team.id_teams)
            for p in players:
                # Ищем всю историю этого игрока в таблице PlayerStats
                all_stats = []
                # Так как у нас нет get_all в StatRepository, мы берем матчи и по ним вытаскиваем статистику
                for m in self.match_repo.get_all():
                    all_stats.extend(self.stat_repo.get_stats_by_match(m.id_matches))
                
                player_events = [s for s in all_stats if s.id_players == p.id_players]
                
                total_goals = sum(s.goals for s in player_events)
                total_yellow = sum(s.yellow_cards for s in player_events)
                total_red = sum(s.red_cards for s in player_events)

                stats_report.append({
                    "ФИО": p.fio,
                    "Команда": team.name,
                    "Номер": p.number,
                    "Позиция": p.position,
                    "Голы": total_goals,
                    "ЖК": total_yellow,
                    "КК": total_red
                })
        
        # Сортируем по голам (лучшие бомбардиры вверху)
        return sorted(stats_report, key=lambda x: x["Голы"], reverse=True)
