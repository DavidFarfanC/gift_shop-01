from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QDialog, QLineEdit, 
    QDateEdit, QSpinBox, QDoubleSpinBox, QTextEdit, QMessageBox,
    QComboBox, QFormLayout, QGroupBox, QHeaderView, QTabWidget,
    QFileDialog, QMainWindow, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
import sqlite3
from datetime import datetime, timedelta
from openpyxl import Workbook
import pandas as pd

class LayawayWindow(QMainWindow):
    inventario_actualizado = pyqtSignal()
    
    def __init__(self, user_data=None):
        super().__init__()
        self.user_data = user_data
        self.init_database()
        self.setup_ui()
        self.load_layaways()

    def init_database(self):
        try:
            conn = sqlite3.connect("db/movements.db")
            cursor = conn.cursor()
            
            # Primero eliminamos la tabla apartados si existe
            cursor.execute("DROP TABLE IF EXISTS apartados")
            
            # Tabla para apartados con la estructura correcta
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS apartados (
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
                dias_restantes INTEGER DEFAULT 30,
                estado TEXT CHECK(estado IN ('pendiente', 'completado', 'cancelado')) NOT NULL DEFAULT 'pendiente',
                usuario_id INTEGER,
                notas TEXT,
                FOREIGN KEY (articulo_id) REFERENCES inventario(id)
            )
            """)
            
            conn.commit()
            conn.close()
            print("Tabla de apartados recreada correctamente")
            
            with sqlite3.connect("db/movements.db") as conn:
                cursor = conn.cursor()
                
                # Verificar si la columna fecha_finalizacion existe
                cursor.execute("PRAGMA table_info(apartados)")
                columns = [column[1] for column in cursor.fetchall()]
                
                # Si no existe la columna, agregarla
                if 'fecha_finalizacion' not in columns:
                    cursor.execute("""
                        ALTER TABLE apartados 
                        ADD COLUMN fecha_finalizacion TIMESTAMP
                    """)
                    conn.commit()
                    
        except sqlite3.Error as e:
            print(f"Error al inicializar la base de datos: {str(e)}")

    def setup_ui(self):
        self.setWindowTitle("Gestión de Apartados")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Crear el widget de pestañas
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Pestaña de Apartados Activos
        self.tab_apartados = QWidget()
        self.setup_apartados_tab()
        self.tab_widget.addTab(self.tab_apartados, "Apartados Activos")

        # Pestaña de Histórico
        self.tab_historico = QWidget()
        self.setup_historico_tab()
        self.tab_widget.addTab(self.tab_historico, "Histórico")

        # Pestaña de Clientes
        self.tab_clientes = QWidget()
        self.setup_clientes_tab()
        self.tab_widget.addTab(self.tab_clientes, "Clientes")

    def setup_apartados_tab(self):
        layout = QVBoxLayout(self.tab_apartados)

        # Botones superiores
        button_layout = QHBoxLayout()
        btn_new_layaway = QPushButton("Nuevo Apartado")
        btn_new_layaway.clicked.connect(self.show_new_layaway)
        btn_new_client = QPushButton("Nuevo Cliente")
        btn_new_client.clicked.connect(self.show_new_client_dialog)
        btn_add_payment = QPushButton("Agregar Abono")
        btn_add_payment.clicked.connect(self.show_add_payment_dialog)
        
        button_layout.addWidget(btn_new_layaway)
        button_layout.addWidget(btn_new_client)
        button_layout.addWidget(btn_add_payment)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)

        # Tabla de apartados activos
        self.layaway_table = QTableWidget()
        self.layaway_table.setColumnCount(10)
        self.layaway_table.setHorizontalHeaderLabels([
            "ID", "Cliente", "Teléfono", "Artículo",
            "Cantidad", "Total", "Anticipo", "Restante",
            "Estado", "Fecha Límite"
        ])
        
        # Permitir selección de fila
        self.layaway_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.layaway_table.setSelectionMode(QTableWidget.SingleSelection)
        
        header = self.layaway_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.layaway_table)

    def setup_historico_tab(self):
        layout = QVBoxLayout(self.tab_historico)

        # Tabla de histórico
        self.historic_table = QTableWidget()
        self.historic_table.setColumnCount(11)
        self.historic_table.setHorizontalHeaderLabels([
            "ID", "Cliente", "Teléfono", "Artículo",
            "Cantidad", "Total", "Anticipo", "Restante",
            "Estado", "Fecha Creación", "Fecha Finalización"
        ])
        
        header = self.historic_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.historic_table)

        # Botón para exportar
        btn_export = QPushButton("Exportar a Excel")
        btn_export.clicked.connect(self.export_historic)
        layout.addWidget(btn_export)

        # Cargar datos históricos
        self.load_historic()

    def setup_clientes_tab(self):
        layout = QVBoxLayout(self.tab_clientes)

        # Botón para agregar cliente
        btn_add_client = QPushButton("Nuevo Cliente")
        btn_add_client.clicked.connect(self.show_new_client_dialog)
        layout.addWidget(btn_add_client)

        # Tabla de clientes
        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(6)
        self.clients_table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Teléfono", "Correo",
            "Fecha Registro", "Apartados Activos"
        ])
        
        header = self.clients_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.clients_table)

        # Cargar datos de clientes
        self.load_clients_table()

    def load_clients_table(self):
        try:
            with sqlite3.connect("db/store.db") as conn_store, \
                 sqlite3.connect("db/movements.db") as conn_movements:
                cursor_store = conn_store.cursor()
                cursor_movements = conn_movements.cursor()
                
                # Obtener clientes
                cursor_store.execute("""
                    SELECT id, nombre, telefono, correo, fecha_registro
                    FROM clientes
                    ORDER BY nombre
                """)
                
                clients = cursor_store.fetchall()
                self.clients_table.setRowCount(len(clients))
                
                for row, client in enumerate(clients):
                    # Obtener cantidad de apartados activos
                    cursor_movements.execute("""
                        SELECT COUNT(*) 
                        FROM apartados 
                        WHERE cliente_telefono = ? 
                        AND estado = 'pendiente'
                    """, (client[2],))
                    
                    apartados_count = cursor_movements.fetchone()[0]
                    
                    # Mostrar datos en la tabla
                    for col, value in enumerate(client):
                        if col == 4:  # Fecha
                            text = value.split()[0] if value else ''
                        else:
                            text = str(value)
                        item = QTableWidgetItem(text)
                        item.setTextAlignment(Qt.AlignCenter)
                        self.clients_table.setItem(row, col, item)
                    
                    # Agregar contador de apartados
                    item = QTableWidgetItem(str(apartados_count))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.clients_table.setItem(row, 5, item)
                
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error al cargar clientes: {str(e)}")

    def show_new_client_dialog(self):
        dialog = ClientDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_clients_table()
            self.load_layaways()

    def show_new_layaway(self):
        dialog = LayawayDialog(self.user_data)
        if dialog.exec_() == QDialog.Accepted:
            self.load_layaways()
            self.load_clients_table()

    def show_add_payment_dialog(self):
        # Obtener el apartado seleccionado
        current_row = self.layaway_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Por favor seleccione un apartado para abonar")
            return

        # Obtener datos del apartado seleccionado
        apartado_id = int(self.layaway_table.item(current_row, 0).text())
        restante = float(self.layaway_table.item(current_row, 7).text().replace('$', ''))
        
        if restante <= 0:
            QMessageBox.warning(self, "Error", "Este apartado ya está pagado")
            return

        dialog = AddPaymentDialog(apartado_id, restante, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_layaways()
            self.load_historic()

    def load_layaways(self):
        try:
            with sqlite3.connect("db/movements.db") as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        id, cliente_nombre, cliente_telefono,
                        articulo_nombre, cantidad, precio_total,
                        anticipo, restante,
                        CASE 
                            WHEN estado = 'pendiente' THEN 'Por Pagar'
                            WHEN estado = 'completado' THEN 'Pagado'
                            WHEN estado = 'cancelado' THEN 'Cancelado'
                        END as estado_pago,
                        fecha_limite
                    FROM apartados
                    ORDER BY fecha_creacion DESC
                """)
                
                apartados = cursor.fetchall()
                self.layaway_table.setRowCount(len(apartados))
                
                for row, apartado in enumerate(apartados):
                    for col, value in enumerate(apartado):
                        if col in [5, 6, 7]:  # Valores monetarios
                            text = f"${value:.2f}"
                        elif col == 9:  # Fecha límite
                            text = value.split()[0] if value else ''
                        else:
                            text = str(value)
                        item = QTableWidgetItem(text)
                        item.setTextAlignment(Qt.AlignCenter)
                        self.layaway_table.setItem(row, col, item)
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error al cargar apartados: {str(e)}")

    def load_historic(self):
        try:
            with sqlite3.connect("db/movements.db") as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        id, cliente_nombre, cliente_telefono,
                        articulo_nombre, cantidad, precio_total,
                        anticipo, restante,
                        CASE 
                            WHEN estado = 'pendiente' THEN 'Por Pagar'
                            WHEN estado = 'completado' THEN 'Pagado'
                            WHEN estado = 'cancelado' THEN 'Cancelado'
                        END as estado_pago,
                        fecha_creacion,
                        fecha_finalizacion
                    FROM apartados
                    WHERE estado != 'pendiente'
                    ORDER BY fecha_creacion DESC
                """)
                
                apartados = cursor.fetchall()
                self.historic_table.setRowCount(len(apartados))
                
                for row, apartado in enumerate(apartados):
                    for col, value in enumerate(apartado):
                        if col in [5, 6, 7]:  # Valores monetarios
                            text = f"${value:.2f}"
                        elif col in [9, 10]:  # Fechas
                            text = value.split()[0] if value else ''
                        else:
                            text = str(value)
                        item = QTableWidgetItem(text)
                        item.setTextAlignment(Qt.AlignCenter)
                        self.historic_table.setItem(row, col, item)
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error al cargar histórico: {str(e)}")

    def export_historic(self):
        try:
            # Obtener datos de la tabla
            data = []
            for row in range(self.historic_table.rowCount()):
                row_data = []
                for col in range(self.historic_table.columnCount()):
                    item = self.historic_table.item(row, col)
                    row_data.append(item.text() if item else '')
                data.append(row_data)
            
            # Crear DataFrame
            df = pd.DataFrame(data, columns=[
                "ID", "Cliente", "Teléfono", "Artículo",
                "Cantidad", "Total", "Anticipo", "Restante",
                "Estado", "Fecha Creación", "Fecha Finalización"
            ])
            
            # Generar nombre de archivo
            filename = f"historico_apartados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            # Guardar archivo
            df.to_excel(filename, index=False)
            
            QMessageBox.information(
                self, 
                "Éxito", 
                f"Archivo exportado correctamente:\n{filename}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Error al exportar: {str(e)}"
            )

class ClientDialog(QDialog):
    def __init__(self, parent=None, client_id=None):
        super().__init__(parent)
        self.client_id = client_id
        self.setup_ui()
        if client_id:
            self.load_client_data()

    def setup_ui(self):
        self.setWindowTitle("Nuevo Cliente")
        layout = QVBoxLayout(self)

        # Formulario
        form_layout = QFormLayout()
        
        self.nombre_input = QLineEdit()
        self.telefono_input = QLineEdit()
        self.correo_input = QLineEdit()
        self.notas_input = QTextEdit()
        
        if self.client_id:
            conn = sqlite3.connect("db/store.db")
            cursor = conn.cursor()
            
            cursor.execute("SELECT nombre, telefono, correo, notas FROM clientes WHERE id = ?", (self.client_id,))
            client_data = cursor.fetchone()
            
            conn.close()
            
            if client_data:
                self.nombre_input.setText(client_data[0])
                self.telefono_input.setText(client_data[1])
                self.correo_input.setText(client_data[2])
                self.notas_input.setText(client_data[3])
        
        form_layout.addRow("Nombre:", self.nombre_input)
        form_layout.addRow("Teléfono:", self.telefono_input)
        form_layout.addRow("Correo:", self.correo_input)
        form_layout.addRow("Notas:", self.notas_input)
        
        layout.addLayout(form_layout)

        # Botones
        buttons = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.clicked.connect(self.accept)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        
        buttons.addWidget(self.btn_guardar)
        buttons.addWidget(btn_cancelar)
        layout.addLayout(buttons)

    def accept(self):
        try:
            # Obtener valores
            nombre = self.nombre_input.text().strip()
            telefono = self.telefono_input.text().strip()
            correo = self.correo_input.text().strip()
            notas = self.notas_input.toPlainText().strip()
            
            # Validaciones
            if not nombre:
                raise ValueError("El nombre es obligatorio")
            if not telefono:
                raise ValueError("El teléfono es obligatorio")
            
            with sqlite3.connect("db/store.db") as conn:
                cursor = conn.cursor()
                
                # Verificar si el teléfono ya existe (solo para nuevos clientes)
                if not self.client_id:  # Solo verificar para nuevos clientes
                    cursor.execute("""
                        SELECT id FROM clientes 
                        WHERE telefono = ?
                    """, (telefono,))
                    
                    if cursor.fetchone():
                        raise ValueError("Ya existe un cliente con ese teléfono")
                
                # Insertar o actualizar cliente
                if self.client_id:
                    cursor.execute("""
                        UPDATE clientes 
                        SET nombre = ?, telefono = ?, correo = ?, notas = ?
                        WHERE id = ?
                    """, (nombre, telefono, correo, notas, self.client_id))
                else:
                    cursor.execute("""
                        INSERT INTO clientes (nombre, telefono, correo, notas)
                        VALUES (?, ?, ?, ?)
                    """, (nombre, telefono, correo, notas))
                
                conn.commit()
            
            # Notificar éxito
            QMessageBox.information(
                self, 
                "Éxito", 
                "Cliente guardado correctamente"
            )
            
            # Actualizar la vista principal
            if isinstance(self.parent(), LayawayWindow):
                self.parent().load_clients_table()
            
            # Cerrar el diálogo
            super().accept()
            
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except sqlite3.Error as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Error en la base de datos: {str(e)}"
            )

    def load_client_data(self):
        conn = sqlite3.connect("db/store.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT nombre, telefono, correo, notas FROM clientes WHERE id = ?", (self.client_id,))
        client_data = cursor.fetchone()
        
        conn.close()
        
        if client_data:
            self.nombre_input.setText(client_data[0])
            self.telefono_input.setText(client_data[1])
            self.correo_input.setText(client_data[2])
            self.notas_input.setText(client_data[3])

class LayawayDialog(QDialog):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.current_client = None
        self.current_item = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Nuevo Apartado")
        layout = QVBoxLayout(self)

        # Grupo de búsqueda de cliente
        client_group = QGroupBox("Búsqueda de Cliente")
        client_layout = QVBoxLayout()
        
        # Layout para búsqueda
        search_layout = QHBoxLayout()
        self.phone_search = QLineEdit()
        self.phone_search.setPlaceholderText("Buscar cliente por teléfono...")
        btn_search_client = QPushButton("Buscar")
        btn_search_client.clicked.connect(self.search_client)
        
        search_layout.addWidget(self.phone_search)
        search_layout.addWidget(btn_search_client)
        client_layout.addLayout(search_layout)
        
        # Información del cliente
        self.client_info = QLabel("No se ha seleccionado ningún cliente")
        client_layout.addWidget(self.client_info)
        
        client_group.setLayout(client_layout)
        layout.addWidget(client_group)

        # Grupo de búsqueda de artículo
        item_group = QGroupBox("Búsqueda de Artículo")
        item_layout = QVBoxLayout()
        
        # Layout para búsqueda de artículo
        item_search_layout = QHBoxLayout()
        self.id_search = QLineEdit()
        self.id_search.setPlaceholderText("Buscar artículo por ID...")
        btn_search_item = QPushButton("Buscar")
        btn_search_item.clicked.connect(self.search_item)
        
        item_search_layout.addWidget(self.id_search)
        item_search_layout.addWidget(btn_search_item)
        item_layout.addLayout(item_search_layout)
        
        # Información del artículo
        self.item_info = QLabel("No se ha seleccionado ningún artículo")
        item_layout.addWidget(self.item_info)
        
        item_group.setLayout(item_layout)
        layout.addWidget(item_group)

        # Grupo de detalles del apartado
        details_group = QGroupBox("Detalles del Apartado")
        details_layout = QFormLayout()
        
        self.cantidad = QSpinBox()
        self.cantidad.setMinimum(1)
        self.cantidad.valueChanged.connect(self.update_price)
        
        self.anticipo = QDoubleSpinBox()
        self.anticipo.setMinimum(0)
        self.anticipo.setMaximum(999999)
        self.anticipo.setDecimals(2)
        self.anticipo.valueChanged.connect(self.update_price)
        
        self.total_label = QLabel("Total: $0.00")
        self.restante_label = QLabel("Restante: $0.00")
        
        self.notas = QTextEdit()
        self.notas.setMaximumHeight(100)
        
        details_layout.addRow("Cantidad:", self.cantidad)
        details_layout.addRow("Anticipo ($):", self.anticipo)
        details_layout.addRow(self.total_label)
        details_layout.addRow(self.restante_label)
        details_layout.addRow("Notas:", self.notas)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)

        # Botones
        buttons = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.clicked.connect(self.save_layaway)
        self.btn_guardar.setEnabled(False)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        
        buttons.addWidget(self.btn_guardar)
        buttons.addWidget(btn_cancelar)
        layout.addLayout(buttons)

    def search_client(self):
        telefono = self.phone_search.text().strip()
        if not telefono:
            QMessageBox.warning(self, "Error", "Ingrese un número de teléfono")
            return
            
        try:
            with sqlite3.connect("db/store.db") as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, nombre, telefono, correo 
                    FROM clientes 
                    WHERE telefono = ?
                """, (telefono,))
                
                client = cursor.fetchone()
                
                if client:
                    self.current_client = {
                        "id": client[0],
                        "nombre": client[1],
                        "telefono": client[2],
                        "correo": client[3]
                    }
                    
                    self.client_info.setText(
                        f"Cliente encontrado:\n"
                        f"Nombre: {client[1]}\n"
                        f"Teléfono: {client[2]}\n"
                        f"Correo: {client[3] or 'No especificado'}"
                    )
                    
                    self.check_enable_save()
                else:
                    QMessageBox.warning(self, "Error", "Cliente no encontrado")
                    self.client_info.setText("No se ha seleccionado ningún cliente")
                    self.current_client = None
                    self.check_enable_save()
                    
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error en la base de datos: {str(e)}")

    def search_item(self):
        search_id = self.id_search.text().strip()
        if not search_id:
            QMessageBox.warning(self, "Error", "Ingrese un ID del artículo")
            return
            
        try:
            id_numero = int(search_id)
            
            with sqlite3.connect("db/store.db") as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, nombre, precio_venta, cantidad 
                    FROM inventario 
                    WHERE id = ? AND cantidad > 0
                """, (id_numero,))
                
                item = cursor.fetchone()
                
                if item:
                    self.current_item = {
                        "id": item[0],
                        "nombre": item[1],
                        "precio": item[2],
                        "disponible": item[3]
                    }
                    
                    self.item_info.setText(
                        f"ID: {item[0]}\n"
                        f"Artículo: {item[1]}\n"
                        f"Precio: ${item[2]:.2f}\n"
                        f"Disponible: {item[3]} unidades"
                    )
                    
                    self.cantidad.setMaximum(item[3])
                    self.check_enable_save()
                    self.update_price()
                else:
                    QMessageBox.warning(self, "Error", "Artículo no encontrado o sin existencias")
                    self.clear_item_info()
                
        except ValueError:
            QMessageBox.warning(self, "Error", "Por favor ingrese un número de ID válido")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error en la base de datos: {str(e)}")
            self.clear_item_info()

    def clear_item_info(self):
        self.item_info.setText("No se ha seleccionado ningún artículo")
        self.current_item = None
        self.check_enable_save()
        self.total_label.setText("Total: $0.00")
        self.restante_label.setText("Restante: $0.00")
        self.cantidad.setValue(1)
        self.anticipo.setValue(0)

    def check_enable_save(self):
        self.btn_guardar.setEnabled(self.current_client is not None and self.current_item is not None)

    def update_price(self):
        if self.current_item:
            total = self.current_item["precio"] * self.cantidad.value()
            self.total_label.setText(f"Total: ${total:.2f}")
            self.anticipo.setMaximum(total)
            restante = max(total - self.anticipo.value(), 0)
            self.restante_label.setText(f"Restante: ${restante:.2f}")

    def save_layaway(self):
        try:
            cantidad = self.cantidad.value()
            total = self.current_item["precio"] * cantidad
            anticipo = self.anticipo.value()
            
            if anticipo < total * 0.20:
                raise ValueError("El anticipo debe ser al menos el 20% del total")
            
            with sqlite3.connect("db/store.db") as conn_store, \
                 sqlite3.connect("db/movements.db") as conn_movements:
                
                cursor_store = conn_store.cursor()
                cursor_movements = conn_movements.cursor()
                
                # Verificar stock
                cursor_store.execute("""
                    SELECT cantidad 
                    FROM inventario 
                    WHERE id = ?
                """, (self.current_item["id"],))
                
                stock_actual = cursor_store.fetchone()[0]
                
                if stock_actual < cantidad:
                    raise ValueError(f"Stock insuficiente. Solo hay {stock_actual} unidades disponibles")
                
                # Registrar apartado
                cursor_movements.execute("""
                    INSERT INTO apartados (
                        fecha_limite,
                        cliente_nombre, cliente_telefono, cliente_correo,
                        articulo_id, articulo_nombre, cantidad,
                        precio_total, anticipo, restante,
                        estado, usuario_id, notas
                    ) VALUES (
                        date('now', '+30 days'),
                        ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        'pendiente', ?, ?
                    )
                """, (
                    self.current_client["nombre"],
                    self.current_client["telefono"],
                    self.current_client["correo"],
                    self.current_item["id"],
                    self.current_item["nombre"],
                    cantidad,
                    total,
                    anticipo,
                    total - anticipo,
                    self.user_data['id'],
                    self.notas.toPlainText()
                ))
                
                # Actualizar inventario
                cursor_store.execute("""
                    UPDATE inventario 
                    SET cantidad = cantidad - ? 
                    WHERE id = ?
                """, (cantidad, self.current_item["id"]))
                
            QMessageBox.information(
                self, 
                "Éxito", 
                f"Apartado registrado correctamente\n"
                f"Stock actualizado: {stock_actual - cantidad} unidades restantes"
            )
            self.accept()
            
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error en la base de datos: {str(e)}")

class AddPaymentDialog(QDialog):
    def __init__(self, apartado_id, restante, parent=None):
        super().__init__(parent)
        self.apartado_id = apartado_id
        self.restante = restante
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Agregar Abono")
        layout = QVBoxLayout(self)

        # Mostrar restante
        layout.addWidget(QLabel(f"Restante por pagar: ${self.restante:.2f}"))

        # Campo para el abono
        form_layout = QFormLayout()
        self.payment_input = QDoubleSpinBox()
        self.payment_input.setMaximum(self.restante)
        self.payment_input.setDecimals(2)
        form_layout.addRow("Monto a abonar:", self.payment_input)
        layout.addLayout(form_layout)

        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        try:
            abono = self.payment_input.value()
            if abono <= 0:
                raise ValueError("El abono debe ser mayor a 0")

            with sqlite3.connect("db/movements.db") as conn:
                cursor = conn.cursor()
                
                # Actualizar el apartado
                cursor.execute("""
                    UPDATE apartados 
                    SET 
                        anticipo = anticipo + ?,
                        restante = restante - ?,
                        estado = CASE 
                            WHEN restante - ? <= 0 THEN 'completado'
                            ELSE estado 
                        END,
                        fecha_finalizacion = CASE 
                            WHEN restante - ? <= 0 THEN CURRENT_TIMESTAMP
                            ELSE fecha_finalizacion 
                        END
                    WHERE id = ?
                """, (abono, abono, abono, abono, self.apartado_id))

            QMessageBox.information(
                self, 
                "Éxito", 
                "Abono registrado correctamente"
            )
            
            super().accept()
            
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except sqlite3.Error as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Error en la base de datos: {str(e)}"
            ) 