# app/models/plan_pago.py
"""
Modelo de Plan de Pago usando PostgreSQL directamente.
"""
import logging
from .base_model import BaseModel

logger = logging.getLogger(__name__)


class PlanPagoModel(BaseModel):
    """Modelo que representa un plan de pago para programas"""

    TABLE_NAME = "planes_pago"

    def __init__(self, **kwargs):
        """
        Inicializa un plan de pago.

        Campos esperados:
            programa_id, nombre, nro_cuotas, intervalo_dias, descripcion, activo
        """
        # Campos obligatorios
        self.programa_id = kwargs.get("programa_id")
        self.nombre = kwargs.get("nombre")
        self.nro_cuotas = kwargs.get("nro_cuotas", 1)
        self.intervalo_dias = kwargs.get("intervalo_dias", 30)

        # Campos opcionales
        self.descripcion = kwargs.get("descripcion")
        self.activo = kwargs.get("activo", 1)
        self.created_at = kwargs.get("created_at")

        # ID (si viene de la base de datos)
        if "id" in kwargs:
            self.id = kwargs["id"]

        # Validaciones
        self._validar()

    def _validar(self):
        """Valida los datos del plan de pago"""
        if not self.programa_id or not self.nombre:
            raise ValueError("programa_id y nombre son obligatorios")

        if self.nro_cuotas <= 0:
            raise ValueError("El número de cuotas debe ser mayor a 0")

        if self.intervalo_dias <= 0:
            raise ValueError("El intervalo de días debe ser mayor a 0")

    def __repr__(self):
        return f"<PlanPago {self.nombre}: {self.nro_cuotas} cuotas cada {self.intervalo_dias} días>"

    def activar(self):
        """Activa el plan de pago"""
        self.activo = 1
        return self.save()

    def desactivar(self):
        """Desactiva el plan de pago"""
        self.activo = 0
        return self.save()

    @classmethod
    def buscar_por_programa(cls, programa_id: int):
        """Busca planes de pago por programa"""
        from database.database import db

        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE programa_id = ?"
        rows = db.fetch_all(query, (programa_id,))

        return [cls(**row) for row in rows]

    @classmethod
    def buscar_activos_por_programa(cls, programa_id: int):
        """Busca planes de pago activos por programa"""
        from database.database import db

        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE programa_id = ? AND activo = 1"
        rows = db.fetch_all(query, (programa_id,))

        return [cls(**row) for row in rows]

    @classmethod
    def crear_plan_pago(
        cls,
        programa_id: int,
        nombre: str,
        nro_cuotas: int,
        intervalo_dias: int,
        descripcion: str = None,
    ) -> "PlanPagoModel":
        """Crea un nuevo plan de pago con validaciones"""
        # Verificar que no exista un plan con el mismo nombre para este programa
        from database.database import db

        query = "SELECT * FROM planes_pago WHERE programa_id = ? AND nombre = ?"
        existente = db.fetch_one(query, (programa_id, nombre))

        if existente:
            raise ValueError(
                f"Ya existe un plan de pago con el nombre '{nombre}' para este programa"
            )

        # Crear el plan
        plan = cls(
            programa_id=programa_id,
            nombre=nombre,
            nro_cuotas=nro_cuotas,
            intervalo_dias=intervalo_dias,
            descripcion=descripcion,
        )

        plan.save()
        return plan

    @classmethod
    def crear_para_programa(
        cls,
        programa_id,
        nombre,
        nro_cuotas,
        monto_cuota=None,
        intervalo_dias=30,
        fecha_inicio=None,
    ):
        """Crea un plan de pago específico para un programa"""
        from app.models.programa_academico_model import ProgramaAcademicoModel

        programa = ProgramaAcademicoModel.find_by_id(programa_id)
        if not programa:
            raise ValueError("Programa no encontrado")

        # Si no se especifica monto_cuota, calcularlo basado en colegiatura
        if monto_cuota is None:
            monto_total = programa.costo_base
            monto_cuota = monto_total / nro_cuotas

        plan_data = {
            "programa_id": programa_id,
            "nombre": nombre,
            "nro_cuotas": nro_cuotas,
            "intervalo_dias": intervalo_dias,
            "activo": True,
        }

        return cls.create(plan_data)
