"""
FormaGestPro - Sistema de Gestión Académica
Punto de entrada principal para la interfaz gráfica
"""
import sys
import os
from pathlib import Path

print("=" * 60)
print("🚀 FORMAGESTPRO - SISTEMA DE GESTIÓN ACADÉMICA")
print("Versión 2.0 - Interfaz con Pestañas")
print("=" * 60)

# Configurar rutas
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "app"))

try:
    from PySide6.QtWidgets import QApplication
    from app.views.windows.main_window_tabs import MainWindowTabs
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindowTabs()
    window.showMaximized()
    
    print("✅ Aplicación iniciada correctamente")
    
    sys.exit(app.exec())
    
except Exception as e:
    print(f"💥 ERROR: {e}")
    import traceback
    traceback.print_exc()
    input("Presiona Enter para salir...")
