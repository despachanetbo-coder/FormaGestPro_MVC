# app/models/empresa_model.py - VERSIÓN CORREGIDA Y OPTIMIZADA

"""
Modelo de Empresa - Gestión de información de la empresa
Hereda de BaseModel para operaciones de base de datos
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from decimal import Decimal

from .base_model import BaseModel

logger = logging.getLogger(__name__)


class EmpresaModel(BaseModel):
    """Modelo para gestión de información empresarial"""

    # Nombre de la tabla en la base de datos
    TABLE_NAME = "empresa"

    # Secuencia para IDs autoincrementales
    SEQUENCE_NAME = "seq_empresa_id"

    def __init__(self):
        """Inicializa el modelo de empresa"""
        super().__init__()

        # Columnas de la tabla para validación y referencia
        self.columns = [
            "id",
            "nombre",
            "nit",
            "direccion",
            "telefono",
            "email",
            "logo_path",
            "created_at",
        ]

        # Columnas requeridas para inserción
        self.required_columns = ["nombre", "nit"]

        # Valores por defecto según la estructura de la tabla
        self.default_values = {
            "nombre": "Formación Continua Consultora",
            "nit": "1234567012",
        }

        # Configuración inicial de empresa
        self._empresa_config = None
        logger.debug(f"✅ EmpresaModel inicializado. Tabla: {self.TABLE_NAME}")

    # ============ MÉTODOS DE VALIDACIÓN ============

    def _validate_empresa_data(
        self, data: Dict[str, Any], for_update: bool = False
    ) -> Tuple[bool, str]:
        """
        Valida los datos de la empresa antes de operaciones CRUD

        Args:
            data: Diccionario con datos de la empresa
            for_update: True si es para actualización, False para creación

        Returns:
            Tuple: (es_válido, mensaje_error)
        """
        try:
            # Validar campos requeridos para creación
            if not for_update:
                for field in self.required_columns:
                    if field not in data or not str(data.get(field, "")).strip():
                        return False, f"Campo requerido faltante: '{field}'"

            # Validar NIT (debe ser único)
            if "nit" in data and data["nit"]:
                nit = str(data["nit"]).strip()
                if not nit:
                    return False, "NIT no puede estar vacío"

                # Verificar unicidad del NIT
                existing_id = data.get("id") if for_update else None
                if self.nit_exists(nit, exclude_id=existing_id):
                    return False, f"El NIT '{nit}' ya está registrado"

            # Validar email si se proporciona
            if "email" in data and data["email"]:
                email = str(data["email"]).strip()
                if email and "@" not in email:
                    return False, "Formato de email inválido"

            # Validar longitud máxima de campos
            field_limits = {
                "nombre": 200,
                "nit": 20,
                "direccion": 500,
                "telefono": 20,
                "email": 100,
                "logo_path": 500,
            }

            for field, max_length in field_limits.items():
                if field in data and data[field]:
                    value = str(data[field])
                    if len(value) > max_length:
                        return (
                            False,
                            f"'{field}' excede el límite de {max_length} caracteres",
                        )

            return True, "Datos válidos"

        except Exception as e:
            logger.error(f"Error en validación de datos de empresa: {e}")
            return False, f"Error de validación: {str(e)}"

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza y formatea los datos de la empresa

        Args:
            data: Datos crudos de la empresa

        Returns:
            Diccionario con datos sanitizados
        """
        sanitized = {}

        for key, value in data.items():
            if key in self.columns:
                # Sanitizar strings: eliminar espacios y convertir a string seguro
                if isinstance(value, str):
                    sanitized[key] = value.strip()
                # Mantener otros tipos de datos
                else:
                    sanitized[key] = value

        return sanitized

    # ============ MÉTODOS CRUD PRINCIPALES ============

    def create(self, data: Dict[str, Any]) -> Optional[int]:
        """
        Crea un nuevo registro de empresa

        Args:
            data: Datos de la empresa a crear

        Returns:
            ID del registro creado o None si hay error
        """
        try:
            # Sanitizar datos
            data = self._sanitize_data(data)

            # Aplicar valores por defecto para campos faltantes
            for field, default_value in self.default_values.items():
                if field not in data or not data[field]:
                    data[field] = default_value

            # Validar datos
            is_valid, error_msg = self._validate_empresa_data(data, for_update=False)
            if not is_valid:
                logger.error(
                    f"❌ Datos inválidos para creación de empresa: {error_msg}"
                )
                return None

            # Insertar en la base de datos
            result = self.insert(self.TABLE_NAME, data, returning="id")

            if result:
                empresa_id = result[0] if isinstance(result, list) else result
                logger.info(f"✅ Empresa creada exitosamente con ID: {empresa_id}")
                return empresa_id

            logger.error("❌ No se pudo crear la empresa (resultado vacío)")
            return None

        except Exception as e:
            logger.error(f"❌ Error creando empresa: {e}", exc_info=True)
            return None

    def read(self, empresa_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene una empresa por su ID

        Args:
            empresa_id: ID de la empresa a buscar

        Returns:
            Diccionario con datos de la empresa o None si no existe
        """
        try:
            query = f"SELECT * FROM {self.TABLE_NAME} WHERE id = %s"
            result = self.fetch_one(query, (empresa_id,))

            if result:
                logger.debug(f"✅ Empresa {empresa_id} obtenida correctamente")
                return result

            logger.warning(f"⚠️  Empresa con ID {empresa_id} no encontrada")
            return None

        except Exception as e:
            logger.error(f"❌ Error obteniendo empresa {empresa_id}: {e}")
            return None

    def update(self, empresa_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza los datos de una empresa existente

        Args:
            empresa_id: ID de la empresa a actualizar
            data: Datos a actualizar

        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        try:
            if not data:
                logger.warning("⚠️  No hay datos para actualizar")
                return False

            # Verificar que la empresa exista
            existing = self.read(empresa_id)
            if not existing:
                logger.error(
                    f"❌ No se puede actualizar: empresa {empresa_id} no existe"
                )
                return False

            # Sanitizar datos
            data = self._sanitize_data(data)

            # Añadir ID para validación de unicidad
            data_with_id = data.copy()
            data_with_id["id"] = empresa_id

            # Validar datos
            is_valid, error_msg = self._validate_empresa_data(
                data_with_id, for_update=True
            )
            if not is_valid:
                logger.error(f"❌ Datos inválidos para actualización: {error_msg}")
                return False

            # Actualizar en la base de datos
            result = self.update_table(
                table=self.TABLE_NAME,
                data=data,
                condition="id = %s",
                params=(empresa_id,),
            )

            if result and result > 0:
                logger.info(f"✅ Empresa {empresa_id} actualizada exitosamente")
                return True

            logger.warning(f"⚠️  No se actualizaron registros para empresa {empresa_id}")
            return False

        except Exception as e:
            logger.error(
                f"❌ Error actualizando empresa {empresa_id}: {e}", exc_info=True
            )
            return False

    def delete(self, empresa_id: int) -> bool:
        """
        Elimina una empresa (¡CUIDADO! Esta operación es permanente)

        Args:
            empresa_id: ID de la empresa a eliminar

        Returns:
            True si la eliminación fue exitosa, False en caso contrario
        """
        try:
            # Verificar que la empresa exista
            existing = self.read(empresa_id)
            if not existing:
                logger.error(f"❌ No se puede eliminar: empresa {empresa_id} no existe")
                return False

            # Eliminar de la base de datos
            query = f"DELETE FROM {self.TABLE_NAME} WHERE id = %s"
            result = self.execute_query(query, (empresa_id,), commit=True)

            if result and result > 0:
                logger.warning(f"⚠️  Empresa {empresa_id} eliminada permanentemente")
                return True

            logger.warning(f"⚠️  No se eliminó la empresa {empresa_id}")
            return False

        except Exception as e:
            logger.error(f"❌ Error eliminando empresa {empresa_id}: {e}")
            return False

    # ============ MÉTODOS DE CONSULTA ESPECÍFICOS ============

    def get_datos_empresa(self) -> Dict[str, Any]:
        """
        Obtiene los datos de la empresa principal

        Returns:
            Diccionario con datos de la empresa o valores por defecto
        """
        try:
            # Intentar obtener la primera empresa registrada
            query = f"SELECT * FROM {self.TABLE_NAME} ORDER BY id LIMIT 1"
            result = self.fetch_one(query)

            if result:
                logger.debug("✅ Datos de empresa obtenidos de la base de datos")
                return result

            # Si no hay empresa registrada, devolver valores por defecto
            logger.warning("⚠️  No hay empresa registrada, usando valores por defecto")
            return {
                "id": None,
                "nombre": self.default_values["nombre"],
                "nit": self.default_values["nit"],
                "direccion": "No especificada",
                "telefono": "No especificado",
                "email": "info@formacioncontinua.com",
                "logo_path": None,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

        except Exception as e:
            logger.error(f"❌ Error obteniendo datos de empresa: {e}")
            # Devolver valores por defecto en caso de error
            return {
                "id": None,
                "nombre": self.default_values["nombre"],
                "nit": self.default_values["nit"],
                "direccion": "Error al cargar datos",
                "telefono": "N/A",
                "email": "error@empresa.com",
                "logo_path": None,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

    def get_configuracion(self) -> Dict[str, Any]:
        """
        Obtiene la configuración de la empresa para el sistema

        Returns:
            Diccionario con configuración del sistema
        """
        try:
            empresa_data = self.get_datos_empresa()

            # Configuración por defecto del sistema
            config = {
                # Información de la empresa
                "empresa_nombre": empresa_data.get(
                    "nombre", self.default_values["nombre"]
                ),
                "empresa_nit": empresa_data.get("nit", self.default_values["nit"]),
                "empresa_direccion": empresa_data.get("direccion", "No especificada"),
                "empresa_telefono": empresa_data.get("telefono", "No especificado"),
                "empresa_email": empresa_data.get(
                    "email", "info@formacioncontinua.com"
                ),
                "empresa_logo": empresa_data.get("logo_path"),
                # Configuración del sistema
                "moneda": "USD",  # Moneda por defecto
                "iva": Decimal("16.00"),  # IVA por defecto 16%
                "retencion_iva": Decimal("75.00"),  # Retención IVA 75%
                "retencion_islr": Decimal("1.00"),  # Retención ISLR 1%
                "formato_fecha": "dd/MM/yyyy",  # Formato de fecha
                "formato_hora": "HH:mm:ss",  # Formato de hora
                "paginacion_registros": 20,  # Registros por página
                # Información de contacto soporte
                "soporte_email": "soporte@formacioncontinua.com",
                "soporte_telefono": "+58 212-1234567",
                "soporte_horario": "Lunes a Viernes 8:00 AM - 5:00 PM",
            }

            logger.debug("✅ Configuración de empresa obtenida")
            return config

        except Exception as e:
            logger.error(f"❌ Error obteniendo configuración: {e}")
            # Configuración por defecto en caso de error
            return {
                "empresa_nombre": self.default_values["nombre"],
                "empresa_nit": self.default_values["nit"],
                "empresa_direccion": "No disponible",
                "empresa_telefono": "No disponible",
                "empresa_email": "no-available@empresa.com",
                "moneda": "USD",
                "iva": Decimal("16.00"),
                "retencion_iva": Decimal("75.00"),
                "retencion_islr": Decimal("1.00"),
            }

    def nit_exists(self, nit: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si un NIT ya está registrado en la base de datos

        Args:
            nit: NIT a verificar
            exclude_id: ID a excluir de la búsqueda (para actualizaciones)

        Returns:
            True si el NIT ya existe, False en caso contrario
        """
        try:
            if exclude_id:
                query = f"SELECT COUNT(*) as count FROM {self.TABLE_NAME} WHERE nit = %s AND id != %s"
                params = (nit, exclude_id)
            else:
                query = (
                    f"SELECT COUNT(*) as count FROM {self.TABLE_NAME} WHERE nit = %s"
                )
                params = (nit,)

            result = self.fetch_one(query, params)
            return result["count"] > 0 if result else False

        except Exception as e:
            logger.error(f"❌ Error verificando existencia de NIT '{nit}': {e}")
            return False

    def buscar_por_nombre(self, nombre: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca empresas por nombre o parte del nombre

        Args:
            nombre: Nombre o parte del nombre a buscar
            limit: Límite de resultados

        Returns:
            Lista de empresas que coinciden con la búsqueda
        """
        try:
            search_term = f"%{nombre}%"
            query = f"""
                SELECT * FROM {self.TABLE_NAME} 
                WHERE nombre ILIKE %s 
                ORDER BY nombre
                LIMIT %s
            """

            results = self.fetch_all(query, (search_term, limit))
            logger.debug(
                f"✅ Búsqueda de empresas por nombre '{nombre}': {len(results)} resultados"
            )
            return results

        except Exception as e:
            logger.error(f"❌ Error buscando empresas por nombre '{nombre}': {e}")
            return []

    def obtener_todas(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtiene todas las empresas registradas

        Args:
            limit: Límite de resultados (por seguridad)

        Returns:
            Lista de todas las empresas
        """
        try:
            query = f"SELECT * FROM {self.TABLE_NAME} ORDER BY nombre LIMIT %s"
            results = self.fetch_all(query, (limit,))

            logger.debug(f"✅ Obtenidas {len(results)} empresas")
            return results

        except Exception as e:
            logger.error(f"❌ Error obteniendo todas las empresas: {e}")
            return []

    # ============ MÉTODOS DE INICIALIZACIÓN ============

    def initialize_empresa(self) -> Tuple[bool, str]:
        """
        Inicializa la empresa principal si no existe

        Returns:
            Tuple: (éxito, mensaje)
        """
        try:
            # Verificar si ya existe una empresa
            existing = self.get_datos_empresa()
            if existing.get("id"):
                return True, f"✅ Empresa ya existe: {existing.get('nombre')}"

            # Crear empresa por defecto
            empresa_data = {
                "nombre": self.default_values["nombre"],
                "nit": self.default_values["nit"],
                "direccion": "Dirección principal de la empresa",
                "telefono": "+58 212-1234567",
                "email": "info@formacioncontinua.com",
                "logo_path": None,
            }

            empresa_id = self.create(empresa_data)

            if empresa_id:
                logger.info(f"✅ Empresa inicializada con ID: {empresa_id}")
                return True, f"Empresa '{empresa_data['nombre']}' creada exitosamente"
            else:
                return False, "No se pudo crear la empresa inicial"

        except Exception as e:
            logger.error(f"❌ Error inicializando empresa: {e}")
            return False, f"Error al inicializar empresa: {str(e)}"

    def verificar_tabla(self) -> bool:
        """
        Verifica que la tabla de empresa exista y esté accesible

        Returns:
            True si la tabla está accesible, False en caso contrario
        """
        try:
            # Verificar si la tabla existe
            table_exists = self.table_exists(self.TABLE_NAME)

            if not table_exists:
                logger.error(f"❌ La tabla '{self.TABLE_NAME}' no existe")
                return False

            # Verificar si podemos acceder a la tabla
            test_query = f"SELECT COUNT(*) as count FROM {self.TABLE_NAME}"
            result = self.fetch_one(test_query)

            if result is not None:
                logger.debug(f"✅ Tabla '{self.TABLE_NAME}' verificada y accesible")
                return True
            else:
                logger.error(f"❌ No se puede acceder a la tabla '{self.TABLE_NAME}'")
                return False

        except Exception as e:
            logger.error(f"❌ Error verificando tabla '{self.TABLE_NAME}': {e}")
            return False

    # ============ MÉTODOS DE FORMATO Y PRESENTACIÓN ============

    def to_dict(self, empresa_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formatea los datos de la empresa para presentación

        Args:
            empresa_data: Datos crudos de la empresa

        Returns:
            Diccionario formateado para presentación
        """
        try:
            formatted = empresa_data.copy()

            # Formatear datos de contacto
            if formatted.get("telefono"):
                formatted["telefono_formateado"] = self._format_telefono(
                    formatted["telefono"]
                )

            if formatted.get("email"):
                formatted["email_link"] = f"mailto:{formatted['email']}"

            # Información adicional
            formatted["tiene_logo"] = bool(formatted.get("logo_path"))

            # Fecha formateada
            if formatted.get("created_at"):
                try:
                    if isinstance(formatted["created_at"], str):
                        fecha_obj = datetime.strptime(
                            formatted["created_at"], "%Y-%m-%d %H:%M:%S"
                        )
                    else:
                        fecha_obj = formatted["created_at"]

                    formatted["created_at_formateado"] = fecha_obj.strftime("%d/%m/%Y")
                except:
                    formatted["created_at_formateado"] = str(
                        formatted.get("created_at", "")
                    )

            return formatted

        except Exception as e:
            logger.error(f"❌ Error formateando datos de empresa: {e}")
            return empresa_data

    def _format_telefono(self, telefono: str) -> str:
        """Formatea un número de teléfono para presentación"""
        if not telefono:
            return ""

        # Eliminar caracteres no numéricos
        numeros = "".join(filter(str.isdigit, telefono))

        # Formatear según longitud
        if len(numeros) == 10:
            return f"({numeros[:3]}) {numeros[3:6]}-{numeros[6:]}"
        elif len(numeros) == 11:
            return f"+{numeros[0]} ({numeros[1:4]}) {numeros[4:7]}-{numeros[7:]}"
        else:
            return telefono

    # ============ MÉTODOS DE MANTENIMIENTO ============

    def backup_datos_empresa(self) -> Optional[Dict[str, Any]]:
        """
        Crea una copia de seguridad de los datos de la empresa

        Returns:
            Diccionario con datos de backup o None si hay error
        """
        try:
            empresa_data = self.get_datos_empresa()

            backup = {
                "empresa_data": empresa_data,
                "configuracion": self.get_configuracion(),
                "fecha_backup": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_empresas": len(self.obtener_todas()),
                "version_sistema": "FormaGestPro v2.0",
            }

            logger.info("✅ Backup de datos de empresa creado")
            return backup

        except Exception as e:
            logger.error(f"❌ Error creando backup de empresa: {e}")
            return None

    def __str__(self) -> str:
        """Representación en string del modelo"""
        empresa_data = self.get_datos_empresa()
        return f"EmpresaModel('{empresa_data.get('nombre', 'Sin nombre')}', NIT: {empresa_data.get('nit', 'Sin NIT')})"
