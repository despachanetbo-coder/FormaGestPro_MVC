# app/controllers/ingreso_controller.py
"""
Controlador unificado de ingresos para PostgreSQL - FormaGestPro
Combina funcionalidades de:
- PagoController (pagos de matrículas)
- IngresosGenericosController (otros ingresos)
Usa el nuevo IngresoModel para PostgreSQL
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta

# Modelos PostgreSQL
from app.models.ingreso_model import IngresoModel
from app.models.matricula_model import MatriculaModel
from app.models.estudiante_model import EstudianteModel
from app.models.programa_academico_model import ProgramaAcademicoModel
from app.models.comprobante_adjunto_model import ComprobanteAdjuntoModel

logger = logging.getLogger(__name__)


class IngresoController:
    """
    Controlador unificado para la gestión de todos los ingresos.

    Maneja:
    1. Ingresos por matrículas (pagos de estudiantes)
    2. Ingresos genéricos (otros ingresos)
    3. Gestión de comprobantes adjuntos
    4. Reportes y estadísticas financieras
    """

    def __init__(self):
        """Inicializa el controlador con los modelos necesarios"""
        self.ingreso_model = IngresoModel
        self.matricula_model = MatriculaModel
        self.estudiante_model = EstudianteModel
        self.programa_model = ProgramaAcademicoModel
        self.comprobante_model = ComprobanteAdjuntoModel

    # ============================================================================
    # MÉTODOS PARA INGRESOS POR MATRÍCULAS (De PagoController)
    # ============================================================================

    def registrar_pago_matricula(
        self,
        matricula_id: int,
        monto: float,
        forma_pago: str,
        nro_comprobante: str = None,
        nro_transaccion: str = None,
        observaciones: str = None,
        nro_cuota: int = None,
    ) -> Dict[str, Any]:
        """
        Registra un pago para una matrícula.

        Args:
            matricula_id: ID de la matrícula
            monto: Monto del pago
            forma_pago: Forma de pago (EFECTIVO, TRANSFERENCIA, etc.)
            nro_comprobante: Número de comprobante
            nro_transaccion: Número de transacción bancaria
            observaciones: Observaciones adicionales
            nro_cuota: Número de cuota (si aplica)

        Returns:
            Dict con resultado de la operación
        """
        try:
            # Verificar que la matrícula existe
            matricula = self.matricula_model.find_by_id(matricula_id)
            if not matricula:
                return {"success": False, "message": "❌ Matrícula no encontrada"}

            # Determinar tipo de ingreso basado en modalidad
            if (
                matricula.modalidad_pago == MatriculaModel.MODALIDAD_CUOTAS
                and nro_cuota
            ):
                tipo_ingreso = IngresoModel.TIPO_MATRICULA_CUOTA
                concepto = f"Cuota {nro_cuota} - Matrícula #{matricula_id}"
            else:
                tipo_ingreso = IngresoModel.TIPO_MATRICULA_CONTADO
                concepto = f"Pago contado - Matrícula #{matricula_id}"

            # Crear el ingreso
            ingreso = self.ingreso_model(
                tipo_ingreso=tipo_ingreso,
                matricula_id=matricula_id,
                nro_cuota=nro_cuota,
                fecha=date.today().isoformat(),
                monto=monto,
                concepto=concepto,
                descripcion=observaciones,
                forma_pago=forma_pago,
                estado=IngresoModel.ESTADO_CONFIRMADO,
                nro_comprobante=nro_comprobante,
                nro_transaccion=nro_transaccion,
            )

            # Guardar el ingreso
            ingreso_id = ingreso.save()

            # Usar el método de matrícula para registrar el pago
            matricula.registrar_pago(
                monto=monto,
                forma_pago=forma_pago,
                nro_comprobante=nro_comprobante,
                nro_transaccion=nro_transaccion,
                observaciones=observaciones,
                nro_cuota=nro_cuota,
            )

            return {
                "success": True,
                "message": "✅ Pago registrado exitosamente",
                "data": {
                    "ingreso_id": ingreso_id,
                    "matricula_id": matricula_id,
                    "monto": monto,
                    "saldo_anterior": matricula.monto_pagado - monto,
                    "saldo_actual": matricula.monto_pagado,
                    "saldo_pendiente": matricula.saldo_pendiente,
                },
            }

        except ValueError as e:
            return {"success": False, "message": f"❌ {str(e)}"}
        except Exception as e:
            logger.error(f"Error registrando pago: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def obtener_pagos_matricula(self, matricula_id: int) -> Dict[str, Any]:
        """
        Obtiene todos los pagos de una matrícula.

        Args:
            matricula_id: ID de la matrícula

        Returns:
            Dict con lista de pagos
        """
        try:
            # Verificar que la matrícula existe
            matricula = self.matricula_model.find_by_id(matricula_id)
            if not matricula:
                return {"success": False, "message": "❌ Matrícula no encontrada"}

            # Obtener ingresos de la matrícula
            ingresos = self.ingreso_model.buscar_por_matricula(matricula_id)

            # Enriquecer datos
            pagos_data = []
            for ingreso in ingresos:
                pago_data = ingreso.to_dict()
                # Agregar información adicional si está disponible
                if hasattr(ingreso, "comprobantes"):
                    pago_data["comprobantes"] = ingreso.comprobantes
                pagos_data.append(pago_data)

            return {
                "success": True,
                "data": {
                    "matricula_id": matricula_id,
                    "total_pagos": len(pagos_data),
                    "total_monto": sum(p.monto for p in ingresos),
                    "pagos": pagos_data,
                    "resumen_matricula": {
                        "monto_total": matricula.monto_total,
                        "monto_final": matricula.monto_final,
                        "monto_pagado": matricula.monto_pagado,
                        "saldo_pendiente": matricula.saldo_pendiente,
                        "porcentaje_pagado": matricula.porcentaje_pagado,
                        "estado_pago": matricula.estado_pago,
                    },
                },
            }

        except Exception as e:
            logger.error(f"Error obteniendo pagos de matrícula: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def obtener_pagos_estudiante(self, estudiante_id: int) -> Dict[str, Any]:
        """
        Obtiene todos los pagos de un estudiante.

        Args:
            estudiante_id: ID del estudiante

        Returns:
            Dict con pagos del estudiante
        """
        try:
            # Verificar que el estudiante existe
            estudiante = self.estudiante_model.find_by_id(estudiante_id)
            if not estudiante:
                return {"success": False, "message": "❌ Estudiante no encontrado"}

            # Obtener matrículas del estudiante
            matriculas = self.matricula_model.buscar_por_estudiante(estudiante_id)

            # Obtener pagos de cada matrícula
            pagos_totales = []
            resumen_programas = []

            for matricula in matriculas:
                # Obtener programa
                programa = self.programa_model.find_by_id(matricula.programa_id)
                programa_nombre = (
                    programa.nombre if programa else "Programa no encontrado"
                )

                # Obtener pagos de esta matrícula
                ingresos = self.ingreso_model.buscar_por_matricula(matricula.id)

                # Agregar a lista total
                for ingreso in ingresos:
                    pago_data = ingreso.to_dict()
                    pago_data["programa_nombre"] = programa_nombre
                    pago_data["estudiante_nombre"] = (
                        f"{estudiante.nombres} {estudiante.apellidos}"
                    )
                    pagos_totales.append(pago_data)

                # Agregar resumen por programa
                resumen_programas.append(
                    {
                        "programa_id": matricula.programa_id,
                        "programa_nombre": programa_nombre,
                        "matricula_id": matricula.id,
                        "total_pagado": matricula.monto_pagado,
                        "total_debe": matricula.monto_final,
                        "saldo_pendiente": matricula.saldo_pendiente,
                        "numero_pagos": len(ingresos),
                    }
                )

            return {
                "success": True,
                "data": {
                    "estudiante_id": estudiante_id,
                    "estudiante_nombre": f"{estudiante.nombres} {estudiante.apellidos}",
                    "total_pagos": len(pagos_totales),
                    "total_monto": sum(p["monto"] for p in pagos_totales),
                    "pagos": pagos_totales,
                    "resumen_programas": resumen_programas,
                },
            }

        except Exception as e:
            logger.error(f"Error obteniendo pagos de estudiante: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    # ============================================================================
    # MÉTODOS PARA INGRESOS GENÉRICOS (De IngresosGenericosController)
    # ============================================================================

    def crear_ingreso_generico(self, datos: Dict) -> Dict[str, Any]:
        """
        Crea un ingreso genérico (no asociado a matrícula).

        Args:
            datos: Diccionario con datos del ingreso

        Returns:
            Dict con resultado de la operación
        """
        try:
            # Validar datos requeridos
            campos_requeridos = ["monto", "concepto", "forma_pago"]
            for campo in campos_requeridos:
                if campo not in datos or not datos[campo]:
                    return {"success": False, "message": f"❌ Campo requerido: {campo}"}

            # Forzar tipo de ingreso
            datos["tipo_ingreso"] = IngresoModel.TIPO_OTRO_INGRESO

            # Crear ingreso genérico
            ingreso = self.ingreso_model.crear_ingreso_generico(datos)

            # Marcar como confirmado automáticamente
            ingreso.marcar_como_confirmado()

            return {
                "success": True,
                "message": "✅ Ingreso genérico registrado exitosamente",
                "data": ingreso.to_dict(),
            }

        except ValueError as e:
            return {"success": False, "message": f"❌ {str(e)}"}
        except Exception as e:
            logger.error(f"Error creando ingreso genérico: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def obtener_ingresos_genericos(self, filtros: Dict = None) -> Dict[str, Any]:
        """
        Obtiene ingresos genéricos con filtros opcionales.

        Args:
            filtros: Diccionario con filtros (fecha_inicio, fecha_fin, etc.)

        Returns:
            Dict con lista de ingresos genéricos
        """
        try:
            # Obtener ingresos genéricos
            fecha_inicio = filtros.get("fecha_inicio") if filtros else None
            fecha_fin = filtros.get("fecha_fin") if filtros else None

            ingresos = self.ingreso_model.buscar_ingresos_genericos(
                fecha_inicio, fecha_fin
            )

            # Aplicar filtros adicionales si existen
            if filtros:
                ingresos_filtrados = []
                for ingreso in ingresos:
                    cumple_filtro = True

                    # Filtro por estado
                    if "estado" in filtros and filtros["estado"]:
                        if ingreso.estado != filtros["estado"]:
                            cumple_filtro = False

                    # Filtro por forma de pago
                    if "forma_pago" in filtros and filtros["forma_pago"]:
                        if ingreso.forma_pago != filtros["forma_pago"]:
                            cumple_filtro = False

                    # Filtro por monto mínimo
                    if "monto_minimo" in filtros and filtros["monto_minimo"]:
                        if ingreso.monto < float(filtros["monto_minimo"]):
                            cumple_filtro = False

                    # Filtro por monto máximo
                    if "monto_maximo" in filtros and filtros["monto_maximo"]:
                        if ingreso.monto > float(filtros["monto_maximo"]):
                            cumple_filtro = False

                    if cumple_filtro:
                        ingresos_filtrados.append(ingreso)

                ingresos = ingresos_filtrados

            # Convertir a diccionarios
            ingresos_data = [i.to_dict() for i in ingresos]
            total_monto = sum(i.monto for i in ingresos)

            return {
                "success": True,
                "data": {
                    "ingresos": ingresos_data,
                    "total_registros": len(ingresos_data),
                    "total_monto": total_monto,
                    "promedio_monto": (
                        total_monto / len(ingresos_data) if ingresos_data else 0
                    ),
                    "filtros_aplicados": bool(filtros),
                },
            }

        except Exception as e:
            logger.error(f"Error obteniendo ingresos genéricos: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    # ============================================================================
    # MÉTODOS UNIFICADOS PARA TODOS LOS INGRESOS
    # ============================================================================

    def obtener_ingreso(self, ingreso_id: int) -> Dict[str, Any]:
        """
        Obtiene un ingreso por su ID.

        Args:
            ingreso_id: ID del ingreso

        Returns:
            Dict con el ingreso encontrado
        """
        try:
            ingreso = self.ingreso_model.find_by_id(ingreso_id)
            if not ingreso:
                return {"success": False, "message": "❌ Ingreso no encontrado"}

            # Enriquecer datos según el tipo
            datos_ingreso = ingreso.to_dict()

            # Si es ingreso de matrícula, agregar información adicional
            if ingreso.matricula_id:
                matricula = self.matricula_model.find_by_id(ingreso.matricula_id)
                if matricula:
                    datos_ingreso["matricula_info"] = {
                        "estudiante_id": matricula.estudiante_id,
                        "programa_id": matricula.programa_id,
                        "estado_pago": matricula.estado_pago,
                        "estado_academico": matricula.estado_academico,
                    }

                    # Obtener estudiante
                    estudiante = self.estudiante_model.find_by_id(
                        matricula.estudiante_id
                    )
                    if estudiante:
                        datos_ingreso["estudiante_info"] = {
                            "nombre_completo": f"{estudiante.nombres} {estudiante.apellidos}",
                            "ci": f"{estudiante.ci_numero}-{estudiante.ci_expedicion}",
                        }

                    # Obtener programa
                    programa = self.programa_model.find_by_id(matricula.programa_id)
                    if programa:
                        datos_ingreso["programa_info"] = {
                            "codigo": programa.codigo,
                            "nombre": programa.nombre,
                        }

            # Obtener comprobantes adjuntos si existen
            try:
                if hasattr(self.comprobante_model, "buscar_por_ingreso"):
                    comprobantes = self.comprobante_model.buscar_por_ingreso(ingreso_id)
                    datos_ingreso["comprobantes"] = [c.to_dict() for c in comprobantes]
            except Exception as e:
                logger.warning(f"No se pudieron obtener comprobantes: {e}")
                datos_ingreso["comprobantes"] = []

            return {"success": True, "data": datos_ingreso}

        except Exception as e:
            logger.error(f"Error obteniendo ingreso: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def actualizar_ingreso(self, ingreso_id: int, datos: Dict) -> Dict[str, Any]:
        """
        Actualiza un ingreso existente.

        Args:
            ingreso_id: ID del ingreso
            datos: Campos a actualizar

        Returns:
            Dict con resultado de la operación
        """
        try:
            ingreso = self.ingreso_model.find_by_id(ingreso_id)
            if not ingreso:
                return {"success": False, "message": "❌ Ingreso no encontrado"}

            # Validar que no se cambie el tipo si ya tiene transacciones
            if (
                "tipo_ingreso" in datos
                and datos["tipo_ingreso"] != ingreso.tipo_ingreso
            ):
                return {
                    "success": False,
                    "message": "❌ No se puede cambiar el tipo de ingreso",
                }

            # Validar que no se cambie la matrícula si ya está asociado
            if (
                "matricula_id" in datos
                and datos["matricula_id"] != ingreso.matricula_id
            ):
                return {
                    "success": False,
                    "message": "❌ No se puede cambiar la matrícula asociada",
                }

            # Campos que no se pueden actualizar directamente
            campos_bloqueados = ["id", "created_at", "registrado_por"]
            for campo in campos_bloqueados:
                if campo in datos:
                    del datos[campo]

            # Actualizar campos
            for campo, valor in datos.items():
                if hasattr(ingreso, campo):
                    setattr(ingreso, campo, valor)

            # Guardar cambios
            ingreso.save()

            return {
                "success": True,
                "message": "✅ Ingreso actualizado exitosamente",
                "data": ingreso.to_dict(),
            }

        except ValueError as e:
            return {"success": False, "message": f"❌ {str(e)}"}
        except Exception as e:
            logger.error(f"Error actualizando ingreso: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def eliminar_ingreso(self, ingreso_id: int, motivo: str = None) -> Dict[str, Any]:
        """
        Elimina un ingreso (marca como anulado en lugar de eliminar físicamente).

        Args:
            ingreso_id: ID del ingreso
            motivo: Motivo de la anulación

        Returns:
            Dict con resultado de la operación
        """
        try:
            ingreso = self.ingreso_model.find_by_id(ingreso_id)
            if not ingreso:
                return {"success": False, "message": "❌ Ingreso no encontrado"}

            # No se pueden anular ingresos ya anulados
            if ingreso.estado == IngresoModel.ESTADO_ANULADO:
                return {"success": False, "message": "❌ El ingreso ya está anulado"}

            # Marcar como anulado
            ingreso.marcar_como_anulado(motivo)

            # Si es ingreso de matrícula, revertir el pago en la matrícula
            if ingreso.matricula_id and ingreso.monto > 0:
                try:
                    matricula = self.matricula_model.find_by_id(ingreso.matricula_id)
                    if matricula:
                        # Revertir el monto pagado
                        matricula.monto_pagado = max(
                            0, matricula.monto_pagado - ingreso.monto
                        )

                        # Recalcular estado de pago
                        if matricula.monto_pagado <= 0:
                            matricula.estado_pago = MatriculaModel.ESTADO_PAGO_PENDIENTE
                        elif matricula.monto_pagado < matricula.monto_final:
                            matricula.estado_pago = MatriculaModel.ESTADO_PAGO_PARCIAL

                        matricula.save()
                except Exception as e:
                    logger.error(f"Error revertiendo pago en matrícula: {e}")

            return {
                "success": True,
                "message": "✅ Ingreso anulado exitosamente",
                "data": ingreso.to_dict(),
            }

        except Exception as e:
            logger.error(f"Error eliminando ingreso: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def listar_ingresos(self, filtros: Dict = None) -> Dict[str, Any]:
        """
        Lista todos los ingresos con filtros avanzados.

        Args:
            filtros: Diccionario con filtros

        Returns:
            Dict con lista de ingresos
        """
        try:
            # Determinar tipo de consulta basado en filtros
            if filtros and "tipo_ingreso" in filtros:
                tipo_ingreso = filtros["tipo_ingreso"]

                if tipo_ingreso == IngresoModel.TIPO_OTRO_INGRESO:
                    # Ingresos genéricos
                    return self.obtener_ingresos_genericos(filtros)
                elif tipo_ingreso in [
                    IngresoModel.TIPO_MATRICULA_CUOTA,
                    IngresoModel.TIPO_MATRICULA_CONTADO,
                ]:
                    # Ingresos de matrículas
                    if "matricula_id" in filtros:
                        return self.obtener_pagos_matricula(filtros["matricula_id"])
                    elif "estudiante_id" in filtros:
                        return self.obtener_pagos_estudiante(filtros["estudiante_id"])

            # Consulta general (todos los ingresos)
            ingresos = self.ingreso_model.find_all(limit=1000)

            # Aplicar filtros
            if filtros:
                ingresos_filtrados = []
                for ingreso in ingresos:
                    cumple_filtro = True

                    # Filtro por tipo
                    if "tipo_ingreso" in filtros and filtros["tipo_ingreso"]:
                        if ingreso.tipo_ingreso != filtros["tipo_ingreso"]:
                            cumple_filtro = False

                    # Filtro por estado
                    if "estado" in filtros and filtros["estado"]:
                        if ingreso.estado != filtros["estado"]:
                            cumple_filtro = False

                    # Filtro por fecha
                    if "fecha_inicio" in filtros and "fecha_fin" in filtros:
                        if not (
                            filtros["fecha_inicio"]
                            <= ingreso.fecha
                            <= filtros["fecha_fin"]
                        ):
                            cumple_filtro = False

                    # Filtro por forma de pago
                    if "forma_pago" in filtros and filtros["forma_pago"]:
                        if ingreso.forma_pago != filtros["forma_pago"]:
                            cumple_filtro = False

                    # Filtro por matrícula
                    if "matricula_id" in filtros and filtros["matricula_id"]:
                        if ingreso.matricula_id != filtros["matricula_id"]:
                            cumple_filtro = False

                    if cumple_filtro:
                        ingresos_filtrados.append(ingreso)

                ingresos = ingresos_filtrados

            # Convertir a diccionarios
            ingresos_data = [i.to_dict() for i in ingresos]

            # Calcular estadísticas
            total_monto = sum(i.monto for i in ingresos)
            por_tipo = {}
            por_estado = {}
            por_forma_pago = {}

            for ingreso in ingresos:
                # Por tipo
                por_tipo[ingreso.tipo_ingreso] = (
                    por_tipo.get(ingreso.tipo_ingreso, 0) + 1
                )

                # Por estado
                por_estado[ingreso.estado] = por_estado.get(ingreso.estado, 0) + 1

                # Por forma de pago
                por_forma_pago[ingreso.forma_pago] = (
                    por_forma_pago.get(ingreso.forma_pago, 0) + 1
                )

            return {
                "success": True,
                "data": {
                    "ingresos": ingresos_data,
                    "estadisticas": {
                        "total_registros": len(ingresos_data),
                        "total_monto": total_monto,
                        "promedio_monto": (
                            total_monto / len(ingresos_data) if ingresos_data else 0
                        ),
                        "por_tipo": por_tipo,
                        "por_estado": por_estado,
                        "por_forma_pago": por_forma_pago,
                    },
                    "filtros_aplicados": bool(filtros),
                },
            }

        except Exception as e:
            logger.error(f"Error listando ingresos: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    # ============================================================================
    # MÉTODOS DE ESTADÍSTICAS Y REPORTES
    # ============================================================================

    def obtener_estadisticas_periodo(
        self, fecha_inicio: str, fecha_fin: str
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de ingresos por período.

        Args:
            fecha_inicio: Fecha de inicio (YYYY-MM-DD)
            fecha_fin: Fecha de fin (YYYY-MM-DD)

        Returns:
            Dict con estadísticas del período
        """
        try:
            # Obtener ingresos del período
            ingresos = self.ingreso_model.buscar_por_rango_fechas(
                fecha_inicio, fecha_fin, IngresoModel.ESTADO_CONFIRMADO
            )

            # Calcular totales
            total_general = sum(i.monto for i in ingresos)

            # Separar por tipo
            ingresos_matriculas = [
                i for i in ingresos if i.tipo_ingreso != IngresoModel.TIPO_OTRO_INGRESO
            ]
            ingresos_genericos = [
                i for i in ingresos if i.tipo_ingreso == IngresoModel.TIPO_OTRO_INGRESO
            ]

            total_matriculas = sum(i.monto for i in ingresos_matriculas)
            total_genericos = sum(i.monto for i in ingresos_genericos)

            # Agrupar por forma de pago
            por_forma_pago = {}
            for ingreso in ingresos:
                forma = ingreso.forma_pago
                por_forma_pago[forma] = por_forma_pago.get(forma, 0) + ingreso.monto

            # Agrupar por día para gráfico
            por_dia = {}
            for ingreso in ingresos:
                fecha = ingreso.fecha
                por_dia[fecha] = por_dia.get(fecha, 0) + ingreso.monto

            # Convertir a lista ordenada
            por_dia_lista = [
                {"fecha": k, "total": v} for k, v in sorted(por_dia.items())
            ]

            return {
                "success": True,
                "data": {
                    "periodo": {
                        "fecha_inicio": fecha_inicio,
                        "fecha_fin": fecha_fin,
                        "dias": (
                            datetime.strptime(fecha_fin, "%Y-%m-%d")
                            - datetime.strptime(fecha_inicio, "%Y-%m-%d")
                        ).days
                        + 1,
                    },
                    "totales": {
                        "general": total_general,
                        "matriculas": total_matriculas,
                        "genericos": total_genericos,
                        "promedio_diario": (
                            total_general
                            / (
                                (
                                    datetime.strptime(fecha_fin, "%Y-%m-%d")
                                    - datetime.strptime(fecha_inicio, "%Y-%m-%d")
                                ).days
                                + 1
                            )
                            if total_general > 0
                            else 0
                        ),
                    },
                    "distribucion": {
                        "por_tipo": {
                            "matriculas": len(ingresos_matriculas),
                            "genericos": len(ingresos_genericos),
                        },
                        "por_forma_pago": por_forma_pago,
                    },
                    "evolucion_diaria": por_dia_lista,
                    "detalle": {
                        "total_ingresos": len(ingresos),
                        "ingresos_matriculas": len(ingresos_matriculas),
                        "ingresos_genericos": len(ingresos_genericos),
                    },
                },
            }

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de período: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def generar_reporte_ingresos(self, filtros: Dict) -> Dict[str, Any]:
        """
        Genera un reporte detallado de ingresos.

        Args:
            filtros: Filtros para el reporte

        Returns:
            Dict con reporte completo
        """
        try:
            # Obtener ingresos filtrados
            resultado = self.listar_ingresos(filtros)

            if not resultado["success"]:
                return resultado

            # Enriquecer reporte
            reporte = {
                "filtros": filtros,
                "fecha_generacion": datetime.now().isoformat(),
                "resumen": resultado["data"]["estadisticas"],
                "detalle": resultado["data"]["ingresos"],
            }

            # Si hay filtro por período, agregar estadísticas detalladas
            if "fecha_inicio" in filtros and "fecha_fin" in filtros:
                estadisticas_periodo = self.obtener_estadisticas_periodo(
                    filtros["fecha_inicio"], filtros["fecha_fin"]
                )
                if estadisticas_periodo["success"]:
                    reporte["estadisticas_periodo"] = estadisticas_periodo["data"]

            return {"success": True, "data": reporte}

        except Exception as e:
            logger.error(f"Error generando reporte: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    # ============================================================================
    # MÉTODOS PARA GESTIÓN DE COMPROBANTES
    # ============================================================================

    def adjuntar_comprobante(
        self,
        ingreso_id: int,
        ruta_archivo: str,
        tipo_documento: str,
        nombre_original: str = None,
    ) -> Dict[str, Any]:
        """
        Adjunta un comprobante a un ingreso.

        Args:
            ingreso_id: ID del ingreso
            ruta_archivo: Ruta del archivo en el sistema
            tipo_documento: Tipo de documento (VOUCHER, FACTURA, etc.)
            nombre_original: Nombre original del archivo

        Returns:
            Dict con resultado de la operación
        """
        try:
            # Verificar que el ingreso existe
            ingreso = self.ingreso_model.find_by_id(ingreso_id)
            if not ingreso:
                return {"success": False, "message": "❌ Ingreso no encontrado"}

            # Crear comprobante adjunto
            comprobante = self.comprobante_model(
                origen_tipo="INGRESO",
                origen_id=ingreso_id,
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
                    "ingreso_id": ingreso_id,
                    "ruta_archivo": ruta_archivo,
                    "tipo_documento": tipo_documento,
                },
            }

        except Exception as e:
            logger.error(f"Error adjuntando comprobante: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def obtener_comprobantes_ingreso(self, ingreso_id: int) -> Dict[str, Any]:
        """
        Obtiene los comprobantes adjuntos de un ingreso.

        Args:
            ingreso_id: ID del ingreso

        Returns:
            Dict con lista de comprobantes
        """
        try:
            comprobantes = self.comprobante_model.buscar_por_origen(
                "INGRESO", ingreso_id
            )

            return {
                "success": True,
                "data": {
                    "ingreso_id": ingreso_id,
                    "total_comprobantes": len(comprobantes),
                    "comprobantes": [c.to_dict() for c in comprobantes],
                },
            }

        except Exception as e:
            logger.error(f"Error obteniendo comprobantes: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}


# Instancia global para uso en la aplicación
ingreso_controller = IngresoController()
