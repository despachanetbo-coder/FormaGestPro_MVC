# app/models/cuota_model.py
"""
Modelo de Cuota usando PostgreSQL directamente.
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
    ESTADOS = ["PENDIENTE", "PAGADA", "VENCIDA", "CANCELADA"]

    def __init__(self, **kwargs):
        """
        Inicializa una cuota.

        Campos esperados:
            matricula_id, nro_cuota, monto, fecha_vencimiento,
            fecha_pago, pago_id, estado, observaciones
        """
        # Campos obligatorios
        self.matricula_id = kwargs.get("matricula_id")
        self.nro_cuota = kwargs.get("nro_cuota")
        self.monto = kwargs.get("monto", 0.0)
        self.fecha_vencimiento = kwargs.get("fecha_vencimiento")

        # Campos con valores por defecto
        self.estado = kwargs.get("estado", "PENDIENTE")

        # Campos opcionales
        self.fecha_pago = kwargs.get("fecha_pago")
        self.pago_id = kwargs.get("pago_id")
        self.observaciones = kwargs.get("observaciones")
        self.created_at = kwargs.get("created_at", datetime.now().isoformat())

        # ID (si viene de la base de datos)
        if "id" in kwargs:
            self.id = kwargs["id"]

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
        if self.estado == "PAGADA" or self.estado == "CANCELADA":
            return False

        try:
            if isinstance(self.fecha_vencimiento, str):
                fecha_venc = datetime.strptime(
                    self.fecha_vencimiento, "%Y-%m-%d"
                ).date()
            else:
                fecha_venc = self.fecha_vencimiento

            if fecha_venc is None:
                return False

            hoy = date.today()
            return hoy > fecha_venc
        except:
            return False

    @property
    def dias_vencimiento(self) -> Optional[int]:
        """Calcula días hasta el vencimiento"""
        try:
            if isinstance(self.fecha_vencimiento, str):
                fecha_venc = datetime.strptime(
                    self.fecha_vencimiento, "%Y-%m-%d"
                ).date()
            else:
                fecha_venc = self.fecha_vencimiento

            if fecha_venc is None:
                return None

            hoy = date.today()
            dias = (fecha_venc - hoy).days
            return dias
        except:
            return None

    @classmethod
    def buscar_por_matricula(cls, matricula_id: int) -> List["CuotaModel"]:
        """Busca cuotas por matrícula"""
        from database.database import db

        query = (
            f"SELECT * FROM {cls.TABLE_NAME} WHERE matricula_id = ? ORDER BY nro_cuota"
        )
        rows = db.fetch_all(query, (matricula_id,))

        return [cls(**row) for row in rows]

    @classmethod
    def buscar_por_matricula_y_estado(
        cls, matricula_id: int, estado: str
    ) -> List["CuotaModel"]:
        """Busca cuotas por matrícula y estado"""
        from database.database import db

        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE matricula_id = ? AND estado = ? ORDER BY nro_cuota"
        rows = db.fetch_all(query, (matricula_id, estado))

        return [cls(**row) for row in rows]

    @classmethod
    def buscar_por_estado(cls, estado: str) -> List["CuotaModel"]:
        """Busca cuotas por estado sin filtrar por matrícula"""
        from database.database import db

        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE estado = ? ORDER BY fecha_vencimiento"
        rows = db.fetch_all(query, (estado,))

        return [cls(**row) for row in rows]

    @classmethod
    def buscar_vencidas(cls) -> List["CuotaModel"]:
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

    def marcar_como_pagada(self, pago_id: int, fecha_pago: Optional[date] = None):
        """Marca la cuota como pagada"""
        self.estado = "PAGADA"
        self.pago_id = pago_id
        self.fecha_pago = (
            fecha_pago.isoformat() if fecha_pago else date.today().isoformat()
        )
        self.save()

    def marcar_como_vencida(self):
        """Marca la cuota como vencida"""
        if self.estado == "PENDIENTE" and self.esta_vencida:
            self.estado = "VENCIDA"
            self.save()

    @classmethod
    def actualizar_vencimientos(cls):
        """Actualiza el estado de cuotas vencidas"""
        cuotas_pendientes = cls.buscar_por_estado("PENDIENTE")

        for cuota in cuotas_pendientes:
            if cuota.esta_vencida:
                cuota.marcar_como_vencida()

        logger.info(f"Actualizadas {len(cuotas_pendientes)} cuotas pendientes")

    def save(self):
        """
        Guarda la cuota en la base de datos.

        Si la cuota ya tiene un ID, actualiza el registro existente.
        Si no tiene ID, inserta un nuevo registro.

        Returns:
            bool: True si la operación fue exitosa, False en caso contrario.
        """
        try:
            # Preparar los datos para guardar
            cuota_data = {
                "matricula_id": self.matricula_id,
                "nro_cuota": self.nro_cuota,
                "monto": float(self.monto),  # Asegurar que sea float
                "fecha_vencimiento": (
                    self.fecha_vencimiento
                    if hasattr(self.fecha_vencimiento, "isoformat")
                    else str(self.fecha_vencimiento)
                ),
                "estado": self.estado,
            }

            # Agregar campos opcionales si tienen valor
            if self.fecha_pago:
                cuota_data["fecha_pago"] = (
                    self.fecha_pago
                    if hasattr(self.fecha_pago, "isoformat")
                    else str(self.fecha_pago)
                )

            if self.pago_id:
                cuota_data["pago_id"] = self.pago_id

            if self.observaciones:
                cuota_data["observaciones"] = self.observaciones

            if hasattr(self, "created_at") and self.created_at:
                cuota_data["created_at"] = (
                    self.created_at.isoformat()
                    if hasattr(self.created_at, "isoformat")
                    else str(self.created_at)
                )

            # Usar el método save del BaseModel
            if hasattr(self, "id") and self.id:
                # Actualizar cuota existente
                result = self.update(
                    table=self.TABLE_NAME,
                    data=cuota_data,
                    condition="id = %s",
                    params=(self.id,),
                )

                if result is not None and result > 0:
                    logger.debug(f"✅ Cuota {self.id} actualizada exitosamente")
                    return True
                else:
                    logger.error(f"❌ No se pudo actualizar la cuota {self.id}")
                    return False
            else:
                # Insertar nueva cuota
                # Verificar que no exista ya una cuota con el mismo nro_cuota para esta matrícula
                existing_query = f"""
                    SELECT id FROM {self.TABLE_NAME} 
                    WHERE matricula_id = %s AND nro_cuota = %s
                """
                existing = self.fetch_one(
                    existing_query, (self.matricula_id, self.nro_cuota)
                )

                if existing:
                    # Ya existe, actualizar
                    self.id = existing["id"]
                    return self.save()

                # Insertar nueva cuota
                result = self.insert(
                    table=self.TABLE_NAME, data=cuota_data, returning="id"
                )

                if result:
                    if isinstance(result, dict):
                        self.id = result.get("id")
                    elif isinstance(result, (list, tuple)):
                        if isinstance(result[0], dict):
                            self.id = result[0].get("id")
                        else:
                            self.id = result[0]
                    else:
                        self.id = result

                    logger.debug(f"✅ Cuota creada exitosamente con ID: {self.id}")
                    return True
                else:
                    logger.error("❌ No se pudo crear la cuota")
                    return False

        except Exception as e:
            logger.error(f"❌ Error al guardar la cuota: {e}")
            return False

    def delete(self):
        """
        Elimina la cuota de la base de datos.

        Returns:
            bool: True si la eliminación fue exitosa, False en caso contrario.
        """
        try:
            if not hasattr(self, "id") or not self.id:
                logger.error("❌ No se puede eliminar una cuota sin ID")
                return False

            result = super().delete(
                table=self.TABLE_NAME, condition="id = %s", params=(self.id,)
            )

            if result is not None and result > 0:
                logger.debug(f"✅ Cuota {self.id} eliminada exitosamente")
                # Limpiar el ID después de eliminar
                del self.id
                return True
            else:
                logger.error(f"❌ No se pudo eliminar la cuota {self.id}")
                return False

        except Exception as e:
            logger.error(f"❌ Error al eliminar la cuota: {e}")
            return False

    @classmethod
    def find_by_id(cls, cuota_id: int) -> Optional["CuotaModel"]:
        """
        Busca una cuota por su ID.

        Args:
            cuota_id (int): ID de la cuota a buscar

        Returns:
            CuotaModel: Instancia de CuotaModel si se encuentra, None en caso contrario
        """
        try:
            query = f"SELECT * FROM {cls.TABLE_NAME} WHERE id = %s"
            result = cls().fetch_one(query, (cuota_id,))

            if result:
                return cls(**result)
            return None
        except Exception as e:
            logger.error(f"❌ Error al buscar cuota por ID {cuota_id}: {e}")
            return None

    @classmethod
    def find_by_pago_id(cls, pago_id: int) -> Optional["CuotaModel"]:
        """
        Busca una cuota por el ID del pago asociado.

        Args:
            pago_id (int): ID del pago

        Returns:
            CuotaModel: Instancia de CuotaModel si se encuentra, None en caso contrario
        """
        try:
            query = f"SELECT * FROM {cls.TABLE_NAME} WHERE pago_id = %s"
            result = cls().fetch_one(query, (pago_id,))

            if result:
                return cls(**result)
            return None
        except Exception as e:
            logger.error(f"❌ Error al buscar cuota por pago_id {pago_id}: {e}")
            return None

    def to_dict(self) -> Dict:
        """
        Convierte la cuota a un diccionario.

        Returns:
            dict: Diccionario con todos los atributos de la cuota
        """
        data = {
            "matricula_id": self.matricula_id,
            "nro_cuota": self.nro_cuota,
            "monto": float(self.monto),
            "fecha_vencimiento": (
                self.fecha_vencimiento
                if hasattr(self.fecha_vencimiento, "isoformat")
                else str(self.fecha_vencimiento)
            ),
            "estado": self.estado,
            "esta_vencida": self.esta_vencida,
        }

        # Agregar campos opcionales
        if hasattr(self, "id") and self.id:
            data["id"] = self.id

        if self.fecha_pago:
            data["fecha_pago"] = (
                self.fecha_pago
                if hasattr(self.fecha_pago, "isoformat")
                else str(self.fecha_pago)
            )

        if self.pago_id:
            data["pago_id"] = self.pago_id

        if self.observaciones:
            data["observaciones"] = self.observaciones

        if hasattr(self, "created_at") and self.created_at:
            data["created_at"] = (
                self.created_at.isoformat()
                if hasattr(self.created_at, "isoformat")
                else str(self.created_at)
            )

        return data

    @classmethod
    def create_table_if_not_exists(cls):
        """
        Crea la tabla de cuotas si no existe.

        Returns:
            bool: True si la tabla fue creada o ya existía, False en caso de error
        """
        try:
            query = f"""
                CREATE TABLE IF NOT EXISTS {cls.TABLE_NAME} (
                    id SERIAL PRIMARY KEY,
                    matricula_id INTEGER NOT NULL,
                    nro_cuota INTEGER NOT NULL,
                    monto DECIMAL(10, 2) NOT NULL,
                    fecha_vencimiento DATE NOT NULL,
                    fecha_pago DATE,
                    pago_id INTEGER,
                    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
                    observaciones TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Restricciones
                    CONSTRAINT fk_matricula 
                        FOREIGN KEY (matricula_id) REFERENCES matriculas(id)
                        ON DELETE CASCADE,
                    CONSTRAINT chk_monto_positivo 
                        CHECK (monto > 0),
                    CONSTRAINT chk_estado_valido 
                        CHECK (estado IN ('PENDIENTE', 'PAGADA', 'VENCIDA', 'CANCELADA')),
                    CONSTRAINT unique_matricula_nro_cuota 
                        UNIQUE (matricula_id, nro_cuota)
                )
            """

            # Crear índices para mejorar rendimiento
            index_queries = [
                f"CREATE INDEX IF NOT EXISTS idx_cuotas_matricula ON {cls.TABLE_NAME}(matricula_id)",
                f"CREATE INDEX IF NOT EXISTS idx_cuotas_estado ON {cls.TABLE_NAME}(estado)",
                f"CREATE INDEX IF NOT EXISTS idx_cuotas_vencimiento ON {cls.TABLE_NAME}(fecha_vencimiento)",
                f"CREATE INDEX IF NOT EXISTS idx_cuotas_pago_id ON {cls.TABLE_NAME}(pago_id)",
            ]

            model = cls()

            # Crear tabla
            result = model.execute_query(query, fetch=False, commit=True)
            if result is None:
                logger.error("❌ Error al crear tabla de cuotas")
                return False

            # Crear índices
            for idx_query in index_queries:
                model.execute_query(idx_query, fetch=False, commit=True)

            logger.info(f"✅ Tabla {cls.TABLE_NAME} verificada/creada correctamente")
            return True

        except Exception as e:
            logger.error(f"❌ Error al crear tabla de cuotas: {e}")
            return False
