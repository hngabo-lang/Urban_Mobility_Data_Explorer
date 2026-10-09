import sqlite3
import sys
from pathlib import Path

<<<<<<< HEAD
DB_PATH = os.path.join(os.path.dirname(__file__), "mobilty_data.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")
=======
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config
>>>>>>> 4b9942557109ed65472caecc6a6cf79c6908c838

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


# open coonection to database with foreign keys switched on
def get_connection():
    conn = sqlite3.connect(config.DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

# create or reset all tables from schema.sql
def init_db():
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn = get_connection()
    try:
       conn.executescript(schema_sql)
       conn.commit()
    finally:
        conn.close() 

if __name__ == "__main__":
    init_db()
    print(f"Database created at {config.DB_PATH}")