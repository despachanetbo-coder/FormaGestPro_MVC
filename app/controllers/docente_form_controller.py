# app/controllers/docente_form_controller.py
"""
Controlador optimizado y único para la gestión de docentes en FormaGestPro_MVC
"""

import logging
import csv
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple, Any

from app.models.docente_model import DocenteModel
from app.models.usuarios_model import UsuarioModel
from app.models.programa_academico_model import ProgramaAcademicoModel

logger = logging.getLogger(__name__)

class DocenteFormController:
    """Controlador único para gestión de docentes"""
    
    def __init__(self, db_path: str = None):
        """
        Inicializar controlador de docentes

        Args:
            db_path: Ruta a la base de datos (opcional)
        """
        self.db_path = db_path
        self._current_usuario = None  # Usuario actual (para auditoría)
    
    @property
    def current_usuario(self) -> Optional[UsuarioModel]:
        """Obtener usuario actual"""
        return self._current_usuario
    
    @current_usuario.setter
    def current_usuario(self, usuario: UsuarioModel):
        """Establecer usuario actual"""
        self._current_usuario = usuario
    
    # ==================== CRUD ESENCIAL ====================
    
    def crear_docente(self, datos: Dict[str, Any]) -> Tuple[bool, str, Optional[DocenteModel]]:
        """
        Crear un nuevo docente (método usado por DocenteFormDialog)
        
        Args:
            datos: Diccionario con datos del docente
            
        Returns:
            Tuple (éxito, mensaje, docente)
        """
        try:
            # Validar permisos
            if not self._tiene_permisos_administrativos():
                return False, "No tiene permisos para crear docentes", None
            
            # Validar datos
            errores = self._validar_datos_docente(datos)
            if errores:
                return False, "Errores de validación: " + "; ".join(errores), None
            
            # Verificar duplicados de CI
            if 'ci_numero' in datos:
                existente = DocenteModel.buscar_por_ci(
                    datos['ci_numero'], 
                    datos.get('ci_expedicion')
                )
                if existente:
                    return False, f"Ya existe un docente con CI {datos['ci_numero']}", None
            
            # Crear docente
            docente = DocenteModel.crear_docente(datos)
            
            if docente and hasattr(docente, 'id') and docente.id:
                docente_creado = DocenteModel.find_by_id(docente.id)
                mensaje = f"Docente creado exitosamente (ID: {docente.id})"
                return True, mensaje, docente_creado
            else:
                return False, "Error al guardar el docente", None
        
        except Exception as e:
            logger.error(f"Error al crear docente: {e}")
            return False, f"Error interno: {str(e)}", None
    
    def actualizar_docente(self, docente_id: int, datos: Dict[str, Any]) -> Tuple[bool, str, Optional[DocenteModel]]:
        """
        Actualizar docente existente (método usado por DocenteFormDialog)
        
        Args:
            docente_id: ID del docente
            datos: Datos a actualizar
            
        Returns:
            Tuple (éxito, mensaje, docente actualizado)
        """
        try:
            # Validar permisos
            if not self._tiene_permisos_administrativos():
                return False, "No tiene permisos para actualizar docentes", None
            
            # Obtener docente existente
            docente = DocenteModel.find_by_id(docente_id)
            if not docente:
                return False, f"No se encontró docente con ID {docente_id}", None
            
            # Verificar duplicados de CI si se modifica
            if 'ci_numero' in datos and datos['ci_numero'] != docente.ci_numero:
                existente = DocenteModel.buscar_por_ci(
                    datos['ci_numero'], 
                    datos.get('ci_expedicion', docente.ci_expedicion)
                )
                if existente and existente.id != docente_id:
                    return False, f"El CI '{datos['ci_numero']}' ya está en uso", None
            
            # Combinar datos y validar
            datos_completos = {k: getattr(docente, k) for k in vars(docente) if not k.startswith('_')}
            datos_completos.update(datos)
            
            errores = self._validar_datos_docente(datos_completos)
            if errores:
                return False, "Errores de validación: " + "; ".join(errores), None
            
            # Actualizar
            for key, value in datos.items():
                if hasattr(docente, key):
                    setattr(docente, key, value)
            
            if docente.save():
                docente_actualizado = DocenteModel.find_by_id(docente_id)
                return True, "Docente actualizado exitosamente", docente_actualizado
            else:
                return False, "Error al actualizar el docente", None
        
        except Exception as e:
            logger.error(f"Error al actualizar docente {docente_id}: {e}")
            return False, f"Error interno: {str(e)}", None
    
    def eliminar_docente(self, docente_id: int) -> Tuple[bool, str]:
        """
        Eliminar (desactivar) docente
        
        Args:
            docente_id: ID del docente
            
        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            docente = DocenteModel.find_by_id(docente_id)
            if not docente:
                return False, f"No se encontró docente con ID {docente_id}"
            
            docente.activo = 0
            if docente.save():
                return True, f"Docente desactivado exitosamente"
            else:
                return False, "Error al desactivar docente"
        
        except Exception as e:
            logger.error(f"Error al eliminar docente {docente_id}: {e}")
            return False, f"Error interno: {str(e)}"
    
    def obtener_docente(self, docente_id: int) -> Optional[DocenteModel]:
        """
        Obtener docente por ID (método usado por DocenteInfoDialog)
        
        Args:
            docente_id: ID del docente
            
        Returns:
            DocenteModel o None
        """
        try:
            return DocenteModel.find_by_id(docente_id)
        except Exception as e:
            logger.error(f"Error al obtener docente {docente_id}: {e}")
            return None
    
    def obtener_docentes_activos(self) -> List[DocenteModel]:
        """
        Obtener docentes activos
        
        Returns:
            Lista de docentes activos
        """
        try:
            return DocenteModel.buscar_activos()
        except Exception as e:
            logger.error(f"Error al obtener docentes activos: {e}")
            return []
    
    # ==================== MÉTODOS AUXILIARES ====================
    
    def _validar_datos_docente(self, datos: Dict[str, Any]) -> List[str]:
        """
        Validar datos del docente
        
        Args:
            datos: Diccionario con datos a validar
            
        Returns:
            Lista de mensajes de error
        """
        errores = []
        
        # Validar campos requeridos
        campos_requeridos = ['ci_numero', 'nombres', 'apellidos']
        for campo in campos_requeridos:
            if campo not in datos or not str(datos.get(campo, '')).strip():
                errores.append(f"El campo '{campo}' es requerido")
        
        # Validar CI
        if 'ci_numero' in datos and datos['ci_numero']:
            ci = str(datos['ci_numero']).strip()
            if not ci.isdigit():
                errores.append("El número de CI debe contener solo dígitos")
            if len(ci) < 4 or len(ci) > 10:
                errores.append("El CI debe tener entre 4 y 10 dígitos")
        
        # Validar email
        if 'email' in datos and datos['email']:
            email = str(datos['email']).strip()
            if '@' not in email or '.' not in email.split('@')[-1]:
                errores.append("Formato de email inválido")
        
        # Validar teléfono
        if 'telefono' in datos and datos['telefono']:
            telefono = str(datos['telefono']).strip()
            if not telefono.replace('+', '').replace(' ', '').isdigit():
                errores.append("Teléfono inválido. Solo dígitos, espacios y +")
        
        return errores
    
    def _tiene_permisos_administrativos(self) -> bool:
        """
        Verificar permisos del usuario actual
        
        Returns:
            True si tiene permisos administrativos
        """
        if not self._current_usuario:
            # Si no hay usuario configurado, permitir (para desarrollo)
            return True
        
        roles_permitidos = ['ADMIN', 'DIRECTOR', 'COORDINADOR']
        return self._current_usuario.rol in roles_permitidos
    
    # ==================== MÉTODOS ADICIONALES (opcionales) ====================
    # Estos métodos pueden eliminarse si no se usan en tu aplicación
    
    def buscar_docentes(self, termino: str, campo: str = 'nombre') -> List[DocenteModel]:
        """Búsqueda de docentes"""
        try:
            return DocenteModel.buscar(termino, campo)
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            return []
    
    def contar_docentes(self, activos: bool = True) -> int:
        """Contar docentes"""
        try:
            return DocenteModel.contar(activos=activos)
        except Exception as e:
            logger.error(f"Error al contar: {e}")
            return 0