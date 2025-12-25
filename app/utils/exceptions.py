# app/utils/exceptions.py
"""
Excepciones personalizadas para FormaGestPro_MVC

Autor: FormaGestPro_MVC Team
Versión: 2.0.0
Última actualización: [Fecha actual]
"""

class FormaGestProException(Exception):
    """Excepción base para todas las excepciones personalizadas"""
    def __init__(self, message: str, code: str = None):
        super().__init__(message)
        self.message = message
        self.code = code or "ERROR_GENERICO"
    
    def to_dict(self) -> dict:
        """Convertir excepción a diccionario para respuestas API"""
        return {
            'error': True,
            'code': self.code,
            'message': self.message
        }


class ValidationException(FormaGestProException):
    """Excepción para errores de validación"""
    def __init__(self, message: str, errors: list = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.errors = errors or []


class BusinessRuleException(FormaGestProException):
    """Excepción para violaciones de reglas de negocio"""
    def __init__(self, message: str):
        super().__init__(message, "BUSINESS_RULE_VIOLATION")


class NotFoundException(FormaGestProException):
    """Excepción para recursos no encontrados"""
    def __init__(self, message: str):
        super().__init__(message, "RESOURCE_NOT_FOUND")


class DatabaseException(FormaGestProException):
    """Excepción para errores de base de datos"""
    def __init__(self, message: str):
        super().__init__(message, "DATABASE_ERROR")


class InvalidEmailException(ValidationException):
    """Excepción para emails inválidos"""
    def __init__(self, message: str = "Email inválido"):
        super().__init__(message)


class InvalidPhoneException(ValidationException):
    """Excepción para teléfonos inválidos"""
    def __init__(self, message: str = "Teléfono inválido"):
        super().__init__(message)


class InvalidDocumentException(ValidationException):
    """Excepción para documentos inválidos (CI, NIT)"""
    def __init__(self, message: str = "Documento inválido"):
        super().__init__(message)


class AuthenticationException(FormaGestProException):
    """Excepción para errores de autenticación"""
    def __init__(self, message: str = "Error de autenticación"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationException(FormaGestProException):
    """Excepción para errores de autorización"""
    def __init__(self, message: str = "No autorizado"):
        super().__init__(message, "AUTHORIZATION_ERROR")


class ConfigurationException(FormaGestProException):
    """Excepción para errores de configuración"""
    def __init__(self, message: str = "Error de configuración"):
        super().__init__(message, "CONFIGURATION_ERROR")


class ExternalServiceException(FormaGestProException):
    """Excepción para errores de servicios externos"""
    def __init__(self, message: str = "Error en servicio externo"):
        super().__init__(message, "EXTERNAL_SERVICE_ERROR")