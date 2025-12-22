# cli.py
"""
CLI principal para FormaGestPro - Sistema de Gestión Académica.
"""
from pathlib import Path
import sys
import os
import logging
from datetime import datetime

# Importar controladores y servicios
from controllers.estudiante_controller import *
from controllers.docente_controller import *
from controllers.ingreso_controller import gestionar_ingresos_genericos
from controllers.programa_controller import *
from controllers.matricula_controller import *
from controllers.pago_controller import *
from controllers.gastos_operativos_controller import *
from controllers.comprobante_controller import gestionar_comprobantes  # <-- AGREGAR ESTE

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

def limpiar_pantalla():
    """Limpia la pantalla de la consola"""
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_encabezado(titulo=""):
    """Muestra un encabezado con título"""
    limpiar_pantalla()
    print("=" * 60)
    print("🎓 FORMA GEST PRO - Sistema de Gestión Académica")
    print("=" * 60)
    if titulo:
        print(f"\n📋 {titulo}")
        print("-" * 40)

# Mostrar resumen de costos
def mostrar_resumen_costos(programa, modalidad_pago, plan=None):
    """Muestra el desglose detallado de costos"""
    from datetime import datetime
    
    print("\n💵 DESGLOSE DE COSTOS:")
    print("-" * 40)
    
    # Costos fijos
    print(f"   • Inscripción:       ${programa.costo_inscripcion:9.2f}")
    print(f"   • Matrícula:         ${programa.costo_matricula:9.2f}")
    print(f"   • Colegiatura base:  ${programa.costo_base:9.2f}")
    
    # Verificar descuento por promoción
    total_colegiatura = programa.costo_base
    descuento_aplicado = 0
    
    if programa.promocion_activa and programa.promocion_fecha_limite:
        hoy = datetime.now().date()
        fecha_limite = datetime.strptime(programa.promocion_fecha_limite, "%Y-%m-%d").date()
        
        if hoy <= fecha_limite:
            descuento = programa.costo_base * (programa.descuento_promocion / 100)
            total_colegiatura = programa.costo_base - descuento
            descuento_aplicado += descuento
            print(f"   • Descuento promoción ({programa.descuento_promocion}%): -${descuento:9.2f}")
            print(f"   • Colegiatura con descuento: ${total_colegiatura:9.2f}")
    
    # Descuento por pago al contado
    if modalidad_pago == 'CONTADO' and programa.descuento_contado > 0:
        descuento_contado = total_colegiatura * (programa.descuento_contado / 100)
        total_colegiatura -= descuento_contado
        descuento_aplicado += descuento_contado
        print(f"   • Descuento contado ({programa.descuento_contado}%): -${descuento_contado:9.2f}")
    
    # Total general
    total_general = programa.costo_inscripcion + programa.costo_matricula + total_colegiatura
    
    print("-" * 40)
    print(f"   TOTAL A PAGAR:       ${total_general:9.2f}")
    
    # Si es cuotas, mostrar detalle
    if modalidad_pago == 'CUOTAS' and plan:
        print(f"\n📅 PLAN DE PAGOS ({plan.nombre}):")
        print(f"   • Colegiatura a financiar: ${total_colegiatura:9.2f}")
        print(f"   • Número de cuotas: {plan.nro_cuotas}")
        monto_cuota = total_colegiatura / plan.nro_cuotas
        print(f"   • Monto por cuota: ${monto_cuota:9.2f}")
        print(f"   • Intervalo: cada {plan.intervalo_dias} días")
        
        # Pagos iniciales
        print(f"\n   PAGOS INICIALES (al momento):")
        print(f"   • Inscripción: ${programa.costo_inscripcion:9.2f}")
        print(f"   • Matrícula:   ${programa.costo_matricula:9.2f}")
        total_inicial = programa.costo_inscripcion + programa.costo_matricula
        print(f"   Total inicial: ${total_inicial:9.2f}")
    
    return total_general

def pausar():
    """Pausa la ejecución hasta que el usuario presione Enter"""
    input("\n⏎ Presione Enter para continuar...")

def mostrar_menu_principal():
    """Muestra el menú principal con estadísticas"""
    mostrar_encabezado("MENÚ PRINCIPAL")
    
    # Importar aquí para evitar errores cíclicos
    try:
        from database.database import db
        from models.estudiante import EstudianteModel
        from models.docente import DocenteModel
        from models.programa import ProgramaModel
        
        # Obtener estadísticas
        total_estudiantes = EstudianteModel.count()
        total_docentes = DocenteModel.count()
        total_programas = ProgramaModel.count()
        
        print(f"📊 ESTADÍSTICAS: Estudiantes: {total_estudiantes} | Docentes: {total_docentes} | Programas: {total_programas}")
    except:
        print("📊 ESTADÍSTICAS: No disponibles (error al conectar)")
    
    print("\n" + "=" * 60)
    print("👤 GESTIÓN DE ESTUDIANTES")
    print("  1. Registrar nuevo estudiante")
    print("  2. Listar todos los estudiantes")
    print("  3. Buscar estudiante por CI")
    print("  4. Buscar estudiante por nombre")
    print("  5. Ver estadísticas de estudiantes")
    
    print("\n👨‍🏫 GESTIÓN DE DOCENTES")
    print("  6. Registrar nuevo docente")
    print("  7. Listar todos los docentes")
    print("  8. Buscar docente por CI")
    print("  9. Buscar docente por especialidad")
    print("  10. Ver estadísticas de docentes")
    
    print("\n📚 GESTIÓN DE PROGRAMAS")
    print("  11. Crear nuevo programa académico")
    print("  12. Listar todos los programas")
    print("  13. Buscar programa por código")
    print("  14. Editar programa existente") 
    print("  15. Configurar promoción de programa") 
    print("  16. Buscar programas con cupos disponibles")
    print("  17. Ver estadísticas de programas")
    
    print("\n💰 GESTIÓN FINANCIERA")
    print("  18. Registrar matrícula (Inscripción completa)")
    print("  19. Registrar pago de cuota")
    print("  20. Ver estado de pagos por estudiante")
    print("  21. Configurar planes de pago")
    print("  22. Ver movimientos de caja")  
    print("  23. Gestionar gastos operativos")
    print("  24. Gestionar comprobantes")
    print("  25. Gestionar ingresos genéricos")

    print("\n🔧 UTILIDADES")
    print("  26. Verificar estado del sistema")
    print("  27. Inicializar base de datos (¡CUIDADO!)")

    print("\n  0. Salir")
    print("=" * 60)

# ============================================
# FUNCIONES DE GESTIÓN DE ESTUDIANTES
# ============================================

def registrar_estudiante():
    """Registra un nuevo estudiante"""
    mostrar_encabezado("REGISTRAR NUEVO ESTUDIANTE")
    
    try:
        from models.estudiante import EstudianteModel
        
        print("📝 Complete los datos del estudiante:")
        print("-" * 40)
        
        # Datos obligatorios
        ci_numero = input("Número de CI: ").strip()
        if not ci_numero:
            print("❌ El número de CI es obligatorio")
            pausar()
            return
        
        # Validar formato de CI (solo números)
        if not ci_numero.isdigit():
            print("❌ El CI debe contener solo números")
            pausar()
            return
        
        ci_expedicion = input("Expedición (BE, CH, CB, LP, OR, PD, PT, SC, TJ, EX): ").strip().upper()
        if ci_expedicion not in EstudianteModel.EXPEDICIONES_VALIDAS:
            print(f"❌ Expedición inválida. Use: {', '.join(EstudianteModel.EXPEDICIONES_VALIDAS)}")
            pausar()
            return
        
        nombres = input("Nombres: ").strip()
        if not nombres:
            print("❌ Los nombres son obligatorios")
            pausar()
            return
        
        apellidos = input("Apellidos: ").strip()
        if not apellidos:
            print("❌ Los apellidos son obligatorios")
            pausar()
            return
        
        # Datos opcionales
        fecha_nacimiento = input("Fecha de nacimiento (AAAA-MM-DD, opcional): ").strip()
        telefono = input("Teléfono (opcional): ").strip()
        email = input("Email (opcional): ").strip()
        universidad_egreso = input("Universidad de egreso (opcional): ").strip()
        profesion = input("Profesión (opcional): ").strip()
        
        # Crear diccionario con datos
        datos = {
            'ci_numero': ci_numero,
            'ci_expedicion': ci_expedicion,
            'nombres': nombres,
            'apellidos': apellidos
        }
        
        # Agregar campos opcionales si se proporcionaron
        if fecha_nacimiento:
            datos['fecha_nacimiento'] = fecha_nacimiento
        if telefono:
            datos['telefono'] = telefono
        if email:
            # Validar email simple
            if '@' in email and '.' in email:
                datos['email'] = email
            else:
                print("⚠️  Email no válido, se omitirá")
        if universidad_egreso:
            datos['universidad_egreso'] = universidad_egreso
        if profesion:
            datos['profesion'] = profesion
        
        # Crear y guardar estudiante
        estudiante = EstudianteModel.crear_estudiante(datos)
        
        print(f"\n✅ ¡ESTUDIANTE REGISTRADO EXITOSAMENTE!")
        print(f"\n📋 DATOS DEL ESTUDIANTE:")
        print(f"   ID: {estudiante.id}")
        print(f"   Nombre completo: {estudiante.nombre_completo}")
        print(f"   CI: {estudiante.ci_numero}-{estudiante.ci_expedicion}")
        if hasattr(estudiante, 'email') and estudiante.email:
            print(f"   Email: {estudiante.email}")
        if hasattr(estudiante, 'telefono') and estudiante.telefono:
            print(f"   Teléfono: {estudiante.telefono}")
        print(f"   Fecha registro: {estudiante.fecha_registro[:10] if estudiante.fecha_registro else 'N/A'}")
        
    except ValueError as e:
        print(f"\n❌ Error de validación: {e}")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    
    pausar()

def listar_estudiantes():
    """Lista todos los estudiantes"""
    mostrar_encabezado("LISTA DE ESTUDIANTES")
    
    try:
        from models.estudiante import EstudianteModel
        
        estudiantes = EstudianteModel.all()
        
        if not estudiantes:
            print("📭 No hay estudiantes registrados en el sistema.")
        else:
            print(f"📊 Total estudiantes: {len(estudiantes)}")
            print("-" * 80)
            print(f"{'ID':<5} {'CI':<15} {'NOMBRE COMPLETO':<30} {'EMAIL':<25} {'TELÉFONO':<15}")
            print("-" * 80)
            
            for estudiante in estudiantes:
                estado = "✅" if estudiante.activo else "❌"
                ci_completo = f"{estudiante.ci_numero}-{estudiante.ci_expedicion}"
                email = estudiante.email if hasattr(estudiante, 'email') and estudiante.email else "N/A"
                telefono = estudiante.telefono if hasattr(estudiante, 'telefono') and estudiante.telefono else "N/A"
                
                print(f"{estudiante.id:<5} {ci_completo:<15} {estudiante.nombre_completo:<30} {email:<25} {telefono:<15} {estado}")
            
            print("-" * 80)
            
            # Opciones adicionales
            print("\n🔍 OPCIONES:")
            print("   • Ingrese 'E' para exportar a archivo")
            print("   • Ingrese ID para ver detalles completos")
            print("   • Enter para volver al menú")
            
            opcion = input("\n👉 Opción: ").strip().upper()
            
            if opcion == 'E':
                exportar_estudiantes_csv(estudiantes)
            elif opcion.isdigit():
                ver_detalles_estudiante(int(opcion))
    
    except Exception as e:
        print(f"❌ Error al listar estudiantes: {e}")
    
    pausar()

def buscar_estudiante_ci():
    """Busca estudiante por CI"""
    mostrar_encabezado("BUSCAR ESTUDIANTE POR CI")
    
    try:
        from models.estudiante import EstudianteModel
        
        ci_numero = input("Número de CI (sin expedición): ").strip()
        if not ci_numero:
            print("❌ Debe ingresar un número de CI")
            pausar()
            return
        
        ci_expedicion = input("Expedición (opcional, Enter para omitir): ").strip().upper()
        
        estudiante = EstudianteModel.buscar_por_ci(ci_numero, ci_expedicion if ci_expedicion else None)
        
        if estudiante:
            print(f"\n✅ ESTUDIANTE ENCONTRADO:")
            mostrar_detalles_estudiante(estudiante)
        else:
            print(f"\n📭 No se encontró estudiante con CI {ci_numero}{'-' + ci_expedicion if ci_expedicion else ''}")
    
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
    
    pausar()

def buscar_estudiante_nombre():
    """Busca estudiantes por nombre"""
    mostrar_encabezado("BUSCAR ESTUDIANTE POR NOMBRE")
    
    try:
        from models.estudiante import EstudianteModel
        
        nombre = input("Nombre o apellido a buscar: ").strip()
        if not nombre:
            print("❌ Debe ingresar un nombre o apellido")
            pausar()
            return
        
        estudiantes = EstudianteModel.buscar_por_nombre(nombre)
        
        if estudiantes:
            print(f"\n🔍 RESULTADOS DE BÚSQUEDA ({len(estudiantes)} encontrados):")
            print("-" * 70)
            
            for i, estudiante in enumerate(estudiantes, 1):
                print(f"{i:2}. {estudiante.nombre_completo:<30} {estudiante.ci_numero}-{estudiante.ci_expedicion:<10} {'✅' if estudiante.activo else '❌'}")
            
            print("-" * 70)
            
            # Opción para ver detalles
            print("\n🔍 Ingrese número para ver detalles (Enter para volver): ")
            seleccion = input("👉 ").strip()
            
            if seleccion.isdigit() and 1 <= int(seleccion) <= len(estudiantes):
                mostrar_detalles_estudiante(estudiantes[int(seleccion)-1])
        else:
            print(f"\n📭 No se encontraron estudiantes con '{nombre}'")
    
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
    
    pausar()

# En la función buscar_estudiante_ci(), después de mostrar_detalles_estudiante(estudiante)
# podemos mantener las opciones que ya tiene o mejorarlas

# En la función mostrar_detalles_estudiante(estudiante), mejorar las opciones:
def mostrar_detalles_estudiante(estudiante):
    """Muestra detalles completos de un estudiante"""
    print(f"\n📋 DETALLES COMPLETOS DEL ESTUDIANTE:")
    print("=" * 60)
    print(f"   ID: {estudiante.id}")
    print(f"   Nombre completo: {estudiante.nombre_completo}")
    print(f"   CI: {estudiante.ci_numero}-{estudiante.ci_expedicion}")
    
    if hasattr(estudiante, 'fecha_nacimiento') and estudiante.fecha_nacimiento:
        print(f"   Fecha nacimiento: {estudiante.fecha_nacimiento}")
        if estudiante.edad:
            print(f"   Edad: {estudiante.edad} años")
    
    if hasattr(estudiante, 'telefono') and estudiante.telefono:
        print(f"   Teléfono: {estudiante.telefono}")
    
    if hasattr(estudiante, 'email') and estudiante.email:
        print(f"   Email: {estudiante.email}")
    
    if hasattr(estudiante, 'universidad_egreso') and estudiante.universidad_egreso:
        print(f"   Universidad: {estudiante.universidad_egreso}")
    
    if hasattr(estudiante, 'profesion') and estudiante.profesion:
        print(f"   Profesión: {estudiante.profesion}")
    
    print(f"   Fecha registro: {estudiante.fecha_registro[:10] if estudiante.fecha_registro else 'N/A'}")
    print(f"   Estado: {'✅ Activo' if estudiante.activo else '❌ Inactivo'}")
    print("=" * 60)
    
    # OPCIONES MEJORADAS
    print("\n🔧 OPCIONES DISPONIBLES:")
    print("  1. Editar información del estudiante")
    print("  2. Activar/Desactivar estudiante")
    print("  3. Ver matrículas del estudiante")
    print("  4. Registrar nueva matrícula")
    print("  5. Eliminar estudiante")
    print("  6. Volver al menú")
    
    opcion = input("\n👉 Seleccione opción: ").strip()
    
    if opcion == '1':
        editar_estudiante(estudiante)
    elif opcion == '2':
        if estudiante.activo:
            estudiante.desactivar()
            print("✅ Estudiante desactivado")
        else:
            estudiante.activar()
            print("✅ Estudiante activado")
    elif opcion == '3':
        # Ver matrículas del estudiante
        from models.matricula import MatriculaModel
        matriculas = MatriculaModel.buscar_por_estudiante(estudiante.id)
        
        if matriculas:
            print(f"\n📚 MATRÍCULAS DEL ESTUDIANTE ({len(matriculas)}):")
            for mat in matriculas:
                # Obtener datos del programa
                from database.database import db
                query = "SELECT codigo, nombre FROM programas_academicos WHERE id = ?"
                programa = db.fetch_one(query, (mat.programa_id,))
                
                if programa:
                    estado_pago = "✅" if mat.estado_pago == 'PAGADO' else "⚠️" if mat.estado_pago == 'PARCIAL' else "❌"
                    print(f"   • {programa['codigo']}: {programa['nombre']} - {estado_pago} {mat.estado_pago}")
        else:
            print("ℹ️  El estudiante no tiene matrículas registradas")
    elif opcion == '4':
        # Registrar nueva matrícula para este estudiante
        print(f"\n🎓 REGISTRAR NUEVA MATRÍCULA PARA: {estudiante.nombre_completo}")
        # Aquí podríamos llamar a una versión simplificada de registrar_matricula()
        # que ya tenga pre-seleccionado el estudiante
        print("⚠️  Esta funcionalidad se implementará próximamente")
    elif opcion == '5':
        confirmar = input("¿Está seguro de eliminar este estudiante? (s/n): ").lower()
        if confirmar == 's':
            try:
                # Verificar que no tenga matrículas activas
                from database.database import db
                query = "SELECT COUNT(*) as count FROM matriculas WHERE estudiante_id = ?"
                resultado = db.fetch_one(query, (estudiante.id,))
                
                if resultado and resultado['count'] > 0:
                    print("❌ No se puede eliminar. El estudiante tiene matrículas registradas.")
                else:
                    estudiante.delete()
                    print("✅ Estudiante eliminado exitosamente")
            except Exception as e:
                print(f"❌ Error al eliminar: {e}")

def editar_estudiante(estudiante):
    """Permite editar un estudiante encontrado"""
    print(f"\n✏️ EDITANDO ESTUDIANTE: {estudiante.nombre_completo}")
    print("-" * 40)
    
    try:
        from models.estudiante import EstudianteModel
        
        print("Deje en blanco para mantener el valor actual.")
        print("-" * 40)
        
        # Nombres (no se puede cambiar el CI)
        print(f"⚠️  CI: {estudiante.ci_numero}-{estudiante.ci_expedicion} (NO SE PUEDE CAMBIAR)")
        
        # Nombres
        nombres_actual = estudiante.nombres
        nuevos_nombres = input(f"Nombres [{nombres_actual}]: ").strip()
        if nuevos_nombres:
            estudiante.nombres = nuevos_nombres
        
        # Apellidos
        apellidos_actual = estudiante.apellidos
        nuevos_apellidos = input(f"Apellidos [{apellidos_actual}]: ").strip()
        if nuevos_apellidos:
            estudiante.apellidos = nuevos_apellidos
        
        # Email
        email_actual = estudiante.email if hasattr(estudiante, 'email') and estudiante.email else ""
        nuevo_email = input(f"Email [{email_actual}]: ").strip()
        if nuevo_email:
            if '@' in nuevo_email and '.' in nuevo_email:
                estudiante.email = nuevo_email
            else:
                print(f"❌ Email no válido. Se mantiene: {email_actual}")
        
        # Teléfono
        telefono_actual = estudiante.telefono if hasattr(estudiante, 'telefono') and estudiante.telefono else ""
        nuevo_telefono = input(f"Teléfono [{telefono_actual}]: ").strip()
        if nuevo_telefono:
            estudiante.telefono = nuevo_telefono
        
        # Fecha de nacimiento
        if hasattr(estudiante, 'fecha_nacimiento'):
            fecha_actual = estudiante.fecha_nacimiento if estudiante.fecha_nacimiento else ""
            nueva_fecha = input(f"Fecha nacimiento (AAAA-MM-DD) [{fecha_actual}]: ").strip()
            if nueva_fecha:
                # Validar formato básico
                if len(nueva_fecha) == 10 and nueva_fecha[4] == '-' and nueva_fecha[7] == '-':
                    estudiante.fecha_nacimiento = nueva_fecha
                else:
                    print(f"❌ Formato no válido. Use AAAA-MM-DD. Se mantiene: {fecha_actual}")
        
        # Universidad
        if hasattr(estudiante, 'universidad_egreso'):
            universidad_actual = estudiante.universidad_egreso if estudiante.universidad_egreso else ""
            nueva_universidad = input(f"Universidad de egreso [{universidad_actual}]: ").strip()
            if nueva_universidad:
                estudiante.universidad_egreso = nueva_universidad
        
        # Profesión
        if hasattr(estudiante, 'profesion'):
            profesion_actual = estudiante.profesion if estudiante.profesion else ""
            nueva_profesion = input(f"Profesión [{profesion_actual}]: ").strip()
            if nueva_profesion:
                estudiante.profesion = nueva_profesion
        
        # Activo/Inactivo
        estado_actual = "Activo" if estudiante.activo else "Inactivo"
        cambiar_estado = input(f"¿Cambiar estado? Actual: {estado_actual} (s/n): ").lower()
        if cambiar_estado == 's':
            estudiante.activo = 0 if estudiante.activo else 1
        
        # Confirmar cambios
        print("\n📋 RESUMEN DE CAMBIOS:")
        print(f"   • Nombre completo: {estudiante.nombre_completo}")
        print(f"   • CI: {estudiante.ci_numero}-{estudiante.ci_expedicion}")
        if hasattr(estudiante, 'email') and estudiante.email:
            print(f"   • Email: {estudiante.email}")
        if hasattr(estudiante, 'telefono') and estudiante.telefono:
            print(f"   • Teléfono: {estudiante.telefono}")
        print(f"   • Estado: {'✅ Activo' if estudiante.activo else '❌ Inactivo'}")
        
        confirmar = input("\n👉 ¿Confirmar cambios? (s/n): ").lower()
        
        if confirmar == 's':
            estudiante.save()
            print("✅ Estudiante actualizado exitosamente")
            return estudiante
        else:
            print("❌ Cambios cancelados")
            return None
    
    except Exception as e:
        print(f"❌ Error al editar estudiante: {e}")
        return None

def ver_estadisticas_estudiantes():
    """Muestra estadísticas de estudiantes"""
    mostrar_encabezado("ESTADÍSTICAS DE ESTUDIANTES")
    
    try:
        from models.estudiante import EstudianteModel
        
        estadisticas = EstudianteModel.obtener_estadisticas()
        
        print("📈 ESTADÍSTICAS GENERALES:")
        print("-" * 40)
        print(f"   • Total estudiantes: {estadisticas['total_estudiantes']}")
        print(f"   • Estudiantes activos: {estadisticas['estudiantes_activos']}")
        print(f"   • Estudiantes inactivos: {estadisticas['estudiantes_inactivos']}")
        print(f"   • Porcentaje activos: {estadisticas['porcentaje_activos']:.1f}%")
        
        # Información adicional de la base de datos
        from database.database import db
        query = "SELECT COUNT(DISTINCT profesion) as profesiones FROM estudiantes WHERE profesion IS NOT NULL"
        resultado = db.fetch_one(query)
        if resultado and resultado['profesiones']:
            print(f"   • Profesiones distintas: {resultado['profesiones']}")
        
        query = "SELECT COUNT(DISTINCT universidad_egreso) as universidades FROM estudiantes WHERE universidad_egreso IS NOT NULL"
        resultado = db.fetch_one(query)
        if resultado and resultado['universidades']:
            print(f"   • Universidades distintas: {resultado['universidades']}")
        
        print("\n📊 DISTRIBUCIÓN POR EXPEDICIÓN:")
        print("-" * 40)
        query = "SELECT ci_expedicion, COUNT(*) as cantidad FROM estudiantes GROUP BY ci_expedicion ORDER BY cantidad DESC"
        resultados = db.fetch_all(query)
        
        for row in resultados:
            print(f"   • {row['ci_expedicion']}: {row['cantidad']} estudiantes")
    
    except Exception as e:
        print(f"❌ Error al obtener estadísticas: {e}")
    
    pausar()

# ============================================
# FUNCIONES DE GESTIÓN DE DOCENTES
# ============================================

def registrar_docente():
    """Registra un nuevo docente - FUNCIÓN COMPLETA"""
    mostrar_encabezado("REGISTRAR NUEVO DOCENTE")
    
    try:
        from models.docente import DocenteModel
        
        print("📝 Complete los datos del docente/tutor:")
        print("-" * 40)
        
        # Datos obligatorios
        ci_numero = input("Número de CI: ").strip()
        if not ci_numero:
            print("❌ El número de CI es obligatorio")
            pausar()
            return
        
        ci_expedicion = input("Expedición (BE, CH, CB, LP, OR, PD, PT, SC, TJ, EX): ").strip().upper()
        if ci_expedicion not in DocenteModel.EXPEDICIONES_VALIDAS:
            print(f"❌ Expedición inválida. Use: {', '.join(DocenteModel.EXPEDICIONES_VALIDAS)}")
            pausar()
            return
        
        nombres = input("Nombres: ").strip()
        if not nombres:
            print("❌ Los nombres son obligatorios")
            pausar()
            return
        
        apellidos = input("Apellidos: ").strip()
        if not apellidos:
            print("❌ Los apellidos son obligatorios")
            pausar()
            return
        
        # Datos opcionales
        fecha_nacimiento = input("Fecha de nacimiento (AAAA-MM-DD, opcional): ").strip()
        
        print("\n🎓 Grado académico máximo (opcional):")
        print("   Opciones: Mtr., Mgtr., Mag., MBA, MSc, M.Sc., PhD., Dr., Dra.")
        max_grado_academico = input("   Grado: ").strip()
        if max_grado_academico and max_grado_academico not in DocenteModel.GRADOS_VALIDOS:
            print(f"⚠️  Grado no válido, se omitirá")
            max_grado_academico = None
        
        telefono = input("Teléfono (opcional): ").strip()
        email = input("Email (opcional): ").strip()
        especialidad = input("Especialidad (opcional): ").strip()
        
        honorario_hora = input("Honorario por hora (opcional, ej: 50.00): ").strip()
        if honorario_hora:
            try:
                honorario_hora = float(honorario_hora)
                if honorario_hora < 0:
                    print("⚠️  Honorario no puede ser negativo, se omitirá")
                    honorario_hora = 0.0
            except ValueError:
                print("⚠️  Valor no válido, se usará 0.00")
                honorario_hora = 0.0
        else:
            honorario_hora = 0.0
        
        # Crear diccionario con datos
        datos = {
            'ci_numero': ci_numero,
            'ci_expedicion': ci_expedicion,
            'nombres': nombres,
            'apellidos': apellidos,
            'honorario_hora': honorario_hora
        }
        
        # Agregar campos opcionales
        if fecha_nacimiento:
            datos['fecha_nacimiento'] = fecha_nacimiento
        if max_grado_academico:
            datos['max_grado_academico'] = max_grado_academico
        if telefono:
            datos['telefono'] = telefono
        if email:
            if '@' in email and '.' in email:
                datos['email'] = email
            else:
                print("⚠️  Email no válido, se omitirá")
        if especialidad:
            datos['especialidad'] = especialidad
        
        # Crear y guardar docente
        docente = DocenteModel.crear_docente(datos)
        
        print(f"\n✅ ¡DOCENTE REGISTRADO EXITOSAMENTE!")
        print(f"\n📋 DATOS DEL DOCENTE:")
        print(f"   ID: {docente.id}")
        print(f"   Nombre completo: {docente.nombre_completo}")
        print(f"   CI: {docente.ci_numero}-{docente.ci_expedicion}")
        
        if hasattr(docente, 'max_grado_academico') and docente.max_grado_academico:
            print(f"   Grado académico: {docente.max_grado_academico}")
            print(f"   Nombre con grado: {docente.obtener_grado_completo}")
        
        if hasattr(docente, 'especialidad') and docente.especialidad:
            print(f"   Especialidad: {docente.especialidad}")
        
        if hasattr(docente, 'honorario_hora') and docente.honorario_hora:
            print(f"   Honorario por hora: ${docente.honorario_hora:.2f}")
        
        print(f"   Fecha registro: {docente.created_at[:10] if docente.created_at else 'N/A'}")
        
    except ValueError as e:
        print(f"\n❌ Error de validación: {e}")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
    
    pausar()

def listar_docentes():
    """Lista todos los docentes"""
    mostrar_encabezado("LISTA DE DOCENTES")
    
    try:
        from models.docente import DocenteModel
        
        docentes = DocenteModel.all()
        
        if not docentes:
            print("📭 No hay docentes registrados en el sistema.")
        else:
            print(f"📊 Total docentes: {len(docentes)}")
            print("-" * 90)
            print(f"{'ID':<5} {'CI':<15} {'NOMBRE COMPLETO':<30} {'ESPECIALIDAD':<20} {'HONORARIO/H':<10} {'ESTADO'}")
            print("-" * 90)
            
            for docente in docentes:
                estado = "✅" if docente.activo else "❌"
                ci_completo = f"{docente.ci_numero}-{docente.ci_expedicion}"
                especialidad = docente.especialidad if hasattr(docente, 'especialidad') and docente.especialidad else "N/A"
                honorario = f"${docente.honorario_hora:.2f}" if hasattr(docente, 'honorario_hora') and docente.honorario_hora else "$0.00"
                
                print(f"{docente.id:<5} {ci_completo:<15} {docente.nombre_completo:<30} {especialidad:<20} {honorario:<10} {estado}")
            
            print("-" * 90)
            
    except Exception as e:
        print(f"❌ Error al listar docentes: {e}")
    
    pausar()

def buscar_docente_ci():
    """Busca docente por CI"""
    mostrar_encabezado("BUSCAR DOCENTE POR CI")
    
    try:
        from models.docente import DocenteModel
        
        ci_numero = input("Número de CI (sin expedición): ").strip()
        if not ci_numero:
            print("❌ Debe ingresar un número de CI")
            pausar()
            return
        
        ci_expedicion = input("Expedición (opcional, Enter para omitir): ").strip().upper()
        
        docente = DocenteModel.buscar_por_ci(ci_numero, ci_expedicion if ci_expedicion else None)
        
        if docente:
            print(f"\n✅ DOCENTE ENCONTRADO:")
            print(f"\n📋 DATOS DEL DOCENTE:")
            print("=" * 60)
            print(f"   ID: {docente.id}")
            print(f"   Nombre completo: {docente.nombre_completo}")
            print(f"   CI: {docente.ci_numero}-{docente.ci_expedicion}")
            
            if hasattr(docente, 'max_grado_academico') and docente.max_grado_academico:
                print(f"   Grado académico: {docente.max_grado_academico}")
                print(f"   Nombre con grado: {docente.obtener_grado_completo}")
            
            if hasattr(docente, 'especialidad') and docente.especialidad:
                print(f"   Especialidad: {docente.especialidad}")
            
            if hasattr(docente, 'honorario_hora') and docente.honorario_hora:
                print(f"   Honorario por hora: ${docente.honorario_hora:.2f}")
            
            if hasattr(docente, 'email') and docente.email:
                print(f"   Email: {docente.email}")
            
            if hasattr(docente, 'telefono') and docente.telefono:
                print(f"   Teléfono: {docente.telefono}")
            
            print(f"   Fecha registro: {docente.created_at[:10] if docente.created_at else 'N/A'}")
            print(f"   Estado: {'✅ Activo' if docente.activo else '❌ Inactivo'}")
            print("=" * 60)
            
            # OPCIONES DESPUÉS DE ENCONTRAR
            print("\n🔧 OPCIONES DISPONIBLES:")
            print("  1. Editar docente")
            print("  2. Activar/Desactivar docente")
            print("  3. Ver programas asignados")
            print("  4. Eliminar docente")
            print("  5. Volver al menú")
            
            opcion = input("\n👉 Seleccione una opción: ").strip()
            
            if opcion == '1':
                editar_docente(docente)
            elif opcion == '2':
                if docente.activo:
                    confirmar = input("¿Desactivar docente? (s/n): ").lower()
                    if confirmar == 's':
                        docente.desactivar()
                        print("✅ Docente desactivado")
                else:
                    confirmar = input("¿Activar docente? (s/n): ").lower()
                    if confirmar == 's':
                        docente.activar()
                        print("✅ Docente activado")
            elif opcion == '3':
                # Ver programas asignados
                from models.programa import ProgramaModel
                programas = ProgramaModel.buscar_por_tutor(docente.id)
                if programas:
                    print(f"\n📚 PROGRAMAS ASIGNADOS ({len(programas)}):")
                    for prog in programas:
                        print(f"   • {prog.codigo}: {prog.nombre} ({prog.estado})")
                else:
                    print("ℹ️  El docente no tiene programas asignados")
            elif opcion == '4':
                confirmar = input("¿Está seguro de eliminar este docente? (s/n): ").lower()
                if confirmar == 's':
                    try:
                        # Verificar si está asignado a programas
                        from database.database import db
                        query = "SELECT COUNT(*) as count FROM programas_academicos WHERE tutor_id = ?"
                        resultado = db.fetch_one(query, (docente.id,))
                        
                        if resultado and resultado['count'] > 0:
                            print("❌ No se puede eliminar. El docente está asignado a programas.")
                            print("   Reasigne los programas primero.")
                        else:
                            docente.delete()
                            print("✅ Docente eliminado exitosamente")
                    except Exception as e:
                        print(f"❌ Error al eliminar: {e}")
            
            # Si no eligió eliminar, mostrar de nuevo los datos actualizados
            if opcion not in ['4', '5']:
                # Refrescar datos
                docente_actualizado = DocenteModel.find_by_id(docente.id)
                if docente_actualizado:
                    print(f"\n📋 DATOS ACTUALIZADOS:")
                    print(f"   • Estado: {'✅ Activo' if docente_actualizado.activo else '❌ Inactivo'}")
                    if hasattr(docente_actualizado, 'honorario_hora'):
                        print(f"   • Honorario: ${docente_actualizado.honorario_hora:.2f}")
        else:
            print(f"\n📭 No se encontró docente con CI {ci_numero}{'-' + ci_expedicion if ci_expedicion else ''}")
    
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
    
    pausar()

def editar_docente(docente):
    """Edita un docente existente"""
    print(f"\n✏️ EDITANDO DOCENTE: {docente.nombre_completo}")
    print("-" * 40)
    
    try:
        # Mostrar valores actuales
        print("Valores actuales (deje en blanco para mantener):")
        
        # Nombres
        nuevos_nombres = input(f"Nombres [{docente.nombres}]: ").strip()
        if nuevos_nombres:
            docente.nombres = nuevos_nombres
        
        # Apellidos
        nuevos_apellidos = input(f"Apellidos [{docente.apellidos}]: ").strip()
        if nuevos_apellidos:
            docente.apellidos = nuevos_apellidos
        
        # Expedición
        print(f"Expedición actual: {docente.ci_expedicion}")
        nueva_expedicion = input("Nueva expedición (BE, CH, CB, LP, OR, PD, PT, SC, TJ, EX) [dejar en blanco para mantener]: ").strip().upper()
        if nueva_expedicion:
            if nueva_expedicion in docente.EXPEDICIONES_VALIDAS:
                docente.ci_expedicion = nueva_expedicion
            else:
                print(f"❌ Expedición no válida. Se mantiene {docente.ci_expedicion}")
        
        # Grado académico
        if hasattr(docente, 'max_grado_academico'):
            print(f"Grado académico actual: {docente.max_grado_academico}")
        nuevo_grado = input("Nuevo grado (Mtr., Mgtr., Mag., MBA, MSc, M.Sc., PhD., Dr., Dra.) [dejar en blanco para mantener]: ").strip()
        if nuevo_grado:
            if nuevo_grado in docente.GRADOS_VALIDOS:
                docente.max_grado_academico = nuevo_grado
            else:
                print("❌ Grado no válido. Se mantiene el actual.")
        
        # Especialidad
        if hasattr(docente, 'especialidad'):
            especialidad_actual = docente.especialidad if docente.especialidad else "No definida"
            print(f"Especialidad actual: {especialidad_actual}")
        nueva_especialidad = input("Nueva especialidad [dejar en blanco para mantener]: ").strip()
        if nueva_especialidad:
            docente.especialidad = nueva_especialidad
        
        # Honorario por hora
        if hasattr(docente, 'honorario_hora'):
            print(f"Honorario por hora actual: ${docente.honorario_hora:.2f}")
            nuevo_honorario = input("Nuevo honorario por hora [dejar en blanco para mantener]: ").strip()
            if nuevo_honorario:
                try:
                    honorario = float(nuevo_honorario)
                    if honorario >= 0:
                        docente.honorario_hora = honorario
                    else:
                        print("❌ Honorario no puede ser negativo. Se mantiene el actual.")
                except ValueError:
                    print("❌ Valor no válido. Se mantiene el actual.")
        
        # Email
        if hasattr(docente, 'email'):
            email_actual = docente.email if docente.email else "No definido"
            print(f"Email actual: {email_actual}")
        nuevo_email = input("Nuevo email [dejar en blanco para mantener]: ").strip()
        if nuevo_email:
            # Validación simple de email
            if '@' in nuevo_email and '.' in nuevo_email:
                docente.email = nuevo_email
            else:
                print("❌ Email no válido. Se mantiene el actual.")
        
        # Teléfono
        if hasattr(docente, 'telefono'):
            telefono_actual = docente.telefono if docente.telefono else "No definido"
            print(f"Teléfono actual: {telefono_actual}")
        nuevo_telefono = input("Nuevo teléfono [dejar en blanco para mantener]: ").strip()
        if nuevo_telefono:
            docente.telefono = nuevo_telefono
        
        # Activo
        estado_actual = "Activo" if docente.activo else "Inactivo"
        print(f"Estado actual: {estado_actual}")
        cambiar_estado = input("¿Cambiar estado? (s/n) [n]: ").strip().lower()
        if cambiar_estado == 's':
            docente.activo = 0 if docente.activo else 1
        
        # Confirmar cambios
        print("\n📋 RESUMEN DE CAMBIOS:")
        print(f"   • Nombre: {docente.nombre_completo}")
        print(f"   • CI: {docente.ci_numero}-{docente.ci_expedicion}")
        if hasattr(docente, 'max_grado_academico') and docente.max_grado_academico:
            print(f"   • Grado: {docente.max_grado_academico}")
        if hasattr(docente, 'especialidad') and docente.especialidad:
            print(f"   • Especialidad: {docente.especialidad}")
        if hasattr(docente, 'honorario_hora'):
            print(f"   • Honorario: ${docente.honorario_hora:.2f}")
        print(f"   • Estado: {'✅ Activo' if docente.activo else '❌ Inactivo'}")
        
        confirmar = input("\n¿Confirmar cambios? (s/n): ").lower()
        
        if confirmar == 's':
            docente.save()
            print("✅ Docente actualizado exitosamente")
        else:
            print("❌ Cambios cancelados")
    
    except Exception as e:
        print(f"❌ Error al editar docente: {e}")

def buscar_docente_especialidad():
    """Busca docentes por especialidad"""
    mostrar_encabezado("BUSCAR DOCENTE POR ESPECIALIDAD")
    
    try:
        from models.docente import DocenteModel
        
        especialidad = input("Especialidad a buscar: ").strip()
        if not especialidad:
            print("❌ Debe ingresar una especialidad")
            pausar()
            return
        
        docentes = DocenteModel.buscar_por_especialidad(especialidad)
        
        if docentes:
            print(f"\n🔍 RESULTADOS DE BÚSQUEDA ({len(docentes)} encontrados):")
            print("-" * 80)
            
            for i, docente in enumerate(docentes, 1):
                honorario = f"${docente.honorario_hora:.2f}" if docente.honorario_hora else "$0.00"
                print(f"{i:2}. {docente.nombre_completo:<30} {docente.especialidad:<25} {honorario:<10} {'✅' if docente.activo else '❌'}")
            
            print("-" * 80)
        else:
            print(f"\n📭 No se encontraron docentes con especialidad '{especialidad}'")
    
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
    
    pausar()

