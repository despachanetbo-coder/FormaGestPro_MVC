# app/models/__init__.py - VERSIÓN CORREGIDA
from .base_model import BaseModel
from .auditoria_transacciones_model import AuditoriaTransaccionesModel
from .comprobantes_adjuntos_model import ComprobantesAdjuntosModel
from .configuracion_model import ConfiguracionesModel
from .cuota_model import CuotaModel
from .estudiante_model import EstudianteModel
from .docente_model import DocenteModel
from .usuarios_model import UsuariosModel
from .programa_academico_model import ProgramasAcademicosModel as ProgramaAcademicoModel

# Para compatibilidad, también podemos exportarlo con ambos nombres
ProgramasAcademicosModel = ProgramaAcademicoModel

# Lista de todos los modelos para fácil importación
__all__ = [
    "BaseModel",
    "ProgramaAcademicoModel",
    "EstudianteModel",
    "DocenteModel",
    "UsuariosModel",
    "AuditoriaTransaccionesModel",
    "ComprobantesAdjuntosModel",
    "ConfiguracionesModel",
    "CuotaModel",
]
