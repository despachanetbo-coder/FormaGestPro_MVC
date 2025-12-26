# app/controllers/dashboard_controller.py - Versión corregida
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.dashboard_model import DashboardModel
from app.models.estudiante_model import EstudianteModel
from app.models.docente_model import DocenteModel

# Eliminamos la importación de departamento_model y programa_model que no existen


class DashboardController:
    def __init__(self):
        """Inicializa el controlador con los modelos existentes"""
        self.dashboard_model = DashboardModel()
        self.estudiante_model = EstudianteModel()
        self.docente_model = DocenteModel()
        self._cache_estadisticas = {}
        self._cache_valida = False

    # ============ MÉTODOS PARA ESTUDIANTES ============

    def get_total_estudiantes(self, usar_cache=True):
        """Obtiene el total de estudiantes registrados"""
        if (
            usar_cache
            and "total_estudiantes" in self._cache_estadisticas
            and self._cache_valida
        ):
            return self._cache_estadisticas["total_estudiantes"]

        try:
            total = self.estudiante_model.get_total_estudiantes()
        except Exception as e:
            print(f"Error obteniendo total estudiantes: {e}")
            total = 0

        self._cache_estadisticas["total_estudiantes"] = total
        return total

    def get_estudiantes_por_genero(self, usar_cache=True):
        """Obtiene distribución de estudiantes por género"""
        if (
            usar_cache
            and "estudiantes_genero" in self._cache_estadisticas
            and self._cache_valida
        ):
            return self._cache_estadisticas["estudiantes_genero"]

        try:
            distribucion = self.estudiante_model.get_distribucion_genero()
        except Exception as e:
            print(f"Error obteniendo distribución por género: {e}")
            distribucion = []

        self._cache_estadisticas["estudiantes_genero"] = distribucion
        return distribucion

    def get_estudiantes_por_programa(self, usar_cache=True):
        """Obtiene estudiantes por programa usando dashboard_model"""
        if (
            usar_cache
            and "estudiantes_programa" in self._cache_estadisticas
            and self._cache_valida
        ):
            return self._cache_estadisticas["estudiantes_programa"]

        try:
            datos = self.dashboard_model.get_estudiantes_por_programa()
        except Exception as e:
            print(f"Error obteniendo estudiantes por programa: {e}")
            datos = []

        self._cache_estadisticas["estudiantes_programa"] = datos
        return datos

    def get_top_programas_estudiantes(self, limite=5):
        """Obtiene los programas con más estudiantes (top N)"""
        try:
            estudiantes_por_programa = self.get_estudiantes_por_programa(
                usar_cache=True
            )
            if not estudiantes_por_programa:
                return []

            # Ordenar por cantidad descendente y limitar
            sorted_data = sorted(
                estudiantes_por_programa,
                key=lambda x: x.get("cantidad", 0),
                reverse=True,
            )
            return sorted_data[:limite]
        except Exception as e:
            print(f"Error obteniendo top programas: {e}")
            return []

    # ============ MÉTODOS PARA DOCENTES ============

    def get_total_docentes(self, usar_cache=True):
        """Obtiene el total de docentes registrados"""
        if (
            usar_cache
            and "total_docentes" in self._cache_estadisticas
            and self._cache_valida
        ):
            return self._cache_estadisticas["total_docentes"]

        try:
            total = self.docente_model.get_total_docentes()
        except Exception as e:
            print(f"Error obteniendo total docentes: {e}")
            total = 0

        self._cache_estadisticas["total_docentes"] = total
        return total

    def get_docentes_por_genero(self, usar_cache=True):
        """Obtiene distribución de docentes por género"""
        if (
            usar_cache
            and "docentes_genero" in self._cache_estadisticas
            and self._cache_valida
        ):
            return self._cache_estadisticas["docentes_genero"]

        try:
            distribucion = self.docente_model.get_distribucion_genero()
        except Exception as e:
            print(f"Error obteniendo distribución docentes por género: {e}")
            distribucion = []

        self._cache_estadisticas["docentes_genero"] = distribucion
        return distribucion

    def get_docentes_por_departamento(self, usar_cache=True):
        """Obtiene docentes por departamento usando dashboard_model"""
        if (
            usar_cache
            and "docentes_departamento" in self._cache_estadisticas
            and self._cache_valida
        ):
            return self._cache_estadisticas["docentes_departamento"]

        try:
            datos = self.dashboard_model.get_docentes_por_departamento()
        except Exception as e:
            print(f"Error obteniendo docentes por departamento: {e}")
            datos = []

        self._cache_estadisticas["docentes_departamento"] = datos
        return datos

    def get_top_departamentos_docentes(self, limite=5):
        """Obtiene los departamentos con más docentes (top N)"""
        try:
            docentes_por_departamento = self.get_docentes_por_departamento(
                usar_cache=True
            )
            if not docentes_por_departamento:
                return []

            # Ordenar por cantidad descendente y limitar
            sorted_data = sorted(
                docentes_por_departamento,
                key=lambda x: x.get("cantidad", 0),
                reverse=True,
            )
            return sorted_data[:limite]
        except Exception as e:
            print(f"Error obteniendo top departamentos: {e}")
            return []

    # ============ MÉTODOS PARA CURSOS ============

    def get_cursos_activos(self, usar_cache=True):
        """Obtiene número de cursos activos"""
        if (
            usar_cache
            and "cursos_activos" in self._cache_estadisticas
            and self._cache_valida
        ):
            return self._cache_estadisticas["cursos_activos"]

        try:
            total = self.dashboard_model.get_cursos_activos()
        except Exception as e:
            print(f"Error obteniendo cursos activos: {e}")
            total = 0

        self._cache_estadisticas["cursos_activos"] = total
        return total

    def get_total_cursos(self, usar_cache=True):
        """Obtiene el total de cursos (activos e inactivos)"""
        if (
            usar_cache
            and "total_cursos" in self._cache_estadisticas
            and self._cache_valida
        ):
            return self._cache_estadisticas["total_cursos"]

        try:
            # Si dashboard_model no tiene este método, lo calculamos de otra forma
            if hasattr(self.dashboard_model, "get_total_cursos"):
                total = self.dashboard_model.get_total_cursos()
            else:
                # Alternativa: podríamos hacer una consulta directa si es necesario
                total = self.cursos_activos()  # Por ahora usamos solo activos
        except Exception as e:
            print(f"Error obteniendo total cursos: {e}")
            total = 0

        self._cache_estadisticas["total_cursos"] = total
        return total

    # ============ MÉTODOS PARA RESUMEN/ESTADÍSTICAS GENERALES ============

    def get_estadisticas_resumen(self, actualizar_cache=False):
        """
        Obtiene todas las estadísticas clave en un solo dict
        Usa cache por defecto para mejorar el rendimiento
        """
        if actualizar_cache:
            self._cache_valida = False
            self._cache_estadisticas.clear()

        if not self._cache_valida:
            self._actualizar_cache_completo()

        return {
            "resumen": {
                "total_estudiantes": self.get_total_estudiantes(usar_cache=True),
                "total_docentes": self.get_total_docentes(usar_cache=True),
                "cursos_activos": self.get_cursos_activos(usar_cache=True),
                "total_cursos": self.get_total_cursos(usar_cache=True),
            },
            "distribuciones": {
                "estudiantes_genero": self.get_estudiantes_por_genero(usar_cache=True),
                "docentes_genero": self.get_docentes_por_genero(usar_cache=True),
                "estudiantes_programa": self.get_top_programas_estudiantes(),
                "docentes_departamento": self.get_top_departamentos_docentes(),
            },
        }

    def _actualizar_cache_completo(self):
        """Actualiza toda la cache en una sola operación para eficiencia"""
        try:
            # Obtener todos los datos necesarios
            estadisticas = {
                "total_estudiantes": self.estudiante_model.get_total_estudiantes(),
                "total_docentes": self.docente_model.get_total_docentes(),
                "cursos_activos": self.dashboard_model.get_cursos_activos(),
                "estudiantes_genero": self.estudiante_model.get_distribucion_genero(),
                "docentes_genero": self.docente_model.get_distribucion_genero(),
                "estudiantes_programa": self.dashboard_model.get_estudiantes_por_programa(),
                "docentes_departamento": self.dashboard_model.get_docentes_por_departamento(),
            }

            # Intentar obtener total cursos si el método existe
            if hasattr(self.dashboard_model, "get_total_cursos"):
                estadisticas["total_cursos"] = self.dashboard_model.get_total_cursos()
            else:
                estadisticas["total_cursos"] = estadisticas.get("cursos_activos", 0)

            self._cache_estadisticas = estadisticas
            self._cache_valida = True
        except Exception as e:
            print(f"Error actualizando cache: {e}")
            self._cache_valida = False

    def invalidar_cache(self):
        """Marca la cache como inválida para forzar una actualización"""
        self._cache_valida = False

    def actualizar_datos(self):
        """Actualiza todos los datos (fuerza recarga de cache)"""
        self.invalidar_cache()
        return self.get_estadisticas_resumen(actualizar_cache=True)

    # ============ MÉTODOS DE FORMATO PARA UI ============

    def get_datos_para_grafico_pastel(self, datos, titulo):
        """
        Formatea datos para gráficos de pastel
        Args:
            datos: Lista de dicts con claves 'nombre' (o similar) y 'cantidad'
            titulo: Título para el gráfico
        Returns:
            Dict con labels, values y título
        """
        if not datos:
            return {"labels": [], "values": [], "titulo": titulo}

        labels = []
        values = []

        for item in datos:
            # Manejar diferentes posibles nombres de columna
            nombre = (
                item.get("programa")
                or item.get("departamento")
                or item.get("genero")
                or item.get("nombre", "")
            )
            cantidad = item.get("cantidad", 0)

            if nombre and cantidad > 0:
                labels.append(str(nombre))
                values.append(int(cantidad))

        return {"labels": labels, "values": values, "titulo": titulo}

    def get_datos_para_grafico_barras(
        self, datos, titulo, eje_x="Categoría", eje_y="Cantidad"
    ):
        """
        Formatea datos para gráficos de barras
        Args:
            datos: Lista de dicts con claves 'nombre' (o similar) y 'cantidad'
            titulo: Título para el gráfico
        Returns:
            Dict con labels, values y metadatos
        """
        if not datos:
            return {
                "labels": [],
                "values": [],
                "titulo": titulo,
                "eje_x": eje_x,
                "eje_y": eje_y,
            }

        labels = []
        values = []

        for item in datos:
            # Manejar diferentes posibles nombres de columna
            nombre = (
                item.get("programa")
                or item.get("departamento")
                or item.get("genero")
                or item.get("nombre", "")
            )
            cantidad = item.get("cantidad", 0)

            if nombre:
                labels.append(str(nombre))
                values.append(int(cantidad))

        return {
            "labels": labels,
            "values": values,
            "titulo": titulo,
            "eje_x": eje_x,
            "eje_y": eje_y,
        }

    def get_metricas_principales(self):
        """Obtiene las métricas principales para mostrar en tarjetas/KPIs"""
        try:
            resumen = self.get_estadisticas_resumen()["resumen"]
        except Exception as e:
            print(f"Error obteniendo métricas principales: {e}")
            resumen = {
                "total_estudiantes": 0,
                "total_docentes": 0,
                "cursos_activos": 0,
                "total_cursos": 0,
            }

        return [
            {
                "titulo": "Estudiantes",
                "valor": resumen["total_estudiantes"],
                "icono": "👨‍🎓",
                "color": "#3498db",  # blue
            },
            {
                "titulo": "Docentes",
                "valor": resumen["total_docentes"],
                "icono": "👨‍🏫",
                "color": "#2ecc71",  # green
            },
            {
                "titulo": "Cursos Activos",
                "valor": resumen["cursos_activos"],
                "icono": "📚",
                "color": "#e67e22",  # orange
            },
            {
                "titulo": "Total Cursos",
                "valor": resumen["total_cursos"],
                "icono": "📖",
                "color": "#9b59b6",  # purple
            },
        ]

    # ============ MÉTODOS DE COMPATIBILIDAD ============

    def cursos_activos(self):
        """Método de compatibilidad con nombres antiguos"""
        return self.get_cursos_activos()

    def total_estudiantes(self):
        """Método de compatibilidad con nombres antiguos"""
        return self.get_total_estudiantes()

    def total_docentes(self):
        """Método de compatibilidad con nombres antiguos"""
        return self.get_total_docentes()