def ver_estadisticas_docentes():
    """Muestra estadísticas de docentes"""
    mostrar_encabezado("ESTADÍSTICAS DE DOCENTES")
    
    try:
        from models.docente import DocenteModel
        
        estadisticas = DocenteModel.obtener_estadisticas()
        
        print("📈 ESTADÍSTICAS GENERALES:")
        print("-" * 40)
        print(f"   • Total docentes: {estadisticas['total_docentes']}")
        print(f"   • Docentes activos: {estadisticas['docentes_activos']}")
        print(f"   • Docentes inactivos: {estadisticas['docentes_inactivos']}")
        
        if estadisticas['promedio_honorario_hora'] > 0:
            print(f"\n💰 ESTADÍSTICAS DE HONORARIOS:")
            print("-" * 40)
            print(f"   • Promedio por hora: ${estadisticas['promedio_honorario_hora']:.2f}")
            print(f"   • Mínimo por hora: ${estadisticas['minimo_honorario_hora']:.2f}")
            print(f"   • Máximo por hora: ${estadisticas['maximo_honorario_hora']:.2f}")
        
        # Información adicional
        from database.database import db
        query = "SELECT COUNT(DISTINCT especialidad) as especialidades FROM docentes WHERE especialidad IS NOT NULL"
        resultado = db.fetch_one(query)
        if resultado and resultado['especialidades']:
            print(f"\n🎓 ESPECIALIDADES DISTINTAS: {resultado['especialidades']}")
            
            query = "SELECT especialidad, COUNT(*) as cantidad FROM docentes WHERE especialidad IS NOT NULL GROUP BY especialidad ORDER BY cantidad DESC"
            resultados = db.fetch_all(query)
            
            print("   Top especialidades:")
            for row in resultados[:5]:  # Mostrar top 5
                print(f"      • {row['especialidad']}: {row['cantidad']} docentes")
    
    except Exception as e:
        print(f"❌ Error al obtener estadísticas: {e}")
    
    pausar()

# ============================================
# FUNCIONES DE GESTIÓN DE PROGRAMAS
# ============================================

def crear_programa():
    """Crea un nuevo programa académico"""
    mostrar_encabezado("CREAR NUEVO PROGRAMA ACADÉMICO")
    
    try:
        from models.programa import ProgramaModel
        from datetime import datetime
        # Importar las funciones de cálculos financieros
        from utils.calculos_financieros import (
            calcular_descuento_exacto,
            calcular_porcentaje_para_monto_final,
            formatear_moneda,
            redondear_a_entero_cercano
        )
        
        print("📝 Complete los datos del programa académico:")
        print("-" * 40)
        
        # Datos obligatorios
        codigo = input("Código del programa (ej: DIP-001): ").strip()
        if not codigo:
            print("❌ El código es obligatorio")
            pausar()
            return
        
        nombre = input("Nombre del programa: ").strip()
        if not nombre:
            print("❌ El nombre es obligatorio")
            pausar()
            return
        
        # NUEVO: Costos separados según el anuncio
        print("\n💵 COSTOS SEPARADOS (según estructura del anuncio):")
        print("-" * 40)
        
        costo_inscripcion = input("Costo de INSCRIPCIÓN (Bs.): ").strip()
        if not costo_inscripcion:
            costo_inscripcion = "0"
        
        costo_matricula = input("Costo de MATRÍCULA (Bs.): ").strip()
        if not costo_matricula:
            costo_matricula = "0"
        
        costo_base = input("Costo de COLEGIATURA (Bs.): ").strip()
        if not costo_base:
            print("❌ El costo de colegiatura es obligatorio")
            pausar()
            return
        
        try:
            costo_inscripcion = float(costo_inscripcion)
            costo_matricula = float(costo_matricula)
            costo_base = float(costo_base)
            
            if costo_base <= 0:
                print("❌ La colegiatura debe ser mayor a 0")
                pausar()
                return
                
            if costo_inscripcion < 0 or costo_matricula < 0:
                print("❌ Los costos no pueden ser negativos")
                pausar()
                return
                
        except ValueError:
            print("❌ Los costos deben ser números válidos")
            pausar()
            return
        
        cupos_totales = input("Cupos totales: ").strip()
        if not cupos_totales:
            print("❌ Los cupos totales son obligatorios")
            pausar()
            return
        
        try:
            cupos_totales = int(cupos_totales)
            if cupos_totales <= 0:
                print("❌ Los cupos deben ser mayor a 0")
                pausar()
                return
        except ValueError:
            print("❌ Los cupos deben ser un número entero")
            pausar()
            return
        
        # NUEVO: Configuración de promoción según anuncio
        print("\n🎁 CONFIGURACIÓN DE PROMOCIÓN (opcional):")
        print("-" * 40)
        
        promocion_activa = False
        descripcion_promocion = ""
        descuento_promocion = 0
        promocion_fecha_limite = None
        
        activar_promo = input("¿Activar promoción? (s/n): ").lower().strip()
        if activar_promo == 's':
            promocion_activa = True
            descripcion_promocion = input("Descripción de la promoción (ej: 'Inscripción temprana'): ").strip()
            
            # Preguntar método de ingreso del descuento
            print("\n📊 ¿Cómo desea ingresar el descuento?")
            print("  1. Porcentaje de descuento (ej: 7.37%)")
            print("  2. Monto final deseado (ej: 3520 Bs.)")
            
            metodo_promo = input("Seleccione (1/2) [1]: ").strip() or "1"
            
            if metodo_promo == "1":
                descuento_promo = input("Porcentaje de descuento sobre colegiatura (%): ").strip()
                if descuento_promo:
                    try:
                        descuento_promocion = float(descuento_promo)
                        if descuento_promocion < 0 or descuento_promocion > 100:
                            print("⚠️  Descuento fuera de rango (0-100), se establecerá en 0")
                            descuento_promocion = 0
                        else:
                            # Calcular y mostrar el monto final exacto
                            descuento_bs, monto_final = calcular_descuento_exacto(
                                costo_base, 
                                descuento_promocion
                            )
                            print(f"   Monto final calculado: ${formatear_moneda(monto_final)} Bs.")
                    except:
                        print("⚠️  Descuento no válido, se establecerá en 0")
                        descuento_promocion = 0
            elif metodo_promo == "2":
                monto_final = input("Monto final deseado de la colegiatura (Bs.): ").strip()
                if monto_final:
                    try:
                        monto_final_float = float(monto_final)
                        if monto_final_float <= 0 or monto_final_float > costo_base:
                            print("⚠️  Monto fuera de rango, se establecerá descuento 0")
                            descuento_promocion = 0
                        else:
                            # Calcular porcentaje necesario con precisión
                            descuento_promocion = calcular_porcentaje_para_monto_final(
                                costo_base, 
                                monto_final_float
                            )
                            print(f"   Descuento calculado: {descuento_promocion:.6f}%")
                            
                            # Verificar cálculo exacto
                            descuento_bs, monto_final_calculado = calcular_descuento_exacto(
                                costo_base, 
                                descuento_promocion
                            )
                            if abs(monto_final_calculado - monto_final_float) > 0.01:
                                print(f"   ⚠️  Monto final: ${formatear_moneda(monto_final_calculado)} Bs. (ajuste por redondeo)")
                            else:
                                print(f"   Monto final exacto: ${formatear_moneda(monto_final_calculado)} Bs.")
                    except ValueError:
                        print("⚠️  Monto no válido, se establecerá descuento 0")
                        descuento_promocion = 0
                    except Exception as e:
                        print(f"⚠️  Error en cálculo: {e}")
                        descuento_promocion = 0
            else:
                print("⚠️  Opción no válida, se usará método 1 (porcentaje)")
                # Si el usuario ingresa una opción no válida, pedir porcentaje
                descuento_promo = input("Porcentaje de descuento sobre colegiatura (%): ").strip()
                if descuento_promo:
                    try:
                        descuento_promocion = float(descuento_promo)
                        if descuento_promocion < 0 or descuento_promocion > 100:
                            print("⚠️  Descuento fuera de rango (0-100), se establecerá en 0")
                            descuento_promocion = 0
                    except:
                        print("⚠️  Descuento no válido, se establecerá en 0")
                        descuento_promocion = 0
            
            fecha_limite = input("Fecha límite de la promoción (YYYY-MM-DD, opcional): ").strip()
            if fecha_limite:
                try:
                    # Validar formato de fecha
                    datetime.strptime(fecha_limite, "%Y-%m-%d")
                    promocion_fecha_limite = fecha_limite
                except ValueError:
                    print("⚠️  Formato de fecha inválido, se omitirá")
        
        # Datos opcionales existentes
        descripcion = input("\nDescripción del programa (opcional): ").strip()
        
        # NUEVO: Duración en MESES (convertiremos a semanas internamente)
        duracion_meses = input("Duración en MESES (opcional): ").strip()
        duracion_semanas = None
        if duracion_meses:
            try:
                duracion_meses_int = int(duracion_meses)
                duracion_semanas = duracion_meses_int * 4  # Conversión aproximada
            except:
                print("⚠️  Duración no válida, se omitirá")
        
        horas_totales = input("Horas totales (opcional): ").strip()
        
        # Descuento por pago al contado
        descuento_contado_input = input("Descuento por pago al contado % (0-100, opcional): ").strip()
        descuento_contado = 0
        if descuento_contado_input:
            try:
                descuento_contado = float(descuento_contado_input)
                if descuento_contado < 0 or descuento_contado > 100:
                    print("⚠️  Descuento fuera de rango (0-100), se establecerá en 0")
                    descuento_contado = 0
                else:
                    # Calcular y mostrar monto con descuento
                    descuento_contado_bs, monto_con_descuento = calcular_descuento_exacto(
                        costo_base, 
                        descuento_contado
                    )
                    print(f"   Colegiatura con descuento contado: ${formatear_moneda(monto_con_descuento)} Bs.")
            except:
                print("⚠️  Descuento no válido, se establecerá en 0")
                descuento_contado = 0
        
        # NUEVO: Configuración de cuotas mensuales
        print("\n📅 CONFIGURACIÓN DE CUOTAS:")
        print("-" * 30)
        cuotas_mensuales = input("¿Cuotas mensuales? (s/n) [s]: ").lower().strip()
        es_mensual = (cuotas_mensuales == 's' or cuotas_mensuales == '')
        
        dias_entre_cuotas = 30  # Por defecto mensual
        if not es_mensual:
            dias_input = input("Días entre cuotas [30]: ").strip()
            if dias_input:
                try:
                    dias_entre_cuotas = int(dias_input)
                except:
                    print("⚠️  Días no válidos, se usará 30")
        
        # Estado por defecto será PLANIFICADO
        estado = "PLANIFICADO"
        
        # Crear diccionario con datos
        datos = {
            'codigo': codigo,
            'nombre': nombre,
            'costo_base': costo_base,
            'costo_inscripcion': costo_inscripcion,
            'costo_matricula': costo_matricula,
            'cupos_totales': cupos_totales,
            'estado': estado,
            'descuento_contado': descuento_contado,
            'promocion_activa': promocion_activa,
            'descripcion_promocion': descripcion_promocion,
            'descuento_promocion': descuento_promocion,
            'promocion_fecha_limite': promocion_fecha_limite,
            'cuotas_mensuales': es_mensual,
            'dias_entre_cuotas': dias_entre_cuotas
        }
        
        # Agregar campos opcionales
        if descripcion:
            datos['descripcion'] = descripcion
        
        if duracion_semanas:
            datos['duracion_semanas'] = duracion_semanas
        
        if horas_totales:
            try:
                datos['horas_totales'] = int(horas_totales)
            except:
                print("⚠️  Horas no válidas, se omitirá")
        
        # Crear y guardar programa
        programa = ProgramaModel.crear_programa(datos)
        
        print(f"\n✅ ¡PROGRAMA CREADO EXITOSAMENTE!")
        print(f"\n📋 DATOS DEL PROGRAMA:")
        print(f"   ID: {programa.id}")
        print(f"   Código: {programa.codigo}")
        print(f"   Nombre: {programa.nombre}")
        
        print(f"\n💵 COSTOS SEPARADOS:")
        print(f"   • Inscripción: ${formatear_moneda(programa.costo_inscripcion)} Bs.")
        print(f"   • Matrícula: ${formatear_moneda(programa.costo_matricula)} Bs.")
        print(f"   • Colegiatura: ${formatear_moneda(programa.costo_base)} Bs.")
        total = programa.costo_inscripcion + programa.costo_matricula + programa.costo_base
        print(f"   • TOTAL: ${formatear_moneda(total)} Bs.")
        
        if hasattr(programa, 'descuento_contado') and programa.descuento_contado > 0:
            descuento_contado_bs, colegiatura_con_descuento = calcular_descuento_exacto(
                programa.costo_base, 
                programa.descuento_contado
            )
            print(f"\n💰 DESCUENTO POR PAGO AL CONTADO:")
            print(f"   • Descuento: {programa.descuento_contado}%")
            print(f"   • Colegiatura con descuento: ${formatear_moneda(colegiatura_con_descuento)} Bs.")
            total_con_descuento = programa.costo_inscripcion + programa.costo_matricula + colegiatura_con_descuento
            print(f"   • Total con descuento: ${formatear_moneda(total_con_descuento)} Bs.")
        
        if hasattr(programa, 'promocion_activa') and programa.promocion_activa:
            print(f"\n🎁 PROMOCIÓN ACTIVA:")
            print(f"   • Descripción: {programa.descripcion_promocion}")
            print(f"   • Descuento sobre colegiatura: {programa.descuento_promocion:.6f}%")
            if hasattr(programa, 'promocion_fecha_limite') and programa.promocion_fecha_limite:
                print(f"   • Válido hasta: {programa.promocion_fecha_limite}")
            
            # Mostrar cálculo con promoción usando la función de cálculo exacto
            descuento_promo_bs, colegiatura_con_promo = calcular_descuento_exacto(
                programa.costo_base, 
                programa.descuento_promocion
            )
            print(f"\n📊 CÁLCULO CON PROMOCIÓN:")
            print(f"   • Colegiatura original: ${formatear_moneda(programa.costo_base)} Bs.")
            print(f"   • Descuento: ${formatear_moneda(descuento_promo_bs)} Bs.")
            print(f"   • Colegiatura con promoción: ${formatear_moneda(colegiatura_con_promo)} Bs.")
            
            # Mostrar si se redondea a entero
            if abs(colegiatura_con_promo - redondear_a_entero_cercano(colegiatura_con_promo)) < 0.01:
                print(f"   • Colegiatura (entero): ${redondear_a_entero_cercano(colegiatura_con_promo):.0f} Bs.")
            
            total_con_promo = programa.costo_inscripcion + programa.costo_matricula + colegiatura_con_promo
            print(f"   • Total con promoción: ${formatear_moneda(total_con_promo)} Bs.")
        
        print(f"\n📊 OTROS DATOS:")
        print(f"   • Cupos: {programa.cupos_disponibles}/{programa.cupos_totales}")
        print(f"   • Estado: {programa.estado}")
        
        if hasattr(programa, 'duracion_semanas') and programa.duracion_semanas:
            meses = programa.duracion_semanas // 4
            print(f"   • Duración: {programa.duracion_semanas} semanas (~{meses} meses)")
        
        if hasattr(programa, 'horas_totales') and programa.horas_totales:
            print(f"   • Horas totales: {programa.horas_totales}")
        
        print(f"   • Cuotas: {'Mensuales' if es_mensual else 'Cada ' + str(dias_entre_cuotas) + ' días'}")
        
    except ValueError as e:
        print(f"\n❌ Error de validación: {e}")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
    
    pausar()

def listar_programas():
    """Lista todos los programas"""
    mostrar_encabezado("LISTA DE PROGRAMAS ACADÉMICOS")
    
    try:
        from models.programa import ProgramaModel
        
        programas = ProgramaModel.all()
        
        if not programas:
            print("📭 No hay programas registrados en el sistema.")
        else:
            print(f"📊 Total programas: {len(programas)}")
            print("-" * 100)
            print(f"{'ID':<5} {'CÓDIGO':<12} {'NOMBRE':<30} {'COSTO':<10} {'CUPOS':<12} {'ESTADO':<15} {'PROMOCIÓN'}")
            print("-" * 100)
            
            for programa in programas:
                estado = programa.estado
                cupos = f"{programa.cupos_disponibles}/{programa.cupos_totales}"
                costo = f"${programa.costo_base:.2f}"
                promocion = "✅" if programa.promocion_activa else "❌"
                
                print(f"{programa.id:<5} {programa.codigo:<12} {programa.nombre[:30]:<30} {costo:<10} {cupos:<12} {estado:<15} {promocion}")
            
            print("-" * 100)
            
            # Estadísticas rápidas
            con_cupos = len([p for p in programas if p.cupos_disponibles > 0])
            promociones = len([p for p in programas if p.promocion_activa])
            
            print(f"\n📈 RESUMEN:")
            print(f"   • Programas con cupos disponibles: {con_cupos}")
            print(f"   • Programas con promoción activa: {promociones}")
            print(f"   • Cupos totales disponibles: {sum(p.cupos_disponibles for p in programas)}")
    
    except Exception as e:
        print(f"❌ Error al listar programas: {e}")
    
    pausar()

