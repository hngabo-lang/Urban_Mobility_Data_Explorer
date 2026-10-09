import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "mobilty_data.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    with open(SCHEMA_PATH, "r") as f:
        schema_sql = f.read()
        cursor.executescript(schema_sql)
        conn.commit()
        conn.close()

if __name__ == "__main__":
    init_db()