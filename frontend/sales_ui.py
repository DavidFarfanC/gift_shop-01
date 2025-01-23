from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QTableWidget, 
    QTableWidgetItem, QMessageBox, QTabWidget, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
import sqlite3
from datetime import datetime, timedelta

class SalesWindow(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setWindowTitle("Sistema de Ventas")
        self.setGeometry(150, 150, 1000, 700)

        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Crear el widget de pestañas
        tabs = QTabWidget()
        
        # Pestaña de Registro de Ventas
        tab_ventas = QWidget()
        self.setup_tab_ventas(tab_ventas)
        tabs.addTab(tab_ventas, "Registro de Ventas")

        # Pestaña de Histórico
        tab_historico = QWidget()
        self.setup_tab_historico(tab_historico)
        tabs.addTab(tab_historico, "Histórico de Movimientos")

        layout.addWidget(tabs)

    def setup_tab_ventas(self, tab):
        """Configurar la pestaña de registro de ventas"""
        layout = QVBoxLayout(tab)
        
        # Campo para código de barras/ID y botón buscar
        id_layout = QHBoxLayout()
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Escanea o ingresa el ID del producto")
        self.id_input.returnPressed.connect(self.buscar_producto)
        
        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.clicked.connect(self.buscar_producto)
        
        id_layout.addWidget(QLabel("ID Producto:"))
        id_layout.addWidget(self.id_input)
        id_layout.addWidget(self.btn_buscar)
        layout.addLayout(id_layout)
        
        # Información del producto
        self.info_producto = QLabel("")
        layout.addWidget(self.info_producto)
        
        # Campos de venta
        form_layout = QHBoxLayout()
        
        # Campo cantidad
        self.cantidad_input = QLineEdit()
        self.cantidad_input.setPlaceholderText("Cantidad")
        form_layout.addWidget(QLabel("Cantidad:"))
        form_layout.addWidget(self.cantidad_input)
        
        # Forma de pago
        self.forma_pago = QComboBox()
        self.forma_pago.addItems(["efectivo", "tarjeta"])
        form_layout.addWidget(QLabel("Forma de Pago:"))
        form_layout.addWidget(self.forma_pago)
        
        # Botón agregar
        self.btn_agregar = QPushButton("Agregar a Venta")
        self.btn_agregar.clicked.connect(self.agregar_a_venta)
        form_layout.addWidget(self.btn_agregar)
        
        layout.addLayout(form_layout)
        
        # Tabla de productos en la venta actual
        self.tabla_venta = QTableWidget()
        self.tabla_venta.setColumnCount(5)
        self.tabla_venta.setHorizontalHeaderLabels([
            "ID", "Nombre", "Cantidad", "Precio Unitario", "Subtotal"
        ])
        layout.addWidget(self.tabla_venta)
        
        # Total y botón finalizar
        total_layout = QHBoxLayout()
        self.lbl_total = QLabel("Total: $0.00")
        self.btn_finalizar = QPushButton("Finalizar Venta")
        self.btn_finalizar.clicked.connect(self.finalizar_venta)
        total_layout.addWidget(self.lbl_total)
        total_layout.addWidget(self.btn_finalizar)
        layout.addLayout(total_layout)
        
        # Variables de control
        self.productos_en_venta = []
        self.total_venta = 0.0

    def setup_tab_historico(self, tab):
        """Configurar la pestaña de histórico de movimientos"""
        layout = QVBoxLayout(tab)

        # Filtros de fecha
        filtros_layout = QHBoxLayout()
        
        # Fecha inicial
        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setDate(QDate.currentDate())
        self.fecha_inicio.setCalendarPopup(True)
        filtros_layout.addWidget(QLabel("Fecha Inicio:"))
        filtros_layout.addWidget(self.fecha_inicio)
        
        # Fecha final
        self.fecha_fin = QDateEdit()
        self.fecha_fin.setDate(QDate.currentDate())
        self.fecha_fin.setCalendarPopup(True)
        filtros_layout.addWidget(QLabel("Fecha Fin:"))
        filtros_layout.addWidget(self.fecha_fin)
        
        # Botón de búsqueda
        btn_buscar_hist = QPushButton("Buscar Movimientos")
        btn_buscar_hist.clicked.connect(self.cargar_historico)
        filtros_layout.addWidget(btn_buscar_hist)
        
        layout.addLayout(filtros_layout)

        # Tabla de movimientos
        self.tabla_historico = QTableWidget()
        self.tabla_historico.setColumnCount(7)
        self.tabla_historico.setHorizontalHeaderLabels([
            "ID", "Fecha", "Usuario", "Total Venta", 
            "Forma Pago", "Núm. Artículos", "Detalles"
        ])
        layout.addWidget(self.tabla_historico)

        # Resumen
        resumen_layout = QHBoxLayout()
        self.lbl_total_periodo = QLabel("Total del período: $0.00")
        self.lbl_num_ventas = QLabel("Número de ventas: 0")
        resumen_layout.addWidget(self.lbl_total_periodo)
        resumen_layout.addWidget(self.lbl_num_ventas)
        layout.addLayout(resumen_layout)

        # Cargar datos iniciales
        self.cargar_historico()

    def cargar_historico(self):
        """Cargar el histórico de movimientos según las fechas seleccionadas"""
        fecha_inicio = self.fecha_inicio.date().toPyDate()
        fecha_fin = self.fecha_fin.date().toPyDate() + timedelta(days=1)  # Incluir el día completo

        try:
            conn = sqlite3.connect("db/movements.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id, fecha, usuario_nombre, total_venta,
                    forma_pago, numero_articulos
                FROM movimientos_ventas
                WHERE fecha BETWEEN ? AND ?
                ORDER BY fecha DESC
            """, (fecha_inicio, fecha_fin))
            
            movimientos = cursor.fetchall()
            
            self.tabla_historico.setRowCount(len(movimientos))
            total_periodo = 0
            
            for row, mov in enumerate(movimientos):
                for col, valor in enumerate(mov):
                    if col == 3:  # Total venta
                        texto = f"${valor:.2f}"
                        total_periodo += valor
                    else:
                        texto = str(valor)
                    self.tabla_historico.setItem(row, col, QTableWidgetItem(texto))
                
                # Agregar botón de detalles
                btn_detalles = QPushButton("Ver Detalles")
                btn_detalles.clicked.connect(lambda checked, x=mov[0]: self.mostrar_detalles_venta(x))
                self.tabla_historico.setCellWidget(row, 6, btn_detalles)
            
            # Actualizar resumen
            self.lbl_total_periodo.setText(f"Total del período: ${total_periodo:.2f}")
            self.lbl_num_ventas.setText(f"Número de ventas: {len(movimientos)}")
            
            conn.close()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error al cargar el histórico: {str(e)}")

    def mostrar_detalles_venta(self, venta_id):
        """Mostrar los detalles de una venta específica"""
        try:
            conn = sqlite3.connect("db/movements.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT articulo_nombre, cantidad, precio_unitario, subtotal
                FROM detalles_venta
                WHERE movimiento_id = ?
            """, (venta_id,))
            
            detalles = cursor.fetchall()
            conn.close()
            
            # Crear mensaje con los detalles
            mensaje = "Detalles de la venta:\n\n"
            for detalle in detalles:
                mensaje += f"Artículo: {detalle[0]}\n"
                mensaje += f"Cantidad: {detalle[1]}\n"
                mensaje += f"Precio unitario: ${detalle[2]:.2f}\n"
                mensaje += f"Subtotal: ${detalle[3]:.2f}\n"
                mensaje += "-" * 30 + "\n"
            
            QMessageBox.information(self, f"Detalles de Venta #{venta_id}", mensaje)
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error al cargar los detalles: {str(e)}")

    def buscar_producto(self):
        id_producto = self.id_input.text()
        if not id_producto.isdigit():
            QMessageBox.warning(self, "Error", "Por favor ingresa un ID válido")
            return
            
        conn = sqlite3.connect("db/database.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nombre, cantidad, valor_venta 
            FROM inventario 
            WHERE id = ?
        """, (id_producto,))
        
        producto = cursor.fetchone()
        conn.close()
        
        if producto:
            self.producto_actual = {
                'id': producto[0],
                'nombre': producto[1],
                'stock': producto[2],
                'precio': producto[3]
            }
            # Mostrar información del producto encontrado
            self.info_producto.setText(
                f"Producto encontrado: {self.producto_actual['nombre']} "
                f"| Stock: {self.producto_actual['stock']} "
                f"| Precio: ${self.producto_actual['precio']:.2f}"
            )
            self.cantidad_input.setFocus()
        else:
            QMessageBox.warning(self, "Error", "Producto no encontrado")
            self.id_input.clear()
            self.info_producto.clear()

    def agregar_a_venta(self):
        if not hasattr(self, 'producto_actual'):
            QMessageBox.warning(self, "Error", "Primero busca un producto")
            return
            
        try:
            cantidad = int(self.cantidad_input.text())
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser positiva")
            if cantidad > self.producto_actual['stock']:
                raise ValueError("No hay suficiente stock")
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
            return
            
        subtotal = cantidad * self.producto_actual['precio']
        
        # Agregar a la tabla
        row = self.tabla_venta.rowCount()
        self.tabla_venta.insertRow(row)
        self.tabla_venta.setItem(row, 0, QTableWidgetItem(str(self.producto_actual['id'])))
        self.tabla_venta.setItem(row, 1, QTableWidgetItem(self.producto_actual['nombre']))
        self.tabla_venta.setItem(row, 2, QTableWidgetItem(str(cantidad)))
        self.tabla_venta.setItem(row, 3, QTableWidgetItem(f"${self.producto_actual['precio']:.2f}"))
        self.tabla_venta.setItem(row, 4, QTableWidgetItem(f"${subtotal:.2f}"))
        
        # Actualizar total
        self.total_venta += subtotal
        self.lbl_total.setText(f"Total: ${self.total_venta:.2f}")
        
        # Guardar para la venta final
        self.productos_en_venta.append({
            'id': self.producto_actual['id'],
            'cantidad': cantidad,
            'precio': self.producto_actual['precio']
        })
        
        # Limpiar campos
        self.id_input.clear()
        self.cantidad_input.clear()
        self.id_input.setFocus()
        delattr(self, 'producto_actual')

    def finalizar_venta(self):
        if not self.productos_en_venta:
            QMessageBox.warning(self, "Error", "No hay productos en la venta")
            return
            
        try:
            # Conexión a la base de datos principal
            conn_main = sqlite3.connect("db/database.db")
            cursor_main = conn_main.cursor()
            
            # Conexión a la base de datos de movimientos
            conn_mov = sqlite3.connect("db/movements.db")
            cursor_mov = conn_mov.cursor()
            
            # 1. Registrar el movimiento principal de venta
            cursor_mov.execute("""
                INSERT INTO movimientos_ventas (
                    usuario_id, 
                    usuario_nombre,
                    total_venta, 
                    forma_pago, 
                    numero_articulos
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                self.user_data['id'],
                f"{self.user_data['rol']} - {self.user_data['telefono']}",
                self.total_venta,
                self.forma_pago.currentText(),
                sum(p['cantidad'] for p in self.productos_en_venta)
            ))
            
            movimiento_id = cursor_mov.lastrowid
            
            # 2. Registrar cada producto vendido
            for producto in self.productos_en_venta:
                # Obtener nombre del producto
                cursor_main.execute("SELECT nombre FROM inventario WHERE id = ?", (producto['id'],))
                nombre_producto = cursor_main.fetchone()[0]
                
                # Registrar detalle en movements.db
                cursor_mov.execute("""
                    INSERT INTO detalles_venta (
                        movimiento_id,
                        articulo_id,
                        articulo_nombre,
                        cantidad,
                        precio_unitario,
                        subtotal
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    movimiento_id,
                    producto['id'],
                    nombre_producto,
                    producto['cantidad'],
                    producto['precio'],
                    producto['cantidad'] * producto['precio']
                ))
                
                # Actualizar inventario en database.db
                cursor_main.execute("""
                    UPDATE inventario 
                    SET cantidad = cantidad - ? 
                    WHERE id = ?
                """, (producto['cantidad'], producto['id']))
                
                # Registrar venta en database.db
                cursor_main.execute("""
                    INSERT INTO ventas (
                        articulo_id, cantidad, precio_unitario, 
                        forma_pago, usuario_id
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    producto['id'], 
                    producto['cantidad'],
                    producto['precio'],
                    self.forma_pago.currentText(),
                    self.user_data['id']
                ))
            
            # 3. Actualizar resumen diario
            fecha_actual = datetime.now().date()
            cursor_mov.execute("""
                INSERT INTO resumen_diario (
                    fecha, total_ventas, 
                    total_efectivo, total_tarjeta, 
                    numero_ventas
                ) 
                VALUES (?, ?, ?, ?, 1)
                ON CONFLICT(fecha) DO UPDATE SET
                    total_ventas = total_ventas + ?,
                    total_efectivo = total_efectivo + CASE WHEN ? = 'efectivo' THEN ? ELSE 0 END,
                    total_tarjeta = total_tarjeta + CASE WHEN ? = 'tarjeta' THEN ? ELSE 0 END,
                    numero_ventas = numero_ventas + 1
            """, (
                fecha_actual, self.total_venta,
                self.total_venta if self.forma_pago.currentText() == 'efectivo' else 0,
                self.total_venta if self.forma_pago.currentText() == 'tarjeta' else 0,
                self.total_venta,
                self.forma_pago.currentText(), self.total_venta,
                self.forma_pago.currentText(), self.total_venta
            ))
            
            # Confirmar todas las transacciones
            conn_main.commit()
            conn_mov.commit()
            
            QMessageBox.information(self, "Éxito", "Venta registrada correctamente")
            
            # Limpiar la venta actual
            self.productos_en_venta = []
            self.total_venta = 0.0
            self.tabla_venta.setRowCount(0)
            self.lbl_total.setText("Total: $0.00")
            
        except sqlite3.Error as e:
            # Revertir cambios en ambas bases de datos si hay error
            conn_main.rollback()
            conn_mov.rollback()
            QMessageBox.critical(self, "Error", f"Error al registrar la venta: {str(e)}")
        finally:
            conn_main.close()
            conn_mov.close() 