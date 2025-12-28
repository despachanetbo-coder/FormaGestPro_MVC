# app/controllers/ingreso_controller.py
"""
Controlador de Ingresos - FormaGestPro MVC
Gestiona todos los ingresos del sistema: matrículas, cuotas y otros ingresos
Versión compatible con los modelos actuales
"""

import sys
import os
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importaciones CORREGIDAS según los modelos proporcionados
from app.models.ingreso_model import IngresoModel
from app.models.facturas_model import FacturasModel
from app.models.usuarios_model import UsuariosModel
from app.models.gasto_model import GastoModel
from app.models.plan_pago_model import PlanPagoModel

logger = logging.getLogger(__name__)


class IngresosController:
    """
    Controlador para la gestión de ingresos
    Proporciona métodos para registrar, consultar, actualizar y reportar ingresos
    """

    def __init__(self):
        """Inicializa el controlador de ingresos"""
        logger.info("✅ IngresosController inicializado")

        # Inicializar modelos
        self.ingreso_model = IngresoModel()
        self.factura_model = FacturasModel()
        self.usuario_model = UsuariosModel()

        # Para compatibilidad
        self.GastoModel = GastoModel
        self.PlanPagoModel = PlanPagoModel

        # Constantes (mantener compatibilidad)
        self.TIPO_MATRICULA_CUOTA = IngresoModel.TIPO_MATRICULA_CUOTA
        self.TIPO_MATRICULA_CONTADO = IngresoModel.TIPO_MATRICULA_CONTADO
        self.TIPO_OTRO_INGRESO = IngresoModel.TIPO_OTRO_INGRESO

        self.ESTADO_REGISTRADO = IngresoModel.ESTADO_REGISTRADO
        self.ESTADO_CONFIRMADO = IngresoModel.ESTADO_CONFIRMADO
        self.ESTADO_ANULADO = IngresoModel.ESTADO_ANULADO

        self.FORMA_EFECTIVO = IngresoModel.FORMA_EFECTIVO
        self.FORMA_TRANSFERENCIA = IngresoModel.FORMA_TRANSFERENCIA
        self.FORMA_TARJETA_CREDITO = IngresoModel.FORMA_TARJETA_CREDITO
        self.FORMA_TARJETA_DEBITO = IngresoModel.FORMA_TARJETA_DEBITO
        self.FORMA_DEPOSITO = IngresoModel.FORMA_DEPOSITO
        self.FORMA_CHEQUE = IngresoModel.FORMA_CHEQUE

    # ============ MÉTODOS PRINCIPALES ============

    def registrar_ingreso_generico(
        self, datos_ingreso: Dict[str, Any], usuario_id: int
    ) -> Dict[str, Any]:
        """
        Registra un ingreso genérico (no relacionado con matrícula)

        Args:
            datos_ingreso: Diccionario con datos del ingreso
            usuario_id: ID del usuario que registra

        Returns:
            Dict con resultado de la operación
        """
        try:
            logger.info(f"📝 Registrando ingreso genérico por usuario {usuario_id}")

            # Validar datos requeridos
            campos_requeridos = ["concepto", "monto", "fecha", "forma_pago"]
            for campo in campos_requeridos:
                if campo not in datos_ingreso or not datos_ingreso[campo]:
                    return {
                        "success": False,
                        "message": f"Campo requerido faltante: {campo}",
                    }

            # Validar monto
            try:
                monto = float(datos_ingreso["monto"])
                if monto <= 0:
                    return {"success": False, "message": "El monto debe ser mayor a 0"}
            except (ValueError, TypeError):
                return {"success": False, "message": "Monto inválido"}

            # Completar datos del ingreso
            datos_completos = {
                "tipo_ingreso": self.TIPO_OTRO_INGRESO,
                "concepto": datos_ingreso["concepto"],
                "descripcion": datos_ingreso.get("descripcion", ""),
                "monto": monto,
                "fecha": datos_ingreso["fecha"],
                "forma_pago": datos_ingreso["forma_pago"],
                "estado": self.ESTADO_REGISTRADO,
                "registrado_por": usuario_id,
            }

            # Campos opcionales
            if "nro_comprobante" in datos_ingreso:
                datos_completos["nro_comprobante"] = datos_ingreso["nro_comprobante"]

            if "nro_transaccion" in datos_ingreso:
                datos_completos["nro_transaccion"] = datos_ingreso["nro_transaccion"]

            # Crear instancia del modelo
            ingreso = IngresoModel(**datos_completos)

            # Guardar en base de datos
            ingreso_id = ingreso.save()

            if ingreso_id:
                logger.info(f"✅ Ingreso genérico registrado con ID: {ingreso_id}")

                # Generar factura si corresponde
                if datos_ingreso.get("generar_factura", False):
                    self._generar_factura_ingreso(
                        ingreso_id, datos_completos, usuario_id
                    )

                return {
                    "success": True,
                    "message": "Ingreso registrado exitosamente",
                    "data": {
                        "ingreso_id": ingreso_id,
                        "concepto": datos_ingreso["concepto"],
                        "monto": monto,
                        "fecha": datos_ingreso["fecha"],
                    },
                }
            else:
                return {
                    "success": False,
                    "message": "Error al guardar el ingreso en la base de datos",
                }

        except Exception as e:
            logger.error(f"❌ Error registrando ingreso genérico: {e}")
            return {
                "success": False,
                "message": f"Error al registrar ingreso: {str(e)}",
            }

    def registrar_pago_matricula(
        self, matricula_id: int, datos_pago: Dict[str, Any], usuario_id: int
    ) -> Dict[str, Any]:
        """
        Registra un pago de matrícula

        Args:
            matricula_id: ID de la matrícula
            datos_pago: Datos del pago
            usuario_id: ID del usuario que registra

        Returns:
            Dict con resultado de la operación
        """
        try:
            logger.info(f"📝 Registrando pago de matrícula {matricula_id}")

            # Validar datos
            campos_requeridos = ["monto", "forma_pago"]
            for campo in campos_requeridos:
                if campo not in datos_pago or not datos_pago[campo]:
                    return {
                        "success": False,
                        "message": f"Campo requerido faltante: {campo}",
                    }

            # Determinar tipo de pago
            es_contado = datos_pago.get("es_contado", False)
            nro_cuota = datos_pago.get("nro_cuota")

            if es_contado:
                tipo_ingreso = self.TIPO_MATRICULA_CONTADO
                concepto = f"Matrícula al contado - Matrícula #{matricula_id}"
            else:
                tipo_ingreso = self.TIPO_MATRICULA_CUOTA
                concepto = f"Cuota {nro_cuota} - Matrícula #{matricula_id}"

            # Preparar datos del ingreso
            datos_ingreso = {
                "tipo_ingreso": tipo_ingreso,
                "matricula_id": matricula_id,
                "nro_cuota": nro_cuota if not es_contado else None,
                "concepto": concepto,
                "descripcion": datos_pago.get("descripcion", ""),
                "monto": float(datos_pago["monto"]),
                "fecha": datos_pago.get("fecha", date.today().isoformat()),
                "forma_pago": datos_pago["forma_pago"],
                "estado": self.ESTADO_REGISTRADO,
                "registrado_por": usuario_id,
            }

            # Campos opcionales
            if "nro_comprobante" in datos_pago:
                datos_ingreso["nro_comprobante"] = datos_pago["nro_comprobante"]

            # Crear y guardar ingreso
            ingreso = IngresoModel(**datos_ingreso)
            ingreso_id = ingreso.save()

            if ingreso_id:
                logger.info(f"✅ Pago de matrícula registrado con ID: {ingreso_id}")

                # Actualizar estado de la matrícula si corresponde
                if es_contado:
                    self._actualizar_matricula_pagada(matricula_id)

                return {
                    "success": True,
                    "message": "Pago de matrícula registrado exitosamente",
                    "data": {
                        "ingreso_id": ingreso_id,
                        "matricula_id": matricula_id,
                        "tipo": "contado" if es_contado else f"cuota {nro_cuota}",
                        "monto": datos_pago["monto"],
                    },
                }
            else:
                return {"success": False, "message": "Error al registrar el pago"}

        except Exception as e:
            logger.error(f"❌ Error registrando pago de matrícula: {e}")
            return {"success": False, "message": f"Error al registrar pago: {str(e)}"}

    # ============ MÉTODOS DE CONSULTA ============

    def obtener_ingreso(self, ingreso_id: int) -> Dict[str, Any]:
        """
        Obtiene un ingreso por su ID

        Args:
            ingreso_id: ID del ingreso

        Returns:
            Dict con datos del ingreso o mensaje de error
        """
        try:
            ingreso = IngresoModel.find_by_id(ingreso_id)

            if ingreso:
                return {"success": True, "data": ingreso.to_dict()}
            else:
                return {
                    "success": False,
                    "message": f"Ingreso con ID {ingreso_id} no encontrado",
                }

        except Exception as e:
            logger.error(f"❌ Error obteniendo ingreso {ingreso_id}: {e}")
            return {"success": False, "message": f"Error al obtener ingreso: {str(e)}"}

    def listar_ingresos(
        self,
        tipo_ingreso: Optional[str] = None,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
        estado: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Lista ingresos con filtros opcionales

        Args:
            tipo_ingreso: Tipo de ingreso a filtrar
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            estado: Estado a filtrar
            limit: Límite de resultados
            offset: Desplazamiento

        Returns:
            Dict con lista de ingresos
        """
        try:
            # Construir consulta dinámica
            condiciones = []
            parametros = []

            if tipo_ingreso:
                condiciones.append("tipo_ingreso = %s")
                parametros.append(tipo_ingreso)

            if fecha_inicio:
                condiciones.append("fecha >= %s")
                parametros.append(fecha_inicio)

            if fecha_fin:
                condiciones.append("fecha <= %s")
                parametros.append(fecha_fin)

            if estado:
                condiciones.append("estado = %s")
                parametros.append(estado)

            # Consulta base
            query = "SELECT * FROM ingresos"

            if condiciones:
                query += " WHERE " + " AND ".join(condiciones)

            query += " ORDER BY fecha DESC, id DESC"
            query += " LIMIT %s OFFSET %s"
            parametros.extend([limit, offset])

            # Ejecutar consulta
            resultados = self.ingreso_model.fetch_all(query, tuple(parametros))

            # Contar total para paginación
            count_query = "SELECT COUNT(*) as total FROM ingresos"
            if condiciones:
                count_query += " WHERE " + " AND ".join(condiciones)

            count_result = self.ingreso_model.fetch_one(
                count_query, tuple(parametros[:-2]) if condiciones else None
            )

            total = count_result["total"] if count_result else 0

            return {
                "success": True,
                "data": {
                    "ingresos": resultados if resultados else [],
                    "pagination": {
                        "total": total,
                        "limit": limit,
                        "offset": offset,
                        "has_more": (
                            (offset + len(resultados)) < total if resultados else False
                        ),
                    },
                },
            }

        except Exception as e:
            logger.error(f"❌ Error listando ingresos: {e}")
            return {"success": False, "message": f"Error al listar ingresos: {str(e)}"}

    def buscar_ingresos_genericos(
        self, fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Busca ingresos genéricos (no relacionados con matrículas)

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin

        Returns:
            Dict con ingresos genéricos encontrados
        """
        try:
            ingresos = IngresoModel.buscar_ingresos_genericos(fecha_inicio, fecha_fin)

            # Convertir a diccionarios
            datos_ingresos = [ingreso.to_dict() for ingreso in ingresos]

            return {
                "success": True,
                "data": {"ingresos": datos_ingresos, "total": len(datos_ingresos)},
            }

        except Exception as e:
            logger.error(f"❌ Error buscando ingresos genéricos: {e}")
            return {"success": False, "message": f"Error al buscar ingresos: {str(e)}"}

    def obtener_ingresos_por_matricula(self, matricula_id: int) -> Dict[str, Any]:
        """
        Obtiene todos los ingresos asociados a una matrícula

        Args:
            matricula_id: ID de la matrícula

        Returns:
            Dict con ingresos de la matrícula
        """
        try:
            ingresos = IngresoModel.buscar_por_matricula(matricula_id)

            datos_ingresos = [ingreso.to_dict() for ingreso in ingresos]

            # Calcular total pagado
            total_pagado = sum(
                ingreso.monto
                for ingreso in ingresos
                if ingreso.estado != self.ESTADO_ANULADO
            )

            return {
                "success": True,
                "data": {
                    "ingresos": datos_ingresos,
                    "total_pagado": total_pagado,
                    "total_ingresos": len(datos_ingresos),
                },
            }

        except Exception as e:
            logger.error(f"❌ Error obteniendo ingresos por matrícula: {e}")
            return {"success": False, "message": f"Error al obtener ingresos: {str(e)}"}

    # ============ MÉTODOS DE ACTUALIZACIÓN ============

    def actualizar_ingreso(
        self, ingreso_id: int, datos_actualizacion: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Actualiza los datos de un ingreso

        Args:
            ingreso_id: ID del ingreso
            datos_actualizacion: Datos a actualizar

        Returns:
            Dict con resultado de la operación
        """
        try:
            # Obtener ingreso existente
            ingreso = IngresoModel.find_by_id(ingreso_id)

            if not ingreso:
                return {
                    "success": False,
                    "message": f"Ingreso con ID {ingreso_id} no encontrado",
                }

            # Validar que no esté confirmado (si se quiere cambiar monto o datos críticos)
            if ingreso.estado == self.ESTADO_CONFIRMADO:
                campos_criticos = ["monto", "fecha", "concepto", "forma_pago"]
                if any(campo in datos_actualizacion for campo in campos_criticos):
                    return {
                        "success": False,
                        "message": "No se pueden modificar datos críticos de un ingreso confirmado",
                    }

            # Actualizar campos permitidos
            campos_permitidos = ["descripcion", "nro_comprobante", "nro_transaccion"]

            for campo in campos_permitidos:
                if campo in datos_actualizacion:
                    setattr(ingreso, campo, datos_actualizacion[campo])

            # Guardar cambios
            if ingreso.update():
                logger.info(f"✅ Ingreso {ingreso_id} actualizado exitosamente")
                return {
                    "success": True,
                    "message": "Ingreso actualizado exitosamente",
                    "data": ingreso.to_dict(),
                }
            else:
                return {"success": False, "message": "Error al actualizar el ingreso"}

        except Exception as e:
            logger.error(f"❌ Error actualizando ingreso {ingreso_id}: {e}")
            return {
                "success": False,
                "message": f"Error al actualizar ingreso: {str(e)}",
            }

    def confirmar_ingreso(self, ingreso_id: int) -> Dict[str, Any]:
        """
        Marca un ingreso como confirmado

        Args:
            ingreso_id: ID del ingreso

        Returns:
            Dict con resultado de la operación
        """
        try:
            ingreso = IngresoModel.find_by_id(ingreso_id)

            if not ingreso:
                return {
                    "success": False,
                    "message": f"Ingreso con ID {ingreso_id} no encontrado",
                }

            if ingreso.estado == self.ESTADO_CONFIRMADO:
                return {"success": False, "message": "El ingreso ya está confirmado"}

            if ingreso.estado == self.ESTADO_ANULADO:
                return {
                    "success": False,
                    "message": "No se puede confirmar un ingreso anulado",
                }

            # Marcar como confirmado
            if ingreso.marcar_como_confirmado():
                logger.info(f"✅ Ingreso {ingreso_id} confirmado")

                # Registrar movimiento en caja si corresponde
                self._registrar_movimiento_caja(ingreso)

                return {
                    "success": True,
                    "message": "Ingreso confirmado exitosamente",
                    "data": ingreso.to_dict(),
                }
            else:
                return {"success": False, "message": "Error al confirmar el ingreso"}

        except Exception as e:
            logger.error(f"❌ Error confirmando ingreso {ingreso_id}: {e}")
            return {
                "success": False,
                "message": f"Error al confirmar ingreso: {str(e)}",
            }

    def anular_ingreso(self, ingreso_id: int, motivo: str) -> Dict[str, Any]:
        """
        Anula un ingreso

        Args:
            ingreso_id: ID del ingreso
            motivo: Motivo de la anulación

        Returns:
            Dict con resultado de la operación
        """
        try:
            ingreso = IngresoModel.find_by_id(ingreso_id)

            if not ingreso:
                return {
                    "success": False,
                    "message": f"Ingreso con ID {ingreso_id} no encontrado",
                }

            if ingreso.estado == self.ESTADO_ANULADO:
                return {"success": False, "message": "El ingreso ya está anulado"}

            # Marcar como anulado
            if ingreso.marcar_como_anulado(motivo):
                logger.info(f"✅ Ingreso {ingreso_id} anulado: {motivo}")

                # Revertir movimiento en caja si existe
                self._revertir_movimiento_caja(ingreso)

                return {
                    "success": True,
                    "message": "Ingreso anulado exitosamente",
                    "data": ingreso.to_dict(),
                }
            else:
                return {"success": False, "message": "Error al anular el ingreso"}

        except Exception as e:
            logger.error(f"❌ Error anulando ingreso {ingreso_id}: {e}")
            return {"success": False, "message": f"Error al anular ingreso: {str(e)}"}

    # ============ MÉTODOS DE REPORTES Y ESTADÍSTICAS ============

    def generar_reporte_ingresos(
        self,
        fecha_inicio: str,
        fecha_fin: str,
        tipo_ingreso: Optional[str] = None,
        forma_pago: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Genera un reporte detallado de ingresos

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            tipo_ingreso: Tipo de ingreso a filtrar
            forma_pago: Forma de pago a filtrar

        Returns:
            Dict con reporte de ingresos
        """
        try:
            # Construir consulta
            condiciones = ["fecha BETWEEN %s AND %s"]
            parametros = [fecha_inicio, fecha_fin]

            if tipo_ingreso:
                condiciones.append("tipo_ingreso = %s")
                parametros.append(tipo_ingreso)

            if forma_pago:
                condiciones.append("forma_pago = %s")
                parametros.append(forma_pago)

            # Excluir anulados
            condiciones.append("estado != %s")
            parametros.append(self.ESTADO_ANULADO)

            where_clause = " AND ".join(condiciones)

            # Consulta para detalles
            query_detalle = f"""
                SELECT 
                    id, tipo_ingreso, concepto, fecha, monto, forma_pago, estado,
                    nro_comprobante, registrado_por
                FROM ingresos 
                WHERE {where_clause}
                ORDER BY fecha, id
            """

            detalles = self.ingreso_model.fetch_all(query_detalle, tuple(parametros))

            # Consulta para resumen
            query_resumen = f"""
                SELECT 
                    tipo_ingreso,
                    forma_pago,
                    COUNT(*) as cantidad,
                    SUM(monto) as total_monto,
                    AVG(monto) as promedio_monto
                FROM ingresos 
                WHERE {where_clause}
                GROUP BY tipo_ingreso, forma_pago
                ORDER BY total_monto DESC
            """

            resumen = self.ingreso_model.fetch_all(query_resumen, tuple(parametros))

            # Calcular total general
            total_general = (
                sum(item["total_monto"] for item in resumen) if resumen else 0
            )

            return {
                "success": True,
                "data": {
                    "periodo": {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin},
                    "filtros": {"tipo_ingreso": tipo_ingreso, "forma_pago": forma_pago},
                    "detalle_ingresos": detalles if detalles else [],
                    "resumen": resumen if resumen else [],
                    "estadisticas": {
                        "total_ingresos": len(detalles) if detalles else 0,
                        "total_monto": total_general,
                        "promedio_monto": (
                            total_general / len(detalles) if detalles else 0
                        ),
                    },
                },
            }

        except Exception as e:
            logger.error(f"❌ Error generando reporte de ingresos: {e}")
            return {"success": False, "message": f"Error al generar reporte: {str(e)}"}

    def obtener_estadisticas_mes(self, año: int, mes: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de ingresos por mes

        Args:
            año: Año
            mes: Mes (1-12)

        Returns:
            Dict con estadísticas del mes
        """
        try:
            estadisticas = IngresoModel.get_estadisticas_mes(año, mes)

            if estadisticas:
                return {"success": True, "data": estadisticas}
            else:
                return {
                    "success": False,
                    "message": "No se pudieron obtener las estadísticas del mes",
                }

        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas del mes: {e}")
            return {
                "success": False,
                "message": f"Error al obtener estadísticas: {str(e)}",
            }

    # ============ MÉTODOS AUXILIARES PRIVADOS ============

    def _generar_factura_ingreso(
        self, ingreso_id: int, datos_ingreso: Dict[str, Any], usuario_id: int
    ) -> Optional[int]:
        """
        Genera una factura para un ingreso

        Args:
            ingreso_id: ID del ingreso
            datos_ingreso: Datos del ingreso
            usuario_id: ID del usuario

        Returns:
            ID de la factura generada o None
        """
        try:
            # Generar número de factura
            numero_factura = self.factura_model.generar_nuevo_numero_factura()

            datos_factura = {
                "numero": numero_factura,
                "cliente_id": datos_ingreso.get("cliente_id", 0),
                "cliente_nombre": datos_ingreso.get("cliente_nombre", "Cliente Varios"),
                "fecha_emision": datos_ingreso["fecha"],
                "subtotal": float(datos_ingreso["monto"]),
                "iva": 0,
                "total": float(datos_ingreso["monto"]),
                "estado": "PAGADA",
                "tipo": "OTRO",
                "observaciones": f"Factura por ingreso: {datos_ingreso['concepto']}",
                "usuario_id": usuario_id,
                "forma_pago": datos_ingreso["forma_pago"],
                "referencia_pago": datos_ingreso.get("nro_comprobante", ""),
                "fecha_pago": datos_ingreso["fecha"],
            }

            # Crear factura
            factura_id = self.factura_model.crear_factura(datos_factura)

            if factura_id:
                logger.info(
                    f"✅ Factura {numero_factura} generada para ingreso {ingreso_id}"
                )
                return factura_id

            return None

        except Exception as e:
            logger.error(f"❌ Error generando factura para ingreso {ingreso_id}: {e}")
            return None

    def _actualizar_matricula_pagada(self, matricula_id: int) -> bool:
        """
        Actualiza el estado de una matrícula cuando se paga al contado

        Args:
            matricula_id: ID de la matrícula

        Returns:
            True si se actualizó correctamente
        """
        try:
            # Esta función debería actualizar la tabla de matrículas
            # Por ahora es un placeholder
            logger.info(f"📋 Matrícula {matricula_id} marcada como pagada")
            return True
        except Exception as e:
            logger.error(f"❌ Error actualizando matrícula {matricula_id}: {e}")
            return False

    def _registrar_movimiento_caja(self, ingreso: IngresoModel) -> bool:
        """
        Registra un movimiento en caja para un ingreso confirmado

        Args:
            ingreso: Instancia de IngresoModel

        Returns:
            True si se registró correctamente
        """
        try:
            # Importar aquí para evitar dependencia circular
            from app.models.movimiento_caja_model import MovimientoCajaModel

            movimiento_data = {
                "fecha": ingreso.fecha,
                "tipo": "INGRESO",
                "monto": ingreso.monto,
                "descripcion": f"Ingreso: {ingreso.concepto}",
                "origen_tipo": "INGRESO",
                "origen_id": ingreso.id,
                "forma_pago": ingreso.forma_pago,
                "comprobante_nro": ingreso.nro_comprobante,
            }

            movimiento_model = MovimientoCajaModel()
            movimiento_id = movimiento_model.create(
                movimiento_data, ingreso.registrado_por
            )

            return movimiento_id is not None

        except Exception as e:
            logger.error(f"❌ Error registrando movimiento en caja: {e}")
            return False

    def _revertir_movimiento_caja(self, ingreso: IngresoModel) -> bool:
        """
        Revierte el movimiento en caja de un ingreso anulado

        Args:
            ingreso: Instancia de IngresoModel

        Returns:
            True si se revirtió correctamente
        """
        try:
            # Importar aquí para evitar dependencia circular
            from app.models.movimiento_caja_model import MovimientoCajaModel

            # Buscar movimiento asociado
            query = """
                SELECT id FROM movimientos_caja 
                WHERE origen_tipo = 'INGRESO' AND origen_id = %s
            """
            resultado = self.ingreso_model.fetch_one(query, (ingreso.id,))

            if resultado:
                movimiento_id = resultado["id"]
                movimiento_model = MovimientoCajaModel()

                # Marcar movimiento como anulado o eliminarlo
                return movimiento_model.delete(movimiento_id)

            return True

        except Exception as e:
            logger.error(f"❌ Error revirtiendo movimiento en caja: {e}")
            return False

    # ============ MÉTODOS DE UTILIDAD ============

    def get_tipos_ingreso(self) -> Dict[str, Any]:
        """
        Obtiene la lista de tipos de ingreso

        Returns:
            Dict con tipos de ingreso
        """
        try:
            tipos = IngresoModel.get_tipos_ingreso()
            return {"success": True, "data": tipos}
        except Exception as e:
            logger.error(f"❌ Error obteniendo tipos de ingreso: {e}")
            return {"success": False, "message": f"Error al obtener tipos: {str(e)}"}

    def get_formas_pago(self) -> Dict[str, Any]:
        """
        Obtiene la lista de formas de pago

        Returns:
            Dict con formas de pago
        """
        try:
            formas = IngresoModel.get_formas_pago()
            return {"success": True, "data": formas}
        except Exception as e:
            logger.error(f"❌ Error obteniendo formas de pago: {e}")
            return {
                "success": False,
                "message": f"Error al obtener formas de pago: {str(e)}",
            }

    def get_estados_ingreso(self) -> Dict[str, Any]:
        """
        Obtiene la lista de estados de ingreso

        Returns:
            Dict con estados de ingreso
        """
        try:
            estados = IngresoModel.get_estados()
            return {"success": True, "data": estados}
        except Exception as e:
            logger.error(f"❌ Error obteniendo estados de ingreso: {e}")
            return {"success": False, "message": f"Error al obtener estados: {str(e)}"}

    # ============ MÉTODOS DE COMPATIBILIDAD ============

    def crear_ingreso(
        self, datos_ingreso: Dict[str, Any], usuario_id: int
    ) -> Dict[str, Any]:
        """Método de compatibilidad (alias de registrar_ingreso_generico)"""
        return self.registrar_ingreso_generico(datos_ingreso, usuario_id)

    def obtener_ingresos(self, **kwargs) -> Dict[str, Any]:
        """Método de compatibilidad (alias de listar_ingresos)"""
        return self.listar_ingresos(**kwargs)

    def actualizar(self, ingreso_id: int, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Método de compatibilidad (alias de actualizar_ingreso)"""
        return self.actualizar_ingreso(ingreso_id, datos)


# Función para obtener instancia del controlador (patrón singleton opcional)
_ingresos_controller_instance = None


def get_ingresos_controller() -> IngresosController:
    """Obtiene una instancia del controlador de ingresos"""
    global _ingresos_controller_instance
    if _ingresos_controller_instance is None:
        _ingresos_controller_instance = IngresosController()
    return _ingresos_controller_instance
