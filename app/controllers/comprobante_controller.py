# app/controllers/comprobante_controller.py
"""
Controlador para gestión de comprobantes.
"""
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Importar modelos y servicios
from app.models.movimiento_caja_model import MovimientoCajaModel
from database import Database
from app.models.usuarios_model import UsuariosModel

logger = logging.getLogger(__name__)

# Asegurar que existe el directorio comprobantes
COMPROBANTES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "comprobantes"
)
os.makedirs(COMPROBANTES_DIR, exist_ok=True)


class ComprobanteController:
    """Controlador para la gestión de comprobantes"""

    def __init__(self, db_path: str = None):  # type:ignore
        """
        Inicializar controlador de comprobantes

        Args:
            db_path: Ruta a la base de datos (opcional)
        """
        self.db_path = db_path
        self._current_usuario = None
        self.db = Database()

    @property
    def current_usuario(self) -> Optional[UsuariosModel]:
        """Obtener usuario actual"""
        return self._current_usuario

    @current_usuario.setter
    def current_usuario(self, usuario: UsuariosModel):
        """Establecer usuario actual"""
        self._current_usuario = usuario

    def mostrar_menu_comprobantes(self):
        """Muestra el menú de gestión de comprobantes"""
        print("\n" + "=" * 60)
        print("🧾 GESTIÓN DE COMPROBANTES")
        print("=" * 60)
        print("1. Buscar movimientos por fecha")
        print("2. Buscar movimientos por tipo (INGRESO/EGRESO)")
        print("3. Buscar movimientos por rango de fechas")
        print("4. Ver últimos 10 movimientos")
        print("5. Generar comprobante PDF")
        print("6. Volver al menú principal")

    def buscar_movimientos_por_fecha(self) -> List[Dict]:
        """Busca movimientos por fecha específica"""
        print("\n📅 BUSCAR MOVIMIENTOS POR FECHA")
        print("-" * 40)

        fecha_str = input("Fecha (YYYY-MM-DD) [hoy]: ").strip()
        if not fecha_str:
            fecha = datetime.now().date().isoformat()
        else:
            try:
                datetime.strptime(fecha_str, "%Y-%m-%d")
                fecha = fecha_str
            except ValueError:
                print("❌ Formato de fecha inválido. Use YYYY-MM-DD")
                return []

        query = """
        SELECT * FROM movimientos_caja 
        WHERE DATE(fecha) = ?
        ORDER BY fecha DESC
        """

        movimientos = self.db.fetch_all(query, (fecha,))

        if not movimientos:
            print(f"\n📭 No hay movimientos registrados para la fecha {fecha}")
            return []

        print(f"\n📋 Movimientos del {fecha}:")
        print("-" * 80)
        for mov in movimientos:
            print(f"  ID: {mov['id']} - {mov['tipo']} - ${mov['monto']:.2f}")
            print(f"     Descripción: {mov['descripcion']}")
            print(f"     Fecha: {mov['fecha']}")
            print("-" * 40)

        return movimientos

    def buscar_movimientos_por_tipo(self) -> List[Dict]:
        """Busca movimientos por tipo (INGRESO/EGRESO)"""
        print("\n🔍 BUSCAR MOVIMIENTOS POR TIPO")
        print("-" * 40)

        print("Tipos disponibles:")
        print("  1. INGRESO")
        print("  2. EGRESO")

        opcion = input("Seleccione tipo (1-2): ").strip()
        if opcion == "1":
            tipo = "INGRESO"
        elif opcion == "2":
            tipo = "EGRESO"
        else:
            print("❌ Opción no válida")
            return []

        # Opcional: filtrar por fecha
        fecha_str = input("Fecha (YYYY-MM-DD) [todas]: ").strip()

        if fecha_str:
            try:
                datetime.strptime(fecha_str, "%Y-%m-%d")
                query = """
                SELECT * FROM movimientos_caja 
                WHERE tipo = ? AND DATE(fecha) = ?
                ORDER BY fecha DESC
                """
                params = (tipo, fecha_str)
            except ValueError:
                print("❌ Formato de fecha inválido. Use YYYY-MM-DD")
                return []
        else:
            query = """
            SELECT * FROM movimientos_caja 
            WHERE tipo = ?
            ORDER BY fecha DESC
            LIMIT 20
            """
            params = (tipo,)

        movimientos = self.db.fetch_all(query, params)

        if not movimientos:
            print(f"\n📭 No hay movimientos de tipo {tipo}")
            return []

        print(f"\n📋 Movimientos de tipo {tipo}:")
        print("-" * 80)
        total = 0
        for mov in movimientos:
            print(f"  ID: {mov['id']} - ${mov['monto']:.2f}")
            print(f"     Descripción: {mov['descripcion']}")
            print(f"     Fecha: {mov['fecha']}")
            print("-" * 40)
            total += mov["monto"]

        print(f"\n💰 TOTAL {tipo}: ${total:.2f}")
        return movimientos

    def buscar_movimientos_por_rango(self) -> List[Dict]:
        """Busca movimientos por rango de fechas"""
        print("\n📅 BUSCAR MOVIMIENTOS POR RANGO DE FECHAS")
        print("-" * 40)

        try:
            fecha_inicio = input("Fecha inicio (YYYY-MM-DD): ").strip()
            fecha_fin = input("Fecha fin (YYYY-MM-DD): ").strip()

            # Validar fechas
            datetime.strptime(fecha_inicio, "%Y-%m-%d")
            datetime.strptime(fecha_fin, "%Y-%m-%d")

            query = """
            SELECT * FROM movimientos_caja 
            WHERE DATE(fecha) BETWEEN ? AND ?
            ORDER BY fecha DESC
            """

            movimientos = self.db.fetch_all(query, (fecha_inicio, fecha_fin))

            if not movimientos:
                print(f"\n📭 No hay movimientos entre {fecha_inicio} y {fecha_fin}")
                return []

            print(f"\n📋 Movimientos del {fecha_inicio} al {fecha_fin}:")
            print("-" * 80)

            total_ingresos = 0
            total_egresos = 0

            for mov in movimientos:
                tipo = mov["tipo"]
                monto = mov["monto"]

                if tipo == "INGRESO":
                    total_ingresos += monto
                    tipo_str = "💰 INGRESO"
                else:
                    total_egresos += monto
                    tipo_str = "💸 EGRESO"

                print(f"  ID: {mov['id']} - {tipo_str} - ${monto:.2f}")
                print(f"     Descripción: {mov['descripcion']}")
                print(f"     Fecha: {mov['fecha']}")
                print("-" * 40)

            print(f"\n📊 RESUMEN DEL PERÍODO:")
            print(f"   Total Ingresos: ${total_ingresos:.2f}")
            print(f"   Total Egresos: ${total_egresos:.2f}")
            print(f"   Saldo Neto: ${total_ingresos - total_egresos:.2f}")

            return movimientos

        except ValueError as e:
            print(f"❌ Error en formato de fecha: {e}")
            return []

    def ver_ultimos_movimientos(self) -> List[Dict]:
        """Muestra los últimos 10 movimientos"""
        print("\n🕐 ÚLTIMOS 10 MOVIMIENTOS")
        print("-" * 40)

        query = """
        SELECT * FROM movimientos_caja 
        ORDER BY fecha DESC 
        LIMIT 10
        """

        movimientos = self.db.fetch_all(query)

        if not movimientos:
            print("\n📭 No hay movimientos registrados")
            return []

        for mov in movimientos:
            tipo = mov["tipo"]
            if tipo == "INGRESO":
                tipo_str = "💰 INGRESO"
            else:
                tipo_str = "💸 EGRESO"

            print(f"  ID: {mov['id']:3d} - {tipo_str:10s} - ${mov['monto']:8.2f}")
            print(f"     {mov['descripcion'][:50]}")
            print(f"     {mov['fecha']}")
            print()

        return movimientos

    def generar_comprobante_seleccionado(self) -> Tuple[bool, str]:
        """
        Permite seleccionar un movimiento y generar su comprobante

        Returns:
            Tuple (éxito, mensaje)
        """
        print("\n🧾 GENERAR COMPROBANTE")
        print("-" * 40)

        try:
            # Pedir ID del movimiento
            movimiento_id = input("ID del movimiento de caja: ").strip()
            if not movimiento_id:
                print("❌ Debe ingresar un ID")
                return False, "Debe ingresar un ID"

            movimiento_id = int(movimiento_id)

            # Verificar que existe
            movimiento = MovimientoCajaModel.get_by_id(
                MovimientoCajaModel(), movimiento_id
            )
            if not movimiento:
                return False, f"No se encontró movimiento con ID {movimiento_id}"

            # Mostrar información del movimiento
            print(f"\n📄 Información del movimiento:")
            print(f"   ID: {movimiento.id}")  # type:ignore
            print(f"   Tipo: {movimiento.tipo}")  # type:ignore
            print(f"   Monto: Bs. {float(movimiento.monto):,.2f}")  # type:ignore
            print(f"   Descripción: {movimiento.descripcion}")  # type:ignore
            print(f"   Fecha: {movimiento.fecha}")  # type:ignore

            # Confirmar generación
            confirmar = input("\n¿Generar comprobante? (s/n): ").strip().lower()
            if confirmar != "s":
                return False, "Generación cancelada por el usuario"

            # Generar comprobante básico
            print("\n⏳ Generando comprobante...")
            comprobante = self._generar_comprobante_texto(movimiento)

            # Guardar en archivo
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo_path = os.path.join(
                COMPROBANTES_DIR, f"comprobante_{movimiento_id}_{fecha}.txt"
            )

            with open(archivo_path, "w", encoding="utf-8") as f:
                f.write(comprobante)

            print(f"\n✅ Comprobante generado exitosamente!")
            print(f"📄 Archivo: {archivo_path}")

            return True, f"Comprobante generado: {archivo_path}"

        except ValueError:
            return False, "ID debe ser un número"
        except Exception as e:
            logger.error(f"Error al generar comprobante: {e}")
            return False, f"Error al generar comprobante: {str(e)}"

    def _generar_comprobante_texto(self, movimiento) -> str:
        """Generar comprobante en formato texto"""
        comprobante = []
        comprobante.append("=" * 50)
        comprobante.append("COMPROBANTE DE CAJA".center(50))
        comprobante.append("=" * 50)
        comprobante.append(f"Número: COMP-{movimiento.id:06d}")
        comprobante.append(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        comprobante.append(f"Tipo: {movimiento.tipo}")
        comprobante.append("-" * 50)

        comprobante.append("DESCRIPCIÓN:")
        comprobante.append(f"  {movimiento.descripcion}")

        comprobante.append("-" * 50)

        comprobante.append("DETALLE:")
        comprobante.append(f"  ID Movimiento: {movimiento.id}")
        comprobante.append(f"  Monto: Bs. {float(movimiento.monto):,.2f}")
        comprobante.append(f"  Fecha Registro: {movimiento.fecha}")

        if movimiento.referencia_tipo:
            comprobante.append(
                f"  Referencia: {movimiento.referencia_tipo} #{movimiento.referencia_id}"
            )

        comprobante.append("-" * 50)

        comprobante.append("FIRMAS:")
        comprobante.append("  ___________________________")
        comprobante.append("        Responsable de Caja")
        comprobante.append("")
        comprobante.append("  ___________________________")
        comprobante.append("            Cliente")

        comprobante.append("=" * 50)

        return "\n".join(comprobante)

    def gestionar_comprobantes(self):
        """Menú principal de gestión de comprobantes"""
        while True:
            self.mostrar_menu_comprobantes()
            opcion = input("\n👉 Seleccione una opción: ").strip()

            if opcion == "1":
                movimientos = self.buscar_movimientos_por_fecha()
                if movimientos:
                    generar = (
                        input("\n¿Generar comprobante para algún movimiento? (s/n): ")
                        .strip()
                        .lower()
                    )
                    if generar == "s":
                        self.generar_comprobante_seleccionado()

            elif opcion == "2":
                movimientos = self.buscar_movimientos_por_tipo()
                if movimientos:
                    generar = (
                        input("\n¿Generar comprobante para algún movimiento? (s/n): ")
                        .strip()
                        .lower()
                    )
                    if generar == "s":
                        self.generar_comprobante_seleccionado()

            elif opcion == "3":
                movimientos = self.buscar_movimientos_por_rango()
                if movimientos:
                    generar = (
                        input("\n¿Generar comprobante para algún movimiento? (s/n): ")
                        .strip()
                        .lower()
                    )
                    if generar == "s":
                        self.generar_comprobante_seleccionado()

            elif opcion == "4":
                movimientos = self.ver_ultimos_movimientos()
                if movimientos:
                    generar = (
                        input("\n¿Generar comprobante para algún movimiento? (s/n): ")
                        .strip()
                        .lower()
                    )
                    if generar == "s":
                        self.generar_comprobante_seleccionado()

            elif opcion == "5":
                exito, mensaje = self.generar_comprobante_seleccionado()
                if not exito:
                    print(f"❌ {mensaje}")

            elif opcion == "6":
                break

            else:
                print("❌ Opción no válida. Intente de nuevo.")

            input("\nPresione Enter para continuar...")
