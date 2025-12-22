# app/controllers/pago_controller.py
"""
Controlador para la gestión de pagos en FormaGestPro_MVC
"""

import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any, Union

from app.models.pago_model import PagoModel
from app.models.usuarios_model import UsuarioModel
from app.models.matricula_model import MatriculaModel
from app.models.estudiante_model import EstudianteModel
from app.models.programa_academico_model import ProgramaAcademicoModel
from app.models.movimiento_caja_model import MovimientoCajaModel

logger = logging.getLogger(__name__)

class PagoController:
    """Controlador para la gestión de pagos"""
    def __init__(self, db_path: str = None):
        """
        Inicializar controlador de pagos

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

    def registrar_pago(self, datos: Dict[str, Any]) -> Tuple[bool, str, Optional[PagoModel]]:
        """
        Registrar un nuevo pago

        Args:
            datos: Diccionario con los datos del pago

        Returns:
            Tuple (éxito, mensaje, pago)
        """
        try:
            # Verificar que haya usuario actual
            if not self._current_usuario:
                return False, "No hay usuario autenticado para registrar pago", None

            # Validar datos requeridos
            errores = self._validar_datos_pago(datos)
            if errores:
                return False, "Errores de validación: " + "; ".join(errores), None

            # Agregar usuario actual a los datos
            if 'registrado_por' not in datos:
                datos['registrado_por'] = self._current_usuario.id

            # Agregar fecha si no se proporciona
            if 'fecha_pago' not in datos:
                datos['fecha_pago'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Crear el pago
            pago = PagoModel(**datos)
            pago_id = pago.save()

            if pago_id:
                pago_creado = PagoModel.get_by_id(pago_id)
                mensaje = f"Pago registrado exitosamente (ID: {pago_id})"

                # Registrar movimiento en caja si está confirmado
                if pago_creado.estado == 'CONFIRMADO':
                    self._registrar_movimiento_caja(pago_creado)

                logger.info(f"✅ Pago registrado: Bs. {pago.monto:.2f} para matrícula {pago.matricula_id}")
                return True, mensaje, pago_creado
            else:
                return False, "Error al guardar el pago en la base de datos", None

        except Exception as e:
            logger.error(f"Error al registrar pago: {e}")
            return False, f"Error interno: {str(e)}", None

    def confirmar_pago(self, pago_id: int) -> Tuple[bool, str, Optional[PagoModel]]:
        """
        Confirmar un pago (cambiar estado a CONFIRMADO)

        Args:
            pago_id: ID del pago

        Returns:
            Tuple (éxito, mensaje, pago actualizado)
        """
        try:
            # Verificar permisos del usuario
            if not self._tiene_permisos_caja():
                return False, "No tiene permisos para confirmar pagos", None

            # Obtener pago
            pago = PagoModel.get_by_id(pago_id)
            if not pago:
                return False, f"No se encontró pago con ID {pago_id}", None

            if pago.estado == 'CONFIRMADO':
                return False, "El pago ya está confirmado", None

            if pago.estado == 'ANULADO':
                return False, "No se puede confirmar un pago anulado", None

            # Actualizar estado
            datos_actualizacion = {
                'estado': 'CONFIRMADO',
                'fecha_confirmacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'confirmado_por': self._current_usuario.id if self._current_usuario else None
            }

            for key, value in datos_actualizacion.items():
                if hasattr(pago, key):
                    setattr(pago, key, value)

            if pago.save():
                # Registrar movimiento en caja
                self._registrar_movimiento_caja(pago)

                pago_actualizado = PagoModel.get_by_id(pago_id)
                mensaje = f"Pago confirmado exitosamente"

                logger.info(f"✅ Pago confirmado: {pago_id}")
                return True, mensaje, pago_actualizado
            else:
                return False, "Error al actualizar el pago en la base de datos", None

        except Exception as e:
            logger.error(f"Error al confirmar pago {pago_id}: {e}")
            return False, f"Error interno: {str(e)}", None

    def anular_pago(self, pago_id: int, motivo: Optional[str] = None) -> Tuple[bool, str]:
        """
        Anular un pago

        Args:
            pago_id: ID del pago
            motivo: Motivo de la anulación (opcional)

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            # Verificar permisos del usuario
            if not self._tiene_permisos_caja():
                return False, "No tiene permisos para anular pagos"

            # Obtener pago
            pago = PagoModel.get_by_id(pago_id)
            if not pago:
                return False, f"No se encontró pago con ID {pago_id}"

            if pago.estado == 'ANULADO':
                return False, "El pago ya está anulado"

            # Verificar si hay movimiento de caja registrado
            if pago.estado == 'CONFIRMADO':
                movimiento = self._obtener_movimiento_caja_pago(pago_id)
                if movimiento:
                    return False, "No se puede anular un pago con movimiento de caja registrado. Use reversión de caja."

            # Actualizar estado
            datos_actualizacion = {
                'estado': 'ANULADO',
                'fecha_anulacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'anulado_por': self._current_usuario.id if self._current_usuario else None
            }

            if motivo:
                observaciones = pago.observaciones or ''
                datos_actualizacion['observaciones'] = f"{observaciones}\nANULADO: {motivo}"

            for key, value in datos_actualizacion.items():
                if hasattr(pago, key):
                    setattr(pago, key, value)

            if pago.save():
                logger.info(f"✅ Pago anulado: {pago_id}")
                return True, f"Pago anulado exitosamente"
            else:
                return False, "Error al actualizar el pago en la base de datos"

        except Exception as e:
            logger.error(f"Error al anular pago {pago_id}: {e}")
            return False, f"Error interno: {str(e)}"

    # ==================== GESTIÓN DE CUOTAS ====================

    def generar_cuotas_matricula(
        self,
        matricula_id: int,
        total: float,
        num_cuotas: int,
        fecha_inicio: Union[str, date],
        intervalo_dias: int = 30
    ) -> Tuple[bool, str, List[PagoModel]]:
        """
        Generar cuotas para una matrícula

        Args:
            matricula_id: ID de la matrícula
            total: Monto total a dividir en cuotas
            num_cuotas: Número de cuotas
            fecha_inicio: Fecha de inicio de las cuotas
            intervalo_dias: Días entre cuotas

        Returns:
            Tuple (éxito, mensaje, lista de cuotas)
        """
        try:
            # Verificar matrícula
            matricula = MatriculaModel.get_by_id(matricula_id)
            if not matricula:
                return False, f"No se encontró matrícula con ID {matricula_id}", []

            # Verificar permisos del usuario
            if not self._tiene_permisos_administrativos():
                return False, "No tiene permisos para generar cuotas", []

            # Verificar si ya tiene cuotas generadas
            cuotas_existentes = PagoModel.get_by_matricula(matricula_id)
            if cuotas_existentes:
                # Solo permitir si todas están anuladas
                cuotas_activas = [c for c in cuotas_existentes if c.estado != 'ANULADO']
                if cuotas_activas:
                    return False, f"La matrícula ya tiene {len(cuotas_activas)} cuotas activas", []

            # Convertir fecha de inicio
            if isinstance(fecha_inicio, date):
                fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
            else:
                fecha_inicio_str = fecha_inicio

            # Generar cuotas
            cuotas = []
            fecha_actual = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')

            for i in range(num_cuotas):
                # Calcular fecha de vencimiento
                fecha_vencimiento = fecha_actual + timedelta(days=intervalo_dias * i)

                # Calcular monto de cuota
                monto_cuota = total / num_cuotas

                # Datos de la cuota
                datos_cuota = {
                    'matricula_id': matricula_id,
                    'monto': monto_cuota,
                    'nro_cuota': i + 1,
                    'fecha_pago': None,  # Se pagará cuando se realice
                    'fecha_vencimiento': fecha_vencimiento.strftime('%Y-%m-%d'),
                    'forma_pago': None,
                    'estado': 'PENDIENTE',
                    'concepto': f"Cuota {i + 1}/{num_cuotas}",
                    'registrado_por': self._current_usuario.id if self._current_usuario else None
                }

                # Registrar cuota
                exito, mensaje, cuota = self.registrar_pago(datos_cuota)
                if exito:
                    cuotas.append(cuota)
                else:
                    logger.error(f"Error al generar cuota {i + 1}: {mensaje}")

            logger.info(f"✅ {len(cuotas)} cuotas generadas para matrícula {matricula_id}")
            return True, f"{len(cuotas)} cuotas generadas exitosamente", cuotas

        except Exception as e:
            logger.error(f"Error al generar cuotas para matrícula {matricula_id}: {e}")
            return False, f"Error interno: {str(e)}", []

    def obtener_cuotas_pendientes(
        self,
        matricula_id: Optional[int] = None,
        estudiante_id: Optional[int] = None,
        programa_id: Optional[int] = None,
        vencimiento_inicio: Optional[Union[str, date]] = None,
        vencimiento_fin: Optional[Union[str, date]] = None
    ) -> List[PagoModel]:
        """
        Obtener cuotas pendientes con filtros

        Args:
            matricula_id: Filtrar por matrícula
            estudiante_id: Filtrar por estudiante
            programa_id: Filtrar por programa
            vencimiento_inicio: Filtrar por fecha de vencimiento desde
            vencimiento_fin: Filtrar por fecha de vencimiento hasta

        Returns:
            Lista de cuotas pendientes
        """
        try:
            # Construir condiciones
            condiciones = ["estado = 'PENDIENTE'"]
            params = []

            # Construir JOIN si se necesita
            joins = []

            if estudiante_id:
                joins.append("JOIN matriculas m ON p.matricula_id = m.id")
                condiciones.append("m.estudiante_id = ?")
                params.append(estudiante_id)

            if programa_id:
                if "JOIN matriculas m" not in " ".join(joins):
                    joins.append("JOIN matriculas m ON p.matricula_id = m.id")
                condiciones.append("m.programa_id = ?")
                params.append(programa_id)

            if matricula_id:
                condiciones.append("p.matricula_id = ?")
                params.append(matricula_id)

            # Filtrar por fechas de vencimiento
            if vencimiento_inicio and vencimiento_fin:
                condiciones.append("p.fecha_vencimiento BETWEEN ? AND ?")
                params.extend([vencimiento_inicio, vencimiento_fin])
            elif vencimiento_inicio:
                condiciones.append("p.fecha_vencimiento >= ?")
                params.append(vencimiento_inicio)
            elif vencimiento_fin:
                condiciones.append("p.fecha_vencimiento <= ?")
                params.append(vencimiento_fin)

            # Construir query
            where_clause = " AND ".join(condiciones)
            join_clause = " ".join(joins) if joins else ""

            query = f"""
                SELECT p.* FROM pagos p
                {join_clause}
                WHERE {where_clause}
                ORDER BY p.fecha_vencimiento ASC
            """

            from database import Database
            db = Database()
            results = db.fetch_all(query, params)

            return [PagoModel(**row) for row in results] if results else []

        except Exception as e:
            logger.error(f"Error al obtener cuotas pendientes: {e}")
            return []

    def obtener_cuotas_vencidas(self) -> List[PagoModel]:
        """
        Obtener cuotas vencidas (pendientes con fecha de vencimiento pasada)

        Returns:
            Lista de cuotas vencidas
        """
        try:
            hoy = date.today().isoformat()

            query = """
                SELECT p.* 
                FROM pagos p
                WHERE estado = 'PENDIENTE'
                AND fecha_vencimiento IS NOT NULL
                AND fecha_vencimiento < ?
                ORDER BY fecha_vencimiento ASC
            """

            from database import Database
            db = Database()
            results = db.fetch_all(query, [hoy])

            return [PagoModel(**row) for row in results] if results else []

        except Exception as e:
            logger.error(f"Error al obtener cuotas vencidas: {e}")
            return []

    # ==================== CONSULTAS Y LISTADOS ====================

    def obtener_pagos_matricula(self, matricula_id: int) -> List[PagoModel]:
        """
        Obtener todos los pagos de una matrícula

        Args:
            matricula_id: ID de la matrícula

        Returns:
            Lista de pagos
        """
        try:
            return PagoModel.get_by_matricula(matricula_id)
        except Exception as e:
            logger.error(f"Error al obtener pagos de matrícula {matricula_id}: {e}")
            return []

    def obtener_pagos_por_rango(
        self,
        fecha_inicio: Union[str, date],
        fecha_fin: Union[str, date],
        estado: Optional[str] = None,
        forma_pago: Optional[str] = None
    ) -> List[PagoModel]:
        """
        Obtener pagos en un rango de fechas

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            estado: Filtrar por estado
            forma_pago: Filtrar por forma de pago

        Returns:
            Lista de pagos
        """
        try:
            # Construir condiciones
            condiciones = ["fecha_pago IS NOT NULL"]
            params = []

            # Fechas
            condiciones.append("fecha_pago >= ? AND fecha_pago <= ?")
            params.extend([fecha_inicio, fecha_fin])

            # Filtros opcionales
            if estado:
                condiciones.append("estado = ?")
                params.append(estado)

            if forma_pago:
                condiciones.append("forma_pago = ?")
                params.append(forma_pago)

            # Construir query
            where_clause = " AND ".join(condiciones)
            query = f"""
                SELECT * FROM {PagoModel.TABLE_NAME} 
                WHERE {where_clause}
                ORDER BY fecha_pago DESC
            """

            from database import Database
            db = Database()
            results = db.fetch_all(query, params)

            return [PagoModel(**row) for row in results] if results else []

        except Exception as e:
            logger.error(f"Error al obtener pagos en rango {fecha_inicio} - {fecha_fin}: {e}")
            return []

    def buscar_pagos(
        self,
        termino: str,
        tipo_busqueda: str = 'comprobante',
        limite: int = 50
    ) -> List[PagoModel]:
        """
        Buscar pagos por diferentes criterios

        Args:
            termino: Término de búsqueda
            tipo_busqueda: 'comprobante', 'transaccion', 'estudiante'
            limite: Límite de resultados

        Returns:
            Lista de pagos encontrados
        """
        try:
            if tipo_busqueda == 'comprobante':
                query = f"""
                    SELECT * FROM {PagoModel.TABLE_NAME} 
                    WHERE nro_comprobante LIKE ?
                    ORDER BY fecha_pago DESC
                    LIMIT ?
                """
                params = [f"%{termino}%", limite]

            elif tipo_busqueda == 'transaccion':
                query = f"""
                    SELECT * FROM {PagoModel.TABLE_NAME} 
                    WHERE nro_transaccion LIKE ?
                    ORDER BY fecha_pago DESC
                    LIMIT ?
                """
                params = [f"%{termino}%", limite]

            elif tipo_busqueda == 'estudiante':
                # Necesita JOIN con matrículas y estudiantes
                query = """
                    SELECT p.* 
                    FROM pagos p
                    JOIN matriculas m ON p.matricula_id = m.id
                    JOIN estudiantes e ON m.estudiante_id = e.id
                    WHERE (e.nombre LIKE ? OR e.apellido LIKE ? OR e.cedula LIKE ?)
                    ORDER BY p.fecha_pago DESC
                    LIMIT ?
                """
                termino_like = f"%{termino}%"
                params = [termino_like, termino_like, termino_like, limite]

            else:
                return []

            from database import Database
            db = Database()
            results = db.fetch_all(query, params)

            return [PagoModel(**row) for row in results] if results else []

        except Exception as e:
            logger.error(f"Error al buscar pagos: {e}")
            return []

    # ==================== ESTADÍSTICAS E INFORMES ====================

    def obtener_estadisticas_pagos(
        self,
        fecha_inicio: Optional[Union[str, date]] = None,
        fecha_fin: Optional[Union[str, date]] = None
    ) -> Dict[str, Any]:
        """
        Obtener estadísticas de pagos

        Args:
            fecha_inicio: Fecha de inicio (opcional)
            fecha_fin: Fecha de fin (opcional)

        Returns:
            Diccionario con estadísticas
        """
        try:
            # Si no se especifican fechas, usar el mes actual
            if not fecha_inicio or not fecha_fin:
                hoy = date.today()
                primer_dia = date(hoy.year, hoy.month, 1)
                ultimo_dia = date(hoy.year, hoy.month + 1, 1) - timedelta(days=1) if hoy.month < 12 else date(hoy.year + 1, 1, 1) - timedelta(days=1)

                fecha_inicio = primer_dia.strftime('%Y-%m-%d')
                fecha_fin = ultimo_dia.strftime('%Y-%m-%d')

            # Obtener pagos en el rango
            pagos = self.obtener_pagos_por_rango(fecha_inicio, fecha_fin)

            # Calcular totales
            total_pagos = len(pagos)
            total_monto = sum(float(p.monto) for p in pagos if p.estado == 'CONFIRMADO')

            # Por estado
            por_estado = {}
            for pago in pagos:
                estado = pago.estado
                if estado not in por_estado:
                    por_estado[estado] = {'cantidad': 0, 'monto': 0.0}

                por_estado[estado]['cantidad'] += 1
                if pago.estado == 'CONFIRMADO':
                    por_estado[estado]['monto'] += float(pago.monto)

            # Por forma de pago
            por_forma_pago = {}
            for pago in pagos:
                if pago.estado == 'CONFIRMADO':
                    forma_pago = pago.forma_pago or 'NO_ESPECIFICADA'
                    if forma_pago not in por_forma_pago:
                        por_forma_pago[forma_pago] = {'cantidad': 0, 'monto': 0.0}

                    por_forma_pago[forma_pago]['cantidad'] += 1
                    por_forma_pago[forma_pago]['monto'] += float(pago.monto)

            # Cuotas pendientes
            cuotas_pendientes = len(self.obtener_cuotas_pendientes())
            cuotas_vencidas = len(self.obtener_cuotas_vencidas())

            return {
                'periodo': {
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin
                },
                'totales': {
                    'pagos': total_pagos,
                    'monto': total_monto,
                    'promedio_pago': total_monto / total_pagos if total_pagos > 0 else 0
                },
                'por_estado': por_estado,
                'por_forma_pago': por_forma_pago,
                'pendientes': {
                    'cuotas_pendientes': cuotas_pendientes,
                    'cuotas_vencidas': cuotas_vencidas
                }
            }

        except Exception as e:
            logger.error(f"Error al obtener estadísticas de pagos: {e}")
            return {'error': str(e)}

    def obtener_resumen_matricula(self, matricula_id: int) -> Dict[str, Any]:
        """
        Obtener resumen de pagos de una matrícula

        Args:
            matricula_id: ID de la matrícula

        Returns:
            Diccionario con resumen
        """
        try:
            # Obtener matrícula
            matricula = MatriculaModel.get_by_id(matricula_id)
            if not matricula:
                return {'error': f'Matrícula {matricula_id} no encontrada'}

            # Obtener pagos
            pagos = self.obtener_pagos_matricula(matricula_id)

            # Calcular totales
            pagos_confirmados = [p for p in pagos if p.estado == 'CONFIRMADO']
            total_pagado = sum(float(p.monto) for p in pagos_confirmados)

            # Obtener programa para calcular costo total
            programa = ProgramaAcademicoModel.get_by_id(matricula.programa_id)
            costo_total = 0.0

            if programa:
                costo_total = float(programa.calcular_costo_total())

            # Cuotas
            cuotas = [p for p in pagos if p.nro_cuota]
            cuotas_pendientes = [p for p in cuotas if p.estado == 'PENDIENTE']
            cuotas_vencidas = [p for p in cuotas_pendientes if p.fecha_vencimiento and p.fecha_vencimiento < date.today().isoformat()]

            return {
                'matricula_id': matricula_id,
                'estudiante_id': matricula.estudiante_id,
                'programa_id': matricula.programa_id,
                'totales': {
                    'costo_total': costo_total,
                    'pagado': total_pagado,
                    'pendiente': costo_total - total_pagado,
                    'porcentaje_pagado': (total_pagado / costo_total * 100) if costo_total > 0 else 0
                },
                'pagos': {
                    'total': len(pagos),
                    'confirmados': len(pagos_confirmados),
                    'pendientes': len([p for p in pagos if p.estado == 'PENDIENTE']),
                    'anulados': len([p for p in pagos if p.estado == 'ANULADO'])
                },
                'cuotas': {
                    'total': len(cuotas),
                    'pagadas': len([c for c in cuotas if c.estado == 'CONFIRMADO']),
                    'pendientes': len(cuotas_pendientes),
                    'vencidas': len(cuotas_vencidas)
                },
                'detalle_pagos': [{
                    'id': p.id,
                    'nro_cuota': p.nro_cuota,
                    'monto': float(p.monto),
                    'estado': p.estado,
                    'fecha_pago': p.fecha_pago,
                    'forma_pago': p.forma_pago,
                    'nro_comprobante': p.nro_comprobante
                } for p in pagos]
            }

        except Exception as e:
            logger.error(f"Error al obtener resumen de matrícula {matricula_id}: {e}")
            return {'error': str(e)}

    def generar_reporte_pagos(
        self,
        fecha_inicio: Union[str, date],
        fecha_fin: Union[str, date],
        formato: str = 'texto',
        detalles_completos: bool = False
    ) -> str:
        """
        Generar reporte de pagos

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            formato: 'texto' o 'html'
            detalles_completos: Incluir detalles completos de cada pago

        Returns:
            Reporte formateado
        """
        try:
            # Obtener pagos
            pagos = self.obtener_pagos_por_rango(fecha_inicio, fecha_fin)

            # Obtener estadísticas
            estadisticas = self.obtener_estadisticas_pagos(fecha_inicio, fecha_fin)

            if formato.lower() == 'html':
                return self._generar_reporte_html(pagos, estadisticas, fecha_inicio, fecha_fin, detalles_completos)
            else:
                return self._generar_reporte_texto(pagos, estadisticas, fecha_inicio, fecha_fin, detalles_completos)

        except Exception as e:
            logger.error(f"Error al generar reporte de pagos: {e}")
            return f"Error al generar reporte: {str(e)}"

    def _generar_reporte_texto(
        self,
        pagos: List[PagoModel],
        estadisticas: Dict[str, Any],
        fecha_inicio: Union[str, date],
        fecha_fin: Union[str, date],
        detalles_completos: bool = False
    ) -> str:
        """Generar reporte en formato texto"""
        # Formatear fechas
        if isinstance(fecha_inicio, date):
            fecha_ini_str = fecha_inicio.strftime('%d/%m/%Y')
        else:
            fecha_ini_str = fecha_inicio

        if isinstance(fecha_fin, date):
            fecha_fin_str = fecha_fin.strftime('%d/%m/%Y')
        else:
            fecha_fin_str = fecha_fin

        reporte = []
        reporte.append("=" * 80)
        reporte.append("REPORTE DE PAGOS".center(80))
        reporte.append("=" * 80)
        reporte.append(f"Período: {fecha_ini_str} al {fecha_fin_str}")
        reporte.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        reporte.append(f"Generado por: {self._current_usuario.nombre if self._current_usuario else 'Sistema'}")
        reporte.append("-" * 80)

        # Estadísticas
        if 'totales' in estadisticas:
            reporte.append("ESTADÍSTICAS DEL PERÍODO:")
            reporte.append(f"  Total pagos registrados: {estadisticas['totales']['pagos']}")
            reporte.append(f"  Monto total: Bs. {estadisticas['totales']['monto']:,.2f}")
            reporte.append(f"  Promedio por pago: Bs. {estadisticas['totales']['promedio_pago']:,.2f}")

            if 'pendientes' in estadisticas:
                reporte.append(f"  Cuotas pendientes: {estadisticas['pendientes']['cuotas_pendientes']}")
                reporte.append(f"  Cuotas vencidas: {estadisticas['pendientes']['cuotas_vencidas']}")

        reporte.append("-" * 80)

        # Detalle por estado
        if 'por_estado' in estadisticas and estadisticas['por_estado']:
            reporte.append("PAGOS POR ESTADO:")
            for estado, datos in estadisticas['por_estado'].items():
                monto_str = f" - Bs. {datos['monto']:,.2f}" if datos['monto'] > 0 else ""
                reporte.append(f"  {estado}: {datos['cantidad']} pagos{monto_str}")

        # Detalle por forma de pago
        if 'por_forma_pago' in estadisticas and estadisticas['por_forma_pago']:
            reporte.append("PAGOS POR FORMA DE PAGO:")
            for forma_pago, datos in estadisticas['por_forma_pago'].items():
                if datos['cantidad'] > 0:
                    reporte.append(f"  {forma_pago}: {datos['cantidad']} pagos - Bs. {datos['monto']:,.2f}")

        reporte.append("-" * 80)

        # Listado de pagos
        if detalles_completos and pagos:
            reporte.append(f"DETALLE DE PAGOS ({len(pagos)} registros):")
            reporte.append("-" * 80)

            for i, pago in enumerate(pagos, 1):
                reporte.append(f"{i:3d}. ID: {pago.id}")
                reporte.append(f"     Matrícula: {pago.matricula_id}")

                if pago.nro_cuota:
                    reporte.append(f"     Cuota: {pago.nro_cuota}")

                reporte.append(f"     Monto: Bs. {float(pago.monto):,.2f}")
                reporte.append(f"     Estado: {pago.estado}")
                reporte.append(f"     Fecha: {pago.fecha_pago or 'No pagado'}")

                if pago.forma_pago:
                    reporte.append(f"     Forma: {pago.forma_pago}")

                if pago.nro_comprobante:
                    reporte.append(f"     Comprobante: {pago.nro_comprobante}")

                if pago.observaciones:
                    reporte.append(f"     Observaciones: {pago.observaciones[:50]}...")

                reporte.append("")
        elif pagos:
            reporte.append(f"Total de pagos en el período: {len(pagos)}")

        reporte.append("=" * 80)

        return "\n".join(reporte)

    def _generar_reporte_html(
        self,
        pagos: List[PagoModel],
        estadisticas: Dict[str, Any],
        fecha_inicio: Union[str, date],
        fecha_fin: Union[str, date],
        detalles_completos: bool = False
    ) -> str:
        """Generar reporte en formato HTML"""
        # Formatear fechas
        if isinstance(fecha_inicio, date):
            fecha_ini_str = fecha_inicio.strftime('%d/%m/%Y')
        else:
            fecha_ini_str = fecha_inicio

        if isinstance(fecha_fin, date):
            fecha_fin_str = fecha_fin.strftime('%d/%m/%Y')
        else:
            fecha_fin_str = fecha_fin

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Reporte de Pagos - FormaGestPro</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                h1, h2, h3 {{ color: #2c3e50; }}
                .section {{ margin-bottom: 30px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
                .stat-card {{ background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }}
                .stat-value {{ font-size: 24px; font-weight: bold; margin: 10px 0; }}
                .stat-label {{ color: #6c757d; font-size: 14px; }}
                .estado-confirmado {{ color: #28a745; font-weight: bold; }}
                .estado-pendiente {{ color: #ffc107; font-weight: bold; }}
                .estado-anulado {{ color: #dc3545; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f8f9fa; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #6c757d; font-size: 12px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Reporte de Pagos</h1>
                <p><strong>Sistema:</strong> FormaGestPro_MVC</p>
                <p><strong>Período:</strong> {fecha_ini_str} al {fecha_fin_str}</p>
                <p><strong>Generado:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                <p><strong>Usuario:</strong> {self._current_usuario.nombre if self._current_usuario else 'Sistema'}</p>
            </div>

            <div class="section">
                <h2>Estadísticas del Período</h2>
                <div class="stats-grid">
        """

        # Tarjetas de estadísticas
        if 'totales' in estadisticas:
            stats = estadisticas['totales']

            html += f"""
                    <div class="stat-card">
                        <div class="stat-value">{stats['pagos']}</div>
                        <div class="stat-label">Pagos Registrados</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">Bs. {stats['monto']:,.2f}</div>
                        <div class="stat-label">Monto Total</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">Bs. {stats['promedio_pago']:,.2f}</div>
                        <div class="stat-label">Promedio por Pago</div>
                    </div>
            """

        if 'pendientes' in estadisticas:
            pendientes = estadisticas['pendientes']

            html += f"""
                    <div class="stat-card">
                        <div class="stat-value">{pendientes['cuotas_pendientes']}</div>
                        <div class="stat-label">Cuotas Pendientes</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{pendientes['cuotas_vencidas']}</div>
                        <div class="stat-label">Cuotas Vencidas</div>
                    </div>
            """

        html += """
                </div>
            </div>
        """

        # Tablas de resumen
        if 'por_estado' in estadisticas and estadisticas['por_estado']:
            html += """
            <div class="section">
                <h3>Pagos por Estado</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Estado</th>
                            <th>Cantidad</th>
                            <th>Monto Total</th>
                        </tr>
                    </thead>
                    <tbody>
            """

            for estado, datos in estadisticas['por_estado'].items():
                html += f"""
                    <tr>
                        <td><span class="estado-{estado.lower()}">{estado}</span></td>
                        <td>{datos['cantidad']}</td>
                        <td>Bs. {datos['monto']:,.2f}</td>
                    </tr>
                """

            html += """
                    </tbody>
                </table>
            </div>
            """

        if 'por_forma_pago' in estadisticas and estadisticas['por_forma_pago']:
            html += """
            <div class="section">
                <h3>Pagos por Forma de Pago</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Forma de Pago</th>
                            <th>Cantidad</th>
                            <th>Monto Total</th>
                        </tr>
                    </thead>
                    <tbody>
            """

            for forma_pago, datos in estadisticas['por_forma_pago'].items():
                if datos['cantidad'] > 0:
                    html += f"""
                    <tr>
                        <td>{forma_pago}</td>
                        <td>{datos['cantidad']}</td>
                        <td>Bs. {datos['monto']:,.2f}</td>
                    </tr>
                    """

            html += """
                    </tbody>
                </table>
            </div>
            """

        # Tabla detallada de pagos
        if detalles_completos and pagos:
            html += f"""
            <div class="section">
                <h2>Detalle de Pagos ({len(pagos)} registros)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>ID</th>
                            <th>Matrícula</th>
                            <th>Cuota</th>
                            <th>Monto</th>
                            <th>Estado</th>
                            <th>Fecha</th>
                            <th>Forma Pago</th>
                            <th>Comprobante</th>
                        </tr>
                    </thead>
                    <tbody>
            """

            for i, pago in enumerate(pagos, 1):
                html += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{pago.id}</td>
                        <td>{pago.matricula_id}</td>
                        <td>{pago.nro_cuota or '-'}</td>
                        <td>Bs. {float(pago.monto):,.2f}</td>
                        <td><span class="estado-{pago.estado.lower()}">{pago.estado}</span></td>
                        <td>{pago.fecha_pago or 'No pagado'}</td>
                        <td>{pago.forma_pago or '-'}</td>
                        <td>{pago.nro_comprobante or '-'}</td>
                    </tr>
                """

            html += """
                    </tbody>
                </table>
            </div>
            """

        html += f"""
            <div class="footer">
                <p><em>Reporte generado automáticamente por FormaGestPro_MVC - Módulo de Pagos</em></p>
                <p><em>Este es un documento oficial para fines de control interno.</em></p>
            </div>
        </body>
        </html>
        """

        return html

    # ==================== MÉTODOS AUXILIARES ====================

    def _validar_datos_pago(self, datos: Dict[str, Any]) -> List[str]:
        """
        Validar datos del pago

        Args:
            datos: Diccionario con datos a validar

        Returns:
            Lista de mensajes de error
        """
        errores = []

        # Validar campos requeridos
        campos_requeridos = ['matricula_id', 'monto']
        for campo in campos_requeridos:
            if campo not in datos or datos.get(campo) is None:
                errores.append(f"El campo '{campo}' es requerido")

        # Validar matrícula
        if 'matricula_id' in datos and datos['matricula_id']:
            matricula = MatriculaModel.get_by_id(datos['matricula_id'])
            if not matricula:
                errores.append(f"La matrícula {datos['matricula_id']} no existe")

        # Validar monto
        if 'monto' in datos and datos['monto']:
            try:
                monto = float(datos['monto'])
                if monto <= 0:
                    errores.append("El monto debe ser mayor a 0")
                if monto > 100000:  # Límite razonable
                    errores.append("El monto no puede exceder 100,000")
            except (ValueError, TypeError):
                errores.append("Monto inválido. Debe ser un número")

        # Validar estado
        if 'estado' in datos and datos['estado']:
            estados_validos = ['PENDIENTE', 'CONFIRMADO', 'ANULADO']
            if datos['estado'] not in estados_validos:
                errores.append(f"Estado inválido. Válidos: {', '.join(estados_validos)}")

        # Validar forma de pago si se proporciona
        if 'forma_pago' in datos and datos['forma_pago']:
            formas_validas = ['EFECTIVO', 'TRANSFERENCIA', 'TARJETA', 'DEPOSITO', 'CHEQUE', 'OTRO']
            if datos['forma_pago'] not in formas_validas:
                errores.append(f"Forma de pago inválida. Válidas: {', '.join(formas_validas)}")

        # Validar número de cuota
        if 'nro_cuota' in datos and datos['nro_cuota']:
            try:
                nro_cuota = int(datos['nro_cuota'])
                if nro_cuota <= 0:
                    errores.append("El número de cuota debe ser mayor a 0")
                if nro_cuota > 100:  # Límite razonable
                    errores.append("El número de cuota no puede exceder 100")
            except (ValueError, TypeError):
                errores.append("Número de cuota inválido. Debe ser un número entero")

        # Validar fecha de vencimiento si se proporciona
        if 'fecha_vencimiento' in datos and datos['fecha_vencimiento']:
            try:
                datetime.strptime(datos['fecha_vencimiento'], '%Y-%m-%d')
            except ValueError:
                errores.append("Fecha de vencimiento inválida. Formato debe ser YYYY-MM-DD")

        return errores

    def _registrar_movimiento_caja(self, pago: PagoModel) -> bool:
        """
        Registrar movimiento de caja para un pago confirmado

        Args:
            pago: Modelo de pago

        Returns:
            True si se registró correctamente
        """
        try:
            # Verificar si ya existe movimiento
            from .movimiento_caja_controller import MovimientoCajaController
            caja_controller = MovimientoCajaController()
            caja_controller.current_usuario = self._current_usuario

            exito, mensaje, movimiento = caja_controller.registrar_ingreso_pago(pago.id)

            if exito:
                logger.info(f"Movimiento de caja registrado para pago {pago.id}")
                return True
            else:
                logger.error(f"Error al registrar movimiento de caja para pago {pago.id}: {mensaje}")
                return False

        except Exception as e:
            logger.error(f"Error al registrar movimiento de caja para pago {pago.id}: {e}")
            return False

    def _obtener_movimiento_caja_pago(self, pago_id: int) -> Optional[MovimientoCajaModel]:
        """
        Obtener movimiento de caja asociado a un pago

        Args:
            pago_id: ID del pago

        Returns:
            Modelo de movimiento de caja o None
        """
        try:
            from .movimiento_caja_controller import MovimientoCajaController
            caja_controller = MovimientoCajaController()

            movimientos = caja_controller.obtener_movimientos_por_referencia('PAGO', pago_id)
            return movimientos[0] if movimientos else None

        except Exception as e:
            logger.error(f"Error al obtener movimiento de caja para pago {pago_id}: {e}")
            return None

    def _tiene_permisos_caja(self) -> bool:
        """Verificar si el usuario tiene permisos para operaciones de caja"""
        if not self._current_usuario:
            return False

        roles_permitidos = ['ADMIN', 'CONTADOR', 'CAJERO']
        return self._current_usuario.rol in roles_permitidos

    def _tiene_permisos_administrativos(self) -> bool:
        """Verificar si el usuario tiene permisos administrativos"""
        if not self._current_usuario:
            return False

        roles_permitidos = ['ADMIN', 'DIRECTOR', 'COORDINADOR']
        return self._current_usuario.rol in roles_permitidos

    # ==================== MÉTODOS DE UTILIDAD ====================

    def exportar_pagos_csv(
        self,
        fecha_inicio: Union[str, date],
        fecha_fin: Union[str, date],
        ruta_archivo: str
    ) -> Tuple[bool, str]:
        """
        Exportar pagos a archivo CSV

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            ruta_archivo: Ruta del archivo CSV

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            import csv

            # Obtener pagos
            pagos = self.obtener_pagos_por_rango(fecha_inicio, fecha_fin)

            # Preparar datos
            datos = []
            for pago in pagos:
                fila = {
                    'ID': pago.id,
                    'Matricula_ID': pago.matricula_id,
                    'Numero_Cuota': pago.nro_cuota or '',
                    'Monto': float(pago.monto),
                    'Estado': pago.estado,
                    'Fecha_Pago': pago.fecha_pago or '',
                    'Fecha_Vencimiento': getattr(pago, 'fecha_vencimiento', '') or '',
                    'Forma_Pago': pago.forma_pago or '',
                    'Numero_Comprobante': pago.nro_comprobante or '',
                    'Numero_Transaccion': pago.nro_transaccion or '',
                    'Observaciones': pago.observaciones or '',
                    'Concepto': getattr(pago, 'concepto', '') or '',
                    'Registrado_Por': pago.registrado_por or '',
                    'Fecha_Registro': getattr(pago, 'fecha_registro', '') or '',
                    'Confirmado_Por': getattr(pago, 'confirmado_por', '') or '',
                    'Fecha_Confirmacion': getattr(pago, 'fecha_confirmacion', '') or ''
                }
                datos.append(fila)

            # Escribir archivo CSV
            with open(ruta_archivo, 'w', newline='', encoding='utf-8') as csvfile:
                if datos:
                    fieldnames = datos[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    writer.writerows(datos)

            logger.info(f"Pagos exportados a {ruta_archivo}")
            return True, f"Pagos exportados exitosamente a {ruta_archivo}"

        except Exception as e:
            logger.error(f"Error al exportar pagos a CSV: {e}")
            return False, f"Error al exportar: {str(e)}"