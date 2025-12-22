# app/controllers/usuarios_controller.py
"""
Controlador para la gestión de usuarios del sistema en FormaGestPro_MVC
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path

from app.models.usuarios_model import UsuarioModel

logger = logging.getLogger(__name__)

class UsuariosController:
    """Controlador para la gestión de usuarios del sistema"""
    def __init__(self, db_path: str = None):
        """
        Inicializar controlador de usuarios

        Args:
            db_path: Ruta a la base de datos (opcional)
        """
        self.db_path = db_path
        self._current_user = None  # Usuario actualmente autenticado

    # ==================== PROPIEDADES ====================

    @property
    def current_user(self) -> Optional[UsuarioModel]:
        """Obtener usuario actualmente autenticado"""
        return self._current_user

    @current_user.setter
    def current_user(self, user: UsuarioModel):
        """Establecer usuario actual"""
        self._current_user = user

    def is_authenticated(self) -> bool:
        """Verificar si hay un usuario autenticado"""
        return self._current_user is not None and self._current_user.activo

    def has_permission(self, required_role: str) -> bool:
        """
        Verificar si el usuario actual tiene permisos suficientes

        Args:
            required_role: Rol mínimo requerido

        Returns:
            True si el usuario tiene permisos suficientes
        """
        if not self._current_user:
            return False

        return self._current_user.has_permission(required_role)

    def can_access_module(self, module: str) -> bool:
        """
        Verificar si el usuario actual puede acceder a un módulo

        Args:
            module: Nombre del módulo

        Returns:
            True si el usuario puede acceder al módulo
        """
        if not self._current_user:
            return False

        return self._current_user.can_access_module(module)

    # ==================== AUTENTICACIÓN ====================

    def login(self, username: str, password: str) -> Tuple[bool, str, Optional[UsuarioModel]]:
        """
        Autenticar usuario

        Args:
            username: Nombre de usuario
            password: Contraseña

        Returns:
            Tuple (éxito, mensaje, usuario)
        """
        try:
            # Validar entrada
            if not username or not password:
                return False, "Nombre de usuario y contraseña son requeridos", None

            # Autenticar
            usuario = UsuarioModel.authenticate(username, password)

            if not usuario:
                return False, "Nombre de usuario o contraseña incorrectos", None

            if not usuario.activo:
                return False, "La cuenta de usuario está desactivada", None

            # Actualizar último login
            usuario.update_last_login()

            # Establecer como usuario actual
            self._current_user = usuario

            mensaje = f"Bienvenido, {usuario.nombre_completo}"
            return True, mensaje, usuario

        except Exception as e:
            logger.error(f"Error en login para usuario {username}: {e}")
            return False, f"Error interno: {str(e)}", None

    def logout(self) -> Tuple[bool, str]:
        """
        Cerrar sesión del usuario actual

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            if not self._current_user:
                return False, "No hay usuario autenticado"

            username = self._current_user.username
            self._current_user = None

            return True, f"Sesión cerrada para {username}"

        except Exception as e:
            logger.error(f"Error en logout: {e}")
            return False, f"Error interno: {str(e)}"

    def change_password(self, current_password: str, new_password: str) -> Tuple[bool, str]:
        """
        Cambiar contraseña del usuario actual

        Args:
            current_password: Contraseña actual
            new_password: Nueva contraseña

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            if not self._current_user:
                return False, "No hay usuario autenticado"

            # Verificar contraseña actual
            if not self._current_user.verify_password(current_password):
                return False, "Contraseña actual incorrecta"

            # Validar nueva contraseña
            valido, mensaje = UsuarioModel.validate_password(new_password)
            if not valido:
                return False, mensaje

            # Cambiar contraseña
            self._current_user.set_password(new_password)

            if self._current_user.save():
                return True, "Contraseña cambiada exitosamente"
            else:
                return False, "Error al guardar la nueva contraseña"

        except Exception as e:
            logger.error(f"Error al cambiar contraseña: {e}")
            return False, f"Error interno: {str(e)}"

    # ==================== OPERACIONES CRUD ====================

    def crear_usuario(self, datos: Dict[str, Any]) -> Tuple[bool, str, Optional[UsuarioModel]]:
        """
        Crear un nuevo usuario

        Args:
            datos: Diccionario con los datos del usuario

        Returns:
            Tuple (éxito, mensaje, usuario)
        """
        try:
            # Verificar permisos
            if not self.has_permission(UsuarioModel.ROL_ADMINISTRADOR):
                return False, "Solo administradores pueden crear usuarios", None

            # Validar datos requeridos
            errores = self._validar_datos_usuario(datos)
            if errores:
                return False, "Errores de validación: " + "; ".join(errores), None

            # Verificar unicidad de username
            username = datos['username']
            existente = UsuarioModel.get_by_username(username)
            if existente:
                return False, f"Ya existe un usuario con el nombre '{username}'", None

            # Verificar unicidad de email si se proporciona
            if 'email' in datos and datos['email']:
                existente_email = UsuarioModel.get_by_email(datos['email'])
                if existente_email:
                    return False, f"Ya existe un usuario con el email '{datos['email']}'", None

            # Crear el usuario
            usuario = UsuarioModel(**datos)

            # Hashear contraseña si se proporciona
            if 'password' in datos:
                usuario.set_password(datos['password'])
            else:
                # Generar contraseña aleatoria
                password_generated = UsuarioModel.generate_random_password()
                usuario.set_password(password_generated)
                datos['password'] = password_generated

            usuario_id = usuario.save()

            if usuario_id:
                usuario_creado = UsuarioModel.get_by_id(usuario_id)
                mensaje = f"Usuario '{username}' creado exitosamente"
                return True, mensaje, usuario_creado
            else:
                return False, "Error al guardar el usuario en la base de datos", None

        except Exception as e:
            logger.error(f"Error al crear usuario: {e}")
            return False, f"Error interno: {str(e)}", None

    def actualizar_usuario(self, usuario_id: int, datos: Dict[str, Any]) -> Tuple[bool, str, Optional[UsuarioModel]]:
        """
        Actualizar un usuario existente

        Args:
            usuario_id: ID del usuario a actualizar
            datos: Diccionario con los datos a actualizar

        Returns:
            Tuple (éxito, mensaje, usuario)
        """
        try:
            # Verificar permisos
            if not self.has_permission(UsuarioModel.ROL_ADMINISTRADOR):
                return False, "Solo administradores pueden actualizar usuarios", None

            # Buscar usuario existente
            usuario = UsuarioModel.get_by_id(usuario_id)
            if not usuario:
                return False, f"No se encontró usuario con ID {usuario_id}", None

            # Validar datos
            errores = self._validar_datos_usuario(datos, es_actualizacion=True)
            if errores:
                return False, "Errores de validación: " + "; ".join(errores), None

            # Verificar unicidad de username si se está actualizando
            if 'username' in datos and datos['username'] != usuario.username:
                existente = UsuarioModel.get_by_username(datos['username'])
                if existente and existente.id != usuario_id:
                    return False, f"Ya existe otro usuario con el nombre '{datos['username']}'", None

            # Verificar unicidad de email si se está actualizando
            if 'email' in datos and datos['email'] != usuario.email:
                existente_email = UsuarioModel.get_by_email(datos['email'])
                if existente_email and existente_email.id != usuario_id:
                    return False, f"Ya existe otro usuario con el email '{datos['email']}'", None

            # Actualizar atributos del usuario
            for key, value in datos.items():
                if hasattr(usuario, key) and key not in ['password', 'password_hash']:
                    setattr(usuario, key, value)

            # Actualizar contraseña si se proporciona
            if 'password' in datos and datos['password']:
                usuario.set_password(datos['password'])

            # Guardar cambios
            if usuario.save():
                mensaje = f"Usuario '{usuario.username}' actualizado exitosamente"
                return True, mensaje, usuario
            else:
                return False, "Error al guardar los cambios", None

        except Exception as e:
            logger.error(f"Error al actualizar usuario {usuario_id}: {e}")
            return False, f"Error interno: {str(e)}", None

    def eliminar_usuario(self, usuario_id: int) -> Tuple[bool, str]:
        """
        Eliminar un usuario (marcar como inactivo)

        Args:
            usuario_id: ID del usuario a eliminar

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            # Verificar permisos
            if not self.has_permission(UsuarioModel.ROL_ADMINISTRADOR):
                return False, "Solo administradores pueden eliminar usuarios"

            usuario = UsuarioModel.get_by_id(usuario_id)
            if not usuario:
                return False, f"No se encontró usuario con ID {usuario_id}"

            # No permitir eliminarse a sí mismo
            if self._current_user and usuario.id == self._current_user.id:
                return False, "No puedes eliminar tu propia cuenta"

            # Cambiar estado a inactivo
            usuario.activo = 0
            if usuario.save():
                return True, f"Usuario '{usuario.username}' desactivado exitosamente"
            else:
                return False, "Error al desactivar el usuario"

        except Exception as e:
            logger.error(f"Error al eliminar usuario {usuario_id}: {e}")
            return False, f"Error interno: {str(e)}"

    def reactivar_usuario(self, usuario_id: int) -> Tuple[bool, str]:
        """
        Reactivar un usuario previamente desactivado

        Args:
            usuario_id: ID del usuario a reactivar

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            # Verificar permisos
            if not self.has_permission(UsuarioModel.ROL_ADMINISTRADOR):
                return False, "Solo administradores pueden reactivar usuarios"

            usuario = UsuarioModel.get_by_id(usuario_id)
            if not usuario:
                return False, f"No se encontró usuario con ID {usuario_id}"

            # Cambiar estado a activo
            usuario.activo = 1
            if usuario.save():
                return True, f"Usuario '{usuario.username}' reactivado exitosamente"
            else:
                return False, "Error al reactivar el usuario"

        except Exception as e:
            logger.error(f"Error al reactivar usuario {usuario_id}: {e}")
            return False, f"Error interno: {str(e)}"

    # ==================== CONSULTAS ====================

    def obtener_usuario(self, usuario_id: int) -> Optional[UsuarioModel]:
        """
        Obtener un usuario por su ID

        Args:
            usuario_id: ID del usuario

        Returns:
            UsuarioModel o None si no se encuentra
        """
        try:
            return UsuarioModel.get_by_id(usuario_id)
        except Exception as e:
            logger.error(f"Error al obtener usuario {usuario_id}: {e}")
            return None

    def obtener_usuario_por_username(self, username: str) -> Optional[UsuarioModel]:
        """
        Obtener usuario por nombre de usuario

        Args:
            username: Nombre de usuario

        Returns:
            UsuarioModel o None si no se encuentra
        """
        try:
            return UsuarioModel.get_by_username(username)
        except Exception as e:
            logger.error(f"Error al obtener usuario por username '{username}': {e}")
            return None

    def obtener_usuarios(
        self, 
        activos: bool = True,
        rol: Optional[str] = None,
        buscar: Optional[str] = None,
        limite: int = 100,
        offset: int = 0,
        orden_por: str = 'nombre_completo',
        orden_asc: bool = True
    ) -> List[UsuarioModel]:
        """
        Obtener lista de usuarios con filtros

        Args:
            activos: Si True, solo usuarios activos
            rol: Filtrar por rol
            buscar: Texto para búsqueda en username, nombre_completo o email
            limite: Número máximo de resultados
            offset: Desplazamiento para paginación
            orden_por: Campo para ordenar ('nombre_completo', 'username', 'rol', 'created_at')
            orden_asc: Orden ascendente (True) o descendente (False)

        Returns:
            Lista de usuarios
        """
        try:
            # Construir condiciones
            condiciones = []
            parametros = []

            if activos:
                condiciones.append("activo = ?")
                parametros.append(1)

            if rol:
                condiciones.append("rol = ?")
                parametros.append(rol)

            if buscar:
                condiciones.append("(username LIKE ? OR nombre_completo LIKE ? OR email LIKE ?)")
                parametros.extend([f"%{buscar}%", f"%{buscar}%", f"%{buscar}%"])

            # Convertir condiciones a string
            where_clause = ""
            if condiciones:
                where_clause = "WHERE " + " AND ".join(condiciones)

            # Validar campo de orden
            campos_validos = ['nombre_completo', 'username', 'rol', 'created_at', 'last_login']
            if orden_por not in campos_validos:
                orden_por = 'nombre_completo'

            # Construir orden
            orden = f"{orden_por} {'ASC' if orden_asc else 'DESC'}"

            # Construir límite
            limit_clause = ""
            if limite > 0:
                limit_clause = f"LIMIT {limite} OFFSET {offset}"

            # Ejecutar consulta
            query = f"""
                SELECT * FROM usuarios 
                {where_clause}
                ORDER BY {orden}
                {limit_clause}
            """

            usuarios = UsuarioModel.query(query, parametros) if parametros else UsuarioModel.query(query)
            return [UsuarioModel(**usuario) for usuario in usuarios] if usuarios else []

        except Exception as e:
            logger.error(f"Error al obtener usuarios: {e}")
            return []

    def contar_usuarios(self, activos: bool = True) -> int:
        """
        Contar número de usuarios

        Args:
            activos: Si True, solo usuarios activos

        Returns:
            Número de usuarios
        """
        try:
            where_clause = "WHERE activo = 1" if activos else ""
            query = f"SELECT COUNT(*) as count FROM usuarios {where_clause}"
            resultado = UsuarioModel.query(query)
            return resultado[0]['count'] if resultado else 0
        except Exception as e:
            logger.error(f"Error al contar usuarios: {e}")
            return 0

    def contar_usuarios_por_rol(self, activos: bool = True) -> Dict[str, int]:
        """
        Contar usuarios por rol

        Args:
            activos: Si True, solo usuarios activos

        Returns:
            Diccionario con conteo por rol
        """
        try:
            where_clause = "WHERE activo = 1" if activos else ""
            query = f"""
                SELECT rol, COUNT(*) as count 
                FROM usuarios 
                {where_clause}
                GROUP BY rol
                ORDER BY count DESC
            """
            resultados = UsuarioModel.query(query)

            conteo = {}
            for row in resultados:
                conteo[row['rol']] = row['count']

            # Asegurar que todos los roles estén en el diccionario
            for rol in UsuarioModel.ROLES:
                if rol not in conteo:
                    conteo[rol] = 0

            return conteo

        except Exception as e:
            logger.error(f"Error al contar usuarios por rol: {e}")
            return {rol: 0 for rol in UsuarioModel.ROLES}

    # ==================== OPERACIONES ESPECÍFICAS ====================

    def cambiar_rol_usuario(self, usuario_id: int, nuevo_rol: str) -> Tuple[bool, str]:
        """
        Cambiar rol de un usuario

        Args:
            usuario_id: ID del usuario
            nuevo_rol: Nuevo rol

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            # Verificar permisos
            if not self.has_permission(UsuarioModel.ROL_ADMINISTRADOR):
                return False, "Solo administradores pueden cambiar roles de usuarios"

            usuario = UsuarioModel.get_by_id(usuario_id)
            if not usuario:
                return False, f"No se encontró usuario con ID {usuario_id}"

            # Cambiar rol
            return usuario.change_role(nuevo_rol, self._current_user)

        except Exception as e:
            logger.error(f"Error al cambiar rol del usuario {usuario_id}: {e}")
            return False, f"Error interno: {str(e)}"

    def toggle_activo_usuario(self, usuario_id: int) -> Tuple[bool, str]:
        """
        Activar/desactivar usuario

        Args:
            usuario_id: ID del usuario

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            # Verificar permisos
            if not self.has_permission(UsuarioModel.ROL_ADMINISTRADOR):
                return False, "Solo administradores pueden activar/desactivar usuarios"

            usuario = UsuarioModel.get_by_id(usuario_id)
            if not usuario:
                return False, f"No se encontró usuario con ID {usuario_id}"

            # Activar/desactivar
            return usuario.toggle_active(self._current_user)

        except Exception as e:
            logger.error(f"Error al activar/desactivar usuario {usuario_id}: {e}")
            return False, f"Error interno: {str(e)}"

    def reset_password_usuario(self, usuario_id: int, nueva_password: str = None) -> Tuple[bool, str, Optional[str]]:
        """
        Restablecer contraseña de un usuario

        Args:
            usuario_id: ID del usuario
            nueva_password: Nueva contraseña (si None, se genera una aleatoria)

        Returns:
            Tuple (éxito, mensaje, contraseña_generada)
        """
        try:
            # Verificar permisos
            if not self.has_permission(UsuarioModel.ROL_ADMINISTRADOR):
                return False, "Solo administradores pueden restablecer contraseñas", None

            usuario = UsuarioModel.get_by_id(usuario_id)
            if not usuario:
                return False, f"No se encontró usuario con ID {usuario_id}", None

            # Restablecer contraseña
            return usuario.reset_password(nueva_password)

        except Exception as e:
            logger.error(f"Error al restablecer contraseña del usuario {usuario_id}: {e}")
            return False, f"Error interno: {str(e)}", None

    def obtener_estadisticas_usuarios(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de usuarios

        Returns:
            Diccionario con estadísticas
        """
        try:
            # Contar usuarios activos
            usuarios_activos = self.contar_usuarios(activos=True)

            # Contar usuarios inactivos
            usuarios_inactivos = self.contar_usuarios(activos=False)

            # Total usuarios
            total_usuarios = usuarios_activos + usuarios_inactivos

            # Usuarios por rol
            usuarios_por_rol = self.contar_usuarios_por_rol(activos=True)

            # Últimos usuarios creados (últimos 30 días)
            fecha_limite = (datetime.now().replace(day=datetime.now().day - 30) 
                          if datetime.now().day > 30 else 
                          datetime.now().replace(month=datetime.now().month - 1, day=1))

            query = """
                SELECT COUNT(*) as count FROM usuarios 
                WHERE created_at >= ?
            """
            resultados = UsuarioModel.query(query, [fecha_limite.isoformat()])
            nuevos_ultimo_mes = resultados[0]['count'] if resultados else 0

            # Usuarios con login reciente (últimos 7 días)
            fecha_login_reciente = datetime.now().replace(day=datetime.now().day - 7)
            query = """
                SELECT COUNT(*) as count FROM usuarios 
                WHERE last_login >= ? AND activo = 1
            """
            resultados = UsuarioModel.query(query, [fecha_login_reciente.isoformat()])
            login_recientes = resultados[0]['count'] if resultados else 0

            return {
                'total_usuarios': total_usuarios,
                'usuarios_activos': usuarios_activos,
                'usuarios_inactivos': usuarios_inactivos,
                'porcentaje_activos': (usuarios_activos / total_usuarios * 100) if total_usuarios > 0 else 0,
                'usuarios_por_rol': usuarios_por_rol,
                'nuevos_ultimo_mes': nuevos_ultimo_mes,
                'login_recientes': login_recientes,
                'fecha_consulta': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            logger.error(f"Error al obtener estadísticas de usuarios: {e}")
            return {
                'total_usuarios': 0,
                'usuarios_activos': 0,
                'usuarios_inactivos': 0,
                'porcentaje_activos': 0,
                'usuarios_por_rol': {},
                'nuevos_ultimo_mes': 0,
                'login_recientes': 0,
                'fecha_consulta': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'error': str(e)
            }

    def inicializar_admin_default(self) -> Tuple[bool, str, Optional[UsuarioModel]]:
        """
        Inicializar administrador por defecto si no existe

        Returns:
            Tuple (éxito, mensaje, usuario)
        """
        try:
            admin = UsuarioModel.create_default_admin()
            if admin:
                mensaje = "Administrador por defecto creado exitosamente"
                return True, mensaje, admin
            else:
                return False, "Ya existe al menos un administrador en el sistema", None

        except Exception as e:
            logger.error(f"Error al inicializar administrador por defecto: {e}")
            return False, f"Error interno: {str(e)}", None

    def generar_reporte_usuarios(
        self, 
        formato: str = 'texto',
        incluir_inactivos: bool = False
    ) -> str:
        """
        Generar reporte de usuarios

        Args:
            formato: 'texto' o 'html'
            incluir_inactivos: Si True, incluir usuarios inactivos

        Returns:
            Reporte formateado
        """
        try:
            usuarios = self.obtener_usuarios(
                activos=not incluir_inactivos,  # Si queremos inactivos, activos=False
                limite=0  # Sin límite
            )

            if formato.lower() == 'html':
                return self._generar_reporte_html(usuarios, incluir_inactivos)
            else:
                return self._generar_reporte_texto(usuarios, incluir_inactivos)

        except Exception as e:
            logger.error(f"Error al generar reporte de usuarios: {e}")
            return f"Error al generar reporte: {str(e)}"

    def _generar_reporte_texto(
        self, 
        usuarios: List[UsuarioModel],
        incluir_inactivos: bool
    ) -> str:
        """Generar reporte en formato texto"""
        titulo = "REPORTE DE USUARIOS DEL SISTEMA"
        if incluir_inactivos:
            titulo += " (INCLUYE INACTIVOS)"

        reporte = []
        reporte.append("=" * 80)
        reporte.append(titulo.center(80))
        reporte.append("=" * 80)
        reporte.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        reporte.append(f"Total de usuarios: {len(usuarios)}")
        reporte.append("-" * 80)

        for i, usuario in enumerate(usuarios, 1):
            estado = "✅ Activo" if usuario.activo else "❌ Inactivo"
            reporte.append(f"{i:3d}. {usuario.nombre_completo}")
            reporte.append(f"     Usuario: {usuario.username}")
            reporte.append(f"     Email: {usuario.email or 'No especificado'}")
            reporte.append(f"     Rol: {usuario.rol}")
            reporte.append(f"     Estado: {estado}")
            if usuario.last_login:
                if isinstance(usuario.last_login, str):
                    last_login = usuario.last_login
                else:
                    last_login = usuario.last_login.strftime('%d/%m/%Y %H:%M')
                reporte.append(f"     Último login: {last_login}")
            reporte.append("")

        # Estadísticas
        reporte.append("-" * 80)
        reporte.append("ESTADÍSTICAS:")

        conteo_roles = {}
        for usuario in usuarios:
            if usuario.rol not in conteo_roles:
                conteo_roles[usuario.rol] = 0
            conteo_roles[usuario.rol] += 1

        for rol, cantidad in sorted(conteo_roles.items()):
            reporte.append(f"  {rol}: {cantidad} usuarios")

        reporte.append("=" * 80)

        return "\n".join(reporte)

    def _generar_reporte_html(
        self, 
        usuarios: List[UsuarioModel],
        incluir_inactivos: bool
    ) -> str:
        """Generar reporte en formato HTML"""
        titulo = "Reporte de Usuarios del Sistema"
        if incluir_inactivos:
            titulo += " (Incluye Inactivos)"

        # Conteo por rol
        conteo_roles = {}
        for usuario in usuarios:
            if usuario.rol not in conteo_roles:
                conteo_roles[usuario.rol] = 0
            conteo_roles[usuario.rol] += 1

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{titulo}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #9b59b6; padding-bottom: 10px; }}
                .header {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .usuario {{ border: 1px solid #ddd; padding: 15px; margin-bottom: 10px; border-radius: 5px; }}
                .usuario:nth-child(even) {{ background-color: #f9f9f9; }}
                .username {{ color: #3498db; font-weight: bold; }}
                .rol {{ color: #9b59b6; font-weight: bold; }}
                .activo {{ color: #27ae60; font-weight: bold; }}
                .inactivo {{ color: #e74c3c; font-weight: bold; }}
                .total {{ font-weight: bold; color: #2c3e50; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #34495e; color: white; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .estadisticas {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>{titulo}</h1>
            <div class="header">
                <p><strong>Fecha de generación:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                <p><strong>Total de usuarios:</strong> <span class="total">{len(usuarios)}</span></p>
            </div>
        """

        if usuarios:
            html += """
            <h2>Lista de Usuarios</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Nombre Completo</th>
                        <th>Usuario</th>
                        <th>Email</th>
                        <th>Rol</th>
                        <th>Estado</th>
                        <th>Último Login</th>
                    </tr>
                </thead>
                <tbody>
            """

            for i, usuario in enumerate(usuarios, 1):
                estado_clase = "activo" if usuario.activo else "inactivo"
                estado_texto = "Activo" if usuario.activo else "Inactivo"

                last_login = ""
                if usuario.last_login:
                    if isinstance(usuario.last_login, str):
                        last_login = usuario.last_login
                    else:
                        last_login = usuario.last_login.strftime('%d/%m/%Y %H:%M')

                html += f"""
                <tr>
                    <td>{i}</td>
                    <td>{usuario.nombre_completo}</td>
                    <td class="username">{usuario.username}</td>
                    <td>{usuario.email or '-'}</td>
                    <td><span class="rol">{usuario.rol}</span></td>
                    <td><span class="{estado_clase}">{estado_texto}</span></td>
                    <td>{last_login or '-'}</td>
                </tr>
                """

            html += """
                </tbody>
            </table>
            """
        else:
            html += "<p>No hay usuarios para mostrar.</p>"

        # Estadísticas
        if conteo_roles:
            html += """
            <div class="estadisticas">
                <h2>Estadísticas por Rol</h2>
            """

            for rol, cantidad in sorted(conteo_roles.items()):
                porcentaje = (cantidad / len(usuarios) * 100) if usuarios else 0
                html += f"""
                <p><strong>{rol}:</strong> {cantidad} usuarios ({porcentaje:.1f}%)</p>
                """

            html += "</div>"

        html += """
            <hr>
            <p><em>Generado por FormaGestPro_MVC - Módulo de Usuarios</em></p>
        </body>
        </html>
        """

        return html

    def exportar_usuarios_a_csv(
        self,
        incluir_inactivos: bool = False,
        archivo_salida: Optional[str] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Exportar usuarios a archivo CSV

        Args:
            incluir_inactivos: Si True, incluir usuarios inactivos
            archivo_salida: Ruta del archivo de salida

        Returns:
            Tuple (éxito, mensaje, ruta_archivo)
        """
        try:
            # Obtener usuarios
            usuarios = self.obtener_usuarios(
                activos=not incluir_inactivos,  # Si queremos inactivos, activos=False
                limite=0
            )

            if not usuarios:
                return False, "No hay usuarios para exportar", None

            # Generar nombre de archivo si no se proporciona
            if not archivo_salida:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                estado = "todos" if incluir_inactivos else "activos"
                archivo_salida = f"usuarios_{estado}_{timestamp}.csv"

            # Asegurar extensión .csv
            if not archivo_salida.lower().endswith('.csv'):
                archivo_salida += '.csv'

            # Crear directorio si no existe
            archivo_path = Path(archivo_salida)
            archivo_path.parent.mkdir(parents=True, exist_ok=True)

            # Escribir CSV
            with open(archivo_path, 'w', encoding='utf-8') as f:
                # Encabezados
                encabezados = [
                    'ID', 'Usuario', 'Nombre Completo', 'Email', 
                    'Rol', 'Activo', 'Fecha Creación', 'Último Login'
                ]
                f.write(';'.join(encabezados) + '\n')

                # Datos
                for usuario in usuarios:
                    # Formatear fechas
                    fecha_creacion = ""
                    if hasattr(usuario, 'created_at') and usuario.created_at:
                        if isinstance(usuario.created_at, str):
                            fecha_creacion = usuario.created_at
                        else:
                            fecha_creacion = usuario.created_at.strftime('%Y-%m-%d %H:%M:%S')

                    ultimo_login = ""
                    if usuario.last_login:
                        if isinstance(usuario.last_login, str):
                            ultimo_login = usuario.last_login
                        else:
                            ultimo_login = usuario.last_login.strftime('%Y-%m-%d %H:%M:%S')

                    fila = [
                        str(usuario.id),
                        usuario.username,
                        usuario.nombre_completo,
                        usuario.email or '',
                        usuario.rol,
                        'Sí' if usuario.activo else 'No',
                        fecha_creacion,
                        ultimo_login or ''
                    ]
                    f.write(';'.join(fila) + '\n')

            mensaje = f"Exportados {len(usuarios)} usuarios a {archivo_path}"
            return True, mensaje, str(archivo_path)

        except Exception as e:
            logger.error(f"Error al exportar usuarios a CSV: {e}")
            return False, f"Error al exportar: {str(e)}", None

    # ==================== VALIDACIONES ====================

    def _validar_datos_usuario(
        self, 
        datos: Dict[str, Any], 
        es_actualizacion: bool = False
    ) -> List[str]:
        """
        Validar datos del usuario

        Args:
            datos: Diccionario con datos a validar
            es_actualizacion: Si es una actualización (algunos campos son opcionales)

        Returns:
            Lista de mensajes de error
        """
        errores = []

        # Validar campos requeridos (solo para creación)
        if not es_actualizacion:
            campos_requeridos = ['username', 'nombre_completo']
            for campo in campos_requeridos:
                if campo not in datos or not str(datos.get(campo, '')).strip():
                    errores.append(f"El campo '{campo}' es requerido")

        # Validar username
        if 'username' in datos and datos['username']:
            valido, mensaje = UsuarioModel.validate_username(datos['username'])
            if not valido:
                errores.append(mensaje)

        # Validar contraseña (solo si se proporciona)
        if 'password' in datos and datos['password']:
            valido, mensaje = UsuarioModel.validate_password(datos['password'])
            if not valido:
                errores.append(mensaje)

        # Validar email si se proporciona
        if 'email' in datos and datos['email']:
            valido, mensaje = UsuarioModel.validate_email(datos['email'])
            if not valido:
                errores.append(mensaje)

        # Validar nombre completo si se proporciona
        if 'nombre_completo' in datos and datos['nombre_completo']:
            valido, mensaje = UsuarioModel.validate_nombre_completo(datos['nombre_completo'])
            if not valido:
                errores.append(mensaje)

        # Validar rol si se proporciona
        if 'rol' in datos and datos['rol']:
            if datos['rol'] not in UsuarioModel.ROLES:
                errores.append(f"Rol inválido. Roles válidos: {', '.join(UsuarioModel.ROLES)}")

        return errores