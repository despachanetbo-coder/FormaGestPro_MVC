# app/controllers/gastos_operativos_controller.py
"""
Controlador para la gestión de gastos operativos en el sistema FormaGestPro_MVC
"""

import logging
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path

from app.models.gasto_operativo_model import GastoOperativoModel
from app.models.docente_model import DocenteModel

logger = logging.getLogger(__name__)

class GastosOperativosController:
    """Controlador para la gestión de gastos operativos"""
    def __init__(self, db_path: str = None):
        """
        Inicializar controlador de gastos operativos

        Args:
            db_path: Ruta a la base de datos (opcional)
        """
        self.db_path = db_path

    # ==================== OPERACIONES CRUD ====================

    def crear_gasto(self, datos: Dict[str, Any]) -> Tuple[bool, str, Optional[GastoOperativoModel]]:
        """
        Crear un nuevo gasto operativo

        Args:
            datos: Diccionario con los datos del gasto

        Returns:
            Tuple (éxito, mensaje, gasto)
        """
        try:
            # Validar datos requeridos
            errores = self._validar_datos_gasto(datos)
            if errores:
                return False, "Errores de validación: " + "; ".join(errores), None

            # Crear el gasto
            gasto = GastoOperativoModel(**datos)
            gasto_id = gasto.save()

            if gasto_id:
                gasto_creado = GastoOperativoModel.find_by_id(gasto_id)
                mensaje = f"Gasto operativo registrado exitosamente (ID: {gasto_id})"
                return True, mensaje, gasto_creado
            else:
                return False, "Error al guardar el gasto en la base de datos", None

        except Exception as e:
            logger.error(f"Error al crear gasto operativo: {e}")
            return False, f"Error interno: {str(e)}", None

    def actualizar_gasto(self, gasto_id: int, datos: Dict[str, Any]) -> Tuple[bool, str, Optional[GastoOperativoModel]]:
        """
        Actualizar un gasto operativo existente

        Args:
            gasto_id: ID del gasto a actualizar
            datos: Diccionario con los datos a actualizar

        Returns:
            Tuple (éxito, mensaje, gasto)
        """
        try:
            # Buscar gasto existente
            gasto = GastoOperativoModel.find_by_id(gasto_id)
            if not gasto:
                return False, f"No se encontró gasto con ID {gasto_id}", None

            # Validar datos
            errores = self._validar_datos_gasto(datos, es_actualizacion=True)
            if errores:
                return False, "Errores de validación: " + "; ".join(errores), None

            # Actualizar atributos del gasto
            for key, value in datos.items():
                if hasattr(gasto, key):
                    setattr(gasto, key, value)

            # Guardar cambios
            if gasto.save():
                mensaje = f"Gasto operativo actualizado exitosamente (ID: {gasto_id})"
                return True, mensaje, gasto
            else:
                return False, "Error al guardar los cambios", None

        except Exception as e:
            logger.error(f"Error al actualizar gasto {gasto_id}: {e}")
            return False, f"Error interno: {str(e)}", None

    def eliminar_gasto(self, gasto_id: int) -> Tuple[bool, str]:
        """
        Eliminar un gasto operativo

        Args:
            gasto_id: ID del gasto a eliminar

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            gasto = GastoOperativoModel.find_by_id(gasto_id)
            if not gasto:
                return False, f"No se encontró gasto con ID {gasto_id}"

            if gasto.delete():
                return True, f"Gasto eliminado exitosamente (ID: {gasto_id})"
            else:
                return False, "Error al eliminar el gasto"

        except Exception as e:
            logger.error(f"Error al eliminar gasto {gasto_id}: {e}")
            return False, f"Error interno: {str(e)}"

    # ==================== CONSULTAS ====================

    def obtener_gasto(self, gasto_id: int) -> Optional[GastoOperativoModel]:
        """
        Obtener un gasto por su ID

        Args:
            gasto_id: ID del gasto

        Returns:
            GastoOperativoModel o None si no se encuentra
        """
        try:
            return GastoOperativoModel.find_by_id(gasto_id)
        except Exception as e:
            logger.error(f"Error al obtener gasto {gasto_id}: {e}")
            return None

    def obtener_gastos(
        self, 
        fecha_inicio: Optional[Union[str, date]] = None,
        fecha_fin: Optional[Union[str, date]] = None,
        categoria: Optional[str] = None,
        subcategoria: Optional[str] = None,
        forma_pago: Optional[str] = None,
        limite: int = 100,
        offset: int = 0,
        ordenar_por: str = 'fecha',
        orden_desc: bool = True
    ) -> List[GastoOperativoModel]:
        """
        Obtener lista de gastos con filtros

        Args:
            fecha_inicio: Fecha de inicio (YYYY-MM-DD o date)
            fecha_fin: Fecha de fin (YYYY-MM-DD o date)
            categoria: Filtrar por categoría
            subcategoria: Filtrar por subcategoría
            forma_pago: Filtrar por forma de pago
            limite: Número máximo de resultados
            offset: Desplazamiento para paginación
            ordenar_por: Campo para ordenar ('fecha', 'monto', 'descripcion')
            orden_desc: Orden descendente (True) o ascendente (False)

        Returns:
            Lista de gastos
        """
        try:
            return GastoOperativoModel.buscar_gastos(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                categoria=categoria,
                subcategoria=subcategoria,
                forma_pago=forma_pago,
                limite=limite,
                offset=offset,
                ordenar_por=ordenar_por,
                orden_desc=orden_desc
            )
        except Exception as e:
            logger.error(f"Error al obtener gastos: {e}")
            return []

    def buscar_gastos(
        self, 
        texto: str,
        campos: List[str] = None
    ) -> List[GastoOperativoModel]:
        """
        Buscar gastos por texto en múltiples campos

        Args:
            texto: Texto a buscar
            campos: Campos donde buscar (None = todos los campos de texto)

        Returns:
            Lista de gastos que coinciden
        """
        try:
            if campos is None:
                campos = ['descripcion', 'proveedor', 'nro_factura', 'comprobante_nro']

            gastos = GastoOperativoModel.obtener_todos()
            resultados = []
            texto_lower = texto.lower()

            for gasto in gastos:
                for campo in campos:
                    if hasattr(gasto, campo):
                        valor = getattr(gasto, campo, '')
                        if valor and texto_lower in str(valor).lower():
                            resultados.append(gasto)
                            break  # No repetir el mismo gasto
                        
            return resultados

        except Exception as e:
            logger.error(f"Error al buscar gastos ({texto}): {e}")
            return []

    def contar_gastos(
        self,
        fecha_inicio: Optional[Union[str, date]] = None,
        fecha_fin: Optional[Union[str, date]] = None,
        categoria: Optional[str] = None
    ) -> int:
        """
        Contar número de gastos

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            categoria: Filtrar por categoría

        Returns:
            Número de gastos
        """
        try:
            gastos = self.obtener_gastos(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                categoria=categoria
            )
            return len(gastos)
        except Exception as e:
            logger.error(f"Error al contar gastos: {e}")
            return 0

    # ==================== OPERACIONES ESPECÍFICAS ====================

    def registrar_pago_honorarios(
        self,
        docente_id: int,
        monto: float,
        horas_trabajadas: Optional[int] = None,
        descripcion_adicional: str = "",
        fecha: Optional[Union[str, date]] = None
    ) -> Tuple[bool, str, Optional[GastoOperativoModel]]:
        """
        Registrar pago de honorarios a docente

        Args:
            docente_id: ID del docente
            monto: Monto total del pago
            horas_trabajadas: Número de horas trabajadas (opcional)
            descripcion_adicional: Descripción adicional (opcional)
            fecha: Fecha del pago (default: hoy)

        Returns:
            Tuple (éxito, mensaje, gasto)
        """
        try:
            # Obtener datos del docente
            docente = DocenteModel.find_by_id(docente_id)
            if not docente:
                return False, f"No se encontró docente con ID {docente_id}", None

            # Preparar descripción
            descripcion = f"PAGO DE HONORARIOS - {docente.nombre_completo} (CI: {docente.ci_numero}-{docente.ci_expedicion})"

            if horas_trabajadas:
                descripcion += f" - {horas_trabajadas} horas"

            if descripcion_adicional:
                descripcion += f" - {descripcion_adicional}"

            # Preparar datos del gasto
            datos_gasto = {
                'fecha': fecha or datetime.now().date().isoformat(),
                'monto': monto,
                'categoria': 'PAGO_DOCENTE',
                'subcategoria': 'HONORARIOS_DOCENTES',
                'descripcion': descripcion,
                'proveedor': docente.nombre_completo,
                'forma_pago': 'TRANSFERENCIA_BANCARIA',  # Por defecto
                'comprobante_nro': f"HON-{docente_id}-{datetime.now().strftime('%Y%m%d')}"
            }

            # Registrar gasto
            return self.crear_gasto(datos_gasto)

        except Exception as e:
            logger.error(f"Error al registrar pago de honorarios para docente {docente_id}: {e}")
            return False, f"Error interno: {str(e)}", None

    def obtener_resumen_mensual(
        self, 
        año: int = None, 
        mes: int = None
    ) -> Dict[str, Any]:
        """
        Obtener resumen mensual de gastos por categoría

        Args:
            año: Año (default: año actual)
            mes: Mes (1-12, default: mes actual)

        Returns:
            Diccionario con resumen
        """
        try:
            if año is None:
                año = datetime.now().year
            if mes is None:
                mes = datetime.now().month

            # Calcular fechas del mes
            fecha_inicio = date(año, mes, 1)
            if mes == 12:
                fecha_fin = date(año + 1, 1, 1)
            else:
                fecha_fin = date(año, mes + 1, 1)

            # Obtener gastos del mes
            gastos = self.obtener_gastos(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                limite=0  # Sin límite
            )

            # Calcular resumen por categoría
            resumen = {
                'año': año,
                'mes': mes,
                'mes_nombre': fecha_inicio.strftime('%B'),
                'total_gastos': len(gastos),
                'total_monto': Decimal('0.00'),
                'por_categoria': {},
                'por_subcategoria': {},
                'gasto_mayor': None,
                'gasto_menor': None
            }

            if gastos:
                # Calcular totales
                montos = []
                for gasto in gastos:
                    monto_decimal = Decimal(str(gasto.monto))
                    resumen['total_monto'] += monto_decimal
                    montos.append((monto_decimal, gasto))

                    # Por categoría
                    categoria = gasto.categoria or 'SIN_CATEGORIA'
                    if categoria not in resumen['por_categoria']:
                        resumen['por_categoria'][categoria] = {
                            'cantidad': 0,
                            'total': Decimal('0.00')
                        }
                    resumen['por_categoria'][categoria]['cantidad'] += 1
                    resumen['por_categoria'][categoria]['total'] += monto_decimal

                    # Por subcategoría
                    subcategoria = gasto.subcategoria or 'SIN_SUBCATEGORIA'
                    if subcategoria not in resumen['por_subcategoria']:
                        resumen['por_subcategoria'][subcategoria] = {
                            'cantidad': 0,
                            'total': Decimal('0.00')
                        }
                    resumen['por_subcategoria'][subcategoria]['cantidad'] += 1
                    resumen['por_subcategoria'][subcategoria]['total'] += monto_decimal

                # Encontrar gasto mayor y menor
                montos.sort(key=lambda x: x[0])
                if montos:
                    resumen['gasto_menor'] = {
                        'id': montos[0][1].id,
                        'descripcion': montos[0][1].descripcion,
                        'monto': float(montos[0][0])
                    }
                    resumen['gasto_mayor'] = {
                        'id': montos[-1][1].id,
                        'descripcion': montos[-1][1].descripcion,
                        'monto': float(montos[-1][0])
                    }

            # Formatear total como float para JSON
            resumen['total_monto'] = float(resumen['total_monto'])

            return resumen

        except Exception as e:
            logger.error(f"Error al obtener resumen mensual ({año}-{mes}): {e}")
            return {
                'año': año or datetime.now().year,
                'mes': mes or datetime.now().month,
                'error': str(e)
            }

    def obtener_estadisticas_anuales(self, año: int = None) -> Dict[str, Any]:
        """
        Obtener estadísticas de gastos por año

        Args:
            año: Año (default: año actual)

        Returns:
            Diccionario con estadísticas anuales
        """
        try:
            if año is None:
                año = datetime.now().year

            estadisticas = {
                'año': año,
                'total_gastos': 0,
                'total_monto': Decimal('0.00'),
                'por_mes': {},
                'por_categoria': {},
                'tendencia_mensual': []
            }

            # Obtener datos por mes
            for mes in range(1, 13):
                resumen_mes = self.obtener_resumen_mensual(año, mes)

                estadisticas['por_mes'][mes] = {
                    'mes_nombre': resumen_mes['mes_nombre'],
                    'total_gastos': resumen_mes['total_gastos'],
                    'total_monto': Decimal(str(resumen_mes['total_monto']))
                }

                estadisticas['total_gastos'] += resumen_mes['total_gastos']
                estadisticas['total_monto'] += Decimal(str(resumen_mes['total_monto']))

                # Acumular por categoría
                for categoria, datos_cat in resumen_mes['por_categoria'].items():
                    if categoria not in estadisticas['por_categoria']:
                        estadisticas['por_categoria'][categoria] = {
                            'cantidad': 0,
                            'total': Decimal('0.00')
                        }
                    estadisticas['por_categoria'][categoria]['cantidad'] += datos_cat['cantidad']
                    estadisticas['por_categoria'][categoria]['total'] += Decimal(str(datos_cat['total']))

            # Calcular tendencia mensual
            for mes in range(1, 13):
                estadisticas['tendencia_mensual'].append(
                    float(estadisticas['por_mes'][mes]['total_monto'])
                )

            # Formatear totales como float
            estadisticas['total_monto'] = float(estadisticas['total_monto'])

            return estadisticas

        except Exception as e:
            logger.error(f"Error al obtener estadísticas anuales ({año}): {e}")
            return {
                'año': año or datetime.now().year,
                'error': str(e)
            }

    def obtener_categorias_disponibles(self) -> List[str]:
        """
        Obtener lista de categorías disponibles

        Returns:
            Lista de categorías
        """
        try:
            return GastoOperativoModel.CATEGORIAS
        except Exception as e:
            logger.error(f"Error al obtener categorías disponibles: {e}")
            return []

    def obtener_subcategorias_por_categoria(self, categoria: str) -> List[str]:
        """
        Obtener subcategorías para una categoría específica

        Args:
            categoria: Categoría

        Returns:
            Lista de subcategorías
        """
        try:
            if categoria in GastoOperativoModel.SUBCATEGORIAS:
                return GastoOperativoModel.SUBCATEGORIAS[categoria]
            return []
        except Exception as e:
            logger.error(f"Error al obtener subcategorías para {categoria}: {e}")
            return []

    def obtener_formas_pago_disponibles(self) -> List[str]:
        """
        Obtener lista de formas de pago disponibles

        Returns:
            Lista de formas de pago
        """
        try:
            return GastoOperativoModel.FORMAS_PAGO
        except Exception as e:
            logger.error(f"Error al obtener formas de pago disponibles: {e}")
            return []

    # ==================== VALIDACIONES ====================

    def _validar_datos_gasto(
        self, 
        datos: Dict[str, Any], 
        es_actualizacion: bool = False
    ) -> List[str]:
        """
        Validar datos del gasto operativo

        Args:
            datos: Diccionario con datos a validar
            es_actualizacion: Si es una actualización (algunos campos son opcionales)

        Returns:
            Lista de mensajes de error
        """
        errores = []

        # Validar campos requeridos (solo para creación)
        if not es_actualizacion:
            campos_requeridos = ['fecha', 'monto', 'categoria', 'descripcion', 'forma_pago']
            for campo in campos_requeridos:
                if campo not in datos or not str(datos.get(campo, '')).strip():
                    errores.append(f"El campo '{campo}' es requerido")

        # Validar fecha
        if 'fecha' in datos and datos['fecha']:
            try:
                if isinstance(datos['fecha'], str):
                    datetime.strptime(datos['fecha'], '%Y-%m-%d')
            except ValueError:
                errores.append("Fecha inválida. Formato: YYYY-MM-DD")

        # Validar monto
        if 'monto' in datos and datos['monto']:
            try:
                monto = float(datos['monto'])
                if monto <= 0:
                    errores.append("El monto debe ser mayor a 0")
                if monto > 1000000:  # Límite razonable
                    errores.append("El monto no puede exceder 1,000,000")
            except (ValueError, TypeError):
                errores.append("Monto inválido. Debe ser un número")

        # Validar categoría
        if 'categoria' in datos and datos['categoria']:
            categorias_validas = self.obtener_categorias_disponibles()
            if datos['categoria'] not in categorias_validas:
                errores.append(f"Categoría inválida. Válidas: {', '.join(categorias_validas)}")

        # Validar subcategoría si se proporciona
        if 'subcategoria' in datos and datos['subcategoria'] and 'categoria' in datos:
            subcategorias_validas = self.obtener_subcategorias_por_categoria(datos['categoria'])
            if datos['subcategoria'] not in subcategorias_validas:
                errores.append(f"Subcategoría inválida para la categoría {datos['categoria']}")

        # Validar forma de pago
        if 'forma_pago' in datos and datos['forma_pago']:
            formas_validas = self.obtener_formas_pago_disponibles()
            if datos['forma_pago'] not in formas_validas:
                errores.append(f"Forma de pago inválida. Válidas: {', '.join(formas_validas)}")

        # Validar descripción (longitud)
        if 'descripcion' in datos and datos['descripcion']:
            descripcion = str(datos['descripcion']).strip()
            if len(descripcion) < 5:
                errores.append("La descripción debe tener al menos 5 caracteres")
            if len(descripcion) > 500:
                errores.append("La descripción no puede exceder 500 caracteres")

        return errores

    # ==================== EXPORTACIÓN E INFORMES ====================

    def exportar_gastos_a_csv(
        self,
        fecha_inicio: Optional[Union[str, date]] = None,
        fecha_fin: Optional[Union[str, date]] = None,
        archivo_salida: Optional[str] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Exportar gastos a archivo CSV

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            archivo_salida: Ruta del archivo de salida

        Returns:
            Tuple (éxito, mensaje, ruta_archivo)
        """
        try:
            # Obtener gastos
            gastos = self.obtener_gastos(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                limite=0
            )

            if not gastos:
                return False, "No hay gastos para exportar", None

            # Generar nombre de archivo si no se proporciona
            if not archivo_salida:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                archivo_salida = f"gastos_operativos_{timestamp}.csv"

            # Asegurar extensión .csv
            if not archivo_salida.lower().endswith('.csv'):
                archivo_salida += '.csv'

            # Crear directorio si no existe
            archivo_path = Path(archivo_salida)
            archivo_path.parent.mkdir(parents=True, exist_ok=True)

            # Escribir CSV
            with open(archivo_path, 'w', encoding='utf-8') as f:
                # Encabezados
                encabezados = [
                    'ID', 'Fecha', 'Monto', 'Categoría', 'Subcategoría',
                    'Descripción', 'Proveedor', 'N° Factura', 'Forma de Pago',
                    'N° Comprobante', 'Fecha Registro'
                ]
                f.write(';'.join(encabezados) + '\n')

                # Datos
                for gasto in gastos:
                    fila = [
                        str(gasto.id),
                        gasto.fecha,
                        str(gasto.monto).replace('.', ','),
                        gasto.categoria or '',
                        gasto.subcategoria or '',
                        f'"{gasto.descripcion}"',
                        gasto.proveedor or '',
                        gasto.nro_factura or '',
                        gasto.forma_pago,
                        gasto.comprobante_nro or '',
                        gasto.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(gasto, 'created_at') else ''
                    ]
                    f.write(';'.join(fila) + '\n')

            mensaje = f"Exportados {len(gastos)} gastos a {archivo_path}"
            return True, mensaje, str(archivo_path)

        except Exception as e:
            logger.error(f"Error al exportar gastos a CSV: {e}")
            return False, f"Error al exportar: {str(e)}", None

    def generar_informe_detallado(
        self,
        fecha_inicio: Optional[Union[str, date]] = None,
        fecha_fin: Optional[Union[str, date]] = None,
        formato: str = 'texto'
    ) -> str:
        """
        Generar informe detallado de gastos

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            formato: 'texto' o 'html'

        Returns:
            Informe formateado
        """
        try:
            # Obtener gastos
            gastos = self.obtener_gastos(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                limite=0,
                ordenar_por='fecha',
                orden_desc=False  # Ascendente
            )

            # Calcular totales
            total_monto = Decimal('0.00')
            for gasto in gastos:
                total_monto += Decimal(str(gasto.monto))

            # Rango de fechas
            rango_fechas = ""
            if fecha_inicio and fecha_fin:
                fecha_ini = fecha_inicio if isinstance(fecha_inicio, str) else fecha_inicio.isoformat()
                fecha_fin_str = fecha_fin if isinstance(fecha_fin, str) else fecha_fin.isoformat()
                rango_fechas = f"({fecha_ini} al {fecha_fin_str})"

            if formato.lower() == 'html':
                return self._generar_informe_html(gastos, total_monto, rango_fechas)
            else:
                return self._generar_informe_texto(gastos, total_monto, rango_fechas)

        except Exception as e:
            logger.error(f"Error al generar informe de gastos: {e}")
            return f"Error al generar informe: {str(e)}"

    def _generar_informe_texto(
        self, 
        gastos: List[GastoOperativoModel],
        total_monto: Decimal,
        rango_fechas: str = ""
    ) -> str:
        """Generar informe en formato texto"""
        titulo = "INFORME DETALLADO DE GASTOS OPERATIVOS"
        if rango_fechas:
            titulo += f" {rango_fechas}"

        informe = []
        informe.append("=" * 80)
        informe.append(titulo.center(80))
        informe.append("=" * 80)
        informe.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        informe.append(f"Total de gastos: {len(gastos):,}")
        informe.append(f"Total monto: Bs. {float(total_monto):,.2f}")
        informe.append("-" * 80)

        for i, gasto in enumerate(gastos, 1):
            informe.append(f"{i:3d}. {gasto.fecha} - Bs. {gasto.monto:,.2f}")
            informe.append(f"     {gasto.descripcion}")
            informe.append(f"     Categoría: {gasto.categoria}")
            if gasto.subcategoria:
                informe.append(f"     Subcategoría: {gasto.subcategoria}")
            informe.append(f"     Forma de pago: {gasto.forma_pago}")
            if gasto.comprobante_nro:
                informe.append(f"     Comprobante: {gasto.comprobante_nro}")
            informe.append("")

        # Resumen por categoría
        informe.append("-" * 80)
        informe.append("RESUMEN POR CATEGORÍA:")

        categorias = {}
        for gasto in gastos:
            categoria = gasto.categoria or 'SIN_CATEGORIA'
            if categoria not in categorias:
                categorias[categoria] = {
                    'cantidad': 0,
                    'total': Decimal('0.00')
                }
            categorias[categoria]['cantidad'] += 1
            categorias[categoria]['total'] += Decimal(str(gasto.monto))

        for categoria, datos in sorted(categorias.items()):
            porcentaje = (datos['total'] / total_monto * 100) if total_monto > 0 else 0
            informe.append(f"  {categoria}: {datos['cantidad']} gastos, Bs. {float(datos['total']):,.2f} ({porcentaje:.1f}%)")

        informe.append("=" * 80)

        return "\n".join(informe)

    def _generar_informe_html(
        self, 
        gastos: List[GastoOperativoModel],
        total_monto: Decimal,
        rango_fechas: str = ""
    ) -> str:
        """Generar informe en formato HTML"""
        titulo = "Informe Detallado de Gastos Operativos"
        if rango_fechas:
            titulo += f" {rango_fechas}"

        # Calcular resumen por categoría
        categorias = {}
        for gasto in gastos:
            categoria = gasto.categoria or 'SIN_CATEGORIA'
            if categoria not in categorias:
                categorias[categoria] = {
                    'cantidad': 0,
                    'total': Decimal('0.00')
                }
            categorias[categoria]['cantidad'] += 1
            categorias[categoria]['total'] += Decimal(str(gasto.monto))

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{titulo}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #e74c3c; padding-bottom: 10px; }}
                .header {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .gasto {{ border: 1px solid #ddd; padding: 15px; margin-bottom: 10px; border-radius: 5px; }}
                .gasto:nth-child(even) {{ background-color: #f9f9f9; }}
                .monto {{ color: #e74c3c; font-weight: bold; }}
                .categoria {{ color: #3498db; font-weight: bold; }}
                .resumen {{ background-color: #2c3e50; color: white; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .resumen-item {{ margin: 5px 0; }}
                .resumen-categoria {{ margin-left: 20px; margin-top: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #34495e; color: white; }}
                tr:hover {{ background-color: #f5f5f5; }}
            </style>
        </head>
        <body>
            <h1>{titulo}</h1>
            <div class="header">
                <p><strong>Fecha de generación:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                <p><strong>Total de gastos:</strong> {len(gastos):,}</p>
                <p><strong>Total monto:</strong> <span class="monto">Bs. {float(total_monto):,.2f}</span></p>
            </div>
        """

        # Tabla de gastos
        if gastos:
            html += """
            <h2>Detalle de Gastos</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Fecha</th>
                        <th>Monto</th>
                        <th>Categoría</th>
                        <th>Descripción</th>
                        <th>Forma de Pago</th>
                    </tr>
                </thead>
                <tbody>
            """

            for i, gasto in enumerate(gastos, 1):
                html += f"""
                <tr>
                    <td>{i}</td>
                    <td>{gasto.fecha}</td>
                    <td class="monto">Bs. {gasto.monto:,.2f}</td>
                    <td><span class="categoria">{gasto.categoria}</span></td>
                    <td>{gasto.descripcion}</td>
                    <td>{gasto.forma_pago}</td>
                </tr>
                """

            html += """
                </tbody>
            </table>
            """

        # Resumen por categoría
        if categorias:
            html += """
            <div class="resumen">
                <h2>Resumen por Categoría</h2>
            """

            for categoria, datos in sorted(categorias.items()):
                porcentaje = (float(datos['total']) / float(total_monto) * 100) if float(total_monto) > 0 else 0
                html += f"""
                <div class="resumen-categoria">
                    <p><strong>{categoria}:</strong> {datos['cantidad']} gastos, 
                    Bs. {float(datos['total']):,.2f} ({porcentaje:.1f}%)</p>
                </div>
                """

            html += "</div>"

        html += """
            <hr>
            <p><em>Generado por FormaGestPro_MVC - Módulo de Gastos Operativos</em></p>
        </body>
        </html>
        """

        return html

    def generar_constancia_egreso(
        self,
        gasto_id: int
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Generar constancia de egreso para un gasto

        Args:
            gasto_id: ID del gasto

        Returns:
            Tuple (éxito, mensaje, contenido_constancia)
        """
        try:
            gasto = self.obtener_gasto(gasto_id)
            if not gasto:
                return False, f"No se encontró gasto con ID {gasto_id}", None

            # Formatear fecha
            try:
                fecha_obj = datetime.strptime(gasto.fecha, '%Y-%m-%d')
                fecha_formateada = fecha_obj.strftime('%d de %B de %Y')
            except:
                fecha_formateada = gasto.fecha

            # Generar constancia
            constancia = f"""
            ============================================
                     CONSTANCIA DE EGRESO
            ============================================

            ID de Egreso: {gasto.id}
            Fecha: {fecha_formateada}

            DETALLES DEL GASTO:
            -------------------
            Descripción: {gasto.descripcion}
            Monto: Bs. {gasto.monto:,.2f}

            CATEGORIZACIÓN:
            ---------------
            Categoría: {gasto.categoria}
            Subcategoría: {gasto.subcategoria or 'No especificada'}

            INFORMACIÓN DE PAGO:
            --------------------
            Forma de Pago: {gasto.forma_pago}
            N° Comprobante: {gasto.comprobante_nro or 'No especificado'}

            INFORMACIÓN ADICIONAL:
            ----------------------
            Proveedor: {gasto.proveedor or 'No especificado'}
            N° Factura: {gasto.nro_factura or 'No especificado'}

            --------------------------------------------
            Fecha de Emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}

            Este documento certifica el egreso registrado
            en el sistema FormaGestPro_MVC.

            ============================================
            """

            mensaje = f"Constancia generada para gasto ID {gasto_id}"
            return True, mensaje, constancia

        except Exception as e:
            logger.error(f"Error al generar constancia para gasto {gasto_id}: {e}")
            return False, f"Error al generar constancia: {str(e)}", None