def buscar_programa_codigo():
    """Busca programa por código"""
    mostrar_encabezado("BUSCAR PROGRAMA POR CÓDIGO")
    
    try:
        from models.programa import ProgramaModel
        from datetime import date
        
        codigo = input("Código del programa: ").strip()
        if not codigo:
            print("❌ Debe ingresar un código")
            pausar()
            return
        
        programa = ProgramaModel.buscar_por_codigo(codigo)
        
        if programa:
            print(f"\n✅ PROGRAMA ENCONTRADO:")
            print(f"\n📋 DATOS DEL PROGRAMA:")
            print("=" * 60)
            print(f"   ID: {programa.id}")
            print(f"   Código: {programa.codigo}")
            print(f"   Nombre: {programa.nombre}")
            
            if hasattr(programa, 'descripcion') and programa.descripcion:
                print(f"   Descripción: {programa.descripcion}")
            
            print(f"   Costo base: ${programa.costo_base:.2f}")
            
            if hasattr(programa, 'descuento_contado') and programa.descuento_contado:
                print(f"   Descuento por contado: {programa.descuento_contado}%")
                print(f"   Costo con descuento: ${programa.costo_con_descuento_contado:.2f}")
            
            print(f"   Cupos: {programa.cupos_disponibles}/{programa.cupos_totales}")
            print(f"   Estado: {programa.estado}")
            
            if hasattr(programa, 'promocion_activa') and programa.promocion_activa:
                print(f"   ⭐ PROMOCIÓN ACTIVA ⭐")
                print(f"   Descuento promoción: {programa.descuento_promocion}%")
                if hasattr(programa, 'descripcion_promocion') and programa.descripcion_promocion:
                    print(f"   Descripción: {programa.descripcion_promocion}")
                print(f"   Costo con promoción: ${programa.costo_con_promocion:.2f}")
            
            if hasattr(programa, 'duracion_semanas') and programa.duracion_semanas:
                print(f"   Duración: {programa.duracion_semanas} semanas")
            
            if hasattr(programa, 'horas_totales') and programa.horas_totales:
                print(f"   Horas totales: {programa.horas_totales}")
            
            if hasattr(programa, 'fecha_inicio_planificada') and programa.fecha_inicio_planificada:
                print(f"   Fecha inicio planificada: {programa.fecha_inicio_planificada}")
            
            if hasattr(programa, 'fecha_inicio_real') and programa.fecha_inicio_real:
                print(f"   Fecha inicio real: {programa.fecha_inicio_real}")
            
            print(f"   Fecha creación: {programa.created_at[:10] if programa.created_at else 'N/A'}")
            print("=" * 60)
            
            # OPCIONES DESPUÉS DE ENCONTRAR
            print("\n🔧 OPCIONES DISPONIBLES:")
            print("  1. Editar programa")
            print("  2. Asignar/Reasignar tutor")
            print("  3. Activar/Desactivar promoción")
            print("  4. Iniciar/Concluir programa")
            print("  5. Ver estudiantes inscritos")
            print("  6. Eliminar programa")
            print("  7. Volver al menú")
            
            opcion = input("\n👉 Seleccione una opción: ").strip()
            
            if opcion == '1':
                editar_programa(programa)
            elif opcion == '2':
                # Asignar tutor
                from models.docente import DocenteModel
                
                print("\n👨‍🏫 ASIGNAR TUTOR AL PROGRAMA")
                print("=" * 40)
                
                # Listar docentes activos
                docentes_activos = DocenteModel.buscar_activos()
                if not docentes_activos:
                    print("❌ No hay docentes activos disponibles")
                else:
                    print("Docentes disponibles:")
                    for i, doc in enumerate(docentes_activos, 1):
                        especialidad = doc.especialidad if hasattr(doc, 'especialidad') and doc.especialidad else "Sin especialidad"
                        print(f"{i:2}. {doc.nombre_completo} - {especialidad}")
                    
                    seleccion = input("\n👉 Seleccione docente (número) o 0 para quitar tutor: ").strip()
                    
                    if seleccion.isdigit():
                        num = int(seleccion)
                        if num == 0:
                            programa.tutor_id = None
                            programa.save()
                            print("✅ Tutor removido del programa")
                        elif 1 <= num <= len(docentes_activos):
                            docente = docentes_activos[num - 1]
                            programa.tutor_id = docente.id
                            programa.save()
                            print(f"✅ Tutor asignado: {docente.nombre_completo}")
                        else:
                            print("❌ Selección inválida")
                    else:
                        print("❌ Selección inválida")
            
            elif opcion == '3':
                # Activar/Desactivar promoción
                if programa.promocion_activa:
                    confirmar = input("¿Desactivar promoción? (s/n): ").lower()
                    if confirmar == 's':
                        programa.desactivar_promocion()
                        print("✅ Promoción desactivada")
                else:
                    descuento = input("Descuento para la promoción % (0-100): ").strip()
                    if descuento:
                        try:
                            desc = float(descuento)
                            if 0 <= desc <= 100:
                                descripcion = input("Descripción de la promoción: ").strip()
                                programa.activar_promocion(desc, descripcion)
                                print("✅ Promoción activada")
                            else:
                                print("❌ Descuento debe estar entre 0 y 100")
                        except ValueError:
                            print("❌ Valor no válido")
            
            elif opcion == '4':
                # Cambiar estado del programa
                print("\n📊 CAMBIAR ESTADO DEL PROGRAMA")
                print("=" * 40)
                print("  1. Iniciar programa")
                print("  2. Concluir programa")
                print("  3. Cancelar programa")
                print("  4. Volver a planificado")
                
                subopcion = input("\n👉 Seleccione: ").strip()
                
                if subopcion == '1':
                    if programa.estado != 'INICIADO':
                        fecha = input(f"Fecha de inicio [{date.today().isoformat()}]: ").strip()
                        if fecha:
                            try:
                                fecha_inicio = date.fromisoformat(fecha)
                                programa.iniciar_programa(fecha_inicio)
                            except ValueError:
                                print("❌ Fecha no válida. Usando fecha actual.")
                                programa.iniciar_programa()
                        else:
                            programa.iniciar_programa()
                        print("✅ Programa iniciado")
                    else:
                        print("ℹ️  El programa ya está iniciado")
                
                elif subopcion == '2':
                    if programa.estado == 'INICIADO':
                        fecha = input(f"Fecha de conclusión [{date.today().isoformat()}]: ").strip()
                        if fecha:
                            try:
                                fecha_fin = date.fromisoformat(fecha)
                                programa.concluir_programa(fecha_fin)
                            except ValueError:
                                print("❌ Fecha no válida. Usando fecha actual.")
                                programa.concluir_programa()
                        else:
                            programa.concluir_programa()
                        print("✅ Programa concluido")
                    else:
                        print("❌ Solo se puede concluir un programa que esté INICIADO")
                
                elif subopcion == '3':
                    confirmar = input("¿Cancelar programa? (s/n): ").lower()
                    if confirmar == 's':
                        programa.cancelar_programa()
                        print("✅ Programa cancelado")
                
                elif subopcion == '4':
                    if programa.estado != 'PLANIFICADO':
                        programa.estado = 'PLANIFICADO'
                        programa.updated_at = datetime.now().isoformat()
                        programa.save()
                        print("✅ Programa vuelto a estado PLANIFICADO")
                    else:
                        print("ℹ️  El programa ya está planificado")
            
            elif opcion == '5':
                # Ver estudiantes inscritos
                from models.matricula import MatriculaModel
                matriculas = MatriculaModel.buscar_por_programa(programa.id)
                
                if matriculas:
                    print(f"\n👥 ESTUDIANTES INSCRITOS ({len(matriculas)}):")
                    print("=" * 80)
                    for mat in matriculas:
                        # Obtener datos del estudiante
                        from database.database import db
                        query = "SELECT nombres, apellidos, ci_numero FROM estudiantes WHERE id = ?"
                        estudiante = db.fetch_one(query, (mat.estudiante_id,))
                        
                        if estudiante:
                            nombre_completo = f"{estudiante['nombres']} {estudiante['apellidos']}"
                            estado = "✅" if mat.estado_pago == 'PAGADO' else "⚠️" if mat.estado_pago == 'PARCIAL' else "❌"
                            print(f"   • {nombre_completo:<30} {estudiante['ci_numero']:<12} {estado} {mat.estado_pago}")
                else:
                    print("ℹ️  No hay estudiantes inscritos en este programa")
            
            elif opcion == '6':
                confirmar = input("¿Está seguro de eliminar este programa? (s/n): ").lower()
                if confirmar == 's':
                    try:
                        # Verificar que no haya matrículas
                        from database.database import db
                        query = "SELECT COUNT(*) as count FROM matriculas WHERE programa_id = ?"
                        resultado = db.fetch_one(query, (programa.id,))
                        
                        if resultado and resultado['count'] > 0:
                            print("❌ No se puede eliminar. Hay matrículas registradas en este programa.")
                        else:
                            programa.delete()
                            print("✅ Programa eliminado exitosamente")
                    except Exception as e:
                        print(f"❌ Error al eliminar: {e}")
            
            # Si no eligió eliminar, mostrar de nuevo los datos actualizados
            if opcion not in ['6', '7']:
                # Refrescar datos
                programa_actualizado = ProgramaModel.find_by_id(programa.id)
                if programa_actualizado:
                    print(f"\n📋 DATOS ACTUALIZADOS:")
                    print(f"   • Estado: {programa_actualizado.estado}")
                    print(f"   • Cupos disponibles: {programa_actualizado.cupos_disponibles}")
                    if hasattr(programa_actualizado, 'promocion_activa') and programa_actualizado.promocion_activa:
                        print(f"   • Promoción: ACTIVA ({programa_actualizado.descuento_promocion}% descuento)")
        else:
            print(f"\n📭 No se encontró programa con código '{codigo}'")
    
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
    
    pausar()

def editar_programa_menu():
    """Menú para editar un programa académico"""
    mostrar_encabezado("EDITAR PROGRAMA ACADÉMICO")
    
    try:
        from models.programa import ProgramaModel
        
        # Buscar programa por código
        codigo = input("Código del programa a editar: ").strip()
        programa = ProgramaModel.buscar_por_codigo(codigo)
        
        if not programa:
            print(f"❌ No se encontró programa con código {codigo}")
            pausar()
            return
        
        # Llamar a tu función existente editar_programa()
        editar_programa(programa)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    pausar()

def editar_programa(programa):
    """Edita un programa existente"""
    print(f"\n✏️ EDITANDO PROGRAMA: {programa.nombre_completo}")
    print("-" * 40)
    
    try:
        from models.programa import EstadoPrograma
        
        # Mostrar valores actuales
        print("Valores actuales (deje en blanco para mantener):")
        
        # Código (no se debe cambiar, es único)
        print(f"Código: {programa.codigo} (NO SE PUEDE CAMBIAR)")
        
        # Nombre
        nuevo_nombre = input(f"Nombre [{programa.nombre}]: ").strip()
        if nuevo_nombre:
            programa.nombre = nuevo_nombre
        
        # Descripción
        if hasattr(programa, 'descripcion'):
            desc_actual = programa.descripcion if programa.descripcion else "No definida"
            print(f"Descripción actual: {desc_actual}")
        nueva_desc = input("Nueva descripción [dejar en blanco para mantener]: ").strip()
        if nueva_desc:
            programa.descripcion = nueva_desc
        
        # Costo base
        if hasattr(programa, 'costo_base'):
            print(f"Costo base actual: ${programa.costo_base:.2f}")
            nuevo_costo = input("Nuevo costo base [dejar en blanco para mantener]: ").strip()
            if nuevo_costo:
                try:
                    costo = float(nuevo_costo)
                    if costo >= 0:
                        programa.costo_base = costo
                    else:
                        print("❌ Costo no puede ser negativo. Se mantiene el actual.")
                except ValueError:
                    print("❌ Valor no válido. Se mantiene el actual.")
        
        # Cupos totales
        if hasattr(programa, 'cupos_totales'):
            print(f"Cupos totales actuales: {programa.cupos_totales}")
            print(f"Cupos disponibles: {programa.cupos_disponibles}")
            nuevos_cupos = input("Nuevos cupos totales [dejar en blanco para mantener]: ").strip()
            if nuevos_cupos:
                try:
                    cupos = int(nuevos_cupos)
                    if cupos >= programa.cupos_totales - programa.cupos_disponibles:
                        # Ajustar cupos disponibles
                        diferencia = cupos - programa.cupos_totales
                        programa.cupos_totales = cupos
                        programa.cupos_disponibles += diferencia
                    else:
                        print(f"❌ No se puede reducir a menos de {programa.cupos_totales - programa.cupos_disponibles} cupos (ya ocupados).")
                except ValueError:
                    print("❌ Valor no válido. Se mantiene el actual.")
        
        # Descuento por contado
        if hasattr(programa, 'descuento_contado'):
            print(f"Descuento por contado actual: {programa.descuento_contado}%")
            nuevo_descuento = input("Nuevo descuento (0-100) [dejar en blanco para mantener]: ").strip()
            if nuevo_descuento:
                try:
                    descuento = float(nuevo_descuento)
                    if 0 <= descuento <= 100:
                        programa.descuento_contado = descuento
                    else:
                        print("❌ Descuento debe estar entre 0 y 100. Se mantiene el actual.")
                except ValueError:
                    print("❌ Valor no válido. Se mantiene el actual.")
        
        # Estado
        if hasattr(programa, 'estado'):
            print(f"Estado actual: {programa.estado}")
            print("Estados posibles: PLANIFICADO, INICIADO, CONCLUIDO, CANCELADO")
            nuevo_estado = input("Nuevo estado [dejar en blanco para mantener]: ").strip().upper()
            if nuevo_estado:
                if nuevo_estado in [e.value for e in EstadoPrograma]:
                    programa.estado = nuevo_estado
                else:
                    print("❌ Estado no válido. Se mantiene el actual.")
        
        # Duración en semanas
        if hasattr(programa, 'duracion_semanas'):
            duracion_actual = programa.duracion_semanas if programa.duracion_semanas else "No definida"
            print(f"Duración en semanas actual: {duracion_actual}")
            nueva_duracion = input("Nueva duración en semanas [dejar en blanco para mantener]: ").strip()
            if nueva_duracion:
                try:
                    duracion = int(nueva_duracion)
                    if duracion > 0:
                        programa.duracion_semanas = duracion
                    else:
                        print("❌ Duración debe ser positiva. Se mantiene el actual.")
                except ValueError:
                    print("❌ Valor no válido. Se mantiene el actual.")
        
        # Horas totales
        if hasattr(programa, 'horas_totales'):
            horas_actual = programa.horas_totales if programa.horas_totales else "No definidas"
            print(f"Horas totales actuales: {horas_actual}")
            nuevas_horas = input("Nuevas horas totales [dejar en blanco para mantener]: ").strip()
            if nuevas_horas:
                try:
                    horas = int(nuevas_horas)
                    if horas > 0:
                        programa.horas_totales = horas
                    else:
                        print("❌ Horas deben ser positivas. Se mantiene el actual.")
                except ValueError:
                    print("❌ Valor no válido. Se mantiene el actual.")
        
        # Promoción
        if hasattr(programa, 'promocion_activa'):
            promocion_actual = "Activa" if programa.promocion_activa else "Inactiva"
            print(f"Promoción actual: {promocion_actual}")
            if hasattr(programa, 'descuento_promocion') and programa.descuento_promocion:
                print(f"Descuento de promoción: {programa.descuento_promocion}%")
            
            activar_promo = input("¿Activar/desactivar promoción? (s/n) [n]: ").strip().lower()
            if activar_promo == 's':
                if programa.promocion_activa:
                    # Desactivar
                    programa.promocion_activa = 0
                else:
                    # Activar
                    programa.promocion_activa = 1
                    desc_promo = input(f"Descuento de promoción (0-100) [{programa.descuento_promocion if hasattr(programa, 'descuento_promocion') else 0}]: ").strip()
                    if desc_promo:
                        try:
                            desc = float(desc_promo)
                            if 0 <= desc <= 100:
                                programa.descuento_promocion = desc
                            else:
                                print("❌ Descuento debe estar entre 0 y 100. Se usa 0.")
                                programa.descuento_promocion = 0
                        except ValueError:
                            print("❌ Valor no válido. Se usa 0.")
                            programa.descuento_promocion = 0
                    
                    descripcion_promo = input("Descripción de la promoción [opcional]: ").strip()
                    if descripcion_promo:
                        programa.descripcion_promocion = descripcion_promo
        
        # Confirmar cambios
        print("\n📋 RESUMEN DE CAMBIOS:")
        print(f"   • Código: {programa.codigo}")
        print(f"   • Nombre: {programa.nombre}")
        print(f"   • Costo base: ${programa.costo_base:.2f}")
        print(f"   • Cupos: {programa.cupos_disponibles}/{programa.cupos_totales}")
        print(f"   • Estado: {programa.estado}")
        if hasattr(programa, 'descuento_contado') and programa.descuento_contado:
            print(f"   • Descuento contado: {programa.descuento_contado}%")
        if hasattr(programa, 'promocion_activa') and programa.promocion_activa:
            print(f"   • Promoción activa: Sí ({programa.descuento_promocion}% descuento)")
        
        confirmar = input("\n¿Confirmar cambios? (s/n): ").lower()
        
        if confirmar == 's':
            programa.save()
            print("✅ Programa actualizado exitosamente")
        else:
            print("❌ Cambios cancelados")
    
    except Exception as e:
        print(f"❌ Error al editar programa: {e}")

def buscar_programas_cupos():
    """Busca programas con cupos disponibles"""
    mostrar_encabezado("PROGRAMAS CON CUPOS DISPONIBLES")
    
    try:
        from models.programa import ProgramaModel
        
        programas = ProgramaModel.buscar_con_cupos_disponibles()
        
        if programas:
            print(f"🎯 PROGRAMAS DISPONIBLES PARA INSCRIPCIÓN ({len(programas)}):")
            print("-" * 100)
            print(f"{'ID':<5} {'CÓDIGO':<12} {'NOMBRE':<30} {'COSTO':<12} {'CUPOS DISP.':<12} {'ESTADO':<15}")
            print("-" * 100)
            
            for programa in programas:
                costo = f"${programa.costo_base:.2f}"
                if programa.promocion_activa and hasattr(programa, 'descuento_promocion'):
                    costo_promo = programa.costo_con_promocion
                    costo = f"${costo_promo:.2f} (Promo: -{programa.descuento_promocion}%)"
                
                print(f"{programa.id:<5} {programa.codigo:<12} {programa.nombre[:30]:<30} {costo:<12} {programa.cupos_disponibles:<12} {programa.estado:<15}")
            
            print("-" * 100)
            
            # Opción para ver detalles
            print("\n🔍 Ingrese ID para ver detalles (Enter para volver): ")
            seleccion = input("👉 ").strip()
            
            if seleccion.isdigit():
                programa_id = int(seleccion)
                programa_detalle = ProgramaModel.find_by_id(programa_id)
                if programa_detalle:
                    print(f"\n📋 DETALLES DEL PROGRAMA {programa_detalle.codigo}:")
                    print(f"   Nombre: {programa_detalle.nombre}")
                    print(f"   Cupos disponibles: {programa_detalle.cupos_disponibles}")
                    print(f"   Costo: ${programa_detalle.costo_base:.2f}")
                    if programa_detalle.descuento_contado:
                        print(f"   Descuento contado: {programa_detalle.descuento_contado}%")
                    if programa_detalle.promocion_activa:
                        print(f"   ⭐ PROMOCIÓN: {programa_detalle.descuento_promocion}% de descuento")
        else:
            print("📭 No hay programas con cupos disponibles en este momento.")
    
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
    
    pausar()

def ver_estadisticas_programas():
    """Muestra estadísticas de programas"""
    mostrar_encabezado("ESTADÍSTICAS DE PROGRAMAS")
    
    try:
        from models.programa import ProgramaModel
        
        estadisticas = ProgramaModel.obtener_estadisticas()
        
        print("📈 ESTADÍSTICAS GENERALES:")
        print("-" * 40)
        print(f"   • Total programas: {estadisticas['total_programas']}")
        print(f"   • Programas activos (INICIADO): {estadisticas['programas_activos']}")
        print(f"   • Programas planificados: {estadisticas['programas_planificados']}")
        print(f"   • Programas con cupos disponibles: {estadisticas['programas_con_cupos_disponibles']}")
        print(f"   • Programas sin cupos: {estadisticas['programas_sin_cupos']}")
        
        print(f"\n📊 ESTADÍSTICAS DE CUPOS:")
        print("-" * 40)
        print(f"   • Total cupos disponibles: {estadisticas['total_cupos_disponibles']}")
        print(f"   • Total cupos ocupados: {estadisticas['total_cupos_ocupados']}")
        
        if estadisticas['total_programas'] > 0:
            porcentaje_disponible = (estadisticas['total_cupos_disponibles'] / 
                                   (estadisticas['total_cupos_disponibles'] + estadisticas['total_cupos_ocupados']) * 100)
            print(f"   • Porcentaje disponible: {porcentaje_disponible:.1f}%")
        
        # Información adicional
        from database.database import db
        query = """
        SELECT estado, COUNT(*) as cantidad, 
               SUM(cupos_totales) as total_cupos,
               SUM(cupos_disponibles) as disponibles
        FROM programas_academicos 
        GROUP BY estado
        """
        resultados = db.fetch_all(query)
        
        if resultados:
            print(f"\n📋 DISTRIBUCIÓN POR ESTADO:")
            print("-" * 60)
            print(f"{'ESTADO':<15} {'CANTIDAD':<10} {'CUPOS TOTAL':<12} {'DISPONIBLES':<12}")
            print("-" * 60)
            
            for row in resultados:
                print(f"{row['estado']:<15} {row['cantidad']:<10} {row['total_cupos']:<12} {row['disponibles']:<12}")
    
    except Exception as e:
        print(f"❌ Error al obtener estadísticas: {e}")
    
    pausar()

# ============================================
# FUNCIONES DE UTILIDADES
# ============================================

def verificar_sistema():
    """Verifica el estado del sistema"""
    mostrar_encabezado("VERIFICACIÓN DEL SISTEMA")
    
    try:
        from database.database import db
        
        print("🔍 VERIFICANDO COMPONENTES DEL SISTEMA:")
        print("-" * 40)
        
        # 1. Base de datos
        print(f"✅ 1. Base de datos: {db._db_path}")
        if os.path.exists(db._db_path):
            size = os.path.getsize(db._db_path)
            print(f"   📏 Tamaño: {size} bytes ({size/1024:.1f} KB)")
            
            tablas = db.get_all_tables()
            print(f"   📊 Tablas: {len(tablas)}")
            
            # Contar registros en tablas principales
            principales = ['estudiantes', 'docentes', 'programas_academicos', 'matriculas', 'pagos']
            for tabla in principales:
                if tabla in tablas:
                    query = f"SELECT COUNT(*) as count FROM {tabla}"
                    resultado = db.fetch_one(query)
                    print(f"      • {tabla}: {resultado['count'] if resultado else 0} registros")
        else:
            print("   ❌ El archivo no existe")
        
        # 2. Modelos
        print("\n✅ 2. Modelos cargados:")
        try:
            from models.estudiante import EstudianteModel
            from models.docente import DocenteModel
            from models.programa import ProgramaModel
            print("   • EstudianteModel ✓")
            print("   • DocenteModel ✓")
            print("   • ProgramaModel ✓")
        except Exception as e:
            print(f"   ❌ Error en modelos: {e}")
        
        # 3. Funciones del CLI
        print("\n✅ 3. Funciones del CLI:")
        funciones = [
            registrar_estudiante, listar_estudiantes, buscar_estudiante_ci,
            buscar_estudiante_nombre, registrar_docente, listar_docentes,
            crear_programa, listar_programas
        ]
        print(f"   • {len(funciones)} funciones implementadas")
        
        # 4. Resumen
        print("\n📊 RESUMEN DEL SISTEMA:")
        print("-" * 40)
        try:
            estudiantes = EstudianteModel.count()
            docentes = DocenteModel.count()
            programas = ProgramaModel.count()
            
            print(f"   • Estudiantes registrados: {estudiantes}")
            print(f"   • Docentes registrados: {docentes}")
            print(f"   • Programas académicos: {programas}")
            
            if estudiantes > 0 and docentes > 0 and programas > 0:
                print("\n🎉 ¡SISTEMA COMPLETAMENTE OPERATIVO!")
            else:
                print("\n⚠️  Sistema operativo pero con datos limitados")
                
        except:
            print("   ❌ No se pudieron obtener estadísticas")
    
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
    
    pausar()

