import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QPushButton, QLabel, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from frontend.login_ui import LoginWindow
from frontend.inventory_ui import InventoryApp
from frontend.sales_ui import SalesWindow

class MainMenu(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Sistema de Gestión - Menú Principal")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 5px;
                font-size: 14px;
                min-width: 200px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QLabel {
                color: #2c3e50;
                font-size: 16px;
            }
        """)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)

        # Título y bienvenida
        title = QLabel("Sistema de Gestión")
        title.setFont(QFont('Arial', 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        welcome = QLabel(f"Bienvenido, {self.user_data['rol'].title()}")
        welcome.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome)

        # Grid para botones
        button_grid = QGridLayout()
        button_grid.setSpacing(20)

        # Botones
        btn_inventory = QPushButton("Gestión de Inventario")
        btn_inventory.clicked.connect(self.open_inventory)
        btn_inventory.setIcon(QIcon('icons/inventory.png'))  # Agregar ícono si lo tienes

        btn_sales = QPushButton("Ventas")
        btn_sales.clicked.connect(self.open_sales)
        btn_sales.setIcon(QIcon('icons/sales.png'))

        btn_reports = QPushButton("Reportes")
        btn_reports.clicked.connect(self.open_reports)
        btn_reports.setIcon(QIcon('icons/reports.png'))

        btn_settings = QPushButton("Configuración")
        btn_settings.clicked.connect(self.open_settings)
        btn_settings.setIcon(QIcon('icons/settings.png'))

        # Agregar botones al grid
        button_grid.addWidget(btn_inventory, 0, 0)
        button_grid.addWidget(btn_sales, 0, 1)
        button_grid.addWidget(btn_reports, 1, 0)
        button_grid.addWidget(btn_settings, 1, 1)

        layout.addLayout(button_grid)

        # Información del usuario
        user_info = QLabel(f"Usuario: {self.user_data['telefono']} | Correo: {self.user_data['correo']}")
        user_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(user_info)

    def open_inventory(self):
        self.inventory_window = InventoryApp(self.user_data)
        self.inventory_window.show()

    def open_sales(self):
        self.sales_window = SalesWindow(self.user_data, self)
        self.sales_window.show()

    def open_reports(self):
        # Por implementar
        pass

    def open_settings(self):
        # Por implementar
        pass

class MainApplication:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_window = LoginWindow()
        self.main_menu = None
        
        # Conectar señal de login exitoso
        self.login_window.login_successful.connect(self.on_login_successful)
        
        self.login_window.show()
        sys.exit(self.app.exec_())
    
    def on_login_successful(self, user_data):
        self.login_window.close()
        self.main_menu = MainMenu(user_data)
        self.main_menu.show()

if __name__ == "__main__":
    MainApplication()
