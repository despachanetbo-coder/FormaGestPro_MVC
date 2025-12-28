# main_gui.py - VERSIÓN CORREGIDA
"""
FormaGestPro - Sistema de Gestión Académica
Punto de entrada principal para la interfaz gráfica - VERSIÓN CORREGIDA
"""
import sys
import os
from pathlib import Path
import traceback

# Y modificar el bloque try-except principal:
try:
    from PySide6.QtWidgets import QApplication
    from app.views.windows.main_window_tabs import MainWindowTabs

    # Configurar aplicación
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("FormaGestPro")

    # Crear ventana principal
    window = MainWindowTabs()
    window.showMaximized()

    print("✅ Aplicación iniciada correctamente")
    print("✅ Todas las importaciones funcionando")

    # Ejecutar aplicación
    sys.exit(app.exec())

except Exception as e:
    print(f"💥 ERROR: {e}")
    traceback.print_exc()
    print("\n📋 VERIFICANDO ARCHIVOS...")

    # Lista de archivos críticos para verificar
    critical_files = [
        "app/__init__.py",
        "app/models/__init__.py",
        "app/views/__init__.py",
        "app/views/windows/main_window_tabs.py",
    ]

    for file in critical_files:
        path = os.path.join(current_dir, file)
        if os.path.exists(path):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - NO EXISTE")

    input("\nPresiona Enter para salir...")

print("=" * 60)
print("🚀 FORMAGESTPRO - SISTEMA DE GESTIÓN ACADÉMICA")
print("Versión 2.0 - Interfaz con Pestañas (Corregida)")
print("=" * 60)

# Configurar rutas ABSOLUTAS
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "app"))
sys.path.insert(0, str(current_dir / "app/models"))
sys.path.insert(0, str(current_dir / "app/controllers"))
sys.path.insert(0, str(current_dir / "app/views"))

try:
    from PySide6.QtWidgets import QApplication
    from app.views.windows.main_window_tabs import MainWindowTabs

    # Configurar aplicación
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("FormaGestPro")

    # Crear ventana principal
    window = MainWindowTabs()
    window.showMaximized()

    print("✅ Aplicación iniciada correctamente")
    print("✅ Todas las importaciones funcionando")

    # Ejecutar aplicación
    sys.exit(app.exec())

except ImportError as e:
    print(f"💥 ERROR DE IMPORTACIÓN: {e}")
    print("\n📋 VERIFICANDO ARCHIVOS CRÍTICOS...")

    # Verificar archivos críticos
    critical_files = [
        "app/__init__.py",
        "app/models/__init__.py",
        "app/models/base_model.py",
        "app/controllers/__init__.py",
        "app/views/__init__.py",
        "app/views/base_view.py",
        "app/views/tabs/__init__.py",
        "app/views/tabs/base_tab.py",
    ]

    for file in critical_files:
        file_path = current_dir / file
        if file_path.exists():
            print(f"  ✅ {file} - EXISTE")
        else:
            print(f"  ❌ {file} - NO EXISTE")

    print("\n🔧 SUGERENCIAS:")
    print("1. Asegúrate de que los archivos __init__.py estén presentes")
    print("2. Verifica que las importaciones relativas usen '.' (ej: .base_model)")
    print("3. Ejecuta python test_imports_fixed.py para diagnóstico detallado")

    import traceback

    traceback.print_exc()
    input("\nPresiona Enter para salir...")

except Exception as e:
    print(f"💥 ERROR INESPERADO: {e}")
    import traceback

    traceback.print_exc()
    input("Presiona Enter para salir...")
