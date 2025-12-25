# app/controllers/matricula_controller.py
"""
Controlador para la gestión de matrículas en FormaGestPro_MVC

Responsabilidades:
- CRUD completo de matrículas
- Gestión de pagos y cuotas
- Validaciones de negocio
- Consultas y estadísticas
- Integración con estudiantes y programas

Autor: FormaGestPro_MVC Team
Versión: 2.0.0
Última actualización: [Fecha actual]
"""

import logging
from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass

from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.orm import Session

# Importar modelos
from app.models.matricula_model import MatriculaModel
from app.models.estudiante_model import EstudianteModel
from app.models.programa_academico_model import ProgramaAcademicoModel
from app.models.plan_pago_model import PlanPagoModel
from app.models.pago_model import PagoModel
from app.models.cuota_model import CuotaModel
from app.models.docente_model import DocenteModel

# Importar utilidades
from app.utils.validators import Validator
from app.utils.exceptions import (
    BusinessRuleException,
    ValidationException,
    NotFoundException,
    DatabaseException
)

logger = logging.getLogger(__name__)


@dataclass
class MatriculaStats:
    """Estructura para estadísticas de matrículas"""
    total: int
    por_estado_pago: Dict[str, int]
    por_estado_academico: Dict[str, int]
    ingresos_totales: Decimal
    ingresos_pagados: Decimal
    ingresos_pendientes: Decimal
    mora_total: Decimal


