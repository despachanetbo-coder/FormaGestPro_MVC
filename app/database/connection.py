# app/database/connection.py
"""
Conexión centralizada a PostgreSQL para FormaGestPro
Reemplaza todas las conexiones SQLite dispersas
"""
import logging
import psycopg2
from psycopg2 import pool, extras
from psycopg2.errors import Error as PGError
from typing import Optional, Dict, List, Any, Tuple
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class PostgreSQLConnection:
    """Clase singleton para gestionar conexiones a PostgreSQL"""

    _instance = None
    _connection_pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.config = self._load_config()
            self._connection_pool = None
            self._initialized = True

    def _load_config(self) -> Dict[str, str]:
        """Cargar configuración de la base de datos"""
        # Puedes cargar desde variables de entorno o archivo de configuración
        return {
            "host": os.getenv("DB_HOST", "localhost"),
            "database": os.getenv("DB_NAME", "formagestpro_db"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", ""),
            "port": os.getenv("DB_PORT", "5432"),
            "min_connections": int(os.getenv("DB_MIN_CONN", "1")),
            "max_connections": int(os.getenv("DB_MAX_CONN", "10")),
        }

    def initialize_pool(self) -> bool:
        """Inicializar el pool de conexiones"""
        try:
            self._connection_pool = pool.SimpleConnectionPool(
                minconn=self.config["min_connections"],
                maxconn=self.config["max_connections"],
                host=self.config["host"],
                database=self.config["database"],
                user=self.config["user"],
                password=self.config["password"],
                port=self.config["port"],
            )
            logger.info(
                f"✅ Pool de conexiones PostgreSQL inicializado: {self.config['database']}"
            )
            return True
        except Exception as e:
            logger.error(f"❌ Error inicializando pool PostgreSQL: {e}")
            return False

    def get_connection(self):
        """Obtener una conexión del pool"""
        try:
            if not self._connection_pool:
                self.initialize_pool()

            connection = self._connection_pool.getconn()
            connection.autocommit = False  # Usar transacciones explícitas
            return connection
        except Exception as e:
            logger.error(f"❌ Error obteniendo conexión: {e}")
            raise

    def return_connection(self, connection):
        """Devolver conexión al pool"""
        if connection and self._connection_pool:
            try:
                self._connection_pool.putconn(connection)
            except Exception as e:
                logger.error(f"Error devolviendo conexión al pool: {e}")

    def execute_query(self, query: str, params: Tuple = None, fetch: bool = False):
        """
        Ejecutar consulta de manera segura con manejo automático de conexión

        Args:
            query: Consulta SQL
            params: Parámetros para la consulta
            fetch: Si True, retorna resultados; si False, solo ejecuta

        Returns:
            List[Dict] si fetch=True, None si fetch=False
        """
        connection = None
        cursor = None

        try:
            connection = self.get_connection()
            cursor = connection.cursor(cursor_factory=extras.RealDictCursor)

            cursor.execute(query, params or ())

            if fetch:
                result = cursor.fetchall()
                return [dict(row) for row in result]
            else:
                connection.commit()
                return None

        except PGError as e:
            if connection:
                connection.rollback()
            logger.error(f"❌ Error PostgreSQL: {e}\nConsulta: {query}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.return_connection(connection)

    def execute_many(self, query: str, params_list: List[Tuple]):
        """Ejecutar múltiples inserciones/actualizaciones en una transacción"""
        connection = None
        cursor = None

        try:
            connection = self.get_connection()
            cursor = connection.cursor()

            for params in params_list:
                cursor.execute(query, params)

            connection.commit()
            logger.info(f"✅ Ejecutadas {len(params_list)} operaciones")

        except PGError as e:
            if connection:
                connection.rollback()
            logger.error(f"❌ Error en execute_many: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.return_connection(connection)

    def fetch_one(self, query: str, params: Tuple = None) -> Optional[Dict]:
        """Obtener un solo registro"""
        result = self.execute_query(query, params, fetch=True)
        return result[0] if result else None

    def fetch_all(self, query: str, params: Tuple = None) -> List[Dict]:
        """Obtener todos los registros"""
        return self.execute_query(query, params, fetch=True) or []

    def close_all(self):
        """Cerrar todas las conexiones del pool"""
        if self._connection_pool:
            self._connection_pool.closeall()
            logger.info("🔒 Pool de conexiones cerrado")
            self._connection_pool = None

    def test_connection(self) -> bool:
        """Probar la conexión a la base de datos"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            cursor.close()
            self.return_connection(connection)

            logger.info(f"✅ Conexión exitosa a PostgreSQL: {version[0]}")
            return True
        except Exception as e:
            logger.error(f"❌ Error probando conexión: {e}")
            return False


# Instancia global para uso en toda la aplicación
db = PostgreSQLConnection()
