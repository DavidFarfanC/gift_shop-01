# Definición de la paleta de colores más opaca y profesional
COLORS = {
    'primary':    '#9B8989',  # Marrón grisáceo medio
    'secondary':  '#B5A4A4',  # Marrón grisáceo claro
    'accent':     '#C9B6B6',  # Marrón muy claro
    'success':    '#8FA896',  # Verde grisáceo
    'warning':    '#C4B097',  # Beige oscuro
    'danger':     '#B79090',  # Rosa grisáceo
    'light':      '#F2EDED',  # Gris muy claro
    'white':      '#FFFFFF',  # Blanco puro
    'gray':       '#D6CECE',  # Gris medio
    'dark':       '#5D4F4F',  # Marrón grisáceo oscuro
}

STYLE_SHEET = f"""
/* Estilos generales */
QMainWindow, QWidget {{
    background-color: {COLORS['white']};
    color: {COLORS['dark']};
}}

/* Logo */
QLabel#logo {{
    padding: 20px;
    background-color: {COLORS['white']};
    border-radius: 10px;
}}

/* Pestañas */
QTabWidget::pane {{
    border: 1px solid {COLORS['gray']};
    background: {COLORS['white']};
    border-radius: 6px;
}}

QTabBar::tab {{
    background: {COLORS['light']};
    color: {COLORS['dark']};
    padding: 8px 20px;
    border: 1px solid {COLORS['gray']};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    min-width: 100px;
    font-size: 13px;
}}

QTabBar::tab:selected {{
    background: {COLORS['primary']};
    color: {COLORS['white']};
}}

QTabBar::tab:hover:!selected {{
    background: {COLORS['secondary']};
    color: {COLORS['white']};
}}

/* Botones */
QPushButton {{
    background-color: {COLORS['primary']};
    color: {COLORS['white']};
    border: none;
    padding: 8px 15px;
    border-radius: 6px;
    font-size: 13px;
    min-width: 80px;
}}

QPushButton:hover {{
    background-color: {COLORS['secondary']};
}}

QPushButton:pressed {{
    background-color: {COLORS['dark']};
}}

QPushButton#success {{
    background-color: {COLORS['success']};
}}

QPushButton#warning {{
    background-color: {COLORS['warning']};
}}

QPushButton#danger {{
    background-color: {COLORS['danger']};
}}

/* Campos de texto */
QLineEdit {{
    padding: 8px;
    border: 2px solid {COLORS['gray']};
    border-radius: 6px;
    background-color: {COLORS['white']};
    font-size: 13px;
    color: {COLORS['dark']};
}}

QLineEdit:focus {{
    border: 2px solid {COLORS['primary']};
    background-color: {COLORS['light']};
}}

/* Tablas */
QTableWidget {{
    background-color: {COLORS['white']};
    alternate-background-color: {COLORS['light']};
    border: 1px solid {COLORS['gray']};
    border-radius: 6px;
    gridline-color: {COLORS['gray']};
}}

QTableWidget::item {{
    padding: 5px;
}}

QTableWidget::item:selected {{
    background-color: {COLORS['primary']};
    color: {COLORS['white']};
}}

QHeaderView::section {{
    background-color: {COLORS['primary']};
    color: {COLORS['white']};
    padding: 8px;
    border: none;
    font-weight: bold;
}}

/* Etiquetas */
QLabel {{
    color: {COLORS['dark']};
    font-size: 13px;
}}

QLabel#title {{
    font-size: 24px;
    font-weight: bold;
    color: {COLORS['dark']};
    padding: 10px;
}}

QLabel#welcome {{
    font-size: 16px;
    color: {COLORS['primary']};
}}

QLabel#total {{
    font-size: 18px;
    font-weight: bold;
    color: {COLORS['dark']};
}}

QLabel#info_producto {{
    font-size: 14px;
    color: {COLORS['dark']};
    padding: 10px;
    background-color: {COLORS['light']};
    border-radius: 6px;
}}

/* ComboBox */
QComboBox {{
    padding: 8px;
    border: 2px solid {COLORS['gray']};
    border-radius: 6px;
    background-color: {COLORS['white']};
    min-width: 100px;
}}

QComboBox:hover {{
    border: 2px solid {COLORS['primary']};
    background-color: {COLORS['light']};
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 10px;
}}

/* DateEdit */
QDateEdit {{
    padding: 8px;
    border: 2px solid {COLORS['gray']};
    border-radius: 6px;
    background-color: {COLORS['white']};
}}

QDateEdit:hover {{
    border: 2px solid {COLORS['primary']};
    background-color: {COLORS['light']};
}}

/* Mensajes */
QMessageBox {{
    background-color: {COLORS['white']};
}}

QMessageBox QPushButton {{
    min-width: 100px;
}}

/* Scrollbars */
QScrollBar:vertical {{
    border: none;
    background: {COLORS['light']};
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background: {COLORS['primary']};
    border-radius: 4px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLORS['secondary']};
}}

/* Grupos */
QGroupBox {{
    border: 2px solid {COLORS['gray']};
    border-radius: 6px;
    margin-top: 1em;
    padding-top: 10px;
}}

QGroupBox::title {{
    color: {COLORS['dark']};
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 3px 0 3px;
}}
""" 