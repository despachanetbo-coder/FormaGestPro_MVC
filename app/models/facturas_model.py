# app/models/facturas_model.py
"""
Modelo para la tabla de facturas en FormaGestPro_MVC
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple, Union
import re
import logging

from .base_model import BaseModel
logger = logging.getLogger(__name__)

class FacturaModel(BaseModel):
    """Modelo para facturas del sistema (solo registro)"""
    TABLE_NAME = "facturas"

    # Tipos de documento válidos
    TIPO_NIT = 'NIT'
    TIPO_CI = 'CI'
    TIPO_CONSUMIDOR_FINAL = 'CONSUMIDOR_FINAL'

    TIPOS_DOCUMENTO = [TIPO_NIT, TIPO_CI, TIPO_CONSUMIDOR_FINAL]

    # Estados de factura
    ESTADO_EMITIDA = 'EMITIDA'
    ESTADO_ANULADA = 'ANULADA'
    ESTADO_PENDIENTE = 'PENDIENTE'
    ESTADO_PAGADA = 'PAGADA'

    ESTADOS = [ESTADO_EMITIDA, ESTADO_ANULADA, ESTADO_PENDIENTE, ESTADO_PAGADA]

    # Códigos de leyenda SIAT (opcional)
    CODIGOS_LEYENDA = {
        'L1': 'Ley N° 453: Tienes derecho a recibir información sobre las características y contenidos de los servicios que utilices',
        'L2': 'Ley N° 453: Puedes acceder a los libros de reclamaciones en forma gratuita en los locales de atención al público',
        'L3': 'Código de Consumidor: El proveedor debe garantizar el derecho a la seguridad e indemnidad',
        'L4': 'Código de Consumidor: El proveedor debe ofrecer servicios de calidad'
    }

    def __init__(self, **kwargs):
        super().__init__()
        self.id = kwargs.get('id')
        self.nro_factura = kwargs.get('nro_factura', '')
        self.fecha_emision = kwargs.get('fecha_emision')
        self.tipo_documento = kwargs.get('tipo_documento', self.TIPO_CONSUMIDOR_FINAL)
        self.nit_ci = kwargs.get('nit_ci')
        self.razon_social = kwargs.get('razon_social', '')
        self.subtotal = self._to_decimal(kwargs.get('subtotal', 0))
        self.iva = self._to_decimal(kwargs.get('iva', 0))
        self.it = self._to_decimal(kwargs.get('it', 0))
        self.total = self._to_decimal(kwargs.get('total', 0))
        self.concepto = kwargs.get('concepto')
        self.estado = kwargs.get('estado', self.ESTADO_EMITIDA)
        self.exportada_siat = kwargs.get('exportada_siat', 0)
        self.created_at = kwargs.get('created_at')

        # Campos calculados
        self._tasa_iva = Decimal('0.13')  # 13% por defecto
        self._tasa_it = Decimal('0.03')   # 3% por defecto

        # Campos adicionales para detalles (no en BD)
        self.detalles = kwargs.get('detalles', [])

    def _to_decimal(self, value) -> Decimal:
        """Convertir valor a Decimal de forma segura"""
        if value is None:
            return Decimal('0')
        if isinstance(value, Decimal):
            return value
        try:
            return Decimal(str(value))
        except:
            return Decimal('0')

    @property
    def fecha_emision_formateada(self) -> str:
        """Retorna la fecha de emisión formateada"""
        if isinstance(self.fecha_emision, str):
            try:
                fecha_obj = datetime.strptime(self.fecha_emision, '%Y-%m-%d')
                return fecha_obj.strftime('%d/%m/%Y')
            except:
                return self.fecha_emision
        elif isinstance(self.fecha_emision, date):
            return self.fecha_emision.strftime('%d/%m/%Y')
        return str(self.fecha_emision)

    @property
    def created_at_formateado(self) -> str:
        """Retorna la fecha de creación formateada"""
        if isinstance(self.created_at, str):
            try:
                fecha_obj = datetime.strptime(self.created_at, '%Y-%m-%d %H:%M:%S')
                return fecha_obj.strftime('%d/%m/%Y %H:%M')
            except:
                return self.created_at
        elif isinstance(self.created_at, datetime):
            return self.created_at.strftime('%d/%m/%Y %H:%M')
        return str(self.created_at)

    @property
    def subtotal_formateado(self) -> str:
        """Retorna el subtotal formateado como moneda"""
        return f"Bs. {self.subtotal:,.2f}"

    @property
    def iva_formateado(self) -> str:
        """Retorna el IVA formateado como moneda"""
        return f"Bs. {self.iva:,.2f}"

    @property
    def it_formateado(self) -> str:
        """Retorna el IT formateado como moneda"""
        return f"Bs. {self.it:,.2f}"

    @property
    def total_formateado(self) -> str:
        """Retorna el total formateado como moneda"""
        return f"Bs. {self.total:,.2f}"

    @property
    def tipo_documento_descripcion(self) -> str:
        """Retorna descripción del tipo de documento"""
        descripciones = {
            self.TIPO_NIT: 'NIT',
            self.TIPO_CI: 'Cédula de Identidad',
            self.TIPO_CONSUMIDOR_FINAL: 'Consumidor Final'
        }
        return descripciones.get(self.tipo_documento, self.tipo_documento)

    @property
    def estado_descripcion(self) -> str:
        """Retorna descripción del estado"""
        descripciones = {
            self.ESTADO_EMITIDA: 'Emitida',
            self.ESTADO_ANULADA: 'Anulada',
            self.ESTADO_PENDIENTE: 'Pendiente',
            self.ESTADO_PAGADA: 'Pagada'
        }
        return descripciones.get(self.estado, self.estado)

    @property
    def exportada_siat_descripcion(self) -> str:
        """Retorna descripción de exportación SIAT"""
        return 'Sí' if self.exportada_siat else 'No'

    @property
    def nit_ci_formateado(self) -> str:
        """Retorna NIT/CI formateado"""
        if not self.nit_ci:
            return ''

        nit_ci = str(self.nit_ci)
        if self.tipo_documento == self.TIPO_NIT:
            # Formato: 123456789-0
            if len(nit_ci) == 10:
                return f"{nit_ci[:9]}-{nit_ci[9]}"
        elif self.tipo_documento == self.TIPO_CI:
            # Formato: 1234567-BE
            if '-' not in nit_ci and len(nit_ci) >= 7:
                return nit_ci[:7]

        return nit_ci

    @property
    def es_consumidor_final(self) -> bool:
        """Verificar si es factura a consumidor final"""
        return self.tipo_documento == self.TIPO_CONSUMIDOR_FINAL

    @property
    def tiene_documento(self) -> bool:
        """Verificar si tiene documento (NIT/CI)"""
        return self.tipo_documento in [self.TIPO_NIT, self.TIPO_CI] and bool(self.nit_ci)

    @property
    def codigo_control(self) -> str:
        """
        Generar código de control simple (para fines de demostración)
        En producción, se debe implementar el algoritmo oficial
        """
        if not self.nro_factura or not self.nit_ci or not self.fecha_emision:
            return ''

        # Código simple para demostración
        import hashlib
        cadena = f"{self.nro_factura}{self.nit_ci}{self.fecha_emision}{self.total}"
        hash_obj = hashlib.md5(cadena.encode())
        return hash_obj.hexdigest()[:8].upper()

    @classmethod
    def get_by_nro_factura(cls, nro_factura: str) -> Optional['FacturaModel']:
        """Obtener factura por número de factura"""
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE nro_factura = ?"
        results = cls.query(query, [nro_factura])
        if results:
            return cls(**results[0])
        return None

    @classmethod
    def get_by_fecha(
        cls, 
        fecha_inicio: Optional[Union[str, date]] = None,
        fecha_fin: Optional[Union[str, date]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List['FacturaModel']:
        """Obtener facturas por rango de fechas"""
        condiciones = []
        parametros = []

        if fecha_inicio:
            condiciones.append("fecha_emision >= ?")
            fecha_inicio_str = fecha_inicio if isinstance(fecha_inicio, str) else fecha_inicio.isoformat()
            parametros.append(fecha_inicio_str)

        if fecha_fin:
            condiciones.append("fecha_emision <= ?")
            fecha_fin_str = fecha_fin if isinstance(fecha_fin, str) else fecha_fin.isoformat()
            parametros.append(fecha_fin_str)

        where_clause = ""
        if condiciones:
            where_clause = "WHERE " + " AND ".join(condiciones)

        query = f"""
            SELECT * FROM {cls.TABLE_NAME} 
            {where_clause}
            ORDER BY fecha_emision DESC, nro_factura DESC
            LIMIT ? OFFSET ?
        """
        parametros.extend([limit, offset])

        results = cls.query(query, parametros)
        return [cls(**row) for row in results] if results else []

    @classmethod
    def get_by_estado(cls, estado: str, limit: int = 100) -> List['FacturaModel']:
        """Obtener facturas por estado"""
        query = f"""
            SELECT * FROM {cls.TABLE_NAME} 
            WHERE estado = ?
            ORDER BY fecha_emision DESC, nro_factura DESC
            LIMIT ?
        """
        results = cls.query(query, [estado, limit])
        return [cls(**row) for row in results] if results else []

    @classmethod
    def get_by_cliente(
        cls, 
        nit_ci: Optional[str] = None,
        razon_social: Optional[str] = None,
        limit: int = 100
    ) -> List['FacturaModel']:
        """Obtener facturas por cliente"""
        condiciones = []
        parametros = []

        if nit_ci:
            condiciones.append("nit_ci LIKE ?")
            parametros.append(f"%{nit_ci}%")

        if razon_social:
            condiciones.append("razon_social LIKE ?")
            parametros.append(f"%{razon_social}%")

        where_clause = ""
        if condiciones:
            where_clause = "WHERE " + " OR ".join(condiciones)

        query = f"""
            SELECT * FROM {cls.TABLE_NAME} 
            {where_clause}
            ORDER BY fecha_emision DESC, nro_factura DESC
            LIMIT ?
        """
        parametros.append(limit)

        results = cls.query(query, parametros)
        return [cls(**row) for row in results] if results else []

    @classmethod
    def get_by_exportacion_siat(cls, exportada: bool = True, limit: int = 100) -> List['FacturaModel']:
        """Obtener facturas por estado de exportación SIAT"""
        query = f"""
            SELECT * FROM {cls.TABLE_NAME} 
            WHERE exportada_siat = ?
            ORDER BY fecha_emision DESC, nro_factura DESC
            LIMIT ?
        """
        results = cls.query(query, [1 if exportada else 0, limit])
        return [cls(**row) for row in results] if results else []

    @classmethod
    def get_ultimo_numero(cls, prefijo: str = 'FAC-') -> str:
        """
        Obtener el último número de factura para generar el siguiente

        Args:
            prefijo: Prefijo de las facturas (ej: 'FAC-')

        Returns:
            Próximo número de factura
        """
        query = f"""
            SELECT nro_factura FROM {cls.TABLE_NAME} 
            WHERE nro_factura LIKE ?
            ORDER BY nro_factura DESC 
            LIMIT 1
        """
        results = cls.query(query, [f"{prefijo}%"])

        if not results:
            return f"{prefijo}000001"

        ultimo_numero = results[0]['nro_factura']
        try:
            # Extraer número secuencial
            numero = int(ultimo_numero.replace(prefijo, ''))
            return f"{prefijo}{numero + 1:06d}"
        except ValueError:
            # Si hay error en el formato, generar nuevo número
            import datetime
            ahora = datetime.datetime.now()
            return f"{prefijo}{ahora.strftime('%Y%m')}-0001"

    @classmethod
    def calcular_totales(
        cls, 
        subtotal: Decimal, 
        aplicar_iva: bool = True,
        aplicar_it: bool = False,
        tasa_iva: Decimal = None,
        tasa_it: Decimal = None
    ) -> Dict[str, Decimal]:
        """
        Calcular totales de factura

        Args:
            subtotal: Subtotal de la factura
            aplicar_iva: Si True, aplicar IVA (13%)
            aplicar_it: Si True, aplicar IT (3%)
            tasa_iva: Tasa de IVA personalizada
            tasa_it: Tasa de IT personalizada

        Returns:
            Diccionario con subtotal, iva, it, total
        """
        if tasa_iva is None:
            tasa_iva = Decimal('0.13')  # 13%
        if tasa_it is None:
            tasa_it = Decimal('0.03')   # 3%

        iva = subtotal * tasa_iva if aplicar_iva else Decimal('0')
        it = subtotal * tasa_it if aplicar_it else Decimal('0')
        total = subtotal + iva + it

        return {
            'subtotal': subtotal,
            'iva': iva,
            'it': it,
            'total': total
        }

    def calcular_desde_subtotal(
        self, 
        subtotal: Decimal,
        aplicar_iva: bool = True,
        aplicar_it: bool = False
    ) -> None:
        """
        Calcular y establecer totales desde subtotal

        Args:
            subtotal: Subtotal de la factura
            aplicar_iva: Si True, aplicar IVA
            aplicar_it: Si True, aplicar IT
        """
        self.subtotal = self._to_decimal(subtotal)
        self.iva = self._to_decimal(subtotal * self._tasa_iva if aplicar_iva else 0)
        self.it = self._to_decimal(subtotal * self._tasa_it if aplicar_it else 0)
        self.total = self._to_decimal(self.subtotal + self.iva + self.it)

    def calcular_desde_total(
        self, 
        total: Decimal,
        aplicar_iva: bool = True,
        aplicar_it: bool = False
    ) -> None:
        """
        Calcular y establecer totales desde total

        Args:
            total: Total de la factura
            aplicar_iva: Si True, aplicar IVA
            aplicar_it: Si True, aplicar IT
        """
        self.total = self._to_decimal(total)

        if aplicar_iva and aplicar_it:
            # Total = Subtotal + 0.13*Subtotal + 0.03*Subtotal = Subtotal * 1.16
            self.subtotal = self._to_decimal(total / Decimal('1.16'))
            self.iva = self._to_decimal(self.subtotal * self._tasa_iva)
            self.it = self._to_decimal(self.subtotal * self._tasa_it)
        elif aplicar_iva:
            # Total = Subtotal + 0.13*Subtotal = Subtotal * 1.13
            self.subtotal = self._to_decimal(total / Decimal('1.13'))
            self.iva = self._to_decimal(self.subtotal * self._tasa_iva)
            self.it = Decimal('0')
        elif aplicar_it:
            # Total = Subtotal + 0.03*Subtotal = Subtotal * 1.03
            self.subtotal = self._to_decimal(total / Decimal('1.03'))
            self.iva = Decimal('0')
            self.it = self._to_decimal(self.subtotal * self._tasa_it)
        else:
            self.subtotal = self._to_decimal(total)
            self.iva = Decimal('0')
            self.it = Decimal('0')

    def anular(self, motivo: str = None) -> Tuple[bool, str]:
        """
        Anular factura

        Args:
            motivo: Motivo de anulación (opcional)

        Returns:
            Tuple (éxito, mensaje)
        """
        if self.estado == self.ESTADO_ANULADA:
            return False, "La factura ya está anulada"

        if self.exportada_siat:
            return False, "No se puede anular una factura exportada al SIAT"

        self.estado = self.ESTADO_ANULADA
        if motivo:
            self.concepto = f"{self.concepto or ''} [ANULADA: {motivo}]".strip()

        if self.save():
            return True, "Factura anulada exitosamente"
        else:
            return False, "Error al anular la factura"

    def marcar_como_pagada(self) -> Tuple[bool, str]:
        """
        Marcar factura como pagada

        Returns:
            Tuple (éxito, mensaje)
        """
        if self.estado == self.ESTADO_ANULADA:
            return False, "No se puede marcar como pagada una factura anulada"

        if self.estado == self.ESTADO_PAGADA:
            return False, "La factura ya está marcada como pagada"

        self.estado = self.ESTADO_PAGADA

        if self.save():
            return True, "Factura marcada como pagada exitosamente"
        else:
            return False, "Error al marcar factura como pagada"

    def marcar_exportada_siat(self) -> Tuple[bool, str]:
        """
        Marcar factura como exportada al SIAT

        Returns:
            Tuple (éxito, mensaje)
        """
        if self.exportada_siat:
            return False, "La factura ya está marcada como exportada al SIAT"

        if self.estado == self.ESTADO_ANULADA:
            return False, "No se puede exportar al SIAT una factura anulada"

        self.exportada_siat = 1

        if self.save():
            return True, "Factura marcada como exportada al SIAT exitosamente"
        else:
            return False, "Error al marcar factura como exportada al SIAT"

    @classmethod
    def validate_nro_factura(cls, nro_factura: str) -> Tuple[bool, str]:
        """
        Validar número de factura

        Args:
            nro_factura: Número de factura a validar

        Returns:
            Tuple (válido, mensaje_error)
        """
        if not nro_factura or not nro_factura.strip():
            return False, "El número de factura no puede estar vacío"

        if len(nro_factura) < 3:
            return False, "El número de factura debe tener al menos 3 caracteres"

        if len(nro_factura) > 20:
            return False, "El número de factura no puede exceder 20 caracteres"

        # Verificar formato común (ej: FAC-000001, 001-001-0000001)
        if not re.match(r'^[A-Z0-9\-_]+$', nro_factura):
            return False, "El número de factura solo puede contener letras mayúsculas, números, guiones y guiones bajos"

        return True, ""

    @classmethod
    def validate_nit(cls, nit: str) -> Tuple[bool, str]:
        """
        Validar NIT boliviano

        Args:
            nit: NIT a validar (con o sin dígito verificador)

        Returns:
            Tuple (válido, mensaje_error)
        """
        if not nit:
            return True, ""  # NIT es opcional para consumidor final

        # Limpiar caracteres
        nit_limpio = nit.replace('-', '').strip()

        if not nit_limpio.isdigit():
            return False, "El NIT debe contener solo números"

        if len(nit_limpio) not in [9, 10]:
            return False, "El NIT debe tener 9 o 10 dígitos"

        # Validar dígito verificador si tiene 10 dígitos
        if len(nit_limpio) == 10:
            base = nit_limpio[:9]
            verificador = nit_limpio[9]

            # Algoritmo simple de verificación (para demostración)
            # En producción usar algoritmo oficial
            suma = sum(int(d) * (i + 1) for i, d in enumerate(base))
            digito_calculado = suma % 11
            if digito_calculado == 10:
                digito_calculado = 0

            if str(digito_calculado) != verificador:
                return False, "NIT inválido: dígito verificador incorrecto"

        return True, ""

    @classmethod
    def validate_ci(cls, ci: str, expedicion: str = None) -> Tuple[bool, str]:
        """
        Validar Cédula de Identidad boliviana

        Args:
            ci: CI a validar
            expedicion: Expedición (opcional)

        Returns:
            Tuple (válido, mensaje_error)
        """
        if not ci:
            return True, ""  # CI es opcional

        # Limpiar caracteres
        ci_limpio = ci.replace('-', '').strip()

        if not ci_limpio.isdigit():
            return False, "La CI debe contener solo números"

        if len(ci_limpio) < 4 or len(ci_limpio) > 10:
            return False, "La CI debe tener entre 4 y 10 dígitos"

        # Validar expedición si se proporciona
        if expedicion:
            expediciones_validas = ['BE', 'CH', 'CB', 'LP', 'OR', 'PD', 'PT', 'SC', 'TJ', 'EX']
            if expedicion not in expediciones_validas:
                return False, f"Expedición inválida. Válidas: {', '.join(expediciones_validas)}"

        return True, ""

    @classmethod
    def validate_razon_social(cls, razon_social: str) -> Tuple[bool, str]:
        """
        Validar razón social o nombre

        Args:
            razon_social: Razón social a validar

        Returns:
            Tuple (válido, mensaje_error)
        """
        if not razon_social or not razon_social.strip():
            return False, "La razón social no puede estar vacía"

        if len(razon_social) < 2:
            return False, "La razón social debe tener al menos 2 caracteres"

        if len(razon_social) > 200:
            return False, "La razón social no puede exceder 200 caracteres"

        return True, ""

    def to_dict(self, include_detalles: bool = False) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        data = {
            'id': self.id,
            'nro_factura': self.nro_factura,
            'fecha_emision': self.fecha_emision.isoformat() if hasattr(self.fecha_emision, 'isoformat') else str(self.fecha_emision),
            'fecha_emision_formateada': self.fecha_emision_formateada,
            'tipo_documento': self.tipo_documento,
            'tipo_documento_descripcion': self.tipo_documento_descripcion,
            'nit_ci': self.nit_ci,
            'nit_ci_formateado': self.nit_ci_formateado,
            'razon_social': self.razon_social,
            'subtotal': float(self.subtotal),
            'subtotal_formateado': self.subtotal_formateado,
            'iva': float(self.iva),
            'iva_formateado': self.iva_formateado,
            'it': float(self.it),
            'it_formateado': self.it_formateado,
            'total': float(self.total),
            'total_formateado': self.total_formateado,
            'concepto': self.concepto,
            'estado': self.estado,
            'estado_descripcion': self.estado_descripcion,
            'exportada_siat': bool(self.exportada_siat),
            'exportada_siat_descripcion': self.exportada_siat_descripcion,
            'created_at': self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else str(self.created_at),
            'created_at_formateado': self.created_at_formateado,
            'codigo_control': self.codigo_control,
            'es_consumidor_final': self.es_consumidor_final,
            'tiene_documento': self.tiene_documento
        }

        if include_detalles and self.detalles:
            data['detalles'] = self.detalles

        return data

    @classmethod
    def generar_resumen_mensual(
        cls, 
        año: int = None, 
        mes: int = None
    ) -> Dict[str, Any]:
        """
        Generar resumen mensual de facturas

        Args:
            año: Año (default: año actual)
            mes: Mes (1-12, default: mes actual)

        Returns:
            Diccionario con resumen
        """
        try:
            if año is None:
                año = datetime.now().year
            if mes is None:
                mes = datetime.now().month

            # Calcular fechas del mes
            fecha_inicio = date(año, mes, 1)
            if mes == 12:
                fecha_fin = date(año + 1, 1, 1)
            else:
                fecha_fin = date(año, mes + 1, 1)

            # Consultar facturas del mes
            query = """
                SELECT 
                    COUNT(*) as total_facturas,
                    SUM(subtotal) as total_subtotal,
                    SUM(iva) as total_iva,
                    SUM(it) as total_it,
                    SUM(total) as total_general,
                    estado,
                    COUNT(*) as cantidad_por_estado
                FROM facturas 
                WHERE fecha_emision >= ? AND fecha_emision < ?
                GROUP BY estado
            """

            resultados = cls.query(query, [fecha_inicio.isoformat(), fecha_fin.isoformat()])

            # Totales generales
            total_facturas = 0
            total_subtotal = Decimal('0')
            total_iva = Decimal('0')
            total_it = Decimal('0')
            total_general = Decimal('0')
            por_estado = {}

            for row in resultados:
                total_facturas += row['cantidad_por_estado']
                total_subtotal += Decimal(str(row['total_subtotal'] or 0))
                total_iva += Decimal(str(row['total_iva'] or 0))
                total_it += Decimal(str(row['total_it'] or 0))
                total_general += Decimal(str(row['total_general'] or 0))
                por_estado[row['estado']] = row['cantidad_por_estado']

            # Facturas por tipo de documento
            query_tipos = """
                SELECT 
                    tipo_documento,
                    COUNT(*) as cantidad,
                    SUM(total) as total
                FROM facturas 
                WHERE fecha_emision >= ? AND fecha_emision < ?
                GROUP BY tipo_documento
            """

            resultados_tipos = cls.query(query_tipos, [fecha_inicio.isoformat(), fecha_fin.isoformat()])
            por_tipo_documento = {}

            for row in resultados_tipos:
                por_tipo_documento[row['tipo_documento']] = {
                    'cantidad': row['cantidad'],
                    'total': Decimal(str(row['total'] or 0))
                }

            # Día con más facturas
            query_dia_max = """
                SELECT 
                    fecha_emision,
                    COUNT(*) as cantidad,
                    SUM(total) as total
                FROM facturas 
                WHERE fecha_emision >= ? AND fecha_emision < ?
                GROUP BY fecha_emision
                ORDER BY cantidad DESC, total DESC
                LIMIT 1
            """

            resultado_dia = cls.query(query_dia_max, [fecha_inicio.isoformat(), fecha_fin.isoformat()])
            dia_maximo = None
            if resultado_dia:
                dia_maximo = {
                    'fecha': resultado_dia[0]['fecha_emision'],
                    'cantidad': resultado_dia[0]['cantidad'],
                    'total': Decimal(str(resultado_dia[0]['total'] or 0))
                }

            return {
                'año': año,
                'mes': mes,
                'mes_nombre': fecha_inicio.strftime('%B'),
                'total_facturas': total_facturas,
                'total_subtotal': total_subtotal,
                'total_iva': total_iva,
                'total_it': total_it,
                'total_general': total_general,
                'por_estado': por_estado,
                'por_tipo_documento': por_tipo_documento,
                'dia_maximo': dia_maximo,
                'fecha_consulta': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            logger.error(f"Error al generar resumen mensual de facturas: {e}")
            return {
                'año': año or datetime.now().year,
                'mes': mes or datetime.now().month,
                'error': str(e)
            }