import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = str(BASE_DIR / "football.db")


def get_connection(db_path: str | Path = DB_PATH) -> sqlite3.Connection:
    """Создаёт соединение с SQLite и включает поддержку внешних ключей."""
    connection = sqlite3.connect(str(db_path))
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection
