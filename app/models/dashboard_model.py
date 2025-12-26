# app/models/dashboard_model.py - Versión completa y optimizada
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_model import BaseModel
from datetime import datetime


class DashboardModel(BaseModel):
    def __init__(self):
        """Inicializa el modelo del dashboard"""
        super().__init__()
        self._ensure_connection()

    def _ensure_connection(self):
        """Asegura que hay una conexión activa a la base de datos"""
        if not hasattr(self, "connection") or self.connection is None:
            from app.database.connection import PostgreSQLConnection

            self.connection = PostgreSQLConnection().get_connection()

    # ============ MÉTODOS PARA ESTUDIANTES ============

    def get_estudiantes_por_programa(self, estado="Activo", limit=10):
        """
        Obtiene la cantidad de estudiantes por programa
        Args:
            estado: Filtrar por estado (Activo/Inactivo/Todos)
            limit: Límite de resultados a retornar
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

    def execute_query(self, query, params=None, fetch=True, commit=False):
        """
        Ejecuta una consulta SQL
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta (tupla o lista)
            fetch: Si es True, retorna resultados de SELECT
            commit: Si es True, hace commit de la transacción
        Returns:
            Resultados de la consulta o None
        """
        return BaseModel.execute_query(query, params)

    def get_total_estudiantes_por_programa(self, programa_id, estado="Activo"):
        """
        Obtiene el total de estudiantes de un programa específico
        Args:
            programa_id: ID del programa
            estado: Estado de los estudiantes
        Returns:
            Número total de estudiantes en el programa
        """
        try:
            if estado == "Todos":
                query = """
                SELECT COUNT(*) as total
                FROM estudiantes
                WHERE programa_id = %s
                """
                params = (programa_id,)
            else:
                query = """
                SELECT COUNT(*) as total
                FROM estudiantes
                WHERE programa_id = %s AND estado = %s
                """
                params = (programa_id, estado)

            result = self.execute_query(query, params)
            return result[0]["total"] if result else 0
        except Exception as e:
            print(f"Error obteniendo total estudiantes por programa: {e}")
            return 0

    # ============ MÉTODOS PARA DOCENTES ============

    def get_docentes_por_departamento(self, estado="Activo", limit=10):
        """
        Obtiene la cantidad de docentes por departamento
        Args:
            estado: Filtrar por estado (Activo/Inactivo/Todos)
            limit: Límite de resultados a retornar
        Returns:
            Lista de diccionarios con departamento y cantidad
        """
        try:
            if estado == "Todos":
                query = """
                SELECT 
                    COALESCE(d.nombre, 'Sin departamento') as departamento,
                    COUNT(doc.id) as cantidad
                FROM docentes doc
                LEFT JOIN departamentos d ON doc.departamento_id = d.id
                GROUP BY d.nombre
                ORDER BY cantidad DESC
                LIMIT %s
                """
                params = (limit,)
            else:
                query = """
                SELECT 
                    COALESCE(d.nombre, 'Sin departamento') as departamento,
                    COUNT(doc.id) as cantidad
                FROM docentes doc
                LEFT JOIN departamentos d ON doc.departamento_id = d.id
                WHERE doc.estado = %s
                GROUP BY d.nombre
                ORDER BY cantidad DESC
                LIMIT %s
                """
                params = (estado, limit)

            return self.execute_query(query, params)
        except Exception as e:
            print(f"Error obteniendo docentes por departamento: {e}")
            return []

    def get_total_docentes_por_departamento(self, departamento_id, estado="Activo"):
        """
        Obtiene el total de docentes de un departamento específico
        Args:
            departamento_id: ID del departamento
            estado: Estado de los docentes
        Returns:
            Número total de docentes en el departamento
        """
        try:
            if estado == "Todos":
                query = """
                SELECT COUNT(*) as total
                FROM docentes
                WHERE departamento_id = %s
                """
                params = (departamento_id,)
            else:
                query = """
                SELECT COUNT(*) as total
                FROM docentes
                WHERE departamento_id = %s AND estado = %s
                """
                params = (departamento_id, estado)

            result = self.execute_query(query, params)
            return result[0]["total"] if result else 0
        except Exception as e:
            print(f"Error obteniendo total docentes por departamento: {e}")
            return 0

    # ============ MÉTODOS PARA CURSOS ============

    def get_cursos_activos(self):
        """
        Obtiene el número de cursos activos
        Returns:
            Número total de cursos activos
        """
        try:
            query = """
            SELECT COUNT(*) as total 
            FROM cursos 
            WHERE estado = 'Activo' OR estado = 'activo'
            """
            result = self.execute_query(query)
            return result[0]["total"] if result else 0
        except Exception as e:
            print(f"Error obteniendo cursos activos: {e}")
            return 0

    def get_total_cursos(self, estado="Todos"):
        """
        Obtiene el total de cursos
        Args:
            estado: Filtrar por estado (Activo/Inactivo/Todos)
        Returns:
            Número total de cursos
        """
        try:
            if estado == "Todos":
                query = "SELECT COUNT(*) as total FROM cursos"
                params = ()
            else:
                query = "SELECT COUNT(*) as total FROM cursos WHERE estado = %s"
                params = (estado,)

            result = self.execute_query(query, params)
            return result[0]["total"] if result else 0
        except Exception as e:
            print(f"Error obteniendo total cursos: {e}")
            return 0

    def get_cursos_por_estado(self):
        """
        Obtiene la distribución de cursos por estado
        Returns:
            Lista de diccionarios con estado y cantidad
        """
        try:
            query = """
            SELECT 
                estado,
                COUNT(*) as cantidad
            FROM cursos
            GROUP BY estado
            ORDER BY cantidad DESC
            """
            return self.execute_query(query)
        except Exception as e:
            print(f"Error obteniendo cursos por estado: {e}")
            return []

    def get_cursos_por_departamento(self, limit=10):
        """
        Obtiene la cantidad de cursos por departamento
        Args:
            limit: Límite de resultados
        Returns:
            Lista de diccionarios con departamento y cantidad
        """
        try:
            query = """
            SELECT 
                COALESCE(d.nombre, 'Sin departamento') as departamento,
                COUNT(c.id) as cantidad
            FROM cursos c
            LEFT JOIN departamentos d ON c.departamento_id = d.id
            WHERE c.estado = 'Activo'
            GROUP BY d.nombre
            ORDER BY cantidad DESC
            LIMIT %s
            """
            return self.execute_query(query, (limit,))
        except Exception as e:
            print(f"Error obteniendo cursos por departamento: {e}")
            return []

    # ============ MÉTODOS PARA ESTADÍSTICAS GENERALES ============

    def get_total_inscripciones(self):
        """
        Obtiene el total de inscripciones
        Returns:
            Número total de inscripciones
        """
        try:
            query = "SELECT COUNT(*) as total FROM inscripciones"
            result = self.execute_query(query)
            return result[0]["total"] if result else 0
        except Exception as e:
            print(f"Error obteniendo total inscripciones: {e}")
            return 0

    def get_inscripciones_activas(self):
        """
        Obtiene el total de inscripciones activas
        Returns:
            Número total de inscripciones activas
        """
        try:
            query = """
            SELECT COUNT(*) as total 
            FROM inscripciones 
            WHERE estado = 'Activo' OR estado = 'activo'
            """
            result = self.execute_query(query)
            return result[0]["total"] if result else 0
        except Exception as e:
            print(f"Error obteniendo inscripciones activas: {e}")
            return 0

    def get_top_cursos_populares(self, limit=5):
        """
        Obtiene los cursos más populares (con más inscripciones)
        Args:
            limit: Límite de cursos a mostrar
        Returns:
            Lista de diccionarios con curso y cantidad de inscripciones
        """
        try:
            query = """
            SELECT 
                c.nombre as curso,
                COUNT(i.id) as inscripciones
            FROM cursos c
            LEFT JOIN inscripciones i ON c.id = i.curso_id
            WHERE c.estado = 'Activo'
            GROUP BY c.id, c.nombre
            ORDER BY inscripciones DESC
            LIMIT %s
            """
            return self.execute_query(query, (limit,))
        except Exception as e:
            print(f"Error obteniendo cursos populares: {e}")
            return []

    # ============ MÉTODOS PARA ESTADÍSTICAS TEMPORALES ============

    def get_registros_mensuales(self, año=None, tipo="estudiantes"):
        """
        Obtiene registros mensuales por tipo
        Args:
            año: Año a consultar (None para año actual)
            tipo: Tipo de registros ('estudiantes', 'docentes', 'cursos')
        Returns:
            Lista de diccionarios con mes y cantidad
        """
        try:
            if año is None:
                año = datetime.now().year

            # Determinar la tabla según el tipo
            if tipo == "estudiantes":
                tabla = "estudiantes"
            elif tipo == "docentes":
                tabla = "docentes"
            elif tipo == "cursos":
                tabla = "cursos"
            else:
                raise ValueError(f"Tipo no válido: {tipo}")

            query = f"""
            SELECT 
                EXTRACT(MONTH FROM fecha_registro) as mes,
                COUNT(*) as cantidad
            FROM {tabla}
            WHERE EXTRACT(YEAR FROM fecha_registro) = %s
            GROUP BY EXTRACT(MONTH FROM fecha_registro)
            ORDER BY mes
            """

            return self.execute_query(query, (año,))
        except Exception as e:
            print(f"Error obteniendo registros mensuales: {e}")
            return []

    def get_estadisticas_crecimiento(self, tipo="estudiantes", meses=6):
        """
        Obtiene estadísticas de crecimiento
        Args:
            tipo: Tipo de entidad ('estudiantes', 'docentes', 'cursos')
            meses: Número de meses a considerar
        Returns:
            Diccionario con estadísticas de crecimiento
        """
        try:
            if tipo == "estudiantes":
                tabla = "estudiantes"
            elif tipo == "docentes":
                tabla = "docentes"
            elif tipo == "cursos":
                tabla = "cursos"
            else:
                raise ValueError(f"Tipo no válido: {tipo}")

            # Total actual
            query_total = f"SELECT COUNT(*) as total FROM {tabla}"
            result_total = self.execute_query(query_total)
            total_actual = result_total[0]["total"] if result_total else 0

            # Total hace X meses
            query_anterior = f"""
            SELECT COUNT(*) as total 
            FROM {tabla} 
            WHERE fecha_registro < CURRENT_DATE - INTERVAL '{meses} months'
            """
            result_anterior = self.execute_query(query_anterior)
            total_anterior = result_anterior[0]["total"] if result_anterior else 0

            # Calcular crecimiento
            if total_anterior > 0:
                crecimiento_porcentaje = (
                    (total_actual - total_anterior) / total_anterior
                ) * 100
            else:
                crecimiento_porcentaje = 100 if total_actual > 0 else 0

            return {
                "total_actual": total_actual,
                "total_anterior": total_anterior,
                "crecimiento_absoluto": total_actual - total_anterior,
                "crecimiento_porcentaje": round(crecimiento_porcentaje, 2),
                "periodo_meses": meses,
            }
        except Exception as e:
            print(f"Error obteniendo estadísticas de crecimiento: {e}")
            return {
                "total_actual": 0,
                "total_anterior": 0,
                "crecimiento_absoluto": 0,
                "crecimiento_porcentaje": 0,
                "periodo_meses": meses,
            }

    # ============ MÉTODOS PARA REPORTES ============

    def get_resumen_general(self):
        """
        Obtiene un resumen general de todas las estadísticas
        Returns:
            Diccionario con resumen completo
        """
        try:
            return {
                "estudiantes": {
                    "total": self.get_total_estudiantes_por_programa(None, "Todos"),
                    "activos": self.get_total_estudiantes_por_programa(None, "Activo"),
                    "por_programa": self.get_estudiantes_por_programa("Activo", 5),
                },
                "docentes": {
                    "total": self.get_total_docentes_por_departamento(None, "Todos"),
                    "activos": self.get_total_docentes_por_departamento(None, "Activo"),
                    "por_departamento": self.get_docentes_por_departamento("Activo", 5),
                },
                "cursos": {
                    "total": self.get_total_cursos("Todos"),
                    "activos": self.get_cursos_activos(),
                    "por_departamento": self.get_cursos_por_departamento(5),
                    "populares": self.get_top_cursos_populares(5),
                },
                "inscripciones": {
                    "total": self.get_total_inscripciones(),
                    "activas": self.get_inscripciones_activas(),
                },
            }
        except Exception as e:
            print(f"Error obteniendo resumen general: {e}")
            return {}

    # ============ MÉTODOS DE COMPATIBILIDAD ============

    def estudiantes_por_programa(self):
        """Método de compatibilidad con nombres antiguos"""
        return self.get_estudiantes_por_programa()

    def docentes_por_departamento(self):
        """Método de compatibilidad con nombres antiguos"""
        return self.get_docentes_por_departamento()

    def cursos_activos(self):
        """Método de compatibilidad con nombres antiguos"""
        return self.get_cursos_activos()
