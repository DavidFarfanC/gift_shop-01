import sys
import os

# Agrega la carpeta raíz del proyecto al PATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLineEdit, QLabel, QWidget, QMessageBox
)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

import sqlite3
from utils.barcode_utils import generar_codigo_desde_db, imprimir_codigo_barras


class InventoryApp(QMainWindow):
    def __init__(self, user_data=None):
        super().__init__()
        self.user_data = user_data
        self.setWindowTitle("Gestor de Inventario")
        self.setGeometry(100, 100, 900, 600)

        # Si hay datos de usuario, mostrar en el título
        if self.user_data:
            self.setWindowTitle(f"Gestor de Inventario - {self.user_data['rol'].title()}")

        # Paleta de colores base
        self.set_estilos()

        # Layout principal
        layout_principal = QVBoxLayout()

        # Tabla para mostrar el inventario
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Descripción", "Cantidad", "Valor Real", "Valor Venta"])
        self.table.cellClicked.connect(self.cargar_fila_seleccionada)
        layout_principal.addWidget(self.table)

        # Layout para formulario de artículos (parte superior de botones y entradas)
        form_layout = QHBoxLayout()

        # Sub-layout con etiquetas y campos de texto
        campos_layout = QVBoxLayout()
        nombre_layout = QHBoxLayout()
        descripcion_layout = QHBoxLayout()
        cantidad_layout = QHBoxLayout()
        valor_real_layout = QHBoxLayout()
        valor_venta_layout = QHBoxLayout()

        # Nombre
        lbl_nombre = QLabel("Nombre:")
        self.input_nombre = QLineEdit()
        nombre_layout.addWidget(lbl_nombre)
        nombre_layout.addWidget(self.input_nombre)
        campos_layout.addLayout(nombre_layout)

        # Descripción
        lbl_descripcion = QLabel("Descripción:")
        self.input_descripcion = QLineEdit()
        descripcion_layout.addWidget(lbl_descripcion)
        descripcion_layout.addWidget(self.input_descripcion)
        campos_layout.addLayout(descripcion_layout)

        # Cantidad
        lbl_cantidad = QLabel("Cantidad:")
        self.input_cantidad = QLineEdit()
        cantidad_layout.addWidget(lbl_cantidad)
        cantidad_layout.addWidget(self.input_cantidad)
        campos_layout.addLayout(cantidad_layout)

        # Valor Real
        lbl_valor_real = QLabel("Valor Real:")
        self.input_valor_real = QLineEdit()
        valor_real_layout.addWidget(lbl_valor_real)
        valor_real_layout.addWidget(self.input_valor_real)
        campos_layout.addLayout(valor_real_layout)

        # Valor Venta
        lbl_valor_venta = QLabel("Valor Venta:")
        self.input_valor_venta = QLineEdit()
        valor_venta_layout.addWidget(lbl_valor_venta)
        valor_venta_layout.addWidget(self.input_valor_venta)
        campos_layout.addLayout(valor_venta_layout)

        # Agrega ese sub-layout al layout del formulario
        form_layout.addLayout(campos_layout)

        # Sub-layout para botones de agregar y editar
        botones_layout = QVBoxLayout()
        self.btn_agregar = QPushButton("Agregar Artículo")
        self.btn_agregar.clicked.connect(self.agregar_articulo)
        self.btn_editar = QPushButton("Editar Artículo")
        self.btn_editar.clicked.connect(self.editar_articulo)
        botones_layout.addWidget(self.btn_agregar)
        botones_layout.addWidget(self.btn_editar)
        form_layout.addLayout(botones_layout)

        # Añade todo el formulario al layout principal
        layout_principal.addLayout(form_layout)

        # Botón para eliminar artículos
        self.btn_eliminar = QPushButton("Eliminar Artículo")
        self.btn_eliminar.clicked.connect(self.eliminar_articulo)
        layout_principal.addWidget(self.btn_eliminar)

        # Sección para generar código de barras
        codigo_layout = QHBoxLayout()
        lbl_id = QLabel("ID del artículo:")
        self.input_id = QLineEdit()
        self.btn_generar_codigo = QPushButton("Generar Código de Barras")
        self.btn_generar_codigo.clicked.connect(self.generar_codigo)

        codigo_layout.addWidget(lbl_id)
        codigo_layout.addWidget(self.input_id)
        codigo_layout.addWidget(self.btn_generar_codigo)

        layout_principal.addLayout(codigo_layout)

        # Botón para abrir ventana de ventas
        self.btn_ventas = QPushButton("Abrir Ventas")
        self.btn_ventas.clicked.connect(self.abrir_ventas)
        layout_principal.addWidget(self.btn_ventas)

        # Contenedor principal
        container = QWidget()
        container.setLayout(layout_principal)
        self.setCentralWidget(container)

        # Cargar datos del inventario al iniciar
        self.cargar_inventario()

    def set_estilos(self):
        """
        Configura la hoja de estilo (QSS) para dar una apariencia en tonos de rosa,
        y ajusta un poco la estética de los widgets.
        """
        # Color principal
        color_rosa_hex = "#F3C7C1"

        # Paleta de ventana
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color_rosa_hex))
        self.setPalette(palette)

        # Hoja de estilo general
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {color_rosa_hex};
            }}
            QTableWidget {{
                background-color: #FFFFFF;
                selection-background-color: #F8E6E3; /* Un tono más claro para la selección */
                gridline-color: #E8B3AD;
            }}
            QHeaderView::section {{
                background-color: #F4B7AC;
                font-weight: bold;
                border: 1px solid #E8B3AD;
            }}
            QLabel {{
                font-weight: bold;
            }}
            QLineEdit {{
                background-color: #FFFFFF;
                border: 1px solid #E8B3AD;
                border-radius: 3px;
                padding: 3px;
            }}
            QPushButton {{
                background-color: #F4B7AC;
                border-radius: 5px;
                padding: 8px 15px;
                border: 1px solid #F1908C;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #F8E6E3;
            }}
            QPushButton:pressed {{
                background-color: #E8B3AD;
            }}
        """)

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

    def cargar_fila_seleccionada(self, row):
        """Cargar datos de la fila seleccionada en los campos de entrada."""
        self.input_id.setText(self.table.item(row, 0).text())
        self.input_nombre.setText(self.table.item(row, 1).text())
        self.input_descripcion.setText(self.table.item(row, 2).text())
        self.input_cantidad.setText(self.table.item(row, 3).text())
        self.input_valor_real.setText(self.table.item(row, 4).text())
        self.input_valor_venta.setText(self.table.item(row, 5).text())

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
        self.limpiar_campos()

    def editar_articulo(self):
        """Editar el artículo seleccionado en la base de datos."""
        id_articulo = self.input_id.text()
        nombre = self.input_nombre.text()
        descripcion = self.input_descripcion.text()
        cantidad = self.input_cantidad.text()
        valor_real = self.input_valor_real.text()
        valor_venta = self.input_valor_venta.text()

        if not (id_articulo.isdigit() and nombre and cantidad.isdigit() 
                and valor_real.replace('.', '', 1).isdigit() 
                and valor_venta.replace('.', '', 1).isdigit()):
            QMessageBox.warning(self, "Error", "Por favor, completa todos los campos correctamente.")
            return

        conn = sqlite3.connect("db/database.db")
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE inventario
        SET nombre = ?, descripcion = ?, cantidad = ?, valor_real = ?, valor_venta = ?
        WHERE id = ?
        """, (nombre, descripcion, int(cantidad), float(valor_real), float(valor_venta), int(id_articulo)))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Éxito", "Artículo editado correctamente.")
        self.cargar_inventario()
        self.limpiar_campos()

    def eliminar_articulo(self):
        """Eliminar el artículo seleccionado de la base de datos."""
        id_articulo = self.input_id.text()

        if not id_articulo.isdigit():
            QMessageBox.warning(self, "Error", "Por favor, selecciona un artículo válido para eliminar.")
            return

        conn = sqlite3.connect("db/database.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventario WHERE id = ?", (int(id_articulo),))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Éxito", "Artículo eliminado correctamente.")
        self.cargar_inventario()
        self.limpiar_campos()

    def generar_codigo(self):
        """
        Generar código de barras para el artículo seleccionado por ID y enviarlo a la impresora
        (o guardarlo según esté implementado en imprimir_codigo_barras).
        """
        id_articulo = self.input_id.text()
        if not id_articulo.isdigit():
            QMessageBox.warning(self, "Error", "Por favor, ingresa un ID válido.")
            return

        imprimir_codigo_barras(int(id_articulo))
        QMessageBox.information(self, "Éxito", f"Código de barras generado e impreso para el ID {id_articulo}.")

    def limpiar_campos(self):
        """Deja en blanco los campos de entrada."""
        self.input_id.clear()
        self.input_nombre.clear()
        self.input_descripcion.clear()
        self.input_cantidad.clear()
        self.input_valor_real.clear()
        self.input_valor_venta.clear()

    def abrir_ventas(self):
        from frontend.sales_ui import SalesWindow
        self.ventana_ventas = SalesWindow(user_data=self.user_data, parent=self)
        self.ventana_ventas.show()


if __name__ == "__main__":
    app = QApplication([])
    window = InventoryApp()
    window.show()
    sys.exit(app.exec_())
