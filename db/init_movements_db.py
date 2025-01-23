import sqlite3
from datetime import datetime

def create_movements_tables():
    conn = sqlite3.connect("db/movements.db")
    cursor = conn.cursor()
    
    # Tabla para movimientos de ventas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimientos_ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        usuario_id INTEGER,
        usuario_nombre TEXT,
        total_venta REAL NOT NULL,
        forma_pago TEXT CHECK(forma_pago IN ('efectivo', 'tarjeta')) NOT NULL,
        numero_articulos INTEGER NOT NULL
    )
    """)
    
    # Tabla para detalles de cada venta
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detalles_venta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movimiento_id INTEGER,
        articulo_id INTEGER,
        articulo_nombre TEXT,
        cantidad INTEGER NOT NULL,
        precio_unitario REAL NOT NULL,
        subtotal REAL NOT NULL,
        FOREIGN KEY (movimiento_id) REFERENCES movimientos_ventas(id)
    )
    """)
    
    # Tabla para resumen diario
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resumen_diario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha DATE UNIQUE,
        total_ventas REAL NOT NULL DEFAULT 0,
        total_efectivo REAL NOT NULL DEFAULT 0,
        total_tarjeta REAL NOT NULL DEFAULT 0,
        numero_ventas INTEGER NOT NULL DEFAULT 0
    )
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_movements_tables() 