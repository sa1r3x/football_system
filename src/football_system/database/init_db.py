import sqlite3
from pathlib import Path

# Вычисляем пути относительно этого файла init_db.py
CURRENT_DIR = Path(__file__).resolve().parent
DB_PATH = CURRENT_DIR.parent / "football.db"
SCHEMA_PATH = CURRENT_DIR / "schema.sql"
DATA_PATH = CURRENT_DIR / "data.sql"

def init_db():
    print(f"Инициализация базы данных по пути: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Читаем и выполняем schema.sql
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
        print("[✓] Таблицы успешно созданы.")
        
        # Читаем и выполняем data.sql
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
        print("[✓] Тестовые данные успешно загружены.")
        
        conn.commit()
        print("База данных готова к работе!")
        
    except Exception as e:
        print(f"[X] Ошибка при инициализации: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
