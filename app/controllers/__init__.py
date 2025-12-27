"""
Módulo de controladores - Todas las clases de controladores disponibles
"""

# Importar usando rutas relativas CORRECTAS
from .comprobante_controller import ComprobanteController
from .configuraciones_controller import ConfiguracionesController
from .dashboard_controller import DashboardController
from .docente_form_controller import DocenteFormController
from .estudiante_controller import EstudianteController
from .factura_controller import FacturaController
from .gasto_controller import GastoController
from .ingreso_controller import IngresoController
from .matricula_controller import MatriculaController
from .movimiento_caja_controller import MovimientoCajaController
from .plan_pago_controller import PlanPagoController
from .programa_academico_controller import ProgramaAcademicoController
from .shared_controller import SharedController
from .usuarios_controller import UsuariosController

# Lista de todos los controladores
__all__ = [
    'DashboardController',
    'EstudianteController',
    'DocenteFormController',
    'ProgramaAcademicoController',
    'MatriculaController',
    'PlanPagoController',
    'ComprobanteController',
    'FacturaController',
    'GastoController',
    'IngresoController',
    'MovimientoCajaController',
    'ConfiguracionesController',
    'UsuariosController',
    'SharedController',
]
