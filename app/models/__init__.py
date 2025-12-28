"""
Módulo de modelos - Todas las clases de modelos disponibles
"""

# Importar usando rutas relativas CORRECTAS
from .base_model import BaseModel
from .auditoria_transacciones_model import AuditoriaTransaccionesModel
from .comprobantes_adjuntos_model import ComprobantesAdjuntosModel
from .configuracion_model import ConfiguracionesModel
from .cuota_model import CuotaModel
from .dashboard_model import DashboardModel
from .docente_model import DocenteModel
from .empresa_model import EmpresaModel
from .estudiante_model import EstudianteModel
from .facturas_model import FacturasModel
from .gasto_model import GastoModel
from .ingreso_model import IngresoModel
from .matricula_model import MatriculaModel
from .movimiento_caja_model import MovimientoCajaModel
from .plan_pago_model import PlanPagoModel
from .programa_academico_model import ProgramasAcademicosModel
from .usuarios_model import UsuariosModel

# Lista de todos los modelos para fácil importación
__all__ = [
    "BaseModel",  # Nombre singular para compatibilidad
    "ProgramasAcademicosModel",  # Nombre original (plural)
    "EstudianteModel",
    "DocenteModel",
    "MatriculaModel",
    "UsuariosModel",
    "EmpresaModel",
    "DashboardModel",
    "CuotaModel",
    "PlanPagoModel",
    "FacturasModel",
    "GastoModel",
    "IngresoModel",
    "MovimientoCajaModel",
    "ConfiguracionesModel",
    "AuditoriaTransaccionesModel",
    "ComprobantesAdjuntosModel",
]
