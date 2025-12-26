# app/models/configuraciones_model.py
"""
Modelo para gestión de configuraciones del sistema (clave-valor).

Este modelo maneja las configuraciones del sistema usando un patrón clave-valor,
permitiendo almacenar, recuperar y actualizar configuraciones de manera eficiente.

Hereda de BaseModel para utilizar el sistema de conexiones y transacciones.
"""

import sys
import os
import json
import logging
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Optional, List, Dict, Any, Tuple, Union, Type, TypeVar
from enum import Enum

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_model import BaseModel

logger = logging.getLogger(__name__)
T = TypeVar("T")


class ConfiguracionesModel(BaseModel):
    """Modelo que representa una configuración del sistema (clave-valor)"""

    def __init__(self):
        """Inicializa el modelo de configuraciones"""
        super().__init__()
        self.table_name = "configuraciones"
        self.sequence_name = "seq_configuraciones_id"

        # Columnas de la tabla
        self.columns = [
            "id",
            "clave",
            "valor",
            "descripcion",
            "created_at",
            "updated_at",
        ]

        # Columnas requeridas
        self.required_columns = ["clave"]

        # Claves de configuración predefinidas del sistema
        self.CLAVES_PREDEFINIDAS = {
            # Configuración general del sistema
            "SISTEMA_NOMBRE": {
                "valor_default": "FormaGestPro",
                "descripcion": "Nombre del sistema",
                "tipo": "string",
            },
            "SISTEMA_VERSION": {
                "valor_default": "1.0.0",
                "descripcion": "Versión del sistema",
                "tipo": "string",
            },
            "SISTEMA_MODO": {
                "valor_default": "produccion",
                "descripcion": "Modo del sistema (desarrollo, pruebas, produccion)",
                "tipo": "string",
                "opciones": ["desarrollo", "pruebas", "produccion"],
            },
            # Configuración de empresa
            "EMPRESA_NOMBRE": {
                "valor_default": "Mi Empresa",
                "descripcion": "Nombre de la empresa",
                "tipo": "string",
            },
            "EMPRESA_NIT": {
                "valor_default": "",
                "descripcion": "NIT de la empresa",
                "tipo": "string",
            },
            "EMPRESA_DIRECCION": {
                "valor_default": "",
                "descripcion": "Dirección de la empresa",
                "tipo": "string",
            },
            "EMPRESA_TELEFONO": {
                "valor_default": "",
                "descripcion": "Teléfono de la empresa",
                "tipo": "string",
            },
            "EMPRESA_EMAIL": {
                "valor_default": "",
                "descripcion": "Email de la empresa",
                "tipo": "string",
            },
            "EMPRESA_LOGO_URL": {
                "valor_default": "",
                "descripcion": "URL del logo de la empresa",
                "tipo": "string",
            },
            # Configuración de facturación
            "FACTURACION_PREFIJO": {
                "valor_default": "FAC-",
                "descripcion": "Prefijo para números de factura",
                "tipo": "string",
            },
            "FACTURACION_LONGITUD_SECUENCIA": {
                "valor_default": "6",
                "descripcion": "Longitud de la secuencia numérica de facturas",
                "tipo": "integer",
            },
            "FACTURACION_TASA_IVA": {
                "valor_default": "0.13",
                "descripcion": "Tasa de IVA aplicable (ej: 0.13 para 13%)",
                "tipo": "decimal",
            },
            "FACTURACION_TASA_IT": {
                "valor_default": "0.03",
                "descripcion": "Tasa de IT aplicable (ej: 0.03 para 3%)",
                "tipo": "decimal",
            },
            "FACTURACION_LEYENDA": {
                "valor_default": "Ley N° 453: Tienes derecho a recibir información sobre las características de los servicios",
                "descripcion": "Leyenda legal para facturas",
                "tipo": "string",
            },
            # Configuración de usuarios y seguridad
            "SEGURIDAD_INTENTOS_LOGIN": {
                "valor_default": "3",
                "descripcion": "Número máximo de intentos de login fallidos",
                "tipo": "integer",
            },
            "SEGURIDAD_TIEMPO_BLOQUEO": {
                "valor_default": "30",
                "descripcion": "Tiempo de bloqueo en minutos después de intentos fallidos",
                "tipo": "integer",
            },
            "SEGURIDAD_LONGITUD_PASSWORD": {
                "valor_default": "8",
                "descripcion": "Longitud mínima de contraseñas",
                "tipo": "integer",
            },
            "SEGURIDAD_EXPIRACION_PASSWORD": {
                "valor_default": "90",
                "descripcion": "Días para expiración de contraseñas (0 para nunca)",
                "tipo": "integer",
            },
            # Configuración de backup y mantenimiento
            "BACKUP_AUTOMATICO": {
                "valor_default": "false",
                "descripcion": "Habilitar backup automático",
                "tipo": "boolean",
            },
            "BACKUP_FRECUENCIA": {
                "valor_default": "diario",
                "descripcion": "Frecuencia de backup (diario, semanal, mensual)",
                "tipo": "string",
                "opciones": ["diario", "semanal", "mensual"],
            },
            "BACKUP_RETENCION": {
                "valor_default": "30",
                "descripcion": "Días de retención de backups",
                "tipo": "integer",
            },
            # Configuración de email
            "EMAIL_SERVIDOR": {
                "valor_default": "smtp.gmail.com",
                "descripcion": "Servidor SMTP para envío de emails",
                "tipo": "string",
            },
            "EMAIL_PUERTO": {
                "valor_default": "587",
                "descripcion": "Puerto del servidor SMTP",
                "tipo": "integer",
            },
            "EMAIL_USUARIO": {
                "valor_default": "",
                "descripcion": "Usuario para autenticación SMTP",
                "tipo": "string",
            },
            "EMAIL_PASSWORD": {
                "valor_default": "",
                "descripcion": "Contraseña para autenticación SMTP",
                "tipo": "string",
                "seguro": True,  # Indica que es un valor sensible
            },
            "EMAIL_FROM": {
                "valor_default": "sistema@miempresa.com",
                "descripcion": "Email remitente por defecto",
                "tipo": "string",
            },
            # Configuración de impresión
            "IMPRESION_TICKET_ANCHO": {
                "valor_default": "80",
                "descripcion": "Ancho de ticket en caracteres",
                "tipo": "integer",
            },
            "IMPRESION_FACTURA_ANCHO": {
                "valor_default": "80",
                "descripcion": "Ancho de factura en caracteres",
                "tipo": "integer",
            },
            "IMPRESION_LOGO_EN_TICKET": {
                "valor_default": "true",
                "descripcion": "Incluir logo en tickets",
                "tipo": "boolean",
            },
            # Configuración de reportes
            "REPORTES_ITEMS_POR_PAGINA": {
                "valor_default": "50",
                "descripcion": "Número de ítems por página en reportes",
                "tipo": "integer",
            },
            "REPORTES_FORMATO_FECHA": {
                "valor_default": "DD/MM/YYYY",
                "descripcion": "Formato de fecha en reportes",
                "tipo": "string",
                "opciones": ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"],
            },
            "REPORTES_MONEDA_SIMBOLO": {
                "valor_default": "Bs.",
                "descripcion": "Símbolo de moneda para reportes",
                "tipo": "string",
            },
            # Configuración de integración SIAT
            "SIAT_HABILITADO": {
                "valor_default": "false",
                "descripcion": "Habilitar integración con SIAT",
                "tipo": "boolean",
            },
            "SIAT_URL": {
                "valor_default": "https://siat.impuestos.gob.bo",
                "descripcion": "URL del servicio SIAT",
                "tipo": "string",
            },
            "SIAT_TOKEN": {
                "valor_default": "",
                "descripcion": "Token de autenticación SIAT",
                "tipo": "string",
                "seguro": True,
            },
            # Configuración de sesión
            "SESION_TIEMPO_EXPIRACION": {
                "valor_default": "60",
                "descripcion": "Tiempo de expiración de sesión en minutos",
                "tipo": "integer",
            },
            "SESION_RENOVACION_AUTOMATICA": {
                "valor_default": "true",
                "descripcion": "Renovar sesión automáticamente con actividad",
                "tipo": "boolean",
            },
        }

        # Cache de configuraciones para mejorar rendimiento
        self._cache = {}
        self._cache_timestamp = None
        self._CACHE_TTL = 300  # 5 minutos en segundos

    # ============ MÉTODOS DE VALIDACIÓN ============

    def _validate_configuracion_data(
        self, data: Dict[str, Any], for_update: bool = False
    ) -> Tuple[bool, str]:
        """
        Valida los datos de configuración

        Args:
            data: Diccionario con datos de configuración
            for_update: Si es True, valida para actualización

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        # Campos requeridos para creación
        if not for_update:
            for field in self.required_columns:
                if field not in data or data[field] is None:
                    return False, f"Campo requerido faltante: {field}"

        # Validar clave
        if "clave" in data and data["clave"]:
            clave = str(data["clave"]).strip()

            # Validar longitud
            if len(clave) < 2:
                return False, "La clave debe tener al menos 2 caracteres"
            if len(clave) > 100:
                return False, "La clave no puede exceder 100 caracteres"

            # Validar formato (solo mayúsculas, números y guión bajo)
            if not all(c.isupper() or c.isdigit() or c == "_" for c in clave):
                return (
                    False,
                    "Clave inválida. Use solo MAYÚSCULAS, números y guión bajo",
                )

            # Para creación, verificar que no exista
            if not for_update and self.clave_exists(clave):
                return False, f"La clave '{clave}' ya existe"

        # Validar valor (opcional pero si existe, validar según tipo)
        if "valor" in data and data["valor"] is not None:
            clave_actual = data.get("clave")
            if clave_actual and clave_actual in self.CLAVES_PREDEFINIDAS:
                # Validar según tipo predefinido
                tipo = self.CLAVES_PREDEFINIDAS[clave_actual].get("tipo", "string")
                valor_str = str(data["valor"])

                if tipo == "integer":
                    try:
                        int(valor_str)
                    except ValueError:
                        return (
                            False,
                            f"Valor para '{clave_actual}' debe ser un número entero",
                        )

                elif tipo == "decimal":
                    try:
                        float(valor_str)
                    except ValueError:
                        return (
                            False,
                            f"Valor para '{clave_actual}' debe ser un número decimal",
                        )

                elif tipo == "boolean":
                    if valor_str.lower() not in [
                        "true",
                        "false",
                        "1",
                        "0",
                        "yes",
                        "no",
                    ]:
                        return (
                            False,
                            f"Valor para '{clave_actual}' debe ser booleano (true/false)",
                        )

                # Validar opciones si existen
                opciones = self.CLAVES_PREDEFINIDAS[clave_actual].get("opciones")
                if opciones and valor_str not in opciones:
                    return (
                        False,
                        f"Valor inválido para '{clave_actual}'. Opciones: {', '.join(opciones)}",
                    )

        # Validar descripción
        if "descripcion" in data and data["descripcion"]:
            descripcion = str(data["descripcion"]).strip()
            if len(descripcion) > 500:
                return False, "La descripción no puede exceder 500 caracteres"

        return True, "Datos válidos"

    def clave_exists(self, clave: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si una clave ya existe

        Args:
            clave: Clave a verificar
            exclude_id: ID a excluir de la verificación (para updates)

        Returns:
            bool: True si existe, False en caso contrario
        """
        try:
            if exclude_id:
                query = """
                SELECT COUNT(*) as count 
                FROM configuraciones 
                WHERE clave = %s AND id != %s
                """
                params = (clave, exclude_id)
            else:
                query = "SELECT COUNT(*) as count FROM configuraciones WHERE clave = %s"
                params = (clave,)

            result = self.fetch_one(query, params)
            return result["count"] > 0 if result else False
        except Exception as e:
            logger.error(f"Error verificando clave: {e}")
            return False

    # ============ MÉTODOS CRUD PRINCIPALES ============

    def create(self, data: Dict[str, Any], validar_tipo: bool = True) -> Optional[int]:
        """
        Crea una nueva configuración

        Args:
            data: Diccionario con datos de configuración
            validar_tipo: Si es True, valida el tipo según clave predefinida

        Returns:
            Optional[int]: ID de la configuración creada o None si hay error
        """
        # Preparar datos
        insert_data = data.copy()

        # Asegurar que la clave esté en mayúsculas
        if "clave" in insert_data:
            insert_data["clave"] = str(insert_data["clave"]).strip().upper()

        # Validar datos
        is_valid, error_msg = self._validate_configuracion_data(
            insert_data, for_update=False
        )

        if not is_valid:
            logger.error(f"Error validando datos de configuración: {error_msg}")
            return None

        try:
            # Iniciar transacción
            self.begin_transaction()

            # Establecer valores por defecto
            defaults = {
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            for key, value in defaults.items():
                if key not in insert_data or insert_data[key] is None:
                    insert_data[key] = value

            # Insertar en base de datos
            config_id = self.insert(self.table_name, insert_data, returning="id")

            if not config_id:
                self.rollback()
                logger.error("No se pudo insertar la configuración en la base de datos")
                return None

            logger.info(f"✓ Configuración creada exitosamente con ID: {config_id}")

            # Invalidar cache
            self._invalidate_cache()

            # Commit de la transacción
            self.commit()

            return config_id

        except Exception as e:
            self.rollback()
            logger.error(f"Error creando configuración: {e}", exc_info=True)
            return None

    def read(self, config_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene una configuración por su ID

        Args:
            config_id: ID de la configuración

        Returns:
            Optional[Dict]: Datos de la configuración o None si no existe
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE id = %s"
            result = self.fetch_one(query, (config_id,))
            return result
        except Exception as e:
            logger.error(f"Error obteniendo configuración: {e}")
            return None

    def read_by_clave(self, clave: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene una configuración por su clave

        Args:
            clave: Clave de la configuración

        Returns:
            Optional[Dict]: Datos de la configuración o None si no existe
        """
        try:
            clave_normalizada = clave.strip().upper()
            query = f"SELECT * FROM {self.table_name} WHERE clave = %s"
            result = self.fetch_one(query, (clave_normalizada,))
            return result
        except Exception as e:
            logger.error(f"Error obteniendo configuración por clave: {e}")
            return None

    def update(self, config_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza una configuración existente

        Args:
            config_id: ID de la configuración a actualizar
            data: Diccionario con datos a actualizar

        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        if not data:
            return False

        # Obtener datos actuales para validación
        config_actual = self.read(config_id)
        if not config_actual:
            return False

        # Combinar datos actuales con los nuevos para validación
        data_with_id = {**config_actual, **data}
        data_with_id["id"] = config_id

        # Asegurar que la clave esté en mayúsculas si se está actualizando
        if "clave" in data and data["clave"]:
            data["clave"] = str(data["clave"]).strip().upper()

        # Validar datos
        is_valid, error_msg = self._validate_configuracion_data(
            data_with_id, for_update=True
        )

        if not is_valid:
            logger.error(f"Error validando datos: {error_msg}")
            return False

        try:
            # Agregar timestamp de actualización
            if "updated_at" not in data:
                data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Actualizar en base de datos
            # Build UPDATE query
            set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
            values = list(data.values()) + [config_id]
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = %s"
            result = self.execute_query(query, tuple(values), commit=True)

            if not result:
                return False

            logger.info(f"✓ Configuración {config_id} actualizada exitosamente")

            # Invalidar cache
            self._invalidate_cache()

            return True

        except Exception as e:
            logger.error(f"Error actualizando configuración: {e}", exc_info=True)
            return False

    def update_by_clave(
        self, clave: str, valor: Any, descripcion: Optional[str] = None
    ) -> bool:
        """
        Actualiza una configuración por su clave

        Args:
            clave: Clave de la configuración
            valor: Nuevo valor
            descripcion: Nueva descripción (opcional)

        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            clave_normalizada = clave.strip().upper()

            # Verificar si existe
            config_actual = self.read_by_clave(clave_normalizada)

            if config_actual:
                # Actualizar existente
                update_data = {
                    "valor": str(valor) if valor is not None else None,
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

                if descripcion is not None:
                    update_data["descripcion"] = descripcion

                return self.update(config_actual["id"], update_data)
            else:
                # Crear nueva
                create_data = {
                    "clave": clave_normalizada,
                    "valor": str(valor) if valor is not None else None,
                    "descripcion": descripcion
                    or f"Configuración para {clave_normalizada}",
                }

                return self.create(create_data) is not None

        except Exception as e:
            logger.error(f"Error actualizando configuración por clave: {e}")
            return False

    def delete(self, config_id: int) -> bool:
        """
        Elimina una configuración

        Args:
            config_id: ID de la configuración

        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            # Verificar si es una clave predefinida del sistema
            config = self.read(config_id)
            if not config:
                return False

            clave = config.get("clave", "")
            if clave in self.CLAVES_PREDEFINIDAS:
                logger.warning(
                    f"No se puede eliminar configuración predefinida del sistema: {clave}"
                )
                return False

            # Eliminar configuración
            query = f"DELETE FROM {self.table_name} WHERE id = %s"
            result = self.execute_query(query, (config_id,), commit=True)

            if result:
                # Invalidar cache
                self._invalidate_cache()
                logger.info(f"✓ Configuración {config_id} eliminada exitosamente")
                return True

            return False

        except Exception as e:
            logger.error(f"Error eliminando configuración: {e}")
            return False

    def delete_by_clave(self, clave: str) -> bool:
        """
        Elimina una configuración por su clave

        Args:
            clave: Clave de la configuración

        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            clave_normalizada = clave.strip().upper()

            # Verificar si es una clave predefinida del sistema
            if clave_normalizada in self.CLAVES_PREDEFINIDAS:
                logger.warning(
                    f"No se puede eliminar configuración predefinida del sistema: {clave_normalizada}"
                )
                return False

            # Eliminar configuración
            query = f"DELETE FROM {self.table_name} WHERE clave = %s"
            result = self.execute_query(query, (clave_normalizada,), commit=True)

            if result:
                # Invalidar cache
                self._invalidate_cache()
                logger.info(
                    f"✓ Configuración '{clave_normalizada}' eliminada exitosamente"
                )
                return True

            return False

        except Exception as e:
            logger.error(f"Error eliminando configuración por clave: {e}")
            return False

    # ============ MÉTODOS DE OBTENCIÓN DE VALORES ============

    def get_valor(
        self, clave: str, tipo_retorno: Type[T] = str, valor_default: Optional[T] = None
    ) -> Optional[T]:
        """
        Obtiene el valor de una configuración con conversión de tipo

        Args:
            clave: Clave de la configuración
            tipo_retorno: Tipo de retorno deseado (str, int, float, bool, Decimal, dict, list)
            valor_default: Valor por defecto si no existe la configuración

        Returns:
            Valor de la configuración convertido al tipo especificado, o valor_default
        """
        try:
            clave_normalizada = clave.strip().upper()

            # Intentar obtener del cache primero
            if clave_normalizada in self._cache:
                cached_value = self._cache[clave_normalizada]
                if isinstance(cached_value, tipo_retorno):
                    return cached_value

            # Obtener de la base de datos
            config = self.read_by_clave(clave_normalizada)

            if config and config.get("valor") is not None:
                valor_str = str(config["valor"])
                valor_convertido = self._convertir_valor(valor_str, tipo_retorno)

                # Almacenar en cache
                self._cache[clave_normalizada] = valor_convertido

                return valor_convertido
            else:
                # Usar valor por defecto de configuración predefinida si existe
                if clave_normalizada in self.CLAVES_PREDEFINIDAS:
                    valor_default_config = self.CLAVES_PREDEFINIDAS[
                        clave_normalizada
                    ].get("valor_default")
                    if valor_default_config is not None:
                        valor_convertido = self._convertir_valor(
                            valor_default_config, tipo_retorno
                        )
                        return valor_convertido

                # Usar valor por defecto proporcionado
                return valor_default

        except Exception as e:
            logger.error(f"Error obteniendo valor de configuración: {e}")
            return valor_default

    def get_valor_string(self, clave: str, valor_default: str = "") -> str:
        """Obtiene un valor como string"""
        valor = self.get_valor(clave, str, valor_default)
        return valor if valor is not None else valor_default

    def get_valor_int(self, clave: str, valor_default: int = 0) -> int:
        """Obtiene un valor como entero"""
        valor = self.get_valor(clave, int, valor_default)
        return valor if valor is not None else valor_default

    def get_valor_float(self, clave: str, valor_default: float = 0.0) -> float:
        """Obtiene un valor como float"""
        valor = self.get_valor(clave, float, valor_default)
        return valor if valor is not None else valor_default

    def get_valor_decimal(
        self, clave: str, valor_default: Decimal = Decimal("0")
    ) -> Decimal:
        """Obtiene un valor como Decimal"""
        valor = self.get_valor(clave, Decimal, valor_default)
        return valor if valor is not None else valor_default

    def get_valor_bool(self, clave: str, valor_default: bool = False) -> bool:
        """Obtiene un valor como booleano"""
        valor = self.get_valor(clave, bool, valor_default)
        return valor if valor is not None else valor_default

    def get_valor_json(
        self, clave: str, valor_default: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Obtiene un valor como JSON (diccionario)"""
        valor = self.get_valor(clave, dict, valor_default)
        return valor

    def get_valor_list(
        self, clave: str, valor_default: Optional[List] = None
    ) -> Optional[List]:
        """Obtiene un valor como JSON (lista)"""
        valor = self.get_valor(clave, list, valor_default)
        return valor

    def _convertir_valor(self, valor_str: str, tipo_destino: Type[T]) -> T:
        """
        Convierte un valor string al tipo especificado

        Args:
            valor_str: Valor como string
            tipo_destino: Tipo de destino

        Returns:
            Valor convertido al tipo destino
        """
        try:
            # Para tipos específicos, necesitamos usar un enfoque diferente
            # debido a las limitaciones de los type hints en Python

            if tipo_destino == str:
                return str(valor_str)  # type: ignore

            elif tipo_destino == int:
                # Maneja "1.0" -> 1
                return int(float(valor_str))  # type: ignore

            elif tipo_destino == float:
                return float(valor_str)  # type: ignore

            elif tipo_destino == Decimal:
                return Decimal(str(valor_str))  # type: ignore

            elif tipo_destino == bool:
                val_lower = valor_str.lower().strip()
                if val_lower in ["true", "1", "yes", "si", "sí", "on"]:
                    return True  # type: ignore
                elif val_lower in ["false", "0", "no", "off"]:
                    return False  # type: ignore
                else:
                    # Intentar convertir a bool
                    return bool(valor_str)  # type: ignore

            elif tipo_destino in [dict, list]:
                # Intentar parsear como JSON
                try:
                    return json.loads(valor_str)  # type: ignore
                except json.JSONDecodeError:
                    # Si no es JSON válido, devolver como string en dict
                    if tipo_destino == dict:
                        return {"value": valor_str}  # type: ignore
                    else:
                        return [valor_str]  # type: ignore

            else:
                # Tipo no soportado, devolver como string
                return str(valor_str)  # type: ignore

        except (ValueError, TypeError, InvalidOperation) as e:
            logger.warning(
                f"Error convirtiendo valor '{valor_str}' a {tipo_destino}: {e}"
            )
            # Devolver valor por defecto según el tipo
            if tipo_destino == str:
                return ""  # type: ignore
            elif tipo_destino == int:
                return 0  # type: ignore
            elif tipo_destino == float:
                return 0.0  # type: ignore
            elif tipo_destino == Decimal:
                return Decimal("0")  # type: ignore
            elif tipo_destino == bool:
                return False  # type: ignore
            elif tipo_destino == dict:
                return {}  # type: ignore
            elif tipo_destino == list:
                return []  # type: ignore
            else:
                # Intentar crear instancia del tipo
                try:
                    return tipo_destino()  # type: ignore
                except:
                    return None  # type: ignore

    # ============ MÉTODOS DE CACHE ============

    def _invalidate_cache(self):
        """Invalida el cache de configuraciones"""
        self._cache = {}
        self._cache_timestamp = None

    def load_all_to_cache(self) -> bool:
        """
        Carga todas las configuraciones a cache

        Returns:
            bool: True si se cargó exitosamente
        """
        try:
            query = f"SELECT clave, valor FROM {self.table_name}"
            results = self.fetch_all(query)

            if results:
                self._cache = {}
                for row in results:
                    clave = row["clave"]
                    valor_str = row["valor"]

                    # Determinar tipo según clave predefinida
                    tipo = "string"
                    if clave in self.CLAVES_PREDEFINIDAS:
                        tipo = self.CLAVES_PREDEFINIDAS[clave].get("tipo", "string")

                    # Convertir según tipo
                    if tipo == "integer":
                        self._cache[clave] = int(float(valor_str)) if valor_str else 0
                    elif tipo == "decimal":
                        self._cache[clave] = (
                            Decimal(valor_str) if valor_str else Decimal("0")
                        )
                    elif tipo == "boolean":
                        val_lower = str(valor_str).lower()
                        self._cache[clave] = val_lower in ["true", "1", "yes"]
                    else:
                        self._cache[clave] = str(valor_str) if valor_str else ""

                self._cache_timestamp = datetime.now()
                logger.info(
                    f"✓ Cache de configuraciones cargado con {len(self._cache)} elementos"
                )
                return True
            else:
                logger.warning("No se encontraron configuraciones para cargar en cache")
                return False

        except Exception as e:
            logger.error(f"Error cargando configuraciones a cache: {e}")
            return False

    def get_all_cached(self) -> Dict[str, Any]:
        """
        Obtiene todas las configuraciones desde cache o las carga si es necesario

        Returns:
            Dict[str, Any]: Todas las configuraciones en cache
        """
        try:
            # Verificar si cache está vacío o expirado
            if not self._cache or not self._cache_timestamp:
                self.load_all_to_cache()
            else:
                # Verificar si cache expiró
                tiempo_transcurrido = (
                    datetime.now() - self._cache_timestamp
                ).total_seconds()
                if tiempo_transcurrido > self._CACHE_TTL:
                    self.load_all_to_cache()

            return self._cache.copy()

        except Exception as e:
            logger.error(f"Error obteniendo configuraciones desde cache: {e}")
            return {}

    # ============ MÉTODOS DE CONFIGURACIONES PREDEFINIDAS ============

    def inicializar_configuraciones_predefinidas(
        self, forzar: bool = False
    ) -> Dict[str, bool]:
        """
        Inicializa las configuraciones predefinidas del sistema

        Args:
            forzar: Si es True, actualiza incluso si ya existen

        Returns:
            Dict[str, bool]: Resultado por cada configuración
        """
        resultados = {}

        try:
            for clave, config_info in self.CLAVES_PREDEFINIDAS.items():
                try:
                    # Verificar si ya existe
                    existe = self.read_by_clave(clave)

                    if existe and not forzar:
                        resultados[clave] = False  # Ya existe, no se actualizó
                        continue

                    # Preparar datos
                    datos = {
                        "clave": clave,
                        "valor": config_info.get("valor_default", ""),
                        "descripcion": config_info.get(
                            "descripcion", f"Configuración para {clave}"
                        ),
                    }

                    # Crear o actualizar
                    if existe:
                        # Actualizar existente
                        success = self.update(existe["id"], datos)
                    else:
                        # Crear nueva
                        success = self.create(datos) is not None

                    resultados[clave] = success

                    if success:
                        logger.debug(
                            f"Configuración '{clave}' {'actualizada' if existe else 'creada'} exitosamente"
                        )
                    else:
                        logger.warning(
                            f"Error {'actualizando' if existe else 'creando'} configuración '{clave}'"
                        )

                except Exception as e:
                    logger.error(f"Error procesando configuración '{clave}': {e}")
                    resultados[clave] = False

            # Invalidar cache después de inicialización
            self._invalidate_cache()

            total_creadas = sum(1 for success in resultados.values() if success)
            logger.info(
                f"✓ Configuraciones predefinidas inicializadas: {total_creadas}/{len(self.CLAVES_PREDEFINIDAS)}"
            )

            return resultados

        except Exception as e:
            logger.error(f"Error inicializando configuraciones predefinidas: {e}")
            return {}

    def get_configuraciones_predefinidas_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene información de todas las configuraciones predefinidas

        Returns:
            Dict[str, Dict[str, Any]]: Información de configuraciones predefinidas
        """
        return self.CLAVES_PREDEFINIDAS.copy()

    # ============ MÉTODOS DE CONSULTA AVANZADOS ============

    def buscar_por_patron(self, patron: str) -> List[Dict[str, Any]]:
        """
        Busca configuraciones por patrón en la clave

        Args:
            patron: Patrón a buscar (ej: "SISTEMA_%")

        Returns:
            List[Dict]: Lista de configuraciones encontradas
        """
        try:
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE clave ILIKE %s
                ORDER BY clave
            """
            results = self.fetch_all(query, (f"%{patron}%",))
            return results if results else []
        except Exception as e:
            logger.error(f"Error buscando configuraciones por patrón: {e}")
            return []

    def obtener_todas(
        self, incluir_sensibles: bool = False
    ) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene todas las configuraciones del sistema

        Args:
            incluir_sensibles: Si es True, incluye configuraciones sensibles

        Returns:
            Dict[str, Dict[str, Any]]: Diccionario con clave -> datos de configuración
        """
        try:
            query = f"SELECT * FROM {self.table_name} ORDER BY clave"
            results = self.fetch_all(query)

            configuraciones = {}
            if results:
                for row in results:
                    clave = row["clave"]

                    # Ocultar valores sensibles si no se solicitan
                    if not incluir_sensibles and clave in self.CLAVES_PREDEFINIDAS:
                        if self.CLAVES_PREDEFINIDAS[clave].get("seguro", False):
                            row["valor"] = "********" if row["valor"] else None

                    configuraciones[clave] = row

            return configuraciones

        except Exception as e:
            logger.error(f"Error obteniendo todas las configuraciones: {e}")
            return {}

    def obtener_por_grupo(self, grupo: str) -> Dict[str, Any]:
        """
        Obtiene configuraciones por grupo (basado en prefijo de clave)

        Args:
            grupo: Grupo a obtener (ej: "SISTEMA", "FACTURACION", etc.)

        Returns:
            Dict[str, Any]: Configuraciones del grupo
        """
        try:
            patron_grupo = f"{grupo}_%"
            configs = self.buscar_por_patron(patron_grupo)

            resultado = {}
            for config in configs:
                clave = config["clave"]
                # Remover prefijo del grupo para la clave en el resultado
                clave_sin_prefijo = (
                    clave[len(grupo) + 1 :] if clave.startswith(f"{grupo}_") else clave
                )
                resultado[clave_sin_prefijo] = config["valor"]

            return resultado

        except Exception as e:
            logger.error(f"Error obteniendo configuraciones del grupo '{grupo}': {e}")
            return {}

    # ============ MÉTODOS DE BACKUP Y RESTAURACIÓN ============

    def exportar_configuraciones(
        self, incluir_sensibles: bool = False
    ) -> Dict[str, Any]:
        """
        Exporta todas las configuraciones a un diccionario

        Args:
            incluir_sensibles: Si es True, incluye configuraciones sensibles

        Returns:
            Dict[str, Any]: Configuraciones exportadas
        """
        try:
            configuraciones = self.obtener_todas(incluir_sensibles)

            return {
                "exportado_en": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_configuraciones": len(configuraciones),
                "configuraciones": configuraciones,
            }

        except Exception as e:
            logger.error(f"Error exportando configuraciones: {e}")
            return {}

    def importar_configuraciones(
        self, configuraciones: Dict[str, Any], modo_importacion: str = "actualizar"
    ) -> Dict[str, bool]:
        """
        Importa configuraciones desde un diccionario

        Args:
            configuraciones: Diccionario con configuraciones a importar
            modo_importacion: "actualizar" (solo existentes), "crear" (solo nuevas), "completo"

        Returns:
            Dict[str, bool]: Resultado por cada configuración
        """
        resultados = {}

        try:
            for clave, datos in configuraciones.items():
                try:
                    if not isinstance(datos, dict):
                        # Si es solo el valor, crear estructura mínima
                        datos = {"valor": datos}

                    clave_normalizada = clave.strip().upper()

                    # Verificar si existe
                    existe = self.read_by_clave(clave_normalizada)

                    # Determinar si se debe procesar según modo
                    procesar = False
                    if modo_importacion == "actualizar" and existe:
                        procesar = True
                    elif modo_importacion == "crear" and not existe:
                        procesar = True
                    elif modo_importacion == "completo":
                        procesar = True

                    if procesar:
                        if existe:
                            # Actualizar existente
                            update_data = {
                                "valor": datos.get("valor"),
                                "descripcion": datos.get("descripcion"),
                                "updated_at": datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                            }
                            # Remover valores None
                            update_data = {
                                k: v for k, v in update_data.items() if v is not None
                            }

                            success = self.update(existe["id"], update_data)
                        else:
                            # Crear nueva
                            create_data = {
                                "clave": clave_normalizada,
                                "valor": datos.get("valor"),
                                "descripcion": datos.get(
                                    "descripcion",
                                    f"Configuración importada para {clave_normalizada}",
                                ),
                            }
                            success = self.create(create_data) is not None

                        resultados[clave] = success
                    else:
                        resultados[clave] = False  # No procesado según modo

                except Exception as e:
                    logger.error(
                        f"Error procesando configuración '{clave}' durante importación: {e}"
                    )
                    resultados[clave] = False

            # Invalidar cache después de importación
            self._invalidate_cache()

            total_procesadas = sum(1 for success in resultados.values() if success)
            logger.info(
                f"✓ Configuraciones importadas: {total_procesadas}/{len(configuraciones)}"
            )

            return resultados

        except Exception as e:
            logger.error(f"Error importando configuraciones: {e}")
            return {}

    # ============ MÉTODOS DE CONFIGURACIÓN DEL SISTEMA ============

    def obtener_configuracion_sistema(self) -> Dict[str, Any]:
        """
        Obtiene la configuración completa del sistema

        Returns:
            Dict[str, Any]: Configuración del sistema organizada por grupos
        """
        try:
            # Obtener todas las configuraciones desde cache
            todas_configs = self.get_all_cached()

            # Organizar por grupos
            grupos = {
                "sistema": {},
                "empresa": {},
                "facturacion": {},
                "seguridad": {},
                "email": {},
                "impresion": {},
                "reportes": {},
                "siat": {},
                "sesion": {},
                "backup": {},
            }

            for clave, valor in todas_configs.items():
                if clave.startswith("SISTEMA_"):
                    grupos["sistema"][clave[8:]] = valor
                elif clave.startswith("EMPRESA_"):
                    grupos["empresa"][clave[8:]] = valor
                elif clave.startswith("FACTURACION_"):
                    grupos["facturacion"][clave[12:]] = valor
                elif clave.startswith("SEGURIDAD_"):
                    grupos["seguridad"][clave[10:]] = valor
                elif clave.startswith("EMAIL_"):
                    grupos["email"][clave[6:]] = valor
                elif clave.startswith("IMPRESION_"):
                    grupos["impresion"][clave[10:]] = valor
                elif clave.startswith("REPORTES_"):
                    grupos["reportes"][clave[9:]] = valor
                elif clave.startswith("SIAT_"):
                    grupos["siat"][clave[5:]] = valor
                elif clave.startswith("SESION_"):
                    grupos["sesion"][clave[7:]] = valor
                elif clave.startswith("BACKUP_"):
                    grupos["backup"][clave[7:]] = valor
                else:
                    # Configuraciones sin grupo específico
                    if "otras" not in grupos:
                        grupos["otras"] = {}
                    grupos["otras"][clave] = valor

            # Agregar metadatos
            resultado = {
                "obtenido_en": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_configuraciones": len(todas_configs),
                "grupos": grupos,
            }

            return resultado

        except Exception as e:
            logger.error(f"Error obteniendo configuración del sistema: {e}")
            return {}


# Ejemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)

    # Crear instancia del modelo
    config_model = ConfiguracionesModel()

    print("=== Inicializando configuraciones predefinidas ===")
    resultados = config_model.inicializar_configuraciones_predefinidas()
    creadas = sum(1 for success in resultados.values() if success)
    print(f"Configuraciones inicializadas: {creadas}/{len(resultados)}")

    print("\n=== Obteniendo valores de configuración ===")

    # Obtener valores con tipos específicos
    nombre_sistema = config_model.get_valor_string("SISTEMA_NOMBRE")
    tasa_iva = config_model.get_valor_decimal("FACTURACION_TASA_IVA")
    backup_automatico = config_model.get_valor_bool("BACKUP_AUTOMATICO")

    print(f"Nombre del sistema: {nombre_sistema}")
    print(f"Tasa de IVA: {tasa_iva}")
    print(
        f"Backup automático: {'Habilitado' if backup_automatico else 'Deshabilitado'}"
    )

    print("\n=== Actualizando configuración ===")
    success = config_model.update_by_clave("SISTEMA_NOMBRE", "FormaGestPro 2.0")
    print(f"Configuración actualizada: {'✓' if success else '✗'}")

    print("\n=== Obteniendo configuración completa del sistema ===")
    config_sistema = config_model.obtener_configuracion_sistema()
    print(f"Total configuraciones: {config_sistema.get('total_configuraciones', 0)}")

    print("\n=== Fin del ejemplo ===")
