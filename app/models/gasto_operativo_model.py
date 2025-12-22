# app/models/gasto_operativo.py
"""
Modelo para Gastos Operativos usando SQLite3 directamente.
"""
import logging
from datetime import datetime

from .movimiento_caja_model import MovimientoCajaModel
from .base_model import BaseModel

logger = logging.getLogger(__name__)

class GastoOperativoModel(BaseModel):
    """Modelo que representa un gasto operativo"""
    
    TABLE_NAME = "gastos_operativos"
    
    # Categorías predefinidas
    CATEGORIAS = [
        'PAGO_DOCENTE', 'ALQUILER', 'SERVICIOS_BASICOS', 'MATERIALES', 
        'PUBLICIDAD', 'TRANSPORTE', 'ALIMENTACION', 'OTROS'
    ]
    
    # Subcategorías opcionales
    SUBCATEGORIAS = {
        'PAGO_DOCENTE': ['HONORARIOS', 'BONOS', 'VIATICOS'],
        'SERVICIOS_BASICOS': ['LUZ', 'AGUA', 'INTERNET', 'TELEFONO'],
        'MATERIALES': ['OFICINA', 'EDUCATIVOS', 'LIMPEZA'],
        'PUBLICIDAD': ['REDES_SOCIALES', 'VOLANTES', 'CARTELES'],
        'TRANSPORTE': ['GASOLINA', 'PASAJES', 'MANTENIMIENTO'],
        'ALIMENTACION': ['REFRIGERIOS', 'ALMUERZOS'],
        'OTROS': ['GASTOS_ADMINISTRATIVOS', 'IMPUESTOS', 'SEGUROS']
    }
    
    FORMAS_PAGO = ['EFECTIVO', 'TRANSFERENCIA', 'TARJETA', 'CHEQUE']
    
    def __init__(self, **kwargs):
        """
        Inicializa un gasto operativo.

        Campos esperados:
            fecha, monto, categoria, subcategoria, descripcion,
            proveedor, nro_factura, forma_pago, comprobante_nro, docente_id
        """
        # Campos obligatorios
        self.fecha = kwargs.get('fecha', datetime.now().date().isoformat())
        self.monto = kwargs.get('monto', 0.0)
        self.categoria = kwargs.get('categoria')

        # Campos opcionales
        self.subcategoria = kwargs.get('subcategoria')
        self.descripcion = kwargs.get('descripcion', '')
        self.proveedor = kwargs.get('proveedor')
        self.nro_factura = kwargs.get('nro_factura')
        self.forma_pago = kwargs.get('forma_pago', 'EFECTIVO')
        self.comprobante_nro = kwargs.get('comprobante_nro')
        self.docente_id = kwargs.get('docente_id')  # <-- IMPORTANTE: Relación con docente

        # ID (si viene de la base de datos)
        if 'id' in kwargs:
            self.id = kwargs['id']

        # Validaciones
        self._validar()
    
    def _validar(self):
        """Valida los datos del gasto"""
        if self.monto <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        
        if self.categoria not in self.CATEGORIAS:
            raise ValueError(f"Categoría inválida. Válidas: {self.CATEGORIAS}")
        
        if self.subcategoria and self.categoria in self.SUBCATEGORIAS:
            if self.subcategoria not in self.SUBCATEGORIAS[self.categoria]:
                raise ValueError(f"Subcategoría inválida para {self.categoria}. Válidas: {self.SUBCATEGORIAS[self.categoria]}")
        
        if self.forma_pago not in self.FORMAS_PAGO:
            raise ValueError(f"Forma de pago inválida. Válidas: {self.FORMAS_PAGO}")
    
    def __repr__(self):
        return f"<Gasto {self.id}: ${self.monto:.2f} - {self.categoria}>"
    
    def save(self):
        """
        Guarda el gasto y registra automáticamente el movimiento de caja (EGRESO)
        """
        # Validación importante para gastos de PAGO_DOCENTE
        if self.categoria == 'PAGO_DOCENTE' and not self.docente_id:
            logger.warning("Gasto de PAGO_DOCENTE sin docente_id asignado")
            # Podrías opcionalmente lanzar una excepción si lo prefieres:
            # raise ValueError("Los gastos de PAGO_DOCENTE requieren docente_id")
    
        # Guardar primero para obtener ID si es nuevo
        gasto_id = super().save()
        
        # Registrar movimiento de caja (EGRESO)
        try:
            # Crear descripción para el movimiento
            descripcion = f"Gasto: {self.categoria}"
            if self.subcategoria:
                descripcion += f" - {self.subcategoria}"
            if self.descripcion:
                descripcion += f" ({self.descripcion[:30]})"
            
            # Si es pago a docente, agregar información del docente a la descripción
            if self.categoria == 'PAGO_DOCENTE' and self.docente_id:
                try:
                    from .docente_model import DocenteModel
                    docente = DocenteModel.find_by_id(self.docente_id)
                    if docente:
                        descripcion = f"Pago docente: {docente.nombre_completo}"
                except:
                    pass
                
            MovimientoCajaModel.registrar_egreso_gasto(
                gasto_id=self.id,
                monto=self.monto,
                descripcion=descripcion
            )
            logger.info(f"💰 Movimiento de caja (EGRESO) registrado automáticamente para gasto {self.id}")
            
        except Exception as e:
            logger.error(f"Error al registrar movimiento de caja para gasto {self.id}: {e}")
        
        return gasto_id
    
    @classmethod
    def buscar_por_fecha(cls, fecha):
        """Busca gastos por fecha"""
        from database.database import db
        
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE fecha = ? ORDER BY id DESC"
        rows = db.fetch_all(query, (fecha,))
        
        return [cls(**row) for row in rows]
    
    @classmethod
    def buscar_por_categoria(cls, categoria):
        """Busca gastos por categoría"""
        from database.database import db
        
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE categoria = ? ORDER BY fecha DESC"
        rows = db.fetch_all(query, (categoria,))
        
        return [cls(**row) for row in rows]
    
    @classmethod
    def obtener_total_por_categoria(cls, mes=None, año=None):
        """Obtiene el total de gastos por categoría, opcionalmente filtrado por mes y año"""
        from database.database import db
        
        if mes and año:
            query = """
            SELECT categoria, SUM(monto) as total
            FROM gastos_operativos
            WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
            GROUP BY categoria
            ORDER BY total DESC
            """
            params = (str(año), f"{mes:02d}")
        else:
            query = """
            SELECT categoria, SUM(monto) as total
            FROM gastos_operativos
            GROUP BY categoria
            ORDER BY total DESC
            """
            params = ()
        
        return db.fetch_all(query, params)