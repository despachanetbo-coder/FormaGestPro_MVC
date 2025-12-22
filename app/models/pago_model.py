# app/models/pago.py
"""
Modelo de Pago usando SQLite3 directamente.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from .movimiento_caja_model import MovimientoCajaModel
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
    
    @classmethod
    def registrar_pago(cls, matricula_id: int, monto: float, tipo_pago: str, 
                      concepto: str = None, fecha_vencimiento: str = None,
                      estado: str = 'PENDIENTE', **kwargs) -> 'PagoModel':
        """Registrar un nuevo pago"""
        from database.database import db
        
        try:
            # Validar tipo de pago
            tipos_validos = ['MATRICULA', 'CUOTA', 'CONTADO', 'OTRO']
            if tipo_pago not in tipos_validos:
                raise ValueError(f"Tipo de pago inválido. Válidos: {tipos_validos}")
            
            # Crear objeto de pago
            pago_data = {
                'matricula_id': matricula_id,
                'monto': monto,
                'tipo_pago': tipo_pago,
                'concepto': concepto or f"Pago {tipo_pago.lower()}",
                'estado': estado,
                'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Agregar fecha de vencimiento si se proporciona
            if fecha_vencimiento:
                pago_data['fecha_vencimiento'] = fecha_vencimiento
            
            # Agregar campos adicionales de kwargs
            for key, value in kwargs.items():
                if key not in pago_data:
                    pago_data[key] = value
            
            # Crear y guardar pago
            pago = cls(**pago_data)
            pago.save()
            
            logger.info(f"✅ Pago registrado: Matrícula {matricula_id}, Monto ${monto:.2f}, Tipo: {tipo_pago}")
            return pago
            
        except Exception as e:
            logger.error(f"Error al registrar pago: {e}")
            raise
        
    @classmethod
    def generar_cuotas(cls, matricula_id: int, total: float, num_cuotas: int, 
                      fecha_inicio: str, intervalo_dias: int = 30) -> List['PagoModel']:
        """Generar cuotas para una matrícula"""
        try:
            cuotas = []
            fecha_actual = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            
            for i in range(num_cuotas):
                # Calcular fecha de vencimiento
                fecha_vencimiento = fecha_actual + timedelta(days=intervalo_dias * i)
                
                # Calcular monto de cuota
                monto_cuota = total / num_cuotas
                
                # Registrar cuota
                cuota = cls.registrar_pago(
                    matricula_id=matricula_id,
                    monto=monto_cuota,
                    tipo_pago='CUOTA',
                    concepto=f"Cuota {i + 1}/{num_cuotas}",
                    fecha_vencimiento=fecha_vencimiento.strftime('%Y-%m-%d'),
                    estado='PENDIENTE'
                )
                
                cuotas.append(cuota)
                logger.info(f"  Cuota {i + 1}: ${monto_cuota:.2f} - Vence: {fecha_vencimiento.strftime('%d/%m/%Y')}")
            
            logger.info(f"✅ {len(cuotas)} cuotas generadas para matrícula {matricula_id}")
            return cuotas
            
        except Exception as e:
            logger.error(f"Error al generar cuotas: {e}")
            raise