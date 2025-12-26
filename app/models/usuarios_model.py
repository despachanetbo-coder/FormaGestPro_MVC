# app/models/usuarios_model.py - Versión optimizada para escalabilidad multiusuario
import sys
import os
import hashlib
import secrets
import string
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple, Union

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_model import BaseModel


class UsuariosModel(BaseModel):
    def __init__(self):
        """Inicializa el modelo de usuarios con soporte para futura escalabilidad"""
        super().__init__()
        self.table_name = "usuarios"
        self.sequence_name = "seq_usuarios_id"

        # Tipos enumerados según la base de datos
        self.ROLES_USUARIO = [
            "ADMINISTRADOR",
            "COORDINADOR",
            "SECRETARIA",
            "DOCENTE",
            "ESTUDIANTE",
        ]

        # Parámetros de seguridad
        self.PASSWORD_MIN_LENGTH = 8
        self.SALT_LENGTH = 32
        self.HASH_ITERATIONS = 100000
        self.HASH_ALGORITHM = "sha256"

        # Columnas de la tabla para validación
        self.columns = [
            "id",
            "username",
            "password_hash",
            "nombre_completo",
            "email",
            "rol",
            "activo",
            "created_at",
            "last_login",
        ]

        # Columnas requeridas
        self.required_columns = ["username", "password_hash", "nombre_completo"]

        # Cache para sesiones (simulado para futura implementación distribuida)
        self._session_cache = {}

    # ============ MÉTODOS DE SEGURIDAD Y HASHING ============

    def _generate_salt(self) -> str:
        """
        Genera una sal criptográfica segura

        Returns:
            str: Sal generada
        """
        alphabet = string.ascii_letters + string.digits + string.punctuation
        return "".join(secrets.choice(alphabet) for _ in range(self.SALT_LENGTH))

    def _hash_password(
        self, password: str, salt: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Genera hash seguro de contraseña

        Args:
            password: Contraseña en texto plano
            salt: Sal opcional (si no se proporciona, se genera una nueva)

        Returns:
            Tuple[str, str]: (hash_generado, sal_usada)
        """
        if salt is None:
            salt = self._generate_salt()

        # Usar PBKDF2 para mayor seguridad
        encoded_password = password.encode("utf-8")
        encoded_salt = salt.encode("utf-8")

        hash_obj = hashlib.pbkdf2_hmac(
            self.HASH_ALGORITHM, encoded_password, encoded_salt, self.HASH_ITERATIONS
        )

        # Formato: algoritmo:iteraciones:salt:hash
        password_hash = (
            f"{self.HASH_ALGORITHM}:{self.HASH_ITERATIONS}:{salt}:{hash_obj.hex()}"
        )

        return password_hash, salt

    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """
        Verifica una contraseña contra su hash almacenado

        Args:
            password: Contraseña en texto plano a verificar
            stored_hash: Hash almacenado en la base de datos

        Returns:
            bool: True si la contraseña es correcta, False en caso contrario
        """
        try:
            # Parsear el hash almacenado
            parts = stored_hash.split(":")
            if len(parts) != 4:
                return False

            algorithm, iterations_str, salt, original_hash = parts

            # Verificar algoritmo
            if algorithm != self.HASH_ALGORITHM:
                return False

            iterations = int(iterations_str)

            # Calcular hash de la contraseña proporcionada
            encoded_password = password.encode("utf-8")
            encoded_salt = salt.encode("utf-8")

            hash_obj = hashlib.pbkdf2_hmac(
                algorithm, encoded_password, encoded_salt, iterations
            )

            computed_hash = hash_obj.hex()

            # Comparar hashes de manera segura (timing-safe)
            return secrets.compare_digest(computed_hash, original_hash)

        except (ValueError, IndexError):
            return False

    def _validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """
        Valida la fortaleza de una contraseña

        Args:
            password: Contraseña a validar

        Returns:
            Tuple[bool, str]: (es_válida, mensaje_error)
        """
        if len(password) < self.PASSWORD_MIN_LENGTH:
            return (
                False,
                f"La contraseña debe tener al menos {self.PASSWORD_MIN_LENGTH} caracteres",
            )

        # Verificar complejidad
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in string.punctuation for c in password)

        if not (has_upper and has_lower and has_digit):
            return False, "La contraseña debe contener mayúsculas, minúsculas y números"

        return True, "Contraseña válida"

    # ============ MÉTODOS DE VALIDACIÓN ============

    def _validate_usuario_data(
        self,
        data: Dict[str, Any],
        for_update: bool = False,
        include_password: bool = True,
    ) -> Tuple[bool, str]:
        """
        Valida los datos del usuario

        Args:
            data: Diccionario con datos del usuario
            for_update: Si es True, valida para actualización
            include_password: Si es True, valida la contraseña

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        # Campos requeridos para creación
        if not for_update:
            for field in self.required_columns:
                if field not in data or not data[field]:
                    return False, f"Campo requerido faltante: {field}"

        # Validar nombre de usuario único
        if "username" in data and data["username"]:
            existing_id = None
            if for_update and "id" in data:
                existing_id = data["id"]

            if self.username_exists(data["username"], exclude_id=existing_id):
                return (
                    False,
                    f"El nombre de usuario '{data['username']}' ya está en uso",
                )

        # Validar email único si se proporciona
        if "email" in data and data["email"]:
            existing_id = None
            if for_update and "id" in data:
                existing_id = data["id"]

            if self.email_exists(data["email"], exclude_id=existing_id):
                return False, f"El email '{data['email']}' ya está registrado"

            # Validar formato de email
            if not self._is_valid_email(data["email"]):
                return False, "Formato de email inválido"

        # Validar rol si se proporciona
        if "rol" in data and data["rol"]:
            if data["rol"] not in self.ROLES_USUARIO:
                return False, f"Rol inválido. Use: {', '.join(self.ROLES_USUARIO)}"

        # Validar contraseña si se incluye
        if include_password and "password" in data and data["password"]:
            is_valid, error_msg = self._validate_password_strength(data["password"])
            if not is_valid:
                return False, error_msg

        return True, "Datos válidos"

    def _is_valid_email(self, email: str) -> bool:
        """Valida formato de email usando regex similar al CHECK constraint de la BD"""
        import re

        pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        return bool(re.match(pattern, email, re.IGNORECASE))

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza los datos del usuario

        Args:
            data: Diccionario con datos crudos

        Returns:
            Dict[str, Any]: Datos sanitizados
        """
        sanitized = {}

        for key, value in data.items():
            if key in self.columns:
                # Sanitizar strings
                if isinstance(value, str):
                    sanitized[key] = value.strip()
                # Mantener otros tipos
                else:
                    sanitized[key] = value

        return sanitized

    # ============ MÉTODOS CRUD PRINCIPALES ============

    def create(self, data: Dict[str, Any]) -> Optional[int]:
        """
        Crea un nuevo usuario

        Args:
            data: Diccionario con datos del usuario

        Returns:
            Optional[int]: ID del usuario creado o None si hay error
        """
        # Sanitizar datos
        data = self._sanitize_data(data)

        # Separar contraseña para procesamiento especial
        password = data.pop("password", None) if "password" in data else None

        if not password:
            print("✗ Error: Se requiere contraseña para crear usuario")
            return None

        # Validar datos (incluyendo contraseña)
        is_valid, error_msg = self._validate_usuario_data(
            {**data, "password": password}, for_update=False, include_password=True
        )

        if not is_valid:
            print(f"✗ Error validando datos: {error_msg}")
            return None

        try:
            # Preparar datos para inserción
            insert_data = data.copy()

            # Hash de la contraseña
            password_hash, _ = self._hash_password(password)
            insert_data["password_hash"] = password_hash

            # Establecer valores por defecto
            defaults = {
                "rol": "COORDINADOR",
                "activo": True,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            for key, value in defaults.items():
                if key not in insert_data or insert_data[key] is None:
                    insert_data[key] = value

            # Insertar en base de datos
            result = self.insert(self.table_name, insert_data, returning="id")

            if result:
                print(f"✓ Usuario creado exitosamente con ID: {result}")
                return result

            return None

        except Exception as e:
            print(f"✗ Error creando usuario: {e}")
            return None

    def read(
        self, usuario_id: int, active_only: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene un usuario por su ID

        Args:
            usuario_id: ID del usuario
            active_only: Si es True, solo usuarios activos

        Returns:
            Optional[Dict]: Datos del usuario (sin password_hash) o None si no existe
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE id = %s"
            params = (usuario_id,)

            if active_only:
                query += " AND activo = TRUE"

            result = self.fetch_one(query, params)

            # Remover password_hash por seguridad
            if result and "password_hash" in result:
                del result["password_hash"]

            return result

        except Exception as e:
            print(f"✗ Error obteniendo usuario: {e}")
            return None

    def update(self, usuario_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un usuario existente

        Args:
            usuario_id: ID del usuario a actualizar
            data: Diccionario con datos a actualizar

        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        if not data:
            return False

        # Obtener datos actuales para validación
        usuario_actual = self.read(usuario_id, active_only=False)
        if not usuario_actual:
            return False

        # Combinar datos actuales con los nuevos para validación
        data_with_id = {**usuario_actual, **data}
        data_with_id["id"] = usuario_id

        # Sanitizar datos
        data = self._sanitize_data(data)

        # Manejar actualización de contraseña si está presente
        if "password" in data and data["password"]:
            # Validar nueva contraseña
            is_valid, error_msg = self._validate_usuario_data(
                {**data, "password": data["password"]},
                for_update=True,
                include_password=True,
            )

            if not is_valid:
                print(f"✗ Error validando nueva contraseña: {error_msg}")
                return False

            # Generar nuevo hash
            password_hash, _ = self._hash_password(data["password"])
            data["password_hash"] = password_hash
            del data["password"]  # Remover contraseña en texto plano

        # Validar otros datos (sin contraseña)
        is_valid, error_msg = self._validate_usuario_data(
            data_with_id, for_update=True, include_password=False
        )

        if not is_valid:
            print(f"✗ Error validando datos: {error_msg}")
            return False

        try:
            # Actualizar en base de datos
            result = self.update_table(self.table_name, data, "id = %s", (usuario_id,))

            if result:
                print(f"✓ Usuario {usuario_id} actualizado exitosamente")
                return True

            return False

        except Exception as e:
            print(f"✗ Error actualizando usuario: {e}")
            return False

    def delete(self, usuario_id: int, soft_delete: bool = True) -> bool:
        """
        Elimina un usuario

        Args:
            usuario_id: ID del usuario
            soft_delete: Si es True, marca como inactivo en lugar de eliminar físicamente

        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            # Prevenir eliminación del último administrador
            if self._is_last_admin(usuario_id):
                print("✗ No se puede eliminar el último usuario administrador")
                return False

            if soft_delete:
                # Soft delete: marcar como inactivo
                query = f"UPDATE {self.table_name} SET activo = FALSE WHERE id = %s"
                params = (usuario_id,)
            else:
                # Hard delete: eliminar físicamente
                query = f"DELETE FROM {self.table_name} WHERE id = %s"
                params = (usuario_id,)

            result = self.execute_query(query, params, commit=True)

            if result:
                delete_type = "desactivado" if soft_delete else "eliminado"
                print(f"✓ Usuario {usuario_id} {delete_type} exitosamente")

                # Limpiar cache de sesión si existe
                self._clear_user_sessions(usuario_id)

                return True

            return False

        except Exception as e:
            print(f"✗ Error eliminando usuario: {e}")
            return False

    # ============ MÉTODOS DE AUTENTICACIÓN Y SESIÓN ============

    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autentica un usuario

        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano

        Returns:
            Optional[Dict]: Datos del usuario autenticado (sin password_hash) o None
        """
        try:
            # Buscar usuario por username
            query = f"""
            SELECT * FROM {self.table_name} 
            WHERE username = %s AND activo = TRUE
            """

            usuario = self.fetch_one(query, (username,))

            if not usuario:
                print("✗ Usuario no encontrado o inactivo")
                return None

            # Verificar contraseña
            stored_hash = usuario.get("password_hash")
            if not stored_hash or not self._verify_password(password, stored_hash):
                print("✗ Contraseña incorrecta")
                return None

            # Actualizar último login
            self._update_last_login(usuario["id"])

            # Remover password_hash por seguridad
            del usuario["password_hash"]

            print(f"✓ Usuario {username} autenticado exitosamente")
            return usuario

        except Exception as e:
            print(f"✗ Error en autenticación: {e}")
            return None

    def _update_last_login(self, usuario_id: int) -> bool:
        """
        Actualiza la fecha del último login

        Args:
            usuario_id: ID del usuario

        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            query = f"""
            UPDATE {self.table_name} 
            SET last_login = %s 
            WHERE id = %s
            """

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result = self.execute_query(query, (current_time, usuario_id), commit=True)

            return result is not None

        except Exception as e:
            print(f"✗ Error actualizando último login: {e}")
            return False

    def change_password(
        self, usuario_id: int, current_password: str, new_password: str
    ) -> bool:
        """
        Cambia la contraseña de un usuario

        Args:
            usuario_id: ID del usuario
            current_password: Contraseña actual
            new_password: Nueva contraseña

        Returns:
            bool: True si se cambió correctamente
        """
        try:
            # Obtener usuario y verificar contraseña actual
            query = f"SELECT password_hash FROM {self.table_name} WHERE id = %s"
            usuario = self.fetch_one(query, (usuario_id,))

            if not usuario:
                return False

            stored_hash = usuario.get("password_hash")
            if not stored_hash or not self._verify_password(
                current_password, stored_hash
            ):
                print("✗ Contraseña actual incorrecta")
                return False

            # Validar nueva contraseña
            is_valid, error_msg = self._validate_password_strength(new_password)
            if not is_valid:
                print(f"✗ Error validando nueva contraseña: {error_msg}")
                return False

            # Generar nuevo hash
            password_hash, _ = self._hash_password(new_password)

            # Actualizar en base de datos
            update_query = f"""
            UPDATE {self.table_name} 
            SET password_hash = %s 
            WHERE id = %s
            """

            result = self.execute_query(
                update_query, (password_hash, usuario_id), commit=True
            )

            if result:
                print(f"✓ Contraseña del usuario {usuario_id} cambiada exitosamente")

                # Limpiar sesiones del usuario por seguridad
                self._clear_user_sessions(usuario_id)

                return True

            return False

        except Exception as e:
            print(f"✗ Error cambiando contraseña: {e}")
            return False

    def reset_password(
        self,
        usuario_id: int,
        new_password: str,
        require_current: bool = False,
        current_password: Optional[str] = None,
    ) -> bool:
        """
        Resetea la contraseña de un usuario (para administradores)

        Args:
            usuario_id: ID del usuario
            new_password: Nueva contraseña
            require_current: Si es True, requiere contraseña actual
            current_password: Contraseña actual (si require_current es True)

        Returns:
            bool: True si se reseteó correctamente
        """
        try:
            if require_current and current_password:
                return self.change_password(usuario_id, current_password, new_password)

            # Reset por administrador
            is_valid, error_msg = self._validate_password_strength(new_password)
            if not is_valid:
                print(f"✗ Error validando nueva contraseña: {error_msg}")
                return False

            password_hash, _ = self._hash_password(new_password)

            update_query = f"""
            UPDATE {self.table_name} 
            SET password_hash = %s 
            WHERE id = %s
            """

            result = self.execute_query(
                update_query, (password_hash, usuario_id), commit=True
            )

            if result:
                print(f"✓ Contraseña del usuario {usuario_id} reseteada exitosamente")

                # Limpiar sesiones del usuario por seguridad
                self._clear_user_sessions(usuario_id)

                return True

            return False

        except Exception as e:
            print(f"✗ Error reseteando contraseña: {e}")
            return False

    # ============ MÉTODOS DE CONSULTA AVANZADOS ============

    def get_all(
        self,
        rol: Optional[str] = None,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "nombre_completo",
        order_desc: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todos los usuarios

        Args:
            rol: Filtrar por rol específico
            active_only: Si es True, solo usuarios activos
            limit: Límite de registros
            offset: Desplazamiento para paginación
            order_by: Campo para ordenar
            order_desc: Si es True, orden descendente

        Returns:
            List[Dict]: Lista de usuarios (sin password_hash)
        """
        try:
            query = f"SELECT * FROM {self.table_name}"
            conditions = []
            params = []

            if rol is not None:
                conditions.append("rol = %s")
                params.append(rol)

            if active_only:
                conditions.append("activo = TRUE")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            # Ordenar
            order_dir = "DESC" if order_desc else "ASC"
            query += f" ORDER BY {order_by} {order_dir}"

            # Paginación
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            results = self.fetch_all(query, params)

            # Remover password_hash por seguridad
            for user in results:
                if "password_hash" in user:
                    del user["password_hash"]

            return results

        except Exception as e:
            print(f"✗ Error obteniendo usuarios: {e}")
            return []

    def get_by_rol(self, rol: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Obtiene usuarios por rol

        Args:
            rol: Rol a buscar
            active_only: Si es True, solo usuarios activos

        Returns:
            List[Dict]: Lista de usuarios con el rol especificado
        """
        return self.get_all(rol=rol, active_only=active_only)

    def search(
        self, search_term: str, active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Busca usuarios por término de búsqueda

        Args:
            search_term: Término a buscar
            active_only: Si es True, solo usuarios activos

        Returns:
            List[Dict]: Lista de usuarios que coinciden
        """
        try:
            query = f"""
            SELECT * FROM {self.table_name}
            WHERE (username ILIKE %s 
                   OR nombre_completo ILIKE %s 
                   OR email ILIKE %s)
            """

            params = [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"]

            if active_only:
                query += " AND activo = TRUE"

            query += " ORDER BY nombre_completo"

            results = self.fetch_all(query, params)

            # Remover password_hash por seguridad
            for user in results:
                if "password_hash" in user:
                    del user["password_hash"]

            return results

        except Exception as e:
            print(f"✗ Error buscando usuarios: {e}")
            return []

    # ============ MÉTODOS PARA GESTIÓN DE SESIONES ============

    def create_session(
        self, usuario_id: int, session_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Crea una nueva sesión para el usuario

        Args:
            usuario_id: ID del usuario
            session_data: Datos de la sesión

        Returns:
            Optional[str]: Token de sesión o None si hay error
        """
        try:
            # Generar token seguro
            session_token = secrets.token_urlsafe(64)

            # Almacenar en cache (en futura versión, usar Redis o DB)
            self._session_cache[session_token] = {
                "usuario_id": usuario_id,
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "data": session_data,
            }

            print(f"✓ Sesión creada para usuario {usuario_id}")
            return session_token

        except Exception as e:
            print(f"✗ Error creando sesión: {e}")
            return None

    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """
        Valida una sesión y devuelve los datos del usuario

        Args:
            session_token: Token de sesión

        Returns:
            Optional[Dict]: Datos del usuario o None si la sesión no es válida
        """
        try:
            if session_token not in self._session_cache:
                return None

            session = self._session_cache[session_token]

            # Actualizar última actividad
            session["last_activity"] = datetime.now().isoformat()

            # Obtener usuario
            usuario = self.read(session["usuario_id"])

            if not usuario:
                # Si el usuario no existe, limpiar sesión
                self._clear_session(session_token)
                return None

            return usuario

        except Exception as e:
            print(f"✗ Error validando sesión: {e}")
            return None

    def _clear_session(self, session_token: str) -> bool:
        """
        Limpia una sesión específica

        Args:
            session_token: Token de sesión

        Returns:
            bool: True si se limpió correctamente
        """
        try:
            if session_token in self._session_cache:
                del self._session_cache[session_token]
                return True
            return False

        except Exception as e:
            print(f"✗ Error limpiando sesión: {e}")
            return False

    def _clear_user_sessions(self, usuario_id: int) -> bool:
        """
        Limpia todas las sesiones de un usuario

        Args:
            usuario_id: ID del usuario

        Returns:
            bool: True si se limpiaron correctamente
        """
        try:
            tokens_to_remove = []

            for token, session in self._session_cache.items():
                if session["usuario_id"] == usuario_id:
                    tokens_to_remove.append(token)

            for token in tokens_to_remove:
                del self._session_cache[token]

            print(f"✓ Sesiones limpiadas para usuario {usuario_id}")
            return True

        except Exception as e:
            print(f"✗ Error limpiando sesiones del usuario: {e}")
            return False

    # ============ MÉTODOS PARA DASHBOARD ============

    def get_total_usuarios(
        self, rol: Optional[str] = None, active_only: bool = True
    ) -> int:
        """
        Obtiene el total de usuarios

        Args:
            rol: Filtrar por rol específico
            active_only: Si es True, solo usuarios activos

        Returns:
            int: Número total de usuarios
        """
        try:
            query = f"SELECT COUNT(*) as total FROM {self.table_name}"
            conditions = []
            params = []

            if rol is not None:
                conditions.append("rol = %s")
                params.append(rol)

            if active_only:
                conditions.append("activo = TRUE")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            result = self.fetch_one(query, params)
            return result["total"] if result else 0

        except Exception as e:
            print(f"✗ Error obteniendo total de usuarios: {e}")
            return 0

    def get_usuarios_por_rol(self) -> List[Dict[str, Any]]:
        """
        Obtiene distribución de usuarios por rol

        Returns:
            List[Dict]: Distribución por rol
        """
        try:
            query = """
            SELECT 
                rol,
                COUNT(*) as cantidad,
                COUNT(CASE WHEN activo = TRUE THEN 1 END) as activos,
                COUNT(CASE WHEN activo = FALSE THEN 1 END) as inactivos
            FROM usuarios
            GROUP BY rol
            ORDER BY cantidad DESC
            """

            return self.fetch_all(query)

        except Exception as e:
            print(f"✗ Error obteniendo usuarios por rol: {e}")
            return []

    def get_estadisticas_actividad(self, days: int = 30) -> Dict[str, Any]:
        """
        Obtiene estadísticas de actividad de usuarios

        Args:
            days: Número de días a considerar

        Returns:
            Dict: Estadísticas de actividad
        """
        try:
            query = """
            SELECT 
                COUNT(*) as total_usuarios,
                COUNT(CASE WHEN last_login >= CURRENT_DATE - INTERVAL '%s days' THEN 1 END) as activos_recientes,
                COUNT(CASE WHEN last_login IS NULL THEN 1 END) as nunca_han_iniciado,
                AVG(CASE WHEN last_login IS NOT NULL THEN EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - last_login)) / 86400 END) as inactividad_promedio_dias
            FROM usuarios
            WHERE activo = TRUE
            """

            result = self.fetch_one(query, (days,))

            if result:
                return {
                    "total_usuarios": result["total_usuarios"],
                    "activos_recientes": result["activos_recientes"],
                    "nunca_han_iniciado": result["nunca_han_iniciado"],
                    "inactividad_promedio_dias": round(
                        result["inactividad_promedio_dias"] or 0, 2
                    ),
                    "periodo_dias": days,
                }

            return {}

        except Exception as e:
            print(f"✗ Error obteniendo estadísticas de actividad: {e}")
            return {}

    # ============ MÉTODOS DE VALIDACIÓN DE UNICIDAD ============

    def username_exists(self, username: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si un nombre de usuario ya existe

        Args:
            username: Nombre de usuario a verificar
            exclude_id: ID a excluir (para actualizaciones)

        Returns:
            bool: True si existe, False en caso contrario
        """
        try:
            query = (
                f"SELECT COUNT(*) as count FROM {self.table_name} WHERE username = %s"
            )
            params = [username]

            if exclude_id is not None:
                query += " AND id != %s"
                params.append(exclude_id)  # type: ignore

            result = self.fetch_one(query, params)
            return result["count"] > 0 if result else False

        except Exception as e:
            print(f"✗ Error verificando nombre de usuario: {e}")
            return False

    def email_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si un email ya existe

        Args:
            email: Email a verificar
            exclude_id: ID a excluir (para actualizaciones)

        Returns:
            bool: True si existe, False en caso contrario
        """
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE email = %s"
            params = [email]

            if exclude_id is not None:
                query += " AND id != %s"
                params.append(exclude_id)  # type: ignore

            result = self.fetch_one(query, params)
            return result["count"] > 0 if result else False

        except Exception as e:
            print(f"✗ Error verificando email: {e}")
            return False

    def _is_last_admin(self, usuario_id: int) -> bool:
        """
        Verifica si el usuario es el último administrador activo

        Args:
            usuario_id: ID del usuario

        Returns:
            bool: True si es el último administrador, False en caso contrario
        """
        try:
            query = """
            SELECT COUNT(*) as count 
            FROM usuarios 
            WHERE rol = 'ADMINISTRADOR' 
              AND activo = TRUE 
              AND id != %s
            """

            result = self.fetch_one(query, (usuario_id,))
            return result["count"] == 0 if result else False

        except Exception as e:
            print(f"✗ Error verificando último administrador: {e}")
            return True  # Por seguridad, asumir que es el último

    # ============ MÉTODOS DE COMPATIBILIDAD ============

    def obtener_todos(self):
        """Método de compatibilidad con nombres antiguos"""
        return self.get_all()

    def obtener_por_id(self, usuario_id):
        """Método de compatibilidad con nombres antiguos"""
        return self.read(usuario_id)

    def autenticar(self, username, password):
        """Método de compatibilidad con nombres antiguos"""
        return self.authenticate(username, password)

    def update_table(self, table, data, condition, params=None):
        """Método helper para actualizar (compatibilidad con BaseModel)"""
        return self.update(table, data, condition, params)  # type: ignore

    # ============ MÉTODOS DE UTILIDAD ============

    def get_roles_usuario(self) -> List[str]:
        """
        Obtiene la lista de roles de usuario

        Returns:
            List[str]: Lista de roles
        """
        return self.ROLES_USUARIO.copy()

    def get_password_requirements(self) -> Dict[str, Any]:
        """
        Obtiene los requisitos de contraseña

        Returns:
            Dict: Requisitos de contraseña
        """
        return {
            "min_length": self.PASSWORD_MIN_LENGTH,
            "requires_uppercase": True,
            "requires_lowercase": True,
            "requires_digits": True,
            "requires_special": False,
            "recommended_length": 12,
        }

    def generar_password_aleatoria(self) -> str:
        """
        Genera una contraseña aleatoria segura

        Returns:
            str: Contraseña generada
        """
        import random

        # Definir conjuntos de caracteres
        uppercase = string.ascii_uppercase
        lowercase = string.ascii_lowercase
        digits = string.digits
        special = string.punctuation

        # Asegurar al menos un carácter de cada tipo
        password_chars = [
            random.choice(uppercase),
            random.choice(lowercase),
            random.choice(digits),
            random.choice(special),
        ]

        # Completar hasta longitud recomendada
        all_chars = uppercase + lowercase + digits + special
        remaining_length = max(0, 12 - len(password_chars))

        for _ in range(remaining_length):
            password_chars.append(random.choice(all_chars))

        # Mezclar aleatoriamente
        random.shuffle(password_chars)

        return "".join(password_chars)
