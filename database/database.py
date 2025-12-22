# database\database.py
"""
Módulo para manejar conexiones a SQLite3 de forma simple y eficiente.
"""
import sqlite3
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    """Clase singleton para manejar la conexión a la base de datos SQLite3"""
    
    _instance = None
    _connection = None
    _db_path = None
    
    def __new__(cls, db_path: str = None):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)

            # ENCONTRAR LA RUTA CORRECTA DE LA BASE DE DATOS
            if db_path is None:
                # Buscar data/formagestpro.db desde múltiples ubicaciones posibles
                posibles_rutas = [
                    # Desde directorio actual de trabajo
                    Path("data/formagestpro.db"),
                    # Desde el directorio del script ejecutado
                    Path(sys.argv[0]).parent / "data" / "formagestpro.db",
                    # Desde el directorio del proyecto (asumiendo que database.py está en raíz/database/)
                    Path(__file__).parent.parent / "data" / "formagestpro.db",
                    # Desde el directorio del proyecto (asumiendo que está en app/database/)
                    Path(__file__).parent.parent.parent / "data" / "formagestpro.db",
                    # Desde el directorio del proyecto (asumiendo que está en app/database/)
                    Path(__file__).parent.parent.parent.parent / "data" / "formagestpro.db",
                    # Ruta absoluta común
                    Path("C:/FormaGestPro_MVC/data/formagestpro.db"),
                    # Ruta absoluta común 2
                    Path("D:/FormaGestPro_MVC/data/formagestpro.db")
                ]
                
                # Buscar la primera ruta que exista
                db_path_encontrada = None
                for ruta in posibles_rutas:
                    if ruta.exists():
                        db_path_encontrada = ruta
                        break
                
                if db_path_encontrada:
                    cls._instance._db_path = str(db_path_encontrada)
                    logger.info(f"📂 Base de datos encontrada en: {db_path_encontrada}")
                else:
                    # Si no existe, crear en ubicación predeterminada
                    default_path = Path("data/formagestpro.db")
                    default_path.parent.mkdir(exist_ok=True, parents=True)
                    cls._instance._db_path = str(default_path)
                    logger.warning(f"⚠️  Base de datos no encontrada, creando nueva en: {default_path}")
            else:
                cls._instance._db_path = db_path
            
            cls._instance._connect()
        
        return cls._instance
    
    def _connect(self):
        """Establece conexión a la base de datos"""
        try:
            # Asegurar que el directorio existe
            db_dir = Path(self._db_path).parent
            db_dir.mkdir(exist_ok=True, parents=True)
            
            self._connection = sqlite3.connect(self._db_path)
            self._connection.row_factory = sqlite3.Row  # Para acceder a columnas por nombre
            logger.info(f"✅ Conectado a base de datos: {self._db_path}")
            
            # Habilitar foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")
            
        except Exception as e:
            logger.error(f"❌ Error conectando a la base de datos: {e}")
            # Mostrar ruta completa para debugging
            logger.error(f"📁 Ruta intentada: {self._db_path}")
            logger.error(f"📁 Directorio actual: {os.getcwd()}")
            raise
    
    def get_connection(self):
        """Obtiene la conexión activa"""
        if self._connection is None:
            self._connect()
        return self._connection
    
    def close(self):
        """Cierra la conexión"""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("🔌 Conexión a base de datos cerrada")
    
    def execute(self, query: str, params: tuple = (), commit: bool = True) -> sqlite3.Cursor:
        """
        Ejecuta una consulta SQL.
        
        Args:
            query: Consulta SQL
            params: Parámetros para la consulta
            commit: Si es True, guarda los cambios automáticamente
        
        Returns:
            Cursor de la consulta
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            if commit:
                conn.commit()
            logger.debug(f"📝 Ejecutada consulta: {query[:50]}...")
            return cursor
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Error ejecutando consulta: {e}")
            raise
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Ejecuta una consulta y devuelve todos los resultados como diccionarios"""
        cursor = self.execute(query, params, commit=False)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Ejecuta una consulta y devuelve un solo resultado como diccionario"""
        cursor = self.execute(query, params, commit=False)
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def table_exists(self, table_name: str) -> bool:
        """Verifica si una tabla existe en la base de datos"""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = self.fetch_one(query, (table_name,))
        return result is not None
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Obtiene el esquema de una tabla"""
        query = f"PRAGMA table_info({table_name})"
        return self.fetch_all(query)
    
    def get_all_tables(self) -> List[str]:
        """Obtiene todas las tablas de la base de datos"""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        tables = self.fetch_all(query)
        return [table['name'] for table in tables]

# Instancia global de la base de datos
db = Database()