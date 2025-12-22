# models/__init__.py
"""
Paquete de modelos de FormaGestPro_MVC
Usando SQLite3 directamente
"""

from .base_model import BaseModel
from .estudiante import EstudianteModel
from .docente import DocenteModel
from .programa import ProgramaModel, EstadoPrograma
from .matricula import MatriculaModel
from .pago import PagoModel
from .cuota import CuotaModel
from .plan_pago import PlanPagoModel

__all__ = [
    'BaseModel',
    'EstudianteModel',
    'DocenteModel',
    'ProgramaModel',
    'EstadoPrograma',
    'MatriculaModel',
    'PagoModel',
    'CuotaModel',
    'PlanPagoModel'
]