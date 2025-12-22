# app/views/tabs/ayuda_tab.py
"""
Pestaña de Ayuda (placeholder)
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class AyudaTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        
        label = QLabel("🔧 AYUDA Y UTILIDADES\n\n🚧 En desarrollo 🚧")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #f39c12;
                padding: 100px;
            }
        """)
        
        layout.addWidget(label)