# app/utils/validators.py
"""
Sistema de validaciones para FormaGestPro_MVC

Responsabilidades:
- Validaciones de datos de entrada
- Validaciones de reglas de negocio
- Sanitización y normalización
- Validaciones específicas por modelo

Autor: FormaGestPro_MVC Team
Versión: 2.0.0
Última actualización: [Fecha actual]
"""

import re
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers import NumberParseException

from app.utils.exceptions import (
    ValidationException,
    BusinessRuleException,
    InvalidEmailException,
    InvalidPhoneException,
    InvalidDocumentException
)

logger = logging.getLogger(__name__)


class Validator:
    """Clase principal para validaciones del sistema"""
    
    # Constantes de validación
    CI_MIN_LENGTH = 5
    CI_MAX_LENGTH = 15
    NOMBRE_MAX_LENGTH = 100
    TELEFONO_MIN_LENGTH = 7
    TELEFONO_MAX_LENGTH = 15
    EMAIL_MAX_LENGTH = 254
    DESCRIPCION_MAX_LENGTH = 500
    OBSERVACIONES_MAX_LENGTH = 1000
    
    # Expresiones regulares
    PATTERN_ALPHANUMERIC = re.compile(r'^[a-zA-Z0-9\sáéíóúÁÉÍÓÚñÑ.,;:¿?¡!()\-"\']+$')
    PATTERN_NUMERIC = re.compile(r'^[0-9]+$')
    PATTERN_ALPHA = re.compile(r'^[a-zA-Z\sáéíóúÁÉÍÓÚñÑ]+$')
    PATTERN_CI = re.compile(r'^[0-9]+[A-Z]?$')
    PATTERN_NIT = re.compile(r'^[0-9]{7,15}$')
    PATTERN_CODIGO = re.compile(r'^[A-Z0-9\-_]+$')
    
    def __init__(self):
        """Inicializar validador"""
        self.errors = []
        self.warnings = []
    
    # ==================== VALIDACIONES GENERALES ====================
    
    def reset(self):
        """Reiniciar lista de errores y advertencias"""
        self.errors.clear()
        self.warnings.clear()
    
    def validate(self, data: Dict[str, Any], rules: Dict[str, List[Callable]]) -> bool:
        """
        Validar datos contra un conjunto de reglas
        
        Args:
            data: Diccionario de datos a validar
            rules: Diccionario de reglas por campo
        
        Returns:
            True si todos los datos son válidos
        """
        self.reset()
        
        for field, field_rules in rules.items():
            value = data.get(field)
            
            for rule in field_rules:
                try:
                    if not rule(value):
                        self.errors.append(f"Campo '{field}' no cumple la regla: {rule.__name__}")
                        break
                except Exception as e:
                    self.errors.append(f"Error validando campo '{field}': {str(e)}")
        
        return len(self.errors) == 0
    
    def get_errors(self) -> List[str]:
        """Obtener lista de errores"""
        return self.errors.copy()
    
    def get_warnings(self) -> List[str]:
        """Obtener lista de advertencias"""
        return self.warnings.copy()
    
    def raise_if_errors(self, custom_message: str = None):
        """Lanzar excepción si hay errores"""
        if self.errors:
            message = custom_message or "Errores de validación encontrados"
            raise ValidationException(f"{message}: {', '.join(self.errors)}")
    
    # ==================== VALIDACIONES DE DOCUMENTOS ====================
    
    def validate_ci(self, ci: str, expedicion: str = None) -> bool:
        """
        Validar número de Carnet de Identidad (CI)
        
        Args:
            ci: Número de CI
            expedicion: Expedición (opcional, ej: 'LP', 'SC')
        
        Returns:
            True si el CI es válido
        """
        if not ci:
            self.errors.append("El CI no puede estar vacío")
            return False
        
        # Validar formato básico
        if not self.PATTERN_CI.match(str(ci)):
            self.errors.append("Formato de CI inválido")
            return False
        
        # Validar longitud
        ci_str = str(ci)
        if len(ci_str) < self.CI_MIN_LENGTH or len(ci_str) > self.CI_MAX_LENGTH:
            self.errors.append(f"El CI debe tener entre {self.CI_MIN_LENGTH} y {self.CI_MAX_LENGTH} caracteres")
            return False
        
        # Validar expedición si se proporciona
        if expedicion:
            expediciones_validas = ['BE', 'CH', 'CB', 'LP', 'OR', 'PD', 'PT', 'SC', 'TJ', 'EX']
            if expedicion not in expediciones_validas:
                self.errors.append(f"Expedición '{expedicion}' no válida")
                return False
        
        return True
    
    def validate_nit(self, nit: str) -> bool:
        """
        Validar Número de Identificación Tributaria (NIT)
        
        Args:
            nit: Número de NIT
        
        Returns:
            True si el NIT es válido
        """
        if not nit:
            self.errors.append("El NIT no puede estar vacío")
            return False
        
        # Validar formato
        if not self.PATTERN_NIT.match(str(nit)):
            self.errors.append("Formato de NIT inválido")
            return False
        
        # Validar longitud
        nit_str = str(nit)
        if len(nit_str) < 7 or len(nit_str) > 15:
            self.errors.append("El NIT debe tener entre 7 y 15 dígitos")
            return False
        
        # Validar dígito verificador (algoritmo boliviano)
        if not self._validar_digito_verificador_nit(nit_str):
            self.warnings.append("El dígito verificador del NIT podría ser incorrecto")
            # No es un error fatal, solo advertencia
        
        return True
    
    def _validar_digito_verificador_nit(self, nit: str) -> bool:
        """
        Validar dígito verificador de NIT (algoritmo boliviano)
        
        Args:
            nit: Número de NIT completo
        
        Returns:
            True si el dígito verificador es correcto
        """
        try:
            if len(nit) < 2:
                return False
            
            # Separar número base y dígito verificador
            base = nit[:-1]
            digito_verificador = int(nit[-1])
            
            # Calcular dígito verificador esperado
            factores = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
            suma = 0
            
            for i, digito in enumerate(reversed(base)):
                factor = factores[i % len(factores)]
                suma += int(digito) * factor
            
            resto = suma % 11
            digito_calculado = 11 - resto if resto > 1 else 0
            
            return digito_verificador == digito_calculado
            
        except (ValueError, IndexError):
            return False
    
    # ==================== VALIDACIONES DE PERSONAS ====================
    
    def validate_nombre_completo(self, nombres: str, apellidos: str) -> bool:
        """
        Validar nombre completo
        
        Args:
            nombres: Nombres de la persona
            apellidos: Apellidos de la persona
        
        Returns:
            True si el nombre es válido
        """
        # Validar nombres
        if not nombres or not nombres.strip():
            self.errors.append("Los nombres no pueden estar vacíos")
            return False
        
        if len(nombres.strip()) > self.NOMBRE_MAX_LENGTH:
            self.errors.append(f"Los nombres no pueden exceder {self.NOMBRE_MAX_LENGTH} caracteres")
            return False
        
        if not self.PATTERN_ALPHA.match(nombres.strip()):
            self.errors.append("Los nombres solo pueden contener letras y espacios")
            return False
        
        # Validar apellidos
        if not apellidos or not apellidos.strip():
            self.errors.append("Los apellidos no pueden estar vacíos")
            return False
        
        if len(apellidos.strip()) > self.NOMBRE_MAX_LENGTH:
            self.errors.append(f"Los apellidos no pueden exceder {self.NOMBRE_MAX_LENGTH} caracteres")
            return False
        
        if not self.PATTERN_ALPHA.match(apellidos.strip()):
            self.errors.append("Los apellidos solo pueden contener letras y espacios")
            return False
        
        return True
    
    def validate_fecha_nacimiento(self, fecha_nacimiento: Union[str, date], edad_minima: int = 16) -> bool:
        """
        Validar fecha de nacimiento
        
        Args:
            fecha_nacimiento: Fecha de nacimiento
            edad_minima: Edad mínima permitida
        
        Returns:
            True si la fecha es válida
        """
        try:
            # Convertir a date si es string
            if isinstance(fecha_nacimiento, str):
                fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
            
            # Verificar que sea una fecha válida
            if not isinstance(fecha_nacimiento, date):
                self.errors.append("Fecha de nacimiento inválida")
                return False
            
            # Verificar que no sea futura
            hoy = date.today()
            if fecha_nacimiento > hoy:
                self.errors.append("La fecha de nacimiento no puede ser futura")
                return False
            
            # Verificar edad mínima
            edad = self.calcular_edad(fecha_nacimiento)
            if edad < edad_minima:
                self.errors.append(f"La edad mínima permitida es {edad_minima} años")
                return False
            
            # Verificar edad máxima razonable (120 años)
            if edad > 120:
                self.errors.append("Edad no válida")
                return False
            
            return True
            
        except ValueError:
            self.errors.append("Formato de fecha inválido. Use YYYY-MM-DD")
            return False
        except Exception as e:
            self.errors.append(f"Error validando fecha de nacimiento: {str(e)}")
            return False
    
    def calcular_edad(self, fecha_nacimiento: date) -> int:
        """
        Calcular edad a partir de fecha de nacimiento
        
        Args:
            fecha_nacimiento: Fecha de nacimiento
        
        Returns:
            Edad en años
        """
        hoy = date.today()
        edad = hoy.year - fecha_nacimiento.year
        
        # Ajustar si aún no ha cumplido años este año
        if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
            edad -= 1
        
        return edad
    
    # ==================== VALIDACIONES DE CONTACTO ====================
    
    def validate_email(self, email: str, requerido: bool = False) -> bool:
        """
        Validar dirección de email
        
        Args:
            email: Dirección de email a validar
            requerido: Si el email es requerido
        
        Returns:
            True si el email es válido
        """
        if not email and not requerido:
            return True
        
        if not email and requerido:
            self.errors.append("El email es requerido")
            return False
        
        email = email.strip()
        
        # Validar longitud
        if len(email) > self.EMAIL_MAX_LENGTH:
            self.errors.append(f"El email no puede exceder {self.EMAIL_MAX_LENGTH} caracteres")
            return False
        
        try:
            # Usar email-validator para validación robusta
            email_info = validate_email(email, check_deliverability=False)
            # Normalizar email
            normalized_email = email_info.normalized
            
            # Validaciones adicionales
            if not self._validar_dominio_email(normalized_email):
                self.warnings.append("El dominio del email podría no ser válido")
            
            return True
            
        except EmailNotValidError as e:
            self.errors.append(f"Email inválido: {str(e)}")
            return False
    
    def _validar_dominio_email(self, email: str) -> bool:
        """
        Validar dominio de email común
        
        Args:
            email: Email a validar
        
        Returns:
            True si el dominio parece válido
        """
        dominios_comunes = [
            'gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com',
            'live.com', 'icloud.com', 'protonmail.com',
            'gob.bo', 'edu.bo', 'com.bo', 'net.bo', 'org.bo'
        ]
        
        try:
            dominio = email.split('@')[1].lower()
            # Verificar si el dominio está en la lista de comunes
            # o si tiene estructura válida
            if dominio in dominios_comunes:
                return True
            
            # Verificar estructura básica de dominio
            if '.' in dominio and len(dominio.split('.')[-1]) >= 2:
                return True
            
            return False
            
        except (IndexError, AttributeError):
            return False
    
    def validate_telefono(self, telefono: str, pais: str = 'BO', requerido: bool = False) -> bool:
        """
        Validar número de teléfono
        
        Args:
            telefono: Número de teléfono
            pais: Código de país (por defecto 'BO' para Bolivia)
            requerido: Si el teléfono es requerido
        
        Returns:
            True si el teléfono es válido
        """
        if not telefono and not requerido:
            return True
        
        if not telefono and requerido:
            self.errors.append("El teléfono es requerido")
            return False
        
        telefono = telefono.strip()
        
        # Validar longitud básica
        if len(telefono) < self.TELEFONO_MIN_LENGTH or len(telefono) > self.TELEFONO_MAX_LENGTH:
            self.errors.append(f"El teléfono debe tener entre {self.TELEFONO_MIN_LENGTH} y {self.TELEFONO_MAX_LENGTH} dígitos")
            return False
        
        # Validar que solo contenga números y caracteres permitidos
        if not re.match(r'^[0-9+\-\s()]+$', telefono):
            self.errors.append("El teléfono solo puede contener números, espacios, +, - y paréntesis")
            return False
        
        try:
            # Usar phonenumbers para validación internacional
            parsed_number = phonenumbers.parse(telefono, pais)
            
            if not phonenumbers.is_valid_number(parsed_number):
                self.errors.append("Número de teléfono inválido")
                return False
            
            # Verificar tipo de número (móvil, fijo, etc.)
            number_type = phonenumbers.number_type(parsed_number)
            
            # Para Bolivia, aceptar móviles y fijos
            if pais == 'BO':
                tipos_validos = [
                    phonenumbers.PhoneNumberType.MOBILE,
                    phonenumbers.PhoneNumberType.FIXED_LINE,
                    phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE
                ]
                
                if number_type not in tipos_validos:
                    self.warnings.append("El número podría no ser móvil ni fijo boliviano")
            
            return True
            
        except NumberParseException as e:
            self.errors.append(f"Número de teléfono inválido: {str(e)}")
            return False
        except Exception as e:
            logger.warning(f"Error validando teléfono {telefono}: {e}")
            # Si hay error con phonenumbers, hacer validación básica
            if re.match(r'^[0-9]{7,10}$', telefono.replace(' ', '')):
                return True
            self.errors.append("Formato de teléfono inválido para Bolivia")
            return False
    
    # ==================== VALIDACIONES ACADÉMICAS ====================
    
    def validate_codigo_programa(self, codigo: str) -> bool:
        """
        Validar código de programa académico
        
        Args:
            codigo: Código del programa
        
        Returns:
            True si el código es válido
        """
        if not codigo or not codigo.strip():
            self.errors.append("El código del programa no puede estar vacío")
            return False
        
        codigo = codigo.strip().upper()
        
        # Validar longitud
        if len(codigo) < 3 or len(codigo) > 20:
            self.errors.append("El código debe tener entre 3 y 20 caracteres")
            return False
        
        # Validar formato
        if not self.PATTERN_CODIGO.match(codigo):
            self.errors.append("El código solo puede contener letras mayúsculas, números, guiones y guiones bajos")
            return False
        
        return True
    
    def validate_duracion_semanas(self, semanas: int) -> bool:
        """
        Validar duración en semanas
        
        Args:
            semanas: Número de semanas
        
        Returns:
            True si la duración es válida
        """
        if not isinstance(semanas, int):
            self.errors.append("La duración debe ser un número entero")
            return False
        
        if semanas < 1:
            self.errors.append("La duración mínima es 1 semana")
            return False
        
        if semanas > 104:  # Máximo 2 años
            self.errors.append("La duración máxima es 104 semanas (2 años)")
            return False
        
        return True
    
    def validate_cupos(self, cupos_totales: int, cupos_disponibles: int = None) -> bool:
        """
        Validar cupos de programa
        
        Args:
            cupos_totales: Total de cupos
            cupos_disponibles: Cupos disponibles (opcional)
        
        Returns:
            True si los cupos son válidos
        """
        if not isinstance(cupos_totales, int):
            self.errors.append("El total de cupos debe ser un número entero")
            return False
        
        if cupos_totales < 1:
            self.errors.append("El total de cupos debe ser al menos 1")
            return False
        
        if cupos_totales > 1000:  # Límite razonable
            self.errors.append("El total de cupos no puede exceder 1000")
            return False
        
        # Validar cupos disponibles si se proporcionan
        if cupos_disponibles is not None:
            if not isinstance(cupos_disponibles, int):
                self.errors.append("Los cupos disponibles deben ser un número entero")
                return False
            
            if cupos_disponibles < 0:
                self.errors.append("Los cupos disponibles no pueden ser negativos")
                return False
            
            if cupos_disponibles > cupos_totales:
                self.errors.append("Los cupos disponibles no pueden ser mayores al total")
                return False
        
        return True
    
    # ==================== VALIDACIONES FINANCIERAS ====================
    
    def validate_monto(self, monto: Any, minimo: Decimal = None, maximo: Decimal = None) -> bool:
        """
        Validar monto monetario
        
        Args:
            monto: Monto a validar
            minimo: Valor mínimo permitido
            maximo: Valor máximo permitido
        
        Returns:
            True si el monto es válido
        """
        try:
            # Convertir a Decimal
            if isinstance(monto, (int, float)):
                monto_decimal = Decimal(str(monto))
            elif isinstance(monto, Decimal):
                monto_decimal = monto
            elif isinstance(monto, str):
                monto_decimal = Decimal(monto.strip())
            else:
                self.errors.append("El monto debe ser un número")
                return False
            
            # Validar que sea positivo
            if monto_decimal < Decimal('0'):
                self.errors.append("El monto no puede ser negativo")
                return False
            
            # Validar mínimo
            if minimo is not None and monto_decimal < minimo:
                self.errors.append(f"El monto mínimo permitido es {minimo}")
                return False
            
            # Validar máximo
            if maximo is not None and monto_decimal > maximo:
                self.errors.append(f"El monto máximo permitido es {maximo}")
                return False
            
            # Validar decimales (máximo 2 decimales)
            if abs(monto_decimal.as_tuple().exponent) > 2:
                self.errors.append("El monto no puede tener más de 2 decimales")
                return False
            
            return True
            
        except InvalidOperation:
            self.errors.append("Formato de monto inválido")
            return False
        except Exception as e:
            self.errors.append(f"Error validando monto: {str(e)}")
            return False
    
    def validate_descuento(self, descuento: Any, maximo: Decimal = Decimal('100')) -> bool:
        """
        Validar porcentaje de descuento
        
        Args:
            descuento: Porcentaje de descuento
            maximo: Porcentaje máximo permitido
        
        Returns:
            True si el descuento es válido
        """
        try:
            # Convertir a Decimal
            if isinstance(descuento, (int, float)):
                descuento_decimal = Decimal(str(descuento))
            elif isinstance(descuento, Decimal):
                descuento_decimal = descuento
            elif isinstance(descuento, str):
                descuento_decimal = Decimal(descuento.strip())
            else:
                self.errors.append("El descuento debe ser un número")
                return False
            
            # Validar rango
            if descuento_decimal < Decimal('0'):
                self.errors.append("El descuento no puede ser negativo")
                return False
            
            if descuento_decimal > maximo:
                self.errors.append(f"El descuento máximo permitido es {maximo}%")
                return False
            
            # Validar decimales (máximo 2 decimales)
            if abs(descuento_decimal.as_tuple().exponent) > 2:
                self.errors.append("El descuento no puede tener más de 2 decimales")
                return False
            
            return True
            
        except InvalidOperation:
            self.errors.append("Formato de descuento inválido")
            return False
    
    def validate_cuotas(self, nro_cuotas: int, intervalo_dias: int) -> bool:
        """
        Validar estructura de cuotas
        
        Args:
            nro_cuotas: Número de cuotas
            intervalo_dias: Días entre cuotas
        
        Returns:
            True si la estructura es válida
        """
        # Validar número de cuotas
        if not isinstance(nro_cuotas, int):
            self.errors.append("El número de cuotas debe ser un entero")
            return False
        
        if nro_cuotas < 1:
            self.errors.append("El número mínimo de cuotas es 1")
            return False
        
        if nro_cuotas > 36:  # Máximo 3 años si es mensual
            self.errors.append("El número máximo de cuotas es 36")
            return False
        
        # Validar intervalo de días
        if not isinstance(intervalo_dias, int):
            self.errors.append("El intervalo de días debe ser un entero")
            return False
        
        if intervalo_dias < 7 and nro_cuotas > 1:
            self.errors.append("El intervalo mínimo entre cuotas es 7 días")
            return False
        
        if intervalo_dias > 365:
            self.errors.append("El intervalo máximo entre cuotas es 365 días")
            return False
        
        # Validar periodo total
        periodo_total = (nro_cuotas - 1) * intervalo_dias
        if periodo_total > 730:  # Máximo 2 años
            self.errors.append("El periodo total de pago no puede exceder 2 años")
            return False
        
        return True
    
    # ==================== VALIDACIONES DE FECHAS ====================
    
    def validate_fecha(self, fecha: Any, formato: str = '%Y-%m-%d', 
                      min_date: date = None, max_date: date = None) -> bool:
        """
        Validar fecha
        
        Args:
            fecha: Fecha a validar
            formato: Formato esperado (si es string)
            min_date: Fecha mínima permitida
            max_date: Fecha máxima permitida
        
        Returns:
            True si la fecha es válida
        """
        try:
            # Convertir a date según el tipo
            if isinstance(fecha, str):
                fecha_date = datetime.strptime(fecha.strip(), formato).date()
            elif isinstance(fecha, datetime):
                fecha_date = fecha.date()
            elif isinstance(fecha, date):
                fecha_date = fecha
            else:
                self.errors.append("Formato de fecha inválido")
                return False
            
            # Validar fecha mínima
            if min_date and fecha_date < min_date:
                self.errors.append(f"La fecha no puede ser anterior a {min_date}")
                return False
            
            # Validar fecha máxima
            if max_date and fecha_date > max_date:
                self.errors.append(f"La fecha no puede ser posterior a {max_date}")
                return False
            
            return True
            
        except ValueError:
            self.errors.append(f"Formato de fecha inválido. Use {formato}")
            return False
        except Exception as e:
            self.errors.append(f"Error validando fecha: {str(e)}")
            return False
    
    def validate_fecha_promocion(self, fecha_limite: date, fecha_inicio: date = None) -> bool:
        """
        Validar fecha límite de promoción
        
        Args:
            fecha_limite: Fecha límite de la promoción
            fecha_inicio: Fecha de inicio (opcional, por defecto hoy)
        
        Returns:
            True si la fecha es válida
        """
        fecha_inicio = fecha_inicio or date.today()
        
        if not self.validate_fecha(fecha_limite):
            return False
        
        fecha_limite_date = fecha_limite if isinstance(fecha_limite, date) else \
                           datetime.strptime(fecha_limite, '%Y-%m-%d').date()
        
        # La fecha límite debe ser futura
        if fecha_limite_date <= fecha_inicio:
            self.errors.append("La fecha límite de promoción debe ser futura")
            return False
        
        # La fecha límite no puede ser muy lejana (max 1 año)
        max_fecha = fecha_inicio + timedelta(days=365)
        if fecha_limite_date > max_fecha:
            self.errors.append("La fecha límite de promoción no puede exceder 1 año")
            return False
        
        return True
    
    # ==================== VALIDACIONES DE MATRÍCULA ====================
    
    def validate_matricula_data(self, data: Dict[str, Any]) -> bool:
        """
        Validar datos completos de matrícula
        
        Args:
            data: Datos de la matrícula
        
        Returns:
            True si todos los datos son válidos
        """
        self.reset()
        
        # Validar campos requeridos
        campos_requeridos = ['estudiante_id', 'programa_id', 'modalidad_pago']
        for campo in campos_requeridos:
            if campo not in data or data[campo] is None:
                self.errors.append(f"El campo '{campo}' es requerido")
        
        if self.errors:
            return False
        
        # Validar estudiante_id
        if not isinstance(data['estudiante_id'], int) or data['estudiante_id'] <= 0:
            self.errors.append("El ID de estudiante debe ser un número positivo")
        
        # Validar programa_id
        if not isinstance(data['programa_id'], int) or data['programa_id'] <= 0:
            self.errors.append("El ID de programa debe ser un número positivo")
        
        # Validar modalidad de pago
        modalidades_validas = ['CONTADO', 'CUOTAS']
        if data['modalidad_pago'] not in modalidades_validas:
            self.errors.append(f"Modalidad de pago inválida. Válidas: {', '.join(modalidades_validas)}")
        
        # Validar montos
        montos_a_validar = ['monto_total', 'monto_final', 'monto_pagado', 'descuento_aplicado']
        for monto_field in montos_a_validar:
            if monto_field in data and data[monto_field] is not None:
                if not self.validate_monto(data[monto_field]):
                    # El error ya está en self.errors
                    pass
        
        # Validar estados
        if 'estado_pago' in data and data['estado_pago']:
            estados_pago_validos = ['PENDIENTE', 'PARCIAL', 'PAGADO', 'MORA']
            if data['estado_pago'] not in estados_pago_validos:
                self.errors.append(f"Estado de pago inválido. Válidos: {', '.join(estados_pago_validos)}")
        
        if 'estado_academico' in data and data['estado_academico']:
            estados_academicos_validos = ['PREINSCRITO', 'INSCRITO', 'EN_CURSO', 'CONCLUIDO', 'RETIRADO']
            if data['estado_academico'] not in estados_academicos_validos:
                self.errors.append(f"Estado académico inválido. Válidos: {', '.join(estados_academicos_validos)}")
        
        # Validar fechas
        if 'fecha_inicio' in data and data['fecha_inicio']:
            if not self.validate_fecha(data['fecha_inicio']):
                # El error ya está en self.errors
                pass
        
        # Validar relación entre montos
        if all(field in data for field in ['monto_total', 'descuento_aplicado', 'monto_final']):
            try:
                total = Decimal(str(data['monto_total']))
                descuento = Decimal(str(data['descuento_aplicado']))
                final = Decimal(str(data['monto_final']))
                
                if total - descuento != final:
                    self.errors.append("El monto final no coincide con (total - descuento)")
            except (ValueError, InvalidOperation):
                pass
        
        return len(self.errors) == 0
    
    # ==================== VALIDACIONES DE PAGO ====================
    
    def validate_pago_data(self, data: Dict[str, Any]) -> bool:
        """
        Validar datos de pago
        
        Args:
            data: Datos del pago
        
        Returns:
            True si todos los datos son válidos
        """
        self.reset()
        
        # Validar campos requeridos
        campos_requeridos = ['matricula_id', 'monto', 'forma_pago']
        for campo in campos_requeridos:
            if campo not in data or data[campo] is None:
                self.errors.append(f"El campo '{campo}' es requerido")
        
        if self.errors:
            return False
        
        # Validar matricula_id
        if not isinstance(data['matricula_id'], int) or data['matricula_id'] <= 0:
            self.errors.append("El ID de matrícula debe ser un número positivo")
        
        # Validar monto
        if not self.validate_monto(data['monto'], minimo=Decimal('0.01')):
            # El error ya está en self.errors
            pass
        
        # Validar forma de pago
        formas_pago_validas = ['EFECTIVO', 'TRANSFERENCIA', 'TARJETA', 'CHEQUE', 'DEPOSITO', 'PAGOS_QR']
        if data['forma_pago'] not in formas_pago_validas:
            self.errors.append(f"Forma de pago inválida. Válidas: {', '.join(formas_pago_validas)}")
        
        # Validar número de cuota si existe
        if 'nro_cuota' in data and data['nro_cuota'] is not None:
            if not isinstance(data['nro_cuota'], int) or data['nro_cuota'] <= 0:
                self.errors.append("El número de cuota debe ser un número positivo")
        
        # Validar fecha de pago
        if 'fecha_pago' in data and data['fecha_pago']:
            if not self.validate_fecha(data['fecha_pago']):
                # El error ya está en self.errors
                pass
        
        return len(self.errors) == 0
    
    # ==================== MÉTODOS DE UTILIDAD ====================
    
    def sanitize_string(self, texto: str, max_length: int = None, 
                       allow_html: bool = False) -> str:
        """
        Sanitizar cadena de texto
        
        Args:
            texto: Texto a sanitizar
            max_length: Longitud máxima (truncar si es necesario)
            allow_html: Permitir HTML (por defecto False)
        
        Returns:
            Texto sanitizado
        """
        if not texto:
            return ""
        
        texto = texto.strip()
        
        # Eliminar caracteres de control
        texto = ''.join(char for char in texto if ord(char) >= 32 or char in '\n\r\t')
        
        # Eliminar HTML si no está permitido
        if not allow_html:
            texto = re.sub(r'<[^>]+>', '', texto)
        
        # Truncar si es necesario
        if max_length and len(texto) > max_length:
            texto = texto[:max_length].rstrip()
        
        return texto
    
    def normalize_ci(self, ci: str) -> str:
        """
        Normalizar número de CI (eliminar espacios, puntos, guiones)
        
        Args:
            ci: Número de CI
        
        Returns:
            CI normalizado
        """
        if not ci:
            return ""
        
        # Eliminar espacios, puntos, guiones
        ci_normalizado = re.sub(r'[\s.\-]', '', str(ci))
        
        # Convertir a mayúsculas
        ci_normalizado = ci_normalizado.upper()
        
        return ci_normalizado
    
    def normalize_telefono(self, telefono: str, pais: str = 'BO') -> str:
        """
        Normalizar número de teléfono
        
        Args:
            telefono: Número de teléfono
            pais: Código de país
        
        Returns:
            Teléfono normalizado
        """
        if not telefono:
            return ""
        
        # Eliminar espacios y caracteres especiales
        telefono_limpio = re.sub(r'[\s+\-()]', '', str(telefono))
        
        # Agregar código de país si no lo tiene
        if pais == 'BO' and not telefono_limpio.startswith('591'):
            # Asumir que es número boliviano sin código de país
            if telefono_limpio.startswith('0'):
                telefono_limpio = '591' + telefono_limpio[1:]
            elif len(telefono_limpio) == 8:  # Número local
                telefono_limpio = '591' + telefono_limpio
        
        return telefono_limpio
    
    # ==================== VALIDACIONES RÁPIDAS (STATIC METHODS) ====================
    
    @staticmethod
    def es_numero_positivo(valor: Any) -> bool:
        """Verificar si es un número positivo"""
        try:
            num = float(valor)
            return num > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def es_entero_positivo(valor: Any) -> bool:
        """Verificar si es un entero positivo"""
        try:
            num = int(valor)
            return num > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def es_porcentaje_valido(valor: Any) -> bool:
        """Verificar si es un porcentaje válido (0-100)"""
        try:
            num = float(valor)
            return 0 <= num <= 100
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def es_fecha_valida(fecha_str: str, formato: str = '%Y-%m-%d') -> bool:
        """Verificar si una cadena es una fecha válida"""
        try:
            datetime.strptime(fecha_str, formato)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def es_email_valido(email: str) -> bool:
        """Verificar formato básico de email"""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None