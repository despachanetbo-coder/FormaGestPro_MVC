import subprocess
import sys
from pathlib import Path

def convertir_ui_a_py():
    base_dir = Path(__file__).parent
    ui_dir = base_dir / "app" / "views" / "ui"
    generated_dir = base_dir / "app" / "views" / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)
    
    contador = 0
    
    def convertir_directorio(dir_ui, dir_dest):
        nonlocal contador
        dir_dest.mkdir(exist_ok=True)
        
        for archivo_ui in dir_ui.glob("*.ui"):
            nombre_py = f"ui_{archivo_ui.stem}.py"
            archivo_py = dir_dest / nombre_py
            
            comando = f"pyside6-uic {archivo_ui} -o {archivo_py}"
            try:
                subprocess.run(comando, shell=True, check=True)
                print(f"✅ Convertido: {archivo_ui.relative_to(base_dir)}")
                contador += 1
            except subprocess.CalledProcessError as e:
                print(f"❌ Error: {archivo_ui}: {e}")
        
        for subdir in dir_ui.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('.'):
                nuevo_dest = dir_dest / subdir.name
                convertir_directorio(subdir, nuevo_dest)
    
    print("🔄 Convirtiendo archivos .ui a .py...")
    convertir_directorio(ui_dir, generated_dir)
    print(f"🎉 {contador} archivos convertidos")

if __name__ == "__main__":
    try:
        subprocess.run(["pyside6-uic", "--version"], capture_output=True, check=True)
        convertir_ui_a_py()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pyside6-uic no encontrado. Instala PySide6: pip install PySide6")
        sys.exit(1)
