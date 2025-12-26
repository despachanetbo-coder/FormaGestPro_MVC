# app/models/matricula_model.py - Versión optimizada y robusta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_model import BaseModel
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple, Union


class MatriculaModel(BaseModel):
    def __init__(self):
        """Inicializa el modelo de matrículas"""
        super().__init__()
        self.table_name = "matriculas"
        self.sequence_name = "seq_matriculas_id"

        # Tipos enumerados según la base de datos
        self.MODALIDADES_PAGO = ["CONTADO", "CUOTAS"]
        self.ESTADOS_PAGO = ["PENDIENTE", "PARCIAL", "PAGADO", "MOROSO", "CANCELADO"]
        self.ESTADOS_ACADEMICOS = [
            "PREINSCRITO",
            "INSCRITO",
            "EN_PROGRESO",
            "COMPLETADO",
            "APROBADO",
            "REPROBADO",
            "RETIRADO",
            "SUSPENDIDO",
        ]

        # Columnas de la tabla para validación
        self.columns = [
            "id",
            "estudiante_id",
            "programa_id",
            "modalidad_pago",
            "plan_pago_id",
            "monto_total",
            "descuento_aplicado",
            "monto_final",
            "monto_pagado",
            "estado_pago",
            "estado_academico",
            "fecha_matricula",
            "fecha_inicio",
            "fecha_conclusion",
            "coordinador_id",
            "observaciones",
        ]

        # Columnas requeridas
        self.required_columns = [
            "estudiante_id",
            "programa_id",
            "modalidad_pago",
            "monto_total",
            "monto_final",
        ]

        # Columnas de tipo decimal
        self.decimal_columns = [
            "monto_total",
            "descuento_aplicado",
            "monto_final",
            "monto_pagado",
        ]

        # Columnas de tipo entero
        self.integer_columns = [
            "estudiante_id",
            "programa_id",
            "plan_pago_id",
            "coordinador_id",
        ]

        # Columnas de tipo fecha
        self.date_columns = ["fecha_inicio", "fecha_conclusion"]

    # ============ MÉTODOS DE VALIDACIÓN ============

    def _validate_matricula_data(
        self, data: Dict[str, Any], for_update: bool = False
    ) -> Tuple[bool, str]:
        """
        Valida los datos de la matrícula

        Args:
            data: Diccionario con datos de la matrícula
            for_update: Si es True, valida para actualización

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        # Campos requeridos para creación
        if not for_update:
            for field in self.required_columns:
                if field not in data or data[field] is None:
                    return False, f"Campo requerido faltante: {field}"

        # Validar modalidad de pago
        if "modalidad_pago" in data and data["modalidad_pago"]:
            if data["modalidad_pago"] not in self.MODALIDADES_PAGO:
                return (
                    False,
                    f"Modalidad de pago inválida. Use: {', '.join(self.MODALIDADES_PAGO)}",
                )

        # Validar estado de pago si se proporciona
        if "estado_pago" in data and data["estado_pago"]:
            if data["estado_pago"] not in self.ESTADOS_PAGO:
                return (
                    False,
                    f"Estado de pago inválido. Use: {', '.join(self.ESTADOS_PAGO)}",
                )

        # Validar estado académico si se proporciona
        if "estado_academico" in data and data["estado_academico"]:
            if data["estado_academico"] not in self.ESTADOS_ACADEMICOS:
                return (
                    False,
                    f"Estado académico inválido. Use: {', '.join(self.ESTADOS_ACADEMICOS)}",
                )

        # Validar consistencia entre modalidad y plan de pago
        if "modalidad_pago" in data and "plan_pago_id" in data:
            if data["modalidad_pago"] == "CUOTAS" and not data["plan_pago_id"]:
                return False, "Modalidad CUOTAS requiere un plan de pago"
            elif data["modalidad_pago"] == "CONTADO" and data["plan_pago_id"]:
                return False, "Modalidad CONTADO no debe tener plan de pago"

        # Validar montos
        montos_a_validar = [
            "monto_total",
            "descuento_aplicado",
            "monto_final",
            "monto_pagado",
        ]
        for monto_field in montos_a_validar:
            if monto_field in data and data[monto_field] is not None:
                try:
                    monto = Decimal(str(data[monto_field]))
                    if monto < 0:
                        return False, f"{monto_field} no puede ser negativo"
                except (ValueError, TypeError):
                    return False, f"{monto_field} inválido"

        # Validar cálculo de monto final
        if (
            "monto_total" in data
            and "descuento_aplicado" in data
            and "monto_final" in data
        ):
            try:
                monto_total = Decimal(str(data.get("monto_total", 0)))
                descuento = Decimal(str(data.get("descuento_aplicado", 0)))
                monto_final = Decimal(str(data.get("monto_final", 0)))

                if monto_final != (monto_total - descuento):
                    return (
                        False,
                        "Monto final debe ser igual a monto_total - descuento_aplicado",
                    )
            except:
                pass  # Si hay error en conversión, ya fue validado arriba

        # Validar que monto pagado no exceda monto final
        if (
            "monto_pagado" in data
            and "monto_final" in data
            and data["monto_pagado"] is not None
        ):
            try:
                monto_pagado = Decimal(str(data["monto_pagado"]))
                monto_final = Decimal(str(data["monto_final"]))

                if monto_pagado > monto_final:
                    return False, "Monto pagado no puede exceder monto final"
            except:
                pass

        # Validar unicidad estudiante-programa
        if "estudiante_id" in data and "programa_id" in data:
            existing_id = None
            if for_update and "id" in data:
                existing_id = data["id"]

            if self.matricula_exists(
                data["estudiante_id"], data["programa_id"], exclude_id=existing_id
            ):
                return False, "El estudiante ya está matriculado en este programa"

        # Validar existencia de referencias
        if "estudiante_id" in data and data["estudiante_id"]:
            if not self._estudiante_exists(data["estudiante_id"]):
                return False, f"Estudiante con ID {data['estudiante_id']} no existe"

        if "programa_id" in data and data["programa_id"]:
            if not self._programa_exists(data["programa_id"]):
                return False, f"Programa con ID {data['programa_id']} no existe"

        if "plan_pago_id" in data and data["plan_pago_id"]:
            if not self._plan_pago_exists(data["plan_pago_id"]):
                return False, f"Plan de pago con ID {data['plan_pago_id']} no existe"

        if "coordinador_id" in data and data["coordinador_id"]:
            if not self._coordinador_exists(data["coordinador_id"]):
                return False, f"Coordinador con ID {data['coordinador_id']} no existe"

        # Validar fechas
        date_fields = ["fecha_inicio", "fecha_conclusion"]
        for field in date_fields:
            if field in data and data[field]:
                if not self._is_valid_date(data[field]):
                    return (
                        False,
                        f"Formato de fecha inválido en {field}. Use YYYY-MM-DD",
                    )

        # Validar relación entre fechas
        if (
            "fecha_inicio" in data
            and data["fecha_inicio"]
            and "fecha_conclusion" in data
            and data["fecha_conclusion"]
        ):
            try:
                fecha_inicio = datetime.strptime(
                    data["fecha_inicio"], "%Y-%m-%d"
                ).date()
                fecha_conclusion = datetime.strptime(
                    data["fecha_conclusion"], "%Y-%m-%d"
                ).date()

                if fecha_conclusion < fecha_inicio:
                    return (
                        False,
                        "Fecha de conclusión no puede ser anterior a fecha de inicio",
                    )
            except:
                pass

        return True, "Datos válidos"

    def _is_valid_date(self, date_value: Any) -> bool:
        """Valida formato de fecha"""
        if isinstance(date_value, str):
            try:
                datetime.strptime(date_value, "%Y-%m-%d")
                return True
            except ValueError:
                return False
        elif isinstance(date_value, (datetime, date)):
            return True
        return False

    def _estudiante_exists(self, estudiante_id: int) -> bool:
        """Verifica si el estudiante existe"""
        try:
            query = "SELECT COUNT(*) as count FROM estudiantes WHERE id = %s AND activo = TRUE"
            result = self.fetch_one(query, (estudiante_id,))
            return result["count"] > 0 if result else False
        except:
            return False

    def _programa_exists(self, programa_id: int) -> bool:
        """Verifica si el programa existe"""
        try:
            query = "SELECT COUNT(*) as count FROM programas_academicos WHERE id = %s"
            result = self.fetch_one(query, (programa_id,))
            return result["count"] > 0 if result else False
        except:
            return False

    def _plan_pago_exists(self, plan_pago_id: int) -> bool:
        """Verifica si el plan de pago existe"""
        try:
            query = "SELECT COUNT(*) as count FROM planes_pago WHERE id = %s AND activo = TRUE"
            result = self.fetch_one(query, (plan_pago_id,))
            return result["count"] > 0 if result else False
        except:
            return False

    def _coordinador_exists(self, coordinador_id: int) -> bool:
        """Verifica si el coordinador existe (asumiendo que es un docente)"""
        try:
            query = (
                "SELECT COUNT(*) as count FROM docentes WHERE id = %s AND activo = TRUE"
            )
            result = self.fetch_one(query, (coordinador_id,))
            return result["count"] > 0 if result else False
        except:
            return False

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza los datos de la matrícula

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
                # Convertir decimales
                elif key in self.decimal_columns and value is not None:
                    try:
                        sanitized[key] = Decimal(str(value))
                    except:
                        sanitized[key] = value
                # Convertir enteros
                elif key in self.integer_columns and value is not None:
                    try:
                        sanitized[key] = int(value)
                    except:
                        sanitized[key] = value
                # Mantener otros tipos
                else:
                    sanitized[key] = value

        return sanitized

    # ============ MÉTODOS CRUD PRINCIPALES ============

    def create(self, data: Dict[str, Any]) -> Optional[int]:
        """
        Crea una nueva matrícula

        Args:
            data: Diccionario con datos de la matrícula

        Returns:
            Optional[int]: ID de la matrícula creada o None si hay error
        """
        # Sanitizar y validar datos
        data = self._sanitize_data(data)
        is_valid, error_msg = self._validate_matricula_data(data, for_update=False)

        if not is_valid:
            print(f"✗ Error validando datos: {error_msg}")
            return None

        try:
            # Preparar datos para inserción
            insert_data = data.copy()

            # Establecer valores por defecto
            defaults = {
                "descuento_aplicado": Decimal("0"),
                "monto_pagado": Decimal("0"),
                "estado_pago": "PENDIENTE",
                "estado_academico": "PREINSCRITO",
                "fecha_matricula": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            for key, value in defaults.items():
                if key not in insert_data or insert_data[key] is None:
                    insert_data[key] = value

            # Insertar en base de datos
            result = self.insert(self.table_name, insert_data, returning="id")

            if result:
                print(f"✓ Matrícula creada exitosamente con ID: {result}")

                # Si hay plan de pago, verificar cupos disponibles
                if insert_data.get("plan_pago_id"):
                    self._actualizar_cupos_programa(insert_data["programa_id"], -1)

                return result

            return None

        except Exception as e:
            print(f"✗ Error creando matrícula: {e}")
            return None

    def read(self, matricula_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene una matrícula por su ID

        Args:
            matricula_id: ID de la matrícula

        Returns:
            Optional[Dict]: Datos de la matrícula o None si no existe
        """
        try:
            query = f"""
            SELECT m.*,
                   e.nombres as estudiante_nombres,
                   e.apellidos as estudiante_apellidos,
                   e.ci_numero as estudiante_ci,
                   p.nombre as programa_nombre,
                   p.codigo as programa_codigo,
                   pp.nombre as plan_pago_nombre,
                   d.nombres as coordinador_nombres,
                   d.apellidos as coordinador_apellidos
            FROM {self.table_name} m
            JOIN estudiantes e ON m.estudiante_id = e.id
            JOIN programas_academicos p ON m.programa_id = p.id
            LEFT JOIN planes_pago pp ON m.plan_pago_id = pp.id
            LEFT JOIN docentes d ON m.coordinador_id = d.id
            WHERE m.id = %s
            """

            result = self.fetch_one(query, (matricula_id,))
            return result

        except Exception as e:
            print(f"✗ Error obteniendo matrícula: {e}")
            return None

    def update(self, matricula_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza una matrícula existente

        Args:
            matricula_id: ID de la matrícula a actualizar
            data: Diccionario con datos a actualizar

        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        if not data:
            return False

        # Obtener datos actuales para validación
        matricula_actual = self.read(matricula_id)
        if not matricula_actual:
            return False

        # Combinar datos actuales con los nuevos para validación
        data_with_id = {**matricula_actual, **data}
        data_with_id["id"] = matricula_id

        # Sanitizar y validar datos
        data = self._sanitize_data(data)
        is_valid, error_msg = self._validate_matricula_data(
            data_with_id, for_update=True
        )

        if not is_valid:
            print(f"✗ Error validando datos: {error_msg}")
            return False

        try:
            # Actualizar en base de datos
            result = self.update_table(
                self.table_name, data, "id = %s", (matricula_id,)
            )

            if result:
                print(f"✓ Matrícula {matricula_id} actualizada exitosamente")

                # Actualizar estado de pago automáticamente si cambia monto_pagado
                if "monto_pagado" in data:
                    self._actualizar_estado_pago_automatico(matricula_id)

                return True

            return False

        except Exception as e:
            print(f"✗ Error actualizando matrícula: {e}")
            return False

    def delete(self, matricula_id: int) -> bool:
        """
        Elimina una matrícula

        Args:
            matricula_id: ID de la matrícula

        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            # Obtener datos de la matrícula para liberar cupos
            matricula = self.read(matricula_id)

            query = f"DELETE FROM {self.table_name} WHERE id = %s"
            result = self.execute_query(query, (matricula_id,), commit=True)

            if result:
                print(f"✓ Matrícula {matricula_id} eliminada exitosamente")

                # Liberar cupo si existe
                if matricula and matricula.get("plan_pago_id"):
                    self._actualizar_cupos_programa(matricula["programa_id"], 1)

                return True

            return False

        except Exception as e:
            print(f"✗ Error eliminando matrícula: {e}")
            return False

    # ============ MÉTODOS DE CONSULTA AVANZADOS ============

    def get_all(
        self,
        estudiante_id: Optional[int] = None,
        programa_id: Optional[int] = None,
        estado_pago: Optional[str] = None,
        estado_academico: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "fecha_matricula",
        order_desc: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todas las matrículas

        Args:
            estudiante_id: Filtrar por estudiante específico
            programa_id: Filtrar por programa específico
            estado_pago: Filtrar por estado de pago
            estado_academico: Filtrar por estado académico
            limit: Límite de registros
            offset: Desplazamiento para paginación
            order_by: Campo para ordenar
            order_desc: Si es True, orden descendente

        Returns:
            List[Dict]: Lista de matrículas
        """
        try:
            query = f"""
            SELECT m.*,
                   e.nombres as estudiante_nombres,
                   e.apellidos as estudiante_apellidos,
                   p.nombre as programa_nombre,
                   p.codigo as programa_codigo
            FROM {self.table_name} m
            JOIN estudiantes e ON m.estudiante_id = e.id
            JOIN programas_academicos p ON m.programa_id = p.id
            """

            conditions = []
            params = []

            if estudiante_id is not None:
                conditions.append("m.estudiante_id = %s")
                params.append(estudiante_id)

            if programa_id is not None:
                conditions.append("m.programa_id = %s")
                params.append(programa_id)

            if estado_pago is not None:
                conditions.append("m.estado_pago = %s")
                params.append(estado_pago)

            if estado_academico is not None:
                conditions.append("m.estado_academico = %s")
                params.append(estado_academico)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            # Ordenar
            order_dir = "DESC" if order_desc else "ASC"
            query += f" ORDER BY m.{order_by} {order_dir}"

            # Paginación
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            return self.fetch_all(query, params)

        except Exception as e:
            print(f"✗ Error obteniendo matrículas: {e}")
            return []

    def get_by_estudiante(self, estudiante_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene matrículas por estudiante

        Args:
            estudiante_id: ID del estudiante

        Returns:
            List[Dict]: Lista de matrículas del estudiante
        """
        return self.get_all(estudiante_id=estudiante_id)

    def get_by_programa(self, programa_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene matrículas por programa

        Args:
            programa_id: ID del programa

        Returns:
            List[Dict]: Lista de matrículas del programa
        """
        return self.get_all(programa_id=programa_id)

    def search(
        self,
        search_term: str,
        estado_pago: Optional[str] = None,
        estado_academico: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Busca matrículas por término de búsqueda

        Args:
            search_term: Término a buscar
            estado_pago: Filtrar por estado de pago
            estado_academico: Filtrar por estado académico

        Returns:
            List[Dict]: Lista de matrículas que coinciden
        """
        try:
            query = f"""
            SELECT m.*,
                   e.nombres as estudiante_nombres,
                   e.apellidos as estudiante_apellidos,
                   e.ci_numero as estudiante_ci,
                   p.nombre as programa_nombre,
                   p.codigo as programa_codigo
            FROM {self.table_name} m
            JOIN estudiantes e ON m.estudiante_id = e.id
            JOIN programas_academicos p ON m.programa_id = p.id
            WHERE (e.ci_numero ILIKE %s 
                   OR e.nombres ILIKE %s 
                   OR e.apellidos ILIKE %s
                   OR p.nombre ILIKE %s 
                   OR p.codigo ILIKE %s)
            """

            params = [
                f"%{search_term}%",
                f"%{search_term}%",
                f"%{search_term}%",
                f"%{search_term}%",
                f"%{search_term}%",
            ]

            if estado_pago is not None:
                query += " AND m.estado_pago = %s"
                params.append(estado_pago)

            if estado_academico is not None:
                query += " AND m.estado_academico = %s"
                params.append(estado_academico)

            query += " ORDER BY m.fecha_matricula DESC"

            return self.fetch_all(query, params)

        except Exception as e:
            print(f"✗ Error buscando matrículas: {e}")
            return []

    # ============ MÉTODOS DE GESTIÓN DE ESTADOS ============

    def cambiar_estado_pago(self, matricula_id: int, nuevo_estado: str) -> bool:
        """
        Cambia el estado de pago de una matrícula

        Args:
            matricula_id: ID de la matrícula
            nuevo_estado: Nuevo estado de pago

        Returns:
            bool: True si se cambió correctamente
        """
        if nuevo_estado not in self.ESTADOS_PAGO:
            print(f"✗ Estado de pago inválido: {nuevo_estado}")
            return False

        try:
            data = {"estado_pago": nuevo_estado}
            return self.update(matricula_id, data)

        except Exception as e:
            print(f"✗ Error cambiando estado de pago: {e}")
            return False

    def cambiar_estado_academico(self, matricula_id: int, nuevo_estado: str) -> bool:
        """
        Cambia el estado académico de una matrícula

        Args:
            matricula_id: ID de la matrícula
            nuevo_estado: Nuevo estado académico

        Returns:
            bool: True si se cambió correctamente
        """
        if nuevo_estado not in self.ESTADOS_ACADEMICOS:
            print(f"✗ Estado académico inválido: {nuevo_estado}")
            return False

        try:
            data = {"estado_academico": nuevo_estado}

            # Si se marca como COMPLETADO o APROBADO y no tiene fecha_conclusion, establecerla
            if nuevo_estado in ["COMPLETADO", "APROBADO"]:
                matricula = self.read(matricula_id)
                if matricula and not matricula.get("fecha_conclusion"):
                    data["fecha_conclusion"] = date.today().strftime("%Y-%m-%d")

            return self.update(matricula_id, data)

        except Exception as e:
            print(f"✗ Error cambiando estado académico: {e}")
            return False

    def registrar_pago(self, matricula_id: int, monto_pagado: Decimal) -> bool:
        """
        Registra un pago en la matrícula

        Args:
            matricula_id: ID de la matrícula
            monto_pagado: Monto pagado a registrar

        Returns:
            bool: True si se registró correctamente
        """
        try:
            # Obtener matrícula actual
            matricula = self.read(matricula_id)
            if not matricula:
                return False

            # Calcular nuevo monto pagado
            monto_actual = Decimal(str(matricula["monto_pagado"]))
            monto_final = Decimal(str(matricula["monto_final"]))
            nuevo_monto = monto_actual + monto_pagado

            # Validar que no exceda el monto final
            if nuevo_monto > monto_final:
                print(
                    f"✗ El pago excede el monto final. Máximo permitido: {monto_final - monto_actual}"
                )
                return False

            data = {"monto_pagado": float(nuevo_monto)}  # Convertir a float para la BD

            return self.update(matricula_id, data)

        except Exception as e:
            print(f"✗ Error registrando pago: {e}")
            return False

    def _actualizar_estado_pago_automatico(self, matricula_id: int) -> bool:
        """
        Actualiza automáticamente el estado de pago basado en el monto pagado

        Args:
            matricula_id: ID de la matrícula

        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            matricula = self.read(matricula_id)
            if not matricula:
                return False

            monto_pagado = Decimal(str(matricula["monto_pagado"]))
            monto_final = Decimal(str(matricula["monto_final"]))

            nuevo_estado = "PENDIENTE"

            if monto_pagado == 0:
                nuevo_estado = "PENDIENTE"
            elif monto_pagado >= monto_final:
                nuevo_estado = "PAGADO"
            elif monto_pagado > 0:
                nuevo_estado = "PARCIAL"

            # Solo actualizar si cambió
            if nuevo_estado != matricula["estado_pago"]:
                return self.cambiar_estado_pago(matricula_id, nuevo_estado)

            return True

        except Exception as e:
            print(f"✗ Error actualizando estado de pago automático: {e}")
            return False

    # ============ MÉTODOS PARA DASHBOARD ============

    def get_total_matriculas(
        self,
        programa_id: Optional[int] = None,
        estado_pago: Optional[str] = None,
        estado_academico: Optional[str] = None,
    ) -> int:
        """
        Obtiene el total de matrículas

        Args:
            programa_id: Filtrar por programa específico
            estado_pago: Filtrar por estado de pago
            estado_academico: Filtrar por estado académico

        Returns:
            int: Número total de matrículas
        """
        try:
            query = f"SELECT COUNT(*) as total FROM {self.table_name}"
            conditions = []
            params = []

            if programa_id is not None:
                conditions.append("programa_id = %s")
                params.append(programa_id)

            if estado_pago is not None:
                conditions.append("estado_pago = %s")
                params.append(estado_pago)

            if estado_academico is not None:
                conditions.append("estado_academico = %s")
                params.append(estado_academico)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            result = self.fetch_one(query, params)
            return result["total"] if result else 0

        except Exception as e:
            print(f"✗ Error obteniendo total de matrículas: {e}")
            return 0

    def get_estadisticas_pagos(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de pagos de matrículas

        Returns:
            Dict: Estadísticas de pagos
        """
        try:
            query = """
            SELECT 
                COUNT(*) as total_matriculas,
                SUM(monto_final) as monto_total_esperado,
                SUM(monto_pagado) as monto_total_pagado,
                AVG(monto_final) as monto_promedio,
                COUNT(CASE WHEN estado_pago = 'PAGADO' THEN 1 END) as pagadas_completas,
                COUNT(CASE WHEN estado_pago = 'PARCIAL' THEN 1 END) as pagadas_parciales,
                COUNT(CASE WHEN estado_pago = 'PENDIENTE' THEN 1 END) as pendientes,
                COUNT(CASE WHEN estado_pago = 'MOROSO' THEN 1 END) as morosas
            FROM matriculas
            """

            result = self.fetch_one(query)
            if result:
                # Calcular porcentajes
                total = result["total_matriculas"] or 0

                return {
                    "total_matriculas": total,
                    "monto_total_esperado": float(result["monto_total_esperado"] or 0),
                    "monto_total_pagado": float(result["monto_total_pagado"] or 0),
                    "monto_promedio": float(result["monto_promedio"] or 0),
                    "monto_pendiente": float(
                        (result["monto_total_esperado"] or 0)
                        - (result["monto_total_pagado"] or 0)
                    ),
                    "pagadas_completas": result["pagadas_completas"] or 0,
                    "pagadas_parciales": result["pagadas_parciales"] or 0,
                    "pendientes": result["pendientes"] or 0,
                    "morosas": result["morosas"] or 0,
                    "porcentaje_pagado": (
                        ((result["pagadas_completas"] or 0) / total * 100)
                        if total > 0
                        else 0
                    ),
                }

            return {}

        except Exception as e:
            print(f"✗ Error obteniendo estadísticas de pagos: {e}")
            return {}

    def get_matriculas_por_estado(self) -> List[Dict[str, Any]]:
        """
        Obtiene distribución de matrículas por estado académico

        Returns:
            List[Dict]: Distribución por estado
        """
        try:
            query = """
            SELECT 
                estado_academico,
                COUNT(*) as cantidad,
                AVG(monto_final) as monto_promedio,
                SUM(monto_final) as monto_total
            FROM matriculas
            GROUP BY estado_academico
            ORDER BY cantidad DESC
            """

            return self.fetch_all(query)

        except Exception as e:
            print(f"✗ Error obteniendo matrículas por estado: {e}")
            return []

    def get_matriculas_por_mes(
        self, year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene matrículas por mes

        Args:
            year: Año específico (None para año actual)

        Returns:
            List[Dict]: Matrículas por mes
        """
        try:
            if year is None:
                year = datetime.now().year

            query = """
            SELECT 
                EXTRACT(MONTH FROM fecha_matricula) as mes,
                COUNT(*) as cantidad,
                SUM(monto_final) as monto_total
            FROM matriculas
            WHERE EXTRACT(YEAR FROM fecha_matricula) = %s
            GROUP BY EXTRACT(MONTH FROM fecha_matricula)
            ORDER BY mes
            """

            return self.fetch_all(query, (year,))

        except Exception as e:
            print(f"✗ Error obteniendo matrículas por mes: {e}")
            return []

    # ============ MÉTODOS DE GESTIÓN DE CUPOS ============

    def _actualizar_cupos_programa(self, programa_id: int, cambio: int) -> bool:
        """
        Actualiza los cupos disponibles del programa

        Args:
            programa_id: ID del programa
            cambio: Cantidad a cambiar (negativo para reducir, positivo para aumentar)

        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            query = """
            UPDATE programas_academicos 
            SET cupos_disponibles = cupos_disponibles + %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """

            result = self.execute_query(query, (cambio, programa_id), commit=True)
            return result is not None

        except Exception as e:
            print(f"✗ Error actualizando cupos del programa: {e}")
            return False

    # ============ MÉTODOS DE VALIDACIÓN DE UNICIDAD ============

    def matricula_exists(
        self, estudiante_id: int, programa_id: int, exclude_id: Optional[int] = None
    ) -> bool:
        """
        Verifica si ya existe una matrícula para el estudiante en el programa

        Args:
            estudiante_id: ID del estudiante
            programa_id: ID del programa
            exclude_id: ID a excluir (para actualizaciones)

        Returns:
            bool: True si existe, False en caso contrario
        """
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE estudiante_id = %s AND programa_id = %s"
            params = [estudiante_id, programa_id]

            if exclude_id is not None:
                query += " AND id != %s"
                params.append(exclude_id)

            result = self.fetch_one(query, params)
            return result["count"] > 0 if result else False

        except Exception as e:
            print(f"✗ Error verificando matrícula: {e}")
            return False

    # ============ MÉTODOS DE COMPATIBILIDAD ============

    def obtener_todos(self):
        """Método de compatibilidad con nombres antiguos"""
        return self.get_all()

    def obtener_por_id(self, matricula_id):
        """Método de compatibilidad con nombres antiguos"""
        return self.read(matricula_id)

    def obtener_por_estudiante(self, estudiante_id):
        """Método de compatibilidad con nombres antiguos"""
        return self.get_by_estudiante(estudiante_id)

    def buscar_matriculas(self, termino):
        """Método de compatibilidad con nombres antiguos"""
        return self.search(termino)

    def update_table(self, table, data, condition, params=None):
        """Método helper para actualizar (compatibilidad con BaseModel)"""
        return self.update(table, data, condition, params)  # type: ignore

    # ============ MÉTODOS DE UTILIDAD ============

    def get_modalidades_pago(self) -> List[str]:
        """
        Obtiene la lista de modalidades de pago

        Returns:
            List[str]: Lista de modalidades
        """
        return self.MODALIDADES_PAGO.copy()

    def get_estados_pago(self) -> List[str]:
        """
        Obtiene la lista de estados de pago

        Returns:
            List[str]: Lista de estados
        """
        return self.ESTADOS_PAGO.copy()

    def get_estados_academicos(self) -> List[str]:
        """
        Obtiene la lista de estados académicos

        Returns:
            List[str]: Lista de estados
        """
        return self.ESTADOS_ACADEMICOS.copy()
