# app/models/base_model.py - Versión corregida
from datetime import datetime
import sys
import os
from typing import Any, Dict, Optional, Tuple, Union

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from app.database.connection import DatabaseConnection
import threading

import logging

logger = logging.getLogger(__name__)


class BaseModel:
    """Clase base para todos los modelos que maneja la conexión a la base de datos"""

    # Pool de conexiones para mejor rendimiento
    _connection_pool = None
    _pool_lock = threading.Lock()

    @classmethod
    def _get_connection_pool(cls):
        """Obtiene o crea el pool de conexiones"""
        if cls._connection_pool is None:
            with cls._pool_lock:
                if cls._connection_pool is None:  # Double-check locking
                    try:
                        config = DatabaseConnection.get_connection
                        cls._connection_pool = pool.SimpleConnectionPool(
                            minconn=1,
                            maxconn=10,
                            host=config.get("host", "localhost"),
                            database=config.get("database"),
                            user=config.get("user"),
                            password=config.get("password"),
                            port=config.get("port", 5432),
                        )
                        print("✓ Pool de conexiones a PostgreSQL creado exitosamente")
                    except Exception as e:
                        print(f"✗ Error creando pool de conexiones: {e}")
                        cls._connection_pool = None
        return cls._connection_pool

    @classmethod
    def get_connection(cls):
        """Obtiene una conexión del pool"""
        pool = cls._get_connection_pool()
        if pool:
            try:
                connection = pool.getconn()
                return connection
            except Exception as e:
                print(f"✗ Error obteniendo conexión del pool: {e}")
                return None
        return None

    @classmethod
    def return_connection(cls, connection):
        """Devuelve una conexión al pool"""
        pool = cls._get_connection_pool()
        if pool and connection:
            try:
                pool.putconn(connection)
            except Exception as e:
                print(f"✗ Error devolviendo conexión al pool: {e}")

    @classmethod
    def close_all_connections(cls):
        """Cierra todas las conexiones del pool"""
        if cls._connection_pool:
            try:
                cls._connection_pool.closeall()
                print("✓ Todas las conexiones del pool cerradas")
            except Exception as e:
                print(f"✗ Error cerrando conexiones del pool: {e}")

    def __init__(self):
        """Inicializa el modelo base con una conexión a la base de datos"""
        self.connection = None
        self.cursor = None
        self._connect()

    def __del__(self):
        """Limpia recursos al destruir el objeto"""
        self._close()

    def _connect(self):
        """Establece la conexión a la base de datos"""
        try:
            self.connection = self.get_connection()
            if self.connection:
                # Configurar autocommit como False para manejar transacciones manualmente
                self.connection.autocommit = False
                print(
                    f"✓ Conexión a base de datos establecida para {self.__class__.__name__}"
                )
            else:
                print(
                    f"✗ No se pudo establecer conexión para {self.__class__.__name__}"
                )
        except Exception as e:
            print(f"✗ Error conectando a la base de datos: {e}")
            self.connection = None

    def _close(self):
        """Cierra la conexión y cursor"""
        try:
            if self.cursor and not self.cursor.closed:
                self.cursor.close()

            if self.connection:
                self.return_connection(self.connection)

        except Exception as e:
            print(f"✗ Error cerrando recursos: {e}")
        finally:
            self.cursor = None
            self.connection = None

    def _get_cursor(self, dict_cursor=False):
        """Obtiene un cursor nuevo"""
        if not self.connection:
            self._connect()
            if not self.connection:
                return None

        try:
            if dict_cursor:
                self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            else:
                self.cursor = self.connection.cursor()
            return self.cursor
        except Exception as e:
            print(f"✗ Error obteniendo cursor: {e}")
            return None

    def execute_query(
        self, query, params=None, fetch=True, commit=False, dict_cursor=True
    ):
        """
        Ejecuta una consulta SQL de forma segura

        Args:
            query (str): Consulta SQL a ejecutar
            params (tuple/list): Parámetros para la consulta
            fetch (bool): Si es True, retorna resultados (para SELECT)
            commit (bool): Si es True, hace commit de la transacción
            dict_cursor (bool): Si es True, retorna resultados como diccionarios

        Returns:
            - Para SELECT: Lista de diccionarios o tuplas con resultados
            - Para INSERT/UPDATE/DELETE: Número de filas afectadas
            - Para INSERT con RETURNING: El valor retornado
            - None en caso de error
        """
        cursor = None
        try:
            # Obtener cursor
            cursor = self._get_cursor(dict_cursor)
            if not cursor:
                return None

            # Ejecutar consulta
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Procesar resultados
            if fetch and cursor.description:  # Es un SELECT que retorna datos
                results = cursor.fetchall()

                if dict_cursor:
                    return results  # Ya son diccionarios por RealDictCursor
                else:
                    # Convertir a lista de diccionarios
                    columns = [desc[0] for desc in cursor.description]
                    return [dict(zip(columns, row)) for row in results]

            elif fetch:  # Es un INSERT/UPDATE/DELETE con RETURNING
                try:
                    result = cursor.fetchone()
                    if result:
                        # Si es diccionario, extraer el valor
                        if isinstance(result, dict) and len(result) == 1:
                            return list(result.values())[0]
                        return result
                except:
                    pass

                # Retornar número de filas afectadas
                rowcount = cursor.rowcount

                if commit:
                    self.commit()

                return rowcount

            else:  # No fetch
                rowcount = cursor.rowcount

                if commit:
                    self.commit()

                return rowcount

        except Exception as e:
            print(f"✗ Error ejecutando consulta: {e}")
            print(f"  Consulta: {query}")
            if params:
                print(f"  Parámetros: {params}")

            # Rollback en caso de error
            if self.connection:
                try:
                    self.connection.rollback()
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
                self.cursor = None

    # ============ MÉTODOS CONVENCIONALES ============

    def fetch_one(self, query, params=None, dict_cursor=True):
        """
        Ejecuta una consulta y retorna solo el primer resultado
        """
        results = self.execute_query(query, params, fetch=True, dict_cursor=dict_cursor)
        return results[0] if results else None

    def fetch_all(self, query, params=None, dict_cursor=True):
        """
        Ejecuta una consulta y retorna todos los resultados
        """
        return self.execute_query(query, params, fetch=True, dict_cursor=dict_cursor)

    def fetch_scalar(self, query, params=None):
        """
        Ejecuta una consulta y retorna un solo valor escalar
        """
        result = self.fetch_one(query, params, dict_cursor=False)
        if result:
            return list(result.values())[0] if isinstance(result, dict) else result[0]
        return None

    # ============ MÉTODOS CRUD BÁSICOS ============

    def insert(self, table, data, returning="id"):
        """
        Inserta un registro en una tabla

        Args:
            table (str): Nombre de la tabla
            data (dict): Datos a insertar (columna: valor)
            returning (str): Columna a retornar después del INSERT

        Returns:
            Valor de la columna returning o None en caso de error
        """
        if not data:
            return None

        try:
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            values = tuple(data.values())

            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

            if returning:
                query += f" RETURNING {returning}"

            return self.execute_query(query, values, fetch=True, commit=True)

        except Exception as e:
            print(f"✗ Error insertando en tabla {table}: {e}")
            return None

    def update(self, table, data, condition, params=None):
        """
        Actualiza registros en una tabla

        Args:
            table (str): Nombre de la tabla
            data (dict): Datos a actualizar (columna: valor)
            condition (str): Condición WHERE
            params (tuple/list): Parámetros adicionales para la condición

        Returns:
            Número de filas afectadas o None en caso de error
        """
        if not data:
            return 0

        try:
            set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
            set_values = tuple(data.values())

            query = f"UPDATE {table} SET {set_clause} WHERE {condition}"

            # Combinar parámetros
            if params:
                all_params = set_values + tuple(params)
            else:
                all_params = set_values

            return self.execute_query(query, all_params, fetch=False, commit=True)

        except Exception as e:
            print(f"✗ Error actualizando tabla {table}: {e}")
            return None

    def delete(self, table, condition, params=None):
        """
        Elimina registros de una tabla

        Args:
            table (str): Nombre de la tabla
            condition (str): Condición WHERE
            params (tuple/list): Parámetros para la condición

        Returns:
            Número de filas afectadas o None en caso de error
        """
        try:
            query = f"DELETE FROM {table} WHERE {condition}"
            return self.execute_query(query, params, fetch=False, commit=True)

        except Exception as e:
            print(f"✗ Error eliminando de tabla {table}: {e}")
            return None

    # ============ MÉTODOS DE TRANSACCIÓN ============

    def begin_transaction(self):
        """Inicia una transacción"""
        try:
            if self.connection:
                self.connection.autocommit = False
                return True
        except Exception as e:
            print(f"✗ Error iniciando transacción: {e}")
        return False

    def commit(self):
        """Confirma la transacción actual"""
        try:
            if self.connection:
                self.connection.commit()
                return True
        except Exception as e:
            print(f"✗ Error confirmando transacción: {e}")
        return False

    def rollback(self):
        """Revierte la transacción actual"""
        try:
            if self.connection:
                self.connection.rollback()
                return True
        except Exception as e:
            print(f"✗ Error revirtiendo transacción: {e}")
        return False

    # ============ MÉTODOS DE METADATOS ============

    def table_exists(self, table_name):
        """Verifica si una tabla existe"""
        try:
            query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            )
            """
            result = self.fetch_scalar(query, (table_name,))
            return bool(result)
        except Exception as e:
            print(f"✗ Error verificando existencia de tabla {table_name}: {e}")
            return False

    def get_table_columns(self, table_name):
        """Obtiene las columnas de una tabla"""
        try:
            query = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = %s 
            ORDER BY ordinal_position
            """
            results = self.fetch_all(query, (table_name,))
            return [row["column_name"] for row in results] if results else []
        except Exception as e:
            print(f"✗ Error obteniendo columnas de tabla {table_name}: {e}")
            return []

    def get_last_insert_id(self, sequence_name=None):
        """Obtiene el último ID insertado"""
        try:
            if sequence_name:
                query = f"SELECT last_value FROM {sequence_name}"
            else:
                query = "SELECT lastval()"

            return self.fetch_scalar(query)
        except Exception as e:
            print(f"✗ Error obteniendo último ID: {e}")
            return None

    def update_table(
        self,
        table: str,
        data: Dict[str, Any],
        condition: str,
        params: Tuple = None,  # type:ignore
        returning: str = None,  # type:ignore
        auto_timestamp: bool = True,
    ) -> Optional[Union[int, Any]]:
        """
        Actualiza registros en una tabla con funcionalidades avanzadas

        Args:
            table (str): Nombre de la tabla
            data (dict): Diccionario con datos a actualizar {columna: valor}
            condition (str): Condición WHERE (sin la palabra WHERE)
            params (tuple/list): Parámetros para la condición WHERE
            returning (str): Columna a retornar después del UPDATE
            auto_timestamp (bool): Si es True, agrega/actualiza campo updated_at

        Returns:
            - Si returning=None: Número de filas afectadas
            - Si returning=columna: Valor de la columna
            - None en caso de error

        Ejemplos:
            # Actualizar sin retorno
            filas = model.update_table(
                table="estudiantes",
                data={"nombre": "Juan"},
                condition="id = %s",
                params=(1,)
            )

            # Actualizar con retorno del ID
            estudiante_id = model.update_table(
                table="estudiantes",
                data={"nombre": "Juan"},
                condition="id = %s",
                params=(1,),
                returning="id"
            )
        """
        if not data:
            return 0

        try:
            # Agregar timestamp de actualización si está habilitado
            if auto_timestamp:
                # Verificar si la tabla tiene columna updated_at
                columns = self.get_table_columns(table)
                if "updated_at" in columns:
                    data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Preparar SET clause
            set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
            set_values = tuple(data.values())

            # Construir consulta
            query = f"UPDATE {table} SET {set_clause} WHERE {condition}"

            # Agregar RETURNING si se especifica
            if returning:
                query += f" RETURNING {returning}"

            # Combinar parámetros
            if params:
                all_params = set_values + tuple(params)
            else:
                all_params = set_values

            # Ejecutar consulta
            if returning:
                # Si hay RETURNING, necesitamos fetch=True
                result = self.execute_query(query, all_params, fetch=True, commit=True)
                if result:
                    # Extraer el valor retornado
                    if isinstance(result, list) and len(result) > 0:
                        row = result[0]
                        if isinstance(row, dict):
                            return row.get(returning)
                        elif isinstance(row, tuple) and len(row) > 0:
                            return row[0]
                    elif isinstance(result, dict):
                        return result.get(returning)
                return None
            else:
                # Sin RETURNING, solo número de filas afectadas
                result = self.execute_query(query, all_params, fetch=False, commit=True)
                return result

        except Exception as e:
            logger.error(f"✗ Error en update_table para tabla {table}: {e}")
            logger.error(f"  Consulta: {query}")
            if params:
                logger.error(f"  Parámetros: {all_params}")

            # Rollback en caso de error
            if self.connection:
                try:
                    self.connection.rollback()
                except:
                    pass
            return None
