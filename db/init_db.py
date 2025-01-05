# db/init_db.py
import sqlite3

def create_tables():
    conn = sqlite3.connect("db/database.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        cantidad INTEGER NOT NULL,
        valor_real REAL NOT NULL,
        valor_venta REAL NOT NULL
    )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
