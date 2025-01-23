import sys
import os

# Agrega la carpeta raíz del proyecto al PATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLineEdit, QLabel, QWidget, QMessageBox, QHeaderView, QFrame
)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

import sqlite3
from utils.barcode_utils import generar_codigo_desde_db, imprimir_codigo_barras


class InventoryApp(QWidget):
    def __init__(self, user_data=None):
        super().__init__()
        self.user_data = user_data
        self.setup_ui()
        self.cargar_inventario()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título de la sección
        title = QLabel("Gestión de Inventario")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Marco para el formulario
        form_frame = QFrame()
        form_frame.setObjectName("form_frame")
        form_frame.setStyleSheet("""
            QFrame#form_frame {
                background-color: #FFF0F3;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        form_layout = QHBoxLayout(form_frame)
        form_layout.setSpacing(15)

        # Campos de entrada con estilo
        input_fields = [
            ("Nombre:", self.create_input("Nombre del artículo")),
            ("Descripción:", self.create_input("Descripción")),
            ("Cantidad:", self.create_input("Cantidad")),
            ("Valor Real:", self.create_input("Valor Real")),
            ("Valor Venta:", self.create_input("Valor Venta"))
        ]

        self.input_widgets = {}  # Para almacenar las referencias
        
        for label_text, input_widget in input_fields:
            field_layout = QVBoxLayout()
            label = QLabel(label_text)
            field_layout.addWidget(label)
            field_layout.addWidget(input_widget)
            form_layout.addLayout(field_layout)
            self.input_widgets[label_text] = input_widget

        # Botón agregar con estilo
        self.btn_agregar = QPushButton("Agregar Artículo")
        self.btn_agregar.setMinimumWidth(120)
        self.btn_agregar.clicked.connect(self.agregar_articulo)
        form_layout.addWidget(self.btn_agregar)

        layout.addWidget(form_frame)

        # Tabla de inventario con estilo
        self.tabla_inventario = QTableWidget()
        self.tabla_inventario.setColumnCount(6)
        self.tabla_inventario.setHorizontalHeaderLabels([
            "ID", "Nombre", "Descripción", "Cantidad", 
            "Valor Real", "Valor Venta"
        ])
        
        # Configurar la tabla
        header = self.tabla_inventario.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_inventario.verticalHeader().setVisible(False)
        self.tabla_inventario.setAlternatingRowColors(True)
        
        layout.addWidget(self.tabla_inventario)

    def create_input(self, placeholder):
        input_widget = QLineEdit()
        input_widget.setPlaceholderText(placeholder)
        return input_widget

    def cargar_inventario(self):
        """Cargar datos del inventario en la tabla."""
        try:
            conn = sqlite3.connect("db/store.db")  # Cambiado a store.db
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM inventario")
            datos = cursor.fetchall()
            
            self.tabla_inventario.setRowCount(len(datos))
            
            for row, dato in enumerate(datos):
                for col, valor in enumerate(dato):
                    if col in [4, 5]:  # Valores monetarios
                        texto = f"${valor:.2f}"
                    else:
                        texto = str(valor)
                    item = QTableWidgetItem(texto)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tabla_inventario.setItem(row, col, item)
            
            conn.close()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error al cargar el inventario: {str(e)}")

    def agregar_articulo(self):
        try:
            # Obtener valores de los campos
            nombre = self.input_widgets["Nombre:"].text().strip()
            descripcion = self.input_widgets["Descripción:"].text().strip()
            cantidad = self.input_widgets["Cantidad:"].text()
            valor_real = self.input_widgets["Valor Real:"].text()
            valor_venta = self.input_widgets["Valor Venta:"].text()

            # Validaciones
            if not nombre:
                raise ValueError("El nombre es obligatorio")
            if not cantidad.isdigit() or int(cantidad) < 0:
                raise ValueError("La cantidad debe ser un número positivo")
            try:
                valor_real = float(valor_real)
                valor_venta = float(valor_venta)
                if valor_real < 0 or valor_venta < 0:
                    raise ValueError()
            except:
                raise ValueError("Los valores deben ser números positivos")

            # Insertar en la base de datos
            conn = sqlite3.connect("db/store.db")  # Cambiado a store.db
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO inventario (nombre, descripcion, cantidad, precio_compra, precio_venta)
                VALUES (?, ?, ?, ?, ?)
            """, (nombre, descripcion, int(cantidad), valor_real, valor_venta))
            
            conn.commit()
            conn.close()
            
            # Limpiar campos
            for input_widget in self.input_widgets.values():
                input_widget.clear()
            
            # Recargar tabla
            self.cargar_inventario()
            
            QMessageBox.information(self, "Éxito", "Artículo agregado correctamente")
            
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error en la base de datos: {str(e)}")

    def editar_articulo(self):
        """Editar el artículo seleccionado en la base de datos."""
        try:
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

            conn = sqlite3.connect("db/store.db")  # Cambiado a store.db
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE inventario
            SET nombre = ?, descripcion = ?, cantidad = ?, precio_compra = ?, precio_venta = ?
            WHERE id = ?
            """, (nombre, descripcion, int(cantidad), float(valor_real), float(valor_venta), int(id_articulo)))
            
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Éxito", "Artículo editado correctamente.")
            self.cargar_inventario()
            self.limpiar_campos()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error en la base de datos: {str(e)}")

    def eliminar_articulo(self):
        """Eliminar el artículo seleccionado de la base de datos."""
        try:
            id_articulo = self.input_id.text()

            if not id_articulo.isdigit():
                QMessageBox.warning(self, "Error", "Por favor, selecciona un artículo válido para eliminar.")
                return

            conn = sqlite3.connect("db/store.db")  # Cambiado a store.db
            cursor = conn.cursor()
            cursor.execute("DELETE FROM inventario WHERE id = ?", (int(id_articulo),))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Éxito", "Artículo eliminado correctamente.")
            self.cargar_inventario()
            self.limpiar_campos()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error en la base de datos: {str(e)}")

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
