"""
Script para inicializar la base de datos con el esquema completo
"""
import sqlite3
import sys
from pathlib import Path

# Agregar el directorio raíz al path de Python
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from config.settings import config

def init_database():
    """Inicializar la base de datos con todas las tablas"""
    
    print("=" * 60)
    print("INICIALIZACIÓN DE BASE DE DATOS - FORMA GEST PRO")
    print("=" * 60)
    
    # Verificar si la base de datos ya existe
    if config.DB_PATH.exists():
        print(f"⚠️  La base de datos ya existe en: {config.DB_PATH}")
        respuesta = input("¿Desea recrearla? (si/no): ").strip().lower()
        if respuesta != 'si':
            print("Operación cancelada.")
            return False
    
    try:
        # Leer el esquema SQL
        schema_path = root_dir / "database" / "schema.sql"
        if not schema_path.exists():
            print(f"❌ No se encontró el archivo de esquema: {schema_path}")
            return False
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Crear conexión a la base de datos
        print(f"📁 Creando base de datos en: {config.DB_PATH}")
        conn = sqlite3.connect(config.DB_PATH)
        cursor = conn.cursor()
        
        # Ejecutar el esquema completo
        print("🔧 Ejecutando esquema SQL...")
        cursor.executescript(schema_sql)
        
        # Insertar datos iniciales
        print("📝 Insertando datos iniciales...")
        
        # Insertar empresa por defecto
        cursor.execute('''
            INSERT OR IGNORE INTO empresa (nombre, nit) 
            VALUES (?, ?)
        ''', (config.EMPRESA_NOMBRE, config.EMPRESA_NIT))
        
        # Insertar configuraciones por defecto
        configuraciones = [
            ('TASA_MORA_DIARIA', '0.0005', 'Tasa de interés diario por mora (0.05%)'),
            ('DIAS_GRACIA', '5', 'Días de gracia antes de aplicar mora'),
            ('RUTA_COMPROBANTES', './resources/comprobantes/', 'Ruta para guardar comprobantes'),
            ('RUTA_FOTOS', './resources/fotos_estudiantes/', 'Ruta para fotos de estudiantes')
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO configuraciones (clave, valor, descripcion)
            VALUES (?, ?, ?)
        ''', configuraciones)
        
        # Insertar usuario administrador por defecto
        cursor.execute('''
            INSERT OR IGNORE INTO usuarios (username, password_hash, nombre_completo, rol)
            VALUES (?, ?, ?, ?)
        ''', ('admin', 'scrypt:32768:8:1$O6y7jXK1mD9pRwQ3$...', 'Administrador', 'ADMINISTRADOR'))
        
        # Verificar tablas creadas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tablas = cursor.fetchall()
        
        # Commit y cerrar conexión
        conn.commit()
        conn.close()
        
        print(f"\n✅ Base de datos inicializada exitosamente!")
        print(f"📊 Tablas creadas: {len(tablas)}")
        
        for tabla in tablas:
            print(f"   • {tabla[0]}")
        
        print("\n🎉 ¡La base de datos está lista para usar!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error inicializando la base de datos: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
