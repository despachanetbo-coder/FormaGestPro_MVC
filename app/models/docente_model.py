# app/models/docente_model.py - Versión corregida y optimizada
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_model import BaseModel
from datetime import datetime


class DocenteModel(BaseModel):
    def __init__(self):
        """Inicializa el modelo de docentes"""
        super().__init__()
        self.table_name = "docentes"

    # ============ MÉTODOS CRUD BÁSICOS ============

    def create(self, data):
        """
        Crea un nuevo docente
        Args:
            data: Diccionario con los datos del docente
        Returns:
            ID del docente creado o None si hay error
        """
        required_fields = ["ci", "nombre", "apellido", "email", "telefono"]

        # Validar campos requeridos
        for field in required_fields:
            if field not in data:
                print(f"Error: Campo requerido '{field}' no encontrado")
                return None

        try:
            query = """
            INSERT INTO docentes 
            (ci, nombre, apellido, email, telefono, direccion, fecha_nacimiento, genero, 
             departamento_id, titulo_academico, especialidad, estado) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            RETURNING id
            """

            params = (
                data["ci"],
                data["nombre"],
                data["apellido"],
                data["email"],
                data.get("telefono", ""),
                data.get("direccion", ""),
                data.get("fecha_nacimiento"),
                data.get("genero", ""),
                data.get("departamento_id"),
                data.get("titulo_academico", ""),
                data.get("especialidad", ""),
                data.get("estado", "Activo"),
            )

            result = self.execute_query(query, params, fetch=True)
            if result:
                return result[0]["id"]
            return None

        except Exception as e:
            print(f"Error creando docente: {e}")
            return None

    def read(self, docente_id):
        """
        Obtiene un docente por su ID
        Args:
            docente_id: ID del docente
        Returns:
            Diccionario con los datos del docente o None si no existe
        """
        try:
            query = """
            SELECT d.*, dep.nombre as departamento_nombre 
            FROM docentes d 
            LEFT JOIN departamentos dep ON d.departamento_id = dep.id 
            WHERE d.id = %s
            """
            result = self.execute_query(query, (docente_id,))
            return result[0] if result else None
        except Exception as e:
            print(f"Error leyendo docente: {e}")
            return None

    def update(self, docente_id, data):
        """
        Actualiza un docente existente
        Args:
            docente_id: ID del docente a actualizar
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

            params.append(docente_id)
            query = f"UPDATE docentes SET {', '.join(set_clauses)} WHERE id = %s"

            self.execute_query(query, params, commit=True)
            return True

        except Exception as e:
            print(f"Error actualizando docente: {e}")
            return False

    def delete(self, docente_id):
        """
        Elimina un docente (cambia estado a Inactivo)
        Args:
            docente_id: ID del docente
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            query = "UPDATE docentes SET estado = 'Inactivo' WHERE id = %s"
            self.execute_query(query, (docente_id,), commit=True)
            return True
        except Exception as e:
            print(f"Error eliminando docente: {e}")
            return False

    # ============ MÉTODOS DE CONSULTA ESPECÍFICOS ============

    def get_all(self, estado="Activo", limit=100, offset=0):
        """
        Obtiene todos los docentes con paginación
        Args:
            estado: Filtrar por estado (Activo/Inactivo/Todos)
            limit: Límite de registros
            offset: Desplazamiento para paginación
        Returns:
            Lista de docentes
        """
        try:
            if estado == "Todos":
                query = """
                SELECT d.*, dep.nombre as departamento_nombre 
                FROM docentes d 
                LEFT JOIN departamentos dep ON d.departamento_id = dep.id 
                ORDER BY d.id DESC 
                LIMIT %s OFFSET %s
                """
                params = (limit, offset)
            else:
                query = """
                SELECT d.*, dep.nombre as departamento_nombre 
                FROM docentes d 
                LEFT JOIN departamentos dep ON d.departamento_id = dep.id 
                WHERE d.estado = %s 
                ORDER BY d.id DESC 
                LIMIT %s OFFSET %s
                """
                params = (estado, limit, offset)

            return self.execute_query(query, params)
        except Exception as e:
            print(f"Error obteniendo todos los docentes: {e}")
            return []

    def search(self, search_term, estado="Activo"):
        """
        Busca docentes por término de búsqueda
        Args:
            search_term: Término a buscar (en ci, nombre, apellido, email, especialidad)
            estado: Estado de los docentes a buscar
        Returns:
            Lista de docentes que coinciden con la búsqueda
        """
        try:
            if estado == "Todos":
                query = """
                SELECT d.*, dep.nombre as departamento_nombre 
                FROM docentes d 
                LEFT JOIN departamentos dep ON d.departamento_id = dep.id 
                WHERE d.ci ILIKE %s OR d.nombre ILIKE %s OR d.apellido ILIKE %s 
                OR d.email ILIKE %s OR d.especialidad ILIKE %s 
                ORDER BY d.id DESC
                """
                params = (
                    f"%{search_term}%",
                    f"%{search_term}%",
                    f"%{search_term}%",
                    f"%{search_term}%",
                    f"%{search_term}%",
                )
            else:
                query = """
                SELECT d.*, dep.nombre as departamento_nombre 
                FROM docentes d 
                LEFT JOIN departamentos dep ON d.departamento_id = dep.id 
                WHERE (d.ci ILIKE %s OR d.nombre ILIKE %s OR d.apellido ILIKE %s 
                OR d.email ILIKE %s OR d.especialidad ILIKE %s) 
                AND d.estado = %s 
                ORDER BY d.id DESC
                """
                params = (
                    f"%{search_term}%",
                    f"%{search_term}%",
                    f"%{search_term}%",
                    f"%{search_term}%",
                    f"%{search_term}%",
                    estado,
                )

            return self.execute_query(query, params)
        except Exception as e:
            print(f"Error buscando docentes: {e}")
            return []

    # ============ MÉTODOS PARA DASHBOARD (IMPLEMENTADOS) ============

    def get_total_docentes(self, estado="Activo"):
        """
        Obtiene el total de docentes registrados
        Args:
            estado: Filtrar por estado (Activo/Inactivo/Todos)
        Returns:
            Número total de docentes
        """
        try:
            if estado == "Todos":
                query = "SELECT COUNT(*) as total FROM docentes"
                params = ()
            else:
                query = "SELECT COUNT(*) as total FROM docentes WHERE estado = %s"
                params = (estado,)

            result = self.execute_query(query, params)
            return result[0]["total"] if result else 0
        except Exception as e:
            print(f"Error obteniendo total docentes: {e}")
            return 0

    def get_distribucion_genero(self, estado="Activo"):
        """
        Obtiene distribución de docentes por género
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
                FROM docentes
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
                FROM docentes
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

    def get_docentes_por_departamento(self, estado="Activo", limit=10):
        """
        Obtiene cantidad de docentes por departamento
        Args:
            estado: Filtrar por estado
            limit: Límite de departamentos a mostrar
        Returns:
            Lista de diccionarios con departamento y cantidad
        """
        try:
            if estado == "Todos":
                query = """
                SELECT 
                    COALESCE(dep.nombre, 'Sin departamento') as departamento,
                    COUNT(d.id) as cantidad
                FROM docentes d
                LEFT JOIN departamentos dep ON d.departamento_id = dep.id
                GROUP BY dep.nombre
                ORDER BY cantidad DESC
                LIMIT %s
                """
                params = (limit,)
            else:
                query = """
                SELECT 
                    COALESCE(dep.nombre, 'Sin departamento') as departamento,
                    COUNT(d.id) as cantidad
                FROM docentes d
                LEFT JOIN departamentos dep ON d.departamento_id = dep.id
                WHERE d.estado = %s
                GROUP BY dep.nombre
                ORDER BY cantidad DESC
                LIMIT %s
                """
                params = (estado, limit)

            return self.execute_query(query, params)
        except Exception as e:
            print(f"Error obteniendo docentes por departamento: {e}")
            return []

    def get_docentes_por_titulo_academico(self, estado="Activo"):
        """
        Obtiene distribución de docentes por título académico
        Args:
            estado: Filtrar por estado
        Returns:
            Lista de diccionarios con título académico y cantidad
        """
        try:
            if estado == "Todos":
                query = """
                SELECT 
                    CASE 
                        WHEN titulo_academico IS NULL OR titulo_academico = '' THEN 'No especificado'
                        ELSE titulo_academico 
                    END as titulo,
                    COUNT(*) as cantidad
                FROM docentes
                GROUP BY 
                    CASE 
                        WHEN titulo_academico IS NULL OR titulo_academico = '' THEN 'No especificado'
                        ELSE titulo_academico 
                    END
                ORDER BY cantidad DESC
                """
                params = ()
            else:
                query = """
                SELECT 
                    CASE 
                        WHEN titulo_academico IS NULL OR titulo_academico = '' THEN 'No especificado'
                        ELSE titulo_academico 
                    END as titulo,
                    COUNT(*) as cantidad
                FROM docentes
                WHERE estado = %s
                GROUP BY 
                    CASE 
                        WHEN titulo_academico IS NULL OR titulo_academico = '' THEN 'No especificado'
                        ELSE titulo_academico 
                    END
                ORDER BY cantidad DESC
                """
                params = (estado,)

            return self.execute_query(query, params)
        except Exception as e:
            print(f"Error obteniendo docentes por título académico: {e}")
            return []

    def get_docentes_por_rango_experiencia(self, estado="Activo"):
        """
        Obtiene distribución de docentes por rango de experiencia (basado en fecha_ingreso)
        Args:
            estado: Filtrar por estado
        Returns:
            Lista de diccionarios con rango de experiencia y cantidad
        """
        try:
            if estado == "Todos":
                query = """
                SELECT 
                    CASE 
                        WHEN fecha_ingreso IS NULL THEN 'Sin fecha de ingreso'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_ingreso)) < 1 THEN 'Menos de 1 año'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_ingreso)) BETWEEN 1 AND 5 THEN '1-5 años'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_ingreso)) BETWEEN 6 AND 10 THEN '6-10 años'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_ingreso)) BETWEEN 11 AND 20 THEN '11-20 años'
                        ELSE 'Más de 20 años'
                    END as rango_experiencia,
                    COUNT(*) as cantidad
                FROM docentes
                GROUP BY 
                    CASE 
                        WHEN fecha_ingreso IS NULL THEN 'Sin fecha de ingreso'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_ingreso)) < 1 THEN 'Menos de 1 año'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_ingreso)) BETWEEN 1 AND 5 THEN '1-5 años'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_ingreso)) BETWEEN 6 AND 10 THEN '6-10 años'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_ingreso)) BETWEEN 11 AND 20 THEN '11-20 años'
                        ELSE 'Más de 20 años'
                    END
                ORDER BY cantidad DESC
                """
                params = ()
            else:
                query = """
                SELECT 
                    CASE 
                        WHEN fecha_ingreso IS NULL THEN 'Sin fecha de ingreso'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_ingreso)) < 1 THEN 'Menos de 1 año'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_ingreso)) BETWEEN 1 AND 5 THEN '1-5 años'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_ingreso)) BETWEEN 6 AND 10 THEN '6-10 años'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_ingreso)) BETWEEN 11 AND 20 THEN '11-20 años'
                        ELSE 'Más de 20 años'
                    END as rango_experiencia,
                    COUNT(*) as cantidad
                FROM docentes
                WHERE estado = %s
                GROUP BY 
                    CASE 
                        WHEN fecha_ingreso IS NULL THEN 'Sin fecha de ingreso'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_ingreso)) < 1 THEN 'Menos de 1 año'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_ingreso)) BETWEEN 1 AND 5 THEN '1-5 años'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_ingreso)) BETWEEN 6 AND 10 THEN '6-10 años'
                        WHEN EXTRACT(YEAR FROM AGE(fecha_ingreso)) BETWEEN 11 AND 20 THEN '11-20 años'
                        ELSE 'Más de 20 años'
                    END
                ORDER BY cantidad DESC
                """
                params = (estado,)

            return self.execute_query(query, params)
        except Exception as e:
            print(f"Error obteniendo docentes por rango de experiencia: {e}")
            return []

    def get_estadisticas_mensuales(self, año=None, estado="Activo"):
        """
        Obtiene estadísticas mensuales de registros de docentes
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
                FROM docentes
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
                FROM docentes
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
                query = (
                    "SELECT COUNT(*) as count FROM docentes WHERE ci = %s AND id != %s"
                )
                params = (ci, exclude_id)
            else:
                query = "SELECT COUNT(*) as count FROM docentes WHERE ci = %s"
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
                query = "SELECT COUNT(*) as count FROM docentes WHERE email = %s AND id != %s"
                params = (email, exclude_id)
            else:
                query = "SELECT COUNT(*) as count FROM docentes WHERE email = %s"
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

    def obtener_por_id(self, docente_id):
        """Método de compatibilidad con nombres antiguos"""
        return self.read(docente_id)

    def buscar_docentes(self, termino):
        """Método de compatibilidad con nombres antiguos"""
        return self.search(termino)
