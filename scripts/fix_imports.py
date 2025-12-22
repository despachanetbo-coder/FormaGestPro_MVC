# scripts/fix_imports.py
import os
from pathlib import Path

def fix_imports():
    """Reparar problemas de importación"""
    print("🔧 Reparando problemas de importación...")
    
    # 1. Crear __init__.py faltantes
    init_files = {
        "app/views/windows/__init__.py": '''"""
Ventanas principales del sistema
"""
from .main_window_tabs import MainWindowTabs

__all__ = ["MainWindowTabs"]
''',
        
        "app/__init__.py": '''"""
FormaGestPro - Sistema de Gestión Académica
"""

__version__ = "2.0.0"
__author__ = "Tu Equipo"
'''
    }
    
    for filepath, content in init_files.items():
        path = Path(filepath)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
            print(f"✅ Creado: {filepath}")
        else:
            print(f"⚠️  Ya existe: {filepath}")
    
    # 2. Verificar main_window_tabs.py
    mw_path = Path("app/views/windows/main_window_tabs.py")
    if mw_path.exists():
        print(f"✅ main_window_tabs.py existe")
        
        # Leer y verificar contenido
        content = mw_path.read_text(encoding='utf-8')
        
        # Verificar si tiene los imports correctos
        if "from app.views.generated.ui_main_window_tabs import Ui_MainWindow" in content:
            print("✅ Imports correctos encontrados")
        else:
            print("⚠️  Los imports pueden necesitar ajustes")
    else:
        print(f"❌ main_window_tabs.py no existe")
        print("💡 Creando archivo básico...")
        
        # Crear archivo básico
        basic_content = '''"""
Ventana principal con sistema de pestañas
"""
import sys
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

try:
    from app.views.generated.ui_main_window_tabs import Ui_MainWindow
except ImportError:
    print("⚠️  No se pudo importar Ui_MainWindow")
    # Crear UI básica
    class Ui_MainWindow:
        def setupUi(self, window):
            pass

class MainWindowTabs(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("FormaGestPro")
        self.setGeometry(100, 100, 800, 600)
        
        # Widget temporal
        label = QLabel("🚧 Ventana principal - En desarrollo")
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)
'''
        
        mw_path.write_text(basic_content, encoding='utf-8')
        print(f"✅ Creado main_window_tabs.py básico")
    
    print("\n🎯 Problemas de importación reparados!")
    print("\n📝 Para probar:")
    print("   python main_gui.py")

if __name__ == "__main__":
    fix_imports()