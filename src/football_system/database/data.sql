INSERT INTO Teams (название) VALUES ('ИРИТ');
INSERT INTO Teams (название) VALUES ('ИНЭУ');

INSERT INTO Players (id_команды, фио, игровой_номер, позиция) VALUES 
(1, 'Вилков И.А.', 19, 'Нападающий'),
(1, 'Иванов А.А.', 1, 'Вратарь'),
(2, 'Петров П.П.', 7, 'Универсал');

INSERT INTO Matches (id_домашней_команды, id_гостевой_команды, дата_время) VALUES 
(1, 2, '25.10.2026 18:00');

INSERT INTO PlayerStats (id_матча, id_игрока, забитые_мячи, желтые_карточки, красные_карточки) VALUES 
(1, 1, 2, 0, 0),
(1, 3, 1, 1, 0);

INSERT OR IGNORE INTO Users (логин, пароль) VALUES ('admin', 'admin123');

