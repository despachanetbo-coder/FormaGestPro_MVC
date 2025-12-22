# models/cuota.py
"""
Modelo de Cuota Programada usando SQLite3 directamente.
"""
import logging
from datetime import datetime, date
from .base_model import BaseModel

logger = logging.getLogger(__name__)

class CuotaModel(BaseModel):
    """Modelo que representa una cuota programada"""
    
    TABLE_NAME = "cuotas_programadas"
    
    # Estados válidos
    ESTADOS = ['PENDIENTE', 'PAGADA', 'VENCIDA', 'CANCELADA']
    
    def __init__(self, **kwargs):
        """
        Inicializa una cuota.
        
        Campos esperados:
            matricula_id, nro_cuota, monto, fecha_vencimiento, estado,
            fecha_pago, pago_id, interes_mora, dias_mora
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
        self.interes_mora = kwargs.get('interes_mora', 0.0)
        self.dias_mora = kwargs.get('dias_mora', 0)
        self.created_at = kwargs.get('created_at', datetime.now().isoformat())
        
        # ID (si viene de la base de datos)
        if 'id' in kwargs:
            self.id = kwargs['id']
        
        # Validaciones
        self._validar()
    
    def _validar(self):
        """Valida los datos de la cuota"""
        if not self.matricula_id or not self.nro_cuota:
            raise ValueError("matricula_id y nro_cuota son obligatorios")
        
        if self.monto <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        
        if not self.fecha_vencimiento:
            raise ValueError("fecha_vencimiento es obligatoria")
        
        if self.estado not in self.ESTADOS:
            raise ValueError(f"Estado inválido. Válidos: {self.ESTADOS}")
    
    def __repr__(self):
        return f"<Cuota {self.nro_cuota}: ${self.monto:.2f} (Vence: {self.fecha_vencimiento})>"
    
    def marcar_como_pagada(self, pago_id: int):
        """Marca la cuota como pagada"""
        self.estado = 'PAGADA'
        self.pago_id = pago_id
        self.fecha_pago = date.today().isoformat()
        self.save()
    
    def calcular_mora(self):
        """Calcula interés por mora si la cuota está vencida"""
        if self.estado == 'PENDIENTE':
            hoy = date.today()
            vencimiento = date.fromisoformat(self.fecha_vencimiento)
            
            if hoy > vencimiento:
                self.dias_mora = (hoy - vencimiento).days
                # Interés simple: 1% por día de mora
                self.interes_mora = self.monto * 0.00 * self.dias_mora # Coloqué intencionalmente 0.00% porque interés por mora no es parte de los requisitos del usuario
                self.estado = 'VENCIDA'
                self.save()
    
    @classmethod
    def buscar_por_matricula(cls, matricula_id: int):
        """Busca cuotas por matrícula"""
        from database.database import db
        
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE matricula_id = ? ORDER BY nro_cuota"
        rows = db.fetch_all(query, (matricula_id,))
        
        return [cls(**row) for row in rows]
    
    @classmethod
    def buscar_por_matricula_y_estado(cls, matricula_id: int, estado: str):
        """Busca cuotas por matrícula y estado"""
        from database.database import db
        
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE matricula_id = ? AND estado = ? ORDER BY nro_cuota"
        rows = db.fetch_all(query, (matricula_id, estado))
        
        return [cls(**row) for row in rows]