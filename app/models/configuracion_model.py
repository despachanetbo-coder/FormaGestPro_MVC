# app/models/configuracion_model.py
"""
Modelo para la tabla de configuraciones del sistema en FormaGestPro_MVC
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
import json

from .base_model import BaseModel

class ConfiguracionModel(BaseModel):
    """Modelo para configuraciones del sistema"""
    TABLE_NAME = "configuraciones"
    
    # Constantes para tipos de valor
    TIPO_STRING = 'string'
    TIPO_INTEGER = 'integer'
    TIPO_FLOAT = 'float'
    TIPO_BOOLEAN = 'boolean'
    TIPO_JSON = 'json'
    TIPO_LIST = 'list'
    
    # Grupos de configuración
    GRUPO_EMPRESA = 'EMPRESA'
    GRUPO_SISTEMA = 'SISTEMA'
    GRUPO_ACADEMICO = 'ACADEMICO'
    GRUPO_NOTIFICACION = 'NOTIFICACION'
    GRUPO_SEGURIDAD = 'SEGURIDAD'
    GRUPO_BACKUP = 'BACKUP'
    GRUPO_REPORTE = 'REPORTE'
    GRUPO_OTROS = 'OTROS'
    
    # Configuraciones predeterminadas del sistema
    CONFIGURACIONES_PREDEFINIDAS = {
        # Grupo EMPRESA
        'EMPRESA_NOMBRE': {
            'valor': 'FormaGestPro Academy',
            'descripcion': 'Nombre de la institución educativa',
            'grupo': GRUPO_EMPRESA,
            'tipo': TIPO_STRING,
            'editable': True
        },
        'EMPRESA_DIRECCION': {
            'valor': 'Av. Principal #123, Ciudad',
            'descripcion': 'Dirección física de la institución',
            'grupo': GRUPO_EMPRESA,
            'tipo': TIPO_STRING,
            'editable': True
        },
        'EMPRESA_TELEFONO': {
            'valor': '+591 77712345',
            'descripcion': 'Teléfono de contacto principal',
            'grupo': GRUPO_EMPRESA,
            'tipo': TIPO_STRING,
            'editable': True
        },
        'EMPRESA_EMAIL': {
            'valor': 'info@formagestpro.edu.bo',
            'descripcion': 'Correo electrónico institucional',
            'grupo': GRUPO_EMPRESA,
            'tipo': TIPO_STRING,
            'editable': True
        },
        'EMPRESA_LOGO_PATH': {
            'valor': '',
            'descripcion': 'Ruta del archivo del logo institucional',
            'grupo': GRUPO_EMPRESA,
            'tipo': TIPO_STRING,
            'editable': True
        },
        'EMPRESA_NIT': {
            'valor': '',
            'descripcion': 'Número de Identificación Tributaria',
            'grupo': GRUPO_EMPRESA,
            'tipo': TIPO_STRING,
            'editable': True
        },
        
        # Grupo SISTEMA
        'SISTEMA_MONEDA': {
            'valor': 'Bs.',
            'descripcion': 'Símbolo de la moneda local',
            'grupo': GRUPO_SISTEMA,
            'tipo': TIPO_STRING,
            'editable': True
        },
        'SISTEMA_PAIS': {
            'valor': 'Bolivia',
            'descripcion': 'País donde opera el sistema',
            'grupo': GRUPO_SISTEMA,
            'tipo': TIPO_STRING,
            'editable': True
        },
        'SISTEMA_IDIOMA': {
            'valor': 'es',
            'descripcion': 'Idioma del sistema (es=Español, en=Inglés)',
            'grupo': GRUPO_SISTEMA,
            'tipo': TIPO_STRING,
            'editable': True
        },
        'SISTEMA_ZONA_HORARIA': {
            'valor': 'America/La_Paz',
            'descripcion': 'Zona horaria del sistema',
            'grupo': GRUPO_SISTEMA,
            'tipo': TIPO_STRING,
            'editable': True
        },
        'SISTEMA_FORMATO_FECHA': {
            'valor': 'DD/MM/YYYY',
            'descripcion': 'Formato de fecha por defecto',
            'grupo': GRUPO_SISTEMA,
            'tipo': TIPO_STRING,
            'editable': True
        },
        'SISTEMA_FORMATO_HORA': {
            'valor': 'HH:MM',
            'descripcion': 'Formato de hora por defecto',
            'grupo': GRUPO_SISTEMA,
            'tipo': TIPO_STRING,
            'editable': True
        },
        'SISTEMA_PAGINACION_LIMITE': {
            'valor': '25',
            'descripcion': 'Número de registros por página por defecto',
            'grupo': GRUPO_SISTEMA,
            'tipo': TIPO_INTEGER,
            'editable': True
        },
        
        # Grupo ACADEMICO
        'ACADEMICO_CUOTA_DEFAULT': {
            'valor': '1500.00',
            'descripcion': 'Valor por defecto de las cuotas (Bs.)',
            'grupo': GRUPO_ACADEMICO,
            'tipo': TIPO_FLOAT,
            'editable': True
        },
        'ACADEMICO_HONORARIO_DEFAULT': {
            'valor': '50.00',
            'descripcion': 'Honorario por hora por defecto para docentes (Bs.)',
            'grupo': GRUPO_ACADEMICO,
            'tipo': TIPO_FLOAT,
            'editable': True
        },
        'ACADEMICO_DIAS_MAX_PAGO': {
            'valor': '30',
            'descripcion': 'Días máximos para realizar pagos sin recargo',
            'grupo': GRUPO_ACADEMICO,
            'tipo': TIPO_INTEGER,
            'editable': True
        },
        'ACADEMICO_TASA_MORA': {
            'valor': '0.5',
            'descripcion': 'Tasa de mora por día de retraso (%)',
            'grupo': GRUPO_ACADEMICO,
            'tipo': TIPO_FLOAT,
            'editable': True
        },
        'ACADEMICO_DESCUENTO_PRONTIPAGO': {
            'valor': '5.0',
            'descripcion': 'Descuento por pronto pago (%)',
            'grupo': GRUPO_ACADEMICO,
            'tipo': TIPO_FLOAT,
            'editable': True
        },
        
        # Grupo NOTIFICACION
        'NOTIFICACION_EMAIL_ENABLED': {
            'valor': '0',
            'descripcion': 'Habilitar notificaciones por email (0=No, 1=Sí)',
            'grupo': GRUPO_NOTIFICACION,
            'tipo': TIPO_BOOLEAN,
            'editable': True
        },
        'NOTIFICACION_EMAIL_SERVER': {
            'valor': 'smtp.gmail.com',
            'descripcion': 'Servidor SMTP para envío de emails',
            'grupo': GRUPO_NOTIFICACION,
            'tipo': TIPO_STRING,
            'editable': True
        },
        'NOTIFICACION_EMAIL_PORT': {
            'valor': '587',
            'descripcion': 'Puerto del servidor SMTP',
            'grupo': GRUPO_NOTIFICACION,
            'tipo': TIPO_INTEGER,
            'editable': True
        },
        'NOTIFICACION_EMAIL_USER': {
            'valor': '',
            'descripcion': 'Usuario para autenticación SMTP',
            'grupo': GRUPO_NOTIFICACION,
            'tipo': TIPO_STRING,
            'editable': True
        },
        'NOTIFICACION_EMAIL_PASSWORD': {
            'valor': '',
            'descripcion': 'Contraseña para autenticación SMTP',
            'grupo': GRUPO_NOTIFICACION,
            'tipo': TIPO_STRING,
            'editable': True,
            'secreto': True
        },
        'NOTIFICACION_EMAIL_FROM': {
            'valor': 'no-reply@formagestpro.edu.bo',
            'descripcion': 'Email remitente por defecto',
            'grupo': GRUPO_NOTIFICACION,
            'tipo': TIPO_STRING,
            'editable': True
        },
        
        # Grupo SEGURIDAD
        'SEGURIDAD_INTENTOS_LOGIN': {
            'valor': '3',
            'descripcion': 'Intentos máximos de login fallidos antes de bloqueo',
            'grupo': GRUPO_SEGURIDAD,
            'tipo': TIPO_INTEGER,
            'editable': True
        },
        'SEGURIDAD_TIEMPO_BLOQUEO': {
            'valor': '30',
            'descripcion': 'Tiempo de bloqueo en minutos después de intentos fallidos',
            'grupo': GRUPO_SEGURIDAD,
            'tipo': TIPO_INTEGER,
            'editable': True
        },
        'SEGURIDAD_PASSWORD_MIN_LENGTH': {
            'valor': '8',
            'descripcion': 'Longitud mínima de contraseñas de usuario',
            'grupo': GRUPO_SEGURIDAD,
            'tipo': TIPO_INTEGER,
            'editable': True
        },
        'SEGURIDAD_SESSION_TIMEOUT': {
            'valor': '60',
            'descripcion': 'Tiempo de expiración de sesión en minutos',
            'grupo': GRUPO_SEGURIDAD,
            'tipo': TIPO_INTEGER,
            'editable': True
        },
        
        # Grupo BACKUP
        'BACKUP_AUTO_ENABLED': {
            'valor': '1',
            'descripcion': 'Backup automático habilitado (0=No, 1=Sí)',
            'grupo': GRUPO_BACKUP,
            'tipo': TIPO_BOOLEAN,
            'editable': True
        },
        'BACKUP_AUTO_HORA': {
            'valor': '02:00',
            'descripcion': 'Hora para ejecución de backup automático (HH:MM)',
            'grupo': GRUPO_BACKUP,
            'tipo': TIPO_STRING,
            'editable': True
        },
        'BACKUP_AUTO_FRECUENCIA': {
            'valor': 'diario',
            'descripcion': 'Frecuencia de backup (diario, semanal, mensual)',
            'grupo': GRUPO_BACKUP,
            'tipo': TIPO_STRING,
            'editable': True
        },
        'BACKUP_RETENCION_DIAS': {
            'valor': '30',
            'descripcion': 'Días de retención de backups automáticos',
            'grupo': GRUPO_BACKUP,
            'tipo': TIPO_INTEGER,
            'editable': True
        },
        
        # Grupo REPORTE
        'REPORTE_FOOTER_TEXT': {
            'valor': 'FormaGestPro - Sistema de Gestión Académica',
            'descripcion': 'Texto del pie de página en reportes',
            'grupo': GRUPO_REPORTE,
            'tipo': TIPO_STRING,
            'editable': True
        },
        'REPORTE_HEADER_IMAGE': {
            'valor': '',
            'descripcion': 'Ruta de la imagen del encabezado en reportes',
            'grupo': GRUPO_REPORTE,
            'tipo': TIPO_STRING,
            'editable': True
        },
        'REPORTE_WATERMARK': {
            'valor': 'CONFIDENCIAL',
            'descripcion': 'Texto de marca de agua en reportes',
            'grupo': GRUPO_REPORTE,
            'tipo': TIPO_STRING,
            'editable': True
        },
        'REPORTE_MARGEN_SUPERIOR': {
            'valor': '20',
            'descripcion': 'Margen superior en milímetros',
            'grupo': GRUPO_REPORTE,
            'tipo': TIPO_INTEGER,
            'editable': True
        },
        'REPORTE_MARGEN_INFERIOR': {
            'valor': '15',
            'descripcion': 'Margen inferior en milímetros',
            'grupo': GRUPO_REPORTE,
            'tipo': TIPO_INTEGER,
            'editable': True
        },
        
        # Grupo OTROS
        'SISTEMA_VERSION': {
            'valor': '2.0.0',
            'descripcion': 'Versión del sistema FormaGestPro',
            'grupo': GRUPO_OTROS,
            'tipo': TIPO_STRING,
            'editable': False
        },
        'SISTEMA_ULTIMA_ACTUALIZACION': {
            'valor': '',
            'descripcion': 'Fecha de última actualización del sistema',
            'grupo': GRUPO_OTROS,
            'tipo': TIPO_STRING,
            'editable': False
        }
    }
    
    def __init__(self, **kwargs):
        super().__init__()
        self.id = kwargs.get('id')
        self.clave = kwargs.get('clave', '')
        self.valor = kwargs.get('valor', '')
        self.descripcion = kwargs.get('descripcion', '')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
        
        # Campos adicionales no en la tabla pero útiles para la aplicación
        self.grupo = kwargs.get('grupo', self._inferir_grupo())
        self.tipo = kwargs.get('tipo', self.TIPO_STRING)
        self.editable = kwargs.get('editable', True)
        self.secreto = kwargs.get('secreto', False)
    
    def _inferir_grupo(self) -> str:
        """Inferir grupo basado en la clave"""
        if not self.clave:
            return self.GRUPO_OTROS
        
        if self.clave.startswith('EMPRESA_'):
            return self.GRUPO_EMPRESA
        elif self.clave.startswith('SISTEMA_'):
            return self.GRUPO_SISTEMA
        elif self.clave.startswith('ACADEMICO_'):
            return self.GRUPO_ACADEMICO
        elif self.clave.startswith('NOTIFICACION_'):
            return self.GRUPO_NOTIFICACION
        elif self.clave.startswith('SEGURIDAD_'):
            return self.GRUPO_SEGURIDAD
        elif self.clave.startswith('BACKUP_'):
            return self.GRUPO_BACKUP
        elif self.clave.startswith('REPORTE_'):
            return self.GRUPO_REPORTE
        else:
            return self.GRUPO_OTROS
    
    @classmethod
    def get_by_key(cls, clave: str) -> Optional['ConfiguracionModel']:
        """Obtener configuración por clave"""
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE clave = ?"
        results = cls.query(query, [clave])
        if results:
            return cls(**results[0])
        return None
    
    @classmethod
    def get_by_group(cls, grupo: str) -> List['ConfiguracionModel']:
        """Obtener configuraciones por grupo"""
        # Nota: El grupo no está en la tabla, lo inferimos
        todas = cls.get_all()
        return [config for config in todas if config.grupo == grupo]
    
    @classmethod
    def get_all(cls) -> List['ConfiguracionModel']:
        """Obtener todas las configuraciones"""
        query = f"SELECT * FROM {cls.TABLE_NAME} ORDER BY clave"
        results = cls.query(query)
        return [cls(**row) for row in results] if results else []
    
    @classmethod
    def get_by_prefix(cls, prefijo: str) -> List['ConfiguracionModel']:
        """Obtener configuraciones por prefijo de clave"""
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE clave LIKE ? ORDER BY clave"
        results = cls.query(query, [f"{prefijo}%"])
        return [cls(**row) for row in results] if results else []
    
    @classmethod
    def get_predefined_keys(cls) -> List[str]:
        """Obtener lista de claves predefinidas"""
        return list(cls.CONFIGURACIONES_PREDEFINIDAS.keys())
    
    @classmethod
    def is_predefined(cls, clave: str) -> bool:
        """Verificar si una clave es predefinida"""
        return clave in cls.CONFIGURACIONES_PREDEFINIDAS
    
    @classmethod
    def get_predefined_config(cls, clave: str) -> Optional[Dict[str, Any]]:
        """Obtener configuración predefinida por clave"""
        return cls.CONFIGURACIONES_PREDEFINIDAS.get(clave)
    
    def save(self) -> Optional[int]:
        """Guardar configuración con timestamp de actualización"""
        self.updated_at = datetime.now()
        return super().save()
    
    def get_typed_value(self) -> Any:
        """
        Obtener el valor con el tipo correcto según la definición
        
        Returns:
            Valor tipado correctamente
        """
        if not self.valor:
            return None
        
        # Si es configuración predefinida, usar su tipo
        if self.clave in self.CONFIGURACIONES_PREDEFINIDAS:
            tipo = self.CONFIGURACIONES_PREDEFINIDAS[self.clave]['tipo']
        else:
            tipo = self.tipo
        
        return self._convert_to_type(self.valor, tipo)
    
    def _convert_to_type(self, valor: str, tipo: str) -> Any:
        """Convertir string al tipo especificado"""
        if valor is None:
            return None
        
        try:
            if tipo == self.TIPO_INTEGER:
                return int(float(valor)) if valor else 0
            elif tipo == self.TIPO_FLOAT:
                return float(valor) if valor else 0.0
            elif tipo == self.TIPO_BOOLEAN:
                if isinstance(valor, str):
                    valor_lower = valor.lower()
                    return valor_lower in ('true', '1', 'yes', 'si', 'sí', 'verdadero', 'on')
                return bool(valor)
            elif tipo == self.TIPO_JSON:
                return json.loads(valor) if valor else {}
            elif tipo == self.TIPO_LIST:
                # Lista separada por comas
                if not valor:
                    return []
                return [item.strip() for item in valor.split(',') if item.strip()]
            else:  # TIPO_STRING
                return str(valor)
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            # En caso de error, devolver el valor original
            return valor
    
    def set_typed_value(self, value: Any) -> None:
        """
        Establecer valor manteniendo el tipo
        
        Args:
            value: Valor a establecer
        """
        if value is None:
            self.valor = ''
            return
        
        # Determinar tipo
        if self.clave in self.CONFIGURACIONES_PREDEFINIDAS:
            tipo = self.CONFIGURACIONES_PREDEFINIDAS[self.clave]['tipo']
        else:
            tipo = self.tipo
        
        # Convertir a string según tipo
        if tipo == self.TIPO_BOOLEAN:
            self.valor = '1' if value else '0'
        elif tipo == self.TIPO_JSON:
            self.valor = json.dumps(value, ensure_ascii=False) if value else ''
        elif tipo == self.TIPO_LIST and isinstance(value, list):
            self.valor = ', '.join(str(item) for item in value)
        else:
            self.valor = str(value)
    
    @property
    def valor_para_mostrar(self) -> str:
        """Obtener valor formateado para mostrar (oculta valores secretos)"""
        if self.secreto and self.valor:
            return '••••••••'
        return self.valor
    
    @property
    def es_critica(self) -> bool:
        """Determinar si es una configuración crítica del sistema"""
        claves_criticas = [
            'EMPRESA_NOMBRE',
            'SISTEMA_MONEDA',
            'SISTEMA_IDIOMA',
            'SISTEMA_FORMATO_FECHA',
            'ACADEMICO_CUOTA_DEFAULT',
            'SEGURIDAD_PASSWORD_MIN_LENGTH',
            'SISTEMA_VERSION'
        ]
        return self.clave in claves_criticas
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Obtener metadatos de la configuración"""
        if self.clave in self.CONFIGURACIONES_PREDEFINIDAS:
            return self.CONFIGURACIONES_PREDEFINIDAS[self.clave].copy()
        
        return {
            'descripcion': self.descripcion,
            'grupo': self.grupo,
            'tipo': self.tipo,
            'editable': self.editable,
            'secreto': self.secreto
        }
    
    def to_dict(self, include_secrets: bool = False) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        data = {
            'id': self.id,
            'clave': self.clave,
            'valor': self.valor if (include_secrets or not self.secreto) else self.valor_para_mostrar,
            'descripcion': self.descripcion,
            'created_at': self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else str(self.created_at),
            'updated_at': self.updated_at.isoformat() if hasattr(self.updated_at, 'isoformat') else str(self.updated_at),
            'grupo': self.grupo,
            'tipo': self.tipo,
            'editable': self.editable,
            'secreto': self.secreto,
            'es_critica': self.es_critica,
            'es_predefinida': self.clave in self.CONFIGURACIONES_PREDEFINIDAS
        }
        return data
    
    @classmethod
    def initialize_predefined_configs(cls) -> Dict[str, Any]:
        """
        Inicializar configuraciones predefinidas en la base de datos
        
        Returns:
            Diccionario con resultados de la inicialización
        """
        resultados = {
            'creadas': 0,
            'actualizadas': 0,
            'omitidas': 0,
            'errores': 0
        }
        
        for clave, config_data in cls.CONFIGURACIONES_PREDEFINIDAS.items():
            try:
                # Verificar si ya existe
                existente = cls.get_by_key(clave)
                
                if existente:
                    # Actualizar solo si el valor es diferente del predefinido
                    if existente.valor != config_data['valor']:
                        existente.valor = config_data['valor']
                        existente.descripcion = config_data['descripcion']
                        existente.save()
                        resultados['actualizadas'] += 1
                    else:
                        resultados['omitidas'] += 1
                else:
                    # Crear nueva configuración
                    nueva_config = cls(
                        clave=clave,
                        valor=config_data['valor'],
                        descripcion=config_data['descripcion'],
                        grupo=config_data['grupo'],
                        tipo=config_data['tipo'],
                        editable=config_data.get('editable', True),
                        secreto=config_data.get('secreto', False)
                    )
                    nueva_config.save()
                    resultados['creadas'] += 1
                    
            except Exception as e:
                resultados['errores'] += 1
                # Log del error sería manejado por el controlador
        
        return resultados
    
    @classmethod
    def get_system_info(cls) -> Dict[str, Any]:
        """
        Obtener información del sistema desde configuraciones
        
        Returns:
            Diccionario con información del sistema
        """
        info = {
            'empresa': {},
            'sistema': {},
            'academico': {},
            'seguridad': {}
        }
        
        # Obtener configuraciones por grupo
        grupos = {
            'empresa': cls.GRUPO_EMPRESA,
            'sistema': cls.GRUPO_SISTEMA,
            'academico': cls.GRUPO_ACADEMICO,
            'seguridad': cls.GRUPO_SEGURIDAD
        }
        
        for clave, grupo in grupos.items():
            configs = cls.get_by_group(grupo)
            for config in configs:
                # Remover prefijo del grupo para la clave
                key = config.clave.replace(f"{grupo}_", "").lower()
                info[clave][key] = {
                    'valor': config.get_typed_value(),
                    'descripcion': config.descripcion
                }
        
        # Información adicional
        version_config = cls.get_by_key('SISTEMA_VERSION')
        info['sistema']['version'] = version_config.get_typed_value() if version_config else '2.0.0'
        
        ultima_actualizacion = cls.get_by_key('SISTEMA_ULTIMA_ACTUALIZACION')
        info['sistema']['ultima_actualizacion'] = ultima_actualizacion.valor if ultima_actualizacion else ''
        
        return info
    
    @classmethod
    def validate_key(cls, clave: str) -> Tuple[bool, str]:
        """
        Validar formato de clave de configuración
        
        Args:
            clave: Clave a validar
            
        Returns:
            Tuple (válido, mensaje_error)
        """
        if not clave or not clave.strip():
            return False, "La clave no puede estar vacía"
        
        if len(clave) < 2:
            return False, "La clave debe tener al menos 2 caracteres"
        
        if len(clave) > 100:
            return False, "La clave no puede exceder 100 caracteres"
        
        if ' ' in clave:
            return False, "La clave no puede contener espacios"
        
        # Para configuraciones predefinidas, verificar formato
        if clave in cls.CONFIGURACIONES_PREDEFINIDAS:
            if not clave.isupper() or '_' not in clave:
                return False, "Las configuraciones predefinidas deben usar formato CONSTANTE_CON_GUION_BAJO"
        
        return True, ""
    
    @classmethod
    def validate_value(cls, clave: str, valor: Any) -> Tuple[bool, str]:
        """
        Validar valor de configuración según su tipo
        
        Args:
            clave: Clave de la configuración
            valor: Valor a validar
            
        Returns:
            Tuple (válido, mensaje_error)
        """
        if valor is None:
            return True, ""  # Valores nulos son permitidos
        
        # Obtener tipo de la configuración
        tipo = cls.TIPO_STRING
        if clave in cls.CONFIGURACIONES_PREDEFINIDAS:
            tipo = cls.CONFIGURACIONES_PREDEFINIDAS[clave]['tipo']
        
        try:
            # Validar según tipo
            if tipo == cls.TIPO_INTEGER:
                int_valor = int(float(valor))
                if int_valor < 0:
                    return False, "El valor debe ser un número entero positivo"
            elif tipo == cls.TIPO_FLOAT:
                float_valor = float(valor)
                if float_valor < 0:
                    return False, "El valor debe ser un número positivo"
            elif tipo == cls.TIPO_BOOLEAN:
                # Cualquier valor es válido para booleano
                pass
            elif tipo == cls.TIPO_JSON:
                # Validar JSON
                if isinstance(valor, str):
                    json.loads(valor)
            elif tipo == cls.TIPO_LIST:
                # Listas son validadas en conversión
                pass
            
            return True, ""
            
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            return False, f"Valor inválido para tipo {tipo}: {str(e)}"