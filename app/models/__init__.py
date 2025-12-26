# app/models/__init__.py
"""
Paquete de modelos de FormaGestPro_MVC
Usando SQLite3 directamente
"""

from .base_model import BaseModel
from .estudiante_model import EstudianteModel
from .docente_model import DocenteModel
from .programa_academico_model import (
    ProgramaAcademicoModel,
    EstadoPrograma,
    ExpedicionCI,
    GradoAcademico,
)
from .matricula_model import MatriculaModel
from .ingreso_model import IngresoModel
from .gasto_model import GastoModel
from .cuota_model import CuotaModel
from .plan_pago_model import PlanPagoModel
from .configuracion_model import ConfiguracionModel

__all__ = [
    "BaseModel",
    "EstudianteModel",
    "DocenteModel",
    "ProgramaAcademicoModel",
    "EstadoPrograma",
    "ExpedicionCI",
    "GradoAcademico",
    "MatriculaModel",
    "IngresoModel",
    "GastoModel",
    "CuotaModel",
    "PlanPagoModel",
    "ConfiguracionModel",
]
