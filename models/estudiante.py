# models/estudiante.py
"""
Modelo Estudiante usando SQLite3 directamente.
"""
import logging
from typing import Any, List, Dict, Optional
from datetime import datetime, date
from .base_model import BaseModel

logger = logging.getLogger(__name__)

class EstudianteModel(BaseModel):
    """Modelo que representa a un estudiante"""
    
    TABLE_NAME = "estudiantes"
    
    # Lista de expediciones válidas para CI
    EXPEDICIONES_VALIDAS = ['BE', 'CH', 'CB', 'LP', 'OR', 'PD', 'PT', 'SC', 'TJ', 'EX']
    
    def __init__(self, **kwargs):
        """
        Inicializa un estudiante.
        
        Campos esperados (según esquema de BD):
            ci_numero, ci_expedicion, nombres, apellidos, fecha_nacimiento,
            telefono, email, universidad_egreso, profesion, fotografia_path,
            fecha_registro, activo
        """
        # Campos obligatorios
        self.ci_numero = kwargs.get('ci_numero')
        self.ci_expedicion = kwargs.get('ci_expedicion')
        self.nombres = kwargs.get('nombres')
        self.apellidos = kwargs.get('apellidos')
        
        # Campos opcionales
        self.fecha_nacimiento = kwargs.get('fecha_nacimiento')
        self.telefono = kwargs.get('telefono')
        self.email = kwargs.get('email')
        self.universidad_egreso = kwargs.get('universidad_egreso')
        self.profesion = kwargs.get('profesion')
        self.fotografia_path = kwargs.get('fotografia_path')
        self.fecha_registro = kwargs.get('fecha_registro', datetime.now().isoformat())
        self.activo = kwargs.get('activo', 1)
        
        # ID (si viene de la base de datos)
        if 'id' in kwargs:
            self.id = kwargs['id']
        
        # Validaciones básicas
        self._validar()
    
    def _validar(self):
        """Valida los datos del estudiante"""
        if not self.ci_numero or not self.nombres or not self.apellidos:
            raise ValueError("CI, nombres y apellidos son obligatorios")
        
        if self.ci_expedicion and self.ci_expedicion not in self.EXPEDICIONES_VALIDAS:
            raise ValueError(f"Expedición de CI inválida. Válidas: {self.EXPEDICIONES_VALIDAS}")
        
        if self.email:
            # Validación simple de email
            if '@' not in self.email or '.' not in self.email.split('@')[-1]:
                raise ValueError("Formato de email inválido")
    
    def __repr__(self):
        return f"<Estudiante {self.ci_numero}: {self.nombres} {self.apellidos}>"
    
    @property
    def nombre_completo(self) -> str:
        """Devuelve el nombre completo del estudiante"""
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def edad(self) -> Optional[int]:
        """Calcula la edad del estudiante"""
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
    
    def activar(self):
        """Activa al estudiante"""
        self.activo = 1
        return self.save()
    
    def desactivar(self):
        """Desactiva al estudiante"""
        self.activo = 0
        return self.save()
    
    @classmethod
    def crear_estudiante(cls, datos: Dict) -> 'EstudianteModel':
        """Crea un nuevo estudiante con validaciones"""
        # Validaciones específicas
        if 'ci_numero' not in datos or not datos['ci_numero']:
            raise ValueError("El número de CI es obligatorio")
        
        # Verificar que el CI no exista
        existente = cls.buscar_por_ci(datos['ci_numero'], datos.get('ci_expedicion'))
        if existente:
            raise ValueError(f"Ya existe un estudiante con CI {datos['ci_numero']}")
        
        # Crear y guardar
        estudiante = cls(**datos)
        estudiante.save()
        return estudiante
    
    @classmethod
    def buscar_por_ci(cls, ci_numero: str, ci_expedicion: str = None) -> Optional['EstudianteModel']:
        """Busca un estudiante por su CI"""
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
    def buscar_por_nombre(cls, nombre: str) -> List['EstudianteModel']:
        """Busca estudiantes por nombre o apellido"""
        from database import db
        
        query = f"""
        SELECT * FROM {cls.TABLE_NAME} 
        WHERE nombres LIKE ? OR apellidos LIKE ? OR nombres || ' ' || apellidos LIKE ?
        """
        param = f"%{nombre}%"
        rows = db.fetch_all(query, (param, param, param))
        
        return [cls(**row) for row in rows]
    
    @classmethod
    def buscar_activos(cls) -> List['EstudianteModel']:
        """Busca estudiantes activos"""
        from database import db
        
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE activo = 1"
        rows = db.fetch_all(query)
        
        return [cls(**row) for row in rows]
    
    @classmethod
    def obtener_estadisticas(cls) -> Dict[str, Any]:
        """Obtiene estadísticas de estudiantes"""
        from database import db
        
        query_total = f"SELECT COUNT(*) as total FROM {cls.TABLE_NAME}"
        query_activos = f"SELECT COUNT(*) as activos FROM {cls.TABLE_NAME} WHERE activo = 1"
        
        total = db.fetch_one(query_total)['total']
        activos = db.fetch_one(query_activos)['activos']
        
        return {
            'total_estudiantes': total,
            'estudiantes_activos': activos,
            'estudiantes_inactivos': total - activos,
            'porcentaje_activos': (activos / total * 100) if total > 0 else 0
        }