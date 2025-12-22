# controllers/comprobante_controller.py
"""
Controlador para gestión de comprobantes.
"""
import os
import logging
from datetime import datetime

from services.comprobante_service import ComprobanteService
from models.movimiento_caja import MovimientoCajaModel
from database.database import db

logger = logging.getLogger(__name__)

# Asegurar que existe el directorio comprobantes (por si acaso)
COMPROBANTES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "comprobantes")
os.makedirs(COMPROBANTES_DIR, exist_ok=True)

def mostrar_menu_comprobantes():
    """Muestra el menú de gestión de comprobantes"""
    print("\n" + "="*60)
    print("🧾 GESTIÓN DE COMPROBANTES")
    print("="*60)
    print("1. Buscar movimientos por fecha")
    print("2. Buscar movimientos por tipo (INGRESO/EGRESO)")
    print("3. Buscar movimientos por rango de fechas")
    print("4. Ver últimos 10 movimientos")
    print("5. Volver al menú principal")

def buscar_movimientos_por_fecha():
    """Busca movimientos por fecha específica"""
    print("\n📅 BUSCAR MOVIMIENTOS POR FECHA")
    print("-"*40)
    
    fecha_str = input("Fecha (YYYY-MM-DD) [hoy]: ").strip()
    if not fecha_str:
        fecha = datetime.now().date().isoformat()
    else:
        try:
            datetime.strptime(fecha_str, '%Y-%m-%d')
            fecha = fecha_str
        except ValueError:
            print("❌ Formato de fecha inválido. Use YYYY-MM-DD")
            return
    
    query = """
    SELECT * FROM movimientos_caja 
    WHERE DATE(fecha) = ?
    ORDER BY fecha DESC
    """
    
    movimientos = db.fetch_all(query, (fecha,))
    
    if not movimientos:
        print(f"\n📭 No hay movimientos registrados para la fecha {fecha}")
        return
    
    print(f"\n📋 Movimientos del {fecha}:")
    print("-"*80)
    for mov in movimientos:
        print(f"  ID: {mov['id']} - {mov['tipo']} - ${mov['monto']:.2f}")
        print(f"     Descripción: {mov['descripcion']}")
        print(f"     Fecha: {mov['fecha']}")
        print("-"*40)
    
    return movimientos

def buscar_movimientos_por_tipo():
    """Busca movimientos por tipo (INGRESO/EGRESO)"""
    print("\n🔍 BUSCAR MOVIMIENTOS POR TIPO")
    print("-"*40)
    
    print("Tipos disponibles:")
    print("  1. INGRESO")
    print("  2. EGRESO")
    
    opcion = input("Seleccione tipo (1-2): ").strip()
    if opcion == '1':
        tipo = 'INGRESO'
    elif opcion == '2':
        tipo = 'EGRESO'
    else:
        print("❌ Opción no válida")
        return
    
    # Opcional: filtrar por fecha
    fecha_str = input("Fecha (YYYY-MM-DD) [todas]: ").strip()
    
    if fecha_str:
        try:
            datetime.strptime(fecha_str, '%Y-%m-%d')
            query = """
            SELECT * FROM movimientos_caja 
            WHERE tipo = ? AND DATE(fecha) = ?
            ORDER BY fecha DESC
            """
            params = (tipo, fecha_str)
        except ValueError:
            print("❌ Formato de fecha inválido. Use YYYY-MM-DD")
            return
    else:
        query = """
        SELECT * FROM movimientos_caja 
        WHERE tipo = ?
        ORDER BY fecha DESC
        LIMIT 20
        """
        params = (tipo,)
    
    movimientos = db.fetch_all(query, params)
    
    if not movimientos:
        print(f"\n📭 No hay movimientos de tipo {tipo}")
        return
    
    print(f"\n📋 Movimientos de tipo {tipo}:")
    print("-"*80)
    total = 0
    for mov in movimientos:
        print(f"  ID: {mov['id']} - ${mov['monto']:.2f}")
        print(f"     Descripción: {mov['descripcion']}")
        print(f"     Fecha: {mov['fecha']}")
        print("-"*40)
        total += mov['monto']
    
    print(f"\n💰 TOTAL {tipo}: ${total:.2f}")
    return movimientos

def buscar_movimientos_por_rango():
    """Busca movimientos por rango de fechas"""
    print("\n📅 BUSCAR MOVIMIENTOS POR RANGO DE FECHAS")
    print("-"*40)
    
    try:
        fecha_inicio = input("Fecha inicio (YYYY-MM-DD): ").strip()
        fecha_fin = input("Fecha fin (YYYY-MM-DD): ").strip()
        
        # Validar fechas
        datetime.strptime(fecha_inicio, '%Y-%m-%d')
        datetime.strptime(fecha_fin, '%Y-%m-%d')
        
        query = """
        SELECT * FROM movimientos_caja 
        WHERE DATE(fecha) BETWEEN ? AND ?
        ORDER BY fecha DESC
        """
        
        movimientos = db.fetch_all(query, (fecha_inicio, fecha_fin))
        
        if not movimientos:
            print(f"\n📭 No hay movimientos entre {fecha_inicio} y {fecha_fin}")
            return
        
        print(f"\n📋 Movimientos del {fecha_inicio} al {fecha_fin}:")
        print("-"*80)
        
        total_ingresos = 0
        total_egresos = 0
        
        for mov in movimientos:
            tipo = mov['tipo']
            monto = mov['monto']
            
            if tipo == 'INGRESO':
                total_ingresos += monto
                tipo_str = "💰 INGRESO"
            else:
                total_egresos += monto
                tipo_str = "💸 EGRESO"
            
            print(f"  ID: {mov['id']} - {tipo_str} - ${monto:.2f}")
            print(f"     Descripción: {mov['descripcion']}")
            print(f"     Fecha: {mov['fecha']}")
            print("-"*40)
        
        print(f"\n📊 RESUMEN DEL PERÍODO:")
        print(f"   Total Ingresos: ${total_ingresos:.2f}")
        print(f"   Total Egresos: ${total_egresos:.2f}")
        print(f"   Saldo Neto: ${total_ingresos - total_egresos:.2f}")
        
        return movimientos
        
    except ValueError as e:
        print(f"❌ Error en formato de fecha: {e}")

