"""
test_minimal.py - Prueba mínima de PySide6
"""
import sys
print("🔧 Test: Importando PySide6...")
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QTabWidget
print("✅ PySide6 importado")

print("🔧 Test: Creando ventana mínima...")
app = QApplication(sys.argv)

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TEST - FormaGestPro")
        self.setGeometry(100, 100, 800, 600)
        
        central = QWidget()
        layout = QVBoxLayout(central)
        
        label = QLabel("✅ PRUEBA EXITOSA\nLa aplicación puede iniciar correctamente.")
        label.setStyleSheet("font-size: 18px; color: green; padding: 50px;")
        layout.addWidget(label)
        
        self.setCentralWidget(central)

window = TestWindow()
window.show()

print("✅ Ventana creada")
print("🎉 Ejecutando aplicación de prueba...")
sys.exit(app.exec())
