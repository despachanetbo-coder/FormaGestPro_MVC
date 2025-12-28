# app/controllers/matricula_controller.py
"""
Controlador para gestionar operaciones de matrícula.
Refactorizado para trabajar con la estructura correcta de la base de datos.
"""

from datetime import datetime
from decimal import Decimal
from app.models.matricula_model import MatriculaModel
from app.models.estudiante_model import EstudianteModel
from app.models.programa_academico_model import ProgramasAcademicosModel
from app.models.plan_pago_model import PlanPagoModel
from app.models.docente_model import DocenteModel


class MatriculaController:
    """
    Controlador principal para operaciones de matrícula.

    Responsabilidades:
    - Gestionar el ciclo completo de matrículas
    - Coordinar entre diferentes modelos
    - Validar reglas de negocio
    - Procesar pagos asociados
    - Generar reportes y estadísticas
    """

    def __init__(self):
        """
        Inicializa el controlador con todos los modelos necesarios.
        """
        self.matricula_model = MatriculaModel()
        self.estudiante_model = EstudianteModel()
        self.programa_model = ProgramasAcademicosModel()
        self.plan_pago_model = PlanPagoModel()
        self.docente_model = DocenteModel()

    # ============================================================================
    # MÉTODOS PRINCIPALES DE MATRÍCULA
    # ============================================================================

    def crear_matricula(
        self,
        estudiante_id,
        programa_id,
        modalidad_pago,
        monto_total,
        descuento_aplicado=0,
        plan_pago_id=None,
        fecha_inicio=None,
        coordinador_id=None,
        observaciones="",
    ):
        """
        Crea una nueva matrícula con validaciones completas.

        Args:
            estudiante_id (int): ID del estudiante
            programa_id (int): ID del programa académico
            modalidad_pago (str): Modalidad de pago ('CONTADO' o 'CUOTAS')
            monto_total (float): Monto total del programa
            descuento_aplicado (float): Descuento aplicado
            plan_pago_id (int, optional): ID del plan de pago (obligatorio si modalidad es 'CUOTAS')
            fecha_inicio (str, optional): Fecha de inicio del programa (YYYY-MM-DD)
            coordinador_id (int, optional): ID del coordinador/docente
            observaciones (str): Observaciones adicionales

        Returns:
            dict: Resultado con 'success', 'message' y datos adicionales
        """
        try:
            # 1. VALIDACIONES PREVIAS
            validacion = self._validar_creacion_matricula(
                estudiante_id, programa_id, modalidad_pago, plan_pago_id
            )
            if not validacion["success"]:
                return validacion

            estudiante = validacion["estudiante"]
            programa = validacion["programa"]

            # 2. VERIFICAR MATRÍCULA EXISTENTE
            if self._verificar_matricula_existente(estudiante_id, programa_id):
                return {
                    "success": False,
                    "message": "El estudiante ya está matriculado en este programa",
                }

            # 3. CALCULAR MONTOS
            monto_total_dec = Decimal(str(monto_total))
            descuento_dec = Decimal(str(descuento_aplicado))
            monto_final_dec = monto_total_dec - descuento_dec

            # 4. PREPARAR DATOS DE MATRÍCULA
            matricula_data = {
                "estudiante_id": estudiante_id,
                "programa_id": programa_id,
                "modalidad_pago": modalidad_pago,
                "plan_pago_id": plan_pago_id,
                "monto_total": float(monto_total_dec),
                "descuento_aplicado": float(descuento_dec),
                "monto_final": float(monto_final_dec),
                "monto_pagado": 0,
                "estado_pago": "PENDIENTE",
                "estado_academico": "PREINSCRITO",
                "fecha_inicio": fecha_inicio or datetime.now().strftime("%Y-%m-%d"),
                "coordinador_id": coordinador_id,
                "observaciones": observaciones,
            }

            # 5. CREAR MATRÍCULA EN BASE DE DATOS
            matricula_id = self.matricula_model.create(matricula_data)

            if not matricula_id:
                return {
                    "success": False,
                    "message": "Error al guardar la matrícula en la base de datos",
                }

            # 6. RESERVAR CUPO EN PROGRAMA
            if not self.programa_model.reservar_cupo(programa_id):
                print("⚠️ Advertencia: No se pudo reservar cupo en el programa")

            # 7. PREPARAR RESPUESTA
            respuesta = {
                "success": True,
                "message": "✅ Matrícula creada exitosamente",
                "matricula_id": matricula_id,
                "datos": {
                    "estudiante": f"{estudiante.get('nombres', '')} {estudiante.get('apellidos', '')}",
                    "programa": programa.get("nombre", ""),
                    "modalidad_pago": modalidad_pago,
                    "monto_total": float(monto_total_dec),
                    "descuento_aplicado": float(descuento_dec),
                    "monto_final": float(monto_final_dec),
                    "estado_pago": "PENDIENTE",
                    "estado_academico": "PREINSCRITO",
                },
            }

            return respuesta

        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error crítico al crear matrícula: {str(e)}",
            }

    # ============================================================================
    # MÉTODOS DE CONSULTA Y BÚSQUEDA
    # ============================================================================

    def obtener_matriculas(self, filtros=None, paginado=False, pagina=1, por_pagina=20):
        """
        Obtiene matrículas con múltiples opciones de filtrado y paginación.

        Args:
            filtros (dict): Diccionario con filtros aplicables
            paginado (bool): True para resultados paginados
            pagina (int): Número de página actual
            por_pagina (int): Elementos por página

        Returns:
            dict/list: Resultados según formato solicitado
        """
        try:
            # Aplicar filtros por defecto si no se especifican
            if filtros is None:
                filtros = {}

            # Extraer parámetros específicos
            estudiante_id = filtros.get("estudiante_id")
            programa_id = filtros.get("programa_id")
            estado_pago = filtros.get("estado_pago")
            estado_academico = filtros.get("estado_academico")

            # Obtener matrículas según formato
            if paginado:
                # Calcular offset para paginación
                offset = (pagina - 1) * por_pagina

                matriculas = self.matricula_model.get_all(
                    estudiante_id=estudiante_id,
                    programa_id=programa_id,
                    estado_pago=estado_pago,
                    estado_academico=estado_academico,
                    limit=por_pagina,
                    offset=offset,
                    order_by="fecha_matricula",
                    order_desc=True,
                )

                total = self.matricula_model.get_total_matriculas(
                    programa_id=programa_id,
                    estado_pago=estado_pago,
                    estado_academico=estado_academico,
                )

                return {
                    "success": True,
                    "pagina": pagina,
                    "por_pagina": por_pagina,
                    "total": total,
                    "total_paginas": (total + por_pagina - 1) // por_pagina,
                    "data": matriculas,
                }
            else:
                matriculas = self.matricula_model.get_all(
                    estudiante_id=estudiante_id,
                    programa_id=programa_id,
                    estado_pago=estado_pago,
                    estado_academico=estado_academico,
                    limit=100,  # Límite razonable para no paginar
                )
                return {"success": True, "total": len(matriculas), "data": matriculas}

        except Exception as e:
            print(f"⚠️ Error al obtener matrículas: {e}")
            return {"success": False, "data": [], "total": 0, "message": str(e)}

    def buscar_matriculas(self, criterio, valor, filtros_adicionales=None):
        """
        Búsqueda avanzada de matrículas por múltiples criterios.

        Args:
            criterio (str): Campo de búsqueda
            valor (str): Valor a buscar
            filtros_adicionales (dict): Filtros adicionales

        Returns:
            list: Matrículas encontradas con detalles
        """
        try:
            if filtros_adicionales is None:
                filtros_adicionales = {}

            # Mapear criterios a métodos del modelo
            criterios_validos = {
                "estudiante": self._buscar_por_estudiante,
                "programa": self._buscar_por_programa,
                "ci": self._buscar_por_ci_estudiante,
                "estado_pago": self._buscar_por_estado_pago,
                "estado_academico": self._buscar_por_estado_academico,
                "general": self._buscar_general,
            }

            if criterio in criterios_validos:
                return criterios_validos[criterio](valor, filtros_adicionales)
            else:
                # Búsqueda general por defecto
                return self._buscar_general(valor, filtros_adicionales)

        except Exception as e:
            print(f"⚠️ Error en búsqueda de matrículas: {e}")
            return []

    def obtener_matricula_por_id(self, matricula_id, completo=True):
        """
        Obtiene una matrícula específica con opción de datos completos.

        Args:
            matricula_id (int): ID de la matrícula
            completo (bool): True para incluir datos relacionados

        Returns:
            dict: Datos de la matrícula o None
        """
        try:
            if completo:
                return self.matricula_model.read(matricula_id)
            else:
                return self.matricula_model.obtener_por_id(matricula_id)

        except Exception as e:
            print(f"⚠️ Error al obtener matrícula {matricula_id}: {e}")
            return None

    # ============================================================================
    # MÉTODOS DE ACTUALIZACIÓN Y GESTIÓN
    # ============================================================================

    def actualizar_matricula(self, matricula_id, datos_actualizacion, usuario=None):
        """
        Actualiza una matrícula existente.

        Args:
            matricula_id (int): ID de la matrícula
            datos_actualizacion (dict): Campos a actualizar
            usuario (str, optional): Usuario que realiza la acción

        Returns:
            dict: Resultado de la operación
        """
        try:
            # 1. VERIFICAR EXISTENCIA
            matricula = self.matricula_model.read(matricula_id)
            if not matricula:
                return {"success": False, "message": "Matrícula no encontrada"}

            # 2. VALIDAR CAMBIOS PERMITIDOS
            validacion = self._validar_actualizacion_matricula(
                matricula, datos_actualizacion
            )
            if not validacion["success"]:
                return validacion

            # 3. APLICAR ACTUALIZACIÓN
            exito = self.matricula_model.update(matricula_id, datos_actualizacion)

            if exito:
                # 4. PROCESAR CAMBIOS ESPECIALES
                self._procesar_cambios_especiales(
                    matricula_id, matricula, datos_actualizacion
                )

                return {
                    "success": True,
                    "message": "✅ Matrícula actualizada exitosamente",
                    "matricula_id": matricula_id,
                }
            else:
                return {
                    "success": False,
                    "message": "❌ Error al actualizar en base de datos",
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error al actualizar matrícula: {str(e)}",
            }

    def anular_matricula(self, matricula_id, motivo="", usuario=None):
        """
        Anula una matrícula cambiando su estado académico a RETIRADO.

        Args:
            matricula_id (int): ID de la matrícula
            motivo (str): Motivo de la anulación
            usuario (str): Usuario que realiza la acción

        Returns:
            dict: Resultado de la operación
        """
        try:
            # Verificar que existe
            matricula = self.matricula_model.read(matricula_id)
            if not matricula:
                return {"success": False, "message": "Matrícula no encontrada"}

            # Verificar que no esté ya RETIRADO
            if matricula.get("estado_academico") == "RETIRADO":
                return {"success": False, "message": "La matrícula ya está retirada"}

            # Preparar datos de anulación
            datos_anulacion = {
                "estado_academico": "RETIRADO",
                "observaciones": f"{matricula.get('observaciones', '')}\nAnulado: {datetime.now().strftime('%Y-%m-%d')} - Motivo: {motivo}".strip(),
            }

            if usuario:
                datos_anulacion["observaciones"] += f" - Usuario: {usuario}"

            # Aplicar anulación
            exito = self.matricula_model.update(matricula_id, datos_anulacion)

            if exito:
                # Liberar cupo en el programa
                programa_id = matricula.get("programa_id")
                if programa_id is not None:
                    self.programa_model.liberar_cupo(programa_id)

                return {"success": True, "message": "✅ Matrícula anulada exitosamente"}
            else:
                return {"success": False, "message": "❌ Error al anular matrícula"}

        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error al anular matrícula: {str(e)}",
            }

    def completar_matricula(self, matricula_id, observaciones=""):
        """
        Marca una matrícula como completada (estado académico COMPLETADO).

        Args:
            matricula_id (int): ID de la matrícula
            observaciones (str): Observaciones del curso

        Returns:
            dict: Resultado de la operación
        """
        try:
            datos_completar = {
                "estado_academico": "COMPLETADO",
                "fecha_conclusion": datetime.now().strftime("%Y-%m-%d"),
                "observaciones": observaciones,
            }

            return self.actualizar_matricula(matricula_id, datos_completar)

        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error al completar matrícula: {str(e)}",
            }

    def registrar_pago_matricula(self, matricula_id, monto_pagado):
        """
        Registra un pago en la matrícula.

        Args:
            matricula_id (int): ID de la matrícula
            monto_pagado (float): Monto pagado a registrar

        Returns:
            dict: Resultado de la operación
        """
        try:
            # Obtener matrícula actual
            matricula = self.matricula_model.read(matricula_id)
            if not matricula:
                return {"success": False, "message": "Matrícula no encontrada"}

            monto_pagado_dec = Decimal(str(monto_pagado))

            # Registrar pago usando el método del modelo
            exito = self.matricula_model.registrar_pago(matricula_id, monto_pagado_dec)

            if exito:
                return {
                    "success": True,
                    "message": "✅ Pago registrado exitosamente",
                    "matricula_id": matricula_id,
                    "monto_pagado": float(monto_pagado_dec),
                }
            else:
                return {"success": False, "message": "❌ Error al registrar el pago"}

        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error al registrar pago: {str(e)}",
            }

    # ============================================================================
    # MÉTODOS DE REPORTES Y ESTADÍSTICAS
    # ============================================================================

    def obtener_estadisticas(
        self, programa_id=None, estado_pago=None, estado_academico=None
    ):
        """
        Obtiene estadísticas detalladas de matrículas.

        Args:
            programa_id (int): ID de programa específico
            estado_pago (str): Estado de pago específico
            estado_academico (str): Estado académico específico

        Returns:
            dict: Estadísticas completas
        """
        try:
            # Obtener estadísticas básicas del modelo
            estadisticas = self.matricula_model.get_estadisticas_pagos()

            # Obtener distribución por estado académico
            distribucion_estado = self.matricula_model.get_matriculas_por_estado()

            # Obtener matrículas por mes
            matriculas_mes = self.matricula_model.get_matriculas_por_mes()

            # Calcular total de matrículas
            total_matriculas = self.matricula_model.get_total_matriculas(
                programa_id=programa_id,
                estado_pago=estado_pago,
                estado_academico=estado_academico,
            )

            # Enriquecer con datos adicionales
            resultado = {
                "success": True,
                "fecha_consulta": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_matriculas": total_matriculas,
                "estadisticas_pagos": estadisticas,
                "distribucion_estado_academico": distribucion_estado,
                "matriculas_por_mes": matriculas_mes,
            }

            return resultado

        except Exception as e:
            print(f"⚠️ Error al obtener estadísticas: {e}")
            return {
                "success": False,
                "message": f"Error al obtener estadísticas: {str(e)}",
            }

    def generar_reporte_matriculas(self, tipo_reporte, parametros):
        """
        Genera diferentes tipos de reportes de matrículas.

        Args:
            tipo_reporte (str): Tipo de reporte a generar
            parametros (dict): Parámetros específicos del reporte

        Returns:
            dict: Datos del reporte generado
        """
        try:
            reportes_disponibles = {
                "por_programa": self._generar_reporte_por_programa,
                "por_estado_pago": self._generar_reporte_por_estado_pago,
                "por_estado_academico": self._generar_reporte_por_estado_academico,
                "por_mes": self._generar_reporte_por_mes,
                "detallado": self._generar_reporte_detallado,
            }

            if tipo_reporte not in reportes_disponibles:
                return {
                    "success": False,
                    "message": f"Tipo de reporte no válido: {tipo_reporte}",
                }

            # Generar reporte específico
            reporte = reportes_disponibles[tipo_reporte](parametros)

            return {
                "success": True,
                "reporte": tipo_reporte,
                "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "parametros": parametros,
                "data": reporte,
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error al generar reporte: {str(e)}",
            }

    # ============================================================================
    # MÉTODOS DE RELACIONES Y CONSULTAS ESPECIALES
    # ============================================================================

    def obtener_matriculas_estudiante(self, estudiante_id, solo_activas=True):
        """
        Obtiene todas las matrículas de un estudiante.

        Args:
            estudiante_id (int): ID del estudiante
            solo_activas (bool): True para filtrar solo matrículas activas (no RETIRADAS)

        Returns:
            dict: Matrículas del estudiante con estadísticas
        """
        try:
            matriculas = self.matricula_model.get_by_estudiante(estudiante_id)

            if solo_activas:
                matriculas = [
                    m for m in matriculas if m.get("estado_academico") != "RETIRADO"
                ]

            # Calcular estadísticas
            total_pagado = sum(
                Decimal(str(m.get("monto_pagado", 0))) for m in matriculas
            )
            total_pendiente = sum(
                Decimal(str(m.get("monto_final", 0)))
                - Decimal(str(m.get("monto_pagado", 0)))
                for m in matriculas
            )

            return {
                "success": True,
                "estudiante_id": estudiante_id,
                "total": len(matriculas),
                "total_pagado": float(total_pagado),
                "total_pendiente": float(total_pendiente),
                "data": matriculas,
            }

        except Exception as e:
            print(f"⚠️ Error al obtener matrículas del estudiante: {e}")
            return {"success": False, "data": [], "total": 0}

    def obtener_matriculas_programa(self, programa_id, estado_academico=None):
        """
        Obtiene todas las matrículas de un programa.

        Args:
            programa_id (int): ID del programa
            estado_academico (str, optional): Estado académico específico

        Returns:
            dict: Matrículas del programa con estadísticas
        """
        try:
            # Obtener información del programa
            programa = self.programa_model.read(programa_id)
            if not programa:
                return {"success": False, "message": "Programa no encontrado"}

            # Obtener matrículas
            matriculas = self.matricula_model.get_by_programa(programa_id)

            if estado_academico:
                matriculas = [
                    m
                    for m in matriculas
                    if m.get("estado_academico") == estado_academico
                ]

            # Calcular estadísticas
            total = len(matriculas)
            activas = len(
                [
                    m
                    for m in matriculas
                    if m.get("estado_academico")
                    not in ["RETIRADO", "SUSPENDIDO", "CANCELADO"]
                ]
            )
            completadas = len(
                [
                    m
                    for m in matriculas
                    if m.get("estado_academico") in ["COMPLETADO", "APROBADO"]
                ]
            )

            total_recaudado = sum(
                Decimal(str(m.get("monto_pagado", 0))) for m in matriculas
            )
            total_esperado = sum(
                Decimal(str(m.get("monto_final", 0))) for m in matriculas
            )

            return {
                "success": True,
                "programa": {
                    "id": programa["id"],
                    "nombre": programa["nombre"],
                    "codigo": programa["codigo"],
                },
                "estadisticas": {
                    "total_matriculas": total,
                    "activas": activas,
                    "completadas": completadas,
                    "retiradas": len(
                        [
                            m
                            for m in matriculas
                            if m.get("estado_academico") == "RETIRADO"
                        ]
                    ),
                    "total_recaudado": float(total_recaudado),
                    "total_esperado": float(total_esperado),
                    "porcentaje_recaudado": float(
                        (total_recaudado / total_esperado * 100)
                        if total_esperado > 0
                        else 0
                    ),
                    "cupos_disponibles": programa.get("cupos_disponibles", 0),
                },
                "data": matriculas,
            }

        except Exception as e:
            print(f"⚠️ Error al obtener matrículas del programa: {e}")
            return {"success": False, "data": [], "estadisticas": {}}

    # ============================================================================
    # MÉTODOS AUXILIARES PRIVADOS
    # ============================================================================

    def _validar_creacion_matricula(
        self, estudiante_id, programa_id, modalidad_pago, plan_pago_id
    ):
        """
        Valida condiciones previas para crear una matrícula.

        Args:
            estudiante_id (int): ID del estudiante
            programa_id (int): ID del programa
            modalidad_pago (str): Modalidad de pago
            plan_pago_id (int): ID del plan de pago

        Returns:
            dict: Resultado de validación
        """
        # 1. Verificar existencia del estudiante
        estudiante = self.estudiante_model.read(estudiante_id)
        if not estudiante:
            return {
                "success": False,
                "message": "Estudiante no encontrado en el sistema",
            }

        # 2. Verificar estado del estudiante
        if not estudiante.get("activo", True):
            return {
                "success": False,
                "message": "Estudiante no está activo",
            }

        # 3. Verificar existencia del programa
        programa = self.programa_model.read(programa_id)
        if not programa:
            return {"success": False, "message": "Programa no encontrado en el sistema"}

        # 4. Verificar estado del programa
        if programa.get("estado") not in ["PLANIFICADO", "INSCRIPCIONES", "EN_CURSO"]:
            return {
                "success": False,
                "message": f'Programa no está disponible para matrícula (Estado: {programa.get("estado")})',
            }

        # 5. Verificar cupos disponibles
        if programa.get("cupos_disponibles", 0) <= 0:
            return {
                "success": False,
                "message": "Programa sin cupos disponibles",
            }

        # 6. Validar modalidad de pago
        modalidades_validas = ["CONTADO", "CUOTAS"]
        if modalidad_pago not in modalidades_validas:
            return {
                "success": False,
                "message": f"Modalidad de pago inválida. Use: {', '.join(modalidades_validas)}",
            }

        # 7. Validar plan de pago si es necesario
        if modalidad_pago == "CUOTAS":
            if not plan_pago_id:
                return {
                    "success": False,
                    "message": "Modalidad CUOTAS requiere un plan de pago",
                }

            # Verificar que el plan de pago existe y está activo
            plan_pago = self.plan_pago_model.read(plan_pago_id)
            if not plan_pago or not plan_pago.get("activo", True):
                return {
                    "success": False,
                    "message": "Plan de pago no encontrado o no está activo",
                }

            # Verificar que el plan pertenece al programa
            if plan_pago.get("programa_id") != programa_id:
                return {
                    "success": False,
                    "message": "El plan de pago no corresponde al programa seleccionado",
                }
        else:
            # Para pago CONTADO, no debe tener plan de pago
            if plan_pago_id:
                return {
                    "success": False,
                    "message": "Modalidad CONTADO no debe tener plan de pago",
                }

        return {
            "success": True,
            "estudiante": estudiante,
            "programa": programa,
        }

    def _verificar_matricula_existente(self, estudiante_id, programa_id):
        """
        Verifica si el estudiante ya está matriculado en el programa.

        Args:
            estudiante_id (int): ID del estudiante
            programa_id (int): ID del programa

        Returns:
            bool: True si ya existe matrícula activa
        """
        try:
            # Usar el método del modelo para verificar existencia
            return self.matricula_model.matricula_exists(estudiante_id, programa_id)
        except Exception:
            return False

    def _validar_actualizacion_matricula(self, matricula_actual, nuevos_datos):
        """
        Valida que los cambios a una matrícula sean permitidos.

        Args:
            matricula_actual (dict): Datos actuales
            nuevos_datos (dict): Nuevos datos propuestos

        Returns:
            dict: Resultado de validación
        """
        # Validar estado académico si se cambia
        if "estado_academico" in nuevos_datos:
            nuevo_estado = nuevos_datos["estado_academico"]
            estado_actual = matricula_actual.get("estado_academico")

            # Estados académicos válidos
            estados_validos = [
                "PREINSCRITO",
                "INSCRITO",
                "EN_PROGRESO",
                "COMPLETADO",
                "APROBADO",
                "REPROBADO",
                "RETIRADO",
                "SUSPENDIDO",
            ]

            if nuevo_estado not in estados_validos:
                return {
                    "success": False,
                    "message": f"Estado académico inválido: {nuevo_estado}",
                }

            # Validar transiciones de estado
            estados_bloqueados = ["RETIRADO", "CANCELADO"]
            if estado_actual in estados_bloqueados and nuevo_estado != estado_actual:
                return {
                    "success": False,
                    "message": f"No se puede cambiar el estado de una matrícula {estado_actual}",
                }

        # Validar monto pagado no exceda monto final
        if "monto_pagado" in nuevos_datos:
            monto_pagado = Decimal(str(nuevos_datos["monto_pagado"]))
            monto_final = Decimal(str(matricula_actual.get("monto_final", 0)))

            if monto_pagado > monto_final:
                return {
                    "success": False,
                    "message": "Monto pagado no puede exceder el monto final",
                }

        return {"success": True}

    def _procesar_cambios_especiales(
        self, matricula_id, matricula_actual, nuevos_datos
    ):
        """
        Procesa cambios especiales en la matrícula.

        Args:
            matricula_id (int): ID de la matrícula
            matricula_actual (dict): Datos actuales
            nuevos_datos (dict): Nuevos datos aplicados
        """
        try:
            # Si se cambia el estado académico a RETIRADO, liberar cupo
            if (
                nuevos_datos.get("estado_academico") == "RETIRADO"
                and matricula_actual.get("estado_academico") != "RETIRADO"
            ):
                self.programa_model.liberar_cupo(matricula_actual.get("programa_id"))

            # Si se cambia de RETIRADO a otro estado, reservar cupo
            if (
                matricula_actual.get("estado_academico") == "RETIRADO"
                and nuevos_datos.get("estado_academico") != "RETIRADO"
            ):
                self.programa_model.reservar_cupo(matricula_actual.get("programa_id"))

        except Exception as e:
            print(f"⚠️ Error procesando cambios especiales: {e}")

    # ============================================================================
    # MÉTODOS DE BÚSQUEDA ESPECÍFICOS (PRIVADOS)
    # ============================================================================

    def _buscar_por_estudiante(self, valor, filtros):
        """Busca matrículas por nombre o apellido de estudiante."""
        try:
            # Buscar estudiantes que coincidan
            estudiantes = self.estudiante_model.search(valor)
            estudiante_ids = [e["id"] for e in estudiantes]

            if not estudiante_ids:
                return []

            # Buscar matrículas de esos estudiantes
            resultado = []
            for estudiante_id in estudiante_ids:
                matriculas = self.matricula_model.get_by_estudiante(estudiante_id)
                resultado.extend(matriculas)

            return resultado
        except Exception as e:
            print(f"⚠️ Error en búsqueda por estudiante: {e}")
            return []

    def _buscar_por_programa(self, valor, filtros):
        """Busca matrículas por nombre o código de programa."""
        try:
            # Buscar programas que coincidan
            programas = self.programa_model.search(valor)
            programa_ids = [p["id"] for p in programas]

            if not programa_ids:
                return []

            # Buscar matrículas de esos programas
            resultado = []
            for programa_id in programa_ids:
                matriculas = self.matricula_model.get_by_programa(programa_id)
                resultado.extend(matriculas)

            return resultado
        except Exception as e:
            print(f"⚠️ Error en búsqueda por programa: {e}")
            return []

    def _buscar_por_ci_estudiante(self, valor, filtros):
        """Busca matrículas por CI de estudiante."""
        try:
            # Buscar estudiante por CI
            estudiante = self.estudiante_model.get_by_ci(valor)
            if not estudiante:
                return []

            # Buscar matrículas del estudiante
            return self.matricula_model.get_by_estudiante(estudiante["id"])
        except Exception as e:
            print(f"⚠️ Error en búsqueda por CI: {e}")
            return []

    def _buscar_por_estado_pago(self, valor, filtros):
        """Busca matrículas por estado de pago."""
        try:
            return self.matricula_model.get_all(estado_pago=valor)
        except Exception as e:
            print(f"⚠️ Error en búsqueda por estado de pago: {e}")
            return []

    def _buscar_por_estado_academico(self, valor, filtros):
        """Busca matrículas por estado académico."""
        try:
            return self.matricula_model.get_all(estado_academico=valor)
        except Exception as e:
            print(f"⚠️ Error en búsqueda por estado académico: {e}")
            return []

    def _buscar_general(self, valor, filtros):
        """Búsqueda general en todas las matrículas."""
        try:
            return self.matricula_model.search(valor)
        except Exception as e:
            print(f"⚠️ Error en búsqueda general: {e}")
            return []

    # ============================================================================
    # MÉTODOS DE GENERACIÓN DE REPORTES (PRIVADOS)
    # ============================================================================

    def _generar_reporte_por_programa(self, parametros):
        """Genera reporte de matrículas por programa."""
        programa_id = parametros.get("programa_id")

        if programa_id:
            return self.obtener_matriculas_programa(programa_id)
        else:
            # Reporte general por programa
            programas = self.programa_model.get_all(active_only=True)
            reporte = []

            for programa in programas:
                programa_id = programa["id"]
                info = self.obtener_matriculas_programa(programa_id)
                if info["success"]:
                    reporte.append(
                        {
                            "programa": programa,
                            "estadisticas": info.get("estadisticas", {}),
                            "total_matriculas": len(info.get("data", [])),
                        }
                    )

            return reporte

    def _generar_reporte_por_estado_pago(self, parametros):
        """Genera reporte de matrículas por estado de pago."""
        estados_pago = self.matricula_model.get_estados_pago()
        reporte = []

        for estado in estados_pago:
            matriculas = self.matricula_model.get_all(estado_pago=estado)
            total_monto = sum(Decimal(str(m.get("monto_final", 0))) for m in matriculas)
            total_pagado = sum(
                Decimal(str(m.get("monto_pagado", 0))) for m in matriculas
            )

            reporte.append(
                {
                    "estado_pago": estado,
                    "total_matriculas": len(matriculas),
                    "total_monto": float(total_monto),
                    "total_pagado": float(total_pagado),
                    "porcentaje_pagado": float(
                        (total_pagado / total_monto * 100) if total_monto > 0 else 0
                    ),
                    "matriculas": matriculas[:10],  # Limitar detalles
                }
            )

        return reporte

    def _generar_reporte_por_estado_academico(self, parametros):
        """Genera reporte de matrículas por estado académico."""
        estados_academicos = self.matricula_model.get_estados_academicos()
        reporte = []

        for estado in estados_academicos:
            matriculas = self.matricula_model.get_all(estado_academico=estado)
            total_monto = sum(Decimal(str(m.get("monto_final", 0))) for m in matriculas)

            reporte.append(
                {
                    "estado_academico": estado,
                    "total_matriculas": len(matriculas),
                    "total_monto": float(total_monto),
                    "matriculas": matriculas[:10],  # Limitar detalles
                }
            )

        return reporte

    def _generar_reporte_por_mes(self, parametros):
        """Genera reporte de matrículas por mes."""
        year = parametros.get("year", datetime.now().year)

        matriculas_mes = self.matricula_model.get_matriculas_por_mes(year)

        # Enriquecer con nombres de mes
        meses = {
            1: "Enero",
            2: "Febrero",
            3: "Marzo",
            4: "Abril",
            5: "Mayo",
            6: "Junio",
            7: "Julio",
            8: "Agosto",
            9: "Septiembre",
            10: "Octubre",
            11: "Noviembre",
            12: "Diciembre",
        }

        for item in matriculas_mes:
            item["mes_nombre"] = meses.get(int(item.get("mes", 0)), "Desconocido")

        return {
            "year": year,
            "matriculas_por_mes": matriculas_mes,
            "total_matriculas": sum(item.get("cantidad", 0) for item in matriculas_mes),
            "total_monto": sum(
                Decimal(str(item.get("monto_total", 0))) for item in matriculas_mes
            ),
        }

    def _generar_reporte_detallado(self, parametros):
        """Genera reporte detallado de matrículas con filtros."""
        filtros = parametros.get("filtros", {})

        # Aplicar filtros
        estudiante_id = filtros.get("estudiante_id")
        programa_id = filtros.get("programa_id")
        estado_pago = filtros.get("estado_pago")
        estado_academico = filtros.get("estado_academico")
        fecha_desde = filtros.get("fecha_desde")
        fecha_hasta = filtros.get("fecha_hasta")

        # Obtener todas las matrículas primero
        matriculas = self.matricula_model.get_all(
            estudiante_id=estudiante_id,
            programa_id=programa_id,
            estado_pago=estado_pago,
            estado_academico=estado_academico,
            limit=1000,  # Límite alto para reportes
        )

        # Filtrar por fecha si se especifica
        if fecha_desde or fecha_hasta:
            matriculas_filtradas = []
            for matricula in matriculas:
                fecha_matricula = matricula.get("fecha_matricula")
                if fecha_matricula:
                    if fecha_desde and fecha_matricula < fecha_desde:
                        continue
                    if fecha_hasta and fecha_matricula > fecha_hasta:
                        continue
                matriculas_filtradas.append(matricula)
            matriculas = matriculas_filtradas

        # Calcular resúmenes
        total_monto_final = sum(
            Decimal(str(m.get("monto_final", 0))) for m in matriculas
        )
        total_monto_pagado = sum(
            Decimal(str(m.get("monto_pagado", 0))) for m in matriculas
        )
        total_monto_pendiente = total_monto_final - total_monto_pagado

        return {
            "filtros_aplicados": filtros,
            "total_matriculas": len(matriculas),
            "resumen_financiero": {
                "total_monto_final": float(total_monto_final),
                "total_monto_pagado": float(total_monto_pagado),
                "total_monto_pendiente": float(total_monto_pendiente),
                "porcentaje_pagado": float(
                    (total_monto_pagado / total_monto_final * 100)
                    if total_monto_final > 0
                    else 0
                ),
            },
            "matriculas": matriculas,
        }

    # ============================================================================
    # MÉTODOS DE UTILIDAD
    # ============================================================================

    def obtener_modalidades_pago(self):
        """
        Obtiene la lista de modalidades de pago disponibles.

        Returns:
            list: Lista de modalidades de pago
        """
        return self.matricula_model.get_modalidades_pago()

    def obtener_estados_pago(self):
        """
        Obtiene la lista de estados de pago disponibles.

        Returns:
            list: Lista de estados de pago
        """
        return self.matricula_model.get_estados_pago()

    def obtener_estados_academicos(self):
        """
        Obtiene la lista de estados académicos disponibles.

        Returns:
            list: Lista de estados académicos
        """
        return self.matricula_model.get_estados_academicos()

    def cambiar_estado_pago(self, matricula_id, nuevo_estado):
        """
        Cambia el estado de pago de una matrícula.

        Args:
            matricula_id (int): ID de la matrícula
            nuevo_estado (str): Nuevo estado de pago

        Returns:
            dict: Resultado de la operación
        """
        try:
            exito = self.matricula_model.cambiar_estado_pago(matricula_id, nuevo_estado)

            if exito:
                return {
                    "success": True,
                    "message": f"✅ Estado de pago cambiado a {nuevo_estado}",
                    "matricula_id": matricula_id,
                }
            else:
                return {
                    "success": False,
                    "message": "❌ Error al cambiar estado de pago",
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error al cambiar estado de pago: {str(e)}",
            }

    def cambiar_estado_academico(self, matricula_id, nuevo_estado):
        """
        Cambia el estado académico de una matrícula.

        Args:
            matricula_id (int): ID de la matrícula
            nuevo_estado (str): Nuevo estado académico

        Returns:
            dict: Resultado de la operación
        """
        try:
            exito = self.matricula_model.cambiar_estado_academico(
                matricula_id, nuevo_estado
            )

            if exito:
                return {
                    "success": True,
                    "message": f"✅ Estado académico cambiado a {nuevo_estado}",
                    "matricula_id": matricula_id,
                }
            else:
                return {
                    "success": False,
                    "message": "❌ Error al cambiar estado académico",
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error al cambiar estado académico: {str(e)}",
            }
