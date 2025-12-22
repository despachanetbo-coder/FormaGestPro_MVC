# controllers/ingreso_controller.py
"""
Controlador para manejar la interfaz de línea de comandos de Ingresos Genéricos.
"""
import logging
from datetime import datetime

from services.ingreso_service import IngresoGenericoService
from models.ingreso_generico import IngresoGenericoModel

logger = logging.getLogger(__name__)

def mostrar_menu_ingresos():
    """Muestra el menú de gestión de ingresos genéricos"""
    print("\n" + "="*60)
    print("💰 GESTIÓN DE INGRESOS GENÉRICOS")
    print("="*60)
    print("1. Registrar nuevo ingreso")
    print("2. Ver ingresos por fecha")
    print("3. Buscar ingresos por concepto")
    print("4. Ver ingresos por rango de fechas")
    print("5. Ver resumen mensual")
    print("6. Volver al menú principal")

def registrar_ingreso_generico():
    """Función CLI para registrar un ingreso genérico"""
    print("\n📝 REGISTRO DE INGRESO GENÉRICO")
    print("-"*40)
    
    try:
        # Fecha
        fecha_str = input("Fecha (YYYY-MM-DD) [hoy]: ").strip()
        if not fecha_str:
            fecha = datetime.now().date().isoformat()
        else:
            # Validar formato de fecha
            try:
                datetime.strptime(fecha_str, '%Y-%m-%d')
                fecha = fecha_str
            except ValueError:
                print("❌ Formato de fecha inválido. Use YYYY-MM-DD")
                return
        
        # Monto
        while True:
            try:
                monto = float(input("Monto: $").strip())
                if monto <= 0:
                    print("❌ El monto debe ser mayor a 0")
                    continue
                break
            except ValueError:
                print("❌ Ingrese un monto válido")
        
        # Concepto (obligatorio)
        while True:
            concepto = input("Concepto del ingreso (ej: Venta materiales, Donación, etc.): ").strip()
            if concepto:
                break
            print("❌ El concepto es obligatorio")
        
        # Descripción (opcional)
        descripcion = input("Descripción detallada (opcional): ").strip()
        if not descripcion:
            descripcion = None
        
        # Forma de pago
        print("\n💳 Formas de pago disponibles:")
        for i, fp in enumerate(IngresoGenericoModel.FORMAS_PAGO, 1):
            print(f"  {i}. {fp}")
        
        while True:
            try:
                fp_idx = int(input(f"Seleccione forma de pago (1-{len(IngresoGenericoModel.FORMAS_PAGO)}): ").strip())
                if 1 <= fp_idx <= len(IngresoGenericoModel.FORMAS_PAGO):
                    forma_pago = IngresoGenericoModel.FORMAS_PAGO[fp_idx-1]
                    break
                else:
                    print("❌ Opción fuera de rango")
            except ValueError:
                print("❌ Ingrese un número válido")
        
        # Número de comprobante (opcional)
        comprobante_nro = input("Número de comprobante (opcional): ").strip()
        if not comprobante_nro:
            comprobante_nro = None
        
        # Confirmar
        print("\n" + "="*60)
        print("📋 RESUMEN DEL INGRESO:")
        print(f"   Fecha: {fecha}")
        print(f"   Monto: ${monto:.2f}")
        print(f"   Concepto: {concepto}")
        if descripcion:
            print(f"   Descripción: {descripcion}")
        print(f"   Forma de pago: {forma_pago}")
        if comprobante_nro:
            print(f"   N° Comprobante: {comprobante_nro}")
        print("="*60)
        
        confirmar = input("\n¿Confirmar registro del ingreso? (s/n): ").strip().lower()
        if confirmar != 's':
            print("❌ Registro cancelado")
            return
        
        # Registrar ingreso
        ingreso = IngresoGenericoService.registrar_ingreso(
            fecha=fecha,
            monto=monto,
            concepto=concepto,
            descripcion=descripcion,
            forma_pago=forma_pago,
            comprobante_nro=comprobante_nro
        )
        
        print(f"\n✅ Ingreso registrado exitosamente (ID: {ingreso.id})")
        print(f"💰 Se ha registrado automáticamente el movimiento de caja (INGRESO)")
        print(f"🧾 Puede generar el comprobante desde la opción de Comprobantes")
        
    except ValueError as e:
        print(f"❌ Error de validación: {e}")
    except Exception as e:
        print(f"❌ Error al registrar ingreso: {e}")
        logger.exception("Error en registrar_ingreso_generico")

def ver_ingresos_por_fecha():
    """Muestra ingresos de una fecha específica"""
    print("\n📅 VER INGRESOS POR FECHA")
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
    
    ingresos = IngresoGenericoService.obtener_ingresos_por_fecha(fecha)
    
    if not ingresos:
        print(f"\n📭 No hay ingresos registrados para la fecha {fecha}")
        return
    
    print(f"\n📋 Ingresos del {fecha}:")
    print("-"*80)
    total = 0
    for ingreso in ingresos:
        print(f"  ID: {ingreso.id}")
        print(f"  Concepto: {ingreso.concepto}")
        if ingreso.descripcion:
            print(f"  Descripción: {ingreso.descripcion}")
        print(f"  Monto: ${ingreso.monto:.2f}")
        print(f"  Forma de pago: {ingreso.forma_pago}")
        if ingreso.comprobante_nro:
            print(f"  N° Comprobante: {ingreso.comprobante_nro}")
        print("-"*40)
        total += ingreso.monto
    
    print(f"\n💰 TOTAL DEL DÍA: ${total:.2f}")

