import sys
from PyQt5.QtWidgets import QApplication
from frontend.login_ui import LoginWindow
from frontend.inventory_ui import InventoryApp

class MainApplication:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_window = LoginWindow()
        self.inventory_window = None
        
        # Conectar señal de login exitoso
        self.login_window.login_successful.connect(self.on_login_successful)
        
        self.login_window.show()
        sys.exit(self.app.exec_())
    
    def on_login_successful(self, user_data):
        self.inventory_window = InventoryApp(user_data)
        self.inventory_window.show()

if __name__ == "__main__":
    MainApplication()
