import sqlite3

def insertar_articulo_prueba():
    conn = sqlite3.connect("db/database.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO inventario (nombre, descripcion, cantidad, valor_real, valor_venta)
    VALUES ('Artículo Prueba', 'Descripción de prueba', 10, 50.0, 75.0)
    """)

    conn.commit()
    conn.close()
    print("Artículo de prueba insertado.")

if __name__ == "__main__":
    insertar_articulo_prueba()
