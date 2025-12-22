# app/views/tabs/financiero_tab.py
"""
Pestaña de Gestión Financiera (placeholder)
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class FinancieroTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        
        label = QLabel("💰 GESTIÓN FINANCIERA\n\n🚧 En desarrollo 🚧")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2ecc71;
                padding: 100px;
            }
        """)
        
        layout.addWidget(label)