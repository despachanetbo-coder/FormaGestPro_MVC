# app/models/comprobantes_adjuntos_model.py - Gestión robusta de comprobantes adjuntos
import sys
import os
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple, Union

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_model import BaseModel


class ComprobantesAdjuntosModel(BaseModel):
    def __init__(self):
        """Inicializa el modelo de comprobantes adjuntos"""
        super().__init__()
        self.table_name = "comprobantes_adjuntos"
        self.sequence_name = "seq_comprobantes_adjuntos_id"

        # Tipos enumerados según la base de datos
        self.TIPOS_ORIGEN = ["INGRESO", "GASTO"]
        self.TIPOS_DOCUMENTO = [
            "FACTURA",
            "RECIBO",
            "BOLETA",
            "NOTA_CREDITO",
            "NOTA_DEBITO",
            "COMPROBANTE_BANCARIO",
            "CONTRATO",
            "OTRO",
        ]
        self.EXTENSIONES_VALIDAS = [
            "PDF",
            "JPG",
            "JPEG",
            "PNG",
            "TIF",
            "TIFF",
            "DOC",
            "DOCX",
            "XLS",
            "XLSX",
        ]

        # Configuración de almacenamiento
        self.BASE_UPLOAD_DIR = "uploads/comprobantes"
        self.MAX_FILE_SIZE_MB = 10  # Tamaño máximo por archivo
        self.ALLOWED_MIME_TYPES = [
            "application/pdf",
            "image/jpeg",
            "image/png",
            "image/tiff",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ]

        # Columnas de la tabla para validación
        self.columns = [
            "id",
            "origen_tipo",
            "origen_id",
            "tipo_documento",
            "ruta_archivo",
            "nombre_original",
            "extension",
            "subido_por",
            "fecha_subida",
        ]

        # Columnas requeridas
        self.required_columns = [
            "origen_tipo",
            "origen_id",
            "tipo_documento",
            "ruta_archivo",
        ]

        # Mapeo de extensiones a MIME types
        self.EXTENSION_MIME_MAP = {
            "PDF": "application/pdf",
            "JPG": "image/jpeg",
            "JPEG": "image/jpeg",
            "PNG": "image/png",
            "TIF": "image/tiff",
            "TIFF": "image/tiff",
            "DOC": "application/msword",
            "DOCX": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "XLS": "application/vnd.ms-excel",
            "XLSX": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }

        # Asegurar directorio base
        self._ensure_upload_directory()

    # ============ MÉTODOS DE INICIALIZACIÓN Y CONFIGURACIÓN ============

    def _ensure_upload_directory(self):
        """Asegura que exista el directorio de uploads"""
        try:
            upload_path = Path(self.BASE_UPLOAD_DIR)
            upload_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Directorio de uploads listo: {upload_path.absolute()}")
        except Exception as e:
            print(f"✗ Error creando directorio de uploads: {e}")

    def _get_upload_path(
        self, origen_tipo: str, origen_id: int, tipo_documento: str, filename: str
    ) -> Tuple[str, str]:
        """
        Genera la ruta de almacenamiento para un archivo

        Args:
            origen_tipo: Tipo de origen (INGRESO/GASTO)
            origen_id: ID del origen
            tipo_documento: Tipo de documento
            filename: Nombre original del archivo

        Returns:
            Tuple[str, str]: (ruta_relativa, nombre_archivo_generado)
        """
        try:
            # Generar nombre único para el archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = Path(filename).suffix.lower()
            safe_filename = f"{origen_tipo.lower()}_{origen_id}_{tipo_documento.lower()}_{timestamp}{file_extension}"

            # Crear estructura de directorios
            year_month = datetime.now().strftime("%Y/%m")
            relative_path = (
                f"{self.BASE_UPLOAD_DIR}/{origen_tipo.lower()}/{origen_id}/{year_month}"
            )

            # Crear directorios si no existen
            full_path = Path(relative_path)
            full_path.mkdir(parents=True, exist_ok=True)

            # Ruta completa del archivo
            file_path = full_path / safe_filename

            return str(file_path.relative_to(self.BASE_UPLOAD_DIR)), safe_filename

        except Exception as e:
            print(f"✗ Error generando ruta de upload: {e}")
            return "", ""

    def _get_extension_from_filename(self, filename: str) -> Optional[str]:
        """
        Obtiene la extensión válida desde el nombre del archivo

        Args:
            filename: Nombre del archivo

        Returns:
            Optional[str]: Extensión en formato válido o None
        """
        try:
            extension = Path(filename).suffix.upper().replace(".", "")

            # Normalizar extensiones comunes
            if extension == "JPG":
                return "JPEG"
            elif extension == "TIF":
                return "TIFF"

            return extension if extension in self.EXTENSIONES_VALIDAS else None

        except Exception as e:
            print(f"✗ Error obteniendo extensión: {e}")
            return None

    # ============ MÉTODOS DE VALIDACIÓN ============

    def _validate_comprobante_data(
        self, data: Dict[str, Any], for_update: bool = False
    ) -> Tuple[bool, str]:
        """
        Valida los datos del comprobante adjunto

        Args:
            data: Diccionario con datos del comprobante
            for_update: Si es True, valida para actualización

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        # Campos requeridos para creación
        if not for_update:
            for field in self.required_columns:
                if field not in data or not data[field]:
                    return False, f"Campo requerido faltante: {field}"

        # Validar tipo de origen
        if "origen_tipo" in data and data["origen_tipo"]:
            if data["origen_tipo"] not in self.TIPOS_ORIGEN:
                return (
                    False,
                    f"Tipo de origen inválido. Use: {', '.join(self.TIPOS_ORIGEN)}",
                )

        # Validar tipo de documento
        if "tipo_documento" in data and data["tipo_documento"]:
            if data["tipo_documento"] not in self.TIPOS_DOCUMENTO:
                return (
                    False,
                    f"Tipo de documento inválido. Use: {', '.join(self.TIPOS_DOCUMENTO)}",
                )

        # Validar extensión si se proporciona
        if "extension" in data and data["extension"]:
            if data["extension"] not in self.EXTENSIONES_VALIDAS:
                return (
                    False,
                    f"Extensión inválida. Use: {', '.join(self.EXTENSIONES_VALIDAS)}",
                )

        # Validar unicidad por origen y tipo de documento
        if (
            "origen_tipo" in data
            and data["origen_tipo"]
            and "origen_id" in data
            and data["origen_id"]
            and "tipo_documento" in data
            and data["tipo_documento"]
        ):

            existing_id = None
            if for_update and "id" in data:
                existing_id = data["id"]

            if self.comprobante_exists(
                data["origen_tipo"],
                data["origen_id"],
                data["tipo_documento"],
                exclude_id=existing_id,
            ):
                return (
                    False,
                    f"Ya existe un comprobante del tipo {data['tipo_documento']} para este {data['origen_tipo']}",
                )

        # Validar usuario que sube si se proporciona
        if "subido_por" in data and data["subido_por"]:
            if not self._usuario_exists(data["subido_por"]):
                return False, f"Usuario con ID {data['subido_por']} no existe"

        # Validar ruta de archivo
        if "ruta_archivo" in data and data["ruta_archivo"]:
            # Verificar que la ruta sea relativa y segura
            ruta = data["ruta_archivo"]
            if ruta.startswith("/") or ".." in ruta or ruta.startswith("http"):
                return False, "Ruta de archivo inválida o insegura"

        return True, "Datos válidos"

    def _validate_file(
        self, file_path: str, file_size: int, mime_type: str
    ) -> Tuple[bool, str]:
        """
        Valida un archivo antes de guardarlo

        Args:
            file_path: Ruta del archivo
            file_size: Tamaño del archivo en bytes
            mime_type: Tipo MIME del archivo

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        # Validar tamaño
        max_size_bytes = self.MAX_FILE_SIZE_MB * 1024 * 1024
        if file_size > max_size_bytes:
            return (
                False,
                f"El archivo excede el tamaño máximo de {self.MAX_FILE_SIZE_MB}MB",
            )

        # Validar tipo MIME
        if mime_type not in self.ALLOWED_MIME_TYPES:
            return False, f"Tipo de archivo no permitido: {mime_type}"

        # Validar extensión
        file_extension = Path(file_path).suffix.upper().replace(".", "")
        if not self._get_extension_from_filename(file_path):
            return False, f"Extensión de archivo no permitida: {file_extension}"

        return True, "Archivo válido"

    def _usuario_exists(self, usuario_id: int) -> bool:
        """Verifica si el usuario existe"""
        try:
            query = (
                "SELECT COUNT(*) as count FROM usuarios WHERE id = %s AND activo = TRUE"
            )
            result = self.fetch_one(query, (usuario_id,))
            return result["count"] > 0 if result else False
        except:
            return False

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza los datos del comprobante

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
                # Mantener otros tipos
                else:
                    sanitized[key] = value

        return sanitized

    # ============ MÉTODOS CRUD PRINCIPALES ============

    def create(
        self,
        data: Dict[str, Any],
        usuario_id: Optional[int] = None,
        file_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[int]:
        """
        Crea un nuevo comprobante adjunto

        Args:
            data: Diccionario con datos del comprobante
            usuario_id: ID del usuario que sube el archivo
            file_data: Datos del archivo (opcional para manejo directo)

        Returns:
            Optional[int]: ID del comprobante creado o None si hay error
        """
        # Sanitizar datos
        data = self._sanitize_data(data)

        # Añadir usuario que sube si se proporciona
        if usuario_id:
            data["subido_por"] = usuario_id

        # Procesar archivo si se proporciona
        if file_data and "filename" in file_data:
            # Generar ruta de almacenamiento
            ruta_relativa, nombre_archivo = self._get_upload_path(
                data.get("origen_tipo", ""),
                data.get("origen_id", 0),
                data.get("tipo_documento", ""),
                file_data["filename"],
            )

            if not ruta_relativa:
                return None

            data["ruta_archivo"] = ruta_relativa
            data["nombre_original"] = file_data["filename"]

            # Determinar extensión
            extension = self._get_extension_from_filename(file_data["filename"])
            if extension:
                data["extension"] = extension

        # Validar datos
        is_valid, error_msg = self._validate_comprobante_data(data, for_update=False)

        if not is_valid:
            print(f"✗ Error validando datos: {error_msg}")
            return None

        try:
            # Preparar datos para inserción
            insert_data = data.copy()

            # Establecer valores por defecto
            defaults = {"fecha_subida": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

            for key, value in defaults.items():
                if key not in insert_data or insert_data[key] is None:
                    insert_data[key] = value

            # Insertar en base de datos
            result = self.insert(self.table_name, insert_data, returning="id")

            if result:
                print(f"✓ Comprobante adjunto creado exitosamente con ID: {result}")
                return result

            return None

        except Exception as e:
            print(f"✗ Error creando comprobante adjunto: {e}")
            return None

    def read(self, comprobante_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un comprobante adjunto por su ID

        Args:
            comprobante_id: ID del comprobante

        Returns:
            Optional[Dict]: Datos del comprobante o None si no existe
        """
        try:
            query = f"""
            SELECT ca.*,
                   u.username as subido_por_usuario,
                   u.nombre_completo as subido_por_nombre
            FROM {self.table_name} ca
            LEFT JOIN usuarios u ON ca.subido_por = u.id
            WHERE ca.id = %s
            """

            result = self.fetch_one(query, (comprobante_id,))
            return result

        except Exception as e:
            print(f"✗ Error obteniendo comprobante adjunto: {e}")
            return None

    def update(self, comprobante_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un comprobante adjunto existente

        Args:
            comprobante_id: ID del comprobante a actualizar
            data: Diccionario con datos a actualizar

        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        if not data:
            return False

        # Obtener datos actuales para validación
        comprobante_actual = self.read(comprobante_id)
        if not comprobante_actual:
            return False

        # Combinar datos actuales con los nuevos para validación
        data_with_id = {**comprobante_actual, **data}
        data_with_id["id"] = comprobante_id

        # Sanitizar y validar datos
        data = self._sanitize_data(data)
        is_valid, error_msg = self._validate_comprobante_data(
            data_with_id, for_update=True
        )

        if not is_valid:
            print(f"✗ Error validando datos: {error_msg}")
            return False

        try:
            # Actualizar en base de datos
            result = self.update_table(
                self.table_name, data, "id = %s", (comprobante_id,)
            )

            if result:
                print(
                    f"✓ Comprobante adjunto {comprobante_id} actualizado exitosamente"
                )
                return True

            return False

        except Exception as e:
            print(f"✗ Error actualizando comprobante adjunto: {e}")
            return False

    def delete(self, comprobante_id: int, delete_file: bool = True) -> bool:
        """
        Elimina un comprobante adjunto

        Args:
            comprobante_id: ID del comprobante
            delete_file: Si es True, elimina también el archivo físico

        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            # Obtener datos del comprobante para eliminar archivo
            comprobante = self.read(comprobante_id)
            if not comprobante:
                return False

            # Eliminar archivo físico si existe y se solicita
            if delete_file and comprobante.get("ruta_archivo"):
                self._delete_physical_file(comprobante["ruta_archivo"])

            query = f"DELETE FROM {self.table_name} WHERE id = %s"
            result = self.execute_query(query, (comprobante_id,), commit=True)

            if result:
                print(f"✓ Comprobante adjunto {comprobante_id} eliminado exitosamente")
                return True

            return False

        except Exception as e:
            print(f"✗ Error eliminando comprobante adjunto: {e}")
            return False

    # ============ MÉTODOS DE GESTIÓN DE ARCHIVOS ============

    def _delete_physical_file(self, ruta_relativa: str) -> bool:
        """
        Elimina un archivo físico del sistema

        Args:
            ruta_relativa: Ruta relativa del archivo

        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            file_path = Path(self.BASE_UPLOAD_DIR) / ruta_relativa

            if file_path.exists():
                file_path.unlink()
                print(f"✓ Archivo físico eliminado: {file_path}")
                return True

            print(f"⚠ Archivo no encontrado: {file_path}")
            return False

        except Exception as e:
            print(f"✗ Error eliminando archivo físico: {e}")
            return False

    def get_file_path(self, comprobante_id: int) -> Optional[Path]:
        """
        Obtiene la ruta física completa de un archivo

        Args:
            comprobante_id: ID del comprobante

        Returns:
            Optional[Path]: Ruta completa del archivo o None
        """
        try:
            comprobante = self.read(comprobante_id)
            if not comprobante or not comprobante.get("ruta_archivo"):
                return None

            file_path = Path(self.BASE_UPLOAD_DIR) / comprobante["ruta_archivo"]

            if file_path.exists():
                return file_path

            return None

        except Exception as e:
            print(f"✗ Error obteniendo ruta de archivo: {e}")
            return None

    def get_file_info(self, comprobante_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene información detallada de un archivo

        Args:
            comprobante_id: ID del comprobante

        Returns:
            Optional[Dict]: Información del archivo o None
        """
        try:
            comprobante = self.read(comprobante_id)
            if not comprobante:
                return None

            file_path = self.get_file_path(comprobante_id)
            if not file_path:
                return None

            # Obtener información del archivo
            file_info = {
                "id": comprobante["id"],
                "nombre_original": comprobante.get("nombre_original"),
                "ruta_relativa": comprobante["ruta_archivo"],
                "ruta_completa": str(file_path),
                "tipo_documento": comprobante["tipo_documento"],
                "extension": comprobante.get("extension"),
                "origen_tipo": comprobante["origen_tipo"],
                "origen_id": comprobante["origen_id"],
                "fecha_subida": comprobante["fecha_subida"],
                "subido_por": comprobante.get("subido_por"),
                "subido_por_nombre": comprobante.get("subido_por_nombre"),
                "exists": file_path.exists(),
                "size_bytes": file_path.stat().st_size if file_path.exists() else 0,
                "size_mb": (
                    round(file_path.stat().st_size / (1024 * 1024), 2)
                    if file_path.exists()
                    else 0
                ),
                "mime_type": self._get_mime_type(file_path),
            }

            return file_info

        except Exception as e:
            print(f"✗ Error obteniendo información de archivo: {e}")
            return None

    def _get_mime_type(self, file_path: Path) -> Optional[str]:
        """
        Obtiene el tipo MIME de un archivo

        Args:
            file_path: Ruta del archivo

        Returns:
            Optional[str]: Tipo MIME o None
        """
        try:
            # Usar mimetypes primero
            mime_type, _ = mimetypes.guess_type(str(file_path))

            if mime_type:
                return mime_type

            # Fallback basado en extensión
            if file_path.suffix.lower() == ".pdf":
                return "application/pdf"
            elif file_path.suffix.lower() in [".jpg", ".jpeg"]:
                return "image/jpeg"
            elif file_path.suffix.lower() == ".png":
                return "image/png"
            elif file_path.suffix.lower() in [".tif", ".tiff"]:
                return "image/tiff"

            return None

        except Exception as e:
            print(f"✗ Error obteniendo MIME type: {e}")
            return None

    # ============ MÉTODOS DE CONSULTA AVANZADOS ============

    def get_all(
        self,
        origen_tipo: Optional[str] = None,
        origen_id: Optional[int] = None,
        tipo_documento: Optional[str] = None,
        subido_por: Optional[int] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "fecha_subida",
        order_desc: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todos los comprobantes adjuntos

        Args:
            origen_tipo: Filtrar por tipo de origen
            origen_id: Filtrar por ID de origen
            tipo_documento: Filtrar por tipo de documento
            subido_por: Filtrar por usuario que subió
            fecha_desde: Fecha inicial (YYYY-MM-DD)
            fecha_hasta: Fecha final (YYYY-MM-DD)
            limit: Límite de registros
            offset: Desplazamiento para paginación
            order_by: Campo para ordenar
            order_desc: Si es True, orden descendente

        Returns:
            List[Dict]: Lista de comprobantes
        """
        try:
            query = f"""
            SELECT ca.*,
                   u.username as subido_por_usuario,
                   u.nombre_completo as subido_por_nombre
            FROM {self.table_name} ca
            LEFT JOIN usuarios u ON ca.subido_por = u.id
            """

            conditions = []
            params = []

            if origen_tipo is not None:
                conditions.append("ca.origen_tipo = %s")
                params.append(origen_tipo)

            if origen_id is not None:
                conditions.append("ca.origen_id = %s")
                params.append(origen_id)

            if tipo_documento is not None:
                conditions.append("ca.tipo_documento = %s")
                params.append(tipo_documento)

            if subido_por is not None:
                conditions.append("ca.subido_por = %s")
                params.append(subido_por)

            if fecha_desde is not None:
                conditions.append("DATE(ca.fecha_subida) >= %s")
                params.append(fecha_desde)

            if fecha_hasta is not None:
                conditions.append("DATE(ca.fecha_subida) <= %s")
                params.append(fecha_hasta)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            # Ordenar
            order_dir = "DESC" if order_desc else "ASC"
            query += f" ORDER BY ca.{order_by} {order_dir}"

            # Paginación
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            return self.fetch_all(query, params)

        except Exception as e:
            print(f"✗ Error obteniendo comprobantes adjuntos: {e}")
            return []

    def get_by_origen(self, origen_tipo: str, origen_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene comprobantes por origen

        Args:
            origen_tipo: Tipo de origen
            origen_id: ID del origen

        Returns:
            List[Dict]: Lista de comprobantes del origen
        """
        return self.get_all(origen_tipo=origen_tipo, origen_id=origen_id)

    def get_by_tipo_documento(self, tipo_documento: str) -> List[Dict[str, Any]]:
        """
        Obtiene comprobantes por tipo de documento

        Args:
            tipo_documento: Tipo de documento

        Returns:
            List[Dict]: Lista de comprobantes del tipo especificado
        """
        return self.get_all(tipo_documento=tipo_documento)

    def search(
        self,
        search_term: str,
        origen_tipo: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Busca comprobantes por término de búsqueda

        Args:
            search_term: Término a buscar
            origen_tipo: Filtrar por tipo de origen
            fecha_desde: Fecha inicial (YYYY-MM-DD)
            fecha_hasta: Fecha final (YYYY-MM-DD)

        Returns:
            List[Dict]: Lista de comprobantes que coinciden
        """
        try:
            query = f"""
            SELECT ca.*,
                   u.username as subido_por_usuario,
                   u.nombre_completo as subido_por_nombre
            FROM {self.table_name} ca
            LEFT JOIN usuarios u ON ca.subido_por = u.id
            WHERE (ca.nombre_original ILIKE %s 
                   OR ca.tipo_documento ILIKE %s)
            """

            params = [f"%{search_term}%", f"%{search_term}%"]

            if origen_tipo is not None:
                query += " AND ca.origen_tipo = %s"
                params.append(origen_tipo)

            if fecha_desde is not None:
                query += " AND DATE(ca.fecha_subida) >= %s"
                params.append(fecha_desde)

            if fecha_hasta is not None:
                query += " AND DATE(ca.fecha_subida) <= %s"
                params.append(fecha_hasta)

            query += " ORDER BY ca.fecha_subida DESC"

            return self.fetch_all(query, params)

        except Exception as e:
            print(f"✗ Error buscando comprobantes: {e}")
            return []

    # ============ MÉTODOS PARA GESTIÓN DE MÚLTIPLES COMPROBANTES ============

    def agregar_comprobantes(
        self,
        origen_tipo: str,
        origen_id: int,
        comprobantes: List[Dict[str, Any]],
        usuario_id: Optional[int] = None,
    ) -> List[int]:
        """
        Agrega múltiples comprobantes a un origen

        Args:
            origen_tipo: Tipo de origen (INGRESO/GASTO)
            origen_id: ID del origen
            comprobantes: Lista de diccionarios con datos de comprobantes
            usuario_id: ID del usuario que sube los archivos

        Returns:
            List[int]: Lista de IDs de comprobantes creados exitosamente
        """
        ids_creados = []

        for comprobante in comprobantes:
            # Asegurar datos básicos
            comprobante_data = comprobante.copy()
            comprobante_data["origen_tipo"] = origen_tipo
            comprobante_data["origen_id"] = origen_id

            # Crear comprobante
            comprobante_id = self.create(comprobante_data, usuario_id)
            if comprobante_id:
                ids_creados.append(comprobante_id)

        print(
            f"✓ Agregados {len(ids_creados)} comprobantes a {origen_tipo} {origen_id}"
        )
        return ids_creados

    def eliminar_comprobantes_por_origen(
        self, origen_tipo: str, origen_id: int, delete_files: bool = True
    ) -> int:
        """
        Elimina todos los comprobantes de un origen

        Args:
            origen_tipo: Tipo de origen
            origen_id: ID del origen
            delete_files: Si es True, elimina también los archivos físicos

        Returns:
            int: Número de comprobantes eliminados
        """
        try:
            # Obtener todos los comprobantes del origen
            comprobantes = self.get_by_origen(origen_tipo, origen_id)

            # Eliminar cada comprobante
            eliminados = 0
            for comprobante in comprobantes:
                if self.delete(comprobante["id"], delete_files):
                    eliminados += 1

            print(
                f"✓ Eliminados {eliminados} comprobantes de {origen_tipo} {origen_id}"
            )
            return eliminados

        except Exception as e:
            print(f"✗ Error eliminando comprobantes por origen: {e}")
            return 0

    # ============ MÉTODOS PARA DASHBOARD ============

    def get_total_comprobantes(
        self,
        origen_tipo: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
    ) -> int:
        """
        Obtiene el total de comprobantes

        Args:
            origen_tipo: Filtrar por tipo de origen
            fecha_desde: Fecha inicial (YYYY-MM-DD)
            fecha_hasta: Fecha final (YYYY-MM-DD)

        Returns:
            int: Número total de comprobantes
        """
        try:
            query = f"SELECT COUNT(*) as total FROM {self.table_name}"
            conditions = []
            params = []

            if origen_tipo is not None:
                conditions.append("origen_tipo = %s")
                params.append(origen_tipo)

            if fecha_desde is not None:
                conditions.append("DATE(fecha_subida) >= %s")
                params.append(fecha_desde)

            if fecha_hasta is not None:
                conditions.append("DATE(fecha_subida) <= %s")
                params.append(fecha_hasta)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            result = self.fetch_one(query, params)
            return result["total"] if result else 0

        except Exception as e:
            print(f"✗ Error obteniendo total de comprobantes: {e}")
            return 0

    def get_comprobantes_por_tipo_documento(self) -> List[Dict[str, Any]]:
        """
        Obtiene distribución de comprobantes por tipo de documento

        Returns:
            List[Dict]: Distribución por tipo de documento
        """
        try:
            query = """
            SELECT 
                tipo_documento,
                COUNT(*) as cantidad,
                COUNT(DISTINCT origen_id) as origenes_unicos
            FROM comprobantes_adjuntos
            GROUP BY tipo_documento
            ORDER BY cantidad DESC
            """

            return self.fetch_all(query)

        except Exception as e:
            print(f"✗ Error obteniendo comprobantes por tipo de documento: {e}")
            return []

    def get_comprobantes_por_origen_tipo(self) -> List[Dict[str, Any]]:
        """
        Obtiene distribución de comprobantes por tipo de origen

        Returns:
            List[Dict]: Distribución por tipo de origen
        """
        try:
            query = """
            SELECT 
                origen_tipo,
                COUNT(*) as cantidad,
                COUNT(DISTINCT origen_id) as origenes_unicos
            FROM comprobantes_adjuntos
            GROUP BY origen_tipo
            ORDER BY cantidad DESC
            """

            return self.fetch_all(query)

        except Exception as e:
            print(f"✗ Error obteniendo comprobantes por tipo de origen: {e}")
            return []

    # ============ MÉTODOS DE VALIDACIÓN DE UNICIDAD ============

    def comprobante_exists(
        self,
        origen_tipo: str,
        origen_id: int,
        tipo_documento: str,
        exclude_id: Optional[int] = None,
    ) -> bool:
        """
        Verifica si ya existe un comprobante para el origen y tipo de documento

        Args:
            origen_tipo: Tipo de origen
            origen_id: ID del origen
            tipo_documento: Tipo de documento
            exclude_id: ID a excluir (para actualizaciones)

        Returns:
            bool: True si existe, False en caso contrario
        """
        try:
            query = f"""
            SELECT COUNT(*) as count 
            FROM {self.table_name} 
            WHERE origen_tipo = %s 
              AND origen_id = %s 
              AND tipo_documento = %s
            """

            params = [origen_tipo, origen_id, tipo_documento]

            if exclude_id is not None:
                query += " AND id != %s"
                params.append(exclude_id)

            result = self.fetch_one(query, params)
            return result["count"] > 0 if result else False

        except Exception as e:
            print(f"✗ Error verificando comprobante: {e}")
            return False

    # ============ MÉTODOS DE COMPATIBILIDAD ============

    def obtener_todos(self):
        """Método de compatibilidad con nombres antiguos"""
        return self.get_all()

    def obtener_por_id(self, comprobante_id):
        """Método de compatibilidad con nombres antiguos"""
        return self.read(comprobante_id)

    def obtener_por_origen(self, origen_tipo, origen_id):
        """Método de compatibilidad con nombres antiguos"""
        return self.get_by_origen(origen_tipo, origen_id)

    def buscar_comprobantes(self, termino):
        """Método de compatibilidad con nombres antiguos"""
        return self.search(termino)

    def update_table(self, table, data, condition, params=None):
        """Método helper para actualizar (compatibilidad con BaseModel)"""
        return self.update(table, data, condition, params)  # type: ignore

    # ============ MÉTODOS DE UTILIDAD ============

    def get_tipos_origen(self) -> List[str]:
        """
        Obtiene la lista de tipos de origen

        Returns:
            List[str]: Lista de tipos
        """
        return self.TIPOS_ORIGEN.copy()

    def get_tipos_documento(self) -> List[str]:
        """
        Obtiene la lista de tipos de documento

        Returns:
            List[str]: Lista de tipos
        """
        return self.TIPOS_DOCUMENTO.copy()

    def get_extensiones_validas(self) -> List[str]:
        """
        Obtiene la lista de extensiones válidas

        Returns:
            List[str]: Lista de extensiones
        """
        return self.EXTENSIONES_VALIDAS.copy()

    def get_upload_requirements(self) -> Dict[str, Any]:
        """
        Obtiene los requisitos para subir archivos

        Returns:
            Dict: Requisitos de upload
        """
        return {
            "max_file_size_mb": self.MAX_FILE_SIZE_MB,
            "allowed_mime_types": self.ALLOWED_MIME_TYPES,
            "allowed_extensions": self.EXTENSIONES_VALIDAS,
            "base_upload_dir": self.BASE_UPLOAD_DIR,
        }
