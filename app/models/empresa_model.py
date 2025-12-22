# app/models/empresa.py
"""
Modelo para los datos de la empresa.
"""
from .base_model import BaseModel

class EmpresaModel(BaseModel):
    """Modelo que representa los datos de la empresa"""
    
    TABLE_NAME = "empresa"
    
    def __init__(self, **kwargs):
        self.nombre = kwargs.get('nombre', '')
        self.nit = kwargs.get('nit', '')
        self.direccion = kwargs.get('direccion', '')
        self.telefono = kwargs.get('telefono', '')
        self.email = kwargs.get('email', '')
        self.logo_path = kwargs.get('logo_path', '')
        self.created_at = kwargs.get('created_at', '')
        
        if 'id' in kwargs:
            self.id = kwargs['id']
    
    def __repr__(self):
        return f"<Empresa: {self.nombre}>"
    
    @classmethod
    def obtener_datos(cls):
        """Obtiene los datos de la empresa (asume solo un registro)"""
        from database.database import db
        
        query = f"SELECT * FROM {cls.TABLE_NAME} LIMIT 1"
        row = db.fetch_one(query)
        
        if row:
            return cls(**row)
        else:
            # Retorna datos por defecto si no hay registro
            return cls(
                nombre="Formación Continua Consultora",
                nit="1234567012",
                direccion="Av. Principal #123",
                telefono="+591 12345678",
                email="info@formacioncontinua.com",
                logo_path=None
            )