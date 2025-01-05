import sqlite3
import barcode
from barcode.writer import ImageWriter

def generar_codigo_barras(id_articulo, nombre_archivo="codigo_barras"):
    codigo = barcode.get('code128', str(id_articulo), writer=ImageWriter())
    ruta_archivo = f"{nombre_archivo}.png"
    codigo.save(ruta_archivo)
    print(f"Código de barras generado: {ruta_archivo}")
    return ruta_archivo

def generar_codigo_desde_db(id_articulo):
    conn = sqlite3.connect("db/database.db")
    cursor = conn.cursor()

    # Buscar el artículo en la base de datos
    cursor.execute("SELECT id, nombre FROM inventario WHERE id = ?", (id_articulo,))
    articulo = cursor.fetchone()

    if articulo:
        id_articulo, nombre = articulo
        nombre_archivo = f"codigo_{id_articulo}"
        generar_codigo_barras(id_articulo, nombre_archivo)
        print(f"Código de barras para el artículo '{nombre}' generado.")
    else:
        print("Artículo no encontrado.")
    
    conn.close()

# Ejemplo de prueba
if __name__ == "__main__":
    generar_codigo_desde_db(1)
