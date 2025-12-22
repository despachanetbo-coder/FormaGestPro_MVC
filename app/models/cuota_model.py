# app/models/cuota_model.py
"""
Modelo de Cuota usando SQLite3 directamente.
"""
import logging
from typing import Any, List, Dict, Optional
from datetime import datetime, date

from .base_model import BaseModel

logger = logging.getLogger(__name__)

class CuotaModel(BaseModel):
    """Modelo que representa una cuota de pago"""
    
    TABLE_NAME = "cuotas"
    
    # Estados válidos
    ESTADOS = ['PENDIENTE', 'PAGADA', 'VENCIDA', 'CANCELADA']
    
    def __init__(self, **kwargs):
        """
        Inicializa una cuota.
        
        Campos esperados:
            matricula_id, nro_cuota, monto, fecha_vencimiento,
            fecha_pago, pago_id, estado, observaciones
        """
        # Campos obligatorios
        self.matricula_id = kwargs.get('matricula_id')
        self.nro_cuota = kwargs.get('nro_cuota')
        self.monto = kwargs.get('monto', 0.0)
        self.fecha_vencimiento = kwargs.get('fecha_vencimiento')
        
        # Campos con valores por defecto
        self.estado = kwargs.get('estado', 'PENDIENTE')
        
        # Campos opcionales
        self.fecha_pago = kwargs.get('fecha_pago')
        self.pago_id = kwargs.get('pago_id')
        self.observaciones = kwargs.get('observaciones')
        self.created_at = kwargs.get('created_at', datetime.now().isoformat())
        
        # ID (si viene de la base de datos)
        if 'id' in kwargs:
            self.id = kwargs['id']
        
        # Validaciones
        self._validar()
    
    def _validar(self):
        """Valida los datos de la cuota"""
        if not self.matricula_id:
            raise ValueError("matricula_id es obligatorio")
        
        if not self.nro_cuota or self.nro_cuota <= 0:
            raise ValueError("nro_cuota debe ser mayor a 0")
        
        if self.monto <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        
        if not self.fecha_vencimiento:
            raise ValueError("fecha_vencimiento es obligatoria")
        
        if self.estado not in self.ESTADOS:
            raise ValueError(f"Estado inválido. Válidos: {self.ESTADOS}")
    
    def __repr__(self):
        return f"<Cuota {self.nro_cuota}: ${self.monto:.2f} para Matrícula {self.matricula_id}>"
    
    @property
    def esta_vencida(self) -> bool:
        """Verifica si la cuota está vencida"""
        if self.estado == 'PAGADA' or self.estado == 'CANCELADA':
            return False
        
        try:
            if isinstance(self.fecha_vencimiento, str):
                fecha_venc = datetime.strptime(self.fecha_vencimiento, '%Y-%m-%d').date()
            else:
                fecha_venc = self.fecha_vencimiento
            
            hoy = date.today()
            return hoy > fecha_venc
        except:
            return False
    
    @property
    def dias_vencimiento(self) -> Optional[int]:
        """Calcula días hasta el vencimiento"""
        try:
            if isinstance(self.fecha_vencimiento, str):
                fecha_venc = datetime.strptime(self.fecha_vencimiento, '%Y-%m-%d').date()
            else:
                fecha_venc = self.fecha_vencimiento
            
            hoy = date.today()
            dias = (fecha_venc - hoy).days
            return dias
        except:
            return None
    
    @classmethod
    def buscar_por_matricula(cls, matricula_id: int) -> List['CuotaModel']:
        """Busca cuotas por matrícula"""
        from database.database import db
        
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE matricula_id = ? ORDER BY nro_cuota"
        rows = db.fetch_all(query, (matricula_id,))
        
        return [cls(**row) for row in rows]
    
    @classmethod
    def buscar_por_matricula_y_estado(cls, matricula_id: int, estado: str) -> List['CuotaModel']:
        """Busca cuotas por matrícula y estado"""
        from database.database import db
        
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE matricula_id = ? AND estado = ? ORDER BY nro_cuota"
        rows = db.fetch_all(query, (matricula_id, estado))
        
        return [cls(**row) for row in rows]
    
    @classmethod
    def buscar_vencidas(cls) -> List['CuotaModel']:
        """Busca cuotas vencidas"""
        from database.database import db
        
        hoy = date.today().isoformat()
        query = f"""
            SELECT * FROM {cls.TABLE_NAME} 
            WHERE estado = 'PENDIENTE' AND fecha_vencimiento < ?
            ORDER BY fecha_vencimiento
        """
        rows = db.fetch_all(query, (hoy,))
        
        return [cls(**row) for row in rows]
    
    def marcar_como_pagada(self, pago_id: int, fecha_pago: date = None):
        """Marca la cuota como pagada"""
        self.estado = 'PAGADA'
        self.pago_id = pago_id
        self.fecha_pago = fecha_pago.isoformat() if fecha_pago else date.today().isoformat()
        self.save()
    
    def marcar_como_vencida(self):
        """Marca la cuota como vencida"""
        if self.estado == 'PENDIENTE' and self.esta_vencida:
            self.estado = 'VENCIDA'
            self.save()
    
    @classmethod
    def actualizar_vencimientos(cls):
        """Actualiza el estado de cuotas vencidas"""
        cuotas_pendientes = cls.buscar_por_matricula_y_estado(None, 'PENDIENTE')
        
        for cuota in cuotas_pendientes:
            if cuota.esta_vencida:
                cuota.marcar_como_vencida()
        
        logger.info(f"Actualizadas {len(cuotas_pendientes)} cuotas pendientes")