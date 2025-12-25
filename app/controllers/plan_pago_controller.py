# app/controllers/plan_pago_controller.py
"""
Controlador para la gestión de Planes de Pago en FormaGestPro_MVC

Responsabilidades:
- CRUD de planes de pago
- Validación y cálculo de cuotas
- Integración con programas académicos
- Generación de estructuras de pago

Autor: FormaGestPro_MVC Team
Versión: 2.0.0
Última actualización: [Fecha actual]
"""

import logging
from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum

from sqlalchemy import and_, or_, func, desc, asc, case
from sqlalchemy.orm import Session, joinedload

# Importar modelos
from app.models.plan_pago_model import PlanPagoModel
from app.models.programa_academico_model import ProgramaAcademicoModel
from app.models.matricula_model import MatriculaModel

# Importar utilidades y excepciones
from app.utils.validators import Validator
from app.utils.exceptions import (
    BusinessRuleException,
    ValidationException,
    NotFoundException,
    DatabaseException
)

logger = logging.getLogger(__name__)


class EstadoPlanPago(Enum):
    """Estados posibles de un plan de pago"""
    ACTIVO = 'ACTIVO'
    INACTIVO = 'INACTIVO'
    ARCHIVADO = 'ARCHIVADO'


@dataclass
class CalculoCuotas:
    """Estructura para resultados de cálculo de cuotas"""
    nro_cuotas: int
    intervalo_dias: int
    monto_cuota: Decimal
    cuotas_detalle: List[Dict[str, Any]]
    total_monto: Decimal
    fecha_inicio: date
    fecha_fin: date


