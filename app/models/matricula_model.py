# app/models/matricula_model.py
"""
Modelo de Matrícula optimizado para PostgreSQL - FormaGestPro
Actualizado para usar IngresoModel en lugar de PagoModel
"""

import logging
from typing import Optional, Dict, List, Any
from datetime import datetime, date

from .base_model import BaseModel
from .ingreso_model import IngresoModel  # Reemplaza PagoModel
from app.database.connection import db

logger = logging.getLogger(__name__)


class MatriculaModel(BaseModel):
    """Modelo que representa una matrícula de estudiante en un programa"""

    TABLE_NAME = "matriculas"

    # ============================================================================
    # CONSTANTES
    # ============================================================================

    # Estados de pago (compatibles con PostgreSQL)
    ESTADO_PAGO_PENDIENTE = "PENDIENTE"
    ESTADO_PAGO_PARCIAL = "PARCIAL"
    ESTADO_PAGO_PAGADO = "PAGADO"
    ESTADO_PAGO_MORA = "MORA"

    ESTADOS_PAGO = [
        ESTADO_PAGO_PENDIENTE,
        ESTADO_PAGO_PARCIAL,
        ESTADO_PAGO_PAGADO,
        ESTADO_PAGO_MORA,
    ]

    # Estados académicos
    ESTADO_ACAD_PREINSCRITO = "PREINSCRITO"
    ESTADO_ACAD_INSCRITO = "INSCRITO"
    ESTADO_ACAD_EN_CURSO = "EN_CURSO"
    ESTADO_ACAD_CONCLUIDO = "CONCLUIDO"
    ESTADO_ACAD_RETIRADO = "RETIRADO"

    ESTADOS_ACADEMICOS = [
        ESTADO_ACAD_PREINSCRITO,
        ESTADO_ACAD_INSCRITO,
        ESTADO_ACAD_EN_CURSO,
        ESTADO_ACAD_CONCLUIDO,
        ESTADO_ACAD_RETIRADO,
    ]

    # Modalidades de pago
    MODALIDAD_CONTADO = "CONTADO"
    MODALIDAD_CUOTAS = "CUOTAS"

    MODALIDADES_PAGO = [MODALIDAD_CONTADO, MODALIDAD_CUOTAS]

    # ============================================================================
    # CONSTRUCTOR
    # ============================================================================

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # --------------------------------------------------------------------
        # CAMPOS OBLIGATORIOS
        # --------------------------------------------------------------------
        self.estudiante_id = kwargs.get("estudiante_id")
        self.programa_id = kwargs.get("programa_id")
        self.modalidad_pago = kwargs.get("modalidad_pago", self.MODALIDAD_CONTADO)

        # --------------------------------------------------------------------
        # CAMPOS FINANCIEROS
        # --------------------------------------------------------------------
        self.monto_total = float(kwargs.get("monto_total", 0.0))
        self.descuento_aplicado = float(kwargs.get("descuento_aplicado", 0.0))
        self.monto_final = float(kwargs.get("monto_final", self.monto_total))
        self.monto_pagado = float(kwargs.get("monto_pagado", 0.0))

        # --------------------------------------------------------------------
        # ESTADOS
        # --------------------------------------------------------------------
        self.estado_pago = kwargs.get("estado_pago", self.ESTADO_PAGO_PENDIENTE)
        self.estado_academico = kwargs.get(
            "estado_academico", self.ESTADO_ACAD_PREINSCRITO
        )

        # --------------------------------------------------------------------
        # CAMPOS DE PLAN DE PAGO (si es CUOTAS)
        # --------------------------------------------------------------------
        self.plan_pago_id = kwargs.get("plan_pago_id")

        # --------------------------------------------------------------------
        # FECHAS
        # --------------------------------------------------------------------
        # Fecha de matrícula
        fecha_matricula = kwargs.get("fecha_matricula")
        if isinstance(fecha_matricula, datetime):
            self.fecha_matricula = fecha_matricula.isoformat()
        elif isinstance(fecha_matricula, str):
            self.fecha_matricula = fecha_matricula
        else:
            self.fecha_matricula = datetime.now().isoformat()

        # Fechas académicas
        self.fecha_inicio = kwargs.get("fecha_inicio")
        self.fecha_conclusion = kwargs.get("fecha_conclusion")

        # --------------------------------------------------------------------
        # CAMPOS ADICIONALES
        # --------------------------------------------------------------------
        self.coordinador_id = kwargs.get("coordinador_id")
        self.observaciones = kwargs.get("observaciones")

        # --------------------------------------------------------------------
        # VALIDACIONES
        # --------------------------------------------------------------------
        self._validar()

    # ============================================================================
    # VALIDACIONES
    # ============================================================================

    def _validar(self):
        """Valida los datos de la matrícula"""
        if not self.estudiante_id or not self.programa_id:
            raise ValueError("estudiante_id y programa_id son obligatorios")

        if self.modalidad_pago not in self.MODALIDADES_PAGO:
            raise ValueError(
                f"Modalidad de pago inválida. Válidas: {self.MODALIDADES_PAGO}"
            )

        if self.modalidad_pago == self.MODALIDAD_CUOTAS and not self.plan_pago_id:
            raise ValueError("Para modalidad CUOTAS se requiere plan_pago_id")

        if self.modalidad_pago == self.MODALIDAD_CONTADO and self.plan_pago_id:
            raise ValueError("Para modalidad CONTADO no debe haber plan_pago_id")

        if self.estado_pago not in self.ESTADOS_PAGO:
            raise ValueError(f"Estado de pago inválido. Válidos: {self.ESTADOS_PAGO}")

        if self.estado_academico not in self.ESTADOS_ACADEMICOS:
            raise ValueError(
                f"Estado académico inválido. Válidos: {self.ESTADOS_ACADEMICOS}"
            )

        if self.monto_total < 0 or self.monto_final < 0 or self.monto_pagado < 0:
            raise ValueError("Los montos no pueden ser negativos")

        if self.monto_pagado > self.monto_final:
            raise ValueError("El monto pagado no puede ser mayor al monto final")

    # ============================================================================
    # MÉTODOS CRUD
    # ============================================================================

    def _prepare_insert_data(self) -> Dict:
        """Preparar datos para inserción"""
        data = {
            "estudiante_id": self.estudiante_id,
            "programa_id": self.programa_id,
            "modalidad_pago": self.modalidad_pago,
            "plan_pago_id": self.plan_pago_id,
            "monto_total": self.monto_total,
            "descuento_aplicado": self.descuento_aplicado,
            "monto_final": self.monto_final,
            "monto_pagado": self.monto_pagado,
            "estado_pago": self.estado_pago,
            "estado_academico": self.estado_academico,
            "fecha_matricula": self.fecha_matricula,
            "fecha_inicio": self.fecha_inicio,
            "fecha_conclusion": self.fecha_conclusion,
            "coordinador_id": self.coordinador_id,
            "observaciones": self.observaciones,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

        # Filtrar valores None
        return {k: v for k, v in data.items() if v is not None}

    def _prepare_update_data(self) -> Dict:
        """Preparar datos para actualización"""
        data = super()._prepare_update_data()

        # Agregar campos específicos
        campos_especificos = [
            "estudiante_id",
            "programa_id",
            "modalidad_pago",
            "plan_pago_id",
            "monto_total",
            "descuento_aplicado",
            "monto_final",
            "monto_pagado",
            "estado_pago",
            "estado_academico",
            "fecha_matricula",
            "fecha_inicio",
            "fecha_conclusion",
            "coordinador_id",
            "observaciones",
        ]

        for campo in campos_especificos:
            if hasattr(self, campo):
                valor = getattr(self, campo)
                if valor is not None:
                    data[campo] = valor

        return data

    # ============================================================================
    # PROPIEDADES CALCULADAS
    # ============================================================================

    @property
    def saldo_pendiente(self) -> float:
        """Calcula el saldo pendiente de pago"""
        return max(0.0, self.monto_final - self.monto_pagado)

    @property
    def porcentaje_pagado(self) -> float:
        """Calcula el porcentaje pagado"""
        if self.monto_final == 0:
            return 0.0
        porcentaje = (self.monto_pagado / self.monto_final) * 100
        return min(100.0, round(porcentaje, 2))

    @property
    def tiene_pagos(self) -> bool:
        """Verifica si la matrícula tiene pagos registrados"""
        return self.monto_pagado > 0

    @property
    def esta_pagada(self) -> bool:
        """Verifica si la matrícula está completamente pagada"""
        return self.saldo_pendiente <= 0.01  # Tolerancia para floats

    # ============================================================================
    # MÉTODOS DE PAGOS (ACTUALIZADOS PARA INGRESOMODEL)
    # ============================================================================

    def registrar_pago(
        self,
        monto: float,
        forma_pago: str,
        nro_comprobante: str = None,
        nro_transaccion: str = None,
        observaciones: str = None,
        nro_cuota: int = None,
    ) -> IngresoModel:
        """
        Registra un pago para esta matrícula usando IngresoModel.

        Args:
            monto (float): Monto del pago
            forma_pago (str): Forma de pago utilizada
            nro_comprobante (str, optional): Número de comprobante
            nro_transaccion (str, optional): Número de transacción
            observaciones (str, optional): Observaciones del pago
            nro_cuota (int, optional): Número de cuota si aplica

        Returns:
            IngresoModel: El ingreso/pago registrado
        """
        # Validar monto
        if monto <= 0:
            raise ValueError("El monto debe ser mayor a 0")

        if monto > self.saldo_pendiente:
            raise ValueError(
                f"Monto excede el saldo pendiente: {self.saldo_pendiente:.2f}"
            )

        # Determinar tipo de ingreso basado en modalidad
        if self.modalidad_pago == self.MODALIDAD_CUOTAS and nro_cuota:
            tipo_ingreso = IngresoModel.TIPO_MATRICULA_CUOTA
            concepto = f"Cuota {nro_cuota} - Matrícula #{self.id}"
        else:
            tipo_ingreso = IngresoModel.TIPO_MATRICULA_CONTADO
            concepto = f"Pago contado - Matrícula #{self.id}"

        # Crear ingreso usando IngresoModel
        ingreso = IngresoModel(
            tipo_ingreso=tipo_ingreso,
            matricula_id=self.id,
            nro_cuota=nro_cuota,
            fecha=date.today().isoformat(),
            monto=monto,
            concepto=concepto,
            descripcion=observaciones,
            forma_pago=forma_pago,
            estado=IngresoModel.ESTADO_CONFIRMADO,  # Confirmado automáticamente
            nro_comprobante=nro_comprobante,
            nro_transaccion=nro_transaccion,
            registrado_por=self.coordinador_id,  # Podría venir de usuario actual
        )

        # Guardar el ingreso
        ingreso.save()

        # Actualizar matrícula
        self.monto_pagado += monto

        # Actualizar estado de pago
        if self.esta_pagada:
            self.estado_pago = self.ESTADO_PAGO_PAGADO
        elif self.monto_pagado > 0:
            self.estado_pago = self.ESTADO_PAGO_PARCIAL

        self.save()

        logger.info(f"✅ Pago registrado: ${monto:.2f} para matrícula #{self.id}")

        # Actualizar cuotas si existen
        self._actualizar_cuota_pagada(nro_cuota, ingreso.id)

        return ingreso

    def _actualizar_cuota_pagada(self, nro_cuota: int = None, ingreso_id: int = None):
        """
        Actualiza las cuotas relacionadas con este pago.

        Args:
            nro_cuota (int, optional): Número de cuota pagada
            ingreso_id (int): ID del ingreso/pago registrado
        """
        try:
            from .cuota_model import CuotaModel

            if nro_cuota:
                # Buscar cuota específica
                cuota = CuotaModel.buscar_por_matricula_y_numero(self.id, nro_cuota)
                if cuota:
                    cuota.marcar_como_pagada(ingreso_id)
                    logger.info(f"✅ Cuota {nro_cuota} marcada como pagada")
            else:
                # Buscar primera cuota pendiente
                cuotas_pendientes = CuotaModel.buscar_por_matricula_y_estado(
                    self.id, "PENDIENTE"
                )
                if cuotas_pendientes:
                    cuota = cuotas_pendientes[0]
                    cuota.marcar_como_pagada(ingreso_id)
                    logger.info(f"✅ Cuota {cuota.nro_cuota} marcada como pagada")

        except ImportError:
            logger.warning("ℹ️ Modelo CuotaModel no disponible")
        except Exception as e:
            logger.warning(f"⚠️ No se pudieron actualizar cuotas: {e}")

    def obtener_pagos(self) -> List[IngresoModel]:
        """
        Obtiene todos los pagos/ingresos asociados a esta matrícula.

        Returns:
            List[IngresoModel]: Lista de pagos/ingresos
        """
        return IngresoModel.buscar_por_matricula(self.id)

    def obtener_total_pagado(self) -> float:
        """
        Obtiene el total pagado sumando todos los ingresos confirmados.

        Returns:
            float: Total pagado
        """
        pagos = self.obtener_pagos()
        total = sum(
            pago.monto
            for pago in pagos
            if pago.estado == IngresoModel.ESTADO_CONFIRMADO
        )
        return total

    # ============================================================================
    # MÉTODOS ACADÉMICOS
    # ============================================================================

    def iniciar_curso(self, fecha_inicio: date = None):
        """Inicia el curso para esta matrícula"""
        self.estado_academico = self.ESTADO_ACAD_EN_CURSO
        if fecha_inicio:
            self.fecha_inicio = fecha_inicio.isoformat()
        else:
            self.fecha_inicio = date.today().isoformat()
        self.save()
        logger.info(f"🎓 Matrícula #{self.id} iniciada")

    def concluir_matricula(self, fecha_conclusion: date = None):
        """Concluye la matrícula"""
        if not self.esta_pagada:
            raise ValueError("No se puede concluir matrícula con pagos pendientes")

        self.estado_academico = self.ESTADO_ACAD_CONCLUIDO
        if fecha_conclusion:
            self.fecha_conclusion = fecha_conclusion.isoformat()
        else:
            self.fecha_conclusion = date.today().isoformat()
        self.save()
        logger.info(f"🎓 Matrícula #{self.id} concluida")

    def retirar_estudiante(self, motivo: str = None):
        """Retira al estudiante del programa"""
        self.estado_academico = self.ESTADO_ACAD_RETIRADO
        if motivo:
            self.observaciones = f"RETIRADO: {motivo}" + (
                f" | {self.observaciones}" if self.observaciones else ""
            )
        self.save()
        logger.info(f"🚪 Matrícula #{self.id} retirada")

    # ============================================================================
    # MÉTODOS ESTÁTICOS
    # ============================================================================

    @classmethod
    def matricular_estudiante(
        cls,
        estudiante_id: int,
        programa_id: int,
        modalidad_pago: str = "CONTADO",
        plan_pago_id: int = None,
        observaciones: str = None,
    ) -> "MatriculaModel":
        """
        Crea una nueva matrícula con validaciones.

        Args:
            estudiante_id (int): ID del estudiante
            programa_id (int): ID del programa
            modalidad_pago (str): Modalidad de pago (CONTADO/CUOTAS)
            plan_pago_id (int, optional): ID del plan de pago (si CUOTAS)
            observaciones (str, optional): Observaciones adicionales

        Returns:
            MatriculaModel: Matrícula creada
        """
        from .programa_academico_model import ProgramaAcademicoModel

        # 1. Verificar que no exista matrícula previa
        existente = cls.buscar_por_estudiante_y_programa(estudiante_id, programa_id)
        if existente:
            raise ValueError("El estudiante ya está matriculado en este programa")

        # 2. Obtener programa y verificar cupos
        programa = ProgramaAcademicoModel.find_by_id(programa_id)
        if not programa:
            raise ValueError(f"Programa con ID {programa_id} no existe")

        if programa.cupos_disponibles <= 0:
            raise ValueError("El programa no tiene cupos disponibles")

        # 3. Calcular montos según modalidad
        monto_total = float(programa.costo_base)

        if modalidad_pago == cls.MODALIDAD_CONTADO:
            # Aplicar descuento por contado
            descuento_contado = float(programa.descuento_contado or 0)
            descuento = monto_total * (descuento_contado / 100)
            monto_final = monto_total - descuento
        else:
            # Sin descuento para cuotas
            monto_final = monto_total
            descuento = 0.0

        # 4. Crear matrícula
        matricula = cls(
            estudiante_id=estudiante_id,
            programa_id=programa_id,
            modalidad_pago=modalidad_pago,
            plan_pago_id=plan_pago_id,
            monto_total=monto_total,
            descuento_aplicado=descuento,
            monto_final=monto_final,
            observaciones=observaciones,
        )

        # 5. Guardar matrícula
        matricula.save()

        # 6. Actualizar cupos del programa
        programa.ocupar_cupo()

        # 7. Generar cuotas si es pago en cuotas
        if modalidad_pago == cls.MODALIDAD_CUOTAS and plan_pago_id:
            matricula._generar_cuotas()

        logger.info(
            f"✅ Matrícula creada: Estudiante {estudiante_id} en Programa {programa_id}"
        )
        return matricula

    @classmethod
    def buscar_por_estudiante(cls, estudiante_id: int) -> List["MatriculaModel"]:
        """
        Busca matrículas por estudiante.

        Args:
            estudiante_id (int): ID del estudiante

        Returns:
            List[MatriculaModel]: Lista de matrículas encontradas
        """
        try:
            query = f"""
                SELECT * FROM {cls.TABLE_NAME} 
                WHERE estudiante_id = %s 
                ORDER BY fecha_matricula DESC
            """
            rows = db.fetch_all(query, (estudiante_id,))
            return [cls(**row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Error al buscar matrículas por estudiante: {e}")
            return []

    @classmethod
    def buscar_por_programa(cls, programa_id: int) -> List["MatriculaModel"]:
        """
        Busca matrículas por programa.

        Args:
            programa_id (int): ID del programa

        Returns:
            List[MatriculaModel]: Lista de matrículas encontradas
        """
        try:
            query = f"""
                SELECT * FROM {cls.TABLE_NAME} 
                WHERE programa_id = %s 
                ORDER BY fecha_matricula DESC
            """
            rows = db.fetch_all(query, (programa_id,))
            return [cls(**row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Error al buscar matrículas por programa: {e}")
            return []

    @classmethod
    def buscar_por_estudiante_y_programa(
        cls, estudiante_id: int, programa_id: int
    ) -> Optional["MatriculaModel"]:
        """
        Busca una matrícula específica por estudiante y programa.

        Args:
            estudiante_id (int): ID del estudiante
            programa_id (int): ID del programa

        Returns:
            MatriculaModel or None: Matrícula encontrada o None
        """
        try:
            query = f"""
                SELECT * FROM {cls.TABLE_NAME} 
                WHERE estudiante_id = %s AND programa_id = %s
                LIMIT 1
            """
            result = db.fetch_one(query, (estudiante_id, programa_id))
            return cls(**result) if result else None
        except Exception as e:
            logger.error(f"❌ Error al buscar matrícula específica: {e}")
            return None

    @classmethod
    def buscar_por_estado_pago(cls, estado_pago: str) -> List["MatriculaModel"]:
        """
        Busca matrículas por estado de pago.

        Args:
            estado_pago (str): Estado de pago a buscar

        Returns:
            List[MatriculaModel]: Lista de matrículas encontradas
        """
        try:
            query = f"""
                SELECT * FROM {cls.TABLE_NAME} 
                WHERE estado_pago = %s 
                ORDER BY fecha_matricula DESC
            """
            rows = db.fetch_all(query, (estado_pago,))
            return [cls(**row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Error al buscar matrículas por estado de pago: {e}")
            return []

    # ============================================================================
    # MÉTODOS DE GENERACIÓN DE CUOTAS (INTERNOS)
    # ============================================================================

    def _generar_cuotas(self):
        """Genera cuotas mensuales fijas según el plan de pago (si existe)"""
        try:
            from .cuota_model import CuotaModel

            if not self.plan_pago_id:
                return

            # Obtener plan de pago
            from .plan_pago_model import PlanPagoModel

            plan = PlanPagoModel.find_by_id(self.plan_pago_id)

            if not plan:
                logger.warning(f"⚠️ Plan de pago {self.plan_pago_id} no encontrado")
                return

            # Generar cuotas (lógica simplificada)
            # En una implementación completa, aquí se calcularían fechas y montos
            logger.info(
                f"ℹ️ Generando {plan.nro_cuotas} cuotas para matrícula #{self.id}"
            )

            # Nota: La lógica completa de generación de cuotas debería implementarse aquí
            # basándose en el plan de pago y el monto final

        except ImportError:
            logger.warning("ℹ️ Modelos de cuotas/planes no disponibles")
        except Exception as e:
            logger.error(f"❌ Error generando cuotas: {e}")

    # ============================================================================
    # REPRESENTACIÓN
    # ============================================================================

    def __repr__(self):
        return f"<Matricula {self.id}: Estudiante {self.estudiante_id} en Programa {self.programa_id}>"

    def __str__(self):
        estado_pago = self.estado_pago
        estado_acad = self.estado_academico
        return f"Matrícula #{self.id} - {estado_pago}/{estado_acad} - ${self.monto_pagado:.2f}/${self.monto_final:.2f}"
