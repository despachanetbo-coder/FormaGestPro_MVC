# app/models/base_model.py
"""
Clase base para todos los modelos usando SQLite3 directamente.
"""
import logging
from typing import List, Dict, Any, Optional
from database import db

logger = logging.getLogger(__name__)

class BaseModel:
    """
    Clase base abstracta para todos los modelos.
    Proporciona operaciones CRUD básicas usando SQLite3.
    """
    
    # Debe ser definido por cada modelo hijo
    TABLE_NAME = None
    
    def __init__(self, **kwargs):
        """Inicializa el modelo con los datos proporcionados"""
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def save(self) -> int:
        """
        Guarda el objeto en la base de datos.
        Si tiene 'id', actualiza; si no, inserta.
        
        Returns:
            ID del objeto guardado
        """
        if hasattr(self, 'id') and self.id:
            return self.update()
        else:
            return self.insert()
    
    def insert(self) -> int:
        """Inserta el objeto en la base de datos y devuelve el ID generado"""
        if not self.TABLE_NAME:
            raise ValueError("TABLE_NAME no está definido en el modelo")
        
        # Obtener atributos del objeto
        attributes = self._get_attributes()
        
        # Si hay 'id', eliminarlo para que la BD lo genere automáticamente
        if 'id' in attributes:
            del attributes['id']
        
        columns = ', '.join(attributes.keys())
        placeholders = ', '.join(['?' for _ in attributes])
        query = f"INSERT INTO {self.TABLE_NAME} ({columns}) VALUES ({placeholders})"
        
        cursor = db.execute(query, tuple(attributes.values()))
        self.id = cursor.lastrowid
        logger.info(f"✅ Insertado en {self.TABLE_NAME} con ID: {self.id}")
        return self.id
    
    def update(self) -> int:
        """Actualiza el objeto en la base de datos"""
        if not self.TABLE_NAME:
            raise ValueError("TABLE_NAME no está definido en el modelo")
        
        if not hasattr(self, 'id') or not self.id:
            raise ValueError("El objeto no tiene 'id', no se puede actualizar")
        
        attributes = self._get_attributes()
        
        # No actualizar el 'id'
        if 'id' in attributes:
            del attributes['id']
        
        set_clause = ', '.join([f"{col} = ?" for col in attributes.keys()])
        query = f"UPDATE {self.TABLE_NAME} SET {set_clause} WHERE id = ?"
        
        params = tuple(attributes.values()) + (self.id,)
        db.execute(query, params)
        logger.info(f"✅ Actualizado en {self.TABLE_NAME} con ID: {self.id}")
        return self.id
    
    def delete(self) -> bool:
        """Elimina el objeto de la base de datos"""
        if not self.TABLE_NAME:
            raise ValueError("TABLE_NAME no está definido en el modelo")
        
        if not hasattr(self, 'id') or not self.id:
            raise ValueError("El objeto no tiene 'id', no se puede eliminar")
        
        query = f"DELETE FROM {self.TABLE_NAME} WHERE id = ?"
        db.execute(query, (self.id,))
        logger.info(f"✅ Eliminado de {self.TABLE_NAME} con ID: {self.id}")
        return True
    
    def _get_attributes(self) -> Dict[str, Any]:
        """Obtiene los atributos del objeto para operaciones de BD"""
        attributes = {}
        for key, value in self.__dict__.items():
            # Ignorar atributos privados y métodos
            if not key.startswith('_') and not callable(value):
                attributes[key] = value
        return attributes
    
    @classmethod
    def find_by_id(cls, id: int) -> Optional['BaseModel']:
        """Busca un objeto por su ID"""
        if not cls.TABLE_NAME:
            raise ValueError("TABLE_NAME no está definido en el modelo")
        
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE id = ?"
        row = db.fetch_one(query, (id,))
        
        if row:
            return cls(**row)
        return None
    
    @classmethod
    def all(cls) -> List['BaseModel']:
        """Devuelve todos los objetos de la tabla"""
        if not cls.TABLE_NAME:
            raise ValueError("TABLE_NAME no está definido en el modelo")
        
        query = f"SELECT * FROM {cls.TABLE_NAME}"
        rows = db.fetch_all(query)
        
        return [cls(**row) for row in rows]
    
    @classmethod
    def count(cls) -> int:
        """Cuenta el número de registros en la tabla"""
        if not cls.TABLE_NAME:
            raise ValueError("TABLE_NAME no está definido en el modelo")
        
        query = f"SELECT COUNT(*) as count FROM {cls.TABLE_NAME}"
        result = db.fetch_one(query)
        
        return result['count'] if result else 0
    
    @classmethod
    def table_exists(cls) -> bool:
        """Verifica si la tabla existe en la base de datos"""
        return db.table_exists(cls.TABLE_NAME)
    
    @classmethod
    def get_schema(cls) -> List[Dict[str, Any]]:
        """Obtiene el esquema de la tabla"""
        if not cls.TABLE_NAME:
            raise ValueError("TABLE_NAME no está definido en el modelo")
        
        return db.get_table_schema(cls.TABLE_NAME)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a un diccionario"""
        return self._get_attributes()
    
    def __repr__(self) -> str:
        """Representación del objeto"""
        return f"<{self.__class__.__name__} id={getattr(self, 'id', 'None')}>"
    
    # En models/base_model.py, añade este método a la clase BaseModel:
    @classmethod
    def update_by_id(cls, id: int, data: dict) -> bool:
        """
        Actualiza un registro por su ID usando un diccionario de datos.

        Args:
            id: ID del registro a actualizar
            data: Diccionario con los campos a actualizar

        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        if not cls.TABLE_NAME:
            raise ValueError("TABLE_NAME no está definido en el modelo")

        if not id or not data:
            return False

        # Filtrar campos que no existen en la tabla (opcional)
        # Obtenemos el esquema de la tabla
        try:
            schema = db.get_table_schema(cls.TABLE_NAME)
            valid_columns = [col['name'] for col in schema]

            # Filtrar solo columnas válidas
            filtered_data = {k: v for k, v in data.items() if k in valid_columns}
        except:
            # Si no podemos obtener el esquema, usamos todos los datos
            filtered_data = data

        if not filtered_data:
            return False

        # Preparar la cláusula SET
        set_clause = ', '.join([f"{key} = ?" for key in filtered_data.keys()])
        query = f"UPDATE {cls.TABLE_NAME} SET {set_clause} WHERE id = ?"

        # Preparar los parámetros
        params = tuple(filtered_data.values()) + (id,)

        try:
            db.execute(query, params)
            logger.info(f"✅ Actualizado en {cls.TABLE_NAME} con ID: {id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error al actualizar en {cls.TABLE_NAME}: {e}")
            return False
        
    @classmethod
    def get_all(cls):
        """Obtener todos los registros"""
        from database.database import db
        
        query = f"SELECT * FROM {cls.TABLE_NAME}"
        rows = db.fetch_all(query)
        return [cls(**row) for row in rows]