def inicializar_base_datos():
    """Inicializa la base de datos desde cero - ¡CUIDADO!"""
    mostrar_encabezado("INICIALIZACIÓN DE BASE DE DATOS")
    
    print("⚠️  ⚠️  ⚠️  ¡ADVERTENCIA! ⚠️  ⚠️  ⚠️")
    print("\nEsta operación ELIMINARÁ TODOS LOS DATOS EXISTENTES")
    print("y creará una base de datos nueva desde cero.")
    print("\nSe perderán:")
    print("   • Todos los estudiantes registrados")
    print("   • Todos los docentes registrados")
    print("   • Todos los programas académicos")
    print("   • Todas las matrículas y pagos")
    
    confirmar1 = input("\n¿Está ABSOLUTAMENTE seguro? (escriba 'CONFIRMAR'): ").strip()
    if confirmar1 != "CONFIRMAR":
        print("❌ Operación cancelada")
        pausar()
        return
    
    confirmar2 = input("\n¿REALMENTE está seguro? Esto NO se puede deshacer (s/n): ").lower()
    if confirmar2 != 's':
        print("❌ Operación cancelada")
        pausar()
        return
    
    try:
        print("\n🗑️  Eliminando base de datos existente...")
        
        # Cerrar conexión primero
        from database.database import db
        db.close()
        
        # Eliminar archivo
        import time
        if os.path.exists(db._db_path):
            os.remove(db._db_path)
            time.sleep(1)  # Esperar para asegurar eliminación
        
        print("✅ Base de datos eliminada")
        print("\n📋 Creando nueva base de datos...")
        
        # Usar el script de inicialización
        from scripts.init_database import init_database
        init_database()
        
        print("\n🎉 ¡BASE DE DATOS INICIALIZADA EXITOSAMENTE!")
        print("\n💡 El sistema ahora está listo para usar.")
        print("   Debe reiniciar el CLI para cargar la nueva base de datos.")
        
    except Exception as e:
        print(f"❌ Error en inicialización: {e}")
        import traceback
        traceback.print_exc()
    
    pausar()

def exportar_estudiantes_csv(estudiantes):
    """Exporta la lista de estudiantes a CSV"""
    try:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"export_estudiantes_{timestamp}.csv"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("ID,CI,NOMBRES,APELLIDOS,EMAIL,TELEFONO,PROFESION,UNIVERSIDAD,FECHA_REGISTRO,ACTIVO\n")
            
            for est in estudiantes:
                ci_completo = f"{est.ci_numero}-{est.ci_expedicion}"
                email = est.email if hasattr(est, 'email') and est.email else ""
                telefono = est.telefono if hasattr(est, 'telefono') and est.telefono else ""
                profesion = est.profesion if hasattr(est, 'profesion') and est.profesion else ""
                universidad = est.universidad_egreso if hasattr(est, 'universidad_egreso') and est.universidad_egreso else ""
                fecha = est.fecha_registro[:10] if est.fecha_registro else ""
                activo = "SI" if est.activo else "NO"
                
                f.write(f"{est.id},{ci_completo},{est.nombres},{est.apellidos},{email},{telefono},{profesion},{universidad},{fecha},{activo}\n")
        
        print(f"✅ Datos exportados a: {filename}")
        
    except Exception as e:
        print(f"❌ Error al exportar: {e}")

def ver_detalles_estudiante(estudiante_id):
    """Muestra detalles de un estudiante por ID"""
    try:
        from models.estudiante import EstudianteModel
        estudiante = EstudianteModel.find_by_id(estudiante_id)
        
        if estudiante:
            mostrar_detalles_estudiante(estudiante)
        else:
            print(f"❌ No se encontró estudiante con ID {estudiante_id}")
    except Exception as e:
        print(f"❌ Error: {e}")

# Añadir esta función al cli_completo.py después de las funciones de programas
def registrar_matricula():
    """Registra una nueva matrícula (inscripción completa)"""
    mostrar_encabezado("REGISTRAR NUEVA MATRÍCULA")
    
    try:
        from models.estudiante import EstudianteModel
        from models.programa import ProgramaModel
        from models.matricula import MatriculaModel
        from models.plan_pago import PlanPagoModel
        
        print("🎓 PROCESO COMPLETO DE INSCRIPCIÓN")
        print("=" * 60)
        
        # PASO 1: Seleccionar o crear estudiante
        print("\n1. 📝 DATOS DEL ESTUDIANTE")
        print("-" * 40)
        
        ci_numero = input("CI del estudiante (o Enter para buscar por ID): ").strip()
        estudiante = None
        
        if ci_numero:
            # Buscar por CI
            estudiante = EstudianteModel.buscar_por_ci(ci_numero)
            if not estudiante:
                print(f"❌ No se encontró estudiante con CI {ci_numero}")
                crear_nuevo = input("¿Desea registrar un nuevo estudiante? (s/n): ").lower()
                if crear_nuevo == 's':
                    # Llamar a función de registro de estudiante
                    print("\n📝 Registrando nuevo estudiante...")
                    # (Aquí se podría llamar a registrar_estudiante() o implementar un flujo rápido)
                    print("⚠️  Esta funcionalidad se implementará en la siguiente versión")
                    pausar()
                    return
                else:
                    print("❌ Inscripción cancelada")
                    pausar()
                    return
        else:
            # Buscar por ID
            estudiante_id = input("ID del estudiante: ").strip()
            if estudiante_id.isdigit():
                estudiante = EstudianteModel.find_by_id(int(estudiante_id))
        
        if not estudiante:
            print("❌ Estudiante no encontrado")
            pausar()
            return
        
        print(f"✅ Estudiante: {estudiante.nombre_completo} (CI: {estudiante.ci_numero})")
        
        # PASO 2: Seleccionar programa
        print("\n2. 📚 SELECCIÓN DE PROGRAMA")
        print("-" * 40)
        
        # Listar programas con cupos disponibles
        programas_disponibles = ProgramaModel.buscar_con_cupos_disponibles()
        
        if not programas_disponibles:
            print("❌ No hay programas con cupos disponibles en este momento")
            pausar()
            return
        
        print("📋 Programas disponibles:")
        for i, programa in enumerate(programas_disponibles, 1):
            cupos = f"{programa.cupos_disponibles}/{programa.cupos_totales}"
            print(f"{i:2}. {programa.codigo:<10} {programa.nombre:<30} ${programa.costo_base:<8.2f} Cupos: {cupos}")
        
        seleccion = input("\n👉 Seleccione número de programa: ").strip()
        
        if not seleccion.isdigit() or not (1 <= int(seleccion) <= len(programas_disponibles)):
            print("❌ Selección inválida")
            pausar()
            return
        
        programa = programas_disponibles[int(seleccion) - 1]
        print(f"✅ Programa seleccionado: {programa.nombre_completo}")
        
        # PASO 3: Modalidad de pago
        print("\n3. 💰 MODALIDAD DE PAGO")
        print("-" * 40)
        
        print("Opciones:")
        print("  1. Pago al contado (Descuento: {programa.descuento_contado}%)")
        print("  2. Pago en cuotas")
        
        modalidad_opcion = input("\n👉 Seleccione modalidad (1-2): ").strip()
        
        if modalidad_opcion == '1':
            modalidad_pago = 'CONTADO'
            plan_pago_id = None
            
            # Mostrar cálculo con descuento
            costo_contado = programa.costo_con_descuento_contado
            descuento = programa.costo_base - costo_contado
            
            print(f"\n💵 RESUMEN DE PAGO AL CONTADO:")
            print(f"   • Costo base: ${programa.costo_base:.2f}")
            print(f"   • Descuento ({programa.descuento_contado}%): ${descuento:.2f}")
            print(f"   • Total a pagar: ${costo_contado:.2f}")
            
        elif modalidad_opcion == '2':
            modalidad_pago = 'CUOTAS'
            
            # Obtener planes de pago para este programa
            planes = PlanPagoModel.buscar_por_programa(programa.id)
            
            if not planes:
                print("❌ Este programa no tiene planes de pago configurados")
                pausar()
                return
            
            print("\n📅 PLANES DE PAGO DISPONIBLES:")
            for i, plan in enumerate(planes, 1):
                print(f"{i:2}. {plan.nombre:<20} {plan.nro_cuotas} cuotas cada {plan.intervalo_dias} días")
                if plan.descripcion:
                    print(f"     Descripción: {plan.descripcion}")
            
            plan_seleccion = input("\n👉 Seleccione plan de pago: ").strip()
            
            if not plan_seleccion.isdigit() or not (1 <= int(plan_seleccion) <= len(planes)):
                print("❌ Selección inválida")
                pausar()
                return
            
            plan = planes[int(plan_seleccion) - 1]
            plan_pago_id = plan.id
            
            # Calcular cuotas
            monto_cuota = programa.costo_base / plan.nro_cuotas
            
            print(f"\n💵 RESUMEN DE PAGO EN CUOTAS:")
            print(f"   • Costo total: ${programa.costo_base:.2f}")
            print(f"   • Plan: {plan.nombre}")
            print(f"   • Número de cuotas: {plan.nro_cuotas}")
            print(f"   • Monto por cuota: ${monto_cuota:.2f}")
            print(f"   • Intervalo: cada {plan.intervalo_dias} días")
            
        else:
            print("❌ Opción inválida")
            pausar()
            return
        
        # PASO 4: Confirmar y crear matrícula
        print("\n4. ✅ CONFIRMACIÓN FINAL")
        print("-" * 40)
        
        print("📋 RESUMEN DE LA INSCRIPCIÓN:")
        print(f"   • Estudiante: {estudiante.nombre_completo}")
        print(f"   • Programa: {programa.nombre_completo}")
        print(f"   • Modalidad: {modalidad_pago}")
        if modalidad_pago == 'CUOTAS':
            print(f"   • Plan de pago: {plan.nombre if 'plan' in locals() else 'N/A'}")
        print(f"   • Cupos antes: {programa.cupos_disponibles + 1}/{programa.cupos_totales}")
        print(f"   • Cupos después: {programa.cupos_disponibles}/{programa.cupos_totales}")
        
        confirmar = input("\n¿Confirmar la inscripción? (s/n): ").lower()
        
        if confirmar != 's':
            print("❌ Inscripción cancelada por el usuario")
            pausar()
            return
        
        # Crear la matrícula
        matricula = MatriculaModel.matricular_estudiante(
            estudiante_id=estudiante.id,
            programa_id=programa.id,
            modalidad_pago=modalidad_pago,
            plan_pago_id=plan_pago_id,
            observaciones=f"Inscripción realizada el {datetime.now().strftime('%Y-%m-%d')}"
        )
        
        print(f"\n🎉 ¡INSCRIPCIÓN EXITOSA!")
        print(f"\n📄 DETALLES DE LA MATRÍCULA:")
        print(f"   • Número de matrícula: {matricula.id}")
        print(f"   • Fecha: {matricula.fecha_matricula[:10]}")
        print(f"   • Estado académico: {matricula.estado_academico}")
        print(f"   • Estado de pago: {matricula.estado_pago}")
        print(f"   • Monto total: ${matricula.monto_total:.2f}")
        
        if matricula.descuento_aplicado > 0:
            print(f"   • Descuento aplicado: ${matricula.descuento_aplicado:.2f}")
        
        print(f"   • Monto final: ${matricula.monto_final:.2f}")
        
        # Opción de registrar primer pago
        if modalidad_pago == 'CONTADO':
            registrar_pago = input("\n¿Desea registrar el pago al contado ahora? (s/n): ").lower()
            if registrar_pago == 's':
                print("\n💵 REGISTRO DE PAGO AL CONTADO")
                print("-" * 40)
                
                formas_pago = ['EFECTIVO', 'TRANSFERENCIA', 'TARJETA', 'DEPOSITO', 'CHEQUE', "QR"]
                print("Formas de pago disponibles:")
                for i, forma in enumerate(formas_pago, 1):
                    print(f"  {i}. {forma}")
                
                forma_seleccion = input("\n👉 Seleccione forma de pago (1-6): ").strip()
                
                if forma_seleccion.isdigit() and 1 <= int(forma_seleccion) <= len(formas_pago):
                    forma_pago = formas_pago[int(forma_seleccion) - 1]
                    nro_comprobante = input("Número de comprobante (opcional): ").strip()
                    nro_transaccion = input("Número de transacción (opcional): ").strip()
                    observaciones = input("Observaciones (opcional): ").strip()
                    monto = matricula.monto_final  # Monto total a pagar
                    
                    pago = matricula.registrar_pago(
                        monto=monto,
                        forma_pago=forma_pago,
                        nro_comprobante=nro_comprobante if nro_comprobante else None,
                        nro_transaccion=nro_transaccion if nro_transaccion else None,
                        observaciones=observaciones if observaciones else None,
                        nro_cuota=None  # Para pagos generales sin cuota específica
                    )
                    
                    print(f"✅ Pago registrado exitosamente (ID: {pago.id})")
                    print(f"   Estado actualizado: {matricula.estado_pago}")

        # En registrar_matricula(), reemplaza la parte de planes de pago:
        if modalidad_pago == 'CUOTAS':
            modalidad_pago = 'CUOTAS'

            # Obtener planes de pago ACTIVOS para este programa
            planes = PlanPagoModel.buscar_activos_por_programa(programa.id)

            if not planes:
                print("❌ Este programa no tiene planes de pago activos.")
                print("   Configure planes de pago primero en 'Configurar planes de pago'.")
                pausar()
                return

            print("\n📅 PLANES DE PAGO DISPONIBLES:")
            for i, plan in enumerate(planes, 1):
                monto_cuota = programa.costo_base / plan.nro_cuotas
                print(f"{i:2}. {plan.nombre:<20} {plan.nro_cuotas} cuotas de ${monto_cuota:.2f}")
                if plan.descripcion:
                    print(f"     Descripción: {plan.descripcion}")

            plan_seleccion = input("\n👉 Seleccione plan de pago: ").strip()

            if not plan_seleccion.isdigit() or not (1 <= int(plan_seleccion) <= len(planes)):
                print("❌ Selección inválida")
                pausar()
                return

            plan = planes[int(plan_seleccion) - 1]
            plan_pago_id = plan.id

            # Calcular cuotas
            monto_cuota = programa.costo_base / plan.nro_cuotas

            print(f"\n💵 RESUMEN DE PAGO EN CUOTAS:")
            print(f"   • Costo total: ${programa.costo_base:.2f}")
            print(f"   • Plan: {plan.nombre}")
            print(f"   • Número de cuotas: {plan.nro_cuotas}")
            print(f"   • Monto por cuota: ${monto_cuota:.2f}")
            print(f"   • Intervalo: cada {plan.intervalo_dias} días")        
    #    print("\n📋 Próximos pasos:")
    #    if modalidad_pago == 'CUOTAS':
    #        print("   • Las cuotas han sido generadas automáticamente")
    #        print("   • Puede registrar pagos en la opción 'Registrar pago'")
    #    print("   • El estudiante puede comenzar el programa cuando esté listo")
        
    except ValueError as e:
        print(f"\n❌ Error de validación: {e}")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
    
    pausar()

# Añadir también esta función para ver estado de pagos
def ver_estado_pagos_estudiante():
    """Muestra el estado de pagos de un estudiante"""
    mostrar_encabezado("ESTADO DE PAGOS POR ESTUDIANTE")
    
    try:
        from models.estudiante import EstudianteModel
        from models.matricula import MatriculaModel
        from models.pago import PagoModel
        from models.cuota import CuotaModel
        
        ci_numero = input("CI del estudiante: ").strip()
        if not ci_numero:
            print("❌ Debe ingresar un CI")
            pausar()
            return
        
        estudiante = EstudianteModel.buscar_por_ci(ci_numero)
        if not estudiante:
            print(f"❌ No se encontró estudiante con CI {ci_numero}")
            pausar()
            return
        
        print(f"\n👤 ESTUDIANTE: {estudiante.nombre_completo}")
        print(f"📧 Email: {estudiante.email if hasattr(estudiante, 'email') else 'N/A'}")
        print(f"📞 Teléfono: {estudiante.telefono if hasattr(estudiante, 'telefono') else 'N/A'}")
        print("-" * 80)
        
        # Obtener matrículas del estudiante
        matriculas = MatriculaModel.buscar_por_estudiante(estudiante.id)
        
        if not matriculas:
            print("📭 El estudiante no tiene matrículas registradas")
            pausar()
            return
        
        for matricula in matriculas:
            detalles = matricula.obtener_detalles_completos()
            
            print(f"\n📚 PROGRAMA: {detalles['programa']['nombre']} ({detalles['programa']['codigo']})")
            print(f"   • Estado académico: {matricula.estado_academico}")
            print(f"   • Estado de pago: {matricula.estado_pago}")
            print(f"   • Monto total: ${matricula.monto_total:.2f}")
            print(f"   • Pagado: ${matricula.monto_pagado:.2f} ({matricula.porcentaje_pagado:.1f}%)")
            print(f"   • Saldo pendiente: ${matricula.saldo_pendiente:.2f}")
            
            # Mostrar cuotas si existen
            if detalles['cuotas']:
                print(f"\n   📅 CUOTAS PROGRAMADAS:")
                print("   N°  Vencimiento   Monto      Estado")
                print("   --- ------------  ---------- ----------")
                
                for cuota in detalles['cuotas']:
                    estado = cuota['estado']
                    icono = "✅" if estado == 'PAGADA' else "⏳" if estado == 'PENDIENTE' else "⚠️ "
                    print(f"   {cuota['nro_cuota']:2}  {cuota['fecha_vencimiento']}  ${cuota['monto']:8.2f}  {icono} {estado}")
            
            # Mostrar pagos realizados
            pagos = PagoModel.buscar_por_matricula(matricula.id)
            if pagos:
                print(f"\n   💵 PAGOS REALIZADOS:")
                for pago in pagos:
                    print(f"      • ${pago.monto:.2f} el {pago.fecha_pago} ({pago.forma_pago})")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    pausar()

def gestionar_planes_pago():
    """Función principal para gestionar planes de pago"""
    mostrar_encabezado("GESTIÓN DE PLANES DE PAGO")
    
    try:
        from models.programa import ProgramaModel
        from models.plan_pago import PlanPagoModel
        
        print("🔧 CONFIGURACIÓN DE PLANES DE PAGO")
        print("=" * 60)
        
        # 1. Seleccionar un programa
        print("\n1. 📚 SELECCIONAR PROGRAMA")
        print("-" * 40)
        
        programas = ProgramaModel.all()
        
        if not programas:
            print("❌ No hay programas registrados. Crea un programa primero.")
            pausar()
            return
        
        print("Programas disponibles:")
        for i, programa in enumerate(programas, 1):
            print(f"{i:2}. {programa.codigo} - {programa.nombre}")
        
        seleccion = input("\n👉 Seleccione un programa (número): ").strip()
        
        if not seleccion.isdigit() or not (1 <= int(seleccion) <= len(programas)):
            print("❌ Selección inválida")
            pausar()
            return
        
        programa = programas[int(seleccion) - 1]
        
        # 2. Mostrar menú de opciones para planes de pago de este programa
        gestionar_planes_programa(programa)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        pausar()

def gestionar_planes_programa(programa):
    """Gestiona los planes de pago para un programa específico"""
    while True:
        mostrar_encabezado(f"PLANES DE PAGO - {programa.nombre}")
        
        try:
            from models.plan_pago import PlanPagoModel
            
            print(f"📋 PROGRAMA: {programa.nombre_completo}")
            print(f"💰 Costo base: ${programa.costo_base:.2f}")
            print(f"📊 Cupos: {programa.cupos_disponibles}/{programa.cupos_totales}")
            print("-" * 60)
            
            # Obtener planes de pago para este programa
            planes = PlanPagoModel.buscar_por_programa(programa.id)
            
            if planes:
                print(f"📅 PLANES DE PAGO CONFIGURADOS ({len(planes)}):")
                print("-" * 80)
                print(f"{'ID':<5} {'NOMBRE':<20} {'CUOTAS':<8} {'INTERVALO':<12} {'ESTADO':<10} {'DESCRIPCIÓN'}")
                print("-" * 80)
                
                for plan in planes:
                    estado = "✅ Activo" if plan.activo else "❌ Inactivo"
                    descripcion = plan.descripcion[:30] + "..." if plan.descripcion and len(plan.descripcion) > 30 else plan.descripcion or "Sin descripción"
                    print(f"{plan.id:<5} {plan.nombre:<20} {plan.nro_cuotas:<8} {plan.intervalo_dias:<12} días {estado:<10} {descripcion}")
                
                print("-" * 80)
                
                # Calcular ejemplo de cuotas
                print("\n💵 EJEMPLO DE PAGOS (basado en primer plan activo):")
                planes_activos = [p for p in planes if p.activo]
                if planes_activos:
                    plan_ejemplo = planes_activos[0]
                    monto_cuota = programa.costo_base / plan_ejemplo.nro_cuotas
                    print(f"   • Plan: {plan_ejemplo.nombre}")
                    print(f"   • Cuotas: {plan_ejemplo.nro_cuotas} de ${monto_cuota:.2f}")
                    print(f"   • Intervalo: cada {plan_ejemplo.intervalo_dias} días")
                    print(f"   • Total: ${programa.costo_base:.2f}")
            else:
                print("📭 No hay planes de pago configurados para este programa.")
            
            # Menú de opciones
            print("\n🔧 OPCIONES:")
            print("  1. Crear nuevo plan de pago")
            print("  2. Editar plan existente")
            print("  3. Activar/Desactivar plan")
            print("  4. Eliminar plan")
            print("  5. Ver simulador de pagos")
            print("  6. Volver al menú anterior")
            
            opcion = input("\n👉 Seleccione una opción: ").strip()
            
            if opcion == '1':
                crear_plan_pago(programa)
            elif opcion == '2' and planes:
                editar_plan_pago(programa, planes)
            elif opcion == '3' and planes:
                activar_desactivar_plan(planes)
            elif opcion == '4' and planes:
                eliminar_plan_pago(planes)
            elif opcion == '5':
                simular_plan_pagos(programa, planes)
            elif opcion == '6':
                break
            else:
                if not planes and opcion in ['2', '3', '4']:
                    print("❌ No hay planes para editar. Crea uno primero.")
                else:
                    print("❌ Opción inválida")
                pausar()
        
        except Exception as e:
            print(f"❌ Error: {e}")
            pausar()

