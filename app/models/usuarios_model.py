# app/models/usuarios_model.py
"""
Modelo para la tabla de usuarios del sistema en FormaGestPro_MVC
"""

import hashlib
import secrets
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import re

from .base_model import BaseModel

class UsuarioModel(BaseModel):
    """Modelo para usuarios del sistema"""
    TABLE_NAME = "usuarios"

    # Roles disponibles
    ROL_ADMINISTRADOR = 'ADMINISTRADOR'
    ROL_COORDINADOR = 'COORDINADOR'
    ROL_CAJERO = 'CAJERO'

    ROLES = [ROL_ADMINISTRADOR, ROL_COORDINADOR, ROL_CAJERO]

    # Niveles de permisos (mayor número = más permisos)
    PERMISOS = {
        ROL_ADMINISTRADOR: 100,  # Acceso total
        ROL_COORDINADOR: 75,     # Acceso casi total, excepto configuraciones críticas
        ROL_CAJERO: 50           # Acceso limitado a módulos financieros
    }

    def __init__(self, **kwargs):
        super().__init__()
        self.id = kwargs.get('id')
        self.username = kwargs.get('username', '')
        self.password_hash = kwargs.get('password_hash', '')
        self.nombre_completo = kwargs.get('nombre_completo', '')
        self.email = kwargs.get('email')
        self.rol = kwargs.get('rol', self.ROL_COORDINADOR)
        self.activo = kwargs.get('activo', 1)
        self.created_at = kwargs.get('created_at')
        self.last_login = kwargs.get('last_login')

        # Campos temporales (no se guardan en BD)
        self._plain_password = None

    @classmethod
    def get_by_username(cls, username: str) -> Optional['UsuarioModel']:
        """Obtener usuario por nombre de usuario"""
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE username = ?"
        results = cls.query(query, [username])
        if results:
            return cls(**results[0])
        return None

    @classmethod
    def get_by_email(cls, email: str) -> Optional['UsuarioModel']:
        """Obtener usuario por email"""
        if not email:
            return None
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE email = ?"
        results = cls.query(query, [email])
        if results:
            return cls(**results[0])
        return None

    @classmethod
    def get_active_users(cls) -> List['UsuarioModel']:
        """Obtener todos los usuarios activos"""
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE activo = 1 ORDER BY nombre_completo"
        results = cls.query(query)
        return [cls(**row) for row in results] if results else []

    @classmethod
    def get_all_users(cls, include_inactive: bool = False) -> List['UsuarioModel']:
        """Obtener todos los usuarios"""
        query = f"SELECT * FROM {cls.TABLE_NAME}"
        if not include_inactive:
            query += " WHERE activo = 1"
        query += " ORDER BY nombre_completo"

        results = cls.query(query)
        return [cls(**row) for row in results] if results else []

    @classmethod
    def get_users_by_role(cls, rol: str, include_inactive: bool = False) -> List['UsuarioModel']:
        """Obtener usuarios por rol"""
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE rol = ?"
        if not include_inactive:
            query += " AND activo = 1"
        query += " ORDER BY nombre_completo"

        results = cls.query(query, [rol])
        return [cls(**row) for row in results] if results else []

    @classmethod
    def authenticate(cls, username: str, password: str) -> Optional['UsuarioModel']:
        """
        Autenticar usuario con nombre de usuario y contraseña

        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano

        Returns:
            UsuarioModel si autenticación exitosa, None si falla
        """
        usuario = cls.get_by_username(username)
        if not usuario:
            return None

        if not usuario.activo:
            return None

        if usuario.verify_password(password):
            return usuario

        return None

    @classmethod
    def hash_password(cls, password: str) -> str:
        """
        Hashear contraseña usando PBKDF2 con salt

        Args:
            password: Contraseña en texto plano

        Returns:
            Hash de la contraseña en formato: salt:hash
        """
        # Generar salt aleatorio
        salt = secrets.token_hex(16)

        # Hashear contraseña con salt
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # Número de iteraciones
        )

        # Formato: salt:hash_hex
        return f"{salt}:{hash_obj.hex()}"

    @classmethod
    def generate_random_password(cls, length: int = 12) -> str:
        """
        Generar contraseña aleatoria segura

        Args:
            length: Longitud de la contraseña

        Returns:
            Contraseña aleatoria
        """
        import random
        import string

        # Caracteres disponibles
        letters = string.ascii_letters
        digits = string.digits
        special = '!@#$%^&*()_+-=[]{}|;:,.<>?'

        # Asegurar al menos un carácter de cada tipo
        password = [
            random.choice(letters.upper()),  # Mayúscula
            random.choice(letters.lower()),  # Minúscula
            random.choice(digits),           # Dígito
            random.choice(special)           # Especial
        ]

        # Completar con caracteres aleatorios
        all_chars = letters + digits + special
        password += [random.choice(all_chars) for _ in range(length - 4)]

        # Mezclar caracteres
        random.shuffle(password)

        return ''.join(password)

    def verify_password(self, password: str) -> bool:
        """
        Verificar si una contraseña coincide con el hash almacenado

        Args:
            password: Contraseña en texto plano a verificar

        Returns:
            True si la contraseña es correcta, False en caso contrario
        """
        if not self.password_hash or ':' not in self.password_hash:
            return False

        # Extraer salt y hash almacenado
        salt, stored_hash = self.password_hash.split(':', 1)

        # Hashear la contraseña proporcionada con el mismo salt
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )

        # Comparar hashes
        return hash_obj.hex() == stored_hash

    def set_password(self, password: str) -> None:
        """
        Establecer nueva contraseña para el usuario

        Args:
            password: Nueva contraseña en texto plano
        """
        self._plain_password = password
        self.password_hash = self.hash_password(password)

    def update_last_login(self) -> None:
        """Actualizar timestamp del último login"""
        self.last_login = datetime.now()
        self.save()

    def has_permission(self, required_role: str) -> bool:
        """
        Verificar si el usuario tiene permisos suficientes

        Args:
            required_role: Rol mínimo requerido

        Returns:
            True si el usuario tiene permisos suficientes
        """
        if required_role not in self.PERMISOS:
            return False

        user_level = self.PERMISOS.get(self.rol, 0)
        required_level = self.PERMISOS.get(required_role, 0)

        return user_level >= required_level

    def can_access_module(self, module: str) -> bool:
        """
        Verificar si el usuario puede acceder a un módulo específico

        Args:
            module: Nombre del módulo

        Returns:
            True si el usuario puede acceder al módulo
        """
        # Definir permisos por módulo
        module_permissions = {
            'dashboard': [self.ROL_ADMINISTRADOR, self.ROL_COORDINADOR, self.ROL_CAJERO],
            'estudiantes': [self.ROL_ADMINISTRADOR, self.ROL_COORDINADOR],
            'docentes': [self.ROL_ADMINISTRADOR, self.ROL_COORDINADOR],
            'programas': [self.ROL_ADMINISTRADOR, self.ROL_COORDINADOR],
            'matriculas': [self.ROL_ADMINISTRADOR, self.ROL_COORDINADOR],
            'pagos': [self.ROL_ADMINISTRADOR, self.ROL_COORDINADOR, self.ROL_CAJERO],
            'gastos': [self.ROL_ADMINISTRADOR, self.ROL_COORDINADOR, self.ROL_CAJERO],
            'ingresos': [self.ROL_ADMINISTRADOR, self.ROL_COORDINADOR, self.ROL_CAJERO],
            'reportes': [self.ROL_ADMINISTRADOR, self.ROL_COORDINADOR],
            'configuracion': [self.ROL_ADMINISTRADOR],
            'usuarios': [self.ROL_ADMINISTRADOR]
        }

        return module in module_permissions and self.rol in module_permissions[module]

    def to_dict(self, include_password: bool = False) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        data = {
            'id': self.id,
            'username': self.username,
            'nombre_completo': self.nombre_completo,
            'email': self.email,
            'rol': self.rol,
            'activo': bool(self.activo),
            'created_at': self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else str(self.created_at),
            'last_login': self.last_login.isoformat() if hasattr(self.last_login, 'isoformat') else str(self.last_login),
            'permisos_nivel': self.PERMISOS.get(self.rol, 0)
        }

        if include_password and self._plain_password:
            data['password'] = self._plain_password

        return data

    @classmethod
    def validate_username(cls, username: str) -> Tuple[bool, str]:
        """
        Validar nombre de usuario

        Args:
            username: Nombre de usuario a validar

        Returns:
            Tuple (válido, mensaje_error)
        """
        if not username or not username.strip():
            return False, "El nombre de usuario no puede estar vacío"

        if len(username) < 3:
            return False, "El nombre de usuario debe tener al menos 3 caracteres"

        if len(username) > 50:
            return False, "El nombre de usuario no puede exceder 50 caracteres"

        # Solo letras, números, guiones bajos y puntos
        if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
            return False, "El nombre de usuario solo puede contener letras, números, guiones bajos, puntos y guiones"

        return True, ""

    @classmethod
    def validate_password(cls, password: str) -> Tuple[bool, str]:
        """
        Validar contraseña según políticas de seguridad

        Args:
            password: Contraseña a validar

        Returns:
            Tuple (válido, mensaje_error)
        """
        if not password:
            return False, "La contraseña no puede estar vacía"

        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"

        if len(password) > 100:
            return False, "La contraseña no puede exceder 100 caracteres"

        # Verificar complejidad
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)

        if not (has_upper and has_lower and has_digit):
            return False, "La contraseña debe contener al menos una letra mayúscula, una minúscula y un número"

        return True, ""

    @classmethod
    def validate_email(cls, email: str) -> Tuple[bool, str]:
        """
        Validar dirección de email

        Args:
            email: Email a validar

        Returns:
            Tuple (válido, mensaje_error)
        """
        if not email:
            return True, ""  # Email es opcional

        if len(email) > 100:
            return False, "El email no puede exceder 100 caracteres"

        # Expresión regular básica para validar email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return False, "Formato de email inválido"

        return True, ""

    @classmethod
    def validate_nombre_completo(cls, nombre: str) -> Tuple[bool, str]:
        """
        Validar nombre completo

        Args:
            nombre: Nombre completo a validar

        Returns:
            Tuple (válido, mensaje_error)
        """
        if not nombre or not nombre.strip():
            return False, "El nombre completo no puede estar vacío"

        if len(nombre) < 2:
            return False, "El nombre completo debe tener al menos 2 caracteres"

        if len(nombre) > 100:
            return False, "El nombre completo no puede exceder 100 caracteres"

        return True, ""

    def change_role(self, new_role: str, current_user: Optional['UsuarioModel'] = None) -> Tuple[bool, str]:
        """
        Cambiar rol del usuario

        Args:
            new_role: Nuevo rol
            current_user: Usuario que realiza el cambio (para verificar permisos)

        Returns:
            Tuple (éxito, mensaje)
        """
        if new_role not in self.ROLES:
            return False, f"Rol inválido. Roles válidos: {', '.join(self.ROLES)}"

        # Verificar permisos si se proporciona current_user
        if current_user:
            if not current_user.has_permission(self.ROL_ADMINISTRADOR):
                return False, "Solo administradores pueden cambiar roles de usuarios"

            # Administrador no puede quitarse su propio rol de administrador
            if self.id == current_user.id and new_role != self.ROL_ADMINISTRADOR:
                return False, "No puedes quitarte tu propio rol de administrador"

        self.rol = new_role
        if self.save():
            return True, f"Rol cambiado exitosamente a {new_role}"
        else:
            return False, "Error al guardar el cambio de rol"

    def toggle_active(self, current_user: Optional['UsuarioModel'] = None) -> Tuple[bool, str]:
        """
        Activar/desactivar usuario

        Args:
            current_user: Usuario que realiza el cambio (para verificar permisos)

        Returns:
            Tuple (éxito, mensaje)
        """
        # Verificar permisos si se proporciona current_user
        if current_user:
            if not current_user.has_permission(self.ROL_ADMINISTRADOR):
                return False, "Solo administradores pueden activar/desactivar usuarios"

            # Administrador no puede desactivarse a sí mismo
            if self.id == current_user.id:
                return False, "No puedes desactivar tu propia cuenta"

        self.activo = 0 if self.activo else 1
        estado = "activada" if self.activo else "desactivada"

        if self.save():
            return True, f"Cuenta {estado} exitosamente"
        else:
            return False, f"Error al {estado} la cuenta"

    def reset_password(self, new_password: str = None) -> Tuple[bool, str, Optional[str]]:
        """
        Restablecer contraseña del usuario

        Args:
            new_password: Nueva contraseña (si None, se genera una aleatoria)

        Returns:
            Tuple (éxito, mensaje, contraseña_generada)
        """
        if new_password:
            # Validar nueva contraseña
            valido, mensaje = self.validate_password(new_password)
            if not valido:
                return False, mensaje, None
            password_generated = new_password
        else:
            # Generar contraseña aleatoria
            password_generated = self.generate_random_password()

        # Establecer nueva contraseña
        self.set_password(password_generated)

        if self.save():
            return True, "Contraseña restablecida exitosamente", password_generated
        else:
            return False, "Error al guardar la nueva contraseña", None

    @classmethod
    def create_default_admin(cls) -> Optional['UsuarioModel']:
        """
        Crear usuario administrador por defecto si no existe ninguno

        Returns:
            UsuarioModel creado o None si ya existe
        """
        # Verificar si ya existe un administrador
        admins = cls.get_users_by_role(cls.ROL_ADMINISTRADOR)
        if admins:
            return None

        # Crear administrador por defecto
        admin = cls(
            username='admin',
            nombre_completo='Administrador del Sistema',
            email='admin@formagestpro.edu.bo',
            rol=cls.ROL_ADMINISTRADOR
        )

        # Contraseña por defecto (debe ser cambiada en primer login)
        admin.set_password('Admin123')

        if admin.save():
            return admin

        return None