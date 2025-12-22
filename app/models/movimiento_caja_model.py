# app/models/movimiento_caja.py
"""
Modelo para movimientos de caja.
"""
import logging
from datetime import datetime
from .base_model import BaseModel

logger = logging.getLogger(__name__)

class MovimientoCajaModel(BaseModel):
    """Modelo que representa un movimiento de caja"""
    
    TABLE_NAME = "movimientos_caja"
    
    def __init__(self, **kwargs):
        """
        Inicializa un movimiento de caja.
        
        Campos esperados:
            tipo: 'INGRESO' o 'EGRESO'
            monto: decimal positivo
            descripcion: descripción del movimiento
            referencia_tipo: tipo de referencia ('PAGO', 'GASTO', 'FACTURA', etc.)
            referencia_id: ID de la referencia
            fecha: fecha del movimiento (de la base de datos)
        """
        # Campos principales
        self.tipo = kwargs.get('tipo')  # 'INGRESO' o 'EGRESO'
        self.monto = kwargs.get('monto', 0.0)
        self.descripcion = kwargs.get('descripcion', '')
        self.referencia_tipo = kwargs.get('referencia_tipo')
        self.referencia_id = kwargs.get('referencia_id')
        self.fecha = kwargs.get('fecha')  # <-- AGREGAR ESTA LÍNEA
        
        # ID (si viene de la base de datos)
        if 'id' in kwargs:
            self.id = kwargs['id']
    
    def __repr__(self):
        return f"<MovimientoCaja {self.id}: {self.tipo} ${self.monto:.2f}>"
    
    # Añadir este método en la clase MovimientoCajaModel
    @classmethod
    def registrar_ingreso_generico(cls, ingreso_id, monto, descripcion, forma_pago='EFECTIVO'):
        """Registra un ingreso en caja por un ingreso genérico"""
        movimiento_data = {
            'tipo': 'INGRESO',
            'monto': monto,
            'descripcion': descripcion,
            'referencia_tipo': 'INGRESO_GENERICO',
            'referencia_id': ingreso_id,
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        movimiento = cls(**movimiento_data)
        movimiento.save()

        logger.info(f"✅ Ingreso genérico registrado en caja: ${monto:.2f} - {descripcion}")
        return movimiento

    @classmethod
    def registrar_ingreso_pago(cls, pago_id, monto, matricula_id, nro_cuota=None):
        """
        Registra un ingreso en caja por un pago.
        
        Args:
            pago_id: ID del pago
            monto: monto del pago
            matricula_id: ID de la matrícula
            nro_cuota: número de cuota (opcional)
        """
        from .matricula_model import MatriculaModel
        from .estudiante_model import EstudianteModel
        from .programa_academico_model import ProgramaAcademicoModel
        from database.database import db
        
        # Obtener detalles para la descripción
        matricula = MatriculaModel.find_by_id(matricula_id)
        if not matricula:
            logger.error(f"No se encontró matrícula {matricula_id} para movimiento de caja")
            return None
        
        estudiante = EstudianteModel.find_by_id(matricula.estudiante_id)
        nombre_estudiante = f"{estudiante.nombres} {estudiante.apellidos}" if estudiante else "Desconocido"
        
        programa = ProgramaAcademicoModel.find_by_id(matricula.programa_id)
        programa_nombre = programa.nombre if programa else "Programa desconocido"
        
        # Crear descripción
        if nro_cuota:
            descripcion = f"Pago cuota {nro_cuota} - {programa_nombre[:20]} - Est: {nombre_estudiante[:15]}"
        else:
            descripcion = f"Pago al contado - {programa_nombre[:20]} - Est: {nombre_estudiante[:15]}"
        
        # Crear movimiento con fecha actual
        movimiento_data = {
            'tipo': 'INGRESO',
            'monto': monto,
            'descripcion': descripcion,
            'referencia_tipo': 'PAGO',
            'referencia_id': pago_id,
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # <-- Formato específico
        }
        
        movimiento = cls(**movimiento_data)
        movimiento.save()
        
        logger.info(f"✅ Ingreso registrado en caja por pago {pago_id}: ${monto:.2f}")
        return movimiento
    
    @classmethod
    def registrar_egreso_gasto(cls, gasto_id, monto, descripcion):
        """Registra un egreso en caja por un gasto"""
        movimiento_data = {
            'tipo': 'EGRESO',
            'monto': monto,
            'descripcion': descripcion,
            'referencia_tipo': 'GASTO',
            'referencia_id': gasto_id,
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # <-- Formato específico
        }
        
        movimiento = cls(**movimiento_data)
        movimiento.save()
        
        logger.info(f"✅ Egreso registrado en caja por gasto {gasto_id}: ${monto:.2f}")
        return movimiento
    
    @classmethod
    def obtener_saldo_actual(cls):
        """Calcula el saldo actual de caja"""
        from database.database import db
        
        query = """
        SELECT 
            COALESCE(SUM(CASE WHEN tipo = 'INGRESO' THEN monto ELSE 0 END), 0) as total_ingresos,
            COALESCE(SUM(CASE WHEN tipo = 'EGRESO' THEN monto ELSE 0 END), 0) as total_egresos
        FROM movimientos_caja
        """
        
        result = db.fetch_one(query)
        print(f"El resultado es {result}")
        if result:
            ingresos = result['total_ingresos'] or 0
            egresos = result['total_egresos'] or 0
            return round(ingresos - egresos, 2)
        return 0.0
    
    @classmethod
    def obtener_movimientos_hoy(cls):
        """Obtiene los movimientos de caja de hoy"""
        from database.database import db
        
        query = """
        SELECT * FROM movimientos_caja 
        WHERE DATE(fecha) = DATE('now')
        ORDER BY fecha DESC
        """
        
        rows = db.fetch_all(query)
        return [cls(**row) for row in rows]
    
    @classmethod
    def obtener_movimientos_rango(cls, fecha_inicio, fecha_fin):
        """Obtiene movimientos en un rango de fechas"""
        from database.database import db
        
        query = """
        SELECT * FROM movimientos_caja 
        WHERE DATE(fecha) BETWEEN ? AND ?
        ORDER BY fecha DESC
        """
        
        rows = db.fetch_all(query, (fecha_inicio, fecha_fin))
        return [cls(**row) for row in rows]
    
    @classmethod
    def existe_movimiento_para_pago(cls, pago_id):
        """Verifica si ya existe un movimiento para un pago"""
        from database.database import db
        
        query = "SELECT COUNT(*) as count FROM movimientos_caja WHERE referencia_tipo = 'PAGO' AND referencia_id = ?"
        result = db.fetch_one(query, (pago_id,))
        
        return result and result['count'] > 0