# database/connection.py
"""
Módulo de conexión a la base de datos para FormaGestPro_MVC.
Configura SQLAlchemy y proporciona la base para los modelos.
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
import os

# Configuración de la base de datos
# Usa SQLite por defecto, pero puede cambiarse por variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///formagestpro.db")

# Crear el motor de base de datos
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Cambiar a True para ver las consultas SQL en consola
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Crear una fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos declarativos
Base = declarative_base()

# Sesión para usar en todo el proyecto (patrón de sesión por hilo)
db_session = scoped_session(SessionLocal)

def get_db_session():
    """
    Obtiene una nueva sesión de base de datos.
    Úsala en un contexto with para asegurar el cierre.
    
    Uso:
        with get_db_session() as session:
            # trabajar con la sesión
    """
    return SessionLocal()

def init_db():
    """
    Inicializa la base de datos creando todas las tablas.
    
    Nota: Asegúrate de importar todos los modelos antes de llamar a esta función.
    """
    # Importar todos los modelos aquí para que SQLAlchemy los registre
    # Esto es necesario para que Base.metadata.create_all funcione
    from models.estudiante import EstudianteModel
    from models.docente import DocenteModel
    from models.programa import ProgramaModel
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    print(f"✅ Base de datos inicializada en: {DATABASE_URL}")

def close_db_session(session=None):
    """Cierra una sesión de base de datos."""
    if session:
        session.close()

# Para compatibilidad con código existente
# Algunos archivos pueden estar usando get_session() en lugar de get_db_session()
get_session = get_db_session