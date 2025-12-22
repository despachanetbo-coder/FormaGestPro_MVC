# app/controllers/dashboard_controller.py
"""
app/controllers/dashboard_controller.py
Controlador para el dashboard - Maneja la lógica de negocio y datos
Versión: 3.2 - Usa Database en lugar de DatabaseConnection
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Configurar logging
logger = logging.getLogger(__name__)

class DashboardController:
    """Controlador para el dashboard del sistema - Versión optimizada"""
    
    def __init__(self):
        """Inicializar controlador con conexión a BD"""
        self.db = self._initialize_database()
        logger.info("✅ DashboardController inicializado")
    
    def _initialize_database(self):
        """Inicializar conexión a BD usando Database de database.database"""
        try:
            # Opción 1: Importar Database desde database.database
            from database.database import Database
            
            # Crear instancia de Database (es singleton)
            db_instance = Database()
            logger.info("✅ Base de datos inicializada usando Database")
            return db_instance
            
        except ImportError as e:
            logger.error(f"❌ No se pudo importar Database: {e}")
            
            # Opción 2: Intentar importar desde database
            try:
                from database import Database
                db_instance = Database()
                logger.info("✅ Base de datos inicializada desde database")
                return db_instance
                
            except ImportError as e2:
                logger.error(f"❌ También falló importar desde database: {e2}")
                
                # Opción 3: Crear clase mínima de respaldo
                logger.warning("⚠️  Creando Database mínima de respaldo")
                return self._create_minimal_database()
    
    def _create_minimal_database(self):
        """Crear conexión mínima a BD para respaldo"""
        class MinimalDatabase:
            def __init__(self):
                self._db_path = "formagestpro.db"
                logger.warning(f"⚠️  Usando Database mínima para: {self._db_path}")
            
            def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
                """Ejecutar consulta SELECT - versión mínima"""
                logger.debug(f"📋 Query ejecutada (mínima): {query[:50]}...")
                return []
            
            def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
                """Fetch all - versión mínima"""
                return []
            
            def fetch_one(self, query: str, params: tuple = ()) -> Dict[str, Any]:
                """Fetch one - versión mínima"""
                return {}
            
            def table_exists(self, table_name: str) -> bool:
                """Verificar si tabla existe - versión mínima"""
                return False
            
            def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
                """Obtener esquema de tabla - versión mínima"""
                return []
            
            def get_all_tables(self) -> List[str]:
                """Obtener todas las tablas - versión mínima"""
                return []
        
        return MinimalDatabase()
    
    # ============================================================================
    # MÉTODO PRINCIPAL - OBTENER TODOS LOS DATOS
    # ============================================================================
    
    def obtener_datos_dashboard(self) -> Dict[str, Any]:
        """
        Obtener todos los datos necesarios para el dashboard
        
        Returns:
            Dict con todos los datos del dashboard organizados
        """
        logger.info("📊 Obteniendo datos del dashboard desde BD...")
        
        try:
            # Si no hay conexión a BD, retornar datos vacíos
            if self.db is None:
                logger.warning("⚠️  No hay conexión a BD, retornando datos vacíos")
                return self._get_empty_data()
            
            # Ejecutar todas las consultas
            datos = {
                # Métricas básicas
                'total_estudiantes': self.obtener_total_estudiantes(),
                'total_docentes': self.obtener_total_docentes(),
                'programas_activos': self.obtener_programas_activos(),
                'programas_registrados_2025': self.obtener_programas_registrados_2025(),
                
                # Datos financieros
                'ingresos_mes_actual': self.obtener_ingresos_mes_actual(),
                'gastos_mes_actual': self.obtener_gastos_mes_actual(),
                
                # Distribuciones y listados
                'estudiantes_por_programa': self.obtener_estudiantes_por_programa(),
                'programas_en_progreso': self.obtener_programas_en_progreso(),
                'datos_financieros': self.obtener_datos_financieros(),
                'ultimos_estudiantes': self.obtener_ultimos_estudiantes(),
                'proximos_vencimientos': self.obtener_proximos_vencimientos(),
                
                # Estadísticas adicionales
                'estadisticas_avance': self.obtener_estadisticas_avance(),
                'top_programas': self.obtener_top_programas(),
            }
            
            # Calcular datos derivados
            self._calcular_datos_derivados(datos)
            
            logger.info("✅ Datos del dashboard cargados correctamente")
            return datos
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo datos del dashboard: {e}", exc_info=True)
            return self._get_empty_data()
    
    def _calcular_datos_derivados(self, datos: Dict[str, Any]):
        """Calcular datos derivados de los datos obtenidos"""
        # Año y mes actual
        datos['año_actual'] = datetime.now().strftime('%Y')
        datos['mes_actual'] = datetime.now().strftime('%B %Y')
        datos['mes_actual_nombre'] = datetime.now().strftime('%B')
        
        # Cálculo de cambios (simplificado)
        datos['estudiantes_cambio'] = self._calcular_cambio_estudiantes(datos.get('total_estudiantes', 0))
        datos['docentes_cambio'] = self._calcular_cambio_docentes(datos.get('total_docentes', 0))
        datos['programas_cambio'] = self._calcular_cambio_programas(datos.get('programas_activos', 0))
        datos['programas_cambio_año'] = self._calcular_cambio_programas_año(datos.get('programas_registrados_2025', 0))
        datos['ingresos_cambio'] = self._calcular_cambio_ingresos(datos.get('ingresos_mes_actual', 0))
        datos['gastos_cambio'] = self._calcular_cambio_gastos(datos.get('gastos_mes_actual', 0))
        
        # Alias para compatibilidad
        datos['programas'] = datos.get('programas_activos', 0)
        datos['programas_total'] = datos.get('programas_activos', 0)
        datos['programas_año_actual'] = datos.get('programas_registrados_2025', 0)
        datos['ingresos_mes'] = datos.get('ingresos_mes_actual', 0)
        datos['gastos_mes'] = datos.get('gastos_mes_actual', 0)
        
        # Cálculos para programas en progreso
        programas = datos.get('programas_en_progreso', [])
        datos['total_programas_activos'] = len(programas)
        datos['total_estudiantes_matriculados'] = sum(p.get('estudiantes_matriculados', 0) for p in programas)
        
        # Ocupación promedio
        if programas:
            ocupacion_promedio = sum(p.get('porcentaje_ocupacion', 0) for p in programas) / len(programas)
            datos['ocupacion_promedio'] = round(ocupacion_promedio, 1)
        else:
            datos['ocupacion_promedio'] = 0
    
    def _get_empty_data(self) -> Dict[str, Any]:
        """Retornar estructura de datos vacía"""
        return {
            'total_estudiantes': 0,
            'total_docentes': 0,
            'programas_activos': 0,
            'programas_registrados_2025': 0,
            'ingresos_mes_actual': 0.0,
            'gastos_mes_actual': 0.0,
            'estudiantes_por_programa': {},
            'programas_en_progreso': [],
            'datos_financieros': [],
            'ultimos_estudiantes': [],
            'proximos_vencimientos': [],
            'estadisticas_avance': {},
            'top_programas': [],
            'año_actual': datetime.now().strftime('%Y'),
            'mes_actual': datetime.now().strftime('%B %Y'),
            'mes_actual_nombre': datetime.now().strftime('%B'),
            'estudiantes_cambio': 'Sin cambios',
            'docentes_cambio': 'Sin cambios',
            'programas_cambio': '0 activos',
            'programas_cambio_año': '0 este año',
            'ingresos_cambio': '0%',
            'gastos_cambio': '0%',
            'programas': 0,
            'programas_total': 0,
            'programas_año_actual': 0,
            'ingresos_mes': 0.0,
            'gastos_mes': 0.0,
            'total_programas_activos': 0,
            'ocupacion_promedio': 0,
            'total_estudiantes_matriculados': 0
        }
    
    # ============================================================================
    # MÉTODOS DE CONSULTA ESPECÍFICOS (ADAPTADOS PARA Database)
    # ============================================================================
    
    def obtener_total_estudiantes(self) -> int:
        """Obtener número total de estudiantes activos"""
        try:
            if not self.db.table_exists("estudiantes"):
                return 0
                
            query = """
            SELECT COUNT(*) as total 
            FROM estudiantes 
            WHERE activo = 1
            """
            result = self.db.fetch_one(query)
            return result['total'] if result and 'total' in result else 0
        except Exception as e:
            logger.error(f"Error obteniendo total estudiantes: {e}")
            return 0
    
    def obtener_total_docentes(self) -> int:
        """Obtener número total de docentes activos"""
        try:
            if not self.db.table_exists("docentes"):
                return 0
                
            query = """
            SELECT COUNT(*) as total 
            FROM docentes 
            WHERE activo = 1
            """
            result = self.db.fetch_one(query)
            return result['total'] if result and 'total' in result else 0
        except Exception as e:
            logger.error(f"Error obteniendo total docentes: {e}")
            return 0
    
    def obtener_programas_activos(self) -> int:
        """Obtener número de programas activos (INICIADO)"""
        try:
            if not self.db.table_exists("programas_academicos"):
                return 0
                
            query = """
            SELECT COUNT(*) as total 
            FROM programas_academicos 
            WHERE estado = 'INICIADO'
            """
            result = self.db.fetch_one(query)
            return result['total'] if result and 'total' in result else 0
        except Exception as e:
            logger.error(f"Error obteniendo programas activos: {e}")
            return 0
    
    def obtener_programas_registrados_2025(self) -> int:
        """Obtener número de programas registrados en 2025"""
        try:
            if not self.db.table_exists("programas_academicos"):
                return 0
                
            query = """
            SELECT COUNT(*) as total 
            FROM programas_academicos 
            WHERE strftime('%Y', fecha_inicio_planificada) = '2025'
               OR strftime('%Y', fecha_inicio_real) = '2025'
               OR strftime('%Y', created_at) = '2025'
            """
            result = self.db.fetch_one(query)
            return result['total'] if result and 'total' in result else 0
        except Exception as e:
            logger.error(f"Error obteniendo programas 2025: {e}")
            return 0
    
    def obtener_ingresos_mes_actual(self) -> float:
        """Obtener ingresos del mes actual"""
        try:
            mes_actual = datetime.now().strftime("%Y-%m")
            
            # Intentar diferentes tablas de ingresos
            ingresos = 0.0
            
            if self.db.table_exists("movimientos_caja"):
                query = """
                SELECT SUM(monto) as total 
                FROM movimientos_caja 
                WHERE tipo = 'INGRESO' 
                AND strftime('%Y-%m', fecha) = ?
                """
                result = self.db.fetch_one(query, (mes_actual,))
                if result and result['total']:
                    ingresos = float(result['total'])
            
            elif self.db.table_exists("pagos"):
                query = """
                SELECT SUM(monto) as total 
                FROM pagos 
                WHERE estado = 'CONFIRMADO'
                AND strftime('%Y-%m', fecha_pago) = ?
                """
                result = self.db.fetch_one(query, (mes_actual,))
                if result and result['total']:
                    ingresos = float(result['total'])
            
            return ingresos
        except Exception as e:
            logger.error(f"Error obteniendo ingresos mes actual: {e}")
            return 0.0
    
    def obtener_gastos_mes_actual(self) -> float:
        """Obtener gastos del mes actual"""
        try:
            mes_actual = datetime.now().strftime("%Y-%m")
            
            gastos = 0.0
            
            if self.db.table_exists("movimientos_caja"):
                query = """
                SELECT SUM(monto) as total 
                FROM movimientos_caja 
                WHERE tipo = 'EGRESO' 
                AND strftime('%Y-%m', fecha) = ?
                """
                result = self.db.fetch_one(query, (mes_actual,))
                if result and result['total']:
                    gastos = float(result['total'])
            
            elif self.db.table_exists("gastos_operativos"):
                query = """
                SELECT SUM(monto) as total 
                FROM gastos_operativos 
                WHERE strftime('%Y-%m', fecha) = ?
                """
                result = self.db.fetch_one(query, (mes_actual,))
                if result and result['total']:
                    gastos = float(result['total'])
            
            return gastos
        except Exception as e:
            logger.error(f"Error obteniendo gastos mes actual: {e}")
            return 0.0
    
    def obtener_estudiantes_por_programa(self) -> Dict[str, int]:
        """Obtener distribución de estudiantes por programa"""
        try:
            if not self.db.table_exists("matriculas") or not self.db.table_exists("programas_academicos"):
                return {}
            
            query = """
            SELECT 
                pa.nombre as programa,
                COUNT(DISTINCT m.estudiante_id) as cantidad_estudiantes
            FROM matriculas m
            INNER JOIN programas_academicos pa ON m.programa_id = pa.id
            WHERE m.estado_academico IN ('PREINSCRITO', 'INSCRITO', 'EN_CURSO', 'CONCLUIDO')
            GROUP BY pa.id, pa.nombre
            ORDER BY cantidad_estudiantes DESC
            LIMIT 10
            """
            
            result = self.db.fetch_all(query)
            distribucion = {}
            
            for row in result:
                programa_nombre = row['programa']
                if len(programa_nombre) > 20:
                    programa_nombre = programa_nombre[:17] + "..."
                distribucion[programa_nombre] = row['cantidad_estudiantes']
            
            logger.info(f"📊 Distribución estudiantes por programa: {len(distribucion)} programas")
            return distribucion
            
        except Exception as e:
            logger.error(f"Error obteniendo estudiantes por programa: {e}")
            return {}
    
    def obtener_programas_en_progreso(self) -> List[Dict[str, Any]]:
        """Obtener programas en estado PLANIFICADO o INICIADO"""
        try:
            logger.info("🔍 Ejecutando obtener_programas_en_progreso()")
            
            if not self.db.table_exists("programas_academicos"):
                logger.warning("❌ Tabla 'programas_academicos' no existe")
                return []
            
            # Consulta principal
            query = """
            SELECT 
                pa.id,
                pa.codigo,
                pa.nombre,
                pa.descripcion,
                pa.estado,
                pa.cupos_totales,
                pa.cupos_disponibles,
                pa.fecha_inicio_planificada,
                pa.fecha_inicio_real,
                pa.tutor_id,
                COALESCE(d.nombres || ' ' || d.apellidos, 'Sin asignar') as tutor_nombre,

                -- Contar estudiantes matriculados activos
                COUNT(DISTINCT CASE 
                    WHEN m.estado_academico IN ('PREINSCRITO', 'INSCRITO', 'EN_CURSO') 
                    THEN m.estudiante_id 
                END) as estudiantes_matriculados

            FROM programas_academicos pa

            -- JOIN con tutor
            LEFT JOIN docentes d ON pa.tutor_id = d.id

            -- JOIN con matrículas
            LEFT JOIN matriculas m ON pa.id = m.programa_id

            WHERE pa.estado NOT IN ('CONCLUIDO', 'CANCELADO')

            GROUP BY 
                pa.id, pa.codigo, pa.nombre, pa.descripcion, 
                pa.estado, pa.cupos_totales, pa.cupos_disponibles,
                pa.fecha_inicio_planificada, pa.fecha_inicio_real,
                pa.tutor_id, d.nombres, d.apellidos

            ORDER BY 
                CASE pa.estado
                    WHEN 'INICIADO' THEN 1
                    WHEN 'PLANIFICADO' THEN 2
                    ELSE 3
                END,
                pa.fecha_inicio_planificada DESC
            """
            
            result = self.db.fetch_all(query)
            programas = []
            
            logger.info(f"📊 Encontrados {len(result)} programas en progreso")
            
            for row in result:
                cupos_totales = row['cupos_totales'] or 0
                estudiantes_matriculados = row['estudiantes_matriculados'] or 0
                
                # Calcular porcentaje de ocupación
                if cupos_totales > 0:
                    porcentaje_ocupacion = (estudiantes_matriculados / cupos_totales) * 100
                else:
                    porcentaje_ocupacion = 0
                
                programa = {
                    'id': row['id'],
                    'codigo': row['codigo'],
                    'nombre': row['nombre'],
                    'descripcion': row['descripcion'] or '',
                    'estado': row['estado'],
                    'estado_display': self._traducir_estado(row['estado']),
                    'cupos_totales': cupos_totales,
                    'cupos_disponibles': row['cupos_disponibles'] or 0,
                    'cupos_ocupados': estudiantes_matriculados,
                    'estudiantes_matriculados': estudiantes_matriculados,
                    'tutor_nombre': row['tutor_nombre'],
                    'fecha_inicio': row['fecha_inicio_real'] or row['fecha_inicio_planificada'] or '',
                    'porcentaje_ocupacion': round(porcentaje_ocupacion, 1)
                }
                programas.append(programa)
            
            return programas
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo programas en progreso: {e}", exc_info=True)
            return []
    
    def obtener_datos_financieros(self, meses: int = 6) -> List[Dict[str, Any]]:
        """Obtener datos financieros de los últimos meses"""
        try:
            datos = []
            ahora = datetime.now()
            
            for i in range(meses - 1, -1, -1):
                fecha = ahora - timedelta(days=30 * i)
                mes = fecha.strftime("%Y-%m")
                mes_nombre = fecha.strftime("%b")
                
                # Ingresos del mes
                ingresos = 0.0
                if self.db.table_exists("movimientos_caja"):
                    query_ingresos = """
                    SELECT SUM(monto) as total 
                    FROM movimientos_caja 
                    WHERE tipo = 'INGRESO' 
                    AND strftime('%Y-%m', fecha) = ?
                    """
                    result_ingresos = self.db.fetch_one(query_ingresos, (mes,))
                    if result_ingresos and result_ingresos['total']:
                        ingresos = float(result_ingresos['total'])
                
                # Gastos del mes
                gastos = 0.0
                if self.db.table_exists("movimientos_caja"):
                    query_gastos = """
                    SELECT SUM(monto) as total 
                    FROM movimientos_caja 
                    WHERE tipo = 'EGRESO' 
                    AND strftime('%Y-%m', fecha) = ?
                    """
                    result_gastos = self.db.fetch_one(query_gastos, (mes,))
                    if result_gastos and result_gastos['total']:
                        gastos = float(result_gastos['total'])
                
                datos.append({
                    'mes': mes_nombre,
                    'mes_key': mes,
                    'ingresos': ingresos,
                    'gastos': gastos,
                    'beneficio': ingresos - gastos
                })
            
            # Calcular saldo acumulado
            saldo_acumulado = 0
            for i, mes_data in enumerate(datos):
                saldo_acumulado += mes_data['beneficio']
                datos[i]['saldo_acumulado'] = saldo_acumulado
            
            logger.info(f"📈 Datos financieros: {len(datos)} meses cargados")
            return datos
            
        except Exception as e:
            logger.error(f"Error obteniendo datos financieros: {e}")
            return []
    
    def obtener_ultimos_estudiantes(self, limite: int = 5) -> List[Dict[str, Any]]:
        """Obtener los últimos estudiantes registrados"""
        try:
            if not self.db.table_exists("estudiantes"):
                return []
            
            query = f"""
            SELECT 
                e.id,
                e.ci_numero as codigo,
                e.nombres,
                e.apellidos,
                e.email,
                e.telefono,
                e.fecha_registro
            FROM estudiantes e
            WHERE e.activo = 1
            ORDER BY e.fecha_registro DESC
            LIMIT {limite}
            """
            
            result = self.db.fetch_all(query)
            estudiantes = []
            
            for row in result:
                estudiantes.append({
                    'id': row['id'],
                    'codigo': row['codigo'],
                    'nombre_completo': f"{row['nombres']} {row['apellidos']}",
                    'email': row['email'],
                    'telefono': row['telefono'],
                    'fecha_registro': row['fecha_registro']
                })
            
            return estudiantes
            
        except Exception as e:
            logger.error(f"Error obteniendo últimos estudiantes: {e}")
            return []
    
    def obtener_proximos_vencimientos(self, dias: int = 30) -> List[Dict[str, Any]]:
        """Obtener próximos vencimientos de pagos"""
        try:
            if not self.db.table_exists("pagos"):
                return []
            
            fecha_limite = (datetime.now() + timedelta(days=dias)).strftime("%Y-%m-%d")
            
            query = """
            SELECT 
                e.ci_numero as estudiante_codigo,
                e.nombres || ' ' || e.apellidos as estudiante_nombre,
                p.codigo as programa_codigo,
                p.nombre as programa_nombre,
                pg.fecha_vencimiento,
                pg.monto,
                pg.estado
            FROM cuotas_programadas pg
            JOIN matriculas m ON pg.matricula_id = m.id
            JOIN estudiantes e ON m.estudiante_id = e.id
            JOIN programas_academicos p ON m.programa_id = p.id
            WHERE pg.estado = 'PENDIENTE'
            AND pg.fecha_vencimiento BETWEEN date('now') AND ?
            ORDER BY pg.fecha_vencimiento ASC
            LIMIT 10
            """
            
            result = self.db.fetch_all(query, (fecha_limite,))
            vencimientos = []
            
            for row in result:
                vencimientos.append({
                    'estudiante_codigo': row['estudiante_codigo'],
                    'estudiante_nombre': row['estudiante_nombre'],
                    'programa_codigo': row['programa_codigo'],
                    'programa_nombre': row['programa_nombre'],
                    'fecha_vencimiento': row['fecha_vencimiento'],
                    'monto': float(row['monto']) if row['monto'] else 0.0,
                    'estado': row['estado'],
                    'dias_restantes': (datetime.strptime(row['fecha_vencimiento'], '%Y-%m-%d') - datetime.now()).days
                })
            
            return vencimientos
            
        except Exception as e:
            logger.error(f"Error obteniendo próximos vencimientos: {e}")
            return []
    
    def obtener_estadisticas_avance(self) -> Dict[str, Any]:
        """Obtener estadísticas de avance de programas"""
        try:
            if not self.db.table_exists("programas_academicos"):
                return self._get_empty_stats()
            
            query = """
            SELECT 
                COUNT(*) as total_programas,
                SUM(CASE WHEN estado = 'COMPLETADO' THEN 1 ELSE 0 END) as completados,
                SUM(CASE WHEN estado = 'INICIADO' THEN 1 ELSE 0 END) as en_progreso,
                SUM(CASE WHEN estado = 'PLANIFICADO' THEN 1 ELSE 0 END) as planificados,
                SUM(CASE WHEN estado = 'CANCELADO' THEN 1 ELSE 0 END) as cancelados
            FROM programas_academicos
            """
            
            result = self.db.fetch_one(query)
            
            if result:
                total = result['total_programas'] or 0
                
                if total > 0:
                    return {
                        'total_programas': total,
                        'completados': result['completados'] or 0,
                        'en_progreso': result['en_progreso'] or 0,
                        'planificados': result['planificados'] or 0,
                        'cancelados': result['cancelados'] or 0,
                        'porcentaje_completados': round(((result['completados'] or 0) / total) * 100, 1),
                        'porcentaje_en_progreso': round(((result['en_progreso'] or 0) / total) * 100, 1)
                    }
            
            return self._get_empty_stats()
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de avance: {e}")
            return self._get_empty_stats()
    
    def obtener_top_programas(self, limite: int = 5) -> List[Dict[str, Any]]:
        """Obtener top programas con más estudiantes"""
        try:
            if not self.db.table_exists("programas_academicos"):
                return []
            
            query = f"""
            SELECT 
                p.codigo,
                p.nombre,
                COUNT(m.estudiante_id) as total_estudiantes,
                p.cupos_totales,
                p.estado
            FROM programas_academicos p
            LEFT JOIN matriculas m ON p.id = m.programa_id
            GROUP BY p.id, p.codigo, p.nombre, p.cupos_totales, p.estado
            HAVING COUNT(m.estudiante_id) > 0
            ORDER BY total_estudiantes DESC
            LIMIT {limite}
            """
            
            result = self.db.fetch_all(query)
            programas = []
            
            for row in result:
                cupos_totales = row['cupos_totales'] or 0
                total_estudiantes = row['total_estudiantes'] or 0
                porcentaje_ocupacion = 0
                
                if cupos_totales > 0:
                    porcentaje_ocupacion = round((total_estudiantes / cupos_totales) * 100, 1)
                
                programas.append({
                    'codigo': row['codigo'],
                    'nombre': row['nombre'],
                    'total_estudiantes': total_estudiantes,
                    'cupos_totales': cupos_totales,
                    'porcentaje_ocupacion': porcentaje_ocupacion,
                    'estado': self._traducir_estado(row['estado'])
                })
            
            return programas
            
        except Exception as e:
            logger.error(f"Error obteniendo top programas: {e}")
            return []
    
    # ============================================================================
    # MÉTODOS AUXILIARES
    # ============================================================================
    
    def _traducir_estado(self, estado: str) -> str:
        """Traducir estado de inglés a español"""
        traducciones = {
            'PLANNED': 'PLANIFICADO',
            'IN_PROGRESS': 'EN PROGRESO',
            'COMPLETED': 'COMPLETADO',
            'CANCELLED': 'CANCELADO',
            'PLANIFICADO': 'PLANIFICADO',
            'INICIADO': 'INICIADO',
            'COMPLETADO': 'COMPLETADO',
            'CANCELADO': 'CANCELADO'
        }
        return traducciones.get(estado.upper(), estado)
    
    def _get_empty_stats(self) -> Dict[str, Any]:
        """Retornar estadísticas vacías"""
        return {
            'total_programas': 0,
            'completados': 0,
            'en_progreso': 0,
            'planificados': 0,
            'cancelados': 0,
            'porcentaje_completados': 0,
            'porcentaje_en_progreso': 0
        }
    
    def _calcular_cambio_estudiantes(self, total: int) -> str:
        """Calcular cambio en estudiantes (simplificado)"""
        if total == 0:
            return "Sin estudiantes"
        elif total < 10:
            return f"+{total} registrados"
        else:
            return f"{total} activos"
    
    def _calcular_cambio_docentes(self, total: int) -> str:
        """Calcular cambio en docentes (simplificado)"""
        if total == 0:
            return "Sin docentes"
        elif total < 5:
            return f"+{total} registrados"
        else:
            return f"{total} activos"
    
    def _calcular_cambio_programas(self, total: int) -> str:
        """Calcular cambio en programas (simplificado)"""
        if total == 0:
            return "Sin programas"
        else:
            return f"{total} activos"
    
    def _calcular_cambio_programas_año(self, total: int) -> str:
        """Calcular cambio en programas del año (simplificado)"""
        if total == 0:
            return "0 este año"
        else:
            return f"{total} en {datetime.now().strftime('%Y')}"
    
    def _calcular_cambio_ingresos(self, total: float) -> str:
        """Calcular cambio en ingresos (simplificado)"""
        if total == 0:
            return "Bs 0"
        else:
            return f"Bs {total:,.0f}"
    
    def _calcular_cambio_gastos(self, total: float) -> str:
        """Calcular cambio en gastos (simplificado)"""
        if total == 0:
            return "Bs 0"
        else:
            return f"Bs {total:,.0f}"
    
    # ============================================================================
    # MÉTODOS PÚBLICOS ADICIONALES
    # ============================================================================
    
    def actualizar_datos(self) -> Dict[str, Any]:
        """Actualizar todos los datos del dashboard"""
        logger.info("🔄 Actualizando datos del dashboard...")
        return self.obtener_datos_dashboard()
    
    def cerrar_conexion(self):
        """Cerrar conexión a la base de datos"""
        if hasattr(self, 'db') and self.db:
            try:
                self.db.close()
                logger.info("✅ Conexión a BD cerrada")
            except:
                pass


# Singleton para fácil acceso
dashboard_controller = DashboardController()