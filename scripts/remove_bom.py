"""
remove_bom.py - Remover BOM de archivos Python
"""
import os
import sys
from pathlib import Path

def remove_bom_from_file(filepath):
    """Remover BOM de un archivo"""
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        
        # Verificar si tiene BOM
        if content.startswith(b'\xef\xbb\xbf'):  # UTF-8 BOM
            print(f"⚠️  {filepath}: Tiene BOM UTF-8")
            # Remover BOM y guardar
            with open(filepath, 'wb') as f:
                f.write(content[3:])
            print(f"✅ BOM removido")
            return True
        elif content.startswith(b'\xff\xfe'):  # UTF-16 LE BOM
            print(f"⚠️  {filepath}: Tiene BOM UTF-16 LE")
            # Convertir a UTF-8 sin BOM
            text = content[2:].decode('utf-16-le')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"✅ Convertido a UTF-8 sin BOM")
            return True
        elif content.startswith(b'\xfe\xff'):  # UTF-16 BE BOM
            print(f"⚠️  {filepath}: Tiene BOM UTF-16 BE")
            text = content[2:].decode('utf-16-be')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"✅ Convertido a UTF-8 sin BOM")
            return True
        else:
            # Verificar bytes nulos
            if b'\x00' in content:
                null_count = content.count(b'\x00')
                print(f"💥 {filepath}: Tiene {null_count} bytes nulos!")
                return False
            return False
            
    except Exception as e:
        print(f"❌ Error procesando {filepath}: {e}")
        return False

def scan_directory(directory):
    """Escanear directorio en busca de archivos con BOM"""
    print(f"🔍 Escaneando: {directory}")
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                remove_bom_from_file(filepath)

if __name__ == "__main__":
    print("🔧 REMOVIENDO BOM DE ARCHIVOS PYTHON")
    print("=" * 50)
    
    # Escanear app/views
    scan_directory("app/views")
    
    # Verificar main_gui.py
    if os.path.exists("main_gui.py"):
        remove_bom_from_file("main_gui.py")
    
    print("=" * 50)
    print("✅ Proceso completado")