# models/matricula.py
"""
Modelo de Matrícula usando SQLite3 directamente.
"""
import logging
from typing import Any, List, Dict, Optional
from datetime import datetime, date, timedelta

from models.pago import PagoModel
from .base_model import BaseModel

logger = logging.getLogger(__name__)

class MatriculaModel(BaseModel):
    """Modelo que representa una matrícula de estudiante en un programa"""
    
    TABLE_NAME = "matriculas"
    
    # Estados válidos
    ESTADOS_PAGO = ['PENDIENTE', 'PARCIAL', 'PAGADO', 'MORA']
    ESTADOS_ACADEMICOS = ['PREINSCRITO', 'INSCRITO', 'EN_CURSO', 'CONCLUIDO', 'RETIRADO']
    MODALIDADES_PAGO = ['CONTADO', 'CUOTAS']
    
    def __init__(self, **kwargs):
        """
        Inicializa una matrícula.
        
        Campos esperados:
            estudiante_id, programa_id, modalidad_pago, plan_pago_id,
            monto_total, descuento_aplicado, monto_final, monto_pagado,
            estado_pago, estado_academico, fecha_matricula, fecha_inicio,
            fecha_conclusion, coordinador_id, observaciones
        """
        # Campos obligatorios
        self.estudiante_id = kwargs.get('estudiante_id')
        self.programa_id = kwargs.get('programa_id')
        self.modalidad_pago = kwargs.get('modalidad_pago', 'CONTADO')
        self.monto_total = kwargs.get('monto_total', 0.0)
        self.monto_final = kwargs.get('monto_final', self.monto_total)
        
        # Campos con valores por defecto
        self.descuento_aplicado = kwargs.get('descuento_aplicado', 0.0)
        self.monto_pagado = kwargs.get('monto_pagado', 0.0)
        self.estado_pago = kwargs.get('estado_pago', 'PENDIENTE')
        self.estado_academico = kwargs.get('estado_academico', 'PREINSCRITO')
        self.fecha_matricula = kwargs.get('fecha_matricula', datetime.now().isoformat())
        self.plan_pago_id = kwargs.get('plan_pago_id')
        
        # Campos opcionales
        self.fecha_inicio = kwargs.get('fecha_inicio')
        self.fecha_conclusion = kwargs.get('fecha_conclusion')
        self.coordinador_id = kwargs.get('coordinador_id')
        self.observaciones = kwargs.get('observaciones')
        
        # ID (si viene de la base de datos)
        if 'id' in kwargs:
            self.id = kwargs['id']
        
        # Validaciones
        self._validar()
    
    def _validar(self):
        """Valida los datos de la matrícula"""
        if not self.estudiante_id or not self.programa_id:
            raise ValueError("estudiante_id y programa_id son obligatorios")
        
        if self.modalidad_pago not in self.MODALIDADES_PAGO:
            raise ValueError(f"Modalidad de pago inválida. Válidas: {self.MODALIDADES_PAGO}")
        
        if self.modalidad_pago == 'CUOTAS' and not self.plan_pago_id:
            raise ValueError("Para modalidad CUOTAS se requiere plan_pago_id")
        
        if self.modalidad_pago == 'CONTADO' and self.plan_pago_id:
            raise ValueError("Para modalidad CONTADO no debe haber plan_pago_id")
        
        if self.estado_pago not in self.ESTADOS_PAGO:
            raise ValueError(f"Estado de pago inválido. Válidos: {self.ESTADOS_PAGO}")
        
        if self.estado_academico not in self.ESTADOS_ACADEMICOS:
            raise ValueError(f"Estado académico inválido. Válidos: {self.ESTADOS_ACADEMICOS}")
        
        if self.monto_total < 0 or self.monto_final < 0 or self.monto_pagado < 0:
            raise ValueError("Los montos no pueden ser negativos")
        
        if self.monto_pagado > self.monto_final:
            raise ValueError("El monto pagado no puede ser mayor al monto final")
    
    def __repr__(self):
        return f"<Matricula {self.id}: Estudiante {self.estudiante_id} en Programa {self.programa_id}>"
    
    @property
    def saldo_pendiente(self) -> float:
        """Calcula el saldo pendiente de pago"""
        return self.monto_final - self.monto_pagado
    
    @property
    def porcentaje_pagado(self) -> float:
        """Calcula el porcentaje pagado"""
        if self.monto_final == 0:
            return 0.0
        return (self.monto_pagado / self.monto_final) * 100
    
    # Método para registrar un pago
    def registrar_pago(self, monto: float, forma_pago: str, nro_comprobante: str = None, 
                      nro_transaccion: str = None, observaciones: str = None, 
                      nro_cuota: int = None) -> 'PagoModel':
        """Registra un pago para esta matrícula"""
        from models.pago import PagoModel

        # Validar monto
        if monto <= 0:
            raise ValueError("El monto debe ser mayor a 0")

        if monto > self.saldo_pendiente:
            raise ValueError(f"Monto excede el saldo pendiente: {self.saldo_pendiente}")

        # Crear pago - ¡IMPORTANTE! Estado CONFIRMADO
        pago = PagoModel(
            matricula_id=self.id,
            nro_cuota=nro_cuota,  # Nuevo: incluir número de cuota
            monto=monto,
            fecha_pago=date.today().isoformat(),
            forma_pago=forma_pago,
            estado='CONFIRMADO',  # Estado fijo como CONFIRMADO
            nro_comprobante=nro_comprobante,
            nro_transaccion=nro_transaccion,
            observaciones=observaciones
        )
        pago.save()  # Esto generará automáticamente el movimiento de caja

        # Actualizar matrícula
        self.monto_pagado += monto

        # Actualizar estado de pago
        if self.monto_pagado >= self.monto_final:
            self.estado_pago = 'PAGADO'
        elif self.monto_pagado > 0:
            self.estado_pago = 'PARCIAL'
        else:
            self.estado_pago = 'PENDIENTE'

        self.save()

        # Actualizar cuotas si existen
        self._actualizar_cuotas_pago(pago)

        return pago
    
    def _actualizar_cuotas_pago(self, pago):
        """Actualiza las cuotas relacionadas con este pago"""
        try:
            from models.cuota import CuotaModel
            # Buscar cuotas pendientes para esta matrícula
            cuotas_pendientes = CuotaModel.buscar_por_matricula_y_estado(self.id, 'PENDIENTE')
            
            if cuotas_pendientes:
                # Asignar el pago a la primera cuota pendiente
                cuota = cuotas_pendientes[0]
                cuota.pago_id = pago.id
                cuota.fecha_pago = date.today().isoformat()
                cuota.estado = 'PAGADA'
                cuota.save()
                
                logger.info(f"✅ Cuota {cuota.nro_cuota} marcada como pagada con pago ID: {pago.id}")
        except Exception as e:
            logger.warning(f"No se pudieron actualizar cuotas: {e}")
    
    def iniciar_curso(self, fecha_inicio: date = None):
        """Inicia el curso para esta matrícula"""
        self.estado_academico = 'EN_CURSO'
        if fecha_inicio:
            self.fecha_inicio = fecha_inicio.isoformat()
        else:
            self.fecha_inicio = date.today().isoformat()
        self.save()
    
    def concluir_matricula(self, fecha_conclusion: date = None):
        """Concluye la matrícula"""
        if self.estado_pago != 'PAGADO':
            raise ValueError("No se puede concluir matrícula con pagos pendientes")
        
        self.estado_academico = 'CONCLUIDO'
        if fecha_conclusion:
            self.fecha_conclusion = fecha_conclusion.isoformat()
        else:
            self.fecha_conclusion = date.today().isoformat()
        self.save()
    
    def retirar_estudiante(self):
        """Retira al estudiante del programa"""
        self.estado_academico = 'RETIRADO'
        self.save()
    
    @classmethod
    def matricular_estudiante(cls, estudiante_id: int, programa_id: int, 
                             modalidad_pago: str = 'CONTADO', plan_pago_id: int = None,
                             observaciones: str = None) -> 'MatriculaModel':
        """Crea una nueva matrícula con validaciones"""
        from database.database import db
        from models.programa import ProgramaModel
        
        # 1. Verificar que no exista matrícula previa
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE estudiante_id = ? AND programa_id = ?"
        existente = db.fetch_one(query, (estudiante_id, programa_id))
        
        if existente:
            raise ValueError(f"El estudiante ya está matriculado en este programa")
        
        # 2. Obtener programa y verificar cupos
        programa = ProgramaModel.find_by_id(programa_id)
        if not programa:
            raise ValueError(f"Programa con ID {programa_id} no existe")
        
        if programa.cupos_disponibles <= 0:
            raise ValueError(f"El programa no tiene cupos disponibles")
        
        # 3. Calcular montos según modalidad
        monto_total = programa.costo_base
        
        if modalidad_pago == 'CONTADO':
            # Aplicar descuento por contado
            descuento = monto_total * (programa.descuento_contado / 100)
            monto_final = monto_total - descuento
        else:
            # Sin descuento para cuotas
            monto_final = monto_total
            descuento = 0.0
        
        # 4. Crear matrícula
        matricula = cls(
            estudiante_id=estudiante_id,
            programa_id=programa_id,
            modalidad_pago=modalidad_pago,
            plan_pago_id=plan_pago_id,
            monto_total=monto_total,
            descuento_aplicado=descuento,
            monto_final=monto_final,
            observaciones=observaciones
        )
        
        # 5. Guardar matrícula
        matricula.save()
        
        # 6. Actualizar cupos del programa
        programa.ocupar_cupo()
        
        # 7. Generar cuotas si es pago en cuotas
        if modalidad_pago == 'CUOTAS' and plan_pago_id:
            matricula._generar_cuotas()
        
        logger.info(f"✅ Matrícula creada: Estudiante {estudiante_id} en Programa {programa_id}")
        return matricula
    
    # Método para generar cuotas
    def _generar_cuotas(self):
        """Genera cuotas mensuales fijas según el plan de pago"""
        from models.cuota import CuotaModel
        from database.database import db
        from datetime import datetime, timedelta
        from models.programa import ProgramaModel

        # Obtener plan de pago
        query = "SELECT * FROM planes_pago WHERE id = ?"
        plan = db.fetch_one(query, (self.plan_pago_id,))

        if not plan:
            raise ValueError(f"Plan de pago con ID {self.plan_pago_id} no existe")

        # Obtener programa para verificar si usa cuotas mensuales
        programa = ProgramaModel.find_by_id(self.programa_id)

        nro_cuotas = plan['nro_cuotas']
        intervalo_dias = plan['intervalo_dias']

        # Determinar monto de cuota
        # En el anuncio: solo la colegiatura se divide en cuotas
        costos = self.calcular_costos_matricula(programa)
        monto_cuota = costos['colegiatura'] / nro_cuotas

        # Fecha base para calcular vencimientos
        if self.fecha_inicio:
            try:
                if isinstance(self.fecha_inicio, str):
                    fecha_base = datetime.strptime(self.fecha_inicio, "%Y-%m-%d").date()
                else:
                    fecha_base = self.fecha_inicio
            except:
                fecha_base = datetime.now().date()
        else:
            fecha_base = datetime.now().date()

        # Generar cuotas mensuales
        print(f"\n📅 GENERANDO {nro_cuotas} CUOTAS MENSUALES:")
        print(f"   • Monto por cuota: ${monto_cuota:.2f}")
        print(f"   • Intervalo: {intervalo_dias} días")
        print(f"   • Fecha base: {fecha_base}")

        for i in range(1, nro_cuotas + 1):
            # Calcular fecha de vencimiento (mensual)
            fecha_vencimiento = fecha_base + timedelta(days=(i * intervalo_dias))

            cuota = CuotaModel(
                matricula_id=self.id,
                nro_cuota=i,
                monto=monto_cuota,
                fecha_vencimiento=fecha_vencimiento.isoformat(),
                estado='PENDIENTE'
            )
            cuota.save()

            print(f"   Cuota {i}: Vence {fecha_vencimiento}")

        # Registrar pagos iniciales (inscripción y matrícula)
        if costos['inscripcion'] > 0:
            self.registrar_pago_inicial('INSCRIPCIÓN', costos['inscripcion'])

        if costos['matricula'] > 0:
            self.registrar_pago_inicial('MATRÍCULA', costos['matricula'])

        logger.info(f"✅ {nro_cuotas} cuotas generadas para matrícula {self.id}")

    @classmethod
    def buscar_por_estudiante(cls, estudiante_id: int) -> List['MatriculaModel']:
        """Busca matrículas por estudiante"""
        from database.database import db
        
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE estudiante_id = ? ORDER BY fecha_matricula DESC"
        rows = db.fetch_all(query, (estudiante_id,))
        
        return [cls(**row) for row in rows]
    
    @classmethod
    def buscar_por_programa(cls, programa_id: int) -> List['MatriculaModel']:
        """Busca matrículas por programa"""
        from database.database import db
        
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE programa_id = ? ORDER BY fecha_matricula DESC"
        rows = db.fetch_all(query, (programa_id,))
        
        return [cls(**row) for row in rows]
    
    @classmethod
    def buscar_por_estado_pago(cls, estado_pago: str) -> List['MatriculaModel']:
        """Busca matrículas por estado de pago"""
        from database.database import db
        
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE estado_pago = ?"
        rows = db.fetch_all(query, (estado_pago,))
        
        return [cls(**row) for row in rows]
    
    def obtener_detalles_completos(self) -> Dict[str, Any]:
        """Obtiene detalles completos de la matrícula con información relacionada"""
        from database.database import db
        
        # Obtener estudiante
        query_est = "SELECT nombres, apellidos, ci_numero, ci_expedicion FROM estudiantes WHERE id = ?"
        estudiante = db.fetch_one(query_est, (self.estudiante_id,))
        
        # Obtener programa
        query_prog = "SELECT codigo, nombre, costo_base FROM programas_academicos WHERE id = ?"
        programa = db.fetch_one(query_prog, (self.programa_id,))
        
        # Obtener cuotas si existen
        cuotas = []
        try:
            from models.cuota import CuotaModel
            cuotas = CuotaModel.buscar_por_matricula(self.id)
        except:
            pass
        
        return {
            'matricula': self.to_dict(),
            'estudiante': estudiante,
            'programa': programa,
            'cuotas': [cuota.to_dict() for cuota in cuotas] if cuotas else [],
            'saldo_pendiente': self.saldo_pendiente,
            'porcentaje_pagado': self.porcentaje_pagado
        }

    # Método para calcular costos separados
    def calcular_costos_matricula(self, programa):
        """Calcula los costos separados de la matrícula"""
        from datetime import datetime

        costos = {
            'inscripcion': programa.costo_inscripcion,
            'matricula': programa.costo_matricula,
            'colegiatura': programa.costo_base,
            'descuento': 0,
            'total': 0
        }

        # Aplicar descuento de promoción si está vigente
        if programa.promocion_activa and programa.promocion_fecha_limite:
            hoy = datetime.now().date()
            fecha_limite = datetime.strptime(programa.promocion_fecha_limite, "%Y-%m-%d").date()
            if hoy <= fecha_limite:
                descuento = programa.costo_base * (programa.descuento_promocion / 100)
                costos['descuento'] = descuento
                costos['colegiatura'] = programa.costo_base - descuento

        # Aplicar descuento por pago al contado
        if self.modalidad_pago == 'CONTADO' and programa.descuento_contado > 0:
            descuento_contado = costos['colegiatura'] * (programa.descuento_contado / 100)
            costos['descuento'] += descuento_contado
            costos['colegiatura'] -= descuento_contado

        costos['total'] = costos['inscripcion'] + costos['matricula'] + costos['colegiatura']

        return costos
    
    # Método para registrar pagos iniciales
    def registrar_pago_inicial(self, concepto, monto, forma_pago='EFECTIVO'):
        """Registra pagos iniciales (inscripción, matrícula)"""
        from models.pago import PagoModel

        pago_data = {
            'matricula_id': self.id,
            'nro_cuota': None,  # No es una cuota
            'monto': monto,
            'fecha_pago': datetime.now().date().isoformat(),
            'forma_pago': forma_pago,
            'estado': 'CONFIRMADO',
            'observaciones': f"Pago inicial: {concepto}"
        }

        pago = PagoModel.create(pago_data)

        # Actualizar monto pagado en la matrícula
        self.monto_pagado += monto
        self.actualizar_estado_pago()

        return pago