def ver_ultimos_movimientos():
    """Muestra los últimos 10 movimientos"""
    print("\n🕐 ÚLTIMOS 10 MOVIMIENTOS")
    print("-"*40)
    
    query = """
    SELECT * FROM movimientos_caja 
    ORDER BY fecha DESC 
    LIMIT 10
    """
    
    movimientos = db.fetch_all(query)
    
    if not movimientos:
        print("\n📭 No hay movimientos registrados")
        return
    
    for mov in movimientos:
        tipo = mov['tipo']
        if tipo == 'INGRESO':
            tipo_str = "💰 INGRESO"
        else:
            tipo_str = "💸 EGRESO"
        
        print(f"  ID: {mov['id']:3d} - {tipo_str:10s} - ${mov['monto']:8.2f}")
        print(f"     {mov['descripcion'][:50]}")
        print(f"     {mov['fecha']}")
        print()
    
    return movimientos

def generar_comprobante_seleccionado():
    """Permite seleccionar un movimiento y generar su comprobante"""
    print("\n🧾 GENERAR COMPROBANTE")
    print("-"*40)
    
    try:
        # Pedir ID del movimiento
        movimiento_id = input("ID del movimiento de caja: ").strip()
        if not movimiento_id:
            print("❌ Debe ingresar un ID")
            return
        
        movimiento_id = int(movimiento_id)
        
        # Verificar que existe
        movimiento = MovimientoCajaModel.find_by_id(movimiento_id)
        if not movimiento:
            print(f"❌ No se encontró movimiento con ID {movimiento_id}")
            return
        
        # Mostrar vista previa
        ComprobanteService.mostrar_previa_comprobante(movimiento_id)
        
        # Confirmar generación
        confirmar = input("\n¿Generar comprobante en PDF? (s/n): ").strip().lower()
        if confirmar != 's':
            print("❌ Generación cancelada")
            return
        
        # Generar comprobante
        print("\n⏳ Generando comprobante...")
        ruta_pdf = ComprobanteService.generar_comprobante(movimiento_id)
        
        print(f"\n✅ Comprobante generado exitosamente!")
        print(f"📄 Archivo: {ruta_pdf}")
        print(f"📁 Ruta absoluta: {os.path.abspath(ruta_pdf)}")
        
        # Preguntar si abrir el archivo
        abrir = input("\n¿Abrir el comprobante? (s/n): ").strip().lower()
        if abrir == 's':
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(os.path.abspath(ruta_pdf))
                elif os.name == 'posix':  # Linux/Mac
                    os.system(f'open "{os.path.abspath(ruta_pdf)}"')
            except:
                print("⚠️  No se pudo abrir el archivo automáticamente")
        
    except ValueError:
        print("❌ ID debe ser un número")
    except Exception as e:
        print(f"❌ Error al generar comprobante: {e}")
        logger.exception("Error en generar_comprobante_seleccionado")

def gestionar_comprobantes():
    """Menú principal de gestión de comprobantes"""
    while True:
        mostrar_menu_comprobantes()
        opcion = input("\n👉 Seleccione una opción: ").strip()
        
        if opcion == '1':
            movimientos = buscar_movimientos_por_fecha()
            if movimientos:
                generar = input("\n¿Generar comprobante para algún movimiento? (s/n): ").strip().lower()
                if generar == 's':
                    generar_comprobante_seleccionado()
        
        elif opcion == '2':
            movimientos = buscar_movimientos_por_tipo()
            if movimientos:
                generar = input("\n¿Generar comprobante para algún movimiento? (s/n): ").strip().lower()
                if generar == 's':
                    generar_comprobante_seleccionado()
        
        elif opcion == '3':
            movimientos = buscar_movimientos_por_rango()
            if movimientos:
                generar = input("\n¿Generar comprobante para algún movimiento? (s/n): ").strip().lower()
                if generar == 's':
                    generar_comprobante_seleccionado()
        
        elif opcion == '4':
            movimientos = ver_ultimos_movimientos()
            if movimientos:
                generar = input("\n¿Generar comprobante para algún movimiento? (s/n): ").strip().lower()
                if generar == 's':
                    generar_comprobante_seleccionado()
        
        elif opcion == '5':
            break
        
        else:
            print("❌ Opción no válida. Intente de nuevo.")
        
        input("\nPresione Enter para continuar...")