# app/models/gasto_model.py
"""
Modelo para gestión de gastos operativos del sistema.

Este modelo maneja el registro, validación y procesamiento de gastos,
incluyendo el registro automático de movimientos de caja (egresos) y
la gestión de comprobantes asociados.

Hereda de BaseModel para utilizar el sistema de conexiones y transacciones.
"""
import sys
import os
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple, Union

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_model import BaseModel
from .movimiento_caja_model import MovimientoCajaModel

logger = logging.getLogger(__name__)


class GastoModel(BaseModel):
    """Modelo que representa un gasto operativo en el sistema"""

    def __init__(self):
        """Inicializa el modelo de gastos"""
        super().__init__()
        self.table_name = "gastos"
        self.sequence_name = "seq_gastos_id"

        # Tipos enumerados según la base de datos
        self.CATEGORIAS = [
            "PAGO_DOCENTE",
            "ALQUILER",
            "SERVICIOS_BASICOS",
            "MATERIALES",
            "PUBLICIDAD",
            "TRANSPORTE",
            "ALIMENTACION",
            "MANTENIMIENTO",
            "TECNOLOGIA",
            "SEGUROS",
            "IMPUESTOS",
            "SERVICIOS PROFESIONALES",
            "GASTOS_BANCARIOS",
            "OTROS",
        ]

        # Subcategorías por categoría (opcional)
        self.SUBCATEGORIAS = {
            "PAGO_DOCENTE": [
                "Pago de honorarios docentes",
                "Viáticos para capacitación docente",
                "Bono por desempeño académico",
                "Pago horas extras docentes",
                "Aguinaldo docente",
            ],
            "ALQUILER": [
                "Alquiler de local comercial",
                "Alquiler de aulas",
                "Alquiler de equipo audiovisual",
                "Alquiler de vehículo institucional",
            ],
            "SERVICIOS_BASICOS": [
                "Pago de servicio de electricidad",
                "Pago de servicio de agua potable",
                "Factura de internet institucional",
                "Pago de servicio de telefonía",
            ],
            "MATERIALES": [
                "Compra de material de oficina",
                "Adquisición de libros educativos",
                "Material de limpieza y aseo",
                "Insumos para laboratorio",
            ],
            "PUBLICIDAD": [
                "Campaña publicitaria en redes sociales",
                "Impresión de volantes promocionales",
                "Publicidad en Google Ads",
                "Anuncios en periódico local",
            ],
            "TRANSPORTE": [
                "Recarga de combustible vehículo institucional",
                "Pasajes para personal administrativo",
                "Mantenimiento preventivo de vehículos",
                "Pago de parqueos institucionales",
            ],
            "ALIMENTACION": [
                "Refrigerios para reunión de personal",
                "Almuerzo para visita de supervisión",
                "Servicio de catering para evento",
                "Viáticos de alimentación para capacitación",
            ],
            "MANTENIMIENTO": [
                "Mantenimiento eléctrico del edificio",
                "Reparación de tuberías de agua",
                "Pintura de aulas y oficinas",
                "Servicio de jardinería y áreas verdes",
            ],
            "TECNOLOGIA": [
                "Renovación de licencias de software",
                "Compra de computadoras nuevas",
                "Servicio de hosting web institucional",
                "Mantenimiento de red de computadoras",
            ],
            "SEGUROS": [
                "Pago de prima de seguro de salud",
                "Seguro de responsabilidad civil",
                "Seguro contra incendios del local",
                "Seguro de equipos tecnológicos",
            ],
            "IMPUESTOS": [
                "Pago de IVA trimestral",
                "Declaración de impuesto a la renta",
                "Patente municipal anual",
                "Tasas por permisos de funcionamiento",
            ],
            "SERVICIOS_PROFESIONALES": [
                "Honorarios de contador externo",
                "Asesoría legal para contratos",
                "Desarrollo de software" "Servicios de auditoría financiera",
                "Consultoría en marketing digital",
            ],
            "GASTOS_BANCARIOS": [
                "Comisión por transferencias bancarias",
                "Intereses de préstamo institucional",
                "Seguro de caja fuerte bancaria",
                "Mantenimiento de cuenta corriente",
            ],
            "LOGISTICA": [
                "Empaque y envío de material educativo",
                "Almacenamiento de libros y materiales",
                "Transporte de equipo entre sedes",
                "Gastos de importación de equipos",
            ],
            "OTROS": [
                "Reposición de Caja Chica",
                "Gastos administrativos varios",
                "Pago de multas administrativas",
                "Gastos de representación institucional",
                "Ajustes y diferencias de caja",
            ],
        }

        # Formas de pago según el tipo ENUM en la base de datos
        self.FORMAS_PAGO = [
            "EFECTIVO",
            "DEPOSITO BANCARIO",
            "TRANSFERENCIA QR",
            "TARJETA",
            "CHEQUE",
        ]

        # Columnas de la tabla para validación
        self.columns = [
            "id",
            "fecha",
            "monto",
            "categoria",
            "subcategoria",
            "descripcion",
            "proveedor",
            "nro_factura",
            "forma_pago",
            "comprobante_nro",
            "registrado_por",
            "created_at",
        ]

        # Columnas requeridas
        self.required_columns = ["fecha", "monto", "categoria"]

        # Columnas de tipo decimal
        self.decimal_columns = ["monto"]

        # Columnas de tipo entero
        self.integer_columns = ["registrado_por"]

        # Columnas de tipo fecha
        self.date_columns = ["fecha"]

    # ============ MÉTODOS DE VALIDACIÓN ============

    def _validate_gasto_data(
        self, data: Dict[str, Any], for_update: bool = False
    ) -> Tuple[bool, str]:
        """
        Valida los datos del gasto antes de operaciones CRUD

        Args:
            data: Diccionario con datos del gasto
            for_update: Si es True, valida para actualización

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        # Campos requeridos para creación
        if not for_update:
            for field in self.required_columns:
                if field not in data or data[field] is None:
                    return False, f"Campo requerido faltante: {field}"

        # Validar categoría
        if "categoria" in data and data["categoria"]:
            if data["categoria"] not in self.CATEGORIAS:
                return (
                    False,
                    f"Categoría inválida. Válidas: {', '.join(self.CATEGORIAS)}",
                )

        # Validar subcategoría si se proporciona
        if "subcategoria" in data and data["subcategoria"]:
            categoria = data.get("categoria")
            if categoria and categoria in self.SUBCATEGORIAS:
                if data["subcategoria"] not in self.SUBCATEGORIAS[categoria]:
                    return (
                        False,
                        f"Subcategoría inválida para {categoria}. "
                        f"Válidas: {', '.join(self.SUBCATEGORIAS[categoria])}",
                    )

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
                    f"Forma de pago inválida. Válidas: {', '.join(self.FORMAS_PAGO)}",
                )

        # Validar número de comprobante único si se proporciona
        if "comprobante_nro" in data and data["comprobante_nro"]:
            existing_id = None
            if for_update and "id" in data:
                existing_id = data["id"]

            if self.comprobante_exists(data["comprobante_nro"], exclude_id=existing_id):
                return (
                    False,
                    f"El número de comprobante {data['comprobante_nro']} ya existe",
                )

        # Validar usuario registrador si se proporciona
        if "registrado_por" in data and data["registrado_por"]:
            if not self._usuario_exists(data["registrado_por"]):
                return False, f"Usuario con ID {data['registrado_por']} no existe"

        # Validar fecha si se proporciona
        if "fecha" in data and data["fecha"]:
            if not self._is_valid_date(data["fecha"]):
                return False, "Formato de fecha inválido. Use YYYY-MM-DD"

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

    def _usuario_exists(self, usuario_id: int) -> bool:
        """Verifica si el usuario existe"""
        try:
            query = (
                "SELECT COUNT(*) as count FROM usuarios WHERE id = %s AND activo = TRUE"
            )
            result = self.fetch_one(query, (usuario_id,))
            return result["count"] > 0 if result else False
        except Exception:
            logger.warning(f"No se pudo verificar usuario con ID {usuario_id}")
            return False

    def comprobante_exists(
        self, comprobante_nro: str, exclude_id: Optional[int] = None
    ) -> bool:
        """
        Verifica si un número de comprobante ya existe

        Args:
            comprobante_nro: Número de comprobante a verificar
            exclude_id: ID a excluir de la verificación (para updates)

        Returns:
            bool: True si existe, False en caso contrario
        """
        try:
            if exclude_id:
                query = """
                SELECT COUNT(*) as count 
                FROM gastos 
                WHERE comprobante_nro = %s AND id != %s
                """
                params = (comprobante_nro, exclude_id)
            else:
                query = (
                    "SELECT COUNT(*) as count FROM gastos WHERE comprobante_nro = %s"
                )
                params = (comprobante_nro,)

            result = self.fetch_one(query, params)
            return result["count"] > 0 if result else False
        except Exception:
            return False

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza los datos del gasto

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
        self,
        data: Dict[str, Any],
        usuario_id: Optional[int] = None,
        registrar_movimiento: bool = True,
    ) -> Optional[int]:
        """
        Crea un nuevo gasto y registra el movimiento de caja correspondiente

        Args:
            data: Diccionario con datos del gasto
            usuario_id: ID del usuario que registra el gasto
            registrar_movimiento: Si es True, registra automáticamente el movimiento de caja

        Returns:
            Optional[int]: ID del gasto creado o None si hay error
        """
        # Sanitizar datos
        data = self._sanitize_data(data)

        # Añadir usuario registrador si se proporciona
        if usuario_id:
            data["registrado_por"] = usuario_id

        # Validar datos
        is_valid, error_msg = self._validate_gasto_data(data, for_update=False)

        if not is_valid:
            logger.error(f"Error validando datos de gasto: {error_msg}")
            return None

        try:
            # Iniciar transacción
            self.begin_transaction()

            # Preparar datos para inserción
            insert_data = data.copy()

            # Establecer valores por defecto
            defaults = {"created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

            for key, value in defaults.items():
                if key not in insert_data or insert_data[key] is None:
                    insert_data[key] = value

            # Insertar en base de datos
            gasto_id = self.insert(self.table_name, insert_data, returning="id")

            if not gasto_id:
                self.rollback()
                logger.error("No se pudo insertar el gasto en la base de datos")
                return None

            logger.info(f"✓ Gasto creado exitosamente con ID: {gasto_id}")

            # Registrar movimiento de caja si corresponde
            if registrar_movimiento:
                movimiento_creado = self._registrar_movimiento_caja(
                    gasto_id, insert_data, usuario_id
                )

                if not movimiento_creado:
                    self.rollback()
                    logger.error("Rollback: No se pudo registrar movimiento en caja")
                    return None

            # Commit de la transacción
            self.commit()
            logger.info(f"✓ Transacción completada para gasto ID: {gasto_id}")

            # Generar comprobantes si corresponde
            self._generar_comprobantes(gasto_id, insert_data)

            return gasto_id

        except Exception as e:
            # Rollback en caso de error
            self.rollback()
            logger.error(f"Error creando gasto: {e}", exc_info=True)
            return None

    def _registrar_movimiento_caja(
        self, gasto_id: int, data: Dict[str, Any], usuario_id: Optional[int] = None
    ) -> bool:
        """
        Registra el movimiento de caja correspondiente al gasto

        Args:
            gasto_id: ID del gasto registrado
            data: Datos del gasto
            usuario_id: ID del usuario que registra

        Returns:
            bool: True si se registró correctamente, False en caso contrario
        """
        try:
            # Crear descripción para el movimiento
            descripcion = f"Gasto: {data['categoria']}"

            if data.get("subcategoria"):
                descripcion += f" - {data['subcategoria']}"

            if data.get("descripcion"):
                # Limitar longitud de descripción
                desc_short = (
                    data["descripcion"][:50] + "..."
                    if len(data["descripcion"]) > 50
                    else data["descripcion"]
                )
                descripcion += f" ({desc_short})"

            if data.get("proveedor"):
                descripcion += f" | Prov: {data['proveedor']}"

            # Crear datos para el movimiento
            movimiento_data = {
                "fecha": data.get("fecha", datetime.now().strftime("%Y-%m-%d")),
                "tipo": "GASTO",
                "monto": data["monto"],
                "descripcion": descripcion,
                "origen_tipo": "GASTO",
                "origen_id": gasto_id,
            }

            # Registrar movimiento usando MovimientoCajaModel
            movimiento_model = MovimientoCajaModel()
            movimiento_id = movimiento_model.create(movimiento_data, usuario_id)

            if movimiento_id:
                logger.info(f"✓ Movimiento de caja registrado con ID: {movimiento_id}")
                return True
            else:
                logger.error("No se pudo crear el movimiento de caja")
                return False

        except Exception as e:
            logger.error(f"Error registrando movimiento de caja: {e}", exc_info=True)
            return False

    def _generar_comprobantes(self, gasto_id: int, data: Dict[str, Any]) -> None:
        """
        Genera comprobantes asociados al gasto según sea necesario

        Args:
            gasto_id: ID del gasto
            data: Datos del gasto
        """
        try:
            comprobantes = []

            # Comprobante principal (si no hay número ya asignado)
            if not data.get("comprobante_nro"):
                comprobante_principal = {
                    "tipo": "GASTO",
                    "numero": self._generar_numero_comprobante(),
                    "gasto_id": gasto_id,
                    "fecha": data["fecha"],
                    "monto": data["monto"],
                    "descripcion": f"Comprobante de gasto: {data['categoria']}",
                }
                comprobantes.append(comprobante_principal)

            # Comprobante fiscal si el monto es significativo
            if data["monto"] >= Decimal("1000.00") and data.get("nro_factura"):
                comprobante_fiscal = {
                    "tipo": "FACTURA",
                    "numero": data["nro_factura"],
                    "gasto_id": gasto_id,
                    "fecha": data["fecha"],
                    "monto": data["monto"],
                    "descripcion": f"Factura: {data.get('proveedor', 'Proveedor')}",
                }
                comprobantes.append(comprobante_fiscal)

            # Comprobante interno adicional
            comprobante_interno = {
                "tipo": "INTERNO",
                "numero": f"INT-GASTO-{gasto_id:06d}",
                "gasto_id": gasto_id,
                "fecha": data["fecha"],
                "monto": data["monto"],
                "descripcion": f"Comprobante interno gasto #{gasto_id}",
            }
            comprobantes.append(comprobante_interno)

            # Guardar comprobantes en base de datos (tabla hipotética 'comprobantes')
            for comp in comprobantes:
                try:
                    self._guardar_comprobante(comp)
                except Exception as e:
                    logger.warning(f"No se pudo guardar comprobante: {e}")

            if comprobantes:
                logger.info(
                    f"Generados {len(comprobantes)} comprobantes para gasto {gasto_id}"
                )

        except Exception as e:
            logger.error(f"Error generando comprobantes: {e}")

    def _generar_numero_comprobante(self) -> str:
        """Genera un número de comprobante secuencial"""
        try:
            # Obtener el último número de comprobante
            query = """
            SELECT MAX(CAST(SUBSTRING(comprobante_nro FROM 7) AS INTEGER)) as ultimo_num
            FROM gastos 
            WHERE comprobante_nro LIKE 'GASTO-%'
            """
            result = self.fetch_one(query)

            if result and result["ultimo_num"]:
                next_num = result["ultimo_num"] + 1
            else:
                next_num = 1

            return f"GASTO-{next_num:06d}"
        except Exception:
            # Fallback: usar timestamp
            return f"GASTO-{int(datetime.now().timestamp())}"

    # En el método _guardar_comprobante (línea ~490)
    def _guardar_comprobante(self, comprobante_data: Dict[str, Any]) -> bool:
        """
        Guarda un comprobante en la base de datos

        Args:
            comprobante_data: Datos del comprobante

        Returns:
            bool: True si se guardó correctamente
        """
        try:
            if comprobante_data["tipo"] == "GASTO":
                update_data = {"comprobante_nro": comprobante_data["numero"]}
                # Cambiar update_table por update
                return self.update(comprobante_data["gasto_id"], update_data) > 0
            return True
        except Exception:
            return False

    def read(self, gasto_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un gasto por su ID con información relacionada

        Args:
            gasto_id: ID del gasto

        Returns:
            Optional[Dict]: Datos del gasto o None si no existe
        """
        try:
            query = f"""
            SELECT g.*,
                   u.username as registrado_por_usuario,
                   u.nombre_completo as registrado_por_nombre,
                   mc.id as movimiento_caja_id,
                   mc.fecha as movimiento_fecha
            FROM {self.table_name} g
            LEFT JOIN usuarios u ON g.registrado_por = u.id
            LEFT JOIN movimientos_caja mc ON mc.origen_id = g.id AND mc.origen_tipo = 'GASTO'
            WHERE g.id = %s
            """

            result = self.fetch_one(query, (gasto_id,))
            return result

        except Exception as e:
            logger.error(f"Error obteniendo gasto: {e}")
            return None

    def update(
        self,
        gasto_id: int,
        data: Dict[str, Any],
        usuario_id: Optional[int] = None,
        actualizar_movimiento: bool = True,
    ) -> bool:
        """
        Actualiza un gasto existente

        Args:
            gasto_id: ID del gasto a actualizar
            data: Diccionario con datos a actualizar
            usuario_id: ID del usuario que realiza la actualización
            actualizar_movimiento: Si es True, actualiza el movimiento de caja asociado

        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        if not data:
            return False

        # Obtener datos actuales para validación
        gasto_actual = self.read(gasto_id)
        if not gasto_actual:
            return False

        # Combinar datos actuales con los nuevos para validación
        data_with_id = {**gasto_actual, **data}
        data_with_id["id"] = gasto_id

        # Sanitizar y validar datos
        data = self._sanitize_data(data)
        is_valid, error_msg = self._validate_gasto_data(data_with_id, for_update=True)

        if not is_valid:
            logger.error(f"Error validando datos: {error_msg}")
            return False

        try:
            # Iniciar transacción
            self.begin_transaction()

            # Actualizar en base de datos
            result = self.update(gasto_id, data)

            if not result:
                self.rollback()
                return False

            logger.info(f"✓ Gasto {gasto_id} actualizado exitosamente")

            # Actualizar movimiento de caja si corresponde
            if actualizar_movimiento and (data.get("monto") or data.get("descripcion")):
                movimiento_actualizado = self._actualizar_movimiento_caja(
                    gasto_id, data, usuario_id
                )

                if not movimiento_actualizado:
                    logger.warning(
                        f"No se pudo actualizar movimiento de caja para gasto {gasto_id}"
                    )

            # Commit de la transacción
            self.commit()

            # Registrar auditoría
            self._registrar_auditoria("ACTUALIZACION", gasto_id, usuario_id)

            return True

        except Exception as e:
            self.rollback()
            logger.error(f"Error actualizando gasto: {e}", exc_info=True)
            return False

    def _actualizar_movimiento_caja(
        self, gasto_id: int, data: Dict[str, Any], usuario_id: Optional[int] = None
    ) -> bool:
        """
        Actualiza el movimiento de caja asociado al gasto

        Args:
            gasto_id: ID del gasto
            data: Datos actualizados del gasto
            usuario_id: ID del usuario que realiza la actualización

        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            movimiento_model = MovimientoCajaModel()

            # Buscar movimiento asociado
            query = """
            SELECT id FROM movimientos_caja 
            WHERE origen_tipo = 'GASTO' AND origen_id = %s
            """
            movimiento = self.fetch_one(query, (gasto_id,))

            if not movimiento:
                logger.warning(
                    f"No se encontró movimiento de caja para gasto {gasto_id}"
                )
                return False

            movimiento_id = movimiento["id"]

            # Actualizar datos del movimiento
            update_data = {}

            if "monto" in data:
                update_data["monto"] = data["monto"]

            # Actualizar descripción si cambió categoría, subcategoría o descripción
            if any(
                key in data
                for key in ["categoria", "subcategoria", "descripcion", "proveedor"]
            ):
                # Obtener datos completos
                gasto_completo = self.read(gasto_id)
                if gasto_completo:
                    descripcion = f"Gasto: {gasto_completo['categoria']}"

                    if gasto_completo.get("subcategoria"):
                        descripcion += f" - {gasto_completo['subcategoria']}"

                    if gasto_completo.get("descripcion"):
                        desc_short = gasto_completo["descripcion"][:50]
                        if len(gasto_completo["descripcion"]) > 50:
                            desc_short += "..."
                        descripcion += f" ({desc_short})"

                    if gasto_completo.get("proveedor"):
                        descripcion += f" | Prov: {gasto_completo['proveedor']}"

                    update_data["descripcion"] = descripcion

            # Actualizar movimiento si hay cambios
            if update_data:
                return movimiento_model.update(movimiento_id, update_data, usuario_id)

            return True

        except Exception as e:
            logger.error(f"Error actualizando movimiento de caja: {e}")
            return False

    def delete(
        self,
        gasto_id: int,
        usuario_id: Optional[int] = None,
        eliminar_movimiento: bool = True,
    ) -> bool:
        """
        Elimina un gasto y opcionalmente su movimiento de caja asociado

        Args:
            gasto_id: ID del gasto
            usuario_id: ID del usuario que realiza la eliminación
            eliminar_movimiento: Si es True, elimina el movimiento de caja asociado

        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            # Verificar si el gasto existe
            gasto = self.read(gasto_id)
            if not gasto:
                return False

            # No permitir eliminar gastos antiguos (más de 30 días)
            fecha_gasto = datetime.strptime(gasto["fecha"], "%Y-%m-%d")
            dias_diferencia = (datetime.now() - fecha_gasto).days

            if dias_diferencia > 30:
                logger.error("No se pueden eliminar gastos de más de 30 días")
                return False

            # Iniciar transacción
            self.begin_transaction()

            # Eliminar movimiento de caja asociado si corresponde
            if eliminar_movimiento:
                movimiento_eliminado = self._eliminar_movimiento_caja(gasto_id)
                if not movimiento_eliminado:
                    logger.warning(
                        f"No se pudo eliminar movimiento de caja para gasto {gasto_id}"
                    )

            # Registrar auditoría antes de eliminar
            self._registrar_auditoria("ELIMINACION", gasto_id, usuario_id)

            # Eliminar el gasto
            query = f"DELETE FROM {self.table_name} WHERE id = %s"
            result = self.execute_query(query, (gasto_id,), commit=False)

            if result:
                self.commit()
                logger.info(f"✓ Gasto {gasto_id} eliminado exitosamente")
                return True
            else:
                self.rollback()
                return False

        except Exception as e:
            self.rollback()
            logger.error(f"Error eliminando gasto: {e}", exc_info=True)
            return False

    def _eliminar_movimiento_caja(self, gasto_id: int) -> bool:
        """
        Elimina el movimiento de caja asociado al gasto

        Args:
            gasto_id: ID del gasto

        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            movimiento_model = MovimientoCajaModel()

            # Buscar movimiento asociado
            query = """
            SELECT id FROM movimientos_caja 
            WHERE origen_tipo = 'GASTO' AND origen_id = %s
            """
            movimiento = self.fetch_one(query, (gasto_id,))

            if movimiento:
                return movimiento_model.delete(movimiento["id"])

            return True

        except Exception as e:
            logger.error(f"Error eliminando movimiento de caja: {e}")
            return False

    def _registrar_auditoria(
        self, accion: str, gasto_id: int, usuario_id: Optional[int] = None
    ) -> None:
        """
        Registra una acción en el log de auditoría

        Args:
            accion: Tipo de acción (CREACION, ACTUALIZACION, ELIMINACION)
            gasto_id: ID del gasto
            usuario_id: ID del usuario que realizó la acción
        """
        try:
            # Esta es una implementación de ejemplo
            # En una implementación real, usarías una tabla de auditoría
            logger.info(
                f"AUDITORIA - Gasto {gasto_id} - Acción: {accion} - "
                f"Usuario: {usuario_id or 'SISTEMA'} - "
                f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        except Exception:
            pass

    # ============ MÉTODOS DE CONSULTA AVANZADOS ============

    def buscar_por_fecha(
        self, fecha: Union[str, date, datetime], incluir_relaciones: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Busca gastos por fecha

        Args:
            fecha: Fecha a buscar
            incluir_relaciones: Si es True, incluye información de relaciones

        Returns:
            List[Dict]: Lista de gastos encontrados
        """
        try:
            # Normalizar fecha
            if isinstance(fecha, (datetime, date)):
                fecha_str = fecha.strftime("%Y-%m-%d")
            else:
                fecha_str = str(fecha)

            if incluir_relaciones:
                query = f"""
                SELECT g.*,
                       u.username as registrado_por_usuario,
                       u.nombre_completo as registrado_por_nombre
                FROM {self.table_name} g
                LEFT JOIN usuarios u ON g.registrado_por = u.id
                WHERE g.fecha = %s
                ORDER BY g.id DESC
                """
            else:
                query = f"""
                SELECT * FROM {self.table_name} 
                WHERE fecha = %s 
                ORDER BY id DESC
                """

            results = self.fetch_all(query, (fecha_str,))
            return results if results else []

        except Exception as e:
            logger.error(f"Error buscando gastos por fecha: {e}")
            return []

    def buscar_por_categoria(
        self,
        categoria: str,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Busca gastos por categoría, opcionalmente filtrados por rango de fechas

        Args:
            categoria: Categoría a buscar
            fecha_inicio: Fecha de inicio del rango (opcional)
            fecha_fin: Fecha de fin del rango (opcional)

        Returns:
            List[Dict]: Lista de gastos encontrados
        """
        try:
            if categoria not in self.CATEGORIAS:
                logger.warning(f"Categoría '{categoria}' no válida")
                return []

            params = [categoria]
            where_clauses = ["categoria = %s"]

            if fecha_inicio:
                where_clauses.append("fecha >= %s")
                params.append(fecha_inicio)

            if fecha_fin:
                where_clauses.append("fecha <= %s")
                params.append(fecha_fin)

            where_sql = " AND ".join(where_clauses)

            query = f"""
            SELECT * FROM {self.table_name} 
            WHERE {where_sql}
            ORDER BY fecha DESC, id DESC
            """

            results = self.fetch_all(query, tuple(params))
            return results if results else []

        except Exception as e:
            logger.error(f"Error buscando gastos por categoría: {e}")
            return []

    def obtener_total_por_categoria(
        self, fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None
    ) -> Dict[str, Decimal]:
        """
        Obtiene el total de gastos por categoría en un rango de fechas

        Args:
            fecha_inicio: Fecha de inicio del rango (opcional)
            fecha_fin: Fecha de fin del rango (opcional)

        Returns:
            Dict[str, Decimal]: Diccionario con categoría como clave y total como valor
        """
        try:
            params = []
            where_clauses = []

            if fecha_inicio:
                where_clauses.append("fecha >= %s")
                params.append(fecha_inicio)

            if fecha_fin:
                where_clauses.append("fecha <= %s")
                params.append(fecha_fin)

            where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

            query = f"""
            SELECT categoria, SUM(monto) as total
            FROM {self.table_name}
            {where_sql}
            GROUP BY categoria
            ORDER BY total DESC
            """

            results = self.fetch_all(query, tuple(params) if params else None)

            if not results:
                return {}

            # Convertir a diccionario con Decimal
            return {row["categoria"]: Decimal(str(row["total"])) for row in results}

        except Exception as e:
            logger.error(f"Error obteniendo total por categoría: {e}")
            return {}

    def obtener_resumen_mensual(self, año: int, mes: int) -> Dict[str, Any]:
        """
        Obtiene un resumen de gastos mensuales

        Args:
            año: Año del resumen
            mes: Mes del resumen (1-12)

        Returns:
            Dict[str, Any]: Diccionario con el resumen mensual
        """
        try:
            fecha_inicio = f"{año:04d}-{mes:02d}-01"

            # Obtener último día del mes
            if mes == 12:
                fecha_fin = f"{año:04d}-12-31"
            else:
                fecha_fin = f"{año:04d}-{(mes+1):02d}-01"
                # Restar un día para obtener el último día del mes actual
                fecha_fin = (
                    datetime.strptime(fecha_fin, "%Y-%m-%d") - timedelta(days=1)
                ).strftime("%Y-%m-%d")

            # Consulta para totales por categoría
            query_categorias = f"""
            SELECT categoria, COUNT(*) as cantidad, SUM(monto) as total
            FROM {self.table_name}
            WHERE fecha >= %s AND fecha <= %s
            GROUP BY categoria
            ORDER BY total DESC
            """

            # Consulta para total general
            query_total = f"""
            SELECT COUNT(*) as total_gastos, SUM(monto) as monto_total
            FROM {self.table_name}
            WHERE fecha >= %s AND fecha <= %s
            """

            categorias = self.fetch_all(query_categorias, (fecha_inicio, fecha_fin))
            total = self.fetch_one(query_total, (fecha_inicio, fecha_fin))

            # Consulta para gasto más alto
            query_max = f"""
            SELECT * FROM {self.table_name}
            WHERE fecha >= %s AND fecha <= %s
            ORDER BY monto DESC
            LIMIT 1
            """

            gasto_max = self.fetch_one(query_max, (fecha_inicio, fecha_fin))

            return {
                "periodo": f"{año}-{mes:02d}",
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "total_gastos": total["total_gastos"] if total else 0,
                "monto_total": (
                    Decimal(str(total["monto_total"]))
                    if total and total["monto_total"]
                    else Decimal("0.00")
                ),
                "categorias": categorias if categorias else [],
                "gasto_maximo": gasto_max if gasto_max else None,
            }

        except Exception as e:
            logger.error(f"Error obteniendo resumen mensual: {e}")
            return {}

    # ============ MÉTODOS DE REPORTES ============

    def generar_reporte_gastos(
        self, fecha_inicio: str, fecha_fin: str, categorias: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Genera un reporte detallado de gastos

        Args:
            fecha_inicio: Fecha de inicio del reporte
            fecha_fin: Fecha de fin del reporte
            categorias: Lista de categorías a incluir (opcional)

        Returns:
            Dict[str, Any]: Reporte de gastos
        """
        try:
            # Validar fechas
            if not self._is_valid_date(fecha_inicio) or not self._is_valid_date(
                fecha_fin
            ):
                return {"error": "Formato de fecha inválido"}

            params = [fecha_inicio, fecha_fin]
            where_clauses = ["fecha >= %s", "fecha <= %s"]

            if categorias:
                placeholders = ", ".join(["%s"] * len(categorias))
                where_clauses.append(f"categoria IN ({placeholders})")
                params.extend(categorias)

            where_sql = " AND ".join(where_clauses)

            # Obtener gastos detallados
            query_detalle = f"""
            SELECT g.*,
                   u.nombre_completo as registrado_por_nombre
            FROM {self.table_name} g
            LEFT JOIN usuarios u ON g.registrado_por = u.id
            WHERE {where_sql}
            ORDER BY g.fecha DESC, g.id DESC
            """

            gastos = self.fetch_all(query_detalle, tuple(params))

            # Obtener resumen por categoría
            query_resumen = f"""
            SELECT categoria, 
                   COUNT(*) as cantidad, 
                   SUM(monto) as total
            FROM {self.table_name}
            WHERE {where_sql}
            GROUP BY categoria
            ORDER BY total DESC
            """

            resumen = self.fetch_all(query_resumen, tuple(params))

            # Calcular totales
            total_general = Decimal("0.00")
            for item in resumen:
                total_general += Decimal(str(item["total"]))

            return {
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "total_gastos": len(gastos) if gastos else 0,
                "monto_total": total_general,
                "detalle_gastos": gastos if gastos else [],
                "resumen_categorias": resumen if resumen else [],
                "generado_en": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

        except Exception as e:
            logger.error(f"Error generando reporte de gastos: {e}")
            return {"error": str(e)}

    # ============ MÉTODOS ESTÁTICOS/DE CLASE ============

    @classmethod
    def obtener_categorias(cls) -> List[str]:
        """
        Obtiene la lista de categorías disponibles

        Returns:
            List[str]: Lista de categorías
        """
        # Esta sería la instancia con las categorías predefinidas
        instance = cls()
        return instance.CATEGORIAS.copy()

    @classmethod
    def obtener_subcategorias(cls, categoria: str) -> List[str]:
        """
        Obtiene las subcategorías para una categoría específica

        Args:
            categoria: Categoría para la cual obtener subcategorías

        Returns:
            List[str]: Lista de subcategorías o lista vacía si no hay
        """
        instance = cls()
        return instance.SUBCATEGORIAS.get(categoria, []).copy()

    @classmethod
    def obtener_formas_pago(cls) -> List[str]:
        """
        Obtiene la lista de formas de pago disponibles

        Returns:
            List[str]: Lista de formas de pago
        """
        instance = cls()
        return instance.FORMAS_PAGO.copy()


# Ejemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)

    # Crear instancia del modelo
    gasto_model = GastoModel()

    # Datos de ejemplo para crear un gasto
    datos_gasto = {
        "fecha": "2024-12-26",
        "monto": 1500.75,
        "categoria": "MATERIALES",
        "subcategoria": "OFICINA",
        "descripcion": "Compra de material de oficina para el nuevo semestre",
        "proveedor": "Papelería Central",
        "nro_factura": "FAC-2024-001234",
        "forma_pago": "TRANSFERENCIA",
        "registrado_por": 1,  # ID de usuario
    }

    # Crear gasto
    print("=== Creando nuevo gasto ===")
    gasto_id = gasto_model.create(datos_gasto, usuario_id=1)

    if gasto_id:
        print(f"✓ Gasto creado con ID: {gasto_id}")

        # Leer gasto creado
        print("\n=== Leyendo gasto creado ===")
        gasto = gasto_model.read(gasto_id)
        if gasto:
            print(f"Gasto ID {gasto['id']}: {gasto['categoria']} - ${gasto['monto']}")

        # Buscar gastos por fecha
        print("\n=== Buscando gastos por fecha ===")
        gastos_hoy = gasto_model.buscar_por_fecha("2024-12-26")
        print(f"Gastos encontrados: {len(gastos_hoy)}")

        # Obtener total por categoría
        print("\n=== Total por categoría ===")
        total_categorias = gasto_model.obtener_total_por_categoria()
        for categoria, total in total_categorias.items():
            print(f"{categoria}: ${total}")

    print("\n=== Fin del ejemplo ===")
