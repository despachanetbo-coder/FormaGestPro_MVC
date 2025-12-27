# app/controllers/configuraciones_controller.py
"""
Controlador para la gestión de configuraciones del sistema en FormaGestPro_MVC
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union, TypeVar, Type
from decimal import Decimal

from app.models.base_model import BaseModel
from app.models.configuracion_model import ConfiguracionesModel

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ConfiguracionesController(BaseModel):
    """Modelo para configuraciones del sistema"""

    def __init__(self, db_path: str = None):
        """
        Inicializar controlador de configuraciones

        Args:
            db_path: Ruta a la base de datos (opcional)
        """
        self.db_path = db_path
        self._cache = {}  # Cache para configuraciones frecuentes

    # ==================== OPERACIONES CRUD ====================

    def crear_configuracion(
        self, datos: Dict[str, Any]
    ) -> Tuple[bool, str, Optional[ConfiguracionesModel]]:
        """
        Crear una nueva configuración

        Args:
            datos: Diccionario con los datos de la configuración

        Returns:
            Tuple (éxito, mensaje, configuración)
        """
        try:
            # Validar datos requeridos
            errores = self._validar_datos_configuracion(datos)
            if errores:
                return False, "Errores de validación: " + "; ".join(errores), None

            # Verificar si ya existe una configuración con la misma clave
            clave = datos["clave"]
            existente = ConfiguracionesModel.get_by_key(clave)
            if existente:
                return (
                    False,
                    f"Ya existe una configuración con la clave '{clave}'",
                    None,
                )

            # Crear la configuración
            configuracion = ConfiguracionesModel(**datos)
            configuracion_id = configuracion.save()

            if configuracion_id:
                config_creada = ConfiguracionesModel.get_by_id(configuracion_id)
                self._cache[clave] = config_creada  # Actualizar cache
                mensaje = f"Configuración '{clave}' creada exitosamente"
                return True, mensaje, config_creada
            else:
                return (
                    False,
                    "Error al guardar la configuración en la base de datos",
                    None,
                )

        except Exception as e:
            logger.error(f"Error al crear configuración: {e}")
            return False, f"Error interno: {str(e)}", None

    def actualizar_configuracion(
        self, config_id: int, datos: Dict[str, Any]
    ) -> Tuple[bool, str, Optional[ConfiguracionesModel]]:
        """
        Actualizar una configuración existente

        Args:
            config_id: ID de la configuración a actualizar
            datos: Diccionario con los datos a actualizar

        Returns:
            Tuple (éxito, mensaje, configuración)
        """
        try:
            # Buscar configuración existente
            configuracion = ConfiguracionesModel.get_by_id(config_id)
            if not configuracion:
                return False, f"No se encontró configuración con ID {config_id}", None

            # Validar datos
            errores = self._validar_datos_configuracion(datos, es_actualizacion=True)
            if errores:
                return False, "Errores de validación: " + "; ".join(errores), None

            # Verificar unicidad de clave si se está actualizando
            if "clave" in datos and datos["clave"] != configuracion.clave:
                existente = ConfiguracionesModel.get_by_key(datos["clave"])
                if existente and existente.id != config_id:
                    return (
                        False,
                        f"Ya existe otra configuración con la clave '{datos['clave']}'",
                        None,
                    )

            # Actualizar atributos de la configuración
            for key, value in datos.items():
                if hasattr(configuracion, key):
                    setattr(configuracion, key, value)

            # Actualizar timestamp
            configuracion.updated_at = datetime.now()

            # Guardar cambios
            if configuracion.save():
                # Actualizar cache
                self._cache[configuracion.clave] = configuracion
                mensaje = (
                    f"Configuración '{configuracion.clave}' actualizada exitosamente"
                )
                return True, mensaje, configuracion
            else:
                return False, "Error al guardar los cambios", None

        except Exception as e:
            logger.error(f"Error al actualizar configuración {config_id}: {e}")
            return False, f"Error interno: {str(e)}", None

    def eliminar_configuracion(self, config_id: int) -> Tuple[bool, str]:
        """
        Eliminar una configuración

        Args:
            config_id: ID de la configuración a eliminar

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            configuracion = ConfiguracionesModel.get_by_id(config_id)
            if not configuracion:
                return False, f"No se encontró configuración con ID {config_id}"

            clave = configuracion.clave

            # No permitir eliminar configuraciones predefinidas críticas
            if clave in self._obtener_claves_criticas():
                return (
                    False,
                    f"No se puede eliminar la configuración predefinida '{clave}'",
                )

            if configuracion.delete():
                # Limpiar cache
                if clave in self._cache:
                    del self._cache[clave]
                return True, f"Configuración '{clave}' eliminada exitosamente"
            else:
                return False, "Error al eliminar la configuración"

        except Exception as e:
            logger.error(f"Error al eliminar configuración {config_id}: {e}")
            return False, f"Error interno: {str(e)}"

    # ==================== CONSULTAS ====================

    def obtener_configuracion(self, config_id: int) -> Optional[ConfiguracionesModel]:
        """
        Obtener una configuración por su ID

        Args:
            config_id: ID de la configuración

        Returns:
            ConfiguracionesModel o None si no se encuentra
        """
        try:
            return ConfiguracionesModel.get_by_id(config_id)
        except Exception as e:
            logger.error(f"Error al obtener configuración {config_id}: {e}")
            return None

    def obtener_configuracion_por_clave(
        self, clave: str, usar_cache: bool = True
    ) -> Optional[ConfiguracionesModel]:
        """
        Obtener configuración por clave

        Args:
            clave: Clave de la configuración
            usar_cache: Si True, usa cache para mejorar rendimiento

        Returns:
            ConfiguracionesModel o None si no se encuentra
        """
        try:
            # Verificar cache primero si está habilitado
            if usar_cache and clave in self._cache:
                return self._cache[clave]

            config = ConfiguracionesModel.get_by_key(clave)
            if config and usar_cache:
                self._cache[clave] = config

            return config
        except Exception as e:
            logger.error(f"Error al obtener configuración por clave '{clave}': {e}")
            return None

    def obtener_valor_configuracion(
        self, clave: str, valor_default: Any = None, tipo: Type[T] = str
    ) -> Union[T, Any]:
        """
        Obtener el valor de una configuración con tipo específico

        Args:
            clave: Clave de la configuración
            valor_default: Valor por defecto si no existe
            tipo: Tipo de dato esperado (str, int, float, bool, Decimal, list, dict)

        Returns:
            Valor de la configuración con el tipo especificado
        """
        try:
            config = self.obtener_configuracion_por_clave(clave)
            if not config or not config.valor:
                return valor_default

            valor = config.valor

            # Intentar deserializar JSON si el tipo es complejo
            if tipo in [list, dict] and isinstance(valor, str):
                try:
                    valor_deserializado = json.loads(valor)
                    if isinstance(valor_deserializado, tipo):
                        return valor_deserializado
                except (json.JSONDecodeError, TypeError):
                    pass

            # Convertir al tipo especificado
            if tipo == bool:
                if isinstance(valor, str):
                    valor_lower = valor.lower()
                    return valor_lower in ("true", "1", "yes", "si", "sí", "verdadero")
                return bool(valor)
            elif tipo == int:
                try:
                    return int(float(valor))
                except (ValueError, TypeError):
                    return valor_default
            elif tipo == float:
                try:
                    return float(valor)
                except (ValueError, TypeError):
                    return valor_default
            elif tipo == Decimal:
                try:
                    return Decimal(str(valor))
                except (ValueError, TypeError):
                    return valor_default
            elif tipo == list and isinstance(valor, str):
                # Intentar parsear lista separada por comas
                return [item.strip() for item in valor.split(",") if item.strip()]
            elif tipo == dict and isinstance(valor, str):
                # Intentar parsear diccionario simple (clave=valor)
                resultado = {}
                for item in valor.split(","):
                    if "=" in item:
                        k, v = item.split("=", 1)
                        resultado[k.strip()] = v.strip()
                return resultado if resultado else valor_default
            else:
                return tipo(valor) if valor else valor_default

        except Exception as e:
            logger.error(f"Error al obtener valor de configuración '{clave}': {e}")
            return valor_default

    def establecer_valor_configuracion(
        self,
        clave: str,
        valor: Any,
        descripcion: str = None,
        crear_si_no_existe: bool = True,
    ) -> Tuple[bool, str, Optional[ConfiguracionesModel]]:
        """
        Establecer el valor de una configuración

        Args:
            clave: Clave de la configuración
            valor: Valor a establecer
            descripcion: Descripción (solo se usa si se crea nueva)
            crear_si_no_existe: Si True, crea la configuración si no existe

        Returns:
            Tuple (éxito, mensaje, configuración)
        """
        try:
            # Buscar configuración existente
            configuracion = self.obtener_configuracion_por_clave(
                clave, usar_cache=False
            )

            if configuracion:
                # Actualizar configuración existente
                datos = {"valor": self._serializar_valor(valor)}
                return self.actualizar_configuracion(configuracion.id, datos)
            elif crear_si_no_existe:
                # Crear nueva configuración
                datos = {
                    "clave": clave,
                    "valor": self._serializar_valor(valor),
                    "descripcion": descripcion or f"Configuración para {clave}",
                }
                return self.crear_configuracion(datos)
            else:
                return False, f"No existe configuración con clave '{clave}'", None

        except Exception as e:
            logger.error(f"Error al establecer valor de configuración '{clave}': {e}")
            return False, f"Error interno: {str(e)}", None

    def obtener_todas_configuraciones(
        self, ordenar_por: str = "clave", orden_asc: bool = True
    ) -> List[ConfiguracionesModel]:
        """
        Obtener todas las configuraciones

        Args:
            ordenar_por: Campo para ordenar ('clave', 'created_at', 'updated_at')
            orden_asc: Orden ascendente (True) o descendente (False)

        Returns:
            Lista de configuraciones
        """
        try:
            # Validar campo de orden
            campos_validos = ["clave", "created_at", "updated_at"]
            if ordenar_por not in campos_validos:
                ordenar_por = "clave"

            orden = "ASC" if orden_asc else "DESC"
            query = f"SELECT * FROM configuraciones ORDER BY {ordenar_por} {orden}"

            configuraciones = ConfiguracionesModel.query(query)
            return (
                [ConfiguracionesModel(**config) for config in configuraciones]
                if configuraciones
                else []
            )

        except Exception as e:
            logger.error(f"Error al obtener todas las configuraciones: {e}")
            return []

    def obtener_configuraciones_por_grupo(
        self, prefijo: str
    ) -> List[ConfiguracionesModel]:
        """
        Obtener configuraciones por prefijo (grupo)

        Args:
            prefijo: Prefijo del grupo (ej: 'EMPRESA_', 'SISTEMA_')

        Returns:
            Lista de configuraciones del grupo
        """
        try:
            configuraciones = ConfiguracionesModel.get_by_prefix(prefijo)
            return configuraciones
        except Exception as e:
            logger.error(f"Error al obtener configuraciones del grupo '{prefijo}': {e}")
            return []

    def buscar_configuraciones(
        self, texto: str, buscar_en: List[str] = None
    ) -> List[ConfiguracionesModel]:
        """
        Buscar configuraciones por texto

        Args:
            texto: Texto a buscar
            buscar_en: Campos donde buscar (None = clave y descripción)

        Returns:
            Lista de configuraciones que coinciden
        """
        try:
            if not texto:
                return []

            if buscar_en is None:
                buscar_en = ["clave", "descripcion", "valor"]

            # Construir condiciones de búsqueda
            condiciones = []
            parametros = []

            for campo in buscar_en:
                condiciones.append(f"{campo} LIKE ?")
                parametros.append(f"%{texto}%")

            where_clause = "WHERE " + " OR ".join(condiciones)
            query = f"""
                SELECT * FROM configuraciones 
                {where_clause}
                ORDER BY clave
                LIMIT 100
            """

            configuraciones = ConfiguracionesModel.query(query, parametros)
            return (
                [ConfiguracionesModel(**config) for config in configuraciones]
                if configuraciones
                else []
            )

        except Exception as e:
            logger.error(f"Error al buscar configuraciones ({texto}): {e}")
            return []

    # ==================== OPERACIONES ESPECÍFICAS ====================

    def inicializar_configuraciones_predeterminadas(
        self,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Inicializar configuraciones predeterminadas del sistema

        Returns:
            Tuple (éxito, mensaje, resultados)
        """
        try:
            resultados = {
                "creadas": 0,
                "actualizadas": 0,
                "omitidas": 0,
                "errores": 0,
                "detalles": [],
            }

            # Configuraciones predeterminadas
            configuraciones_predeterminadas = {
                # Configuraciones generales
                "EMPRESA_NOMBRE": ("FormaGestPro Academy", "Nombre de la institución"),
                "EMPRESA_DIRECCION": (
                    "Av. Principal #123, Ciudad",
                    "Dirección de la institución",
                ),
                "EMPRESA_TELEFONO": ("+591 77712345", "Teléfono de contacto"),
                "EMPRESA_EMAIL": ("info@formagestpro.edu.bo", "Email de contacto"),
                # Configuraciones del sistema
                "SISTEMA_MONEDA": ("Bs.", "Símbolo de moneda local"),
                "SISTEMA_PAIS": ("Bolivia", "País donde opera el sistema"),
                "SISTEMA_IDIOMA": ("es", "Idioma del sistema (es, en)"),
                "SISTEMA_ZONA_HORARIA": ("America/La_Paz", "Zona horaria"),
                "SISTEMA_FORMATO_FECHA": ("DD/MM/YYYY", "Formato de fecha por defecto"),
                # Configuraciones académicas
                "ACADEMICO_CUOTA_DEFAULT": (
                    "1500.00",
                    "Valor por defecto de cuotas (Bs.)",
                ),
                "ACADEMICO_HONORARIO_DEFAULT": (
                    "50.00",
                    "Honorario por hora por defecto (Bs.)",
                ),
                "ACADEMICO_DIAS_MAX_PAGO": ("30", "Días máximos para realizar pagos"),
                "ACADEMICO_TASA_MORA": ("0.5", "Tasa de mora por día de retraso (%)"),
                # Configuraciones de notificaciones
                "NOTIFICACION_EMAIL_ENABLED": (
                    "0",
                    "Habilitar notificaciones por email (0=No, 1=Sí)",
                ),
                # Configuraciones de seguridad
                "SEGURIDAD_INTENTOS_LOGIN": ("3", "Intentos máximos de login fallidos"),
                "SEGURIDAD_TIEMPO_BLOQUEO": ("30", "Tiempo de bloqueo en minutos"),
                "SEGURIDAD_PASSWORD_MIN_LENGTH": ("8", "Longitud mínima de contraseña"),
                # Configuraciones de backup
                "BACKUP_AUTO_ENABLED": (
                    "1",
                    "Backup automático habilitado (0=No, 1=Sí)",
                ),
                "BACKUP_AUTO_HORA": ("02:00", "Hora para backup automático (HH:MM)"),
                "BACKUP_RETENCION_DIAS": ("30", "Días de retención de backups"),
                # Configuraciones de reportes
                "REPORTE_FOOTER_TEXT": (
                    "FormaGestPro - Sistema de Gestión Académica",
                    "Texto del pie de página en reportes",
                ),
            }

            for clave, (valor, descripcion) in configuraciones_predeterminadas.items():
                try:
                    # Verificar si ya existe
                    config_existente = self.obtener_configuracion_por_clave(
                        clave, usar_cache=False
                    )

                    if config_existente:
                        # Actualizar solo si el valor es diferente
                        if config_existente.valor != valor:
                            datos = {"valor": valor}
                            exito, mensaje, _ = self.actualizar_configuracion(
                                config_existente.id, datos
                            )
                            if exito:
                                resultados["actualizadas"] += 1
                                resultados["detalles"].append(f"Actualizada: {clave}")
                            else:
                                resultados["errores"] += 1
                                resultados["detalles"].append(
                                    f"Error actualizando {clave}: {mensaje}"
                                )
                        else:
                            resultados["omitidas"] += 1
                    else:
                        # Crear nueva configuración
                        datos = {
                            "clave": clave,
                            "valor": valor,
                            "descripcion": descripcion,
                        }
                        exito, mensaje, _ = self.crear_configuracion(datos)
                        if exito:
                            resultados["creadas"] += 1
                            resultados["detalles"].append(f"Creada: {clave}")
                        else:
                            resultados["errores"] += 1
                            resultados["detalles"].append(
                                f"Error creando {clave}: {mensaje}"
                            )

                except Exception as e:
                    logger.error(f"Error al procesar configuración {clave}: {e}")
                    resultados["errores"] += 1
                    resultados["detalles"].append(f"Error procesando {clave}: {str(e)}")

            # Limpiar cache después de la inicialización
            self._cache.clear()

            # Determinar mensaje final
            if resultados["errores"] == 0:
                mensaje_final = f"Inicialización completada: {resultados['creadas']} creadas, {resultados['actualizadas']} actualizadas, {resultados['omitidas']} omitidas"
            else:
                mensaje_final = f"Inicialización con errores: {resultados['creadas']} creadas, {resultados['actualizadas']} actualizadas, {resultados['omitidas']} omitidas, {resultados['errores']} errores"

            return True, mensaje_final, resultados

        except Exception as e:
            logger.error(f"Error al inicializar configuraciones predeterminadas: {e}")
            return False, f"Error al inicializar configuraciones: {str(e)}", {}

    def obtener_configuracion_empresa(self) -> Dict[str, Any]:
        """
        Obtener todas las configuraciones relacionadas con la empresa

        Returns:
            Diccionario con configuraciones de la empresa
        """
        try:
            configuraciones = self.obtener_configuraciones_por_grupo("EMPRESA_")

            empresa_config = {}
            for config in configuraciones:
                clave_sin_prefijo = config.clave.replace("EMPRESA_", "").lower()
                empresa_config[clave_sin_prefijo] = config.valor

            return empresa_config

        except Exception as e:
            logger.error(f"Error al obtener configuración de empresa: {e}")
            return {}

    def obtener_configuracion_sistema(self) -> Dict[str, Any]:
        """
        Obtener todas las configuraciones del sistema

        Returns:
            Diccionario con configuraciones del sistema
        """
        try:
            grupos = [
                "SISTEMA_",
                "ACADEMICO_",
                "NOTIFICACION_",
                "SEGURIDAD_",
                "BACKUP_",
                "REPORTE_",
            ]

            sistema_config = {}
            for grupo in grupos:
                configuraciones = self.obtener_configuraciones_por_grupo(grupo)
                for config in configuraciones:
                    clave_sin_prefijo = config.clave
                    for prefijo in grupos:
                        if config.clave.startswith(prefijo):
                            clave_sin_prefijo = config.clave.replace(prefijo, "")
                            break
                    clave_formateada = clave_sin_prefijo.lower()
                    sistema_config[clave_formateada] = config.valor

            return sistema_config

        except Exception as e:
            logger.error(f"Error al obtener configuración del sistema: {e}")
            return {}

    def limpiar_cache(self) -> None:
        """Limpiar cache de configuraciones"""
        self._cache.clear()

    # ==================== VALIDACIONES ====================

    def _validar_datos_configuracion(
        self, datos: Dict[str, Any], es_actualizacion: bool = False
    ) -> List[str]:
        """
        Validar datos de configuración

        Args:
            datos: Diccionario con datos a validar
            es_actualizacion: Si es una actualización (algunos campos son opcionales)

        Returns:
            Lista de mensajes de error
        """
        errores = []

        # Validar campos requeridos (solo para creación)
        if not es_actualizacion:
            campos_requeridos = ["clave"]
            for campo in campos_requeridos:
                if campo not in datos or not str(datos.get(campo, "")).strip():
                    errores.append(f"El campo '{campo}' es requerido")

        # Validar clave
        if "clave" in datos and datos["clave"]:
            clave = str(datos["clave"]).strip()
            if len(clave) < 2:
                errores.append("La clave debe tener al menos 2 caracteres")
            if len(clave) > 100:
                errores.append("La clave no puede exceder 100 caracteres")
            if " " in clave:
                errores.append("La clave no puede contener espacios")
            if not clave.isupper() and "_" in clave:
                # Sugerir formato si parece ser una constante
                errores.append(
                    "La clave debe estar en mayúsculas para configuraciones predefinidas"
                )

        # Validar valor si se proporciona
        if "valor" in datos and datos["valor"] is not None:
            valor = datos["valor"]
            if isinstance(valor, str) and len(valor) > 1000:
                errores.append("El valor no puede exceder 1000 caracteres")

        # Validar descripción si se proporciona
        if "descripcion" in datos and datos["descripcion"]:
            descripcion = str(datos["descripcion"]).strip()
            if len(descripcion) > 500:
                errores.append("La descripción no puede exceder 500 caracteres")

        return errores

    def _serializar_valor(self, valor: Any) -> str:
        """
        Serializar valor para almacenamiento en base de datos

        Args:
            valor: Valor a serializar

        Returns:
            Valor serializado como string
        """
        if valor is None:
            return ""
        elif isinstance(valor, (list, dict, tuple, set)):
            try:
                return json.dumps(valor, ensure_ascii=False)
            except (TypeError, ValueError):
                return str(valor)
        else:
            return str(valor)

    def _obtener_claves_criticas(self) -> List[str]:
        """
        Obtener lista de claves de configuración críticas que no deben eliminarse

        Returns:
            Lista de claves críticas
        """
        return [
            "EMPRESA_NOMBRE",
            "SISTEMA_MONEDA",
            "SISTEMA_IDIOMA",
            "SISTEMA_FORMATO_FECHA",
            "ACADEMICO_CUOTA_DEFAULT",
            "SEGURIDAD_PASSWORD_MIN_LENGTH",
        ]

    # ==================== BACKUP Y RESTAURACIÓN ====================

    def exportar_configuraciones_a_json(
        self, archivo_salida: str = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Exportar todas las configuraciones a archivo JSON

        Args:
            archivo_salida: Ruta del archivo de salida

        Returns:
            Tuple (éxito, mensaje, ruta_archivo)
        """
        try:
            # Obtener todas las configuraciones
            configuraciones = self.obtener_todas_configuraciones()

            if not configuraciones:
                return False, "No hay configuraciones para exportar", None

            # Preparar datos para exportación
            datos_exportacion = {
                "metadata": {
                    "sistema": "FormaGestPro_MVC",
                    "version": "2.0",
                    "fecha_exportacion": datetime.now().isoformat(),
                    "total_configuraciones": len(configuraciones),
                },
                "configuraciones": [],
            }

            for config in configuraciones:
                config_data = {
                    "clave": config.clave,
                    "valor": config.valor,
                    "descripcion": config.descripcion,
                    "created_at": (
                        config.created_at.isoformat()
                        if hasattr(config.created_at, "isoformat")
                        else str(config.created_at)
                    ),
                    "updated_at": (
                        config.updated_at.isoformat()
                        if hasattr(config.updated_at, "isoformat")
                        else str(config.updated_at)
                    ),
                }
                datos_exportacion["configuraciones"].append(config_data)

            # Generar nombre de archivo si no se proporciona
            if not archivo_salida:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archivo_salida = f"configuraciones_backup_{timestamp}.json"

            # Asegurar extensión .json
            if not archivo_salida.lower().endswith(".json"):
                archivo_salida += ".json"

            # Crear directorio si no existe
            archivo_path = Path(archivo_salida)
            archivo_path.parent.mkdir(parents=True, exist_ok=True)

            # Escribir JSON
            with open(archivo_path, "w", encoding="utf-8") as f:
                json.dump(datos_exportacion, f, indent=2, ensure_ascii=False)

            mensaje = (
                f"Exportadas {len(configuraciones)} configuraciones a {archivo_path}"
            )
            return True, mensaje, str(archivo_path)

        except Exception as e:
            logger.error(f"Error al exportar configuraciones a JSON: {e}")
            return False, f"Error al exportar: {str(e)}", None

    def importar_configuraciones_desde_json(
        self, archivo_entrada: str
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Importar configuraciones desde archivo JSON

        Args:
            archivo_entrada: Ruta del archivo de entrada

        Returns:
            Tuple (éxito, mensaje, resultados)
        """
        try:
            # Verificar que el archivo exista
            archivo_path = Path(archivo_entrada)
            if not archivo_path.exists():
                return False, f"El archivo no existe: {archivo_entrada}", {}

            # Leer JSON
            with open(archivo_path, "r", encoding="utf-8") as f:
                datos_importacion = json.load(f)

            # Validar estructura
            if "configuraciones" not in datos_importacion:
                return (
                    False,
                    "Formato de archivo inválido: falta sección 'configuraciones'",
                    {},
                )

            configuraciones = datos_importacion["configuraciones"]
            if not isinstance(configuraciones, list):
                return (
                    False,
                    "Formato de archivo inválido: 'configuraciones' debe ser una lista",
                    {},
                )

            resultados = {
                "importadas": 0,
                "actualizadas": 0,
                "omitidas": 0,
                "errores": 0,
                "detalles": [],
            }

            for config_data in configuraciones:
                try:
                    # Validar datos mínimos
                    if "clave" not in config_data:
                        resultados["errores"] += 1
                        resultados["detalles"].append(f"Error: configuración sin clave")
                        continue

                    clave = config_data["clave"]
                    valor = config_data.get("valor", "")
                    descripcion = config_data.get(
                        "descripcion", f"Importada desde backup - {clave}"
                    )

                    # Verificar si ya existe
                    config_existente = self.obtener_configuracion_por_clave(
                        clave, usar_cache=False
                    )

                    if config_existente:
                        # Actualizar si el valor es diferente
                        if config_existente.valor != valor:
                            datos = {"valor": valor}
                            exito, mensaje, _ = self.actualizar_configuracion(
                                config_existente.id, datos
                            )
                            if exito:
                                resultados["actualizadas"] += 1
                                resultados["detalles"].append(f"Actualizada: {clave}")
                            else:
                                resultados["errores"] += 1
                                resultados["detalles"].append(
                                    f"Error actualizando {clave}: {mensaje}"
                                )
                        else:
                            resultados["omitidas"] += 1
                    else:
                        # Crear nueva configuración
                        datos = {
                            "clave": clave,
                            "valor": valor,
                            "descripcion": descripcion,
                        }
                        exito, mensaje, _ = self.crear_configuracion(datos)
                        if exito:
                            resultados["importadas"] += 1
                            resultados["detalles"].append(f"Importada: {clave}")
                        else:
                            resultados["errores"] += 1
                            resultados["detalles"].append(
                                f"Error importando {clave}: {mensaje}"
                            )

                except Exception as e:
                    logger.error(
                        f"Error al procesar configuración {config_data.get('clave', 'DESCONOCIDA')}: {e}"
                    )
                    resultados["errores"] += 1
                    resultados["detalles"].append(
                        f"Error procesando configuración: {str(e)}"
                    )

            # Limpiar cache después de la importación
            self._cache.clear()

            # Determinar mensaje final
            if resultados["errores"] == 0:
                mensaje_final = f"Importación completada: {resultados['importadas']} importadas, {resultados['actualizadas']} actualizadas, {resultados['omitidas']} omitidas"
            else:
                mensaje_final = f"Importación con errores: {resultados['importadas']} importadas, {resultados['actualizadas']} actualizadas, {resultados['omitidas']} omitidas, {resultados['errores']} errores"

            return True, mensaje_final, resultados

        except json.JSONDecodeError as e:
            return False, f"Error al decodificar JSON: {str(e)}", {}
        except Exception as e:
            logger.error(f"Error al importar configuraciones desde JSON: {e}")
            return False, f"Error al importar: {str(e)}", {}
