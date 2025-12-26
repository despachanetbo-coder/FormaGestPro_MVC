# app/models/programas_academicos_model.py - Versión optimizada y robusta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_model import BaseModel
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple, Union


class ProgramasAcademicosModel(BaseModel):
    def __init__(self):
        """Inicializa el modelo de programas académicos"""
        super().__init__()
        self.table_name = "programas_academicos"
        self.sequence_name = "seq_programas_academicos_id"

        # Estados válidos según el tipo enumerado d_estado_programa
        self.ESTADOS_PROGRAMA = [
            "PLANIFICADO",
            "INSCRIPCIONES",
            "EN_CURSO",
            "SUSPENDIDO",
            "CANCELADO",
            "FINALIZADO",
        ]

        # Columnas de la tabla para validación
        self.columns = [
            "id",
            "codigo",
            "nombre",
            "descripcion",
            "duracion_semanas",
            "horas_totales",
            "costo_base",
            "descuento_contado",
            "cupos_totales",
            "cupos_disponibles",
            "estado",
            "fecha_inicio_planificada",
            "fecha_inicio_real",
            "fecha_fin_real",
            "tutor_id",
            "promocion_activa",
            "descripcion_promocion",
            "descuento_promocion",
            "costo_inscripcion",
            "costo_matricula",
            "promocion_fecha_limite",
            "cuotas_mensuales",
            "dias_entre_cuotas",
            "created_at",
            "updated_at",
        ]

        # Columnas requeridas
        self.required_columns = ["codigo", "nombre", "costo_base", "cupos_totales"]

        # Columnas de tipo decimal
        self.decimal_columns = [
            "costo_base",
            "descuento_contado",
            "descuento_promocion",
            "costo_inscripcion",
            "costo_matricula",
        ]

        # Columnas de tipo entero
        self.integer_columns = [
            "duracion_semanas",
            "horas_totales",
            "cupos_totales",
            "cupos_disponibles",
            "tutor_id",
            "cuotas_mensuales",
            "dias_entre_cuotas",
        ]

    # ============ MÉTODOS DE VALIDACIÓN ============

    def _validate_programa_data(
        self, data: Dict[str, Any], for_update: bool = False
    ) -> Tuple[bool, str]:
        """
        Valida los datos del programa académico

        Args:
            data: Diccionario con datos del programa
            for_update: Si es True, valida para actualización

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        # Campos requeridos para creación
        if not for_update:
            for field in self.required_columns:
                if field not in data or not str(data[field]).strip():
                    return False, f"Campo requerido faltante: {field}"

        # Validar código único si se proporciona
        if "codigo" in data and data["codigo"]:
            existing_id = None
            if for_update and "id" in data:
                existing_id = data["id"]

            if self.codigo_exists(data["codigo"], exclude_id=existing_id):
                return False, f"El código {data['codigo']} ya está registrado"

        # Validar estado si se proporciona
        if "estado" in data and data["estado"]:
            if data["estado"] not in self.ESTADOS_PROGRAMA:
                return (
                    False,
                    f"Estado inválido. Use: {', '.join(self.ESTADOS_PROGRAMA)}",
                )

        # Validar fechas si se proporcionan
        date_fields = [
            "fecha_inicio_planificada",
            "fecha_inicio_real",
            "fecha_fin_real",
            "promocion_fecha_limite",
        ]

        for field in date_fields:
            if field in data and data[field]:
                if not self._is_valid_date(data[field]):
                    return (
                        False,
                        f"Formato de fecha inválido en {field}. Use YYYY-MM-DD",
                    )

        # Validar descuentos (0-100)
        if "descuento_contado" in data and data["descuento_contado"] is not None:
            try:
                descuento = Decimal(str(data["descuento_contado"]))
                if descuento < 0 or descuento > 100:
                    return False, "Descuento contado debe estar entre 0 y 100"
            except (ValueError, TypeError):
                return False, "Descuento contado inválido"

        if "descuento_promocion" in data and data["descuento_promocion"] is not None:
            try:
                descuento = Decimal(str(data["descuento_promocion"]))
                if descuento < 0 or descuento > 100:
                    return False, "Descuento promoción debe estar entre 0 y 100"
            except (ValueError, TypeError):
                return False, "Descuento promoción inválido"

        # Validar cupos disponibles <= cupos totales
        if "cupos_totales" in data and "cupos_disponibles" in data:
            if (
                data["cupos_disponibles"] is not None
                and data["cupos_totales"] is not None
            ):
                if data["cupos_disponibles"] > data["cupos_totales"]:
                    return (
                        False,
                        "Cupos disponibles no pueden ser mayores a cupos totales",
                    )

        # Validar tutor si se proporciona
        if "tutor_id" in data and data["tutor_id"]:
            if not self._tutor_exists(data["tutor_id"]):
                return False, f"Tutor con ID {data['tutor_id']} no existe"

        # Validar costo base positivo
        if "costo_base" in data and data["costo_base"] is not None:
            try:
                costo = Decimal(str(data["costo_base"]))
                if costo < 0:
                    return False, "Costo base no puede ser negativo"
            except (ValueError, TypeError):
                return False, "Costo base inválido"

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

    def _tutor_exists(self, tutor_id: int) -> bool:
        """Verifica si el tutor existe en la tabla docentes"""
        try:
            query = (
                "SELECT COUNT(*) as count FROM docentes WHERE id = %s AND activo = TRUE"
            )
            result = self.fetch_one(query, (tutor_id,))
            return result["count"] > 0 if result else False
        except:
            return False

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza los datos del programa académico

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
        Crea un nuevo programa académico

        Args:
            data: Diccionario con datos del programa

        Returns:
            Optional[int]: ID del programa creado o None si hay error
        """
        # Sanitizar y validar datos
        data = self._sanitize_data(data)
        is_valid, error_msg = self._validate_programa_data(data, for_update=False)

        if not is_valid:
            print(f"✗ Error validando datos: {error_msg}")
            return None

        try:
            # Preparar datos para inserción
            insert_data = data.copy()

            # Establecer valores por defecto
            defaults = {
                "estado": "PLANIFICADO",
                "descuento_contado": Decimal("0"),
                "cupos_disponibles": insert_data.get("cupos_totales", 0),
                "promocion_activa": False,
                "descuento_promocion": Decimal("0"),
                "costo_inscripcion": Decimal("0"),
                "costo_matricula": Decimal("0"),
                "cuotas_mensuales": 1,
                "dias_entre_cuotas": 30,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            for key, value in defaults.items():
                if key not in insert_data or insert_data[key] is None:
                    insert_data[key] = value

            # Insertar en base de datos
            result = self.insert(self.table_name, insert_data, returning="id")

            if result:
                print(f"✓ Programa académico creado exitosamente con ID: {result}")
                return result

            return None

        except Exception as e:
            print(f"✗ Error creando programa académico: {e}")
            return None

    def read(self, programa_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un programa académico por su ID

        Args:
            programa_id: ID del programa

        Returns:
            Optional[Dict]: Datos del programa o None si no existe
        """
        try:
            query = f"""
            SELECT pa.*, 
                   d.nombres as tutor_nombres, 
                   d.apellidos as tutor_apellidos,
                   d.email as tutor_email
            FROM {self.table_name} pa
            LEFT JOIN docentes d ON pa.tutor_id = d.id
            WHERE pa.id = %s
            """
            result = self.fetch_one(query, (programa_id,))
            return result

        except Exception as e:
            print(f"✗ Error obteniendo programa académico: {e}")
            return None

    def update(self, programa_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un programa académico existente

        Args:
            programa_id: ID del programa a actualizar
            data: Diccionario con datos a actualizar

        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        if not data:
            return False

        # Añadir ID para validación
        data_with_id = data.copy()
        data_with_id["id"] = programa_id

        # Sanitizar y validar datos
        data = self._sanitize_data(data)
        is_valid, error_msg = self._validate_programa_data(
            data_with_id, for_update=True
        )

        if not is_valid:
            print(f"✗ Error validando datos: {error_msg}")
            return False

        try:
            # Añadir updated_at
            data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Actualizar en base de datos
            result = self.update_table(self.table_name, data, "id = %s", (programa_id,))

            if result:
                print(f"✓ Programa académico {programa_id} actualizado exitosamente")
                return True

            return False

        except Exception as e:
            print(f"✗ Error actualizando programa académico: {e}")
            return False

    def delete(self, programa_id: int) -> bool:
        """
        Elimina un programa académico (solo si está PLANIFICADO o CANCELADO)

        Args:
            programa_id: ID del programa

        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            # Verificar que el programa pueda ser eliminado
            programa = self.read(programa_id)
            if not programa:
                return False

            if programa["estado"] not in ["PLANIFICADO", "CANCELADO"]:
                print(
                    f"✗ No se puede eliminar programa en estado: {programa['estado']}"
                )
                return False

            query = f"DELETE FROM {self.table_name} WHERE id = %s"
            result = self.execute_query(query, (programa_id,), commit=True)

            if result:
                print(f"✓ Programa académico {programa_id} eliminado exitosamente")
                return True

            return False

        except Exception as e:
            print(f"✗ Error eliminando programa académico: {e}")
            return False

    # ============ MÉTODOS DE CONSULTA AVANZADOS ============

    def get_all(
        self,
        estado: Optional[str] = None,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todos los programas académicos

        Args:
            estado: Filtrar por estado específico
            active_only: Si es True, excluye programas CANCELADOS
            limit: Límite de registros
            offset: Desplazamiento para paginación
            order_by: Campo para ordenar
            order_desc: Si es True, orden descendente

        Returns:
            List[Dict]: Lista de programas
        """
        try:
            query = f"""
            SELECT pa.*, 
                   d.nombres as tutor_nombres, 
                   d.apellidos as tutor_apellidos
            FROM {self.table_name} pa
            LEFT JOIN docentes d ON pa.tutor_id = d.id
            """

            conditions = []
            params = []

            if estado:
                conditions.append("pa.estado = %s")
                params.append(estado)
            elif active_only:
                conditions.append("pa.estado != %s")
                params.append("CANCELADO")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            # Ordenar
            order_dir = "DESC" if order_desc else "ASC"
            query += f" ORDER BY pa.{order_by} {order_dir}"

            # Paginación
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            return self.fetch_all(query, params)

        except Exception as e:
            print(f"✗ Error obteniendo programas académicos: {e}")
            return []

    def search(
        self, search_term: str, estado: Optional[str] = None, active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Busca programas académicos por término de búsqueda

        Args:
            search_term: Término a buscar
            estado: Filtrar por estado
            active_only: Si es True, excluye programas CANCELADOS

        Returns:
            List[Dict]: Lista de programas que coinciden
        """
        try:
            query = f"""
            SELECT pa.*, 
                   d.nombres as tutor_nombres, 
                   d.apellidos as tutor_apellidos
            FROM {self.table_name} pa
            LEFT JOIN docentes d ON pa.tutor_id = d.id
            WHERE (pa.codigo ILIKE %s 
                   OR pa.nombre ILIKE %s 
                   OR pa.descripcion ILIKE %s)
            """

            params = [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"]

            if estado:
                query += " AND pa.estado = %s"
                params.append(estado)
            elif active_only:
                query += " AND pa.estado != %s"
                params.append("CANCELADO")

            query += " ORDER BY pa.nombre"

            return self.fetch_all(query, params)

        except Exception as e:
            print(f"✗ Error buscando programas académicos: {e}")
            return []

    def get_by_estado(self, estado: str) -> List[Dict[str, Any]]:
        """
        Obtiene programas académicos por estado

        Args:
            estado: Estado del programa

        Returns:
            List[Dict]: Lista de programas con el estado especificado
        """
        try:
            query = f"""
            SELECT pa.*, 
                   d.nombres as tutor_nombres, 
                   d.apellidos as tutor_apellidos
            FROM {self.table_name} pa
            LEFT JOIN docentes d ON pa.tutor_id = d.id
            WHERE pa.estado = %s
            ORDER BY pa.nombre
            """

            return self.fetch_all(query, (estado,))

        except Exception as e:
            print(f"✗ Error obteniendo programas por estado: {e}")
            return []

    def get_by_tutor(self, tutor_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene programas académicos por tutor

        Args:
            tutor_id: ID del tutor

        Returns:
            List[Dict]: Lista de programas del tutor
        """
        try:
            query = f"""
            SELECT pa.*, 
                   d.nombres as tutor_nombres, 
                   d.apellidos as tutor_apellidos
            FROM {self.table_name} pa
            LEFT JOIN docentes d ON pa.tutor_id = d.id
            WHERE pa.tutor_id = %s AND pa.estado != 'CANCELADO'
            ORDER BY pa.estado, pa.nombre
            """

            return self.fetch_all(query, (tutor_id,))

        except Exception as e:
            print(f"✗ Error obteniendo programas por tutor: {e}")
            return []

    def get_with_promocion(self) -> List[Dict[str, Any]]:
        """
        Obtiene programas académicos con promoción activa

        Returns:
            List[Dict]: Lista de programas con promoción
        """
        try:
            query = f"""
            SELECT pa.*, 
                   d.nombres as tutor_nombres, 
                   d.apellidos as tutor_apellidos
            FROM {self.table_name} pa
            LEFT JOIN docentes d ON pa.tutor_id = d.id
            WHERE pa.promocion_activa = TRUE 
              AND pa.estado != 'CANCELADO'
              AND (pa.promocion_fecha_limite IS NULL 
                   OR pa.promocion_fecha_limite >= CURRENT_DATE)
            ORDER BY pa.descuento_promocion DESC, pa.nombre
            """

            return self.fetch_all(query)

        except Exception as e:
            print(f"✗ Error obteniendo programas con promoción: {e}")
            return []

    # ============ MÉTODOS PARA DASHBOARD ============

    def get_total_programas(self, estado: Optional[str] = None) -> int:
        """
        Obtiene el total de programas académicos

        Args:
            estado: Filtrar por estado específico

        Returns:
            int: Número total de programas
        """
        try:
            query = f"SELECT COUNT(*) as total FROM {self.table_name}"
            params = []

            if estado:
                query += " WHERE estado = %s"
                params.append(estado)

            result = self.fetch_one(query, params)
            return result["total"] if result else 0

        except Exception as e:
            print(f"✗ Error obteniendo total de programas: {e}")
            return 0

    def get_programas_por_estado(self) -> List[Dict[str, Any]]:
        """
        Obtiene distribución de programas por estado

        Returns:
            List[Dict]: Distribución por estado
        """
        try:
            query = f"""
            SELECT 
                estado,
                COUNT(*) as cantidad,
                SUM(cupos_totales) as total_cupos,
                SUM(cupos_disponibles) as cupos_disponibles_total
            FROM {self.table_name}
            GROUP BY estado
            ORDER BY cantidad DESC
            """

            return self.fetch_all(query)

        except Exception as e:
            print(f"✗ Error obteniendo programas por estado: {e}")
            return []

    def get_programas_con_cupos(self, min_cupos: int = 1) -> List[Dict[str, Any]]:
        """
        Obtiene programas con cupos disponibles

        Args:
            min_cupos: Mínimo de cupos disponibles requeridos

        Returns:
            List[Dict]: Programas con cupos disponibles
        """
        try:
            query = f"""
            SELECT pa.*, 
                   d.nombres as tutor_nombres, 
                   d.apellidos as tutor_apellidos
            FROM {self.table_name} pa
            LEFT JOIN docentes d ON pa.tutor_id = d.id
            WHERE pa.cupos_disponibles >= %s 
              AND pa.estado IN ('PLANIFICADO', 'INSCRIPCIONES')
            ORDER BY pa.cupos_disponibles DESC, pa.nombre
            """

            return self.fetch_all(query, (min_cupos,))

        except Exception as e:
            print(f"✗ Error obteniendo programas con cupos: {e}")
            return []

    # ============ MÉTODOS DE GESTIÓN DE ESTADO ============

    def cambiar_estado(self, programa_id: int, nuevo_estado: str) -> bool:
        """
        Cambia el estado de un programa académico

        Args:
            programa_id: ID del programa
            nuevo_estado: Nuevo estado del programa

        Returns:
            bool: True si se cambió correctamente
        """
        if nuevo_estado not in self.ESTADOS_PROGRAMA:
            print(f"✗ Estado inválido: {nuevo_estado}")
            return False

        try:
            data = {
                "estado": nuevo_estado,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            # Si el estado es EN_CURSO y no tiene fecha_inicio_real, establecerla
            if nuevo_estado == "EN_CURSO":
                programa = self.read(programa_id)
                if programa and not programa.get("fecha_inicio_real"):
                    data["fecha_inicio_real"] = date.today().strftime("%Y-%m-%d")

            # Si el estado es FINALIZADO y no tiene fecha_fin_real, establecerla
            elif nuevo_estado == "FINALIZADO":
                programa = self.read(programa_id)
                if programa and not programa.get("fecha_fin_real"):
                    data["fecha_fin_real"] = date.today().strftime("%Y-%m-%d")

            return self.update(programa_id, data)

        except Exception as e:
            print(f"✗ Error cambiando estado del programa: {e}")
            return False

    def activar_promocion(
        self,
        programa_id: int,
        descripcion: str,
        descuento: Decimal,
        fecha_limite: Optional[str] = None,
    ) -> bool:
        """
        Activa una promoción para un programa

        Args:
            programa_id: ID del programa
            descripcion: Descripción de la promoción
            descuento: Porcentaje de descuento (0-100)
            fecha_limite: Fecha límite de la promoción (YYYY-MM-DD)

        Returns:
            bool: True si se activó correctamente
        """
        try:
            # Validar descuento
            descuento_dec = Decimal(str(descuento))
            if descuento_dec < 0 or descuento_dec > 100:
                print("✗ Descuento debe estar entre 0 y 100")
                return False

            data = {
                "promocion_activa": True,
                "descripcion_promocion": descripcion,
                "descuento_promocion": descuento_dec,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            if fecha_limite:
                if not self._is_valid_date(fecha_limite):
                    print("✗ Formato de fecha límite inválido")
                    return False
                data["promocion_fecha_limite"] = fecha_limite

            return self.update(programa_id, data)

        except Exception as e:
            print(f"✗ Error activando promoción: {e}")
            return False

    def desactivar_promocion(self, programa_id: int) -> bool:
        """
        Desactiva la promoción de un programa

        Args:
            programa_id: ID del programa

        Returns:
            bool: True si se desactivó correctamente
        """
        try:
            data = {
                "promocion_activa": False,
                "descripcion_promocion": None,
                "descuento_promocion": Decimal("0"),
                "promocion_fecha_limite": None,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            return self.update(programa_id, data)

        except Exception as e:
            print(f"✗ Error desactivando promoción: {e}")
            return False

    # ============ MÉTODOS DE GESTIÓN DE CUPOS ============

    def actualizar_cupos_disponibles(self, programa_id: int, cantidad: int) -> bool:
        """
        Actualiza los cupos disponibles de un programa

        Args:
            programa_id: ID del programa
            cantidad: Cantidad a ajustar (positivo para aumentar, negativo para disminuir)

        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            programa = self.read(programa_id)
            if not programa:
                return False

            nuevos_cupos = programa["cupos_disponibles"] + cantidad

            # Validar que no sea negativo ni mayor al total
            if nuevos_cupos < 0:
                print("✗ No hay suficientes cupos disponibles")
                return False

            if nuevos_cupos > programa["cupos_totales"]:
                print("✗ Cupos disponibles no pueden ser mayores al total")
                return False

            data = {
                "cupos_disponibles": nuevos_cupos,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            return self.update(programa_id, data)

        except Exception as e:
            print(f"✗ Error actualizando cupos: {e}")
            return False

    def reservar_cupo(self, programa_id: int) -> bool:
        """
        Reserva un cupo en el programa

        Args:
            programa_id: ID del programa

        Returns:
            bool: True si se reservó correctamente
        """
        return self.actualizar_cupos_disponibles(programa_id, -1)

    def liberar_cupo(self, programa_id: int) -> bool:
        """
        Libera un cupo en el programa

        Args:
            programa_id: ID del programa

        Returns:
            bool: True si se liberó correctamente
        """
        return self.actualizar_cupos_disponibles(programa_id, 1)

    # ============ MÉTODOS DE CÁLCULO ============

    def calcular_costo_total(
        self, programa_id: int, pago_contado: bool = False
    ) -> Dict[str, Decimal]:
        """
        Calcula el costo total del programa

        Args:
            programa_id: ID del programa
            pago_contado: Si es True, aplica descuento por pago contado

        Returns:
            Dict: Costos calculados
        """
        try:
            programa = self.read(programa_id)
            if not programa:
                return {}

            costo_base = Decimal(str(programa["costo_base"]))
            costo_inscripcion = Decimal(str(programa["costo_inscripcion"] or 0))
            costo_matricula = Decimal(str(programa["costo_matricula"] or 0))

            # Calcular descuento a aplicar
            descuento_aplicar = Decimal("0")

            if programa["promocion_activa"]:
                # Verificar si la promoción está vigente
                if programa["promocion_fecha_limite"]:
                    fecha_limite = datetime.strptime(
                        programa["promocion_fecha_limite"], "%Y-%m-%d"
                    ).date()
                    if date.today() <= fecha_limite:
                        descuento_aplicar = Decimal(
                            str(programa["descuento_promocion"] or 0)
                        )
            elif pago_contado:
                descuento_aplicar = Decimal(str(programa["descuento_contado"] or 0))

            # Calcular montos
            subtotal = costo_base + costo_inscripcion + costo_matricula
            descuento_monto = (subtotal * descuento_aplicar) / 100
            total = subtotal - descuento_monto

            return {
                "costo_base": costo_base,
                "costo_inscripcion": costo_inscripcion,
                "costo_matricula": costo_matricula,
                "subtotal": subtotal,
                "descuento_porcentaje": descuento_aplicar,
                "descuento_monto": descuento_monto,
                "total": total,
                "cuota_mensual": (
                    total / Decimal(str(programa["cuotas_mensuales"]))
                    if programa["cuotas_mensuales"] > 0
                    else total
                ),
            }

        except Exception as e:
            print(f"✗ Error calculando costo total: {e}")
            return {}

    # ============ MÉTODOS DE VALIDACIÓN DE UNICIDAD ============

    def codigo_exists(self, codigo: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si un código ya existe

        Args:
            codigo: Código a verificar
            exclude_id: ID a excluir (para actualizaciones)

        Returns:
            bool: True si existe, False en caso contrario
        """
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE codigo = %s"
            params = [codigo]

            if exclude_id is not None:
                query += " AND id != %s"
                params.append(exclude_id)  # type: ignore

            result = self.fetch_one(query, params)
            return result["count"] > 0 if result else False

        except Exception as e:
            print(f"✗ Error verificando código: {e}")
            return False

    # ============ MÉTODOS DE COMPATIBILIDAD ============

    def obtener_todos(self):
        """Método de compatibilidad con nombres antiguos"""
        return self.get_all()

    def obtener_por_id(self, programa_id):
        """Método de compatibilidad con nombres antiguos"""
        return self.read(programa_id)

    def buscar_programas(self, termino):
        """Método de compatibilidad con nombres antiguos"""
        return self.search(termino)

    def update_table(self, table, data, condition, params=None):
        """Método helper para actualizar (compatibilidad con BaseModel)"""
        return self.update(table, data, condition, params)  # type: ignore

    # ============ MÉTODOS DE UTILIDAD ============

    def get_estados_programa(self) -> List[str]:
        """
        Obtiene la lista de estados válidos para programas

        Returns:
            List[str]: Lista de estados
        """
        return self.ESTADOS_PROGRAMA.copy()

    def get_programas_activos(self) -> List[Dict[str, Any]]:
        """
        Obtiene programas activos (no cancelados)

        Returns:
            List[Dict]: Programas activos
        """
        return self.get_all(active_only=True)
