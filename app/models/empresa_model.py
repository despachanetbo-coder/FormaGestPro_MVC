# app/models/docente_model.py - Versión optimizada y robusta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_model import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple, Union


class DocenteModel(BaseModel):
    def __init__(self):
        """Inicializa el modelo de docentes"""
        super().__init__()
        self.table_name = "docentes"
        self.sequence_name = "seq_docentes_id"

        # Tipos enumerados de la base de datos
        self.EXPEDICIONES_CI = ["LP", "CB", "SC", "CH", "TA", "PA", "BE", "OR", "PO"]
        self.GRADOS_ACADEMICOS = [
            "Licenciatura",
            "Maestría",
            "Doctorado",
            "Especialidad",
            "Diplomado",
            "Técnico",
        ]

        # Columnas de la tabla para validación
        self.columns = [
            "id",
            "ci_numero",
            "ci_expedicion",
            "nombres",
            "apellidos",
            "fecha_nacimiento",
            "max_grado_academico",
            "telefono",
            "email",
            "curriculum_path",
            "especialidad",
            "honorario_hora",
            "activo",
            "created_at",
        ]

        # Columnas requeridas
        self.required_columns = ["ci_numero", "nombres", "apellidos"]

    # ============ MÉTODOS DE VALIDACIÓN ============

    def _validate_docente_data(
        self, data: Dict[str, Any], for_update: bool = False
    ) -> Tuple[bool, str]:
        """
        Valida los datos del docente

        Args:
            data: Diccionario con datos del docente
            for_update: Si es True, valida para actualización

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        # Campos requeridos para creación
        if not for_update:
            for field in self.required_columns:
                if field not in data or not str(data[field]).strip():
                    return False, f"Campo requerido faltante: {field}"

        # Validar CI único si se proporciona
        if "ci_numero" in data and data["ci_numero"]:
            existing_id = None
            if for_update and "id" in data:
                existing_id = data["id"]

            if self.ci_exists(data["ci_numero"], exclude_id=existing_id):
                return False, f"El CI {data['ci_numero']} ya está registrado"

        # Validar email único si se proporciona
        if "email" in data and data["email"]:
            existing_id = None
            if for_update and "id" in data:
                existing_id = data["id"]

            if self.email_exists(data["email"], exclude_id=existing_id):
                return False, f"El email {data['email']} ya está registrado"

            # Validar formato de email
            if not self._is_valid_email(data["email"]):
                return False, "Formato de email inválido"

        # Validar formato de fecha si se proporciona
        if "fecha_nacimiento" in data and data["fecha_nacimiento"]:
            try:
                if isinstance(data["fecha_nacimiento"], str):
                    datetime.strptime(data["fecha_nacimiento"], "%Y-%m-%d")
            except ValueError:
                return False, "Formato de fecha inválido. Use YYYY-MM-DD"

        # Validar expedición de CI si se proporciona
        if "ci_expedicion" in data and data["ci_expedicion"]:
            if data["ci_expedicion"] not in self.EXPEDICIONES_CI:
                return (
                    False,
                    f"Expedición de CI inválida. Use: {', '.join(self.EXPEDICIONES_CI)}",
                )

        # Validar grado académico si se proporciona
        if "max_grado_academico" in data and data["max_grado_academico"]:
            if data["max_grado_academico"] not in self.GRADOS_ACADEMICOS:
                return (
                    False,
                    f"Grado académico inválido. Use: {', '.join(self.GRADOS_ACADEMICOS)}",
                )

        # Validar honorario por hora si se proporciona
        if "honorario_hora" in data and data["honorario_hora"] is not None:
            try:
                honorario = Decimal(str(data["honorario_hora"]))
                if honorario < 0:
                    return False, "El honorario por hora no puede ser negativo"
            except (ValueError, TypeError):
                return False, "Honorario por hora inválido. Use un número decimal"

        return True, "Datos válidos"

    def _is_valid_email(self, email: str) -> bool:
        """Valida formato de email usando regex similar al CHECK constraint de la BD"""
        import re

        pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        return bool(re.match(pattern, email, re.IGNORECASE))

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza los datos del docente

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
                # Convertir honorario a Decimal
                elif key == "honorario_hora" and value is not None:
                    try:
                        sanitized[key] = Decimal(str(value))
                    except:
                        sanitized[key] = value
                # Mantener otros tipos
                else:
                    sanitized[key] = value

        return sanitized

    # ============ MÉTODOS CRUD PRINCIPALES ============

    def create(self, data: Dict[str, Any]) -> Optional[int]:
        """
        Crea un nuevo docente

        Args:
            data: Diccionario con datos del docente

        Returns:
            Optional[int]: ID del docente creado o None si hay error
        """
        # Sanitizar y validar datos
        data = self._sanitize_data(data)
        is_valid, error_msg = self._validate_docente_data(data, for_update=False)

        if not is_valid:
            print(f"✗ Error validando datos: {error_msg}")
            return None

        try:
            # Preparar datos para inserción
            insert_data = data.copy()

            # Añadir campos por defecto si no están presentes
            if "activo" not in insert_data:
                insert_data["activo"] = True
            if "created_at" not in insert_data:
                insert_data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if "honorario_hora" not in insert_data:
                insert_data["honorario_hora"] = Decimal("0.00")

            # Insertar en base de datos
            result = self.insert(self.table_name, insert_data, returning="id")

            if result:
                print(f"✓ Docente creado exitosamente con ID: {result}")
                return result

            return None

        except Exception as e:
            print(f"✗ Error creando docente: {e}")
            return None

    def read(
        self, docente_id: int, include_inactive: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene un docente por su ID

        Args:
            docente_id: ID del docente
            include_inactive: Si es True, incluye docentes inactivos

        Returns:
            Optional[Dict]: Datos del docente o None si no existe
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE id = %s"
            params = (docente_id,)

            if not include_inactive:
                query += " AND activo = TRUE"

            result = self.fetch_one(query, params)
            return result

        except Exception as e:
            print(f"✗ Error obteniendo docente: {e}")
            return None

    def update(self, docente_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un docente existente

        Args:
            docente_id: ID del docente a actualizar
            data: Diccionario con datos a actualizar

        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        if not data:
            return False

        # Añadir ID para validación
        data_with_id = data.copy()
        data_with_id["id"] = docente_id

        # Sanitizar y validar datos
        data = self._sanitize_data(data)
        is_valid, error_msg = self._validate_docente_data(data_with_id, for_update=True)

        if not is_valid:
            print(f"✗ Error validando datos: {error_msg}")
            return False

        try:
            # Actualizar en base de datos
            result = self.update_table(
                self.table_name, data, f"id = %s AND activo = TRUE", (docente_id,)
            )

            if result:
                print(f"✓ Docente {docente_id} actualizado exitosamente")
                return True

            return False

        except Exception as e:
            print(f"✗ Error actualizando docente: {e}")
            return False

    def delete(self, docente_id: int, soft_delete: bool = True) -> bool:
        """
        Elimina un docente

        Args:
            docente_id: ID del docente
            soft_delete: Si es True, marca como inactivo en lugar de eliminar físicamente

        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            if soft_delete:
                # Soft delete: marcar como inactivo
                query = f"UPDATE {self.table_name} SET activo = FALSE WHERE id = %s"
                params = (docente_id,)
            else:
                # Hard delete: eliminar físicamente
                query = f"DELETE FROM {self.table_name} WHERE id = %s"
                params = (docente_id,)

            result = self.execute_query(query, params, commit=True)

            if result:
                delete_type = "desactivado" if soft_delete else "eliminado"
                print(f"✓ Docente {docente_id} {delete_type} exitosamente")
                return True

            return False

        except Exception as e:
            print(f"✗ Error eliminando docente: {e}")
            return False

    # ============ MÉTODOS DE CONSULTA AVANZADOS ============

    def get_all(
        self,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "apellidos",
        order_desc: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todos los docentes con paginación

        Args:
            active_only: Si es True, solo docentes activos
            limit: Límite de registros
            offset: Desplazamiento para paginación
            order_by: Campo para ordenar
            order_desc: Si es True, orden descendente

        Returns:
            List[Dict]: Lista de docentes
        """
        try:
            query = f"SELECT * FROM {self.table_name}"
            params = []

            # Filtrar por estado activo
            if active_only:
                query += " WHERE activo = TRUE"

            # Ordenar
            order_dir = "DESC" if order_desc else "ASC"
            query += f" ORDER BY {order_by} {order_dir}, nombres ASC"

            # Paginación
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            return self.fetch_all(query, params)

        except Exception as e:
            print(f"✗ Error obteniendo docentes: {e}")
            return []

    def search(
        self,
        search_term: str,
        active_only: bool = True,
        search_fields: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Busca docentes por término de búsqueda

        Args:
            search_term: Término a buscar
            active_only: Si es True, solo docentes activos
            search_fields: Campos donde buscar (None para todos los campos de texto)

        Returns:
            List[Dict]: Lista de docentes que coinciden
        """
        try:
            if search_fields is None:
                search_fields = [
                    "ci_numero",
                    "nombres",
                    "apellidos",
                    "email",
                    "telefono",
                    "especialidad",
                    "max_grado_academico",
                ]

            # Construir condiciones de búsqueda
            conditions = []
            params = []

            for field in search_fields:
                conditions.append(f"{field} ILIKE %s")
                params.append(f"%{search_term}%")

            where_clause = " OR ".join(conditions)

            query = f"SELECT * FROM {self.table_name} WHERE ({where_clause})"

            if active_only:
                query += " AND activo = TRUE"

            query += " ORDER BY apellidos, nombres"

            return self.fetch_all(query, params)

        except Exception as e:
            print(f"✗ Error buscando docentes: {e}")
            return []

    def get_by_ci(
        self, ci_numero: str, active_only: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene un docente por su número de CI

        Args:
            ci_numero: Número de CI
            active_only: Si es True, solo docentes activos

        Returns:
            Optional[Dict]: Datos del docente o None
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE ci_numero = %s"
            params = (ci_numero,)

            if active_only:
                query += " AND activo = TRUE"

            return self.fetch_one(query, params)

        except Exception as e:
            print(f"✗ Error obteniendo docente por CI: {e}")
            return None

    def get_by_email(
        self, email: str, active_only: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene un docente por su email

        Args:
            email: Email del docente
            active_only: Si es True, solo docentes activos

        Returns:
            Optional[Dict]: Datos del docente o None
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE email = %s"
            params = (email,)

            if active_only:
                query += " AND activo = TRUE"

            return self.fetch_one(query, params)

        except Exception as e:
            print(f"✗ Error obteniendo docente por email: {e}")
            return None

    def get_by_especialidad(
        self, especialidad: str, active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Obtiene docentes por especialidad

        Args:
            especialidad: Especialidad a buscar
            active_only: Si es True, solo docentes activos

        Returns:
            List[Dict]: Lista de docentes con la especialidad
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE especialidad ILIKE %s"
            params = (f"%{especialidad}%",)

            if active_only:
                query += " AND activo = TRUE"

            query += " ORDER BY apellidos, nombres"

            return self.fetch_all(query, params)

        except Exception as e:
            print(f"✗ Error obteniendo docentes por especialidad: {e}")
            return []

    def get_by_grado_academico(
        self, grado_academico: str, active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Obtiene docentes por grado académico

        Args:
            grado_academico: Grado académico a buscar
            active_only: Si es True, solo docentes activos

        Returns:
            List[Dict]: Lista de docentes con el grado académico
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE max_grado_academico = %s"
            params = (grado_academico,)

            if active_only:
                query += " AND activo = TRUE"

            query += " ORDER BY apellidos, nombres"

            return self.fetch_all(query, params)

        except Exception as e:
            print(f"✗ Error obteniendo docentes por grado académico: {e}")
            return []

    # ============ MÉTODOS PARA DASHBOARD ============

    def get_total_docentes(self, active_only: bool = True) -> int:
        """
        Obtiene el total de docentes

        Args:
            active_only: Si es True, solo docentes activos

        Returns:
            int: Número total de docentes
        """
        try:
            query = f"SELECT COUNT(*) as total FROM {self.table_name}"
            params = []

            if active_only:
                query += " WHERE activo = TRUE"

            result = self.fetch_one(query, params)
            return result["total"] if result else 0

        except Exception as e:
            print(f"✗ Error obteniendo total de docentes: {e}")
            return 0

    def get_distribucion_genero(self) -> List[Dict[str, Any]]:
        """
        Obtiene distribución de docentes por género
        Nota: Esta función necesita que la tabla tenga una columna 'genero'

        Returns:
            List[Dict]: Distribución por género
        """
        try:
            # Verificar si existe la columna genero
            table_columns = self.get_table_columns(self.table_name)

            if "genero" not in table_columns:
                print("⚠ La tabla docentes no tiene columna 'genero'")
                return []

            query = """
            SELECT 
                CASE 
                    WHEN genero IS NULL OR genero = '' THEN 'No especificado'
                    ELSE genero 
                END as genero,
                COUNT(*) as cantidad
            FROM docentes
            WHERE activo = TRUE
            GROUP BY 
                CASE 
                    WHEN genero IS NULL OR genero = '' THEN 'No especificado'
                    ELSE genero 
                END
            ORDER BY cantidad DESC
            """

            return self.fetch_all(query)

        except Exception as e:
            print(f"✗ Error obteniendo distribución por género: {e}")
            return []

    def get_docentes_por_departamento(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene cantidad de docentes por departamento
        Nota: Esto asume que hay una tabla 'departamentos' y relación con docentes

        Returns:
            List[Dict]: Docentes por departamento
        """
        try:
            query = """
            SELECT 
                COALESCE(d.nombre, 'Sin departamento') as departamento,
                COUNT(doc.id) as cantidad
            FROM docentes doc
            LEFT JOIN departamentos d ON doc.departamento_id = d.id
            WHERE doc.activo = TRUE
            GROUP BY d.nombre
            ORDER BY cantidad DESC
            LIMIT %s
            """

            return self.fetch_all(query, (limit,))

        except Exception as e:
            print(f"✗ Error obteniendo docentes por departamento: {e}")
            return []

    def get_estadisticas_honorarios(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de honorarios de docentes

        Returns:
            Dict: Estadísticas de honorarios
        """
        try:
            query = """
            SELECT 
                COUNT(*) as total_docentes,
                AVG(honorario_hora) as honorario_promedio,
                MIN(honorario_hora) as honorario_minimo,
                MAX(honorario_hora) as honorario_maximo,
                SUM(honorario_hora) as honorario_total
            FROM docentes
            WHERE activo = TRUE AND honorario_hora > 0
            """

            result = self.fetch_one(query)
            if result:
                # Convertir Decimal a float para serialización
                return {
                    "total_docentes": result["total_docentes"],
                    "honorario_promedio": (
                        float(result["honorario_promedio"])
                        if result["honorario_promedio"]
                        else 0.0
                    ),
                    "honorario_minimo": (
                        float(result["honorario_minimo"])
                        if result["honorario_minimo"]
                        else 0.0
                    ),
                    "honorario_maximo": (
                        float(result["honorario_maximo"])
                        if result["honorario_maximo"]
                        else 0.0
                    ),
                    "honorario_total": (
                        float(result["honorario_total"])
                        if result["honorario_total"]
                        else 0.0
                    ),
                }

            return {}

        except Exception as e:
            print(f"✗ Error obteniendo estadísticas de honorarios: {e}")
            return {}

    def get_docentes_por_grado_academico(self) -> List[Dict[str, Any]]:
        """
        Obtiene distribución de docentes por grado académico

        Returns:
            List[Dict]: Distribución por grado académico
        """
        try:
            query = """
            SELECT 
                COALESCE(max_grado_academico, 'No especificado') as grado_academico,
                COUNT(*) as cantidad
            FROM docentes
            WHERE activo = TRUE
            GROUP BY max_grado_academico
            ORDER BY cantidad DESC
            """

            return self.fetch_all(query)

        except Exception as e:
            print(f"✗ Error obteniendo docentes por grado académico: {e}")
            return []

    # ============ MÉTODOS DE VALIDACIÓN DE UNICIDAD ============

    def ci_exists(self, ci_numero: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si un CI ya existe

        Args:
            ci_numero: Número de CI a verificar
            exclude_id: ID a excluir (para actualizaciones)

        Returns:
            bool: True si existe, False en caso contrario
        """
        try:
            query = (
                f"SELECT COUNT(*) as count FROM {self.table_name} WHERE ci_numero = %s"
            )
            params = [ci_numero]

            if exclude_id is not None:
                query += " AND id != %s"
                params.append(str(exclude_id))

            result = self.fetch_one(query, params)
            return result["count"] > 0 if result else False

        except Exception as e:
            print(f"✗ Error verificando CI: {e}")
            return False

    def email_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si un email ya existe

        Args:
            email: Email a verificar
            exclude_id: ID a excluir (para actualizaciones)

        Returns:
            bool: True si existe, False en caso contrario
        """
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE email = %s"
            params = [email]

            if exclude_id is not None:
                query += " AND id != %s"
                params.append(str(exclude_id))

            result = self.fetch_one(query, params)
            return result["count"] > 0 if result else False

        except Exception as e:
            print(f"✗ Error verificando email: {e}")
            return False

    # ============ MÉTODOS DE ANÁLISIS Y REPORTES ============

    def get_estadisticas_por_edad(self) -> List[Dict[str, Any]]:
        """
        Obtiene distribución de docentes por rango de edad

        Returns:
            List[Dict]: Distribución por edad
        """
        try:
            query = """
            SELECT 
                CASE 
                    WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) < 30 THEN 'Menor de 30'
                    WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) BETWEEN 30 AND 40 THEN '30-40'
                    WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) BETWEEN 41 AND 50 THEN '41-50'
                    WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) BETWEEN 51 AND 60 THEN '51-60'
                    WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) > 60 THEN 'Mayor de 60'
                    ELSE 'Edad no especificada'
                END as rango_edad,
                COUNT(*) as cantidad
            FROM docentes
            WHERE activo = TRUE
            GROUP BY 
                CASE 
                    WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) < 30 THEN 'Menor de 30'
                    WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) BETWEEN 30 AND 40 THEN '30-40'
                    WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) BETWEEN 41 AND 50 THEN '41-50'
                    WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) BETWEEN 51 AND 60 THEN '51-60'
                    WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) > 60 THEN 'Mayor de 60'
                    ELSE 'Edad no especificada'
                END
            ORDER BY cantidad DESC
            """

            return self.fetch_all(query)

        except Exception as e:
            print(f"✗ Error obteniendo estadísticas por edad: {e}")
            return []

    def get_registros_por_mes(self, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Obtiene registros de docentes por mes

        Args:
            year: Año específico (None para año actual)

        Returns:
            List[Dict]: Registros por mes
        """
        try:
            if year is None:
                year = datetime.now().year

            query = """
            SELECT 
                EXTRACT(MONTH FROM created_at) as mes,
                COUNT(*) as cantidad
            FROM docentes
            WHERE EXTRACT(YEAR FROM created_at) = %s
            AND activo = TRUE
            GROUP BY EXTRACT(MONTH FROM created_at)
            ORDER BY mes
            """

            return self.fetch_all(query, (year,))

        except Exception as e:
            print(f"✗ Error obteniendo registros por mes: {e}")
            return []

    def get_top_especialidades(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene las especialidades más comunes entre los docentes

        Args:
            limit: Número de especialidades a retornar

        Returns:
            List[Dict]: Especialidades más comunes
        """
        try:
            query = """
            SELECT 
                COALESCE(especialidad, 'Sin especialidad') as especialidad,
                COUNT(*) as cantidad
            FROM docentes
            WHERE activo = TRUE
            GROUP BY especialidad
            ORDER BY cantidad DESC
            LIMIT %s
            """

            return self.fetch_all(query, (limit,))

        except Exception as e:
            print(f"✗ Error obteniendo top especialidades: {e}")
            return []

    # ============ MÉTODOS DE CONFIGURACIÓN ============

    def get_expediciones_ci(self) -> List[str]:
        """
        Obtiene la lista de expediciones de CI válidas

        Returns:
            List[str]: Lista de expediciones
        """
        return self.EXPEDICIONES_CI.copy()

    def get_grados_academicos(self) -> List[str]:
        """
        Obtiene la lista de grados académicos válidos

        Returns:
            List[str]: Lista de grados académicos
        """
        return self.GRADOS_ACADEMICOS.copy()

    # ============ MÉTODOS DE COMPATIBILIDAD ============

    def obtener_todos(self):
        """Método de compatibilidad con nombres antiguos"""
        return self.get_all()

    def obtener_por_id(self, docente_id):
        """Método de compatibilidad con nombres antiguos"""
        return self.read(docente_id)

    def buscar_docentes(self, termino):
        """Método de compatibilidad con nombres antiguos"""
        return self.search(termino)

    def update_table(self, table, data, condition, params=None):
        """Método helper para actualizar (compatibilidad con BaseModel)"""
        return self.update(table, data, condition, params)  # type: ignore
