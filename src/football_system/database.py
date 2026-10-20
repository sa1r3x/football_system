import sqlite3
import os

# 2.1. Подключить базу данных SQLite к проекту
db_path = os.path.join(os.path.dirname(__file__), 'football.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON;")

# 2.2. Создать таблицы с помощью SQL-запросов (CREATE TABLE)
cursor.execute('''
CREATE TABLE IF NOT EXISTS Teams (
    id_команды INTEGER PRIMARY KEY AUTOINCREMENT,
    название TEXT NOT NULL
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Players (
    id_игрока INTEGER PRIMARY KEY AUTOINCREMENT,
    id_команды INTEGER,
    фио TEXT NOT NULL,
    игровой_номер INTEGER,
    позиция TEXT,
    FOREIGN KEY (id_команды) REFERENCES Teams(id_команды) ON DELETE CASCADE
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Matches (
    id_матча INTEGER PRIMARY KEY AUTOINCREMENT,
    id_домашней_команды INTEGER,
    id_гостевой_команды INTEGER,
    дата_время TEXT NOT NULL,
    итоговый_счет TEXT,
    FOREIGN KEY (id_домашней_команды) REFERENCES Teams(id_команды),
    FOREIGN KEY (id_гостевой_команды) REFERENCES Teams(id_команды)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS PlayerStats (
    id_записи INTEGER PRIMARY KEY AUTOINCREMENT,
    id_матча INTEGER,
    id_игрока INTEGER,
    забитые_мячи INTEGER DEFAULT 0,
    желтые_карточки INTEGER DEFAULT 0,
    красные_карточки INTEGER DEFAULT 0,
    FOREIGN KEY (id_матча) REFERENCES Matches(id_матча) ON DELETE CASCADE,
    FOREIGN KEY (id_игрока) REFERENCES Players(id_игрока) ON DELETE CASCADE
);
''')

# 2.3. Добавить несколько тестовых записей в каждую таблицу (INSERT INTO)
cursor.executemany('INSERT INTO Teams (название) VALUES (?);', [
    ('ИРИТ',),
    ('ИНЭУ',)
])

cursor.executemany('INSERT INTO Players (id_команды, фио, игровой_номер, позиция) VALUES (?, ?, ?, ?);', [
    (1, 'Вилков И.А.', 19, 'Нападающий'),
    (1, 'Иванов А.А.', 1, 'Вратарь'),
    (2, 'Петров П.П.', 7, 'Универсал')
])

cursor.execute('''
INSERT INTO Matches (id_домашней_команды, id_гостевой_команды, дата_время) 
VALUES (1, 2, '25.10.2026 18:00');
''')

cursor.executemany('''
INSERT INTO PlayerStats (id_матча, id_игрока, забитые_мячи, желтые_карточки, красные_карточки)
VALUES (?, ?, ?, ?, ?);
''', [
    (1, 1, 2, 0, 0),
    (1, 3, 1, 1, 0)
])

conn.commit()
conn.close()

