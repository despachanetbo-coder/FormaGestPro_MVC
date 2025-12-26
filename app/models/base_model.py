# app/models/base_model.py
"""
Base Model optimizado para PostgreSQL - FormaGestPro
Reemplaza SQLite por PostgreSQL manteniendo compatibilidad con código existente.
"""

import logging
import json
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime

from app.database.connection import db  # Conexión PostgreSQL centralizada

logger = logging.getLogger(__name__)


class BaseModel:
    """Clase base para todos los modelos usando PostgreSQL

    Mantiene compatibilidad con métodos existentes mientras migra de SQLite a PostgreSQL.
    """

    TABLE_NAME = ""  # Debe ser sobrescrito por cada modelo

    def __init__(self, **kwargs):
        # Campos base de auditoría
        self.id = kwargs.get("id")

        # Manejo flexible de fechas (ISO 8601 o timestamp string)
        created_at = kwargs.get("created_at")
        if isinstance(created_at, str):
            self.created_at = created_at
        else:
            self.created_at = created_at or datetime.now().isoformat()

        updated_at = kwargs.get("updated_at")
        if isinstance(updated_at, str):
            self.updated_at = updated_at
        else:
            self.updated_at = updated_at or datetime.now().isoformat()

        # Para compatibilidad con código existente
        self._fields = {}  # Diccionario interno para almacenar datos

    # ============================================================================
    # MÉTODOS CRUD PRINCIPALES (COMPATIBLES CON CÓDIGO EXISTENTE)
    # ============================================================================

    def save(self) -> Optional[int]:
        """
        Guarda el objeto en la base de datos.
        Si tiene id, actualiza; si no, inserta.

        Returns:
            int: ID del registro guardado, None en caso de error
        """
        try:
            if self.id:
                return self._update()
            else:
                return self._insert()
        except Exception as e:
            logger.error(f"❌ Error guardando {self.__class__.__name__}: {e}")
            return None

    def _insert(self) -> int:
        """Insertar nuevo registro en PostgreSQL"""
        data = self._prepare_insert_data()

        if not data:
            logger.warning(f"⚠️ No hay datos para insertar en {self.__class__.__name__}")
            return None

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))

        # PostgreSQL usa RETURNING id
        query = f"INSERT INTO {self.TABLE_NAME} ({columns}) VALUES ({placeholders}) RETURNING id"

        try:
            result = db.execute_query(query, tuple(data.values()), fetch=True)
            if result and len(result) > 0:
                self.id = result[0]["id"]
                logger.info(f"✅ {self.__class__.__name__} creado con ID: {self.id}")
                return self.id
        except Exception as e:
            logger.error(f"❌ Error en _insert para {self.__class__.__name__}: {e}")
            raise

        return None

    def _update(self) -> int:
        """Actualizar registro existente en PostgreSQL"""
        data = self._prepare_update_data()

        if not data:
            logger.debug(
                f"ℹ️ Sin cambios para actualizar en {self.__class__.__name__} ID: {self.id}"
            )
            return self.id

        set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
        query = f"UPDATE {self.TABLE_NAME} SET {set_clause} WHERE id = %s"
        params = tuple(data.values()) + (self.id,)

        try:
            db.execute_query(query, params, fetch=False)
            logger.info(f"✏️ {self.__class__.__name__} actualizado con ID: {self.id}")
            return self.id
        except Exception as e:
            logger.error(f"❌ Error en _update para {self.__class__.__name__}: {e}")
            raise

    def delete(self) -> bool:
        """
        Elimina el registro de la base de datos.

        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        if not self.id:
            logger.warning(f"⚠️ {self.__class__.__name__} no tiene ID para eliminar")
            return False

        query = f"DELETE FROM {self.TABLE_NAME} WHERE id = %s"
        try:
            db.execute_query(query, (self.id,), fetch=False)
            logger.info(f"🗑️ {self.__class__.__name__} eliminado con ID: {self.id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error eliminando {self.__class__.__name__}: {e}")
            return False

    # ============================================================================
    # MÉTODOS QUE DEBEN SER IMPLEMENTADOS POR MODELOS HIJO
    # ============================================================================

    def _prepare_insert_data(self) -> Dict:
        """
        Preparar datos para inserción.

        Returns:
            Dict: Diccionario con columnas y valores para INSERT
        """
        # Método base que puede ser usado por modelos simples
        data = {}
        for key, value in self.__dict__.items():
            if not key.startswith("_") and key not in [
                "id",
                "created_at",
                "updated_at",
            ]:
                if value is not None:
                    data[key] = value

        # Agregar timestamps si no están en el modelo
        if "created_at" not in data and hasattr(self, "created_at"):
            data["created_at"] = self.created_at
        if "updated_at" not in data and hasattr(self, "updated_at"):
            data["updated_at"] = self.updated_at

        return data

    def _prepare_update_data(self) -> Dict:
        """
        Preparar datos para actualización.

        Returns:
            Dict: Diccionario con columnas y valores para UPDATE
        """
        data = {}
        for key, value in self.__dict__.items():
            if not key.startswith("_") and key not in ["id", "created_at"]:
                if value is not None:
                    data[key] = value

        # Siempre actualizar updated_at
        data["updated_at"] = datetime.now().isoformat()

        return data

    # ============================================================================
    # MÉTODOS DE CONSULTA ESTÁTICOS (COMPATIBLES)
    # ============================================================================

    @classmethod
    def find_by_id(cls, id: int) -> Optional["BaseModel"]:
        """
        Busca un registro por su ID.

        Args:
            id (int): ID del registro a buscar

        Returns:
            BaseModel: Instancia del modelo o None si no se encuentra
        """
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE id = %s"
        result = db.fetch_one(query, (id,))
        return cls(**result) if result else None

    @classmethod
    def find_all(cls, limit: int = 100, offset: int = 0) -> List["BaseModel"]:
        """
        Obtiene todos los registros con paginación.

        Args:
            limit (int): Límite de registros
            offset (int): Desplazamiento para paginación

        Returns:
            List[BaseModel]: Lista de instancias del modelo
        """
        query = f"SELECT * FROM {cls.TABLE_NAME} ORDER BY id DESC LIMIT %s OFFSET %s"
        results = db.fetch_all(query, (limit, offset))
        return [cls(**row) for row in results]

    @classmethod
    def count(cls) -> int:
        """
        Cuenta el total de registros en la tabla.

        Returns:
            int: Número total de registros
        """
        query = f"SELECT COUNT(*) as total FROM {cls.TABLE_NAME}"
        result = db.fetch_one(query)
        return result["total"] if result else 0

    @classmethod
    def find_by_field(
        cls, field: str, value: Any, limit: int = 100
    ) -> List["BaseModel"]:
        """
        Busca registros por un campo específico.

        Args:
            field (str): Nombre del campo
            value (Any): Valor a buscar
            limit (int): Límite de resultados

        Returns:
            List[BaseModel]: Lista de instancias encontradas
        """
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE {field} = %s LIMIT %s"
        results = db.fetch_all(query, (value, limit))
        return [cls(**row) for row in results]

    @classmethod
    def search(
        cls, field: str, search_term: str, limit: int = 100
    ) -> List["BaseModel"]:
        """
        Búsqueda parcial (LIKE) en un campo.

        Args:
            field (str): Campo donde buscar
            search_term (str): Término de búsqueda
            limit (int): Límite de resultados

        Returns:
            List[BaseModel]: Lista de instancias encontradas
        """
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE {field} ILIKE %s LIMIT %s"
        results = db.fetch_all(query, (f"%{search_term}%", limit))
        return [cls(**row) for row in results]

    # ============================================================================
    # MÉTODOS DE UTILIDAD (COMPATIBLES)
    # ============================================================================

    def to_dict(self) -> Dict:
        """
        Convierte el modelo a diccionario.

        Returns:
            Dict: Diccionario con todos los atributos del modelo
        """
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                # Convertir objetos datetime a string para JSON
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                else:
                    result[key] = value
        return result

    def to_json(self) -> str:
        """
        Convierte el modelo a JSON.

        Returns:
            str: Representación JSON del modelo
        """
        return json.dumps(self.to_dict(), default=str, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict) -> "BaseModel":
        """
        Crea una instancia del modelo desde un diccionario.

        Args:
            data (Dict): Diccionario con datos del modelo

        Returns:
            BaseModel: Instancia del modelo
        """
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "BaseModel":
        """
        Crea una instancia del modelo desde JSON.

        Args:
            json_str (str): String JSON con datos del modelo

        Returns:
            BaseModel: Instancia del modelo
        """
        data = json.loads(json_str)
        return cls(**data)

    def exists(self) -> bool:
        """
        Verifica si el registro existe en la base de datos.

        Returns:
            bool: True si existe, False en caso contrario
        """
        if not self.id:
            return False

        query = f"SELECT EXISTS(SELECT 1 FROM {self.TABLE_NAME} WHERE id = %s)"
        result = db.fetch_one(query, (self.id,))
        return result["exists"] if result else False

    def refresh(self) -> bool:
        """
        Actualiza la instancia con los datos actuales de la base de datos.

        Returns:
            bool: True si se pudo actualizar, False en caso contrario
        """
        if not self.id:
            return False

        query = f"SELECT * FROM {self.TABLE_NAME} WHERE id = %s"
        result = db.fetch_one(query, (self.id,))

        if result:
            for key, value in result.items():
                setattr(self, key, value)
            return True

        return False

    # ============================================================================
    # MÉTODOS ESPECIALES
    # ============================================================================

    def __str__(self) -> str:
        """Representación en string legible del modelo."""
        return f"{self.__class__.__name__} (ID: {self.id})"

    def __repr__(self) -> str:
        """Representación oficial del modelo."""
        return f"<{self.__class__.__name__} id={self.id}>"

    def __eq__(self, other) -> bool:
        """Compara dos modelos por ID."""
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash del modelo basado en ID."""
        return hash((self.__class__.__name__, self.id))

    # ============================================================================
    # MÉTODOS PARA MIGRACIÓN DE SQLite (COMPATIBILIDAD)
    # ============================================================================

    @classmethod
    def execute_raw_query(cls, query: str, params: Tuple = None) -> List[Dict]:
        """
        Ejecuta una consulta SQL cruda (para migración o consultas complejas).

        Args:
            query (str): Consulta SQL
            params (Tuple): Parámetros para la consulta

        Returns:
            List[Dict]: Resultados de la consulta
        """
        try:
            return db.fetch_all(query, params)
        except Exception as e:
            logger.error(f"❌ Error en consulta cruda: {e}\nConsulta: {query}")
            return []

    @classmethod
    def execute_update(cls, query: str, params: Tuple = None) -> bool:
        """
        Ejecuta una consulta de actualización sin retorno.

        Args:
            query (str): Consulta SQL
            params (Tuple): Parámetros para la consulta

        Returns:
            bool: True si se ejecutó correctamente
        """
        try:
            db.execute_query(query, params, fetch=False)
            return True
        except Exception as e:
            logger.error(
                f"❌ Error en consulta de actualización: {e}\nConsulta: {query}"
            )
            return False

    @classmethod
    def get_table_info(cls) -> Dict:
        """
        Obtiene información de la tabla (columnas, tipos, etc.).

        Returns:
            Dict: Información de la tabla
        """
        query = """
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_name = %s AND table_schema = 'public'
            ORDER BY ordinal_position
        """
        results = db.fetch_all(query, (cls.TABLE_NAME,))

        info = {
            "table_name": cls.TABLE_NAME,
            "columns": results,
            "column_count": len(results),
        }

        return info

    @classmethod
    def backup_to_json(cls, filepath: str) -> bool:
        """
        Realiza un backup de la tabla a un archivo JSON.

        Args:
            filepath (str): Ruta del archivo JSON de salida

        Returns:
            bool: True si se realizó el backup correctamente
        """
        try:
            records = cls.find_all(limit=10000)  # Limitar para backups grandes
            data = [record.to_dict() for record in records]

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, default=str, ensure_ascii=False, indent=2)

            logger.info(
                f"✅ Backup realizado: {len(data)} registros guardados en {filepath}"
            )
            return True
        except Exception as e:
            logger.error(f"❌ Error en backup: {e}")
            return False