class PlanPagoController:
    """Controlador principal para operaciones de Planes de Pago"""
    
    def __init__(self, session: Session = None):
        """
        Inicializar controlador de planes de pago
        
        Args:
            session: Sesión de SQLAlchemy (opcional)
        """
        self.session = session
        self.validator = Validator()
        self._cuota_minima = Decimal('10.00')  # Cuota mínima permitida
    
    # ==================== OPERACIONES CRUD PRINCIPALES ====================
    
    def crear_plan_pago(
        self,
        programa_id: int,
        nombre: str,
        nro_cuotas: int,
        intervalo_dias: int,
        descripcion: Optional[str] = None,
        activo: bool = True,
        usuario_id: Optional[int] = None
    ) -> Tuple[bool, str, Optional[PlanPagoModel]]:
        """
        Crear un nuevo plan de pago
        
        Args:
            programa_id: ID del programa asociado
            nombre: Nombre del plan (ej: "Plan 3 Cuotas Mensuales")
            nro_cuotas: Número de cuotas (1-36)
            intervalo_dias: Días entre cuotas (ej: 30 para mensual)
            descripcion: Descripción detallada del plan
            activo: Estado activo/inactivo
            usuario_id: ID del usuario creador
        
        Returns:
            Tuple (éxito, mensaje, plan_pago_creado)
        """
        try:
            logger.info(f"Iniciando creación de plan de pago para programa {programa_id}")
            
            # 1. Validaciones básicas
            errores = self._validar_datos_plan_pago(
                programa_id, nombre, nro_cuotas, intervalo_dias
            )
            if errores:
                return False, "; ".join(errores), None
            
            # 2. Verificar que el programa existe y está activo
            programa = self._obtener_programa(programa_id)
            if not programa:
                return False, f"Programa {programa_id} no encontrado", None
            
            # 3. Verificar nombre único por programa
            if self._existe_plan_con_nombre(programa_id, nombre):
                return False, f"Ya existe un plan con el nombre '{nombre}' para este programa", None
            
            # 4. Validar límites según el programa
            monto_base = Decimal(str(programa.costo_base))
            errores_limites = self._validar_limites_plan(
                monto_base, nro_cuotas, intervalo_dias
            )
            if errores_limites:
                return False, "; ".join(errores_limites), None
            
            # 5. Crear el plan de pago
            plan_data = {
                'programa_id': programa_id,
                'nombre': nombre.strip(),
                'nro_cuotas': nro_cuotas,
                'intervalo_dias': intervalo_dias,
                'descripcion': descripcion,
                'activo': activo,
                'creado_por': usuario_id,
                'fecha_creacion': datetime.now()
            }
            
            plan_pago = PlanPagoModel(**plan_data)
            
            # 6. Guardar en base de datos
            if not plan_pago.save():
                raise DatabaseException("Error al guardar el plan de pago")
            
            # 7. Registrar auditoría
            self._registrar_auditoria(
                'CREACION_PLAN_PAGO',
                f'Plan de pago {plan_pago.id} creado para programa {programa_id}',
                usuario_id
            )
            
            logger.info(f"Plan de pago {plan_pago.id} creado exitosamente")
            return True, f"Plan de pago creado exitosamente (ID: {plan_pago.id})", plan_pago
            
        except ValidationException as e:
            logger.warning(f"Validación fallida: {e}")
            return False, str(e), None
        except BusinessRuleException as e:
            logger.warning(f"Regla de negocio violada: {e}")
            return False, str(e), None
        except Exception as e:
            logger.error(f"Error crítico creando plan de pago: {e}", exc_info=True)
            return False, f"Error interno del sistema: {str(e)}", None
    
    def actualizar_plan_pago(
        self,
        plan_pago_id: int,
        datos_actualizacion: Dict[str, Any],
        usuario_id: Optional[int] = None
    ) -> Tuple[bool, str, Optional[PlanPagoModel]]:
        """
        Actualizar un plan de pago existente
        
        Args:
            plan_pago_id: ID del plan a actualizar
            datos_actualizacion: Datos a actualizar
            usuario_id: ID del usuario que realiza la operación
        
        Returns:
            Tuple (éxito, mensaje, plan_pago_actualizado)
        """
        try:
            # 1. Obtener plan existente
            plan_pago = self._obtener_plan_por_id(plan_pago_id)
            if not plan_pago:
                raise NotFoundException(f"Plan de pago {plan_pago_id} no encontrado")
            
            # 2. Validar que el plan se pueda actualizar
            if not self._validar_plan_para_actualizacion(plan_pago):
                return False, "No se puede actualizar un plan con matrículas activas", None
            
            # 3. Validar datos de actualización
            errores = self._validar_datos_actualizacion(datos_actualizacion, plan_pago)
            if errores:
                return False, "; ".join(errores), None
            
            # 4. Campos que no se pueden actualizar directamente
            campos_protegidos = ['id', 'programa_id', 'fecha_creacion', 'creado_por']
            for campo in campos_protegidos:
                if campo in datos_actualizacion:
                    del datos_actualizacion[campo]
            
            # 5. Validar nombre único si se está actualizando
            if 'nombre' in datos_actualizacion:
                nuevo_nombre = datos_actualizacion['nombre'].strip()
                if nuevo_nombre != plan_pago.nombre:
                    if self._existe_plan_con_nombre(plan_pago.programa_id, nuevo_nombre, excluir_id=plan_pago_id):
                        return False, f"Ya existe un plan con el nombre '{nuevo_nombre}'", None
            
            # 6. Actualizar campos
            for campo, valor in datos_actualizacion.items():
                if hasattr(plan_pago, campo):
                    # Validaciones específicas por campo
                    if campo in ['nro_cuotas', 'intervalo_dias']:
                        if not self._validar_cambio_cuotas(plan_pago, campo, valor):
                            return False, f"No se puede cambiar {campo} en un plan con matrículas", None
                    
                    setattr(plan_pago, campo, valor)
            
            # 7. Actualizar fecha de modificación
            plan_pago.fecha_modificacion = datetime.now()
            plan_pago.modificado_por = usuario_id
            
            # 8. Guardar cambios
            if not plan_pago.save():
                raise DatabaseException("Error al guardar cambios en el plan de pago")
            
            # 9. Registrar auditoría
            self._registrar_auditoria(
                'ACTUALIZACION_PLAN_PAGO',
                f'Plan de pago {plan_pago_id} actualizado',
                usuario_id
            )
            
            return True, f"Plan de pago {plan_pago_id} actualizado exitosamente", plan_pago
            
        except (ValidationException, BusinessRuleException, NotFoundException) as e:
            logger.warning(f"Error controlado actualizando plan de pago: {e}")
            return False, str(e), None
        except Exception as e:
            logger.error(f"Error actualizando plan de pago {plan_pago_id}: {e}", exc_info=True)
            return False, f"Error interno: {str(e)}", None
    
    def cambiar_estado_plan_pago(
        self,
        plan_pago_id: int,
        activo: bool,
        usuario_id: Optional[int] = None,
        motivo: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Cambiar estado activo/inactivo de un plan de pago
        
        Args:
            plan_pago_id: ID del plan
            activo: Nuevo estado
            usuario_id: ID del usuario
            motivo: Motivo del cambio (opcional)
        
        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            plan_pago = self._obtener_plan_por_id(plan_pago_id)
            if not plan_pago:
                return False, f"Plan de pago {plan_pago_id} no encontrado"
            
            # Verificar si se puede cambiar el estado
            if not activo and self._tiene_matriculas_activas(plan_pago_id):
                return False, "No se puede desactivar un plan con matrículas activas"
            
            # Cambiar estado
            estado_anterior = plan_pago.activo
            plan_pago.activo = activo
            plan_pago.fecha_modificacion = datetime.now()
            plan_pago.modificado_por = usuario_id
            
            # Registrar motivo si existe
            if motivo:
                plan_pago.observaciones = f"{plan_pago.observaciones or ''}\nCambio estado: {motivo}"
            
            if plan_pago.save():
                # Registrar auditoría
                accion = 'ACTIVACION' if activo else 'DESACTIVACION'
                self._registrar_auditoria(
                    f'{accion}_PLAN_PAGO',
                    f'Plan de pago {plan_pago_id} cambiado de {estado_anterior} a {activo}',
                    usuario_id
                )
                
                estado_texto = "activado" if activo else "desactivado"
                return True, f"Plan de pago {plan_pago_id} {estado_texto} exitosamente"
            else:
                return False, "Error al cambiar estado del plan"
            
        except Exception as e:
            logger.error(f"Error cambiando estado del plan {plan_pago_id}: {e}")
            return False, f"Error interno: {str(e)}"
    
    # ==================== CONSULTAS Y BÚSQUEDAS ====================
    
    def obtener_planes_activos_programa(
        self,
        programa_id: int,
        incluir_inactivos: bool = False
    ) -> List[PlanPagoModel]:
        """
        Obtener planes de pago activos para un programa
        
        Args:
            programa_id: ID del programa
            incluir_inactivos: Incluir planes inactivos
        
        Returns:
            Lista de planes de pago
        """
        try:
            query = self.session.query(PlanPagoModel)\
                .filter(PlanPagoModel.programa_id == programa_id)
            
            if not incluir_inactivos:
                query = query.filter(PlanPagoModel.activo == True)
            
            return query.order_by(
                asc(PlanPagoModel.nro_cuotas),
                asc(PlanPagoModel.nombre)
            ).all()
            
        except Exception as e:
            logger.error(f"Error obteniendo planes para programa {programa_id}: {e}")
            return []
    
    def obtener_planes_con_detalles(
        self,
        programa_id: Optional[int] = None,
        activo: Optional[bool] = None,
        nro_cuotas_min: Optional[int] = None,
        nro_cuotas_max: Optional[int] = None,
        ordenar_por: str = 'nombre',
        orden_descendente: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Obtener planes de pago con detalles completos
        
        Args:
            programa_id: Filtrar por programa
            activo: Filtrar por estado activo
            nro_cuotas_min: Número mínimo de cuotas
            nro_cuotas_max: Número máximo de cuotas
            ordenar_por: Campo para ordenar
            orden_descendente: Orden descendente
        
        Returns:
            Lista de planes con detalles
        """
        try:
            query = self.session.query(PlanPagoModel)
            
            # Aplicar filtros
            if programa_id:
                query = query.filter(PlanPagoModel.programa_id == programa_id)
            
            if activo is not None:
                query = query.filter(PlanPagoModel.activo == activo)
            
            if nro_cuotas_min is not None:
                query = query.filter(PlanPagoModel.nro_cuotas >= nro_cuotas_min)
            
            if nro_cuotas_max is not None:
                query = query.filter(PlanPagoModel.nro_cuotas <= nro_cuotas_max)
            
            # Aplicar ordenamiento
            campos_validos = ['nombre', 'nro_cuotas', 'intervalo_dias', 'fecha_creacion']
            if ordenar_por not in campos_validos:
                ordenar_por = 'nombre'
            
            campo_orden = getattr(PlanPagoModel, ordenar_por)
            if orden_descendente:
                query = query.order_by(desc(campo_orden))
            else:
                query = query.order_by(asc(campo_orden))
            
            planes = query.all()
            
            # Enriquecer con detalles
            resultado = []
            for plan in planes:
                detalles = self._enriquecer_detalles_plan(plan)
                resultado.append(detalles)
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error obteniendo planes con detalles: {e}")
            return []
    
    def obtener_plan_por_id_completo(self, plan_pago_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtener un plan de pago con todos sus detalles
        
        Args:
            plan_pago_id: ID del plan
        
        Returns:
            Diccionario con detalles completos del plan
        """
        try:
            plan = self._obtener_plan_por_id(plan_pago_id)
            if not plan:
                return None
            
            return self._enriquecer_detalles_plan(plan)
            
        except Exception as e:
            logger.error(f"Error obteniendo plan completo {plan_pago_id}: {e}")
            return None
    
    def buscar_planes_por_nombre(
        self,
        nombre_busqueda: str,
        programa_id: Optional[int] = None,
        limite: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Buscar planes de pago por nombre
        
        Args:
            nombre_busqueda: Texto a buscar en el nombre
            programa_id: Filtrar por programa
            limite: Límite de resultados
        
        Returns:
            Lista de planes encontrados
        """
        try:
            query = self.session.query(PlanPagoModel)\
                .filter(PlanPagoModel.nombre.ilike(f"%{nombre_busqueda}%"))
            
            if programa_id:
                query = query.filter(PlanPagoModel.programa_id == programa_id)
            
            query = query.filter(PlanPagoModel.activo == True)\
                .limit(limite)\
                .order_by(asc(PlanPagoModel.nombre))
            
            planes = query.all()
            
            return [
                {
                    'id': plan.id,
                    'nombre': plan.nombre,
                    'nro_cuotas': plan.nro_cuotas,
                    'intervalo_dias': plan.intervalo_dias,
                    'programa_id': plan.programa_id,
                    'programa_nombre': plan.programa.nombre if plan.programa else None
                }
                for plan in planes
            ]
            
        except Exception as e:
            logger.error(f"Error buscando planes por nombre: {e}")
            return []
    
    # ==================== CÁLCULOS Y SIMULACIONES ====================
    
    def calcular_cuotas_plan(
        self,
        plan_pago_id: int,
        monto_total: Decimal,
        fecha_inicio: Optional[date] = None,
        incluir_detalle: bool = True
    ) -> CalculoCuotas:
        """
        Calcular estructura de cuotas para un plan de pago
        
        Args:
            plan_pago_id: ID del plan
            monto_total: Monto total a dividir en cuotas
            fecha_inicio: Fecha de inicio para cálculo de vencimientos
            incluir_detalle: Incluir detalle de cada cuota
        
        Returns:
            Objeto CalculoCuotas con resultados
        """
        try:
            # 1. Obtener plan
            plan = self._obtener_plan_por_id(plan_pago_id)
            if not plan:
                raise NotFoundException(f"Plan de pago {plan_pago_id} no encontrado")
            
            # 2. Validar monto mínimo por cuota
            monto_cuota = monto_total / Decimal(str(plan.nro_cuotas))
            if monto_cuota < self._cuota_minima:
                raise BusinessRuleException(
                    f"Monto por cuota ({monto_cuota:.2f}) menor al mínimo permitido ({self._cuota_minima})"
                )
            
            # 3. Calcular fechas de vencimiento
            fecha_inicio = fecha_inicio or date.today()
            cuotas_detalle = []
            
            for i in range(plan.nro_cuotas):
                fecha_vencimiento = fecha_inicio + timedelta(days=i * plan.intervalo_dias)
                
                if incluir_detalle:
                    cuota_detalle = {
                        'nro_cuota': i + 1,
                        'monto': float(monto_cuota.quantize(Decimal('0.01'), ROUND_HALF_UP)),
                        'fecha_vencimiento': fecha_vencimiento,
                        'dias_desde_inicio': i * plan.intervalo_dias,
                        'estado': 'PENDIENTE'
                    }
                    cuotas_detalle.append(cuota_detalle)
            
            # 4. Calcular fecha final
            fecha_fin = fecha_inicio + timedelta(days=(plan.nro_cuotas - 1) * plan.intervalo_dias)
            
            return CalculoCuotas(
                nro_cuotas=plan.nro_cuotas,
                intervalo_dias=plan.intervalo_dias,
                monto_cuota=monto_cuota.quantize(Decimal('0.01'), ROUND_HALF_UP),
                cuotas_detalle=cuotas_detalle,
                total_monto=monto_total,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            
        except Exception as e:
            logger.error(f"Error calculando cuotas para plan {plan_pago_id}: {e}")
            raise
    
    def simular_planes_pago(
        self,
        programa_id: int,
        monto_total: Decimal,
        fecha_inicio: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Simular todos los planes de pago disponibles para un programa
        
        Args:
            programa_id: ID del programa
            monto_total: Monto total a financiar
            fecha_inicio: Fecha de inicio para simulación
        
        Returns:
            Lista de planes con simulaciones
        """
        try:
            # 1. Obtener planes activos del programa
            planes = self.obtener_planes_activos_programa(programa_id)
            
            # 2. Simular cada plan
            simulaciones = []
            fecha_inicio = fecha_inicio or date.today()
            
            for plan in planes:
                try:
                    calculo = self.calcular_cuotas_plan(
                        plan.id, monto_total, fecha_inicio, incluir_detalle=False
                    )
                    
                    simulacion = {
                        'plan_id': plan.id,
                        'plan_nombre': plan.nombre,
                        'nro_cuotas': calculo.nro_cuotas,
                        'intervalo_dias': calculo.intervalo_dias,
                        'monto_cuota': float(calculo.monto_cuota),
                        'total_monto': float(calculo.total_monto),
                        'fecha_inicio': calculo.fecha_inicio,
                        'fecha_fin': calculo.fecha_fin,
                        'dias_totales': (calculo.fecha_fin - calculo.fecha_inicio).days,
                        'descripcion': plan.descripcion,
                        'recomendado': self._es_plan_recomendado(plan, monto_total)
                    }
                    
                    simulaciones.append(simulacion)
                    
                except Exception as e:
                    logger.warning(f"Error simulando plan {plan.id}: {e}")
                    continue
            
            # 3. Ordenar por número de cuotas
            simulaciones.sort(key=lambda x: x['nro_cuotas'])
            
            return simulaciones
            
        except Exception as e:
            logger.error(f"Error simulando planes para programa {programa_id}: {e}")
            return []
    
    def obtener_plan_recomendado(
        self,
        programa_id: int,
        monto_total: Decimal,
        preferencia_cuotas: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Obtener plan de pago recomendado para un monto
        
        Args:
            programa_id: ID del programa
            monto_total: Monto total a financiar
            preferencia_cuotas: Preferencia de número de cuotas
        
        Returns:
            Plan recomendado o None
        """
        try:
            # 1. Si hay preferencia, buscar ese plan específico
            if preferencia_cuotas:
                planes = self.obtener_planes_activos_programa(programa_id)
                for plan in planes:
                    if plan.nro_cuotas == preferencia_cuotas:
                        calculo = self.calcular_cuotas_plan(plan.id, monto_total, incluir_detalle=False)
                        return {
                            'plan_id': plan.id,
                            'plan_nombre': plan.nombre,
                            'nro_cuotas': calculo.nro_cuotas,
                            'monto_cuota': float(calculo.monto_cuota),
                            'recomendacion': 'PREFERENCIA_USUARIO'
                        }
            
            # 2. Calcular plan recomendado por algoritmo
            planes = self.simular_planes_pago(programa_id, monto_total)
            if not planes:
                return None
            
            # 3. Algoritmo de recomendación (priorizar cuotas moderadas)
            planes_validos = [
                p for p in planes 
                if Decimal(str(p['monto_cuota'])) >= self._cuota_minima * Decimal('2')
            ]
            
            if not planes_validos:
                # Si no hay planes válidos, usar el de menos cuotas
                planes_validos = planes
            
            # Ordenar por monto de cuota (ascendente) y luego por número de cuotas
            planes_validos.sort(key=lambda x: (x['monto_cuota'], x['nro_cuotas']))
            
            # Tomar el del medio para balancear
            indice_recomendado = len(planes_validos) // 2
            plan_recomendado = planes_validos[indice_recomendado]
            
            plan_recomendado['recomendacion'] = 'ALGORITMO_BALANCEADO'
            return plan_recomendado
            
        except Exception as e:
            logger.error(f"Error obteniendo plan recomendado: {e}")
            return None
    
    # ==================== VALIDACIONES ESPECÍFICAS ====================
    
    def validar_plan_para_matricula(
        self,
        plan_pago_id: int,
        programa_id: int,
        monto_total: Decimal
    ) -> Tuple[bool, str, Optional[CalculoCuotas]]:
        """
        Validar si un plan es válido para una matrícula
        
        Args:
            plan_pago_id: ID del plan
            programa_id: ID del programa
            monto_total: Monto total a financiar
        
        Returns:
            Tuple (válido, mensaje, cálculo_cuotas)
        """
        try:
            # 1. Verificar que el plan existe
            plan = self._obtener_plan_por_id(plan_pago_id)
            if not plan:
                return False, "Plan de pago no encontrado", None
            
            # 2. Verificar que el plan pertenece al programa
            if plan.programa_id != programa_id:
                return False, "El plan de pago no pertenece a este programa", None
            
            # 3. Verificar que el plan está activo
            if not plan.activo:
                return False, "El plan de pago no está activo", None
            
            # 4. Calcular cuotas para validar montos
            calculo = self.calcular_cuotas_plan(plan_pago_id, monto_total, incluir_detalle=False)
            
            # 5. Verificar cuota mínima
            if calculo.monto_cuota < self._cuota_minima:
                return False, f"La cuota resultante ({calculo.monto_cuota:.2f}) es menor al mínimo permitido", None
            
            return True, "Plan válido para matrícula", calculo
            
        except BusinessRuleException as e:
            return False, str(e), None
        except Exception as e:
            logger.error(f"Error validando plan para matrícula: {e}")
            return False, f"Error en validación: {str(e)}", None
    
    # ==================== MÉTODOS PRIVADOS DE VALIDACIÓN ====================
    
    def _validar_datos_plan_pago(
        self,
        programa_id: int,
        nombre: str,
        nro_cuotas: int,
        intervalo_dias: int
    ) -> List[str]:
        """Validar datos básicos para creación de plan de pago"""
        errores = []
        
        # Validar nombre
        if not nombre or not nombre.strip():
            errores.append("El nombre del plan es requerido")
        elif len(nombre.strip()) > 100:
            errores.append("El nombre no puede exceder 100 caracteres")
        
        # Validar número de cuotas
        if not isinstance(nro_cuotas, int) or nro_cuotas < 1:
            errores.append("El número de cuotas debe ser un entero positivo")
        elif nro_cuotas > 36:  # Límite máximo
            errores.append("El número máximo de cuotas es 36")
        
        # Validar intervalo de días
        if not isinstance(intervalo_dias, int) or intervalo_dias < 1:
            errores.append("El intervalo de días debe ser un entero positivo")
        elif intervalo_dias > 365:  # Límite máximo (1 año)
            errores.append("El intervalo máximo entre cuotas es 365 días")
        elif intervalo_dias < 7 and nro_cuotas > 1:  # Mínimo semanal para múltiples cuotas
            errores.append("El intervalo mínimo entre cuotas es 7 días")
        
        return errores
    
    def _validar_limites_plan(
        self,
        monto_base: Decimal,
        nro_cuotas: int,
        intervalo_dias: int
    ) -> List[str]:
        """Validar límites específicos del plan"""
        errores = []
        
        # Calcular cuota aproximada
        if nro_cuotas > 0:
            cuota_aproximada = monto_base / Decimal(str(nro_cuotas))
            
            # Validar cuota mínima
            if cuota_aproximada < self._cuota_minima:
                errores.append(
                    f"La cuota aproximada ({cuota_aproximada:.2f}) es menor al mínimo permitido ({self._cuota_minima})"
                )
            
            # Validar periodo total máximo (2 años)
            periodo_total_dias = (nro_cuotas - 1) * intervalo_dias
            if periodo_total_dias > 730:  # 2 años
                errores.append("El periodo total de pago no puede exceder 2 años")
        
        return errores
    
    def _validar_plan_para_actualizacion(self, plan_pago: PlanPagoModel) -> bool:
        """Validar si un plan se puede actualizar"""
        # No se puede actualizar si tiene matrículas activas
        return not self._tiene_matriculas_activas(plan_pago.id)
    
    def _validar_cambio_cuotas(
        self,
        plan_pago: PlanPagoModel,
        campo: str,
        nuevo_valor: Any
    ) -> bool:
        """Validar cambio en número de cuotas o intervalo"""
        # Si ya tiene matrículas, no se pueden cambiar estos campos
        if self._tiene_matriculas(plan_pago.id):
            return False
        
        # Validaciones específicas
        if campo == 'nro_cuotas':
            return 1 <= nuevo_valor <= 36
        elif campo == 'intervalo_dias':
            return 7 <= nuevo_valor <= 365
        
        return True
    
    # ==================== MÉTODOS PRIVADOS DE CONSULTA ====================
    
    def _obtener_plan_por_id(self, plan_pago_id: int) -> Optional[PlanPagoModel]:
        """Obtener plan por ID con manejo de errores"""
        try:
            return self.session.query(PlanPagoModel).get(plan_pago_id)
        except Exception as e:
            logger.error(f"Error obteniendo plan {plan_pago_id}: {e}")
            return None
    
    def _obtener_programa(self, programa_id: int) -> Optional[ProgramaAcademicoModel]:
        """Obtener programa por ID"""
        try:
            return self.session.query(ProgramaAcademicoModel).get(programa_id)
        except Exception as e:
            logger.error(f"Error obteniendo programa {programa_id}: {e}")
            return None
    
    def _existe_plan_con_nombre(
        self,
        programa_id: int,
        nombre: str,
        excluir_id: Optional[int] = None
    ) -> bool:
        """Verificar si ya existe un plan con ese nombre en el programa"""
        try:
            query = self.session.query(PlanPagoModel)\
                .filter(
                    and_(
                        PlanPagoModel.programa_id == programa_id,
                        PlanPagoModel.nombre.ilike(nombre.strip())
                    )
                )
            
            if excluir_id:
                query = query.filter(PlanPagoModel.id != excluir_id)
            
            return query.first() is not None
            
        except Exception as e:
            logger.error(f"Error verificando nombre de plan: {e}")
            return False
    
    def _tiene_matriculas(self, plan_pago_id: int) -> bool:
        """Verificar si el plan tiene matrículas asociadas"""
        try:
            count = self.session.query(func.count(MatriculaModel.id))\
                .filter(MatriculaModel.plan_pago_id == plan_pago_id)\
                .scalar()
            return count > 0
        except Exception as e:
            logger.error(f"Error verificando matrículas del plan {plan_pago_id}: {e}")
            return False
    
    def _tiene_matriculas_activas(self, plan_pago_id: int) -> bool:
        """Verificar si el plan tiene matrículas activas"""
        try:
            count = self.session.query(func.count(MatriculaModel.id))\
                .filter(
                    and_(
                        MatriculaModel.plan_pago_id == plan_pago_id,
                        MatriculaModel.estado_academico.in_(['INSCRITO', 'EN_CURSO', 'PREINSCRITO'])
                    )
                )\
                .scalar()
            return count > 0
        except Exception as e:
            logger.error(f"Error verificando matrículas activas del plan {plan_pago_id}: {e}")
            return False
    
    # ==================== MÉTODOS PRIVADOS DE UTILIDAD ====================
    
    def _enriquecer_detalles_plan(self, plan: PlanPagoModel) -> Dict[str, Any]:
        """Enriquecer detalles de un plan de pago"""
        try:
            # Contar matrículas asociadas
            nro_matriculas = self.session.query(func.count(MatriculaModel.id))\
                .filter(MatriculaModel.plan_pago_id == plan.id)\
                .scalar() or 0
            
            # Obtener programa
            programa = plan.programa
            
            # Calcular cuota de ejemplo (usando costo base del programa)
            monto_ejemplo = Decimal(str(programa.costo_base)) if programa else Decimal('1000')
            cuota_ejemplo = monto_ejemplo / Decimal(str(plan.nro_cuotas)) if plan.nro_cuotas > 0 else monto_ejemplo
            
            return {
                'id': plan.id,
                'nombre': plan.nombre,
                'descripcion': plan.descripcion,
                'nro_cuotas': plan.nro_cuotas,
                'intervalo_dias': plan.intervalo_dias,
                'activo': plan.activo,
                'programa_id': plan.programa_id,
                'programa_nombre': programa.nombre if programa else None,
                'programa_codigo': programa.codigo if programa else None,
                'fecha_creacion': plan.fecha_creacion.isoformat() if plan.fecha_creacion else None,
                'fecha_modificacion': plan.fecha_modificacion.isoformat() if plan.fecha_modificacion else None,
                'creado_por': plan.creado_por,
                'modificado_por': plan.modificado_por,
                'estadisticas': {
                    'nro_matriculas': nro_matriculas,
                    'cuota_ejemplo': float(cuota_ejemplo.quantize(Decimal('0.01'))),
                    'periodo_total_dias': (plan.nro_cuotas - 1) * plan.intervalo_dias if plan.nro_cuotas > 1 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error enriqueciendo detalles del plan {plan.id}: {e}")
            return plan.to_dict() if hasattr(plan, 'to_dict') else plan.__dict__
    
    def _es_plan_recomendado(self, plan: PlanPagoModel, monto_total: Decimal) -> bool:
        """Determinar si un plan es recomendado para un monto"""
        try:
            cuota = monto_total / Decimal(str(plan.nro_cuotas))
            
            # Reglas de recomendación:
            # 1. Cuota entre 100 y 1000 Bs (ajustable)
            # 2. Número de cuotas entre 3 y 12
            # 3. Intervalo entre 15 y 60 días
            
            cuota_minima_recomendada = Decimal('100.00')
            cuota_maxima_recomendada = Decimal('1000.00')
            
            return (
                cuota_minima_recomendada <= cuota <= cuota_maxima_recomendada and
                3 <= plan.nro_cuotas <= 12 and
                15 <= plan.intervalo_dias <= 60
            )
            
        except:
            return False
    
    def _registrar_auditoria(self, accion: str, descripcion: str, usuario_id: Optional[int]) -> None:
        """Registrar acción de auditoría"""
        # Implementar según tu sistema de auditoría
        logger.info(f"AUDITORIA_PLAN_PAGO - {accion} - Usuario: {usuario_id} - {descripcion}")
    
    # ==================== MÉTODOS DE FACTORÍA ====================
    
    @classmethod
    def crear_con_sesion(cls, session: Session) -> 'PlanPagoController':
        """Crear instancia con sesión proporcionada"""
        return cls(session=session)
    
    @classmethod
    def crear_singleton(cls) -> 'PlanPagoController':
        """Crear instancia singleton (para uso global)"""
        if not hasattr(cls, '_instancia'):
            from database import SessionLocal
            session = SessionLocal()
            cls._instancia = cls(session=session)
        return cls._instancia