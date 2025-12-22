# services/gasto_service.py
"""
Servicio para manejar la lógica de negocio de Gastos Operativos.
"""
import logging
from datetime import datetime
from models.gasto_operativo import GastoOperativoModel

logger = logging.getLogger(__name__)

class GastoService:
    """Servicio para operaciones relacionadas con gastos"""
    
    @staticmethod
    def registrar_gasto(fecha, monto, categoria, subcategoria=None, 
                       descripcion=None, proveedor=None, nro_factura=None,
                       forma_pago='EFECTIVO', comprobante_nro=None):
        """
        Registra un nuevo gasto operativo.
        
        Returns:
            GastoOperativoModel: El gasto registrado
        """
        try:
            # Validar monto positivo
            if monto <= 0:
                raise ValueError("El monto debe ser mayor a 0")
            
            # Crear el gasto
            gasto_data = {
                'fecha': fecha,
                'monto': monto,
                'categoria': categoria,
                'subcategoria': subcategoria,
                'descripcion': descripcion,
                'proveedor': proveedor,
                'nro_factura': nro_factura,
                'forma_pago': forma_pago,
                'comprobante_nro': comprobante_nro
            }
            
            gasto = GastoOperativoModel(**gasto_data)
            gasto.save()
            
            logger.info(f"✅ Gasto registrado: {gasto.id} - ${monto:.2f} - {categoria}")
            return gasto
            
        except Exception as e:
            logger.error(f"❌ Error al registrar gasto: {e}")
            raise
    
    @staticmethod
    def obtener_gastos_por_fecha(fecha):
        """Obtiene gastos de una fecha específica"""
        return GastoOperativoModel.buscar_por_fecha(fecha)
    
    @staticmethod
    def obtener_gastos_por_categoria(categoria):
        """Obtiene gastos por categoría"""
        return GastoOperativoModel.buscar_por_categoria(categoria)
    
    @staticmethod
    def obtener_resumen_por_categoria(mes=None, año=None):
        """Obtiene un resumen de gastos por categoría"""
        return GastoOperativoModel.obtener_total_por_categoria(mes, año)
    
    @staticmethod
    def obtener_total_gastos(mes=None, año=None):
        """Calcula el total de gastos, opcionalmente por mes/año"""
        from database.database import db
        
        if mes and año:
            query = """
            SELECT SUM(monto) as total
            FROM gastos_operativos
            WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
            """
            params = (str(año), f"{mes:02d}")
        else:
            query = "SELECT SUM(monto) as total FROM gastos_operativos"
            params = ()
        
        result = db.fetch_one(query, params)
        return result['total'] if result and result['total'] else 0.0