# app/controllers/programa_academico_controller.py
"""
Controlador para la gestión de programas académicos en FormaGestPro_MVC
"""

import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any, Union

from app.models.programa_academico_model import ProgramaAcademicoModel
from app.models.usuarios_model import UsuarioModel
from app.models.docente_model import DocenteModel
from app.models.matricula_model import MatriculaModel
from app.models.estudiante_model import EstudianteModel
from app.models.pago_model import PagoModel

logger = logging.getLogger(__name__)

class ProgramaAcademicoController:
    """Controlador para la gestión de programas académicos"""
    def __init__(self, db_path: str = None):
        """
        Inicializar controlador de programas académicos
        
        Args:
            db_path: Ruta a la base de datos (opcional)
        """
        self.db_path = db_path
        self._current_usuario = None  # Usuario actual (para auditoría)
    
    # ==================== PROPIEDADES ====================
    
    @property
    def current_usuario(self) -> Optional[UsuarioModel]:
        """Obtener usuario actual"""
        return self._current_usuario
    
    @current_usuario.setter
    def current_usuario(self, usuario: UsuarioModel):
        """Establecer usuario actual"""
        self._current_usuario = usuario
    
    # ==================== OPERACIONES BÁSICAS ====================
    
    def crear_programa(self, datos: Dict[str, Any]) -> Tuple[bool, str, Optional[ProgramaAcademicoModel]]:
        """
        Crear un nuevo programa académico
        
        Args:
            datos: Diccionario con los datos del programa
            
        Returns:
            Tuple (éxito, mensaje, programa)
        """
        try:
            # Verificar permisos del usuario
            if not self._tiene_permisos_administrativos():
                return False, "No tiene permisos para crear programas académicos", None
            
            # Validar datos
            valido, errores = ProgramaAcademicoModel.validar_datos(datos)
            if not valido:
                return False, "Errores de validación: " + "; ".join(errores), None
            
            # Verificar que el código no exista
            if 'codigo' in datos:
                programa_existente = ProgramaAcademicoModel.get_by_codigo(datos['codigo'])
                if programa_existente:
                    return False, f"El código '{datos['codigo']}' ya está en uso", None
            
            # Ajustar cupos disponibles si no se especifica
            if 'cupos_totales' in datos and 'cupos_disponibles' not in datos:
                datos['cupos_disponibles'] = datos['cupos_totales']
            
            # Crear el programa
            programa = ProgramaAcademicoModel(**datos)
            programa_id = programa.save()
            
            if programa_id:
                programa_creado = ProgramaAcademicoModel.get_by_id(programa_id)
                mensaje = f"Programa académico creado exitosamente (ID: {programa_id})"
                
                logger.info(f"✅ Programa académico creado: {programa.codigo} - {programa.nombre}")
                return True, mensaje, programa_creado
            else:
                return False, "Error al guardar el programa en la base de datos", None
                
        except Exception as e:
            logger.error(f"Error al crear programa académico: {e}")
            return False, f"Error interno: {str(e)}", None
    
    def actualizar_programa(self, programa_id: int, datos: Dict[str, Any]) -> Tuple[bool, str, Optional[ProgramaAcademicoModel]]:
        """
        Actualizar un programa académico existente
        
        Args:
            programa_id: ID del programa a actualizar
            datos: Diccionario con los datos a actualizar
            
        Returns:
            Tuple (éxito, mensaje, programa actualizado)
        """
        try:
            # Verificar permisos del usuario
            if not self._tiene_permisos_administrativos():
                return False, "No tiene permisos para actualizar programas académicos", None
            
            # Obtener programa existente
            programa = ProgramaAcademicoModel.get_by_id(programa_id)
            if not programa:
                return False, f"No se encontró programa con ID {programa_id}", None
            
            # Validar que no se modifique el código a uno existente
            if 'codigo' in datos and datos['codigo'] != programa.codigo:
                programa_existente = ProgramaAcademicoModel.get_by_codigo(datos['codigo'])
                if programa_existente and programa_existente.id != programa_id:
                    return False, f"El código '{datos['codigo']}' ya está en uso por otro programa", None
            
            # Validar datos
            datos_completos = programa.to_dict()
            datos_completos.update(datos)
            valido, errores = ProgramaAcademicoModel.validar_datos(datos_completos)
            if not valido:
                return False, "Errores de validación: " + "; ".join(errores), None
            
            # Validar que los cupos disponibles no sean mayores a los ocupados
            if 'cupos_totales' in datos:
                nuevos_cupos_totales = datos['cupos_totales']
                cupos_ocupados = programa.cupos_totales - programa.cupos_disponibles
                
                if nuevos_cupos_totales < cupos_ocupados:
                    return False, f"No se pueden reducir los cupos totales a menos de {cupos_ocupados} (cupos ocupados)", None
                
                if 'cupos_disponibles' not in datos:
                    datos['cupos_disponibles'] = nuevos_cupos_totales - cupos_ocupados
            
            # Actualizar programa
            for key, value in datos.items():
                if hasattr(programa, key):
                    setattr(programa, key, value)
            
            if programa.save():
                programa_actualizado = ProgramaAcademicoModel.get_by_id(programa_id)
                mensaje = f"Programa académico actualizado exitosamente"
                
                logger.info(f"✅ Programa académico actualizado: {programa.codigo} - {programa.nombre}")
                return True, mensaje, programa_actualizado
            else:
                return False, "Error al actualizar el programa en la base de datos", None
                
        except Exception as e:
            logger.error(f"Error al actualizar programa académico {programa_id}: {e}")
            return False, f"Error interno: {str(e)}", None
    
    def eliminar_programa(self, programa_id: int) -> Tuple[bool, str]:
        """
        Eliminar un programa académico
        
        Args:
            programa_id: ID del programa a eliminar
            
        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            # Verificar permisos del usuario
            if not self._tiene_permisos_administrativos():
                return False, "No tiene permisos para eliminar programas académicos"
            
            # Obtener programa
            programa = ProgramaAcademicoModel.get_by_id(programa_id)
            if not programa:
                return False, f"No se encontró programa con ID {programa_id}"
            
            # Verificar que no tenga estudiantes matriculados
            matriculas = programa.obtener_matriculas()
            if matriculas:
                return False, f"No se puede eliminar el programa. Tiene {len(matriculas)} estudiantes matriculados"
            
            # Eliminar programa
            if programa.delete():
                logger.info(f"✅ Programa académico eliminado: {programa.codigo} - {programa.nombre}")
                return True, f"Programa académico eliminado exitosamente"
            else:
                return False, "Error al eliminar el programa de la base de datos"
                
        except Exception as e:
            logger.error(f"Error al eliminar programa académico {programa_id}: {e}")
            return False, f"Error interno: {str(e)}"
    
    def obtener_programa(self, programa_id: int) -> Optional[ProgramaAcademicoModel]:
        """
        Obtener un programa académico por ID
        
        Args:
            programa_id: ID del programa
            
        Returns:
            Modelo de programa académico o None
        """
        try:
            return ProgramaAcademicoModel.get_by_id(programa_id)
        except Exception as e:
            logger.error(f"Error al obtener programa {programa_id}: {e}")
            return None
    
    # ==================== CONSULTAS Y LISTADOS ====================
    
    def obtener_todos(
        self,
        estado: Optional[str] = None,
        promocion_activa: Optional[bool] = None,
        tutor_id: Optional[int] = None,
        limite: int = 100
    ) -> List[ProgramaAcademicoModel]:
        """
        Obtener todos los programas académicos con filtros
        
        Args:
            estado: Filtrar por estado
            promocion_activa: Filtrar por promoción activa
            tutor_id: Filtrar por tutor
            limite: Límite de resultados
            
        Returns:
            Lista de programas académicos
        """
        try:
            return ProgramaAcademicoModel.get_all(
                estado=estado,
                promocion_activa=promocion_activa,
                tutor_id=tutor_id,
                limite=limite
            )
        except Exception as e:
            logger.error(f"Error al obtener programas académicos: {e}")
            return []
    
    def obtener_disponibles(self) -> List[ProgramaAcademicoModel]:
        """
        Obtener programas con cupos disponibles y activos
        
        Returns:
            Lista de programas disponibles
        """
        try:
            return ProgramaAcademicoModel.get_disponibles()
        except Exception as e:
            logger.error(f"Error al obtener programas disponibles: {e}")
            return []
    
    def obtener_con_promocion(self) -> List[ProgramaAcademicoModel]:
        """
        Obtener programas con promoción activa
        
        Returns:
            Lista de programas con promoción
        """
        try:
            return ProgramaAcademicoModel.get_con_promocion()
        except Exception as e:
            logger.error(f"Error al obtener programas con promoción: {e}")
            return []
    
    def buscar_programas(
        self,
        termino: str,
        campo: str = 'nombre',
        limite: int = 50
    ) -> List[ProgramaAcademicoModel]:
        """
        Buscar programas académicos
        
        Args:
            termino: Término de búsqueda
            campo: Campo a buscar (nombre, codigo, descripcion)
            limite: Límite de resultados
            
        Returns:
            Lista de programas encontrados
        """
        try:
            return ProgramaAcademicoModel.buscar(termino, campo, limite)
        except Exception as e:
            logger.error(f"Error al buscar programas: {e}")
            return []
    
    def obtener_por_inicio(
        self,
        mes: Optional[int] = None,
        año: Optional[int] = None
    ) -> List[ProgramaAcademicoModel]:
        """
        Obtener programas por fecha de inicio planificada
        
        Args:
            mes: Mes (1-12)
            año: Año
            
        Returns:
            Lista de programas
        """
        try:
            return ProgramaAcademicoModel.obtener_programas_por_inicio(mes, año)
        except Exception as e:
            logger.error(f"Error al obtener programas por inicio: {e}")
            return []
    
    # ==================== GESTIÓN DE ESTADOS ====================
    
    def iniciar_programa(self, programa_id: int) -> Tuple[bool, str, Optional[ProgramaAcademicoModel]]:
        """
        Iniciar un programa académico (cambiar estado a INICIADO)
        
        Args:
            programa_id: ID del programa
            
        Returns:
            Tuple (éxito, mensaje, programa actualizado)
        """
        try:
            # Verificar permisos del usuario
            if not self._tiene_permisos_administrativos():
                return False, "No tiene permisos para iniciar programas académicos", None
            
            programa = ProgramaAcademicoModel.get_by_id(programa_id)
            if not programa:
                return False, f"No se encontró programa con ID {programa_id}", None
            
            if programa.estado == 'INICIADO':
                return False, "El programa ya está iniciado", None
            
            if programa.estado not in ['PLANIFICADO']:
                return False, f"No se puede iniciar un programa en estado '{programa.estado}'", None
            
            # Verificar que haya fecha de inicio planificada
            if not programa.fecha_inicio_planificada:
                return False, "El programa no tiene fecha de inicio planificada", None
            
            # Actualizar estado
            if programa.actualizar_estado('INICIADO'):
                programa_actualizado = ProgramaAcademicoModel.get_by_id(programa_id)
                mensaje = f"Programa académico iniciado exitosamente"
                
                logger.info(f"✅ Programa académico iniciado: {programa.codigo} - {programa.nombre}")
                return True, mensaje, programa_actualizado
            else:
                return False, "Error al actualizar el estado del programa", None
                
        except Exception as e:
            logger.error(f"Error al iniciar programa {programa_id}: {e}")
            return False, f"Error interno: {str(e)}", None
    
    def concluir_programa(self, programa_id: int) -> Tuple[bool, str, Optional[ProgramaAcademicoModel]]:
        """
        Concluir un programa académico (cambiar estado a CONCLUIDO)
        
        Args:
            programa_id: ID del programa
            
        Returns:
            Tuple (éxito, mensaje, programa actualizado)
        """
        try:
            # Verificar permisos del usuario
            if not self._tiene_permisos_administrativos():
                return False, "No tiene permisos para concluir programas académicos", None
            
            programa = ProgramaAcademicoModel.get_by_id(programa_id)
            if not programa:
                return False, f"No se encontró programa con ID {programa_id}", None
            
            if programa.estado == 'CONCLUIDO':
                return False, "El programa ya está concluido", None
            
            if programa.estado != 'INICIADO':
                return False, f"No se puede concluir un programa en estado '{programa.estado}'", None
            
            # Verificar que todos los estudiantes hayan completado el programa
            # (Esto es un ejemplo - podrías implementar verificaciones más complejas)
            matriculas = programa.obtener_matriculas()
            if matriculas:
                # Verificar que todas las matrículas estén en estado apropiado
                for matricula in matriculas:
                    if hasattr(matricula, 'estado') and matricula.estado not in ['CONCLUIDO', 'APROBADO']:
                        return False, "No se puede concluir el programa mientras haya estudiantes activos", None
            
            # Actualizar estado
            if programa.actualizar_estado('CONCLUIDO'):
                programa_actualizado = ProgramaAcademicoModel.get_by_id(programa_id)
                mensaje = f"Programa académico concluido exitosamente"
                
                logger.info(f"✅ Programa académico concluido: {programa.codigo} - {programa.nombre}")
                return True, mensaje, programa_actualizado
            else:
                return False, "Error al actualizar el estado del programa", None
                
        except Exception as e:
            logger.error(f"Error al concluir programa {programa_id}: {e}")
            return False, f"Error interno: {str(e)}", None
    
    def cancelar_programa(self, programa_id: int, motivo: Optional[str] = None) -> Tuple[bool, str, Optional[ProgramaAcademicoModel]]:
        """
        Cancelar un programa académico (cambiar estado a CANCELADO)
        
        Args:
            programa_id: ID del programa
            motivo: Motivo de cancelación (opcional)
            
        Returns:
            Tuple (éxito, mensaje, programa actualizado)
        """
        try:
            # Verificar permisos del usuario
            if not self._tiene_permisos_administrativos():
                return False, "No tiene permisos para cancelar programas académicos", None
            
            programa = ProgramaAcademicoModel.get_by_id(programa_id)
            if not programa:
                return False, f"No se encontró programa con ID {programa_id}", None
            
            if programa.estado == 'CANCELADO':
                return False, "El programa ya está cancelado", None
            
            if programa.estado == 'CONCLUIDO':
                return False, "No se puede cancelar un programa ya concluido", None
            
            # Registrar motivo en la descripción si se proporciona
            if motivo:
                descripcion_original = programa.descripcion or ''
                programa.descripcion = f"{descripcion_original}\n\nCANCELADO: {motivo}"
            
            # Actualizar estado
            if programa.actualizar_estado('CANCELADO'):
                programa_actualizado = ProgramaAcademicoModel.get_by_id(programa_id)
                mensaje = f"Programa académico cancelado exitosamente"
                
                logger.info(f"✅ Programa académico cancelado: {programa.codigo} - {programa.nombre}")
                return True, mensaje, programa_actualizado
            else:
                return False, "Error al actualizar el estado del programa", None
                
        except Exception as e:
            logger.error(f"Error al cancelar programa {programa_id}: {e}")
            return False, f"Error interno: {str(e)}", None
    
    # ==================== GESTIÓN DE PROMOCIONES ====================
    
    def activar_promocion(
        self,
        programa_id: int,
        descuento: float,
        descripcion: str,
        fecha_limite: Optional[Union[str, date]] = None
    ) -> Tuple[bool, str, Optional[ProgramaAcademicoModel]]:
        """
        Activar promoción en un programa académico
        
        Args:
            programa_id: ID del programa
            descuento: Porcentaje de descuento (0-100)
            descripcion: Descripción de la promoción
            fecha_limite: Fecha límite de la promoción
            
        Returns:
            Tuple (éxito, mensaje, programa actualizado)
        """
        try:
            # Verificar permisos del usuario
            if not self._tiene_permisos_administrativos():
                return False, "No tiene permisos para activar promociones", None
            
            programa = ProgramaAcademicoModel.get_by_id(programa_id)
            if not programa:
                return False, f"No se encontró programa con ID {programa_id}", None
            
            if programa.estado not in ['PLANIFICADO', 'INICIADO']:
                return False, f"No se puede activar promoción en un programa en estado '{programa.estado}'", None
            
            # Validar descuento
            if descuento < 0 or descuento > 100:
                return False, "El descuento debe estar entre 0 y 100", None
            
            # Actualizar datos de promoción
            datos_actualizacion = {
                'promocion_activa': True,
                'descuento_promocion': Decimal(str(descuento)),
                'descripcion_promocion': descripcion
            }
            
            if fecha_limite:
                if isinstance(fecha_limite, date):
                    fecha_limite = fecha_limite.isoformat()
                datos_actualizacion['promocion_fecha_limite'] = fecha_limite
            
            return self.actualizar_programa(programa_id, datos_actualizacion)
                
        except Exception as e:
            logger.error(f"Error al activar promoción para programa {programa_id}: {e}")
            return False, f"Error interno: {str(e)}", None
    
    def desactivar_promocion(self, programa_id: int) -> Tuple[bool, str, Optional[ProgramaAcademicoModel]]:
        """
        Desactivar promoción en un programa académico
        
        Args:
            programa_id: ID del programa
            
        Returns:
            Tuple (éxito, mensaje, programa actualizado)
        """
        try:
            # Verificar permisos del usuario
            if not self._tiene_permisos_administrativos():
                return False, "No tiene permisos para desactivar promociones", None
            
            programa = ProgramaAcademicoModel.get_by_id(programa_id)
            if not programa:
                return False, f"No se encontró programa con ID {programa_id}", None
            
            if not programa.promocion_activa:
                return False, "El programa no tiene promoción activa", None
            
            # Actualizar datos de promoción
            datos_actualizacion = {
                'promocion_activa': False,
                'descripcion_promocion': None,
                'promocion_fecha_limite': None
            }
            
            return self.actualizar_programa(programa_id, datos_actualizacion)
                
        except Exception as e:
            logger.error(f"Error al desactivar promoción para programa {programa_id}: {e}")
            return False, f"Error interno: {str(e)}", None
    
    # ==================== CÁLCULOS FINANCIEROS ====================
    
    def calcular_costos_programa(self, programa_id: int) -> Dict[str, Any]:
        """
        Calcular todos los costos relacionados con un programa
        
        Args:
            programa_id: ID del programa
            
        Returns:
            Diccionario con cálculos de costos
        """
        try:
            programa = ProgramaAcademicoModel.get_by_id(programa_id)
            if not programa:
                return {'error': f'Programa {programa_id} no encontrado'}
            
            # Costos base
            costo_base = programa.calcular_costo_total(incluir_matricula=True)
            costo_sin_matricula = programa.costo_base
            
            # Costos con descuentos
            costo_contado = programa.calcular_costo_contado()
            costo_promocion = programa.calcular_costo_promocion()
            
            # Valor de cuotas
            valor_cuota = programa.calcular_valor_cuota(incluir_matricula=True)
            valor_cuota_sin_matricula = programa.calcular_valor_cuota(incluir_matricula=False)
            
            # Información de cuotas
            cuotas_info = {
                'numero_cuotas': programa.cuotas_mensuales,
                'dias_entre_cuotas': programa.dias_entre_cuotas,
                'valor_cuota_con_matricula': float(valor_cuota),
                'valor_cuota_sin_matricula': float(valor_cuota_sin_matricula)
            }
            
            # Descuentos disponibles
            descuentos = {
                'contado': float(programa.descuento_contado),
                'promocion_activa': programa.promocion_activa,
                'descuento_promocion': float(programa.descuento_promocion),
                'costo_con_descuento_contado': float(costo_contado),
                'costo_con_promocion': float(costo_promocion)
            }
            
            # Ingresos potenciales
            cupos_ocupados = programa.cupos_totales - programa.cupos_disponibles
            ingresos_potenciales = float(costo_base * Decimal(str(programa.cupos_totales)))
            ingresos_actuales = float(costo_base * Decimal(str(cupos_ocupados)))
            
            return {
                'programa_id': programa_id,
                'programa_nombre': programa.nombre,
                'costos': {
                    'costo_base': float(costo_sin_matricula),
                    'costo_inscripcion': float(programa.costo_inscripcion),
                    'costo_matricula': float(programa.costo_matricula),
                    'costo_total': float(costo_base)
                },
                'descuentos': descuentos,
                'cuotas': cuotas_info,
                'ingresos': {
                    'cupos_totales': programa.cupos_totales,
                    'cupos_ocupados': cupos_ocupados,
                    'cupos_disponibles': programa.cupos_disponibles,
                    'ingresos_potenciales': ingresos_potenciales,
                    'ingresos_actuales': ingresos_actuales,
                    'porcentaje_ocupacion': (cupos_ocupados / programa.cupos_totales * 100) if programa.cupos_totales > 0 else 0
                },
                'fechas': {
                    'promocion_limite': programa.promocion_fecha_limite,
                    'inicio_planificado': programa.fecha_inicio_planificada,
                    'inicio_real': programa.fecha_inicio_real,
                    'fin_real': programa.fecha_fin_real
                }
            }
            
        except Exception as e:
            logger.error(f"Error al calcular costos para programa {programa_id}: {e}")
            return {'error': str(e)}
    
    def simular_matricula(
        self,
        programa_id: int,
        forma_pago: str = 'CONTADO',
        incluir_matricula: bool = True
    ) -> Dict[str, Any]:
        """
        Simular los costos de una matrícula
        
        Args:
            programa_id: ID del programa
            forma_pago: 'CONTADO' o 'CUOTAS'
            incluir_matricula: Incluir costo de matrícula
            
        Returns:
            Diccionario con simulación de costos
        """
        try:
            programa = ProgramaAcademicoModel.get_by_id(programa_id)
            if not programa:
                return {'error': f'Programa {programa_id} no encontrado'}
            
            if not programa.verificar_disponibilidad():
                return {'error': 'No hay cupos disponibles'}
            
            # Costo base según incluir matrícula
            if incluir_matricula:
                costo_base = programa.calcular_costo_total(incluir_matricula=True)
            else:
                costo_base = programa.costo_base
            
            resultado = {
                'programa': programa.nombre,
                'codigo': programa.codigo,
                'forma_pago': forma_pago,
                'incluye_matricula': incluir_matricula,
                'costo_base': float(costo_base),
                'descuentos_aplicables': []
            }
            
            # Calcular costos según forma de pago
            if forma_pago.upper() == 'CONTADO':
                # Aplicar descuento por contado
                costo_final = programa.calcular_costo_contado()
                if incluir_matricula:
                    costo_final += programa.costo_matricula
                
                descuento_contado = float(programa.descuento_contado)
                ahorro_contado = float(costo_base - costo_final)
                
                resultado['costo_final'] = float(costo_final)
                resultado['descuento_contado'] = descuento_contado
                resultado['ahorro_contado'] = ahorro_contado
                resultado['descuentos_aplicables'].append(f'Descuento por pago al contado: {descuento_contado}%')
                
                # Aplicar promoción si está activa
                if programa.promocion_activa:
                    costo_promocion = programa.calcular_costo_promocion()
                    if incluir_matricula:
                        costo_promocion += programa.costo_matricula
                    
                    if costo_promocion < costo_final:
                        descuento_extra = float(costo_final - costo_promocion)
                        resultado['costo_final'] = float(costo_promocion)
                        resultado['descuento_promocion'] = float(programa.descuento_promocion)
                        resultado['ahorro_promocion'] = descuento_extra
                        resultado['descuentos_aplicables'].append(f'Promoción activa: {programa.descuento_promocion}%')
                
            else:  # CUOTAS
                # Calcular valor de cuota
                valor_cuota = programa.calcular_valor_cuota(incluir_matricula=incluir_matricula)
                total_cuotas = float(valor_cuota * Decimal(str(programa.cuotas_mensuales)))
                
                resultado['numero_cuotas'] = programa.cuotas_mensuales
                resultado['valor_cuota'] = float(valor_cuota)
                resultado['costo_final'] = total_cuotas
                resultado['dias_entre_cuotas'] = programa.dias_entre_cuotas
            
            # Calcular ahorro total
            resultado['ahorro_total'] = float(costo_base - Decimal(str(resultado['costo_final'])))
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error al simular matrícula para programa {programa_id}: {e}")
            return {'error': str(e)}
    
    # ==================== INFORMES Y ESTADÍSTICAS ====================
    
    def obtener_estadisticas_generales(self) -> Dict[str, Any]:
        """
        Obtener estadísticas generales de todos los programas
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            return ProgramaAcademicoModel.obtener_estadisticas()
        except Exception as e:
            logger.error(f"Error al obtener estadísticas de programas: {e}")
            return {'error': str(e)}
    
    def obtener_estadisticas_programa(self, programa_id: int) -> Dict[str, Any]:
        """
        Obtener estadísticas específicas de un programa
        
        Args:
            programa_id: ID del programa
            
        Returns:
            Diccionario con estadísticas del programa
        """
        try:
            programa = ProgramaAcademicoModel.get_by_id(programa_id)
            if not programa:
                return {'error': f'Programa {programa_id} no encontrado'}
            
            # Obtener matrículas
            matriculas = programa.obtener_matriculas()
            
            # Obtener estudiantes
            estudiantes = programa.obtener_estudiantes()
            
            # Obtener pagos
            pagos = programa.obtener_pagos()
            
            # Calcular estadísticas de pagos
            total_pagado = Decimal('0')
            pagos_completos = 0
            pagos_pendientes = 0
            
            for pago in pagos:
                if hasattr(pago, 'monto'):
                    total_pagado += Decimal(str(pago.monto))
                
                if hasattr(pago, 'estado'):
                    if pago.estado == 'COMPLETADO':
                        pagos_completos += 1
                    else:
                        pagos_pendientes += 1
            
            # Calcular promedios
            promedio_edad = 0
            if estudiantes:
                edades = []
                hoy = date.today()
                
                for estudiante in estudiantes:
                    if hasattr(estudiante, 'fecha_nacimiento') and estudiante.fecha_nacimiento:
                        try:
                            if isinstance(estudiante.fecha_nacimiento, str):
                                fecha_nac = datetime.strptime(estudiante.fecha_nacimiento, '%Y-%m-%d').date()
                            else:
                                fecha_nac = estudiante.fecha_nacimiento
                            
                            edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
                            edades.append(edad)
                        except:
                            pass
                        
                if edades:
                    promedio_edad = sum(edades) / len(edades)
            
            return {
                'programa': {
                    'id': programa.id,
                    'nombre': programa.nombre,
                    'codigo': programa.codigo,
                    'estado': programa.estado,
                    'cupos_totales': programa.cupos_totales,
                    'cupos_ocupados': programa.cupos_totales - programa.cupos_disponibles,
                    'cupos_disponibles': programa.cupos_disponibles
                },
                'matriculas': {
                    'total': len(matriculas),
                    'activas': len([m for m in matriculas if hasattr(m, 'estado') and m.estado not in ['CANCELADO', 'CONCLUIDO']]),
                    'canceladas': len([m for m in matriculas if hasattr(m, 'estado') and m.estado == 'CANCELADO']),
                    'concluidas': len([m for m in matriculas if hasattr(m, 'estado') and m.estado == 'CONCLUIDO'])
                },
                'estudiantes': {
                    'total': len(estudiantes),
                    'hombres': len([e for e in estudiantes if hasattr(e, 'genero') and e.genero == 'M']),
                    'mujeres': len([e for e in estudiantes if hasattr(e, 'genero') and e.genero == 'F']),
                    'promedio_edad': promedio_edad
                },
                'pagos': {
                    'total': len(pagos),
                    'completados': pagos_completos,
                    'pendientes': pagos_pendientes,
                    'total_pagado': float(total_pagado),
                    'porcentaje_pagos': (pagos_completos / len(pagos) * 100) if pagos else 0
                },
                'financiero': {
                    'ingreso_potencial': float(programa.calcular_costo_total() * Decimal(str(programa.cupos_totales))),
                    'ingreso_real': float(total_pagado),
                    'porcentaje_recaudado': (float(total_pagado) / float(programa.calcular_costo_total() * Decimal(str(programa.cupos_totales))) * 100) if programa.cupos_totales > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error al obtener estadísticas para programa {programa_id}: {e}")
            return {'error': str(e)}
    
    def generar_reporte_programa(
        self,
        programa_id: int,
        formato: str = 'texto'
    ) -> str:
        """
        Generar reporte detallado de un programa
        
        Args:
            programa_id: ID del programa
            formato: 'texto' o 'html'
            
        Returns:
            Reporte formateado
        """
        try:
            programa = ProgramaAcademicoModel.get_by_id(programa_id)
            if not programa:
                return f"Error: Programa {programa_id} no encontrado"
            
            # Obtener información adicional
            tutor = programa.obtener_tutor()
            matriculas = programa.obtener_matriculas()
            estudiantes = programa.obtener_estudiantes()
            estadisticas = self.obtener_estadisticas_programa(programa_id)
            costos = self.calcular_costos_programa(programa_id)
            
            if formato.lower() == 'html':
                return self._generar_reporte_html(
                    programa, tutor, matriculas, estudiantes, estadisticas, costos
                )
            else:
                return self._generar_reporte_texto(
                    programa, tutor, matriculas, estudiantes, estadisticas, costos
                )
                
        except Exception as e:
            logger.error(f"Error al generar reporte para programa {programa_id}: {e}")
            return f"Error al generar reporte: {str(e)}"
    
    def _generar_reporte_texto(
        self,
        programa: ProgramaAcademicoModel,
        tutor: Optional[Any],
        matriculas: List,
        estudiantes: List,
        estadisticas: Dict[str, Any],
        costos: Dict[str, Any]
    ) -> str:
        """Generar reporte en formato texto"""
        reporte = []
        reporte.append("=" * 80)
        reporte.append("REPORTE DE PROGRAMA ACADÉMICO".center(80))
        reporte.append("=" * 80)
        reporte.append(f"Programa: {programa.codigo} - {programa.nombre}")
        reporte.append(f"Estado: {programa.estado}")
        reporte.append(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        reporte.append("-" * 80)
        
        # Información básica
        reporte.append("INFORMACIÓN BÁSICA:")
        reporte.append(f"  Duración: {programa.duracion_semanas} semanas")
        reporte.append(f"  Horas totales: {programa.horas_totales}")
        if programa.descripcion:
            reporte.append(f"  Descripción: {programa.descripcion[:100]}...")
        
        # Tutor
        if tutor:
            reporte.append(f"  Tutor: {tutor.nombre} {tutor.apellido}")
        
        # Fechas
        reporte.append(f"  Inicio planificado: {programa.fecha_inicio_planificada or 'No definido'}")
        if programa.fecha_inicio_real:
            reporte.append(f"  Inicio real: {programa.fecha_inicio_real}")
        if programa.fecha_fin_real:
            reporte.append(f"  Fin real: {programa.fecha_fin_real}")
        
        # Cupos
        reporte.append(f"  Cupos: {programa.cupos_disponibles}/{programa.cupos_totales} disponibles")
        
        reporte.append("-" * 80)
        
        # Costos
        if 'costos' in costos:
            reporte.append("INFORMACIÓN FINANCIERA:")
            reporte.append(f"  Costo base: Bs. {costos['costos']['costo_base']:,.2f}")
            reporte.append(f"  Matrícula: Bs. {costos['costos']['costo_matricula']:,.2f}")
            reporte.append(f"  Costo total: Bs. {costos['costos']['costo_total']:,.2f}")
            
            if costos['descuentos']['promocion_activa']:
                reporte.append(f"  Promoción activa: {costos['descuentos']['descuento_promocion']}%")
                reporte.append(f"  Costo con promoción: Bs. {costos['descuentos']['costo_con_promocion']:,.2f}")
            
            reporte.append(f"  Descuento por contado: {costos['descuentos']['contado']}%")
            reporte.append(f"  Cuotas: {costos['cuotas']['numero_cuotas']} de Bs. {costos['cuotas']['valor_cuota_con_matricula']:,.2f}")
        
        reporte.append("-" * 80)
        
        # Estadísticas
        if 'matriculas' in estadisticas:
            reporte.append("ESTADÍSTICAS:")
            reporte.append(f"  Matrículas totales: {estadisticas['matriculas']['total']}")
            reporte.append(f"  Estudiantes: {estadisticas['estudiantes']['total']}")
            reporte.append(f"  Hombres: {estadisticas['estudiantes']['hombres']}")
            reporte.append(f"  Mujeres: {estadisticas['estudiantes']['mujeres']}")
            
            if 'financiero' in estadisticas:
                reporte.append(f"  Ingreso real: Bs. {estadisticas['financiero']['ingreso_real']:,.2f}")
                reporte.append(f"  Porcentaje recaudado: {estadisticas['financiero']['porcentaje_recaudado']:.1f}%")
        
        reporte.append("=" * 80)
        
        return "\n".join(reporte)
    
    def _generar_reporte_html(
        self,
        programa: ProgramaAcademicoModel,
        tutor: Optional[Any],
        matriculas: List,
        estudiantes: List,
        estadisticas: Dict[str, Any],
        costos: Dict[str, Any]
    ) -> str:
        """Generar reporte en formato HTML"""
        # Formatear nombre del tutor
        nombre_tutor = ""
        if tutor:
            nombre_tutor = f"{tutor.nombre} {tutor.apellido}"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Reporte de Programa Académico</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                h1, h2, h3 {{ color: #2c3e50; }}
                .section {{ margin-bottom: 30px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }}
                .info-item {{ background-color: #f8f9fa; padding: 15px; border-radius: 3px; }}
                .estado-{programa.estado.lower()} {{ 
                    display: inline-block; 
                    padding: 5px 10px; 
                    border-radius: 3px; 
                    font-weight: bold; 
                    margin-left: 10px;
                }}
                .PLANIFICADO {{ background-color: #ffc107; color: #212529; }}
                .INICIADO {{ background-color: #28a745; color: white; }}
                .CONCLUIDO {{ background-color: #17a2b8; color: white; }}
                .CANCELADO {{ background-color: #dc3545; color: white; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
                .stat-card {{ background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }}
                .stat-value {{ font-size: 24px; font-weight: bold; margin: 10px 0; }}
                .stat-label {{ color: #6c757d; font-size: 14px; }}
                .financiero-positivo {{ color: #28a745; }}
                .financiero-negativo {{ color: #dc3545; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f8f9fa; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #6c757d; font-size: 12px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Reporte de Programa Académico</h1>
                <p><strong>Sistema:</strong> FormaGestPro_MVC</p>
                <p><strong>Generado:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            </div>
            
            <div class="section">
                <h2>Información del Programa</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <strong>Código:</strong><br>
                        {programa.codigo}
                    </div>
                    <div class="info-item">
                        <strong>Nombre:</strong><br>
                        {programa.nombre}
                    </div>
                    <div class="info-item">
                        <strong>Estado:</strong><br>
                        <span class="estado-{programa.estado.lower()}">{programa.estado}</span>
                    </div>
                    <div class="info-item">
                        <strong>Tutor:</strong><br>
                        {nombre_tutor or 'No asignado'}
                    </div>
                    <div class="info-item">
                        <strong>Duración:</strong><br>
                        {programa.duracion_semanas} semanas ({programa.horas_totales} horas)
                    </div>
                    <div class="info-item">
                        <strong>Cupos:</strong><br>
                        {programa.cupos_disponibles} / {programa.cupos_totales} disponibles
                        ({((programa.cupos_totales - programa.cupos_disponibles) / programa.cupos_totales * 100 if programa.cupos_totales > 0 else 0):.1f}% ocupados)
                    </div>
                </div>
                
                <div class="info-grid" style="margin-top: 15px;">
                    <div class="info-item">
                        <strong>Inicio planificado:</strong><br>
                        {programa.fecha_inicio_planificada or 'No definido'}
                    </div>
                    <div class="info-item">
                        <strong>Inicio real:</strong><br>
                        {programa.fecha_inicio_real or 'No iniciado'}
                    </div>
                    <div class="info-item">
                        <strong>Fin real:</strong><br>
                        {programa.fecha_fin_real or 'No concluido'}
                    </div>
                </div>
                
                {f'<div class="info-item" style="grid-column: 1 / -1; margin-top: 15px;"><strong>Descripción:</strong><br>{programa.descripcion}</div>' if programa.descripcion else ''}
            </div>
            
            <div class="section">
                <h2>Información Financiera</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <strong>Costo base:</strong><br>
                        Bs. {float(programa.costo_base):,.2f}
                    </div>
                    <div class="info-item">
                        <strong>Costo matrícula:</strong><br>
                        Bs. {float(programa.costo_matricula):,.2f}
                    </div>
                    <div class="info-item">
                        <strong>Costo total:</strong><br>
                        Bs. {float(programa.calcular_costo_total()):,.2f}
                    </div>
                    <div class="info-item">
                        <strong>Descuento por contado:</strong><br>
                        {float(programa.descuento_contado)}%
                    </div>
        """
        
        if programa.promocion_activa:
            html += f"""
                    <div class="info-item">
                        <strong>Promoción activa:</strong><br>
                        {float(programa.descuento_promocion)}%
                        {f'<br><small>Válida hasta: {programa.promocion_fecha_limite}</small>' if programa.promocion_fecha_limite else ''}
                    </div>
            """
        
        html += f"""
                </div>
                
                <div class="info-grid" style="margin-top: 15px;">
                    <div class="info-item">
                        <strong>Cuotas:</strong><br>
                        {programa.cuotas_mensuales} cuotas
                    </div>
                    <div class="info-item">
                        <strong>Valor cuota:</strong><br>
                        Bs. {float(programa.calcular_valor_cuota()):,.2f}
                    </div>
                    <div class="info-item">
                        <strong>Días entre cuotas:</strong><br>
                        {programa.dias_entre_cuotas} días
                    </div>
                </div>
            </div>
        """
        
        # Sección de estadísticas
        if 'matriculas' in estadisticas:
            html += f"""
            <div class="section">
                <h2>Estadísticas</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{estadisticas['matriculas']['total']}</div>
                        <div class="stat-label">Total Matrículas</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{estadisticas['matriculas']['activas']}</div>
                        <div class="stat-label">Matrículas Activas</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{estadisticas['estudiantes']['total']}</div>
                        <div class="stat-label">Estudiantes</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{estadisticas['estudiantes']['hombres']}</div>
                        <div class="stat-label">Hombres</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{estadisticas['estudiantes']['mujeres']}</div>
                        <div class="stat-label">Mujeres</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{estadisticas['pagos']['total']}</div>
                        <div class="stat-label">Pagos Registrados</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{estadisticas['pagos']['completados']}</div>
                        <div class="stat-label">Pagos Completados</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value financiero-{'positivo' if estadisticas['financiero']['porcentaje_recaudado'] > 0 else 'negativo'}">
                            Bs. {estadisticas['financiero']['ingreso_real']:,.2f}
                        </div>
                        <div class="stat-label">Ingreso Real</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value financiero-{'positivo' if estadisticas['financiero']['porcentaje_recaudado'] > 50 else 'negativo'}">
                            {estadisticas['financiero']['porcentaje_recaudado']:.1f}%
                        </div>
                        <div class="stat-label">Recaudado</div>
                    </div>
                </div>
            </div>
            """
        
        html += f"""
            <div class="footer">
                <p><em>Reporte generado automáticamente por FormaGestPro_MVC - Módulo de Programas Académicos</em></p>
                <p><em>Este es un documento oficial para fines de control interno.</em></p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    # ==================== MÉTODOS DE UTILIDAD ====================
    
    def exportar_programas_csv(self, ruta_archivo: str) -> Tuple[bool, str]:
        """
        Exportar todos los programas a archivo CSV
        
        Args:
            ruta_archivo: Ruta del archivo CSV
            
        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            import csv
            
            # Obtener todos los programas
            programas = self.obtener_todos(limite=1000)
            
            # Preparar datos
            datos = []
            for programa in programas:
                fila = programa.to_dict()
                
                # Convertir Decimal a float para CSV
                for key, value in fila.items():
                    if isinstance(value, Decimal):
                        fila[key] = float(value)
                
                datos.append(fila)
            
            # Escribir archivo CSV
            with open(ruta_archivo, 'w', newline='', encoding='utf-8') as csvfile:
                if datos:
                    fieldnames = datos[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    writer.writerows(datos)
            
            logger.info(f"Programas exportados a {ruta_archivo}")
            return True, f"Programas exportados exitosamente a {ruta_archivo}"
            
        except Exception as e:
            logger.error(f"Error al exportar programas a CSV: {e}")
            return False, f"Error al exportar: {str(e)}"
    
    def _tiene_permisos_administrativos(self) -> bool:
        """
        Verificar si el usuario actual tiene permisos administrativos
        
        Returns:
            True si tiene permisos
        """
        if not self._current_usuario:
            return False
        
        # Roles con permisos para gestionar programas
        roles_permitidos = ['ADMIN', 'DIRECTOR', 'COORDINADOR']
        return self._current_usuario.rol in roles_permitidos
    
    def obtener_programas_para_dashboard(self) -> Dict[str, Any]:
        """
        Obtener datos de programas para el dashboard
        
        Returns:
            Diccionario con datos para dashboard
        """
        try:
            # Obtener estadísticas generales
            estadisticas = self.obtener_estadisticas_generales()
            
            # Obtener programas disponibles
            programas_disponibles = self.obtener_disponibles()
            
            # Obtener programas con promoción
            programas_promocion = self.obtener_con_promocion()
            
            # Obtener programas próximos a iniciar (próximos 30 días)
            hoy = date.today()
            proximos_30_dias = (hoy + timedelta(days=30)).isoformat()
            
            programas_proximos = []
            todos_programas = self.obtener_todos(estado='PLANIFICADO')
            
            for programa in todos_programas:
                if programa.fecha_inicio_planificada:
                    try:
                        fecha_inicio = datetime.strptime(programa.fecha_inicio_planificada, '%Y-%m-%d').date()
                        if hoy <= fecha_inicio <= (hoy + timedelta(days=30)):
                            programas_proximos.append(programa)
                    except:
                        pass
                    
            return {
                'estadisticas': estadisticas,
                'programas_disponibles': len(programas_disponibles),
                'programas_promocion': len(programas_promocion),
                'programas_proximos': len(programas_proximos),
                'programas_proximos_lista': [{
                    'id': p.id,
                    'nombre': p.nombre,
                    'codigo': p.codigo,
                    'fecha_inicio': p.fecha_inicio_planificada,
                    'cupos_disponibles': p.cupos_disponibles
                } for p in programas_proximos[:5]],  # Solo primeros 5
                'ultima_actualizacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"Error al obtener datos para dashboard: {e}")
            return {
                'error': str(e),
                'programas_disponibles': 0,
                'programas_promocion': 0,
                'programas_proximos': 0
            }