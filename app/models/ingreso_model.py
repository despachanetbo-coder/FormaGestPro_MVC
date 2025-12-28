# app/models/ingreso_model.py
"""
Modelo para gestión de ingresos - FormaGestPro MVC
Hereda de BaseModel para conexión a PostgreSQL
"""

import sys
import os
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple, Union

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_model import BaseModel


class IngresoModel(BaseModel):
    """
    Modelo para gestión de ingresos en el sistema FormaGestPro

    Atributos:
        - id: Identificador único
        - tipo_ingreso: Tipo de ingreso (MATRICULA_CUOTA, MATRICULA_CONTADO, OTRO_INGRESO)
        - matricula_id: ID de la matrícula asociada (opcional)
        - nro_cuota: Número de cuota (para pagos por cuotas)
        - fecha: Fecha del ingreso
        - monto: Monto del ingreso
        - concepto: Concepto del ingreso
        - descripcion: Descripción adicional
        - forma_pago: Forma de pago (EFECTIVO, TRANSFERENCIA, TARJETA, etc.)
        - estado: Estado del ingreso (REGISTRADO, CONFIRMADO, ANULADO)
        - nro_comprobante: Número de comprobante
        - nro_transaccion: Número de transacción bancaria
        - registrado_por: ID del usuario que registró el ingreso
        - created_at: Fecha de creación
    """

    # Constantes de tipo de ingreso (coinciden con el controlador)
    TIPO_MATRICULA_CUOTA = "MATRICULA_CUOTA"
    TIPO_MATRICULA_CONTADO = "MATRICULA_CONTADO"
    TIPO_OTRO_INGRESO = "OTRO_INGRESO"

    # Constantes de estado (coinciden con el controlador)
    ESTADO_REGISTRADO = "REGISTRADO"
    ESTADO_CONFIRMADO = "CONFIRMADO"
    ESTADO_ANULADO = "ANULADO"

    # Constantes de formas de pago
    FORMA_EFECTIVO = "EFECTIVO"
    FORMA_TRANSFERENCIA = "TRANSFERENCIA"
    FORMA_TARJETA_CREDITO = "TARJETA_CREDITO"
    FORMA_TARJETA_DEBITO = "TARJETA_DEBITO"
    FORMA_DEPOSITO = "DEPOSITO"
    FORMA_CHEQUE = "CHEQUE"

    def __init__(self, **kwargs):
        """
        Inicializa un nuevo ingreso

        Args:
            **kwargs: Atributos del ingreso
        """
        super().__init__()
        self.table_name = "ingresos"

        # Atributos del modelo
        self.id = kwargs.get("id")
        self.tipo_ingreso = kwargs.get("tipo_ingreso", self.TIPO_OTRO_INGRESO)
        self.matricula_id = kwargs.get("matricula_id")
        self.nro_cuota = kwargs.get("nro_cuota")
        self.fecha = kwargs.get("fecha", date.today().isoformat())
        self.monto = kwargs.get("monto", 0.0)
        self.concepto = kwargs.get("concepto", "")
        self.descripcion = kwargs.get("descripcion", "")
        self.forma_pago = kwargs.get("forma_pago", self.FORMA_EFECTIVO)
        self.estado = kwargs.get("estado", self.ESTADO_REGISTRADO)
        self.nro_comprobante = kwargs.get("nro_comprobante")
        self.nro_transaccion = kwargs.get("nro_transaccion")
        self.registrado_por = kwargs.get("registrado_por")
        self.created_at = kwargs.get("created_at", datetime.now().isoformat())

        # Validar datos requeridos
        self._validate_required_fields()

    def _validate_required_fields(self):
        """Valida campos requeridos"""
        if not self.tipo_ingreso:
            raise ValueError("El tipo de ingreso es requerido")
        if not self.fecha:
            raise ValueError("La fecha es requerida")
        if not self.monto or self.monto <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        if not self.concepto:
            raise ValueError("El concepto es requerido")
        if not self.forma_pago:
            raise ValueError("La forma de pago es requerida")

    def save(self) -> Optional[int]:
        """
        Guarda el ingreso en la base de datos

        Returns:
            Optional[int]: ID del ingreso guardado o None si hay error
        """
        try:
            # Preparar datos para inserción
            data = {
                "tipo_ingreso": self.tipo_ingreso,
                "fecha": self.fecha,
                "monto": float(self.monto),  # Convertir a float para PostgreSQL
                "concepto": self.concepto,
                "forma_pago": self.forma_pago,
                "estado": self.estado,
                "created_at": self.created_at,
            }

            # Campos opcionales
            if self.matricula_id:
                data["matricula_id"] = self.matricula_id
            if self.nro_cuota is not None:
                data["nro_cuota"] = self.nro_cuota
            if self.descripcion:
                data["descripcion"] = self.descripcion
            if self.nro_comprobante:
                data["nro_comprobante"] = self.nro_comprobante
            if self.nro_transaccion:
                data["nro_transaccion"] = self.nro_transaccion
            if self.registrado_por:
                data["registrado_por"] = self.registrado_por

            # Insertar en base de datos
            result = self.insert(self.table_name, data, returning="id")

            if result:
                self.id = result
                return result

            return None

        except Exception as e:
            print(f"✗ Error guardando ingreso: {e}")
            return None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el objeto a diccionario

        Returns:
            Dict[str, Any]: Diccionario con todos los atributos
        """
        return {
            "id": self.id,
            "tipo_ingreso": self.tipo_ingreso,
            "matricula_id": self.matricula_id,
            "nro_cuota": self.nro_cuota,
            "fecha": self.fecha,
            "monto": self.monto,
            "concepto": self.concepto,
            "descripcion": self.descripcion,
            "forma_pago": self.forma_pago,
            "estado": self.estado,
            "nro_comprobante": self.nro_comprobante,
            "nro_transaccion": self.nro_transaccion,
            "registrado_por": self.registrado_por,
            "created_at": self.created_at,
        }

    def update(self) -> bool:
        """
        Actualiza el ingreso en la base de datos

        Returns:
            bool: True si se actualizó correctamente
        """
        if not self.id:
            return False

        try:
            data = self.to_dict()
            # No actualizar ID ni created_at
            del data["id"]
            del data["created_at"]

            condition = "id = %s"
            params = (self.id,)

            result = self.update_table(self.table_name, data, condition, params)
            return result is not None

        except Exception as e:
            print(f"✗ Error actualizando ingreso: {e}")
            return False

    def delete(self) -> bool:
        """
        Elimina el ingreso de la base de datos

        Returns:
            bool: True si se eliminó correctamente
        """
        if not self.id:
            return False

        try:
            condition = "id = %s"
            params = (self.id,)

            result = self.delete_rows(self.table_name, condition, params)
            return result is not None

        except Exception as e:
            print(f"✗ Error eliminando ingreso: {e}")
            return False

    def marcar_como_confirmado(self) -> bool:
        """
        Marca el ingreso como confirmado

        Returns:
            bool: True si se actualizó correctamente
        """
        self.estado = self.ESTADO_CONFIRMADO
        return self.update()

    def marcar_como_anulado(
        self, motivo: str = None  # type:ignore
    ) -> bool:
        """
        Marca el ingreso como anulado

        Args:
            motivo: Motivo de la anulación (opcional)

        Returns:
            bool: True si se actualizó correctamente
        """
        self.estado = self.ESTADO_ANULADO
        if motivo and not self.descripcion:
            self.descripcion = f"Anulado: {motivo}"
        elif motivo:
            self.descripcion += f"\nAnulado: {motivo}"

        return self.update()

    # ============ MÉTODOS DE CLASE (STATIC) ============

    @classmethod
    def find_by_id(cls, ingreso_id: int) -> Optional["IngresoModel"]:
        """
        Busca un ingreso por su ID

        Args:
            ingreso_id: ID del ingreso

        Returns:
            Optional[IngresoModel]: Instancia del modelo o None si no existe
        """
        try:
            instance = cls()
            query = "SELECT * FROM ingresos WHERE id = %s"
            result = instance.fetch_one(query, (ingreso_id,))

            if result:
                return cls(**result)

            return None

        except Exception as e:
            print(f"✗ Error buscando ingreso por ID: {e}")
            return None

    @classmethod
    def find_all(cls, limit: int = 100) -> List["IngresoModel"]:
        """
        Obtiene todos los ingresos

        Args:
            limit: Límite de resultados

        Returns:
            List[IngresoModel]: Lista de ingresos
        """
        try:
            instance = cls()
            query = "SELECT * FROM ingresos ORDER BY fecha DESC LIMIT %s"
            results = instance.fetch_all(query, (limit,))

            return [cls(**row) for row in results] if results else []

        except Exception as e:
            print(f"✗ Error obteniendo todos los ingresos: {e}")
            return []

    @classmethod
    def buscar_por_matricula(cls, matricula_id: int) -> List["IngresoModel"]:
        """
        Busca ingresos por matrícula

        Args:
            matricula_id: ID de la matrícula

        Returns:
            List[IngresoModel]: Lista de ingresos de la matrícula
        """
        try:
            instance = cls()
            query = """
                SELECT * FROM ingresos 
                WHERE matricula_id = %s 
                ORDER BY fecha DESC
            """
            results = instance.fetch_all(query, (matricula_id,))

            return [cls(**row) for row in results] if results else []

        except Exception as e:
            print(f"✗ Error buscando ingresos por matrícula: {e}")
            return []

    @classmethod
    def crear_ingreso_generico(cls, datos: Dict[str, Any]) -> "IngresoModel":
        """
        Crea un ingreso genérico

        Args:
            datos: Diccionario con datos del ingreso

        Returns:
            IngresoModel: Instancia del ingreso creado
        """
        # Asegurar que sea ingreso genérico
        datos["tipo_ingreso"] = cls.TIPO_OTRO_INGRESO
        datos["matricula_id"] = None
        datos["nro_cuota"] = None

        # Crear instancia
        ingreso = cls(**datos)

        # Guardar en base de datos
        ingreso.save()

        return ingreso

    @classmethod
    def buscar_ingresos_genericos(
        cls, fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None
    ) -> List["IngresoModel"]:
        """
        Busca ingresos genéricos

        Args:
            fecha_inicio: Fecha de inicio (opcional)
            fecha_fin: Fecha de fin (opcional)

        Returns:
            List[IngresoModel]: Lista de ingresos genéricos
        """
        try:
            instance = cls()

            query = """
                SELECT * FROM ingresos 
                WHERE tipo_ingreso = %s
            """
            params = [cls.TIPO_OTRO_INGRESO]

            if fecha_inicio:
                query += " AND fecha >= %s"
                params.append(fecha_inicio)

            if fecha_fin:
                query += " AND fecha <= %s"
                params.append(fecha_fin)

            query += " ORDER BY fecha DESC"

            results = instance.fetch_all(query, params)

            return [cls(**row) for row in results] if results else []

        except Exception as e:
            print(f"✗ Error buscando ingresos genéricos: {e}")
            return []

    @classmethod
    def buscar_por_rango_fechas(
        cls, fecha_inicio: str, fecha_fin: str, estado: Optional[str] = None
    ) -> List["IngresoModel"]:
        """
        Busca ingresos por rango de fechas

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            estado: Estado a filtrar (opcional)

        Returns:
            List[IngresoModel]: Lista de ingresos en el rango
        """
        try:
            instance = cls()

            query = "SELECT * FROM ingresos WHERE fecha BETWEEN %s AND %s"
            params = [fecha_inicio, fecha_fin]

            if estado:
                query += " AND estado = %s"
                params.append(estado)

            query += " ORDER BY fecha DESC"

            results = instance.fetch_all(query, params)

            return [cls(**row) for row in results] if results else []

        except Exception as e:
            print(f"✗ Error buscando ingresos por rango de fechas: {e}")
            return []

    @classmethod
    def get_estadisticas_mes(cls, año: int, mes: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de ingresos por mes

        Args:
            año: Año a consultar
            mes: Mes a consultar (1-12)

        Returns:
            Dict[str, Any]: Estadísticas del mes
        """
        try:
            instance = cls()

            fecha_inicio = f"{año:04d}-{mes:02d}-01"
            if mes == 12:
                fecha_fin = f"{año:04d}-12-31"
            else:
                fecha_fin = f"{año:04d}-{(mes+1):02d}-01"

            query = """
                SELECT 
                    tipo_ingreso,
                    COUNT(*) as cantidad,
                    SUM(monto) as total_monto,
                    forma_pago,
                    COUNT(CASE WHEN estado = %s THEN 1 END) as confirmados,
                    COUNT(CASE WHEN estado = %s THEN 1 END) as anulados
                FROM ingresos 
                WHERE fecha BETWEEN %s AND %s
                GROUP BY tipo_ingreso, forma_pago
                ORDER BY total_monto DESC
            """

            params = [
                cls.ESTADO_CONFIRMADO,
                cls.ESTADO_ANULADO,
                fecha_inicio,
                fecha_fin,
            ]

            results = instance.fetch_all(query, params)

            # Calcular totales
            total_general = 0
            for row in results:
                total_general += row["total_monto"] or 0

            return {
                "año": año,
                "mes": mes,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "total_general": total_general,
                "detalle": results if results else [],
                "total_registros": len(results) if results else 0,
            }

        except Exception as e:
            print(f"✗ Error obteniendo estadísticas del mes: {e}")
            return {}

    # ============ MÉTODOS DE VALIDACIÓN ============

    @classmethod
    def validar_forma_pago(cls, forma_pago: str) -> bool:
        """
        Valida si una forma de pago es válida

        Args:
            forma_pago: Forma de pago a validar

        Returns:
            bool: True si es válida
        """
        formas_validas = [
            cls.FORMA_EFECTIVO,
            cls.FORMA_TRANSFERENCIA,
            cls.FORMA_TARJETA_CREDITO,
            cls.FORMA_TARJETA_DEBITO,
            cls.FORMA_DEPOSITO,
            cls.FORMA_CHEQUE,
        ]

        return forma_pago in formas_validas

    @classmethod
    def validar_tipo_ingreso(cls, tipo_ingreso: str) -> bool:
        """
        Valida si un tipo de ingreso es válido

        Args:
            tipo_ingreso: Tipo de ingreso a validar

        Returns:
            bool: True si es válido
        """
        tipos_validos = [
            cls.TIPO_MATRICULA_CUOTA,
            cls.TIPO_MATRICULA_CONTADO,
            cls.TIPO_OTRO_INGRESO,
        ]

        return tipo_ingreso in tipos_validos

    @classmethod
    def validar_estado(cls, estado: str) -> bool:
        """
        Valida si un estado es válido

        Args:
            estado: Estado a validar

        Returns:
            bool: True si es válido
        """
        estados_validos = [
            cls.ESTADO_REGISTRADO,
            cls.ESTADO_CONFIRMADO,
            cls.ESTADO_ANULADO,
        ]

        return estado in estados_validos

    # ============ MÉTODOS DE UTILIDAD ============

    @classmethod
    def get_tipos_ingreso(cls) -> List[Dict[str, str]]:
        """
        Obtiene la lista de tipos de ingreso con descripción

        Returns:
            List[Dict[str, str]]: Lista de tipos con descripción
        """
        return [
            {"valor": cls.TIPO_MATRICULA_CUOTA, "descripcion": "Matrícula por cuotas"},
            {
                "valor": cls.TIPO_MATRICULA_CONTADO,
                "descripcion": "Matrícula al contado",
            },
            {"valor": cls.TIPO_OTRO_INGRESO, "descripcion": "Otro ingreso"},
        ]

    @classmethod
    def get_formas_pago(cls) -> List[Dict[str, str]]:
        """
        Obtiene la lista de formas de pago con descripción

        Returns:
            List[Dict[str, str]]: Lista de formas de pago con descripción
        """
        return [
            {"valor": cls.FORMA_EFECTIVO, "descripcion": "Efectivo"},
            {"valor": cls.FORMA_TRANSFERENCIA, "descripcion": "Transferencia bancaria"},
            {"valor": cls.FORMA_TARJETA_CREDITO, "descripcion": "Tarjeta de crédito"},
            {"valor": cls.FORMA_TARJETA_DEBITO, "descripcion": "Tarjeta de débito"},
            {"valor": cls.FORMA_DEPOSITO, "descripcion": "Depósito bancario"},
            {"valor": cls.FORMA_CHEQUE, "descripcion": "Cheque"},
        ]

    @classmethod
    def get_estados(cls) -> List[Dict[str, str]]:
        """
        Obtiene la lista de estados con descripción

        Returns:
            List[Dict[str, str]]: Lista de estados con descripción
        """
        return [
            {"valor": cls.ESTADO_REGISTRADO, "descripcion": "Registrado"},
            {"valor": cls.ESTADO_CONFIRMADO, "descripcion": "Confirmado"},
            {"valor": cls.ESTADO_ANULADO, "descripcion": "Anulado"},
        ]

    def __str__(self) -> str:
        """Representación en string del ingreso"""
        return (
            f"Ingreso #{self.id}: {self.concepto} - ${self.monto:.2f} ({self.estado})"
        )

    def __repr__(self) -> str:
        """Representación oficial del objeto"""
        return f"IngresoModel(id={self.id}, tipo={self.tipo_ingreso}, monto={self.monto}, estado={self.estado})"


# Métodos adicionales para compatibilidad con controladores antiguos
def crear_ingreso_generico(datos: Dict[str, Any]) -> IngresoModel:
    """Función helper para compatibilidad"""
    return IngresoModel.crear_ingreso_generico(datos)


def buscar_por_matricula(matricula_id: int) -> List[IngresoModel]:
    """Función helper para compatibilidad"""
    return IngresoModel.buscar_por_matricula(matricula_id)


def buscar_ingresos_genericos(
    fecha_inicio: str = None, fecha_fin: str = None  # type:ignore
) -> List[IngresoModel]:
    """Función helper para compatibilidad"""
    return IngresoModel.buscar_ingresos_genericos(fecha_inicio, fecha_fin)
