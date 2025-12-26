# app/models/plan_pago_model.py - Versión optimizada y robusta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_model import BaseModel
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple, Union


class PlanPagoModel(BaseModel):
    def __init__(self):
        """Inicializa el modelo de planes de pago"""
        super().__init__()
        self.table_name = "planes_pago"
        self.sequence_name = "seq_planes_pago_id"

        # Columnas de la tabla para validación
        self.columns = [
            "id",
            "programa_id",
            "nombre",
            "nro_cuotas",
            "intervalo_dias",
            "descripcion",
            "activo",
            "created_at",
        ]

        # Columnas requeridas
        self.required_columns = [
            "programa_id",
            "nombre",
            "nro_cuotas",
            "intervalo_dias",
        ]

        # Columnas de tipo entero
        self.integer_columns = ["programa_id", "nro_cuotas", "intervalo_dias"]

    # ============ MÉTODOS DE VALIDACIÓN ============

    def _validate_plan_data(
        self, data: Dict[str, Any], for_update: bool = False
    ) -> Tuple[bool, str]:
        """
        Valida los datos del plan de pago

        Args:
            data: Diccionario con datos del plan
            for_update: Si es True, valida para actualización

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        # Campos requeridos para creación
        if not for_update:
            for field in self.required_columns:
                if field not in data or data[field] is None:
                    return False, f"Campo requerido faltante: {field}"

        # Validar número de cuotas positivo
        if "nro_cuotas" in data and data["nro_cuotas"] is not None:
            try:
                nro_cuotas = int(data["nro_cuotas"])
                if nro_cuotas <= 0:
                    return False, "El número de cuotas debe ser mayor a 0"
            except (ValueError, TypeError):
                return False, "Número de cuotas inválido"

        # Validar intervalo de días positivo
        if "intervalo_dias" in data and data["intervalo_dias"] is not None:
            try:
                intervalo = int(data["intervalo_dias"])
                if intervalo <= 0:
                    return False, "El intervalo de días debe ser mayor a 0"
            except (ValueError, TypeError):
                return False, "Intervalo de días inválido"

        # Validar unicidad del nombre por programa
        if "programa_id" in data and "nombre" in data and data["nombre"]:
            existing_id = None
            if for_update and "id" in data:
                existing_id = data["id"]

            if self.nombre_exists_en_programa(
                data["programa_id"], data["nombre"], exclude_id=existing_id
            ):
                return (
                    False,
                    f"Ya existe un plan con el nombre '{data['nombre']}' para este programa",
                )

        # Validar que el programa existe
        if "programa_id" in data and data["programa_id"]:
            if not self._programa_exists(data["programa_id"]):
                return False, f"El programa con ID {data['programa_id']} no existe"

        return True, "Datos válidos"

    def _programa_exists(self, programa_id: int) -> bool:
        """Verifica si el programa existe en la tabla programas_academicos"""
        try:
            query = "SELECT COUNT(*) as count FROM programas_academicos WHERE id = %s"
            result = self.fetch_one(query, (programa_id,))
            return result["count"] > 0 if result else False
        except Exception as e:
            print(f"✗ Error verificando existencia de programa: {e}")
            return False

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza los datos del plan de pago

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
                # Convertir enteros
                elif key in self.integer_columns and value is not None:
                    try:
                        sanitized[key] = int(value)
                    except (ValueError, TypeError):
                        sanitized[key] = value
                # Mantener otros tipos
                else:
                    sanitized[key] = value

        return sanitized

    # ============ MÉTODOS CRUD PRINCIPALES ============

    def create(self, data: Dict[str, Any]) -> Optional[int]:
        """
        Crea un nuevo plan de pago

        Args:
            data: Diccionario con datos del plan

        Returns:
            Optional[int]: ID del plan creado o None si hay error
        """
        # Sanitizar y validar datos
        data = self._sanitize_data(data)
        is_valid, error_msg = self._validate_plan_data(data, for_update=False)

        if not is_valid:
            print(f"✗ Error validando datos: {error_msg}")
            return None

        try:
            # Preparar datos para inserción
            insert_data = data.copy()

            # Establecer valores por defecto
            defaults = {
                "activo": True,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            for key, value in defaults.items():
                if key not in insert_data or insert_data[key] is None:
                    insert_data[key] = value

            # Insertar en base de datos
            result = self.insert(self.table_name, insert_data, returning="id")

            if result:
                print(f"✓ Plan de pago creado exitosamente con ID: {result}")
                return result

            return None

        except Exception as e:
            print(f"✗ Error creando plan de pago: {e}")
            return None

    def read(self, plan_id: int, active_only: bool = True) -> Optional[Dict[str, Any]]:
        """
        Obtiene un plan de pago por su ID

        Args:
            plan_id: ID del plan
            active_only: Si es True, solo planes activos

        Returns:
            Optional[Dict]: Datos del plan o None si no existe
        """
        try:
            query = f"""
            SELECT pp.*, 
                   pa.nombre as programa_nombre,
                   pa.codigo as programa_codigo
            FROM {self.table_name} pp
            JOIN programas_academicos pa ON pp.programa_id = pa.id
            WHERE pp.id = %s
            """

            params = [plan_id]

            if active_only:
                query += " AND pp.activo = TRUE"

            result = self.fetch_one(query, params)
            return result

        except Exception as e:
            print(f"✗ Error obteniendo plan de pago: {e}")
            return None

    def update(self, plan_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un plan de pago existente

        Args:
            plan_id: ID del plan a actualizar
            data: Diccionario con datos a actualizar

        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        if not data:
            return False

        # Obtener datos actuales para validación
        plan_actual = self.read(plan_id, active_only=False)
        if not plan_actual:
            return False

        # Combinar datos actuales con los nuevos para validación
        data_with_id = {**plan_actual, **data}
        data_with_id["id"] = plan_id

        # Sanitizar y validar datos
        data = self._sanitize_data(data)
        is_valid, error_msg = self._validate_plan_data(data_with_id, for_update=True)

        if not is_valid:
            print(f"✗ Error validando datos: {error_msg}")
            return False

        try:
            # Actualizar en base de datos
            result = self.update_table(self.table_name, data, "id = %s", (plan_id,))

            if result:
                print(f"✓ Plan de pago {plan_id} actualizado exitosamente")
                return True

            return False

        except Exception as e:
            print(f"✗ Error actualizando plan de pago: {e}")
            return False

    def delete(self, plan_id: int, soft_delete: bool = True) -> bool:
        """
        Elimina un plan de pago

        Args:
            plan_id: ID del plan
            soft_delete: Si es True, marca como inactivo en lugar de eliminar físicamente

        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            if soft_delete:
                # Soft delete: marcar como inactivo
                query = f"UPDATE {self.table_name} SET activo = FALSE WHERE id = %s"
                params = (plan_id,)
            else:
                # Hard delete: eliminar físicamente
                query = f"DELETE FROM {self.table_name} WHERE id = %s"
                params = (plan_id,)

            result = self.execute_query(query, params, commit=True)

            if result:
                delete_type = "desactivado" if soft_delete else "eliminado"
                print(f"✓ Plan de pago {plan_id} {delete_type} exitosamente")
                return True

            return False

        except Exception as e:
            print(f"✗ Error eliminando plan de pago: {e}")
            return False

    # ============ MÉTODOS DE CONSULTA AVANZADOS ============

    def get_all(
        self,
        programa_id: Optional[int] = None,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "nombre",
        order_desc: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todos los planes de pago

        Args:
            programa_id: Filtrar por programa específico
            active_only: Si es True, solo planes activos
            limit: Límite de registros
            offset: Desplazamiento para paginación
            order_by: Campo para ordenar
            order_desc: Si es True, orden descendente

        Returns:
            List[Dict]: Lista de planes de pago
        """
        try:
            query = f"""
            SELECT pp.*, 
                   pa.nombre as programa_nombre,
                   pa.codigo as programa_codigo
            FROM {self.table_name} pp
            JOIN programas_academicos pa ON pp.programa_id = pa.id
            """

            conditions = []
            params = []

            if programa_id is not None:
                conditions.append("pp.programa_id = %s")
                params.append(programa_id)

            if active_only:
                conditions.append("pp.activo = TRUE")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            # Ordenar
            order_dir = "DESC" if order_desc else "ASC"
            query += f" ORDER BY pp.{order_by} {order_dir}"

            # Paginación
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            return self.fetch_all(query, params)

        except Exception as e:
            print(f"✗ Error obteniendo planes de pago: {e}")
            return []

    def get_by_programa(
        self, programa_id: int, active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Obtiene planes de pago por programa

        Args:
            programa_id: ID del programa
            active_only: Si es True, solo planes activos

        Returns:
            List[Dict]: Lista de planes del programa
        """
        return self.get_all(programa_id=programa_id, active_only=active_only)

    def search(
        self,
        search_term: str,
        programa_id: Optional[int] = None,
        active_only: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Busca planes de pago por término de búsqueda

        Args:
            search_term: Término a buscar
            programa_id: Filtrar por programa específico
            active_only: Si es True, solo planes activos

        Returns:
            List[Dict]: Lista de planes que coinciden
        """
        try:
            query = f"""
            SELECT pp.*, 
                   pa.nombre as programa_nombre,
                   pa.codigo as programa_codigo
            FROM {self.table_name} pp
            JOIN programas_academicos pa ON pp.programa_id = pa.id
            WHERE (pp.nombre ILIKE %s OR pp.descripcion ILIKE %s)
            """

            params = [f"%{search_term}%", f"%{search_term}%"]

            if programa_id is not None:
                query += " AND pp.programa_id = %s"
                params.append(programa_id)  # type: ignore

            if active_only:
                query += " AND pp.activo = TRUE"

            query += " ORDER BY pp.nombre"

            return self.fetch_all(query, params)

        except Exception as e:
            print(f"✗ Error buscando planes de pago: {e}")
            return []

    # ============ MÉTODOS DE GESTIÓN DE PLANES ============

    def activar_plan(self, plan_id: int) -> bool:
        """
        Activa un plan de pago

        Args:
            plan_id: ID del plan

        Returns:
            bool: True si se activó correctamente
        """
        try:
            data = {"activo": True}
            return self.update(plan_id, data)

        except Exception as e:
            print(f"✗ Error activando plan de pago: {e}")
            return False

    def desactivar_plan(self, plan_id: int) -> bool:
        """
        Desactiva un plan de pago

        Args:
            plan_id: ID del plan

        Returns:
            bool: True si se desactivó correctamente
        """
        try:
            data = {"activo": False}
            return self.update(plan_id, data)

        except Exception as e:
            print(f"✗ Error desactivando plan de pago: {e}")
            return False

    def duplicar_plan(
        self, plan_id: int, nuevo_nombre: str, nuevo_programa_id: Optional[int] = None
    ) -> Optional[int]:
        """
        Duplica un plan de pago existente

        Args:
            plan_id: ID del plan a duplicar
            nuevo_nombre: Nombre para el nuevo plan
            nuevo_programa_id: ID del programa para el nuevo plan (opcional)

        Returns:
            Optional[int]: ID del nuevo plan creado o None si hay error
        """
        try:
            # Obtener plan original
            plan_original = self.read(plan_id, active_only=False)
            if not plan_original:
                return None

            # Preparar datos para el nuevo plan
            nuevo_plan = {
                "programa_id": (
                    nuevo_programa_id
                    if nuevo_programa_id
                    else plan_original["programa_id"]
                ),
                "nombre": nuevo_nombre,
                "nro_cuotas": plan_original["nro_cuotas"],
                "intervalo_dias": plan_original["intervalo_dias"],
                "descripcion": (
                    f"Copia de: {plan_original['descripcion']}"
                    if plan_original["descripcion"]
                    else "Plan duplicado"
                ),
            }

            # Crear nuevo plan
            return self.create(nuevo_plan)

        except Exception as e:
            print(f"✗ Error duplicando plan de pago: {e}")
            return None

    # ============ MÉTODOS DE CÁLCULO DE CUOTAS ============

    def generar_calendario_pagos(
        self, plan_id: int, fecha_inicio: str, monto_total: Decimal
    ) -> List[Dict[str, Any]]:
        """
        Genera un calendario de pagos basado en el plan

        Args:
            plan_id: ID del plan de pago
            fecha_inicio: Fecha de inicio (YYYY-MM-DD)
            monto_total: Monto total a distribuir

        Returns:
            List[Dict]: Calendario de pagos con fechas y montos
        """
        try:
            # Obtener datos del plan
            plan = self.read(plan_id)
            if not plan:
                return []

            # Validar fecha
            try:
                fecha_actual = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            except ValueError:
                print("✗ Formato de fecha inválido")
                return []

            nro_cuotas = plan["nro_cuotas"]
            intervalo_dias = plan["intervalo_dias"]

            # Calcular monto por cuota
            monto_cuota = monto_total / Decimal(str(nro_cuotas))

            # Generar calendario
            calendario = []

            for i in range(nro_cuotas):
                numero_cuota = i + 1
                fecha_vencimiento = fecha_actual + timedelta(days=intervalo_dias * i)

                calendario.append(
                    {
                        "numero_cuota": numero_cuota,
                        "fecha_vencimiento": fecha_vencimiento.strftime("%Y-%m-%d"),
                        "monto_cuota": float(
                            monto_cuota
                        ),  # Convertir a float para serialización
                        "monto_cuota_decimal": monto_cuota,  # Mantener como Decimal para cálculos
                        "dias_desde_inicio": intervalo_dias * i,
                        "estado": "PENDIENTE",
                    }
                )

            return calendario

        except Exception as e:
            print(f"✗ Error generando calendario de pagos: {e}")
            return []

    def calcular_monto_cuota(self, plan_id: int, monto_total: Decimal) -> Decimal:
        """
        Calcula el monto de cada cuota basado en el plan

        Args:
            plan_id: ID del plan de pago
            monto_total: Monto total a distribuir

        Returns:
            Decimal: Monto por cuota
        """
        try:
            plan = self.read(plan_id)
            if not plan:
                return Decimal("0")

            nro_cuotas = plan["nro_cuotas"]
            if nro_cuotas <= 0:
                return Decimal("0")

            return monto_total / Decimal(str(nro_cuotas))

        except Exception as e:
            print(f"✗ Error calculando monto de cuota: {e}")
            return Decimal("0")

    def get_total_meses(self, plan_id: int) -> int:
        """
        Calcula el total de meses del plan

        Args:
            plan_id: ID del plan de pago

        Returns:
            int: Total de meses
        """
        try:
            plan = self.read(plan_id)
            if not plan:
                return 0

            nro_cuotas = plan["nro_cuotas"]
            intervalo_dias = plan["intervalo_dias"]

            # Calcular días totales y convertir a meses aproximados
            dias_totales = nro_cuotas * intervalo_dias
            meses_aproximados = dias_totales // 30  # Aproximación de 30 días por mes

            return max(1, meses_aproximados)  # Mínimo 1 mes

        except Exception as e:
            print(f"✗ Error calculando total de meses: {e}")
            return 0

    # ============ MÉTODOS PARA DASHBOARD ============

    def get_total_planes(
        self, programa_id: Optional[int] = None, active_only: bool = True
    ) -> int:
        """
        Obtiene el total de planes de pago

        Args:
            programa_id: Filtrar por programa específico
            active_only: Si es True, solo planes activos

        Returns:
            int: Número total de planes
        """
        try:
            query = f"SELECT COUNT(*) as total FROM {self.table_name}"
            conditions = []
            params = []

            if programa_id is not None:
                conditions.append("programa_id = %s")
                params.append(programa_id)

            if active_only:
                conditions.append("activo = TRUE")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            result = self.fetch_one(query, params)
            return result["total"] if result else 0

        except Exception as e:
            print(f"✗ Error obteniendo total de planes: {e}")
            return 0

    def get_planes_por_programa(self) -> List[Dict[str, Any]]:
        """
        Obtiene distribución de planes por programa

        Returns:
            List[Dict]: Distribución por programa
        """
        try:
            query = """
            SELECT 
                pa.nombre as programa_nombre,
                pa.codigo as programa_codigo,
                COUNT(pp.id) as cantidad_planes,
                SUM(CASE WHEN pp.activo = TRUE THEN 1 ELSE 0 END) as planes_activos
            FROM planes_pago pp
            JOIN programas_academicos pa ON pp.programa_id = pa.id
            GROUP BY pa.id, pa.nombre, pa.codigo
            ORDER BY cantidad_planes DESC
            """

            return self.fetch_all(query)

        except Exception as e:
            print(f"✗ Error obteniendo planes por programa: {e}")
            return []

    # ============ MÉTODOS DE VALIDACIÓN DE UNICIDAD ============

    def nombre_exists_en_programa(
        self, programa_id: int, nombre: str, exclude_id: Optional[int] = None
    ) -> bool:
        """
        Verifica si un nombre ya existe para un programa específico

        Args:
            programa_id: ID del programa
            nombre: Nombre a verificar
            exclude_id: ID a excluir (para actualizaciones)

        Returns:
            bool: True si existe, False en caso contrario
        """
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE programa_id = %s AND nombre = %s"
            params = [programa_id, nombre]

            if exclude_id is not None:
                query += " AND id != %s"
                params.append(exclude_id)

            result = self.fetch_one(query, params)
            return result["count"] > 0 if result else False

        except Exception as e:
            print(f"✗ Error verificando nombre en programa: {e}")
            return False

    def plan_exists(self, plan_id: int, active_only: bool = True) -> bool:
        """
        Verifica si un plan de pago existe

        Args:
            plan_id: ID del plan
            active_only: Si es True, solo verifica planes activos

        Returns:
            bool: True si existe, False en caso contrario
        """
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE id = %s"
            params = [plan_id]

            if active_only:
                query += " AND activo = TRUE"

            result = self.fetch_one(query, params)
            return result["count"] > 0 if result else False

        except Exception as e:
            print(f"✗ Error verificando existencia de plan: {e}")
            return False

    # ============ MÉTODOS DE COMPATIBILIDAD ============

    def obtener_todos(self):
        """Método de compatibilidad con nombres antiguos"""
        return self.get_all()

    def obtener_por_id(self, plan_id):
        """Método de compatibilidad con nombres antiguos"""
        return self.read(plan_id)

    def obtener_por_programa(self, programa_id):
        """Método de compatibilidad con nombres antiguos"""
        return self.get_by_programa(programa_id)

    def buscar_planes(self, termino):
        """Método de compatibilidad con nombres antiguos"""
        return self.search(termino)

    def update_table(self, table, data, condition, params=None):
        """Método helper para actualizar (compatibilidad con BaseModel)"""
        return self.update(table, data, condition, params)  # type: ignore

    # ============ MÉTODOS DE UTILIDAD ============

    def get_planes_disponibles(self, programa_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene planes de pago disponibles para un programa

        Args:
            programa_id: ID del programa

        Returns:
            List[Dict]: Planes disponibles
        """
        return self.get_by_programa(programa_id, active_only=True)

    def get_plan_default_programa(self, programa_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene el plan de pago por defecto para un programa

        Args:
            programa_id: ID del programa

        Returns:
            Optional[Dict]: Plan por defecto o None
        """
        try:
            query = f"""
            SELECT pp.*, 
                   pa.nombre as programa_nombre,
                   pa.codigo as programa_codigo
            FROM {self.table_name} pp
            JOIN programas_academicos pa ON pp.programa_id = pa.id
            WHERE pp.programa_id = %s 
              AND pp.activo = TRUE
              AND pp.nombre ILIKE '%contado%' OR pp.nro_cuotas = 1
            ORDER BY pp.nro_cuotas ASC, pp.created_at DESC
            LIMIT 1
            """

            result = self.fetch_one(query, (programa_id,))

            # Si no hay plan con "contado" o 1 cuota, obtener el primero activo
            if not result:
                planes = self.get_by_programa(programa_id, active_only=True)
                if planes:
                    return planes[0]

            return result

        except Exception as e:
            print(f"✗ Error obteniendo plan por defecto: {e}")
            return None
