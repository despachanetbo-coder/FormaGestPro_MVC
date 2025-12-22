import os
from pathlib import Path
from datetime import datetime

class Config:
    """Configuración central de la aplicación"""
    
    def __init__(self):
        self.BASE_DIR = Path(__file__).parent.parent
        self.DB_PATH = self.BASE_DIR / "data" / "formagestpro.db"
        self.LOGS_DIR = self.BASE_DIR / "logs"
        self.RESOURCES_DIR = self.BASE_DIR / "resources"
        
        # Configuración de la empresa
        self.EMPRESA_NOMBRE = "Formación Continua Consultora"
        self.EMPRESA_NIT = "1234567012"
        
        # Configuración financiera
        self.TASA_MORA_DIARIA = 0.0005  # 0.05% diario
        self.DIAS_GRACIA = 5
        
        # Crear directorios necesarios
        self._crear_directorios()
    
    def _crear_directorios(self):
        """Crear estructura de directorios necesaria"""
        directorios = [
            self.BASE_DIR / "data",
            self.LOGS_DIR,
            self.RESOURCES_DIR / "comprobantes",
            self.RESOURCES_DIR / "fotos_estudiantes",
            self.RESOURCES_DIR / "curriculums",
            self.RESOURCES_DIR / "templates"
        ]
        
        for directorio in directorios:
            directorio.mkdir(parents=True, exist_ok=True)
    
    @property
    def fecha_actual(self):
        """Fecha actual en formato YYYY-MM-DD"""
        return datetime.now().strftime('%Y-%m-%d')

# Instancia global de configuración
config = Config()
