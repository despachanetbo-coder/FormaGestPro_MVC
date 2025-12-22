# app/controllers/ingresos_genericos_controller.py
"""
Controlador para la gestión de ingresos genéricos en el sistema FormaGestPro_MVC
"""

import logging
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path

from app.models.base_model import BaseModel
from app.models.ingreso_generico_model import IngresoGenericoModel

logger = logging.getLogger(__name__)

class IngresoGenericoModel(BaseModel):
    """Modelo para ingresos genéricos"""
    def __init__(self, db_path: str = None):
        """
        Inicializar controlador de ingresos genéricos

        Args:
            db_path: Ruta a la base de datos (opcional)
        """
        self.db_path = db_path

    # ==================== OPERACIONES CRUD ====================

    def crear_ingreso(self, datos: Dict[str, Any]) -> Tuple[bool, str, Optional[IngresoGenericoModel]]:
        """
        Crear un nuevo ingreso genérico

        Args:
            datos: Diccionario con los datos del ingreso

        Returns:
            Tuple (éxito, mensaje, ingreso)
        """
        try:
            # Validar datos requeridos
            errores = self._validar_datos_ingreso(datos)
            if errores:
                return False, "Errores de validación: " + "; ".join(errores), None

            # Crear el ingreso
            ingreso = IngresoGenericoModel(**datos)
            ingreso_id = ingreso.save()

            if ingreso_id:
                ingreso_creado = IngresoGenericoModel.get_by_id(ingreso_id)
                mensaje = f"Ingreso genérico registrado exitosamente (ID: {ingreso_id})"
                return True, mensaje, ingreso_creado
            else:
                return False, "Error al guardar el ingreso en la base de datos", None

        except Exception as e:
            logger.error(f"Error al crear ingreso genérico: {e}")
            return False, f"Error interno: {str(e)}", None

    def actualizar_ingreso(self, ingreso_id: int, datos: Dict[str, Any]) -> Tuple[bool, str, Optional[IngresoGenericoModel]]:
        """
        Actualizar un ingreso genérico existente

        Args:
            ingreso_id: ID del ingreso a actualizar
            datos: Diccionario con los datos a actualizar

        Returns:
            Tuple (éxito, mensaje, ingreso)
        """
        try:
            # Buscar ingreso existente
            ingreso = IngresoGenericoModel.get_by_id(ingreso_id)
            if not ingreso:
                return False, f"No se encontró ingreso con ID {ingreso_id}", None

            # Validar datos
            errores = self._validar_datos_ingreso(datos, es_actualizacion=True)
            if errores:
                return False, "Errores de validación: " + "; ".join(errores), None

            # Actualizar atributos del ingreso
            for key, value in datos.items():
                if hasattr(ingreso, key):
                    setattr(ingreso, key, value)

            # Guardar cambios
            if ingreso.save():
                mensaje = f"Ingreso genérico actualizado exitosamente (ID: {ingreso_id})"
                return True, mensaje, ingreso
            else:
                return False, "Error al guardar los cambios", None

        except Exception as e:
            logger.error(f"Error al actualizar ingreso {ingreso_id}: {e}")
            return False, f"Error interno: {str(e)}", None

    def eliminar_ingreso(self, ingreso_id: int) -> Tuple[bool, str]:
        """
        Eliminar un ingreso genérico

        Args:
            ingreso_id: ID del ingreso a eliminar

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            ingreso = IngresoGenericoModel.get_by_id(ingreso_id)
            if not ingreso:
                return False, f"No se encontró ingreso con ID {ingreso_id}"

            if ingreso.delete():
                return True, f"Ingreso eliminado exitosamente (ID: {ingreso_id})"
            else:
                return False, "Error al eliminar el ingreso"

        except Exception as e:
            logger.error(f"Error al eliminar ingreso {ingreso_id}: {e}")
            return False, f"Error interno: {str(e)}"

    # ==================== CONSULTAS ====================

    def obtener_ingreso(self, ingreso_id: int) -> Optional[IngresoGenericoModel]:
        """
        Obtener un ingreso por su ID

        Args:
            ingreso_id: ID del ingreso

        Returns:
            IngresoGenericoModel o None si no se encuentra
        """
        try:
            return IngresoGenericoModel.get_by_id(ingreso_id)
        except Exception as e:
            logger.error(f"Error al obtener ingreso {ingreso_id}: {e}")
            return None

    def obtener_ingresos(
        self, 
        fecha_inicio: Optional[Union[str, date]] = None,
        fecha_fin: Optional[Union[str, date]] = None,
        concepto: Optional[str] = None,
        forma_pago: Optional[str] = None,
        limite: int = 100,
        offset: int = 0,
        ordenar_por: str = 'fecha',
        orden_desc: bool = True
    ) -> List[IngresoGenericoModel]:
        """
        Obtener lista de ingresos con filtros

        Args:
            fecha_inicio: Fecha de inicio (YYYY-MM-DD o date)
            fecha_fin: Fecha de fin (YYYY-MM-DD o date)
            concepto: Filtrar por concepto (búsqueda parcial)
            forma_pago: Filtrar por forma de pago
            limite: Número máximo de resultados
            offset: Desplazamiento para paginación
            ordenar_por: Campo para ordenar ('fecha', 'monto', 'concepto')
            orden_desc: Orden descendente (True) o ascendente (False)

        Returns:
            Lista de ingresos
        """
        try:
            condiciones = []
            parametros = []

            if fecha_inicio:
                condiciones.append("fecha >= ?")
                fecha_inicio_str = fecha_inicio if isinstance(fecha_inicio, str) else fecha_inicio.isoformat()
                parametros.append(fecha_inicio_str)

            if fecha_fin:
                condiciones.append("fecha <= ?")
                fecha_fin_str = fecha_fin if isinstance(fecha_fin, str) else fecha_fin.isoformat()
                parametros.append(fecha_fin_str)

            if concepto:
                condiciones.append("concepto LIKE ?")
                parametros.append(f"%{concepto}%")

            if forma_pago:
                condiciones.append("forma_pago = ?")
                parametros.append(forma_pago)

            where_clause = ""
            if condiciones:
                where_clause = "WHERE " + " AND ".join(condiciones)

            # Validar campo de orden
            campos_validos = ['fecha', 'monto', 'concepto', 'created_at']
            if ordenar_por not in campos_validos:
                ordenar_por = 'fecha'

            # Construir orden
            orden = f"{ordenar_por} {'DESC' if orden_desc else 'ASC'}"

            # Construir límite
            limit_clause = ""
            if limite > 0:
                limit_clause = f"LIMIT {limite} OFFSET {offset}"

            # Ejecutar consulta
            query = f"""
                SELECT * FROM ingresos_genericos 
                {where_clause}
                ORDER BY {orden}
                {limit_clause}
            """

            ingresos = IngresoGenericoModel.query(query, parametros) if parametros else IngresoGenericoModel.query(query)
            return [IngresoGenericoModel(**ing) for ing in ingresos] if ingresos else []

        except Exception as e:
            logger.error(f"Error al obtener ingresos: {e}")
            return []

    def buscar_ingresos(
        self, 
        texto: str,
        campos: List[str] = None
    ) -> List[IngresoGenericoModel]:
        """
        Buscar ingresos por texto en múltiples campos

        Args:
            texto: Texto a buscar
            campos: Campos donde buscar (None = todos los campos de texto)

        Returns:
            Lista de ingresos que coinciden
        """
        try:
            if not texto:
                return []

            if campos is None:
                campos = ['concepto', 'descripcion', 'comprobante_nro']

            # Construir condiciones de búsqueda
            condiciones = []
            parametros = []

            for campo in campos:
                condiciones.append(f"{campo} LIKE ?")
                parametros.append(f"%{texto}%")

            where_clause = "WHERE " + " OR ".join(condiciones)
            query = f"""
                SELECT * FROM ingresos_genericos 
                {where_clause}
                ORDER BY fecha DESC, id DESC 
                LIMIT 100
            """

            ingresos = IngresoGenericoModel.query(query, parametros)
            return [IngresoGenericoModel(**ing) for ing in ingresos] if ingresos else []

        except Exception as e:
            logger.error(f"Error al buscar ingresos ({texto}): {e}")
            return []

    def contar_ingresos(
        self,
        fecha_inicio: Optional[Union[str, date]] = None,
        fecha_fin: Optional[Union[str, date]] = None
    ) -> int:
        """
        Contar número de ingresos

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin

        Returns:
            Número de ingresos
        """
        try:
            ingresos = self.obtener_ingresos(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                limite=0  # Sin límite para contar
            )
            return len(ingresos)
        except Exception as e:
            logger.error(f"Error al contar ingresos: {e}")
            return 0

    # ==================== OPERACIONES ESPECÍFICAS ====================

    def obtener_total_ingresos(
        self,
        fecha_inicio: Optional[Union[str, date]] = None,
        fecha_fin: Optional[Union[str, date]] = None
    ) -> Decimal:
        """
        Obtener el total de ingresos en un periodo

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin

        Returns:
            Total de ingresos como Decimal
        """
        try:
            return IngresoGenericoModel.obtener_total_por_periodo(fecha_inicio, fecha_fin)
        except Exception as e:
            logger.error(f"Error al obtener total de ingresos: {e}")
            return Decimal('0')

    def obtener_resumen_mensual(
        self, 
        año: int = None, 
        mes: int = None
    ) -> Dict[str, Any]:
        """
        Obtener resumen mensual de ingresos

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

            # Obtener ingresos del mes
            ingresos = self.obtener_ingresos(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                limite=0  # Sin límite
            )

            # Obtener total por forma de pago
            total_por_pago = IngresoGenericoModel.obtener_ingresos_por_forma_pago(fecha_inicio, fecha_fin)

            # Calcular resumen
            resumen = {
                'año': año,
                'mes': mes,
                'mes_nombre': fecha_inicio.strftime('%B'),
                'total_ingresos': len(ingresos),
                'total_monto': Decimal('0.00'),
                'por_forma_pago': total_por_pago,
                'ingreso_mayor': None,
                'ingreso_menor': None,
                'conceptos_frecuentes': {}
            }

            if ingresos:
                # Calcular totales
                montos = []
                conceptos = {}

                for ingreso in ingresos:
                    monto_decimal = ingreso.monto
                    resumen['total_monto'] += monto_decimal
                    montos.append((monto_decimal, ingreso))

                    # Contar conceptos
                    concepto = ingreso.concepto or 'SIN_CONCEPTO'
                    if concepto not in conceptos:
                        conceptos[concepto] = 0
                    conceptos[concepto] += 1

                # Encontrar ingreso mayor y menor
                montos.sort(key=lambda x: x[0])
                if montos:
                    resumen['ingreso_menor'] = {
                        'id': montos[0][1].id,
                        'concepto': montos[0][1].concepto,
                        'monto': float(montos[0][0])
                    }
                    resumen['ingreso_mayor'] = {
                        'id': montos[-1][1].id,
                        'concepto': montos[-1][1].concepto,
                        'monto': float(montos[-1][0])
                    }

                # Ordenar conceptos por frecuencia
                conceptos_ordenados = sorted(conceptos.items(), key=lambda x: x[1], reverse=True)
                resumen['conceptos_frecuentes'] = dict(conceptos_ordenados[:5])  # Top 5

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
        Obtener estadísticas de ingresos por año

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
                'total_ingresos': 0,
                'total_monto': Decimal('0.00'),
                'por_mes': {},
                'por_forma_pago': {},
                'tendencia_mensual': []
            }

            # Obtener datos por mes
            for mes in range(1, 13):
                resumen_mes = self.obtener_resumen_mensual(año, mes)

                estadisticas['por_mes'][mes] = {
                    'mes_nombre': resumen_mes['mes_nombre'],
                    'total_ingresos': resumen_mes['total_ingresos'],
                    'total_monto': resumen_mes['total_monto']
                }

                estadisticas['total_ingresos'] += resumen_mes['total_ingresos']
                estadisticas['total_monto'] += resumen_mes['total_monto']

                # Acumular por forma de pago
                for forma_pago, monto in resumen_mes['por_forma_pago'].items():
                    if forma_pago not in estadisticas['por_forma_pago']:
                        estadisticas['por_forma_pago'][forma_pago] = Decimal('0.00')
                    estadisticas['por_forma_pago'][forma_pago] += monto

            # Calcular tendencia mensual
            for mes in range(1, 13):
                estadisticas['tendencia_mensual'].append(
                    float(estadisticas['por_mes'][mes]['total_monto'])
                )

            return estadisticas

        except Exception as e:
            logger.error(f"Error al obtener estadísticas anuales ({año}): {e}")
            return {
                'año': año or datetime.now().year,
                'error': str(e)
            }

    def obtener_formas_pago_disponibles(self) -> List[str]:
        """
        Obtener lista de formas de pago disponibles

        Returns:
            Lista de formas de pago
        """
        return IngresoGenericoModel.FORMAS_PAGO

    def registrar_ingreso_rapido(
        self,
        monto: float,
        concepto: str,
        forma_pago: str = 'EFECTIVO',
        descripcion: str = "",
        comprobante_nro: str = ""
    ) -> Tuple[bool, str, Optional[IngresoGenericoModel]]:
        """
        Registrar un ingreso rápido con valores por defecto

        Args:
            monto: Monto del ingreso
            concepto: Concepto del ingreso
            forma_pago: Forma de pago (default: EFECTIVO)
            descripcion: Descripción adicional (opcional)
            comprobante_nro: Número de comprobante (opcional)

        Returns:
            Tuple (éxito, mensaje, ingreso)
        """
        try:
            # Preparar datos
            datos = {
                'fecha': datetime.now().date().isoformat(),
                'monto': monto,
                'concepto': concepto,
                'descripcion': descripcion,
                'forma_pago': forma_pago,
                'comprobante_nro': comprobante_nro
            }

            # Registrar ingreso
            return self.crear_ingreso(datos)

        except Exception as e:
            logger.error(f"Error al registrar ingreso rápido: {e}")
            return False, f"Error interno: {str(e)}", None

    # ==================== VALIDACIONES ====================

    def _validar_datos_ingreso(
        self, 
        datos: Dict[str, Any], 
        es_actualizacion: bool = False
    ) -> List[str]:
        """
        Validar datos del ingreso genérico

        Args:
            datos: Diccionario con datos a validar
            es_actualizacion: Si es una actualización (algunos campos son opcionales)

        Returns:
            Lista de mensajes de error
        """
        errores = []

        # Validar campos requeridos (solo para creación)
        if not es_actualizacion:
            campos_requeridos = ['fecha', 'monto', 'concepto', 'forma_pago']
            for campo in campos_requeridos:
                if campo not in datos or not str(datos.get(campo, '')).strip():
                    errores.append(f"El campo '{campo}' es requerido")

        # Validar fecha
        if 'fecha' in datos and datos['fecha']:
            try:
                if isinstance(datos['fecha'], str):
                    fecha_obj = datetime.strptime(datos['fecha'], '%Y-%m-%d').date()
                    # Verificar que no sea una fecha futura
                    if fecha_obj > date.today():
                        errores.append("La fecha no puede ser futura")
            except ValueError:
                errores.append("Fecha inválida. Formato: YYYY-MM-DD")

        # Validar monto
        if 'monto' in datos and datos['monto']:
            try:
                monto = Decimal(str(datos['monto']))
                if monto <= 0:
                    errores.append("El monto debe ser mayor a 0")
                if monto > 1000000:  # Límite razonable
                    errores.append("El monto no puede exceder 1,000,000")
            except (ValueError, TypeError):
                errores.append("Monto inválido. Debe ser un número")

        # Validar concepto
        if 'concepto' in datos and datos['concepto']:
            concepto = str(datos['concepto']).strip()
            if len(concepto) < 3:
                errores.append("El concepto debe tener al menos 3 caracteres")
            if len(concepto) > 200:
                errores.append("El concepto no puede exceder 200 caracteres")

        # Validar descripción si se proporciona
        if 'descripcion' in datos and datos['descripcion']:
            descripcion = str(datos['descripcion']).strip()
            if len(descripcion) > 500:
                errores.append("La descripción no puede exceder 500 caracteres")

        # Validar forma de pago
        if 'forma_pago' in datos and datos['forma_pago']:
            formas_validas = self.obtener_formas_pago_disponibles()
            if datos['forma_pago'] not in formas_validas:
                errores.append(f"Forma de pago inválida. Válidas: {', '.join(formas_validas)}")

        # Validar número de comprobante si se proporciona
        if 'comprobante_nro' in datos and datos['comprobante_nro']:
            comprobante = str(datos['comprobante_nro']).strip()
            if len(comprobante) > 50:
                errores.append("El número de comprobante no puede exceder 50 caracteres")

        # Validar registrado_por si se proporciona
        if 'registrado_por' in datos and datos['registrado_por']:
            try:
                registrado_por = int(datos['registrado_por'])
                if registrado_por <= 0:
                    errores.append("ID de usuario inválido")
            except (ValueError, TypeError):
                errores.append("ID de usuario debe ser un número entero")

        return errores

    # ==================== EXPORTACIÓN E INFORMES ====================

    def exportar_ingresos_a_csv(
        self,
        fecha_inicio: Optional[Union[str, date]] = None,
        fecha_fin: Optional[Union[str, date]] = None,
        archivo_salida: Optional[str] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Exportar ingresos a archivo CSV

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            archivo_salida: Ruta del archivo de salida

        Returns:
            Tuple (éxito, mensaje, ruta_archivo)
        """
        try:
            # Obtener ingresos
            ingresos = self.obtener_ingresos(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                limite=0
            )

            if not ingresos:
                return False, "No hay ingresos para exportar", None

            # Generar nombre de archivo si no se proporciona
            if not archivo_salida:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                archivo_salida = f"ingresos_genericos_{timestamp}.csv"

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
                    'ID', 'Fecha', 'Monto', 'Concepto', 'Descripción',
                    'Forma de Pago', 'N° Comprobante', 'Registrado por', 'Fecha Registro'
                ]
                f.write(';'.join(encabezados) + '\n')

                # Datos
                for ingreso in ingresos:
                    # Formatear fecha de registro
                    fecha_reg = ""
                    if hasattr(ingreso, 'created_at') and ingreso.created_at:
                        if isinstance(ingreso.created_at, str):
                            fecha_reg = ingreso.created_at
                        else:
                            fecha_reg = ingreso.created_at.strftime('%Y-%m-%d %H:%M:%S')

                    fila = [
                        str(ingreso.id),
                        ingreso.fecha,
                        str(ingreso.monto).replace('.', ','),
                        f'"{ingreso.concepto}"',
                        f'"{ingreso.descripcion or ""}"',
                        ingreso.forma_pago,
                        ingreso.comprobante_nro or '',
                        str(ingreso.registrado_por) if ingreso.registrado_por else '',
                        fecha_reg
                    ]
                    f.write(';'.join(fila) + '\n')

            mensaje = f"Exportados {len(ingresos)} ingresos a {archivo_path}"
            return True, mensaje, str(archivo_path)

        except Exception as e:
            logger.error(f"Error al exportar ingresos a CSV: {e}")
            return False, f"Error al exportar: {str(e)}", None

    def generar_informe_detallado(
        self,
        fecha_inicio: Optional[Union[str, date]] = None,
        fecha_fin: Optional[Union[str, date]] = None,
        formato: str = 'texto'
    ) -> str:
        """
        Generar informe detallado de ingresos

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            formato: 'texto' o 'html'

        Returns:
            Informe formateado
        """
        try:
            # Obtener ingresos
            ingresos = self.obtener_ingresos(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                limite=0,
                ordenar_por='fecha',
                orden_desc=False  # Ascendente
            )

            # Obtener totales y distribución por forma de pago
            total_monto = self.obtener_total_ingresos(fecha_inicio, fecha_fin)
            ingresos_por_pago = IngresoGenericoModel.obtener_ingresos_por_forma_pago(fecha_inicio, fecha_fin)

            # Rango de fechas
            rango_fechas = ""
            if fecha_inicio and fecha_fin:
                fecha_ini = fecha_inicio if isinstance(fecha_inicio, str) else fecha_inicio.isoformat()
                fecha_fin_str = fecha_fin if isinstance(fecha_fin, str) else fecha_fin.isoformat()
                rango_fechas = f"({fecha_ini} al {fecha_fin_str})"

            if formato.lower() == 'html':
                return self._generar_informe_html(ingresos, total_monto, ingresos_por_pago, rango_fechas)
            else:
                return self._generar_informe_texto(ingresos, total_monto, ingresos_por_pago, rango_fechas)

        except Exception as e:
            logger.error(f"Error al generar informe de ingresos: {e}")
            return f"Error al generar informe: {str(e)}"

    def _generar_informe_texto(
        self, 
        ingresos: List[IngresoGenericoModel],
        total_monto: Decimal,
        ingresos_por_pago: Dict[str, Decimal],
        rango_fechas: str = ""
    ) -> str:
        """Generar informe en formato texto"""
        titulo = "INFORME DETALLADO DE INGRESOS GENÉRICOS"
        if rango_fechas:
            titulo += f" {rango_fechas}"

        informe = []
        informe.append("=" * 80)
        informe.append(titulo.center(80))
        informe.append("=" * 80)
        informe.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        informe.append(f"Total de ingresos: {len(ingresos):,}")
        informe.append(f"Total monto: Bs. {float(total_monto):,.2f}")
        informe.append("-" * 80)

        for i, ingreso in enumerate(ingresos, 1):
            informe.append(f"{i:3d}. {ingreso.fecha} - Bs. {float(ingreso.monto):,.2f}")
            informe.append(f"     {ingreso.concepto}")
            if ingreso.descripcion:
                informe.append(f"     Descripción: {ingreso.descripcion}")
            informe.append(f"     Forma de pago: {ingreso.forma_pago}")
            if ingreso.comprobante_nro:
                informe.append(f"     Comprobante: {ingreso.comprobante_nro}")
            informe.append("")

        # Resumen por forma de pago
        informe.append("-" * 80)
        informe.append("RESUMEN POR FORMA DE PAGO:")

        for forma_pago, monto in ingresos_por_pago.items():
            porcentaje = (monto / total_monto * 100) if total_monto > 0 else 0
            informe.append(f"  {forma_pago}: Bs. {float(monto):,.2f} ({porcentaje:.1f}%)")

        informe.append("=" * 80)

        return "\n".join(informe)

    def _generar_informe_html(
        self, 
        ingresos: List[IngresoGenericoModel],
        total_monto: Decimal,
        ingresos_por_pago: Dict[str, Decimal],
        rango_fechas: str = ""
    ) -> str:
        """Generar informe en formato HTML"""
        titulo = "Informe Detallado de Ingresos Genéricos"
        if rango_fechas:
            titulo += f" {rango_fechas}"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{titulo}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #27ae60; padding-bottom: 10px; }}
                .header {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .ingreso {{ border: 1px solid #ddd; padding: 15px; margin-bottom: 10px; border-radius: 5px; }}
                .ingreso:nth-child(even) {{ background-color: #f9f9f9; }}
                .monto {{ color: #27ae60; font-weight: bold; }}
                .concepto {{ color: #3498db; font-weight: bold; }}
                .resumen {{ background-color: #2c3e50; color: white; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .resumen-item {{ margin: 5px 0; }}
                .resumen-pago {{ margin-left: 20px; margin-top: 10px; }}
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
                <p><strong>Total de ingresos:</strong> {len(ingresos):,}</p>
                <p><strong>Total monto:</strong> <span class="monto">Bs. {float(total_monto):,.2f}</span></p>
            </div>
        """

        # Tabla de ingresos
        if ingresos:
            html += """
            <h2>Detalle de Ingresos</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Fecha</th>
                        <th>Monto</th>
                        <th>Concepto</th>
                        <th>Forma de Pago</th>
                        <th>Descripción</th>
                    </tr>
                </thead>
                <tbody>
            """

            for i, ingreso in enumerate(ingresos, 1):
                html += f"""
                <tr>
                    <td>{i}</td>
                    <td>{ingreso.fecha_formateada}</td>
                    <td class="monto">Bs. {float(ingreso.monto):,.2f}</td>
                    <td><span class="concepto">{ingreso.concepto}</span></td>
                    <td>{ingreso.forma_pago}</td>
                    <td>{ingreso.descripcion or '-'}</td>
                </tr>
                """

            html += """
                </tbody>
            </table>
            """

        # Resumen por forma de pago
        if ingresos_por_pago:
            html += """
            <div class="resumen">
                <h2>Resumen por Forma de Pago</h2>
            """

            for forma_pago, monto in ingresos_por_pago.items():
                porcentaje = (float(monto) / float(total_monto) * 100) if float(total_monto) > 0 else 0
                html += f"""
                <div class="resumen-pago">
                    <p><strong>{forma_pago}:</strong> Bs. {float(monto):,.2f} ({porcentaje:.1f}%)</p>
                </div>
                """

            html += "</div>"

        html += """
            <hr>
            <p><em>Generado por FormaGestPro_MVC - Módulo de Ingresos Genéricos</em></p>
        </body>
        </html>
        """

        return html