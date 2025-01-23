import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QLabel, QTabWidget, QStyleFactory, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from frontend.login_ui import LoginWindow
from frontend.inventory_ui import InventoryApp
from frontend.sales_ui import SalesWindow
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
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Logo
        logo_label = QLabel()
        logo_label.setObjectName("logo")
        
        # Intentar diferentes rutas para el logo
        possible_paths = [
            "assets/logo.png",
            "./assets/logo.png",
            "../assets/logo.png",
            os.path.join(os.path.dirname(__file__), "assets/logo.png")
        ]
        
        logo_loaded = False
        for path in possible_paths:
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    logo_label.setPixmap(scaled_pixmap)
                    logo_loaded = True
                    print(f"Logo cargado exitosamente desde: {path}")
                    break
        
        if not logo_loaded:
            print("No se pudo cargar el logo. Rutas intentadas:", possible_paths)
            print("Directorio actual:", os.getcwd())
            logo_label.setText("W Gift Shop")
            logo_label.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: #9B8989;
                    padding: 20px;
                }
            """)

        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # Título y bienvenida
        welcome = QLabel(f"Bienvenido, {self.user_data['rol'].title()}")
        welcome.setObjectName("welcome")
        welcome.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome)

        # Sistema de pestañas
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyle(QStyleFactory.create('Fusion'))

        # Pestaña de inicio
        home_tab = QWidget()
        home_layout = QVBoxLayout(home_tab)
        
        # Información del usuario
        user_info = QLabel(f"Usuario: {self.user_data['telefono']} | Correo: {self.user_data['correo']}")
        user_info.setAlignment(Qt.AlignCenter)
        home_layout.addWidget(user_info)

        # Pestaña de inventario
        inventory_tab = InventoryApp(self.user_data)
        
        # Pestaña de ventas
        sales_tab = SalesWindow(self.user_data, self)

        # Agregar pestañas
        self.tab_widget.addTab(home_tab, "Inicio")
        self.tab_widget.addTab(inventory_tab, "Inventario")
        self.tab_widget.addTab(sales_tab, "Ventas")

        layout.addWidget(self.tab_widget)

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
