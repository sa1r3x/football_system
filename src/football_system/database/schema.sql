PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS PlayerStats;
DROP TABLE IF EXISTS Matches;
DROP TABLE IF EXISTS Players;
DROP TABLE IF EXISTS Teams;

CREATE TABLE IF NOT EXISTS Teams (
    id_команды INTEGER PRIMARY KEY AUTOINCREMENT,
    название TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Players (
    id_игрока INTEGER PRIMARY KEY AUTOINCREMENT,
    id_команды INTEGER,
    фио TEXT NOT NULL,
    игровой_номер INTEGER,
    позиция TEXT,
    FOREIGN KEY (id_команды) REFERENCES Teams(id_команды) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Matches (
    id_матча INTEGER PRIMARY KEY AUTOINCREMENT,
    id_домашней_команды INTEGER,
    id_гостевой_команды INTEGER,
    дата_время TEXT NOT NULL,
    итоговый_счет TEXT,
    FOREIGN KEY (id_домашней_команды) REFERENCES Teams(id_команды),
    FOREIGN KEY (id_гостевой_команды) REFERENCES Teams(id_команды)
);

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
CREATE TABLE IF NOT EXISTS Users (
    id_пользователя INTEGER PRIMARY KEY AUTOINCREMENT,
    логин TEXT NOT NULL UNIQUE,
    пароль TEXT NOT NULL
);


