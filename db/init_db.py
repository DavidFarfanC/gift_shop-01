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
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telefono TEXT NOT NULL UNIQUE,
        correo TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        rol TEXT CHECK(rol IN ('vendedor', 'superusuario')) NOT NULL,
        activo BOOLEAN DEFAULT 1
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        articulo_id INTEGER,
        cantidad INTEGER NOT NULL,
        precio_unitario REAL NOT NULL,
        forma_pago TEXT CHECK(forma_pago IN ('efectivo', 'tarjeta')) NOT NULL,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        usuario_id INTEGER,
        FOREIGN KEY (articulo_id) REFERENCES inventario(id),
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS apartados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        articulo_id INTEGER,
        cantidad INTEGER NOT NULL,
        estado TEXT CHECK(estado IN ('pendiente', 'pagado', 'cancelado')) NOT NULL,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_vencimiento TIMESTAMP,
        FOREIGN KEY (articulo_id) REFERENCES inventario(id),
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
