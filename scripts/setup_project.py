# scripts/setup_project.py
import os
import sys
from pathlib import Path

def setup_project():
    """Configurar proyecto completo"""
    print("🔧 Configurando proyecto FormaGestPro...")
    print("=" * 50)
    
    current_dir = Path(__file__).parent.parent
    print(f"📁 Directorio del proyecto: {current_dir}")
    
    # 1. Crear directorios necesarios
    directories = [
        "app/views/windows",
        "app/views/tabs",
        "app/views/generated",
        "app/views/ui",
        "scripts",
        "resources/icons",
        "data"
    ]
    
    for directory in directories:
        dir_path = current_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Directorio: {directory}")
    
    # 2. Crear archivos __init__.py
    init_files = [
        "app/__init__.py",
        "app/views/__init__.py",
        "app/views/windows/__init__.py",
        "app/views/tabs/__init__.py"
    ]
    
    init_content = "# Módulo inicializado\n"
    
    for init_file in init_files:
        file_path = current_dir / init_file
        if not file_path.exists():
            file_path.write_text(init_content, encoding='utf-8')
            print(f"✅ Creado: {init_file}")
        else:
            print(f"⚠️  Ya existe: {init_file}")
    
    # 3. Crear main_gui.py si no existe
    main_gui_path = current_dir / "main_gui.py"
    if not main_gui_path.exists():
        main_gui_content = '''"""
FormaGestPro - Sistema de Gestión Académica
Punto de entrada principal
"""
import sys
from PySide6.QtWidgets import QApplication
from app.views.windows.main_window_tabs import MainWindowTabs

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindowTabs()
    window.show()
    
    sys.exit(app.exec())
'''
        main_gui_path.write_text(main_gui_content, encoding='utf-8')
        print(f"✅ Creado: main_gui.py")
    
    # 4. Verificar PySide6
    print("\n🔍 Verificando PySide6...")
    try:
        from PySide6.QtWidgets import QApplication
        print("✅ PySide6 está instalado correctamente")
    except ImportError:
        print("❌ PySide6 no está instalado")
        print("💡 Ejecuta: pip install pyside6")
    
    print("\n" + "=" * 50)
    print("🎉 Configuración completada!")
    print("\n📝 Para iniciar la aplicación:")
    print("   python main_gui.py")
    print("=" * 50)

if __name__ == "__main__":
    setup_project()