class MatriculaController:
    """Controlador principal para operaciones de matrículas"""
    
    def __init__(self, session: Session = None):
        """
        Inicializar controlador de matrículas
        
        Args:
            session: Sesión de SQLAlchemy (opcional, se crea una si no se proporciona)
        """
        self.session = session
        self.validator = Validator()
    
    # ==================== OPERACIONES CRUD PRINCIPALES ====================

    def crear_matricula(self, datos: dict):
        """Ejemplo de validación completa"""
        
        # 1. Validar datos básicos
        if not self.validator.validate_matricula_data(datos):
            self.validator.raise_if_errors("Datos de matrícula inválidos")
        
        # 2. Validaciones específicas
        if not self.validator.validate_monto(datos['monto_total'], minimo=Decimal('100')):
            self.validator.raise_if_errors()
        
        # 3. Validar fechas
        if 'fecha_inicio' in datos:
            if not self.validator.validate_fecha(
                datos['fecha_inicio'], 
                min_date=date.today()
            ):
                self.validator.raise_if_errors()
        
        # 4. Validar descuentos
        if 'descuento_aplicado' in datos:
            if not self.validator.validate_descuento(
                datos['descuento_aplicado'], 
                maximo=Decimal('50')
            ):
                self.validator.raise_if_errors()
        
        # 5. Si hay cuotas, validar estructura
        if datos.get('modalidad_pago') == 'CUOTAS' and 'plan_pago_id' in datos:
            plan = self._obtener_plan(datos['plan_pago_id'])
            if plan:
                if not self.validator.validate_cuotas(plan.nro_cuotas, plan.intervalo_dias):
                    self.validator.raise_if_errors()
        
        # 6. Validar reglas de negocio específicas
        self._validar_reglas_negocio(datos)
        
        # Si llegamos aquí, todas las validaciones pasaron
        return self._crear_matricula_en_db(datos)

    def crear_matricula_completa(
        self,
        estudiante_id: int,
        programa_id: int,
        modalidad_pago: str,
        plan_pago_id: Optional[int] = None,
        observaciones: Optional[str] = None,
        descuento_personalizado: Optional[Decimal] = None,
        fecha_inicio: Optional[date] = None,
        usuario_id: Optional[int] = None
    ) -> Tuple[bool, str, Optional[MatriculaModel]]:
        """
        Crear una matrícula completa con todas sus dependencias
        
        Args:
            estudiante_id: ID del estudiante
            programa_id: ID del programa académico
            modalidad_pago: 'CONTADO' o 'CUOTAS'
            plan_pago_id: ID del plan de pago (requerido si modalidad es CUOTAS)
            observaciones: Observaciones adicionales
            descuento_personalizado: Descuento personalizado en porcentaje
            fecha_inicio: Fecha de inicio del programa
            usuario_id: ID del usuario que realiza la operación
        
        Returns:
            Tuple (éxito, mensaje, matrícula_creada)
        """
        try:
            logger.info(f"Iniciando creación de matrícula para estudiante {estudiante_id}")
            
            # 1. Validaciones previas
            errores = self._validar_creacion_matricula(
                estudiante_id, programa_id, modalidad_pago, plan_pago_id
            )
            if errores:
                return False, "; ".join(errores), None
            
            # 2. Obtener datos necesarios
            estudiante = self._obtener_estudiante(estudiante_id)
            programa = self._obtener_programa(programa_id)
            plan_pago = self._obtener_plan_pago(plan_pago_id) if plan_pago_id else None
            
            # 3. Calcular montos
            montos = self._calcular_montos_matricula(
                programa, modalidad_pago, plan_pago, descuento_personalizado
            )
            
            # 4. Crear matrícula base
            matricula_data = {
                'estudiante_id': estudiante_id,
                'programa_id': programa_id,
                'modalidad_pago': modalidad_pago,
                'plan_pago_id': plan_pago_id,
                'monto_total': float(montos['monto_base']),
                'descuento_aplicado': float(montos['descuento_total']),
                'monto_final': float(montos['monto_final']),
                'monto_pagado': 0.0,
                'estado_pago': 'PENDIENTE',
                'estado_academico': 'INSCRITO',
                'fecha_inicio': fecha_inicio or date.today(),
                'coordinador_id': programa.tutor_id,
                'observaciones': observaciones,
                'creado_por': usuario_id
            }
            
            # 5. Crear matrícula en base de datos
            matricula = MatriculaModel(**matricula_data)
            self._guardar_matricula(matricula)
            
            # 6. Crear cuotas programadas si corresponde
            if modalidad_pago == 'CUOTAS' and plan_pago:
                self._crear_cuotas_programadas(
                    matricula.id, montos['monto_final'], plan_pago, fecha_inicio
                )
            
            # 7. Actualizar cupos del programa
            self._actualizar_cupos_programa(programa_id, -1)
            
            # 8. Registrar movimiento de auditoría
            self._registrar_auditoria(
                'CREACION_MATRICULA',
                f'Matrícula {matricula.id} creada para estudiante {estudiante_id}',
                usuario_id
            )
            
            logger.info(f"Matrícula {matricula.id} creada exitosamente")
            return True, f"Matrícula creada exitosamente (ID: {matricula.id})", matricula
            
        except ValidationException as e:
            logger.warning(f"Validación fallida: {e}")
            return False, str(e), None
        except BusinessRuleException as e:
            logger.warning(f"Regla de negocio violada: {e}")
            return False, str(e), None
        except NotFoundException as e:
            logger.warning(f"Recurso no encontrado: {e}")
            return False, str(e), None
        except Exception as e:
            logger.error(f"Error crítico creando matrícula: {e}", exc_info=True)
            return False, f"Error interno del sistema: {str(e)}", None
    
    def actualizar_matricula(
        self,
        matricula_id: int,
        datos_actualizacion: Dict[str, Any],
        usuario_id: Optional[int] = None
    ) -> Tuple[bool, str, Optional[MatriculaModel]]:
        """
        Actualizar una matrícula existente
        
        Args:
            matricula_id: ID de la matrícula a actualizar
            datos_actualizacion: Datos a actualizar
            usuario_id: ID del usuario que realiza la operación
        
        Returns:
            Tuple (éxito, mensaje, matrícula_actualizada)
        """
        try:
            matricula = self._obtener_matricula_por_id(matricula_id)
            if not matricula:
                raise NotFoundException(f"Matrícula {matricula_id} no encontrada")
            
            # Validar que la matrícula se pueda actualizar
            self._validar_matricula_para_actualizacion(matricula)
            
            # Validar datos de actualización
            errores = self._validar_datos_actualizacion(datos_actualizacion)
            if errores:
                raise ValidationException("; ".join(errores))
            
            # Campos que no se pueden actualizar directamente
            campos_protegidos = ['id', 'estudiante_id', 'programa_id', 'fecha_matricula']
            for campo in campos_protegidos:
                if campo in datos_actualizacion:
                    del datos_actualizacion[campo]
            
            # Actualizar campos permitidos
            for campo, valor in datos_actualizacion.items():
                if hasattr(matricula, campo):
                    # Validaciones específicas por campo
                    if campo in ['monto_total', 'monto_final', 'monto_pagado', 'descuento_aplicado']:
                        valor = self._validar_monto(valor)
                    
                    setattr(matricula, campo, valor)
            
            # Recalcular estados si es necesario
            if 'monto_pagado' in datos_actualizacion:
                self._actualizar_estado_pago(matricula)
            
            # Guardar cambios
            if not matricula.save():
                raise DatabaseException("Error al guardar cambios en la matrícula")
            
            # Registrar auditoría
            self._registrar_auditoria(
                'ACTUALIZACION_MATRICULA',
                f'Matrícula {matricula_id} actualizada',
                usuario_id
            )
            
            return True, f"Matrícula {matricula_id} actualizada exitosamente", matricula
            
        except (ValidationException, BusinessRuleException, NotFoundException) as e:
            logger.warning(f"Error controlado actualizando matrícula: {e}")
            return False, str(e), None
        except Exception as e:
            logger.error(f"Error actualizando matrícula {matricula_id}: {e}", exc_info=True)
            return False, f"Error interno: {str(e)}", None
    
    # ==================== OPERACIONES ESPECÍFICAS ====================
    
    def matricular_estudiante_desde_dialogo(
        self,
        estudiante_id: int,
        programa_id: int,
        modalidad_pago: str,
        plan_pago_id: Optional[int] = None,
        descuento_contado: bool = False,
        descuento_promocion: bool = False,
        descuento_manual: Optional[Decimal] = None,
        monto_manual: Optional[Decimal] = None,
        observaciones: Optional[str] = None,
        fecha_inicio: Optional[date] = None
    ) -> Tuple[bool, str, Optional[Dict]]:
        """
        Matricular estudiante desde interfaz de diálogo
        
        Args:
            estudiante_id: ID del estudiante
            programa_id: ID del programa
            modalidad_pago: Modalidad de pago
            plan_pago_id: ID del plan de pago
            descuento_contado: Aplicar descuento por pago contado
            descuento_promocion: Aplicar descuento por promoción
            descuento_manual: Porcentaje de descuento manual
            monto_manual: Monto manual (sobrescribe cálculos)
            observaciones: Observaciones adicionales
            fecha_inicio: Fecha de inicio
        
        Returns:
            Tuple (éxito, mensaje, datos_completos)
        """
        try:
            # Obtener programa para cálculos
            programa = self._obtener_programa(programa_id)
            
            # Calcular descuentos
            descuentos = self._calcular_descuentos_dialogo(
                programa,
                modalidad_pago,
                descuento_contado,
                descuento_promocion,
                descuento_manual,
                monto_manual
            )
            
            # Crear matrícula
            success, message, matricula = self.crear_matricula_completa(
                estudiante_id=estudiante_id,
                programa_id=programa_id,
                modalidad_pago=modalidad_pago,
                plan_pago_id=plan_pago_id,
                observaciones=observaciones,
                descuento_personalizado=descuentos['descuento_total_porcentaje'],
                fecha_inicio=fecha_inicio
            )
            
            if not success:
                return False, message, None
            
            # Preparar respuesta detallada
            respuesta = {
                'matricula_id': matricula.id,
                'estudiante': self._obtener_estudiante(estudiante_id).to_dict(),
                'programa': programa.to_dict(),
                'montos': {
                    'base': float(descuentos['monto_base']),
                    'descuento_total': float(descuentos['descuento_total']),
                    'final': float(descuentos['monto_final']),
                    'descuentos_detalle': descuentos['detalle']
                },
                'modalidad_pago': modalidad_pago,
                'fecha_inicio': matricula.fecha_inicio.isoformat() if matricula.fecha_inicio else None,
                'cuotas': []
            }
            
            # Agregar información de cuotas si corresponde
            if modalidad_pago == 'CUOTAS' and plan_pago_id:
                cuotas = self.obtener_cuotas_matricula(matricula.id)
                respuesta['cuotas'] = [
                    {
                        'nro_cuota': c.nro_cuota,
                        'monto': c.monto,
                        'fecha_vencimiento': c.fecha_vencimiento.isoformat(),
                        'estado': c.estado
                    }
                    for c in cuotas
                ]
            
            return True, message, respuesta
            
        except Exception as e:
            logger.error(f"Error en matrícula desde diálogo: {e}", exc_info=True)
            return False, f"Error en proceso de matrícula: {str(e)}", None
    
    def registrar_pago_matricula(
        self,
        matricula_id: int,
        monto: Decimal,
        forma_pago: str,
        nro_comprobante: Optional[str] = None,
        nro_transaccion: Optional[str] = None,
        observaciones: Optional[str] = None,
        nro_cuota: Optional[int] = None,
        usuario_id: Optional[int] = None
    ) -> Tuple[bool, str, Optional[PagoModel]]:
        """
        Registrar un pago para una matrícula
        
        Args:
            matricula_id: ID de la matrícula
            monto: Monto del pago
            forma_pago: Forma de pago
            nro_comprobante: Número de comprobante
            nro_transaccion: Número de transacción
            observaciones: Observaciones del pago
            nro_cuota: Número de cuota (si aplica)
            usuario_id: ID del usuario
        
        Returns:
            Tuple (éxito, mensaje, pago)
        """
        try:
            matricula = self._obtener_matricula_por_id(matricula_id)
            if not matricula:
                raise NotFoundException(f"Matrícula {matricula_id} no encontrada")
            
            # Validar pago
            self._validar_pago(matricula, monto, nro_cuota)
            
            # Crear registro de pago
            pago_data = {
                'matricula_id': matricula_id,
                'nro_cuota': nro_cuota,
                'monto': float(monto),
                'fecha_pago': date.today(),
                'forma_pago': forma_pago,
                'estado': 'CONFIRMADO',
                'nro_comprobante': nro_comprobante,
                'nro_transaccion': nro_transaccion,
                'observaciones': observaciones,
                'registrado_por': usuario_id
            }
            
            pago = PagoModel(**pago_data)
            if not pago.save():
                raise DatabaseException("Error al guardar el pago")
            
            # Actualizar estado de la matrícula
            matricula.monto_pagado += float(monto)
            self._actualizar_estado_pago(matricula)
            
            # Actualizar cuota si corresponde
            if nro_cuota:
                self._actualizar_estado_cuota(matricula_id, nro_cuota, pago.id)
            
            # Registrar movimiento de caja
            self._registrar_movimiento_caja(
                tipo='INGRESO',
                monto=monto,
                descripcion=f"Pago matrícula {matricula_id}",
                referencia_tipo='PAGO',
                referencia_id=pago.id
            )
            
            # Registrar auditoría
            self._registrar_auditoria(
                'REGISTRO_PAGO',
                f'Pago registrado para matrícula {matricula_id} - Monto: {monto}',
                usuario_id
            )
            
            return True, f"Pago registrado exitosamente (ID: {pago.id})", pago
            
        except (ValidationException, BusinessRuleException) as e:
            logger.warning(f"Validación fallida para pago: {e}")
            return False, str(e), None
        except Exception as e:
            logger.error(f"Error registrando pago: {e}", exc_info=True)
            return False, f"Error interno: {str(e)}", None
    
    # ==================== CONSULTAS Y BÚSQUEDAS ====================
    
    def obtener_matriculas_activas_estudiante(self, estudiante_id: int) -> List[MatriculaModel]:
        """Obtener matrículas activas de un estudiante"""
        return MatriculaModel.query.filter(
            and_(
                MatriculaModel.estudiante_id == estudiante_id,
                MatriculaModel.estado_academico.in_(['INSCRITO', 'EN_CURSO', 'PREINSCRITO'])
            )
        ).order_by(desc(MatriculaModel.fecha_matricula)).all()
    
    def obtener_matriculas_con_detalles(
        self,
        filtros: Optional[Dict[str, Any]] = None,
        pagina: int = 1,
        por_pagina: int = 20,
        ordenar_por: str = 'fecha_matricula',
        orden_descendente: bool = True
    ) -> Dict[str, Any]:
        """
        Obtener matrículas con detalles completos y paginación
        
        Args:
            filtros: Diccionario de filtros
            pagina: Número de página
            por_pagina: Elementos por página
            ordenar_por: Campo para ordenar
            orden_descendente: Orden descendente
        
        Returns:
            Diccionario con resultados y metadatos
        """
        try:
            # Construir consulta base
            query = self.session.query(MatriculaModel)
            
            # Aplicar joins para obtener detalles
            query = query.join(EstudianteModel)
            query = query.join(ProgramaAcademicoModel)
            
            # Aplicar filtros
            if filtros:
                query = self._aplicar_filtros_matriculas(query, filtros)
            
            # Contar total de resultados
            total = query.count()
            
            # Aplicar ordenamiento
            campo_orden = getattr(MatriculaModel, ordenar_por, MatriculaModel.fecha_matricula)
            if orden_descendente:
                query = query.order_by(desc(campo_orden))
            else:
                query = query.order_by(asc(campo_orden))
            
            # Aplicar paginación
            offset = (pagina - 1) * por_pagina
            resultados = query.offset(offset).limit(por_pagina).all()
            
            # Enriquecer resultados con detalles
            resultados_enriquecidos = []
            for matricula in resultados:
                detalles = {
                    'matricula': matricula.to_dict(),
                    'estudiante': {
                        'id': matricula.estudiante.id,
                        'nombre_completo': f"{matricula.estudiante.nombres} {matricula.estudiante.apellidos}",
                        'ci': matricula.estudiante.ci_numero
                    },
                    'programa': {
                        'id': matricula.programa.id,
                        'nombre': matricula.programa.nombre,
                        'codigo': matricula.programa.codigo
                    },
                    'estadisticas': {
                        'saldo_pendiente': matricula.saldo_pendiente,
                        'porcentaje_pagado': matricula.porcentaje_pagado,
                        'dias_mora': self._calcular_dias_mora(matricula)
                    }
                }
                resultados_enriquecidos.append(detalles)
            
            return {
                'resultados': resultados_enriquecidos,
                'paginacion': {
                    'pagina_actual': pagina,
                    'por_pagina': por_pagina,
                    'total_resultados': total,
                    'total_paginas': (total + por_pagina - 1) // por_pagina
                },
                'filtros_aplicados': filtros or {}
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo matrículas con detalles: {e}")
            return {
                'resultados': [],
                'paginacion': {},
                'error': str(e)
            }
    
    def buscar_matriculas_por_texto(self, texto: str) -> List[Dict[str, Any]]:
        """
        Buscar matrículas por texto (nombre estudiante, CI, programa)
        
        Args:
            texto: Texto a buscar
        
        Returns:
            Lista de matrículas encontradas
        """
        try:
            # Buscar en múltiples campos
            resultados = self.session.query(MatriculaModel)\
                .join(EstudianteModel)\
                .join(ProgramaAcademicoModel)\
                .filter(
                    or_(
                        EstudianteModel.nombres.ilike(f"%{texto}%"),
                        EstudianteModel.apellidos.ilike(f"%{texto}%"),
                        EstudianteModel.ci_numero.ilike(f"%{texto}%"),
                        ProgramaAcademicoModel.nombre.ilike(f"%{texto}%"),
                        ProgramaAcademicoModel.codigo.ilike(f"%{texto}%"),
                        MatriculaModel.id.cast(str).ilike(f"%{texto}%")
                    )
                )\
                .limit(50)\
                .all()
            
            return [
                {
                    'id': m.id,
                    'estudiante': f"{m.estudiante.nombres} {m.estudiante.apellidos}",
                    'ci': m.estudiante.ci_numero,
                    'programa': m.programa.nombre,
                    'estado_pago': m.estado_pago,
                    'estado_academico': m.estado_academico,
                    'monto_final': m.monto_final,
                    'monto_pagado': m.monto_pagado
                }
                for m in resultados
            ]
            
        except Exception as e:
            logger.error(f"Error buscando matrículas por texto: {e}")
            return []
    
    # ==================== ESTADÍSTICAS E INFORMES ====================
    
    def obtener_estadisticas_completas(self) -> MatriculaStats:
        """
        Obtener estadísticas completas de matrículas
        
        Returns:
            Objeto MatriculaStats con estadísticas
        """
        try:
            # Consultas optimizadas
            total = self.session.query(func.count(MatriculaModel.id)).scalar()
            
            # Por estado de pago
            estados_pago = ['PENDIENTE', 'PARCIAL', 'PAGADO', 'MORA']
            por_estado_pago = {}
            for estado in estados_pago:
                count = self.session.query(func.count(MatriculaModel.id))\
                    .filter(MatriculaModel.estado_pago == estado)\
                    .scalar()
                por_estado_pago[estado] = count
            
            # Por estado académico
            estados_academicos = ['PREINSCRITO', 'INSCRITO', 'EN_CURSO', 'CONCLUIDO', 'RETIRADO']
            por_estado_academico = {}
            for estado in estados_academicos:
                count = self.session.query(func.count(MatriculaModel.id))\
                    .filter(MatriculaModel.estado_academico == estado)\
                    .scalar()
                por_estado_academico[estado] = count
            
            # Ingresos
            ingresos_result = self.session.query(
                func.sum(MatriculaModel.monto_final).label('total'),
                func.sum(MatriculaModel.monto_pagado).label('pagado')
            ).first()
            
            ingresos_totales = Decimal(ingresos_result.total or 0)
            ingresos_pagados = Decimal(ingresos_result.pagado or 0)
            ingresos_pendientes = ingresos_totales - ingresos_pagados
            
            # Mora total
            mora_result = self.session.query(
                func.sum(MatriculaModel.monto_final - MatriculaModel.monto_pagado)
            ).filter(MatriculaModel.estado_pago == 'MORA').scalar()
            
            mora_total = Decimal(mora_result or 0)
            
            return MatriculaStats(
                total=total,
                por_estado_pago=por_estado_pago,
                por_estado_academico=por_estado_academico,
                ingresos_totales=ingresos_totales,
                ingresos_pagados=ingresos_pagados,
                ingresos_pendientes=ingresos_pendientes,
                mora_total=mora_total
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return MatriculaStats(
                total=0,
                por_estado_pago={},
                por_estado_academico={},
                ingresos_totales=Decimal('0'),
                ingresos_pagados=Decimal('0'),
                ingresos_pendientes=Decimal('0'),
                mora_total=Decimal('0')
            )
    
    def generar_reporte_matriculas(
        self,
        fecha_inicio: date,
        fecha_fin: date,
        formato: str = 'json'
    ) -> Dict[str, Any]:
        """
        Generar reporte detallado de matrículas en un período
        
        Args:
            fecha_inicio: Fecha de inicio del período
            fecha_fin: Fecha de fin del período
            formato: Formato del reporte ('json', 'csv', 'pdf')
        
        Returns:
            Diccionario con datos del reporte
        """
        try:
            # Obtener matrículas en el período
            matriculas = self.session.query(MatriculaModel)\
                .filter(
                    and_(
                        MatriculaModel.fecha_matricula >= fecha_inicio,
                        MatriculaModel.fecha_matricula <= fecha_fin
                    )
                )\
                .all()
            
            # Estadísticas del período
            total_matriculas = len(matriculas)
            ingresos_totales = sum(Decimal(str(m.monto_final)) for m in matriculas)
            ingresos_pagados = sum(Decimal(str(m.monto_pagado)) for m in matriculas)
            
            # Agrupar por programa
            programas = {}
            for matricula in matriculas:
                programa_nombre = matricula.programa.nombre
                if programa_nombre not in programas:
                    programas[programa_nombre] = {
                        'matriculas': 0,
                        'ingresos_totales': Decimal('0'),
                        'ingresos_pagados': Decimal('0')
                    }
                
                programas[programa_nombre]['matriculas'] += 1
                programas[programa_nombre]['ingresos_totales'] += Decimal(str(matricula.monto_final))
                programas[programa_nombre]['ingresos_pagados'] += Decimal(str(matricula.monto_pagado))
            
            # Formatear respuesta según formato solicitado
            reporte = {
                'periodo': {
                    'fecha_inicio': fecha_inicio.isoformat(),
                    'fecha_fin': fecha_fin.isoformat()
                },
                'estadisticas_generales': {
                    'total_matriculas': total_matriculas,
                    'ingresos_totales': float(ingresos_totales),
                    'ingresos_pagados': float(ingresos_pagados),
                    'ingresos_pendientes': float(ingresos_totales - ingresos_pagados)
                },
                'por_programa': [
                    {
                        'programa': nombre,
                        'matriculas': datos['matriculas'],
                        'ingresos_totales': float(datos['ingresos_totales']),
                        'ingresos_pagados': float(datos['ingresos_pagados'])
                    }
                    for nombre, datos in programas.items()
                ],
                'matriculas_detalladas': [
                    {
                        'id': m.id,
                        'estudiante': f"{m.estudiante.nombres} {m.estudiante.apellidos}",
                        'programa': m.programa.nombre,
                        'fecha_matricula': m.fecha_matricula.isoformat(),
                        'monto_final': m.monto_final,
                        'monto_pagado': m.monto_pagado,
                        'estado_pago': m.estado_pago,
                        'estado_academico': m.estado_academico
                    }
                    for m in matriculas
                ],
                'generado_en': datetime.now().isoformat()
            }
            
            # Convertir a otros formatos si es necesario
            if formato == 'csv':
                # Implementar conversión a CSV
                pass
            elif formato == 'pdf':
                # Implementar generación de PDF
                pass
            
            return reporte
            
        except Exception as e:
            logger.error(f"Error generando reporte: {e}")
            return {'error': str(e)}
    
    # ==================== MÉTODOS PRIVADOS DE VALIDACIÓN ====================
    
    def _validar_creacion_matricula(
        self,
        estudiante_id: int,
        programa_id: int,
        modalidad_pago: str,
        plan_pago_id: Optional[int] = None
    ) -> List[str]:
        """Validar datos para creación de matrícula"""
        errores = []
        
        # Validar modalidad de pago
        if modalidad_pago not in ['CONTADO', 'CUOTAS']:
            errores.append("Modalidad de pago inválida")
        
        # Validar plan de pago para modalidad CUOTAS
        if modalidad_pago == 'CUOTAS' and not plan_pago_id:
            errores.append("Plan de pago requerido para modalidad CUOTAS")
        
        # Verificar si ya está matriculado
        if self._esta_matriculado(estudiante_id, programa_id):
            errores.append("El estudiante ya está matriculado en este programa")
        
        # Verificar cupos disponibles
        programa = self._obtener_programa(programa_id)
        if programa and programa.cupos_disponibles <= 0:
            errores.append("No hay cupos disponibles en este programa")
        
        return errores
    
    def _validar_matricula_para_actualizacion(self, matricula: MatriculaModel) -> None:
        """Validar que una matrícula se pueda actualizar"""
        if matricula.estado_academico in ['CONCLUIDO', 'RETIRADO']:
            raise BusinessRuleException(
                f"No se puede actualizar una matrícula en estado {matricula.estado_academico}"
            )
    
    def _validar_pago(
        self,
        matricula: MatriculaModel,
        monto: Decimal,
        nro_cuota: Optional[int] = None
    ) -> None:
        """Validar un pago antes de registrarlo"""
        if matricula.estado_academico in ['CONCLUIDO', 'RETIRADO']:
            raise BusinessRuleException(
                f"No se pueden registrar pagos en matrículas {matricula.estado_academico}"
            )
        
        saldo_pendiente = Decimal(str(matricula.monto_final - matricula.monto_pagado))
        if monto > saldo_pendiente:
            raise ValidationException(
                f"Monto excede el saldo pendiente. Saldo: {saldo_pendiente}, Pago: {monto}"
            )
        
        if nro_cuota:
            cuota = self._obtener_cuota(matricula.id, nro_cuota)
            if not cuota:
                raise NotFoundException(f"Cuota {nro_cuota} no encontrada")
            
            if cuota.estado == 'PAGADA':
                raise BusinessRuleException(f"La cuota {nro_cuota} ya está pagada")
    
    # ==================== MÉTODOS PRIVADOS DE CÁLCULO ====================
    
    def _calcular_montos_matricula(
        self,
        programa: ProgramaAcademicoModel,
        modalidad_pago: str,
        plan_pago: Optional[PlanPagoModel] = None,
        descuento_personalizado: Optional[Decimal] = None
    ) -> Dict[str, Decimal]:
        """Calcular montos para una matrícula"""
        monto_base = Decimal(str(programa.costo_base))
        
        # Descuento por pago contado
        descuento_contado = Decimal('0')
        if modalidad_pago == 'CONTADO':
            descuento_contado = monto_base * Decimal(str(programa.descuento_contado)) / Decimal('100')
        
        # Descuento por promoción
        descuento_promocion = Decimal('0')
        if programa.promocion_activa:
            descuento_promocion = monto_base * Decimal(str(programa.descuento_promocion)) / Decimal('100')
        
        # Descuento personalizado
        descuento_personal = Decimal('0')
        if descuento_personalizado:
            descuento_personal = monto_base * descuento_personalizado / Decimal('100')
        
        # Total descuentos
        descuento_total = descuento_contado + descuento_promocion + descuento_personal
        
        # Monto final
        monto_final = monto_base - descuento_total
        if monto_final < Decimal('0'):
            monto_final = Decimal('0')
        
        return {
            'monto_base': monto_base,
            'descuento_contado': descuento_contado,
            'descuento_promocion': descuento_promocion,
            'descuento_personal': descuento_personal,
            'descuento_total': descuento_total,
            'monto_final': monto_final
        }
    
    def _calcular_descuentos_dialogo(
        self,
        programa: ProgramaAcademicoModel,
        modalidad_pago: str,
        descuento_contado: bool,
        descuento_promocion: bool,
        descuento_manual: Optional[Decimal],
        monto_manual: Optional[Decimal]
    ) -> Dict[str, Any]:
        """Calcular descuentos desde diálogo de matrícula"""
        monto_base = Decimal(str(programa.costo_base))
        
        # Calcular descuentos individuales
        descuentos = []
        total_descuento = Decimal('0')
        
        # Descuento por contado
        if modalidad_pago == 'CONTADO' and descuento_contado:
            desc_contado = monto_base * Decimal(str(programa.descuento_contado)) / Decimal('100')
            descuentos.append({
                'tipo': 'PAGO_CONTADO',
                'porcentaje': programa.descuento_contado,
                'monto': desc_contado
            })
            total_descuento += desc_contado
        
        # Descuento por promoción
        if descuento_promocion and programa.promocion_activa:
            desc_promocion = monto_base * Decimal(str(programa.descuento_promocion)) / Decimal('100')
            descuentos.append({
                'tipo': 'PROMOCION',
                'nombre': programa.descripcion_promocion,
                'porcentaje': programa.descuento_promocion,
                'monto': desc_promocion
            })
            total_descuento += desc_promocion
        
        # Descuento manual
        if descuento_manual:
            desc_manual = monto_base * descuento_manual / Decimal('100')
            descuentos.append({
                'tipo': 'DESCUENTO_MANUAL',
                'porcentaje': float(descuento_manual),
                'monto': desc_manual
            })
            total_descuento += desc_manual
        
        # Calcular monto final
        if monto_manual:
            monto_final = monto_manual
            total_descuento = monto_base - monto_final
        else:
            monto_final = monto_base - total_descuento
        
        # Asegurar que no sea negativo
        if monto_final < Decimal('0'):
            monto_final = Decimal('0')
            total_descuento = monto_base
        
        return {
            'monto_base': monto_base,
            'descuento_total': total_descuento,
            'descuento_total_porcentaje': (total_descuento / monto_base * Decimal('100')) if monto_base > Decimal('0') else Decimal('0'),
            'monto_final': monto_final,
            'detalle': descuentos
        }
    
    # ==================== MÉTODOS PRIVADOS DE BASE DE DATOS ====================
    
    def _obtener_matricula_por_id(self, matricula_id: int) -> Optional[MatriculaModel]:
        """Obtener matrícula por ID con manejo de errores"""
        try:
            return self.session.query(MatriculaModel).get(matricula_id)
        except Exception as e:
            logger.error(f"Error obteniendo matrícula {matricula_id}: {e}")
            return None
    
    def _obtener_estudiante(self, estudiante_id: int) -> EstudianteModel:
        """Obtener estudiante o lanzar excepción"""
        estudiante = self.session.query(EstudianteModel).get(estudiante_id)
        if not estudiante:
            raise NotFoundException(f"Estudiante {estudiante_id} no encontrado")
        return estudiante
    
    def _obtener_programa(self, programa_id: int) -> ProgramaAcademicoModel:
        """Obtener programa o lanzar excepción"""
        programa = self.session.query(ProgramaAcademicoModel).get(programa_id)
        if not programa:
            raise NotFoundException(f"Programa {programa_id} no encontrado")
        return programa
    
    def _esta_matriculado(self, estudiante_id: int, programa_id: int) -> bool:
        """Verificar si ya está matriculado"""
        count = self.session.query(func.count(MatriculaModel.id))\
            .filter(
                and_(
                    MatriculaModel.estudiante_id == estudiante_id,
                    MatriculaModel.programa_id == programa_id,
                    MatriculaModel.estado_academico.in_(['INSCRITO', 'EN_CURSO', 'PREINSCRITO'])
                )
            )\
            .scalar()
        return count > 0
    
    def _crear_cuotas_programadas(
        self,
        matricula_id: int,
        monto_total: Decimal,
        plan_pago: PlanPagoModel,
        fecha_inicio: Optional[date] = None
    ) -> None:
        """Crear cuotas programadas para una matrícula"""
        fecha_inicio = fecha_inicio or date.today()
        monto_cuota = monto_total / Decimal(str(plan_pago.nro_cuotas))
        
        for i in range(plan_pago.nro_cuotas):
            fecha_vencimiento = fecha_inicio + timedelta(days=i * plan_pago.intervalo_dias)
            
            cuota = CuotaModel(
                matricula_id=matricula_id,
                nro_cuota=i + 1,
                monto=float(monto_cuota.quantize(Decimal('0.01'), ROUND_HALF_UP)),
                fecha_vencimiento=fecha_vencimiento,
                estado='PENDIENTE'
            )
            cuota.save()
    
    # ==================== MÉTODOS PRIVADOS DE UTILIDAD ====================
    
    def _actualizar_estado_pago(self, matricula: MatriculaModel) -> None:
        """Actualizar estado de pago de una matrícula"""
        saldo_pendiente = matricula.monto_final - matricula.monto_pagado
        
        if matricula.monto_pagado <= 0:
            nuevo_estado = 'PENDIENTE'
        elif saldo_pendiente <= 0:
            nuevo_estado = 'PAGADO'
        elif self._tiene_cuotas_vencidas(matricula.id):
            nuevo_estado = 'MORA'
        else:
            nuevo_estado = 'PARCIAL'
        
        if matricula.estado_pago != nuevo_estado:
            matricula.estado_pago = nuevo_estado
            matricula.save()
    
    def _tiene_cuotas_vencidas(self, matricula_id: int) -> bool:
        """Verificar si tiene cuotas vencidas"""
        hoy = date.today()
        count = self.session.query(func.count(CuotaModel.id))\
            .filter(
                and_(
                    CuotaModel.matricula_id == matricula_id,
                    CuotaModel.fecha_vencimiento < hoy,
                    CuotaModel.estado == 'PENDIENTE'
                )
            )\
            .scalar()
        return count > 0
    
    def _calcular_dias_mora(self, matricula: MatriculaModel) -> int:
        """Calcular días en mora para una matrícula"""
        if matricula.estado_pago != 'MORA':
            return 0
        
        # Obtener la cuota más antigua vencida
        cuota_vencida = self.session.query(CuotaModel)\
            .filter(
                and_(
                    CuotaModel.matricula_id == matricula.id,
                    CuotaModel.fecha_vencimiento < date.today(),
                    CuotaModel.estado == 'PENDIENTE'
                )
            )\
            .order_by(asc(CuotaModel.fecha_vencimiento))\
            .first()
        
        if cuota_vencida:
            dias_mora = (date.today() - cuota_vencida.fecha_vencimiento).days
            return max(0, dias_mora)
        
        return 0
    
    # ==================== MÉTODOS DE AUDITORÍA Y LOG ====================
    
    def _registrar_auditoria(self, accion: str, descripcion: str, usuario_id: Optional[int]) -> None:
        """Registrar acción de auditoría"""
        # Implementar según tu sistema de auditoría
        logger.info(f"AUDITORIA - {accion} - Usuario: {usuario_id} - {descripcion}")
    
    def _registrar_movimiento_caja(
        self,
        tipo: str,
        monto: Decimal,
        descripcion: str,
        referencia_tipo: str,
        referencia_id: int
    ) -> None:
        """Registrar movimiento de caja"""
        # Implementar según tu sistema de movimientos de caja
        logger.info(f"CAJA - {tipo} - {monto} - {descripcion}")
    
    def _guardar_matricula(self, matricula: MatriculaModel) -> None:
        """Guardar matrícula con manejo de errores"""
        try:
            if not matricula.save():
                raise DatabaseException("Error al guardar matrícula")
        except Exception as e:
            logger.error(f"Error guardando matrícula: {e}")
            raise
    
    # ==================== MÉTODOS DE FACTORÍA ====================
    
    @classmethod
    def crear_con_sesion(cls, session: Session) -> 'MatriculaController':
        """Crear instancia con sesión proporcionada"""
        return cls(session=session)
    
    @classmethod
    def crear_singleton(cls) -> 'MatriculaController':
        """Crear instancia singleton (para uso global)"""
        if not hasattr(cls, '_instancia'):
            from database import SessionLocal
            session = SessionLocal()
            cls._instancia = cls(session=session)
        return cls._instancia