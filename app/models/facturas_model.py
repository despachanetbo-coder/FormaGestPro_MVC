# app/models/facturas_model.py - VERSIÓN COMPLETA Y COMPATIBLE
"""
Modelo de Facturas - Implementación completa según estructura de base de datos
Hereda de BaseModel y proporciona todos los métodos necesarios
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, date
from decimal import Decimal

from .base_model import BaseModel

logger = logging.getLogger(__name__)


class FacturasModel(BaseModel):
    """
    Modelo para gestión de facturas según estructura:
    CREATE TABLE facturas (
        id INTEGER PRIMARY KEY DEFAULT nextval('seq_facturas_id'),
        numero TEXT NOT NULL,
        cliente_id INTEGER NOT NULL,
        cliente_nombre TEXT,
        cliente_cedula TEXT,
        cliente_direccion TEXT,
        cliente_telefono TEXT,
        cliente_email TEXT,
        fecha_emision DATE NOT NULL,
        fecha_vencimiento DATE,
        subtotal DECIMAL(12,2) NOT NULL DEFAULT 0,
        iva DECIMAL(12,2) NOT NULL DEFAULT 0,
        total DECIMAL(12,2) NOT NULL DEFAULT 0,
        estado TEXT NOT NULL DEFAULT 'PENDIENTE',
        tipo TEXT,
        observaciones TEXT,
        usuario_id INTEGER,
        forma_pago TEXT,
        referencia_pago TEXT,
        fecha_pago DATE,
        anulada BOOLEAN NOT NULL DEFAULT FALSE,
        motivo_anulacion TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        CONSTRAINT uk_factura_numero UNIQUE (numero),
        CONSTRAINT chk_factura_total CHECK (total >= 0),
        CONSTRAINT chk_factura_subtotal CHECK (subtotal >= 0),
        CONSTRAINT chk_factura_iva CHECK (iva >= 0)
    );
    """

    TABLE_NAME = "facturas"
    SEQUENCE_NAME = "seq_facturas_id"

    # ============ CONSTANTES FALTANTES ============
    # Tipos de documento para el SIAT (Bolivia)
    TIPO_NIT = "NIT"  # Número de Identificación Tributaria
    TIPO_CI = "CI"  # Cédula de Identidad
    TIPO_CONSUMIDOR_FINAL = "CONSUMIDOR_FINAL"  # Cliente sin identificación

    # Estados de factura según controlador
    ESTADO_EMITIDA = "EMITIDA"
    ESTADO_PAGADA = "PAGADA"
    ESTADO_ANULADA = "ANULADA"
    ESTADO_PENDIENTE = "PENDIENTE"

    # Constantes para mapeo
    TIPOS_DOCUMENTO = [TIPO_NIT, TIPO_CI, TIPO_CONSUMIDOR_FINAL]

    TIPOS_DOCUMENTO_DESC = {
        TIPO_NIT: "NIT (Número de Identificación Tributaria)",
        TIPO_CI: "CI (Cédula de Identidad)",
        TIPO_CONSUMIDOR_FINAL: "Consumidor Final",
    }

    ESTADOS = [ESTADO_EMITIDA, ESTADO_PAGADA, ESTADO_ANULADA, ESTADO_PENDIENTE]

    ESTADOS_DESC = {
        ESTADO_EMITIDA: "Factura Emitida",
        ESTADO_PAGADA: "Factura Pagada",
        ESTADO_ANULADA: "Factura Anulada",
        ESTADO_PENDIENTE: "Factura Pendiente",
    }

    # Estados válidos según CHECK constraint en la base de datos
    ESTADOS_VALIDOS = ["PENDIENTE", "PAGADA", "ANULADA", "CANCELADA"]

    # Tipos de factura comunes en el sistema
    TIPOS_FACTURA = ["MATRICULA", "MENSUALIDAD", "OTRO", "SERVICIO"]
    # ============ FIN CONSTANTES FALTANTES ============

    def __init__(self):
        """Inicializa el modelo de facturas"""
        super().__init__()

        # Columnas según estructura de la tabla
        self.columns = [
            "id",
            "numero",
            "cliente_id",
            "cliente_nombre",
            "cliente_cedula",
            "cliente_direccion",
            "cliente_telefono",
            "cliente_email",
            "fecha_emision",
            "fecha_vencimiento",
            "subtotal",
            "iva",
            "total",
            "estado",
            "tipo",
            "observaciones",
            "usuario_id",
            "forma_pago",
            "referencia_pago",
            "fecha_pago",
            "anulada",
            "motivo_anulacion",
            "created_at",
            "updated_at",
        ]

        logger.debug(f"✅ FacturasModel inicializado. Tabla: {self.TABLE_NAME}")

    # ============ MÉTODOS CRUD BÁSICOS (para controlador) ============

    def crear_factura(self, datos_factura: Dict[str, Any]) -> Optional[int]:
        """
        Crea una nueva factura en la base de datos

        Args:
            datos_factura: Diccionario con datos de la factura

        Returns:
            ID de la factura creada o None si hay error
        """
        try:
            # Validar datos requeridos
            campos_requeridos = ["numero", "cliente_id", "fecha_emision", "total"]
            for campo in campos_requeridos:
                if campo not in datos_factura or not datos_factura[campo]:
                    logger.error(f"❌ Campo requerido faltante: {campo}")
                    return None

            # Establecer valores por defecto
            datos_completos = datos_factura.copy()

            if "estado" not in datos_completos:
                datos_completos["estado"] = "PENDIENTE"

            if "subtotal" not in datos_completos:
                datos_completos["subtotal"] = datos_completos.get("total", 0)

            if "iva" not in datos_completos:
                datos_completos["iva"] = 0

            if "anulada" not in datos_completos:
                datos_completos["anulada"] = False

            # Insertar en base de datos
            result = self.insert(self.TABLE_NAME, datos_completos, returning="id")

            if result:
                factura_id = result[0] if isinstance(result, list) else result
                logger.info(f"✅ Factura creada exitosamente con ID: {factura_id}")
                return factura_id

            return None

        except Exception as e:
            logger.error(f"❌ Error creando factura: {e}", exc_info=True)
            return None

    def obtener_factura(self, factura_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene una factura por su ID

        Args:
            factura_id: ID de la factura a buscar

        Returns:
            Diccionario con datos de la factura o None si no existe
        """
        try:
            query = f"SELECT * FROM {self.TABLE_NAME} WHERE id = %s"
            result = self.fetch_one(query, (factura_id,))
            return result
        except Exception as e:
            logger.error(f"❌ Error obteniendo factura {factura_id}: {e}")
            return None

    def obtener_factura_por_numero(self, numero: str) -> Optional[Dict[str, Any]]:
        """
        Busca una factura por su número

        Args:
            numero: Número de factura a buscar

        Returns:
            Diccionario con datos de la factura o None si no existe
        """
        try:
            query = f"SELECT * FROM {self.TABLE_NAME} WHERE numero = %s"
            result = self.fetch_one(query, (numero,))
            return result
        except Exception as e:
            logger.error(f"❌ Error obteniendo factura por número '{numero}': {e}")
            return None

    def actualizar_factura(self, factura_id: int, datos: Dict[str, Any]) -> bool:
        """
        Actualiza los datos de una factura existente

        Args:
            factura_id: ID de la factura a actualizar
            datos: Datos a actualizar

        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        try:
            if not datos:
                return False

            # Agregar timestamp de actualización
            datos["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Usar método update heredado
            result = self.update(
                table=self.TABLE_NAME,
                data=datos,
                condition="id = %s",
                params=(factura_id,),
            )

            return result is not None and result > 0

        except Exception as e:
            logger.error(f"❌ Error actualizando factura {factura_id}: {e}")
            return False

    def eliminar_factura(self, factura_id: int) -> bool:
        """
        Elimina una factura (solo si está anulada o en estado cancelado)

        Args:
            factura_id: ID de la factura a eliminar

        Returns:
            True si la eliminación fue exitosa, False en caso contrario
        """
        try:
            # Verificar estado de la factura primero
            factura = self.obtener_factura(factura_id)
            if not factura:
                return False

            estado = factura.get("estado", "")
            anulada = factura.get("anulada", False)

            # Solo permitir eliminar facturas anuladas o canceladas
            if not anulada and estado != "CANCELADA":
                logger.error(f"❌ No se puede eliminar factura en estado: {estado}")
                return False

            query = f"DELETE FROM {self.TABLE_NAME} WHERE id = %s"
            result = self.execute_query(query, (factura_id,), commit=True)

            return result is not None and result > 0

        except Exception as e:
            logger.error(f"❌ Error eliminando factura {factura_id}: {e}")
            return False

    # ============ MÉTODOS DE CONSULTA (para controlador) ============

    def obtener_todas_facturas(
        self,
        estado: Optional[str] = None,
        cliente_id: Optional[int] = None,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todas las facturas con filtros opcionales

        Args:
            estado: Filtrar por estado
            cliente_id: Filtrar por cliente
            fecha_inicio: Fecha inicio para rango
            fecha_fin: Fecha fin para rango
            limit: Límite de resultados
            offset: Desplazamiento para paginación

        Returns:
            Lista de facturas que coinciden con los filtros
        """
        try:
            conditions = ["anulada = FALSE"]
            params = []

            if estado:
                conditions.append("estado = %s")
                params.append(estado)

            if cliente_id:
                conditions.append("cliente_id = %s")
                params.append(cliente_id)

            if fecha_inicio:
                conditions.append("fecha_emision >= %s")
                params.append(fecha_inicio)

            if fecha_fin:
                conditions.append("fecha_emision <= %s")
                params.append(fecha_fin)

            where_clause = " AND ".join(conditions)

            query = f"""
                SELECT * FROM {self.TABLE_NAME} 
                WHERE {where_clause}
                ORDER BY fecha_emision DESC, id DESC
                LIMIT %s OFFSET %s
            """

            params.extend([limit, offset])
            return self.fetch_all(query, tuple(params))

        except Exception as e:
            logger.error(f"❌ Error obteniendo facturas: {e}")
            return []

    def obtener_facturas_pendientes(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtiene facturas pendientes de pago

        Args:
            limit: Límite de resultados

        Returns:
            Lista de facturas pendientes
        """
        try:
            query = f"""
                SELECT * FROM {self.TABLE_NAME} 
                WHERE estado = 'PENDIENTE' AND anulada = FALSE
                ORDER BY fecha_vencimiento ASC 
                LIMIT %s
            """
            return self.fetch_all(query, (limit,))
        except Exception as e:
            logger.error(f"❌ Error obteniendo facturas pendientes: {e}")
            return []

    def obtener_facturas_vencidas(self) -> List[Dict[str, Any]]:
        """
        Obtiene facturas vencidas (pendientes con fecha de vencimiento pasada)

        Returns:
            Lista de facturas vencidas
        """
        try:
            hoy = date.today().isoformat()
            query = f"""
                SELECT * FROM {self.TABLE_NAME} 
                WHERE estado = 'PENDIENTE' 
                AND fecha_vencimiento < %s 
                AND anulada = FALSE
                ORDER BY fecha_vencimiento ASC
            """
            return self.fetch_all(query, (hoy,))
        except Exception as e:
            logger.error(f"❌ Error obteniendo facturas vencidas: {e}")
            return []

    def obtener_facturas_por_cliente(
        self, cliente_id: int, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Obtiene facturas de un cliente específico

        Args:
            cliente_id: ID del cliente
            limit: Límite de resultados

        Returns:
            Lista de facturas del cliente
        """
        try:
            query = f"""
                SELECT * FROM {self.TABLE_NAME} 
                WHERE cliente_id = %s AND anulada = FALSE
                ORDER BY fecha_emision DESC 
                LIMIT %s
            """
            return self.fetch_all(query, (cliente_id, limit))
        except Exception as e:
            logger.error(f"❌ Error obteniendo facturas del cliente {cliente_id}: {e}")
            return []

    # ============ MÉTODOS DE ESTADÍSTICAS (para controlador) ============

    def obtener_estadisticas_facturas(
        self, fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales de facturas

        Args:
            fecha_inicio: Fecha inicio para filtro (opcional)
            fecha_fin: Fecha fin para filtro (opcional)

        Returns:
            Diccionario con estadísticas
        """
        try:
            where_clause = "WHERE anulada = FALSE"
            params = []

            if fecha_inicio and fecha_fin:
                where_clause += " AND fecha_emision BETWEEN %s AND %s"
                params.extend([fecha_inicio, fecha_fin])

            query = f"""
                SELECT 
                    COUNT(*) as total_facturas,
                    COALESCE(SUM(total), 0) as total_ingresos,
                    COALESCE(AVG(total), 0) as promedio_factura,
                    MIN(fecha_emision) as primera_factura,
                    MAX(fecha_emision) as ultima_factura,
                    COALESCE(SUM(CASE WHEN estado = 'PAGADA' THEN total ELSE 0 END), 0) as total_pagado,
                    COALESCE(SUM(CASE WHEN estado = 'PENDIENTE' THEN total ELSE 0 END), 0) as total_pendiente,
                    COUNT(CASE WHEN estado = 'PENDIENTE' THEN 1 END) as count_pendientes,
                    COUNT(CASE WHEN estado = 'PAGADA' THEN 1 END) as count_pagadas
                FROM {self.TABLE_NAME}
                {where_clause}
            """

            result = self.fetch_one(query, tuple(params) if params else None)
            return result if result else {}

        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}

    def obtener_ingresos_por_mes(
        self, año: int = None  # type:ignore
    ) -> List[Dict[str, Any]]:
        """
        Obtiene ingresos agrupados por mes

        Args:
            año: Año para filtrar (opcional, por defecto año actual)

        Returns:
            Lista con ingresos por mes
        """
        try:
            if año is None:
                año = date.today().year

            query = f"""
                SELECT 
                    EXTRACT(MONTH FROM fecha_emision) as mes,
                    COUNT(*) as cantidad_facturas,
                    COALESCE(SUM(total), 0) as total_ingresos
                FROM {self.TABLE_NAME}
                WHERE EXTRACT(YEAR FROM fecha_emision) = %s 
                    AND anulada = FALSE 
                    AND estado = 'PAGADA'
                GROUP BY EXTRACT(MONTH FROM fecha_emision)
                ORDER BY mes
            """

            return self.fetch_all(query, (año,))
        except Exception as e:
            logger.error(f"❌ Error obteniendo ingresos por mes: {e}")
            return []

    # ============ MÉTODOS DE OPERACIÓN (para controlador) ============

    def marcar_factura_como_pagada(
        self, factura_id: int, forma_pago: str, referencia: str = None  # type:ignore
    ) -> bool:
        """
        Marca una factura como pagada

        Args:
            factura_id: ID de la factura
            forma_pago: Forma de pago utilizada
            referencia: Referencia del pago (opcional)

        Returns:
            True si la operación fue exitosa, False en caso contrario
        """
        try:
            datos = {
                "estado": "PAGADA",
                "forma_pago": forma_pago,
                "referencia_pago": referencia,
                "fecha_pago": datetime.now().strftime("%Y-%m-%d"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            return self.actualizar_factura(factura_id, datos)
        except Exception as e:
            logger.error(f"❌ Error marcando factura como pagada: {e}")
            return False

    def anular_factura(self, factura_id: int, motivo: str) -> bool:
        """
        Anula una factura

        Args:
            factura_id: ID de la factura
            motivo: Motivo de la anulación

        Returns:
            True si la operación fue exitosa, False en caso contrario
        """
        try:
            datos = {
                "estado": "ANULADA",
                "anulada": True,
                "motivo_anulacion": motivo,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            return self.actualizar_factura(factura_id, datos)
        except Exception as e:
            logger.error(f"❌ Error anulando factura: {e}")
            return False

    def generar_nuevo_numero_factura(self) -> str:
        """
        Genera un nuevo número de factura único

        Returns:
            Nuevo número de factura
        """
        try:
            # Obtener el máximo número actual
            query = f"SELECT MAX(numero) as ultimo_numero FROM {self.TABLE_NAME}"
            result = self.fetch_one(query)

            if result and result["ultimo_numero"]:
                try:
                    ultimo = int(result["ultimo_numero"])
                    nuevo = str(ultimo + 1).zfill(8)
                except ValueError:
                    # Si no es numérico, empezar desde 1
                    nuevo = "00000001"
            else:
                nuevo = "00000001"

            return nuevo
        except Exception as e:
            logger.error(f"❌ Error generando número de factura: {e}")
            # Número basado en fecha como respaldo
            return datetime.now().strftime("%Y%m%d") + "001"

    def existe_numero_factura(
        self, numero: str, excluir_id: int = None  # type:ignore
    ) -> bool:
        """
        Verifica si un número de factura ya existe

        Args:
            numero: Número de factura a verificar
            excluir_id: ID a excluir de la verificación (para actualizaciones)

        Returns:
            True si el número ya existe, False en caso contrario
        """
        try:
            if excluir_id:
                query = f"SELECT COUNT(*) as count FROM {self.TABLE_NAME} WHERE numero = %s AND id != %s"
                params = (numero, excluir_id)
            else:
                query = (
                    f"SELECT COUNT(*) as count FROM {self.TABLE_NAME} WHERE numero = %s"
                )
                params = (numero,)

            result = self.fetch_one(query, params)
            return result["count"] > 0 if result else False
        except Exception as e:
            logger.error(f"❌ Error verificando número de factura: {e}")
            return False

    # ============ MÉTODOS DE BÚSQUEDA (para controlador) ============

    def buscar_facturas(self, termino: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Busca facturas por término en varios campos

        Args:
            termino: Término de búsqueda
            limit: Límite de resultados

        Returns:
            Lista de facturas que coinciden con la búsqueda
        """
        try:
            search_term = f"%{termino}%"
            query = f"""
                SELECT * FROM {self.TABLE_NAME}
                WHERE (numero ILIKE %s OR 
                       cliente_nombre ILIKE %s OR 
                       cliente_cedula ILIKE %s OR 
                       observaciones ILIKE %s)
                AND anulada = FALSE
                ORDER BY fecha_emision DESC
                LIMIT %s
            """

            return self.fetch_all(
                query, (search_term, search_term, search_term, search_term, limit)
            )
        except Exception as e:
            logger.error(f"❌ Error buscando facturas: {e}")
            return []

    def obtener_ultimas_facturas(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene las últimas facturas creadas

        Args:
            limit: Límite de resultados

        Returns:
            Lista de las últimas facturas
        """
        try:
            query = f"""
                SELECT * FROM {self.TABLE_NAME} 
                WHERE anulada = FALSE
                ORDER BY created_at DESC 
                LIMIT %s
            """
            return self.fetch_all(query, (limit,))
        except Exception as e:
            logger.error(f"❌ Error obteniendo últimas facturas: {e}")
            return []

    # ============ MÉTODOS DE VALIDACIÓN (para controlador) ============

    def validar_datos_factura(self, datos: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Valida los datos de una factura antes de guardar

        Args:
            datos: Datos de la factura a validar

        Returns:
            Tuple: (es_válido, mensaje_error)
        """
        try:
            # Validar campos requeridos
            campos_requeridos = ["numero", "cliente_id", "fecha_emision", "total"]
            for campo in campos_requeridos:
                if campo not in datos or not datos[campo]:
                    return False, f"Campo requerido faltante: {campo}"

            # Validar número único
            if "numero" in datos:
                excluir_id = datos.get("id")
                if self.existe_numero_factura(
                    datos["numero"], excluir_id  # type:ignore
                ):
                    return False, f"El número de factura '{datos['numero']}' ya existe"

            # Validar estado
            if "estado" in datos and datos["estado"]:
                if datos["estado"] not in self.ESTADOS_VALIDOS:
                    return (
                        False,
                        f"Estado inválido. Válidos: {', '.join(self.ESTADOS_VALIDOS)}",
                    )

            # Validar montos positivos
            for campo in ["subtotal", "iva", "total"]:
                if campo in datos and datos[campo] is not None:
                    try:
                        valor = Decimal(str(datos[campo]))
                        if valor < 0:
                            return False, f"{campo} no puede ser negativo"
                    except:
                        return False, f"{campo} inválido"

            return True, "Datos válidos"
        except Exception as e:
            logger.error(f"❌ Error validando datos: {e}")
            return False, f"Error de validación: {str(e)}"

    # ============ MÉTODOS AUXILIARES ============

    def contar_facturas_por_estado(self, estado: str = None) -> int:  # type:ignore
        """
        Cuenta el total de facturas (opcionalmente por estado)

        Args:
            estado: Estado para filtrar (opcional)

        Returns:
            Número de facturas que coinciden
        """
        try:
            if estado:
                query = f"SELECT COUNT(*) as count FROM {self.TABLE_NAME} WHERE estado = %s AND anulada = FALSE"
                result = self.fetch_one(query, (estado,))
            else:
                query = f"SELECT COUNT(*) as count FROM {self.TABLE_NAME} WHERE anulada = FALSE"
                result = self.fetch_one(query)

            return result["count"] if result else 0
        except Exception as e:
            logger.error(f"❌ Error contando facturas: {e}")
            return 0


# Para compatibilidad con importaciones existentes que usan FacturaModel (singular)
FacturaModel = FacturasModel
