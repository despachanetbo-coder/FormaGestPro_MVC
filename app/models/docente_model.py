# app/models/docente_model.py
"""
Modelo Docente usando SQLite3 directamente.
"""
import logging
from typing import Any, List, Dict, Optional
from datetime import datetime, date
from .base_model import BaseModel

logger = logging.getLogger(__name__)

class DocenteModel(BaseModel):
    """Modelo que representa a un docente/tutor"""
    
    TABLE_NAME = "docentes"
    
    # Lista de expediciones válidas para CI
    EXPEDICIONES_VALIDAS = ['BE', 'CH', 'CB', 'LP', 'OR', 'PD', 'PT', 'SC', 'TJ', 'EX']
    
    # Grados académicos válidos
    GRADOS_VALIDOS = ['Mtr.', 'Mgtr.', 'Mag.', 'MBA', 'MSc', 'M.Sc.', 'PhD.', 'Dr.', 'Dra.']
    
    def __init__(self, **kwargs):
        """
        Inicializa un docente.
        
        Campos esperados (según esquema de BD):
            ci_numero, ci_expedicion, nombres, apellidos, fecha_nacimiento,
            max_grado_academico, telefono, email, curriculum_path,
            especialidad, honorario_hora, activo, created_at
        """
        # Campos obligatorios
        self.ci_numero = kwargs.get('ci_numero')
        self.ci_expedicion = kwargs.get('ci_expedicion')
        self.nombres = kwargs.get('nombres')
        self.apellidos = kwargs.get('apellidos')
        
        # Campos opcionales
        self.fecha_nacimiento = kwargs.get('fecha_nacimiento')
        self.max_grado_academico = kwargs.get('max_grado_academico')
        self.telefono = kwargs.get('telefono')
        self.email = kwargs.get('email')
        self.curriculum_path = kwargs.get('curriculum_path')
        self.especialidad = kwargs.get('especialidad')
        self.honorario_hora = kwargs.get('honorario_hora', 0.0)
        self.activo = kwargs.get('activo', 1)
        self.created_at = kwargs.get('created_at', datetime.now().isoformat())
        
        # ID (si viene de la base de datos)
        if 'id' in kwargs:
            self.id = kwargs['id']
        
        # Validaciones básicas
        self._validar()
    
    def _validar(self):
        """Valida los datos del docente"""
        if not self.ci_numero or not self.nombres or not self.apellidos:
            raise ValueError("CI, nombres y apellidos son obligatorios")
        
        if self.ci_expedicion and self.ci_expedicion not in self.EXPEDICIONES_VALIDAS:
            raise ValueError(f"Expedición de CI inválida. Válidas: {self.EXPEDICIONES_VALIDAS}")
        
        if self.max_grado_academico and self.max_grado_academico not in self.GRADOS_VALIDOS:
            raise ValueError(f"Grado académico inválido. Válidos: {self.GRADOS_VALIDOS}")
        
        if self.honorario_hora and self.honorario_hora < 0:
            raise ValueError("El honorario por hora no puede ser negativo")
        
        if self.email:
            # Validación simple de email
            if '@' not in self.email or '.' not in self.email.split('@')[-1]:
                raise ValueError("Formato de email inválido")
    
    def __repr__(self):
        return f"<Docente {self.ci_numero}: {self.nombres} {self.apellidos}>"
    
    @property
    def nombre_completo(self) -> str:
        """Devuelve el nombre completo del docente"""
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def obtener_grado_completo(self) -> str:
        """Devuelve el grado académico completo"""
        if self.max_grado_academico:
            return f"{self.max_grado_academico} {self.nombre_completo}"
        return self.nombre_completo
    
    @property
    def edad(self) -> Optional[int]:
        """Calcula la edad del docente"""
        if not self.fecha_nacimiento:
            return None
        
        try:
            if isinstance(self.fecha_nacimiento, str):
                nacimiento = datetime.strptime(self.fecha_nacimiento, '%Y-%m-%d').date()
            else:
                nacimiento = self.fecha_nacimiento
            
            hoy = date.today()
            edad = hoy.year - nacimiento.year
            
            # Ajustar si aún no ha pasado el cumpleaños este año
            if (hoy.month, hoy.day) < (nacimiento.month, nacimiento.day):
                edad -= 1
            
            return edad
        except (ValueError, AttributeError):
            return None
    
    @staticmethod
    def contar_total():
        """Contar el total de docentes registrados"""
        try:
            from database.database import db
            
            query = "SELECT COUNT(*) as total FROM docentes"
            resultado = db.fetch_one(query)
            return resultado['total'] if resultado else 0
            
        except Exception as e:
            print(f"❌ Error contando docentes: {e}")
            return 0
    
    def activar(self):
        """Activa al docente"""
        self.activo = 1
        return self.save()
    
    def desactivar(self):
        """Desactiva al docente"""
        self.activo = 0
        return self.save()
    
    @classmethod
    def crear_docente(cls, datos: Dict) -> 'DocenteModel':
        """Crea un nuevo docente con validaciones"""
        # Validaciones específicas
        if 'ci_numero' not in datos or not datos['ci_numero']:
            raise ValueError("El número de CI es obligatorio")
        
        # Verificar que el CI no exista
        existente = cls.buscar_por_ci(datos['ci_numero'], datos.get('ci_expedicion'))
        if existente:
            raise ValueError(f"Ya existe un docente con CI {datos['ci_numero']}")
        
        # Crear y guardar
        docente = cls(**datos)
        docente.save()
        return docente
    
    @classmethod
    def buscar_por_ci(cls, ci_numero: str, ci_expedicion: str = None) -> Optional['DocenteModel']:
        """Busca un docente por su CI"""
        from database import db
        
        if ci_expedicion:
            query = f"SELECT * FROM {cls.TABLE_NAME} WHERE ci_numero = ? AND ci_expedicion = ?"
            params = (ci_numero, ci_expedicion)
        else:
            query = f"SELECT * FROM {cls.TABLE_NAME} WHERE ci_numero = ?"
            params = (ci_numero,)
        
        row = db.fetch_one(query, params)
        return cls(**row) if row else None
    
    @classmethod
    def buscar_por_especialidad(cls, especialidad: str) -> List['DocenteModel']:
        """Busca docentes por especialidad"""
        from database import db
        
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE especialidad LIKE ? AND activo = 1"
        param = f"%{especialidad}%"
        rows = db.fetch_all(query, (param,))
        
        return [cls(**row) for row in rows]
    
    @classmethod
    def buscar_activos(cls) -> List['DocenteModel']:
        """Busca docentes activos"""
        from database import db
        
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE activo = 1"
        rows = db.fetch_all(query)
        
        return [cls(**row) for row in rows]
    
    @classmethod
    def obtener_estadisticas(cls) -> Dict[str, Any]:
        """Obtiene estadísticas de docentes"""
        from database import db
        
        query_total = f"SELECT COUNT(*) as total FROM {cls.TABLE_NAME}"
        query_activos = f"SELECT COUNT(*) as activos FROM {cls.TABLE_NAME} WHERE activo = 1"
        query_honorario = f"""
        SELECT 
            AVG(honorario_hora) as promedio_honorario,
            MIN(honorario_hora) as minimo_honorario,
            MAX(honorario_hora) as maximo_honorario
        FROM {cls.TABLE_NAME} 
        WHERE honorario_hora > 0
        """
        
        total = db.fetch_one(query_total)['total']
        activos = db.fetch_one(query_activos)['activos']
        honorarios = db.fetch_one(query_honorario)
        
        return {
            'total_docentes': total,
            'docentes_activos': activos,
            'docentes_inactivos': total - activos,
            'promedio_honorario_hora': honorarios['promedio_honorario'] if honorarios else 0,
            'minimo_honorario_hora': honorarios['minimo_honorario'] if honorarios else 0,
            'maximo_honorario_hora': honorarios['maximo_honorario'] if honorarios else 0
        }
    
    def delete(self):
        """Elimina el docente de la base de datos"""
        from database import db
        
        if not hasattr(self, 'id') or not self.id:
            return False
        
        try:
            query = f"DELETE FROM {self.TABLE_NAME} WHERE id = ?"
            result = db.execute(query, (self.id,))
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error eliminando docente {self.id}: {e}")
            return False
    
    @classmethod
    def find_by_id(cls, docente_id):
        """Busca un docente por su ID"""
        from database import db
        
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE id = ?"
        row = db.fetch_one(query, (docente_id,))
        return cls(**row) if row else None