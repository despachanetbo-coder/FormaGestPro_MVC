# app/models/base_model.py - Versión completa con execute_query
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_connection


class BaseModel:
    def __init__(self):
        """Inicializa el modelo base con conexión a la base de datos"""
        self.connection = get_connection()
        self.cursor = None

    def __del__(self):
        """Limpia recursos al destruir el objeto"""
        self.close_cursor()

    def close_cursor(self):
        """Cierra el cursor si está abierto"""
        if self.cursor:
            self.cursor.close()
            self.cursor = None

    def get_cursor(self):
        """Obtiene un cursor nuevo si no existe uno activo"""
        if self.cursor is None or self.cursor.closed:
            self.cursor = self.connection.cursor()
        return self.cursor

    def execute_query(self, query, params=None, fetch=True, commit=False):
        """
        Ejecuta una consulta SQL de forma segura

        Args:
            query (str): Consulta SQL a ejecutar
            params (tuple/list/dict): Parámetros para la consulta
            fetch (bool): Si es True, retorna resultados (para SELECT)
            commit (bool): Si es True, hace commit de la transacción

        Returns:
            - Para SELECT con fetch=True: Lista de diccionarios con resultados
            - Para SELECT con fetch=False: Cursor para procesamiento manual
            - Para INSERT/UPDATE/DELETE: Número de filas afectadas o ID si hay RETURNING
            - None en caso de error
        """
        cursor = None
        try:
            # Obtener cursor
            cursor = self.get_cursor()

            # Ejecutar consulta
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Commit si es necesario
            if commit:
                self.connection.commit()

            # Procesar resultados según el tipo de consulta
            if fetch and cursor.description:  # Es un SELECT que retorna datos
                # Obtener nombres de columnas
                columns = [desc[0] for desc in cursor.description]

                # Convertir resultados a lista de diccionarios
                results = cursor.fetchall()
                return [dict(zip(columns, row)) for row in results]

            elif (
                fetch and not cursor.description
            ):  # Es un SELECT que no retorna datos o es otra operación
                # Intentar obtener resultado si hay RETURNING
                try:
                    result = cursor.fetchone()
                    if result:
                        return result[0] if len(result) == 1 else result
                except:
                    pass

                # Retornar número de filas afectadas
                return cursor.rowcount

            else:  # No fetch, retornar cursor para procesamiento manual
                return cursor

        except Exception as e:
            print(f"Error ejecutando consulta: {e}")
            print(f"Consulta: {query}")
            print(f"Parámetros: {params}")

            # Rollback en caso de error
            if commit:
                try:
                    self.connection.rollback()
                except:
                    pass

            return None

        finally:
            # No cerrar cursor aquí si no se solicitó fetch, para permitir procesamiento posterior
            if fetch and cursor:
                cursor.close()
                self.cursor = None

    def fetch_one(self, query, params=None):
        """
        Ejecuta una consulta y retorna solo el primer resultado

        Args:
            query (str): Consulta SQL
            params (tuple/list/dict): Parámetros

        Returns:
            Diccionario con el primer resultado o None
        """
        results = self.execute_query(query, params, fetch=True)
        return results[0] if results else None

    def fetch_all(self, query, params=None):
        """
        Ejecuta una consulta y retorna todos los resultados

        Args:
            query (str): Consulta SQL
            params (tuple/list/dict): Parámetros

        Returns:
            Lista de diccionarios con resultados
        """
        return self.execute_query(query, params, fetch=True)

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

            result = self.execute_query(query, values, fetch=True, commit=True)

            if result:
                return (
                    result[0]
                    if isinstance(result, list) and len(result) == 1
                    else result
                )
            return None

        except Exception as e:
            print(f"Error insertando en tabla {table}: {e}")
            return None

    def update(self, table, data, where_condition, where_params=None):
        """
        Actualiza registros en una tabla

        Args:
            table (str): Nombre de la tabla
            data (dict): Datos a actualizar (columna: valor)
            where_condition (str): Condición WHERE
            where_params (tuple/list): Parámetros para la condición WHERE

        Returns:
            Número de filas afectadas o None en caso de error
        """
        if not data:
            return 0

        try:
            set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
            values = tuple(data.values())

            query = f"UPDATE {table} SET {set_clause} WHERE {where_condition}"

            # Combinar parámetros
            if where_params:
                params = values + tuple(where_params)
            else:
                params = values

            result = self.execute_query(query, params, fetch=False, commit=True)
            return result.rowcount if result else 0

        except Exception as e:
            print(f"Error actualizando tabla {table}: {e}")
            return None

    def delete(self, table, where_condition, where_params=None):
        """
        Elimina registros de una tabla

        Args:
            table (str): Nombre de la tabla
            where_condition (str): Condición WHERE
            where_params (tuple/list): Parámetros para la condición WHERE

        Returns:
            Número de filas afectadas o None en caso de error
        """
        try:
            query = f"DELETE FROM {table} WHERE {where_condition}"
            result = self.execute_query(query, where_params, fetch=False, commit=True)
            return result.rowcount if result else 0

        except Exception as e:
            print(f"Error eliminando de tabla {table}: {e}")
            return None

    def begin_transaction(self):
        """Inicia una transacción"""
        try:
            self.execute_query("BEGIN", commit=False)
            return True
        except Exception as e:
            print(f"Error iniciando transacción: {e}")
            return False

    def commit_transaction(self):
        """Confirma una transacción"""
        try:
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error confirmando transacción: {e}")
            return False

    def rollback_transaction(self):
        """Revierte una transacción"""
        try:
            self.connection.rollback()
            return True
        except Exception as e:
            print(f"Error revirtiendo transacción: {e}")
            return False

    def table_exists(self, table_name):
        """
        Verifica si una tabla existe en la base de datos

        Args:
            table_name (str): Nombre de la tabla

        Returns:
            bool: True si la tabla existe, False en caso contrario
        """
        try:
            query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            )
            """
            result = self.fetch_one(query, (table_name,))
            return result["exists"] if result else False
        except Exception as e:
            print(f"Error verificando existencia de tabla {table_name}: {e}")
            return False

    def get_table_columns(self, table_name):
        """
        Obtiene las columnas de una tabla

        Args:
            table_name (str): Nombre de la tabla

        Returns:
            Lista de nombres de columnas
        """
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
            print(f"Error obteniendo columnas de tabla {table_name}: {e}")
            return []