def crear_plan_pago(programa):
    """Crea un nuevo plan de pago para un programa"""
    print(f"\n📝 CREAR NUEVO PLAN DE PAGO")
    print(f"   Programa: {programa.nombre}")
    print("-" * 40)
    
    try:
        from models.plan_pago import PlanPagoModel
        
        print("Complete los datos del plan de pago:")
        print("-" * 40)
        
        # Nombre del plan
        nombre = input("Nombre del plan (ej: 'Plan 3 cuotas', 'Plan mensual'): ").strip()
        if not nombre:
            print("❌ El nombre es obligatorio")
            pausar()
            return
        
        # Número de cuotas
        nro_cuotas = input("Número de cuotas: ").strip()
        if not nro_cuotas.isdigit() or int(nro_cuotas) <= 0:
            print("❌ El número de cuotas debe ser un número positivo")
            pausar()
            return
        nro_cuotas = int(nro_cuotas)
        
        # Intervalo entre cuotas
        intervalo_dias = input("Intervalo entre cuotas (días): ").strip()
        if not intervalo_dias.isdigit() or int(intervalo_dias) <= 0:
            print("❌ El intervalo debe ser un número positivo de días")
            pausar()
            return
        intervalo_dias = int(intervalo_dias)
        
        # Descripción
        descripcion = input("Descripción (opcional): ").strip()
        
        # Calcular monto por cuota
        monto_cuota = programa.costo_base / nro_cuotas
        
        # Mostrar resumen
        print(f"\n📋 RESUMEN DEL PLAN:")
        print(f"   • Programa: {programa.nombre}")
        print(f"   • Nombre del plan: {nombre}")
        print(f"   • Cuotas: {nro_cuotas}")
        print(f"   • Intervalo: cada {intervalo_dias} días")
        print(f"   • Monto por cuota: ${monto_cuota:.2f}")
        print(f"   • Total a pagar: ${programa.costo_base:.2f}")
        if descripcion:
            print(f"   • Descripción: {descripcion}")
        
        confirmar = input("\n👉 ¿Crear este plan de pago? (s/n): ").lower()
        
        if confirmar != 's':
            print("❌ Creación cancelada")
            pausar()
            return
        
        # Crear el plan
        plan = PlanPagoModel.crear_plan_pago(
            programa_id=programa.id,
            nombre=nombre,
            nro_cuotas=nro_cuotas,
            intervalo_dias=intervalo_dias,
            descripcion=descripcion if descripcion else None
        )
        
        print(f"\n✅ ¡PLAN DE PAGO CREADO EXITOSAMENTE!")
        print(f"   • ID del plan: {plan.id}")
        print(f"   • Nombre: {plan.nombre}")
        print(f"   • Estado: {'✅ Activo' if plan.activo else '❌ Inactivo'}")
        
        # Preguntar si activar
        activar = input("\n¿Activar este plan ahora? (s/n): ").lower()
        if activar == 's':
            plan.activar()
            print("✅ Plan activado")
        else:
            plan.desactivar()
            print("ℹ️  Plan creado pero inactivo. Actívelo cuando esté listo para usar.")
        
    except ValueError as e:
        print(f"\n❌ Error de validación: {e}")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    
    pausar()

def editar_plan_pago(programa, planes):
    """Edita un plan de pago existente"""
    print(f"\n✏️ EDITAR PLAN DE PAGO")
    print(f"   Programa: {programa.nombre}")
    print("-" * 40)
    
    # Seleccionar plan
    print("Planes disponibles:")
    for i, plan in enumerate(planes, 1):
        estado = "✅" if plan.activo else "❌"
        print(f"{i:2}. [{estado}] {plan.nombre}: {plan.nro_cuotas} cuotas cada {plan.intervalo_dias} días")
    
    seleccion = input("\n👉 Seleccione el plan a editar (número): ").strip()
    
    if not seleccion.isdigit() or not (1 <= int(seleccion) <= len(planes)):
        print("❌ Selección inválida")
        pausar()
        return
    
    plan = planes[int(seleccion) - 1]
    
    print(f"\n✏️ Editando: {plan.nombre}")
    print("Nota: Deje en blanco para mantener el valor actual.")
    print("-" * 40)
    
    # Nombre
    nombre_actual = plan.nombre
    nuevo_nombre = input(f"Nombre del plan [{nombre_actual}]: ").strip()
    if nuevo_nombre:
        plan.nombre = nuevo_nombre
    
    # Número de cuotas
    nro_cuotas_actual = plan.nro_cuotas
    nuevo_nro_cuotas = input(f"Número de cuotas [{nro_cuotas_actual}]: ").strip()
    if nuevo_nro_cuotas:
        if nuevo_nro_cuotas.isdigit() and int(nuevo_nro_cuotas) > 0:
            plan.nro_cuotas = int(nuevo_nro_cuotas)
        else:
            print("❌ Número de cuotas no válido. Se mantiene el actual.")
    
    # Intervalo
    intervalo_actual = plan.intervalo_dias
    nuevo_intervalo = input(f"Intervalo entre cuotas (días) [{intervalo_actual}]: ").strip()
    if nuevo_intervalo:
        if nuevo_intervalo.isdigit() and int(nuevo_intervalo) > 0:
            plan.intervalo_dias = int(nuevo_intervalo)
        else:
            print("❌ Intervalo no válido. Se mantiene el actual.")
    
    # Descripción
    descripcion_actual = plan.descripcion if plan.descripcion else ""
    nueva_descripcion = input(f"Descripción [{descripcion_actual}]: ").strip()
    if nueva_descripcion:
        plan.descripcion = nueva_descripcion
    
    # Calcular nuevo monto por cuota
    monto_cuota = programa.costo_base / plan.nro_cuotas
    
    # Mostrar resumen de cambios
    print(f"\n📋 RESUMEN DE CAMBIOS:")
    print(f"   • Nombre: {plan.nombre}")
    print(f"   • Cuotas: {plan.nro_cuotas}")
    print(f"   • Intervalo: cada {plan.intervalo_dias} días")
    print(f"   • Monto por cuota: ${monto_cuota:.2f}")
    if plan.descripcion:
        print(f"   • Descripción: {plan.descripcion}")
    
    confirmar = input("\n👉 ¿Confirmar cambios? (s/n): ").lower()
    
    if confirmar == 's':
        try:
            plan.save()
            print("✅ Plan de pago actualizado exitosamente")
        except Exception as e:
            print(f"❌ Error al actualizar: {e}")
    else:
        print("❌ Cambios cancelados")
    
    pausar()

def activar_desactivar_plan(planes):
    """Activa o desactiva un plan de pago"""
    print(f"\n⚙️ ACTIVAR/DESACTIVAR PLAN DE PAGO")
    print("-" * 40)
    
    # Seleccionar plan
    print("Planes disponibles:")
    for i, plan in enumerate(planes, 1):
        estado = "✅ Activo" if plan.activo else "❌ Inactivo"
        print(f"{i:2}. {plan.nombre} - {estado}")
    
    seleccion = input("\n👉 Seleccione el plan (número): ").strip()
    
    if not seleccion.isdigit() or not (1 <= int(seleccion) <= len(planes)):
        print("❌ Selección inválida")
        pausar()
        return
    
    plan = planes[int(seleccion) - 1]
    
    if plan.activo:
        print(f"\n⚠️  Desactivar plan: {plan.nombre}")
        print(f"   Al desactivar, no estará disponible para nuevas matrículas.")
        print(f"   Las matrículas existentes con este plan no se verán afectadas.")
        
        confirmar = input("\n👉 ¿Desactivar este plan? (s/n): ").lower()
        if confirmar == 's':
            plan.desactivar()
            print("✅ Plan desactivado")
        else:
            print("❌ Operación cancelada")
    else:
        print(f"\n✅ Activar plan: {plan.nombre}")
        print(f"   Al activar, estará disponible para nuevas matrículas.")
        
        confirmar = input("\n👉 ¿Activar este plan? (s/n): ").lower()
        if confirmar == 's':
            plan.activar()
            print("✅ Plan activado")
        else:
            print("❌ Operación cancelada")
    
    pausar()

def eliminar_plan_pago(planes):
    """Elimina un plan de pago"""
    print(f"\n🗑️ ELIMINAR PLAN DE PAGO")
    print("-" * 40)
    
    # Seleccionar plan
    print("Planes disponibles:")
    for i, plan in enumerate(planes, 1):
        estado = "✅ Activo" if plan.activo else "❌ Inactivo"
        print(f"{i:2}. {plan.nombre} - {estado}")
    
    seleccion = input("\n👉 Seleccione el plan a eliminar (número): ").strip()
    
    if not seleccion.isdigit() or not (1 <= int(seleccion) <= len(planes)):
        print("❌ Selección inválida")
        pausar()
        return
    
    plan = planes[int(seleccion) - 1]
    
    # Verificar si hay matrículas usando este plan
    from database.database import db
    query = "SELECT COUNT(*) as count FROM matriculas WHERE plan_pago_id = ?"
    resultado = db.fetch_one(query, (plan.id,))
    
    if resultado and resultado['count'] > 0:
        print(f"\n❌ No se puede eliminar este plan.")
        print(f"   Hay {resultado['count']} matrícula(s) usando este plan.")
        print(f"   En su lugar, puede desactivarlo para que no esté disponible para nuevas matrículas.")
        pausar()
        return
    
    print(f"\n⚠️  ADVERTENCIA: Eliminación permanente")
    print(f"   Plan a eliminar: {plan.nombre}")
    print(f"   Programa: Se perderá esta configuración de pagos.")
    print(f"   Esta acción NO se puede deshacer.")
    
    confirmar = input("\n👉 ¿Está SEGURO de eliminar este plan? (escriba 'ELIMINAR' para confirmar): ").strip()
    
    if confirmar == "ELIMINAR":
        try:
            plan.delete()
            print("✅ Plan eliminado exitosamente")
        except Exception as e:
            print(f"❌ Error al eliminar: {e}")
    else:
        print("❌ Eliminación cancelada")
    
    pausar()

def simular_plan_pagos(programa, planes):
    """Simula los pagos de un plan para mostrar al estudiante"""
    print(f"\n🧮 SIMULADOR DE PLANES DE PAGO")
    print(f"   Programa: {programa.nombre}")
    print(f"💰 Costo total: ${programa.costo_base:.2f}")
    print("-" * 60)
    
    if not planes:
        print("ℹ️  Este programa no tiene planes de pago configurados.")
        pausar()
        return
    
    # Mostrar opción de pago al contado primero
    if programa.descuento_contado and programa.descuento_contado > 0:
        costo_contado = programa.costo_con_descuento_contado
        ahorro = programa.costo_base - costo_contado
        
        print(f"\n💵 PAGO AL CONTADO:")
        print(f"   • Descuento: {programa.descuento_contado}%")
        print(f"   • Ahorro: ${ahorro:.2f}")
        print(f"   • Total a pagar: ${costo_contado:.2f}")
        print(f"   • Ventaja: Pago único, sin cuotas, sin intereses")
    
    # Mostrar planes activos
    planes_activos = [p for p in planes if p.activo]
    
    if planes_activos:
        print(f"\n📅 PLANES DE PAGO DISPONIBLES ({len(planes_activos)}):")
        
        for i, plan in enumerate(planes_activos, 1):
            monto_cuota = programa.costo_base / plan.nro_cuotas
            
            print(f"\n{i}. {plan.nombre}:")
            print(f"   • Cuotas: {plan.nro_cuotas} de ${monto_cuota:.2f}")
            print(f"   • Intervalo: cada {plan.intervalo_dias} días")
            print(f"   • Total: ${programa.costo_base:.2f}")
            if plan.descripcion:
                print(f"   • Descripción: {plan.descripcion}")
            
            # Simulación de fechas
            from datetime import date, timedelta
            hoy = date.today()
            
            print(f"   📅 SIMULACIÓN DE FECHAS:")
            for j in range(1, min(plan.nro_cuotas + 1, 7)):  # Mostrar máximo 6 cuotas
                fecha_cuota = hoy + timedelta(days=(j * plan.intervalo_dias))
                print(f"      Cuota {j}: {fecha_cuota.strftime('%d/%m/%Y')} - ${monto_cuota:.2f}")
            
            if plan.nro_cuotas > 6:
                print(f"      ... y {plan.nro_cuotas - 6} cuotas más")
    else:
        print("\nℹ️  No hay planes de pago activos para este programa.")
    
    # Comparativa
    if len(planes_activos) > 1:
        print(f"\n📊 COMPARATIVA ENTRE PLANES:")
        print(f"{'PLAN':<20} {'CUOTAS':<10} {'VALOR CUOTA':<15} {'TOTAL':<10}")
        print("-" * 55)
        
        for plan in planes_activos:
            monto_cuota = programa.costo_base / plan.nro_cuotas
            print(f"{plan.nombre:<20} {plan.nro_cuotas:<10} ${monto_cuota:<14.2f} ${programa.costo_base:<9.2f}")
    
    pausar()

def registrar_pago_cuota():
    """Registra el pago de una cuota o pago parcial"""
    mostrar_encabezado("REGISTRAR PAGO DE CUOTA")
    
    try:
        from models.estudiante import EstudianteModel
        from models.matricula import MatriculaModel
        from models.cuota import CuotaModel
        from models.pago import PagoModel
        from datetime import date, datetime
        
        print("💰 REGISTRO DE PAGOS DE CUOTAS")
        print("=" * 60)
        
        # Opción 1: Buscar por CI de estudiante
        # Opción 2: Buscar por ID de matrícula
        print("\n🔍 BUSCAR ESTUDIANTE CON CUOTAS PENDIENTES:")
        print("  1. Por CI de estudiante")
        print("  2. Por ID de matrícula")
        print("  3. Ver todos los vencimientos próximos")
        
        opcion_busqueda = input("\n👉 Seleccione opción de búsqueda (1-3): ").strip()
        
        matricula = None
        estudiante = None
        
        if opcion_busqueda == '1':
            # Buscar por CI
            ci_numero = input("CI del estudiante: ").strip()
            if not ci_numero:
                print("❌ Debe ingresar un CI")
                pausar()
                return
            
            estudiante = EstudianteModel.buscar_por_ci(ci_numero)
            if not estudiante:
                print(f"❌ No se encontró estudiante con CI {ci_numero}")
                pausar()
                return
            
            print(f"\n✅ Estudiante encontrado: {estudiante.nombre_completo}")
            
            # Buscar matrículas del estudiante con pagos pendientes
            matriculas = MatriculaModel.buscar_por_estudiante(estudiante.id)
            matriculas_pendientes = [m for m in matriculas if m.estado_pago in ['PENDIENTE', 'PARCIAL']]
            
            if not matriculas_pendientes:
                print("ℹ️  El estudiante no tiene matrículas con pagos pendientes")
                pausar()
                return
            
            # Mostrar matrículas para seleccionar
            print(f"\n📋 MATRÍCULAS CON PAGOS PENDIENTES ({len(matriculas_pendientes)}):")
            for i, mat in enumerate(matriculas_pendientes, 1):
                detalles = mat.obtener_detalles_completos()
                programa_nombre = detalles['programa']['nombre'] if detalles['programa'] else 'N/A'
                saldo = mat.saldo_pendiente
                print(f"{i:2}. Matrícula {mat.id}: {programa_nombre[:30]} | Saldo: ${saldo:.2f}")
            
            seleccion = input("\n👉 Seleccione matrícula (número): ").strip()
            if not seleccion.isdigit() or not (1 <= int(seleccion) <= len(matriculas_pendientes)):
                print("❌ Selección inválida")
                pausar()
                return
            
            matricula = matriculas_pendientes[int(seleccion) - 1]
            
        elif opcion_busqueda == '2':
            # Buscar por ID de matrícula
            matricula_id = input("ID de matrícula: ").strip()
            if not matricula_id.isdigit():
                print("❌ ID de matrícula debe ser un número")
                pausar()
                return
            
            matricula = MatriculaModel.find_by_id(int(matricula_id))
            if not matricula:
                print(f"❌ No se encontró matrícula con ID {matricula_id}")
                pausar()
                return
            
            # Obtener estudiante
            estudiante = EstudianteModel.find_by_id(matricula.estudiante_id)
            
        elif opcion_busqueda == '3':
            # Mostrar todos los vencimientos próximos (próximos 30 días)
            mostrar_vencimientos_proximos()
            pausar()
            return
            
        else:
            print("❌ Opción inválida")
            pausar()
            return
        
        if not matricula:
            print("❌ No se pudo encontrar la matrícula")
            pausar()
            return
        
        # Obtener detalles de la matrícula
        detalles = matricula.obtener_detalles_completos()
        programa_nombre = detalles['programa']['nombre'] if detalles['programa'] else 'N/A'
        
        print(f"\n📋 INFORMACIÓN DE LA MATRÍCULA:")
        print("-" * 50)
        print(f"   • Matrícula ID: {matricula.id}")
        print(f"   • Estudiante: {estudiante.nombre_completo}")
        print(f"   • Programa: {programa_nombre}")
        print(f"   • Modalidad: {matricula.modalidad_pago}")
        print(f"   • Estado pago: {matricula.estado_pago}")
        print(f"   • Total a pagar: ${matricula.monto_final:.2f}")
        print(f"   • Pagado: ${matricula.monto_pagado:.2f}")
        print(f"   • Saldo pendiente: ${matricula.saldo_pendiente:.2f}")
        print(f"   • Porcentaje pagado: {matricula.porcentaje_pagado:.1f}%")
        print("-" * 50)
        
        # Obtener cuotas pendientes
        cuotas_pendientes = CuotaModel.buscar_por_matricula_y_estado(matricula.id, 'PENDIENTE')
        cuotas_vencidas = CuotaModel.buscar_por_matricula_y_estado(matricula.id, 'VENCIDA')
        
        todas_cuotas = CuotaModel.buscar_por_matricula(matricula.id)
        
        if not todas_cuotas:
            # No hay cuotas programadas (pago al contado o cuotas no generadas)
            print("\nℹ️  Esta matrícula no tiene cuotas programadas.")
            print("   ¿Desea registrar un pago al saldo general?")
            
            confirmar = input("\n👉 Registrar pago al saldo general? (s/n): ").lower()
            if confirmar == 's':
                registrar_pago_general(matricula, estudiante)
            pausar()
            return
        
        # Calcular días de mora e intereses para cuotas vencidas
        for cuota in cuotas_vencidas:
            cuota.calcular_mora()
        
        # Mostrar resumen de cuotas
        print(f"\n📅 ESTADO DE CUOTAS:")
        print(f"   • Total cuotas: {len(todas_cuotas)}")
        print(f"   • Pagadas: {len([c for c in todas_cuotas if c.estado == 'PAGADA'])}")
        print(f"   • Pendientes: {len(cuotas_pendientes)}")
        print(f"   • Vencidas: {len(cuotas_vencidas)}")
        
        # Mostrar detalle de cuotas pendientes y vencidas
        cuotas_a_mostrar = [c for c in todas_cuotas if c.estado in ['PENDIENTE', 'VENCIDA']]
        
        if cuotas_a_mostrar:
            print(f"\n📋 DETALLE DE CUOTAS PENDIENTES/VENCIDAS:")
            print("-" * 80)
            print(f"{'#':<3} {'Vencimiento':<12} {'Monto':<10} {'Estado':<10} {'Días Mora':<10} {'Interés':<10} {'Total':<10}")
            print("-" * 80)
            
            for cuota in sorted(cuotas_a_mostrar, key=lambda x: x.nro_cuota):
                hoy = date.today()
                vencimiento = date.fromisoformat(cuota.fecha_vencimiento)
                dias_mora = max(0, (hoy - vencimiento).days) if cuota.estado == 'VENCIDA' else 0
                
                estado_display = cuota.estado
                if cuota.estado == 'VENCIDA':
                    estado_display = "⚠️ VENCIDA"
                elif cuota.estado == 'PENDIENTE' and hoy > vencimiento:
                    estado_display = "⏳ POR VENCER"
                
                total_cuota = cuota.monto + (cuota.interes_mora if hasattr(cuota, 'interes_mora') else 0)
                
                print(f"{cuota.nro_cuota:<3} {cuota.fecha_vencimiento:<12} ${cuota.monto:<9.2f} "
                      f"{estado_display:<10} {dias_mora:<10} ${cuota.interes_mora:<9.2f} ${total_cuota:<9.2f}")
            
            print("-" * 80)
            
            # Calcular total a pagar incluyendo intereses
            total_pendiente = sum(c.monto for c in cuotas_a_mostrar)
            total_intereses = sum(c.interes_mora for c in cuotas_a_mostrar if hasattr(c, 'interes_mora'))
            total_a_pagar = total_pendiente + total_intereses
            
            print(f"\n💰 TOTAL A PAGAR: ${total_a_pagar:.2f} "
                  f"(Cuotas: ${total_pendiente:.2f} + Intereses: ${total_intereses:.2f})")
        
        # Opciones de pago
        print(f"\n💳 OPCIONES DE PAGO:")
        print("  1. Pagar cuota específica")
        print("  2. Pagar todas las cuotas pendientes")
        print("  3. Pagar monto personalizado")
        print("  4. Pagar solo los intereses de mora")
        
        opcion_pago = input("\n👉 Seleccione opción de pago (1-4): ").strip()
        
        if opcion_pago == '1':
            # Pagar cuota específica
            if not cuotas_a_mostrar:
                print("❌ No hay cuotas pendientes para pagar")
                pausar()
                return
            
            nro_cuota = input("Número de cuota a pagar: ").strip()
            if not nro_cuota.isdigit():
                print("❌ Debe ingresar un número válido")
                pausar()
                return
            
            nro_cuota = int(nro_cuota)
            cuota_a_pagar = None
            
            for cuota in cuotas_a_mostrar:
                if cuota.nro_cuota == nro_cuota:
                    cuota_a_pagar = cuota
                    break
            
            if not cuota_a_pagar:
                print(f"❌ No se encontró la cuota {nro_cuota} entre las pendientes")
                pausar()
                return
            
            pagar_cuota_especifica(matricula, estudiante, cuota_a_pagar)
            
        elif opcion_pago == '2':
            # Pagar todas las cuotas pendientes
            if not cuotas_a_mostrar:
                print("❌ No hay cuotas pendientes para pagar")
                pausar()
                return
            
            pagar_todas_cuotas(matricula, estudiante, cuotas_a_mostrar)
            
        elif opcion_pago == '3':
            # Pagar monto personalizado
            pagar_monto_personalizado(matricula, estudiante, cuotas_a_mostrar)
            
        elif opcion_pago == '4':
            # Pagar solo intereses de mora
            pagar_solo_intereses(matricula, estudiante, cuotas_a_mostrar)
            
        else:
            print("❌ Opción inválida")
            pausar()
            return
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        pausar()

