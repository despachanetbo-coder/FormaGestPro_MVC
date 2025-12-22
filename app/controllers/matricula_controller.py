# app/controllers/matricula_controller.py
"""
Controlador para la gestión de matrículas en el sistema FormaGestPro_MVC
"""

import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple, Any

from app.models.matricula_model import MatriculaModel
from app.models.estudiante_model import EstudianteModel
from app.models.programa_academico_model import ProgramaAcademicoModel
from app.models.pago_model import PagoModel
from app.models.cuota_model import CuotaModel

logger = logging.getLogger(__name__)

class MatriculaController:
    """Controlador para la gestión de matrículas"""
    
    def __init__(self, db_path: str = None):
        """
        Inicializar controlador de matrículas

        Args:
            db_path: Ruta a la base de datos (opcional)
        """
        self.db_path = db_path
    
    # ==================== OPERACIONES CRUD ====================
    
    def crear_matricula(self, datos: Dict[str, Any]) -> Tuple[bool, str, Optional[MatriculaModel]]:
        """
        Crear una nueva matrícula

        Args:
            datos: Diccionario con los datos de la matrícula

        Returns:
            Tuple (éxito, mensaje, matrícula)
        """
        try:
            # Validar datos requeridos
            errores = self._validar_datos_matricula(datos)
            if errores:
                return False, "Errores de validación: " + "; ".join(errores), None

            # Verificar que el estudiante exista
            estudiante = EstudianteModel.get_by_id(datos.get('estudiante_id'))
            if not estudiante:
                return False, f"No se encontró estudiante con ID {datos.get('estudiante_id')}", None

            # Verificar que el programa exista
            programa = ProgramaAcademicoModel.find_by_id(datos.get('programa_id'))
            if not programa:
                return False, f"No se encontró programa con ID {datos.get('programa_id')}", None

            # Verificar cupos disponibles
            if programa.cupos_disponibles <= 0:
                return False, f"El programa '{programa.nombre}' no tiene cupos disponibles", None

            # Verificar que el estudiante no esté ya matriculado en este programa
            existente = MatriculaModel.buscar_por_estudiante_programa(
                datos.get('estudiante_id'), 
                datos.get('programa_id')
            )
            if existente:
                return False, f"El estudiante ya está matriculado en este programa", None

            # Crear la matrícula usando el método de clase
            matricula = MatriculaModel.matricular_estudiante(
                estudiante_id=datos.get('estudiante_id'),
                programa_id=datos.get('programa_id'),
                modalidad_pago=datos.get('modalidad_pago', 'CONTADO'),
                plan_pago_id=datos.get('plan_pago_id'),
                observaciones=datos.get('observaciones')
            )

            mensaje = f"Matrícula creada exitosamente (ID: {matricula.id})"
            return True, mensaje, matricula

        except ValueError as e:
            logger.error(f"Error de validación al crear matrícula: {e}")
            return False, str(e), None
        except Exception as e:
            logger.error(f"Error al crear matrícula: {e}")
            return False, f"Error interno: {str(e)}", None
    
    def actualizar_matricula(self, matricula_id: int, datos: Dict[str, Any]) -> Tuple[bool, str, Optional[MatriculaModel]]:
        """
        Actualizar una matrícula existente

        Args:
            matricula_id: ID de la matrícula a actualizar
            datos: Diccionario con los datos a actualizar

        Returns:
            Tuple (éxito, mensaje, matrícula)
        """
        try:
            # Buscar matrícula existente
            matricula = MatriculaModel.get_by_id(matricula_id)
            if not matricula:
                return False, f"No se encontró matrícula con ID {matricula_id}", None

            # Validar datos
            errores = self._validar_datos_matricula(datos, es_actualizacion=True)
            if errores:
                return False, "Errores de validación: " + "; ".join(errores), None

            # Verificar que los IDs relacionados existan (si se están actualizando)
            if 'estudiante_id' in datos:
                estudiante = EstudianteModel.get_by_id(datos['estudiante_id'])
                if not estudiante:
                    return False, f"No se encontró estudiante con ID {datos['estudiante_id']}", None

            if 'programa_id' in datos:
                programa = ProgramaAcademicoModel.find_by_id(datos['programa_id'])
                if not programa:
                    return False, f"No se encontró programa con ID {datos['programa_id']}", None

            # Actualizar atributos de la matrícula
            for key, value in datos.items():
                if hasattr(matricula, key):
                    setattr(matricula, key, value)

            # Guardar cambios
            if matricula.save():
                mensaje = f"Matrícula actualizada exitosamente (ID: {matricula_id})"
                return True, mensaje, matricula
            else:
                return False, "Error al guardar los cambios", None

        except Exception as e:
            logger.error(f"Error al actualizar matrícula {matricula_id}: {e}")
            return False, f"Error interno: {str(e)}", None
    
    def anular_matricula(self, matricula_id: int, motivo: str = None) -> Tuple[bool, str]:
        """
        Anular una matrícula (marcar como inactiva)

        Args:
            matricula_id: ID de la matrícula a anular
            motivo: Motivo de la anulación (opcional)

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            matricula = MatriculaModel.get_by_id(matricula_id)
            if not matricula:
                return False, f"No se encontró matrícula con ID {matricula_id}"

            # Cambiar estado académico a RETIRADO
            matricula.estado_academico = 'RETIRADO'
            
            # Agregar motivo a observaciones
            if motivo:
                if matricula.observaciones:
                    matricula.observaciones += f"\nANULADA: {motivo}"
                else:
                    matricula.observaciones = f"ANULADA: {motivo}"
            
            if matricula.save():
                # Liberar cupo del programa
                try:
                    programa = ProgramaAcademicoModel.find_by_id(matricula.programa_id)
                    if programa:
                        programa.liberar_cupo()
                except Exception as e:
                    logger.warning(f"No se pudo liberar cupo del programa: {e}")
                
                return True, f"Matrícula anulada exitosamente (ID: {matricula_id})"
            else:
                return False, "Error al anular matrícula"

        except Exception as e:
            logger.error(f"Error al anular matrícula {matricula_id}: {e}")
            return False, f"Error interno: {str(e)}"
    
    def reactivar_matricula(self, matricula_id: int) -> Tuple[bool, str]:
        """
        Reactivar una matrícula previamente anulada

        Args:
            matricula_id: ID de la matrícula a reactivar

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            matricula = MatriculaModel.get_by_id(matricula_id)
            if not matricula:
                return False, f"No se encontró matrícula con ID {matricula_id}"

            # Cambiar estado académico a PREINSCRITO
            matricula.estado_academico = 'PREINSCRITO'
            
            # Ocupar cupo del programa
            try:
                programa = ProgramaAcademicoModel.find_by_id(matricula.programa_id)
                if programa and programa.cupos_disponibles > 0:
                    programa.ocupar_cupo()
                else:
                    return False, "No hay cupos disponibles en el programa"
            except Exception as e:
                logger.warning(f"No se pudo ocupar cupo del programa: {e}")
                return False, f"Error al ocupar cupo: {str(e)}"
            
            if matricula.save():
                return True, f"Matrícula reactivada exitosamente (ID: {matricula_id})"
            else:
                return False, "Error al reactivar matrícula"

        except Exception as e:
            logger.error(f"Error al reactivar matrícula {matricula_id}: {e}")
            return False, f"Error interno: {str(e)}"
    
    # ==================== CONSULTAS ====================
    
    def obtener_matricula(self, matricula_id: int) -> Optional[MatriculaModel]:
        """
        Obtener una matrícula por su ID

        Args:
            matricula_id: ID de la matrícula

        Returns:
            MatriculaModel o None si no se encuentra
        """
        try:
            return MatriculaModel.get_by_id(matricula_id)
        except Exception as e:
            logger.error(f"Error al obtener matrícula {matricula_id}: {e}")
            return None
    
    def obtener_matriculas_estudiante(self, estudiante_id: int) -> List[MatriculaModel]:
        """
        Obtener matrículas de un estudiante

        Args:
            estudiante_id: ID del estudiante

        Returns:
            Lista de matrículas del estudiante
        """
        try:
            return MatriculaModel.buscar_por_estudiante(estudiante_id)
        except Exception as e:
            logger.error(f"Error al obtener matrículas del estudiante {estudiante_id}: {e}")
            return []
    
    def obtener_matriculas_programa(self, programa_id: int) -> List[MatriculaModel]:
        """
        Obtener matrículas de un programa

        Args:
            programa_id: ID del programa

        Returns:
            Lista de matrículas del programa
        """
        try:
            return MatriculaModel.buscar_por_programa(programa_id)
        except Exception as e:
            logger.error(f"Error al obtener matrículas del programa {programa_id}: {e}")
            return []
    
    def buscar_matriculas(
        self, 
        estudiante_id: Optional[int] = None,
        programa_id: Optional[int] = None,
        estado_pago: Optional[str] = None,
        estado_academico: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        limite: int = 100,
        offset: int = 0,
        orden_por: str = 'fecha_matricula',
        orden_asc: bool = False
    ) -> List[MatriculaModel]:
        """
        Buscar matrículas con múltiples filtros

        Args:
            estudiante_id: Filtrar por estudiante
            programa_id: Filtrar por programa
            estado_pago: Filtrar por estado de pago
            estado_academico: Filtrar por estado académico
            fecha_desde: Filtrar desde fecha
            fecha_hasta: Filtrar hasta fecha
            limite: Número máximo de resultados
            offset: Desplazamiento para paginación
            orden_por: Campo para ordenar ('fecha_matricula', 'estudiante_id', 'programa_id')
            orden_asc: Orden ascendente (True) o descendente (False)

        Returns:
            Lista de matrículas
        """
        try:
            # Construir condiciones
            condiciones = []
            parametros = []

            if estudiante_id:
                condiciones.append("estudiante_id = ?")
                parametros.append(estudiante_id)

            if programa_id:
                condiciones.append("programa_id = ?")
                parametros.append(programa_id)

            if estado_pago:
                condiciones.append("estado_pago = ?")
                parametros.append(estado_pago)

            if estado_academico:
                condiciones.append("estado_academico = ?")
                parametros.append(estado_academico)

            if fecha_desde:
                condiciones.append("fecha_matricula >= ?")
                parametros.append(fecha_desde.isoformat())

            if fecha_hasta:
                condiciones.append("fecha_matricula <= ?")
                parametros.append(fecha_hasta.isoformat())
            
            # Convertir condiciones a string
            where_clause = ""
            if condiciones:
                where_clause = "WHERE " + " AND ".join(condiciones)

            # Validar campo de orden
            campos_validos = ['fecha_matricula', 'estudiante_id', 'programa_id', 'estado_pago', 'estado_academico']
            if orden_por not in campos_validos:
                orden_por = 'fecha_matricula'

            # Construir orden
            orden = f"{orden_por} {'ASC' if orden_asc else 'DESC'}"

            # Construir límite
            limit_clause = ""
            if limite > 0:
                limit_clause = f"LIMIT {limite} OFFSET {offset}"

            # Ejecutar consulta
            query = f"""
                SELECT * FROM matriculas 
                {where_clause}
                ORDER BY {orden}
                {limit_clause}
            """

            matriculas = MatriculaModel.query(query, parametros) if parametros else MatriculaModel.query(query)
            return [MatriculaModel(**mat) for mat in matriculas] if matriculas else []

        except Exception as e:
            logger.error(f"Error al buscar matrículas: {e}")
            return []
    
    def contar_matriculas(self, estado_pago: str = None, estado_academico: str = None) -> int:
        """
        Contar número de matrículas

        Args:
            estado_pago: Filtrar por estado de pago
            estado_academico: Filtrar por estado académico

        Returns:
            Número de matrículas
        """
        try:
            condiciones = []
            parametros = []

            if estado_pago:
                condiciones.append("estado_pago = ?")
                parametros.append(estado_pago)

            if estado_academico:
                condiciones.append("estado_academico = ?")
                parametros.append(estado_academico)

            where_clause = ""
            if condiciones:
                where_clause = "WHERE " + " AND ".join(condiciones)

            query = f"SELECT COUNT(*) as count FROM matriculas {where_clause}"
            resultado = MatriculaModel.query(query, parametros)
            return resultado[0]['count'] if resultado else 0
        except Exception as e:
            logger.error(f"Error al contar matrículas: {e}")
            return 0
    
    # ==================== OPERACIONES DE PAGO ====================
    
    def registrar_pago_matricula(self, matricula_id: int, datos_pago: Dict[str, Any]) -> Tuple[bool, str, Optional[PagoModel]]:
        """
        Registrar un pago para una matrícula

        Args:
            matricula_id: ID de la matrícula
            datos_pago: Datos del pago

        Returns:
            Tuple (éxito, mensaje, pago)
        """
        try:
            matricula = MatriculaModel.get_by_id(matricula_id)
            if not matricula:
                return False, f"No se encontró matrícula con ID {matricula_id}", None

            # Validar datos del pago
            errores = self._validar_datos_pago(datos_pago)
            if errores:
                return False, "Errores de validación: " + "; ".join(errores), None

            # Registrar el pago usando el método de la matrícula
            pago = matricula.registrar_pago(
                monto=datos_pago.get('monto'),
                forma_pago=datos_pago.get('forma_pago'),
                nro_comprobante=datos_pago.get('nro_comprobante'),
                nro_transaccion=datos_pago.get('nro_transaccion'),
                observaciones=datos_pago.get('observaciones'),
                nro_cuota=datos_pago.get('nro_cuota')
            )

            mensaje = f"Pago registrado exitosamente (ID: {pago.id})"
            return True, mensaje, pago

        except ValueError as e:
            logger.error(f"Error de validación al registrar pago: {e}")
            return False, str(e), None
        except Exception as e:
            logger.error(f"Error al registrar pago: {e}")
            return False, f"Error interno: {str(e)}", None
    
    def obtener_pagos_matricula(self, matricula_id: int) -> List[PagoModel]:
        """
        Obtener pagos de una matrícula

        Args:
            matricula_id: ID de la matrícula

        Returns:
            Lista de pagos
        """
        try:
            return PagoModel.buscar_por_matricula(matricula_id)
        except Exception as e:
            logger.error(f"Error al obtener pagos de matrícula {matricula_id}: {e}")
            return []
    
    def obtener_cuotas_matricula(self, matricula_id: int) -> List[CuotaModel]:
        """
        Obtener cuotas de una matrícula

        Args:
            matricula_id: ID de la matrícula

        Returns:
            Lista de cuotas
        """
        try:
            return CuotaModel.buscar_por_matricula(matricula_id)
        except Exception as e:
            logger.error(f"Error al obtener cuotas de matrícula {matricula_id}: {e}")
            return []
    
    # ==================== OPERACIONES ACADÉMICAS ====================
    
    def iniciar_curso(self, matricula_id: int, fecha_inicio: date = None) -> Tuple[bool, str]:
        """
        Iniciar curso para una matrícula

        Args:
            matricula_id: ID de la matrícula
            fecha_inicio: Fecha de inicio (opcional, hoy por defecto)

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            matricula = MatriculaModel.get_by_id(matricula_id)
            if not matricula:
                return False, f"No se encontró matricula con ID {matricula_id}"

            matricula.iniciar_curso(fecha_inicio)
            return True, f"Curso iniciado para matrícula {matricula_id}"

        except Exception as e:
            logger.error(f"Error al iniciar curso para matrícula {matricula_id}: {e}")
            return False, f"Error: {str(e)}"
    
    def concluir_matricula(self, matricula_id: int, fecha_conclusion: date = None) -> Tuple[bool, str]:
        """
        Concluir una matrícula

        Args:
            matricula_id: ID de la matrícula
            fecha_conclusion: Fecha de conclusión (opcional, hoy por defecto)

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            matricula = MatriculaModel.get_by_id(matricula_id)
            if not matricula:
                return False, f"No se encontró matrícula con ID {matricula_id}"

            matricula.concluir_matricula(fecha_conclusion)
            return True, f"Matrícula {matricula_id} concluida exitosamente"

        except Exception as e:
            logger.error(f"Error al concluir matrícula {matricula_id}: {e}")
            return False, f"Error: {str(e)}"
    
    # ==================== VALIDACIONES ====================
    
    def _validar_datos_matricula(
        self, 
        datos: Dict[str, Any], 
        es_actualizacion: bool = False
    ) -> List[str]:
        """
        Validar datos de matrícula

        Args:
            datos: Diccionario con datos a validar
            es_actualizacion: Si es una actualización (algunos campos son opcionales)

        Returns:
            Lista de mensajes de error
        """
        errores = []

        # Validar campos requeridos (solo para creación)
        if not es_actualizacion:
            campos_requeridos = ['estudiante_id', 'programa_id']
            for campo in campos_requeridos:
                if campo not in datos or not datos.get(campo):
                    errores.append(f"El campo '{campo}' es requerido")

        # Validar estudiante_id
        if 'estudiante_id' in datos and datos['estudiante_id']:
            try:
                estudiante_id = int(datos['estudiante_id'])
                if estudiante_id <= 0:
                    errores.append("El ID de estudiante debe ser positivo")
            except (ValueError, TypeError):
                errores.append("El ID de estudiante debe ser un número entero")

        # Validar programa_id
        if 'programa_id' in datos and datos['programa_id']:
            try:
                programa_id = int(datos['programa_id'])
                if programa_id <= 0:
                    errores.append("El ID de programa debe ser positivo")
            except (ValueError, TypeError):
                errores.append("El ID de programa debe ser un número entero")

        # Validar modalidad_pago
        if 'modalidad_pago' in datos and datos['modalidad_pago']:
            modalidades_validas = ['CONTADO', 'CUOTAS']
            if datos['modalidad_pago'] not in modalidades_validas:
                errores.append(f"Modalidad de pago inválida. Válidas: {', '.join(modalidades_validas)}")

        # Validar estado_pago
        if 'estado_pago' in datos and datos['estado_pago']:
            estados_validos = ['PENDIENTE', 'PARCIAL', 'PAGADO', 'MORA']
            if datos['estado_pago'] not in estados_validos:
                errores.append(f"Estado de pago inválido. Válidos: {', '.join(estados_validos)}")

        # Validar estado_academico
        if 'estado_academico' in datos and datos['estado_academico']:
            estados_validos = ['PREINSCRITO', 'INSCRITO', 'EN_CURSO', 'CONCLUIDO', 'RETIRADO']
            if datos['estado_academico'] not in estados_validos:
                errores.append(f"Estado académico inválido. Válidos: {', '.join(estados_validos)}")

        # Validar montos
        for campo_monto in ['monto_total', 'monto_final', 'monto_pagado', 'descuento_aplicado']:
            if campo_monto in datos and datos[campo_monto] is not None:
                try:
                    monto = float(datos[campo_monto])
                    if monto < 0:
                        errores.append(f"El campo '{campo_monto}' no puede ser negativo")
                except (ValueError, TypeError):
                    errores.append(f"El campo '{campo_monto}' debe ser un número")

        return errores
    
    def _validar_datos_pago(self, datos: Dict[str, Any]) -> List[str]:
        """
        Validar datos de pago

        Args:
            datos: Diccionario con datos a validar

        Returns:
            Lista de mensajes de error
        """
        errores = []

        # Validar campos requeridos
        campos_requeridos = ['monto', 'forma_pago']
        for campo in campos_requeridos:
            if campo not in datos or not datos.get(campo):
                errores.append(f"El campo '{campo}' es requerido")

        # Validar monto
        if 'monto' in datos and datos['monto']:
            try:
                monto = float(datos['monto'])
                if monto <= 0:
                    errores.append("El monto debe ser mayor a 0")
            except (ValueError, TypeError):
                errores.append("El monto debe ser un número válido")

        # Validar forma de pago
        if 'forma_pago' in datos and datos['forma_pago']:
            formas_validas = ['EFECTIVO', 'TRANSFERENCIA', 'TARJETA', 'DEPOSITO', 'CHEQUE']
            if datos['forma_pago'] not in formas_validas:
                errores.append(f"Forma de pago inválida. Válidas: {', '.join(formas_validas)}")

        return errores
    
    # ==================== ESTADÍSTICAS E INFORMES ====================
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de matrículas

        Returns:
            Diccionario con estadísticas
        """
        try:
            # Contar total de matrículas
            total_matriculas = self.contar_matriculas()

            # Contar por estado de pago
            pendientes = self.contar_matriculas(estado_pago='PENDIENTE')
            parciales = self.contar_matriculas(estado_pago='PARCIAL')
            pagadas = self.contar_matriculas(estado_pago='PAGADO')
            mora = self.contar_matriculas(estado_pago='MORA')

            # Contar por estado académico
            preinscritos = self.contar_matriculas(estado_academico='PREINSCRITO')
            inscritos = self.contar_matriculas(estado_academico='INSCRITO')
            en_curso = self.contar_matriculas(estado_academico='EN_CURSO')
            concluidos = self.contar_matriculas(estado_academico='CONCLUIDO')
            retirados = self.contar_matriculas(estado_academico='RETIRADO')

            # Matrículas por mes (últimos 6 meses)
            hoy = date.today()
            matriculas_por_mes = {}
            
            for i in range(6):
                mes = hoy.month - i
                año = hoy.year
                if mes <= 0:
                    mes += 12
                    año -= 1
                
                fecha_inicio = date(año, mes, 1)
                if mes == 12:
                    fecha_fin = date(año + 1, 1, 1)
                else:
                    fecha_fin = date(año, mes + 1, 1)
                
                query = """
                    SELECT COUNT(*) as count FROM matriculas 
                    WHERE fecha_matricula >= ? AND fecha_matricula < ?
                """
                resultado = MatriculaModel.query(query, [fecha_inicio.isoformat(), fecha_fin.isoformat()])
                count = resultado[0]['count'] if resultado else 0
                
                mes_nombre = fecha_inicio.strftime('%b %Y')
                matriculas_por_mes[mes_nombre] = count

            # Ingresos totales
            try:
                query_ingresos = """
                    SELECT 
                        SUM(monto_total) as total_ingresos,
                        SUM(monto_pagado) as total_pagado,
                        SUM(monto_total - monto_pagado) as total_pendiente
                    FROM matriculas
                """
                resultado = MatriculaModel.query(query_ingresos)
                if resultado:
                    ingresos = resultado[0]
                else:
                    ingresos = {'total_ingresos': 0, 'total_pagado': 0, 'total_pendiente': 0}
            except:
                ingresos = {'total_ingresos': 0, 'total_pagado': 0, 'total_pendiente': 0}

            return {
                'total_matriculas': total_matriculas,
                'por_estado_pago': {
                    'pendientes': pendientes,
                    'parciales': parciales,
                    'pagadas': pagadas,
                    'mora': mora
                },
                'por_estado_academico': {
                    'preinscritos': preinscritos,
                    'inscritos': inscritos,
                    'en_curso': en_curso,
                    'concluidos': concluidos,
                    'retirados': retirados
                },
                'matriculas_por_mes': matriculas_por_mes,
                'ingresos': ingresos,
                'fecha_consulta': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            logger.error(f"Error al obtener estadísticas de matrículas: {e}")
            return {
                'total_matriculas': 0,
                'por_estado_pago': {},
                'por_estado_academico': {},
                'matriculas_por_mes': {},
                'ingresos': {'total_ingresos': 0, 'total_pagado': 0, 'total_pendiente': 0},
                'fecha_consulta': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'error': str(e)
            }
    
    def obtener_detalles_completos(self, matricula_id: int) -> Dict[str, Any]:
        """
        Obtener detalles completos de una matrícula

        Args:
            matricula_id: ID de la matrícula

        Returns:
            Diccionario con detalles completos
        """
        try:
            matricula = self.obtener_matricula(matricula_id)
            if not matricula:
                return {'error': f'Matrícula {matricula_id} no encontrada'}

            # Obtener estudiante
            estudiante = EstudianteModel.get_by_id(matricula.estudiante_id)

            # Obtener programa
            programa = ProgramaAcademicoModel.find_by_id(matricula.programa_id)

            # Obtener pagos
            pagos = self.obtener_pagos_matricula(matricula_id)

            # Obtener cuotas
            cuotas = self.obtener_cuotas_matricula(matricula_id)

            # Calcular estadísticas
            saldo_pendiente = matricula.saldo_pendiente
            porcentaje_pagado = matricula.porcentaje_pagado

            return {
                'matricula': matricula.to_dict() if hasattr(matricula, 'to_dict') else matricula.__dict__,
                'estudiante': estudiante.to_dict() if estudiante and hasattr(estudiante, 'to_dict') else (estudiante.__dict__ if estudiante else None),
                'programa': programa.to_dict() if programa and hasattr(programa, 'to_dict') else (programa.__dict__ if programa else None),
                'pagos': [pago.to_dict() if hasattr(pago, 'to_dict') else pago.__dict__ for pago in pagos],
                'cuotas': [cuota.to_dict() if hasattr(cuota, 'to_dict') else cuota.__dict__ for cuota in cuotas],
                'saldo_pendiente': saldo_pendiente,
                'porcentaje_pagado': porcentaje_pagado,
                'estado_actual': {
                    'pago': matricula.estado_pago,
                    'academico': matricula.estado_academico,
                    'modalidad': matricula.modalidad_pago
                }
            }

        except Exception as e:
            logger.error(f"Error al obtener detalles de matrícula {matricula_id}: {e}")
            return {'error': str(e)}