import os
import sys
import sqlite3

sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'football_system'))

try:
    from models import Team, Player, Match, PlayerStat
    from repositories import TeamRepository, PlayerRepository, MatchRepository, StatRepository
    from services import LeagueService
except ImportError as e:
    print(f"Ошибка импорта. Проверь структуру папок! Детали: {e}")
    sys.exit(1)

sys.stdout.reconfigure(encoding='utf-8')

# База данных лежит в той же папке, что и сам main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'football.db')

team_repo = TeamRepository(DB_PATH)
player_repo = PlayerRepository(DB_PATH)
match_repo = MatchRepository(DB_PATH)
stat_repo = StatRepository(DB_PATH)
service = LeagueService(team_repo, player_repo, match_repo, stat_repo)

def display_tournament_table():
    print("\n=== ТУРНИРНАЯ ТАБЛИЦА ===")
    table = service.generate_tournament_table()
    if not table:
        print("Команд пока нет в турнире.")
        return
    
    print(f"{'№':<3} | {'Команда':<20} | {'Игры':<6} | {'Победы':<7} | {'Ничьи':<6} | {'Поражения':<9} | {'Очки':<5}")
    print("-" * 72)
    
    for idx, row in enumerate(table, 1):
        print(f"{idx:<3} | {row['Название']:<20} | {row['Игр']:<6} | {row['Побед']:<7} | {row['Ничьих']:<6} | {row['Поражений']:<9} | {row['Очки']:<5}")

def display_matches():
    print("\n=== РАСПИСАНИЕ И РЕЗУЛЬТАТЫ МАТЧЕЙ ===")
    matches = match_repo.get_all()
    if not matches:
        print("Матчей пока не запланировано.")
        return
    for m in matches:
        home_team = team_repo.get_by_id(m.id_home_team)
        away_team = team_repo.get_by_id(m.id_away_team)
        home_name = home_team.name if home_team else f"ID {m.id_home_team}"
        away_name = away_team.name if away_team else f"ID {m.id_away_team}"
        current_score = service.get_calculated_match_score(m.id_matches)
        print(f"Матч №{m.id_matches} | {m.date_time} | {home_name} {current_score} {away_name}")

def display_player_stats():
    """Новая функция: Вывод общей статистики игроков турнира"""
    print("\n=== СТАТИСТИКА ИГРОКОВ ТУРНИРА ===")
    stats = service.get_all_players_statistics()
    if not stats:
        print("Игроков или статистики пока нет в базе.")
        return
    print(f"{'ФИО':<20} | {'Команда':<15} | {'№':<3} | {'Позиция':<12} | {'Голы':<5} | {'ЖК':<3} | {'КК':<3}")
    print("-" * 75)
    for row in stats:
        print(f"{row['ФИО']:<20} | {row['Команда']:<15} | {row['Номер']:<3} | {row['Позиция']:<12} | {row['Голы']:<5} | {row['ЖК']:<3} | {row['КК']:<3}")

def fan_menu():
    while True:
        print("\n--- МЕНЮ БОЛЕЛЬЩИКА ---")
        print("1. Посмотреть турнирную таблицу")
        print("2. Посмотреть расписание и результаты матчей")
        print("3. Посмотреть общую статистику игроков (Бомбардиры/Штрафы)")
        print("0. Выйти в главное меню выбора ролей")
        
        choice = input("Выберите действие: ")
        if choice == "1":
            display_tournament_table()
        elif choice == "2":
            display_matches()
        elif choice == "3":
            display_player_stats()
        elif choice == "0":
            break
        else:
            print("Неверный ввод, попробуйте снова.")

