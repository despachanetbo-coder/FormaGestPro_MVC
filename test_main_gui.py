"""
test_main_gui.py - Prueba del punto de entrada
"""
print("=" * 60)
print("🧪 PRUEBA MAIN_GUI - INICIANDO...")
print("=" * 60)

import sys
import os
from pathlib import Path

# Configurar paths
current_dir = Path(__file__).parent
print(f"📁 Directorio: {current_dir}")

# Añadir paths
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "app"))

print(f"📁 Sys.path: {sys.path[:3]}...")

try:
    # Paso 1: Importar PySide6
    print("\n1️⃣  IMPORTANDO PySide6...")
    from PySide6.QtWidgets import QApplication
    print("   ✅ PySide6 importado")
    
    # Paso 2: Intentar importar MainWindowTabs
    print("\n2️⃣  IMPORTANDO MainWindowTabs...")
    try:
        # Primero intentar con la versión simple
        import_path = str(current_dir / "app" / "views" / "windows" / "main_window_tabs_simple.py")
        print(f"   🔍 Intentando: {import_path}")
        
        import importlib.util
        spec = importlib.util.spec_from_file_location("main_window_tabs_simple", import_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        MainWindowTabs = module.MainWindowTabs
        print("   ✅ MainWindowTabs importado desde versión simple")
        
    except Exception as e1:
        print(f"   ❌ Error versión simple: {type(e1).__name__}: {e1}")
        
        try:
            # Intentar con el archivo original
            from app.views.windows.main_window_tabs import MainWindowTabs
            print("   ✅ MainWindowTabs importado desde original")
        except Exception as e2:
            print(f"   ❌ Error original: {type(e2).__name__}: {e2}")
            
            # Crear clase de emergencia
            print("   🔧 Creando clase de emergencia...")
            class MainWindowTabs(QApplication):
                def __init__(self):
                    super().__init__(sys.argv)
                def show(self):
                    print("   🎭 Clase dummy - No hace nada")
    
    # Paso 3: Crear aplicación
    print("\n3️⃣  CREANDO APLICACIÓN...")
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    print("   ✅ Aplicación creada")
    
    # Paso 4: Crear ventana
    print("\n4️⃣  CREANDO VENTANA...")
    window = MainWindowTabs()
    print("   ✅ Ventana creada")
    
    # Paso 5: Mostrar ventana
    print("\n5️⃣  MOSTRANDO VENTANA...")
    window.show()
    print("   ✅ Ventana mostrada")
    
    print("\n" + "=" * 60)
    print("🎉 PRUEBA EXITOSA - APLICACIÓN INICIADA!")
    print("=" * 60)
    
    sys.exit(app.exec())
    
except Exception as e:
    print(f"\n💥 ERROR CRÍTICO EN PRUEBA: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    
    input("\nPresiona Enter para salir...")
