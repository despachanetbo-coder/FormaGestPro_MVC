# app/models/estudiante.py
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
        self.fotografia_path = kwargs.get('fotografia_path')  # Asegurar que se guarda
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
    
    # ============================================================================
    # MÉTODOS DE PERSISTENCIA (CRUD) - ¡ESTOS SON LOS QUE FALTAN!
    # ============================================================================
    
    def save(self):
        """Guardar o actualizar el estudiante en la base de datos"""
        try:
            from database.database import db
            
            print(f"DEBUG EstudianteModel.save():")
            print(f"  - Tipo de operación: {'UPDATE' if hasattr(self, 'id') and self.id else 'INSERT'}")
            print(f"  - ID: {getattr(self, 'id', 'Nuevo')}")
            print(f"  - fotografia_path: {self.fotografia_path}")
            
            if hasattr(self, 'id') and self.id:
                # ACTUALIZAR registro existente
                query = f"""
                    UPDATE {self.TABLE_NAME} 
                    SET ci_numero = ?, ci_expedicion = ?, nombres = ?, apellidos = ?,
                        fecha_nacimiento = ?, telefono = ?, email = ?, 
                        universidad_egreso = ?, profesion = ?, fotografia_path = ?, 
                        activo = ?
                    WHERE id = ?
                """
                params = (
                    self.ci_numero, self.ci_expedicion, self.nombres, self.apellidos,
                    self.fecha_nacimiento, self.telefono, self.email,
                    self.universidad_egreso, self.profesion, self.fotografia_path,
                    self.activo, self.id
                )
                db.execute(query, params)
                print(f"  - ✅ UPDATE ejecutado para ID {self.id}")
                
            else:
                # INSERTAR nuevo registro
                query = f"""
                    INSERT INTO {self.TABLE_NAME} 
                    (ci_numero, ci_expedicion, nombres, apellidos, fecha_nacimiento,
                     telefono, email, universidad_egreso, profesion, fotografia_path,
                     fecha_registro, activo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    self.ci_numero, self.ci_expedicion, self.nombres, self.apellidos,
                    self.fecha_nacimiento, self.telefono, self.email,
                    self.universidad_egreso, self.profesion, self.fotografia_path,
                    self.fecha_registro, self.activo
                )
                db.execute(query, params)
                self.id = db.lastrowid
                print(f"  - ✅ INSERT ejecutado, nuevo ID: {self.id}")
            
            print(f"  - Guardado exitoso")
            
        except Exception as e:
            print(f"❌ ERROR en EstudianteModel.save(): {e}")
            import traceback
            traceback.print_exc()
            raise
    
    @classmethod
    def find_by_id(cls, estudiante_id: int) -> Optional['EstudianteModel']:
        """Buscar estudiante por ID"""
        try:
            from database.database import db
            
            print(f"DEBUG find_by_id: Buscando estudiante ID {estudiante_id}")
            
            query = f"SELECT * FROM {cls.TABLE_NAME} WHERE id = ?"
            row = db.fetch_one(query, (estudiante_id,))
            
            if row:
                print(f"  - ✅ Estudiante encontrado")
                return cls(**row)
            else:
                print(f"  - ❌ Estudiante no encontrado")
                return None
                
        except Exception as e:
            print(f"ERROR en find_by_id: {e}")
            return None
    
    @classmethod
    def get_all(cls) -> List['EstudianteModel']:
        """Obtener todos los estudiantes"""
        try:
            from database.database import db
            
            query = f"SELECT * FROM {cls.TABLE_NAME} ORDER BY apellidos, nombres"
            rows = db.fetch_all(query)
            
            return [cls(**row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error en get_all: {e}")
            return []
    
    @classmethod
    def delete_by_id(cls, estudiante_id: int) -> bool:
        """Eliminar estudiante por ID"""
        try:
            from database.database import db
            
            query = f"DELETE FROM {cls.TABLE_NAME} WHERE id = ?"
            db.execute(query, (estudiante_id,))
            
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando estudiante: {e}")
            return False
    
    # ============================================================================
    # MÉTODOS DE BÚSQUEDA
    # ============================================================================
    
    @classmethod
    def buscar_por_ci(cls, ci_numero: str, ci_expedicion: str = None) -> Optional['EstudianteModel']:
        """Busca un estudiante por su CI"""
        from database.database import db
        
        if ci_expedicion:
            query = f"SELECT * FROM {cls.TABLE_NAME} WHERE ci_numero = ? AND ci_expedicion = ?"
            params = (ci_numero, ci_expedicion)
        else:
            query = f"SELECT * FROM {cls.TABLE_NAME} WHERE ci_numero = ?"
            params = (ci_numero,)
        
        row = db.fetch_one(query, params)
        return cls(**row) if row else None
    
    @classmethod
    def buscar_por_nombre(cls, texto: str) -> List['EstudianteModel']:
        """Buscar estudiantes por nombre o apellido"""
        from database.database import db

        try:
            query = f"""
                SELECT * FROM {cls.TABLE_NAME} 
                WHERE nombres LIKE ? OR apellidos LIKE ? 
                ORDER BY apellidos, nombres
            """
            parametro = f"%{texto}%"
            rows = db.fetch_all(query, (parametro, parametro))

            return [cls(**row) for row in rows]

        except Exception as e:
            logger.error(f"Error en buscar_por_nombre: {e}")
            return []
    
    @classmethod
    def buscar_activos(cls) -> List['EstudianteModel']:
        """Buscar estudiantes activos"""
        from database.database import db
        
        try:
            query = f"""
                SELECT * FROM {cls.TABLE_NAME} 
                WHERE activo = 1 
                ORDER BY apellidos, nombres
                LIMIT 100
            """
            rows = db.fetch_all(query)
            
            return [cls(**row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error en buscar_activos: {e}")
            return []
    
    # ============================================================================
    # MÉTODOS ESTADÍSTICOS
    # ============================================================================
    
    @staticmethod
    def contar_total():
        """Contar el total de estudiantes registrados"""
        try:
            from database.database import db
            
            query = "SELECT COUNT(*) as total FROM estudiantes"
            resultado = db.fetch_one(query)
            return resultado['total'] if resultado else 0
            
        except Exception as e:
            print(f"❌ Error contando estudiantes: {e}")
            return 0
    
    @classmethod
    def obtener_estadisticas(cls) -> Dict[str, Any]:
        """Obtiene estadísticas de estudiantes"""
        from database.database import db
        
        query_total = f"SELECT COUNT(*) as total FROM {cls.TABLE_NAME}"
        query_activos = f"SELECT COUNT(*) as activos FROM {cls.TABLE_NAME} WHERE activo = 1"
        
        total = db.fetch_one(query_total)['total']
        activos = db.fetch_one(query_activos)['activos']
        
        return {
            'total_estudiantes': total,
            'estudiantes_activos': activos,
            'estudiantes_inactivos': total - activos
        }
    
    # ============================================================================
    # MÉTODOS DE ESTADO
    # ============================================================================
    
    def activar(self):
        """Activa al estudiante"""
        self.activo = 1
        return self.save()
    
    def desactivar(self):
        """Desactiva al estudiante"""
        self.activo = 0
        return self.save()
    
    # ============================================================================
    # MÉTODO DE CREACIÓN CON VALIDACIÓN
    # ============================================================================
    
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
    

    