def admin_menu():
    while True:
        print("\n--- МЕНЮ АДМИНИСТРАТОРА (СУДЬИ) ---")
        print("1. Зарегистрировать новую команду")
        print("2. Добавить футболиста в состав")
        print("3. Запланировать новый матч")
        print("4. Зафиксировать ГОЛ в матче")
        print("5. Зафиксировать КАРТОЧКУ (желтая/красная)")
        print("6. Посмотреть турнирную таблицу")
        print("7. Посмотреть расписание матчей")
        print("8. Посмотреть общую статистику игроков")
        print("0. Выйти в главное меню выбора ролей")
        
        choice = input("Выберите действие: ")
        
        try:
            if choice == "1":
                name = input("Введите название команды (института): ")
                new_id = service.register_team(name)
                print(f"Успешно! Команда '{name}' добавлена с ID: {new_id}")
                
            elif choice == "2":
                print("\nСписок доступных команд:")
                for t in team_repo.get_all():
                    print(f"ID: {t.id_teams} | {t.name}")
                id_team = int(input("Введите ID команды, куда добавить игрока: "))
                fio = input("Введите ФИО футболиста: ")
                num = int(input("Введите игровой номер (1-99): "))
                pos = input("Введите позицию (Нападающий/Вратарь/Защитник/Универсал): ")
                new_p_id = service.add_player_to_team(id_team, fio, num, pos)
                print(f"Успешно! Игрок {fio} добавлен под ID: {new_p_id}")
                
            elif choice == "3":
                print("\nСписок доступных команд:")
                for t in team_repo.get_all():
                    print(f"ID: {t.id_teams} | {t.name}")
                id_home = int(input("Введите ID домашней команды: "))
                id_away = int(input("Введите ID гостевой команды: "))
                dt = input("Введите дату и время матча: ")
                new_m_id = service.schedule_match(id_home, id_away, dt)
                print(f"Успешно! Матч №{new_m_id} добавлен в расписание.")
                
            elif choice == "4":
                display_matches()
                id_m = int(input("Введите номер матча: "))
                fio_search = input("Введите ФИО игрока, забившего гол: ")
                
                all_teams = team_repo.get_all()
                found_player = None
                for t in all_teams:
                    for p in player_repo.get_all_by_team(t.id_teams):
                        if p.fio.lower() == fio_search.lower():
                            found_player = p
                            break
                
                if found_player:
                    service.record_goal(id_m, found_player.id_players)
                    print(f"Гол игрока {found_player.fio} успешно занесен в протокол!")
                else:
                    print("Игрок с таким ФИО не найден в базе данных.")
                    
            elif choice == "5":
                display_matches()
                id_m = int(input("Введите номер матча: "))
                fio_search = input("Введите ФИО нарушителя: ")
                ctype = input("Тип карточки (желтая/красная): ")
                
                all_teams = team_repo.get_all()
                found_player = None
                for t in all_teams:
                    for p in player_repo.get_all_by_team(t.id_teams):
                        if p.fio.lower() == fio_search.lower():
                            found_player = p
                            break
                            
                if found_player:
                    service.record_card(id_m, found_player.id_players, ctype)
                    print(f"Карточка ({ctype}) игроку {found_player.fio} успешно добавлена.")
                else:
                    print("Игрок с таким ФИО не найден.")
                    
            elif choice == "6":
                display_tournament_table()
            elif choice == "7":
                display_matches()
            elif choice == "8":
                display_player_stats()
            elif choice == "0":
                break
            else:
                print("Неверный ввод.")
        except Exception as e:
            print(f"\n[ОШИБКА БИЗНЕС-ЛОГИКИ]: {e}")

def main():
    while True:
        print("\n=============================================")
        print("ДОБРО ПОЖАЛОВАТЬ В СИСТЕМУ УПРАВЛЕНИЯ ТУРНИРОМ")
        print("=============================================")
        print("Выберите вашу роль в системе:")
        print("1. Войти как Болельщик (Только просмотр данных)")
        print("2. Войти как Администратор / Судья (Полный доступ)")
        print("0. Закрыть приложение")
        
        role = input("Введите номер роли: ")
        if role == "1":
            fan_menu()
        elif role == "2":
            admin_menu()
        elif role == "0":
            print("Приложение закрыто. Удачи в турнире!")
            break
        else:
            print("Ошибка: выберите 1, 2 или 0.")

if __name__ == "__main__":
    main()


