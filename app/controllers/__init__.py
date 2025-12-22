# app/controllers/__init__.py
"""
Paquete de controladores de FormaGestPro_MVC
"""

# Importar controladores principales
from .estudiante_controller import EstudianteController
from .docente_form_controller import DocenteFormController 
from .programa_academico_controller import ProgramaAcademicoController
from .pago_controller import PagoController
from .matricula_controller import MatriculaController

# Intentar importar otros controladores opcionales
try:
    from .movimiento_caja_controller import MovimientoCajaController
except ImportError:
    MovimientoCajaController = None

try:
    from .usuarios_controller import UsuarioController
except ImportError:
    UsuarioController = None

try:
    from .comprobante_controller import ComprobanteController
except ImportError:
    ComprobanteController = None

try:
    from .gastos_operativos_controller import GastoOperativoController
except ImportError:
    GastoOperativoController = None

try:
    from .factura_controller import FacturaController
except ImportError:
    FacturaController = None

try:
    from .ingresos_genericos_controller import IngresoGenericoModel
except ImportError:
    IngresoGenericoModel = None

# Lista de controladores disponibles
__all__ = [
    'EstudianteController',
    'DocenteFormController',  # ¡CAMBIADO!
    'ProgramaAcademicoController',
    'PagoController',
    'MatriculaController',
    'MovimientoCajaController',
    'UsuarioController',
    'ComprobanteController',
    'GastoOperativoController',
    'FacturaController',
    'IngresoGenericoModel'
]

# Crear instancias preconfiguradas para acceso rápido
def create_controllers(db_path=None):
    """
    Crear instancias de todos los controladores
    
    Args:
        db_path: Ruta a la base de datos
        
    Returns:
        Diccionario con instancias de controladores
    """
    controllers = {
        'estudiante': EstudianteController(db_path),
        'docente': DocenteFormController(db_path),  # ¡CAMBIADO!
        'programa': ProgramaAcademicoController(db_path),
        'pago': PagoController(db_path),
        'matricula': MatriculaController(db_path)
    }
    
    # Agregar controladores opcionales si existen
    if MovimientoCajaController:
        controllers['caja'] = MovimientoCajaController(db_path)
    
    if UsuarioController:
        controllers['usuario'] = UsuarioController(db_path)
    
    if ComprobanteController:
        controllers['comprobante'] = ComprobanteController()
    
    if GastoOperativoController:
        controllers['gasto'] = GastoOperativoController(db_path)
    
    if FacturaController:
        controllers['factura'] = FacturaController(db_path)
    
    if IngresoGenericoModel:
        controllers['ingreso'] = IngresoGenericoModel(db_path)
    
    return controllers