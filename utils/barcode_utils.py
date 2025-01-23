import sqlite3
import barcode
from barcode.writer import ImageWriter
import os
import subprocess

def generar_codigo_barras(id_articulo, nombre_archivo="codigo_barras"):
    """Genera un código de barras y lo guarda como imagen."""
    codigo = barcode.get('code128', str(id_articulo), writer=ImageWriter())
    ruta_archivo = f"{nombre_archivo}.png"
    codigo.save(ruta_archivo)
    print(f"Código de barras generado: {ruta_archivo}")
    return ruta_archivo

def generar_codigo_desde_db(id_articulo):
    """Genera un código de barras para un artículo de la base de datos."""
    conn = sqlite3.connect("db/database.db")
    cursor = conn.cursor()

    # Buscar el artículo en la base de datos
    cursor.execute("SELECT id, nombre FROM inventario WHERE id = ?", (id_articulo,))
    articulo = cursor.fetchone()

    if articulo:
        id_articulo, nombre = articulo
        nombre_archivo = f"codigo_{id_articulo}"
        ruta_archivo = generar_codigo_barras(id_articulo, nombre_archivo)
        print(f"Código de barras para el artículo '{nombre}' generado en {ruta_archivo}.")
    else:
        print("Artículo no encontrado.")
    
    conn.close()

def imprimir_codigo_barras(id_articulo):
    """Genera un código de barras y lo envía a la impresora."""
    nombre_archivo = f"codigo_{id_articulo}.png"
    ruta_archivo = generar_codigo_barras(id_articulo, nombre_archivo)
    
    # Comando para imprimir el archivo
    try:
        subprocess.run(["lp", ruta_archivo], check=True)
        print(f"Código de barras enviado a la impresora: {ruta_archivo}")
    except subprocess.CalledProcessError as e:
        print(f"Error al imprimir el código de barras: {e}")

# Ejemplo de prueba
if __name__ == "__main__":
    # Cambia el ID a un artículo existente en tu base de datos
    generar_codigo_desde_db(1)
    imprimir_codigo_barras(1)
