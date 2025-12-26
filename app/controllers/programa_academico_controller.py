# app/controllers/programa_academico_controller.py
"""
Controlador para la gestión de programas académicos - PostgreSQL
Refactorizado para usar IngresoModel en lugar de PagoModel
Mantiene compatibilidad total con código existente
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date

# Modelos actualizados para PostgreSQL
from app.models.programa_academico_model import ProgramaAcademicoModel
from app.models.ingreso_model import IngresoModel  # Reemplaza PagoModel
from app.models.matricula_model import MatriculaModel
from app.models.estudiante_model import EstudianteModel

logger = logging.getLogger(__name__)


class ProgramaAcademicoController:
    """
    Controlador para la gestión de programas académicos.

    Responsabilidades:
    - CRUD de programas académicos
    - Gestión de promociones y descuentos
    - Estadísticas y reportes financieros
    - Control de cupos y matriculaciones
    """

    def __init__(self):
        """Inicializa el controlador con los modelos necesarios"""
        self.programa_model = ProgramaAcademicoModel
        self.ingreso_model = IngresoModel  # Reemplaza PagoModel
        self.matricula_model = MatriculaModel
        self.estudiante_model = EstudianteModel

    # ============================================================================
    # MÉTODOS CRUD - PROGRAMAS ACADÉMICOS
    # ============================================================================

    def crear_programa(self, datos: Dict) -> Dict[str, Any]:
        """
        Crea un nuevo programa académico.

        Args:
            datos: Diccionario con los datos del programa

        Returns:
            Dict con resultado de la operación
        """
        try:
            programa = self.programa_model.crear_programa(datos)
            return {
                "success": True,
                "message": "✅ Programa creado exitosamente",
                "data": programa.to_dict(),
            }
        except ValueError as e:
            return {"success": False, "message": f"❌ {str(e)}"}
        except Exception as e:
            logger.error(f"Error creando programa: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def obtener_programa(self, programa_id: int) -> Dict[str, Any]:
        """
        Obtiene un programa por su ID.

        Args:
            programa_id: ID del programa

        Returns:
            Dict con el programa encontrado o mensaje de error
        """
        try:
            programa = self.programa_model.find_by_id(programa_id)
            if not programa:
                return {"success": False, "message": "❌ Programa no encontrado"}

            return {"success": True, "data": programa.to_dict()}
        except Exception as e:
            logger.error(f"Error obteniendo programa: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def actualizar_programa(self, programa_id: int, datos: Dict) -> Dict[str, Any]:
        """
        Actualiza un programa existente.

        Args:
            programa_id: ID del programa a actualizar
            datos: Diccionario con campos a actualizar

        Returns:
            Dict con resultado de la operación
        """
        try:
            programa = self.programa_model.find_by_id(programa_id)
            if not programa:
                return {"success": False, "message": "❌ Programa no encontrado"}

            # Actualizar solo los campos proporcionados
            for campo, valor in datos.items():
                if hasattr(programa, campo):
                    setattr(programa, campo, valor)

            programa.save()

            return {
                "success": True,
                "message": "✅ Programa actualizado exitosamente",
                "data": programa.to_dict(),
            }
        except ValueError as e:
            return {"success": False, "message": f"❌ {str(e)}"}
        except Exception as e:
            logger.error(f"Error actualizando programa: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def eliminar_programa(self, programa_id: int) -> Dict[str, Any]:
        """
        Elimina un programa académico.

        Verifica que no tenga matrículas asociadas antes de eliminar.

        Args:
            programa_id: ID del programa a eliminar

        Returns:
            Dict con resultado de la operación
        """
        try:
            programa = self.programa_model.find_by_id(programa_id)
            if not programa:
                return {"success": False, "message": "❌ Programa no encontrado"}

            # Verificar si tiene matrículas asociadas
            matriculas = self.matricula_model.buscar_por_programa(programa_id)
            if matriculas:
                return {
                    "success": False,
                    "message": f"❌ No se puede eliminar. Tiene {len(matriculas)} matrícula(s) activa(s)",
                }

            # Eliminar programa
            if programa.delete():
                return {
                    "success": True,
                    "message": "✅ Programa eliminado exitosamente",
                }
            else:
                return {
                    "success": False,
                    "message": "❌ No se pudo eliminar el programa",
                }

        except Exception as e:
            logger.error(f"Error eliminando programa: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def listar_programas(self, filtros: Dict = None) -> Dict[str, Any]:
        """
        Lista programas académicos con filtros opcionales.

        Args:
            filtros: Diccionario con filtros (estado, tutor_id, con_cupos, etc.)

        Returns:
            Dict con lista de programas
        """
        try:
            # Obtener todos los programas
            programas = self.programa_model.find_all(limit=1000)

            # Aplicar filtros si existen
            if filtros:
                programas_filtrados = []
                for programa in programas:
                    cumple_filtro = True

                    # Filtro por estado
                    if "estado" in filtros and filtros["estado"]:
                        if programa.estado != filtros["estado"]:
                            cumple_filtro = False

                    # Filtro por tutor
                    if "tutor_id" in filtros and filtros["tutor_id"]:
                        if programa.tutor_id != filtros["tutor_id"]:
                            cumple_filtro = False

                    # Filtro por cupos disponibles
                    if "con_cupos" in filtros and filtros["con_cupos"]:
                        if programa.cupos_disponibles <= 0:
                            cumple_filtro = False

                    # Filtro por promoción activa
                    if "con_promocion" in filtros and filtros["con_promocion"]:
                        if not programa.promocion_activa:
                            cumple_filtro = False

                    # Filtro por búsqueda en nombre
                    if "busqueda" in filtros and filtros["busqueda"]:
                        busqueda = filtros["busqueda"].lower()
                        nombre = programa.nombre.lower()
                        codigo = programa.codigo.lower()
                        if busqueda not in nombre and busqueda not in codigo:
                            cumple_filtro = False

                    if cumple_filtro:
                        programas_filtrados.append(programa)

                programas = programas_filtrados

            # Convertir a diccionarios
            programas_data = [p.to_dict() for p in programas]

            return {
                "success": True,
                "data": programas_data,
                "total": len(programas_data),
                "filtros_aplicados": bool(filtros),
            }
        except Exception as e:
            logger.error(f"Error listando programas: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    # ============================================================================
    # MÉTODOS DE PROMOCIONES Y DESCUENTOS
    # ============================================================================

    def activar_promocion(
        self,
        programa_id: int,
        descuento: float,
        descripcion: str = "",
        fecha_limite: str = None,
    ) -> Dict[str, Any]:
        """
        Activa una promoción en un programa.

        Args:
            programa_id: ID del programa
            descuento: Porcentaje de descuento (0-100)
            descripcion: Descripción de la promoción
            fecha_limite: Fecha límite de la promoción (YYYY-MM-DD)

        Returns:
            Dict con resultado de la operación
        """
        try:
            programa = self.programa_model.find_by_id(programa_id)
            if not programa:
                return {"success": False, "message": "❌ Programa no encontrado"}

            # Validar descuento
            if descuento < 0 or descuento > 100:
                return {
                    "success": False,
                    "message": "❌ El descuento debe estar entre 0 y 100%",
                }

            # Activar promoción
            programa.activar_promocion(descuento, descripcion)

            # Establecer fecha límite si se proporciona
            if fecha_limite:
                programa.promocion_fecha_limite = fecha_limite
                programa.save()

            return {
                "success": True,
                "message": "✅ Promoción activada exitosamente",
                "data": programa.to_dict(),
            }
        except ValueError as e:
            return {"success": False, "message": f"❌ {str(e)}"}
        except Exception as e:
            logger.error(f"Error activando promoción: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def desactivar_promocion(self, programa_id: int) -> Dict[str, Any]:
        """
        Desactiva la promoción de un programa.

        Args:
            programa_id: ID del programa

        Returns:
            Dict con resultado de la operación
        """
        try:
            programa = self.programa_model.find_by_id(programa_id)
            if not programa:
                return {"success": False, "message": "❌ Programa no encontrado"}

            programa.desactivar_promocion()

            return {
                "success": True,
                "message": "✅ Promoción desactivada exitosamente",
                "data": programa.to_dict(),
            }
        except Exception as e:
            logger.error(f"Error desactivando promoción: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    # ============================================================================
    # MÉTODOS DE ESTADO DEL PROGRAMA
    # ============================================================================

    def iniciar_programa(
        self, programa_id: int, fecha_inicio: str = None
    ) -> Dict[str, Any]:
        """
        Inicia un programa académico.

        Args:
            programa_id: ID del programa
            fecha_inicio: Fecha de inicio (YYYY-MM-DD), opcional

        Returns:
            Dict con resultado de la operación
        """
        try:
            programa = self.programa_model.find_by_id(programa_id)
            if not programa:
                return {"success": False, "message": "❌ Programa no encontrado"}

            programa.iniciar_programa(fecha_inicio)

            return {
                "success": True,
                "message": "✅ Programa iniciado exitosamente",
                "data": programa.to_dict(),
            }
        except Exception as e:
            logger.error(f"Error iniciando programa: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def concluir_programa(
        self, programa_id: int, fecha_fin: str = None
    ) -> Dict[str, Any]:
        """
        Concluye un programa académico.

        Args:
            programa_id: ID del programa
            fecha_fin: Fecha de conclusión (YYYY-MM-DD), opcional

        Returns:
            Dict con resultado de la operación
        """
        try:
            programa = self.programa_model.find_by_id(programa_id)
            if not programa:
                return {"success": False, "message": "❌ Programa no encontrado"}

            programa.concluir_programa(fecha_fin)

            return {
                "success": True,
                "message": "✅ Programa concluido exitosamente",
                "data": programa.to_dict(),
            }
        except Exception as e:
            logger.error(f"Error concluyendo programa: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def cancelar_programa(self, programa_id: int) -> Dict[str, Any]:
        """
        Cancela un programa académico.

        Args:
            programa_id: ID del programa

        Returns:
            Dict con resultado de la operación
        """
        try:
            programa = self.programa_model.find_by_id(programa_id)
            if not programa:
                return {"success": False, "message": "❌ Programa no encontrado"}

            programa.cancelar_programa()

            return {
                "success": True,
                "message": "✅ Programa cancelado exitosamente",
                "data": programa.to_dict(),
            }
        except Exception as e:
            logger.error(f"Error cancelando programa: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    # ============================================================================
    # MÉTODOS FINANCIEROS Y ESTADÍSTICAS (ACTUALIZADOS PARA INGRESOMODEL)
    # ============================================================================

    def obtener_estadisticas_financieras(self, programa_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas financieras de un programa.

        Reemplaza funcionalidad que usaba PagoModel.

        Args:
            programa_id: ID del programa

        Returns:
            Dict con estadísticas financieras
        """
        try:
            # Usar método del modelo (que ahora usa IngresoModel internamente)
            estadisticas = self.programa_model.obtener_estadisticas_financieras(
                programa_id
            )

            if not estadisticas:
                return {"success": False, "message": "❌ Programa no encontrado"}

            return {"success": True, "data": estadisticas}
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas financieras: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def obtener_ingresos_por_periodo(
        self, programa_id: int, fecha_inicio: str, fecha_fin: str
    ) -> Dict[str, Any]:
        """
        Obtiene ingresos de un programa en un período específico.

        Reemplaza funcionalidad que usaba PagoModel.

        Args:
            programa_id: ID del programa
            fecha_inicio: Fecha de inicio (YYYY-MM-DD)
            fecha_fin: Fecha de fin (YYYY-MM-DD)

        Returns:
            Dict con total de ingresos
        """
        try:
            # Usar método del modelo (que ahora usa IngresoModel internamente)
            total_ingresos = self.programa_model.obtener_ingresos_por_programa(
                programa_id, fecha_inicio, fecha_fin
            )

            # Obtener también detalle de ingresos por mes
            detalle_mensual = self._obtener_detalle_ingresos_mensual(
                programa_id, fecha_inicio, fecha_fin
            )

            return {
                "success": True,
                "data": {
                    "programa_id": programa_id,
                    "fecha_inicio": fecha_inicio,
                    "fecha_fin": fecha_fin,
                    "total_ingresos": round(total_ingresos, 2),
                    "detalle_mensual": detalle_mensual,
                },
            }
        except Exception as e:
            logger.error(f"Error obteniendo ingresos por período: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def _obtener_detalle_ingresos_mensual(
        self, programa_id: int, fecha_inicio: str, fecha_fin: str
    ) -> List[Dict]:
        """
        Obtiene detalle mensual de ingresos.

        Args:
            programa_id: ID del programa
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin

        Returns:
            Lista con ingresos por mes
        """
        try:
            # Obtener todas las matrículas del programa
            matriculas = self.matricula_model.buscar_por_programa(programa_id)

            if not matriculas:
                return []

            # Agrupar ingresos por mes
            ingresos_por_mes = {}

            for matricula in matriculas:
                # Obtener ingresos de esta matrícula
                ingresos = self.ingreso_model.buscar_por_matricula(matricula.id)

                for ingreso in ingresos:
                    # Filtrar por período y estado confirmado
                    if (
                        fecha_inicio <= ingreso.fecha <= fecha_fin
                        and ingreso.estado == self.ingreso_model.ESTADO_CONFIRMADO
                    ):

                        # Extraer año y mes
                        fecha = datetime.strptime(ingreso.fecha, "%Y-%m-%d")
                        clave_mes = fecha.strftime("%Y-%m")

                        if clave_mes not in ingresos_por_mes:
                            ingresos_por_mes[clave_mes] = {
                                "mes": clave_mes,
                                "total": 0.0,
                                "ingresos": [],
                            }

                        ingresos_por_mes[clave_mes]["total"] += ingreso.monto
                        ingresos_por_mes[clave_mes]["ingresos"].append(
                            {
                                "id": ingreso.id,
                                "matricula_id": ingreso.matricula_id,
                                "monto": ingreso.monto,
                                "fecha": ingreso.fecha,
                                "concepto": ingreso.concepto,
                            }
                        )

            # Convertir a lista y ordenar por mes
            resultado = list(ingresos_por_mes.values())
            resultado.sort(key=lambda x: x["mes"], reverse=True)

            return resultado

        except Exception as e:
            logger.error(f"Error obteniendo detalle mensual: {e}")
            return []

    def obtener_estadisticas_estudiantes(self, programa_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de estudiantes en un programa.

        Args:
            programa_id: ID del programa

        Returns:
            Dict con estadísticas de estudiantes
        """
        try:
            # Obtener matrículas del programa
            matriculas = self.matricula_model.buscar_por_programa(programa_id)

            if not matriculas:
                return {
                    "success": True,
                    "data": {
                        "total_estudiantes": 0,
                        "por_estado_academico": {},
                        "por_estado_pago": {},
                        "promedio_pago": 0.0,
                    },
                }

            # Contar por estado académico
            por_estado_academico = {}
            por_estado_pago = {}
            total_pagado = 0.0
            total_deberia = 0.0

            for matricula in matriculas:
                # Estado académico
                estado_acad = matricula.estado_academico
                por_estado_academico[estado_acad] = (
                    por_estado_academico.get(estado_acad, 0) + 1
                )

                # Estado de pago
                estado_pago = matricula.estado_pago
                por_estado_pago[estado_pago] = por_estado_pago.get(estado_pago, 0) + 1

                # Totales financieros
                total_pagado += matricula.monto_pagado
                total_deberia += matricula.monto_final

            # Calcular porcentaje promedio de pago
            porcentaje_pago = 0.0
            if total_deberia > 0:
                porcentaje_pago = (total_pagado / total_deberia) * 100

            return {
                "success": True,
                "data": {
                    "total_estudiantes": len(matriculas),
                    "por_estado_academico": por_estado_academico,
                    "por_estado_pago": por_estado_pago,
                    "total_pagado": round(total_pagado, 2),
                    "total_deberia": round(total_deberia, 2),
                    "porcentaje_pago": round(porcentaje_pago, 2),
                    "saldo_pendiente": round(total_deberia - total_pagado, 2),
                },
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de estudiantes: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    # ============================================================================
    # MÉTODOS DE REPORTES Y EXPORTACIÓN
    # ============================================================================

    def generar_reporte_completo(self, programa_id: int) -> Dict[str, Any]:
        """
        Genera un reporte completo del programa.

        Args:
            programa_id: ID del programa

        Returns:
            Dict con reporte completo
        """
        try:
            programa = self.programa_model.find_by_id(programa_id)
            if not programa:
                return {"success": False, "message": "❌ Programa no encontrado"}

            # Obtener todas las estadísticas
            estadisticas_financieras = self.obtener_estadisticas_financieras(
                programa_id
            )
            estadisticas_estudiantes = self.obtener_estadisticas_estudiantes(
                programa_id
            )

            # Obtener matrículas recientes
            matriculas = self.matricula_model.buscar_por_programa(programa_id)
            matriculas_recientes = []

            for matricula in matriculas[:10]:  # Últimas 10 matrículas
                estudiante = self.estudiante_model.find_by_id(matricula.estudiante_id)
                if estudiante:
                    matriculas_recientes.append(
                        {
                            "matricula_id": matricula.id,
                            "estudiante_id": estudiante.id,
                            "estudiante_nombre": f"{estudiante.nombres} {estudiante.apellidos}",
                            "fecha_matricula": matricula.fecha_matricula,
                            "estado_academico": matricula.estado_academico,
                            "estado_pago": matricula.estado_pago,
                            "monto_pagado": matricula.monto_pagado,
                            "monto_final": matricula.monto_final,
                        }
                    )

            # Construir reporte
            reporte = {
                "programa": programa.to_dict(),
                "estadisticas_financieras": (
                    estadisticas_financieras.get("data", {})
                    if estadisticas_financieras["success"]
                    else {}
                ),
                "estadisticas_estudiantes": (
                    estadisticas_estudiantes.get("data", {})
                    if estadisticas_estudiantes["success"]
                    else {}
                ),
                "matriculas_recientes": matriculas_recientes,
                "fecha_generacion": datetime.now().isoformat(),
                "total_matriculas": len(matriculas),
            }

            return {"success": True, "data": reporte}
        except Exception as e:
            logger.error(f"Error generando reporte completo: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def obtener_estadisticas_generales(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales de todos los programas.

        Returns:
            Dict con estadísticas generales
        """
        try:
            estadisticas = self.programa_model.obtener_estadisticas()

            return {"success": True, "data": estadisticas}
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas generales: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    # ============================================================================
    # MÉTODOS DE UTILIDAD
    # ============================================================================

    def verificar_cupos_disponibles(self, programa_id: int) -> Dict[str, Any]:
        """
        Verifica si un programa tiene cupos disponibles.

        Args:
            programa_id: ID del programa

        Returns:
            Dict con información de cupos
        """
        try:
            programa = self.programa_model.find_by_id(programa_id)
            if not programa:
                return {"success": False, "message": "❌ Programa no encontrado"}

            return {
                "success": True,
                "data": {
                    "programa_id": programa_id,
                    "programa_nombre": programa.nombre,
                    "cupos_disponibles": programa.cupos_disponibles,
                    "cupos_totales": programa.cupos_totales,
                    "tiene_cupos": programa.cupos_disponibles > 0,
                    "porcentaje_ocupacion": programa.porcentaje_ocupacion,
                },
            }
        except Exception as e:
            logger.error(f"Error verificando cupos: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}

    def obtener_costos_desglosados(self, programa_id: int) -> Dict[str, Any]:
        """
        Obtiene costos desglosados de un programa.

        Args:
            programa_id: ID del programa

        Returns:
            Dict con costos desglosados
        """
        try:
            programa = self.programa_model.find_by_id(programa_id)
            if not programa:
                return {"success": False, "message": "❌ Programa no encontrado"}

            costos = programa.calcular_costos_matricula()

            return {
                "success": True,
                "data": {
                    "programa_id": programa_id,
                    "programa_nombre": programa.nombre,
                    "costos": costos,
                    "costo_total_estudiante": programa.costo_total_estudiante,
                    "costo_con_descuento_contado": programa.costo_con_descuento_contado,
                    "costo_con_promocion": programa.costo_con_promocion,
                },
            }
        except Exception as e:
            logger.error(f"Error obteniendo costos desglosados: {e}")
            return {"success": False, "message": "❌ Error interno del servidor"}


# Instancia global para uso en la aplicación
programa_academico_controller = ProgramaAcademicoController()
