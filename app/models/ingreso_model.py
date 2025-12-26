# app/models/ingreso_model.py
"""
Modelo unificado de ingresos para PostgreSQL - FormaGestPro
Combina funcionalidades de:
1. PagoModel (pagos de matrículas)
2. IngresoGenericoModel (otros ingresos)
3. Nuevas funcionalidades para PostgreSQL
"""

import logging
from datetime import datetime, date
from typing import Optional, Dict, List, Any, Union
import json

from .base_model import BaseModel
from app.database.connection import db  # Conexión PostgreSQL centralizada

logger = logging.getLogger(__name__)


class IngresoModel(BaseModel):
    """Modelo unificado de ingresos - PostgreSQL"""

    TABLE_NAME = "ingresos"

    # ============================================================================
    # CONSTANTES (DE TODAS LAS FUENTES)
    # ============================================================================

    # Tipos de ingreso (unificados)
    TIPO_MATRICULA_CUOTA = "MATRICULA_CUOTA"
    TIPO_MATRICULA_CONTADO = "MATRICULA_CONTADO"
    TIPO_OTRO_INGRESO = "OTRO_INGRESO"

    # Estados (de PagoModel e IngresoGenericoModel)
    ESTADO_REGISTRADO = "REGISTRADO"
    ESTADO_CONFIRMADO = "CONFIRMADO"
    ESTADO_ANULADO = "ANULADO"
    ESTADO_VENCIDO = "VENCIDO"  # De PagoModel

    # Formas de pago (unificadas)
    FORMA_EFECTIVO = "EFECTIVO"
    FORMA_TRANSFERENCIA = "TRANSFERENCIA"
    FORMA_TARJETA = "TARJETA"
    FORMA_CHEQUE = "CHEQUE"
    FORMA_DEPOSITO = "DEPOSITO"
    FORMA_QR = "QR"

    # Campos requeridos (de PagoModel)
    CAMPOS_REQUERIDOS = ["monto", "concepto"]

    # ============================================================================
    # CONSTRUCTOR (FUSIÓN DE TODOS)
    # ============================================================================

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # --------------------------------------------------------------------
        # CAMPOS DE PagoModel (matrículas)
        # --------------------------------------------------------------------
        self.matricula_id = kwargs.get("matricula_id")
        self.nro_cuota = kwargs.get("nro_cuota")

        # --------------------------------------------------------------------
        # CAMPOS DE IngresoGenericoModel (otros ingresos)
        # --------------------------------------------------------------------
        self.tipo_ingreso = kwargs.get("tipo_ingreso", self.TIPO_OTRO_INGRESO)

        # Si viene de pago de matrícula, determinar tipo automáticamente
        if self.matricula_id and not self.tipo_ingreso:
            self.tipo_ingreso = self.TIPO_MATRICULA_CONTADO  # Por defecto

        # --------------------------------------------------------------------
        # CAMPOS COMUNES (AMBOS MODELOS)
        # --------------------------------------------------------------------
        # Fecha - manejo flexible
        fecha_param = kwargs.get("fecha")
        if isinstance(fecha_param, date):
            self.fecha = fecha_param.isoformat()
        elif isinstance(fecha_param, datetime):
            self.fecha = fecha_param.date().isoformat()
        elif fecha_param:
            self.fecha = fecha_param
        else:
            self.fecha = date.today().isoformat()

        # Monto - siempre float
        monto_param = kwargs.get("monto", 0.0)
        try:
            self.monto = float(monto_param)
        except (ValueError, TypeError):
            self.monto = 0.0

        # Concepto y descripción
        self.concepto = kwargs.get("concepto", "")
        self.descripcion = kwargs.get("descripcion", "")

        # Forma de pago - normalizar
        forma_pago = kwargs.get("forma_pago", self.FORMA_EFECTIVO)
        formas_validas = [
            self.FORMA_EFECTIVO,
            self.FORMA_TRANSFERENCIA,
            self.FORMA_TARJETA,
            self.FORMA_CHEQUE,
            self.FORMA_DEPOSITO,
            self.FORMA_QR,
        ]
        self.forma_pago = (
            forma_pago if forma_pago in formas_validas else self.FORMA_EFECTIVO
        )

        # Estado - normalizar (CONFIRMADO → PAGADO, etc.)
        estado_original = kwargs.get("estado", self.ESTADO_REGISTRADO)
        if estado_original == "PAGADO":  # De PagoModel antiguo
            self.estado = self.ESTADO_CONFIRMADO
        elif estado_original == "REGISTRADO":  # De IngresoGenericoModel
            self.estado = self.ESTADO_REGISTRADO
        else:
            self.estado = estado_original

        # --------------------------------------------------------------------
        # CAMPOS DE COMPROBANTE Y TRANSACCIÓN
        # --------------------------------------------------------------------
        self.nro_comprobante = kwargs.get("nro_comprobante")
        self.nro_transaccion = kwargs.get("nro_transaccion")
        self.registrado_por = kwargs.get("registrado_por")

        # --------------------------------------------------------------------
        # CAMPOS ESPECIALES DE PagoModel
        # --------------------------------------------------------------------
        self.fecha_pago = kwargs.get("fecha_pago", self.fecha)  # Para compatibilidad
        self.fecha_vencimiento = kwargs.get("fecha_vencimiento")
        self.fecha_registro = kwargs.get(
            "fecha_registro", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        self.observaciones = kwargs.get("observaciones")

        # Validación básica
        self._validar()

    # ============================================================================
    # MÉTODOS DE VALIDACIÓN (DE PagoModel)
    # ============================================================================

    def _validar(self):
        """Validación unificada de datos"""
        # Validación de monto
        if self.monto <= 0:
            logger.warning(
                f"⚠️ Ingreso #{getattr(self, 'id', 'Nuevo')} tiene monto {self.monto}"
            )

        # Validación de estado
        estados_permitidos = [
            self.ESTADO_REGISTRADO,
            self.ESTADO_CONFIRMADO,
            self.ESTADO_ANULADO,
            self.ESTADO_VENCIDO,
            "PAGADO",
            "REGISTRADO",
        ]  # Para compatibilidad
        if self.estado not in estados_permitidos:
            logger.warning(
                f"⚠️ Estado no estándar en ingreso #{getattr(self, 'id', 'Nuevo')}: {self.estado}"
            )

        # Validación de matrícula si es tipo MATRICULA
        if self.tipo_ingreso in [
            self.TIPO_MATRICULA_CUOTA,
            self.TIPO_MATRICULA_CONTADO,
        ]:
            if not self.matricula_id:
                raise ValueError("Para ingresos de matrícula se requiere matricula_id")

    # ============================================================================
    # MÉTODOS CRUD (SOBREESCRITOS)
    # ============================================================================

    def _prepare_insert_data(self) -> Dict:
        """Preparar datos para inserción - PostgreSQL"""
        data = {
            "tipo_ingreso": self.tipo_ingreso,
            "matricula_id": self.matricula_id,
            "nro_cuota": self.nro_cuota,
            "fecha": self.fecha,
            "monto": self.monto,
            "concepto": self.concepto,
            "descripcion": self.descripcion,
            "forma_pago": self.forma_pago,
            "estado": self.estado,
            "nro_comprobante": self.nro_comprobante,
            "nro_transaccion": self.nro_transaccion,
            "registrado_por": self.registrado_por,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

        # Filtrar valores None (PostgreSQL maneja NULL)
        return {k: v for k, v in data.items() if v is not None}

    def _prepare_update_data(self) -> Dict:
        """Preparar datos para actualización"""
        data = super()._prepare_update_data()

        # Agregar campos específicos si existen
        campos_especificos = [
            "tipo_ingreso",
            "matricula_id",
            "nro_cuota",
            "fecha",
            "monto",
            "concepto",
            "descripcion",
            "forma_pago",
            "estado",
            "nro_comprobante",
            "nro_transaccion",
            "registrado_por",
        ]

        for campo in campos_especificos:
            if hasattr(self, campo):
                valor = getattr(self, campo)
                if valor is not None:
                    data[campo] = valor

        return data

    # ============================================================================
    # MÉTODOS DE ESTADO (DE PagoModel)
    # ============================================================================

    def marcar_como_confirmado(
        self,
        forma_pago: str = None,
        fecha_pago: str = None,
        nro_comprobante: str = None,
        registrado_por: str = None,
    ):
        """
        Marcar ingreso como CONFIRMADO (equivalente a PAGADO en PagoModel).

        Args:
            forma_pago (str, optional): Forma de pago utilizada
            fecha_pago (str, optional): Fecha del pago (YYYY-MM-DD)
            nro_comprobante (str, optional): Número de comprobante
            registrado_por (str, optional): Usuario que registró el pago
        """
        try:
            # Actualizar campos
            self.estado = self.ESTADO_CONFIRMADO
            self.fecha_pago = fecha_pago or date.today().isoformat()

            if forma_pago:
                self.forma_pago = forma_pago

            if nro_comprobante:
                self.nro_comprobante = nro_comprobante

            if registrado_por:
                self.registrado_por = registrado_por

            # Guardar cambios
            self.save()

            logger.info(f"💰 Ingreso #{self.id} marcado como CONFIRMADO")

            # Registrar movimiento de caja automático
            self._registrar_movimiento_caja()

        except Exception as e:
            logger.error(f"❌ Error al marcar ingreso como confirmado: {e}")
            raise

    def marcar_como_anulado(self, motivo: str = None):
        """
        Marcar ingreso como ANULADO.

        Args:
            motivo (str, optional): Motivo de la anulación
        """
        try:
            # Actualizar estado
            self.estado = self.ESTADO_ANULADO

            if motivo:
                self.observaciones = f"ANULADO: {motivo}" + (
                    f" | {self.observaciones}" if self.observaciones else ""
                )

            # Guardar cambios
            self.save()

            # Eliminar movimiento de caja asociado si existe
            self._eliminar_movimiento_caja()

            logger.info(f"❌ Ingreso #{self.id} marcado como ANULADO")

        except Exception as e:
            logger.error(f"❌ Error al anular ingreso: {e}")
            raise

    def verificar_vencimiento(self) -> bool:
        """
        Verifica si el ingreso está vencido (para cuotas).

        Returns:
            bool: True si está vencido, False en caso contrario
        """
        if not self.fecha_vencimiento or self.estado == self.ESTADO_CONFIRMADO:
            return False

        try:
            fecha_vencimiento = datetime.strptime(
                self.fecha_vencimiento, "%Y-%m-%d"
            ).date()
            fecha_actual = date.today()

            if fecha_actual > fecha_vencimiento:
                self.estado = self.ESTADO_VENCIDO
                self.save()
                return True

            return False

        except Exception as e:
            logger.error(f"❌ Error al verificar vencimiento: {e}")
            return False

    # ============================================================================
    # MÉTODOS DE MOVIMIENTO DE CAJA (DE PagoModel)
    # ============================================================================

    def _registrar_movimiento_caja(self):
        """Registra automáticamente un movimiento de caja para el ingreso."""
        try:
            if not self.id:
                raise ValueError(
                    "El ingreso debe tener un ID para registrar movimiento de caja"
                )

            # Verificar si ya existe un movimiento para este ingreso
            if self._existe_movimiento_caja():
                logger.warning(
                    f"⚠️ Ya existe movimiento de caja para el ingreso #{self.id}"
                )
                return

            # Registrar movimiento de caja
            from .movimiento_caja_model import MovimientoCajaModel

            MovimientoCajaModel.registrar_ingreso(
                ingreso_id=self.id,
                monto=self.monto,
                matricula_id=self.matricula_id,
                nro_cuota=self.nro_cuota,
                concepto=self.concepto,
                forma_pago=self.forma_pago,
            )

            logger.info(f"💰 Movimiento de caja registrado para ingreso #{self.id}")

        except Exception as e:
            logger.error(f"❌ Error al registrar movimiento de caja: {e}")
            # No lanzar excepción para no interrumpir el flujo principal

    def _eliminar_movimiento_caja(self):
        """Elimina el movimiento de caja asociado al ingreso."""
        try:
            if not self.id:
                return

            from .movimiento_caja_model import MovimientoCajaModel

            MovimientoCajaModel.eliminar_por_ingreso(self.id)

        except Exception as e:
            logger.error(f"❌ Error al eliminar movimiento de caja: {e}")

    def _existe_movimiento_caja(self) -> bool:
        """Verifica si existe movimiento de caja para este ingreso."""
        try:
            query = """
                SELECT EXISTS(
                    SELECT 1 FROM movimientos_caja 
                    WHERE origen_tipo = 'INGRESO' AND origen_id = %s
                )
            """
            result = db.fetch_one(query, (self.id,))
            return result["exists"] if result else False
        except Exception as e:
            logger.error(f"❌ Error verificando movimiento de caja: {e}")
            return False

    # ============================================================================
    # MÉTODOS DE BÚSQUEDA ESTÁTICOS (DE AMBOS MODELOS Y NUEVOS)
    # ============================================================================

    @classmethod
    def buscar_por_matricula(
        cls, matricula_id: int, estado: str = None
    ) -> List["IngresoModel"]:
        """
        Busca ingresos por ID de matrícula (de PagoModel).

        Args:
            matricula_id (int): ID de la matrícula
            estado (str, optional): Filtrar por estado específico

        Returns:
            List[IngresoModel]: Lista de ingresos encontrados
        """
        try:
            query = f"SELECT * FROM {cls.TABLE_NAME} WHERE matricula_id = %s"
            params = [matricula_id]

            if estado:
                query += " AND estado = %s"
                params.append(estado)

            query += " ORDER BY fecha DESC, nro_cuota"

            rows = db.fetch_all(query, tuple(params))
            return [cls(**row) for row in rows]

        except Exception as e:
            logger.error(f"❌ Error al buscar ingresos por matrícula: {e}")
            return []

    @classmethod
    def buscar_por_estudiante(cls, estudiante_id: int) -> List["IngresoModel"]:
        """Buscar todos los ingresos de un estudiante"""
        query = """
            SELECT i.* 
            FROM ingresos i
            JOIN matriculas m ON i.matricula_id = m.id
            WHERE m.estudiante_id = %s
            ORDER BY i.fecha DESC
        """
        results = db.fetch_all(query, (estudiante_id,))
        return [cls(**row) for row in results]

    @classmethod
    def buscar_por_estado(cls, estado: str) -> List["IngresoModel"]:
        """
        Busca ingresos por estado (de PagoModel).

        Args:
            estado (str): Estado a buscar

        Returns:
            List[IngresoModel]: Lista de ingresos encontrados
        """
        try:
            query = (
                f"SELECT * FROM {cls.TABLE_NAME} WHERE estado = %s ORDER BY fecha DESC"
            )
            rows = db.fetch_all(query, (estado,))
            return [cls(**row) for row in rows]

        except Exception as e:
            logger.error(f"❌ Error al buscar ingresos por estado: {e}")
            return []

    @classmethod
    def buscar_por_rango_fechas(
        cls, fecha_inicio: str, fecha_fin: str, estado: str = None
    ) -> List["IngresoModel"]:
        """
        Busca ingresos por rango de fechas (de PagoModel).

        Args:
            fecha_inicio (str): Fecha de inicio (YYYY-MM-DD)
            fecha_fin (str): Fecha de fin (YYYY-MM-DD)
            estado (str, optional): Filtrar por estado

        Returns:
            List[IngresoModel]: Lista de ingresos encontrados
        """
        try:
            query = f"""
                SELECT * FROM {cls.TABLE_NAME} 
                WHERE fecha BETWEEN %s AND %s
            """
            params = [fecha_inicio, fecha_fin]

            if estado:
                query += " AND estado = %s"
                params.append(estado)

            query += " ORDER BY fecha DESC, created_at DESC"

            rows = db.fetch_all(query, tuple(params))
            return [cls(**row) for row in rows]

        except Exception as e:
            logger.error(f"❌ Error al buscar ingresos por rango de fechas: {e}")
            return []

    @classmethod
    def buscar_ingresos_genericos(
        cls, fecha_inicio: str = None, fecha_fin: str = None
    ) -> List["IngresoModel"]:
        """
        Busca ingresos genéricos (no de matrículas) - de IngresoGenericoModel.

        Args:
            fecha_inicio (str, optional): Fecha de inicio (YYYY-MM-DD)
            fecha_fin (str, optional): Fecha de fin (YYYY-MM-DD)

        Returns:
            List[IngresoModel]: Lista de ingresos genéricos
        """
        try:
            query = f"""
                SELECT * FROM {cls.TABLE_NAME} 
                WHERE tipo_ingreso = %s
            """
            params = [cls.TIPO_OTRO_INGRESO]

            if fecha_inicio and fecha_fin:
                query += " AND fecha BETWEEN %s AND %s"
                params.extend([fecha_inicio, fecha_fin])

            query += " ORDER BY fecha DESC, created_at DESC"

            rows = db.fetch_all(query, tuple(params))
            return [cls(**row) for row in rows]

        except Exception as e:
            logger.error(f"❌ Error al buscar ingresos genéricos: {e}")
            return []

    # ============================================================================
    # MÉTODOS DE CÁLCULO Y REPORTES
    # ============================================================================

    @classmethod
    def total_ingresos_por_periodo(
        cls, fecha_inicio: str, fecha_fin: str, tipo_ingreso: str = None
    ) -> float:
        """
        Calcular total de ingresos en un período.

        Args:
            fecha_inicio (str): Fecha de inicio (YYYY-MM-DD)
            fecha_fin (str): Fecha de fin (YYYY-MM-DD)
            tipo_ingreso (str, optional): Filtrar por tipo de ingreso

        Returns:
            float: Total de ingresos en el período
        """
        try:
            query = """
                SELECT COALESCE(SUM(monto), 0) as total
                FROM ingresos
                WHERE fecha BETWEEN %s AND %s
                AND estado = %s
            """
            params = [fecha_inicio, fecha_fin, cls.ESTADO_CONFIRMADO]

            if tipo_ingreso:
                query += " AND tipo_ingreso = %s"
                params.append(tipo_ingreso)

            result = db.fetch_one(query, tuple(params))
            return float(result["total"]) if result else 0.0

        except Exception as e:
            logger.error(f"❌ Error calculando total de ingresos: {e}")
            return 0.0

    @classmethod
    def resumen_por_tipo(cls, fecha_inicio: str, fecha_fin: str) -> Dict[str, float]:
        """
        Obtiene resumen de ingresos por tipo.

        Args:
            fecha_inicio (str): Fecha de inicio (YYYY-MM-DD)
            fecha_fin (str): Fecha de fin (YYYY-MM-DD)

        Returns:
            Dict[str, float]: Diccionario con total por tipo
        """
        try:
            query = """
                SELECT 
                    tipo_ingreso,
                    COALESCE(SUM(monto), 0) as total
                FROM ingresos
                WHERE fecha BETWEEN %s AND %s
                AND estado = %s
                GROUP BY tipo_ingreso
                ORDER BY total DESC
            """

            results = db.fetch_all(
                query, (fecha_inicio, fecha_fin, cls.ESTADO_CONFIRMADO)
            )

            resumen = {}
            for row in results:
                resumen[row["tipo_ingreso"]] = float(row["total"])

            return resumen

        except Exception as e:
            logger.error(f"❌ Error en resumen por tipo: {e}")
            return {}

    # ============================================================================
    # MÉTODOS PARA COMPATIBILIDAD
    # ============================================================================

    @classmethod
    def buscar_pagos_por_matricula(cls, matricula_id: int) -> List["IngresoModel"]:
        """Alias para compatibilidad con código existente que usa 'pagos'"""
        return cls.buscar_por_matricula(matricula_id)

    @classmethod
    def crear_ingreso_generico(cls, datos: Dict) -> "IngresoModel":
        """
        Crea un ingreso genérico (para compatibilidad con IngresoGenericoModel).

        Args:
            datos (Dict): Datos del ingreso

        Returns:
            IngresoModel: Ingreso creado
        """
        # Forzar tipo OTRO_INGRESO
        datos["tipo_ingreso"] = cls.TIPO_OTRO_INGRESO

        ingreso = cls(**datos)
        ingreso.save()

        return ingreso

    # ============================================================================
    # REPRESENTACIÓN
    # ============================================================================

    def __repr__(self):
        """Representación en string del ingreso."""
        tipo_str = self.tipo_ingreso or "OTRO"
        return f"<Ingreso #{self.id}: ${self.monto:.2f} - {tipo_str} - {self.estado}>"
