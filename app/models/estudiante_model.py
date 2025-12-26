# app/models/estudiante_model.py - Versión corregida y optimizada
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_model import BaseModel
from datetime import datetime


class EstudianteModel(BaseModel):
    def __init__(self):
        """Inicializa el modelo de estudiantes"""
        super().__init__()
        self.table_name = "estudiantes"

    # ============ MÉTODOS CRUD BÁSICOS ============

    def create(self, data):
        """
        Crea un nuevo estudiante
        Args:
            data: Diccionario con los datos del estudiante
        Returns:
            ID del estudiante creado o None si hay error
        """
        required_fields = [
            "ci",
            "nombre",
            "apellido",
            "email",
            "telefono",
            "direccion",
            "fecha_nacimiento",
        ]

        # Validar campos requeridos
        for field in required_fields:
            if field not in data:
                print(f"Error: Campo requerido '{field}' no encontrado")
                return None

        try:
            query = """
            INSERT INTO estudiantes 
            (ci, nombre, apellido, email, telefono, direccion, fecha_nacimiento, genero, programa_id, estado) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            RETURNING id
            """

            params = (
                data["ci"],
                data["nombre"],
                data["apellido"],
                data["email"],
                data.get("telefono", ""),
                data.get("direccion", ""),
                data["fecha_nacimiento"],
                data.get("genero", ""),
                data.get("programa_id"),
                data.get("estado", "Activo"),
            )

            result = self.execute_query(query, params, fetch=True)
            if result:
                return result[0]["id"]
            return None

        except Exception as e:
            print(f"Error creando estudiante: {e}")
            return None

    def read(self, estudiante_id):
        """
        Obtiene un estudiante por su ID
        Args:
            estudiante_id: ID del estudiante
        Returns:
            Diccionario con los datos del estudiante o None si no existe
        """
        try:
            query = """
            SELECT e.*, p.nombre as programa_nombre 
            FROM estudiantes e 
            LEFT JOIN programas p ON e.programa_id = p.id 
            WHERE e.id = %s
            """
            result = self.execute_query(query, (estudiante_id,))
            return result[0] if result else None
        except Exception as e:
            print(f"Error leyendo estudiante: {e}")
            return None

    def update(self, estudiante_id, data):
        """
        Actualiza un estudiante existente
        Args:
            estudiante_id: ID del estudiante a actualizar
            data: Diccionario con los datos a actualizar
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        if not data:
            return False

        try:
            # Construir la consulta dinámicamente
            set_clauses = []
            params = []

            for key, value in data.items():
                if key != "id":  # No actualizar el ID
                    set_clauses.append(f"{key} = %s")
                    params.append(value)

            if not set_clauses:
                return False

            params.append(estudiante_id)
            query = f"UPDATE estudiantes SET {', '.join(set_clauses)} WHERE id = %s"

            self.execute_query(query, params, commit=True)
            return True

        except Exception as e:
            print(f"Error actualizando estudiante: {e}")
            return False

    def delete(self, estudiante_id):
        """
        Elimina un estudiante (cambia estado a Inactivo)
        Args:
            estudiante_id: ID del estudiante
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            query = "UPDATE estudiantes SET estado = 'Inactivo' WHERE id = %s"
            self.execute_query(query, (estudiante_id,), commit=True)
            return True
        except Exception as e:
            print(f"Error eliminando estudiante: {e}")
            return False

    # ============ MÉTODOS DE CONSULTA ESPECÍFICOS ============

    def get_all(self, estado="Activo", limit=100, offset=0):
        """
        Obtiene todos los estudiantes con paginación
        Args:
            estado: Filtrar por estado (Activo/Inactivo/Todos)
            limit: Límite de registros
            offset: Desplazamiento para paginación
        Returns:
            Lista de estudiantes
        """
        try:
            if estado == "Todos":
                query = """
                SELECT e.*, p.nombre as programa_nombre 
                FROM estudiantes e 
                LEFT JOIN programas p ON e.programa_id = p.id 
                ORDER BY e.id DESC 
                LIMIT %s OFFSET %s
                """
                params = (limit, offset)
            else:
                query = """
                SELECT e.*, p.nombre as programa_nombre 
                FROM estudiantes e 
                LEFT JOIN programas p ON e.programa_id = p.id 
                WHERE e.estado = %s 
                ORDER BY e.id DESC 
                LIMIT %s OFFSET %s
                """
                params = (estado, limit, offset)

            return self.execute_query(query, params)
        except Exception as e:
            print(f"Error obteniendo todos los estudiantes: {e}")
            return []

    def search(self, search_term, estado="Activo"):
        """
        Busca estudiantes por término de búsqueda
        Args:
            search_term: Término a buscar (en ci, nombre, apellido, email)
            estado: Estado de los estudiantes a buscar
        Returns:
            Lista de estudiantes que coinciden con la búsqueda
        """
        try:
            if estado == "Todos":
                query = """
                SELECT e.*, p.nombre as programa_nombre 
                FROM estudiantes e 
                LEFT JOIN programas p ON e.programa_id = p.id 
                WHERE e.ci ILIKE %s OR e.nombre ILIKE %s OR e.apellido ILIKE %s OR e.email ILIKE %s 
                ORDER BY e.id DESC
                """
                params = (
                    f"%{search_term}%",
                    f"%{search_term}%",
                    f"%{search_term}%",
                    f"%{search_term}%",
                )
            else:
                query = """
                SELECT e.*, p.nombre as programa_nombre 
                FROM estudiantes e 
                LEFT JOIN programas p ON e.programa_id = p.id 
                WHERE (e.ci ILIKE %s OR e.nombre ILIKE %s OR e.apellido ILIKE %s OR e.email ILIKE %s) 
                AND e.estado = %s 
                ORDER BY e.id DESC
                """
                params = (
                    f"%{search_term}%",
                    f"%{search_term}%",
                    f"%{search_term}%",
                    f"%{search_term}%",
                    estado,
                )

            return self.execute_query(query, params)
        except Exception as e:
            print(f"Error buscando estudiantes: {e}")
            return []

    # ============ MÉTODOS PARA DASHBOARD ============

    def get_total_estudiantes(self, estado="Activo"):
        """
        Obtiene el total de estudiantes registrados
        Args:
            estado: Filtrar por estado (Activo/Inactivo/Todos)
        Returns:
            Número total de estudiantes
        """
        try:
            if estado == "Todos":
                query = "SELECT COUNT(*) as total FROM estudiantes"
                params = ()
            else:
                query = "SELECT COUNT(*) as total FROM estudiantes WHERE estado = %s"
                params = (estado,)

            result = self.execute_query(query, params)
            return result[0]["total"] if result else 0
        except Exception as e:
            print(f"Error obteniendo total estudiantes: {e}")
            return 0

    def get_distribucion_genero(self, estado="Activo"):
        """
        Obtiene distribución de estudiantes por género
        Args:
            estado: Filtrar por estado
        Returns:
            Lista de diccionarios con género y cantidad
        """
        try:
            if estado == "Todos":
                query = """
                SELECT 
                    CASE 
                        WHEN genero IS NULL OR genero = '' THEN 'No especificado'
                        ELSE genero 
                    END as genero,
                    COUNT(*) as cantidad
                FROM estudiantes
                GROUP BY 
                    CASE 
                        WHEN genero IS NULL OR genero = '' THEN 'No especificado'
                        ELSE genero 
                    END
                ORDER BY cantidad DESC
                """
                params = ()
            else:
                query = """
                SELECT 
                    CASE 
                        WHEN genero IS NULL OR genero = '' THEN 'No especificado'
                        ELSE genero 
                    END as genero,
                    COUNT(*) as cantidad
                FROM estudiantes
                WHERE estado = %s
                GROUP BY 
                    CASE 
                        WHEN genero IS NULL OR genero = '' THEN 'No especificado'
                        ELSE genero 
                    END
                ORDER BY cantidad DESC
                """
                params = (estado,)

            return self.execute_query(query, params)
        except Exception as e:
            print(f"Error obteniendo distribución por género: {e}")
            return []

    def get_estudiantes_por_programa(self, estado="Activo", limit=10):
        """
        Obtiene cantidad de estudiantes por programa
        Args:
            estado: Filtrar por estado
            limit: Límite de programas a mostrar
        Returns:
            Lista de diccionarios con programa y cantidad
        """
        try:
            if estado == "Todos":
                query = """
                SELECT 
                    COALESCE(p.nombre, 'Sin programa') as programa,
                    COUNT(e.id) as cantidad
                FROM estudiantes e
                LEFT JOIN programas p ON e.programa_id = p.id
                GROUP BY p.nombre
                ORDER BY cantidad DESC
                LIMIT %s
                """
                params = (limit,)
            else:
                query = """
                SELECT 
                    COALESCE(p.nombre, 'Sin programa') as programa,
                    COUNT(e.id) as cantidad
                FROM estudiantes e
                LEFT JOIN programas p ON e.programa_id = p.id
                WHERE e.estado = %s
                GROUP BY p.nombre
                ORDER BY cantidad DESC
                LIMIT %s
                """
                params = (estado, limit)

            return self.execute_query(query, params)
        except Exception as e:
            print(f"Error obteniendo estudiantes por programa: {e}")
            return []

    def get_estudiantes_por_rango_edad(self, estado="Activo"):
        """
        Obtiene distribución de estudiantes por rango de edad
        Args:
            estado: Filtrar por estado
        Returns:
            Lista de diccionarios con rango de edad y cantidad
        """
        try:
            if estado == "Todos":
                query = """
                SELECT 
                    CASE 
                        WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) < 18 THEN 'Menor de 18'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) BETWEEN 18 AND 22 THEN '18-22'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) BETWEEN 23 AND 30 THEN '23-30'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) > 30 THEN 'Mayor de 30'
                        ELSE 'Edad no especificada'
                    END as rango_edad,
                    COUNT(*) as cantidad
                FROM estudiantes
                GROUP BY 
                    CASE 
                        WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) < 18 THEN 'Menor de 18'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) BETWEEN 18 AND 22 THEN '18-22'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) BETWEEN 23 AND 30 THEN '23-30'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) > 30 THEN 'Mayor de 30'
                        ELSE 'Edad no especificada'
                    END
                ORDER BY cantidad DESC
                """
                params = ()
            else:
                query = """
                SELECT 
                    CASE 
                        WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) < 18 THEN 'Menor de 18'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) BETWEEN 18 AND 22 THEN '18-22'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) BETWEEN 23 AND 30 THEN '23-30'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) > 30 THEN 'Mayor de 30'
                        ELSE 'Edad no especificada'
                    END as rango_edad,
                    COUNT(*) as cantidad
                FROM estudiantes
                WHERE estado = %s
                GROUP BY 
                    CASE 
                        WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) < 18 THEN 'Menor de 18'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) BETWEEN 18 AND 22 THEN '18-22'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) BETWEEN 23 AND 30 THEN '23-30'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) > 30 THEN 'Mayor de 30'
                        ELSE 'Edad no especificada'
                    END
                ORDER BY cantidad DESC
                """
                params = (estado,)

            return self.execute_query(query, params)
        except Exception as e:
            print(f"Error obteniendo distribución por edad: {e}")
            return []

    def get_estadisticas_mensuales(self, año=None, estado="Activo"):
        """
        Obtiene estadísticas mensuales de registros de estudiantes
        Args:
            año: Año a consultar (None para año actual)
            estado: Filtrar por estado
        Returns:
            Lista de diccionarios con mes y cantidad de registros
        """
        try:
            if año is None:
                año = datetime.now().year

            if estado == "Todos":
                query = """
                SELECT 
                    EXTRACT(MONTH FROM fecha_registro) as mes,
                    COUNT(*) as cantidad
                FROM estudiantes
                WHERE EXTRACT(YEAR FROM fecha_registro) = %s
                GROUP BY EXTRACT(MONTH FROM fecha_registro)
                ORDER BY mes
                """
                params = (año,)
            else:
                query = """
                SELECT 
                    EXTRACT(MONTH FROM fecha_registro) as mes,
                    COUNT(*) as cantidad
                FROM estudiantes
                WHERE EXTRACT(YEAR FROM fecha_registro) = %s AND estado = %s
                GROUP BY EXTRACT(MONTH FROM fecha_registro)
                ORDER BY mes
                """
                params = (año, estado)

            return self.execute_query(query, params)
        except Exception as e:
            print(f"Error obteniendo estadísticas mensuales: {e}")
            return []

    # ============ MÉTODOS DE VALIDACIÓN ============

    def ci_exists(self, ci, exclude_id=None):
        """
        Verifica si un CI ya existe en la base de datos
        Args:
            ci: CI a verificar
            exclude_id: ID a excluir (para actualizaciones)
        Returns:
            True si existe, False en caso contrario
        """
        try:
            if exclude_id:
                query = "SELECT COUNT(*) as count FROM estudiantes WHERE ci = %s AND id != %s"
                params = (ci, exclude_id)
            else:
                query = "SELECT COUNT(*) as count FROM estudiantes WHERE ci = %s"
                params = (ci,)

            result = self.execute_query(query, params)
            return result[0]["count"] > 0 if result else False
        except Exception as e:
            print(f"Error verificando CI: {e}")
            return False

    def email_exists(self, email, exclude_id=None):
        """
        Verifica si un email ya existe en la base de datos
        Args:
            email: Email a verificar
            exclude_id: ID a excluir (para actualizaciones)
        Returns:
            True si existe, False en caso contrario
        """
        try:
            if exclude_id:
                query = "SELECT COUNT(*) as count FROM estudiantes WHERE email = %s AND id != %s"
                params = (email, exclude_id)
            else:
                query = "SELECT COUNT(*) as count FROM estudiantes WHERE email = %s"
                params = (email,)

            result = self.execute_query(query, params)
            return result[0]["count"] > 0 if result else False
        except Exception as e:
            print(f"Error verificando email: {e}")
            return False

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