def mostrar_vencimientos_proximos():
    """Muestra cuotas con vencimiento próximo (próximos 30 días)"""
    try:
        from database.database import db
        from datetime import date, timedelta
        
        hoy = date.today()
        fecha_limite = hoy + timedelta(days=30)
        
        print("\n📅 CUOTAS CON VENCIMIENTO PRÓXIMO (30 días):")
        print("=" * 100)
        
        query = """
        SELECT 
            c.id as cuota_id,
            c.nro_cuota,
            c.fecha_vencimiento,
            c.monto,
            c.interes_mora,
            c.estado,
            m.id as matricula_id,
            e.nombres || ' ' || e.apellidos as estudiante,
            e.ci_numero,
            p.nombre as programa,
            p.codigo
        FROM cuotas_programadas c
        JOIN matriculas m ON c.matricula_id = m.id
        JOIN estudiantes e ON m.estudiante_id = e.id
        JOIN programas_academicos p ON m.programa_id = p.id
        WHERE c.estado IN ('PENDIENTE', 'VENCIDA')
          AND c.fecha_vencimiento BETWEEN ? AND ?
        ORDER BY c.fecha_vencimiento
        """
        
        resultados = db.fetch_all(query, (hoy.isoformat(), fecha_limite.isoformat()))
        
        if not resultados:
            print("✅ No hay cuotas con vencimiento en los próximos 30 días")
            return
        
        print(f"{'Estudiante':<25} {'CI':<12} {'Programa':<20} {'Cuota':<6} {'Vence':<12} {'Monto':<10} {'Estado':<10}")
        print("-" * 100)
        
        for row in resultados:
            estudiante_nombre = row['estudiante'][:25] if len(row['estudiante']) > 25 else row['estudiante']
            programa_nombre = row['programa'][:20] if len(row['programa']) > 20 else row['programa']
            
            estado = row['estado']
            if estado == 'VENCIDA':
                estado = "⚠️ VENCIDA"
            
            print(f"{estudiante_nombre:<25} {row['ci_numero']:<12} {programa_nombre:<20} "
                  f"{row['nro_cuota']:<6} {row['fecha_vencimiento']:<12} "
                  f"${row['monto']:<9.2f} {estado:<10}")
        
        print("-" * 100)
        
        # Total pendiente
        total = sum(row['monto'] + row['interes_mora'] for row in resultados)
        print(f"\n💰 TOTAL PENDIENTE (próximos 30 días): ${total:.2f}")
        
    except Exception as e:
        print(f"❌ Error al mostrar vencimientos: {e}")

def pagar_cuota_especifica(matricula, estudiante, cuota):
    """Paga una cuota específica"""
    try:
        monto_total = cuota.monto + getattr(cuota, 'interes_mora', 0)
        
        print(f"\n💰 PAGO DE CUOTA {cuota.nro_cuota}")
        print(f"   • Monto cuota: ${cuota.monto:.2f}")
        if getattr(cuota, 'interes_mora', 0) > 0:
            print(f"   • Interés mora: ${cuota.interes_mora:.2f}")
        print(f"   • Total a pagar: ${monto_total:.2f}")
        
        forma_pago, nro_comprobante, nro_transaccion, observaciones = obtener_detalles_pago()
        
        if not forma_pago:
            print("❌ Pago cancelado")
            return
        
        confirmar = input("\n👉 ¿Confirmar el pago? (s/n): ").lower()
        if confirmar != 's':
            print("❌ Pago cancelado")
            return
        
        # Registrar pago
        pago = matricula.registrar_pago(
            monto=monto_total,
            forma_pago=forma_pago,
            nro_comprobante=nro_comprobante,
            nro_transaccion=nro_transaccion,
            observaciones=observaciones,
            nro_cuota=cuota.nro_cuota  # Especificar número de cuota
        )
        
        print(f"\n✅ ¡CUOTA {cuota.nro_cuota} PAGADA EXITOSAMENTE!")
        
        # Generar comprobante
        generar_comprobante_pago(pago, estudiante, matricula)
        
    except Exception as e:
        print(f"❌ Error al pagar cuota: {e}")

def pagar_todas_cuotas(matricula, estudiante, cuotas_pendientes):
    """Paga todas las cuotas pendientes"""
    total_pendiente = sum(c.monto for c in cuotas_pendientes)
    total_intereses = sum(getattr(c, 'interes_mora', 0) for c in cuotas_pendientes)
    total_a_pagar = total_pendiente + total_intereses
    
    print(f"\n💰 PAGO DE TODAS LAS CUOTAS PENDIENTES")
    print(f"   • Cuotas pendientes: {len(cuotas_pendientes)}")
    print(f"   • Total cuotas: ${total_pendiente:.2f}")
    if total_intereses > 0:
        print(f"   • Intereses mora: ${total_intereses:.2f}")
    print(f"   • Total a pagar: ${total_a_pagar:.2f}")
    
    forma_pago, nro_comprobante, nro_transaccion, observaciones = obtener_detalles_pago()
    
    if not forma_pago:
        print("❌ Pago cancelado")
        return
    
    confirmar = input("\n👉 ¿Confirmar el pago? (s/n): ").lower()
    if confirmar != 's':
        print("❌ Pago cancelado")
        return
    
    # Registrar pago (sin cuota específica ya que son múltiples)
    pago = matricula.registrar_pago(
        monto=total_a_pagar,
        forma_pago=forma_pago,
        nro_comprobante=nro_comprobante,
        nro_transaccion=nro_transaccion,
        observaciones=observaciones,
        nro_cuota=None  # Múltiples cuotas
    )
    
    print(f"\n✅ ¡TODAS LAS CUOTAS PAGADAS EXITOSAMENTE!")
    
    # Generar comprobante
    generar_comprobante_pago(pago, estudiante, matricula)

def pagar_monto_personalizado(matricula, estudiante, cuotas_pendientes):
    """Paga un monto personalizado"""
    total_pendiente = sum(c.monto for c in cuotas_pendientes)
    total_intereses = sum(getattr(c, 'interes_mora', 0) for c in cuotas_pendientes)
    max_a_pagar = total_pendiente + total_intereses
    
    print(f"\n💰 PAGO PERSONALIZADO")
    print(f"   • Máximo posible: ${max_a_pagar:.2f}")
    
    monto = None
    while monto is None:
        monto_str = input(f"\n👉 Ingrese monto a pagar (máximo ${max_a_pagar:.2f}): $").strip()
        
        try:
            monto = float(monto_str)
            
            if monto <= 0:
                print("❌ El monto debe ser mayor a 0")
                monto = None
                continue
            
            if monto > max_a_pagar:
                print(f"❌ El monto excede el máximo posible (${max_a_pagar:.2f})")
                monto = None
                continue
                
        except ValueError:
            print("❌ Monto inválido. Debe ser un número.")
            monto = None
    
    forma_pago, nro_comprobante, nro_transaccion, observaciones = obtener_detalles_pago()
    
    if not forma_pago:
        print("❌ Pago cancelado")
        return
    
    confirmar = input("\n👉 ¿Confirmar el pago? (s/n): ").lower()
    if confirmar != 's':
        print("❌ Pago cancelado")
        return
    
    # Registrar pago (sin cuota específica)
    pago = matricula.registrar_pago(
        monto=monto,
        forma_pago=forma_pago,
        nro_comprobante=nro_comprobante,
        nro_transaccion=nro_transaccion,
        observaciones=observaciones,
        nro_cuota=None  # Pago parcial sin cuota específica
    )
    
    print(f"\n✅ ¡PAGO PARCIAL REGISTRADO EXITOSAMENTE!")
    
    # Generar comprobante
    generar_comprobante_pago(pago, estudiante, matricula)

def pagar_solo_intereses(matricula, estudiante, cuotas):
    """Procesa el pago solo de intereses de mora"""
    from datetime import date
    
    print(f"\n💵 PAGO DE INTERESES DE MORA")
    print("-" * 40)
    
    # Calcular total de intereses
    total_intereses = sum(c.interes_mora for c in cuotas if hasattr(c, 'interes_mora') and c.interes_mora > 0)
    
    if total_intereses <= 0:
        print("ℹ️  No hay intereses de mora pendientes")
        return
    
    print(f"   • Total intereses de mora: ${total_intereses:.2f}")
    print(f"   • Cuotas con mora: {sum(1 for c in cuotas if hasattr(c, 'interes_mora') and c.interes_mora > 0)}")
    
    for cuota in cuotas:
        if hasattr(cuota, 'interes_mora') and cuota.interes_mora > 0:
            print(f"      • Cuota {cuota.nro_cuota}: ${cuota.interes_mora:.2f} ({cuota.dias_mora} días)")
    
    # Obtener detalles del pago
    forma_pago, nro_comprobante, nro_transaccion, observaciones = obtener_detalles_pago()
    
    if not forma_pago:
        print("❌ Pago cancelado")
        return
    
    # Confirmar pago
    confirmar = input(f"\n👉 ¿Confirmar pago de ${total_intereses:.2f} en intereses? (s/n): ").lower()
    if confirmar != 's':
        print("❌ Pago cancelado")
        return
    
    try:
        # Registrar pago en la matrícula
        pago = matricula.registrar_pago(
            monto=total_intereses,
            forma_pago=forma_pago,
            nro_comprobante=nro_comprobante if nro_comprobante else None,
            nro_transaccion=nro_transaccion if nro_transaccion else None,
            observaciones=observaciones if observaciones else f"Pago de intereses de mora"
        )
        
        print(f"\n✅ ¡PAGO DE INTERESES REGISTRADO EXITOSAMENTE!")
        print(f"   • Número de pago: {pago.id}")
        print(f"   • Intereses pagados: ${total_intereses:.2f}")
        print(f"   • Nuevo saldo: ${matricula.saldo_pendiente:.2f}")
        
        # Generar comprobante
        generar_comprobante_pago(pago, estudiante, matricula, None, es_intereses=True)
        
    except Exception as e:
        print(f"❌ Error al registrar el pago: {e}")

def registrar_pago_general(matricula, estudiante):
    """Registra un pago al saldo general (sin cuotas específicas)"""
    from datetime import date
    from models.pago import PagoModel
    
    print(f"\n💵 PAGO AL SALDO GENERAL")
    print("-" * 40)
    
    saldo_pendiente = matricula.saldo_pendiente
    print(f"   • Saldo pendiente: ${saldo_pendiente:.2f}")
    
    # Inicializar monto como None
    monto = None
    
    # Obtener el monto del usuario
    while monto is None:
        monto_str = input(f"\n👉 Ingrese monto a pagar (máximo ${saldo_pendiente:.2f}): $").strip()
        
        if not monto_str:
            print("❌ Debe ingresar un monto")
            continue
        
        try:
            monto = float(monto_str)
            
            if monto <= 0:
                print("❌ El monto debe ser mayor a 0")
                monto = None
                continue
            
            if monto > saldo_pendiente:
                print(f"❌ El monto excede el saldo pendiente (${saldo_pendiente:.2f})")
                monto = None
                continue
                
        except ValueError:
            print("❌ Monto inválido. Debe ser un número.")
            monto = None
    
    # Obtener detalles del pago
    try:
        forma_pago, nro_comprobante, nro_transaccion, observaciones = obtener_detalles_pago()
    except Exception as e:
        print(f"❌ Error al obtener detalles del pago: {e}")
        return
    
    if not forma_pago:
        print("❌ Pago cancelado")
        return
    
    # Confirmar pago
    confirmar = input("\n👉 ¿Confirmar el pago? (s/n): ").lower()
    if confirmar != 's':
        print("❌ Pago cancelado")
        return
    
    try:
        # Registrar pago en la matrícula
        pago = matricula.registrar_pago(
            monto=monto,  # Ahora monto está definitivamente definido
            forma_pago=forma_pago,
            nro_comprobante=nro_comprobante if nro_comprobante else None,
            nro_transaccion=nro_transaccion if nro_transaccion else None,
            observaciones=observaciones if observaciones else None,
            nro_cuota=None  # Para pagos generales sin cuota específica
        )
        
        print(f"\n✅ ¡PAGO REGISTRADO EXITOSAMENTE!")
        print(f"   • Número de pago: {pago.id}")
        print(f"   • Monto pagado: ${monto:.2f}")
        print(f"   • Nuevo saldo: ${matricula.saldo_pendiente:.2f}")
        print(f"   • Estado actual: {matricula.estado_pago}")
        
        # Generar comprobante
        generar_comprobante_pago(pago, estudiante, matricula)
        
    except Exception as e:
        print(f"❌ Error al registrar el pago: {e}")

def obtener_detalles_pago():
    """Obtiene los detalles de un pago del usuario"""
    
    print("\n📄 DETALLES DEL PAGO:")
    print("-" * 40)
    
    # Forma de pago
    formas_pago = ['EFECTIVO', 'TRANSFERENCIA', 'TARJETA', 'DEPOSITO', 'CHEQUE', "QR"]
    print("Formas de pago disponibles:")
    for i, forma in enumerate(formas_pago, 1):
        print(f"  {i}. {forma}")
    
    forma_seleccion = input("\n👉 Seleccione forma de pago (1-6): ").strip()
    
    if not forma_seleccion.isdigit() or not (1 <= int(forma_seleccion) <= len(formas_pago)):
        print("❌ Selección inválida")
        return None, None, None, None
    
    forma_pago = formas_pago[int(forma_seleccion) - 1]
    
    # Número de comprobante
    nro_comprobante = input("Número de comprobante (opcional): ").strip()
    if nro_comprobante == "":
        nro_comprobante = None
    
    # Número de transacción
    nro_transaccion = input("Número de transacción (opcional): ").strip()
    if nro_transaccion == "":
        nro_transaccion = None
    
    # Observaciones
    observaciones = input("Observaciones (opcional): ").strip()
    if observaciones == "":
        observaciones = None
    
    return forma_pago, nro_comprobante, nro_transaccion, observaciones

# Gestión de gastos operativos
def gestionar_gastos_operativos():
    """Menú de gestión de gastos operativos"""
    from controllers.gastos_operativos_controller import (
        mostrar_menu_gastos, 
        registrar_gasto_operativo,
        ver_gastos_por_fecha,
        ver_gastos_por_categoria,
        ver_resumen_por_categoria
    )
    
    while True:
        mostrar_menu_gastos()
        opcion = input("\n👉 Seleccione una opción: ").strip()
        
        if opcion == '1':
            registrar_gasto_operativo()
        elif opcion == '2':
            ver_gastos_por_fecha()
        elif opcion == '3':
            ver_gastos_por_categoria()
        elif opcion == '4':
            ver_resumen_por_categoria()
        elif opcion == '5':
            break
        else:
            print("❌ Opción no válida. Intente de nuevo.")
        
        input("\nPresione Enter para continuar...")

