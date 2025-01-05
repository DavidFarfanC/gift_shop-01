import sys
import os

# Agrega la carpeta raíz del proyecto al PATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.barcode_utils import generar_codigo_desde_db

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLineEdit, QLabel, QWidget, QMessageBox
)
import sqlite3
from utils.barcode_utils import generar_codigo_desde_db


class InventoryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestor de Inventario")
        self.setGeometry(100, 100, 800, 600)

        # Layout principal
        layout = QVBoxLayout()

        # Tabla para mostrar el inventario
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Descripción", "Cantidad", "Valor Real", "Valor Venta"])
        layout.addWidget(self.table)

        # Formulario para agregar artículos
        form_layout = QHBoxLayout()
        self.input_nombre = QLineEdit()
        self.input_descripcion = QLineEdit()
        self.input_cantidad = QLineEdit()
        self.input_valor_real = QLineEdit()
        self.input_valor_venta = QLineEdit()
        self.btn_agregar = QPushButton("Agregar Artículo")
        self.btn_agregar.clicked.connect(self.agregar_articulo)

        form_layout.addWidget(QLabel("Nombre:"))
        form_layout.addWidget(self.input_nombre)
        form_layout.addWidget(QLabel("Descripción:"))
        form_layout.addWidget(self.input_descripcion)
        form_layout.addWidget(QLabel("Cantidad:"))
        form_layout.addWidget(self.input_cantidad)
        form_layout.addWidget(QLabel("Valor Real:"))
        form_layout.addWidget(self.input_valor_real)
        form_layout.addWidget(QLabel("Valor Venta:"))
        form_layout.addWidget(self.input_valor_venta)
        form_layout.addWidget(self.btn_agregar)
        layout.addLayout(form_layout)

        # Botón para generar código de barras
        self.input_id = QLineEdit()
        self.btn_generar_codigo = QPushButton("Generar Código de Barras")
        self.btn_generar_codigo.clicked.connect(self.generar_codigo)
        layout.addWidget(QLabel("ID del artículo:"))
        layout.addWidget(self.input_id)
        layout.addWidget(self.btn_generar_codigo)

        # Contenedor principal
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Cargar datos del inventario al iniciar
        self.cargar_inventario()

    def cargar_inventario(self):
        """Cargar datos del inventario en la tabla."""
        conn = sqlite3.connect("db/database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventario")
        rows = cursor.fetchall()
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, col in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col)))
        conn.close()

    def agregar_articulo(self):
        """Agregar un nuevo artículo a la base de datos."""
        nombre = self.input_nombre.text()
        descripcion = self.input_descripcion.text()
        cantidad = self.input_cantidad.text()
        valor_real = self.input_valor_real.text()
        valor_venta = self.input_valor_venta.text()

        if not (nombre and cantidad.isdigit() and valor_real.replace('.', '', 1).isdigit() and valor_venta.replace('.', '', 1).isdigit()):
            QMessageBox.warning(self, "Error", "Por favor, completa todos los campos correctamente.")
            return

        conn = sqlite3.connect("db/database.db")
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO inventario (nombre, descripcion, cantidad, valor_real, valor_venta)
        VALUES (?, ?, ?, ?, ?)
        """, (nombre, descripcion, int(cantidad), float(valor_real), float(valor_venta)))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Éxito", "Artículo agregado correctamente.")
        self.cargar_inventario()

    def generar_codigo(self):
        """Generar código de barras para el artículo seleccionado por ID."""
        id_articulo = self.input_id.text()
        if not id_articulo.isdigit():
            QMessageBox.warning(self, "Error", "Por favor, ingresa un ID válido.")
            return

        generar_codigo_desde_db(int(id_articulo))
        QMessageBox.information(self, "Éxito", f"Código de barras generado para el ID {id_articulo}.")


if __name__ == "__main__":
    app = QApplication([])
    window = InventoryApp()
    window.show()
    app.exec_()
