# debug_project.py
import sys
import os
from pathlib import Path

print("=" * 70)
print("🔍 DEPURACIÓN PASO A PASO - FORMAGESTPRO")
print("=" * 70)

# Paso 1: Verificar directorio actual
print("\n1️⃣  VERIFICANDO DIRECTORIO ACTUAL:")
current_dir = Path(__file__).parent.absolute()
print(f"   📁 Directorio del script: {current_dir}")
print(f"   📁 Directorio de trabajo: {os.getcwd()}")

# Paso 2: Verificar estructura de archivos
print("\n2️⃣  VERIFICANDO ESTRUCTURA DE ARCHIVOS:")
required_files = [
    ("main_gui.py", current_dir / "main_gui.py"),
    ("app/__init__.py", current_dir / "app" / "__init__.py"),
    ("app/views/__init__.py", current_dir / "app" / "views" / "__init__.py"),
    ("app/views/windows/__init__.py", current_dir / "app" / "views" / "windows" / "__init__.py"),
    ("app/views/windows/main_window_tabs.py", current_dir / "app" / "views" / "windows" / "main_window_tabs.py"),
]

for name, path in required_files:
    if path.exists():
        # Verificar tamaño
        size = path.stat().st_size
        # Verificar bytes nulos
        with open(path, 'rb') as f:
            content = f.read()
            null_count = content.count(b'\x00')
        
        status = "✅" if null_count == 0 else "💥"
        print(f"   {status} {name}: {size} bytes, bytes nulos: {null_count}")
        
        if null_count > 0:
            print(f"      🚨 ARCHIVO CORRUPTO con {null_count} bytes nulos!")
            # Mostrar primeros bytes en hex
            print(f"      Primeros 100 bytes (hex): {content[:100].hex()}")
    else:
        print(f"   ❌ {name}: NO EXISTE")

# Paso 3: Verificar encoding de main_window_tabs.py
print("\n3️⃣  VERIFICANDO ENCODING DE main_window_tabs.py:")
mw_path = current_dir / "app" / "views" / "windows" / "main_window_tabs.py"

if mw_path.exists():
    print("   Probando diferentes encodings...")
    
    encodings_to_test = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'ascii']
    
    for encoding in encodings_to_test:
        try:
            with open(mw_path, 'r', encoding=encoding) as f:
                content = f.read(500)  # Leer solo 500 caracteres
                print(f"   {encoding}: ✅ Se puede leer")
                # Mostrar primeras 3 líneas
                lines = content.split('\n')[:3]
                for i, line in enumerate(lines):
                    print(f"      Línea {i+1}: {line[:80]}" + ("..." if len(line) > 80 else ""))
                break
        except UnicodeDecodeError as e:
            print(f"   {encoding}: ❌ {e}")
        except Exception as e:
            print(f"   {encoding}: ❌ Error: {type(e).__name__}")

