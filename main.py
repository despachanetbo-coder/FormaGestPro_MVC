"""
FormaGestPro - Sistema de Gestión Académica
Punto de entrada principal de la aplicación
"""
import sys
import argparse
from pathlib import Path

# Agregar el directorio raíz al path de Python
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

def init_database():
    """Inicializar la base de datos"""
    from scripts.init_database import init_database as init_db
    return init_db()

def run_cli():
    """Ejecutar la interfaz de línea de comandos"""
    from cli import main as cli_main
    cli_main()

def show_info():
    """Mostrar información del sistema"""
    from config.settings import config
    
    print("=" * 60)
    print("FORMA GEST PRO - Sistema de Gestión Académica")
    print("=" * 60)
    print(f"Versión: 1.0.0")
    print(f"Directorio base: {config.BASE_DIR}")
    print(f"Base de datos: {config.DB_PATH}")
    print(f"Empresa: {config.EMPRESA_NOMBRE}")
    print(f"NIT: {config.EMPRESA_NIT}")
    print("=" * 60)

def main():
    """Función principal de la aplicación"""
    
    parser = argparse.ArgumentParser(description='FormaGestPro - Sistema de Gestión Académica')
    parser.add_argument('--init', action='store_true', help='Inicializar base de datos')
    parser.add_argument('--cli', action='store_true', help='Ejecutar interfaz CLI')
    parser.add_argument('--info', action='store_true', help='Mostrar información del sistema')
    
    args = parser.parse_args()
    
    if args.init:
        return 0 if init_database() else 1
    elif args.cli:
        run_cli()
        return 0
    elif args.info:
        show_info()
        return 0
    else:
        # Modo interactivo por defecto
        show_info()
        print("\nModos de operación disponibles:")
        print("  1. Interfaz CLI (python main.py --cli)")
        print("  2. Inicializar BD (python main.py --init)")
        print("  3. Información (python main.py --info)")
        print()
        print("Para desarrollo, usa: python cli.py")
        return 0

if __name__ == "__main__":
    sys.exit(main())
