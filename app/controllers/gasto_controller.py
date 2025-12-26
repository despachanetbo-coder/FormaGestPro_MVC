# app/controllers/gasto_controller.py
"""
Controlador de Gastos para PostgreSQL - FormaGestPro
Reemplaza y mejora GastosOperativosController
Gestiona todos los gastos del sistema con integración PostgreSQL
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal

# Modelos PostgreSQL
from app.models.gasto_model import GastoModel
from app.models.comprobante_adjunto_model import ComprobanteAdjuntoModel
from app.models.movimiento_caja_model import MovimientoCajaModel
from app.database.connection import db

logger = logging.getLogger(__name__)


class GastoController:
    """
    Controlador para la gestión de gastos del sistema.

    Responsabilidades:
    - CRUD de gastos operativos
    - Categorización y clasificación de gastos
    - Gestión de comprobantes adjuntos
    - Reportes y estadísticas financieras
    - Integración con movimientos de caja
    """

    # Categorías predefinidas para gastos
    CATEGORIAS_PREDEFINIDAS = [
        "SERVICIOS BASICOS",
        "ALQUILERES",
        "SUELDOS Y SALARIOS",
        "MATERIALES OFICINA",
        "EQUIPOS Y TECNOLOGIA",
        "MANTENIMIENTO",
        "TRANSPORTE Y VIATICOS",
        "PUBLICIDAD Y MARKETING",
        "CAPACITACION",
        "IMPUESTOS Y TRIBUTOS",
        "SEGUROS",
        "SERVICIOS PROFESIONALES",
        "OTROS GASTOS",
    ]

    # Subcategorías comunes
    SUBCATEGORIAS = {
        "SERVICIOS BASICOS": ["AGUA", "LUZ", "INTERNET", "TELEFONIA"],
        "ALQUILERES": ["OFICINA", "ALMACEN", "EQUIPOS"],
        "SUELDOS Y SALARIOS": ["DOCENTES", "ADMINISTRATIVOS", "LIMPEZA"],
        "MATERIALES OFICINA": ["PAPELERIA", "TONER", "MOBILIARIO"],
        "EQUIPOS Y TECNOLOGIA": ["COMPUTADORAS", "SOFTWARE", "IMPRESORAS"],
    }

    def __init__(self):
        """Inicializa el controlador con los modelos necesarios"""
        self.gasto_model = GastoModel
        self.comprobante_model = ComprobanteAdjuntoModel
        self.movimiento_model = MovimientoCajaModel

    # ============================================================================
    # MÉTODOS CRUD - GASTOS
    # ============================================================================

    def crear_gasto(self, datos: Dict) -> Dict[str, Any]:
        """
        Crea un nuevo gasto en el sistema.

        Args:
            datos: Diccionario con los datos del gasto

        Returns:
            Dict con resultado de la operación
        """
        try:
            # Validar datos requeridos
            campos_requeridos = ["fecha", "monto", "categoria", "descripcion"]
            for campo in campos_requeridos:
                if campo not in datos or not datos[campo]:
                    return {"success": False, "message": f"❌ Campo requerido: {campo}"}

            # Validar monto positivo
            try:
                monto = float(datos["monto"])
                if monto <= 0:
                    return {
                        "success": False,
                        "message": "❌ El monto debe ser mayor a 0",
                    }
            except (ValueError, TypeError):
                return {"success": False, "message": "❌ Monto inválido"}

            # Validar categoría
            categoria = datos["categoria"].upper()
            if categoria not in self.CATEGORIAS_PREDEFINIDAS and categoria != "OTROS":
                logger.warning(f"⚠️ Categoría no predefinida usada: {categoria}")

            # Crear número de comprobante automático si no se proporciona
            if "nro_factura" not in datos or not datos["nro_factura"]:
                # Generar número secuencial
                ultimo_gasto = self.gasto_model.find_all(limit=1)
                if ultimo_gasto:
                    ultimo_numero = getattr(ultimo_gasto[0], "nro_factura", "GST-0000")
                    if ultimo_numero and ultimo_numero.startswith("GST-"):
                        try:
                            numero = int(ultimo_numero.split("-")[1]) + 1
                            datos["nro_factura"] = f"GST-{numero:04d}"
                        except:
                            datos["nro_factura"] = f"GST-0001"
                else:
                    datos["nro_factura"] = f"GST-0001"

            # Crear gasto
            gasto = self.gasto_model(**datos)
            gasto_id = gasto.save()

            # Registrar movimiento de caja automático
            self._registrar_movimiento_caja(gasto_id, gasto.monto, gasto.descripcion)

            logger.info(f"✅ Gasto creado: {gasto.nro_factura} - ${gasto.monto:.2f}")

            return {
                "success": True,
                "message": "✅ Gasto registrado exitosamente",
                "data": {
                    "gasto_id": gasto_id,
                    "nro_factura": gasto.nro_factura,
                    "monto": float(gasto.monto),
                    "fecha": gasto.fecha,
                    "categoria": gasto.categoria,
                },
            }

        except ValueError as e:
            return {"success": False, "message": f"❌ {str(e)}"}
        except Exception as e:
            logger.error(f"Error creando gasto: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def obtener_gasto(self, gasto_id: int) -> Dict[str, Any]:
        """
        Obtiene un gasto por su ID.

        Args:
            gasto_id: ID del gasto

        Returns:
            Dict con el gasto encontrado
        """
        try:
            gasto = self.gasto_model.find_by_id(gasto_id)
            if not gasto:
                return {"success": False, "message": "❌ Gasto no encontrado"}

            # Enriquecer datos
            datos_gasto = gasto.to_dict()

            # Obtener comprobantes adjuntos
            try:
                comprobantes = self.comprobante_model.buscar_por_origen(
                    "GASTO", gasto_id
                )
                datos_gasto["comprobantes"] = [c.to_dict() for c in comprobantes]
            except Exception as e:
                logger.warning(f"No se pudieron obtener comprobantes: {e}")
                datos_gasto["comprobantes"] = []

            # Obtener movimiento de caja asociado
            try:
                movimiento = self.movimiento_model.buscar_por_origen("GASTO", gasto_id)
                if movimiento:
                    datos_gasto["movimiento_caja"] = movimiento.to_dict()
            except Exception as e:
                logger.warning(f"No se pudo obtener movimiento de caja: {e}")

            return {"success": True, "data": datos_gasto}

        except Exception as e:
            logger.error(f"Error obteniendo gasto: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def actualizar_gasto(self, gasto_id: int, datos: Dict) -> Dict[str, Any]:
        """
        Actualiza un gasto existente.

        Args:
            gasto_id: ID del gasto a actualizar
            datos: Campos a actualizar

        Returns:
            Dict con resultado de la operación
        """
        try:
            gasto = self.gasto_model.find_by_id(gasto_id)
            if not gasto:
                return {"success": False, "message": "❌ Gasto no encontrado"}

            # Campos que no se pueden actualizar
            campos_bloqueados = ["id", "created_at", "registrado_por"]
            for campo in campos_bloqueados:
                if campo in datos:
                    del datos[campo]

            # Validar monto si se actualiza
            if "monto" in datos:
                try:
                    nuevo_monto = float(datos["monto"])
                    if nuevo_monto <= 0:
                        return {
                            "success": False,
                            "message": "❌ El monto debe ser mayor a 0",
                        }

                    # Actualizar movimiento de caja si el monto cambia
                    if abs(nuevo_monto - gasto.monto) > 0.01:
                        self._actualizar_movimiento_caja(gasto_id, nuevo_monto)
                except (ValueError, TypeError):
                    return {"success": False, "message": "❌ Monto inválido"}

            # Actualizar campos
            for campo, valor in datos.items():
                if hasattr(gasto, campo):
                    setattr(gasto, campo, valor)

            # Guardar cambios
            gasto.save()

            logger.info(f"✏️ Gasto actualizado: {gasto.nro_factura}")

            return {
                "success": True,
                "message": "✅ Gasto actualizado exitosamente",
                "data": gasto.to_dict(),
            }

        except ValueError as e:
            return {"success": False, "message": f"❌ {str(e)}"}
        except Exception as e:
            logger.error(f"Error actualizando gasto: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def eliminar_gasto(self, gasto_id: int, motivo: str = None) -> Dict[str, Any]:
        """
        Elimina un gasto del sistema.

        Args:
            gasto_id: ID del gasto a eliminar
            motivo: Motivo de la eliminación

        Returns:
            Dict con resultado de la operación
        """
        try:
            gasto = self.gasto_model.find_by_id(gasto_id)
            if not gasto:
                return {"success": False, "message": "❌ Gasto no encontrado"}

            # Eliminar movimiento de caja asociado
            self._eliminar_movimiento_caja(gasto_id)

            # Eliminar comprobantes adjuntos
            try:
                comprobantes = self.comprobante_model.buscar_por_origen(
                    "GASTO", gasto_id
                )
                for comprobante in comprobantes:
                    comprobante.delete()
            except Exception as e:
                logger.warning(f"Error eliminando comprobantes: {e}")

            # Eliminar gasto
            if gasto.delete():
                # Registrar en auditoría
                logger.info(
                    f"🗑️ Gasto eliminado: {gasto.nro_factura} - Motivo: {motivo}"
                )

                return {
                    "success": True,
                    "message": "✅ Gasto eliminado exitosamente",
                    "data": {
                        "gasto_id": gasto_id,
                        "nro_factura": gasto.nro_factura,
                        "motivo": motivo,
                    },
                }
            else:
                return {"success": False, "message": "❌ No se pudo eliminar el gasto"}

        except Exception as e:
            logger.error(f"Error eliminando gasto: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def listar_gastos(self, filtros: Dict = None) -> Dict[str, Any]:
        """
        Lista gastos con filtros opcionales.

        Args:
            filtros: Diccionario con filtros

        Returns:
            Dict con lista de gastos
        """
        try:
            # Obtener todos los gastos
            gastos = self.gasto_model.find_all(limit=1000)

            # Aplicar filtros si existen
            if filtros:
                gastos_filtrados = []
                for gasto in gastos:
                    cumple_filtro = True

                    # Filtro por categoría
                    if "categoria" in filtros and filtros["categoria"]:
                        if gasto.categoria.upper() != filtros["categoria"].upper():
                            cumple_filtro = False

                    # Filtro por subcategoría
                    if "subcategoria" in filtros and filtros["subcategoria"]:
                        if (gasto.subcategoria or "").upper() != filtros[
                            "subcategoria"
                        ].upper():
                            cumple_filtro = False

                    # Filtro por proveedor
                    if "proveedor" in filtros and filtros["proveedor"]:
                        proveedor_busqueda = filtros["proveedor"].lower()
                        proveedor_gasto = (gasto.proveedor or "").lower()
                        if proveedor_busqueda not in proveedor_gasto:
                            cumple_filtro = False

                    # Filtro por fecha
                    if "fecha_inicio" in filtros and "fecha_fin" in filtros:
                        if not (
                            filtros["fecha_inicio"]
                            <= gasto.fecha
                            <= filtros["fecha_fin"]
                        ):
                            cumple_filtro = False

                    # Filtro por forma de pago
                    if "forma_pago" in filtros and filtros["forma_pago"]:
                        if gasto.forma_pago != filtros["forma_pago"]:
                            cumple_filtro = False

                    # Filtro por monto mínimo
                    if "monto_minimo" in filtros and filtros["monto_minimo"]:
                        if gasto.monto < float(filtros["monto_minimo"]):
                            cumple_filtro = False

                    # Filtro por monto máximo
                    if "monto_maximo" in filtros and filtros["monto_maximo"]:
                        if gasto.monto > float(filtros["monto_maximo"]):
                            cumple_filtro = False

                    if cumple_filtro:
                        gastos_filtrados.append(gasto)

                gastos = gastos_filtrados

            # Ordenar por fecha descendente
            gastos.sort(key=lambda x: x.fecha, reverse=True)

            # Convertir a diccionarios
            gastos_data = [g.to_dict() for g in gastos]

            # Calcular estadísticas
            total_gastos = sum(g.monto for g in gastos)
            por_categoria = {}
            por_forma_pago = {}

            for gasto in gastos:
                # Por categoría
                categoria = gasto.categoria
                por_categoria[categoria] = por_categoria.get(categoria, 0) + gasto.monto

                # Por forma de pago
                forma_pago = gasto.forma_pago or "NO ESPECIFICADO"
                por_forma_pago[forma_pago] = (
                    por_forma_pago.get(forma_pago, 0) + gasto.monto
                )

            return {
                "success": True,
                "data": {
                    "gastos": gastos_data,
                    "estadisticas": {
                        "total_registros": len(gastos_data),
                        "total_monto": float(total_gastos),
                        "promedio_monto": (
                            float(total_gastos / len(gastos_data)) if gastos_data else 0
                        ),
                        "por_categoria": {
                            k: float(v) for k, v in por_categoria.items()
                        },
                        "por_forma_pago": {
                            k: float(v) for k, v in por_forma_pago.items()
                        },
                        "gasto_maximo": (
                            float(max(g.monto for g in gastos)) if gastos else 0
                        ),
                        "gasto_minimo": (
                            float(min(g.monto for g in gastos)) if gastos else 0
                        ),
                    },
                    "filtros_aplicados": bool(filtros),
                    "categorias_disponibles": self.CATEGORIAS_PREDEFINIDAS,
                },
            }

        except Exception as e:
            logger.error(f"Error listando gastos: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    # ============================================================================
    # MÉTODOS DE BÚSQUEDA ESPECÍFICA
    # ============================================================================

    def buscar_gastos_por_categoria(
        self, categoria: str, fecha_inicio: str = None, fecha_fin: str = None
    ) -> Dict[str, Any]:
        """
        Busca gastos por categoría.

        Args:
            categoria: Categoría a buscar
            fecha_inicio: Fecha de inicio (opcional)
            fecha_fin: Fecha de fin (opcional)

        Returns:
            Dict con gastos de la categoría
        """
        try:
            # Construir filtros
            filtros = {"categoria": categoria.upper()}
            if fecha_inicio and fecha_fin:
                filtros.update({"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin})

            return self.listar_gastos(filtros)

        except Exception as e:
            logger.error(f"Error buscando gastos por categoría: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def buscar_gastos_por_proveedor(self, proveedor: str) -> Dict[str, Any]:
        """
        Busca gastos por proveedor.

        Args:
            proveedor: Nombre del proveedor

        Returns:
            Dict con gastos del proveedor
        """
        try:
            # Buscar en base de datos
            query = """
                SELECT * FROM gastos 
                WHERE proveedor ILIKE %s 
                ORDER BY fecha DESC
            """
            results = db.fetch_all(query, (f"%{proveedor}%",))

            if not results:
                return {
                    "success": True,
                    "data": {
                        "gastos": [],
                        "total_registros": 0,
                        "total_monto": 0,
                        "proveedor": proveedor,
                    },
                }

            # Convertir a modelos
            gastos = [self.gasto_model(**row) for row in results]
            gastos_data = [g.to_dict() for g in gastos]
            total_monto = sum(g.monto for g in gastos)

            return {
                "success": True,
                "data": {
                    "gastos": gastos_data,
                    "total_registros": len(gastos_data),
                    "total_monto": float(total_monto),
                    "proveedor": proveedor,
                    "primer_gasto": gastos[0].fecha if gastos else None,
                    "ultimo_gasto": gastos[-1].fecha if gastos else None,
                },
            }

        except Exception as e:
            logger.error(f"Error buscando gastos por proveedor: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def buscar_gastos_por_periodo(
        self, fecha_inicio: str, fecha_fin: str
    ) -> Dict[str, Any]:
        """
        Busca gastos en un período específico.

        Args:
            fecha_inicio: Fecha de inicio (YYYY-MM-DD)
            fecha_fin: Fecha de fin (YYYY-MM-DD)

        Returns:
            Dict con gastos del período
        """
        try:
            return self.listar_gastos(
                {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}
            )

        except Exception as e:
            logger.error(f"Error buscando gastos por período: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    # ============================================================================
    # MÉTODOS DE ESTADÍSTICAS Y REPORTES
    # ============================================================================

    def obtener_estadisticas_mensuales(
        self, año: int, mes: int = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de gastos mensuales.

        Args:
            año: Año a consultar
            mes: Mes específico (opcional)

        Returns:
            Dict con estadísticas mensuales
        """
        try:
            # Construir rango de fechas
            if mes:
                # Mes específico
                fecha_inicio = f"{año}-{mes:02d}-01"
                ultimo_dia = 31 if mes in [1, 3, 5, 7, 8, 10, 12] else 30
                if mes == 2:
                    ultimo_dia = (
                        29
                        if (año % 4 == 0 and año % 100 != 0) or (año % 400 == 0)
                        else 28
                    )
                fecha_fin = f"{año}-{mes:02d}-{ultimo_dia}"

                return self._estadisticas_por_mes(
                    fecha_inicio, fecha_fin, f"{año}-{mes:02d}"
                )
            else:
                # Todo el año
                resultados_meses = []
                total_anual = 0

                for m in range(1, 13):
                    fecha_inicio = f"{año}-{m:02d}-01"
                    ultimo_dia = 31 if m in [1, 3, 5, 7, 8, 10, 12] else 30
                    if m == 2:
                        ultimo_dia = (
                            29
                            if (año % 4 == 0 and año % 100 != 0) or (año % 400 == 0)
                            else 28
                        )
                    fecha_fin = f"{año}-{m:02d}-{ultimo_dia}"

                    estadisticas_mes = self._estadisticas_por_mes(
                        fecha_inicio, fecha_fin, f"{año}-{m:02d}"
                    )
                    if estadisticas_mes["success"]:
                        resultados_meses.append(estadisticas_mes["data"])
                        total_anual += estadisticas_mes["data"]["total_monto"]

                return {
                    "success": True,
                    "data": {
                        "año": año,
                        "total_anual": float(total_anual),
                        "promedio_mensual": (
                            float(total_anual / 12) if total_anual > 0 else 0
                        ),
                        "meses": resultados_meses,
                        "mes_mayor_gasto": (
                            max(resultados_meses, key=lambda x: x["total_monto"])
                            if resultados_meses
                            else None
                        ),
                        "mes_menor_gasto": (
                            min(resultados_meses, key=lambda x: x["total_monto"])
                            if resultados_meses
                            else None
                        ),
                    },
                }

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas mensuales: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def _estadisticas_por_mes(
        self, fecha_inicio: str, fecha_fin: str, mes_label: str
    ) -> Dict[str, Any]:
        """Estadísticas internas por mes"""
        try:
            # Obtener gastos del mes
            resultado = self.buscar_gastos_por_periodo(fecha_inicio, fecha_fin)

            if not resultado["success"]:
                return resultado

            datos = resultado["data"]

            # Calcular estadísticas adicionales
            if datos["gastos"]:
                gastos_por_dia = {}
                for gasto in datos["gastos"]:
                    dia = gasto["fecha"]
                    gastos_por_dia[dia] = gastos_por_dia.get(dia, 0) + gasto["monto"]

                dias_con_gastos = list(gastos_por_dia.keys())
                dias_con_gastos.sort()

                return {
                    "success": True,
                    "data": {
                        "mes": mes_label,
                        "fecha_inicio": fecha_inicio,
                        "fecha_fin": fecha_fin,
                        "total_registros": datos["estadisticas"]["total_registros"],
                        "total_monto": datos["estadisticas"]["total_monto"],
                        "promedio_diario": (
                            datos["estadisticas"]["total_monto"] / len(dias_con_gastos)
                            if dias_con_gastos
                            else 0
                        ),
                        "dias_con_gastos": len(dias_con_gastos),
                        "distribucion_categorias": datos["estadisticas"][
                            "por_categoria"
                        ],
                        "distribucion_pago": datos["estadisticas"]["por_forma_pago"],
                        "gasto_maximo": datos["estadisticas"]["gasto_maximo"],
                        "gasto_minimo": datos["estadisticas"]["gasto_minimo"],
                    },
                }
            else:
                return {
                    "success": True,
                    "data": {
                        "mes": mes_label,
                        "fecha_inicio": fecha_inicio,
                        "fecha_fin": fecha_fin,
                        "total_registros": 0,
                        "total_monto": 0,
                        "promedio_diario": 0,
                        "dias_con_gastos": 0,
                        "distribucion_categorias": {},
                        "distribucion_pago": {},
                        "gasto_maximo": 0,
                        "gasto_minimo": 0,
                    },
                }

        except Exception as e:
            logger.error(f"Error en estadísticas por mes: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def obtener_resumen_anual(self, año: int) -> Dict[str, Any]:
        """
        Obtiene resumen anual de gastos.

        Args:
            año: Año a consultar

        Returns:
            Dict con resumen anual
        """
        try:
            estadisticas = self.obtener_estadisticas_mensuales(año)

            if not estadisticas["success"]:
                return estadisticas

            datos = estadisticas["data"]

            # Calcular top categorías
            categorias_totales = {}
            for mes in datos["meses"]:
                for categoria, monto in mes["distribucion_categorias"].items():
                    categorias_totales[categoria] = (
                        categorias_totales.get(categoria, 0) + monto
                    )

            top_categorias = sorted(
                categorias_totales.items(), key=lambda x: x[1], reverse=True
            )[:5]

            # Calcular evolución mensual
            evolucion_mensual = []
            for mes in datos["meses"]:
                evolucion_mensual.append(
                    {
                        "mes": mes["mes"],
                        "total": mes["total_monto"],
                        "registros": mes["total_registros"],
                    }
                )

            return {
                "success": True,
                "data": {
                    "año": año,
                    "resumen": {
                        "total_anual": datos["total_anual"],
                        "promedio_mensual": datos["promedio_mensual"],
                        "total_registros": sum(
                            m["total_registros"] for m in datos["meses"]
                        ),
                        "meses_con_gastos": len(
                            [m for m in datos["meses"] if m["total_monto"] > 0]
                        ),
                    },
                    "top_categorias": [
                        {"categoria": k, "monto": float(v)} for k, v in top_categorias
                    ],
                    "evolucion_mensual": evolucion_mensual,
                    "mes_mas_costoso": datos["mes_mayor_gasto"],
                    "mes_menos_costoso": datos["mes_menor_gasto"],
                    "distribucion_anual": {
                        "por_categoria": {
                            k: float(v) for k, v in categorias_totales.items()
                        },
                        "por_mes": {m["mes"]: m["total_monto"] for m in datos["meses"]},
                    },
                },
            }

        except Exception as e:
            logger.error(f"Error obteniendo resumen anual: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def generar_reporte_gastos(self, filtros: Dict) -> Dict[str, Any]:
        """
        Genera un reporte detallado de gastos.

        Args:
            filtros: Filtros para el reporte

        Returns:
            Dict con reporte completo
        """
        try:
            # Obtener gastos filtrados
            resultado = self.listar_gastos(filtros)

            if not resultado["success"]:
                return resultado

            # Enriquecer reporte
            reporte = {
                "filtros": filtros,
                "fecha_generacion": datetime.now().isoformat(),
                "resumen": resultado["data"]["estadisticas"],
                "detalle": resultado["data"]["gastos"],
                "metadatos": {
                    "categorias_disponibles": self.CATEGORIAS_PREDEFINIDAS,
                    "subcategorias_disponibles": self.SUBCATEGORIAS,
                },
            }

            # Si hay filtro por período, agregar estadísticas detalladas
            if "fecha_inicio" in filtros and "fecha_fin" in filtros:
                fecha_inicio = filtros["fecha_inicio"]
                fecha_fin = filtros["fecha_fin"]

                # Calcular días del período
                dias_periodo = (
                    datetime.strptime(fecha_fin, "%Y-%m-%d")
                    - datetime.strptime(fecha_inicio, "%Y-%m-%d")
                ).days + 1

                reporte["analisis_periodo"] = {
                    "dias": dias_periodo,
                    "promedio_diario": (
                        resultado["data"]["estadisticas"]["total_monto"] / dias_periodo
                        if dias_periodo > 0
                        else 0
                    ),
                    "dias_con_gastos": len(
                        set(g["fecha"] for g in resultado["data"]["gastos"])
                    ),
                }

            return {"success": True, "data": reporte}

        except Exception as e:
            logger.error(f"Error generando reporte: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    # ============================================================================
    # MÉTODOS DE GESTIÓN DE COMPROBANTES
    # ============================================================================

    def adjuntar_comprobante_gasto(
        self,
        gasto_id: int,
        ruta_archivo: str,
        tipo_documento: str,
        nombre_original: str = None,
    ) -> Dict[str, Any]:
        """
        Adjunta un comprobante a un gasto.

        Args:
            gasto_id: ID del gasto
            ruta_archivo: Ruta del archivo en el sistema
            tipo_documento: Tipo de documento (FACTURA, RECIBO, VOUCHER, etc.)
            nombre_original: Nombre original del archivo

        Returns:
            Dict con resultado de la operación
        """
        try:
            # Verificar que el gasto existe
            gasto = self.gasto_model.find_by_id(gasto_id)
            if not gasto:
                return {"success": False, "message": "❌ Gasto no encontrado"}

            # Crear comprobante adjunto
            comprobante = self.comprobante_model(
                origen_tipo="GASTO",
                origen_id=gasto_id,
                tipo_documento=tipo_documento,
                ruta_archivo=ruta_archivo,
                nombre_original=nombre_original,
            )

            comprobante_id = comprobante.save()

            return {
                "success": True,
                "message": "✅ Comprobante adjuntado exitosamente",
                "data": {
                    "comprobante_id": comprobante_id,
                    "gasto_id": gasto_id,
                    "ruta_archivo": ruta_archivo,
                    "tipo_documento": tipo_documento,
                    "gasto_info": {
                        "nro_factura": gasto.nro_factura,
                        "monto": float(gasto.monto),
                        "proveedor": gasto.proveedor,
                    },
                },
            }

        except Exception as e:
            logger.error(f"Error adjuntando comprobante: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def obtener_comprobantes_gasto(self, gasto_id: int) -> Dict[str, Any]:
        """
        Obtiene los comprobantes adjuntos de un gasto.

        Args:
            gasto_id: ID del gasto

        Returns:
            Dict con lista de comprobantes
        """
        try:
            comprobantes = self.comprobante_model.buscar_por_origen("GASTO", gasto_id)

            return {
                "success": True,
                "data": {
                    "gasto_id": gasto_id,
                    "total_comprobantes": len(comprobantes),
                    "comprobantes": [c.to_dict() for c in comprobantes],
                },
            }

        except Exception as e:
            logger.error(f"Error obteniendo comprobantes: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    # ============================================================================
    # MÉTODOS DE MOVIMIENTOS DE CAJA (INTERNOS)
    # ============================================================================

    def _registrar_movimiento_caja(self, gasto_id: int, monto: float, descripcion: str):
        """Registra movimiento de caja para un gasto"""
        try:
            movimiento = self.movimiento_model(
                tipo="EGRESO",
                monto=monto,
                origen_tipo="GASTO",
                origen_id=gasto_id,
                descripcion=f"Gasto: {descripcion[:100]}",
            )
            movimiento.save()
            logger.info(f"💰 Movimiento de caja registrado para gasto #{gasto_id}")
        except Exception as e:
            logger.error(f"Error registrando movimiento de caja: {e}")

    def _actualizar_movimiento_caja(self, gasto_id: int, nuevo_monto: float):
        """Actualiza movimiento de caja existente"""
        try:
            movimiento = self.movimiento_model.buscar_por_origen("GASTO", gasto_id)
            if movimiento:
                movimiento.monto = nuevo_monto
                movimiento.save()
                logger.info(f"💰 Movimiento de caja actualizado para gasto #{gasto_id}")
        except Exception as e:
            logger.error(f"Error actualizando movimiento de caja: {e}")

    def _eliminar_movimiento_caja(self, gasto_id: int):
        """Elimina movimiento de caja asociado"""
        try:
            movimiento = self.movimiento_model.buscar_por_origen("GASTO", gasto_id)
            if movimiento:
                movimiento.delete()
                logger.info(f"💰 Movimiento de caja eliminado para gasto #{gasto_id}")
        except Exception as e:
            logger.error(f"Error eliminando movimiento de caja: {e}")

    # ============================================================================
    # MÉTODOS DE UTILIDAD
    # ============================================================================

    def obtener_categorias(self) -> Dict[str, Any]:
        """
        Obtiene lista de categorías y subcategorías disponibles.

        Returns:
            Dict con categorías del sistema
        """
        return {
            "success": True,
            "data": {
                "categorias": self.CATEGORIAS_PREDEFINIDAS,
                "subcategorias": self.SUBCATEGORIAS,
                "formas_pago": [
                    "EFECTIVO",
                    "TRANSFERENCIA",
                    "TARJETA",
                    "CHEQUE",
                    "DEPOSITO",
                    "QR",
                ],
                "total_categorias": len(self.CATEGORIAS_PREDEFINIDAS),
            },
        }

    def obtener_total_gastos_periodo(
        self, fecha_inicio: str, fecha_fin: str
    ) -> Dict[str, Any]:
        """
        Obtiene solo el total de gastos en un período.

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin

        Returns:
            Dict con total de gastos
        """
        try:
            query = """
                SELECT COALESCE(SUM(monto), 0) as total 
                FROM gastos 
                WHERE fecha BETWEEN %s AND %s
            """
            result = db.fetch_one(query, (fecha_inicio, fecha_fin))

            return {
                "success": True,
                "data": {
                    "fecha_inicio": fecha_inicio,
                    "fecha_fin": fecha_fin,
                    "total_gastos": float(result["total"]) if result else 0.0,
                },
            }

        except Exception as e:
            logger.error(f"Error obteniendo total de gastos: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}


# Instancia global para uso en la aplicación
gasto_controller = GastoController()
