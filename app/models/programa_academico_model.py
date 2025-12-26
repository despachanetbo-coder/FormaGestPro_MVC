# app/models/programa_academico_model.py
"""
Modelo para gestión de programas académicos - FormaGestPro MVC

Este modelo maneja todas las operaciones de base de datos relacionadas con programas académicos,
siguiendo estrictamente el esquema PostgreSQL definido en PgSQL_Scheme.sql y utilizando la
arquitectura de conexión centralizada a través de BaseModel.

Características principales:
- Totalmente compatible con el esquema PostgreSQL oficial
- Usa la conexión centralizada mediante BaseModel y connection.py
- Implementa todas las operaciones CRUD y consultas especializadas
- Manejo robusto de errores con logging detallado
- Enumeraciones para los dominios de PostgreSQL
- Documentación completa en español
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from .base_model import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


# ============================================================================
# ENUMERACIONES PARA DOMINIOS DE POSTGRESQL
# ============================================================================


class EstadoPrograma(Enum):
    """
    Enumeración que representa el dominio d_estado_programa de PostgreSQL.

    CREATE DOMAIN d_estado_programa AS TEXT
        CHECK (VALUE IN ('PLANIFICADO', 'INICIADO', 'CONCLUIDO', 'CANCELADO'));

    Esta enumeración asegura la consistencia de datos entre Python y PostgreSQL.
    """

    PLANIFICADO = "PLANIFICADO"
    INICIADO = "INICIADO"
    CONCLUIDO = "CONCLUIDO"
    CANCELADO = "CANCELADO"

    @classmethod
    def get_values(cls) -> List[str]:
        """Retorna la lista de valores válidos."""
        return [estado.value for estado in cls]

    @classmethod
    def is_valid(cls, estado: str) -> bool:
        """Verifica si un estado es válido según el dominio."""
        try:
            cls(estado.upper())
            return True
        except ValueError:
            return False

    @classmethod
    def get_default(cls) -> str:
        """Retorna el estado por defecto (PLANIFICADO)."""
        return cls.PLANIFICADO.value

    @classmethod
    def get_estados_activos(cls) -> List[str]:
        """Retorna los estados considerados activos."""
        return [cls.PLANIFICADO.value, cls.INICIADO.value]


class ExpedicionCI(Enum):
    """
    Enumeración para el dominio d_expedicion_ci.

    CREATE DOMAIN d_expedicion_ci AS TEXT
        CHECK (VALUE IN ('BE', 'CH', 'CB', 'LP', 'OR', 'PD', 'PT', 'SC', 'TJ', 'EX'));
    """

    BE = "BE"
    CH = "CH"
    CB = "CB"
    LP = "LP"
    OR = "OR"
    PD = "PD"
    PT = "PT"
    SC = "SC"
    TJ = "TJ"
    EX = "EX"

    @classmethod
    def is_valid(cls, expedicion: str) -> bool:
        """Verifica si una expedición es válida."""
        try:
            cls(expedicion.upper())
            return True
        except ValueError:
            return False


class GradoAcademico(Enum):
    """
    Enumeración para el dominio d_grado_academico.

    CREATE DOMAIN d_grado_academico AS TEXT
        CHECK (VALUE IN ('Mtr.', 'Mgtr.', 'Mag.', 'MBA', 'MSc', 'M.Sc.', 'PhD.', 'Dr.', 'Dra.'));
    """

    MTR = "Mtr."
    MGTR = "Mgtr."
    MAG = "Mag."
    MBA = "MBA"
    MSC = "MSc"
    MSC_PUNTO = "M.Sc."
    PHD = "PhD."
    DR = "Dr."
    DRA = "Dra."

    @classmethod
    def is_valid(cls, grado: str) -> bool:
        """Verifica si un grado académico es válido."""
        try:
            cls(grado)
            return True
        except ValueError:
            return False


# ============================================================================
# MODELO PRINCIPAL
# ============================================================================


class ProgramaAcademicoModel(BaseModel):
    """
    Modelo para operaciones de base de datos de programas académicos.

    Tabla: programas_academicos
    Esquema: Definido en database/PgSQL_Scheme.sql

    Este modelo proporciona una interfaz completa para gestionar programas académicos
    manteniendo la integridad referencial y las restricciones definidas en el esquema.
    """

    def __init__(self):
        """
        Inicializa el modelo de programas académicos.

        Configura el nombre de la tabla según el esquema PostgreSQL.
        """
        super().__init__()
        self.table_name = "programas_academicos"
        self._setup_cache()

    def _setup_cache(self):
        """Configura variables de caché para mejorar rendimiento."""
        self._cache_programas = {}
        self._cache_codigos = set()
        self._last_cache_update = None

    def _actualizar_cache(self) -> None:
        """
        Actualiza la caché interna de programas.

        Nota: Se ejecuta automáticamente cuando la caché está desactualizada.
        """
        try:
            programas = self.get_all()
            self._cache_programas = {p["id"]: p for p in programas}
            self._cache_codigos = {p["codigo"] for p in programas}
            self._last_cache_update = datetime.now()
        except Exception as e:
            self._log_warning(f"Error al actualizar caché: {e}")

    def _get_from_cache(self, programa_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un programa de la caché si está disponible.

        Args:
            programa_id (int): ID del programa.

        Returns:
            Optional[Dict[str, Any]]: Programa desde caché o None.
        """
        if (
            self._last_cache_update
            and (datetime.now() - self._last_cache_update).seconds < 300
        ):
            return self._cache_programas.get(programa_id)
        return None

    # ============================================================================
    # MÉTODOS CRUD BÁSICOS - OPTIMIZADOS
    # ============================================================================

    def create(self, datos: Dict[str, Any]) -> Optional[int]:
        """
        Crea un nuevo programa académico en la base de datos de forma optimizada.

        Args:
            datos (Dict[str, Any]): Diccionario con los datos del programa.

        Returns:
            Optional[int]: ID del programa creado si es exitoso, None si falla.

        Raises:
            ValueError: Si faltan campos requeridos o los datos son inválidos.
            IntegrityError: Si viola restricciones de integridad (ej: código duplicado).
        """
        try:
            # Validación rápida de campos requeridos
            campos_requeridos = ["codigo", "nombre", "costo_base", "cupos_totales"]
            for campo in campos_requeridos:
                if not datos.get(campo):
                    raise ValueError(f"Campo requerido faltante: {campo}")

            # Validación de unicidad usando caché primero
            codigo = datos["codigo"].strip().upper()
            if codigo in self._cache_codigos or self._existe_codigo(codigo):
                raise IntegrityError(f"El código '{codigo}' ya existe en el sistema")

            # Normalización y validación de datos
            datos_normalizados = self._normalizar_datos(datos)
            datos_completos = self._preparar_datos_creacion(datos_normalizados)

            # Validación de restricciones del esquema
            self._validar_datos_esquema(datos_completos)

            with self.engine.connect() as conn:
                # Construir consulta optimizada
                columnas = ", ".join(datos_completos.keys())
                marcadores = ", ".join([f":{key}" for key in datos_completos.keys()])

                query = text(
                    f"""
                    INSERT INTO {self.table_name} ({columnas})
                    VALUES ({marcadores})
                    RETURNING id
                """
                )

                # Ejecutar con transacción explícita
                with conn.begin():
                    result = conn.execute(query, datos_completos)
                    programa_id = result.scalar()

                # Actualizar caché
                datos_completos["id"] = programa_id
                self._cache_programas[programa_id] = datos_completos
                self._cache_codigos.add(codigo)

                self._log_info(
                    f"Programa creado exitosamente - ID: {programa_id}, Código: {codigo}"
                )
                return programa_id

        except (ValueError, IntegrityError) as e:
            self._log_error(f"Error de validación/integridad al crear programa: {e}")
            raise
        except SQLAlchemyError as e:
            self._log_error(f"Error de base de datos al crear programa: {e}")
            return None
        except Exception as e:
            self._log_error(f"Error inesperado al crear programa: {e}")
            return None

    def get_all(
        self, filtros: Optional[Dict[str, Any]] = None, use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todos los programas académicos con filtrado avanzado.

        Args:
            filtros (Optional[Dict[str, Any]]): Diccionario con filtros opcionales.
                Ejemplo: {'estado': 'PLANIFICADO', 'tutor_id': 5, 'promocion_activa': True}
            use_cache (bool): Usar caché para mejorar rendimiento (default: True).

        Returns:
            List[Dict[str, Any]]: Lista de programas encontrados, optimizada.

        Performance: Usa caché y consultas parametrizadas para mejor rendimiento.
        """
        # Verificar si podemos usar caché
        if use_cache and filtros is None and self._cache_programas:
            return list(self._cache_programas.values())

        try:
            with self.engine.connect() as conn:
                # Consulta base optimizada con solo campos necesarios
                campos_base = [
                    "pa.id",
                    "pa.codigo",
                    "pa.nombre",
                    "pa.descripcion",
                    "pa.estado",
                    "pa.costo_base",
                    "pa.cupos_totales",
                    "pa.cupos_disponibles",
                    "pa.fecha_inicio_planificada",
                    "pa.tutor_id",
                    "pa.promocion_activa",
                    "pa.descuento_promocion",
                ]

                query_parts = [
                    "SELECT",
                    ", ".join(campos_base),
                    f", d.nombres || ' ' || d.apellidos as tutor_nombre_completo",
                    f"FROM {self.table_name} pa",
                    "LEFT JOIN docentes d ON pa.tutor_id = d.id",
                    "WHERE 1=1",
                ]

                params = {}
                condiciones = []

                # Construcción dinámica de filtros optimizada
                if filtros:
                    condiciones, params = self._construir_filtros_avanzados(filtros)

                if condiciones:
                    query_parts.append("AND " + " AND ".join(condiciones))

                query_parts.append("ORDER BY pa.estado, pa.codigo, pa.nombre")

                query = text(" ".join(query_parts))
                result = conn.execute(query, params)

                # Conversión optimizada a diccionarios
                columnas = result.keys()
                programas = [
                    {col: val for col, val in zip(columnas, row)}
                    for row in result.fetchall()
                ]

                return programas

        except SQLAlchemyError as e:
            self._log_error(f"Error de base de datos al obtener programas: {e}")
            return []
        except Exception as e:
            self._log_error(f"Error inesperado al obtener programas: {e}")
            return []

    def get_by_id(
        self, programa_id: int, use_cache: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene un programa académico por su ID de forma optimizada.

        Args:
            programa_id (int): ID del programa a buscar.
            use_cache (bool): Usar caché para mejorar rendimiento.

        Returns:
            Optional[Dict[str, Any]]: Datos del programa o None si no existe.

        Performance: Primero intenta obtener de caché, luego de base de datos.
        """
        # Intentar obtener de caché primero
        if use_cache:
            programa_cache = self._get_from_cache(programa_id)
            if programa_cache:
                return programa_cache

        try:
            with self.engine.connect() as conn:
                # Consulta específica optimizada
                query = text(
                    f"""
                    SELECT pa.*,
                           d.nombres || ' ' || d.apellidos as tutor_nombre_completo,
                           d.email as tutor_email,
                           d.telefono as tutor_telefono,
                           d.especialidad as tutor_especialidad
                    FROM {self.table_name} pa
                    LEFT JOIN docentes d ON pa.tutor_id = d.id
                    WHERE pa.id = :programa_id
                """
                )

                result = conn.execute(query, {"programa_id": programa_id})
                row = result.fetchone()

                if row:
                    programa = dict(row)
                    # Actualizar caché
                    if use_cache:
                        self._cache_programas[programa_id] = programa
                    return programa

                return None

        except SQLAlchemyError as e:
            self._log_error(
                f"Error de base de datos al obtener programa {programa_id}: {e}"
            )
            return None
        except Exception as e:
            self._log_error(f"Error inesperado al obtener programa {programa_id}: {e}")
            return None

    def get_by_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un programa académico por su código único de forma optimizada.

        Args:
            codigo (str): Código del programa (ej: 'DIP-001').

        Returns:
            Optional[Dict[str, Any]]: Datos del programa o None si no existe.

        Performance: Usa índice UNIQUE de la base de datos para búsqueda rápida.
        """
        try:
            with self.engine.connect() as conn:
                query = text(
                    f"""
                    SELECT * FROM {self.table_name}
                    WHERE codigo = :codigo
                    LIMIT 1
                """
                )

                result = conn.execute(query, {"codigo": codigo.strip().upper()})
                programa = result.fetchone()

                return dict(programa) if programa else None

        except SQLAlchemyError as e:
            self._log_error(f"Error de base de datos al buscar código '{codigo}': {e}")
            return None

    def update(self, programa_id: int, datos_actualizacion: Dict[str, Any]) -> bool:
        """
        Actualiza los datos de un programa académico existente de forma optimizada.

        Args:
            programa_id (int): ID del programa a actualizar.
            datos_actualizacion (Dict[str, Any]): Campos a actualizar.

        Returns:
            bool: True si la actualización fue exitosa, False en caso contrario.

        Performance: Solo actualiza campos modificados y mantiene caché sincronizada.
        """
        try:
            # Verificar que el programa existe (usando caché si está disponible)
            programa = self.get_by_id(programa_id, use_cache=True)
            if not programa:
                self._log_error(
                    f"No se puede actualizar - Programa ID {programa_id} no encontrado"
                )
                return False

            # Validaciones rápidas
            if "estado" in datos_actualizacion:
                estado = datos_actualizacion["estado"]
                if not EstadoPrograma.is_valid(estado):
                    raise ValueError(f"Estado inválido: {estado}")

            if "codigo" in datos_actualizacion:
                nuevo_codigo = datos_actualizacion["codigo"].strip().upper()
                if nuevo_codigo != programa["codigo"]:
                    if self._existe_codigo(nuevo_codigo):
                        raise IntegrityError(
                            f"Ya existe un programa con código: {nuevo_codigo}"
                        )

            # Preparar datos para actualización (solo campos modificados)
            datos_preparados = self._preparar_datos_actualizacion(datos_actualizacion)
            if not datos_preparados:
                self._log_info("No hay datos válidos para actualizar")
                return False

            # Validar restricciones del esquema
            self._validar_datos_esquema(datos_preparados)

            with self.engine.connect() as conn:
                # Construir consulta dinámica solo con campos a actualizar
                set_clause = ", ".join(
                    [f"{key} = :{key}" for key in datos_preparados.keys()]
                )

                query = text(
                    f"""
                    UPDATE {self.table_name}
                    SET {set_clause}
                    WHERE id = :programa_id
                    RETURNING *
                """
                )

                # Agregar ID a los parámetros
                datos_preparados["programa_id"] = programa_id

                # Ejecutar con transacción
                with conn.begin():
                    result = conn.execute(query, datos_preparados)
                    fila_actualizada = result.fetchone()

                actualizado = fila_actualizada is not None

                if actualizado:
                    # Actualizar caché
                    programa_actualizado = dict(fila_actualizada)
                    self._cache_programas[programa_id] = programa_actualizado

                    if "codigo" in datos_preparados:
                        self._cache_codigos.discard(programa.get("codigo", ""))
                        self._cache_codigos.add(datos_preparados["codigo"])

                    self._log_info(
                        f"Programa ID {programa_id} actualizado exitosamente"
                    )
                else:
                    self._log_warning(f"No se actualizó el programa ID {programa_id}")

                return actualizado

        except (ValueError, IntegrityError) as e:
            self._log_error(f"Error de validación/integridad al actualizar: {e}")
            return False
        except SQLAlchemyError as e:
            self._log_error(
                f"Error de base de datos al actualizar programa {programa_id}: {e}"
            )
            return False
        except Exception as e:
            self._log_error(
                f"Error inesperado al actualizar programa {programa_id}: {e}"
            )
            return False

    def delete(self, programa_id: int) -> bool:
        """
        Marca un programa como CANCELADO en lugar de eliminarlo físicamente.

        Args:
            programa_id (int): ID del programa a cancelar.

        Returns:
            bool: True si la cancelación fue exitosa, False en caso contrario.

        Nota: Según mejores prácticas, no se eliminan datos físicamente.
        """
        try:
            datos_cancelacion = {
                "estado": EstadoPrograma.CANCELADO.value,
                "updated_at": datetime.now(),
                "cupos_disponibles": 0,  # Liberar cupos cuando se cancela
            }

            return self.update(programa_id, datos_cancelacion)

        except Exception as e:
            self._log_error(f"Error al cancelar programa {programa_id}: {e}")
            return False

    # ============================================================================
    # MÉTODOS DE CONSULTA ESPECIALIZADA - OPTIMIZADOS
    # ============================================================================

    def get_all(self, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Obtiene programas con filtros."""
        try:
            with self.engine.connect() as conn:
                query = f"SELECT * FROM {self.table_name} WHERE 1=1"
                params = {}

                if filtros and "estado" in filtros:
                    query += " AND estado = :estado"
                    params["estado"] = filtros["estado"]

                query += " ORDER BY nombre"
                result = conn.execute(text(query), params)
                return [dict(row) for row in result.fetchall()]
        except Exception as e:
            self._log_error(f"Error obteniendo programas: {e}")
            return []

    def get_activos(self, solo_con_cupos: bool = False) -> List[Dict[str, Any]]:
        """
        Obtiene programas activos de forma optimizada.

        Args:
            solo_con_cupos (bool): Filtrar solo programas con cupos disponibles.

        Returns:
            List[Dict[str, Any]]: Programas activos.

        Performance: Usa índices de base de datos para consulta rápida.
        """
        filtros = {"estado_in": EstadoPrograma.get_estados_activos()}
        if solo_con_cupos:
            filtros["cupos_disponibles_gt"] = 0

        return self.get_all(filtros)

    def get_programas_con_cupos_disponibles(self) -> List[Dict[str, Any]]:
        """
        Obtiene programas que tienen cupos disponibles para matrícula.

        Returns:
            List[Dict[str, Any]]: Programas con cupos disponibles.

        Performance: Consulta específica optimizada con índices.
        """
        try:
            with self.engine.connect() as conn:
                query = text(
                    f"""
                    SELECT pa.*,
                           d.nombres || ' ' || d.apellidos as tutor_nombre_completo
                    FROM {self.table_name} pa
                    LEFT JOIN docentes d ON pa.tutor_id = d.id
                    WHERE pa.estado IN (:estado1, :estado2)
                    AND pa.cupos_disponibles > 0
                    ORDER BY pa.cupos_disponibles DESC, 
                             pa.fecha_inicio_planificada NULLS LAST
                    LIMIT 50  -- Límite para rendimiento
                """
                )

                result = conn.execute(
                    query,
                    {
                        "estado1": EstadoPrograma.PLANIFICADO.value,
                        "estado2": EstadoPrograma.INICIADO.value,
                    },
                )

                columnas = result.keys()
                return [
                    {col: val for col, val in zip(columnas, row)}
                    for row in result.fetchall()
                ]

        except SQLAlchemyError as e:
            self._log_error(f"Error al obtener programas con cupos disponibles: {e}")
            return []

    def get_programas_con_promociones_activas(self) -> List[Dict[str, Any]]:
        """
        Obtiene programas con promociones activas y vigentes.

        Returns:
            List[Dict[str, Any]]: Programas con promociones vigentes.

        Performance: Incluye verificación de fecha límite.
        """
        try:
            fecha_actual = date.today()

            with self.engine.connect() as conn:
                query = text(
                    f"""
                    SELECT pa.*,
                           d.nombres || ' ' || d.apellidos as tutor_nombre_completo,
                           CASE 
                               WHEN pa.promocion_fecha_limite IS NULL THEN 'SIN_LIMITE'
                               WHEN pa.promocion_fecha_limite >= :fecha_actual THEN 'VIGENTE'
                               ELSE 'VENCIDA'
                           END as estado_promocion
                    FROM {self.table_name} pa
                    LEFT JOIN docentes d ON pa.tutor_id = d.id
                    WHERE pa.promocion_activa = TRUE
                    AND pa.estado IN (:estado1, :estado2)
                    AND (pa.promocion_fecha_limite IS NULL 
                         OR pa.promocion_fecha_limite >= :fecha_actual)
                    ORDER BY pa.descuento_promocion DESC,
                             pa.promocion_fecha_limite NULLS FIRST
                """
                )

                result = conn.execute(
                    query,
                    {
                        "fecha_actual": fecha_actual,
                        "estado1": EstadoPrograma.PLANIFICADO.value,
                        "estado2": EstadoPrograma.INICIADO.value,
                    },
                )

                columnas = result.keys()
                return [
                    {col: val for col, val in zip(columnas, row)}
                    for row in result.fetchall()
                ]

        except SQLAlchemyError as e:
            self._log_error(f"Error al obtener programas con promociones: {e}")
            return []

    def get_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales de todos los programas de forma optimizada.

        Returns:
            Dict[str, Any]: Estadísticas agregadas de programas.

        Performance: Una sola consulta con agregaciones.
        """
        try:
            with self.engine.connect() as conn:
                query = text(
                    f"""
                    SELECT 
                        COUNT(*) as total_programas,
                        COUNT(CASE WHEN estado = :planificado THEN 1 END) as planificados,
                        COUNT(CASE WHEN estado = :iniciado THEN 1 END) as iniciados,
                        COUNT(CASE WHEN estado = :concluido THEN 1 END) as concluidos,
                        COUNT(CASE WHEN estado = :cancelado THEN 1 END) as cancelados,
                        COALESCE(SUM(cupos_totales), 0) as cupos_totales,
                        COALESCE(SUM(cupos_disponibles), 0) as cupos_disponibles,
                        COALESCE(SUM(costo_base), 0) as valor_total_programas,
                        COALESCE(AVG(duracion_semanas), 0) as duracion_promedio_semanas,
                        COUNT(DISTINCT tutor_id) as tutores_asignados,
                        COUNT(CASE WHEN promocion_activa = TRUE THEN 1 END) as promociones_activas,
                        COALESCE(SUM(cupos_totales - cupos_disponibles), 0) as cupos_ocupados
                    FROM {self.table_name}
                """
                )

                result = conn.execute(
                    query,
                    {
                        "planificado": EstadoPrograma.PLANIFICADO.value,
                        "iniciado": EstadoPrograma.INICIADO.value,
                        "concluido": EstadoPrograma.CONCLUIDO.value,
                        "cancelado": EstadoPrograma.CANCELADO.value,
                    },
                )

                row = result.fetchone()

                if row:
                    estadisticas = dict(row)
                    total_cupos = estadisticas["cupos_totales"]
                    cupos_ocupados = estadisticas.get("cupos_ocupados", 0)

                    estadisticas["ocupacion_porcentaje"] = (
                        (cupos_ocupados / total_cupos * 100) if total_cupos > 0 else 0
                    )

                    # Calcular estadísticas adicionales
                    estadisticas["tasa_ocupacion"] = (
                        estadisticas["ocupacion_porcentaje"] / 100
                    )
                    estadisticas["valor_promedio_programa"] = (
                        estadisticas["valor_total_programas"]
                        / estadisticas["total_programas"]
                        if estadisticas["total_programas"] > 0
                        else 0
                    )

                    estadisticas["fecha_consulta"] = datetime.now().isoformat()
                    estadisticas["cache_actualizada"] = (
                        self._last_cache_update.isoformat()
                        if self._last_cache_update
                        else None
                    )

                    return estadisticas
                else:
                    return self._estadisticas_por_defecto()

        except SQLAlchemyError as e:
            self._log_error(f"Error al obtener estadísticas: {e}")
            return self._estadisticas_por_defecto()

    def search(
        self, criterio: str, valor: str, solo_activos: bool = True, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Búsqueda avanzada de programas con múltiples criterios y límite de resultados.

        Args:
            criterio (str): Campo de búsqueda ('codigo', 'nombre', 'descripcion', 'todos').
            valor (str): Valor a buscar.
            solo_activos (bool): Filtrar solo programas activos.
            limit (int): Límite de resultados para rendimiento.

        Returns:
            List[Dict[str, Any]]: Programas que coinciden con la búsqueda.

        Performance: Incluye límite y uso de índices.
        """
        try:
            with self.engine.connect() as conn:
                # Construir WHERE dinámico
                where_conditions = self._construir_condiciones_busqueda(criterio, valor)

                if solo_activos:
                    estados_activos = EstadoPrograma.get_estados_activos()
                    estados_placeholder = ", ".join(
                        [f"'{estado}'" for estado in estados_activos]
                    )
                    where_conditions.append(f"estado IN ({estados_placeholder})")

                where_clause = (
                    "WHERE " + " AND ".join(where_conditions)
                    if where_conditions
                    else ""
                )

                query = text(
                    f"""
                    SELECT * FROM {self.table_name}
                    {where_clause}
                    ORDER BY 
                        CASE 
                            WHEN nombre ILIKE :exact_match THEN 1
                            WHEN nombre ILIKE :start_with THEN 2
                            ELSE 3
                        END,
                        codigo, nombre
                    LIMIT {limit}
                """
                )

                # Parámetros optimizados para búsqueda
                params = {
                    "valor": f"%{valor}%",
                    "exact_match": f"{valor}",
                    "start_with": f"{valor}%",
                }

                result = conn.execute(query, params)
                columnas = result.keys()

                return [
                    {col: val for col, val in zip(columnas, row)}
                    for row in result.fetchall()
                ]

        except SQLAlchemyError as e:
            self._log_error(
                f"Error en búsqueda (criterio={criterio}, valor={valor}): {e}"
            )
            return []

    def actualizar_cupos_disponibles(
        self, programa_id: int, cantidad: int = 1, operacion: str = "decrementar"
    ) -> bool:
        """
        Actualiza los cupos disponibles de un programa de forma segura.

        Args:
            programa_id (int): ID del programa.
            cantidad (int): Cantidad a actualizar.
            operacion (str): 'incrementar' o 'decrementar'.

        Returns:
            bool: True si la actualización fue exitosa.

        Performance: Operación atómica con verificación de límites.
        """
        try:
            with self.engine.connect() as conn:
                if operacion == "incrementar":
                    query = text(
                        f"""
                        UPDATE {self.table_name}
                        SET cupos_disponibles = LEAST(cupos_disponibles + :cantidad, cupos_totales),
                            updated_at = :updated_at
                        WHERE id = :programa_id
                        RETURNING cupos_disponibles
                    """
                    )
                else:  # decrementar
                    query = text(
                        f"""
                        UPDATE {self.table_name}
                        SET cupos_disponibles = GREATEST(cupos_disponibles - :cantidad, 0),
                            updated_at = :updated_at
                        WHERE id = :programa_id
                        AND cupos_disponibles >= :cantidad
                        RETURNING cupos_disponibles
                    """
                    )

                result = conn.execute(
                    query,
                    {
                        "programa_id": programa_id,
                        "cantidad": cantidad,
                        "updated_at": datetime.now(),
                    },
                )

                with conn.begin():
                    fila_actualizada = result.fetchone()

                actualizado = fila_actualizada is not None

                if actualizado:
                    # Actualizar caché
                    if programa_id in self._cache_programas:
                        self._cache_programas[programa_id]["cupos_disponibles"] = (
                            fila_actualizada[0]
                        )

                    self._log_info(
                        f"Cupos actualizados para programa ID {programa_id} ({operacion}: {cantidad})"
                    )

                return actualizado

        except SQLAlchemyError as e:
            self._log_error(
                f"Error al actualizar cupos del programa {programa_id}: {e}"
            )
            return False

    # ============================================================================
    # MÉTODOS AUXILIARES PRIVADOS - OPTIMIZADOS
    # ============================================================================

    def _normalizar_datos(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normaliza los datos para consistencia en la base de datos.

        Args:
            datos (Dict[str, Any]): Datos crudos.

        Returns:
            Dict[str, Any]: Datos normalizados.
        """
        normalizados = datos.copy()

        # Normalizar strings
        for campo in ["codigo", "nombre", "descripcion"]:
            if campo in normalizados and isinstance(normalizados[campo], str):
                normalizados[campo] = normalizados[campo].strip()
                if campo == "codigo":
                    normalizados[campo] = normalizados[campo].upper()

        # Normalizar estados
        if "estado" in normalizados and isinstance(normalizados["estado"], str):
            normalizados["estado"] = normalizados["estado"].upper()

        return normalizados

    def _preparar_datos_creacion(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepara los datos para la creación de un nuevo programa.

        Args:
            datos (Dict[str, Any]): Datos normalizados.

        Returns:
            Dict[str, Any]: Datos preparados con valores por defecto.
        """
        datos_preparados = datos.copy()

        # Valores por defecto según esquema
        defaults = {
            "estado": EstadoPrograma.get_default(),
            "descuento_contado": 0.00,
            "descuento_promocion": 0.00,
            "costo_inscripcion": 0.00,
            "costo_matricula": 0.00,
            "cuotas_mensuales": 1,
            "dias_entre_cuotas": 30,
            "promocion_activa": False,
            "cupos_disponibles": datos.get("cupos_totales", 0),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        # Aplicar defaults solo si no están presentes
        for key, value in defaults.items():
            if key not in datos_preparados or datos_preparados[key] is None:
                datos_preparados[key] = value

        # Validar y ajustar cupos_disponibles
        if "cupos_totales" in datos_preparados:
            cupos_totales = datos_preparados["cupos_totales"]
            cupos_disponibles = datos_preparados.get("cupos_disponibles", cupos_totales)
            datos_preparados["cupos_disponibles"] = min(
                cupos_disponibles, cupos_totales
            )

        return datos_preparados

    def _preparar_datos_actualizacion(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepara los datos para la actualización de un programa.

        Args:
            datos (Dict[str, Any]): Datos a actualizar.

        Returns:
            Dict[str, Any]: Datos preparados para actualización.
        """
        # Excluir campos que no se deben actualizar directamente
        campos_excluidos = ["id", "created_at"]

        datos_preparados = {
            key: value
            for key, value in datos.items()
            if (
                key not in campos_excluidos and value is not None and value != ""
            )  # Excluir strings vacíos
        }

        # Siempre actualizar timestamp
        if datos_preparados:  # Solo si hay algo que actualizar
            datos_preparados["updated_at"] = datetime.now()

        return datos_preparados

    def _validar_datos_esquema(self, datos: Dict[str, Any]) -> None:
        """
        Valida que los datos cumplan con las restricciones del esquema PostgreSQL.

        Args:
            datos (Dict[str, Any]): Datos a validar.

        Raises:
            ValueError: Si los datos no cumplen con las restricciones.
        """
        # Validar estado según dominio
        if "estado" in datos:
            if not EstadoPrograma.is_valid(datos["estado"]):
                raise ValueError(
                    f"Estado inválido: '{datos['estado']}'. "
                    f"Válidos: {', '.join(EstadoPrograma.get_values())}"
                )

        # Validar porcentajes de descuento (0-100)
        for campo_descuento in ["descuento_contado", "descuento_promocion"]:
            if campo_descuento in datos:
                descuento = float(datos[campo_descuento])
                if not (0 <= descuento <= 100):
                    raise ValueError(
                        f"{campo_descuento} inválido: {descuento}. Debe estar entre 0 y 100"
                    )

        # Validar montos positivos
        campos_monetarios = ["costo_base", "costo_inscripcion", "costo_matricula"]
        for campo in campos_monetarios:
            if campo in datos:
                valor = float(datos[campo])
                if valor < 0:
                    raise ValueError(f"{campo} no puede ser negativo: {valor}")

        # Validar cupos
        if "cupos_totales" in datos:
            cupos_totales = int(datos["cupos_totales"])
            if cupos_totales < 0:
                raise ValueError(
                    f"cupos_totales no puede ser negativo: {cupos_totales}"
                )

            if "cupos_disponibles" in datos:
                cupos_disp = int(datos["cupos_disponibles"])
                if not (0 <= cupos_disp <= cupos_totales):
                    raise ValueError(
                        f"cupos_disponibles ({cupos_disp}) fuera de rango válido: "
                        f"0 a {cupos_totales}"
                    )

    def _existe_codigo(self, codigo: str) -> bool:
        """
        Verifica si ya existe un programa con el código especificado.

        Args:
            codigo (str): Código a verificar.

        Returns:
            bool: True si el código ya existe, False en caso contrario.

        Performance: Consulta rápida usando índice UNIQUE.
        """
        try:
            with self.engine.connect() as conn:
                query = text(
                    f"""
                    SELECT EXISTS(
                        SELECT 1 FROM {self.table_name}
                        WHERE codigo = :codigo
                        LIMIT 1
                    ) as existe
                """
                )

                result = conn.execute(query, {"codigo": codigo})
                return bool(result.scalar())

        except SQLAlchemyError:
            return False

    def _construir_filtros_avanzados(self, filtros: Dict[str, Any]) -> tuple:
        """
        Construye condiciones y parámetros para filtros avanzados.

        Args:
            filtros (Dict[str, Any]): Diccionario de filtros.

        Returns:
            tuple: (condiciones, parametros)
        """
        condiciones = []
        parametros = {}

        mapeo_filtros = {
            "estado": ("pa.estado = :estado", "estado"),
            "tutor_id": ("pa.tutor_id = :tutor_id", "tutor_id"),
            "promocion_activa": (
                "pa.promocion_activa = :promocion_activa",
                "promocion_activa",
            ),
            "codigo": ("pa.codigo ILIKE :codigo", "codigo"),
            "nombre": ("pa.nombre ILIKE :nombre", "nombre"),
            "descripcion": ("pa.descripcion ILIKE :descripcion", "descripcion"),
            "cupos_disponibles_gt": (
                "pa.cupos_disponibles > :cupos_disponibles_gt",
                "cupos_disponibles_gt",
            ),
            "costo_base_min": ("pa.costo_base >= :costo_base_min", "costo_base_min"),
            "costo_base_max": ("pa.costo_base <= :costo_base_max", "costo_base_max"),
        }

        for filtro, valor in filtros.items():
            if filtro in mapeo_filtros:
                condicion, param_key = mapeo_filtros[filtro]
                condiciones.append(condicion)

                # Manejar patrones LIKE
                if filtro in ["codigo", "nombre", "descripcion"]:
                    parametros[param_key] = f"%{valor}%"
                else:
                    parametros[param_key] = valor

            # Manejar filtro especial para múltiples estados
            elif filtro == "estado_in" and isinstance(valor, list):
                placeholders = ", ".join([f":estado_in_{i}" for i in range(len(valor))])
                condiciones.append(f"pa.estado IN ({placeholders})")
                for i, estado in enumerate(valor):
                    parametros[f"estado_in_{i}"] = estado

        return condiciones, parametros

    def _construir_condiciones_busqueda(self, criterio: str, valor: str) -> List[str]:
        """
        Construye condiciones WHERE optimizadas para búsquedas.

        Args:
            criterio (str): Tipo de búsqueda.
            valor (str): Valor a buscar.

        Returns:
            List[str]: Lista de condiciones SQL optimizadas.
        """
        if not valor or not valor.strip():
            return []

        valor = valor.strip()

        # Mapeo de criterios a condiciones optimizadas
        condiciones_map = {
            "codigo": [f"codigo ILIKE :valor"],
            "nombre": [f"nombre ILIKE :valor"],
            "descripcion": [f"descripcion ILIKE :valor"],
            "todos": [
                f"codigo ILIKE :valor",
                f"nombre ILIKE :valor",
                f"descripcion ILIKE :valor",
            ],
        }

        return condiciones_map.get(criterio, [f"nombre ILIKE :valor"])

    def _estadisticas_por_defecto(self) -> Dict[str, Any]:
        """
        Retorna estadísticas por defecto en caso de error.

        Returns:
            Dict[str, Any]: Estadísticas con valores cero.
        """
        return {
            "total_programas": 0,
            "planificados": 0,
            "iniciados": 0,
            "concluidos": 0,
            "cancelados": 0,
            "cupos_totales": 0,
            "cupos_disponibles": 0,
            "valor_total_programas": 0.0,
            "duracion_promedio_semanas": 0.0,
            "tutores_asignados": 0,
            "promociones_activas": 0,
            "cupos_ocupados": 0,
            "ocupacion_porcentaje": 0.0,
            "tasa_ocupacion": 0.0,
            "valor_promedio_programa": 0.0,
            "fecha_consulta": datetime.now().isoformat(),
            "cache_actualizada": None,
        }

    def _log_info(self, mensaje: str) -> None:
        """Registra mensajes informativos con formato optimizado."""
        print(f"📝 [{self.__class__.__name__}] {datetime.now():%H:%M:%S} - {mensaje}")

    def _log_error(self, mensaje: str) -> None:
        """Registra mensajes de error con formato optimizado."""
        print(
            f"❌ [{self.__class__.__name__}] {datetime.now():%H:%M:%S} - ERROR: {mensaje}"
        )

    def _log_warning(self, mensaje: str) -> None:
        """Registra mensajes de advertencia con formato optimizado."""
        print(
            f"⚠️ [{self.__class__.__name__}] {datetime.now():%H:%M:%S} - WARNING: {mensaje}"
        )
