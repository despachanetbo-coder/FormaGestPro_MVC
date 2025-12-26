# app/models/programa_academico_model.py
"""
Modelo Programa Académico optimizado para PostgreSQL - FormaGestPro
Mantiene todas las funcionalidades existentes
"""

import logging
import enum
from typing import Any, List, Dict, Optional, Union
from datetime import datetime, date

from .base_model import BaseModel
from app.database.connection import db  # Conexión PostgreSQL centralizada

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS Y CONSTANTES
# ============================================================================


class EstadoPrograma(enum.Enum):
    """Estados posibles de un programa académico"""

    PLANIFICADO = "PLANIFICADO"
    INICIADO = "INICIADO"
    CONCLUIDO = "CONCLUIDO"
    CANCELADO = "CANCELADO"


# ============================================================================
# MODELO PROGRAMA ACADÉMICO
# ============================================================================


class ProgramaAcademicoModel(BaseModel):
    """Modelo que representa un programa académico para PostgreSQL"""

    TABLE_NAME = "programas_academicos"

    def __init__(self, **kwargs):
        """
        Inicializa un programa académico.

        Campos esperados (según esquema PostgreSQL):
            codigo, nombre, descripcion, duracion_semanas, horas_totales,
            costo_base, descuento_contado, cupos_totales, cupos_disponibles,
            estado, fecha_inicio_planificada, fecha_inicio_real, fecha_fin_real,
            tutor_id, promocion_activa, descripcion_promocion, descuento_promocion,
            created_at, updated_at, costo_inscripcion, costo_matricula,
            promocion_fecha_limite, cuotas_mensuales, dias_entre_cuotas
        """
        super().__init__(**kwargs)

        # --------------------------------------------------------------------
        # CAMPOS OBLIGATORIOS
        # --------------------------------------------------------------------
        self.codigo = kwargs.get("codigo")
        self.nombre = kwargs.get("nombre")
        self.costo_base = float(kwargs.get("costo_base", 0.0))
        self.cupos_totales = int(kwargs.get("cupos_totales", 0))

        # --------------------------------------------------------------------
        # CAMPOS OPCIONALES
        # --------------------------------------------------------------------
        self.descripcion = kwargs.get("descripcion")
        self.duracion_semanas = kwargs.get("duracion_semanas")
        self.horas_totales = kwargs.get("horas_totales")
        self.descuento_contado = float(kwargs.get("descuento_contado", 0.0))

        # Cupos disponibles (calculado si no se proporciona)
        cupos_disponibles = kwargs.get("cupos_disponibles")
        if cupos_disponibles is not None:
            self.cupos_disponibles = int(cupos_disponibles)
        else:
            self.cupos_disponibles = self.cupos_totales

        # Estado
        estado = kwargs.get("estado", EstadoPrograma.PLANIFICADO.value)
        self.estado = estado

        # --------------------------------------------------------------------
        # FECHAS
        # --------------------------------------------------------------------
        self.fecha_inicio_planificada = kwargs.get("fecha_inicio_planificada")
        self.fecha_inicio_real = kwargs.get("fecha_inicio_real")
        self.fecha_fin_real = kwargs.get("fecha_fin_real")
        self.promocion_fecha_limite = kwargs.get("promocion_fecha_limite")

        # --------------------------------------------------------------------
        # TUTOR Y PROMOCIONES
        # --------------------------------------------------------------------
        self.tutor_id = kwargs.get("tutor_id")
        self.promocion_activa = bool(kwargs.get("promocion_activa", 0))
        self.descripcion_promocion = kwargs.get("descripcion_promocion")
        self.descuento_promocion = float(kwargs.get("descuento_promocion", 0.0))

        # --------------------------------------------------------------------
        # CAMPOS DE COSTOS ADICIONALES
        # --------------------------------------------------------------------
        self.costo_inscripcion = float(kwargs.get("costo_inscripcion", 0.0))
        self.costo_matricula = float(kwargs.get("costo_matricula", 0.0))

        # --------------------------------------------------------------------
        # CONFIGURACIÓN DE CUOTAS
        # --------------------------------------------------------------------
        self.cuotas_mensuales = int(kwargs.get("cuotas_mensuales", 1))
        self.dias_entre_cuotas = int(kwargs.get("dias_entre_cuotas", 30))

        # --------------------------------------------------------------------
        # VALIDACIÓN
        # --------------------------------------------------------------------
        self._validar()

    # ============================================================================
    # VALIDACIÓN
    # ============================================================================

    def _validar(self):
        """Valida los datos del programa"""
        if not self.codigo or not self.nombre:
            raise ValueError("Código y nombre son obligatorios")

        if self.costo_base < 0:
            raise ValueError("El costo base no puede ser negativo")

        if self.cupos_totales < 0:
            raise ValueError("Los cupos totales no pueden ser negativos")

        if self.cupos_disponibles < 0 or self.cupos_disponibles > self.cupos_totales:
            raise ValueError(
                "Los cupos disponibles deben estar entre 0 y el total de cupos"
            )

        if self.descuento_contado < 0 or self.descuento_contado > 100:
            raise ValueError("El descuento por contado debe estar entre 0 y 100")

        if self.descuento_promocion < 0 or self.descuento_promocion > 100:
            raise ValueError("El descuento por promoción debe estar entre 0 y 100")

        # Validar estado
        estados_validos = [e.value for e in EstadoPrograma]
        if self.estado not in estados_validos:
            raise ValueError(f"Estado inválido. Válidos: {estados_validos}")

    # ============================================================================
    # MÉTODOS CRUD
    # ============================================================================

    def _prepare_insert_data(self) -> Dict:
        """Preparar datos para inserción en PostgreSQL"""
        data = {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "duracion_semanas": self.duracion_semanas,
            "horas_totales": self.horas_totales,
            "costo_base": self.costo_base,
            "descuento_contado": self.descuento_contado,
            "cupos_totales": self.cupos_totales,
            "cupos_disponibles": self.cupos_disponibles,
            "estado": self.estado,
            "fecha_inicio_planificada": self.fecha_inicio_planificada,
            "fecha_inicio_real": self.fecha_inicio_real,
            "fecha_fin_real": self.fecha_fin_real,
            "tutor_id": self.tutor_id,
            "promocion_activa": self.promocion_activa,
            "descripcion_promocion": self.descripcion_promocion,
            "descuento_promocion": self.descuento_promocion,
            "costo_inscripcion": self.costo_inscripcion,
            "costo_matricula": self.costo_matricula,
            "promocion_fecha_limite": self.promocion_fecha_limite,
            "cuotas_mensuales": self.cuotas_mensuales,
            "dias_entre_cuotas": self.dias_entre_cuotas,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

        # Filtrar valores None para PostgreSQL
        return {k: v for k, v in data.items() if v is not None}

    def _prepare_update_data(self) -> Dict:
        """Preparar datos para actualización"""
        data = super()._prepare_update_data()

        # Agregar campos específicos
        campos_especificos = [
            "codigo",
            "nombre",
            "descripcion",
            "duracion_semanas",
            "horas_totales",
            "costo_base",
            "descuento_contado",
            "cupos_totales",
            "cupos_disponibles",
            "estado",
            "fecha_inicio_planificada",
            "fecha_inicio_real",
            "fecha_fin_real",
            "tutor_id",
            "promocion_activa",
            "descripcion_promocion",
            "descuento_promocion",
            "costo_inscripcion",
            "costo_matricula",
            "promocion_fecha_limite",
            "cuotas_mensuales",
            "dias_entre_cuotas",
        ]

        for campo in campos_especificos:
            if hasattr(self, campo):
                valor = getattr(self, campo)
                if valor is not None:
                    data[campo] = valor

        return data

    # ============================================================================
    # PROPIEDADES CALCULADAS (MANTENIDAS DEL CÓDIGO ORIGINAL)
    # ============================================================================

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

    @property
    def tiene_cupos_disponibles(self) -> bool:
        """Verifica si el programa tiene cupos disponibles"""
        return self.cupos_disponibles > 0

    @property
    def porcentaje_ocupacion(self) -> float:
        """Calcula el porcentaje de ocupación del programa"""
        if self.cupos_totales == 0:
            return 0.0
        ocupados = self.cupos_totales - self.cupos_disponibles
        return (ocupados / self.cupos_totales) * 100

    @property
    def esta_activo(self) -> bool:
        """Verifica si el programa está activo (INICIADO)"""
        return self.estado == EstadoPrograma.INICIADO.value

    @property
    def costo_total_estudiante(self) -> float:
        """
        Calcula el costo total para un estudiante (base + matrícula + inscripción)
        """
        return self.costo_base + self.costo_matricula + self.costo_inscripcion

    # ============================================================================
    # MÉTODOS DE CÁLCULO DE COSTOS (MANTENIDOS)
    # ============================================================================

    def calcular_costo_final(self, pago_contado: bool = False) -> float:
        """
        Calcula el costo final según modalidad de pago.

        Args:
            pago_contado (bool): Si el pago es al contado

        Returns:
            float: Costo final
        """
        if pago_contado:
            return self.costo_con_descuento_contado
        return self.costo_con_promocion if self.promocion_activa else self.costo_base

    def calcular_costos_matricula(self) -> Dict[str, float]:
        """
        Calcula los costos desglosados para matrícula.

        Returns:
            Dict[str, float]: Diccionario con costos desglosados
        """
        return {
            "costo_base": self.costo_base,
            "costo_matricula": self.costo_matricula,
            "costo_inscripcion": self.costo_inscripcion,
            "descuento_contado": self.descuento_contado,
            "descuento_promocion": (
                self.descuento_promocion if self.promocion_activa else 0.0
            ),
            "total_sin_descuento": self.costo_total_estudiante,
            "total_con_descuento_contado": self.costo_total_estudiante
            * (1 - self.descuento_contado / 100),
            "total_con_promocion": (
                self.costo_total_estudiante * (1 - self.descuento_promocion / 100)
                if self.promocion_activa
                else self.costo_total_estudiante
            ),
        }

    # ============================================================================
    # MÉTODOS DE GESTIÓN DE CUPOS (ACTUALIZADOS PARA PostgreSQL)
    # ============================================================================

    def ocupar_cupo(self) -> int:
        """Ocupa un cupo disponible"""
        if self.cupos_disponibles <= 0:
            raise ValueError("No hay cupos disponibles")

        self.cupos_disponibles -= 1
        self.updated_at = datetime.now().isoformat()
        self.save()

        logger.info(
            f"📝 Cupo ocupado en programa {self.codigo}. Disponibles: {self.cupos_disponibles}"
        )
        return self.cupos_disponibles

    def liberar_cupo(self) -> int:
        """Libera un cupo ocupado"""
        if self.cupos_disponibles >= self.cupos_totales:
            raise ValueError("No hay cupos ocupados para liberar")

        self.cupos_disponibles += 1
        self.updated_at = datetime.now().isoformat()
        self.save()

        logger.info(
            f"📝 Cupo liberado en programa {self.codigo}. Disponibles: {self.cupos_disponibles}"
        )
        return self.cupos_disponibles

    @classmethod
    def actualizar_cupos(cls, programa_id: int, cantidad: int = -1) -> bool:
        """
        Actualizar cupos disponibles de un programa.

        Args:
            programa_id (int): ID del programa
            cantidad (int): Cantidad a modificar (negativo para ocupar, positivo para liberar)

        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            # Obtener programa actual
            programa = cls.find_by_id(programa_id)
            if not programa:
                logger.error(f"❌ Programa {programa_id} no encontrado")
                return False

            # Calcular nuevos cupos (asegurar que no sea negativo)
            nuevos_cupos = max(0, programa.cupos_disponibles + cantidad)

            # Actualizar en base de datos
            query = f"""
                UPDATE {cls.TABLE_NAME} 
                SET cupos_disponibles = %s, 
                    updated_at = CURRENT_TIMESTAMP 
                WHERE id = %s
            """
            db.execute_query(query, (nuevos_cupos, programa_id), fetch=False)

            logger.info(
                f"✅ Cupos actualizados: Programa {programa_id} - {cantidad} cupos"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Error en actualizar_cupos: {e}")
            return False

    # ============================================================================
    # MÉTODOS DE ESTADO DEL PROGRAMA (MANTENIDOS)
    # ============================================================================

    def iniciar_programa(self, fecha_inicio_real: date = None):
        """Inicia el programa"""
        self.estado = EstadoPrograma.INICIADO.value
        if fecha_inicio_real:
            self.fecha_inicio_real = fecha_inicio_real.isoformat()
        else:
            self.fecha_inicio_real = date.today().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.save()
        logger.info(f"🚀 Programa {self.codigo} iniciado")

    def concluir_programa(self, fecha_fin_real: date = None):
        """Concluye el programa"""
        self.estado = EstadoPrograma.CONCLUIDO.value
        if fecha_fin_real:
            self.fecha_fin_real = fecha_fin_real.isoformat()
        else:
            self.fecha_fin_real = date.today().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.save()
        logger.info(f"🎓 Programa {self.codigo} concluido")

    def cancelar_programa(self):
        """Cancela el programa"""
        self.estado = EstadoPrograma.CANCELADO.value
        self.updated_at = datetime.now().isoformat()
        self.save()
        logger.info(f"❌ Programa {self.codigo} cancelado")

    # ============================================================================
    # MÉTODOS DE PROMOCIONES (MANTENIDOS)
    # ============================================================================

    def activar_promocion(self, descuento: float, descripcion: str = ""):
        """Activa una promoción"""
        if descuento < 0 or descuento > 100:
            raise ValueError("El descuento debe estar entre 0 y 100")

        self.promocion_activa = True
        self.descuento_promocion = descuento
        self.descripcion_promocion = descripcion
        self.updated_at = datetime.now().isoformat()
        self.save()
        logger.info(f"🏷️ Promoción activada en programa {self.codigo}: {descuento}%")

    def desactivar_promocion(self):
        """Desactiva la promoción"""
        self.promocion_activa = False
        self.updated_at = datetime.now().isoformat()
        self.save()
        logger.info(f"🏷️ Promoción desactivada en programa {self.codigo}")

    # ============================================================================
    # MÉTODOS ESTÁTICOS DE BÚSQUEDA (ACTUALIZADOS PARA PostgreSQL)
    # ============================================================================

    @classmethod
    def crear_programa(cls, datos: Dict) -> "ProgramaAcademicoModel":
        """
        Crea un nuevo programa con validaciones.

        Args:
            datos (Dict): Datos del programa

        Returns:
            ProgramaAcademicoModel: Programa creado
        """
        # Validaciones básicas
        required_fields = ["codigo", "nombre", "costo_base", "cupos_totales"]
        for field in required_fields:
            if field not in datos or not datos[field]:
                raise ValueError(f"Campo requerido: {field}")

        # Validar estado si se proporciona
        if "estado" in datos and datos["estado"]:
            estados_validos = [e.value for e in EstadoPrograma]
            if datos["estado"] not in estados_validos:
                raise ValueError(
                    f"Estado inválido. Debe ser: {', '.join(estados_validos)}"
                )

        # Verificar que el código sea único
        existente = cls.buscar_por_codigo(datos["codigo"])
        if existente:
            raise ValueError(f"Ya existe un programa con código {datos['codigo']}")

        # Crear y guardar
        programa = cls(**datos)
        programa.save()

        logger.info(f"✅ Programa creado: {programa.codigo} - {programa.nombre}")
        return programa

    @classmethod
    def buscar_por_codigo(cls, codigo: str) -> Optional["ProgramaAcademicoModel"]:
        """Busca un programa por su código"""
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE codigo = %s"
        row = db.fetch_one(query, (codigo,))
        return cls(**row) if row else None

    @classmethod
    def buscar_por_estado(cls, estado: str) -> List["ProgramaAcademicoModel"]:
        """Busca programas por estado"""
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE estado = %s ORDER BY nombre"
        rows = db.fetch_all(query, (estado,))
        return [cls(**row) for row in rows]

    @classmethod
    def buscar_por_tutor(cls, tutor_id: int) -> List["ProgramaAcademicoModel"]:
        """Busca programas por tutor"""
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE tutor_id = %s ORDER BY nombre"
        rows = db.fetch_all(query, (tutor_id,))
        return [cls(**row) for row in rows]

    @classmethod
    def buscar_con_cupos_disponibles(cls) -> List["ProgramaAcademicoModel"]:
        """Busca programas con cupos disponibles"""
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE cupos_disponibles > 0 ORDER BY nombre"
        rows = db.fetch_all(query)
        return [cls(**row) for row in rows]

    @classmethod
    def buscar_promociones_activas(cls) -> List["ProgramaAcademicoModel"]:
        """Busca programas con promociones activas"""
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE promocion_activa = TRUE ORDER BY nombre"
        rows = db.fetch_all(query)
        return [cls(**row) for row in rows]

    @classmethod
    def buscar_por_nombre(cls, nombre: str) -> List["ProgramaAcademicoModel"]:
        """Busca programas por nombre (búsqueda parcial)"""
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE nombre ILIKE %s ORDER BY nombre"
        rows = db.fetch_all(query, (f"%{nombre}%",))
        return [cls(**row) for row in rows]

    # ============================================================================
    # MÉTODOS DE ESTADÍSTICAS (ACTUALIZADOS)
    # ============================================================================

    @classmethod
    def contar_total(cls) -> int:
        """Contar el total de programas registrados"""
        try:
            query = "SELECT COUNT(*) as total FROM programas_academicos"
            resultado = db.fetch_one(query)
            return resultado["total"] if resultado else 0
        except Exception as e:
            logger.error(f"❌ Error contando programas: {e}")
            return 0

    @classmethod
    def obtener_estadisticas(cls) -> Dict[str, Any]:
        """Obtiene estadísticas de programas"""
        try:
            # Totales
            query_total = "SELECT COUNT(*) as total FROM programas_academicos"
            query_activos = "SELECT COUNT(*) as activos FROM programas_academicos WHERE estado = 'INICIADO'"
            query_planificados = "SELECT COUNT(*) as planificados FROM programas_academicos WHERE estado = 'PLANIFICADO'"
            query_concluidos = "SELECT COUNT(*) as concluidos FROM programas_academicos WHERE estado = 'CONCLUIDO'"
            query_promociones = "SELECT COUNT(*) as promociones FROM programas_academicos WHERE promocion_activa = TRUE"

            total = db.fetch_one(query_total)
            activos = db.fetch_one(query_activos)
            planificados = db.fetch_one(query_planificados)
            concluidos = db.fetch_one(query_concluidos)
            promociones = db.fetch_one(query_promociones)

            return {
                "total": total["total"] if total else 0,
                "activos": activos["activos"] if activos else 0,
                "planificados": planificados["planificados"] if planificados else 0,
                "concluidos": concluidos["concluidos"] if concluidos else 0,
                "con_promocion": promociones["promociones"] if promociones else 0,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {
                "total": 0,
                "activos": 0,
                "planificados": 0,
                "concluidos": 0,
                "con_promocion": 0,
                "error": str(e),
            }

    # ============================================================================
    # MÉTODOS PARA EL CONTROLADOR (REEMPLAZAN NECESIDAD DE PAGOMODEL)
    # ============================================================================

    @classmethod
    def obtener_ingresos_por_programa(
        cls, programa_id: int, fecha_inicio: str = None, fecha_fin: str = None
    ) -> float:
        """
        Obtiene el total de ingresos de un programa.
        Reemplaza la funcionalidad que necesitaba PagoModel.

        Args:
            programa_id (int): ID del programa
            fecha_inicio (str, optional): Fecha de inicio (YYYY-MM-DD)
            fecha_fin (str, optional): Fecha de fin (YYYY-MM-DD)

        Returns:
            float: Total de ingresos del programa
        """
        try:
            from .ingreso_model import IngresoModel

            # Obtener todas las matrículas del programa
            from .matricula_model import MatriculaModel

            matriculas = MatriculaModel.buscar_por_programa(programa_id)

            if not matriculas:
                return 0.0

            # Sumar ingresos de todas las matrículas
            total_ingresos = 0.0

            for matricula in matriculas:
                # Obtener ingresos de esta matrícula
                ingresos = IngresoModel.buscar_por_matricula(matricula.id)

                for ingreso in ingresos:
                    # Filtrar por fechas si se especifican
                    if fecha_inicio and fecha_fin:
                        if fecha_inicio <= ingreso.fecha <= fecha_fin:
                            total_ingresos += ingreso.monto
                    else:
                        total_ingresos += ingreso.monto

            return total_ingresos

        except ImportError as e:
            logger.error(f"❌ Error importando modelos: {e}")
            return 0.0
        except Exception as e:
            logger.error(f"❌ Error calculando ingresos por programa: {e}")
            return 0.0

    @classmethod
    def obtener_estadisticas_financieras(cls, programa_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas financieras del programa.

        Args:
            programa_id (int): ID del programa

        Returns:
            Dict[str, Any]: Estadísticas financieras
        """
        try:
            from .matricula_model import MatriculaModel

            # Obtener programa
            programa = cls.find_by_id(programa_id)
            if not programa:
                return {}

            # Obtener matrículas del programa
            matriculas = MatriculaModel.buscar_por_programa(programa_id)

            # Calcular estadísticas
            total_matriculas = len(matriculas)
            ingresos_potenciales = sum(m.monto_final for m in matriculas)
            ingresos_reales = sum(m.monto_pagado for m in matriculas)
            saldo_pendiente = sum(m.saldo_pendiente for m in matriculas)

            # Porcentaje de cobranza
            porcentaje_cobranza = 0.0
            if ingresos_potenciales > 0:
                porcentaje_cobranza = (ingresos_reales / ingresos_potenciales) * 100

            return {
                "programa_id": programa_id,
                "programa_nombre": programa.nombre,
                "total_matriculas": total_matriculas,
                "ingresos_potenciales": round(ingresos_potenciales, 2),
                "ingresos_reales": round(ingresos_reales, 2),
                "saldo_pendiente": round(saldo_pendiente, 2),
                "porcentaje_cobranza": round(porcentaje_cobranza, 2),
                "cupos_disponibles": programa.cupos_disponibles,
                "cupos_totales": programa.cupos_totales,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas financieras: {e}")
            return {}

    # ============================================================================
    # REPRESENTACIÓN
    # ============================================================================

    def __repr__(self):
        return f"<Programa {self.codigo}: {self.nombre}>"

    def __str__(self):
        return f"{self.codigo} - {self.nombre} ({self.estado}) - Cupos: {self.cupos_disponibles}/{self.cupos_totales}"
