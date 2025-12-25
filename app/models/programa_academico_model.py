# apps/models/programa_academico_model.py
"""
Modelo Programa Académico usando SQLite3 directamente.
Según el esquema real de la base de datos.
"""
import logging
import enum
from typing import Any, List, Dict, Optional
from datetime import datetime, date, timedelta
from .base_model import BaseModel

logger = logging.getLogger(__name__)

# Enums según el esquema real
class EstadoPrograma(enum.Enum):
    PLANIFICADO = "PLANIFICADO"
    INICIADO = "INICIADO"
    CONCLUIDO = "CONCLUIDO"
    CANCELADO = "CANCELADO"

class ProgramaAcademicoModel(BaseModel):
    """Modelo que representa un programa académico"""
    
    TABLE_NAME = "programas_academicos"
    
    def __init__(self, **kwargs):
        """
        Inicializa un programa académico.
        
        Campos esperados (según esquema de BD):
            codigo, nombre, descripcion, duracion_semanas, horas_totales,
            costo_base, descuento_contado, cupos_totales, cupos_disponibles,
            estado, fecha_inicio_planificada, fecha_inicio_real, fecha_fin_real,
            tutor_id, promocion_activa, descripcion_promocion, descuento_promocion,
            created_at, updated_at
        """
        # Campos obligatorios
        self.codigo = kwargs.get('codigo')
        self.nombre = kwargs.get('nombre')
        self.costo_base = kwargs.get('costo_base', 0.0)
        self.cupos_totales = kwargs.get('cupos_totales', 0)
        
        # Campos opcionales
        self.descripcion = kwargs.get('descripcion')
        self.duracion_semanas = kwargs.get('duracion_semanas')
        self.horas_totales = kwargs.get('horas_totales')
        self.descuento_contado = kwargs.get('descuento_contado', 0.0)
        self.cupos_disponibles = kwargs.get('cupos_disponibles', self.cupos_totales if self.cupos_totales else 0)
        self.estado = kwargs.get('estado', EstadoPrograma.PLANIFICADO.value)
        self.fecha_inicio_planificada = kwargs.get('fecha_inicio_planificada')
        self.fecha_inicio_real = kwargs.get('fecha_inicio_real')
        self.fecha_fin_real = kwargs.get('fecha_fin_real')
        self.tutor_id = kwargs.get('tutor_id')
        self.promocion_activa = kwargs.get('promocion_activa', 0)  # 0 = False, 1 = True
        self.descripcion_promocion = kwargs.get('descripcion_promocion')
        self.descuento_promocion = kwargs.get('descuento_promocion', 0.0)
        self.created_at = kwargs.get('created_at', datetime.now().isoformat())
        self.updated_at = kwargs.get('updated_at', datetime.now().isoformat())
        
        # ID (si viene de la base de datos)
        if 'id' in kwargs:
            self.id = kwargs['id']
        
        # Validaciones básicas
        self._validar()
    
    def _validar(self):
        """Valida los datos del programa"""
        if not self.codigo or not self.nombre:
            raise ValueError("Código y nombre son obligatorios")
        
        if self.costo_base < 0:
            raise ValueError("El costo base no puede ser negativo")
        
        if self.cupos_totales < 0:
            raise ValueError("Los cupos totales no pueden ser negativos")
        
        if self.cupos_disponibles < 0 or self.cupos_disponibles > self.cupos_totales:
            raise ValueError("Los cupos disponibles deben estar entre 0 y el total de cupos")
        
        if self.descuento_contado < 0 or self.descuento_contado > 100:
            raise ValueError("El descuento por contado debe estar entre 0 y 100")
        
        if self.descuento_promocion < 0 or self.descuento_promocion > 100:
            raise ValueError("El descuento por promoción debe estar entre 0 y 100")
        
        # Validar estado
        estados_validos = [e.value for e in EstadoPrograma]
        if self.estado not in estados_validos:
            raise ValueError(f"Estado inválido. Válidos: {estados_validos}")
    
    def __repr__(self):
        return f"<Programa {self.codigo}: {self.nombre}>"
    
    @property
    def nombre_completo(self) -> str:
        """Devuelve el nombre completo del programa con código"""
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def costo_con_descuento_contado(self) -> float:
        """Calcula el costo con descuento por pago al contado"""
        if self.descuento_contado and self.descuento_contado > 0:
            return self.costo_base * (1 - self.descuento_contado / 100)
        return self.costo_base
    
    @property
    def costo_con_promocion(self) -> float:
        """Calcula el costo con promoción activa"""
        if self.promocion_activa and self.descuento_promocion:
            return self.costo_base * (1 - self.descuento_promocion / 100)
        return self.costo_base
    
    @staticmethod
    def contar_total():
        """Contar el total de programas registrados"""
        try:
            from database.database import db
            
            query = "SELECT COUNT(*) as total FROM programas_academicos"
            resultado = db.fetch_one(query)
            return resultado['total'] if resultado else 0
            
        except Exception as e:
            print(f"❌ Error contando programas: {e}")
            return 0

    def calcular_costo_final(self, pago_contado: bool = False) -> float:
        """Calcula el costo final según modalidad de pago"""
        if pago_contado:
            return self.costo_con_descuento_contado
        return self.costo_con_promocion if self.promocion_activa else self.costo_base
    
    def ocupar_cupo(self) -> int:
        """Ocupa un cupo disponible"""
        if self.cupos_disponibles <= 0:
            raise ValueError("No hay cupos disponibles")
        
        self.cupos_disponibles -= 1
        self.updated_at = datetime.now().isoformat()
        self.save()
        return self.cupos_disponibles
    
    def liberar_cupo(self) -> int:
        """Libera un cupo ocupado"""
        if self.cupos_disponibles >= self.cupos_totales:
            raise ValueError("No hay cupos ocupados para liberar")
        
        self.cupos_disponibles += 1
        self.updated_at = datetime.now().isoformat()
        self.save()
        return self.cupos_disponibles
    
    def iniciar_programa(self, fecha_inicio_real: date = None):
        """Inicia el programa"""
        self.estado = EstadoPrograma.INICIADO.value
        if fecha_inicio_real:
            self.fecha_inicio_real = fecha_inicio_real.isoformat()
        else:
            self.fecha_inicio_real = date.today().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.save()
    
    def concluir_programa(self, fecha_fin_real: date = None):
        """Concluye el programa"""
        self.estado = EstadoPrograma.CONCLUIDO.value
        if fecha_fin_real:
            self.fecha_fin_real = fecha_fin_real.isoformat()
        else:
            self.fecha_fin_real = date.today().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.save()

    @classmethod
    def update_programa(cls, id: int, data: dict) -> bool:
        """
        Actualiza un programa por su ID.

        Args:
            id: ID del programa
            data: Diccionario con los campos a actualizar

        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        if not id or not data:
            return False

        # Validar los datos si es necesario
        # (podemos omitir validaciones complejas para actualizaciones parciales)

        # Preparar la cláusula SET
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {cls.TABLE_NAME} SET {set_clause} WHERE id = ?"

        # Preparar los parámetros
        params = tuple(data.values()) + (id,)

        try:
            from database import db
            db.execute(query, params)
            logger.info(f"✅ Programa actualizado con ID: {id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error al actualizar programa: {e}")
            return False
    
    def cancelar_programa(self):
        """Cancela el programa"""
        self.estado = EstadoPrograma.CANCELADO.value
        self.updated_at = datetime.now().isoformat()
        self.save()
    
    def activar_promocion(self, descuento: float, descripcion: str = ""):
        """Activa una promoción"""
        if descuento < 0 or descuento > 100:
            raise ValueError("El descuento debe estar entre 0 y 100")
        
        self.promocion_activa = 1
        self.descuento_promocion = descuento
        self.descripcion_promocion = descripcion
        self.updated_at = datetime.now().isoformat()
        self.save()
    
    def desactivar_promocion(self):
        """Desactiva la promoción"""
        self.promocion_activa = 0
        self.updated_at = datetime.now().isoformat()
        self.save()
    
    @classmethod
    def crear_programa(cls, datos: Dict) -> 'ProgramaAcademicoModel':
        """Crea un nuevo programa con validaciones"""
        # Validaciones básicas
        required_fields = ['codigo', 'nombre', 'costo_base', 'cupos_totales']
        for field in required_fields:
            if field not in datos or not datos[field]:
                raise ValueError(f"Campo requerido: {field}")
        
        # Validar estado si se proporciona
        if 'estado' in datos and datos['estado']:
            estados_validos = [e.value for e in EstadoPrograma]
            if datos['estado'] not in estados_validos:
                raise ValueError(f"Estado inválido. Debe ser: {', '.join(estados_validos)}")
        
        # Verificar que el código sea único
        existente = cls.buscar_por_codigo(datos['codigo'])
        if existente:
            raise ValueError(f"Ya existe un programa con código {datos['codigo']}")
        
        # Crear y guardar
        programa = cls(**datos)
        programa.save()
        return programa
    
    @classmethod
    def buscar_por_codigo(cls, codigo: str) -> Optional['ProgramaAcademicoModel']:
        """Busca un programa por su código"""
        from database import db
        
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE codigo = ?"
        row = db.fetch_one(query, (codigo,))
        
        return cls(**row) if row else None
    
    @classmethod
    def buscar_por_estado(cls, estado: str) -> List['ProgramaAcademicoModel']:
        """Busca programas por estado"""
        from database import db
        
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE estado = ?"
        rows = db.fetch_all(query, (estado,))
        
        return [cls(**row) for row in rows]
    
    @classmethod
    def buscar_por_tutor(cls, tutor_id: int) -> List['ProgramaAcademicoModel']:
        """Busca programas por tutor"""
        from database import db
        
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE tutor_id = ?"
        rows = db.fetch_all(query, (tutor_id,))
        
        return [cls(**row) for row in rows]
    
    @classmethod
    def buscar_con_cupos_disponibles(cls) -> List['ProgramaAcademicoModel']:
        """Busca programas con cupos disponibles"""
        from database import db
        
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE cupos_disponibles > 0"
        rows = db.fetch_all(query)
        
        return [cls(**row) for row in rows]
    
    @classmethod
    def actualizar_cupos(cls, programa_id: int, cantidad: int = -1) -> bool:
        """Actualizar cupos disponibles de un programa"""
        from database import db

        try:
            # Obtener programa actual
            programa = cls.find_by_id(programa_id)
            if not programa:
                logger.error(f"Programa {programa_id} no encontrado")
                return False

            # Calcular nuevos cupos (asegurar que no sea negativo)
            nuevos_cupos = max(0, programa.cupos_disponibles + cantidad)

            # Actualizar en base de datos
            query = f"""
                UPDATE {cls.TABLE_NAME} 
                SET cupos_disponibles = ?, 
                    fecha_actualizacion = CURRENT_TIMESTAMP 
                WHERE id = ?
            """
            success = db.execute(query, (nuevos_cupos, programa_id))

            if success:
                logger.info(f"✅ Cupos actualizados: Programa {programa_id} - {cantidad} cupos")
                # Actualizar objeto en memoria si está en uso
                programa.cupos_disponibles = nuevos_cupos
            else:
                logger.error(f"❌ Error al actualizar cupos para programa {programa_id}")

            return success

        except Exception as e:
            logger.error(f"Error en actualizar_cupos: {e}")
            return False

    # También necesitamos el método ocupar_cupo que usa matricular_estudiante
    def ocupar_cupo(self):
        """Ocupar un cupo del programa (reducir en 1)"""
        return self.__class__.actualizar_cupos(self.id, -1)    
    
    @classmethod
    def buscar_promociones_activas(cls) -> List['ProgramaAcademicoModel']:
        """Busca programas con promociones activas"""
        from database import db
        
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE promocion_activa = 1"
        rows = db.fetch_all(query)
        
        return [cls(**row) for row in rows]
    
    @classmethod
    def obtener_estadisticas(cls) -> Dict[str, Any]:
        """Obtiene estadísticas de programas"""
        from database import db
        
        # Totales
        query_total = f"SELECT COUNT(*) as total FROM {cls.TABLE_NAME}"
        query_activos = f"SELECT COUNT(*) as activos FROM {cls.TABLE_NAME} WHERE estado = 'INICIADO'"
        query_planificados = f"SELECT COUNT(*) as planificados FROM {cls.TABLE_NAME} WHERE estado = 'PLANIFICADO'"
        query_con_cupos = f"SELECT COUNT(*) as con_cupos FROM {cls.TABLE_NAME} WHERE cupos_disponibles > 0"
        
        total = db.fetch_one(query_total)['total']
        activos = db.fetch_one(query_activos)['activos']
        planificados = db.fetch_one(query_planificados)['planificados']
        con_cupos = db.fetch_one(query_con_cupos)['con_cupos']
        
        # Cupos totales
        query_cupos = f"""
        SELECT 
            SUM(cupos_totales) as total_cupos,
            SUM(cupos_disponibles) as total_disponibles
        FROM {cls.TABLE_NAME}
        """
        cupos = db.fetch_one(query_cupos)
        
        return {
            'total_programas': total,
            'programas_activos': activos,
            'programas_planificados': planificados,
            'programas_con_cupos_disponibles': con_cupos,
            'programas_sin_cupos': total - con_cupos,
            'total_cupos_disponibles': cupos['total_disponibles'] if cupos else 0,
            'total_cupos_ocupados': (cupos['total_cupos'] - cupos['total_disponibles']) if cupos else 0
        }
    
    # models/programa.py - Añadir propiedad para calcular intervalo de cuotas
    @property
    def intervalo_cuotas_auto(self, nro_cuotas):
        """Calcula el intervalo entre cuotas basado en duración del programa"""
        if not self.duracion_semanas or nro_cuotas <= 0:
            return 30  # Valor por defecto
        
        # Convertir semanas a días y dividir por número de cuotas
        dias_totales = self.duracion_semanas * 7
        intervalo = dias_totales / nro_cuotas
        return max(7, round(intervalo))  # Mínimo 7 días entre cuotas
    
    def calcular_fechas_vencimiento(self, fecha_inicio, nro_cuota, nro_cuotas_total):
        """Calcula fecha de vencimiento para una cuota específica"""
        if not fecha_inicio:
            fecha_inicio = datetime.now().date()
        
        if not self.duracion_semanas or nro_cuotas_total <= 0:
            # Fallback: cada 30 días
            dias = nro_cuota * 30
            return fecha_inicio + timedelta(days=dias)
        
        # Calcular intervalo basado en duración total
        dias_totales = self.duracion_semanas * 7
        intervalo = dias_totales / nro_cuotas_total
        
        # Calcular días para esta cuota específica
        dias = round(intervalo * nro_cuota)
        return fecha_inicio + timedelta(days=dias)
    
    @classmethod
    def contar_por_año(cls, año: int = None) -> int:
        """Contar programas registrados en un año específico"""
        try:
            from database.database import db
            
            if año is None:
                año = datetime.now().year
            
            query = """
            SELECT COUNT(*) as total 
            FROM programas_academicos 
            WHERE strftime('%Y', created_at) = ?
            """
            
            resultado = db.fetch_one(query, (str(año),))
            return resultado['total'] if resultado else 0
            
        except Exception as e:
            logger.error(f"Error contando programas por año: {e}")
            return 0

# ==================== ALIAS PARA COMPATIBILIDAD ====================
# Alias para compatibilidad con código existente

    @classmethod
    def get_activos(cls):
        """Obtener programas activos (PLANIFICADO o INICIADO)"""
        try:
            # Si es SQLAlchemy
            if hasattr(cls, 'query'):
                from sqlalchemy import or_
                return cls.query.filter(
                    or_(cls.estado == 'PLANIFICADO', cls.estado == 'INICIADO')
                ).all()
            # Si es otra implementación
            else:
                # Necesitarías implementar la lógica según tu almacenamiento
                pass
        except Exception as e:
            logger.error(f"Error en get_activos: {e}")
            return []

    @classmethod
    def get_by_id(cls, programa_id):
        """Obtener programa por ID"""
        try:
            if hasattr(cls, 'query'):
                return cls.query.get(programa_id)
            else:
                # Implementación según tu sistema
                pass
        except Exception as e:
            logger.error(f"Error en get_by_id: {e}")
            return None
    
    @classmethod
    def update_by_id(cls, programa_id: int, datos: dict) -> bool:
        '''Actualizar programa por ID - compatibilidad'''
        try:
            programa = cls.find_by_id(programa_id)
            if not programa:
                return False
            
            for key, value in datos.items():
                if hasattr(programa, key):
                    setattr(programa, key, value)
            
            return programa.save()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Error al actualizar programa {programa_id}: {e}')
            return False
ProgramaModel = ProgramaAcademicoModel
