"""
controllers/dashboard_controller.py
Versión ligera de DashboardController para compatibilidad
"""

import sys
import os

# Añadir ruta de la aplicación al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Intentar importar la versión principal
    from app.controllers.dashboard_controller import DashboardController, dashboard_controller
    print("✅ DashboardController importado desde app/controllers/")
    
except ImportError as e:
    print(f"⚠️  No se pudo importar DashboardController principal: {e}")
    
    # Versión mínima de respaldo
    class DashboardController:
        """Controlador mínimo para compatibilidad"""
        def __init__(self):
            print("⚠️  Usando DashboardController de respaldo")
        
        def obtener_datos_dashboard(self):
            """Retornar datos vacíos"""
            return {
                'total_estudiantes': 0,
                'total_docentes': 0,
                'programas_activos': 0,
                'programas_registrados_2025': 0,
                'ingresos_mes_actual': 0.0,
                'gastos_mes_actual': 0.0,
                'estudiantes_por_programa': {},
                'programas_en_progreso': [],
                'datos_financieros': [],
                'ultimos_estudiantes': [],
                'proximos_vencimientos': []
            }
    
    dashboard_controller = DashboardController()


# Exportar las mismas funciones que la versión principal
__all__ = ['DashboardController', 'dashboard_controller']