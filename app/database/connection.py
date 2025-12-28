# app/database/connection.py - Versión corregida con método commit()
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import configparser
import threading


class DatabaseConnection:
    """Clase para manejar la conexión a la base de datos PostgreSQL"""

    _instance = None
    _pool = None
    _lock = threading.Lock()
    _config = None

    def __new__(cls):
        """Implementa el patrón Singleton"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseConnection, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Inicializa la configuración de la base de datos"""
        try:
            config = configparser.ConfigParser()

            # Buscar archivo de configuración en diferentes ubicaciones
            config_locations = [
                "config/database.ini",
                "app/config/database.ini",
                "../config/database.ini",
                "../../config/database.ini",
            ]

            config_file = None
            for location in config_locations:
                if os.path.exists(location):
                    config_file = location
                    break

            if not config_file:
                raise FileNotFoundError("No se encontró el archivo database.ini")

            config.read(config_file, encoding="utf-8")

            self._config = {
                "host": config.get("postgresql", "host", fallback="localhost"),
                "database": config.get("postgresql", "database"),
                "user": config.get("postgresql", "user"),
                "password": config.get("postgresql", "password"),
                "port": config.get("postgresql", "port", fallback="5432"),
            }

            print(f"✓ Configuración de base de datos cargada desde: {config_file}")

        except Exception as e:
            print(f"✗ Error cargando configuración: {e}")
            # Configuración por defecto para desarrollo
            self._config = {
                "host": "localhost",
                "database": "formagestpro_db",
                "user": "postgres",
                "password": "postgres",
                "port": "5432",
            }
            print("⚠ Usando configuración por defecto para desarrollo")

    def get_connection_pool(self, minconn=1, maxconn=10):
        """Obtiene o crea el pool de conexiones"""
        if self._pool is None:
            with self._lock:
                if self._pool is None:
                    if self._config is None:
                        self._initialize()
                    try:
                        self._pool = pool.SimpleConnectionPool(
                            minconn=minconn,
                            maxconn=maxconn,
                            host=self._config["host"],
                            database=self._config["database"],
                            user=self._config["user"],
                            password=self._config["password"],
                            port=self._config["port"],
                        )
                        print("✓ Pool de conexiones PostgreSQL creado exitosamente")
                    except Exception as e:
                        print(f"✗ Error creando pool de conexiones: {e}")
                        self._pool = None

        return self._pool

    def get_connection(self):
        """Obtiene una conexión del pool"""
        try:
            pool = self.get_connection_pool()
            if pool:
                connection = pool.getconn()
                # Configurar autocommit como False para manejar transacciones manualmente
                connection.autocommit = False
                return connection
        except Exception as e:
            print(f"✗ Error obteniendo conexión: {e}")

        return None

    def return_connection(self, connection):
        """Devuelve una conexión al pool"""
        try:
            if self._pool and connection:
                # Asegurar que no hay transacciones pendientes
                if not connection.closed:
                    connection.rollback()
                self._pool.putconn(connection)
        except Exception as e:
            print(f"✗ Error devolviendo conexión: {e}")

    def close_all_connections(self):
        """Cierra todas las conexiones del pool"""
        try:
            if self._pool:
                self._pool.closeall()
                self._pool = None
                print("✓ Todas las conexiones del pool cerradas")
        except Exception as e:
            print(f"✗ Error cerrando conexiones: {e}")

    # ============ MÉTODOS DE TRANSACCIÓN ============

    def commit(self, connection):
        """
        Confirma una transacción en la conexión especificada

        Args:
            connection: Objeto de conexión a PostgreSQL

        Returns:
            bool: True si se confirmó exitosamente, False en caso contrario
        """
        if not connection or connection.closed:
            print("✗ No se puede confirmar: conexión cerrada o inválida")
            return False

        try:
            connection.commit()
            return True
        except Exception as e:
            print(f"✗ Error confirmando transacción: {e}")
            return False

    def rollback(self, connection):
        """
        Revierte una transacción en la conexión especificada

        Args:
            connection: Objeto de conexión a PostgreSQL

        Returns:
            bool: True si se revirtió exitosamente, False en caso contrario
        """
        if not connection or connection.closed:
            print("✗ No se puede revertir: conexión cerrada o inválida")
            return False

        try:
            connection.rollback()
            return True
        except Exception as e:
            print(f"✗ Error revirtiendo transacción: {e}")
            return False

    def begin_transaction(self, connection):
        """
        Inicia una transacción explícita

        Args:
            connection: Objeto de conexión a PostgreSQL

        Returns:
            bool: True si se inició exitosamente, False en caso contrario
        """
        if not connection or connection.closed:
            print("✗ No se puede iniciar transacción: conexión cerrada o inválida")
            return False

        try:
            # En PostgreSQL, BEGIN se inicia automáticamente con la primera consulta
            # cuando autocommit=False, pero podemos ejecutarlo explícitamente
            connection.cursor().execute("BEGIN")
            return True
        except Exception as e:
            print(f"✗ Error iniciando transacción: {e}")
            return False

    # ============ MÉTODOS DE CONSULTA ============

    def execute_query(
        self,
        query,
        params=None,
        connection=None,
        commit=True,
        fetch=True,
        dict_cursor=True,
    ):
        """
        Ejecuta una consulta SQL

        Args:
            query (str): Consulta SQL a ejecutar
            params (tuple/list): Parámetros para la consulta
            connection: Conexión a usar (si es None, obtiene una nueva)
            commit (bool): Si es True, confirma la transacción automáticamente
            fetch (bool): Si es True, retorna resultados (para SELECT)
            dict_cursor (bool): Si es True, retorna resultados como diccionarios

        Returns:
            Resultados de la consulta o None en caso de error
        """
        own_connection = False
        cursor = None

        try:
            # Obtener conexión si no se proporciona
            if connection is None:
                connection = self.get_connection()
                own_connection = True

            if connection is None or connection.closed:
                print("✗ No hay conexión disponible")
                return None

            # Crear cursor
            if dict_cursor:
                cursor = connection.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = connection.cursor()

            # Ejecutar consulta
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Procesar resultados
            if fetch and cursor.description:
                results = cursor.fetchall()
            else:
                results = cursor.rowcount

            # Confirmar transacción si es necesario
            if commit and own_connection:
                connection.commit()

            return results

        except Exception as e:
            print(f"✗ Error ejecutando consulta: {e}")
            print(f"  Consulta: {query}")

            # Revertir en caso de error
            if connection and not connection.closed and own_connection:
                try:
                    connection.rollback()
                except:
                    pass

            return None

        finally:
            # Cerrar cursor
            if cursor:
                try:
                    cursor.close()
                except:
                    pass

            # Devolver conexión al pool si era propia
            if own_connection and connection:
                self.return_connection(connection)

    # ============ MÉTODOS DE CONFIGURACIÓN ============

    def get_db_config(self):
        """Obtiene la configuración de la base de datos"""
        return self._config.copy() if self._config else {}

    def test_connection(self):
        """Prueba la conexión a la base de datos"""
        connection = None
        try:
            connection = self.get_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("SELECT version(), current_database(), current_user")
                result = cursor.fetchone()
                cursor.close()

                print("✓ Conexión a PostgreSQL exitosa:")
                print(f"  Versión: {result[0]}")
                print(f"  Base de datos: {result[1]}")
                print(f"  Usuario: {result[2]}")

                self.return_connection(connection)
                return True

        except Exception as e:
            print(f"✗ Error probando conexión: {e}")
            if connection:
                self.return_connection(connection)

        return False

    def get_database_info(self):
        """Obtiene información detallada de la base de datos"""
        try:
            query = """
            SELECT 
                (SELECT COUNT(*) FROM estudiantes) as total_estudiantes,
                (SELECT COUNT(*) FROM docentes) as total_docentes,
                (SELECT COUNT(*) FROM cursos) as total_cursos,
                (SELECT COUNT(*) FROM programas) as total_programas,
                (SELECT COUNT(*) FROM departamentos) as total_departamentos,
                version() as postgres_version,
                pg_database_size(current_database()) as database_size_bytes
            """

            result = self.execute_query(query, commit=False)
            if result:
                info = result[0]
                info["database_size_mb"] = round(
                    info["database_size_bytes"] / (1024 * 1024), 2
                )
                return info

        except Exception as e:
            print(f"✗ Error obteniendo información de BD: {e}")

        return None