def buscar_ingresos_por_concepto():
    """Busca ingresos por concepto"""
    print("\n🔍 BUSCAR INGRESOS POR CONCEPTO")
    print("-"*40)
    
    concepto = input("Texto a buscar en el concepto: ").strip()
    if not concepto:
        print("❌ Debe ingresar un texto para buscar")
        return
    
    ingresos = IngresoGenericoService.obtener_ingresos_por_concepto(concepto)
    
    if not ingresos:
        print(f"\n📭 No hay ingresos que coincidan con '{concepto}'")
        return
    
    print(f"\n📋 Ingresos encontrados:")
    print("-"*80)
    total = 0
    for ingreso in ingresos:
        print(f"  ID: {ingreso.id} - Fecha: {ingreso.fecha}")
        print(f"  Concepto: {ingreso.concepto}")
        print(f"  Monto: ${ingreso.monto:.2f}")
        print(f"  Forma de pago: {ingreso.forma_pago}")
        print("-"*40)
        total += ingreso.monto
    
    print(f"\n💰 TOTAL ENCONTRADO: ${total:.2f}")

def ver_ingresos_por_rango():
    """Muestra ingresos por rango de fechas"""
    print("\n📅 VER INGRESOS POR RANGO DE FECHAS")
    print("-"*40)
    
    try:
        fecha_inicio = input("Fecha inicio (YYYY-MM-DD): ").strip()
        fecha_fin = input("Fecha fin (YYYY-MM-DD): ").strip()
        
        # Validar fechas
        datetime.strptime(fecha_inicio, '%Y-%m-%d')
        datetime.strptime(fecha_fin, '%Y-%m-%d')
        
        ingresos = IngresoGenericoService.obtener_ingresos_por_rango(fecha_inicio, fecha_fin)
        
        if not ingresos:
            print(f"\n📭 No hay ingresos entre {fecha_inicio} y {fecha_fin}")
            return
        
        print(f"\n📋 Ingresos del {fecha_inicio} al {fecha_fin}:")
        print("-"*80)
        
        total = 0
        for ingreso in ingresos:
            print(f"  ID: {ingreso.id} - Fecha: {ingreso.fecha}")
            print(f"  Concepto: {ingreso.concepto}")
            print(f"  Monto: ${ingreso.monto:.2f}")
            print(f"  Forma de pago: {ingreso.forma_pago}")
            print("-"*40)
            total += ingreso.monto
        
        print(f"\n💰 TOTAL DEL PERÍODO: ${total:.2f}")
        
    except ValueError as e:
        print(f"❌ Error en formato de fecha: {e}")

def ver_resumen_mensual():
    """Muestra un resumen de ingresos por mes"""
    print("\n📊 RESUMEN MENSUAL DE INGRESOS")
    print("-"*40)
    
    # Preguntar si filtrar por año/mes específico
    filtrar = input("¿Filtrar por mes y año específicos? (s/n): ").strip().lower()
    
    if filtrar == 's':
        try:
            año = int(input("Año (ej: 2024): ").strip())
            mes = int(input("Mes (1-12): ").strip())
            if not (1 <= mes <= 12):
                print("❌ Mes debe estar entre 1 y 12")
                return
        except ValueError:
            print("❌ Ingrese valores numéricos válidos")
            return
        resumen = IngresoGenericoService.obtener_resumen_mensual(año, mes)
        print(f"\n📈 Ingresos del mes {mes:02d}/{año}:")
    else:
        resumen = IngresoGenericoService.obtener_resumen_mensual()
        print("\n📈 Ingresos totales por mes:")
    
    if not resumen:
        print("\n📭 No hay ingresos registrados")
        return
    
    print("-"*50)
    total_general = 0
    for item in resumen:
        periodo = item['periodo']
        total = float(item['total']) if item['total'] else 0
        print(f"  {periodo:<20} ${total:>10.2f}")
        total_general += total
    
    print("-"*50)
    print(f"  {'TOTAL':<20} ${total_general:>10.2f}")

def gestionar_ingresos_genericos():
    """Menú principal de gestión de ingresos genéricos"""
    while True:
        mostrar_menu_ingresos()
        opcion = input("\n👉 Seleccione una opción: ").strip()
        
        if opcion == '1':
            registrar_ingreso_generico()
        elif opcion == '2':
            ver_ingresos_por_fecha()
        elif opcion == '3':
            buscar_ingresos_por_concepto()
        elif opcion == '4':
            ver_ingresos_por_rango()
        elif opcion == '5':
            ver_resumen_mensual()
        elif opcion == '6':
            break
        else:
            print("❌ Opción no válida. Intente de nuevo.")
        
        input("\nPresione Enter para continuar...")