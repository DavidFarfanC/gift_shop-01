from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import pyqtSignal
import sqlite3
import hashlib

class LoginWindow(QWidget):
    login_successful = pyqtSignal(dict)  # Señal para cuando el login es exitoso

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Campos de entrada
        self.telefono_input = QLineEdit()
        self.telefono_input.setPlaceholderText("Teléfono")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)

        # Botón de login
        self.login_btn = QPushButton("Iniciar Sesión")
        self.login_btn.clicked.connect(self.intentar_login)

        # Agregar widgets al layout
        layout.addWidget(QLabel("Teléfono:"))
        layout.addWidget(self.telefono_input)
        layout.addWidget(QLabel("Contraseña:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def intentar_login(self):
        telefono = self.telefono_input.text()
        password = self.password_input.text()

        if not telefono or not password:
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos")
            return

        # Hash de la contraseña
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect("db/database.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, telefono, correo, rol 
            FROM usuarios 
            WHERE telefono = ? AND password = ? AND activo = 1
        """, (telefono, hashed_password))
        
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            user_data = {
                'id': usuario[0],
                'telefono': usuario[1],
                'correo': usuario[2],
                'rol': usuario[3]
            }
            self.login_successful.emit(user_data)
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Credenciales inválidas") 