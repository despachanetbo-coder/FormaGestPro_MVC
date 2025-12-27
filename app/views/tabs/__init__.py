"""
Módulo de pestañas - Todas las clases de pestañas disponibles
"""

# Importar usando rutas relativas CORRECTAS
from .base_tab import BaseTab
from .ayuda_tab import AyudaTab
from .dashboard_tab import DashboardTab
from .docentes_tab import DocentesTab
from .estudiantes_tab import EstudiantesTab
from .financiero_tab import FinancieroTab
from .programas_tab import ProgramasTab

# Lista de todas las pestañas
__all__ = [
    'BaseTab',
    'DashboardTab',
    'EstudiantesTab',
    'DocentesTab',
    'ProgramasTab',
    'FinancieroTab',
    'AyudaTab',
]
