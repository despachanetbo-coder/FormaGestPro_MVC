# services/ingreso_service.py
"""
Servicio para manejar la lógica de negocio de Ingresos Genéricos.
"""
import logging
from datetime import datetime
from models.ingreso_generico import IngresoGenericoModel

logger = logging.getLogger(__name__)

class IngresoGenericoService:
    """Servicio para operaciones relacionadas con ingresos genéricos"""
    
    @staticmethod
    def registrar_ingreso(fecha, monto, concepto, descripcion=None,
                         forma_pago='EFECTIVO', comprobante_nro=None, registrado_por=None):
        """
        Registra un nuevo ingreso genérico.
        
        Returns:
            IngresoGenericoModel: El ingreso registrado
        """
        try:
            # Validar monto positivo
            if monto <= 0:
                raise ValueError("El monto debe ser mayor a 0")
            
            # Validar concepto no vacío
            if not concepto or concepto.strip() == '':
                raise ValueError("El concepto es obligatorio")
            
            # Crear el ingreso
            ingreso_data = {
                'fecha': fecha,
                'monto': monto,
                'concepto': concepto,
                'descripcion': descripcion,
                'forma_pago': forma_pago,
                'comprobante_nro': comprobante_nro,
                'registrado_por': registrado_por
            }
            
            ingreso = IngresoGenericoModel(**ingreso_data)
            ingreso.save()
            
            logger.info(f"✅ Ingreso genérico registrado: {ingreso.id} - ${monto:.2f} - {concepto}")
            return ingreso
            
        except Exception as e:
            logger.error(f"❌ Error al registrar ingreso genérico: {e}")
            raise
    
    @staticmethod
    def obtener_ingresos_por_fecha(fecha):
        """Obtiene ingresos de una fecha específica"""
        return IngresoGenericoModel.buscar_por_fecha(fecha)
    
    @staticmethod
    def obtener_ingresos_por_concepto(concepto):
        """Obtiene ingresos por concepto (búsqueda parcial)"""
        return IngresoGenericoModel.buscar_por_concepto(concepto)
    
    @staticmethod
    def obtener_ingresos_por_rango(fecha_inicio, fecha_fin):
        """Obtiene ingresos por rango de fechas"""
        return IngresoGenericoModel.buscar_por_rango_fechas(fecha_inicio, fecha_fin)
    
    @staticmethod
    def obtener_resumen_mensual(año=None, mes=None):
        """Obtiene un resumen de ingresos por mes"""
        return IngresoGenericoModel.obtener_total_por_mes(año, mes)
    
    @staticmethod
    def obtener_total_ingresos(mes=None, año=None):
        """Calcula el total de ingresos genéricos, opcionalmente por mes/año"""
        from database.database import db
        
        if mes and año:
            query = """
            SELECT SUM(monto) as total
            FROM ingresos_genericos
            WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
            """
            params = (str(año), f"{mes:02d}")
        else:
            query = "SELECT SUM(monto) as total FROM ingresos_genericos"
            params = ()
        
        result = db.fetch_one(query, params)
        return result['total'] if result and result['total'] else 0.0