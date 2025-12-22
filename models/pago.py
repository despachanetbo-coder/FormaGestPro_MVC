# models/pago.py
"""
Modelo de Pago usando SQLite3 directamente.
"""
import logging
from datetime import datetime

from models.movimiento_caja import MovimientoCajaModel
from .base_model import BaseModel

logger = logging.getLogger(__name__)

class PagoModel(BaseModel):
    """Modelo que representa un pago realizado"""
    
    TABLE_NAME = "pagos"
    
    # Formas de pago válidas
    FORMAS_PAGO = ['EFECTIVO', 'TRANSFERENCIA', 'TARJETA', 'DEPOSITO', 'CHEQUE']
    ESTADOS = ['REGISTRADO', 'CONFIRMADO', 'ANULADO']
    
    def __init__(self, **kwargs):
        """
        Inicializa un pago.
        
        Campos esperados:
            matricula_id, nro_cuota, monto, fecha_pago, forma_pago,
            estado, nro_comprobante, nro_transaccion, observaciones,
            registrado_por
        """
        # Campos obligatorios
        self.matricula_id = kwargs.get('matricula_id')
        self.monto = kwargs.get('monto', 0.0)
        self.fecha_pago = kwargs.get('fecha_pago')
        
        # Campos con valores por defecto
        self.forma_pago = kwargs.get('forma_pago', 'EFECTIVO')
        self.estado = kwargs.get('estado', 'REGISTRADO')
        self.nro_cuota = kwargs.get('nro_cuota')
        
        # Campos opcionales
        self.nro_comprobante = kwargs.get('nro_comprobante')
        self.nro_transaccion = kwargs.get('nro_transaccion')
        self.observaciones = kwargs.get('observaciones')
        self.registrado_por = kwargs.get('registrado_por')
        self.created_at = kwargs.get('created_at', datetime.now().isoformat())
        
        # ID (si viene de la base de datos)
        if 'id' in kwargs:
            self.id = kwargs['id']
        
        # Validaciones
        self._validar()
    
    def _validar(self):
        """Valida los datos del pago"""
        if not self.matricula_id:
            raise ValueError("matricula_id es obligatorio")
        
        if self.monto <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        
        if self.forma_pago not in self.FORMAS_PAGO:
            raise ValueError(f"Forma de pago inválida. Válidas: {self.FORMAS_PAGO}")
        
        if self.estado not in self.ESTADOS:
            raise ValueError(f"Estado inválido. Válidos: {self.ESTADOS}")
        
        if self.nro_cuota and self.nro_cuota <= 0:
            raise ValueError("El número de cuota debe ser mayor a 0")
    
    def __repr__(self):
        return f"<Pago {self.id}: ${self.monto:.2f} para Matrícula {self.matricula_id}>"
    
    @classmethod
    def buscar_por_matricula(cls, matricula_id: int):
        """Busca pagos por matrícula"""
        from database.database import db
        
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE matricula_id = ? ORDER BY fecha_pago DESC"
        rows = db.fetch_all(query, (matricula_id,))
        
        return [cls(**row) for row in rows]
    
    # Nuevo método sobrescrito para guardar el pago y registrar movimiento de caja
    def save(self):
        """
        Guarda el pago y registra automáticamente el movimiento de caja
        si está CONFIRMADO y no tiene movimiento previo
        """
        # Guardar primero para obtener ID si es nuevo
        pago_id = super().save()
        
        # Solo registrar movimiento si está CONFIRMADO y no tiene movimiento previo
        if hasattr(self, 'estado') and self.estado == 'CONFIRMADO':
            if not MovimientoCajaModel.existe_movimiento_para_pago(self.id):
                try:
                    MovimientoCajaModel.registrar_ingreso_pago(
                        pago_id=self.id,
                        monto=self.monto,
                        matricula_id=self.matricula_id,
                        nro_cuota=getattr(self, 'nro_cuota', None)
                    )
                    print(f"💰 Movimiento de caja registrado automáticamente para pago {self.id}")
                except Exception as e:
                    logger.error(f"Error al registrar movimiento de caja para pago {self.id}: {e}")
        
        return pago_id
    