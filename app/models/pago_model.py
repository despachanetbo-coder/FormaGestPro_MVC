# app/models/pago_model.py
"""
Modelo de Pago usando SQLite3 directamente.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from .movimiento_caja_model import MovimientoCajaModel
from .base_model import BaseModel

logger = logging.getLogger(__name__)

class PagoModel(BaseModel):
    """Modelo que representa un pago realizado
        Atributos principales:
            id: Identificador único del pago
            matricula_id: ID de la matrícula asociada
            monto: Monto del pago
            tipo_pago: Tipo de pago (MATRICULA, CUOTA, CONTADO, OTRO)
            estado: Estado del pago (PENDIENTE, PAGADO, ANULADO, VENCIDO)
            fecha_pago: Fecha en que se realizó el pago
            fecha_vencimiento: Fecha límite para pagar
            forma_pago: Forma de pago utilizada
            concepto: Descripción del pago
    """

    TABLE_NAME = "pagos"

    # Constantes del modelo
    TIPOS_PAGO = ['MATRICULA', 'CUOTA', 'CONTADO', 'OTRO']
    ESTADOS = ['PENDIENTE', 'PAGADO', 'ANULADO', 'VENCIDO']
    FORMAS_PAGO = ['EFECTIVO', 'TRANSFERENCIA', 'TARJETA', 'DEPOSITO', 'CHEQUE']

    # Campos requeridos para crear un pago
    CAMPOS_REQUERIDOS = ['matricula_id', 'monto', 'tipo_pago']

    def __init__(self, **kwargs):
        """
        Inicializa una instancia de PagoModel.
        """
        # Campos de identificación
        if 'id' in kwargs:
            self.id = kwargs['id']

        # Campos obligatorios (con valores por defecto)
        self.matricula_id = kwargs.get('matricula_id', 0)
        self.monto = float(kwargs.get('monto', 0.0))

        # Campos con valores por defecto inteligentes
        # Determinar tipo_pago basado en el concepto
        concepto = kwargs.get('concepto', '').lower()
        if 'matricula' in concepto or 'matrícula' in concepto:
            self.tipo_pago = 'MATRICULA'
        elif 'cuota' in concepto:
            self.tipo_pago = 'CUOTA'
        else:
            self.tipo_pago = kwargs.get('tipo_pago', 'OTRO')

        self.concepto = kwargs.get('concepto', '')

        # Normalizar estado (CONFIRMADO -> PAGADO)
        estado_original = kwargs.get('estado', 'PENDIENTE')
        if estado_original == 'CONFIRMADO':
            self.estado = 'PAGADO'
        elif estado_original == 'REGISTRADO':
            self.estado = 'PENDIENTE'
        else:
            self.estado = estado_original

        self.forma_pago = kwargs.get('forma_pago', 'EFECTIVO')

        # Campos de fechas
        self.fecha_pago = kwargs.get('fecha_pago')
        self.fecha_vencimiento = kwargs.get('fecha_vencimiento')

        # Usar created_at como fecha_registro si está disponible
        if 'created_at' in kwargs and not self.fecha_pago:
            self.fecha_pago = kwargs['created_at'].split('T')[0]  # Solo la fecha

        self.fecha_registro = kwargs.get('fecha_registro', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        # Campos administrativos
        self.nro_comprobante = kwargs.get('nro_comprobante')
        self.nro_transaccion = kwargs.get('nro_transaccion')
        self.observaciones = kwargs.get('observaciones')
        self.registrado_por = kwargs.get('registrado_por')
        self.created_at = kwargs.get('created_at', datetime.now().isoformat())

        # Campos específicos de cuotas
        self.nro_cuota = kwargs.get('nro_cuota')

        # Validar datos (versión más flexible)
        self._validar_flexible()

    def _validar(self):
        """
        Valida los datos del pago antes de guardar.

        Raises:
            ValueError: Si algún campo no cumple con las validaciones
        """
        # Validar campos obligatorios
        if not self.matricula_id:
            raise ValueError("matricula_id es obligatorio")

        if self.monto <= 0:
            raise ValueError(f"El monto debe ser mayor a 0. Recibido: {self.monto}")

        if not self.tipo_pago:
            raise ValueError("tipo_pago es obligatorio")

        # Validar valores contra listas permitidas
        if self.tipo_pago not in self.TIPOS_PAGO:
            raise ValueError(f"Tipo de pago inválido: {self.tipo_pago}. Válidos: {self.TIPOS_PAGO}")

        if self.estado not in self.ESTADOS:
            raise ValueError(f"Estado inválido: {self.estado}. Válidos: {self.ESTADOS}")

        if self.forma_pago not in self.FORMAS_PAGO:
            raise ValueError(f"Forma de pago inválida: {self.forma_pago}. Válidos: {self.FORMAS_PAGO}")

        # Validar número de cuota si aplica
        if self.nro_cuota is not None and self.nro_cuota <= 0:
            raise ValueError("El número de cuota debe ser mayor a 0")
        
    def _validar_flexible(self):
        """
        Validación flexible que acepta datos históricos.
        """
        try:
            if self.monto <= 0:
                logger.warning(f"⚠️ Pago #{getattr(self, 'id', 'Nuevo')} tiene monto {self.monto}")

            # Aceptar cualquier estado pero normalizar
            estados_permitidos = ['PENDIENTE', 'PAGADO', 'ANULADO', 'VENCIDO', 'CONFIRMADO', 'REGISTRADO']
            if self.estado not in estados_permitidos:
                logger.warning(f"⚠️ Estado no estándar en pago #{getattr(self, 'id', 'Nuevo')}: {self.estado}")

            # Tipos de pago personalizados si no está en la lista estándar
            if self.tipo_pago not in self.TIPOS_PAGO:
                logger.debug(f"ℹ️ Tipo de pago personalizado: {self.tipo_pago}")

            # Formas de pago personalizadas
            if self.forma_pago and self.forma_pago not in self.FORMAS_PAGO:
                logger.debug(f"ℹ️ Forma de pago personalizada: {self.forma_pago}")

        except Exception as e:
            logger.error(f"❌ Error en validación flexible: {e}")

    def __repr__(self):
        """Representación en string del pago."""
        return f"<Pago #{self.id}: ${self.monto:.2f} - {self.estado} - Matrícula {self.matricula_id}>"

    # ============================================================================
    # MÉTODOS CRUD PRINCIPALES (HEREDADOS DE BASEMODEL)
    # ============================================================================

    def save(self):
        """
        Guarda el pago en la base de datos.

        Si el pago está en estado PAGADO, registra automáticamente
        un movimiento de caja asociado.

        Returns:
            int: ID del pago guardado

        Raises:
            Exception: Si ocurre un error al guardar
        """
        try:
            # Guardar pago en la base de datos
            pago_id = super().save()

            # Registrar movimiento de caja si el pago está PAGADO
            if self.estado == 'PAGADO':
                self._registrar_movimiento_caja()

            logger.info(f"✅ Pago guardado: ID {pago_id}, Monto ${self.monto:.2f}")
            return pago_id

        except Exception as e:
            logger.error(f"❌ Error al guardar pago: {e}")
            raise

    def delete(self):
        """
        Elimina el pago de la base de datos.

        También elimina cualquier movimiento de caja asociado.

        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            # Eliminar movimiento de caja asociado si existe
            if hasattr(self, 'id'):
                MovimientoCajaModel.eliminar_por_pago(self.id)

            # Eliminar pago
            resultado = super().delete()

            if resultado:
                logger.info(f"🗑️ Pago eliminado: ID {self.id}")

            return resultado

        except Exception as e:
            logger.error(f"❌ Error al eliminar pago ID {self.id}: {e}")
            return False

    # ============================================================================
    # MÉTODOS DE ESTADO Y TRANSICIONES
    # ============================================================================

    def marcar_como_pagado(self, forma_pago: str = None, fecha_pago: str = None,
                          nro_comprobante: str = None, registrado_por: str = None):
        """
        Marca el pago como PAGADO.

        Args:
            forma_pago (str, optional): Forma de pago utilizada
            fecha_pago (str, optional): Fecha del pago (YYYY-MM-DD)
            nro_comprobante (str, optional): Número de comprobante
            registrado_por (str, optional): Usuario que registró el pago
        """
        try:
            # Actualizar campos
            self.estado = 'PAGADO'
            self.fecha_pago = fecha_pago or datetime.now().strftime('%Y-%m-%d')

            if forma_pago:
                self.forma_pago = forma_pago

            if nro_comprobante:
                self.nro_comprobante = nro_comprobante

            if registrado_por:
                self.registrado_por = registrado_por

            # Guardar cambios
            self.save()

            logger.info(f"💰 Pago #{self.id} marcado como PAGADO")

        except Exception as e:
            logger.error(f"❌ Error al marcar pago como pagado: {e}")
            raise

    def marcar_como_anulado(self, motivo: str = None):
        """
        Marca el pago como ANULADO.

        Args:
            motivo (str, optional): Motivo de la anulación
        """
        try:
            # Actualizar estado
            self.estado = 'ANULADO'

            if motivo:
                self.observaciones = f"ANULADO: {motivo}" + (
                    f" | {self.observaciones}" if self.observaciones else ""
                )

            # Guardar cambios
            self.save()

            # Eliminar movimiento de caja asociado
            if hasattr(self, 'id'):
                MovimientoCajaModel.eliminar_por_pago(self.id)

            logger.info(f"❌ Pago #{self.id} marcado como ANULADO")

        except Exception as e:
            logger.error(f"❌ Error al anular pago: {e}")
            raise

    def verificar_vencimiento(self):
        """
        Verifica si el pago está vencido.

        Returns:
            bool: True si está vencido, False en caso contrario
        """
        if not self.fecha_vencimiento or self.estado == 'PAGADO':
            return False

        try:
            fecha_vencimiento = datetime.strptime(self.fecha_vencimiento, '%Y-%m-%d')
            fecha_actual = datetime.now()

            if fecha_actual > fecha_vencimiento:
                self.estado = 'VENCIDO'
                self.save()
                return True

            return False

        except Exception as e:
            logger.error(f"❌ Error al verificar vencimiento: {e}")
            return False

    # ============================================================================
    # MÉTODOS DE MOVIMIENTO DE CAJA
    # ============================================================================

    def _registrar_movimiento_caja(self):
        """
        Registra automáticamente un movimiento de caja para el pago.

        Este método se llama automáticamente cuando un pago se marca como PAGADO.
        """
        try:
            if not hasattr(self, 'id'):
                raise ValueError("El pago debe tener un ID para registrar movimiento de caja")

            # Verificar si ya existe un movimiento para este pago
            if MovimientoCajaModel.existe_movimiento_para_pago(self.id):
                logger.warning(f"⚠️ Ya existe movimiento de caja para el pago #{self.id}")
                return

            # Registrar movimiento de caja
            MovimientoCajaModel.registrar_ingreso_pago(
                pago_id=self.id,
                monto=self.monto,
                matricula_id=self.matricula_id,
                nro_cuota=getattr(self, 'nro_cuota', None),
                concepto=self.concepto,
                forma_pago=self.forma_pago
            )

            logger.info(f"💰 Movimiento de caja registrado para pago #{self.id}")

        except Exception as e:
            logger.error(f"❌ Error al registrar movimiento de caja: {e}")
            raise

    # ============================================================================
    # MÉTODOS ESTÁTICOS (BÚSQUEDA Y CONSULTAS)
    # ============================================================================

    @classmethod
    def buscar_por_matricula(cls, matricula_id: int, estado: str = None) -> List['PagoModel']:
        """
        Busca pagos por ID de matrícula.

        Args:
            matricula_id (int): ID de la matrícula
            estado (str, optional): Filtrar por estado específico

        Returns:
            List[PagoModel]: Lista de pagos encontrados
        """
        from database.database import db

        try:
            query = f"SELECT * FROM {cls.TABLE_NAME} WHERE matricula_id = ?"
            params = [matricula_id]

            if estado:
                query += " AND estado = ?"
                params.append(estado)

            query += " ORDER BY fecha_vencimiento, created_at"

            rows = db.fetch_all(query, tuple(params))
            return [cls(**row) for row in rows]

        except Exception as e:
            logger.error(f"❌ Error al buscar pagos por matrícula: {e}")
            return []

    @classmethod
    def buscar_por_estado(cls, estado: str) -> List['PagoModel']:
        """
        Busca pagos por estado.

        Args:
            estado (str): Estado a buscar

        Returns:
            List[PagoModel]: Lista de pagos encontrados
        """
        from database.database import db

        try:
            query = f"SELECT * FROM {cls.TABLE_NAME} WHERE estado = ? ORDER BY fecha_vencimiento"
            rows = db.fetch_all(query, (estado,))
            return [cls(**row) for row in rows]

        except Exception as e:
            logger.error(f"❌ Error al buscar pagos por estado: {e}")
            return []

    @classmethod
    def buscar_por_rango_fechas(cls, fecha_inicio: str, fecha_fin: str, 
                               estado: str = None) -> List['PagoModel']:
        """
        Busca pagos dentro de un rango de fechas.

        Args:
            fecha_inicio (str): Fecha inicio (YYYY-MM-DD)
            fecha_fin (str): Fecha fin (YYYY-MM-DD)
            estado (str, optional): Filtrar por estado

        Returns:
            List[PagoModel]: Lista de pagos encontrados
        """
        from database.database import db

        try:
            query = f"""
                SELECT * FROM {cls.TABLE_NAME} 
                WHERE fecha_pago BETWEEN ? AND ?
            """
            params = [fecha_inicio, fecha_fin]

            if estado:
                query += " AND estado = ?"
                params.append(estado)

            query += " ORDER BY fecha_pago, id"

            rows = db.fetch_all(query, tuple(params))
            return [cls(**row) for row in rows]

        except Exception as e:
            logger.error(f"❌ Error al buscar pagos por rango de fechas: {e}")
            return []

    @classmethod
    def get_all(cls, limit: int = 100, offset: int = 0) -> List['PagoModel']:
        """
        Obtiene todos los pagos usando método de compatibilidad.
        """
        try:
            # Usar método de compatibilidad para estructura actual
            pagos = cls.get_all_compatibilidad()

            # Aplicar límite y offset
            if limit > 0:
                start = offset
                end = offset + limit
                return pagos[start:end]

            return pagos

        except Exception as e:
            logger.error(f"❌ Error en get_all: {e}")
            return []

    @classmethod
    def get_total_pagos_por_estado(cls) -> Dict[str, int]:
        """
        Obtiene el total de pagos agrupados por estado.

        Returns:
            Dict[str, int]: Diccionario con estado como clave y cantidad como valor
        """
        from database.database import db

        try:
            query = f"""
                SELECT estado, COUNT(*) as cantidad 
                FROM {cls.TABLE_NAME} 
                GROUP BY estado
            """
            rows = db.fetch_all(query)

            resultado = {}
            for estado in cls.ESTADOS:
                resultado[estado] = 0

            for row in rows:
                resultado[row['estado']] = row['cantidad']

            return resultado

        except Exception as e:
            logger.error(f"❌ Error al obtener total de pagos por estado: {e}")
            return {}

    @classmethod
    def get_ingresos_totales(cls, fecha_inicio: str = None, fecha_fin: str = None) -> float:
        """
        Calcula los ingresos totales de pagos PAGADOS.

        Args:
            fecha_inicio (str, optional): Fecha inicio (YYYY-MM-DD)
            fecha_fin (str, optional): Fecha fin (YYYY-MM-DD)

        Returns:
            float: Total de ingresos
        """
        from database.database import db

        try:
            query = f"""
                SELECT SUM(monto) as total 
                FROM {cls.TABLE_NAME} 
                WHERE estado = 'PAGADO'
            """
            params = []

            if fecha_inicio and fecha_fin:
                query += " AND fecha_pago BETWEEN ? AND ?"
                params.extend([fecha_inicio, fecha_fin])

            result = db.fetch_one(query, tuple(params))
            return float(result['total'] or 0)

        except Exception as e:
            logger.error(f"❌ Error al calcular ingresos totales: {e}")
            return 0.0

    # ============================================================================
    # MÉTODOS DE CREACIÓN ESPECÍFICOS
    # ============================================================================

    @classmethod
    def crear_pago_matricula(cls, matricula_id: int, monto: float, 
                           concepto: str = None, **kwargs) -> 'PagoModel':
        """
        Crea un pago de matrícula.

        Args:
            matricula_id (int): ID de la matrícula
            monto (float): Monto de la matrícula
            concepto (str, optional): Concepto del pago
            **kwargs: Campos adicionales del pago

        Returns:
            PagoModel: Pago creado
        """
        pago_data = {
            'matricula_id': matricula_id,
            'monto': monto,
            'tipo_pago': 'MATRICULA',
            'concepto': concepto or "Pago de Matrícula",
            'estado': 'PENDIENTE',
            **kwargs
        }

        return cls(**pago_data)

    @classmethod
    def crear_pago_cuota(cls, matricula_id: int, monto: float, nro_cuota: int,
                        fecha_vencimiento: str, **kwargs) -> 'PagoModel':
        """
        Crea un pago de cuota.

        Args:
            matricula_id (int): ID de la matrícula
            monto (float): Monto de la cuota
            nro_cuota (int): Número de cuota
            fecha_vencimiento (str): Fecha de vencimiento (YYYY-MM-DD)
            **kwargs: Campos adicionales

        Returns:
            PagoModel: Pago creado
        """
        pago_data = {
            'matricula_id': matricula_id,
            'monto': monto,
            'tipo_pago': 'CUOTA',
            'nro_cuota': nro_cuota,
            'fecha_vencimiento': fecha_vencimiento,
            'concepto': f"Cuota {nro_cuota}",
            'estado': 'PENDIENTE',
            **kwargs
        }

        return cls(**pago_data)

    @classmethod
    def crear_pago_contado(cls, matricula_id: int, monto: float, 
                          concepto: str, **kwargs) -> 'PagoModel':
        """
        Crea un pago al contado.

        Args:
            matricula_id (int): ID de la matrícula
            monto (float): Monto del pago
            concepto (str): Concepto del pago
            **kwargs: Campos adicionales

        Returns:
            PagoModel: Pago creado
        """
        pago_data = {
            'matricula_id': matricula_id,
            'monto': monto,
            'tipo_pago': 'CONTADO',
            'concepto': concepto,
            'estado': 'PENDIENTE',
            **kwargs
        }

        return cls(**pago_data)

    @classmethod
    def generar_plan_cuotas(cls, matricula_id: int, monto_total: float, 
                          num_cuotas: int, fecha_inicio: str, 
                          intervalo_dias: int = 30) -> List['PagoModel']:
        """
        Genera un plan de cuotas para una matrícula.

        Args:
            matricula_id (int): ID de la matrícula
            monto_total (float): Monto total a dividir en cuotas
            num_cuotas (int): Número de cuotas
            fecha_inicio (str): Fecha inicio (YYYY-MM-DD)
            intervalo_dias (int): Días entre cuotas

        Returns:
            List[PagoModel]: Lista de cuotas generadas
        """
        try:
            cuotas = []
            fecha_actual = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            monto_cuota = round(monto_total / num_cuotas, 2)

            # Ajustar la última cuota para compensar redondeos
            monto_total_ajustado = 0.0

            for i in range(num_cuotas):
                fecha_vencimiento = fecha_actual + timedelta(days=intervalo_dias * i)

                # Para la última cuota, ajustar monto
                if i == num_cuotas - 1:
                    monto_ultima = round(monto_total - monto_total_ajustado, 2)
                    monto_cuota_actual = monto_ultima
                else:
                    monto_cuota_actual = monto_cuota
                    monto_total_ajustado += monto_cuota

                # Crear cuota
                cuota = cls.crear_pago_cuota(
                    matricula_id=matricula_id,
                    monto=monto_cuota_actual,
                    nro_cuota=i + 1,
                    fecha_vencimiento=fecha_vencimiento.strftime('%Y-%m-%d'),
                    concepto=f"Cuota {i + 1}/{num_cuotas} - Plan de Pagos"
                )

                # Guardar cuota
                cuota.save()
                cuotas.append(cuota)

                logger.info(f"  📝 Cuota {i + 1}: ${monto_cuota_actual:.2f} - Vence: {fecha_vencimiento.strftime('%d/%m/%Y')}")

            logger.info(f"✅ Plan de {len(cuotas)} cuotas generado para matrícula #{matricula_id}")
            return cuotas

        except Exception as e:
            logger.error(f"❌ Error al generar plan de cuotas: {e}")
            raise

    # ============================================================================
    # MÉTODOS DE FACTORY (CREACIÓN RÁPIDA)
    # ============================================================================

    @classmethod
    def create(cls, **kwargs) -> 'PagoModel':
        """
        Factory method para crear un pago rápidamente.

        Args:
            **kwargs: Campos del pago

        Returns:
            PagoModel: Pago creado
        """
        pago = cls(**kwargs)
        pago.save()
        return pago

    @classmethod
    def create_from_dict(cls, data: Dict[str, Any]) -> 'PagoModel':
        """
        Crea un pago a partir de un diccionario.

        Args:
            data (Dict[str, Any]): Datos del pago

        Returns:
            PagoModel: Pago creado
        """
        return cls.create(**data)

    # ============================================================================
    # MÉTODOS DE UTILIDAD
    # ============================================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el pago a un diccionario.

        Returns:
            Dict[str, Any]: Diccionario con los datos del pago
        """
        return {
            'id': getattr(self, 'id', None),
            'matricula_id': self.matricula_id,
            'monto': self.monto,
            'tipo_pago': self.tipo_pago,
            'concepto': self.concepto,
            'estado': self.estado,
            'forma_pago': self.forma_pago,
            'fecha_pago': self.fecha_pago,
            'fecha_vencimiento': self.fecha_vencimiento,
            'fecha_registro': self.fecha_registro,
            'nro_comprobante': self.nro_comprobante,
            'nro_transaccion': self.nro_transaccion,
            'observaciones': self.observaciones,
            'registrado_por': self.registrado_por,
            'nro_cuota': getattr(self, 'nro_cuota', None),
            'created_at': getattr(self, 'created_at', None)
        }

    @classmethod
    def get_estados_disponibles(cls) -> List[str]:
        """
        Obtiene la lista de estados disponibles.

        Returns:
            List[str]: Lista de estados
        """
        return cls.ESTADOS.copy()

    @classmethod
    def get_formas_pago_disponibles(cls) -> List[str]:
        """
        Obtiene la lista de formas de pago disponibles.

        Returns:
            List[str]: Lista de formas de pago
        """
        return cls.FORMAS_PAGO.copy()

    @classmethod
    def get_tipos_pago_disponibles(cls) -> List[str]:
        """
        Obtiene la lista de tipos de pago disponibles.

        Returns:
            List[str]: Lista de tipos de pago
        """
        return cls.TIPOS_PAGO.copy()

    # ============================================================================
    # MÉTODOS PARA LA INTERFAZ GRÁFICA
    # ============================================================================

    @classmethod
    def obtener_para_tabla_financiera(cls, filtros: Dict[str, Any] = None) -> List['PagoModel']:
        """
        Obtiene pagos formateados para la tabla financiera.

        Args:
            filtros (Dict[str, Any], optional): Diccionario con filtros:
                - estado (str): Filtrar por estado
                - fecha_desde (str): Fecha desde
                - fecha_hasta (str): Fecha hasta
                - matricula_id (int): ID de matrícula
                - tipo_pago (str): Tipo de pago

        Returns:
            List[PagoModel]: Lista de pagos formateados
        """
        from database.database import db

        try:
            query = f"""
                SELECT p.*, e.nombre as estudiante_nombre, pr.nombre as programa_nombre
                FROM {cls.TABLE_NAME} p
                LEFT JOIN matricula m ON p.matricula_id = m.id
                LEFT JOIN estudiantes e ON m.estudiante_id = e.id
                LEFT JOIN programas pr ON m.programa_id = pr.id
                WHERE 1=1
            """
            params = []

            # Aplicar filtros
            if filtros:
                if filtros.get('estado'):
                    query += " AND p.estado = ?"
                    params.append(filtros['estado'])

                if filtros.get('fecha_desde') and filtros.get('fecha_hasta'):
                    query += " AND p.fecha_pago BETWEEN ? AND ?"
                    params.extend([filtros['fecha_desde'], filtros['fecha_hasta']])

                if filtros.get('matricula_id'):
                    query += " AND p.matricula_id = ?"
                    params.append(filtros['matricula_id'])

                if filtros.get('tipo_pago'):
                    query += " AND p.tipo_pago = ?"
                    params.append(filtros['tipo_pago'])

            query += " ORDER BY p.fecha_pago DESC, p.id DESC"

            rows = db.fetch_all(query, tuple(params))
            return [cls(**row) for row in rows]

        except Exception as e:
            logger.error(f"❌ Error al obtener pagos para tabla financiera: {e}")
            return []

    @classmethod
    def obtener_resumen_financiero(cls) -> Dict[str, Any]:
        """
        Obtiene un resumen financiero para el dashboard.

        Returns:
            Dict[str, Any]: Diccionario con:
                - total_ingresos_mes (float)
                - pagos_pendientes (int)
                - pagos_completados (int)
                - estudiantes_con_deuda (int)
        """
        from database.database import db

        try:
            resumen = {}

            # Total ingresos del mes actual
            mes_actual = datetime.now().strftime('%Y-%m')
            query_ingresos = f"""
                SELECT SUM(monto) as total 
                FROM {cls.TABLE_NAME} 
                WHERE estado = 'PAGADO' 
                AND strftime('%Y-%m', fecha_pago) = ?
            """
            result = db.fetch_one(query_ingresos, (mes_actual,))
            resumen['total_ingresos_mes'] = float(result['total'] or 0)

            # Pagos pendientes
            query_pendientes = f"""
                SELECT COUNT(*) as total 
                FROM {cls.TABLE_NAME} 
                WHERE estado = 'PENDIENTE'
            """
            result = db.fetch_one(query_pendientes)
            resumen['pagos_pendientes'] = result['total'] or 0

            # Pagos completados
            query_completados = f"""
                SELECT COUNT(*) as total 
                FROM {cls.TABLE_NAME} 
                WHERE estado = 'PAGADO'
            """
            result = db.fetch_one(query_completados)
            resumen['pagos_completados'] = result['total'] or 0

            # Estudiantes con deuda (matrículas con pagos pendientes)
            query_deuda = """
                SELECT COUNT(DISTINCT matricula_id) as total
                FROM pagos 
                WHERE estado = 'PENDIENTE'
            """
            result = db.fetch_one(query_deuda)
            resumen['estudiantes_con_deuda'] = result['total'] or 0

            return resumen

        except Exception as e:
            logger.error(f"❌ Error al obtener resumen financiero: {e}")
            return {
                'total_ingresos_mes': 0.0,
                'pagos_pendientes': 0,
                'pagos_completados': 0,
                'estudiantes_con_deuda': 0
            }
        
    @classmethod
    def get_all_compatibilidad(cls) -> List['PagoModel']:
        """
        Método de compatibilidad que lee la estructura actual de la base de datos.
        """
        from database.database import db

        try:
            # Primero, verificar la estructura de la tabla
            query_estructura = "PRAGMA table_info(pagos)"
            columnas = db.fetch_all(query_estructura)
            nombres_columnas = [col['name'] for col in columnas]

            logger.info(f"📋 Estructura de tabla pagos: {nombres_columnas}")

            # Construir query dinámica basada en columnas disponibles
            columnas_select = []
            for col in nombres_columnas:
                if col == 'nro_cuota':
                    columnas_select.append(f'CAST({col} AS INTEGER) as nro_cuota')
                else:
                    columnas_select.append(col)

            select_clause = ', '.join(columnas_select)
            query = f"SELECT {select_clause} FROM pagos ORDER BY id DESC"

            rows = db.fetch_all(query)

            # Mapear filas a objetos PagoModel
            pagos = []
            for row in rows:
                try:
                    # Crear diccionario con mapeo inteligente
                    datos_pago = {}

                    # Mapear columnas conocidas
                    for key, value in row.items():
                        if value is not None:
                            datos_pago[key] = value

                    # Agregar campos calculados
                    if 'concepto' not in datos_pago or not datos_pago['concepto']:
                        datos_pago['concepto'] = 'Pago registrado'

                    # Determinar tipo de pago basado en concepto
                    concepto = datos_pago.get('concepto', '').lower()
                    if 'contado' in concepto:
                        datos_pago['tipo_pago'] = 'CONTADO'
                    elif 'cuota' in concepto:
                        datos_pago['tipo_pago'] = 'CUOTA'
                    elif 'matricula' in concepto or 'matrícula' in concepto:
                        datos_pago['tipo_pago'] = 'MATRICULA'
                    else:
                        datos_pago['tipo_pago'] = 'OTRO'

                    # Normalizar estado
                    estado = datos_pago.get('estado', 'PENDIENTE')
                    if estado == 'CONFIRMADO':
                        datos_pago['estado'] = 'PAGADO'
                    elif estado == 'REGISTRADO':
                        datos_pago['estado'] = 'PENDIENTE'

                    # Agregar codigo_pago si no existe
                    if 'nro_comprobante' in datos_pago and datos_pago['nro_comprobante']:
                        datos_pago['codigo_pago'] = datos_pago['nro_comprobante']
                    else:
                        datos_pago['codigo_pago'] = f"PAGO-{datos_pago.get('id', '')}"

                    # Crear instancia
                    pago = cls(**datos_pago)

                    # Agregar campos adicionales para la vista
                    pago.codigo_pago = datos_pago.get('codigo_pago')
                    pago.metodo_pago = datos_pago.get('forma_pago', 'EFECTIVO')

                    # Intentar obtener información del estudiante
                    try:
                        from .matricula_model import MatriculaModel
                        matricula = MatriculaModel.get_by_id(pago.matricula_id)
                        if matricula:
                            from .estudiante_model import EstudianteModel
                            estudiante = EstudianteModel.get_by_id(matricula.estudiante_id)
                            if estudiante:
                                pago.estudiante_nombre = estudiante.nombre_completo
                            else:
                                pago.estudiante_nombre = f"Estudiante {pago.matricula_id}"
                        else:
                            pago.estudiante_nombre = f"Matrícula {pago.matricula_id}"
                    except:
                        pago.estudiante_nombre = "Información no disponible"

                    pagos.append(pago)

                except Exception as e:
                    logger.error(f"❌ Error procesando pago: {e}. Datos: {row}")
                    continue
                
            logger.info(f"✅ {len(pagos)} pagos cargados desde estructura actual")
            return pagos

        except Exception as e:
            logger.error(f"❌ Error en get_all_compatibilidad: {e}")
            return []
        
    def cargar_pagos(self, filtro='todos'):
        """Cargar pagos desde la base de datos"""
        try:
            self.lbl_estado.setText("Cargando pagos...")
            
            # Obtener pagos con método de compatibilidad
            self.pagos_data = PagoModel.get_all_compatibilidad()
            
            # Depuración: mostrar información de los pagos cargados
            if self.pagos_data:
                logger.info(f"📊 {len(self.pagos_data)} pagos cargados:")
                for pago in self.pagos_data[:3]:  # Mostrar primeros 3
                    logger.info(f"  - Pago #{pago.id}: ${pago.monto} - {pago.estado} - {pago.concepto}")
                
                self.lbl_estado.setText(f"✅ {len(self.pagos_data)} pagos cargados")
            else:
                logger.warning("⚠️ No se encontraron pagos en la base de datos")
                self.lbl_estado.setText("📭 No hay pagos registrados")
            
            # Resetear paginación
            self.current_page = 1
            
            # Aplicar filtro inicial
            self.current_filter = filtro
            self.filtrar_pagos(desde_paginacion=False)
            
            # Actualizar resumen
            self.actualizar_resumen()
                
        except Exception as e:
            logger.error(f"Error al cargar pagos: {e}")
            self.lbl_estado.setText("❌ Error al cargar pagos")
            import traceback
            traceback.print_exc()