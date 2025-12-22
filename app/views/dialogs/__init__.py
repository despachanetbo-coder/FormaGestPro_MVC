# app/views/dialogs/__init__.py
"""
Paquete de diálogos de FormaGestPro_MVC
"""

# Importar diálogos con importaciones relativas correctas
try:
    from .estudiante_form_dialog import EstudianteFormDialog
except ImportError as e:
    print(f"⚠️ Error importando EstudianteFormDialog: {e}")
    EstudianteFormDialog = None

try:
    from .docente_form_dialog import DocenteFormDialog
except ImportError as e:
    print(f"⚠️ Error importando DocenteFormDialog: {e}")
    DocenteFormDialog = None

# Lista de diálogos disponibles
__all__ = [
    'EstudianteFormDialog',
    'DocenteFormDialog'
]