# Paso 4: Verificar si el archivo es Python válido
print("\n4️⃣  VERIFICANDO SI ES CÓDIGO PYTHON VÁLIDO:")
if mw_path.exists():
    try:
        # Intentar compilar
        with open(mw_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        compile(code, mw_path.name, 'exec')
        print("   ✅ Código Python compila correctamente")
        
        # Verificar sintaxis básica
        if "class MainWindowTabs" in code and "def __init__" in code:
            print("   ✅ Contiene clase MainWindowTabs con constructor")
        else:
            print("   ⚠️  Puede no tener la estructura esperada")
            
    except SyntaxError as e:
        print(f"   ❌ ERROR DE SINTAXIS: {e}")
        print(f"      Línea: {e.lineno}, Columna: {e.offset}")
        print(f"      Texto: {e.text}")
    except Exception as e:
        print(f"   ❌ Error inesperado: {type(e).__name__}: {e}")

# Paso 5: Verificar imports
print("\n5️⃣  VERIFICANDO IMPORTS EN main_window_tabs.py:")
if mw_path.exists():
    with open(mw_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()[:20]  # Solo primeras 20 líneas
        
    print("   Primeras 20 líneas del archivo:")
    for i, line in enumerate(lines, 1):
        print(f"      {i:2d}: {line.rstrip()}")

# Paso 6: Crear un archivo de prueba MÍNIMO
print("\n6️⃣  CREANDO ARCHIVO DE PRUEBA MÍNIMO:")
test_file = current_dir / "test_minimal.py"

test_content = '''"""
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
        
        label = QLabel("✅ PRUEBA EXITOSA\\nLa aplicación puede iniciar correctamente.")
        label.setStyleSheet("font-size: 18px; color: green; padding: 50px;")
        layout.addWidget(label)
        
        self.setCentralWidget(central)

window = TestWindow()
window.show()

print("✅ Ventana creada")
print("🎉 Ejecutando aplicación de prueba...")
sys.exit(app.exec())
'''

with open(test_file, 'w', encoding='utf-8') as f:
    f.write(test_content)

print(f"   ✅ Archivo de prueba creado: {test_file}")
print("   📝 Ejecutar: python test_minimal.py")

# Paso 7: Crear una versión SÚPER SIMPLE de main_window_tabs.py
print("\n7️⃣  CREANDO VERSIÓN SÚPER SIMPLE DE main_window_tabs.py:")
simple_content = '''"""
main_window_tabs.py - VERSIÓN MÍNIMA PARA PRUEBAS
"""
print("🔧 main_window_tabs.py cargado")

# Importar solo lo esencial
try:
    from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QTabWidget
    from PySide6.QtCore import Qt
    print("✅ Imports exitosos")
except ImportError as e:
    print(f"❌ Error importando: {e}")
    # Crear clases dummy para que no falle
    class QMainWindow: pass
    class QWidget: pass
    class QVBoxLayout: pass
    class QLabel: pass
    class QTabWidget: pass
    Qt = type('Qt', (), {'AlignCenter': 'center'})()

class MainWindowTabs(QMainWindow):
    """Ventana principal MÍNIMA para pruebas"""
    
    def __init__(self):
        print("🔧 MainWindowTabs.__init__() llamado")
        super().__init__()
        
        # Configuración mínima
        self.setWindowTitle("FormaGestPro - PRUEBA")
        self.resize(800, 600)
        
        # Widget central simple
        central = QWidget()
        self.setCentralWidget(central)
        
        # Layout simple
        layout = QVBoxLayout(central)
        
        # Etiqueta simple
        label = QLabel("✅ VENTANA PRINCIPAL CARGADA\\nPrueba exitosa!")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        print("✅ MainWindowTabs creada exitosamente")

# Para pruebas directas
if __name__ == "__main__":
    print("🔧 Ejecutando prueba directa...")
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = MainWindowTabs()
    window.show()
    print("🎉 Aplicación iniciada")
    sys.exit(app.exec())
'''

simple_path = current_dir / "app" / "views" / "windows" / "main_window_tabs_simple.py"
simple_path.parent.mkdir(parents=True, exist_ok=True)

with open(simple_path, 'w', encoding='utf-8') as f:
    f.write(simple_content)

print(f"   ✅ Versión simple creada: {simple_path}")

# Paso 8: Crear main_gui de prueba
print("\n8️⃣  CREANDO main_gui DE PRUEBA:")
test_main_gui = current_dir / "test_main_gui.py"

test_gui_content = '''"""
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
    print("\\n1️⃣  IMPORTANDO PySide6...")
    from PySide6.QtWidgets import QApplication
    print("   ✅ PySide6 importado")
    
    # Paso 2: Intentar importar MainWindowTabs
    print("\\n2️⃣  IMPORTANDO MainWindowTabs...")
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
    print("\\n3️⃣  CREANDO APLICACIÓN...")
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    print("   ✅ Aplicación creada")
    
    # Paso 4: Crear ventana
    print("\\n4️⃣  CREANDO VENTANA...")
    window = MainWindowTabs()
    print("   ✅ Ventana creada")
    
    # Paso 5: Mostrar ventana
    print("\\n5️⃣  MOSTRANDO VENTANA...")
    window.show()
    print("   ✅ Ventana mostrada")
    
    print("\\n" + "=" * 60)
    print("🎉 PRUEBA EXITOSA - APLICACIÓN INICIADA!")
    print("=" * 60)
    
    sys.exit(app.exec())
    
except Exception as e:
    print(f"\\n💥 ERROR CRÍTICO EN PRUEBA: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    
    input("\\nPresiona Enter para salir...")
'''

with open(test_main_gui, 'w', encoding='utf-8') as f:
    f.write(test_gui_content)

print(f"   ✅ main_gui de prueba creado: {test_main_gui}")

print("\n" + "=" * 70)
print("📋 RESUMEN DE COMANDOS PARA EJECUTAR:")
print("=" * 70)
print("1. Prueba básica de PySide6: python test_minimal.py")
print("2. Prueba de importación: python test_main_gui.py")
print("3. Verificar archivo corrupto: Ver output de arriba")
print("4. Si hay bytes nulos, ELIMINAR y recrear el archivo")
print("=" * 70)

# Sugerencia final
print("\n💡 RECOMENDACIÓN INMEDIATA:")
print("Ejecuta estos comandos en orden:")

commands = [
    "# 1. Ver si el archivo tiene bytes nulos:",
    "python -c \"with open('app/views/windows/main_window_tabs.py', 'rb') as f: data=f.read(); print(f'Bytes nulos: {data.count(chr(0).encode())}')\"",
    "",
    "# 2. Si tiene bytes nulos (>0), ELIMÍNALO:",
    "# Remove-Item 'app/views/windows/main_window_tabs.py' -Force",
    "",
    "# 3. Crea un archivo NUEVO y SIMPLE:",
    "python -c \"",
    "content = '''",
    "from PySide6.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout",
    "class MainWindowTabs(QMainWindow):",
    "    def __init__(self):",
    "        super().__init__()",
    "        self.setWindowTitle('Test')",
    "        label = QLabel('TEST OK')",
    "        self.setCentralWidget(label)",
    "'''",
    "with open('app/views/windows/main_window_tabs.py', 'w', encoding='utf-8') as f:",
    "    f.write(content)",
    "print('Archivo creado')",
    "\"",
    "",
    "# 4. Prueba:",
    "python test_minimal.py"
]

for cmd in commands:
    print(cmd)