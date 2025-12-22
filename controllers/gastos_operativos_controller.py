# controllers/gasto_controller.py
"""
Controlador para manejar la interfaz de línea de comandos de Gastos Operativos.
"""
import logging
from datetime import datetime

from services.gasto_service import GastoService
from models.gasto_operativo import GastoOperativoModel

logger = logging.getLogger(__name__)

def mostrar_menu_gastos():
    """Muestra el menú de gestión de gastos"""
    print("\n" + "="*50)
    print("💰 GESTIÓN DE GASTOS OPERATIVOS")
    print("="*50)
    print("1. Registrar nuevo gasto")
    print("2. Ver gastos por fecha")
    print("3. Ver gastos por categoría")
    print("4. Ver resumen por categoría")
    print("5. Volver al menú principal")

def registrar_gasto_operativo():
    """Función CLI para registrar un gasto operativo"""
    print("\n📝 REGISTRO DE GASTO OPERATIVO")
    print("-"*30)
    
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
        
        # Categoría
        print("\n📂 Categorías disponibles:")
        for i, cat in enumerate(GastoOperativoModel.CATEGORIAS, 1):
            print(f"  {i}. {cat}")
        
        while True:
            try:
                cat_idx = int(input(f"Seleccione categoría (1-{len(GastoOperativoModel.CATEGORIAS)}): ").strip())
                if 1 <= cat_idx <= len(GastoOperativoModel.CATEGORIAS):
                    categoria = GastoOperativoModel.CATEGORIAS[cat_idx-1]
                    break
                else:
                    print("❌ Opción fuera de rango")
            except ValueError:
                print("❌ Ingrese un número válido")
        
        # Subcategoría (opcional)
        subcategoria = None
        if categoria in GastoOperativoModel.SUBCATEGORIAS and GastoOperativoModel.SUBCATEGORIAS[categoria]:
            print("\n📂 Subcategorías disponibles:")
            subcats = GastoOperativoModel.SUBCATEGORIAS[categoria]
            for i, sub in enumerate(subcats, 1):
                print(f"  {i}. {sub}")
            
            opcion = input(f"Seleccione subcategoría (1-{len(subcats)}) o Enter para omitir: ").strip()
            if opcion:
                try:
                    sub_idx = int(opcion)
                    if 1 <= sub_idx <= len(subcats):
                        subcategoria = subcats[sub_idx-1]
                except ValueError:
                    print("⚠️  Se omitirá subcategoría")
        
        # Descripción
        descripcion = input("Descripción (opcional): ").strip()
        if not descripcion:
            descripcion = None
        
        # Proveedor
        proveedor = input("Proveedor (opcional): ").strip()
        if not proveedor:
            proveedor = None
        
        # Número de factura
        nro_factura = input("Número de factura (opcional): ").strip()
        if not nro_factura:
            nro_factura = None
        
        # Forma de pago
        print("\n💳 Formas de pago disponibles:")
        for i, fp in enumerate(GastoOperativoModel.FORMAS_PAGO, 1):
            print(f"  {i}. {fp}")
        
        while True:
            try:
                fp_idx = int(input(f"Seleccione forma de pago (1-{len(GastoOperativoModel.FORMAS_PAGO)}): ").strip())
                if 1 <= fp_idx <= len(GastoOperativoModel.FORMAS_PAGO):
                    forma_pago = GastoOperativoModel.FORMAS_PAGO[fp_idx-1]
                    break
                else:
                    print("❌ Opción fuera de rango")
            except ValueError:
                print("❌ Ingrese un número válido")
        
        # Número de comprobante
        comprobante_nro = input("Número de comprobante (opcional): ").strip()
        if not comprobante_nro:
            comprobante_nro = None
        
        # Confirmar
        print("\n" + "="*50)
        print("📋 RESUMEN DEL GASTO:")
        print(f"   Fecha: {fecha}")
        print(f"   Monto: ${monto:.2f}")
        print(f"   Categoría: {categoria}")
        if subcategoria:
            print(f"   Subcategoría: {subcategoria}")
        if descripcion:
            print(f"   Descripción: {descripcion}")
        if proveedor:
            print(f"   Proveedor: {proveedor}")
        print(f"   Forma de pago: {forma_pago}")
        print("="*50)
        
        confirmar = input("\n¿Confirmar registro del gasto? (s/n): ").strip().lower()
        if confirmar != 's':
            print("❌ Registro cancelado")
            return
        
        # Registrar gasto
        gasto = GastoService.registrar_gasto(
            fecha=fecha,
            monto=monto,
            categoria=categoria,
            subcategoria=subcategoria,
            descripcion=descripcion,
            proveedor=proveedor,
            nro_factura=nro_factura,
            forma_pago=forma_pago,
            comprobante_nro=comprobante_nro
        )
        
        print(f"\n✅ Gasto registrado exitosamente (ID: {gasto.id})")
        print(f"💰 Se ha registrado automáticamente el movimiento de caja (EGRESO)")
        
    except ValueError as e:
        print(f"❌ Error de validación: {e}")
    except Exception as e:
        print(f"❌ Error al registrar gasto: {e}")
        logger.exception("Error en registrar_gasto_operativo")

