import sqlite3
import os

def check_users_database():
    try:
        # Verificar si existe la base de datos
        if not os.path.exists("db/store.db"):
            print("La base de datos store.db no existe")
            return
            
        conn = sqlite3.connect("db/store.db")
        cursor = conn.cursor()
        
        # Verificar si existe la tabla usuarios
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='usuarios'
        """)
        
        if cursor.fetchone() is None:
            print("La tabla 'usuarios' no existe en la base de datos")
            return
            
        # Mostrar la estructura de la tabla
        cursor.execute("PRAGMA table_info(usuarios)")
        columns = cursor.fetchall()
        print("\nEstructura de la tabla usuarios:")
        for col in columns:
            print(f"Columna: {col[1]}, Tipo: {col[2]}")
            
        # Mostrar todos los usuarios
        cursor.execute("SELECT * FROM usuarios")
        users = cursor.fetchall()
        print("\nUsuarios en la base de datos:")
        if users:
            for user in users:
                print(f"\nID: {user[0]}")
                print(f"Teléfono: {user[1]}")
                print(f"Correo: {user[2]}")
                print(f"Rol: {user[4]}")
        else:
            print("No hay usuarios en la base de datos")
            
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Error al verificar la base de datos: {str(e)}")

if __name__ == "__main__":
    check_users_database() 