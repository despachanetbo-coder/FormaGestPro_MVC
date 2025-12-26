# app/controllers/movimiento_caja_controller.py
"""
Controlador para la gestión de movimientos de caja en FormaGestPro_MVC
"""

import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any, Union

from app.models.movimiento_caja_model import MovimientoCajaModel
from app.models.programa_academico_model import ProgramaAcademicoModel
from app.models.usuarios_model import UsuarioModel
from app.models.ingreso_model import IngresoModel
from app.models.gasto_model import GastoModel
from app.models.facturas_model import FacturaModel

logger = logging.getLogger(__name__)


class MovimientoCajaController:
    """Controlador para la gestión de movimientos de caja"""

    def __init__(self, db_path: str = None):
        """
        Inicializar controlador de movimientos de caja

        Args:
            db_path: Ruta a la base de datos (opcional)
        """
        self.db_path = db_path
        self._current_usuario = None  # Usuario actual (para auditoría)

    # ==================== PROPIEDADES ====================

    @property
    def current_usuario(self) -> Optional[UsuarioModel]:
        """Obtener usuario actual"""
        return self._current_usuario

    @current_usuario.setter
    def current_usuario(self, usuario: UsuarioModel):
        """Establecer usuario actual"""
        self._current_usuario = usuario

    # ==================== OPERACIONES BÁSICAS ====================

    def registrar_movimiento(
        self, datos: Dict[str, Any]
    ) -> Tuple[bool, str, Optional[MovimientoCajaModel]]:
        """
        Registrar un nuevo movimiento de caja

        Args:
            datos: Diccionario con los datos del movimiento

        Returns:
            Tuple (éxito, mensaje, movimiento)
        """
        try:
            # Verificar que haya usuario actual
            if not self._current_usuario:
                return (
                    False,
                    "No hay usuario autenticado para registrar movimiento",
                    None,
                )

            # Validar datos requeridos
            errores = self._validar_datos_movimiento(datos)
            if errores:
                return False, "Errores de validación: " + "; ".join(errores), None

            # Agregar usuario actual a los datos
            if "usuario_id" not in datos:
                datos["usuario_id"] = self._current_usuario.id

            # Agregar fecha si no se proporciona
            if "fecha" not in datos:
                datos["fecha"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Crear el movimiento
            movimiento = MovimientoCajaModel(**datos)
            movimiento_id = movimiento.save()

            if movimiento_id:
                movimiento_creado = MovimientoCajaModel.get_by_id(movimiento_id)
                mensaje = f"Movimiento registrado exitosamente (ID: {movimiento_id})"

                logger.info(
                    f"✅ Movimiento de caja registrado: {movimiento.tipo} - Bs. {movimiento.monto:.2f}"
                )
                return True, mensaje, movimiento_creado
            else:
                return False, "Error al guardar el movimiento en la base de datos", None

        except Exception as e:
            logger.error(f"Error al registrar movimiento de caja: {e}")
            return False, f"Error interno: {str(e)}", None

    def obtener_movimiento(self, movimiento_id: int) -> Optional[MovimientoCajaModel]:
        """
        Obtener un movimiento por ID

        Args:
            movimiento_id: ID del movimiento

        Returns:
            Modelo de movimiento o None
        """
        try:
            return MovimientoCajaModel.get_by_id(movimiento_id)
        except Exception as e:
            logger.error(f"Error al obtener movimiento {movimiento_id}: {e}")
            return None

    def eliminar_movimiento(self, movimiento_id: int) -> Tuple[bool, str]:
        """
        Eliminar un movimiento de caja

        Args:
            movimiento_id: ID del movimiento

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            movimiento = MovimientoCajaModel.get_by_id(movimiento_id)
            if not movimiento:
                return False, f"No se encontró movimiento con ID {movimiento_id}"

            # Verificar permisos del usuario
            if self._current_usuario and self._current_usuario.rol not in [
                "ADMIN",
                "CONTADOR",
            ]:
                return False, "No tiene permisos para eliminar movimientos"

            # Verificar si el movimiento tiene referencias
            if movimiento.referencia_tipo and movimiento.referencia_id:
                return (
                    False,
                    f"No se puede eliminar movimiento con referencia {movimiento.referencia_tipo} #{movimiento.referencia_id}",
                )

            # Eliminar movimiento
            if MovimientoCajaModel.delete(movimiento_id):
                logger.info(
                    f"Movimiento {movimiento_id} eliminado por usuario {self._current_usuario.id if self._current_usuario else 'desconocido'}"
                )
                return True, f"Movimiento {movimiento_id} eliminado exitosamente"
            else:
                return False, "Error al eliminar movimiento"

        except Exception as e:
            logger.error(f"Error al eliminar movimiento {movimiento_id}: {e}")
            return False, f"Error interno: {str(e)}"

    def anular_movimiento(self, movimiento_id: int) -> Tuple[bool, str]:
        """
        Anular un movimiento (crea movimiento inverso)

        Args:
            movimiento_id: ID del movimiento a anular

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            movimiento = MovimientoCajaModel.get_by_id(movimiento_id)
            if not movimiento:
                return False, f"No se encontró movimiento con ID {movimiento_id}"

            if movimiento.anulado:
                return False, f"El movimiento {movimiento_id} ya está anulado"

            # Verificar permisos del usuario
            if self._current_usuario and self._current_usuario.rol not in [
                "ADMIN",
                "CONTADOR",
            ]:
                return False, "No tiene permisos para anular movimientos"

            # Crear movimiento de anulación (inverso)
            datos_anulacion = {
                "tipo": "EGRESO" if movimiento.tipo == "INGRESO" else "INGRESO",
                "monto": float(movimiento.monto),
                "descripcion": f"ANULACIÓN de movimiento {movimiento_id}: {movimiento.descripcion}",
                "referencia_tipo": "ANULACION",
                "referencia_id": movimiento_id,
                "usuario_id": (
                    self._current_usuario.id if self._current_usuario else None
                ),
                "forma_pago": (
                    movimiento.forma_pago
                    if hasattr(movimiento, "forma_pago")
                    else "EFECTIVO"
                ),
            }

            exito, mensaje, movimiento_anulacion = self.registrar_movimiento(
                datos_anulacion
            )
            if exito:
                # Marcar el movimiento original como anulado
                movimiento.anulado = True
                movimiento.save()

                logger.info(
                    f"Movimiento {movimiento_id} anulado por movimiento {movimiento_anulacion.id}"
                )
                return True, f"Movimiento {movimiento_id} anulado exitosamente"
            else:
                return False, f"Error al anular movimiento: {mensaje}"

        except Exception as e:
            logger.error(f"Error al anular movimiento {movimiento_id}: {e}")
            return False, f"Error interno: {str(e)}"

    # ==================== MOVIMIENTOS POR TIPO DE REFERENCIA ====================

    def registrar_ingreso_pago(
        self, pago_id: int
    ) -> Tuple[bool, str, Optional[MovimientoCajaModel]]:
        """
        Registrar ingreso en caja por un pago

        Args:
            pago_id: ID del pago

        Returns:
            Tuple (éxito, mensaje, movimiento)
        """
        try:
            # Obtener datos del pago
            pago = PagoModel.get_by_id(pago_id)
            if not pago:
                return False, f"No se encontró pago con ID {pago_id}", None

            # Verificar si ya existe movimiento para este pago
            if self._existe_movimiento_para_referencia("PAGO", pago_id):
                return (
                    False,
                    f"Ya existe un movimiento registrado para el pago {pago_id}",
                    None,
                )

            # Obtener detalles adicionales para la descripción
            descripcion = self._generar_descripcion_pago(pago)

            # Obtener forma de pago del pago
            forma_pago = getattr(pago, "forma_pago", "EFECTIVO")

            # Crear movimiento
            datos_movimiento = {
                "tipo": "INGRESO",
                "monto": float(pago.monto),
                "descripcion": descripcion,
                "referencia_tipo": "PAGO",
                "referencia_id": pago_id,
                "usuario_id": (
                    self._current_usuario.id if self._current_usuario else None
                ),
                "forma_pago": forma_pago,
            }

            return self.registrar_movimiento(datos_movimiento)

        except Exception as e:
            logger.error(f"Error al registrar ingreso por pago {pago_id}: {e}")
            return False, f"Error interno: {str(e)}", None

    def registrar_ingreso_generico(
        self, ingreso_id: int
    ) -> Tuple[bool, str, Optional[MovimientoCajaModel]]:
        """
        Registrar ingreso en caja por un ingreso genérico

        Args:
            ingreso_id: ID del ingreso genérico

        Returns:
            Tuple (éxito, mensaje, movimiento)
        """
        try:
            # Obtener datos del ingreso
            ingreso = IngresoGenericoModel.get_by_id(ingreso_id)
            if not ingreso:
                return (
                    False,
                    f"No se encontró ingreso genérico con ID {ingreso_id}",
                    None,
                )

            # Verificar si ya existe movimiento para este ingreso
            if self._existe_movimiento_para_referencia("INGRESO_GENERICO", ingreso_id):
                return (
                    False,
                    f"Ya existe un movimiento registrado para el ingreso {ingreso_id}",
                    None,
                )

            # Crear descripción
            descripcion = f"Ingreso genérico: {ingreso.concepto}"
            if ingreso.descripcion:
                descripcion += f" - {ingreso.descripcion[:50]}"

            # Obtener forma de pago del ingreso
            forma_pago = getattr(ingreso, "forma_pago", "EFECTIVO")

            # Crear movimiento
            datos_movimiento = {
                "tipo": "INGRESO",
                "monto": float(ingreso.monto),
                "descripcion": descripcion,
                "referencia_tipo": "INGRESO_GENERICO",
                "referencia_id": ingreso_id,
                "usuario_id": (
                    self._current_usuario.id if self._current_usuario else None
                ),
                "forma_pago": forma_pago,
            }

            return self.registrar_movimiento(datos_movimiento)

        except Exception as e:
            logger.error(
                f"Error al registrar ingreso por ingreso genérico {ingreso_id}: {e}"
            )
            return False, f"Error interno: {str(e)}", None

    def registrar_egreso_gasto(
        self, gasto_id: int
    ) -> Tuple[bool, str, Optional[MovimientoCajaModel]]:
        """
        Registrar egreso en caja por un gasto operativo

        Args:
            gasto_id: ID del gasto operativo

        Returns:
            Tuple (éxito, mensaje, movimiento)
        """
        try:
            # Obtener datos del gasto
            gasto = GastoOperativoModel.get_by_id(gasto_id)
            if not gasto:
                return False, f"No se encontró gasto operativo con ID {gasto_id}", None

            # Verificar si ya existe movimiento para este gasto
            if self._existe_movimiento_para_referencia("GASTO", gasto_id):
                return (
                    False,
                    f"Ya existe un movimiento registrado para el gasto {gasto_id}",
                    None,
                )

            # Crear descripción
            descripcion = f"Gasto operativo: {gasto.descripcion[:100]}"
            if hasattr(gasto, "categoria") and gasto.categoria:
                descripcion += f" [{gasto.categoria}]"

            # Obtener forma de pago del gasto
            forma_pago = getattr(gasto, "forma_pago", "EFECTIVO")

            # Crear movimiento
            datos_movimiento = {
                "tipo": "EGRESO",
                "monto": float(gasto.monto),
                "descripcion": descripcion,
                "referencia_tipo": "GASTO",
                "referencia_id": gasto_id,
                "usuario_id": (
                    self._current_usuario.id if self._current_usuario else None
                ),
                "forma_pago": forma_pago,
            }

            return self.registrar_movimiento(datos_movimiento)

        except Exception as e:
            logger.error(f"Error al registrar egreso por gasto {gasto_id}: {e}")
            return False, f"Error interno: {str(e)}", None

    def registrar_ingreso_factura(
        self, factura_id: int
    ) -> Tuple[bool, str, Optional[MovimientoCajaModel]]:
        """
        Registrar ingreso en caja por una factura

        Args:
            factura_id: ID de la factura

        Returns:
            Tuple (éxito, mensaje, movimiento)
        """
        try:
            # Obtener datos de la factura
            factura = FacturaModel.get_by_id(factura_id)
            if not factura:
                return False, f"No se encontró factura con ID {factura_id}", None

            # Verificar si ya existe movimiento para esta factura
            if self._existe_movimiento_para_referencia("FACTURA", factura_id):
                return (
                    False,
                    f"Ya existe un movimiento registrado para la factura {factura_id}",
                    None,
                )

            # Crear descripción
            descripcion = f"Factura {factura.nro_factura}: {factura.razon_social}"
            if hasattr(factura, "concepto") and factura.concepto:
                descripcion += f" - {factura.concepto[:50]}"

            # Obtener forma de pago de la factura
            forma_pago = getattr(factura, "forma_pago", "EFECTIVO")

            # Crear movimiento
            datos_movimiento = {
                "tipo": "INGRESO",
                "monto": float(factura.total),
                "descripcion": descripcion,
                "referencia_tipo": "FACTURA",
                "referencia_id": factura_id,
                "usuario_id": (
                    self._current_usuario.id if self._current_usuario else None
                ),
                "forma_pago": forma_pago,
            }

            return self.registrar_movimiento(datos_movimiento)

        except Exception as e:
            logger.error(f"Error al registrar ingreso por factura {factura_id}: {e}")
            return False, f"Error interno: {str(e)}", None

    # ==================== CONSULTAS Y REPORTES ====================

    def obtener_saldo_actual(self) -> float:
        """
        Obtener saldo actual de caja

        Returns:
            Saldo actual como float
        """
        try:
            return MovimientoCajaModel.obtener_saldo_actual()
        except Exception as e:
            logger.error(f"Error al obtener saldo actual: {e}")
            return 0.0

    def obtener_movimientos_hoy(self) -> List[MovimientoCajaModel]:
        """
        Obtener movimientos de hoy

        Returns:
            Lista de movimientos
        """
        try:
            return MovimientoCajaModel.obtener_movimientos_hoy()
        except Exception as e:
            logger.error(f"Error al obtener movimientos de hoy: {e}")
            return []

    def obtener_movimientos_rango(
        self,
        fecha_inicio: Union[str, date],
        fecha_fin: Union[str, date],
        tipo: Optional[str] = None,
        referencia_tipo: Optional[str] = None,
        usuario_id: Optional[int] = None,
    ) -> List[MovimientoCajaModel]:
        """
        Obtener movimientos en un rango de fechas con filtros opcionales

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            tipo: Tipo de movimiento (INGRESO/EGRESO)
            referencia_tipo: Tipo de referencia
            usuario_id: ID del usuario

        Returns:
            Lista de movimientos
        """
        try:
            # Construir condiciones
            condiciones = []
            params = []

            # Fechas
            condiciones.append("fecha >= ? AND fecha <= ?")
            params.extend([fecha_inicio, fecha_fin])

            # Filtros opcionales
            if tipo:
                condiciones.append("tipo = ?")
                params.append(tipo)

            if referencia_tipo:
                condiciones.append("referencia_tipo = ?")
                params.append(referencia_tipo)

            if usuario_id:
                condiciones.append("usuario_id = ?")
                params.append(usuario_id)

            # Construir query
            where_clause = " AND ".join(condiciones)
            query = f"""
                SELECT * FROM {MovimientoCajaModel.TABLE_NAME} 
                WHERE {where_clause}
                ORDER BY fecha DESC
            """

            results = MovimientoCajaModel.query(query, params)
            return [MovimientoCajaModel(**row) for row in results] if results else []

        except Exception as e:
            logger.error(
                f"Error al obtener movimientos en rango {fecha_inicio} - {fecha_fin}: {e}"
            )
            return []

    def obtener_movimientos_por_referencia(
        self,
        referencia_tipo: str,
        referencia_id: Optional[int] = None,
        limite: int = 100,
    ) -> List[MovimientoCajaModel]:
        """
        Obtener movimientos por tipo de referencia

        Args:
            referencia_tipo: Tipo de referencia
            referencia_id: ID específico de referencia (opcional)
            limite: Límite de resultados

        Returns:
            Lista de movimientos
        """
        try:
            condiciones = ["referencia_tipo = ?"]
            params = [referencia_tipo]

            if referencia_id:
                condiciones.append("referencia_id = ?")
                params.append(referencia_id)

            where_clause = " AND ".join(condiciones)
            query = f"""
                SELECT * FROM {MovimientoCajaModel.TABLE_NAME} 
                WHERE {where_clause}
                ORDER BY fecha DESC
                LIMIT ?
            """

            params.append(limite)
            results = MovimientoCajaModel.query(query, params)
            return [MovimientoCajaModel(**row) for row in results] if results else []

        except Exception as e:
            logger.error(
                f"Error al obtener movimientos por referencia {referencia_tipo}: {e}"
            )
            return []

    def obtener_resumen_diario(
        self, fecha: Optional[Union[str, date]] = None
    ) -> Dict[str, Any]:
        """
        Obtener resumen diario de movimientos

        Args:
            fecha: Fecha (default: hoy)

        Returns:
            Diccionario con resumen
        """
        try:
            if fecha is None:
                fecha = date.today()

            # Convertir a string si es date
            if isinstance(fecha, date):
                fecha_str = fecha.strftime("%Y-%m-%d")
            else:
                fecha_str = fecha

            # Obtener movimientos del día
            movimientos = self.obtener_movimientos_rango(
                f"{fecha_str} 00:00:00", f"{fecha_str} 23:59:59"
            )

            # Calcular totales
            total_ingresos = 0.0
            total_egresos = 0.0
            por_tipo_referencia = {}
            por_forma_pago = {}

            for mov in movimientos:
                if mov.tipo == "INGRESO":
                    total_ingresos += float(mov.monto)
                else:  # EGRESO
                    total_egresos += float(mov.monto)

                # Agrupar por tipo de referencia
                ref_tipo = mov.referencia_tipo or "OTRO"
                if ref_tipo not in por_tipo_referencia:
                    por_tipo_referencia[ref_tipo] = {"ingresos": 0.0, "egresos": 0.0}

                if mov.tipo == "INGRESO":
                    por_tipo_referencia[ref_tipo]["ingresos"] += float(mov.monto)
                else:
                    por_tipo_referencia[ref_tipo]["egresos"] += float(mov.monto)

                # Agrupar por forma de pago
                forma_pago = getattr(mov, "forma_pago", "EFECTIVO") or "EFECTIVO"
                if forma_pago not in por_forma_pago:
                    por_forma_pago[forma_pago] = {"ingresos": 0.0, "egresos": 0.0}

                if mov.tipo == "INGRESO":
                    por_forma_pago[forma_pago]["ingresos"] += float(mov.monto)
                else:
                    por_forma_pago[forma_pago]["egresos"] += float(mov.monto)

            # Calcular saldo del día
            saldo_dia = total_ingresos - total_egresos

            return {
                "fecha": fecha_str,
                "total_movimientos": len(movimientos),
                "total_ingresos": total_ingresos,
                "total_egresos": total_egresos,
                "saldo_dia": saldo_dia,
                "por_tipo_referencia": por_tipo_referencia,
                "por_forma_pago": por_forma_pago,
                "movimientos": [mov.to_dict() for mov in movimientos],
            }

        except Exception as e:
            logger.error(f"Error al obtener resumen diario para {fecha}: {e}")
            return {
                "fecha": fecha.isoformat() if isinstance(fecha, date) else str(fecha),
                "error": str(e),
            }

    def obtener_resumen_mensual(
        self, año: int = None, mes: int = None
    ) -> Dict[str, Any]:
        """
        Obtener resumen mensual de movimientos

        Args:
            año: Año (default: año actual)
            mes: Mes (1-12, default: mes actual)

        Returns:
            Diccionario con resumen mensual
        """
        try:
            if año is None:
                año = datetime.now().year
            if mes is None:
                mes = datetime.now().month

            # Calcular fechas del mes
            fecha_inicio = date(año, mes, 1)
            if mes == 12:
                fecha_fin = date(año + 1, 1, 1) - timedelta(days=1)
            else:
                fecha_fin = date(año, mes + 1, 1) - timedelta(days=1)

            # Obtener movimientos del mes
            movimientos = self.obtener_movimientos_rango(
                fecha_inicio.strftime("%Y-%m-%d"), fecha_fin.strftime("%Y-%m-%d")
            )

            # Calcular totales
            total_ingresos = 0.0
            total_egresos = 0.0
            por_dia = {}

            for mov in movimientos:
                # Determinar día
                if isinstance(mov.fecha, str):
                    try:
                        fecha_mov = datetime.strptime(mov.fecha[:10], "%Y-%m-%d").date()
                        dia = fecha_mov.day
                    except:
                        dia = 1
                elif hasattr(mov.fecha, "day"):
                    dia = mov.fecha.day
                else:
                    dia = 1

                # Inicializar día si no existe
                if dia not in por_dia:
                    por_dia[dia] = {"ingresos": 0.0, "egresos": 0.0, "saldo": 0.0}

                # Acumular
                monto = float(mov.monto)
                if mov.tipo == "INGRESO":
                    total_ingresos += monto
                    por_dia[dia]["ingresos"] += monto
                    por_dia[dia]["saldo"] += monto
                else:  # EGRESO
                    total_egresos += monto
                    por_dia[dia]["egresos"] += monto
                    por_dia[dia]["saldo"] -= monto

            # Calcular saldo del mes
            saldo_mes = total_ingresos - total_egresos

            # Calcular promedio diario
            dias_con_movimientos = len(
                [d for d in por_dia.values() if d["ingresos"] > 0 or d["egresos"] > 0]
            )
            promedio_ingresos_diario = (
                total_ingresos / dias_con_movimientos if dias_con_movimientos > 0 else 0
            )
            promedio_egresos_diario = (
                total_egresos / dias_con_movimientos if dias_con_movimientos > 0 else 0
            )

            return {
                "año": año,
                "mes": mes,
                "mes_nombre": fecha_inicio.strftime("%B"),
                "fecha_inicio": fecha_inicio.strftime("%Y-%m-%d"),
                "fecha_fin": fecha_fin.strftime("%Y-%m-%d"),
                "total_movimientos": len(movimientos),
                "total_ingresos": total_ingresos,
                "total_egresos": total_egresos,
                "saldo_mes": saldo_mes,
                "dias_con_movimientos": dias_con_movimientos,
                "promedio_ingresos_diario": promedio_ingresos_diario,
                "promedio_egresos_diario": promedio_egresos_diario,
                "por_dia": por_dia,
            }

        except Exception as e:
            logger.error(f"Error al obtener resumen mensual {año}-{mes}: {e}")
            return {
                "año": año or datetime.now().year,
                "mes": mes or datetime.now().month,
                "error": str(e),
            }

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtener estadísticas generales de caja

        Returns:
            Diccionario con estadísticas
        """
        try:
            # Saldo actual
            saldo_actual = self.obtener_saldo_actual()

            # Movimientos hoy
            movimientos_hoy = self.obtener_movimientos_hoy()
            total_hoy = len(movimientos_hoy)

            # Total ingresos y egresos hoy
            ingresos_hoy = sum(
                float(m.monto) for m in movimientos_hoy if m.tipo == "INGRESO"
            )
            egresos_hoy = sum(
                float(m.monto) for m in movimientos_hoy if m.tipo == "EGRESO"
            )

            # Resumen del mes actual
            hoy = datetime.now()
            resumen_mes = self.obtener_resumen_mensual(hoy.year, hoy.month)

            # Top formas de pago
            formas_pago = {}
            query = f"""
                SELECT forma_pago, tipo, SUM(monto) as total
                FROM {MovimientoCajaModel.TABLE_NAME}
                WHERE fecha >= date('now', '-30 days')
                GROUP BY forma_pago, tipo
            """
            results = MovimientoCajaModel.query(query)

            if results:
                for row in results:
                    forma_pago = row["forma_pago"] or "EFECTIVO"
                    if forma_pago not in formas_pago:
                        formas_pago[forma_pago] = {"ingresos": 0.0, "egresos": 0.0}

                    if row["tipo"] == "INGRESO":
                        formas_pago[forma_pago]["ingresos"] += float(row["total"])
                    else:
                        formas_pago[forma_pago]["egresos"] += float(row["total"])

            return {
                "saldo_actual": saldo_actual,
                "movimientos_hoy": total_hoy,
                "ingresos_hoy": ingresos_hoy,
                "egresos_hoy": egresos_hoy,
                "resumen_mes": resumen_mes,
                "formas_pago": formas_pago,
                "ultima_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            return {
                "error": str(e),
                "saldo_actual": 0.0,
                "movimientos_hoy": 0,
                "ingresos_hoy": 0.0,
                "egresos_hoy": 0.0,
            }

    def generar_reporte_caja(
        self,
        fecha_inicio: Union[str, date],
        fecha_fin: Union[str, date],
        formato: str = "texto",
        incluir_detalle: bool = True,
    ) -> str:
        """
        Generar reporte de caja

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            formato: 'texto' o 'html'
            incluir_detalle: Incluir detalle de movimientos

        Returns:
            Reporte formateado
        """
        try:
            # Obtener movimientos
            movimientos = self.obtener_movimientos_rango(fecha_inicio, fecha_fin)

            # Obtener resumen del período
            resumen = self.obtener_resumen_diario()  # Para estructura básica

            # Calcular totales
            total_ingresos = sum(
                float(m.monto) for m in movimientos if m.tipo == "INGRESO"
            )
            total_egresos = sum(
                float(m.monto) for m in movimientos if m.tipo == "EGRESO"
            )
            saldo_periodo = total_ingresos - total_egresos

            # Saldo inicial (necesitaríamos la fecha anterior)
            saldo_inicial = 0.0
            if movimientos:
                # Obtener saldo acumulado hasta el día anterior al inicio
                try:
                    fecha_ini_obj = datetime.strptime(fecha_inicio[:10], "%Y-%m-%d")
                    fecha_anterior = (fecha_ini_obj - timedelta(days=1)).strftime(
                        "%Y-%m-%d"
                    )

                    # Consultar saldo acumulado hasta fecha anterior
                    query = f"""
                        SELECT 
                            COALESCE(SUM(CASE WHEN tipo = 'INGRESO' THEN monto ELSE 0 END), 0) -
                            COALESCE(SUM(CASE WHEN tipo = 'EGRESO' THEN monto ELSE 0 END), 0) as saldo
                        FROM {MovimientoCajaModel.TABLE_NAME}
                        WHERE fecha < ?
                    """
                    result = MovimientoCajaModel.query(query, [fecha_inicio])
                    if result and result[0]["saldo"]:
                        saldo_inicial = float(result[0]["saldo"])
                except:
                    pass

            # Calcular saldo final
            saldo_final = saldo_inicial + saldo_periodo

            if formato.lower() == "html":
                return self._generar_reporte_html(
                    movimientos,
                    fecha_inicio,
                    fecha_fin,
                    total_ingresos,
                    total_egresos,
                    saldo_periodo,
                    saldo_inicial,
                    saldo_final,
                    incluir_detalle,
                )
            else:
                return self._generar_reporte_texto(
                    movimientos,
                    fecha_inicio,
                    fecha_fin,
                    total_ingresos,
                    total_egresos,
                    saldo_periodo,
                    saldo_inicial,
                    saldo_final,
                    incluir_detalle,
                )

        except Exception as e:
            logger.error(f"Error al generar reporte de caja: {e}")
            return f"Error al generar reporte: {str(e)}"

    def _generar_reporte_texto(
        self,
        movimientos: List[MovimientoCajaModel],
        fecha_inicio: Union[str, date],
        fecha_fin: Union[str, date],
        total_ingresos: float,
        total_egresos: float,
        saldo_periodo: float,
        saldo_inicial: float,
        saldo_final: float,
        incluir_detalle: bool = True,
    ) -> str:
        """Generar reporte en formato texto"""
        # Formatear fechas
        if isinstance(fecha_inicio, date):
            fecha_ini_str = fecha_inicio.strftime("%d/%m/%Y")
        else:
            fecha_ini_str = fecha_inicio

        if isinstance(fecha_fin, date):
            fecha_fin_str = fecha_fin.strftime("%d/%m/%Y")
        else:
            fecha_fin_str = fecha_fin

        reporte = []
        reporte.append("=" * 80)
        reporte.append("REPORTE DE CAJA".center(80))
        reporte.append("=" * 80)
        reporte.append(f"Período: {fecha_ini_str} al {fecha_fin_str}")
        reporte.append(
            f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        reporte.append(
            f"Generado por: {self._current_usuario.nombre if self._current_usuario else 'Sistema'}"
        )
        reporte.append("-" * 80)
        reporte.append(f"Saldo inicial:     Bs. {saldo_inicial:,.2f}")
        reporte.append(f"Total ingresos:    Bs. {total_ingresos:,.2f}")
        reporte.append(f"Total egresos:     Bs. {total_egresos:,.2f}")
        reporte.append(f"Saldo del período: Bs. {saldo_periodo:,.2f}")
        reporte.append(f"Saldo final:       Bs. {saldo_final:,.2f}")
        reporte.append("-" * 80)
        reporte.append(f"Movimientos registrados: {len(movimientos)}")
        reporte.append("-" * 80)

        if incluir_detalle and movimientos:
            reporte.append("DETALLE DE MOVIMIENTOS:")
            reporte.append("-" * 80)

            for i, mov in enumerate(movimientos, 1):
                tipo_simbolo = "[+]" if mov.tipo == "INGRESO" else "[-]"

                # Formatear fecha
                if isinstance(mov.fecha, str):
                    try:
                        fecha_mov = datetime.strptime(mov.fecha, "%Y-%m-%d %H:%M:%S")
                        fecha_str = fecha_mov.strftime("%d/%m/%Y %H:%M")
                    except:
                        fecha_str = mov.fecha
                else:
                    fecha_str = str(mov.fecha)

                reporte.append(
                    f"{i:3d}. {fecha_str} {tipo_simbolo} Bs. {float(mov.monto):,.2f}"
                )
                reporte.append(f"     {mov.descripcion[:70]}")

                # Información adicional
                info_extra = []
                if mov.referencia_tipo:
                    info_extra.append(
                        f"Ref: {mov.referencia_tipo} #{mov.referencia_id}"
                    )

                if hasattr(mov, "forma_pago") and mov.forma_pago:
                    info_extra.append(f"Forma: {mov.forma_pago}")

                if info_extra:
                    reporte.append(f"     ({', '.join(info_extra)})")

                reporte.append("")
        else:
            reporte.append("Sin movimientos en el período")

        reporte.append("=" * 80)

        return "\n".join(reporte)

    def _generar_reporte_html(
        self,
        movimientos: List[MovimientoCajaModel],
        fecha_inicio: Union[str, date],
        fecha_fin: Union[str, date],
        total_ingresos: float,
        total_egresos: float,
        saldo_periodo: float,
        saldo_inicial: float,
        saldo_final: float,
        incluir_detalle: bool = True,
    ) -> str:
        """Generar reporte en formato HTML"""
        # Formatear fechas
        if isinstance(fecha_inicio, date):
            fecha_ini_str = fecha_inicio.strftime("%d/%m/%Y")
        else:
            fecha_ini_str = fecha_inicio

        if isinstance(fecha_fin, date):
            fecha_fin_str = fecha_fin.strftime("%d/%m/%Y")
        else:
            fecha_fin_str = fecha_fin

        # Estilos CSS
        styles = """
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
            h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            h2 { color: #34495e; margin-top: 30px; }
            .resumen { background-color: #e9ecef; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .resumen-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
            .resumen-item { background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .resumen-item h3 { margin-top: 0; color: #495057; }
            .monto-positivo { color: #28a745; font-weight: bold; font-size: 18px; }
            .monto-negativo { color: #dc3545; font-weight: bold; font-size: 18px; }
            .monto-neutral { color: #007bff; font-weight: bold; font-size: 18px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #34495e; color: white; }
            tr:hover { background-color: #f5f5f5; }
            .ingreso-row { background-color: #d4edda; }
            .egreso-row { background-color: #f8d7da; }
            .no-data { text-align: center; padding: 20px; color: #6c757d; font-style: italic; }
            .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #6c757d; font-size: 12px; }
        </style>
        """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Reporte de Caja - FormaGestPro</title>
            {styles}
        </head>
        <body>
            <div class="header">
                <h1>Reporte de Caja</h1>
                <p><strong>Sistema:</strong> FormaGestPro_MVC</p>
                <p><strong>Período:</strong> {fecha_ini_str} al {fecha_fin_str}</p>
                <p><strong>Generado:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                <p><strong>Usuario:</strong> {self._current_usuario.nombre if self._current_usuario else 'Sistema'}</p>
            </div>
            
            <div class="resumen">
                <h2>Resumen del Período</h2>
                <div class="resumen-grid">
                    <div class="resumen-item">
                        <h3>Saldo Inicial</h3>
                        <p class="monto-neutral">Bs. {saldo_inicial:,.2f}</p>
                    </div>
                    <div class="resumen-item">
                        <h3>Total Ingresos</h3>
                        <p class="monto-positivo">Bs. {total_ingresos:,.2f}</p>
                    </div>
                    <div class="resumen-item">
                        <h3>Total Egresos</h3>
                        <p class="monto-negativo">Bs. {total_egresos:,.2f}</p>
                    </div>
                    <div class="resumen-item">
                        <h3>Saldo del Período</h3>
                        <p class="monto-{'positivo' if saldo_periodo >= 0 else 'negativo'}">Bs. {saldo_periodo:,.2f}</p>
                    </div>
                    <div class="resumen-item">
                        <h3>Saldo Final</h3>
                        <p class="monto-{'positivo' if saldo_final >= 0 else 'negativo'}">Bs. {saldo_final:,.2f}</p>
                    </div>
                    <div class="resumen-item">
                        <h3>Movimientos</h3>
                        <p><strong>{len(movimientos)}</strong> registros</p>
                    </div>
                </div>
            </div>
        """

        if incluir_detalle:
            html += """
            <h2>Detalle de Movimientos</h2>
            """

            if movimientos:
                html += """
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Fecha</th>
                            <th>Tipo</th>
                            <th>Monto</th>
                            <th>Descripción</th>
                            <th>Referencia</th>
                            <th>Forma Pago</th>
                        </tr>
                    </thead>
                    <tbody>
                """

                for i, mov in enumerate(movimientos, 1):
                    clase_fila = (
                        "ingreso-row" if mov.tipo == "INGRESO" else "egreso-row"
                    )
                    clase_monto = (
                        "monto-positivo" if mov.tipo == "INGRESO" else "monto-negativo"
                    )

                    # Formatear fecha
                    if isinstance(mov.fecha, str):
                        try:
                            fecha_mov = datetime.strptime(
                                mov.fecha, "%Y-%m-%d %H:%M:%S"
                            )
                            fecha_str = fecha_mov.strftime("%d/%m/%Y %H:%M")
                        except:
                            fecha_str = mov.fecha
                    else:
                        fecha_str = str(mov.fecha)

                    referencia = ""
                    if mov.referencia_tipo and mov.referencia_id:
                        referencia = f"{mov.referencia_tipo} #{mov.referencia_id}"

                    forma_pago = getattr(mov, "forma_pago", "EFECTIVO") or "EFECTIVO"

                    html += f"""
                    <tr class="{clase_fila}">
                        <td>{i}</td>
                        <td>{fecha_str}</td>
                        <td>{mov.tipo}</td>
                        <td class="{clase_monto}">Bs. {float(mov.monto):,.2f}</td>
                        <td>{mov.descripcion[:50]}{'...' if len(mov.descripcion) > 50 else ''}</td>
                        <td>{referencia}</td>
                        <td>{forma_pago}</td>
                    </tr>
                    """

                html += """
                    </tbody>
                </table>
                """
            else:
                html += """
                <div class="no-data">
                    <p>No hay movimientos en el período seleccionado.</p>
                </div>
                """

        html += f"""
            <div class="footer">
                <p><em>Reporte generado automáticamente por FormaGestPro_MVC - Módulo de Caja</em></p>
                <p><em>Este es un documento oficial para fines de control interno.</em></p>
            </div>
        </body>
        </html>
        """

        return html

    # ==================== MÉTODOS AUXILIARES ====================

    def _validar_datos_movimiento(
        self, datos: Dict[str, Any], es_actualizacion: bool = False
    ) -> List[str]:
        """
        Validar datos del movimiento de caja

        Args:
            datos: Diccionario con datos a validar
            es_actualizacion: Si es una actualización

        Returns:
            Lista de mensajes de error
        """
        errores = []

        # Validar campos requeridos
        campos_requeridos = ["tipo", "monto", "descripcion"]
        for campo in campos_requeridos:
            if campo not in datos or not str(datos.get(campo, "")).strip():
                errores.append(f"El campo '{campo}' es requerido")

        # Validar tipo
        if "tipo" in datos and datos["tipo"]:
            if datos["tipo"] not in ["INGRESO", "EGRESO"]:
                errores.append("Tipo debe ser 'INGRESO' o 'EGRESO'")

        # Validar monto
        if "monto" in datos and datos["monto"]:
            try:
                monto = float(datos["monto"])
                if monto <= 0:
                    errores.append("El monto debe ser mayor a 0")
                if monto > 1000000:  # Límite razonable
                    errores.append("El monto no puede exceder 1,000,000")
            except (ValueError, TypeError):
                errores.append("Monto inválido. Debe ser un número")

        # Validar descripción
        if "descripcion" in datos and datos["descripcion"]:
            descripcion = str(datos["descripcion"]).strip()
            if len(descripcion) < 3:
                errores.append("La descripción debe tener al menos 3 caracteres")
            if len(descripcion) > 200:
                errores.append("La descripción no puede exceder 200 caracteres")

        # Validar referencia_tipo si se proporciona
        if "referencia_tipo" in datos and datos["referencia_tipo"]:
            ref_tipo = datos["referencia_tipo"]
            tipos_validos = [
                "PAGO",
                "GASTO",
                "FACTURA",
                "INGRESO_GENERICO",
                "ANULACION",
                "OTRO",
            ]
            if ref_tipo not in tipos_validos:
                errores.append(
                    f"Tipo de referencia inválido. Válidos: {', '.join(tipos_validos)}"
                )

        # Validar referencia_id si se proporciona referencia_tipo
        if (
            "referencia_tipo" in datos
            and datos["referencia_tipo"]
            and datos["referencia_tipo"] != "OTRO"
        ):
            if "referencia_id" not in datos or not datos["referencia_id"]:
                errores.append(
                    f"ID de referencia requerido para tipo '{datos['referencia_tipo']}'"
                )

        # Validar forma_pago si se proporciona
        if "forma_pago" in datos and datos["forma_pago"]:
            formas_validas = ["EFECTIVO", "TRANSFERENCIA", "TARJETA", "CHEQUE", "OTRO"]
            if datos["forma_pago"] not in formas_validas:
                errores.append(
                    f"Forma de pago inválida. Válidas: {', '.join(formas_validas)}"
                )

        return errores

    def _existe_movimiento_para_referencia(
        self, referencia_tipo: str, referencia_id: int
    ) -> bool:
        """
        Verificar si ya existe movimiento para una referencia

        Args:
            referencia_tipo: Tipo de referencia
            referencia_id: ID de la referencia

        Returns:
            True si ya existe movimiento
        """
        try:
            query = """
                SELECT COUNT(*) as count FROM movimientos_caja 
                WHERE referencia_tipo = ? AND referencia_id = ? AND anulado = 0
            """
            results = MovimientoCajaModel.query(query, [referencia_tipo, referencia_id])
            return results and results[0]["count"] > 0

        except Exception as e:
            logger.error(
                f"Error al verificar movimiento para {referencia_tipo}/{referencia_id}: {e}"
            )
            return False

    def _generar_descripcion_pago(self, pago: PagoModel) -> str:
        """
        Generar descripción para movimiento de pago

        Args:
            pago: Modelo de pago

        Returns:
            Descripción formateada
        """
        try:
            descripcion = f"Pago "

            # Agregar información de matrícula si existe
            if hasattr(pago, "matricula_id") and pago.matricula_id:
                try:
                    from app.models.matricula_model import MatriculaModel
                    from app.models.estudiante_model import EstudianteModel

                    # from app.models.programa_academico_model import ProgramaAcademicoModel

                    # Obtener matrícula
                    matricula = MatriculaModel.get_by_id(pago.matricula_id)
                    if matricula:
                        # Obtener estudiante
                        estudiante = EstudianteModel.get_by_id(matricula.estudiante_id)
                        if estudiante:
                            descripcion += (
                                f"estudiante {estudiante.nombre} {estudiante.apellido}"
                            )

                        # Obtener programa
                        programa = ProgramaAcademicoModel.get_by_id(
                            matricula.programa_id
                        )
                        if programa:
                            descripcion += f" - {programa.nombre}"
                except ImportError:
                    # Si no están disponibles los modelos, usar ID
                    descripcion += f"matrícula #{pago.matricula_id}"

            # Agregar información del concepto si existe
            if hasattr(pago, "concepto") and pago.concepto:
                descripcion += f" - {pago.concepto}"

            return descripcion

        except Exception as e:
            logger.error(f"Error al generar descripción para pago: {e}")
            return f"Pago #{pago.id}"

    # ==================== MÉTODOS DE UTILIDAD ====================

    def exportar_movimientos_csv(
        self,
        fecha_inicio: Union[str, date],
        fecha_fin: Union[str, date],
        ruta_archivo: str,
    ) -> Tuple[bool, str]:
        """
        Exportar movimientos a archivo CSV

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            ruta_archivo: Ruta del archivo CSV

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            import csv

            # Obtener movimientos
            movimientos = self.obtener_movimientos_rango(fecha_inicio, fecha_fin)

            # Preparar datos
            datos = []
            for mov in movimientos:
                fila = {
                    "ID": mov.id,
                    "Fecha": mov.fecha,
                    "Tipo": mov.tipo,
                    "Monto": float(mov.monto),
                    "Descripción": mov.descripcion,
                    "Referencia_Tipo": mov.referencia_tipo or "",
                    "Referencia_ID": mov.referencia_id or "",
                    "Forma_Pago": getattr(mov, "forma_pago", "") or "",
                    "Usuario_ID": mov.usuario_id or "",
                    "Anulado": "SI" if mov.anulado else "NO",
                    "Creado": mov.created_at,
                    "Actualizado": mov.updated_at or "",
                }
                datos.append(fila)

            # Escribir archivo CSV
            with open(ruta_archivo, "w", newline="", encoding="utf-8") as csvfile:
                if datos:
                    fieldnames = datos[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    writer.writerows(datos)

            logger.info(f"Movimientos exportados a {ruta_archivo}")
            return True, f"Movimientos exportados exitosamente a {ruta_archivo}"

        except Exception as e:
            logger.error(f"Error al exportar movimientos a CSV: {e}")
            return False, f"Error al exportar: {str(e)}"

    def realizar_cierre_caja(
        self, fecha: Optional[Union[str, date]] = None
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Realizar cierre de caja para una fecha específica

        Args:
            fecha: Fecha del cierre (default: hoy)

        Returns:
            Tuple (éxito, mensaje, datos_del_cierre)
        """
        try:
            if fecha is None:
                fecha = date.today()

            # Obtener resumen del día
            resumen = self.obtener_resumen_diario(fecha)

            # Verificar si ya existe un cierre para esta fecha
            query = """
                SELECT COUNT(*) as count FROM movimientos_caja 
                WHERE referencia_tipo = 'CIERRE' 
                AND DATE(fecha) = DATE(?)
            """
            fecha_str = fecha if isinstance(fecha, str) else fecha.strftime("%Y-%m-%d")
            results = MovimientoCajaModel.query(query, [fecha_str])

            if results and results[0]["count"] > 0:
                return (
                    False,
                    f"Ya existe un cierre de caja para la fecha {fecha_str}",
                    resumen,
                )

            # Verificar permisos del usuario
            if self._current_usuario and self._current_usuario.rol not in [
                "ADMIN",
                "CONTADOR",
            ]:
                return False, "No tiene permisos para realizar cierre de caja", resumen

            # Crear movimiento de cierre (informativo, sin monto)
            datos_cierre = {
                "tipo": "CIERRE",
                "monto": 0.0,
                "descripcion": f"CIERRE DE CAJA - {fecha_str} - Ingresos: Bs. {resumen.get('total_ingresos', 0):,.2f} - Egresos: Bs. {resumen.get('total_egresos', 0):,.2f}",
                "referencia_tipo": "CIERRE",
                "referencia_id": 0,
                "usuario_id": (
                    self._current_usuario.id if self._current_usuario else None
                ),
                "forma_pago": "EFECTIVO",
            }

            exito, mensaje, movimiento_cierre = self.registrar_movimiento(datos_cierre)

            if exito:
                # Agregar detalles del cierre a los datos de retorno
                resumen["cierre_id"] = movimiento_cierre.id
                resumen["fecha_cierre"] = movimiento_cierre.fecha
                resumen["usuario_cierre"] = (
                    self._current_usuario.nombre if self._current_usuario else "Sistema"
                )

                logger.info(
                    f"Cierre de caja realizado para {fecha_str} por usuario {self._current_usuario.id if self._current_usuario else 'desconocido'}"
                )
                return (
                    True,
                    f"Cierre de caja realizado exitosamente para {fecha_str}",
                    resumen,
                )
            else:
                return False, f"Error al registrar cierre: {mensaje}", resumen

        except Exception as e:
            logger.error(f"Error al realizar cierre de caja: {e}")
            return False, f"Error interno: {str(e)}", {}
