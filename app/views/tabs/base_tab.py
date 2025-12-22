# app/views/tabs/base_tab.py
"""
Tab base con funcionalidades comunes
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt

class BaseTab(QWidget):
    """Tab base con funcionalidades comunes"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.buttons = {}
        
    def create_header(self, title=None):
        """Crear encabezado de la pestaña"""
        header = QLabel(title or self.title)
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                border-bottom: 2px solid #3498db;
                margin-bottom: 20px;
            }
        """)
        header.setAlignment(Qt.AlignCenter)
        return header
    
    def create_button(self, text, callback, style="primary"):
        """Crear botón estilizado"""
        btn = QPushButton(text)
        btn.clicked.connect(callback)
        
        styles = {
            "primary": """
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    font-weight: bold;
                    padding: 10px 20px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """,
            "success": """
                QPushButton {
                    background-color: #2ecc71;
                    color: white;
                    font-weight: bold;
                    padding: 10px 20px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #27ae60;
                }
            """,
            "warning": """
                QPushButton {
                    background-color: #f39c12;
                    color: white;
                    font-weight: bold;
                    padding: 10px 20px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #d68910;
                }
            """,
            "danger": """
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    font-weight: bold;
                    padding: 10px 20px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """
        }
        
        btn.setStyleSheet(styles.get(style, styles["primary"]))
        return btn