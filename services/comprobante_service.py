# services/comprobante_service.py
"""
Servicio para generar Comprobantes de Ingreso y Egreso en PDF.
"""
import os
import logging
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
import textwrap

from models.movimiento_caja import MovimientoCajaModel
from models.empresa import EmpresaModel
from models.pago import PagoModel
from models.matricula import MatriculaModel
from models.estudiante import EstudianteModel
from models.programa import ProgramaModel
from models.gasto_operativo import GastoOperativoModel

logger = logging.getLogger(__name__)

# Obtener la ruta del directorio del proyecto (2 niveles arriba de services/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPROBANTES_DIR = os.path.join(PROJECT_ROOT, "comprobantes")
os.makedirs(COMPROBANTES_DIR, exist_ok=True)
LOGO_PATH = os.path.join(PROJECT_ROOT, "assets", "images", "logo_empresa.png")

class ComprobanteService:
    """Servicio para generar comprobantes en PDF"""
    
    @staticmethod
    def obtener_detalles_movimiento(movimiento_id):
        """
        Obtiene detalles completos de un movimiento de caja para generar comprobante.
        
        Returns:
            dict: Detalles del movimiento con información relacionada
        """
        movimiento = MovimientoCajaModel.find_by_id(movimiento_id)
        if not movimiento:
            raise ValueError(f"Movimiento de caja {movimiento_id} no encontrado")
        
        detalles = {
            'movimiento': movimiento,
            'empresa': EmpresaModel.obtener_datos(),
            'tipo': movimiento.tipo,  # 'INGRESO' o 'EGRESO'
            'fecha': getattr(movimiento, 'fecha', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            'monto': movimiento.monto,
            'descripcion': movimiento.descripcion
        }
        
        # Si es un INGRESO (pago)
        if movimiento.tipo == 'INGRESO' and movimiento.referencia_tipo == 'PAGO':
            pago = PagoModel.find_by_id(movimiento.referencia_id)
            if pago:
                detalles['pago'] = pago
                
                # Obtener matrícula, estudiante y programa
                matricula = MatriculaModel.find_by_id(pago.matricula_id)
                if matricula:
                    detalles['matricula'] = matricula
                    
                    estudiante = EstudianteModel.find_by_id(matricula.estudiante_id)
                    if estudiante:
                        detalles['estudiante'] = estudiante
                    
                    programa = ProgramaModel.find_by_id(matricula.programa_id)
                    if programa:
                        detalles['programa'] = programa
        
        # Si es un EGRESO (gasto)
        elif movimiento.tipo == 'EGRESO' and movimiento.referencia_tipo == 'GASTO':
            gasto = GastoOperativoModel.find_by_id(movimiento.referencia_id)
            if gasto:
                detalles['gasto'] = gasto
        
        # Si es un INGRESO_GENERICO (ingreso genérico)
        elif movimiento.tipo == 'INGRESO' and movimiento.referencia_tipo == 'INGRESO_GENERICO':
            from models.ingreso_generico import IngresoGenericoModel
            ingreso = IngresoGenericoModel.find_by_id(movimiento.referencia_id)
            if ingreso:
                detalles['ingreso_generico'] = ingreso
        
        return detalles
    
    @staticmethod
    def generar_comprobante_ingreso_pdf(detalles, output_path):
        """
        Genera un PDF de Comprobante de Ingreso.
        
        Args:
            detalles: Dict con detalles del movimiento
            output_path: Ruta donde guardar el PDF
        """
        movimiento = detalles['movimiento']
        empresa = detalles['empresa']
        pago = detalles.get('pago')
        estudiante = detalles.get('estudiante')
        programa = detalles.get('programa')
        ingreso_generico = detalles.get('ingreso_generico')
        
        # Crear PDF
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        
        # --- ENCABEZADO ---
        # Fondo de color para el encabezado
        c.setFillColor(HexColor("#2E86AB"))  # Azul profesional
        c.rect(0, height - 150, width, 150, fill=True, stroke=False)
        
        # Logo (si existe)
        logo_path = ComprobanteService.obtener_ruta_logo()
        if logo_path:
            try:
                logo = ImageReader(logo_path)
                c.drawImage(logo, 50, height - 120, width=1.2*inch, height=1.2*inch, preserveAspectRatio=True)
            except Exception as e:
                logger.error(f"No se pudo cargar el logo: {e}")
        
        # Título en blanco sobre fondo azul
        c.setFillColor(HexColor("#FFFFFF"))
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width/2, height - 70, "COMPROBANTE DE INGRESO")
        
        # Subtítulo
        c.setFont("Helvetica", 12)
        c.drawCentredString(width/2, height - 95, "Documento Válido como Recibo de Pago")
        
        # --- INFORMACIÓN DE LA EMPRESA ---
        c.setFillColor(HexColor("#000000"))
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 160, empresa.nombre if empresa else "FORMACIÓN CONTINUA CONSULTORA")
        
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 175, f"NIT: {empresa.nit if empresa and hasattr(empresa, 'nit') else '1234567012'}")
        if empresa and hasattr(empresa, 'direccion') and empresa.direccion:
            c.drawString(50, height - 190, f"Dirección: {empresa.direccion}")
        if empresa and hasattr(empresa, 'telefono') and empresa.telefono:
            c.drawString(50, height - 205, f"Teléfono: {empresa.telefono}")
        
        # --- INFORMACIÓN DEL COMPROBANTE ---
        y_pos = height - 220
        
        # Marco para información del comprobante
        c.setStrokeColor(HexColor("#2E86AB"))
        c.setLineWidth(1)
        c.rect(50, y_pos - 100, width - 100, 100)
        
        c.setFillColor(HexColor("#000000"))
        c.setFont("Helvetica-Bold", 14)
        c.drawString(60, y_pos - 20, "INFORMACIÓN DEL COMPROBANTE")
        
        c.setFont("Helvetica", 10)
        c.drawString(60, y_pos - 40, f"N° de Comprobante: CI-{movimiento.id:06d}")
        c.drawString(60, y_pos - 55, f"Fecha: {movimiento.fecha.split(' ')[0] if ' ' in movimiento.fecha else movimiento.fecha}")
        c.drawString(60, y_pos - 70, f"Hora: {movimiento.fecha.split(' ')[1] if ' ' in movimiento.fecha else '00:00:00'}")
        
        # Determinar forma de pago según el tipo de ingreso
        forma_pago = 'EFECTIVO'
        if pago:
            forma_pago = pago.forma_pago
        elif ingreso_generico:
            forma_pago = ingreso_generico.forma_pago
            
        c.drawString(width - 200, y_pos - 40, f"Tipo: INGRESO")
        c.drawString(width - 200, y_pos - 55, f"Forma Pago: {forma_pago}")
        
        # --- DETALLES DEL INGRESO ---
        y_pos = y_pos - 120
        
        c.setFont("Helvetica-Bold", 14)
        if pago:
            c.drawString(60, y_pos, "DETALLES DEL PAGO")
        else:
            c.drawString(60, y_pos, "DETALLES DEL INGRESO")
        
        c.setFont("Helvetica", 10)
        c.drawString(60, y_pos - 20, f"Monto: ${movimiento.monto:.2f}")
        c.drawString(60, y_pos - 35, f"Descripción: {movimiento.descripcion}")
        
        if pago:
            if pago.nro_cuota:
                c.drawString(60, y_pos - 50, f"N° Cuota: {pago.nro_cuota}")
            if pago.nro_comprobante:
                c.drawString(60, y_pos - 65, f"N° Comprobante: {pago.nro_comprobante}")
            if pago.nro_transaccion:
                c.drawString(60, y_pos - 80, f"N° Transacción: {pago.nro_transaccion}")
        
        elif ingreso_generico:
            c.drawString(60, y_pos - 50, f"Concepto: {ingreso_generico.concepto}")
            if ingreso_generico.descripcion:
                # Manejo de descripción larga
                desc_lines = textwrap.wrap(ingreso_generico.descripcion, width=60)
                for i, line in enumerate(desc_lines):
                    c.drawString(60, y_pos - 65 - (i * 15), line)
            if ingreso_generico.comprobante_nro:
                c.drawString(60, y_pos - 95, f"N° Comprobante: {ingreso_generico.comprobante_nro}")
        
        # --- INFORMACIÓN DEL ESTUDIANTE (solo para pagos) ---
        if estudiante:
            y_pos = y_pos - 110 if ingreso_generico else y_pos - 95
            
            c.setFont("Helvetica-Bold", 14)
            c.drawString(60, y_pos, "INFORMACIÓN DEL ESTUDIANTE")
            
            c.setFont("Helvetica", 10)
            c.drawString(60, y_pos - 20, f"Nombre: {estudiante.nombres} {estudiante.apellidos}")
            c.drawString(60, y_pos - 35, f"CI: {estudiante.ci_numero} {estudiante.ci_expedicion if estudiante.ci_expedicion else ''}")
            if estudiante.email:
                c.drawString(60, y_pos - 50, f"Email: {estudiante.email}")
            
            if programa:
                c.drawString(60, y_pos - 65, f"Programa: {programa.nombre}")
        
        # --- FIRMAS Y SELLOS ---
        y_pos = 150
        
        # Línea para firma
        c.setStrokeColor(HexColor("#000000"))
        c.setLineWidth(0.5)
        c.line(100, y_pos, 300, y_pos)
        
        c.setFont("Helvetica", 10)
        c.drawCentredString(200, y_pos - 15, "Firma Autorizada")
        
        # Sello de la empresa
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(HexColor("#2E86AB"))
        c.drawCentredString(width/2, y_pos - 40, "FORMACIÓN CONTINUA CONSULTORA")
        c.setFillColor(HexColor("#000000"))
        c.drawCentredString(width/2, y_pos - 55, "Sistema de Gestión Académica")
        
        # Pie de página
        c.setFont("Helvetica", 8)
        c.drawCentredString(width/2, 30, "Este documento es válido como comprobante de ingreso. Conserve este comprobante.")
        c.drawCentredString(width/2, 20, f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Guardar PDF
        c.save()
        
        return output_path
    
    @staticmethod
    def generar_comprobante_egreso_pdf(detalles, output_path):
        """
        Genera un PDF de Comprobante de Egreso.
        
        Args:
            detalles: Dict con detalles del movimiento
            output_path: Ruta donde guardar el PDF
        """
        movimiento = detalles['movimiento']
        empresa = detalles['empresa']
        gasto = detalles.get('gasto')
        
        # Crear PDF
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        
        # --- ENCABEZADO ---
        # Fondo de color para el encabezado
        c.setFillColor(HexColor("#AB2E2E"))  # Rojo para egresos
        c.rect(0, height - 150, width, 150, fill=True, stroke=False)
        
        # Logo (si existe)
        logo_path = ComprobanteService.obtener_ruta_logo()
        if logo_path:
            try:
                logo = ImageReader(logo_path)
                c.drawImage(logo, 50, height - 120, width=1.2*inch, height=1.2*inch, preserveAspectRatio=True)
            except Exception as e:
                logger.error(f"No se pudo cargar el logo: {e}")
        
        # Título en blanco sobre fondo rojo
        c.setFillColor(HexColor("#FFFFFF"))
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width/2, height - 70, "COMPROBANTE DE EGRESO")
        
        # Subtítulo
        c.setFont("Helvetica", 12)
        c.drawCentredString(width/2, height - 95, "Documento de Egreso - Control Interno")
        
        # --- INFORMACIÓN DE LA EMPRESA ---
        c.setFillColor(HexColor("#000000"))
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 160, empresa.nombre if empresa else "FORMACIÓN CONTINUA CONSULTORA")
        
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 175, f"NIT: {empresa.nit if empresa and hasattr(empresa, 'nit') else '1234567012'}")
        if empresa and hasattr(empresa, 'direccion') and empresa.direccion:
            c.drawString(50, height - 190, f"Dirección: {empresa.direccion}")
        if empresa and hasattr(empresa, 'telefono') and empresa.telefono:
            c.drawString(50, height - 205, f"Teléfono: {empresa.telefono}")
        
        # --- INFORMACIÓN DEL COMPROBANTE ---
        y_pos = height - 220
        
        # Marco para información del comprobante
        c.setStrokeColor(HexColor("#AB2E2E"))
        c.setLineWidth(1)
        c.rect(50, y_pos - 100, width - 100, 100)
        
        c.setFillColor(HexColor("#000000"))
        c.setFont("Helvetica-Bold", 14)
        c.drawString(60, y_pos - 20, "INFORMACIÓN DEL COMPROBANTE")
        
        c.setFont("Helvetica", 10)
        c.drawString(60, y_pos - 40, f"N° de Comprobante: CE-{movimiento.id:06d}")
        c.drawString(60, y_pos - 55, f"Fecha: {movimiento.fecha.split(' ')[0] if ' ' in movimiento.fecha else movimiento.fecha}")
        c.drawString(60, y_pos - 70, f"Hora: {movimiento.fecha.split(' ')[1] if ' ' in movimiento.fecha else '00:00:00'}")
        
        c.drawString(width - 200, y_pos - 40, f"Tipo: EGRESO")
        if gasto:
            c.drawString(width - 200, y_pos - 55, f"Forma Pago: {gasto.forma_pago}")
        
        # --- DETALLES DEL EGRESO ---
        y_pos = y_pos - 120
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(60, y_pos, "DETALLES DEL EGRESO")
        
        c.setFont("Helvetica", 10)
        c.drawString(60, y_pos - 20, f"Monto: ${movimiento.monto:.2f}")
        c.drawString(60, y_pos - 35, f"Descripción: {movimiento.descripcion}")
        
        if gasto:
            c.drawString(60, y_pos - 50, f"Categoría: {gasto.categoria}")
            if gasto.subcategoria:
                c.drawString(60, y_pos - 65, f"Subcategoría: {gasto.subcategoria}")
            if gasto.proveedor:
                c.drawString(60, y_pos - 80, f"Proveedor: {gasto.proveedor}")
            if gasto.nro_factura:
                c.drawString(60, y_pos - 95, f"N° Factura: {gasto.nro_factura}")
            if gasto.comprobante_nro:
                c.drawString(60, y_pos - 110, f"N° Comprobante: {gasto.comprobante_nro}")
        
        # --- JUSTIFICACIÓN ---
        y_pos = y_pos - 130
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(60, y_pos, "JUSTIFICACIÓN DEL EGRESO")
        
        if gasto and gasto.descripcion:
            # Text wrapping para la descripción larga
            desc_lines = textwrap.wrap(gasto.descripcion, width=80)
            c.setFont("Helvetica", 10)
            for i, line in enumerate(desc_lines):
                c.drawString(60, y_pos - 20 - (i * 15), line)
        
        # --- FIRMAS Y SELLOS ---
        y_pos = 150
        
        # Línea para firma del responsable
        c.setStrokeColor(HexColor("#000000"))
        c.setLineWidth(0.5)
        c.line(100, y_pos, 300, y_pos)
        
        c.setFont("Helvetica", 10)
        c.drawCentredString(200, y_pos - 15, "Firma del Responsable")
        
        # Línea para firma de contabilidad
        c.line(350, y_pos, 550, y_pos)
        c.drawCentredString(450, y_pos - 15, "Firma de Contabilidad")
        
        # Sello de la empresa
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(HexColor("#AB2E2E"))
        c.drawCentredString(width/2, y_pos - 40, "COMPROBANTE DE EGRESO AUTORIZADO")
        c.setFillColor(HexColor("#000000"))
        c.drawCentredString(width/2, y_pos - 55, "Control Interno - Sistema de Gestión")
        
        # Pie de página
        c.setFont("Helvetica", 8)
        c.drawCentredString(width/2, 30, "Documento interno para control de egresos. No válido como factura.")
        c.drawCentredString(width/2, 20, f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Guardar PDF
        c.save()
        
        return output_path
    
    @staticmethod
    def generar_comprobante(movimiento_id):
        """
        Genera un comprobante (Ingreso o Egreso) en PDF según el tipo de movimiento.
        
        Args:
            movimiento_id: ID del movimiento de caja
        
        Returns:
            str: Ruta del archivo PDF generado
        """
        try:
            # Obtener detalles del movimiento
            detalles = ComprobanteService.obtener_detalles_movimiento(movimiento_id)
            movimiento = detalles['movimiento']
            
            # Generar nombre de archivo según formato: YYYY_MM_DD_CI/CE_ID.pdf
            fecha_actual = datetime.now().strftime("%Y_%m_%d")
            tipo = "CI" if movimiento.tipo == "INGRESO" else "CE"
            nombre_archivo = f"{fecha_actual}_{tipo}_{movimiento.id}.pdf"
            output_path = os.path.join(COMPROBANTES_DIR, nombre_archivo)  # Usar COMPROBANTES_DIR
            
            # Generar PDF según tipo
            if movimiento.tipo == "INGRESO":
                return ComprobanteService.generar_comprobante_ingreso_pdf(detalles, output_path)
            else:
                return ComprobanteService.generar_comprobante_egreso_pdf(detalles, output_path)
            
        except Exception as e:
            logger.error(f"Error al generar comprobante: {e}")
            raise
    
    @staticmethod
    def mostrar_previa_comprobante(movimiento_id):
        """
        Muestra una vista previa del comprobante en consola.
        
        Args:
            movimiento_id: ID del movimiento de caja
        """
        try:
            detalles = ComprobanteService.obtener_detalles_movimiento(movimiento_id)
            movimiento = detalles['movimiento']
            empresa = detalles['empresa']
            
            print("\n" + "="*60)
            print("🧾 VISTA PREVIA DE COMPROBANTE")
            print("="*60)
            
            print(f"\n📋 INFORMACIÓN GENERAL:")
            print(f"   • Tipo: {movimiento.tipo}")
            print(f"   • ID Movimiento: {movimiento.id}")
            print(f"   • Fecha: {movimiento.fecha}")
            print(f"   • Monto: ${movimiento.monto:.2f}")
            print(f"   • Descripción: {movimiento.descripcion}")
            
            print(f"\n🏢 EMPRESA:")
            print(f"   • Nombre: {empresa.nombre if empresa else 'Formación Continua Consultora'}")
            print(f"   • NIT: {empresa.nit if empresa and hasattr(empresa, 'nit') else '1234567012'}")
            
            # Detalles específicos según tipo
            if movimiento.tipo == "INGRESO" and 'pago' in detalles:
                pago = detalles['pago']
                print(f"\n💰 DETALLES DEL PAGO:")
                print(f"   • Forma de pago: {pago.forma_pago}")
                if pago.nro_cuota:
                    print(f"   • N° Cuota: {pago.nro_cuota}")
                if pago.nro_comprobante:
                    print(f"   • N° Comprobante: {pago.nro_comprobante}")
                
                if 'estudiante' in detalles:
                    estudiante = detalles['estudiante']
                    print(f"\n👤 ESTUDIANTE:")
                    print(f"   • Nombre: {estudiante.nombres} {estudiante.apellidos}")
                    print(f"   • CI: {estudiante.ci_numero} {estudiante.ci_expedicion if estudiante.ci_expedicion else ''}")
                
                if 'programa' in detalles:
                    programa = detalles['programa']
                    print(f"   • Programa: {programa.nombre}")
            
            elif movimiento.tipo == "EGRESO" and 'gasto' in detalles:
                gasto = detalles['gasto']
                print(f"\n💸 DETALLES DEL GASTO:")
                print(f"   • Categoría: {gasto.categoria}")
                if gasto.subcategoria:
                    print(f"   • Subcategoría: {gasto.subcategoria}")
                if gasto.proveedor:
                    print(f"   • Proveedor: {gasto.proveedor}")
                print(f"   • Forma de pago: {gasto.forma_pago}")
            
            # Detalles específicos para INGRESO_GENERICO
            elif movimiento.tipo == "INGRESO" and 'ingreso_generico' in detalles:
                ingreso = detalles['ingreso_generico']
                print(f"\n💰 DETALLES DEL INGRESO GENÉRICO:")
                print(f"   • Concepto: {ingreso.concepto}")
                if ingreso.descripcion:
                    print(f"   • Descripción: {ingreso.descripcion}")
                print(f"   • Forma de pago: {ingreso.forma_pago}")
                if ingreso.comprobante_nro:
                    print(f"   • N° Comprobante: {ingreso.comprobante_nro}")
            
            print("\n" + "="*60)
            
        except Exception as e:
            print(f"❌ Error al mostrar vista previa: {e}")

    @staticmethod
    def obtener_ruta_logo():
        """Obtiene la ruta del logo con manejo robusto de errores"""
        import os

        # 1. Intentar desde la base de datos
        empresa = EmpresaModel.obtener_datos()
        if empresa and hasattr(empresa, 'logo_path') and empresa.logo_path:
            if os.path.exists(empresa.logo_path):
                return empresa.logo_path

        # 2. Ruta por defecto en assets/
        PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        rutas_posibles = [
            os.path.join(PROJECT_ROOT, "assets", "images", "logo_empresa.png"),
            os.path.join(PROJECT_ROOT, "assets", "images", "logo.png"),
            os.path.join(PROJECT_ROOT, "assets", "logo.png"),
        ]

        for ruta in rutas_posibles:
            if os.path.exists(ruta):
                # Actualizar BD con ruta encontrada
                try:
                    from database.database import db
                    db.execute("UPDATE empresa SET logo_path = ? WHERE id = 1", (ruta,))
                    logger.info(f"✅ Ruta del logo actualizada en BD: {ruta}")
                except:
                    pass
                return ruta

        # 3. Si no existe, devolver None (sin logo)
        logger.warning("⚠️  No se encontró el logo en ninguna ubicación esperada")
        return None