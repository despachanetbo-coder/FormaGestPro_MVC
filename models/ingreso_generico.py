# models/ingreso_generico.py
"""
Modelo para Ingresos Genéricos usando SQLite3 directamente.
"""
import logging
from datetime import datetime

from models.movimiento_caja import MovimientoCajaModel
from .base_model import BaseModel

logger = logging.getLogger(__name__)

class IngresoGenericoModel(BaseModel):
    """Modelo que representa un ingreso genérico (no asociado a matrícula)"""
    
    TABLE_NAME = "ingresos_genericos"
    
    # Formas de pago válidas (consistentes con otros modelos)
    FORMAS_PAGO = ['EFECTIVO', 'TRANSFERENCIA', 'TARJETA', 'CHEQUE', 'DEPOSITO', 'PAGOS QR']
    
    # Categorías sugeridas para ingresos (opcional)
    CATEGORIAS_SUGERIDAS = [
        'VENTA_MATERIALES', 'SERVICIOS_EXTERNOS', 'DONACIONES', 
        'REEMBOLSOS', 'INTERESES', 'ALQUILERES', 'OTROS'
    ]
    
    def __init__(self, **kwargs):
        """
        Inicializa un ingreso genérico.
        
        Campos esperados:
            fecha, monto, concepto, descripcion, forma_pago,
            comprobante_nro, registrado_por
        """
        # Campos obligatorios
        self.fecha = kwargs.get('fecha', datetime.now().date().isoformat())
        self.monto = kwargs.get('monto', 0.0)
        self.concepto = kwargs.get('concepto', '')
        
        # Campos con valores por defecto
        self.forma_pago = kwargs.get('forma_pago', 'EFECTIVO')
        
        # Campos opcionales
        self.descripcion = kwargs.get('descripcion')
        self.comprobante_nro = kwargs.get('comprobante_nro')
        self.registrado_por = kwargs.get('registrado_por')
        
        # ID (si viene de la base de datos)
        if 'id' in kwargs:
            self.id = kwargs['id']
        
        # Validaciones
        self._validar()
    
    def _validar(self):
        """Valida los datos del ingreso"""
        if self.monto <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        
        if not self.concepto or not self.concepto.strip():
            raise ValueError("El concepto es obligatorio")
        
        if self.forma_pago not in self.FORMAS_PAGO:
            raise ValueError(f"Forma de pago inválida. Válidas: {self.FORMAS_PAGO}")
    
    def __repr__(self):
        return f"<IngresoGenerico {self.id}: ${self.monto:.2f} - {self.concepto[:30]}>"
    
    def save(self):
        """
        Guarda el ingreso y registra automáticamente el movimiento de caja (INGRESO)
        """
        # Guardar primero para obtener ID si es nuevo
        ingreso_id = super().save()
        
        # Registrar movimiento de caja (INGRESO)
        try:
            # Crear descripción para el movimiento
            descripcion = f"Ingreso: {self.concepto}"
            if self.descripcion:
                descripcion += f" ({self.descripcion[:30]})"
            
            MovimientoCajaModel.registrar_ingreso_generico(
                ingreso_id=self.id,
                monto=self.monto,
                descripcion=descripcion,
                forma_pago=self.forma_pago
            )
            logger.info(f"✅ Movimiento de caja registrado para ingreso {self.id}")
        except Exception as e:
            logger.error(f"Error al registrar movimiento de caja para ingreso {self.id}: {e}")
            raise
        
        return ingreso_id
    
    @classmethod
    def buscar_por_fecha(cls, fecha):
        """Busca ingresos por fecha"""
        from database.database import db
        
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE fecha = ? ORDER BY id DESC"
        rows = db.fetch_all(query, (fecha,))
        
        return [cls(**row) for row in rows]
    
    @classmethod
    def buscar_por_concepto(cls, concepto):
        """Busca ingresos por concepto (búsqueda parcial)"""
        from database.database import db
        
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE concepto LIKE ? ORDER BY fecha DESC"
        rows = db.fetch_all(query, (f'%{concepto}%',))
        
        return [cls(**row) for row in rows]
    
    @classmethod
    def buscar_por_rango_fechas(cls, fecha_inicio, fecha_fin):
        """Busca ingresos por rango de fechas"""
        from database.database import db
        
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE fecha BETWEEN ? AND ? ORDER BY fecha DESC"
        rows = db.fetch_all(query, (fecha_inicio, fecha_fin))
        
        return [cls(**row) for row in rows]
    
    @classmethod
    def obtener_total_por_mes(cls, año=None, mes=None):
        """Obtiene el total de ingresos por mes"""
        from database.database import db
        
        if año and mes:
            query = """
            SELECT strftime('%Y-%m', fecha) as periodo, SUM(monto) as total
            FROM ingresos_genericos
            WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
            GROUP BY strftime('%Y-%m', fecha)
            """
            params = (str(año), f"{mes:02d}")
        else:
            query = """
            SELECT strftime('%Y-%m', fecha) as periodo, SUM(monto) as total
            FROM ingresos_genericos
            GROUP BY strftime('%Y-%m', fecha)
            ORDER BY periodo DESC
            """
            params = ()
        
        return db.fetch_all(query, params)