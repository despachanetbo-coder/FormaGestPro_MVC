# app/models/ingreso_model.py - Versión optimizada y robusta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_model import BaseModel
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple, Union


class IngresoModel(BaseModel):
    def __init__(self):
        """Inicializa el modelo de ingresos"""
        super().__init__()
        self.table_name = "ingresos"
        self.sequence_name = "seq_ingresos_id"

        # Tipos enumerados según la base de datos
        self.TIPOS_INGRESO = ["MATRICULA_CUOTA", "MATRICULA_CONTADO", "OTRO_INGRESO"]
        self.FORMAS_PAGO = [
            "EFECTIVO",
            "TRANSFERENCIA",
            "TARJETA_CREDITO",
            "TARJETA_DEBITO",
            "DEPOSITO",
            "CHEQUE",
        ]
        self.ESTADOS_TRANSACCION = [
            "REGISTRADO",
            "CONFIRMADO",
            "ANULADO",
            "DEVUELTO",
            "CONTABILIZADO",
        ]

        # Columnas de la tabla para validación
        self.columns = [
            "id",
            "tipo_ingreso",
            "matricula_id",
            "nro_cuota",
            "fecha",
            "monto",
            "concepto",
            "descripcion",
            "forma_pago",
            "estado",
            "nro_comprobante",
            "nro_transaccion",
            "registrado_por",
            "created_at",
        ]

        # Columnas requeridas
        self.required_columns = ["tipo_ingreso", "fecha", "monto", "concepto"]

        # Columnas de tipo decimal
        self.decimal_columns = ["monto"]

        # Columnas de tipo entero
        self.integer_columns = ["matricula_id", "nro_cuota", "registrado_por"]

        # Columnas de tipo fecha
        self.date_columns = ["fecha"]

    # ============ MÉTODOS DE VALIDACIÓN ============

    def _validate_ingreso_data(
        self, data: Dict[str, Any], for_update: bool = False
    ) -> Tuple[bool, str]:
        """
        Valida los datos del ingreso

        Args:
            data: Diccionario con datos del ingreso
            for_update: Si es True, valida para actualización

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        # Campos requeridos para creación
        if not for_update:
            for field in self.required_columns:
                if field not in data or data[field] is None:
                    return False, f"Campo requerido faltante: {field}"

        # Validar tipo de ingreso
        if "tipo_ingreso" in data and data["tipo_ingreso"]:
            if data["tipo_ingreso"] not in self.TIPOS_INGRESO:
                return (
                    False,
                    f"Tipo de ingreso inválido. Use: {', '.join(self.TIPOS_INGRESO)}",
                )

        # Validar consistencia entre tipo de ingreso y matrícula
        if "tipo_ingreso" in data and data["tipo_ingreso"]:
            tipo = data["tipo_ingreso"]
            matricula_id = data.get("matricula_id")

            if tipo in ["MATRICULA_CUOTA", "MATRICULA_CONTADO"] and not matricula_id:
                return False, f"Tipo {tipo} requiere matrícula asociada"
            elif tipo == "OTRO_INGRESO" and matricula_id:
                return False, "Tipo OTRO_INGRESO no debe tener matrícula asociada"

        # Validar número de cuota si se proporciona
        if "nro_cuota" in data and data["nro_cuota"] is not None:
            try:
                nro_cuota = int(data["nro_cuota"])
                if nro_cuota <= 0:
                    return False, "El número de cuota debe ser mayor a 0"

                # Validar que si hay número de cuota, el tipo sea MATRICULA_CUOTA
                if "tipo_ingreso" in data and data["tipo_ingreso"] != "MATRICULA_CUOTA":
                    return (
                        False,
                        "Número de cuota solo válido para tipo MATRICULA_CUOTA",
                    )
            except (ValueError, TypeError):
                return False, "Número de cuota inválido"

        # Validar monto positivo
        if "monto" in data and data["monto"] is not None:
            try:
                monto = Decimal(str(data["monto"]))
                if monto <= 0:
                    return False, "El monto debe ser mayor a 0"
            except (ValueError, TypeError):
                return False, "Monto inválido. Debe ser un número decimal positivo"

        # Validar forma de pago si se proporciona
        if "forma_pago" in data and data["forma_pago"]:
            if data["forma_pago"] not in self.FORMAS_PAGO:
                return (
                    False,
                    f"Forma de pago inválida. Use: {', '.join(self.FORMAS_PAGO)}",
                )

        # Validar estado si se proporciona
        if "estado" in data and data["estado"]:
            if data["estado"] not in self.ESTADOS_TRANSACCION:
                return (
                    False,
                    f"Estado inválido. Use: {', '.join(self.ESTADOS_TRANSACCION)}",
                )

        # Validar número de comprobante único si se proporciona
        if "nro_comprobante" in data and data["nro_comprobante"]:
            existing_id = None
            if for_update and "id" in data:
                existing_id = data["id"]

            if self.comprobante_exists(data["nro_comprobante"], exclude_id=existing_id):
                return (
                    False,
                    f"El número de comprobante {data['nro_comprobante']} ya existe",
                )

        # Validar matrícula si se proporciona
        if "matricula_id" in data and data["matricula_id"]:
            if not self._matricula_exists(data["matricula_id"]):
                return False, f"Matrícula con ID {data['matricula_id']} no existe"

            # Validar unicidad matrícula-tipo_ingreso
            if "tipo_ingreso" in data and data["tipo_ingreso"]:
                existing_id = None
                if for_update and "id" in data:
                    existing_id = data["id"]

                if self.matricula_tipo_exists(
                    data["matricula_id"], data["tipo_ingreso"], exclude_id=existing_id
                ):
                    return (
                        False,
                        f"Ya existe un ingreso del tipo {data['tipo_ingreso']} para esta matrícula",
                    )

        # Validar usuario registrador si se proporciona
        if "registrado_por" in data and data["registrado_por"]:
            if not self._usuario_exists(data["registrado_por"]):
                return False, f"Usuario con ID {data['registrado_por']} no existe"

        # Validar fecha si se proporciona
        if "fecha" in data and data["fecha"]:
            if not self._is_valid_date(data["fecha"]):
                return False, "Formato de fecha inválido. Use YYYY-MM-DD"

            # No permitir fechas futuras
            try:
                fecha_ing = (
                    datetime.strptime(data["fecha"], "%Y-%m-%d").date()
                    if isinstance(data["fecha"], str)
                    else data["fecha"]
                )
                if fecha_ing > date.today():
                    return False, "No se pueden registrar ingresos con fecha futura"
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

    def _matricula_exists(self, matricula_id: int) -> bool:
        """Verifica si la matrícula existe"""
        try:
            query = "SELECT COUNT(*) as count FROM matriculas WHERE id = %s"
            result = self.fetch_one(query, (matricula_id,))
            return result["count"] > 0 if result else False
        except:
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
        Sanitiza los datos del ingreso

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
                        sanitized[key] = value.strftime("%Y-%m-%d")
                    elif isinstance(value, date):
                        sanitized[key] = value.strftime("%Y-%m-%d")
                # Mantener otros tipos
                else:
                    sanitized[key] = value

        return sanitized

    # ============ MÉTODOS CRUD PRINCIPALES ============

    def create(
        self, data: Dict[str, Any], usuario_id: Optional[int] = None
    ) -> Optional[int]:
        """
        Crea un nuevo ingreso

        Args:
            data: Diccionario con datos del ingreso
            usuario_id: ID del usuario que registra el ingreso

        Returns:
            Optional[int]: ID del ingreso creado o None si hay error
        """
        # Sanitizar datos
        data = self._sanitize_data(data)

        # Añadir usuario registrador si se proporciona
        if usuario_id:
            data["registrado_por"] = usuario_id

        # Validar datos
        is_valid, error_msg = self._validate_ingreso_data(data, for_update=False)

        if not is_valid:
            print(f"✗ Error validando datos: {error_msg}")
            return None

        try:
            # Iniciar transacción
            self.begin_transaction()

            # Preparar datos para inserción
            insert_data = data.copy()

            # Establecer valores por defecto
            defaults = {
                "estado": "REGISTRADO",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            for key, value in defaults.items():
                if key not in insert_data or insert_data[key] is None:
                    insert_data[key] = value

            # Insertar en base de datos
            result = self.insert(self.table_name, insert_data, returning="id")

            if result:
                print(f"✓ Ingreso creado exitosamente con ID: {result}")

                # Registrar movimiento en caja
                movimiento_creado = self._registrar_movimiento_caja(
                    result, insert_data, usuario_id
                )

                if movimiento_creado:
                    # Actualizar estado de pago en matrícula si es de tipo matrícula
                    if insert_data.get("tipo_ingreso") in [
                        "MATRICULA_CUOTA",
                        "MATRICULA_CONTADO",
                    ]:
                        matricula_id = insert_data.get("matricula_id")
                        if matricula_id is not None and isinstance(matricula_id, int):
                            self._actualizar_estado_matricula(matricula_id, result)

                    # Commit de la transacción
                    self.commit()
                    print(f"✓ Transacción completada para ingreso ID: {result}")
                    return result
                else:
                    # Rollback si no se pudo crear movimiento en caja
                    self.rollback()
                    print(f"✗ Rollback: No se pudo registrar movimiento en caja")
                    return None

            return None

        except Exception as e:
            # Rollback en caso de error
            self.rollback()
            print(f"✗ Error creando ingreso: {e}")
            return None

    def read(self, ingreso_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un ingreso por su ID

        Args:
            ingreso_id: ID del ingreso

        Returns:
            Optional[Dict]: Datos del ingreso o None si no existe
        """
        try:
            query = f"""
            SELECT i.*,
                   m.estudiante_id,
                   e.nombres as estudiante_nombres,
                   e.apellidos as estudiante_apellidos,
                   p.nombre as programa_nombre,
                   u.username as registrado_por_usuario,
                   u.nombre_completo as registrado_por_nombre
            FROM {self.table_name} i
            LEFT JOIN matriculas m ON i.matricula_id = m.id
            LEFT JOIN estudiantes e ON m.estudiante_id = e.id
            LEFT JOIN programas_academicos p ON m.programa_id = p.id
            LEFT JOIN usuarios u ON i.registrado_por = u.id
            WHERE i.id = %s
            """

            result = self.fetch_one(query, (ingreso_id,))
            return result

        except Exception as e:
            print(f"✗ Error obteniendo ingreso: {e}")
            return None

    def update(
        self, ingreso_id: int, data: Dict[str, Any], usuario_id: Optional[int] = None
    ) -> bool:
        """
        Actualiza un ingreso existente

        Args:
            ingreso_id: ID del ingreso a actualizar
            data: Diccionario con datos a actualizar
            usuario_id: ID del usuario que realiza la actualización

        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        if not data:
            return False

        # Obtener datos actuales para validación
        ingreso_actual = self.read(ingreso_id)
        if not ingreso_actual:
            return False

        # No permitir actualizar ingresos confirmados o contabilizados
        if ingreso_actual["estado"] in ["CONFIRMADO", "CONTABILIZADO"]:
            print(
                f"✗ No se puede actualizar un ingreso en estado: {ingreso_actual['estado']}"
            )
            return False

        # Combinar datos actuales con los nuevos para validación
        data_with_id = {**ingreso_actual, **data}
        data_with_id["id"] = ingreso_id

        # Sanitizar y validar datos
        data = self._sanitize_data(data)
        is_valid, error_msg = self._validate_ingreso_data(data_with_id, for_update=True)

        if not is_valid:
            print(f"✗ Error validando datos: {error_msg}")
            return False

        try:
            # Iniciar transacción
            self.begin_transaction()

            # Actualizar en base de datos
            result = self.update_table(self.table_name, data, "id = %s", (ingreso_id,))

            if result:
                print(f"✓ Ingreso {ingreso_id} actualizado exitosamente")

                # Si cambió el monto, actualizar movimiento en caja
                if "monto" in data and Decimal(str(data["monto"])) != Decimal(
                    str(ingreso_actual["monto"])
                ):
                    self._actualizar_movimiento_caja(ingreso_id, data)

                # Registrar auditoría
                self._registrar_auditoria("ACTUALIZACION", ingreso_id, usuario_id)

                # Commit de la transacción
                self.commit()
                return True

            return False

        except Exception as e:
            # Rollback en caso de error
            self.rollback()
            print(f"✗ Error actualizando ingreso: {e}")
            return False

    def delete(self, ingreso_id: int, usuario_id: Optional[int] = None) -> bool:
        """
        Elimina un ingreso (solo si está en estado REGISTRADO)

        Args:
            ingreso_id: ID del ingreso
            usuario_id: ID del usuario que realiza la eliminación

        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            # Verificar estado del ingreso
            ingreso = self.read(ingreso_id)
            if not ingreso:
                return False

            if ingreso["estado"] != "REGISTRADO":
                print(
                    f"✗ No se puede eliminar un ingreso en estado: {ingreso['estado']}"
                )
                return False

            # Iniciar transacción
            self.begin_transaction()

            # Eliminar movimiento en caja asociado
            movimiento_eliminado = self._eliminar_movimiento_caja(ingreso_id)

            if not movimiento_eliminado:
                print("✗ No se pudo eliminar movimiento en caja asociado")
                self.rollback()
                return False

            # Eliminar ingreso
            query = f"DELETE FROM {self.table_name} WHERE id = %s"
            result = self.execute_query(query, (ingreso_id,), commit=False)

            if result:
                # Registrar auditoría
                self._registrar_auditoria("ELIMINACION", ingreso_id, usuario_id)

                # Commit de la transacción
                self.commit()
                print(f"✓ Ingreso {ingreso_id} eliminado exitosamente")
                return True

            self.rollback()
            return False

        except Exception as e:
            self.rollback()
            print(f"✗ Error eliminando ingreso: {e}")
            return False

    # ============ MÉTODOS DE MOVIMIENTO DE CAJA ============

    def _registrar_movimiento_caja(
        self, ingreso_id: int, data: Dict[str, Any], usuario_id: Optional[int] = None
    ) -> bool:
        """
        Registra un movimiento en caja para el ingreso

        Args:
            ingreso_id: ID del ingreso
            data: Datos del ingreso
            usuario_id: ID del usuario que registra

        Returns:
            bool: True si se registró correctamente
        """
        try:
            # Importar modelo de movimiento de caja
            from models.movimiento_caja_model import MovimientoCajaModel

            movimiento_model = MovimientoCajaModel()

            # Preparar datos del movimiento
            movimiento_data = {
                "tipo": "INGRESO",
                "monto": data["monto"],
                "origen_tipo": "INGRESO",
                "origen_id": ingreso_id,
                "descripcion": data.get("concepto", "Ingreso registrado"),
                "registrado_por": usuario_id,
                "fecha": data.get("fecha", date.today().strftime("%Y-%m-%d")),
            }

            # Crear movimiento en caja
            movimiento_id = movimiento_model.create(movimiento_data, usuario_id)

            if movimiento_id:
                print(f"✓ Movimiento en caja registrado con ID: {movimiento_id}")
                return True

            return False

        except Exception as e:
            print(f"✗ Error registrando movimiento en caja: {e}")
            return False

    def _actualizar_movimiento_caja(
        self, ingreso_id: int, data: Dict[str, Any]
    ) -> bool:
        """
        Actualiza el movimiento en caja asociado al ingreso

        Args:
            ingreso_id: ID del ingreso
            data: Nuevos datos del ingreso

        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            # Importar modelo de movimiento de caja
            from models.movimiento_caja_model import MovimientoCajaModel

            movimiento_model = MovimientoCajaModel()

            # Buscar movimiento asociado
            movimiento = movimiento_model.get_by_origen("INGRESO", ingreso_id)

            if not movimiento:
                print("⚠ No se encontró movimiento en caja asociado")
                return False

            # Actualizar monto si cambió
            if "monto" in data:
                update_data = {
                    "monto": data["monto"],
                    "descripcion": data.get("concepto", movimiento.get("descripcion")),
                }

                return movimiento_model.update(movimiento["id"], update_data)

            return True

        except Exception as e:
            print(f"✗ Error actualizando movimiento en caja: {e}")
            return False

    def _eliminar_movimiento_caja(self, ingreso_id: int) -> bool:
        """
        Elimina el movimiento en caja asociado al ingreso

        Args:
            ingreso_id: ID del ingreso

        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            # Importar modelo de movimiento de caja
            from models.movimiento_caja_model import MovimientoCajaModel

            movimiento_model = MovimientoCajaModel()

            # Buscar movimiento asociado
            movimiento = movimiento_model.get_by_origen("INGRESO", ingreso_id)

            if not movimiento:
                print("⚠ No se encontró movimiento en caja asociado")
                return False

            # Eliminar movimiento
            return movimiento_model.delete(movimiento["id"])

        except Exception as e:
            print(f"✗ Error eliminando movimiento en caja: {e}")
            return False

    # ============ MÉTODOS DE GESTIÓN DE ESTADOS ============

    def cambiar_estado(
        self, ingreso_id: int, nuevo_estado: str, usuario_id: Optional[int] = None
    ) -> bool:
        """
        Cambia el estado de un ingreso

        Args:
            ingreso_id: ID del ingreso
            nuevo_estado: Nuevo estado del ingreso
            usuario_id: ID del usuario que realiza el cambio

        Returns:
            bool: True si se cambió correctamente
        """
        if nuevo_estado not in self.ESTADOS_TRANSACCION:
            print(f"✗ Estado inválido: {nuevo_estado}")
            return False

        try:
            data = {"estado": nuevo_estado}

            # Si se confirma, registrar fecha de confirmación
            if nuevo_estado == "CONFIRMADO":
                # En una implementación completa, se podría agregar un campo fecha_confirmacion
                pass

            # Si se anula, también anular movimiento en caja
            elif nuevo_estado == "ANULADO":
                self._anular_movimiento_caja(ingreso_id)

            return self.update(ingreso_id, data, usuario_id)

        except Exception as e:
            print(f"✗ Error cambiando estado del ingreso: {e}")
            return False

    def _anular_movimiento_caja(self, ingreso_id: int) -> bool:
        """
        Anula el movimiento en caja asociado al ingreso

        Args:
            ingreso_id: ID del ingreso

        Returns:
            bool: True si se anuló correctamente
        """
        try:
            # Importar modelo de movimiento de caja
            from models.movimiento_caja_model import MovimientoCajaModel

            movimiento_model = MovimientoCajaModel()

            # Buscar movimiento asociado
            movimiento = movimiento_model.get_by_origen("INGRESO", ingreso_id)

            if not movimiento:
                return False

            # En una implementación completa, se marcaría el movimiento como anulado
            # Por ahora, simplemente actualizamos la descripción
            update_data = {
                "descripcion": f"ANULADO - {movimiento.get('descripcion', '')}"
            }

            return movimiento_model.update(movimiento["id"], update_data)

        except Exception as e:
            print(f"✗ Error anulando movimiento en caja: {e}")
            return False

    def _actualizar_estado_matricula(self, matricula_id: int, ingreso_id: int) -> bool:
        """
        Actualiza el estado de pago en la matrícula

        Args:
            matricula_id: ID de la matrícula
            ingreso_id: ID del ingreso registrado

        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            if not matricula_id:
                return False

            # Importar modelo de matrícula
            from models.matricula_model import MatriculaModel

            matricula_model = MatriculaModel()

            # Obtener matrícula
            matricula = matricula_model.read(matricula_id)
            if not matricula:
                return False

            # Obtener total pagado de matrícula
            total_pagado = self.get_total_pagado_matricula(matricula_id)
            monto_final = Decimal(str(matricula.get("monto_final", 0)))

            # Actualizar monto pagado en matrícula
            data = {"monto_pagado": float(total_pagado)}
            return matricula_model.update(matricula_id, data)

        except Exception as e:
            print(f"✗ Error actualizando estado de matrícula: {e}")
            return False

    # ============ MÉTODOS DE CONSULTA AVANZADOS ============

    def get_all(
        self,
        tipo_ingreso: Optional[str] = None,
        matricula_id: Optional[int] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        estado: Optional[str] = None,
        registrado_por: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "fecha",
        order_desc: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todos los ingresos

        Args:
            tipo_ingreso: Filtrar por tipo de ingreso
            matricula_id: Filtrar por matrícula específica
            fecha_desde: Fecha inicial (YYYY-MM-DD)
            fecha_hasta: Fecha final (YYYY-MM-DD)
            estado: Filtrar por estado
            registrado_por: Filtrar por usuario que registró
            limit: Límite de registros
            offset: Desplazamiento para paginación
            order_by: Campo para ordenar
            order_desc: Si es True, orden descendente

        Returns:
            List[Dict]: Lista de ingresos
        """
        try:
            query = f"""
            SELECT i.*,
                   m.estudiante_id,
                   e.nombres as estudiante_nombres,
                   e.apellidos as estudiante_apellidos,
                   p.nombre as programa_nombre,
                   u.username as registrado_por_usuario,
                   u.nombre_completo as registrado_por_nombre
            FROM {self.table_name} i
            LEFT JOIN matriculas m ON i.matricula_id = m.id
            LEFT JOIN estudiantes e ON m.estudiante_id = e.id
            LEFT JOIN programas_academicos p ON m.programa_id = p.id
            LEFT JOIN usuarios u ON i.registrado_por = u.id
            """

            conditions: List[str] = []
            params: List[Any] = []

            if tipo_ingreso is not None:
                conditions.append("i.tipo_ingreso = %s")
                params.append(tipo_ingreso)

            if matricula_id is not None:
                conditions.append("i.matricula_id = %s")
                params.append(matricula_id)

            if fecha_desde is not None:
                conditions.append("i.fecha >= %s")
                params.append(fecha_desde)

            if fecha_hasta is not None:
                conditions.append("i.fecha <= %s")
                params.append(fecha_hasta)

            if estado is not None:
                conditions.append("i.estado = %s")
                params.append(estado)

            if registrado_por is not None:
                conditions.append("i.registrado_por = %s")
                params.append(registrado_por)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            # Ordenar
            order_dir = "DESC" if order_desc else "ASC"
            query += f" ORDER BY i.{order_by} {order_dir}"

            # Paginación
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            return self.fetch_all(query, params)

        except Exception as e:
            print(f"✗ Error obteniendo ingresos: {e}")
            return []

    def get_by_matricula(
        self, matricula_id: int, estado: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene ingresos por matrícula

        Args:
            matricula_id: ID de la matrícula
            estado: Filtrar por estado

        Returns:
            List[Dict]: Lista de ingresos de la matrícula
        """
        return self.get_all(matricula_id=matricula_id, estado=estado)

    def get_by_estudiante(
        self,
        estudiante_id: int,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene ingresos por estudiante

        Args:
            estudiante_id: ID del estudiante
            fecha_desde: Fecha inicial (YYYY-MM-DD)
            fecha_hasta: Fecha final (YYYY-MM-DD)

        Returns:
            List[Dict]: Lista de ingresos del estudiante
        """
        try:
            query = f"""
            SELECT i.*,
                   m.estudiante_id,
                   e.nombres as estudiante_nombres,
                   e.apellidos as estudiante_apellidos,
                   p.nombre as programa_nombre
            FROM {self.table_name} i
            JOIN matriculas m ON i.matricula_id = m.id
            JOIN estudiantes e ON m.estudiante_id = e.id
            JOIN programas_academicos p ON m.programa_id = p.id
            WHERE m.estudiante_id = %s
            """

            params = [estudiante_id]

            if fecha_desde is not None:
                query += " AND i.fecha >= %s"
                params.append(fecha_desde)  # type: ignore

            if fecha_hasta is not None:
                query += " AND i.fecha <= %s"
                params.append(fecha_hasta)  # type: ignore

            query += " ORDER BY i.fecha DESC"

            return self.fetch_all(query, params)

        except Exception as e:
            print(f"✗ Error obteniendo ingresos por estudiante: {e}")
            return []

    def get_by_fecha(
        self, fecha: str, estado: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene ingresos por fecha específica

        Args:
            fecha: Fecha a consultar (YYYY-MM-DD)
            estado: Filtrar por estado

        Returns:
            List[Dict]: Lista de ingresos de la fecha
        """
        return self.get_all(fecha_desde=fecha, fecha_hasta=fecha, estado=estado)

    def search(
        self,
        search_term: str,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        estado: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Busca ingresos por término de búsqueda

        Args:
            search_term: Término a buscar
            fecha_desde: Fecha inicial (YYYY-MM-DD)
            fecha_hasta: Fecha final (YYYY-MM-DD)
            estado: Filtrar por estado

        Returns:
            List[Dict]: Lista de ingresos que coinciden
        """
        try:
            query = f"""
            SELECT i.*,
                   m.estudiante_id,
                   e.nombres as estudiante_nombres,
                   e.apellidos as estudiante_apellidos,
                   p.nombre as programa_nombre,
                   u.username as registrado_por_usuario
            FROM {self.table_name} i
            LEFT JOIN matriculas m ON i.matricula_id = m.id
            LEFT JOIN estudiantes e ON m.estudiante_id = e.id
            LEFT JOIN programas_academicos p ON m.programa_id = p.id
            LEFT JOIN usuarios u ON i.registrado_por = u.id
            WHERE (i.concepto ILIKE %s 
                   OR i.nro_comprobante ILIKE %s 
                   OR i.nro_transaccion ILIKE %s
                   OR e.nombres ILIKE %s 
                   OR e.apellidos ILIKE %s)
            """

            params = [
                f"%{search_term}%",
                f"%{search_term}%",
                f"%{search_term}%",
                f"%{search_term}%",
                f"%{search_term}%",
            ]

            if fecha_desde is not None:
                query += " AND i.fecha >= %s"
                params.append(fecha_desde)

            if fecha_hasta is not None:
                query += " AND i.fecha <= %s"
                params.append(fecha_hasta)

            if estado is not None:
                query += " AND i.estado = %s"
                params.append(estado)

            query += " ORDER BY i.fecha DESC"

            return self.fetch_all(query, params)

        except Exception as e:
            print(f"✗ Error buscando ingresos: {e}")
            return []

    # ============ MÉTODOS DE CÁLCULO Y REPORTES ============

    def get_total_pagado_matricula(self, matricula_id: int) -> Decimal:
        """
        Calcula el total pagado por una matrícula

        Args:
            matricula_id: ID de la matrícula

        Returns:
            Decimal: Total pagado
        """
        try:
            query = f"""
            SELECT COALESCE(SUM(monto), 0) as total_pagado
            FROM {self.table_name}
            WHERE matricula_id = %s 
              AND estado IN ('REGISTRADO', 'CONFIRMADO', 'CONTABILIZADO')
            """

            result = self.fetch_one(query, (matricula_id,))
            return Decimal(str(result["total_pagado"])) if result else Decimal("0")

        except Exception as e:
            print(f"✗ Error calculando total pagado: {e}")
            return Decimal("0")

    def get_ingresos_por_periodo(
        self, fecha_desde: str, fecha_hasta: str
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de ingresos por período

        Args:
            fecha_desde: Fecha inicial (YYYY-MM-DD)
            fecha_hasta: Fecha final (YYYY-MM-DD)

        Returns:
            Dict: Estadísticas del período
        """
        try:
            query = f"""
            SELECT 
                tipo_ingreso,
                COUNT(*) as cantidad,
                SUM(monto) as total_monto,
                AVG(monto) as promedio_monto
            FROM {self.table_name}
            WHERE fecha BETWEEN %s AND %s 
              AND estado IN ('REGISTRADO', 'CONFIRMADO', 'CONTABILIZADO')
            GROUP BY tipo_ingreso
            ORDER BY total_monto DESC
            """

            resultados = self.fetch_all(query, (fecha_desde, fecha_hasta))

            # Calcular totales
            total_general = Decimal("0")
            cantidad_total = 0

            for row in resultados:
                total_general += Decimal(str(row["total_monto"]))
                cantidad_total += row["cantidad"]

            return {
                "fecha_desde": fecha_desde,
                "fecha_hasta": fecha_hasta,
                "total_general": float(total_general),
                "cantidad_total": cantidad_total,
                "promedio_general": (
                    float(total_general / Decimal(str(cantidad_total)))
                    if cantidad_total > 0
                    else 0
                ),
                "detalle_por_tipo": resultados,
            }

        except Exception as e:
            print(f"✗ Error obteniendo ingresos por período: {e}")
            return {
                "fecha_desde": fecha_desde,
                "fecha_hasta": fecha_hasta,
                "total_general": 0.0,
                "cantidad_total": 0,
                "promedio_general": 0.0,
                "detalle_por_tipo": [],
            }

    def get_ingresos_por_mes(
        self, año: int, mes: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene ingresos por mes

        Args:
            año: Año a consultar
            mes: Mes específico (opcional)

        Returns:
            List[Dict]: Ingresos por mes
        """
        try:
            if mes:
                fecha_desde = f"{año:04d}-{mes:02d}-01"
                if mes == 12:
                    fecha_hasta = f"{año:04d}-12-31"
                else:
                    fecha_hasta = f"{año:04d}-{(mes+1):02d}-01"

                query = f"""
                SELECT 
                    EXTRACT(DAY FROM fecha) as dia,
                    COUNT(*) as cantidad,
                    SUM(monto) as total
                FROM {self.table_name}
                WHERE fecha BETWEEN %s AND %s 
                  AND estado IN ('REGISTRADO', 'CONFIRMADO', 'CONTABILIZADO')
                GROUP BY EXTRACT(DAY FROM fecha)
                ORDER BY dia
                """

                params: List[Any] = [fecha_desde, fecha_hasta]
                return self.fetch_all(query, params)
            else:
                query = f"""
                SELECT 
                    EXTRACT(MONTH FROM fecha) as mes,
                    COUNT(*) as cantidad,
                    SUM(monto) as total
                FROM {self.table_name}
                    WHERE EXTRACT(YEAR FROM fecha) = %s 
                  AND estado IN ('REGISTRADO', 'CONFIRMADO', 'CONTABILIZADO')
                GROUP BY EXTRACT(MONTH FROM fecha)
                ORDER BY mes
                """

                return self.fetch_all(query, (año,))

        except Exception as e:
            print(f"✗ Error obteniendo ingresos por mes: {e}")
            return []

    # ============ MÉTODOS PARA DASHBOARD ============

    def get_total_ingresos(
        self,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        estado: Optional[str] = None,
    ) -> Decimal:
        """
        Obtiene el total de ingresos

        Args:
            fecha_desde: Fecha inicial (YYYY-MM-DD)
            fecha_hasta: Fecha final (YYYY-MM-DD)
            estado: Filtrar por estado

        Returns:
            Decimal: Total de ingresos
        """
        try:
            query = f"SELECT COALESCE(SUM(monto), 0) as total FROM {self.table_name}"
            conditions = []
            params = []

            if fecha_desde is not None:
                conditions.append("fecha >= %s")
                params.append(fecha_desde)

            if fecha_hasta is not None:
                conditions.append("fecha <= %s")
                params.append(fecha_hasta)

            if estado is not None:
                conditions.append("estado = %s")
                params.append(estado)
            else:
                # Por defecto, solo contar ingresos válidos
                conditions.append(
                    "estado IN ('REGISTRADO', 'CONFIRMADO', 'CONTABILIZADO')"
                )

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            result = self.fetch_one(query, params)
            return Decimal(str(result["total"])) if result else Decimal("0")

        except Exception as e:
            print(f"✗ Error obteniendo total de ingresos: {e}")
            return Decimal("0")

    def get_ingresos_por_tipo(
        self, fecha_desde: Optional[str] = None, fecha_hasta: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene distribución de ingresos por tipo

        Args:
            fecha_desde: Fecha inicial (YYYY-MM-DD)
            fecha_hasta: Fecha final (YYYY-MM-DD)

        Returns:
            List[Dict]: Distribución por tipo
        """
        try:
            query = f"""
            SELECT 
                tipo_ingreso,
                COUNT(*) as cantidad,
                SUM(monto) as total_monto
            FROM {self.table_name}
            WHERE estado IN ('REGISTRADO', 'CONFIRMADO', 'CONTABILIZADO')
            """

            conditions = []
            params = []

            if fecha_desde is not None:
                conditions.append("fecha >= %s")
                params.append(fecha_desde)

            if fecha_hasta is not None:
                conditions.append("fecha <= %s")
                params.append(fecha_hasta)

            if conditions:
                query += " AND " + " AND ".join(conditions)

            query += " GROUP BY tipo_ingreso ORDER BY total_monto DESC"

            return self.fetch_all(query, params)

        except Exception as e:
            print(f"✗ Error obteniendo ingresos por tipo: {e}")
            return []

    # ============ MÉTODOS DE AUDITORÍA ============

    def _registrar_auditoria(
        self, accion: str, ingreso_id: int, usuario_id: Optional[int] = None
    ):
        """
        Registra acción de auditoría para el ingreso

        Args:
            accion: Acción realizada (CREACION, ACTUALIZACION, ELIMINACION)
            ingreso_id: ID del ingreso
            usuario_id: ID del usuario que realizó la acción
        """
        try:
            # En una implementación real, esto se registraría en una tabla de auditoría
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            usuario_info = f" (Usuario: {usuario_id})" if usuario_id else ""

            print(
                f"📋 Auditoría - {timestamp} - {accion} ingreso {ingreso_id}{usuario_info}"
            )

        except Exception as e:
            print(f"✗ Error registrando auditoría: {e}")

    # ============ MÉTODOS DE VALIDACIÓN DE UNICIDAD ============

    def comprobante_exists(
        self, nro_comprobante: str, exclude_id: Optional[int] = None
    ) -> bool:
        """
        Verifica si un número de comprobante ya existe

        Args:
            nro_comprobante: Número de comprobante a verificar
            exclude_id: ID a excluir (para actualizaciones)

        Returns:
            bool: True si existe, False en caso contrario
        """
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE nro_comprobante = %s"
            params: List[Any] = [nro_comprobante]

            if exclude_id is not None:
                query += " AND id != %s"
                params.append(exclude_id)

            result = self.fetch_one(query, params)
            return result["count"] > 0 if result else False

        except Exception as e:
            print(f"✗ Error verificando número de comprobante: {e}")
            return False

    def matricula_tipo_exists(
        self, matricula_id: int, tipo_ingreso: str, exclude_id: Optional[int] = None
    ) -> bool:
        """
        Verifica si ya existe un ingreso del mismo tipo para la matrícula

        Args:
            matricula_id: ID de la matrícula
            tipo_ingreso: Tipo de ingreso
            exclude_id: ID a excluir (para actualizaciones)

        Returns:
            bool: True si existe, False en caso contrario
        """
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE matricula_id = %s AND tipo_ingreso = %s"
            params: List[Any] = [matricula_id, tipo_ingreso]

            if exclude_id is not None:
                query += " AND id != %s"
                params.append(exclude_id)

            result = self.fetch_one(query, params)
            return result["count"] > 0 if result else False

        except Exception as e:
            print(f"✗ Error verificando matrícula-tipo: {e}")
            return False

    # ============ MÉTODOS DE COMPATIBILIDAD ============

    def obtener_todos(self):
        """Método de compatibilidad con nombres antiguos"""
        return self.get_all()

    def obtener_por_id(self, ingreso_id):
        """Método de compatibilidad con nombres antiguos"""
        return self.read(ingreso_id)

    def obtener_por_matricula(self, matricula_id):
        """Método de compatibilidad con nombres antiguos"""
        return self.get_by_matricula(matricula_id)

    def buscar_ingresos(self, termino):
        """Método de compatibilidad con nombres antiguos"""
        return self.search(termino)

    def update_table(self, table, data, condition, params=None):
        """Método helper para actualizar (compatibilidad con BaseModel)"""
        return self.update(table, data, condition, params)  # type: ignore

    # ============ MÉTODOS DE UTILIDAD ============

    def get_tipos_ingreso(self) -> List[str]:
        """
        Obtiene la lista de tipos de ingreso

        Returns:
            List[str]: Lista de tipos
        """
        return self.TIPOS_INGRESO.copy()

    def get_formas_pago(self) -> List[str]:
        """
        Obtiene la lista de formas de pago

        Returns:
            List[str]: Lista de formas de pago
        """
        return self.FORMAS_PAGO.copy()

    def get_estados_transaccion(self) -> List[str]:
        """
        Obtiene la lista de estados de transacción

        Returns:
            List[str]: Lista de estados
        """
        return self.ESTADOS_TRANSACCION.copy()
