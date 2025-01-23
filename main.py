import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QTabWidget, QStyleFactory, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from frontend.login_ui import LoginWindow
from frontend.inventory_ui import InventoryApp
from frontend.sales_ui import SalesWindow
from frontend.layaway_ui import LayawayWindow
from utils.styles import STYLE_SHEET

class MainWindow(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setStyleSheet(STYLE_SHEET)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("W Gift Shop - Sistema de Gestión")
        self.setGeometry(50, 50, 1200, 800)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Contenedor superior para el logo y bienvenida
        top_container = QWidget()
        top_layout = QHBoxLayout(top_container)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Logo (ahora más pequeño y a la izquierda)
        logo_label = QLabel()
        logo_label.setObjectName("logo")
        logo_path = "assets/logo.jpg"
        
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                # Logo más pequeño (100x100)
                scaled_pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
                logo_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Contenedor para el texto de bienvenida
        welcome_container = QWidget()
        welcome_layout = QVBoxLayout(welcome_container)
        
        # Título y bienvenida
        welcome = QLabel(f"Bienvenido, {self.user_data['rol'].title()}")
        welcome.setObjectName("welcome")
        welcome.setAlignment(Qt.AlignLeft)
        
        # Información del usuario
        user_info = QLabel(f"Usuario: {self.user_data['telefono']} | Correo: {self.user_data['correo']}")
        user_info.setAlignment(Qt.AlignLeft)
        
        welcome_layout.addWidget(welcome)
        welcome_layout.addWidget(user_info)
        
        # Agregar logo y bienvenida al contenedor superior
        top_layout.addWidget(logo_label)
        top_layout.addWidget(welcome_container)
        top_layout.addStretch()  # Esto empuja todo hacia la izquierda
        
        # Agregar el contenedor superior al layout principal
        main_layout.addWidget(top_container)

        # Sistema de pestañas
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyle(QStyleFactory.create('Fusion'))

        # Pestaña de inicio
        home_tab = QWidget()
        home_layout = QVBoxLayout(home_tab)

        # Pestaña de inventario
        inventory_tab = InventoryApp(self.user_data)
        
        # Pestaña de ventas
        sales_tab = SalesWindow(self.user_data, self)

        # Pestaña de apartados
        layaway_tab = LayawayWindow(self.user_data)

        # Agregar pestañas
        self.tab_widget.addTab(home_tab, "Inicio")
        self.tab_widget.addTab(inventory_tab, "Inventario")
        self.tab_widget.addTab(sales_tab, "Ventas")
        self.tab_widget.addTab(layaway_tab, "Apartados")

        main_layout.addWidget(self.tab_widget)

class MainApplication:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_window = LoginWindow()
        self.main_window = None
        
        self.login_window.login_successful.connect(self.on_login_successful)
        
        self.login_window.show()
        sys.exit(self.app.exec_())
    
    def on_login_successful(self, user_data):
        self.login_window.close()
        self.main_window = MainWindow(user_data)
        self.main_window.show()

if __name__ == "__main__":
    MainApplication()
