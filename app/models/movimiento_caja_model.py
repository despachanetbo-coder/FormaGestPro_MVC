# app/models/movimiento_caja_model.py - Versión optimizada y robusta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_model import BaseModel
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple, Union


class MovimientoCajaModel(BaseModel):
    def __init__(self):
        """Inicializa el modelo de movimientos de caja"""
        super().__init__()
        self.table_name = "movimientos_caja"
        self.sequence_name = "seq_movimientos_caja_id"

        # Tipos enumerados según la base de datos
        self.TIPOS_MOVIMIENTO = ["INGRESO", "GASTO", "SALDO_INICIAL", "AJUSTE"]
        self.TIPOS_ORIGEN = ["INGRESO", "GASTO"]

        # Columnas de la tabla para validación
        self.columns = [
            "id",
            "fecha",
            "tipo",
            "monto",
            "origen_tipo",
            "origen_id",
            "descripcion",
            "registrado_por",
        ]

        # Columnas requeridas
        self.required_columns = ["fecha", "tipo", "monto", "descripcion"]

        # Columnas de tipo decimal
        self.decimal_columns = ["monto"]

        # Columnas de tipo entero
        self.integer_columns = ["origen_id", "registrado_por"]

        # Columnas de tipo fecha
        self.date_columns = ["fecha"]

    # ============ MÉTODOS DE VALIDACIÓN ============

    def _validate_movimiento_data(
        self, data: Dict[str, Any], for_update: bool = False
    ) -> Tuple[bool, str]:
        """
        Valida los datos del movimiento de caja

        Args:
            data: Diccionario con datos del movimiento
            for_update: Si es True, valida para actualización

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        # Campos requeridos para creación
        if not for_update:
            for field in self.required_columns:
                if field not in data or data[field] is None:
                    return False, f"Campo requerido faltante: {field}"

        # Validar tipo de movimiento
        if "tipo" in data and data["tipo"]:
            if data["tipo"] not in self.TIPOS_MOVIMIENTO:
                return (
                    False,
                    f"Tipo de movimiento inválido. Use: {', '.join(self.TIPOS_MOVIMIENTO)}",
                )

        # Validar tipo de origen si se proporciona
        if "origen_tipo" in data and data["origen_tipo"]:
            if data["origen_tipo"] not in self.TIPOS_ORIGEN:
                return (
                    False,
                    f"Tipo de origen inválido. Use: {', '.join(self.TIPOS_ORIGEN)}",
                )

            # Si hay tipo de origen, debe haber origen_id
            if "origen_id" not in data or not data["origen_id"]:
                return (
                    False,
                    "Si se especifica origen_tipo, debe especificarse origen_id",
                )

        # Validar monto positivo
        if "monto" in data and data["monto"] is not None:
            try:
                monto = Decimal(str(data["monto"]))
                if monto <= 0:
                    return False, "El monto debe ser mayor a 0"
            except (ValueError, TypeError):
                return False, "Monto inválido. Debe ser un número decimal positivo"

        # Validar unicidad origen_tipo/origen_id si se proporcionan
        if (
            "origen_tipo" in data
            and data["origen_tipo"]
            and "origen_id" in data
            and data["origen_id"]
        ):
            existing_id = None
            if for_update and "id" in data:
                existing_id = data["id"]

            if self.origen_exists(
                data["origen_tipo"], data["origen_id"], exclude_id=existing_id
            ):
                return (
                    False,
                    f"Ya existe un movimiento para el origen {data['origen_tipo']} con ID {data['origen_id']}",
                )

        # Validar usuario registrador si se proporciona
        if "registrado_por" in data and data["registrado_por"]:
            if not self._usuario_exists(data["registrado_por"]):
                return False, f"Usuario con ID {data['registrado_por']} no existe"

        # Validar fecha si se proporciona
        if "fecha" in data and data["fecha"]:
            if not self._is_valid_datetime(data["fecha"]):
                return False, "Formato de fecha inválido. Use YYYY-MM-DD HH:MM:SS"

            # No permitir fechas futuras para movimientos
            try:
                fecha_mov = (
                    datetime.strptime(data["fecha"], "%Y-%m-%d %H:%M:%S")
                    if isinstance(data["fecha"], str)
                    else data["fecha"]
                )
                if fecha_mov > datetime.now() + timedelta(days=1):  # Margen de 1 día
                    return False, "No se pueden registrar movimientos con fecha futura"
            except:
                pass

        return True, "Datos válidos"

    def _is_valid_datetime(self, datetime_value: Any) -> bool:
        """Valida formato de fecha y hora"""
        if isinstance(datetime_value, str):
            try:
                # Intentar diferentes formatos
                formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"]
                for fmt in formats:
                    try:
                        datetime.strptime(datetime_value, fmt)
                        return True
                    except ValueError:
                        continue
                return False
            except ValueError:
                return False
        elif isinstance(datetime_value, (datetime, date)):
            return True
        return False

    def _usuario_exists(self, usuario_id: int) -> bool:
        """Verifica si el usuario existe"""
        try:
            query = (
                "SELECT COUNT(*) as count FROM usuarios WHERE id = %s AND activo = TRUE"
            )
            result = self.fetch_one(query, (usuario_id,))
            return result["count"] > 0 if result else False
        except:
            return False

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza los datos del movimiento

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
                # Formatear fecha
                elif key in self.date_columns and value is not None:
                    if isinstance(value, str):
                        sanitized[key] = value
                    elif isinstance(value, datetime):
                        sanitized[key] = value.strftime("%Y-%m-%d %H:%M:%S")
                    elif isinstance(value, date):
                        sanitized[key] = value.strftime("%Y-%m-%d 00:00:00")
                # Mantener otros tipos
                else:
                    sanitized[key] = value

        return sanitized

    # ============ MÉTODOS CRUD PRINCIPALES ============

    def create(
        self, data: Dict[str, Any], usuario_id: Optional[int] = None
    ) -> Optional[int]:
        """
        Crea un nuevo movimiento de caja

        Args:
            data: Diccionario con datos del movimiento
            usuario_id: ID del usuario que registra el movimiento

        Returns:
            Optional[int]: ID del movimiento creado o None si hay error
        """
        # Sanitizar y validar datos
        data = self._sanitize_data(data)

        # Añadir usuario registrador si se proporciona
        if usuario_id:
            data["registrado_por"] = usuario_id

        is_valid, error_msg = self._validate_movimiento_data(data, for_update=False)

        if not is_valid:
            print(f"✗ Error validando datos: {error_msg}")
            return None

        try:
            # Preparar datos para inserción
            insert_data = data.copy()

            # Establecer valores por defecto
            defaults = {"fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

            for key, value in defaults.items():
                if key not in insert_data or insert_data[key] is None:
                    insert_data[key] = value

            # Insertar en base de datos
            result = self.insert(self.table_name, insert_data, returning="id")

            if result:
                print(f"✓ Movimiento de caja creado exitosamente con ID: {result}")

                # Registrar en log de auditoría
                self._registrar_auditoria("CREACION", result, usuario_id)

                return result

            return None

        except Exception as e:
            print(f"✗ Error creando movimiento de caja: {e}")
            return None

    def read(self, movimiento_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un movimiento de caja por su ID

        Args:
            movimiento_id: ID del movimiento

        Returns:
            Optional[Dict]: Datos del movimiento o None si no existe
        """
        try:
            query = f"""
            SELECT mc.*,
                   u.username as registrado_por_usuario,
                   u.nombre_completo as registrado_por_nombre
            FROM {self.table_name} mc
            LEFT JOIN usuarios u ON mc.registrado_por = u.id
            WHERE mc.id = %s
            """

            result = self.fetch_one(query, (movimiento_id,))
            return result

        except Exception as e:
            print(f"✗ Error obteniendo movimiento de caja: {e}")
            return None

    def update(
        self, movimiento_id: int, data: Dict[str, Any], usuario_id: Optional[int] = None
    ) -> bool:
        """
        Actualiza un movimiento de caja existente

        Args:
            movimiento_id: ID del movimiento a actualizar
            data: Diccionario con datos a actualizar
            usuario_id: ID del usuario que realiza la actualización

        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        if not data:
            return False

        # Obtener datos actuales para validación
        movimiento_actual = self.read(movimiento_id)
        if not movimiento_actual:
            return False

        # Combinar datos actuales con los nuevos para validación
        data_with_id = {**movimiento_actual, **data}
        data_with_id["id"] = movimiento_id

        # Sanitizar y validar datos
        data = self._sanitize_data(data)
        is_valid, error_msg = self._validate_movimiento_data(
            data_with_id, for_update=True
        )

        if not is_valid:
            print(f"✗ Error validando datos: {error_msg}")
            return False

        try:
            # No permitir actualizar movimientos muy antiguos (excepto para administradores)
            # Esta validación se podría hacer basada en roles en una implementación completa

            # Actualizar en base de datos
            result = self.update_table(
                self.table_name, data, "id = %s", (movimiento_id,)
            )

            if result:
                print(f"✓ Movimiento de caja {movimiento_id} actualizado exitosamente")

                # Registrar en log de auditoría
                self._registrar_auditoria("ACTUALIZACION", movimiento_id, usuario_id)

                return True

            return False

        except Exception as e:
            print(f"✗ Error actualizando movimiento de caja: {e}")
            return False

    def delete(self, movimiento_id: int, usuario_id: Optional[int] = None) -> bool:
        """
        Elimina un movimiento de caja

        Args:
            movimiento_id: ID del movimiento
            usuario_id: ID del usuario que realiza la eliminación

        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            # Verificar si el movimiento puede ser eliminado
            movimiento = self.read(movimiento_id)
            if not movimiento:
                return False

            # No permitir eliminar movimientos muy antiguos
            fecha_mov = datetime.strptime(movimiento["fecha"], "%Y-%m-%d %H:%M:%S")
            dias_diferencia = (datetime.now() - fecha_mov).days

            if (
                dias_diferencia > 30
            ):  # No permitir eliminar movimientos de más de 30 días
                print("✗ No se pueden eliminar movimientos de más de 30 días")
                return False

            # Registrar en log de auditoría antes de eliminar
            self._registrar_auditoria("ELIMINACION", movimiento_id, usuario_id)

            query = f"DELETE FROM {self.table_name} WHERE id = %s"
            result = self.execute_query(query, (movimiento_id,), commit=True)

            if result:
                print(f"✓ Movimiento de caja {movimiento_id} eliminado exitosamente")
                return True

            return False

        except Exception as e:
            print(f"✗ Error eliminando movimiento de caja: {e}")
            return False

    # ============ MÉTODOS DE CONSULTA AVANZADOS ============

    def get_all(
        self,
        tipo: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        origen_tipo: Optional[str] = None,
        registrado_por: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "fecha",
        order_desc: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todos los movimientos de caja

        Args:
            tipo: Filtrar por tipo de movimiento
            fecha_desde: Fecha inicial (YYYY-MM-DD)
            fecha_hasta: Fecha final (YYYY-MM-DD)
            origen_tipo: Filtrar por tipo de origen
            registrado_por: Filtrar por usuario que registró
            limit: Límite de registros
            offset: Desplazamiento para paginación
            order_by: Campo para ordenar
            order_desc: Si es True, orden descendente

        Returns:
            List[Dict]: Lista de movimientos
        """
        try:
            query = f"""
            SELECT mc.*,
                   u.username as registrado_por_usuario,
                   u.nombre_completo as registrado_por_nombre
            FROM {self.table_name} mc
            LEFT JOIN usuarios u ON mc.registrado_por = u.id
            """

            conditions = []
            params = []

            if tipo is not None:
                conditions.append("mc.tipo = %s")
                params.append(tipo)

            if fecha_desde is not None:
                conditions.append("DATE(mc.fecha) >= %s")
                params.append(fecha_desde)

            if fecha_hasta is not None:
                conditions.append("DATE(mc.fecha) <= %s")
                params.append(fecha_hasta)

            if origen_tipo is not None:
                conditions.append("mc.origen_tipo = %s")
                params.append(origen_tipo)

            if registrado_por is not None:
                conditions.append("mc.registrado_por = %s")
                params.append(registrado_por)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            # Ordenar
            order_dir = "DESC" if order_desc else "ASC"
            query += f" ORDER BY mc.{order_by} {order_dir}"

            # Paginación
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            return self.fetch_all(query, params)

        except Exception as e:
            print(f"✗ Error obteniendo movimientos de caja: {e}")
            return []

    def get_ingresos(
        self, fecha_desde: Optional[str] = None, fecha_hasta: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todos los ingresos de caja

        Args:
            fecha_desde: Fecha inicial (YYYY-MM-DD)
            fecha_hasta: Fecha final (YYYY-MM-DD)

        Returns:
            List[Dict]: Lista de ingresos
        """
        return self.get_all(
            tipo="INGRESO", fecha_desde=fecha_desde, fecha_hasta=fecha_hasta
        )

    def get_gastos(
        self, fecha_desde: Optional[str] = None, fecha_hasta: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todos los gastos de caja

        Args:
            fecha_desde: Fecha inicial (YYYY-MM-DD)
            fecha_hasta: Fecha final (YYYY-MM-DD)

        Returns:
            List[Dict]: Lista de gastos
        """
        return self.get_all(
            tipo="GASTO", fecha_desde=fecha_desde, fecha_hasta=fecha_hasta
        )

    def get_by_fecha(self, fecha: str) -> List[Dict[str, Any]]:
        """
        Obtiene movimientos por fecha específica

        Args:
            fecha: Fecha a consultar (YYYY-MM-DD)

        Returns:
            List[Dict]: Lista de movimientos de la fecha
        """
        return self.get_all(fecha_desde=fecha, fecha_hasta=fecha)

    def get_by_origen(
        self, origen_tipo: str, origen_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene un movimiento por su origen

        Args:
            origen_tipo: Tipo de origen
            origen_id: ID del origen

        Returns:
            Optional[Dict]: Movimiento asociado al origen
        """
        try:
            query = f"""
            SELECT mc.*,
                   u.username as registrado_por_usuario,
                   u.nombre_completo as registrado_por_nombre
            FROM {self.table_name} mc
            LEFT JOIN usuarios u ON mc.registrado_por = u.id
            WHERE mc.origen_tipo = %s AND mc.origen_id = %s
            """

            result = self.fetch_one(query, (origen_tipo, origen_id))
            return result

        except Exception as e:
            print(f"✗ Error obteniendo movimiento por origen: {e}")
            return None

    def search(
        self,
        search_term: str,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Busca movimientos por término de búsqueda

        Args:
            search_term: Término a buscar
            fecha_desde: Fecha inicial (YYYY-MM-DD)
            fecha_hasta: Fecha final (YYYY-MM-DD)

        Returns:
            List[Dict]: Lista de movimientos que coinciden
        """
        try:
            query = f"""
            SELECT mc.*,
                   u.username as registrado_por_usuario,
                   u.nombre_completo as registrado_por_nombre
            FROM {self.table_name} mc
            LEFT JOIN usuarios u ON mc.registrado_por = u.id
            WHERE mc.descripcion ILIKE %s
            """

            params = [f"%{search_term}%"]

            if fecha_desde is not None:
                query += " AND DATE(mc.fecha) >= %s"
                params.append(fecha_desde)

            if fecha_hasta is not None:
                query += " AND DATE(mc.fecha) <= %s"
                params.append(fecha_hasta)

            query += " ORDER BY mc.fecha DESC"

            return self.fetch_all(query, params)

        except Exception as e:
            print(f"✗ Error buscando movimientos: {e}")
            return []

    # ============ MÉTODOS DE CÁLCULO Y REPORTES ============

    def calcular_saldo(self, fecha_corte: Optional[str] = None) -> Dict[str, Any]:
        """
        Calcula el saldo de caja hasta una fecha específica

        Args:
            fecha_corte: Fecha de corte (YYYY-MM-DD), None para fecha actual

        Returns:
            Dict: Estadísticas de saldo
        """
        try:
            # Construir consulta base
            query_base = f"""
            SELECT 
                COALESCE(SUM(CASE WHEN tipo = 'INGRESO' THEN monto ELSE 0 END), 0) as total_ingresos,
                COALESCE(SUM(CASE WHEN tipo = 'GASTO' THEN monto ELSE 0 END), 0) as total_gastos,
                COALESCE(SUM(CASE WHEN tipo = 'SALDO_INICIAL' THEN monto ELSE 0 END), 0) as saldo_inicial,
                COUNT(*) as total_movimientos
            FROM {self.table_name}
            """

            params = []

            if fecha_corte:
                query_base += " WHERE DATE(fecha) <= %s"
                params.append(fecha_corte)

            result = self.fetch_one(query_base, params)

            if result:
                total_ingresos = Decimal(str(result["total_ingresos"]))
                total_gastos = Decimal(str(result["total_gastos"]))
                saldo_inicial = Decimal(str(result["saldo_inicial"]))

                saldo_actual = saldo_inicial + total_ingresos - total_gastos

                return {
                    "saldo_inicial": float(saldo_inicial),
                    "total_ingresos": float(total_ingresos),
                    "total_gastos": float(total_gastos),
                    "saldo_actual": float(saldo_actual),
                    "total_movimientos": result["total_movimientos"],
                    "fecha_corte": fecha_corte or datetime.now().strftime("%Y-%m-%d"),
                }

            return {
                "saldo_inicial": 0.0,
                "total_ingresos": 0.0,
                "total_gastos": 0.0,
                "saldo_actual": 0.0,
                "total_movimientos": 0,
                "fecha_corte": fecha_corte or datetime.now().strftime("%Y-%m-%d"),
            }

        except Exception as e:
            print(f"✗ Error calculando saldo: {e}")
            return {
                "saldo_inicial": 0.0,
                "total_ingresos": 0.0,
                "total_gastos": 0.0,
                "saldo_actual": 0.0,
                "total_movimientos": 0,
                "fecha_corte": fecha_corte or datetime.now().strftime("%Y-%m-%d"),
            }

    def get_resumen_por_dia(self, fecha: str) -> Dict[str, Any]:
        """
        Obtiene resumen de movimientos por día

        Args:
            fecha: Fecha a consultar (YYYY-MM-DD)

        Returns:
            Dict: Resumen del día
        """
        try:
            query = f"""
            SELECT 
                tipo,
                COUNT(*) as cantidad,
                SUM(monto) as total
            FROM {self.table_name}
            WHERE DATE(fecha) = %s
            GROUP BY tipo
            ORDER BY tipo
            """

            resultados = self.fetch_all(query, (fecha,))

            # Procesar resultados
            resumen = {
                "fecha": fecha,
                "ingresos": 0.0,
                "gastos": 0.0,
                "otros": 0.0,
                "total_movimientos": 0,
                "detalle": {},
            }

            for row in resultados:
                tipo = row["tipo"]
                total = float(row["total"])
                cantidad = row["cantidad"]

                resumen["detalle"][tipo] = {"total": total, "cantidad": cantidad}

                if tipo == "INGRESO":
                    resumen["ingresos"] = total
                elif tipo == "GASTO":
                    resumen["gastos"] = total
                else:
                    resumen["otros"] += total

                resumen["total_movimientos"] += cantidad

            resumen["saldo_dia"] = resumen["ingresos"] - resumen["gastos"]

            return resumen

        except Exception as e:
            print(f"✗ Error obteniendo resumen por día: {e}")
            return {
                "fecha": fecha,
                "ingresos": 0.0,
                "gastos": 0.0,
                "otros": 0.0,
                "saldo_dia": 0.0,
                "total_movimientos": 0,
                "detalle": {},
            }

    def get_estadisticas_periodo(
        self, fecha_desde: str, fecha_hasta: str
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de un período específico

        Args:
            fecha_desde: Fecha inicial (YYYY-MM-DD)
            fecha_hasta: Fecha final (YYYY-MM-DD)

        Returns:
            Dict: Estadísticas del período
        """
        try:
            # Obtener saldo inicial del período
            saldo_anterior = self.calcular_saldo(
                (
                    datetime.strptime(fecha_desde, "%Y-%m-%d") - timedelta(days=1)
                ).strftime("%Y-%m-%d")
            )

            # Obtener movimientos del período
            query = f"""
            SELECT 
                tipo,
                COUNT(*) as cantidad,
                SUM(monto) as total,
                DATE(fecha) as fecha_dia
            FROM {self.table_name}
            WHERE DATE(fecha) BETWEEN %s AND %s
            GROUP BY tipo, DATE(fecha)
            ORDER BY DATE(fecha), tipo
            """

            resultados = self.fetch_all(query, (fecha_desde, fecha_hasta))

            # Procesar resultados
            estadisticas = {
                "fecha_desde": fecha_desde,
                "fecha_hasta": fecha_hasta,
                "saldo_inicial_periodo": saldo_anterior.get("saldo_actual", 0.0),
                "total_ingresos": 0.0,
                "total_gastos": 0.0,
                "total_movimientos": 0,
                "movimientos_por_dia": {},
                "promedio_diario_ingresos": 0.0,
                "promedio_diario_gastos": 0.0,
            }

            dias = {}

            for row in resultados:
                fecha_dia = (
                    row["fecha_dia"].strftime("%Y-%m-%d")
                    if hasattr(row["fecha_dia"], "strftime")
                    else row["fecha_dia"]
                )
                tipo = row["tipo"]
                total = float(row["total"])
                cantidad = row["cantidad"]

                # Inicializar día si no existe
                if fecha_dia not in dias:
                    dias[fecha_dia] = {"ingresos": 0.0, "gastos": 0.0, "movimientos": 0}

                # Acumular por tipo
                if tipo == "INGRESO":
                    estadisticas["total_ingresos"] += total
                    dias[fecha_dia]["ingresos"] += total
                elif tipo == "GASTO":
                    estadisticas["total_gastos"] += total
                    dias[fecha_dia]["gastos"] += total

                dias[fecha_dia]["movimientos"] += cantidad
                estadisticas["total_movimientos"] += cantidad

            estadisticas["movimientos_por_dia"] = dias
            estadisticas["saldo_final"] = (
                estadisticas["saldo_inicial_periodo"]
                + estadisticas["total_ingresos"]
                - estadisticas["total_gastos"]
            )

            # Calcular promedios diarios
            total_dias = len(dias)
            if total_dias > 0:
                estadisticas["promedio_diario_ingresos"] = (
                    estadisticas["total_ingresos"] / total_dias
                )
                estadisticas["promedio_diario_gastos"] = (
                    estadisticas["total_gastos"] / total_dias
                )

            return estadisticas

        except Exception as e:
            print(f"✗ Error obteniendo estadísticas del período: {e}")
            return {
                "fecha_desde": fecha_desde,
                "fecha_hasta": fecha_hasta,
                "saldo_inicial_periodo": 0.0,
                "total_ingresos": 0.0,
                "total_gastos": 0.0,
                "saldo_final": 0.0,
                "total_movimientos": 0,
                "movimientos_por_dia": {},
                "promedio_diario_ingresos": 0.0,
                "promedio_diario_gastos": 0.0,
            }

    # ============ MÉTODOS PARA DASHBOARD ============

    def get_total_movimientos(
        self,
        tipo: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
    ) -> int:
        """
        Obtiene el total de movimientos

        Args:
            tipo: Filtrar por tipo de movimiento
            fecha_desde: Fecha inicial (YYYY-MM-DD)
            fecha_hasta: Fecha final (YYYY-MM-DD)

        Returns:
            int: Número total de movimientos
        """
        try:
            query = f"SELECT COUNT(*) as total FROM {self.table_name}"
            conditions = []
            params = []

            if tipo is not None:
                conditions.append("tipo = %s")
                params.append(tipo)

            if fecha_desde is not None:
                conditions.append("DATE(fecha) >= %s")
                params.append(fecha_desde)

            if fecha_hasta is not None:
                conditions.append("DATE(fecha) <= %s")
                params.append(fecha_hasta)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            result = self.fetch_one(query, params)
            return result["total"] if result else 0

        except Exception as e:
            print(f"✗ Error obteniendo total de movimientos: {e}")
            return 0

    def get_movimientos_por_tipo(
        self, fecha_desde: Optional[str] = None, fecha_hasta: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene distribución de movimientos por tipo

        Args:
            fecha_desde: Fecha inicial (YYYY-MM-DD)
            fecha_hasta: Fecha final (YYYY-MM-DD)

        Returns:
            List[Dict]: Distribución por tipo
        """
        try:
            query = f"""
            SELECT 
                tipo,
                COUNT(*) as cantidad,
                SUM(monto) as total_monto
            FROM {self.table_name}
            """

            conditions = []
            params = []

            if fecha_desde is not None:
                conditions.append("DATE(fecha) >= %s")
                params.append(fecha_desde)

            if fecha_hasta is not None:
                conditions.append("DATE(fecha) <= %s")
                params.append(fecha_hasta)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " GROUP BY tipo ORDER BY total_monto DESC"

            return self.fetch_all(query, params)

        except Exception as e:
            print(f"✗ Error obteniendo movimientos por tipo: {e}")
            return []

    # ============ MÉTODOS DE AUDITORÍA ============

    def _registrar_auditoria(
        self, accion: str, movimiento_id: int, usuario_id: Optional[int] = None
    ):
        """
        Registra acción de auditoría para el movimiento

        Args:
            accion: Acción realizada (CREACION, ACTUALIZACION, ELIMINACION)
            movimiento_id: ID del movimiento
            usuario_id: ID del usuario que realizó la acción
        """
        try:
            # En una implementación real, esto se registraría en una tabla de auditoría
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            usuario_info = f" (Usuario: {usuario_id})" if usuario_id else ""

            print(
                f"📋 Auditoría - {timestamp} - {accion} movimiento {movimiento_id}{usuario_info}"
            )

        except Exception as e:
            print(f"✗ Error registrando auditoría: {e}")

    # ============ MÉTODOS DE VALIDACIÓN DE UNICIDAD ============

    def origen_exists(
        self, origen_tipo: str, origen_id: int, exclude_id: Optional[int] = None
    ) -> bool:
        """
        Verifica si ya existe un movimiento para el origen especificado

        Args:
            origen_tipo: Tipo de origen
            origen_id: ID del origen
            exclude_id: ID a excluir (para actualizaciones)

        Returns:
            bool: True si existe, False en caso contrario
        """
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE origen_tipo = %s AND origen_id = %s"
            params = [origen_tipo, origen_id]

            if exclude_id is not None:
                query += " AND id != %s"
                params.append(exclude_id)

            result = self.fetch_one(query, params)
            return result["count"] > 0 if result else False

        except Exception as e:
            print(f"✗ Error verificando origen: {e}")
            return False

    # ============ MÉTODOS DE COMPATIBILIDAD ============

    def obtener_todos(self):
        """Método de compatibilidad con nombres antiguos"""
        return self.get_all()

    def obtener_por_id(self, movimiento_id):
        """Método de compatibilidad con nombres antiguos"""
        return self.read(movimiento_id)

    def obtener_ingresos(self, fecha_desde=None, fecha_hasta=None):
        """Método de compatibilidad con nombres antiguos"""
        return self.get_ingresos(fecha_desde, fecha_hasta)

    def obtener_gastos(self, fecha_desde=None, fecha_hasta=None):
        """Método de compatibilidad con nombres antiguos"""
        return self.get_gastos(fecha_desde, fecha_hasta)

    def update_table(self, table, data, condition, params=None):
        """Método helper para actualizar (compatibilidad con BaseModel)"""
        return self.update(table, data, condition, params)  # type: ignore

    # ============ MÉTODOS DE UTILIDAD ============

    def get_tipos_movimiento(self) -> List[str]:
        """
        Obtiene la lista de tipos de movimiento

        Returns:
            List[str]: Lista de tipos
        """
        return self.TIPOS_MOVIMIENTO.copy()

    def get_tipos_origen(self) -> List[str]:
        """
        Obtiene la lista de tipos de origen

        Returns:
            List[str]: Lista de tipos
        """
        return self.TIPOS_ORIGEN.copy()

    def get_resumen_mensual(self, año: int, mes: int) -> Dict[str, Any]:
        """
        Obtiene resumen mensual de movimientos

        Args:
            año: Año a consultar
            mes: Mes a consultar (1-12)

        Returns:
            Dict: Resumen mensual
        """
        try:
            fecha_desde = f"{año:04d}-{mes:02d}-01"

            # Calcular última fecha del mes
            if mes == 12:
                fecha_hasta = f"{año:04d}-12-31"
            else:
                fecha_hasta = f"{año:04d}-{(mes+1):02d}-01"
                fecha_hasta_obj = datetime.strptime(
                    fecha_hasta, "%Y-%m-%d"
                ) - timedelta(days=1)
                fecha_hasta = fecha_hasta_obj.strftime("%Y-%m-%d")

            return self.get_estadisticas_periodo(fecha_desde, fecha_hasta)

        except Exception as e:
            print(f"✗ Error obteniendo resumen mensual: {e}")
            return {}
