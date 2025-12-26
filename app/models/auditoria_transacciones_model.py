# app/models/auditoria_transacciones_model.py
"""
Modelo para gestión de auditoría de transacciones del sistema.

Este modelo registra todas las acciones críticas del sistema (creación, modificación,
eliminación, anulación) sobre ingresos y gastos para fines de auditoría, trazabilidad
y pericia informática.

Hereda de BaseModel para utilizar el sistema de conexiones y transacciones.
"""

import sys
import os
import json
import logging
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any, Tuple, Union
from decimal import Decimal
import hashlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_model import BaseModel

logger = logging.getLogger(__name__)


class AuditoriaTransaccionesModel(BaseModel):
    """Modelo que representa un registro de auditoría de transacciones"""

    def __init__(self):
        """Inicializa el modelo de auditoría"""
        super().__init__()
        self.table_name = "auditoria_transacciones"
        self.sequence_name = "seq_auditoria_transacciones_id"

        # Tipos de origen según CHECK constraint
        self.ORIGEN_TIPOS = ["INGRESO", "GASTO"]

        # Acciones según CHECK constraint
        self.ACCIONES = ["CREACION", "MODIFICACION", "ELIMINACION", "ANULACION"]

        # Niveles de severidad para filtrado y alertas
        self.NIVELES_SEVERIDAD = {
            "CREACION": "INFO",
            "MODIFICACION": "MEDIO",
            "ANULACION": "ALTO",
            "ELIMINACION": "CRITICO",
        }

        # Columnas de la tabla
        self.columns = [
            "id",
            "fecha_hora",
            "usuario_id",
            "origen_tipo",
            "origen_id",
            "accion",
            "motivo",
            "responsable_autoriza",
            "ruta_resolucion",
            "datos_anteriores",
            "datos_nuevos",
        ]

        # Columnas requeridas
        self.required_columns = [
            "usuario_id",
            "origen_tipo",
            "origen_id",
            "accion",
            "motivo",
        ]

        # Columnas de tipo entero
        self.integer_columns = ["usuario_id", "origen_id"]

        # Columnas de tipo fecha/hora
        self.datetime_columns = ["fecha_hora"]

        # Configuración de retención (días)
        self.RETENCION_DIAS = 365  # 1 año por defecto

        # Límites de consulta
        self.LIMITE_CONSULTA = 1000

    # ============ MÉTODOS DE VALIDACIÓN ============

    def _validate_auditoria_data(
        self, data: Dict[str, Any], for_update: bool = False
    ) -> Tuple[bool, str]:
        """
        Valida los datos del registro de auditoría

        Args:
            data: Diccionario con datos de auditoría
            for_update: Si es True, valida para actualización

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        # Campos requeridos
        if not for_update:
            for field in self.required_columns:
                if field not in data or data[field] is None:
                    return False, f"Campo requerido faltante: {field}"

        # Validar tipo de origen
        if "origen_tipo" in data and data["origen_tipo"]:
            if data["origen_tipo"] not in self.ORIGEN_TIPOS:
                return (
                    False,
                    f"Tipo de origen inválido. Válidos: {', '.join(self.ORIGEN_TIPOS)}",
                )

        # Validar acción
        if "accion" in data and data["accion"]:
            if data["accion"] not in self.ACCIONES:
                return (False, f"Acción inválida. Válidas: {', '.join(self.ACCIONES)}")

        # Validar usuario_id
        if "usuario_id" in data and data["usuario_id"]:
            if not self._usuario_exists(data["usuario_id"]):
                return False, f"Usuario con ID {data['usuario_id']} no existe"

        # Validar origen_id según tipo
        if "origen_id" in data and data["origen_id"] and "origen_tipo" in data:
            origen_tipo = data["origen_tipo"]
            origen_id = data["origen_id"]

            if not self._origen_exists(origen_tipo, origen_id):
                logger.warning(
                    f"Origen {origen_tipo} con ID {origen_id} no existe. "
                    "Registrando auditoría de todos modos."
                )
                # No retornamos error aquí porque podría ser auditoría de eliminación

        # Validar motivo
        if "motivo" in data and data["motivo"]:
            motivo = str(data["motivo"]).strip()
            if len(motivo) < 5:
                return False, "El motivo debe tener al menos 5 caracteres"
            if len(motivo) > 500:
                return False, "El motivo no puede exceder 500 caracteres"

        # Validar responsable_autoriza si se proporciona
        if "responsable_autoriza" in data and data["responsable_autoriza"]:
            responsable = str(data["responsable_autoriza"]).strip()
            if len(responsable) > 200:
                return False, "El responsable no puede exceder 200 caracteres"

        # Validar ruta_resolucion si se proporciona
        if "ruta_resolucion" in data and data["ruta_resolucion"]:
            ruta = str(data["ruta_resolucion"]).strip()
            if len(ruta) > 500:
                return False, "La ruta de resolución no puede exceder 500 caracteres"
            # Validar que sea una ruta válida (opcional)
            if not (ruta.startswith("/") or "\\" in ruta or "." in ruta):
                logger.warning(f"Ruta de resolución podría no ser válida: {ruta}")

        # Validar datos_anteriores y datos_nuevos si se proporcionan
        for campo in ["datos_anteriores", "datos_nuevos"]:
            if campo in data and data[campo]:
                try:
                    # Intentar validar como JSON si es string
                    if isinstance(data[campo], str):
                        json.loads(data[campo])
                    elif isinstance(data[campo], (dict, list)):
                        json.dumps(data[campo])  # Validar que sea serializable
                except (json.JSONDecodeError, TypeError) as e:
                    return (
                        False,
                        f"{campo.replace('_', ' ').title()} no es JSON válido: {e}",
                    )

        return True, "Datos válidos"

    def _usuario_exists(self, usuario_id: int) -> bool:
        """Verifica si el usuario existe"""
        try:
            query = "SELECT COUNT(*) as count FROM usuarios WHERE id = %s"
            result = self.fetch_one(query, (usuario_id,))
            return result["count"] > 0 if result else False
        except Exception as e:
            logger.warning(f"No se pudo verificar usuario con ID {usuario_id}: {e}")
            return True  # Asumir que existe para permitir auditoría

    def _origen_exists(self, origen_tipo: str, origen_id: int) -> bool:
        """Verifica si el origen existe"""
        try:
            if origen_tipo == "INGRESO":
                query = "SELECT COUNT(*) as count FROM ingresos WHERE id = %s"
            elif origen_tipo == "GASTO":
                query = "SELECT COUNT(*) as count FROM gastos WHERE id = %s"
            else:
                return False

            result = self.fetch_one(query, (origen_id,))
            return result["count"] > 0 if result else False
        except Exception as e:
            logger.warning(
                f"No se pudo verificar origen {origen_tipo} con ID {origen_id}: {e}"
            )
            return False

    # ============ MÉTODOS CRUD PRINCIPALES ============

    def create(self, data: Dict[str, Any], calcular_hash: bool = True) -> Optional[int]:
        """
        Crea un nuevo registro de auditoría

        Args:
            data: Diccionario con datos de auditoría
            calcular_hash: Si es True, calcula hash de integridad para datos anteriores/nuevos

        Returns:
            Optional[int]: ID del registro de auditoría creado o None si hay error
        """
        # Preparar datos
        insert_data = data.copy()

        # Validar datos
        is_valid, error_msg = self._validate_auditoria_data(
            insert_data, for_update=False
        )

        if not is_valid:
            logger.error(f"Error validando datos de auditoría: {error_msg}")
            return None

        try:
            # Iniciar transacción
            self.begin_transaction()

            # Establecer valores por defecto
            defaults = {"fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

            for key, value in defaults.items():
                if key not in insert_data or insert_data[key] is None:
                    insert_data[key] = value

            # Procesar datos_anteriores y datos_nuevos
            for campo in ["datos_anteriores", "datos_nuevos"]:
                if campo in insert_data and insert_data[campo] is not None:
                    # Convertir a JSON string si es dict/list
                    if isinstance(insert_data[campo], (dict, list)):
                        insert_data[campo] = json.dumps(
                            insert_data[campo], ensure_ascii=False, default=str
                        )

            # Calcular hash de integridad si se solicita
            if calcular_hash:
                self._agregar_hash_integridad(insert_data)

            # Insertar en base de datos
            auditoria_id = self.insert(self.table_name, insert_data, returning="id")

            if not auditoria_id:
                self.rollback()
                logger.error("No se pudo insertar el registro de auditoría")
                return None

            logger.info(
                f"✓ Registro de auditoría creado exitosamente con ID: {auditoria_id}"
            )

            # Commit de la transacción
            self.commit()

            # Log de auditoría (meta-auditoría)
            self._log_auditoria_creada(auditoria_id, insert_data)

            return auditoria_id

        except Exception as e:
            self.rollback()
            logger.error(f"Error creando registro de auditoría: {e}", exc_info=True)
            return None

    def _agregar_hash_integridad(self, data: Dict[str, Any]) -> None:
        """
        Agrega hash de integridad a los datos de auditoría

        Args:
            data: Datos de auditoría
        """
        try:
            # Crear cadena para hash
            cadena_hash = ""

            if data.get("datos_anteriores"):
                cadena_hash += str(data["datos_anteriores"])

            if data.get("datos_nuevos"):
                cadena_hash += str(data["datos_nuevos"])

            if cadena_hash:
                # Calcular hash SHA-256
                hash_obj = hashlib.sha256(cadena_hash.encode("utf-8"))
                data_hash = hash_obj.hexdigest()

                # Agregar al motivo
                motivo_original = data.get("motivo", "")
                data["motivo"] = f"{motivo_original} [HASH:{data_hash[:16]}]"

                logger.debug(f"Hash de integridad calculado: {data_hash[:16]}")

        except Exception as e:
            logger.warning(f"No se pudo calcular hash de integridad: {e}")

    def _log_auditoria_creada(self, auditoria_id: int, data: Dict[str, Any]) -> None:
        """
        Registra log adicional cuando se crea una auditoría

        Args:
            auditoria_id: ID del registro de auditoría
            data: Datos del registro
        """
        try:
            origen_info = f"{data.get('origen_tipo', '')}-{data.get('origen_id', '')}"
            accion = data.get("accion", "")
            usuario = data.get("usuario_id", "")

            logger.info(
                f"AUDITORIA_CREADA - ID: {auditoria_id} - "
                f"Origen: {origen_info} - Acción: {accion} - "
                f"Usuario: {usuario} - Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        except Exception:
            pass

    def read(self, auditoria_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un registro de auditoría por su ID

        Args:
            auditoria_id: ID del registro de auditoría

        Returns:
            Optional[Dict]: Datos del registro de auditoría o None si no existe
        """
        try:
            query = f"""
                SELECT a.*,
                       u.username as usuario_username,
                       u.nombre_completo as usuario_nombre,
                       u.email as usuario_email
                FROM {self.table_name} a
                LEFT JOIN usuarios u ON a.usuario_id = u.id
                WHERE a.id = %s
            """
            result = self.fetch_one(query, (auditoria_id,))

            if result:
                # Procesar datos JSON
                result = self._procesar_resultado_auditoria(result)

            return result

        except Exception as e:
            logger.error(f"Error obteniendo registro de auditoría: {e}")
            return None

    def _procesar_resultado_auditoria(
        self, resultado: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Procesa y formatea los resultados de auditoría

        Args:
            resultado: Resultado de la consulta

        Returns:
            Dict[str, Any]: Resultado procesado
        """
        try:
            procesado = resultado.copy()

            # Formatear fecha/hora
            if "fecha_hora" in procesado and procesado["fecha_hora"]:
                try:
                    fecha_obj = (
                        datetime.strptime(procesado["fecha_hora"], "%Y-%m-%d %H:%M:%S")
                        if isinstance(procesado["fecha_hora"], str)
                        else procesado["fecha_hora"]
                    )
                    if isinstance(fecha_obj, datetime):
                        procesado["fecha_hora_formateada"] = fecha_obj.strftime(
                            "%d/%m/%Y %H:%M:%S"
                        )
                        procesado["fecha_formateada"] = fecha_obj.strftime("%d/%m/%Y")
                        procesado["hora_formateada"] = fecha_obj.strftime("%H:%M:%S")
                except:
                    pass

            # Parsear datos JSON si existen
            for campo in ["datos_anteriores", "datos_nuevos"]:
                if campo in procesado and procesado[campo]:
                    try:
                        if isinstance(procesado[campo], str):
                            procesado[f"{campo}_parsed"] = json.loads(procesado[campo])
                        else:
                            procesado[f"{campo}_parsed"] = procesado[campo]
                    except json.JSONDecodeError:
                        procesado[f"{campo}_parsed"] = {"raw": procesado[campo]}

            # Agregar descripciones
            if "accion" in procesado:
                descripciones = {
                    "CREACION": "Creación",
                    "MODIFICACION": "Modificación",
                    "ELIMINACION": "Eliminación",
                    "ANULACION": "Anulación",
                }
                procesado["accion_descripcion"] = descripciones.get(
                    procesado["accion"], procesado["accion"]
                )

            if "origen_tipo" in procesado:
                descripciones = {"INGRESO": "Ingreso", "GASTO": "Gasto"}
                procesado["origen_tipo_descripcion"] = descripciones.get(
                    procesado["origen_tipo"], procesado["origen_tipo"]
                )

            # Agregar nivel de severidad
            if "accion" in procesado:
                procesado["nivel_severidad"] = self.NIVELES_SEVERIDAD.get(
                    procesado["accion"], "INFO"
                )

            return procesado

        except Exception as e:
            logger.warning(f"Error procesando resultado de auditoría: {e}")
            return resultado

    def update(self, auditoria_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un registro de auditoría (uso limitado para correcciones)

        Nota: Los registros de auditoría generalmente no deben actualizarse
        excepto para correcciones administrativas.

        Args:
            auditoria_id: ID del registro a actualizar
            data: Datos a actualizar

        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            logger.warning(
                f"Actualizando registro de auditoría {auditoria_id} - "
                "Esta operación debe estar justificada"
            )

            # Obtener registro actual
            registro_actual = self.read(auditoria_id)
            if not registro_actual:
                return False

            # Solo permitir actualizar ciertos campos
            campos_permitidos = ["motivo", "responsable_autoriza", "ruta_resolucion"]
            data_filtrado = {k: v for k, v in data.items() if k in campos_permitidos}

            if not data_filtrado:
                logger.error("No se permiten actualizar los campos solicitados")
                return False

            # Agregar timestamp de actualización
            data_filtrado["fecha_hora"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Actualizar en base de datos usando el método de BaseModel
            result = super().update(  # ¡CUIDADO! Esto causaría recursión infinita
                self.table_name, data_filtrado, "id = %s", (auditoria_id,)
            )

            if result:
                logger.warning(
                    f"✓ Registro de auditoría {auditoria_id} actualizado "
                    f"(campos: {', '.join(data_filtrado.keys())})"
                )
                return True

            return False

        except Exception as e:
            logger.error(f"Error actualizando registro de auditoría: {e}")
            return False

    def delete(self, auditoria_id: int) -> bool:
        """
        Elimina un registro de auditoría (uso excepcional)

        Nota: Los registros de auditoría generalmente NO deben eliminarse.
        Solo para casos excepcionales y con autorización documentada.

        Args:
            auditoria_id: ID del registro a eliminar

        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            logger.critical(
                f"ELIMINANDO registro de auditoría {auditoria_id} - "
                "Operación CRÍTICA que requiere autorización"
            )

            # Registrar intento de eliminación antes de proceder
            self._log_intento_eliminacion(auditoria_id)

            # Solo permitir eliminar registros muy antiguos
            registro = self.read(auditoria_id)
            if registro and "fecha_hora" in registro:
                try:
                    fecha_registro = (
                        datetime.strptime(registro["fecha_hora"], "%Y-%m-%d %H:%M:%S")
                        if isinstance(registro["fecha_hora"], str)
                        else registro["fecha_hora"]
                    )

                    # No permitir eliminar registros de menos de 30 días
                    if (datetime.now() - fecha_registro).days < 30:
                        logger.error(
                            "No se pueden eliminar registros de auditoría de menos de 30 días"
                        )
                        return False
                except:
                    pass

            # Eliminar registro
            query = f"DELETE FROM {self.table_name} WHERE id = %s"
            result = self.execute_query(query, (auditoria_id,), commit=True)

            if result:
                logger.critical(
                    f"✗ Registro de auditoría {auditoria_id} ELIMINADO permanentemente"
                )
                return True

            return False

        except Exception as e:
            logger.error(f"Error eliminando registro de auditoría: {e}")
            return False

    def _log_intento_eliminacion(self, auditoria_id: int) -> None:
        """
        Registra intento de eliminación de auditoría

        Args:
            auditoria_id: ID del registro que se intenta eliminar
        """
        try:
            # Registrar en log del sistema
            logger.critical(
                f"INTENTO_ELIMINACION_AUDITORIA - ID: {auditoria_id} - "
                f"Usuario del sistema - "
                f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - "
                f"IP: {self._obtener_ip_sistema()}"
            )
        except Exception:
            pass

    def _obtener_ip_sistema(self) -> str:
        """Obtiene IP del sistema (simplificado)"""
        try:
            import socket

            return socket.gethostbyname(socket.gethostname())
        except:
            return "DESCONOCIDA"

    # ============ MÉTODOS DE CONSULTA ESPECIALIZADOS ============

    def buscar_por_rango_fechas(
        self,
        fecha_inicio: Union[str, datetime, date],
        fecha_fin: Union[str, datetime, date],
        origen_tipo: Optional[str] = None,
        accion: Optional[str] = None,
        usuario_id: Optional[int] = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Busca registros de auditoría por rango de fechas

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            origen_tipo: Tipo de origen (opcional)
            accion: Acción específica (opcional)
            usuario_id: ID de usuario (opcional)
            limit: Límite de resultados
            offset: Desplazamiento para paginación

        Returns:
            List[Dict]: Lista de registros de auditoría
        """
        try:
            # Convertir fechas a string
            fecha_inicio_str = self._formatear_fecha_consulta(fecha_inicio)
            fecha_fin_str = self._formatear_fecha_consulta(fecha_fin, es_fin=True)

            condiciones = ["fecha_hora >= %s", "fecha_hora <= %s"]
            params = [fecha_inicio_str, fecha_fin_str]

            if origen_tipo:
                condiciones.append("origen_tipo = %s")
                params.append(origen_tipo)

            if accion:
                condiciones.append("accion = %s")
                params.append(accion)

            if usuario_id:
                condiciones.append("usuario_id = %s")
                params.append(str(usuario_id))  # Convertir int a str

            where_clause = "WHERE " + " AND ".join(condiciones)

            query = f"""
                    SELECT a.*,
                           u.username as usuario_username,
                           u.nombre_completo as usuario_nombre
                    FROM {self.table_name} a
                    LEFT JOIN usuarios u ON a.usuario_id = u.id
                    {where_clause}
                    ORDER BY a.fecha_hora DESC, a.id DESC
                    LIMIT %s OFFSET %s
                """

            # Agregar limit y offset como strings
            params.extend([str(limit), str(offset)])

            results = self.fetch_all(query, tuple(params))

            # Procesar resultados
            return (
                [self._procesar_resultado_auditoria(row) for row in results]
                if results
                else []
            )

        except Exception as e:
            logger.error(f"Error buscando auditorías por rango de fechas: {e}")
            return []

    def buscar_por_origen(
        self, origen_tipo: str, origen_id: int, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Busca todos los registros de auditoría para un origen específico

        Args:
            origen_tipo: Tipo de origen (INGRESO/GASTO)
            origen_id: ID del origen
            limit: Límite de resultados

        Returns:
            List[Dict]: Lista de registros de auditoría para el origen
        """
        try:
            if origen_tipo not in self.ORIGEN_TIPOS:
                return []

            query = f"""
                SELECT a.*,
                       u.username as usuario_username,
                       u.nombre_completo as usuario_nombre
                FROM {self.table_name} a
                LEFT JOIN usuarios u ON a.usuario_id = u.id
                WHERE a.origen_tipo = %s AND a.origen_id = %s
                ORDER BY a.fecha_hora DESC
                LIMIT %s
            """

            results = self.fetch_all(query, (origen_tipo, origen_id, limit))

            # Procesar resultados
            return (
                [self._procesar_resultado_auditoria(row) for row in results]
                if results
                else []
            )

        except Exception as e:
            logger.error(f"Error buscando auditorías por origen: {e}")
            return []

    def buscar_por_usuario(
        self, usuario_id: int, dias_atras: int = 30, limit: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Busca registros de auditoría para un usuario específico

        Args:
            usuario_id: ID del usuario
            dias_atras: Días hacia atrás para buscar
            limit: Límite de resultados

        Returns:
            List[Dict]: Lista de registros de auditoría del usuario
        """
        try:
            fecha_limite = (datetime.now() - timedelta(days=dias_atras)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            query = f"""
                SELECT a.*,
                       u.username as usuario_username,
                       u.nombre_completo as usuario_nombre
                FROM {self.table_name} a
                LEFT JOIN usuarios u ON a.usuario_id = u.id
                WHERE a.usuario_id = %s AND a.fecha_hora >= %s
                ORDER BY a.fecha_hora DESC
                LIMIT %s
            """

            results = self.fetch_all(query, (usuario_id, fecha_limite, limit))

            # Procesar resultados
            return (
                [self._procesar_resultado_auditoria(row) for row in results]
                if results
                else []
            )

        except Exception as e:
            logger.error(f"Error buscando auditorías por usuario: {e}")
            return []

    def buscar_acciones_criticas(
        self, dias_atras: int = 7, acciones: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca acciones críticas para revisión de seguridad

        Args:
            dias_atras: Días hacia atrás para buscar
            acciones: Lista de acciones a considerar críticas

        Returns:
            List[Dict]: Lista de acciones críticas
        """
        try:
            if acciones is None:
                acciones = ["ELIMINACION", "ANULACION"]

            fecha_limite = (datetime.now() - timedelta(days=dias_atras)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            condiciones = ["fecha_hora >= %s", "accion IN %s"]
            params = [fecha_limite, tuple(acciones)]

            where_clause = "WHERE " + " AND ".join(condiciones)

            query = f"""
                SELECT a.*,
                       u.username as usuario_username,
                       u.nombre_completo as usuario_nombre,
                       u.email as usuario_email
                FROM {self.table_name} a
                LEFT JOIN usuarios u ON a.usuario_id = u.id
                {where_clause}
                ORDER BY a.fecha_hora DESC
                LIMIT %s
            """

            params.append(100)  # Límite adicional para acciones críticas
            results = self.fetch_all(query, tuple(params))

            # Procesar resultados
            return (
                [self._procesar_resultado_auditoria(row) for row in results]
                if results
                else []
            )

        except Exception as e:
            logger.error(f"Error buscando acciones críticas: {e}")
            return []

    def _formatear_fecha_consulta(
        self, fecha: Union[str, datetime, date], es_fin: bool = False
    ) -> str:
        """
        Formatea fecha para consulta SQL

        Args:
            fecha: Fecha a formatear
            es_fin: Si es True, es fecha fin (se agrega tiempo 23:59:59)

        Returns:
            str: Fecha formateada para SQL
        """
        try:
            if isinstance(fecha, str):
                # Intentar parsear
                for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y"]:
                    try:
                        fecha_dt = datetime.strptime(fecha, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    fecha_dt = datetime.now()
            elif isinstance(fecha, datetime):
                fecha_dt = fecha
            elif isinstance(fecha, date):
                fecha_dt = datetime.combine(fecha, datetime.min.time())
            else:
                fecha_dt = datetime.now()

            if es_fin:
                fecha_dt = fecha_dt.replace(hour=23, minute=59, second=59)

            return fecha_dt.strftime("%Y-%m-%d %H:%M:%S")

        except Exception:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ============ MÉTODOS DE REPORTES Y ESTADÍSTICAS ============

    def obtener_estadisticas(
        self,
        fecha_inicio: Union[str, datetime, date],
        fecha_fin: Union[str, datetime, date],
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de auditoría para un período

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin

        Returns:
            Dict[str, Any]: Estadísticas de auditoría
        """
        try:
            fecha_inicio_str = self._formatear_fecha_consulta(fecha_inicio)
            fecha_fin_str = self._formatear_fecha_consulta(fecha_fin, es_fin=True)

            # Estadísticas generales
            query_general = f"""
                SELECT 
                    COUNT(*) as total_registros,
                    COUNT(DISTINCT usuario_id) as usuarios_unicos,
                    COUNT(DISTINCT origen_tipo) as tipos_origen,
                    MIN(fecha_hora) as primera_fecha,
                    MAX(fecha_hora) as ultima_fecha
                FROM {self.table_name}
                WHERE fecha_hora >= %s AND fecha_hora <= %s
            """

            general = self.fetch_one(query_general, (fecha_inicio_str, fecha_fin_str))

            # Por acción
            query_acciones = f"""
                SELECT 
                    accion,
                    COUNT(*) as cantidad
                FROM {self.table_name}
                WHERE fecha_hora >= %s AND fecha_hora <= %s
                GROUP BY accion
                ORDER BY cantidad DESC
            """

            por_accion = self.fetch_all(
                query_acciones, (fecha_inicio_str, fecha_fin_str)
            )

            # Por origen
            query_origenes = f"""
                SELECT 
                    origen_tipo,
                    COUNT(*) as cantidad
                FROM {self.table_name}
                WHERE fecha_hora >= %s AND fecha_hora <= %s
                GROUP BY origen_tipo
                ORDER BY cantidad DESC
            """

            por_origen = self.fetch_all(
                query_origenes, (fecha_inicio_str, fecha_fin_str)
            )

            # Por usuario
            query_usuarios = f"""
                SELECT 
                    a.usuario_id,
                    u.username,
                    u.nombre_completo,
                    COUNT(*) as cantidad
                FROM {self.table_name} a
                LEFT JOIN usuarios u ON a.usuario_id = u.id
                WHERE a.fecha_hora >= %s AND a.fecha_hora <= %s
                GROUP BY a.usuario_id, u.username, u.nombre_completo
                ORDER BY cantidad DESC
                LIMIT 10
            """

            por_usuario = self.fetch_all(
                query_usuarios, (fecha_inicio_str, fecha_fin_str)
            )

            # Actividad por día
            query_diaria = f"""
                SELECT 
                    DATE(fecha_hora) as fecha,
                    COUNT(*) as registros
                FROM {self.table_name}
                WHERE fecha_hora >= %s AND fecha_hora <= %s
                GROUP BY DATE(fecha_hora)
                ORDER BY fecha DESC
                LIMIT 30
            """

            diaria = self.fetch_all(query_diaria, (fecha_inicio_str, fecha_fin_str))

            return {
                "periodo": {
                    "fecha_inicio": fecha_inicio_str,
                    "fecha_fin": fecha_fin_str,
                },
                "general": general if general else {},
                "por_accion": por_accion if por_accion else [],
                "por_origen": por_origen if por_origen else [],
                "top_usuarios": por_usuario if por_usuario else [],
                "actividad_diaria": diaria if diaria else [],
                "generado_en": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de auditoría: {e}")
            return {}

    def generar_reporte_auditoria(
        self,
        fecha_inicio: Union[str, datetime, date],
        fecha_fin: Union[str, datetime, date],
        formato: str = "detallado",
    ) -> Dict[str, Any]:
        """
        Genera un reporte completo de auditoría

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            formato: Formato del reporte (detallado, resumen, csv)

        Returns:
            Dict[str, Any]: Reporte de auditoría
        """
        try:
            fecha_inicio_str = self._formatear_fecha_consulta(fecha_inicio)
            fecha_fin_str = self._formatear_fecha_consulta(fecha_fin, es_fin=True)

            # Obtener estadísticas
            estadisticas = self.obtener_estadisticas(fecha_inicio, fecha_fin)

            # Obtener registros detallados si se solicita
            registros_detallados = []
            if formato == "detallado":
                registros_detallados = self.buscar_por_rango_fechas(
                    fecha_inicio, fecha_fin, limit=1000
                )

            # Calcular tendencias
            tendencias = self._calcular_tendencias(fecha_inicio, fecha_fin)

            # Identificar anomalías
            anomalias = self._identificar_anomalias(fecha_inicio, fecha_fin)

            return {
                "metadatos": {
                    "titulo": "Reporte de Auditoría del Sistema",
                    "periodo": f"{fecha_inicio_str} a {fecha_fin_str}",
                    "formato": formato,
                    "generado_en": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "sistema": "FormaGestPro MVC",
                },
                "estadisticas": estadisticas,
                "tendencias": tendencias,
                "alertas_anomalias": anomalias,
                "registros_detallados": (
                    registros_detallados if formato == "detallado" else []
                ),
                "resumen_ejecutivo": self._generar_resumen_ejecutivo(
                    estadisticas, anomalias
                ),
            }

        except Exception as e:
            logger.error(f"Error generando reporte de auditoría: {e}")
            return {"error": str(e)}

    def _calcular_tendencias(
        self,
        fecha_inicio: Union[str, datetime, date],
        fecha_fin: Union[str, datetime, date],
    ) -> Dict[str, Any]:
        """
        Calcula tendencias de actividad de auditoría

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin

        Returns:
            Dict[str, Any]: Tendencias identificadas
        """
        try:
            # Implementación simplificada
            # En una implementación real, usarías análisis más sofisticado

            fecha_inicio_dt = (
                datetime.strptime(fecha_inicio, "%Y-%m-%d")
                if isinstance(fecha_inicio, str)
                else fecha_inicio
            )
            fecha_fin_dt = (
                datetime.strptime(fecha_fin, "%Y-%m-%d")
                if isinstance(fecha_fin, str)
                else fecha_fin
            )

            # dias_periodo = (fecha_fin_dt - fecha_inicio_dt).days + 1
            if isinstance(fecha_inicio_dt, date) and not isinstance(
                fecha_inicio_dt, datetime
            ):
                fecha_inicio_dt = datetime.combine(fecha_inicio_dt, datetime.min.time())
            if isinstance(fecha_fin_dt, date) and not isinstance(
                fecha_fin_dt, datetime
            ):
                fecha_fin_dt = datetime.combine(fecha_fin_dt, datetime.min.time())

            dias_periodo = (fecha_fin_dt - fecha_inicio_dt).days + 1

            # Consulta para actividad diaria
            query = f"""
                SELECT 
                    DATE(fecha_hora) as fecha,
                    COUNT(*) as registros,
                    SUM(CASE WHEN accion IN ('ELIMINACION', 'ANULACION') THEN 1 ELSE 0 END) as criticas
                FROM {self.table_name}
                WHERE fecha_hora >= %s AND fecha_hora <= %s
                GROUP BY DATE(fecha_hora)
                ORDER BY fecha
            """

            fecha_inicio_str = self._formatear_fecha_consulta(fecha_inicio)
            fecha_fin_str = self._formatear_fecha_consulta(fecha_fin, es_fin=True)

            resultados = self.fetch_all(query, (fecha_inicio_str, fecha_fin_str))

            if not resultados:
                return {}

            # Calcular promedios y tendencias
            total_registros = sum(r["registros"] for r in resultados)
            total_criticas = sum(r["criticas"] for r in resultados)

            promedio_diario = total_registros / dias_periodo if dias_periodo > 0 else 0
            porcentaje_criticas = (
                (total_criticas / total_registros * 100) if total_registros > 0 else 0
            )

            return {
                "total_dias": dias_periodo,
                "promedio_diario": round(promedio_diario, 2),
                "porcentaje_acciones_criticas": round(porcentaje_criticas, 2),
                "pico_actividad": (
                    max(r["registros"] for r in resultados) if resultados else 0
                ),
                "actividad_consistente": (
                    all(
                        abs(r["registros"] - promedio_diario) < (promedio_diario * 0.5)
                        for r in resultados
                    )
                    if resultados and promedio_diario > 0
                    else True
                ),
            }

        except Exception as e:
            logger.warning(f"Error calculando tendencias: {e}")
            return {}

    def _identificar_anomalias(
        self,
        fecha_inicio: Union[str, datetime, date],
        fecha_fin: Union[str, datetime, date],
    ) -> List[Dict[str, Any]]:
        """
        Identifica anomalías en los registros de auditoría

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin

        Returns:
            List[Dict[str, Any]]: Lista de anomalías identificadas
        """
        anomalias = []

        try:
            fecha_inicio_str = self._formatear_fecha_consulta(fecha_inicio)
            fecha_fin_str = self._formatear_fecha_consulta(fecha_fin, es_fin=True)

            # 1. Múltiples eliminaciones por mismo usuario en poco tiempo
            query_eliminaciones = f"""
                SELECT 
                    usuario_id,
                    COUNT(*) as cantidad,
                    MIN(fecha_hora) as primera,
                    MAX(fecha_hora) as ultima
                FROM {self.table_name}
                WHERE fecha_hora >= %s AND fecha_hora <= %s
                  AND accion = 'ELIMINACION'
                GROUP BY usuario_id
                HAVING COUNT(*) > 3
            """

            elims = self.fetch_all(
                query_eliminaciones, (fecha_inicio_str, fecha_fin_str)
            )

            for elim in elims or []:
                anomalias.append(
                    {
                        "tipo": "ELIMINACIONES_MULTIPLES",
                        "severidad": "ALTA",
                        "descripcion": f"Usuario {elim['usuario_id']} realizó {elim['cantidad']} eliminaciones",
                        "detalles": elim,
                    }
                )

            # 2. Actividad fuera de horario laboral (simplificado)
            query_nocturna = f"""
                SELECT 
                    usuario_id,
                    COUNT(*) as cantidad
                FROM {self.table_name}
                WHERE fecha_hora >= %s AND fecha_hora <= %s
                  AND EXTRACT(HOUR FROM fecha_hora) BETWEEN 22 AND 6
                GROUP BY usuario_id
                HAVING COUNT(*) > 1
            """

            nocturna = self.fetch_all(query_nocturna, (fecha_inicio_str, fecha_fin_str))

            for noct in nocturna or []:
                anomalias.append(
                    {
                        "tipo": "ACTIVIDAD_NOCTURNA",
                        "severidad": "MEDIA",
                        "descripcion": f"Usuario {noct['usuario_id']} con {noct['cantidad']} acciones nocturnas",
                        "detalles": noct,
                    }
                )

            # 3. Múltiples modificaciones al mismo registro
            query_modificaciones = f"""
                SELECT 
                    origen_tipo,
                    origen_id,
                    COUNT(*) as modificaciones
                FROM {self.table_name}
                WHERE fecha_hora >= %s AND fecha_hora <= %s
                  AND accion = 'MODIFICACION'
                GROUP BY origen_tipo, origen_id
                HAVING COUNT(*) > 5
            """

            mods = self.fetch_all(
                query_modificaciones, (fecha_inicio_str, fecha_fin_str)
            )

            for mod in mods or []:
                anomalias.append(
                    {
                        "tipo": "MODIFICACIONES_EXCESIVAS",
                        "severidad": "MEDIA",
                        "descripcion": f"{mod['origen_tipo']} {mod['origen_id']} modificado {mod['modificaciones']} veces",
                        "detalles": mod,
                    }
                )

            return anomalias

        except Exception as e:
            logger.warning(f"Error identificando anomalías: {e}")
            return []

    def _generar_resumen_ejecutivo(
        self, estadisticas: Dict[str, Any], anomalias: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Genera un resumen ejecutivo del reporte

        Args:
            estadisticas: Estadísticas del período
            anomalias: Lista de anomalías identificadas

        Returns:
            Dict[str, Any]: Resumen ejecutivo
        """
        try:
            general = estadisticas.get("general", {})

            total_registros = general.get("total_registros", 0)
            usuarios_unicos = general.get("usuarios_unicos", 0)

            # Calcular calificación de seguridad
            num_anomalias = len(anomalias)
            anomalias_criticas = sum(
                1 for a in anomalias if a.get("severidad") == "ALTA"
            )

            if num_anomalias == 0:
                calificacion = "EXCELENTE"
            elif anomalias_criticas == 0:
                calificacion = "BUENA"
            elif anomalias_criticas <= 2:
                calificacion = "REGULAR"
            else:
                calificacion = "CRITICA"

            # Recomendaciones basadas en análisis
            recomendaciones = []

            if anomalias_criticas > 0:
                recomendaciones.append(
                    "Revisar inmediatamente las anomalías críticas identificadas"
                )

            if total_registros == 0:
                recomendaciones.append("No se registró actividad en el período")
            elif usuarios_unicos == 1 and total_registros > 10:
                recomendaciones.append("Considerar rotación de responsabilidades")

            return {
                "calificacion_seguridad": calificacion,
                "resumen_numerico": {
                    "total_auditorias": total_registros,
                    "usuarios_activos": usuarios_unicos,
                    "anomalias_detectadas": num_anomalias,
                    "anomalias_criticas": anomalias_criticas,
                },
                "recomendaciones": recomendaciones,
                "observaciones_clave": self._generar_observaciones_clave(
                    estadisticas, anomalias
                ),
            }

        except Exception as e:
            logger.warning(f"Error generando resumen ejecutivo: {e}")
            return {}

    def _generar_observaciones_clave(
        self, estadisticas: Dict[str, Any], anomalias: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Genera observaciones clave del análisis

        Args:
            estadisticas: Estadísticas del período
            anomalias: Lista de anomalías

        Returns:
            List[str]: Observaciones clave
        """
        observaciones = []

        try:
            # Análisis de acciones
            por_accion = estadisticas.get("por_accion", [])

            for accion in por_accion:
                if accion["accion"] == "ELIMINACION" and accion["cantidad"] > 10:
                    observaciones.append(
                        f"Alto número de eliminaciones: {accion['cantidad']}"
                    )
                elif accion["accion"] == "ANULACION" and accion["cantidad"] > 5:
                    observaciones.append(
                        f"Alto número de anulaciones: {accion['cantidad']}"
                    )

            # Análisis de anomalías
            if anomalias:
                observaciones.append(
                    f"Se detectaron {len(anomalias)} anomalías que requieren revisión"
                )

            # Actividad de usuarios
            top_usuarios = estadisticas.get("top_usuarios", [])
            if top_usuarios:
                usuario_mas_activo = top_usuarios[0]
                observaciones.append(
                    f"Usuario más activo: {usuario_mas_activo.get('username', usuario_mas_activo['usuario_id'])} "
                    f"con {usuario_mas_activo['cantidad']} acciones"
                )

            return observaciones

        except Exception:
            return []

    # ============ MÉTODOS DE MANTENIMIENTO ============

    def limpiar_registros_antiguos(
        self, dias_retener: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Limpia registros de auditoría más antiguos que el período de retención

        Args:
            dias_retener: Días a retener (si None, usa RETENCION_DIAS)

        Returns:
            Dict[str, Any]: Resultado de la limpieza
        """
        try:
            if dias_retener is None:
                dias_retener = self.RETENCION_DIAS

            fecha_limite = (datetime.now() - timedelta(days=dias_retener)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            # Contar registros a eliminar
            query_count = f"""
                SELECT COUNT(*) as total 
                FROM {self.table_name} 
                WHERE fecha_hora < %s
            """

            count_result = self.fetch_one(query_count, (fecha_limite,))
            total_a_eliminar = count_result["total"] if count_result else 0

            if total_a_eliminar == 0:
                return {
                    "eliminados": 0,
                    "fecha_limite": fecha_limite,
                    "mensaje": "No hay registros antiguos para eliminar",
                }

            logger.warning(
                f"Iniciando limpieza de {total_a_eliminar} registros de auditoría "
                f"anteriores a {fecha_limite}"
            )

            # Crear backup de registros antiguos (en una implementación real)
            backup_exitoso = self._crear_backup_antes_limpieza(fecha_limite)

            # Eliminar registros
            query_delete = f"DELETE FROM {self.table_name} WHERE fecha_hora < %s"
            eliminados = self.execute_query(query_delete, (fecha_limite,), commit=True)

            if eliminados:
                logger.warning(
                    f"✓ Limpieza completada: {eliminados} registros eliminados"
                )

                return {
                    "eliminados": eliminados,
                    "fecha_limite": fecha_limite,
                    "backup_creado": backup_exitoso,
                    "mensaje": f"Se eliminaron {eliminados} registros anteriores a {fecha_limite}",
                }
            else:
                return {
                    "eliminados": 0,
                    "fecha_limite": fecha_limite,
                    "mensaje": "No se pudieron eliminar los registros",
                }

        except Exception as e:
            logger.error(f"Error en limpieza de registros antiguos: {e}")
            return {
                "eliminados": 0,
                "error": str(e),
                "mensaje": "Error durante la limpieza",
            }

    def _crear_backup_antes_limpieza(self, fecha_limite: str) -> bool:
        """
        Crea backup de registros antes de limpiar (implementación de ejemplo)

        Args:
            fecha_limite: Fecha límite para los registros a respaldar

        Returns:
            bool: True si el backup fue exitoso
        """
        try:
            # En una implementación real, exportarías a archivo o tabla de backup
            logger.info(f"Backup simulado para registros anteriores a {fecha_limite}")

            # Ejemplo: Exportar a archivo JSON
            query_backup = f"""
                SELECT * FROM {self.table_name} 
                WHERE fecha_hora < %s 
                ORDER BY fecha_hora
            """

            registros = self.fetch_all(query_backup, (fecha_limite,))

            if registros:
                # Crear nombre de archivo con timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_archivo = f"backup_auditoria_{timestamp}.json"

                # Exportar a JSON (simulado)
                datos_backup = {
                    "fecha_backup": datetime.now().isoformat(),
                    "fecha_limite": fecha_limite,
                    "total_registros": len(registros),
                    "registros": registros,
                }

                # En una implementación real, guardarías el archivo
                logger.info(
                    f"Backup simulado: {len(registros)} registros en {nombre_archivo}"
                )

                return True
            else:
                logger.info("No hay registros para respaldar")
                return True

        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            return False

    def verificar_integridad(self) -> Dict[str, Any]:
        """
        Verifica la integridad de los registros de auditoría

        Returns:
            Dict[str, Any]: Resultado de la verificación de integridad
        """
        try:
            verificaciones = []

            # 1. Verificar usuarios existentes
            query_usuarios_invalidos = f"""
                SELECT COUNT(*) as cantidad
                FROM {self.table_name} a
                LEFT JOIN usuarios u ON a.usuario_id = u.id
                WHERE u.id IS NULL
            """

            usuarios_inv = self.fetch_one(query_usuarios_invalidos)
            usuarios_invalidos = usuarios_inv["cantidad"] if usuarios_inv else 0

            verificaciones.append(
                {
                    "nombre": "Usuarios válidos",
                    "estado": "OK" if usuarios_invalidos == 0 else "ERROR",
                    "detalles": f"{usuarios_invalidos} referencias a usuarios no existentes",
                }
            )

            # 2. Verificar duplicados por índice único
            query_duplicados = f"""
                SELECT COUNT(*) - COUNT(DISTINCT fecha_hora, accion) as duplicados
                FROM {self.table_name}
            """

            dup_result = self.fetch_one(query_duplicados)
            duplicados = dup_result["duplicados"] if dup_result else 0

            verificaciones.append(
                {
                    "nombre": "Índices únicos",
                    "estado": "OK" if duplicados == 0 else "ADVERTENCIA",
                    "detalles": f"{duplicados} posibles violaciones de unicidad",
                }
            )

            # 3. Verificar fechas válidas
            query_fechas_invalidas = f"""
                SELECT COUNT(*) as cantidad
                FROM {self.table_name}
                WHERE fecha_hora > CURRENT_TIMESTAMP + INTERVAL '1 day'
                   OR fecha_hora < '2000-01-01'
            """

            fechas_inv = self.fetch_one(query_fechas_invalidas)
            fechas_invalidas = fechas_inv["cantidad"] if fechas_inv else 0

            verificaciones.append(
                {
                    "nombre": "Fechas válidas",
                    "estado": "OK" if fechas_invalidas == 0 else "ERROR",
                    "detalles": f"{fechas_invalidas} fechas fuera de rango válido",
                }
            )

            # Resumen
            total_ok = sum(1 for v in verificaciones if v["estado"] == "OK")
            total_error = sum(1 for v in verificaciones if v["estado"] == "ERROR")

            return {
                "fecha_verificacion": datetime.now().isoformat(),
                "total_verificaciones": len(verificaciones),
                "verificaciones_ok": total_ok,
                "verificaciones_error": total_error,
                "verificaciones": verificaciones,
                "estado_general": "OK" if total_error == 0 else "REVISAR",
            }

        except Exception as e:
            logger.error(f"Error verificando integridad: {e}")
            return {"error": str(e), "estado_general": "ERROR"}

    # ============ MÉTODOS DE UTILIDAD PARA OTROS MÓDULOS ============

    @staticmethod
    def crear_registro_auditoria(
        usuario_id: int,
        origen_tipo: str,
        origen_id: int,
        accion: str,
        motivo: str,
        datos_anteriores: Optional[Any] = None,
        datos_nuevos: Optional[Any] = None,
        responsable_autoriza: Optional[str] = None,
        ruta_resolucion: Optional[str] = None,
    ) -> Optional[int]:
        """
        Método estático para crear registros de auditoría fácilmente

        Args:
            usuario_id: ID del usuario que realiza la acción
            origen_tipo: Tipo de origen (INGRESO/GASTO)
            origen_id: ID del origen
            accion: Acción realizada
            motivo: Motivo de la acción
            datos_anteriores: Datos anteriores (opcional)
            datos_nuevos: Datos nuevos (opcional)
            responsable_autoriza: Responsable que autoriza (opcional)
            ruta_resolucion: Ruta de resolución/documento (opcional)

        Returns:
            Optional[int]: ID del registro creado o None si hay error
        """
        try:
            auditoria_model = AuditoriaTransaccionesModel()

            datos = {
                "usuario_id": usuario_id,
                "origen_tipo": origen_tipo,
                "origen_id": origen_id,
                "accion": accion,
                "motivo": motivo,
            }

            if datos_anteriores is not None:
                datos["datos_anteriores"] = datos_anteriores

            if datos_nuevos is not None:
                datos["datos_nuevos"] = datos_nuevos

            if responsable_autoriza:
                datos["responsable_autoriza"] = responsable_autoriza

            if ruta_resolucion:
                datos["ruta_resolucion"] = ruta_resolucion

            return auditoria_model.create(datos)

        except Exception as e:
            logger.error(f"Error creando registro de auditoría estático: {e}")
            return None


# Ejemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)

    # Crear instancia del modelo
    auditoria_model = AuditoriaTransaccionesModel()

    print("=== Ejemplo de creación de registro de auditoría ===")

    # Datos de ejemplo
    registro_id = auditoria_model.crear_registro_auditoria(
        usuario_id=1,
        origen_tipo="INGRESO",
        origen_id=100,
        accion="MODIFICACION",
        motivo="Corrección de monto por error de digitación",
        datos_anteriores={"monto": 1000.00, "concepto": "Pago inicial"},
        datos_nuevos={"monto": 1500.00, "concepto": "Pago inicial corregido"},
        responsable_autoriza="Jefe de Finanzas",
        ruta_resolucion="/resoluciones/2024/res-001.pdf",
    )

    if registro_id:
        print(f"✓ Registro de auditoría creado con ID: {registro_id}")

        # Leer registro creado
        print("\n=== Leyendo registro creado ===")
        registro = auditoria_model.read(registro_id)
        if registro:
            print(f"Acción: {registro.get('accion_descripcion')}")
            print(
                f"Origen: {registro.get('origen_tipo_descripcion')} {registro.get('origen_id')}"
            )
            print(f"Usuario: {registro.get('usuario_nombre', 'N/A')}")
            print(f"Fecha: {registro.get('fecha_hora_formateada', 'N/A')}")

        # Generar reporte de hoy
        print("\n=== Generando reporte del día ===")
        hoy = datetime.now().date()
        reporte = auditoria_model.generar_reporte_auditoria(hoy, hoy, "resumen")
        print(
            f"Total auditorías hoy: {reporte.get('estadisticas', {}).get('general', {}).get('total_registros', 0)}"
        )

    print("\n=== Verificando integridad ===")
    integridad = auditoria_model.verificar_integridad()
    print(f"Estado general: {integridad.get('estado_general', 'N/A')}")

    print("\n=== Fin del ejemplo ===")
