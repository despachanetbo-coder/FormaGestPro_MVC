# app/models/estudiante_model.py - Versión optimizada y robusta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_model import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple


class EstudianteModel(BaseModel):
    def __init__(self):
        """Inicializa el modelo de estudiantes"""
        super().__init__()
        self.table_name = "estudiantes"
        self.sequence_name = "seq_estudiantes_id"

        # Columnas de la tabla para validación
        self.columns = [
            "id",
            "ci_numero",
            "ci_expedicion",
            "nombres",
            "apellidos",
            "fecha_nacimiento",
            "telefono",
            "email",
            "universidad_egreso",
            "profesion",
            "fotografia_path",
            "fecha_registro",
            "activo",
        ]

    # ============ MÉTODOS DE VALIDACIÓN ============

    def _validate_estudiante_data(
        self, data: Dict[str, Any], for_update: bool = False
    ) -> Tuple[bool, str]:
        """
        Valida los datos del estudiante

        Args:
            data: Diccionario con datos del estudiante
            for_update: Si es True, valida para actualización

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        # Campos requeridos para creación
        required_fields = ["ci_numero", "nombres", "apellidos"]

        if not for_update:
            for field in required_fields:
                if field not in data or not data[field]:
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

        # Validar formato de fecha si se proporciona
        if "fecha_nacimiento" in data and data["fecha_nacimiento"]:
            try:
                datetime.strptime(data["fecha_nacimiento"], "%Y-%m-%d")
            except ValueError:
                return False, "Formato de fecha inválido. Use YYYY-MM-DD"

        # Validar expedición de CI si se proporciona
        if "ci_expedicion" in data and data["ci_expedicion"]:
            valid_expediciones = ["LP", "CB", "SC", "CH", "TA", "PA", "BE", "OR", "PO"]
            if data["ci_expedicion"] not in valid_expediciones:
                return (
                    False,
                    f"Expedición de CI inválida. Use: {', '.join(valid_expediciones)}",
                )

        return True, "Datos válidos"

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza los datos del estudiante

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

    def create(self, data: Dict[str, Any]) -> Optional[int]:
        """
        Crea un nuevo estudiante

        Args:
            data: Diccionario con datos del estudiante

        Returns:
            Optional[int]: ID del estudiante creado o None si hay error
        """
        # Sanitizar y validar datos
        data = self._sanitize_data(data)
        is_valid, error_msg = self._validate_estudiante_data(data, for_update=False)

        if not is_valid:
            print(f"✗ Error validando datos: {error_msg}")
            return None

        try:
            # Preparar datos para inserción
            insert_data = data.copy()

            # Añadir campos por defecto si no están presentes
            if "activo" not in insert_data:
                insert_data["activo"] = True
            if "fecha_registro" not in insert_data:
                insert_data["fecha_registro"] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            # Insertar en base de datos
            result = self.insert(
                table=self.table_name, data=insert_data, returning="id"  # type: ignore
            )

            if result:
                print(f"✓ Estudiante creado exitosamente con ID: {result}")
                return result

            return None

        except Exception as e:
            print(f"✗ Error creando estudiante: {e}")
            return None

    def read(
        self, estudiante_id: int, include_inactive: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene un estudiante por su ID

        Args:
            estudiante_id: ID del estudiante
            include_inactive: Si es True, incluye estudiantes inactivos

        Returns:
            Optional[Dict]: Datos del estudiante o None si no existe
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE id = %s"
            params = (estudiante_id,)

            if not include_inactive:
                query += " AND activo = TRUE"

            result = self.fetch_one(query, params)
            return result

        except Exception as e:
            print(f"✗ Error obteniendo estudiante: {e}")
            return None

    def update(self, estudiante_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un estudiante existente

        Args:
            estudiante_id: ID del estudiante a actualizar
            data: Diccionario con datos a actualizar

        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        if not data:
            return False

        # Añadir ID para validación
        data_with_id = data.copy()
        data_with_id["id"] = estudiante_id

        # Sanitizar y validar datos
        data = self._sanitize_data(data)
        is_valid, error_msg = self._validate_estudiante_data(
            data_with_id, for_update=True
        )

        if not is_valid:
            print(f"✗ Error validando datos: {error_msg}")
            return False

        try:
            # Actualizar en base de datos
            result = self.update_table(
                self.table_name, data, f"id = %s AND activo = TRUE", (estudiante_id,)
            )

            if result:
                print(f"✓ Estudiante {estudiante_id} actualizado exitosamente")
                return True

            return False

        except Exception as e:
            print(f"✗ Error actualizando estudiante: {e}")
            return False

    def delete(self, estudiante_id: int, soft_delete: bool = True) -> bool:
        """
        Elimina un estudiante

        Args:
            estudiante_id: ID del estudiante
            soft_delete: Si es True, marca como inactivo en lugar de eliminar físicamente

        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            if soft_delete:
                # Soft delete: marcar como inactivo
                query = f"UPDATE {self.table_name} SET activo = FALSE WHERE id = %s"
                params = (estudiante_id,)
            else:
                # Hard delete: eliminar físicamente
                query = f"DELETE FROM {self.table_name} WHERE id = %s"
                params = (estudiante_id,)

            result = self.execute_query(query, params, commit=True)

            if result:
                delete_type = "desactivado" if soft_delete else "eliminado"
                print(f"✓ Estudiante {estudiante_id} {delete_type} exitosamente")
                return True

            return False

        except Exception as e:
            print(f"✗ Error eliminando estudiante: {e}")
            return False

    # ============ MÉTODOS DE CONSULTA AVANZADOS ============

    def get_all(
        self,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "id",
        order_desc: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todos los estudiantes con paginación

        Args:
            active_only: Si es True, solo estudiantes activos
            limit: Límite de registros
            offset: Desplazamiento para paginación
            order_by: Campo para ordenar
            order_desc: Si es True, orden descendente

        Returns:
            List[Dict]: Lista de estudiantes
        """
        try:
            query = f"SELECT * FROM {self.table_name}"
            params = []

            # Filtrar por estado activo
            if active_only:
                query += " WHERE activo = TRUE"

            # Ordenar
            order_dir = "DESC" if order_desc else "ASC"
            query += f" ORDER BY {order_by} {order_dir}"

            # Paginación
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            return self.fetch_all(query, params)

        except Exception as e:
            print(f"✗ Error obteniendo estudiantes: {e}")
            return []

    def search(
        self,
        search_term: str,
        active_only: bool = True,
        search_fields: List[str] = None,  # type: ignore
    ) -> List[Dict[str, Any]]:
        """
        Busca estudiantes por término de búsqueda

        Args:
            search_term: Término a buscar
            active_only: Si es True, solo estudiantes activos
            search_fields: Campos donde buscar (None para todos los campos de texto)

        Returns:
            List[Dict]: Lista de estudiantes que coinciden
        """
        try:
            if search_fields is None:
                search_fields = [
                    "ci_numero",
                    "nombres",
                    "apellidos",
                    "email",
                    "telefono",
                    "universidad_egreso",
                    "profesion",
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
            print(f"✗ Error buscando estudiantes: {e}")
            return []

    def get_by_ci(
        self, ci_numero: str, active_only: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene un estudiante por su número de CI

        Args:
            ci_numero: Número de CI
            active_only: Si es True, solo estudiantes activos

        Returns:
            Optional[Dict]: Datos del estudiante o None
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE ci_numero = %s"
            params = (ci_numero,)

            if active_only:
                query += " AND activo = TRUE"

            return self.fetch_one(query, params)

        except Exception as e:
            print(f"✗ Error obteniendo estudiante por CI: {e}")
            return None

    def get_by_email(
        self, email: str, active_only: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene un estudiante por su email

        Args:
            email: Email del estudiante
            active_only: Si es True, solo estudiantes activos

        Returns:
            Optional[Dict]: Datos del estudiante o None
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE email = %s"
            params = (email,)

            if active_only:
                query += " AND activo = TRUE"

            return self.fetch_one(query, params)

        except Exception as e:
            print(f"✗ Error obteniendo estudiante por email: {e}")
            return None

    # ============ MÉTODOS PARA DASHBOARD ============

    def get_total_estudiantes(self, active_only: bool = True) -> int:
        """
        Obtiene el total de estudiantes

        Args:
            active_only: Si es True, solo estudiantes activos

        Returns:
            int: Número total de estudiantes
        """
        try:
            query = f"SELECT COUNT(*) as total FROM {self.table_name}"
            params = []

            if active_only:
                query += " WHERE activo = TRUE"

            result = self.fetch_one(query, params)
            return result["total"] if result else 0

        except Exception as e:
            print(f"✗ Error obteniendo total de estudiantes: {e}")
            return 0

    def get_distribucion_genero(self) -> List[Dict[str, Any]]:
        """
        Obtiene distribución de estudiantes por género
        Nota: Esta función necesita que la tabla tenga una columna 'genero'

        Returns:
            List[Dict]: Distribución por género
        """
        try:
            # Verificar si existe la columna genero
            table_columns = self.get_table_columns(self.table_name)

            if "genero" not in table_columns:
                print("⚠ La tabla estudiantes no tiene columna 'genero'")
                return []

            query = """
            SELECT 
                CASE 
                    WHEN genero IS NULL OR genero = '' THEN 'No especificado'
                    ELSE genero 
                END as genero,
                COUNT(*) as cantidad
            FROM estudiantes
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

    def get_estudiantes_por_programa(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene cantidad de estudiantes por programa
        Nota: Esto asume que hay una tabla 'programas' y relación con estudiantes

        Returns:
            List[Dict]: Estudiantes por programa
        """
        try:
            query = """
            SELECT 
                COALESCE(p.nombre, 'Sin programa') as programa,
                COUNT(e.id) as cantidad
            FROM estudiantes e
            LEFT JOIN programas p ON e.programa_id = p.id
            WHERE e.activo = TRUE
            GROUP BY p.nombre
            ORDER BY cantidad DESC
            LIMIT %s
            """

            return self.fetch_all(query, (limit,))

        except Exception as e:
            print(f"✗ Error obteniendo estudiantes por programa: {e}")
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
                params.append(exclude_id)  # type: ignore

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
                params.append(exclude_id)  # type: ignore

            result = self.fetch_one(query, params)
            return result["count"] > 0 if result else False

        except Exception as e:
            print(f"✗ Error verificando email: {e}")
            return False

    # ============ MÉTODOS DE ANÁLISIS Y REPORTES ============

    def get_estadisticas_por_edad(self) -> List[Dict[str, Any]]:
        """
        Obtiene distribución de estudiantes por rango de edad

        Returns:
            List[Dict]: Distribución por edad
        """
        try:
            query = """
            SELECT 
                CASE 
                    WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) < 18 THEN 'Menor de 18'
                    WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) BETWEEN 18 AND 25 THEN '18-25'
                    WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) BETWEEN 26 AND 35 THEN '26-35'
                    WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) BETWEEN 36 AND 45 THEN '36-45'
                    WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) > 45 THEN 'Mayor de 45'
                    ELSE 'Edad no especificada'
                END as rango_edad,
                COUNT(*) as cantidad
            FROM estudiantes
            WHERE activo = TRUE
            GROUP BY 
                CASE 
                    WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) < 18 THEN 'Menor de 18'
                    WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) BETWEEN 18 AND 25 THEN '18-25'
                    WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) BETWEEN 26 AND 35 THEN '26-35'
                    WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) BETWEEN 36 AND 45 THEN '36-45'
                    WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) > 45 THEN 'Mayor de 45'
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
        Obtiene registros de estudiantes por mes

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
                EXTRACT(MONTH FROM fecha_registro) as mes,
                COUNT(*) as cantidad
            FROM estudiantes
            WHERE EXTRACT(YEAR FROM fecha_registro) = %s
            AND activo = TRUE
            GROUP BY EXTRACT(MONTH FROM fecha_registro)
            ORDER BY mes
            """

            return self.fetch_all(query, (year,))

        except Exception as e:
            print(f"✗ Error obteniendo registros por mes: {e}")
            return []

    # ============ MÉTODOS DE COMPATIBILIDAD ============

    def obtener_todos(self):
        """Método de compatibilidad con nombres antiguos"""
        return self.get_all()

    def obtener_por_id(self, estudiante_id):
        """Método de compatibilidad con nombres antiguos"""
        return self.read(estudiante_id)

    def buscar_estudiantes(self, termino):
        """Método de compatibilidad con nombres antiguos"""
        return self.search(termino)

    def update_table(self, table, data, condition, params=None):
        """Método helper para actualizar (compatibilidad con BaseModel)"""
        return self.update(table, data, condition, params)  # type: ignore
