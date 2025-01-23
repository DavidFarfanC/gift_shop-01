from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QDialog, QLineEdit, 
    QDateEdit, QSpinBox, QDoubleSpinBox, QTextEdit, QMessageBox,
    QComboBox, QFormLayout, QGroupBox, QHeaderView, QTabWidget
)
from PyQt5.QtCore import Qt, QDate
import sqlite3
from datetime import datetime, timedelta

class LayawayWindow(QWidget):
    def __init__(self, user_data):
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
            
        except sqlite3.Error as e:
            print(f"Error al inicializar la base de datos: {str(e)}")

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Crear el widget de pestañas
        self.tabs = QTabWidget()
        
        # Pestaña de Apartados
        self.tab_apartados = QWidget()
        self.setup_apartados_tab()
        self.tabs.addTab(self.tab_apartados, "Apartados")
        
        # Pestaña de Clientes
        self.tab_clientes = QWidget()
        self.setup_clientes_tab()
        self.tabs.addTab(self.tab_clientes, "Clientes")
        
        layout.addWidget(self.tabs)

    def setup_apartados_tab(self):
        layout = QVBoxLayout(self.tab_apartados)
        
        # Botones superiores
        button_layout = QHBoxLayout()
        
        self.btn_new_client = QPushButton("Nuevo Cliente")
        self.btn_new_layaway = QPushButton("Nuevo Apartado")
        self.btn_new_client.clicked.connect(self.show_new_client_dialog)
        self.btn_new_layaway.clicked.connect(self.show_new_layaway_dialog)
        
        button_layout.addWidget(self.btn_new_client)
        button_layout.addWidget(self.btn_new_layaway)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Tabla de apartados
        self.layaway_table = QTableWidget()
        self.layaway_table.setColumnCount(10)
        self.layaway_table.setHorizontalHeaderLabels([
            "ID", "Cliente", "Teléfono", "Artículo", "Cantidad",
            "Total", "Anticipo", "Monto Restante", "Estado Pago", "Fecha Límite"
        ])
        header = self.layaway_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        
        layout.addWidget(self.layaway_table)
        self.load_layaways()

    def setup_clientes_tab(self):
        layout = QVBoxLayout(self.tab_clientes)
        
        # Botones y búsqueda
        top_layout = QHBoxLayout()
        
        # Búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar cliente...")
        self.search_input.textChanged.connect(self.filter_clients)
        top_layout.addWidget(self.search_input)
        
        # Botón nuevo cliente
        btn_add_client = QPushButton("Nuevo Cliente")
        btn_add_client.clicked.connect(self.show_new_client_dialog)
        top_layout.addWidget(btn_add_client)
        
        layout.addLayout(top_layout)
        
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
        
        # Botones de acción
        action_layout = QHBoxLayout()
        
        btn_edit = QPushButton("Editar")
        btn_edit.clicked.connect(self.edit_client)
        btn_view_layaways = QPushButton("Ver Apartados")
        btn_view_layaways.clicked.connect(self.view_client_layaways)
        
        action_layout.addWidget(btn_edit)
        action_layout.addWidget(btn_view_layaways)
        action_layout.addStretch()
        
        layout.addLayout(action_layout)
        
        self.load_clients_table()

    def load_clients_table(self):
        try:
            conn = sqlite3.connect("db/store.db")
            cursor = conn.cursor()
            
            # Primero obtenemos los clientes
            cursor.execute("""
                SELECT 
                    id, nombre, telefono, correo, fecha_registro
                FROM clientes
                ORDER BY nombre
            """)
            
            clients = cursor.fetchall()
            self.clients_table.setRowCount(len(clients))
            
            # Conectamos a la base de datos de movements para contar apartados
            conn_movements = sqlite3.connect("db/movements.db")
            cursor_movements = conn_movements.cursor()
            
            for row, client in enumerate(clients):
                # Obtener cantidad de apartados activos para este cliente
                cursor_movements.execute("""
                    SELECT COUNT(*) 
                    FROM apartados 
                    WHERE cliente_telefono = ? 
                    AND estado = 'pendiente'
                """, (client[2],))  # client[2] es el teléfono
                
                apartados_count = cursor_movements.fetchone()[0]
                
                # Mostrar datos en la tabla
                for col, value in enumerate(client):
                    if col == 4:  # Fecha
                        text = value.split()[0] if value else ''  # Solo la fecha, sin hora
                    else:
                        text = str(value)
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.clients_table.setItem(row, col, item)
                
                # Agregar contador de apartados
                item = QTableWidgetItem(str(apartados_count))
                item.setTextAlignment(Qt.AlignCenter)
                self.clients_table.setItem(row, 5, item)
            
            conn.close()
            conn_movements.close()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error al cargar clientes: {str(e)}")

    def filter_clients(self):
        search_text = self.search_input.text().lower()
        for row in range(self.clients_table.rowCount()):
            show_row = False
            for col in range(1, 4):  # Buscar en nombre, teléfono y correo
                item = self.clients_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            self.clients_table.setRowHidden(row, not show_row)

    def edit_client(self):
        current_row = self.clients_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Por favor seleccione un cliente")
            return
            
        client_id = self.clients_table.item(current_row, 0).text()
        dialog = ClientDialog(self, client_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_clients_table()

    def view_client_layaways(self):
        current_row = self.clients_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Por favor seleccione un cliente")
            return
            
        telefono = self.clients_table.item(current_row, 2).text()
        dialog = ClientLayawaysDialog(self, telefono)
        dialog.exec_()

    def show_new_client_dialog(self):
        dialog = ClientDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_layaways()

    def show_new_layaway_dialog(self):
        dialog = LayawayDialog(self.user_data)
        if dialog.exec_() == QDialog.Accepted:
            self.load_layaways()

    def load_layaways(self):
        try:
            conn = sqlite3.connect("db/movements.db")
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
                        text = value.split()[0] if value else ''  # Solo la fecha
                    else:
                        text = str(value)
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.layaway_table.setItem(row, col, item)
            
            conn.close()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error al cargar apartados: {str(e)}")

class ClientDialog(QDialog):
    def __init__(self, parent=None, client_id=None):
        super().__init__(parent)
        self.client_id = client_id
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Nuevo Cliente")
        layout = QVBoxLayout(self)

        # Formulario
        form_layout = QFormLayout()
        
        self.nombre = QLineEdit()
        self.telefono = QLineEdit()
        self.correo = QLineEdit()
        self.notas = QTextEdit()
        
        if self.client_id:
            conn = sqlite3.connect("db/store.db")
            cursor = conn.cursor()
            
            cursor.execute("SELECT nombre, telefono, correo, notas FROM clientes WHERE id = ?", (self.client_id,))
            client_data = cursor.fetchone()
            
            conn.close()
            
            if client_data:
                self.nombre.setText(client_data[0])
                self.telefono.setText(client_data[1])
                self.correo.setText(client_data[2])
                self.notas.setText(client_data[3])
        
        form_layout.addRow("Nombre:", self.nombre)
        form_layout.addRow("Teléfono:", self.telefono)
        form_layout.addRow("Correo:", self.correo)
        form_layout.addRow("Notas:", self.notas)
        
        layout.addLayout(form_layout)

        # Botones
        buttons = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.clicked.connect(self.save_client)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        
        buttons.addWidget(self.btn_guardar)
        buttons.addWidget(btn_cancelar)
        layout.addLayout(buttons)

    def save_client(self):
        try:
            if not self.nombre.text().strip():
                raise ValueError("El nombre es obligatorio")
            if not self.telefono.text().strip():
                raise ValueError("El teléfono es obligatorio")
            
            conn = sqlite3.connect("db/store.db")
            cursor = conn.cursor()
            
            if self.client_id:
                cursor.execute("""
                    UPDATE clientes 
                    SET nombre = ?, telefono = ?, correo = ?, notas = ?
                    WHERE id = ?
                """, (
                    self.nombre.text().strip(),
                    self.telefono.text().strip(),
                    self.correo.text().strip(),
                    self.notas.toPlainText().strip(),
                    self.client_id
                ))
            else:
                cursor.execute("""
                    INSERT INTO clientes (nombre, telefono, correo, notas)
                    VALUES (?, ?, ?, ?)
                """, (
                    self.nombre.text().strip(),
                    self.telefono.text().strip(),
                    self.correo.text().strip(),
                    self.notas.toPlainText().strip()
                ))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Éxito", "Cliente registrado correctamente")
            self.accept()
            
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Ya existe un cliente con ese teléfono")
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error en la base de datos: {str(e)}")

class LayawayDialog(QDialog):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
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

        # Inicializar variables
        self.current_item = None
        self.current_client = None

    def search_client(self):
        telefono = self.phone_search.text().strip()
        if not telefono:
            QMessageBox.warning(self, "Error", "Ingrese un número de teléfono")
            return
            
        try:
            conn = sqlite3.connect("db/store.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, nombre, telefono, correo 
                FROM clientes 
                WHERE telefono = ?
            """, (telefono,))
            
            client = cursor.fetchone()
            conn.close()
            
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

    def check_enable_save(self):
        # Habilitar el botón guardar solo si hay cliente y artículo seleccionados
        self.btn_guardar.setEnabled(self.current_client is not None and self.current_item is not None)

    def search_item(self):
        search_id = self.id_search.text().strip()
        if not search_id:
            QMessageBox.warning(self, "Error", "Ingrese un ID del artículo")
            return
            
        try:
            # Convertimos a número para buscar por ID
            try:
                id_numero = int(search_id)
            except ValueError:
                QMessageBox.warning(self, "Error", "Por favor ingrese un número de ID válido")
                return
                
            print(f"Buscando artículo con ID: {id_numero}")  # Debug
            conn = sqlite3.connect("db/store.db")
            cursor = conn.cursor()
            
            # Buscamos solo por ID numérico
            cursor.execute("""
                SELECT id, nombre, precio_venta, cantidad 
                FROM inventario 
                WHERE id = ? AND cantidad > 0
            """, (id_numero,))
            
            item = cursor.fetchone()
            
            if item:
                print(f"Artículo encontrado: {item}")  # Debug
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
                self.btn_guardar.setEnabled(True)
                self.update_price()
            else:
                print(f"No se encontró el artículo con ID: {id_numero}")  # Debug
                QMessageBox.warning(self, "Error", "Artículo no encontrado o sin existencias")
                self.clear_item_info()
            
            conn.close()
            
        except sqlite3.Error as e:
            print(f"Error de SQLite: {str(e)}")  # Debug
            QMessageBox.critical(self, "Error", f"Error en la base de datos: {str(e)}")
            self.clear_item_info()

    def clear_item_info(self):
        self.item_info.setText("Artículo no seleccionado")
        self.current_item = None
        self.btn_guardar.setEnabled(False)
        self.total_label.setText("Total: $0.00")
        self.restante_label.setText("Restante: $0.00")
        self.cantidad.setValue(1)
        self.anticipo.setValue(0)

    def update_price(self):
        if hasattr(self, 'current_item') and self.current_item:
            total = self.current_item["precio"] * self.cantidad.value()
            self.total_label.setText(f"Total: ${total:.2f}")
            self.anticipo.setMaximum(total)
            self.update_remaining()

    def update_remaining(self):
        if hasattr(self, 'current_item') and self.current_item:
            total = self.current_item["precio"] * self.cantidad.value()
            anticipo = self.anticipo.value()
            self.restante_label.setText(f"Restante: ${max(total - anticipo, 0):.2f}")

    def save_layaway(self):
        if not self.current_client:
            QMessageBox.warning(self, "Error", "Debe seleccionar un cliente")
            return
            
        try:
            cantidad = self.cantidad.value()
            total = self.current_item["precio"] * cantidad
            anticipo = self.anticipo.value()
            
            if anticipo < total * 0.20:  # Mínimo 20% de anticipo
                raise ValueError("El anticipo debe ser al menos el 20% del total")
            
            conn = sqlite3.connect("db/movements.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO apartados (
                    fecha_creacion,
                    fecha_limite,
                    cliente_nombre,
                    cliente_telefono,
                    cliente_correo,
                    articulo_id,
                    articulo_nombre,
                    cantidad,
                    precio_total,
                    anticipo,
                    restante,
                    estado,
                    usuario_id,
                    notas
                ) VALUES (
                    CURRENT_TIMESTAMP,
                    date('now', '+30 days'),
                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    'pendiente',
                    ?,
                    ?
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
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Éxito", "Apartado registrado correctamente")
            self.accept()
            
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error en la base de datos: {str(e)}")

class ClientLayawaysDialog(QDialog):
    def __init__(self, parent, telefono):
        super().__init__(parent)
        self.telefono = telefono
        self.setup_ui()
        self.load_layaways()

    def setup_ui(self):
        self.setWindowTitle("Apartados del Cliente")
        self.setMinimumWidth(800)
        layout = QVBoxLayout(self)
        
        # Tabla de apartados
        self.layaway_table = QTableWidget()
        self.layaway_table.setColumnCount(8)
        self.layaway_table.setHorizontalHeaderLabels([
            "ID", "Artículo", "Cantidad", "Total",
            "Anticipo", "Restante", "Estado", "Fecha Límite"
        ])
        header = self.layaway_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        
        layout.addWidget(self.layaway_table)
        
        # Botón cerrar
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def load_layaways(self):
        try:
            conn = sqlite3.connect("db/movements.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id, articulo_nombre, cantidad,
                    precio_total, anticipo, restante,
                    estado, fecha_limite
                FROM apartados
                WHERE cliente_telefono = ?
                ORDER BY fecha_creacion DESC
            """, (self.telefono,))
            
            layaways = cursor.fetchall()
            self.layaway_table.setRowCount(len(layaways))
            
            for row, layaway in enumerate(layaways):
                for col, value in enumerate(layaway):
                    if col in [3, 4, 5]:  # Valores monetarios
                        text = f"${value:.2f}"
                    else:
                        text = str(value)
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.layaway_table.setItem(row, col, item)
            
            conn.close()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error al cargar apartados: {str(e)}") 