# ============ FUNCIONES DE FÁCIL ACCESO ============


def get_connection():
    """Obtiene una conexión a la base de datos"""
    return DatabaseConnection().get_connection()


def return_connection(connection):
    """Devuelve una conexión al pool"""
    DatabaseConnection().return_connection(connection)


def execute_query(query, params=None, commit=True, fetch=True, dict_cursor=True):
    """Ejecuta una consulta SQL"""
    return DatabaseConnection().execute_query(
        query, params, None, commit, fetch, dict_cursor
    )


def commit(connection):
    """Confirma una transacción"""
    return DatabaseConnection().commit(connection)


def rollback(connection):
    """Revierte una transacción"""
    return DatabaseConnection().rollback(connection)


def begin_transaction(connection):
    """Inicia una transacción explícita"""
    return DatabaseConnection().begin_transaction(connection)


def get_db_config():
    """Obtiene la configuración de la base de datos"""
    return DatabaseConnection().get_db_config()


def test_connection():
    """Prueba la conexión a la base de datos"""
    return DatabaseConnection().test_connection()


def get_database_info():
    """Obtiene información de la base de datos"""
    return DatabaseConnection().get_database_info()


def close_all_connections():
    """Cierra todas las conexiones"""
    DatabaseConnection().close_all_connections()


# Prueba de conexión al importar el módulo
if __name__ == "__main__":
    print("=" * 50)
    print("Probando conexión a base de datos...")
    print("=" * 50)

    if test_connection():
        print("\n✓ Todas las funciones de conexión están operativas")

        # Obtener información adicional
        info = get_database_info()
        if info:
            print("\nInformación de la base de datos:")
            print(f"  Estudiantes: {info['total_estudiantes']}")
            print(f"  Docentes: {info['total_docentes']}")
            print(f"  Cursos: {info['total_cursos']}")
            print(f"  Tamaño de BD: {info['database_size_mb']} MB")
    else:
        print("\n✗ Hay problemas con la conexión a la base de datos")

    print("=" * 50)