def ver_gastos_por_fecha():
    """Muestra gastos de una fecha específica"""
    print("\n📅 VER GASTOS POR FECHA")
    print("-"*30)
    
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
    
    gastos = GastoService.obtener_gastos_por_fecha(fecha)
    
    if not gastos:
        print(f"\n📭 No hay gastos registrados para la fecha {fecha}")
        return
    
    print(f"\n📋 Gastos del {fecha}:")
    print("-"*80)
    total = 0
    for gasto in gastos:
        print(f"  ID: {gasto.id}")
        print(f"  Categoría: {gasto.categoria}" + 
              (f" / {gasto.subcategoria}" if gasto.subcategoria else ""))
        print(f"  Monto: ${gasto.monto:.2f}")
        if gasto.descripcion:
            print(f"  Descripción: {gasto.descripcion}")
        if gasto.proveedor:
            print(f"  Proveedor: {gasto.proveedor}")
        print(f"  Forma de pago: {gasto.forma_pago}")
        print("-"*40)
        total += gasto.monto
    
    print(f"\n💰 TOTAL DEL DÍA: ${total:.2f}")

def ver_gastos_por_categoria():
    """Muestra gastos por categoría"""
    print("\n📂 VER GASTOS POR CATEGORÍA")
    print("-"*30)
    
    print("Categorías disponibles:")
    for i, cat in enumerate(GastoOperativoModel.CATEGORIAS, 1):
        print(f"  {i}. {cat}")
    
    try:
        cat_idx = int(input(f"Seleccione categoría (1-{len(GastoOperativoModel.CATEGORIAS)}): ").strip())
        if not (1 <= cat_idx <= len(GastoOperativoModel.CATEGORIAS)):
            print("❌ Opción fuera de rango")
            return
        
        categoria = GastoOperativoModel.CATEGORIAS[cat_idx-1]
        gastos = GastoService.obtener_gastos_por_categoria(categoria)
        
        if not gastos:
            print(f"\n📭 No hay gastos registrados en la categoría {categoria}")
            return
        
        print(f"\n📋 Gastos en categoría '{categoria}':")
        print("-"*80)
        total = 0
        for gasto in gastos:
            print(f"  ID: {gasto.id} - Fecha: {gasto.fecha}")
            print(f"  Monto: ${gasto.monto:.2f}")
            if gasto.subcategoria:
                print(f"  Subcategoría: {gasto.subcategoria}")
            if gasto.descripcion:
                print(f"  Descripción: {gasto.descripcion}")
            print(f"  Forma de pago: {gasto.forma_pago}")
            print("-"*40)
            total += gasto.monto
        
        print(f"\n💰 TOTAL EN CATEGORÍA: ${total:.2f}")
        
    except ValueError:
        print("❌ Ingrese un número válido")
    except Exception as e:
        print(f"❌ Error: {e}")

def ver_resumen_por_categoria():
    """Muestra un resumen de gastos por categoría"""
    print("\n📊 RESUMEN DE GASTOS POR CATEGORÍA")
    print("-"*30)
    
    # Preguntar si filtrar por mes/año
    filtrar = input("¿Filtrar por mes y año? (s/n): ").strip().lower()
    
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
        resumen = GastoService.obtener_resumen_por_categoria(mes, año)
        print(f"\n📈 Gastos del mes {mes:02d}/{año}:")
    else:
        resumen = GastoService.obtener_resumen_por_categoria()
        print("\n📈 Gastos totales por categoría:")
    
    if not resumen:
        print("\n📭 No hay gastos registrados")
        return
    
    print("-"*50)
    total_general = 0
    for item in resumen:
        categoria = item['categoria']
        total = float(item['total']) if item['total'] else 0
        print(f"  {categoria:<20} ${total:>10.2f}")
        total_general += total
    
    print("-"*50)
    print(f"  {'TOTAL':<20} ${total_general:>10.2f}")