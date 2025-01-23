import sqlite3
import hashlib

def insertar_usuario_prueba():
    conn = sqlite3.connect("db/database.db")
    cursor = conn.cursor()

    # Crear un usuario de prueba
    telefono = "1234567890"
    correo = "admin@test.com"
    password = "admin123"  # En producción usar una contraseña más segura
    # Hashear la contraseña
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    cursor.execute("""
    INSERT INTO usuarios (telefono, correo, password, rol, activo)
    VALUES (?, ?, ?, 'superusuario', 1)
    """, (telefono, correo, hashed_password))

    conn.commit()
    conn.close()
    print("Usuario de prueba insertado.")
    print(f"Teléfono: {telefono}")
    print(f"Contraseña: {password}")

if __name__ == "__main__":
    insertar_usuario_prueba()
