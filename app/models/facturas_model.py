# app/models/facturas_model.py
"""
Modelo para gestión de facturas emitidas en el sistema.

Este modelo maneja el registro, validación y consulta de facturas emitidas,
incluyendo validación de montos, tipos de documento y estados.

Hereda de BaseModel para utilizar el sistema de conexiones y transacciones.
Solo gestiona facturas emitidas (no recibidas) según requerimiento del cliente.
"""
import sys
import os
import logging
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Optional, List, Dict, Any, Tuple, Union
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_model import BaseModel

logger = logging.getLogger(__name__)


class FacturaModel(BaseModel):
    """Modelo que representa una factura emitida en el sistema"""

    def __init__(self):
        """Inicializa el modelo de facturas"""
        super().__init__()
        self.table_name = "facturas"
        self.sequence_name = "seq_facturas_id"

        # Tipos de documento válidos según CHECK constraint
        self.TIPOS_DOCUMENTO = ["NIT", "CI", "CONSUMIDOR_FINAL"]

        # Estados de factura
        self.ESTADOS = ["EMITIDA", "ANULADA", "PENDIENTE", "PAGADA", "CONTABILIZADA"]

        # Columnas de la tabla para validación
        self.columns = [
            "id",
            "nro_factura",
            "fecha_emision",
            "tipo_documento",
            "nit_ci",
            "razon_social",
            "subtotal",
            "iva",
            "it",
            "total",
            "concepto",
            "estado",
            "exportada_siat",
            "created_at",
        ]

        # Columnas requeridas
        self.required_columns = [
            "nro_factura",
            "fecha_emision",
            "razon_social",
            "subtotal",
            "iva",
            "it",
            "total",
        ]

        # Columnas de tipo decimal
        self.decimal_columns = ["subtotal", "iva", "it", "total"]

        # Columnas de tipo fecha
        self.date_columns = ["fecha_emision"]

        # Columnas de tipo booleano
        self.boolean_columns = ["exportada_siat"]

        # Tasa por defecto para cálculos (ajustable según legislación)
        self.TASA_IVA = Decimal("0.13")  # 13%
        self.TASA_IT = Decimal("0.03")  # 3%

        # Expresiones regulares para validación
        self.PATRON_NIT = re.compile(r"^\d{7,10}[-]?\d?$")
        self.PATRON_CI = re.compile(r"^\d{7,8}[A-Z]?$")
        self.PATRON_NRO_FACTURA = re.compile(r"^[A-Z0-9\-]+$")

    # ============ MÉTODOS DE VALIDACIÓN ============

    def _validate_factura_data(
        self, data: Dict[str, Any], for_update: bool = False
    ) -> Tuple[bool, str]:
        """
        Valida los datos de la factura antes de operaciones CRUD

        Args:
            data: Diccionario con datos de la factura
            for_update: Si es True, valida para actualización

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        # Campos requeridos para creación
        if not for_update:
            for field in self.required_columns:
                if field not in data or data[field] is None:
                    return False, f"Campo requerido faltante: {field}"

        # Validar número de factura único
        if "nro_factura" in data and data["nro_factura"]:
            existing_id = None
            if for_update and "id" in data:
                existing_id = data["id"]

            if self.nro_factura_exists(data["nro_factura"], exclude_id=existing_id):
                return False, f"El número de factura {data['nro_factura']} ya existe"

            # Validar formato del número de factura
            if not self.PATRON_NRO_FACTURA.match(str(data["nro_factura"])):
                return False, "Formato de número de factura inválido"

        # Validar tipo de documento
        if "tipo_documento" in data and data["tipo_documento"]:
            if data["tipo_documento"] not in self.TIPOS_DOCUMENTO:
                return (
                    False,
                    f"Tipo de documento inválido. Válidos: {', '.join(self.TIPOS_DOCUMENTO)}",
                )

            # Validar NIT/CI según tipo de documento
            tipo_doc = data["tipo_documento"]
            nit_ci = data.get("nit_ci", "")

            if tipo_doc in ["NIT", "CI"]:
                if not nit_ci:
                    return False, f"Tipo {tipo_doc} requiere NIT/CI"

                if tipo_doc == "NIT" and not self.PATRON_NIT.match(str(nit_ci)):
                    return False, "Formato de NIT inválido. Ejemplo: 123456789-0"

                if tipo_doc == "CI" and not self.PATRON_CI.match(str(nit_ci)):
                    return False, "Formato de CI inválido. Ejemplo: 1234567-BE"

            elif tipo_doc == "CONSUMIDOR_FINAL" and nit_ci:
                return False, "Consumidor final no debe tener NIT/CI"

        # Validar montos decimales positivos
        montos = ["subtotal", "iva", "it", "total"]
        for monto in montos:
            if monto in data and data[monto] is not None:
                try:
                    valor = self._to_decimal(data[monto])
                    if valor < Decimal("0"):
                        return False, f"El {monto} debe ser mayor o igual a 0"
                except (ValueError, InvalidOperation):
                    return (
                        False,
                        f"{monto.capitalize()} inválido. Debe ser un número decimal",
                    )

        # Validar que total = subtotal + iva + it (restricción de base de datos)
        if all(monto in data for monto in ["subtotal", "iva", "it", "total"]):
            subtotal = self._to_decimal(data["subtotal"])
            iva = self._to_decimal(data["iva"])
            it = self._to_decimal(data["it"])
            total = self._to_decimal(data["total"])

            total_calculado = subtotal + iva + it

            if total != total_calculado:
                return (
                    False,
                    f"Total incorrecto. Debería ser {total_calculado:.2f}, "
                    f"no {total:.2f}. Fórmula: subtotal + iva + it",
                )

        # Validar fecha de emisión
        if "fecha_emision" in data and data["fecha_emision"]:
            if not self._is_valid_date(data["fecha_emision"]):
                return False, "Formato de fecha inválido. Use YYYY-MM-DD"

            # No permitir fechas futuras
            try:
                fecha_emision = (
                    datetime.strptime(data["fecha_emision"], "%Y-%m-%d").date()
                    if isinstance(data["fecha_emision"], str)
                    else data["fecha_emision"]
                )
                if fecha_emision > date.today():
                    return False, "No se pueden registrar facturas con fecha futura"
            except:
                pass

        # Validar estado si se proporciona
        if "estado" in data and data["estado"]:
            if data["estado"] not in self.ESTADOS:
                return (False, f"Estado inválido. Válidos: {', '.join(self.ESTADOS)}")

        # Validar razón social
        if "razon_social" in data and data["razon_social"]:
            razon_social = str(data["razon_social"]).strip()
            if len(razon_social) < 3:
                return False, "La razón social debe tener al menos 3 caracteres"
            if len(razon_social) > 255:
                return False, "La razón social no puede exceder 255 caracteres"

        # Validar concepto si se proporciona
        if "concepto" in data and data["concepto"]:
            concepto = str(data["concepto"]).strip()
            if len(concepto) > 1000:
                return False, "El concepto no puede exceder 1000 caracteres"

        return True, "Datos válidos"

    def _to_decimal(self, value: Any) -> Decimal:
        """
        Convierte un valor a Decimal de forma segura

        Args:
            value: Valor a convertir

        Returns:
            Decimal: Valor convertido
        """
        if value is None:
            return Decimal("0")
        if isinstance(value, Decimal):
            return value
        try:
            return Decimal(str(value).replace(",", ""))
        except (ValueError, InvalidOperation):
            return Decimal("0")

    def _is_valid_date(self, date_value: Any) -> bool:
        """Valida formato de fecha"""
        if isinstance(date_value, str):
            try:
                datetime.strptime(date_value, "%Y-%m-%d")
                return True
            except ValueError:
                return False
        elif isinstance(date_value, (datetime, date)):
            return True
        return False

    def nro_factura_exists(
        self, nro_factura: str, exclude_id: Optional[int] = None
    ) -> bool:
        """
        Verifica si un número de factura ya existe

        Args:
            nro_factura: Número de factura a verificar
            exclude_id: ID a excluir de la verificación (para updates)

        Returns:
            bool: True si existe, False en caso contrario
        """
        try:
            if exclude_id:
                query = """
                SELECT COUNT(*) as count 
                FROM facturas 
                WHERE nro_factura = %s AND id != %s
                """
                params = (nro_factura, exclude_id)
            else:
                query = "SELECT COUNT(*) as count FROM facturas WHERE nro_factura = %s"
                params = (nro_factura,)

            result = self.fetch_one(query, params)
            return result["count"] > 0 if result else False
        except Exception as e:
            logger.error(f"Error verificando número de factura: {e}")
            return False

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza los datos de la factura

        Args:
            data: Diccionario con datos crudos

        Returns:
            Dict[str, Any]: Datos sanitizados
        """
        sanitized = {}

        for key, value in data.items():
            if key in self.columns:
                # Sanitizar strings
                if isinstance(value, str):
                    sanitized[key] = value.strip()
                # Convertir decimales
                elif key in self.decimal_columns and value is not None:
                    sanitized[key] = self._to_decimal(value)
                # Convertir booleanos
                elif key in self.boolean_columns and value is not None:
                    sanitized[key] = (
                        bool(int(value))
                        if isinstance(value, (int, float, str))
                        else bool(value)
                    )
                # Formatear fecha
                elif key in self.date_columns and value is not None:
                    if isinstance(value, str):
                        sanitized[key] = value
                    elif isinstance(value, datetime):
                        sanitized[key] = value.strftime("%Y-%m-%d")
                    elif isinstance(value, date):
                        sanitized[key] = value.strftime("%Y-%m-%d")
                # Mantener otros tipos
                else:
                    sanitized[key] = value

        return sanitized

    # ============ MÉTODOS DE CÁLCULO ============

    def calcular_totales(
        self,
        subtotal: Union[Decimal, float, str],
        aplicar_iva: bool = True,
        aplicar_it: bool = False,
        tasa_iva: Optional[Decimal] = None,
        tasa_it: Optional[Decimal] = None,
    ) -> Dict[str, Decimal]:
        """
        Calcula los totales de una factura a partir del subtotal

        Args:
            subtotal: Subtotal de la factura
            aplicar_iva: Si True, aplicar IVA (por defecto True)
            aplicar_it: Si True, aplicar IT (por defecto False)
            tasa_iva: Tasa de IVA personalizada (por defecto 13%)
            tasa_it: Tasa de IT personalizada (por defecto 3%)

        Returns:
            Dict[str, Decimal]: Diccionario con subtotal, iva, it, total
        """
        try:
            # Convertir y validar subtotal
            subtotal_dec = self._to_decimal(subtotal)
            if subtotal_dec <= Decimal("0"):
                raise ValueError("El subtotal debe ser mayor a 0")

            # Usar tasas por defecto si no se proporcionan
            if tasa_iva is None:
                tasa_iva = self.TASA_IVA
            if tasa_it is None:
                tasa_it = self.TASA_IT

            # Calcular impuestos
            iva = subtotal_dec * tasa_iva if aplicar_iva else Decimal("0")
            it = subtotal_dec * tasa_it if aplicar_it else Decimal("0")
            total = subtotal_dec + iva + it

            # Redondear a 2 decimales
            iva = iva.quantize(Decimal("0.01"))
            it = it.quantize(Decimal("0.01"))
            total = total.quantize(Decimal("0.01"))

            return {"subtotal": subtotal_dec, "iva": iva, "it": it, "total": total}

        except Exception as e:
            logger.error(f"Error calculando totales: {e}")
            raise

    def calcular_desde_subtotal(
        self, subtotal: Union[Decimal, float, str], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calcula y establece totales a partir del subtotal en datos existentes

        Args:
            subtotal: Nuevo subtotal
            data: Datos existentes de la factura

        Returns:
            Dict[str, Any]: Datos actualizados con totales calculados
        """
        # Obtener configuración de impuestos de los datos existentes
        aplicar_iva = data.get("aplicar_iva", True)
        aplicar_it = data.get("aplicar_it", False)

        # Calcular nuevos totales
        totales = self.calcular_totales(subtotal, aplicar_iva, aplicar_it)

        # Actualizar datos
        data_actualizado = data.copy()
        data_actualizado["subtotal"] = totales["subtotal"]
        data_actualizado["iva"] = totales["iva"]
        data_actualizado["it"] = totales["it"]
        data_actualizado["total"] = totales["total"]

        return data_actualizado

    # ============ MÉTODOS CRUD PRINCIPALES ============

    def create(
        self, data: Dict[str, Any], calcular_totales_auto: bool = False
    ) -> Optional[int]:
        """
        Crea una nueva factura

        Args:
            data: Diccionario con datos de la factura
            calcular_totales_auto: Si True, calcula automáticamente totales desde subtotal

        Returns:
            Optional[int]: ID de la factura creada o None si hay error
        """
        # Sanitizar datos
        data = self._sanitize_data(data)

        # Calcular totales automáticamente si se solicita
        if calcular_totales_auto and "subtotal" in data:
            data = self.calcular_desde_subtotal(data["subtotal"], data)

        # Validar datos
        is_valid, error_msg = self._validate_factura_data(data, for_update=False)

        if not is_valid:
            logger.error(f"Error validando datos de factura: {error_msg}")
            return None

        try:
            # Iniciar transacción
            self.begin_transaction()

            # Preparar datos para inserción
            insert_data = data.copy()

            # Establecer valores por defecto
            defaults = {
                "estado": "EMITIDA",
                "exportada_siat": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            for key, value in defaults.items():
                if key not in insert_data or insert_data[key] is None:
                    insert_data[key] = value

            # Insertar en base de datos
            factura_id = self.insert(self.table_name, insert_data, returning="id")

            if not factura_id:
                self.rollback()
                logger.error("No se pudo insertar la factura en la base de datos")
                return None

            logger.info(f"✓ Factura creada exitosamente con ID: {factura_id}")

            # Commit de la transacción
            self.commit()
            logger.info(f"✓ Transacción completada para factura ID: {factura_id}")

            # Registrar auditoría
            self._registrar_auditoria("CREACION", factura_id, None)

            return factura_id

        except Exception as e:
            # Rollback en caso de error
            self.rollback()
            logger.error(f"Error creando factura: {e}", exc_info=True)
            return None

    def read(self, factura_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene una factura por su ID

        Args:
            factura_id: ID de la factura

        Returns:
            Optional[Dict]: Datos de la factura o None si no existe
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE id = %s"
            result = self.fetch_one(query, (factura_id,))

            if result:
                # Formatear valores para mejor presentación
                result = self._formatear_resultado(result)

            return result

        except Exception as e:
            logger.error(f"Error obteniendo factura: {e}")
            return None

    def read_by_nro_factura(self, nro_factura: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene una factura por su número de factura

        Args:
            nro_factura: Número de factura

        Returns:
            Optional[Dict]: Datos de la factura o None si no existe
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE nro_factura = %s"
            result = self.fetch_one(query, (nro_factura,))

            if result:
                # Formatear valores para mejor presentación
                result = self._formatear_resultado(result)

            return result

        except Exception as e:
            logger.error(f"Error obteniendo factura por número: {e}")
            return None

    def update(
        self, factura_id: int, data: Dict[str, Any], calcular_totales_auto: bool = False
    ) -> bool:
        """
        Actualiza una factura existente

        Args:
            factura_id: ID de la factura a actualizar
            data: Diccionario con datos a actualizar
            calcular_totales_auto: Si True, calcula automáticamente totales desde subtotal

        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        if not data:
            return False

        # Obtener datos actuales para validación
        factura_actual = self.read(factura_id)
        if not factura_actual:
            return False

        # Calcular totales automáticamente si se solicita
        if calcular_totales_auto and "subtotal" in data:
            # Combinar datos actuales con nuevos para cálculo
            datos_calculo = {**factura_actual, **data}
            data = self.calcular_desde_subtotal(data["subtotal"], datos_calculo)

        # Combinar datos actuales con los nuevos para validación
        data_with_id = {**factura_actual, **data}
        data_with_id["id"] = factura_id

        # Sanitizar y validar datos
        data = self._sanitize_data(data)
        is_valid, error_msg = self._validate_factura_data(data_with_id, for_update=True)

        if not is_valid:
            logger.error(f"Error validando datos: {error_msg}")
            return False

        try:
            # Iniciar transacción
            self.begin_transaction()

            # No permitir actualizar facturas exportadas a SIAT
            if factura_actual.get("exportada_siat"):
                logger.warning(
                    f"Factura {factura_id} ya exportada a SIAT. Actualización limitada."
                )
                # Podrías limitar qué campos se pueden actualizar aquí

            # Actualizar en base de datos
            result = self.execute_query(
                f"UPDATE {self.table_name} SET "
                + ", ".join([f"{k} = %s" for k in data.keys()])
                + " WHERE id = %s",
                tuple(data.values()) + (factura_id,),
                commit=True,
            )

            if not result:
                self.rollback()
                return False

            logger.info(f"✓ Factura {factura_id} actualizada exitosamente")

            # Commit de la transacción
            self.commit()

            # Registrar auditoría
            self._registrar_auditoria("ACTUALIZACION", factura_id, None)

            return True

        except Exception as e:
            self.rollback()
            logger.error(f"Error actualizando factura: {e}", exc_info=True)
            return False

    def delete(self, factura_id: int) -> bool:
        """
        Elimina una factura

        Args:
            factura_id: ID de la factura

        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            # Verificar si la factura existe
            factura = self.read(factura_id)
            if not factura:
                return False

            # No permitir eliminar facturas exportadas a SIAT
            if factura.get("exportada_siat"):
                logger.error(
                    f"No se puede eliminar factura {factura_id} ya exportada a SIAT"
                )
                return False

            # No permitir eliminar facturas emitidas hace mucho tiempo
            fecha_emision = datetime.strptime(
                factura["fecha_emision"], "%Y-%m-%d"
            ).date()
            dias_diferencia = (date.today() - fecha_emision).days

            if dias_diferencia > 30:
                logger.error("No se pueden eliminar facturas de más de 30 días")
                return False

            # Cambiar estado a ANULADA en lugar de eliminar (mejor práctica)
            logger.info(f"Cambiando estado de factura {factura_id} a ANULADA")
            return self.update(factura_id, {"estado": "ANULADA"})

            # Para eliminación física (no recomendado):
            # query = f"DELETE FROM {self.table_name} WHERE id = %s"
            # result = self.execute_query(query, (factura_id,), commit=True)
            # return bool(result)

        except Exception as e:
            logger.error(f"Error eliminando factura: {e}", exc_info=True)
            return False

    def anular(self, factura_id: int, motivo: Optional[str] = None) -> bool:
        """
        Anula una factura cambiando su estado

        Args:
            factura_id: ID de la factura
            motivo: Motivo de la anulación (opcional)

        Returns:
            bool: True si se anuló correctamente
        """
        try:
            update_data = {"estado": "ANULADA"}
            if motivo:
                # Agregar motivo al concepto
                factura = self.read(factura_id)
                if factura and factura.get("concepto"):
                    nuevo_concepto = f"{factura['concepto']} [ANULADA: {motivo}]"
                    update_data["concepto"] = nuevo_concepto

            return self.update(factura_id, update_data)

        except Exception as e:
            logger.error(f"Error anulando factura: {e}")
            return False

    # ============ MÉTODOS DE CONSULTA AVANZADOS ============

    def buscar_por_fecha(
        self,
        fecha_inicio: Optional[Union[str, date]] = None,
        fecha_fin: Optional[Union[str, date]] = None,
        estado: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Busca facturas por rango de fechas

        Args:
            fecha_inicio: Fecha de inicio (opcional)
            fecha_fin: Fecha de fin (opcional)
            estado: Estado específico (opcional)
            limit: Límite de resultados
            offset: Desplazamiento para paginación

        Returns:
            List[Dict]: Lista de facturas encontradas
        """
        try:
            condiciones = []
            params = []

            if fecha_inicio:
                condiciones.append("fecha_emision >= %s")
                fecha_inicio_str = (
                    fecha_inicio
                    if isinstance(fecha_inicio, str)
                    else fecha_inicio.strftime("%Y-%m-%d")
                )
                params.append(fecha_inicio_str)

            if fecha_fin:
                condiciones.append("fecha_emision <= %s")
                fecha_fin_str = (
                    fecha_fin
                    if isinstance(fecha_fin, str)
                    else fecha_fin.strftime("%Y-%m-%d")
                )
                params.append(fecha_fin_str)

            if estado:
                condiciones.append("estado = %s")
                params.append(estado)

            where_clause = "WHERE " + " AND ".join(condiciones) if condiciones else ""

            query = f"""
                SELECT * FROM {self.table_name}
                {where_clause}
                ORDER BY fecha_emision DESC, nro_factura DESC
                LIMIT %s OFFSET %s
            """

            params.extend([limit, offset])
            results = self.fetch_all(query, tuple(params))

            # Formatear resultados
            return (
                [self._formatear_resultado(row) for row in results] if results else []
            )

        except Exception as e:
            logger.error(f"Error buscando facturas por fecha: {e}")
            return []

    def buscar_por_cliente(
        self,
        razon_social: Optional[str] = None,
        nit_ci: Optional[str] = None,
        tipo_documento: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Busca facturas por datos del cliente

        Args:
            razon_social: Razón social o parte de ella (opcional)
            nit_ci: NIT o CI (opcional)
            tipo_documento: Tipo de documento (opcional)
            limit: Límite de resultados

        Returns:
            List[Dict]: Lista de facturas encontradas
        """
        try:
            condiciones = []
            params = []

            if razon_social:
                condiciones.append("razon_social ILIKE %s")
                params.append(f"%{razon_social}%")

            if nit_ci:
                condiciones.append("nit_ci ILIKE %s")
                params.append(f"%{nit_ci}%")

            if tipo_documento:
                condiciones.append("tipo_documento = %s")
                params.append(tipo_documento)

            where_clause = "WHERE " + " AND ".join(condiciones) if condiciones else ""

            query = f"""
                SELECT * FROM {self.table_name}
                {where_clause}
                ORDER BY fecha_emision DESC
                LIMIT %s
            """

            params.append(limit)
            results = self.fetch_all(query, tuple(params))

            # Formatear resultados
            return (
                [self._formatear_resultado(row) for row in results] if results else []
            )

        except Exception as e:
            logger.error(f"Error buscando facturas por cliente: {e}")
            return []

    def buscar_por_estado(
        self, estado: str, exportada_siat: Optional[bool] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Busca facturas por estado

        Args:
            estado: Estado de la factura
            exportada_siat: Si está exportada a SIAT (opcional)
            limit: Límite de resultados

        Returns:
            List[Dict]: Lista de facturas encontradas
        """
        try:
            if estado not in self.ESTADOS:
                logger.warning(f"Estado '{estado}' no válido")
                return []

            condiciones = ["estado = %s"]
            params = [estado]

            if exportada_siat is not None:
                condiciones.append("exportada_siat = %s")
                params.append(exportada_siat)  # type: ignore

            where_clause = "WHERE " + " AND ".join(condiciones)

            query = f"""
                SELECT * FROM {self.table_name}
                {where_clause}
                ORDER BY fecha_emision DESC
                LIMIT %s
            """

            params.append(limit)  # type: ignore
            results = self.fetch_all(query, tuple(params))

            # Formatear resultados
            return (
                [self._formatear_resultado(row) for row in results] if results else []
            )

        except Exception as e:
            logger.error(f"Error buscando facturas por estado: {e}")
            return []

    def obtener_resumen_mensual(
        self, año: int, mes: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene un resumen de facturas mensual

        Args:
            año: Año del resumen
            mes: Mes del resumen (1-12, opcional)

        Returns:
            Dict[str, Any]: Diccionario con el resumen mensual
        """
        try:
            condiciones = ["EXTRACT(YEAR FROM fecha_emision) = %s"]
            params = [float(año)]

            if mes:
                condiciones.append("EXTRACT(MONTH FROM fecha_emision) = %s")
                params.append(float(mes))

            where_clause = "WHERE " + " AND ".join(condiciones)

            # Consulta para totales
            query_totales = f"""
                SELECT 
                    COUNT(*) as total_facturas,
                    SUM(subtotal) as subtotal_total,
                    SUM(iva) as iva_total,
                    SUM(it) as it_total,
                    SUM(total) as total_general,
                    AVG(total) as promedio_factura,
                    MIN(fecha_emision) as primera_fecha,
                    MAX(fecha_emision) as ultima_fecha
                FROM {self.table_name}
                {where_clause}
                AND estado != 'ANULADA'
            """

            totales = self.fetch_one(query_totales, tuple(params))

            # Consulta por estado
            query_estados = f"""
                SELECT 
                    estado,
                    COUNT(*) as cantidad,
                    SUM(total) as total
                FROM {self.table_name}
                {where_clause}
                GROUP BY estado
                ORDER BY total DESC
            """

            estados = self.fetch_all(query_estados, tuple(params))

            # Consulta por tipo de documento
            query_tipos = f"""
                SELECT 
                    tipo_documento,
                    COUNT(*) as cantidad,
                    SUM(total) as total
                FROM {self.table_name}
                {where_clause}
                GROUP BY tipo_documento
                ORDER BY total DESC
            """

            tipos = self.fetch_all(query_tipos, tuple(params))

            return {
                "periodo": f"{año}-{mes:02d}" if mes else str(año),
                "totales": totales if totales else {},
                "por_estado": estados if estados else [],
                "por_tipo_documento": tipos if tipos else [],
            }

        except Exception as e:
            logger.error(f"Error obteniendo resumen mensual: {e}")
            return {}

    def obtener_siguiente_numero(
        self, prefijo: str = "FAC-", longitud_secuencia: int = 6
    ) -> str:
        """
        Obtiene el siguiente número de factura disponible

        Args:
            prefijo: Prefijo para el número de factura
            longitud_secuencia: Longitud de la secuencia numérica

        Returns:
            str: Siguiente número de factura disponible
        """
        try:
            # Buscar el último número con el prefijo dado
            query = f"""
                SELECT nro_factura
                FROM {self.table_name}
                WHERE nro_factura LIKE %s
                ORDER BY LENGTH(nro_factura) DESC, nro_factura DESC
                LIMIT 1
            """

            result = self.fetch_one(query, (f"{prefijo}%",))

            if not result:
                return f"{prefijo}{1:0{longitud_secuencia}d}"

            ultimo_numero = result["nro_factura"]

            # Extraer la parte numérica
            try:
                # Asumir formato: PREFIJO-NUMERO
                numero_str = ultimo_numero.replace(prefijo, "")
                numero = int(numero_str)
                siguiente = numero + 1
                return f"{prefijo}{siguiente:0{longitud_secuencia}d}"
            except ValueError:
                # Si hay error en el formato, usar timestamp
                timestamp = int(datetime.now().timestamp())
                return f"{prefijo}{timestamp}"

        except Exception as e:
            logger.error(f"Error obteniendo siguiente número de factura: {e}")
            # Fallback: usar timestamp
            timestamp = int(datetime.now().timestamp())
            return f"{prefijo}{timestamp}"

    # ============ MÉTODOS DE UTILIDAD ============

    def _formatear_resultado(self, resultado: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formatea los resultados para mejor presentación

        Args:
            resultado: Diccionario con datos de la base de datos

        Returns:
            Dict[str, Any]: Datos formateados
        """
        if not resultado:
            return {}

        formateado = resultado.copy()

        # Formatear decimales como strings para mejor presentación
        for campo in self.decimal_columns:
            if campo in formateado and formateado[campo] is not None:
                try:
                    valor = self._to_decimal(formateado[campo])
                    formateado[f"{campo}_formateado"] = f"Bs. {valor:,.2f}"
                except:
                    formateado[f"{campo}_formateado"] = str(formateado[campo])

        # Formatear fecha
        if "fecha_emision" in formateado and formateado["fecha_emision"]:
            try:
                fecha = (
                    datetime.strptime(formateado["fecha_emision"], "%Y-%m-%d")
                    if isinstance(formateado["fecha_emision"], str)
                    else formateado["fecha_emision"]
                )
                formateado["fecha_emision_formateada"] = fecha.strftime("%d/%m/%Y")
            except:
                formateado["fecha_emision_formateada"] = str(
                    formateado["fecha_emision"]
                )

        # Formatear estado
        if "estado" in formateado:
            estado = formateado["estado"]
            descripciones = {
                "EMITIDA": "Emitida",
                "ANULADA": "Anulada",
                "PENDIENTE": "Pendiente",
                "PAGADA": "Pagada",
                "CONTABILIZADA": "Contabilizada",
            }
            formateado["estado_descripcion"] = descripciones.get(estado, estado)

        # Formatear tipo de documento
        if "tipo_documento" in formateado:
            tipo = formateado["tipo_documento"]
            descripciones = {
                "NIT": "NIT",
                "CI": "Cédula de Identidad",
                "CONSUMIDOR_FINAL": "Consumidor Final",
            }
            formateado["tipo_documento_descripcion"] = descripciones.get(tipo, tipo)

        # Formatear exportada SIAT
        if "exportada_siat" in formateado:
            formateado["exportada_siat_descripcion"] = (
                "Sí" if formateado["exportada_siat"] else "No"
            )

        return formateado

    def _registrar_auditoria(
        self, accion: str, factura_id: int, usuario_id: Optional[int] = None
    ) -> None:
        """
        Registra una acción en el log de auditoría

        Args:
            accion: Tipo de acción (CREACION, ACTUALIZACION, ELIMINACION)
            factura_id: ID de la factura
            usuario_id: ID del usuario que realizó la acción
        """
        try:
            # En una implementación real, insertar en tabla de auditoría
            logger.info(
                f"AUDITORIA - Factura {factura_id} - Acción: {accion} - "
                f"Usuario: {usuario_id or 'SISTEMA'} - "
                f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        except Exception:
            pass

    def validar_para_siat(self, factura_id: int) -> Tuple[bool, List[str]]:
        """
        Valida si una factura cumple requisitos para exportar a SIAT

        Args:
            factura_id: ID de la factura

        Returns:
            Tuple[bool, List[str]]: (es_válida, lista_de_errores)
        """
        try:
            factura = self.read(factura_id)
            if not factura:
                return False, ["Factura no encontrada"]

            errores = []

            # Verificar estado
            if factura.get("estado") != "EMITIDA":
                errores.append("La factura debe estar en estado EMITIDA")

            # Verificar que ya no esté exportada
            if factura.get("exportada_siat"):
                errores.append("La factura ya fue exportada a SIAT")

            # Verificar datos del cliente
            tipo_doc = factura.get("tipo_documento")
            nit_ci = factura.get("nit_ci")

            if tipo_doc in ["NIT", "CI"] and not nit_ci:
                errores.append(f"Factura tipo {tipo_doc} requiere NIT/CI")

            if tipo_doc == "NIT" and nit_ci:
                if not self.PATRON_NIT.match(str(nit_ci)):
                    errores.append("Formato de NIT inválido para SIAT")

            # Verificar montos
            for campo in ["subtotal", "iva", "it", "total"]:
                valor = factura.get(campo)
                if valor is None or Decimal(str(valor)) < Decimal("0"):
                    errores.append(f"Campo {campo} inválido")

            # Verificar que total = subtotal + iva + it
            subtotal = self._to_decimal(factura.get("subtotal", 0))
            iva = self._to_decimal(factura.get("iva", 0))
            it = self._to_decimal(factura.get("it", 0))
            total = self._to_decimal(factura.get("total", 0))

            if total != subtotal + iva + it:
                errores.append("Total no coincide con subtotal + iva + it")

            return len(errores) == 0, errores

        except Exception as e:
            logger.error(f"Error validando para SIAT: {e}")
            return False, [f"Error de validación: {str(e)}"]

    def exportar_a_siat(self, factura_id: int) -> bool:
        """
        Marca una factura como exportada a SIAT

        Args:
            factura_id: ID de la factura

        Returns:
            bool: True si se marcó como exportada
        """
        try:
            # Validar que se puede exportar
            es_valida, errores = self.validar_para_siat(factura_id)
            if not es_valida:
                logger.error(f"Factura {factura_id} no válida para SIAT: {errores}")
                return False

            # Marcar como exportada
            return self.update(factura_id, {"exportada_siat": True})

        except Exception as e:
            logger.error(f"Error exportando a SIAT: {e}")
            return False

    # ============ MÉTODOS DE REPORTES ============

    def generar_reporte_facturacion(
        self,
        fecha_inicio: str,
        fecha_fin: str,
        estado: Optional[str] = None,
        tipo_documento: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Genera un reporte detallado de facturación

        Args:
            fecha_inicio: Fecha de inicio del reporte
            fecha_fin: Fecha de fin del reporte
            estado: Estado específico (opcional)
            tipo_documento: Tipo de documento específico (opcional)

        Returns:
            Dict[str, Any]: Reporte de facturación
        """
        try:
            # Validar fechas
            if not self._is_valid_date(fecha_inicio) or not self._is_valid_date(
                fecha_fin
            ):
                return {"error": "Formato de fecha inválido"}

            condiciones = ["fecha_emision >= %s", "fecha_emision <= %s"]
            params = [fecha_inicio, fecha_fin]

            if estado:
                condiciones.append("estado = %s")
                params.append(estado)

            if tipo_documento:
                condiciones.append("tipo_documento = %s")
                params.append(tipo_documento)

            where_sql = " AND ".join(condiciones)

            # Obtener facturas detalladas
            query_detalle = f"""
                SELECT * FROM {self.table_name}
                WHERE {where_sql}
                ORDER BY fecha_emision DESC, nro_factura DESC
            """

            facturas = self.fetch_all(query_detalle, tuple(params))

            # Obtener resumen por estado
            query_resumen_estado = f"""
                SELECT 
                    estado,
                    COUNT(*) as cantidad,
                    SUM(subtotal) as subtotal,
                    SUM(iva) as iva,
                    SUM(it) as it,
                    SUM(total) as total
                FROM {self.table_name}
                WHERE {where_sql}
                GROUP BY estado
                ORDER BY total DESC
            """

            resumen_estado = self.fetch_all(query_resumen_estado, tuple(params))

            # Obtener resumen por tipo de documento
            query_resumen_tipo = f"""
                SELECT 
                    tipo_documento,
                    COUNT(*) as cantidad,
                    SUM(total) as total
                FROM {self.table_name}
                WHERE {where_sql}
                GROUP BY tipo_documento
                ORDER BY total DESC
            """

            resumen_tipo = self.fetch_all(query_resumen_tipo, tuple(params))

            # Calcular totales generales
            total_facturas = len(facturas) if facturas else 0
            total_general = Decimal("0")

            for factura in facturas or []:
                total_general += self._to_decimal(factura.get("total", 0))

            return {
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "total_facturas": total_facturas,
                "total_general": total_general,
                "detalle_facturas": (
                    [self._formatear_resultado(f) for f in facturas] if facturas else []
                ),
                "resumen_por_estado": resumen_estado if resumen_estado else [],
                "resumen_por_tipo_documento": resumen_tipo if resumen_tipo else [],
                "generado_en": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

        except Exception as e:
            logger.error(f"Error generando reporte de facturación: {e}")
            return {"error": str(e)}


# Ejemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)

    # Crear instancia del modelo
    factura_model = FacturaModel()

    # Datos de ejemplo para crear una factura
    datos_factura = {
        "nro_factura": "FAC-20241227-0001",
        "fecha_emision": "2024-12-27",
        "tipo_documento": "NIT",
        "nit_ci": "123456789-0",
        "razon_social": "EMPRESA EJEMPLO S.A.",
        "subtotal": 1000.00,
        "iva": 130.00,
        "it": 30.00,
        "total": 1160.00,
        "concepto": "Servicios de consultoría diciembre 2024",
        "estado": "EMITIDA",
    }

    # Crear factura
    print("=== Creando nueva factura ===")
    factura_id = factura_model.create(datos_factura)

    if factura_id:
        print(f"✓ Factura creada con ID: {factura_id}")

        # Leer factura creada
        print("\n=== Leyendo factura creada ===")
        factura = factura_model.read(factura_id)
        if factura:
            print(
                f"Factura {factura['nro_factura']}: {factura['razon_social']} - Bs. {factura['total']}"
            )

        # Buscar facturas por fecha
        print("\n=== Buscando facturas por fecha ===")
        facturas_hoy = factura_model.buscar_por_fecha("2024-12-27", "2024-12-27")
        print(f"Facturas encontradas: {len(facturas_hoy)}")

        # Obtener resumen mensual
        print("\n=== Resumen mensual ===")
        resumen = factura_model.obtener_resumen_mensual(2024, 12)
        print(
            f"Total general: Bs. {resumen.get('totales', {}).get('total_general', 0)}"
        )

    print("\n=== Fin del ejemplo ===")
