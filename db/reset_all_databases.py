import sqlite3
import os
import hashlib

def reset_all_databases():
    try:
        print("Iniciando reinicio completo de bases de datos...")
        
        # 1. Eliminar todas las bases de datos existentes
        db_files = ['store.db', 'movements.db']
        for db_file in db_files:
            db_path = os.path.join('db', db_file)
            if os.path.exists(db_path):
                os.remove(db_path)
                print(f"Base de datos {db_file} eliminada")
        
        # 2. Crear directorio db si no existe
        os.makedirs('db', exist_ok=True)
        
        # 3. Crear store.db y sus tablas
        conn_store = sqlite3.connect("db/store.db")
        cursor_store = conn_store.cursor()
        
        # Eliminar tablas existentes
        cursor_store.execute("DROP TABLE IF EXISTS usuarios")
        cursor_store.execute("DROP TABLE IF EXISTS inventario")
        cursor_store.execute("DROP TABLE IF EXISTS clientes")
        
        # Crear tabla usuarios
        cursor_store.execute("""
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telefono TEXT NOT NULL,
            correo TEXT NOT NULL,
            contrasena TEXT NOT NULL,
            rol TEXT NOT NULL,
            UNIQUE(telefono),
            UNIQUE(correo)
        )
        """)
        
        # Crear tabla inventario
        cursor_store.execute("""
        CREATE TABLE inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            cantidad INTEGER NOT NULL,
            precio_compra REAL NOT NULL,
            precio_venta REAL NOT NULL,
            categoria TEXT,
            codigo_barras TEXT UNIQUE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usuario_creacion INTEGER,
            FOREIGN KEY (usuario_creacion) REFERENCES usuarios(id)
        )
        """)
        
        # Crear tabla clientes
        cursor_store.execute("""
        CREATE TABLE clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL UNIQUE,
            correo TEXT,
            notas TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Crear usuario administrador por defecto
        admin_password = "admin123"
        hashed_password = hashlib.sha256(admin_password.encode()).hexdigest()
        
        cursor_store.execute("""
        INSERT INTO usuarios (telefono, correo, contrasena, rol)
        VALUES (?, ?, ?, ?)
        """, ('1234567890', 'admin@wgiftshop.com', hashed_password, 'admin'))
        
        # Verificar que el usuario se creó correctamente
        cursor_store.execute("SELECT * FROM usuarios")
        users = cursor_store.fetchall()
        print("\nUsuarios en la base de datos:")
        for user in users:
            print(f"ID: {user[0]}")
            print(f"Teléfono: {user[1]}")
            print(f"Correo: {user[2]}")
            print(f"Rol: {user[4]}")
        
        # 4. Insertar datos de prueba en el inventario
        test_items = [
            ('Playera Negra', 'Playera básica color negro', 10, 150.00, 299.99, 'Ropa', '001'),
            ('Pantalón Mezclilla', 'Pantalón mezclilla azul', 5, 300.00, 599.99, 'Ropa', '002'),
            ('Tenis Deportivos', 'Tenis para correr', 8, 400.00, 899.99, 'Calzado', '003'),
            ('Chamarra Piel', 'Chamarra de piel negra', 3, 800.00, 1499.99, 'Ropa', '004'),
            ('Gorra Baseball', 'Gorra deportiva ajustable', 15, 100.00, 249.99, 'Accesorios', '005')
        ]
        
        cursor_store.executemany("""
            INSERT INTO inventario (
                nombre, descripcion, cantidad, 
                precio_compra, precio_venta, 
                categoria, codigo_barras
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, test_items)
        
        # 5. Crear movements.db y sus tablas
        conn_movements = sqlite3.connect("db/movements.db")
        cursor_movements = conn_movements.cursor()
        
        cursor_movements.execute("DROP TABLE IF EXISTS apartados")
        cursor_movements.execute("DROP TABLE IF EXISTS movimientos_ventas")
        cursor_movements.execute("DROP TABLE IF EXISTS detalles_venta")
        
        cursor_movements.execute("""
        CREATE TABLE apartados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_limite DATE NOT NULL,
            cliente_nombre TEXT NOT NULL,
            cliente_telefono TEXT NOT NULL,
            cliente_correo TEXT,
            articulo_id INTEGER NOT NULL,
            articulo_nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_total REAL NOT NULL,
            anticipo REAL NOT NULL,
            restante REAL NOT NULL,
            estado TEXT NOT NULL,
            usuario_id INTEGER NOT NULL,
            notas TEXT
        )
        """)
        
        cursor_movements.execute("""
        CREATE TABLE movimientos_ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tipo_movimiento TEXT NOT NULL,
            total REAL NOT NULL,
            metodo_pago TEXT NOT NULL,
            usuario_id INTEGER NOT NULL,
            notas TEXT
        )
        """)
        
        cursor_movements.execute("""
        CREATE TABLE detalles_venta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            articulo_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (venta_id) REFERENCES movimientos_ventas(id)
        )
        """)
        
        # Guardar cambios y cerrar conexiones
        conn_store.commit()
        conn_movements.commit()
        conn_store.close()
        conn_movements.close()
        
        print("\n¡Bases de datos reiniciadas correctamente!")
        print("\nCredenciales de administrador:")
        print("Teléfono: 1234567890")
        print("Contraseña: admin123")
        
    except sqlite3.Error as e:
        print(f"Error durante el reinicio de las bases de datos: {str(e)}")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")

if __name__ == "__main__":
    reset_all_databases() 