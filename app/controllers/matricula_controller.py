# app/controllers/matricula_controller.py
"""
Controlador para gestionar operaciones de matrícula.
Refactorizado para mantener todas las funcionalidades existentes del repositorio
con una arquitectura mejorada y documentación completa.
"""

from datetime import datetime
from app.models.matricula_model import MatriculaModel
from app.models.estudiante_model import EstudianteModel
from app.models.curso_model import CursoModel
from app.models.ingreso_model import IngresoModel
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
        self.curso_model = CursoModel()
        self.ingreso_model = IngresoModel()
        self.docente_model = DocenteModel()

    # ============================================================================
    # MÉTODOS PRINCIPALES DE MATRÍCULA
    # ============================================================================

    def crear_matricula(
        self,
        estudiante_id,
        curso_id,
        fecha_matricula=None,
        estado="Activa",
        monto_pagado=0,
        metodo_pago="Efectivo",
    ):
        """
        Crea una nueva matrícula con validaciones completas.

        Args:
            estudiante_id (int): ID del estudiante
            curso_id (int): ID del curso
            fecha_matricula (str, optional): Fecha en formato YYYY-MM-DD. Default: hoy
            estado (str): Estado inicial de la matrícula
            monto_pagado (float): Monto pagado inicialmente
            metodo_pago (str): Método de pago utilizado

        Returns:
            dict: Resultado con 'success', 'message' y datos adicionales
        """
        try:
            # 1. VALIDACIONES PREVIAS
            validacion = self._validar_creacion_matricula(estudiante_id, curso_id)
            if not validacion["success"]:
                return validacion

            estudiante = validacion["estudiante"]
            curso = validacion["curso"]

            # 2. VERIFICAR MATRÍCULA EXISTENTE
            if self._verificar_matricula_existente(estudiante_id, curso_id):
                return {
                    "success": False,
                    "message": "El estudiante ya está matriculado en este curso",
                }

            # 3. PREPARAR DATOS DE MATRÍCULA
            fecha_matricula = fecha_matricula or datetime.now().strftime("%Y-%m-%d")
            matricula_data = {
                "estudiante_id": estudiante_id,
                "curso_id": curso_id,
                "fecha_matricula": fecha_matricula,
                "estado": estado,
                "monto_pagado": monto_pagado,
                "metodo_pago": metodo_pago,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }

            # 4. CREAR MATRÍCULA EN BASE DE DATOS
            matricula_id = self.matricula_model.create(matricula_data)

            if not matricula_id:
                return {
                    "success": False,
                    "message": "Error al guardar la matrícula en la base de datos",
                }

            # 5. PROCESAR PAGO SI EXISTE
            resultado_pago = None
            if monto_pagado > 0:
                resultado_pago = self._procesar_pago_matricula(
                    matricula_id,
                    estudiante_id,
                    curso,
                    monto_pagado,
                    metodo_pago,
                    fecha_matricula,
                )

            # 6. ACTUALIZAR CONTADORES
            self._actualizar_contadores_matricula(estudiante_id, curso_id)

            # 7. PREPARAR RESPUESTA
            respuesta = {
                "success": True,
                "message": "✅ Matrícula creada exitosamente",
                "matricula_id": matricula_id,
                "datos": {
                    "estudiante": f"{estudiante.get('nombre', '')} {estudiante.get('apellido', '')}",
                    "curso": curso.get("nombre", ""),
                    "fecha": fecha_matricula,
                    "estado": estado,
                    "monto_pagado": monto_pagado,
                },
            }

            if resultado_pago:
                respuesta["pago"] = resultado_pago

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

            # Obtener matrículas según formato
            if paginado:
                return self.matricula_model.get_paginados(
                    pagina=pagina, por_pagina=por_pagina, filtros=filtros
                )
            else:
                matriculas = self.matricula_model.get_all_with_details(filtros)
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
            # Mapear criterios a métodos del modelo
            criterios_validos = {
                "estudiante": "search_by_estudiante",
                "curso": "search_by_curso",
                "estado": "search_by_estado",
                "fecha": "search_by_fecha",
                "docente": "search_by_docente",
                "codigo": "search_by_codigo_matricula",
            }

            if criterio not in criterios_validos:
                # Búsqueda general
                return self.matricula_model.search_general(valor, filtros_adicionales)

            # Llamar al método específico del modelo
            metodo_busqueda = getattr(self.matricula_model, criterios_validos[criterio])
            return metodo_busqueda(valor, filtros_adicionales)

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
                return self.matricula_model.get_completa_by_id(matricula_id)
            else:
                return self.matricula_model.get_by_id(matricula_id)

        except Exception as e:
            print(f"⚠️ Error al obtener matrícula {matricula_id}: {e}")
            return None

    # ============================================================================
    # MÉTODOS DE ACTUALIZACIÓN Y GESTIÓN
    # ============================================================================

    def actualizar_matricula(self, matricula_id, datos_actualizacion, usuario=None):
        """
        Actualiza una matrícula existente con registro de cambios.

        Args:
            matricula_id (int): ID de la matrícula
            datos_actualizacion (dict): Campos a actualizar
            usuario (str, optional): Usuario que realiza la acción

        Returns:
            dict: Resultado de la operación
        """
        try:
            # 1. VERIFICAR EXISTENCIA
            matricula = self.matricula_model.get_by_id(matricula_id)
            if not matricula:
                return {"success": False, "message": "Matrícula no encontrada"}

            # 2. VALIDAR CAMBIOS PERMITIDOS
            validacion = self._validar_actualizacion_matricula(
                matricula, datos_actualizacion
            )
            if not validacion["success"]:
                return validacion

            # 3. REGISTRAR HISTÓRICO DE CAMBIOS
            if usuario:
                self._registrar_cambio_matricula(
                    matricula_id, matricula, datos_actualizacion, usuario
                )

            # 4. APLICAR ACTUALIZACIÓN
            datos_actualizacion["updated_at"] = datetime.now()
            exito = self.matricula_model.update(matricula_id, datos_actualizacion)

            if exito:
                # 5. PROCESAR CAMBIOS ESPECIALES
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
        Anula una matrícula cambiando su estado.

        Args:
            matricula_id (int): ID de la matrícula
            motivo (str): Motivo de la anulación
            usuario (str): Usuario que realiza la acción

        Returns:
            dict: Resultado de la operación
        """
        try:
            # Verificar que existe
            matricula = self.matricula_model.get_by_id(matricula_id)
            if not matricula:
                return {"success": False, "message": "Matrícula no encontrada"}

            # Verificar que no esté ya anulada
            if matricula.get("estado") == "Anulada":
                return {"success": False, "message": "La matrícula ya está anulada"}

            # Preparar datos de anulación
            datos_anulacion = {
                "estado": "Anulada",
                "fecha_anulacion": datetime.now().strftime("%Y-%m-%d"),
                "motivo_anulacion": motivo,
                "updated_at": datetime.now(),
            }

            if usuario:
                datos_anulacion["anulado_por"] = usuario

            # Aplicar anulación
            exito = self.matricula_model.update(matricula_id, datos_anulacion)

            if exito:
                # Registrar en histórico
                self._registrar_anulacion(matricula_id, matricula, motivo, usuario)

                # Actualizar contadores
                self._actualizar_contadores_anulacion(matricula)

                return {"success": True, "message": "✅ Matrícula anulada exitosamente"}
            else:
                return {"success": False, "message": "❌ Error al anular matrícula"}

        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error al anular matrícula: {str(e)}",
            }

    def completar_matricula(self, matricula_id, calificacion=None, observaciones=""):
        """
        Marca una matrícula como completada.

        Args:
            matricula_id (int): ID de la matrícula
            calificacion (float, optional): Calificación final
            observaciones (str): Observaciones del curso

        Returns:
            dict: Resultado de la operación
        """
        try:
            datos_completar = {
                "estado": "Completada",
                "fecha_completacion": datetime.now().strftime("%Y-%m-%d"),
                "observaciones": observaciones,
                "updated_at": datetime.now(),
            }

            if calificacion is not None:
                datos_completar["calificacion_final"] = calificacion

            return self.actualizar_matricula(matricula_id, datos_completar)

        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error al completar matrícula: {str(e)}",
            }

    # ============================================================================
    # MÉTODOS DE REPORTES Y ESTADÍSTICAS
    # ============================================================================

    def obtener_estadisticas(self, periodo=None, curso_id=None, docente_id=None):
        """
        Obtiene estadísticas detalladas de matrículas.

        Args:
            periodo (str): Periodo específico (YYYY-MM)
            curso_id (int): ID de curso específico
            docente_id (int): ID de docente específico

        Returns:
            dict: Estadísticas completas
        """
        try:
            filtros = {}
            if periodo:
                filtros["periodo"] = periodo
            if curso_id:
                filtros["curso_id"] = curso_id
            if docente_id:
                filtros["docente_id"] = docente_id

            # Obtener estadísticas básicas
            estadisticas = self.matricula_model.get_estadisticas(filtros)

            # Enriquecer con datos adicionales
            estadisticas["periodo"] = periodo or "General"
            estadisticas["fecha_consulta"] = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            # Calcular porcentajes
            total = estadisticas.get("total_matriculas", 0)
            if total > 0:
                estadisticas["porcentaje_activas"] = (
                    estadisticas.get("activas", 0) / total
                ) * 100
                estadisticas["porcentaje_completadas"] = (
                    estadisticas.get("completadas", 0) / total
                ) * 100
                estadisticas["porcentaje_anuladas"] = (
                    estadisticas.get("anuladas", 0) / total
                ) * 100
                estadisticas["tasa_completacion"] = (
                    estadisticas.get("completadas", 0)
                    / max(estadisticas.get("activas", 0), 1)
                ) * 100

            return {"success": True, "data": estadisticas}

        except Exception as e:
            print(f"⚠️ Error al obtener estadísticas: {e}")
            return {
                "success": False,
                "data": {
                    "total_matriculas": 0,
                    "activas": 0,
                    "completadas": 0,
                    "anuladas": 0,
                    "total_recaudado": 0,
                },
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
                "diario": self._generar_reporte_diario,
                "mensual": self._generar_reporte_mensual,
                "por_curso": self._generar_reporte_por_curso,
                "por_docente": self._generar_reporte_por_docente,
                "ingresos": self._generar_reporte_ingresos,
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
            solo_activas (bool): True para filtrar solo matrículas activas

        Returns:
            list: Matrículas del estudiante
        """
        try:
            matriculas = self.matricula_model.get_matriculas_estudiante(estudiante_id)

            if solo_activas:
                matriculas = [m for m in matriculas if m.get("estado") == "Activa"]

            return {
                "success": True,
                "estudiante_id": estudiante_id,
                "total": len(matriculas),
                "activas": len([m for m in matriculas if m.get("estado") == "Activa"]),
                "data": matriculas,
            }

        except Exception as e:
            print(f"⚠️ Error al obtener matrículas del estudiante: {e}")
            return {"success": False, "data": [], "total": 0}

    def obtener_matriculas_curso(self, curso_id, periodo=None):
        """
        Obtiene todas las matrículas de un curso.

        Args:
            curso_id (int): ID del curso
            periodo (str, optional): Periodo específico

        Returns:
            dict: Matrículas del curso con estadísticas
        """
        try:
            filtros = {"curso_id": curso_id}
            if periodo:
                filtros["periodo"] = periodo

            matriculas = self.matricula_model.get_matriculas_curso(curso_id, filtros)

            # Obtener información del curso
            curso = self.curso_model.get_by_id(curso_id)

            # Calcular estadísticas
            total = len(matriculas)
            activas = len([m for m in matriculas if m.get("estado") == "Activa"])
            completadas = len(
                [m for m in matriculas if m.get("estado") == "Completada"]
            )

            return {
                "success": True,
                "curso": curso,
                "estadisticas": {
                    "total_matriculas": total,
                    "activas": activas,
                    "completadas": completadas,
                    "anuladas": total - activas - completadas,
                    "cupos_disponibles": (
                        curso.get("cupo_maximo", 0) - total if curso else 0
                    ),
                },
                "data": matriculas,
            }

        except Exception as e:
            print(f"⚠️ Error al obtener matrículas del curso: {e}")
            return {"success": False, "data": [], "estadisticas": {}}

    # ============================================================================
    # MÉTODOS AUXILIARES PRIVADOS
    # ============================================================================

    def _validar_creacion_matricula(self, estudiante_id, curso_id):
        """
        Valida condiciones previas para crear una matrícula.

        Args:
            estudiante_id (int): ID del estudiante
            curso_id (int): ID del curso

        Returns:
            dict: Resultado de validación
        """
        # 1. Verificar existencia del estudiante
        estudiante = self.estudiante_model.get_by_id(estudiante_id)
        if not estudiante:
            return {
                "success": False,
                "message": "Estudiante no encontrado en el sistema",
            }

        # 2. Verificar estado del estudiante
        if estudiante.get("estado") != "Activo":
            return {
                "success": False,
                "message": f'Estudiante no está activo (Estado: {estudiante.get("estado")})',
            }

        # 3. Verificar existencia del curso
        curso = self.curso_model.get_by_id(curso_id)
        if not curso:
            return {"success": False, "message": "Curso no encontrado en el sistema"}

        # 4. Verificar estado del curso
        if curso.get("estado") != "Activo":
            return {
                "success": False,
                "message": f'Curso no está activo (Estado: {curso.get("estado")})',
            }

        # 5. Verificar cupos disponibles
        matriculas_curso = self.matricula_model.get_matriculas_curso(curso_id)
        cupo_maximo = curso.get("cupo_maximo", 0)

        if cupo_maximo > 0 and len(matriculas_curso) >= cupo_maximo:
            return {
                "success": False,
                "message": f"Curso sin cupos disponibles (Cupo máximo: {cupo_maximo})",
            }

        return {"success": True, "estudiante": estudiante, "curso": curso}

    def _verificar_matricula_existente(self, estudiante_id, curso_id):
        """
        Verifica si el estudiante ya está matriculado en el curso.

        Args:
            estudiante_id (int): ID del estudiante
            curso_id (int): ID del curso

        Returns:
            bool: True si ya existe matrícula activa
        """
        try:
            matriculas = self.matricula_model.get_matriculas_estudiante(estudiante_id)

            for matricula in matriculas:
                if matricula.get("curso_id") == curso_id and matricula.get(
                    "estado"
                ) in ["Activa", "En proceso"]:
                    return True

            return False

        except Exception:
            return False

    def _procesar_pago_matricula(
        self, matricula_id, estudiante_id, curso, monto, metodo_pago, fecha_pago
    ):
        """
        Procesa el pago asociado a una matrícula.

        Args:
            matricula_id (int): ID de la matrícula
            estudiante_id (int): ID del estudiante
            curso (dict): Datos del curso
            monto (float): Monto del pago
            metodo_pago (str): Método de pago
            fecha_pago (str): Fecha del pago

        Returns:
            dict: Resultado del procesamiento del pago
        """
        try:
            # Registrar ingreso
            ingreso_data = {
                "estudiante_id": estudiante_id,
                "matricula_id": matricula_id,
                "monto": monto,
                "concepto": f'Matrícula - {curso.get("nombre", "Curso")}',
                "metodo_pago": metodo_pago,
                "fecha_pago": fecha_pago,
                "tipo_ingreso": "Matrícula",
                "estado": "Confirmado",
            }

            ingreso_id = self.ingreso_model.registrar_ingreso(ingreso_data)

            if ingreso_id:
                return {
                    "success": True,
                    "ingreso_id": ingreso_id,
                    "message": "Pago registrado exitosamente",
                }
            else:
                return {"success": False, "message": "Error al registrar el pago"}

        except Exception as e:
            print(f"⚠️ Error al procesar pago: {e}")
            return {
                "success": False,
                "message": f"Error en procesamiento de pago: {str(e)}",
            }

    def _actualizar_contadores_matricula(self, estudiante_id, curso_id):
        """
        Actualiza contadores después de crear una matrícula.

        Args:
            estudiante_id (int): ID del estudiante
            curso_id (int): ID del curso
        """
        try:
            # Actualizar contador de matrículas del estudiante
            self.estudiante_model.incrementar_contador_matriculas(estudiante_id)

            # Actualizar contador de estudiantes en curso
            self.curso_model.incrementar_contador_estudiantes(curso_id)

        except Exception as e:
            print(f"⚠️ Error al actualizar contadores: {e}")

    def _validar_actualizacion_matricula(self, matricula_actual, nuevos_datos):
        """
        Valida que los cambios a una matrícula sean permitidos.

        Args:
            matricula_actual (dict): Datos actuales
            nuevos_datos (dict): Nuevos datos propuestos

        Returns:
            dict: Resultado de validación
        """
        estado_actual = matricula_actual.get("estado")
        nuevo_estado = nuevos_datos.get("estado")

        # Validar transiciones de estado
        if nuevo_estado and nuevo_estado != estado_actual:
            transiciones_validas = {
                "Activa": ["En proceso", "Completada", "Anulada"],
                "En proceso": ["Activa", "Anulada"],
                "Completada": [],  # No se puede cambiar desde completada
                "Anulada": [],  # No se puede cambiar desde anulada
            }

            if estado_actual in transiciones_validas:
                if nuevo_estado not in transiciones_validas[estado_actual]:
                    return {
                        "success": False,
                        "message": f'No se puede cambiar de "{estado_actual}" a "{nuevo_estado}"',
                    }

        return {"success": True}

    def _registrar_cambio_matricula(
        self, matricula_id, datos_anteriores, datos_nuevos, usuario
    ):
        """
        Registra un cambio en el histórico de matrículas.

        Args:
            matricula_id (int): ID de la matrícula
            datos_anteriores (dict): Datos antes del cambio
            datos_nuevos (dict): Datos después del cambio
            usuario (str): Usuario que realiza el cambio
        """
        try:
            cambios = []
            for campo, valor_nuevo in datos_nuevos.items():
                if campo in datos_anteriores and datos_anteriores[campo] != valor_nuevo:
                    cambios.append(
                        {
                            "campo": campo,
                            "valor_anterior": datos_anteriores[campo],
                            "valor_nuevo": valor_nuevo,
                            "fecha_cambio": datetime.now(),
                            "usuario": usuario,
                        }
                    )

            if cambios:
                self.matricula_model.registrar_cambios(matricula_id, cambios)

        except Exception as e:
            print(f"⚠️ Error al registrar cambios: {e}")

    def _registrar_anulacion(self, matricula_id, matricula, motivo, usuario):
        """
        Registra detalles específicos de una anulación.

        Args:
            matricula_id (int): ID de la matrícula
            matricula (dict): Datos de la matrícula
            motivo (str): Motivo de anulación
            usuario (str): Usuario que realiza la anulación
        """
        try:
            registro_anulacion = {
                "matricula_id": matricula_id,
                "estudiante_id": matricula.get("estudiante_id"),
                "curso_id": matricula.get("curso_id"),
                "fecha_anulacion": datetime.now(),
                "motivo": motivo,
                "usuario": usuario,
                "monto_pagado": matricula.get("monto_pagado", 0),
                "estado_anterior": matricula.get("estado"),
            }

            self.matricula_model.registrar_anulacion(registro_anulacion)

        except Exception as e:
            print(f"⚠️ Error al registrar anulación: {e}")

    def _actualizar_contadores_anulacion(self, matricula):
        """
        Actualiza contadores después de anular una matrícula.

        Args:
            matricula (dict): Datos de la matrícula anulada
        """
        try:
            # Decrementar contador en curso si estaba activa
            if matricula.get("estado") == "Activa":
                self.curso_model.decrementar_contador_estudiantes(
                    matricula.get("curso_id")
                )

        except Exception as e:
            print(f"⚠️ Error al actualizar contadores de anulación: {e}")

    # ============================================================================
    # MÉTODOS DE GENERACIÓN DE REPORTES (PRIVADOS)
    # ============================================================================

    def _generar_reporte_diario(self, parametros):
        """Genera reporte diario de matrículas."""
        fecha = parametros.get("fecha", datetime.now().strftime("%Y-%m-%d"))

        filtros = {"fecha_matricula": fecha}

        matriculas = self.matricula_model.get_all_with_details(filtros)

        return {
            "fecha": fecha,
            "total_matriculas": len(matriculas),
            "matriculas": matriculas,
            "resumen_por_curso": self._resumir_por_curso(matriculas),
        }

    def _generar_reporte_mensual(self, parametros):
        """Genera reporte mensual de matrículas."""
        mes = parametros.get("mes", datetime.now().strftime("%Y-%m"))

        filtros = {"mes_matricula": mes}

        matriculas = self.matricula_model.get_all_with_details(filtros)

        return {
            "mes": mes,
            "total_matriculas": len(matriculas),
            "ingresos_totales": sum(m.get("monto_pagado", 0) for m in matriculas),
            "matriculas_por_dia": self._agrupar_por_dia(matriculas),
            "resumen_por_curso": self._resumir_por_curso(matriculas),
        }

    def _generar_reporte_por_curso(self, parametros):
        """Genera reporte de matrículas por curso."""
        curso_id = parametros.get("curso_id")
        periodo = parametros.get("periodo")

        return self.obtener_matriculas_curso(curso_id, periodo)

    def _generar_reporte_por_docente(self, parametros):
        """Genera reporte de matrículas por docente."""
        docente_id = parametros.get("docente_id")

        # Obtener cursos del docente
        cursos_docente = self.curso_model.get_cursos_por_docente(docente_id)

        reporte = {
            "docente": self.docente_model.get_by_id(docente_id),
            "total_cursos": len(cursos_docente),
            "cursos": [],
        }

        # Para cada curso, obtener matrículas
        for curso in cursos_docente:
            curso_id = curso["id"]
            matricula_info = self.obtener_matriculas_curso(curso_id)
            reporte["cursos"].append({"curso": curso, "matriculas": matricula_info})

        return reporte

    def _generar_reporte_ingresos(self, parametros):
        """Genera reporte de ingresos por matrículas."""
        fecha_inicio = parametros.get("fecha_inicio")
        fecha_fin = parametros.get("fecha_fin") or datetime.now().strftime("%Y-%m-%d")

        # Obtener ingresos del periodo
        ingresos = self.ingreso_model.obtener_ingresos_periodo(
            fecha_inicio, fecha_fin, tipo="Matrícula"
        )

        return {
            "periodo": f"{fecha_inicio} a {fecha_fin}",
            "total_ingresos": sum(i.get("monto", 0) for i in ingresos),
            "ingresos_por_metodo": self._agrupar_por_metodo_pago(ingresos),
            "ingresos_por_curso": self._agrupar_ingresos_por_curso(ingresos),
            "detalle": ingresos,
        }

    # ============================================================================
    # MÉTODOS DE AGRUPAMIENTO Y RESUMEN (PRIVADOS)
    # ============================================================================

    def _resumir_por_curso(self, matriculas):
        """Agrupa matrículas por curso."""
        resumen = {}

        for matricula in matriculas:
            curso_id = matricula.get("curso_id")
            curso_nombre = matricula.get("curso_nombre", "Sin nombre")

            if curso_id not in resumen:
                resumen[curso_id] = {
                    "nombre": curso_nombre,
                    "total": 0,
                    "activas": 0,
                    "completadas": 0,
                    "anuladas": 0,
                }

            resumen[curso_id]["total"] += 1

            estado = matricula.get("estado", "")
            if estado == "Activa":
                resumen[curso_id]["activas"] += 1
            elif estado == "Completada":
                resumen[curso_id]["completadas"] += 1
            elif estado == "Anulada":
                resumen[curso_id]["anuladas"] += 1

        return resumen

    def _agrupar_por_dia(self, matriculas):
        """Agrupa matrículas por día."""
        agrupado = {}

        for matricula in matriculas:
            fecha = matricula.get("fecha_matricula")
            if fecha not in agrupado:
                agrupado[fecha] = []

            agrupado[fecha].append(matricula)

        # Ordenar por fecha
        return dict(sorted(agrupado.items()))

    def _agrupar_por_metodo_pago(self, ingresos):
        """Agrupa ingresos por método de pago."""
        agrupado = {}

        for ingreso in ingresos:
            metodo = ingreso.get("metodo_pago", "No especificado")
            if metodo not in agrupado:
                agrupado[metodo] = 0

            agrupado[metodo] += ingreso.get("monto", 0)

        return agrupado

    def _agrupar_ingresos_por_curso(self, ingresos):
        """Agrupa ingresos por curso."""
        agrupado = {}

        for ingreso in ingresos:
            # Extraer curso del concepto o usar matrícula
            concepto = ingreso.get("concepto", "")
            curso_id = ingreso.get("curso_id") or 0

            if "Matrícula - " in concepto:
                curso_nombre = concepto.replace("Matrícula - ", "")
            else:
                curso_nombre = "Varios"

            if curso_id not in agrupado:
                agrupado[curso_id] = {
                    "nombre": curso_nombre,
                    "total": 0,
                    "ingresos": [],
                }

            agrupado[curso_id]["total"] += ingreso.get("monto", 0)
            agrupado[curso_id]["ingresos"].append(ingreso)

        return agrupado