# Ver movimientos de caja 
def ver_movimientos_caja():
    """Muestra los movimientos de caja y estado actual"""
    mostrar_encabezado("MOVIMIENTOS DE CAJA")
    
    try:
        from models.movimiento_caja import MovimientoCajaModel
        from datetime import datetime, timedelta
        
        # Obtener saldo actual
        saldo_actual = MovimientoCajaModel.obtener_saldo_actual()
        
        print(f"💰 SALDO ACTUAL DE CAJA: ${saldo_actual:,.2f} Bs.")
        print("-" * 60)
        
        # Opciones de filtro
        print("\n📅 SELECCIONE PERÍODO:")
        print("  1. Hoy")
        print("  2. Últimos 7 días")
        print("  3. Este mes")
        print("  4. Rango personalizado")
        print("  5. Todos los movimientos")
        
        opcion = input("\n👉 Seleccione opción (1-5): ").strip()
        
        movimientos = []
        hoy = datetime.now().date()
        
        if opcion == "1":
            # Movimientos de hoy
            movimientos = MovimientoCajaModel.obtener_movimientos_hoy()
            print(f"\n📋 MOVIMIENTOS DE HOY ({hoy})")
            
        elif opcion == "2":
            # Últimos 7 días
            fecha_inicio = (hoy - timedelta(days=7)).isoformat()
            fecha_fin = hoy.isoformat()
            movimientos = MovimientoCajaModel.obtener_movimientos_rango(fecha_inicio, fecha_fin)
            print(f"\n📋 MOVIMIENTOS ÚLTIMOS 7 DÍAS")
            
        elif opcion == "3":
            # Este mes
            fecha_inicio = hoy.replace(day=1).isoformat()
            fecha_fin = hoy.isoformat()
            movimientos = MovimientoCajaModel.obtener_movimientos_rango(fecha_inicio, fecha_fin)
            print(f"\n📋 MOVIMIENTOS DE ESTE MES")
            
        elif opcion == "4":
            # Rango personalizado
            fecha_inicio = input("Fecha inicio (YYYY-MM-DD): ").strip()
            fecha_fin = input("Fecha fin (YYYY-MM-DD): ").strip()
            movimientos = MovimientoCajaModel.obtener_movimientos_rango(fecha_inicio, fecha_fin)
            print(f"\n📋 MOVIMIENTOS DE {fecha_inicio} A {fecha_fin}")
            
        elif opcion == "5":
            # Todos los movimientos
            from database.database import db
            query = "SELECT * FROM movimientos_caja ORDER BY fecha DESC"
            rows = db.fetch_all(query)
            movimientos = [MovimientoCajaModel(**row) for row in rows]
            print(f"\n📋 TODOS LOS MOVIMIENTOS")
            
        else:
            print("❌ Opción no válida")
            pausar()
            return
        
        if not movimientos:
            print("\nℹ️  No hay movimientos registrados en este período")
            pausar()
            return
        
        # Mostrar movimientos en tabla
        print("\n" + "=" * 100)
        print(f"{'FECHA':<20} {'TIPO':<10} {'MONTO':<15} {'DESCRIPCIÓN':<40} {'REFERENCIA':<20}")
        print("=" * 100)
        
        total_ingresos = 0
        total_egresos = 0
        
        for movimiento in movimientos:
            # Formatear fecha
            fecha_str = ""
            if hasattr(movimiento, 'fecha') and movimiento.fecha:
                fecha_str = str(movimiento.fecha)
                if len(fecha_str) > 10:
                    fecha_str = fecha_str[:16]  # YYYY-MM-DD HH:MM
            
            # Formatear tipo con emoji
            tipo_emoji = "📈" if movimiento.tipo == 'INGRESO' else "📉"
            tipo_str = f"{tipo_emoji} {movimiento.tipo}"
            
            # Formatear monto
            monto_str = f"${movimiento.monto:,.2f}"
            
            # Formatear referencia
            referencia = ""
            if hasattr(movimiento, 'referencia_tipo') and movimiento.referencia_tipo:
                ref_id = getattr(movimiento, 'referencia_id', '')
                referencia = f"{movimiento.referencia_tipo} #{ref_id}"
            
            # Descripción (cortar si es muy larga)
            descripcion = getattr(movimiento, 'descripcion', '')
            if len(descripcion) > 38:
                descripcion = descripcion[:35] + "..."
            
            print(f"{fecha_str:<20} {tipo_str:<10} {monto_str:<15} {descripcion:<40} {referencia:<20}")
            
            # Acumular totales
            if movimiento.tipo == 'INGRESO':
                total_ingresos += movimiento.monto
            else:
                total_egresos += movimiento.monto
        
        print("=" * 100)
        print(f"{'TOTAL INGRESOS:':<60} ${total_ingresos:,.2f}")
        print(f"{'TOTAL EGRESOS:':<60} ${total_egresos:,.2f}")
        print(f"{'SALDO NETO DEL PERÍODO:':<60} ${total_ingresos - total_egresos:,.2f}")
        
        # Mostrar resumen
        print(f"\n📊 RESUMEN:")
        print(f"   • Movimientos totales: {len(movimientos)}")
        print(f"   • Ingresos totales: ${total_ingresos:,.2f}")
        print(f"   • Egresos totales: ${total_egresos:,.2f}")
        print(f"   • Saldo período: ${total_ingresos - total_egresos:,.2f}")
        print(f"   • Saldo acumulado: ${saldo_actual:,.2f}")
        
        # Opción para exportar
        exportar = input("\n💾 ¿Desea exportar a archivo? (s/n): ").lower()
        if exportar == 's':
            nombre_archivo = f"movimientos_caja_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            try:
                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                    f.write("MOVIMIENTOS DE CAJA\n")
                    f.write("=" * 60 + "\n")
                    f.write(f"Fecha de reporte: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Saldo actual: ${saldo_actual:,.2f} Bs.\n\n")
                    
                    for movimiento in movimientos:
                        fecha_str = str(getattr(movimiento, 'fecha', ''))
                        f.write(f"{fecha_str[:16]} | {movimiento.tipo} | ${movimiento.monto:,.2f} | {getattr(movimiento, 'descripcion', '')}\n")
                    
                    f.write(f"\nTOTAL INGRESOS: ${total_ingresos:,.2f}\n")
                    f.write(f"TOTAL EGRESOS: ${total_egresos:,.2f}\n")
                    f.write(f"SALDO NETO: ${total_ingresos - total_egresos:,.2f}\n")
                
                print(f"✅ Reporte exportado a: {nombre_archivo}")
            except Exception as e:
                print(f"❌ Error al exportar: {e}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    pausar()

def generar_comprobante_pago(pago, estudiante, matricula, cuota=None, es_intereses=False):
    """Genera un comprobante de pago en formato texto"""
    try:
        from datetime import datetime
        
        # Crear nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprobante_pago_{pago.id}_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("         FORMA GEST PRO - COMPROBANTE DE PAGO\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"📅 Fecha de emisión: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"📄 Número de comprobante: {pago.id}\n\n")
            
            f.write("👤 DATOS DEL ESTUDIANTE:\n")
            f.write(f"   • Nombre: {estudiante.nombre_completo}\n")
            f.write(f"   • CI: {estudiante.ci_numero}-{estudiante.ci_expedicion}\n")
            if hasattr(estudiante, 'email') and estudiante.email:
                f.write(f"   • Email: {estudiante.email}\n")
            f.write("\n")
            
            detalles = matricula.obtener_detalles_completos()
            if detalles['programa']:
                f.write("📚 DATOS DEL PROGRAMA:\n")
                f.write(f"   • Programa: {detalles['programa']['nombre']}\n")
                f.write(f"   • Código: {detalles['programa']['codigo']}\n")
                f.write(f"   • Matrícula ID: {matricula.id}\n")
                f.write("\n")
            
            f.write("💰 DETALLES DEL PAGO:\n")
            f.write(f"   • Monto pagado: ${pago.monto:.2f}\n")
            f.write(f"   • Forma de pago: {pago.forma_pago}\n")
            f.write(f"   • Fecha de pago: {pago.fecha_pago}\n")
            
            if pago.nro_comprobante:
                f.write(f"   • N° Comprobante: {pago.nro_comprobante}\n")
            if pago.nro_transaccion:
                f.write(f"   • N° Transacción: {pago.nro_transaccion}\n")
            
            if cuota:
                f.write(f"   • Cuota aplicada: {cuota.nro_cuota}\n")
                f.write(f"   • Vencimiento original: {cuota.fecha_vencimiento}\n")
            
            if es_intereses:
                f.write(f"   • Tipo: Pago de intereses de mora\n")
            
            f.write("\n")
            f.write("📊 ESTADO ACTUAL DE LA MATRÍCULA:\n")
            f.write(f"   • Total del programa: ${matricula.monto_final:.2f}\n")
            f.write(f"   • Pagado a la fecha: ${matricula.monto_pagado:.2f}\n")
            f.write(f"   • Saldo pendiente: ${matricula.saldo_pendiente:.2f}\n")
            f.write(f"   • Porcentaje pagado: {matricula.porcentaje_pagado:.1f}%\n")
            f.write(f"   • Estado de pago: {matricula.estado_pago}\n")
            f.write("\n")
            
            f.write("=" * 60 + "\n")
            f.write("         ¡GRACIAS POR SU PAGO!\n")
            f.write("=" * 60 + "\n")
        
        print(f"✅ Comprobante generado: {filename}")
        
        # Mostrar opción para imprimir
        imprimir = input("\n¿Desea imprimir el comprobante? (s/n): ").lower()
        if imprimir == 's':
            try:
                import os
                if os.name == 'nt':  # Windows
                    os.startfile(filename, "print")
                else:  # Linux/Mac
                    os.system(f"lpr {filename}")
                print("✅ Comprobante enviado a impresión")
            except:
                print("⚠️  No se pudo imprimir automáticamente")
    
    except Exception as e:
        print(f"⚠️  No se pudo generar el comprobante: {e}")

# Configurar o modificar promoción de un programa
def configurar_promocion():
    """Configura o modifica solo la promoción de un programa"""
    mostrar_encabezado("CONFIGURAR PROMOCIÓN DE PROGRAMA")
    
    try:
        from models.programa import ProgramaModel
        from datetime import datetime
        from utils.calculos_financieros import (
            calcular_descuento_exacto,
            calcular_porcentaje_para_monto_final,
            formatear_moneda,
            redondear_a_entero_cercano
        )
        
        # Buscar programa por código
        codigo = input("Código del programa: ").strip()
        programa = ProgramaModel.buscar_por_codigo(codigo)
        
        if not programa:
            print(f"❌ No se encontró programa con código {codigo}")
            pausar()
            return
        
        print(f"\n📋 Programa: {programa.nombre}")
        print(f"   Colegiatura base: ${formatear_moneda(programa.costo_base)} Bs.")
        
        # Mostrar estado actual de promoción
        promocion_activa = getattr(programa, 'promocion_activa', False)
        descripcion_promocion = getattr(programa, 'descripcion_promocion', '')
        descuento_promocion = getattr(programa, 'descuento_promocion', 0)
        promocion_fecha_limite = getattr(programa, 'promocion_fecha_limite', None)
        
        if promocion_activa:
            print(f"\n🎁 PROMOCIÓN ACTUAL:")
            print(f"   • Descripción: {descripcion_promocion}")
            print(f"   • Descuento: {descuento_promocion}%")
            if promocion_fecha_limite:
                print(f"   • Fecha límite: {promocion_fecha_limite}")
            
            # Mostrar cálculo actual
            descuento_actual, monto_final_actual = calcular_descuento_exacto(
                programa.costo_base, 
                descuento_promocion
            )
            print(f"   • Colegiatura con descuento: ${formatear_moneda(monto_final_actual)} Bs.")
        else:
            print(f"\n🎁 PROMOCIÓN: No activa")
        
        print("\n" + "=" * 50)
        print("OPCIONES DE CONFIGURACIÓN")
        print("=" * 50)
        
        print("\n1. Activar nueva promoción")
        print("2. Modificar promoción existente")
        print("3. Desactivar promoción")
        print("4. Solo cambiar fecha límite")
        print("5. Cancelar")
        
        opcion = input("\n👉 Seleccione opción (1-5): ").strip()
        
        if opcion in ["1", "2"]:
            # Preguntar cómo desea ingresar el descuento
            print("\n📊 MÉTODO DE INGRESO DE DESCUENTO:")
            print("  1. Porcentaje de descuento (ej: 7.37%)")
            print("  2. Monto final deseado (ej: 3520 Bs.)")
            
            metodo = input("\n👉 Seleccione método (1-2): ").strip()
            
            descuento = 0
            monto_final_deseado = 0
            
            if metodo == "1":
                # Ingresar porcentaje
                descuento_input = input("Porcentaje de descuento sobre colegiatura (%): ").strip()
                try:
                    descuento = float(descuento_input)
                    if descuento < 0 or descuento > 100:
                        print("❌ El descuento debe estar entre 0 y 100%")
                        pausar()
                        return
                except ValueError:
                    print("❌ El descuento debe ser un número")
                    pausar()
                    return
                
                # Calcular monto final con redondeo preciso
                descuento_calculado, monto_final = calcular_descuento_exacto(
                    programa.costo_base, 
                    descuento
                )
                monto_final_deseado = monto_final
                
            elif metodo == "2":
                # Ingresar monto final deseado
                monto_input = input("Monto final deseado de la colegiatura (Bs.): ").strip()
                try:
                    monto_final_deseado = float(monto_input)
                    if monto_final_deseado <= 0 or monto_final_deseado > programa.costo_base:
                        print(f"❌ El monto debe estar entre 0 y {programa.costo_base}")
                        pausar()
                        return
                except ValueError:
                    print("❌ El monto debe ser un número")
                    pausar()
                    return
                
                # Calcular porcentaje necesario
                descuento = calcular_porcentaje_para_monto_final(
                    programa.costo_base, 
                    monto_final_deseado
                )
                descuento_calculado = programa.costo_base - monto_final_deseado
            else:
                print("❌ Método no válido")
                pausar()
                return
            
            # Resto de los datos de la promoción
            descripcion = input("Descripción de la promoción: ").strip()
            if not descripcion:
                print("❌ La descripción es obligatoria")
                pausar()
                return
            
            fecha_limite = input("Fecha límite (YYYY-MM-DD, opcional): ").strip()
            if fecha_limite:
                try:
                    datetime.strptime(fecha_limite, "%Y-%m-%d")
                except ValueError:
                    print("❌ Formato de fecha inválido. Use YYYY-MM-DD")
                    pausar()
                    return
            
            # Mostrar cálculo exacto con redondeo
            print(f"\n📊 CÁLCULO EXACTO CON REDONDEO:")
            print(f"   • Colegiatura original: ${formatear_moneda(programa.costo_base)} Bs.")
            print(f"   • Descuento ({descuento:.6f}%): ${formatear_moneda(descuento_calculado)} Bs.")
            print(f"   • Colegiatura con descuento: ${formatear_moneda(monto_final_deseado)} Bs.")
            
            # Mostrar también redondeado a entero si el usuario quiere
            if abs(monto_final_deseado - redondear_a_entero_cercano(monto_final_deseado)) < 0.01:
                print(f"   • Colegiatura (entero): ${redondear_a_entero_cercano(monto_final_deseado):.0f} Bs.")
            
            confirmar = input("\n¿Confirmar cambios? (s/n): ").lower().strip()
            if confirmar != 's':
                print("❌ Cambios cancelados")
                pausar()
                return
            
            # Usar el nuevo método de clase update_by_id
            datos_actualizacion = {
                'promocion_activa': 1,
                'descripcion_promocion': descripcion,
                'descuento_promocion': round(descuento, 6),
                'promocion_fecha_limite': fecha_limite if fecha_limite else None,
                'updated_at': datetime.now().isoformat()
            }
            
            # Llamar al método de clase que actualiza por ID
            if ProgramaModel.update_by_id(programa.id, datos_actualizacion):
                print("\n✅ Promoción configurada exitosamente!")
            else:
                print("❌ Error al actualizar la promoción")
                pausar()
                return
            
        elif opcion == "3":
            # Desactivar promoción
            confirmar = input("¿Desactivar promoción actual? (s/n): ").lower().strip()
            if confirmar != 's':
                print("❌ Operación cancelada")
                pausar()
                return
            
            # Usar el nuevo método de clase update_by_id
            datos_actualizacion = {
                'promocion_activa': 0,
                'descripcion_promocion': '',
                'descuento_promocion': 0,
                'promocion_fecha_limite': None,
                'updated_at': datetime.now().isoformat()
            }
            
            if ProgramaModel.update_by_id(programa.id, datos_actualizacion):
                print("\n✅ Promoción desactivada exitosamente!")
            else:
                print("❌ Error al desactivar la promoción")
                pausar()
                return
            
        elif opcion == "4":
            # Solo cambiar fecha límite
            if not getattr(programa, 'promocion_activa', False):
                print("❌ No hay promoción activa para modificar")
                pausar()
                return
            
            nueva_fecha = input("Nueva fecha límite (YYYY-MM-DD): ").strip()
            if not nueva_fecha:
                print("❌ La fecha es obligatoria")
                pausar()
                return
            
            try:
                datetime.strptime(nueva_fecha, "%Y-%m-%d")
            except ValueError:
                print("❌ Formato de fecha inválido")
                pausar()
                return
            
            # Usar el nuevo método de clase update_by_id
            datos_actualizacion = {
                'promocion_fecha_limite': nueva_fecha,
                'updated_at': datetime.now().isoformat()
            }
            
            if ProgramaModel.update_by_id(programa.id, datos_actualizacion):
                print("\n✅ Fecha límite actualizada exitosamente!")
            else:
                print("❌ Error al actualizar la fecha límite")
                pausar()
                return
            
        elif opcion == "5":
            print("❌ Operación cancelada")
            pausar()
            return
        
        else:
            print("❌ Opción no válida")
            pausar()
            return
        
        # Mostrar resumen actualizado
        programa_actualizado = ProgramaModel.find_by_id(programa.id)
        if programa_actualizado:
            promocion_activa = getattr(programa_actualizado, 'promocion_activa', False)
            if promocion_activa:
                print(f"\n🎁 NUEVO ESTADO DE PROMOCIÓN:")
                print(f"   • Descripción: {getattr(programa_actualizado, 'descripcion_promocion', '')}")
                print(f"   • Descuento: {getattr(programa_actualizado, 'descuento_promocion', 0):.2f}%")
                fecha_limite = getattr(programa_actualizado, 'promocion_fecha_limite', None)
                if fecha_limite:
                    print(f"   • Fecha límite: {fecha_limite}")
                
                # Mostrar cálculo exacto
                descuento_calc, monto_final = calcular_descuento_exacto(
                    programa_actualizado.costo_base,
                    getattr(programa_actualizado, 'descuento_promocion', 0)
                )
                print(f"   • Colegiatura con descuento: ${formatear_moneda(monto_final)} Bs.")
            else:
                print(f"\n   • Promoción: Desactivada")
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
    
    pausar()

# En cli.py, agrega esta función (puede ir cerca de otras funciones similares):
def gestionar_gastos_operativos():
    """Menú de gestión de gastos operativos"""
    from controllers.gastos_operativos_controller import (
        mostrar_menu_gastos, 
        registrar_gasto_operativo,
        ver_gastos_por_fecha,
        ver_gastos_por_categoria,
        ver_resumen_por_categoria
    )
    
    while True:
        mostrar_menu_gastos()
        opcion = input("\n👉 Seleccione una opción: ").strip()
        
        if opcion == '1':
            registrar_gasto_operativo()
        elif opcion == '2':
            ver_gastos_por_fecha()
        elif opcion == '3':
            ver_gastos_por_categoria()
        elif opcion == '4':
            ver_resumen_por_categoria()
        elif opcion == '5':
            break
        else:
            print("❌ Opción no válida. Intente de nuevo.")
        
        input("\nPresione Enter para continuar...")

# ============================================
# FUNCIÓN PRINCIPAL
# ============================================

def main():
    """Función principal del CLI"""
    print("🚀 Iniciando FormaGestPro - Sistema de Gestión Académica")
    print("🔌 Conectando a la base de datos...")
    
    try:
        from database.database import db
        print(f"✅ Conectado a: {db._db_path}")
        
        # Verificar si hay tablas
        tablas = db.get_all_tables()
        if not tablas:
            print("⚠️  No hay tablas en la base de datos")
            respuesta = input("¿Desea inicializar la base de datos? (s/n): ").lower()
            if respuesta == 's':
                inicializar_base_datos()
                return
        
    except Exception as e:
        print(f"❌ Error al conectar con la base de datos: {e}")
        print("💡 Ejecute: python scripts/init_database.py")
        pausar()
        return
    
    # Bucle principal del menú
    while True:
        try:
            mostrar_menu_principal()
            opcion = input("\n👉 Seleccione una opción: ").strip()
            
            if opcion == '0':
                print("\n👋 ¡Gracias por usar FormaGestPro! ¡Hasta pronto!")
                break
            
            # Gestión de Estudiantes
            elif opcion == '1':
                registrar_estudiante()
            elif opcion == '2':
                listar_estudiantes()
            elif opcion == '3':
                buscar_estudiante_ci()
            elif opcion == '4':
                buscar_estudiante_nombre()
            elif opcion == '5':
                ver_estadisticas_estudiantes()
            
            # Gestión de Docentes
            elif opcion == '6':
                registrar_docente()
            elif opcion == '7':
                listar_docentes()
            elif opcion == '8':
                buscar_docente_ci()
            elif opcion == '9':
                buscar_docente_especialidad()
            elif opcion == '10':
                ver_estadisticas_docentes()
            
            # Gestión de Programas
            elif opcion == '11':
                crear_programa()
            elif opcion == '12':
                listar_programas()
            elif opcion == '13':
                buscar_programa_codigo()
            elif opcion == '14':
                editar_programa_menu()
            elif opcion == '15':
                configurar_promocion()
            elif opcion == '16':
                buscar_programas_cupos()
            elif opcion == '17':
                ver_estadisticas_programas()

            # Gestión Financiera
            elif opcion == '18':
                registrar_matricula()
            elif opcion == '19':
                registrar_pago_cuota()
            elif opcion == '20':
                ver_estado_pagos_estudiante()
            elif opcion == '21':
                gestionar_planes_pago()
            elif opcion == "22":
                ver_movimientos_caja()
            elif opcion == "23":
                gestionar_gastos_operativos()
            elif opcion == "24":
                gestionar_comprobantes()
            elif opcion == "25":
                gestionar_ingresos_genericos()
            
            # Utilidades
            elif opcion == '26':
                verificar_sistema()
            elif opcion == '27':
                inicializar_base_datos()
            
            else:
                print(f"\n❌ Opción '{opcion}' no válida. Intente de nuevo.")
                pausar()
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupción por usuario")
            confirmar = input("¿Desea salir del sistema? (s/n): ").lower()
            if confirmar == 's':
                print("\n👋 ¡Hasta pronto!")
                break
        
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            import traceback
            traceback.print_exc()
            pausar()

if __name__ == "__main__":
    main()