# app/controllers/facturas_controller.py
"""
Controlador para la gestión de facturas en FormaGestPro_MVC
"""

import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any, Union

from app.models.facturas_model import FacturaModel
from app.models.usuarios_model import UsuarioModel
from app.models.movimiento_caja_model import MovimientoCajaModel
from app.models.facturas_model import FacturaModel

logger = logging.getLogger(__name__)

class FacturaController:
    """Controlador para la gestión de facturas"""
    def __init__(self, db_path: str = None):
        """
        Inicializar controlador de facturas

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

    def crear_factura(self, datos: Dict[str, Any]) -> Tuple[bool, str, Optional[FacturaModel]]:
        """
        Crear una nueva factura

        Args:
            datos: Diccionario con los datos de la factura

        Returns:
            Tuple (éxito, mensaje, factura)
        """
        try:
            # Verificar permisos del usuario
            if not self._tiene_permisos_facturacion():
                return False, "No tiene permisos para crear facturas", None

            # Validar datos
            valido, errores = self._validar_datos_factura(datos)
            if not valido:
                return False, "Errores de validación: " + "; ".join(errores), None

            # Generar número de factura si no se proporciona
            if 'nro_factura' not in datos or not datos['nro_factura']:
                prefijo = datos.get('prefijo_factura', 'FAC-')
                datos['nro_factura'] = FacturaModel.get_ultimo_numero(prefijo)

            # Verificar que el número de factura no exista
            if 'nro_factura' in datos:
                factura_existente = FacturaModel.get_by_nro_factura(datos['nro_factura'])
                if factura_existente:
                    return False, f"El número de factura '{datos['nro_factura']}' ya está en uso", None

            # Calcular totales si no se proporcionan
            if 'subtotal' in datos and datos['subtotal']:
                subtotal = Decimal(str(datos['subtotal']))
                aplicar_iva = datos.get('aplicar_iva', True)
                aplicar_it = datos.get('aplicar_it', False)

                totales = FacturaModel.calcular_totales(
                    subtotal=subtotal,
                    aplicar_iva=aplicar_iva,
                    aplicar_it=aplicar_it
                )

                datos['iva'] = float(totales['iva'])
                datos['it'] = float(totales['it'])
                datos['total'] = float(totales['total'])

            # Agregar fecha actual si no se proporciona
            if 'fecha_emision' not in datos or not datos['fecha_emision']:
                datos['fecha_emision'] = datetime.now().strftime('%Y-%m-%d')

            # Agregar estado inicial
            if 'estado' not in datos:
                datos['estado'] = FacturaModel.ESTADO_EMITIDA

            # Crear la factura
            factura = FacturaModel(**datos)
            factura_id = factura.save()

            if factura_id:
                factura_creada = FacturaModel.get_by_id(factura_id)
                mensaje = f"Factura creada exitosamente (N°: {factura.nro_factura})"

                # Registrar movimiento en caja automáticamente
                self._registrar_movimiento_caja_factura(factura_creada)

                logger.info(f"✅ Factura creada: {factura.nro_factura} - Cliente: {factura.razon_social}")
                return True, mensaje, factura_creada
            else:
                return False, "Error al guardar la factura en la base de datos", None

        except Exception as e:
            logger.error(f"Error al crear factura: {e}")
            return False, f"Error interno: {str(e)}", None

    def actualizar_factura(self, factura_id: int, datos: Dict[str, Any]) -> Tuple[bool, str, Optional[FacturaModel]]:
        """
        Actualizar una factura existente

        Args:
            factura_id: ID de la factura a actualizar
            datos: Diccionario con los datos a actualizar

        Returns:
            Tuple (éxito, mensaje, factura actualizada)
        """
        try:
            # Verificar permisos del usuario
            if not self._tiene_permisos_facturacion():
                return False, "No tiene permisos para actualizar facturas", None

            # Obtener factura existente
            factura = FacturaModel.get_by_id(factura_id)
            if not factura:
                return False, f"No se encontró factura con ID {factura_id}", None

            # Verificar que no esté anulada
            if factura.estado == FacturaModel.ESTADO_ANULADA:
                return False, "No se puede actualizar una factura anulada", None

            # Verificar que no esté exportada al SIAT
            if factura.exportada_siat:
                return False, "No se puede actualizar una factura exportada al SIAT", None

            # Verificar que no se modifique el número de factura a uno existente
            if 'nro_factura' in datos and datos['nro_factura'] != factura.nro_factura:
                factura_existente = FacturaModel.get_by_nro_factura(datos['nro_factura'])
                if factura_existente and factura_existente.id != factura_id:
                    return False, f"El número de factura '{datos['nro_factura']}' ya está en uso", None

            # Validar datos
            datos_completos = factura.to_dict()
            datos_completos.update(datos)
            valido, errores = self._validar_datos_factura(datos_completos, es_actualizacion=True)
            if not valido:
                return False, "Errores de validación: " + "; ".join(errores), None

            # Actualizar factura
            for key, value in datos.items():
                if hasattr(factura, key):
                    setattr(factura, key, value)

            if factura.save():
                factura_actualizada = FacturaModel.get_by_id(factura_id)
                mensaje = f"Factura actualizada exitosamente"

                logger.info(f"✅ Factura actualizada: {factura.nro_factura}")
                return True, mensaje, factura_actualizada
            else:
                return False, "Error al actualizar la factura en la base de datos", None

        except Exception as e:
            logger.error(f"Error al actualizar factura {factura_id}: {e}")
            return False, f"Error interno: {str(e)}", None

    def anular_factura(self, factura_id: int, motivo: Optional[str] = None) -> Tuple[bool, str]:
        """
        Anular una factura

        Args:
            factura_id: ID de la factura
            motivo: Motivo de anulación (opcional)

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            # Verificar permisos del usuario
            if not self._tiene_permisos_facturacion():
                return False, "No tiene permisos para anular facturas"

            # Obtener factura
            factura = FacturaModel.get_by_id(factura_id)
            if not factura:
                return False, f"No se encontró factura con ID {factura_id}"

            # Intentar anular
            exito, mensaje = factura.anular(motivo)

            if exito:
                # Registrar movimiento de reversión en caja
                self._registrar_movimiento_reversion_factura(factura)

                logger.info(f"✅ Factura anulada: {factura.nro_factura}")
                return True, mensaje
            else:
                return False, mensaje

        except Exception as e:
            logger.error(f"Error al anular factura {factura_id}: {e}")
            return False, f"Error interno: {str(e)}"

    def obtener_factura(self, factura_id: int) -> Optional[FacturaModel]:
        """
        Obtener una factura por ID

        Args:
            factura_id: ID de la factura

        Returns:
            Modelo de factura o None
        """
        try:
            return FacturaModel.get_by_id(factura_id)
        except Exception as e:
            logger.error(f"Error al obtener factura {factura_id}: {e}")
            return None

    def obtener_factura_por_numero(self, nro_factura: str) -> Optional[FacturaModel]:
        """
        Obtener una factura por número

        Args:
            nro_factura: Número de factura

        Returns:
            Modelo de factura o None
        """
        try:
            return FacturaModel.get_by_nro_factura(nro_factura)
        except Exception as e:
            logger.error(f"Error al obtener factura {nro_factura}: {e}")
            return None

    # ==================== CONSULTAS Y LISTADOS ====================

    def obtener_todas(
        self,
        estado: Optional[str] = None,
        fecha_inicio: Optional[Union[str, date]] = None,
        fecha_fin: Optional[Union[str, date]] = None,
        tipo_documento: Optional[str] = None,
        exportada_siat: Optional[bool] = None,
        limite: int = 100,
        offset: int = 0
    ) -> List[FacturaModel]:
        """
        Obtener todas las facturas con filtros

        Args:
            estado: Filtrar por estado
            fecha_inicio: Filtrar por fecha de emisión desde
            fecha_fin: Filtrar por fecha de emisión hasta
            tipo_documento: Filtrar por tipo de documento
            exportada_siat: Filtrar por exportación al SIAT
            limite: Límite de resultados
            offset: Desplazamiento para paginación

        Returns:
            Lista de facturas
        """
        try:
            # Construir condiciones
            condiciones = []
            params = []

            if estado:
                condiciones.append("estado = ?")
                params.append(estado)

            if tipo_documento:
                condiciones.append("tipo_documento = ?")
                params.append(tipo_documento)

            if exportada_siat is not None:
                condiciones.append("exportada_siat = ?")
                params.append(1 if exportada_siat else 0)

            if fecha_inicio and fecha_fin:
                condiciones.append("fecha_emision BETWEEN ? AND ?")
                params.extend([fecha_inicio, fecha_fin])
            elif fecha_inicio:
                condiciones.append("fecha_emision >= ?")
                params.append(fecha_inicio)
            elif fecha_fin:
                condiciones.append("fecha_emision <= ?")
                params.append(fecha_fin)

            # Construir query
            where_clause = " AND ".join(condiciones) if condiciones else "1=1"
            query = f"""
                SELECT * FROM {FacturaModel.TABLE_NAME} 
                WHERE {where_clause}
                ORDER BY fecha_emision DESC, nro_factura DESC
                LIMIT ? OFFSET ?
            """

            params.extend([limite, offset])
            results = FacturaModel.query(query, params)

            return [FacturaModel(**row) for row in results] if results else []

        except Exception as e:
            logger.error(f"Error al obtener facturas: {e}")
            return []

    def buscar_facturas(
        self,
        termino: str,
        campo: str = 'razon_social',
        limite: int = 50
    ) -> List[FacturaModel]:
        """
        Buscar facturas

        Args:
            termino: Término de búsqueda
            campo: Campo a buscar (razon_social, nit_ci, nro_factura, concepto)
            limite: Límite de resultados

        Returns:
            Lista de facturas encontradas
        """
        try:
            if campo == 'razon_social':
                return FacturaModel.get_by_cliente(razon_social=termino, limit=limite)
            elif campo == 'nit_ci':
                return FacturaModel.get_by_cliente(nit_ci=termino, limit=limite)
            elif campo == 'nro_factura':
                factura = FacturaModel.get_by_nro_factura(termino)
                return [factura] if factura else []
            elif campo == 'concepto':
                query = f"""
                    SELECT * FROM {FacturaModel.TABLE_NAME} 
                    WHERE concepto LIKE ?
                    ORDER BY fecha_emision DESC
                    LIMIT ?
                """
                results = FacturaModel.query(query, [f"%{termino}%", limite])
                return [FacturaModel(**row) for row in results] if results else []
            else:
                # Búsqueda general
                query = f"""
                    SELECT * FROM {FacturaModel.TABLE_NAME} 
                    WHERE (razon_social LIKE ? OR nit_ci LIKE ? OR nro_factura LIKE ? OR concepto LIKE ?)
                    ORDER BY fecha_emision DESC
                    LIMIT ?
                """
                termino_like = f"%{termino}%"
                results = FacturaModel.query(query, [termino_like, termino_like, termino_like, termino_like, limite])
                return [FacturaModel(**row) for row in results] if results else []

        except Exception as e:
            logger.error(f"Error al buscar facturas: {e}")
            return []

    def obtener_facturas_por_cliente(
        self,
        nit_ci: Optional[str] = None,
        razon_social: Optional[str] = None
    ) -> List[FacturaModel]:
        """
        Obtener facturas por cliente

        Args:
            nit_ci: NIT/CI del cliente
            razon_social: Razón social del cliente

        Returns:
            Lista de facturas del cliente
        """
        try:
            return FacturaModel.get_by_cliente(nit_ci=nit_ci, razon_social=razon_social)
        except Exception as e:
            logger.error(f"Error al obtener facturas por cliente: {e}")
            return []

    def obtener_facturas_hoy(self) -> List[FacturaModel]:
        """
        Obtener facturas emitidas hoy

        Returns:
            Lista de facturas de hoy
        """
        try:
            hoy = date.today().isoformat()
            return self.obtener_todas(fecha_inicio=hoy, fecha_fin=hoy)
        except Exception as e:
            logger.error(f"Error al obtener facturas de hoy: {e}")
            return []

    # ==================== GESTIÓN DE ESTADO ====================

    def marcar_como_pagada(self, factura_id: int) -> Tuple[bool, str, Optional[FacturaModel]]:
        """
        Marcar factura como pagada

        Args:
            factura_id: ID de la factura

        Returns:
            Tuple (éxito, mensaje, factura actualizada)
        """
        try:
            # Verificar permisos del usuario
            if not self._tiene_permisos_facturacion():
                return False, "No tiene permisos para marcar facturas como pagadas", None

            factura = FacturaModel.get_by_id(factura_id)
            if not factura:
                return False, f"No se encontró factura con ID {factura_id}", None

            exito, mensaje = factura.marcar_como_pagada()

            if exito:
                factura_actualizada = FacturaModel.get_by_id(factura_id)

                # Registrar movimiento en caja si no está registrado
                if not self._existe_movimiento_caja_factura(factura_id):
                    self._registrar_movimiento_caja_factura(factura_actualizada)

                logger.info(f"✅ Factura marcada como pagada: {factura.nro_factura}")
                return True, mensaje, factura_actualizada
            else:
                return False, mensaje, None

        except Exception as e:
            logger.error(f"Error al marcar factura {factura_id} como pagada: {e}")
            return False, f"Error interno: {str(e)}", None

    def marcar_exportada_siat(self, factura_id: int) -> Tuple[bool, str, Optional[FacturaModel]]:
        """
        Marcar factura como exportada al SIAT

        Args:
            factura_id: ID de la factura

        Returns:
            Tuple (éxito, mensaje, factura actualizada)
        """
        try:
            # Verificar permisos del usuario
            if not self._tiene_permisos_siat():
                return False, "No tiene permisos para exportar facturas al SIAT", None

            factura = FacturaModel.get_by_id(factura_id)
            if not factura:
                return False, f"No se encontró factura con ID {factura_id}", None

            exito, mensaje = factura.marcar_exportada_siat()

            if exito:
                factura_actualizada = FacturaModel.get_by_id(factura_id)
                logger.info(f"✅ Factura exportada al SIAT: {factura.nro_factura}")
                return True, mensaje, factura_actualizada
            else:
                return False, mensaje, None

        except Exception as e:
            logger.error(f"Error al marcar factura {factura_id} como exportada al SIAT: {e}")
            return False, f"Error interno: {str(e)}", None

    # ==================== CÁLCULOS Y TOTALES ====================

    def calcular_totales(
        self,
        subtotal: Union[float, Decimal, str],
        aplicar_iva: bool = True,
        aplicar_it: bool = False,
        tasa_iva: Optional[Union[float, Decimal]] = None,
        tasa_it: Optional[Union[float, Decimal]] = None
    ) -> Dict[str, Any]:
        """
        Calcular totales de factura

        Args:
            subtotal: Subtotal de la factura
            aplicar_iva: Si True, aplicar IVA
            aplicar_it: Si True, aplicar IT
            tasa_iva: Tasa de IVA personalizada
            tasa_it: Tasa de IT personalizada

        Returns:
            Diccionario con totales calculados
        """
        try:
            # Convertir a Decimal
            if isinstance(subtotal, (int, float)):
                subtotal_dec = Decimal(str(subtotal))
            elif isinstance(subtotal, str):
                subtotal_dec = Decimal(subtotal)
            else:
                subtotal_dec = subtotal

            # Convertir tasas a Decimal
            tasa_iva_dec = Decimal(str(tasa_iva)) if tasa_iva is not None else None
            tasa_it_dec = Decimal(str(tasa_it)) if tasa_it is not None else None

            # Calcular totales
            totales = FacturaModel.calcular_totales(
                subtotal=subtotal_dec,
                aplicar_iva=aplicar_iva,
                aplicar_it=aplicar_it,
                tasa_iva=tasa_iva_dec,
                tasa_it=tasa_it_dec
            )

            return {
                'subtotal': float(totales['subtotal']),
                'iva': float(totales['iva']),
                'it': float(totales['it']),
                'total': float(totales['total']),
                'tasa_iva': float(tasa_iva_dec or Decimal('0.13')),
                'tasa_it': float(tasa_it_dec or Decimal('0.03')),
                'aplicar_iva': aplicar_iva,
                'aplicar_it': aplicar_it
            }

        except Exception as e:
            logger.error(f"Error al calcular totales: {e}")
            return {
                'error': str(e),
                'subtotal': 0.0,
                'iva': 0.0,
                'it': 0.0,
                'total': 0.0
            }

    def simular_factura(
        self,
        subtotal: float,
        tipo_documento: str = FacturaModel.TIPO_CONSUMIDOR_FINAL,
        aplicar_iva: bool = True,
        aplicar_it: bool = False
    ) -> Dict[str, Any]:
        """
        Simular una factura con diferentes escenarios

        Args:
            subtotal: Subtotal de la factura
            tipo_documento: Tipo de documento del cliente
            aplicar_iva: Si True, aplicar IVA
            aplicar_it: Si True, aplicar IT

        Returns:
            Diccionario con simulación
        """
        try:
            # Calcular totales base
            totales_base = self.calcular_totales(subtotal, aplicar_iva, aplicar_it)

            # Escenarios de cálculo
            escenarios = []

            # Escenario 1: Solo IVA (13%)
            if aplicar_iva and not aplicar_it:
                escenarios.append({
                    'nombre': 'Con IVA (13%)',
                    'descripcion': 'Aplicación de Impuesto al Valor Agregado',
                    'subtotal': totales_base['subtotal'],
                    'iva': totales_base['iva'],
                    'it': 0.0,
                    'total': totales_base['subtotal'] + totales_base['iva']
                })

            # Escenario 2: Solo IT (3%)
            if aplicar_it and not aplicar_iva:
                escenarios.append({
                    'nombre': 'Con IT (3%)',
                    'descripcion': 'Aplicación de Impuesto a las Transacciones',
                    'subtotal': totales_base['subtotal'],
                    'iva': 0.0,
                    'it': totales_base['it'],
                    'total': totales_base['subtotal'] + totales_base['it']
                })

            # Escenario 3: IVA + IT
            if aplicar_iva and aplicar_it:
                escenarios.append({
                    'nombre': 'Con IVA (13%) e IT (3%)',
                    'descripcion': 'Aplicación de ambos impuestos',
                    'subtotal': totales_base['subtotal'],
                    'iva': totales_base['iva'],
                    'it': totales_base['it'],
                    'total': totales_base['total']
                })

            # Escenario 4: Sin impuestos
            escenarios.append({
                'nombre': 'Sin impuestos',
                'descripcion': 'Exento de impuestos',
                'subtotal': subtotal,
                'iva': 0.0,
                'it': 0.0,
                'total': subtotal
            })

            # Calcular próximos números de factura
            prefijos = {
                FacturaModel.TIPO_NIT: 'FAC-NIT-',
                FacturaModel.TIPO_CI: 'FAC-CI-',
                FacturaModel.TIPO_CONSUMIDOR_FINAL: 'FAC-CF-'
            }

            prefijo = prefijos.get(tipo_documento, 'FAC-')
            siguiente_numero = FacturaModel.get_ultimo_numero(prefijo)

            return {
                'simulacion': True,
                'fecha_simulacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'subtotal_base': subtotal,
                'tipo_documento': tipo_documento,
                'tipo_documento_descripcion': FacturaModel.TIPOS_DOCUMENTO_DESC.get(tipo_documento, tipo_documento),
                'siguiente_numero': siguiente_numero,
                'escenarios': escenarios,
                'recomendacion': self._obtener_recomendacion_impuestos(tipo_documento, subtotal)
            }

        except Exception as e:
            logger.error(f"Error al simular factura: {e}")
            return {'error': str(e)}

    def _obtener_recomendacion_impuestos(self, tipo_documento: str, subtotal: float) -> Dict[str, Any]:
        """
        Obtener recomendación de impuestos según tipo de documento y monto

        Args:
            tipo_documento: Tipo de documento
            subtotal: Subtotal de la factura

        Returns:
            Dict con recomendación
        """
        if tipo_documento == FacturaModel.TIPO_NIT:
            # Para NIT: aplicar IVA e IT según monto
            if subtotal < 1000:  # Monto pequeño
                return {
                    'aplicar_iva': True,
                    'aplicar_it': False,
                    'razon': 'Para montos menores a Bs. 1,000 se recomienda solo IVA'
                }
            else:
                return {
                    'aplicar_iva': True,
                    'aplicar_it': True,
                    'razon': 'Para montos mayores a Bs. 1,000 se recomienda aplicar ambos impuestos'
                }

        elif tipo_documento == FacturaModel.TIPO_CI:
            # Para CI: solo IVA generalmente
            return {
                'aplicar_iva': True,
                'aplicar_it': False,
                'razon': 'Para facturas a personas naturales se aplica solo IVA'
            }

        else:  # CONSUMIDOR_FINAL
            # Para consumidor final: sin impuestos o solo IVA según monto
            if subtotal < 500:
                return {
                    'aplicar_iva': False,
                    'aplicar_it': False,
                    'razon': 'Para consumidor final con montos pequeños, puede ser exento'
                }
            else:
                return {
                    'aplicar_iva': True,
                    'aplicar_it': False,
                    'razon': 'Para montos mayores a Bs. 500, aplicar IVA'
                }

    # ==================== ESTADÍSTICAS E INFORMES ====================

    def obtener_estadisticas(
        self,
        fecha_inicio: Optional[Union[str, date]] = None,
        fecha_fin: Optional[Union[str, date]] = None
    ) -> Dict[str, Any]:
        """
        Obtener estadísticas de facturas

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

                fecha_inicio = primer_dia.isoformat()
                fecha_fin = ultimo_dia.isoformat()

            # Obtener facturas en el rango
            facturas = self.obtener_todas(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, limite=1000)

            # Calcular totales
            total_facturas = len(facturas)
            total_subtotal = Decimal('0')
            total_iva = Decimal('0')
            total_it = Decimal('0')
            total_general = Decimal('0')

            # Por estado
            por_estado = {}
            por_tipo_documento = {}
            por_dia = {}

            for factura in facturas:
                # Totales
                total_subtotal += factura.subtotal
                total_iva += factura.iva
                total_it += factura.it
                total_general += factura.total

                # Por estado
                estado = factura.estado
                if estado not in por_estado:
                    por_estado[estado] = {'cantidad': 0, 'monto': Decimal('0')}
                por_estado[estado]['cantidad'] += 1
                por_estado[estado]['monto'] += factura.total

                # Por tipo de documento
                tipo_doc = factura.tipo_documento
                if tipo_doc not in por_tipo_documento:
                    por_tipo_documento[tipo_doc] = {'cantidad': 0, 'monto': Decimal('0')}
                por_tipo_documento[tipo_doc]['cantidad'] += 1
                por_tipo_documento[tipo_doc]['monto'] += factura.total

                # Por día
                if hasattr(factura.fecha_emision, 'day'):
                    dia = factura.fecha_emision.day
                elif isinstance(factura.fecha_emision, str):
                    try:
                        dia = datetime.strptime(factura.fecha_emision, '%Y-%m-%d').day
                    except:
                        dia = 1
                else:
                    dia = 1

                if dia not in por_dia:
                    por_dia[dia] = {'cantidad': 0, 'monto': Decimal('0')}
                por_dia[dia]['cantidad'] += 1
                por_dia[dia]['monto'] += factura.total

            # Estadísticas de exportación SIAT
            exportadas_siat = len([f for f in facturas if f.exportada_siat])

            # Factura con mayor monto
            factura_mayor = max(facturas, key=lambda f: f.total) if facturas else None

            return {
                'periodo': {
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin
                },
                'totales': {
                    'facturas': total_facturas,
                    'subtotal': float(total_subtotal),
                    'iva': float(total_iva),
                    'it': float(total_it),
                    'total': float(total_general),
                    'promedio_factura': float(total_general / total_facturas) if total_facturas > 0 else 0
                },
                'por_estado': por_estado,
                'por_tipo_documento': por_tipo_documento,
                'por_dia': por_dia,
                'exportacion_siat': {
                    'exportadas': exportadas_siat,
                    'no_exportadas': total_facturas - exportadas_siat,
                    'porcentaje_exportadas': (exportadas_siat / total_facturas * 100) if total_facturas > 0 else 0
                },
                'factura_mayor': {
                    'nro_factura': factura_mayor.nro_factura if factura_mayor else None,
                    'cliente': factura_mayor.razon_social if factura_mayor else None,
                    'monto': float(factura_mayor.total) if factura_mayor else 0
                } if factura_mayor else None,
                'fecha_consulta': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            logger.error(f"Error al obtener estadísticas de facturas: {e}")
            return {'error': str(e)}

    def obtener_resumen_factura(self, factura_id: int) -> Dict[str, Any]:
        """
        Obtener resumen completo de una factura

        Args:
            factura_id: ID de la factura

        Returns:
            Diccionario con resumen
        """
        try:
            factura = FacturaModel.get_by_id(factura_id)
            if not factura:
                return {'error': f'Factura {factura_id} no encontrada'}

            # Obtener detalles si existen
            detalles = []
            try:
                # Buscar detalles de la factura
                from database import Database
                db = Database()
                query = f"SELECT * FROM detalles_factura WHERE factura_id = ?"
                results = db.fetch_all(query, [factura_id])
                if results:
                    detalles = results
            except:
                pass
            
            # Obtener movimiento de caja asociado
            movimiento = self._obtener_movimiento_caja_factura(factura_id)

            return {
                'factura': factura.to_dict(),
                'detalles': detalles,
                'movimiento_caja': movimiento.to_dict() if movimiento else None,
                'total_detallado': sum(d['subtotal'] for d in detalles) if detalles else 0,
                'codigo_qr': self._generar_codigo_qr_factura(factura),
                'leyenda_siat': self._obtener_leyenda_siat(factura)
            }

        except Exception as e:
            logger.error(f"Error al obtener resumen de factura {factura_id}: {e}")
            return {'error': str(e)}

    def _generar_codigo_qr_factura(self, factura: FacturaModel) -> str:
        """
        Generar datos para código QR de factura

        Args:
            factura: Modelo de factura

        Returns:
            Cadena para generar QR
        """
        try:
            # Datos para QR según formato SIAT
            datos = {
                'nit_emisor': '1234567890',  # NIT del emisor (configurable)
                'nro_factura': factura.nro_factura,
                'nro_autorizacion': '1234567890',  # Número de autorización (configurable)
                'fecha_emision': factura.fecha_emision,
                'nit_cliente': factura.nit_ci if factura.tipo_documento == FacturaModel.TIPO_NIT else '',
                'importe_total': float(factura.total),
                'codigo_control': factura.codigo_control,
                'fecha_limite': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            }

            # Formatear como cadena
            return f"NIT:{datos['nit_emisor']}|NRO:{datos['nro_factura']}|AUT:{datos['nro_autorizacion']}|FEC:{datos['fecha_emision']}|NITC:{datos['nit_cliente']}|IMP:{datos['importe_total']}|COD:{datos['codigo_control']}|FECL:{datos['fecha_limite']}"

        except Exception as e:
            logger.error(f"Error al generar código QR para factura {factura.nro_factura}: {e}")
            return ""

    def _obtener_leyenda_siat(self, factura: FacturaModel) -> List[str]:
        """
        Obtener leyendas SIAT aplicables

        Args:
            factura: Modelo de factura

        Returns:
            Lista de leyendas
        """
        leyendas = []

        # Leyendas generales
        leyendas.append("Ley N° 453: Tienes derecho a recibir información sobre las características y contenidos de los servicios que utilices")
        leyendas.append("Ley N° 453: Puedes acceder a los libros de reclamaciones en forma gratuita en los locales de atención al público")

        # Leyendas según tipo de documento
        if factura.tipo_documento == FacturaModel.TIPO_CONSUMIDOR_FINAL:
            leyendas.append("Código de Consumidor: El proveedor debe garantizar el derecho a la seguridad e indemnidad")
            leyendas.append("Código de Consumidor: El proveedor debe ofrecer servicios de calidad")

        return leyendas

    def generar_reporte_factura(
        self,
        factura_id: int,
        formato: str = 'texto'
    ) -> str:
        """
        Generar reporte de factura

        Args:
            factura_id: ID de la factura
            formato: 'texto' o 'html'

        Returns:
            Reporte formateado
        """
        try:
            factura = FacturaModel.get_by_id(factura_id)
            if not factura:
                return f"Error: Factura {factura_id} no encontrada"

            # Obtener resumen
            resumen = self.obtener_resumen_factura(factura_id)

            if formato.lower() == 'html':
                return self._generar_reporte_html(factura, resumen)
            else:
                return self._generar_reporte_texto(factura, resumen)

        except Exception as e:
            logger.error(f"Error al generar reporte de factura {factura_id}: {e}")
            return f"Error al generar reporte: {str(e)}"

    def _generar_reporte_texto(
        self,
        factura: FacturaModel,
        resumen: Dict[str, Any]
    ) -> str:
        """Generar reporte en formato texto"""
        reporte = []
        reporte.append("=" * 80)
        reporte.append("REPORTE DE FACTURA".center(80))
        reporte.append("=" * 80)
        reporte.append(f"Factura N°: {factura.nro_factura}")
        reporte.append(f"Fecha Emisión: {factura.fecha_emision_formateada}")
        reporte.append(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        reporte.append(f"Generado por: {self._current_usuario.nombre if self._current_usuario else 'Sistema'}")
        reporte.append("-" * 80)

        # Información del cliente
        reporte.append("INFORMACIÓN DEL CLIENTE:")
        reporte.append(f"  Razón Social: {factura.razon_social}")
        reporte.append(f"  Tipo Documento: {factura.tipo_documento_descripcion}")

        if factura.nit_ci:
            reporte.append(f"  NIT/CI: {factura.nit_ci_formateado}")

        reporte.append("-" * 80)

        # Totales
        reporte.append("TOTALES DE LA FACTURA:")
        reporte.append(f"  Subtotal: {factura.subtotal_formateado}")
        if float(factura.iva) > 0:
            reporte.append(f"  IVA (13%): {factura.iva_formateado}")
        if float(factura.it) > 0:
            reporte.append(f"  IT (3%): {factura.it_formateado}")
        reporte.append(f"  Total: {factura.total_formateado}")

        reporte.append("-" * 80)

        # Estado
        reporte.append("INFORMACIÓN ADICIONAL:")
        reporte.append(f"  Estado: {factura.estado_descripcion}")
        reporte.append(f"  Exportada SIAT: {factura.exportada_siat_descripcion}")

        if factura.concepto:
            reporte.append(f"  Concepto: {factura.concepto}")

        # Detalles
        if 'detalles' in resumen and resumen['detalles']:
            reporte.append("-" * 80)
            reporte.append("DETALLES DE LA FACTURA:")
            for i, detalle in enumerate(resumen['detalles'], 1):
                reporte.append(f"  {i}. {detalle.get('descripcion', 'Sin descripción')}")
                reporte.append(f"     Cantidad: {detalle.get('cantidad', 1)} x Bs. {detalle.get('precio_unitario', 0):,.2f}")
                reporte.append(f"     Subtotal: Bs. {detalle.get('subtotal', 0):,.2f}")

        reporte.append("=" * 80)

        return "\n".join(reporte)

    def _generar_reporte_html(
        self,
        factura: FacturaModel,
        resumen: Dict[str, Any]
    ) -> str:
        """Generar reporte en formato HTML"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Reporte de Factura - {factura.nro_factura}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                h1, h2, h3 {{ color: #2c3e50; }}
                .section {{ margin-bottom: 30px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; }}
                .info-item {{ background-color: #f8f9fa; padding: 15px; border-radius: 3px; }}
                .totales-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
                .total-item {{ background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }}
                .total-value {{ font-size: 24px; font-weight: bold; margin: 10px 0; }}
                .total-label {{ color: #6c757d; font-size: 14px; }}
                .estado-emitida {{ color: #28a745; font-weight: bold; }}
                .estado-anulada {{ color: #dc3545; font-weight: bold; }}
                .estado-pagada {{ color: #17a2b8; font-weight: bold; }}
                .estado-pendiente {{ color: #ffc107; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f8f9fa; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #6c757d; font-size: 12px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Reporte de Factura</h1>
                <p><strong>Sistema:</strong> FormaGestPro_MVC</p>
                <p><strong>Factura N°:</strong> {factura.nro_factura}</p>
                <p><strong>Generado:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                <p><strong>Usuario:</strong> {self._current_usuario.nombre if self._current_usuario else 'Sistema'}</p>
            </div>

            <div class="section">
                <h2>Información de la Factura</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <strong>Número de Factura:</strong><br>
                        {factura.nro_factura}
                    </div>
                    <div class="info-item">
                        <strong>Fecha de Emisión:</strong><br>
                        {factura.fecha_emision_formateada}
                    </div>
                    <div class="info-item">
                        <strong>Estado:</strong><br>
                        <span class="estado-{factura.estado.lower()}">{factura.estado_descripcion}</span>
                    </div>
                    <div class="info-item">
                        <strong>Exportada SIAT:</strong><br>
                        {factura.exportada_siat_descripcion}
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>Información del Cliente</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <strong>Razón Social:</strong><br>
                        {factura.razon_social}
                    </div>
                    <div class="info-item">
                        <strong>Tipo de Documento:</strong><br>
                        {factura.tipo_documento_descripcion}
                    </div>
                    {f'<div class="info-item"><strong>NIT/CI:</strong><br>{factura.nit_ci_formateado}</div>' if factura.nit_ci else ''}
                    {f'<div class="info-item"><strong>Concepto:</strong><br>{factura.concepto}</div>' if factura.concepto else ''}
                </div>
            </div>

            <div class="section">
                <h2>Totales</h2>
                <div class="totales-grid">
                    <div class="total-item">
                        <div class="total-label">Subtotal</div>
                        <div class="total-value">{factura.subtotal_formateado}</div>
                    </div>
                    {f'<div class="total-item"><div class="total-label">IVA (13%)</div><div class="total-value">{factura.iva_formateado}</div></div>' if float(factura.iva) > 0 else ''}
                    {f'<div class="total-item"><div class="total-label">IT (3%)</div><div class="total-value">{factura.it_formateado}</div></div>' if float(factura.it) > 0 else ''}
                    <div class="total-item">
                        <div class="total-label">Total General</div>
                        <div class="total-value" style="color: #28a745; font-size: 28px;">{factura.total_formateado}</div>
                    </div>
                </div>
            </div>
        """

        # Detalles si existen
        if 'detalles' in resumen and resumen['detalles']:
            html += f"""
            <div class="section">
                <h2>Detalles de la Factura</h2>
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Descripción</th>
                            <th>Cantidad</th>
                            <th>Precio Unitario</th>
                            <th>Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>
            """

            for i, detalle in enumerate(resumen['detalles'], 1):
                html += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{detalle.get('descripcion', 'Sin descripción')}</td>
                        <td>{detalle.get('cantidad', 1)}</td>
                        <td>Bs. {detalle.get('precio_unitario', 0):,.2f}</td>
                        <td>Bs. {detalle.get('subtotal', 0):,.2f}</td>
                    </tr>
                """

            html += """
                    </tbody>
                </table>
            </div>
            """

        # Código QR si está disponible
        qr_data = self._generar_codigo_qr_factura(factura)
        if qr_data:
            html += f"""
            <div class="section">
                <h2>Código QR</h2>
                <div class="info-item" style="text-align: center;">
                    <p><strong>Datos para QR:</strong></p>
                    <p style="font-family: monospace; font-size: 12px; word-break: break-all;">{qr_data}</p>
                    <p><small><em>Escanea este código para verificar la factura</em></small></p>
                </div>
            </div>
            """

        html += f"""
            <div class="footer">
                <p><em>Reporte generado automáticamente por FormaGestPro_MVC - Módulo de Facturación</em></p>
                <p><em>Este es un documento oficial para fines de control interno.</em></p>
            </div>
        </body>
        </html>
        """

        return html

    # ==================== MÉTODOS AUXILIARES ====================

    def _validar_datos_factura(
        self, 
        datos: Dict[str, Any], 
        es_actualizacion: bool = False
    ) -> Tuple[bool, List[str]]:
        """
        Validar datos de factura

        Args:
            datos: Diccionario con datos a validar
            es_actualizacion: Si es una actualización

        Returns:
            Tuple (válido, lista de errores)
        """
        errores = []

        # Validar campos requeridos
        campos_requeridos = ['razon_social']
        for campo in campos_requeridos:
            if campo not in datos or not str(datos.get(campo, '')).strip():
                errores.append(f"El campo '{campo}' es requerido")

        # Validar número de factura
        if 'nro_factura' in datos and datos['nro_factura']:
            valido, mensaje = FacturaModel.validate_nro_factura(datos['nro_factura'])
            if not valido:
                errores.append(f"Número de factura: {mensaje}")

        # Validar tipo de documento
        if 'tipo_documento' in datos and datos['tipo_documento']:
            if datos['tipo_documento'] not in FacturaModel.TIPOS_DOCUMENTO:
                errores.append(f"Tipo de documento inválido. Válidos: {', '.join(FacturaModel.TIPOS_DOCUMENTO)}")

        # Validar NIT/CI según tipo de documento
        tipo_doc = datos.get('tipo_documento', FacturaModel.TIPO_CONSUMIDOR_FINAL)
        nit_ci = datos.get('nit_ci')

        if tipo_doc == FacturaModel.TIPO_NIT:
            if not nit_ci:
                errores.append("NIT es requerido para facturas con tipo NIT")
            else:
                valido, mensaje = FacturaModel.validate_nit(nit_ci)
                if not valido:
                    errores.append(f"NIT: {mensaje}")

        elif tipo_doc == FacturaModel.TIPO_CI:
            if not nit_ci:
                errores.append("CI es requerido para facturas con tipo CI")
            else:
                valido, mensaje = FacturaModel.validate_ci(nit_ci)
                if not valido:
                    errores.append(f"CI: {mensaje}")

        # Validar razón social
        if 'razon_social' in datos and datos['razon_social']:
            valido, mensaje = FacturaModel.validate_razon_social(datos['razon_social'])
            if not valido:
                errores.append(f"Razón social: {mensaje}")

        # Validar montos
        for campo_monto in ['subtotal', 'iva', 'it', 'total']:
            if campo_monto in datos and datos[campo_monto] is not None:
                try:
                    monto = float(datos[campo_monto])
                    if monto < 0:
                        errores.append(f"El {campo_monto} no puede ser negativo")
                    if monto > 1000000:  # Límite razonable
                        errores.append(f"El {campo_monto} no puede exceder 1,000,000")
                except (ValueError, TypeError):
                    errores.append(f"{campo_monto.capitalize()} inválido. Debe ser un número")

        # Validar fecha de emisión
        if 'fecha_emision' in datos and datos['fecha_emision']:
            try:
                fecha = datetime.strptime(datos['fecha_emision'], '%Y-%m-%d').date()
                if fecha > date.today():
                    errores.append("La fecha de emisión no puede ser futura")
            except ValueError:
                errores.append("Fecha de emisión inválida. Formato debe ser YYYY-MM-DD")

        # Validar estado
        if 'estado' in datos and datos['estado']:
            if datos['estado'] not in FacturaModel.ESTADOS:
                errores.append(f"Estado inválido. Válidos: {', '.join(FacturaModel.ESTADOS)}")

        return len(errores) == 0, errores

    def _registrar_movimiento_caja_factura(self, factura: FacturaModel) -> bool:
        """
        Registrar movimiento de caja para una factura

        Args:
            factura: Modelo de factura

        Returns:
            True si se registró correctamente
        """
        try:
            # Solo registrar si la factura está pagada o emitida
            if factura.estado not in [FacturaModel.ESTADO_PAGADA, FacturaModel.ESTADO_EMITIDA]:
                return False

            # Verificar si ya existe movimiento
            from .movimiento_caja_controller import MovimientoCajaController
            caja_controller = MovimientoCajaController()
            caja_controller.current_usuario = self._current_usuario

            exito, mensaje, movimiento = caja_controller.registrar_ingreso_factura(factura.id)

            if exito:
                logger.info(f"Movimiento de caja registrado para factura {factura.nro_factura}")
                return True
            else:
                logger.error(f"Error al registrar movimiento de caja para factura {factura.nro_factura}: {mensaje}")
                return False

        except Exception as e:
            logger.error(f"Error al registrar movimiento de caja para factura {factura.id}: {e}")
            return False

    def _registrar_movimiento_reversion_factura(self, factura: FacturaModel) -> bool:
        """
        Registrar movimiento de reversión para factura anulada

        Args:
            factura: Modelo de factura

        Returns:
            True si se registró correctamente
        """
        try:
            # Solo revertir si hay movimiento registrado
            movimiento = self._obtener_movimiento_caja_factura(factura.id)
            if not movimiento:
                return False

            from .movimiento_caja_controller import MovimientoCajaController
            caja_controller = MovimientoCajaController()
            caja_controller.current_usuario = self._current_usuario

            exito, mensaje = caja_controller.anular_movimiento(movimiento.id)

            if exito:
                logger.info(f"Movimiento de caja revertido para factura anulada {factura.nro_factura}")
                return True
            else:
                logger.error(f"Error al revertir movimiento de caja para factura {factura.nro_factura}: {mensaje}")
                return False

        except Exception as e:
            logger.error(f"Error al registrar reversión para factura {factura.id}: {e}")
            return False

    def _existe_movimiento_caja_factura(self, factura_id: int) -> bool:
        """
        Verificar si existe movimiento de caja para una factura

        Args:
            factura_id: ID de la factura

        Returns:
            True si existe movimiento
        """
        try:
            from .movimiento_caja_controller import MovimientoCajaController
            caja_controller = MovimientoCajaController()

            movimientos = caja_controller.obtener_movimientos_por_referencia('FACTURA', factura_id)
            return len(movimientos) > 0

        except Exception as e:
            logger.error(f"Error al verificar movimiento de caja para factura {factura_id}: {e}")
            return False

    def _obtener_movimiento_caja_factura(self, factura_id: int) -> Optional[MovimientoCajaModel]:
        """
        Obtener movimiento de caja asociado a una factura

        Args:
            factura_id: ID de la factura

        Returns:
            Modelo de movimiento de caja o None
        """
        try:
            from .movimiento_caja_controller import MovimientoCajaController
            caja_controller = MovimientoCajaController()

            movimientos = caja_controller.obtener_movimientos_por_referencia('FACTURA', factura_id)
            return movimientos[0] if movimientos else None

        except Exception as e:
            logger.error(f"Error al obtener movimiento de caja para factura {factura_id}: {e}")
            return None

    def _tiene_permisos_facturacion(self) -> bool:
        """Verificar si el usuario tiene permisos para facturación"""
        if not self._current_usuario:
            return False

        roles_permitidos = ['ADMIN', 'CONTADOR', 'FACTURADOR']
        return self._current_usuario.rol in roles_permitidos

    def _tiene_permisos_siat(self) -> bool:
        """Verificar si el usuario tiene permisos para exportar al SIAT"""
        if not self._current_usuario:
            return False

        # Solo administradores y contadores pueden exportar al SIAT
        roles_permitidos = ['ADMIN', 'CONTADOR']
        return self._current_usuario.rol in roles_permitidos

    # ==================== MÉTODOS DE UTILIDAD ====================

    def exportar_facturas_csv(
        self,
        fecha_inicio: Union[str, date],
        fecha_fin: Union[str, date],
        ruta_archivo: str
    ) -> Tuple[bool, str]:
        """
        Exportar facturas a archivo CSV

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            ruta_archivo: Ruta del archivo CSV

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            import csv

            # Obtener facturas
            facturas = self.obtener_todas(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, limite=1000)

            # Preparar datos
            datos = []
            for factura in facturas:
                fila = factura.to_dict()
                datos.append(fila)

            # Escribir archivo CSV
            with open(ruta_archivo, 'w', newline='', encoding='utf-8') as csvfile:
                if datos:
                    fieldnames = datos[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    writer.writerows(datos)

            logger.info(f"Facturas exportadas a {ruta_archivo}")
            return True, f"Facturas exportadas exitosamente a {ruta_archivo}"

        except Exception as e:
            logger.error(f"Error al exportar facturas a CSV: {e}")
            return False, f"Error al exportar: {str(e)}"