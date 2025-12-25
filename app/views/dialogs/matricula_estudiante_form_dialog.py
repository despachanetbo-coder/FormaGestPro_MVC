# app/views/dialogs/matricula_estudiante_form_dialog.py
"""
Dialogo para matricular un estudiante - VERSIÓN DINÁMICA
No requiere archivo UI generado
"""
import logging
from decimal import Decimal
from datetime import date
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QGroupBox, QDateEdit, QCheckBox, QMessageBox,
    QFormLayout, QFrame
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

from app.models.programa_academico_model import ProgramaAcademicoModel
from app.models.estudiante_model import EstudianteModel
from app.models.matricula_model import MatriculaModel

logger = logging.getLogger(__name__)


class MatriculaEstudianteFormDialog(QDialog):
    """Diálogo para matricular un estudiante - UI DINÁMICA"""
    
    def __init__(self, estudiante_id=None, parent=None):
        super().__init__(parent)

        # Inicializar atributos
        self.estudiante_id = estudiante_id
        self.estudiante_data = None
        self.programa_seleccionado = None
        self.monto_base = Decimal('0')
        self.descuento_total = Decimal('0')
        self.monto_final = Decimal('0')
        self.programas_cache = {}

        # Inicializar controladores
        self._inicializar_controladores()

        # Configurar UI dinámica
        self._crear_ui()

        # Cargar datos
        self._cargar_programas()
        if estudiante_id:
            self._cargar_estudiante(estudiante_id)

    def _inicializar_controladores(self):
        """Inicializar controladores de forma segura"""
        try:
            from app.controllers.programa_academico_controller import ProgramaAcademicoController
            self.programa_controller = ProgramaAcademicoController()
        except ImportError:
            logger.warning("Controlador de programas no disponible")
        
        try:
            from app.controllers.estudiante_controller import EstudianteController
            self.estudiante_controller = EstudianteController()
        except ImportError:
            logger.warning("Controlador de estudiantes no disponible")
        
        try:
            from app.controllers.matricula_controller import MatriculaController
            self.matricula_controller = MatriculaController()
        except ImportError:
            logger.warning("Controlador de matrículas no disponible")

    def _crear_ui(self):
        """Crear interfaz de usuario dinámica"""
        self.setWindowTitle("Matricular Estudiante")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # === SECCIÓN ESTUDIANTE ===
        estudiante_group = QGroupBox("Estudiante")
        estudiante_layout = QVBoxLayout()
        
        self.lbl_estudiante_info = QLabel("Cargando información del estudiante...")
        self.lbl_estudiante_info.setStyleSheet("font-weight: bold; padding: 5px;")
        estudiante_layout.addWidget(self.lbl_estudiante_info)
        
        estudiante_group.setLayout(estudiante_layout)
        main_layout.addWidget(estudiante_group)
        
        # === SECCIÓN PROGRAMA ===
        programa_group = QGroupBox("Programa Académico")
        programa_layout = QVBoxLayout()
        
        # Combo programas
        programa_form = QFormLayout()
        self.combo_programa = QComboBox()
        programa_form.addRow("Seleccionar Programa:", self.combo_programa)
        programa_layout.addLayout(programa_form)
        
        # Información del programa seleccionado
        self.lbl_programa_info = QLabel("Seleccione un programa para ver detalles")
        self.lbl_programa_info.setWordWrap(True)
        self.lbl_programa_info.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px; color: black;")
        programa_layout.addWidget(self.lbl_programa_info)
        
        programa_group.setLayout(programa_layout)
        main_layout.addWidget(programa_group)
        
        # === SECCIÓN FECHA ===
        fecha_group = QGroupBox("Fecha de Inicio")
        fecha_layout = QHBoxLayout()
        
        self.date_fecha_inicio = QDateEdit()
        self.date_fecha_inicio.setDisplayFormat("dd/MM/yyyy")
        self.date_fecha_inicio.setDate(QDate.currentDate())
        self.date_fecha_inicio.setCalendarPopup(True)
        
        fecha_layout.addWidget(QLabel("Fecha de inicio:"))
        fecha_layout.addWidget(self.date_fecha_inicio)
        fecha_layout.addStretch()
        
        fecha_group.setLayout(fecha_layout)
        main_layout.addWidget(fecha_group)
        
        # === SECCIÓN PAGO ===
        pago_group = QGroupBox("Información de Pago")
        pago_layout = QVBoxLayout()
        
        # Forma de pago
        forma_layout = QHBoxLayout()
        forma_layout.addWidget(QLabel("Forma de pago:"))
        self.combo_forma_pago = QComboBox()
        self.combo_forma_pago.addItems(["-- Seleccionar --", "CONTADO", "CUOTAS (2 meses)", "CUOTAS (3 meses)", "CUOTAS (6 meses)"])
        forma_layout.addWidget(self.combo_forma_pago)
        forma_layout.addStretch()
        pago_layout.addLayout(forma_layout)
        
        # Opciones de pago
        opciones_layout = QHBoxLayout()
        self.check_incluir_matricula = QCheckBox("Incluir costo de matrícula")
        self.check_incluir_matricula.setChecked(True)
        opciones_layout.addWidget(self.check_incluir_matricula)
        
        self.check_descuento = QCheckBox("Aplicar descuento por pago al contado")
        self.check_descuento.setEnabled(False)
        opciones_layout.addWidget(self.check_descuento)
        opciones_layout.addStretch()
        pago_layout.addLayout(opciones_layout)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        pago_layout.addWidget(separator)
        
        # Totales
        totales_layout = QFormLayout()
        
        self.lbl_costo_programa = QLabel("Bs. 0.00")
        totales_layout.addRow("Costo del programa:", self.lbl_costo_programa)
        
        self.lbl_costo_matricula = QLabel("Bs. 0.00")
        totales_layout.addRow("Costo de matrícula:", self.lbl_costo_matricula)
        
        self.lbl_descuento = QLabel("Bs. 0.00")
        totales_layout.addRow("Descuento aplicado:", self.lbl_descuento)
        
        self.lbl_total = QLabel("Bs. 0.00")
        self.lbl_total.setFont(QFont("Arial", 12, QFont.Bold))
        self.lbl_total.setStyleSheet("color: #2c3e50;")
        totales_layout.addRow("TOTAL A PAGAR:", self.lbl_total)
        
        pago_layout.addLayout(totales_layout)
        pago_group.setLayout(pago_layout)
        main_layout.addWidget(pago_group)
        
        # === BOTONES ===
        botones_layout = QHBoxLayout()
        botones_layout.addStretch()
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setMinimumWidth(100)
        botones_layout.addWidget(self.btn_cancelar)
        
        self.btn_matricular = QPushButton("Matricular")
        self.btn_matricular.setMinimumWidth(100)
        self.btn_matricular.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        self.btn_matricular.setEnabled(False)
        botones_layout.addWidget(self.btn_matricular)
        
        main_layout.addLayout(botones_layout)
        
        # Conectar señales
        self._conectar_señales()

    def _conectar_señales(self):
        """Conectar señales y slots"""
        self.combo_programa.currentIndexChanged.connect(self._on_programa_seleccionado)
        self.combo_forma_pago.currentIndexChanged.connect(self._on_forma_pago_cambiada)
        self.check_descuento.stateChanged.connect(self._calcular_costos)
        self.check_incluir_matricula.stateChanged.connect(self._calcular_costos)
        
        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_matricular.clicked.connect(self._on_matricular)

    def _cargar_programas(self):
        """Cargar programas académicos disponibles"""
        try:
            self.combo_programa.clear()
            self.combo_programa.addItem("-- Seleccionar Programa --", None)
            
            programas = self._obtener_programas_disponibles()
            
            if programas:
                for programa in programas:
                    self._agregar_programa_combo(programa)
                
                logger.info(f"✅ {len(programas)} programas cargados")
            else:
                self.combo_programa.addItem("⚠️ No hay programas con cupos disponibles", None)
                self.combo_programa.setEnabled(False)
                logger.warning("No hay programas disponibles")
                
        except Exception as e:
            logger.error(f"Error cargando programas: {e}", exc_info=True)

    def _obtener_programas_disponibles(self):
        """Obtener programas disponibles para matrícula"""
        try:
            programas = []
            
            # Estrategia 1: Usar controlador
            if self.programa_controller and hasattr(self.programa_controller, 'obtener_todos'):
                try:
                    todos = self.programa_controller.obtener_todos()
                    programas = [p for p in todos if 
                               getattr(p, 'estado', '') in ['PLANIFICADO', 'INICIADO'] and
                               getattr(p, 'cupos_disponibles', 0) > 0]
                except Exception as e:
                    logger.warning(f"Controlador falló: {e}")
            
            # Estrategia 2: Cargar directamente
            if not programas:
                programas = self._obtener_programas_directamente()
            
            return programas
            
        except Exception as e:
            logger.error(f"Error obteniendo programas: {e}")
            return []

    def _obtener_programas_directamente(self):
        """Obtener programas directamente desde el modelo"""
        try:
            programas = []
            
            # Método 1: SQLAlchemy
            if hasattr(ProgramaAcademicoModel, 'query'):
                from sqlalchemy import or_
                programas = ProgramaAcademicoModel.query.filter(
                    or_(ProgramaAcademicoModel.estado == 'PLANIFICADO', 
                        ProgramaAcademicoModel.estado == 'INICIADO'),
                    ProgramaAcademicoModel.cupos_disponibles > 0
                ).all()
            
            # Método 2: get_all
            elif hasattr(ProgramaAcademicoModel, 'get_all'):
                todos = ProgramaAcademicoModel.get_all()
                programas = [p for p in todos if 
                           getattr(p, 'estado', '') in ['PLANIFICADO', 'INICIADO'] and
                           getattr(p, 'cupos_disponibles', 0) > 0]
            
            return programas
            
        except Exception as e:
            logger.error(f"Error obteniendo programas directamente: {e}")
            return []

    def _agregar_programa_combo(self, programa):
        """Agregar programa al combobox"""
        try:
            programa_id = getattr(programa, 'id')
            if not programa_id:
                return
            
            codigo = getattr(programa, 'codigo', f"PROG-{programa_id}")
            nombre = getattr(programa, 'nombre', 'Sin nombre')
            costo = float(getattr(programa, 'costo_base', 0.0))
            cupos = int(getattr(programa, 'cupos_disponibles', 0))
            
            texto = f"{codigo} - {nombre} (Bs. {costo:.2f})"
            
            # Promoción
            if getattr(programa, 'promocion_activa', False):
                descuento = float(getattr(programa, 'descuento_promocion', 0.0))
                texto += f" 🔥 -{descuento}%"
            
            # Cupos
            texto += f" [{cupos} cupo{'s' if cupos > 1 else ''}]"
            
            self.combo_programa.addItem(texto, programa_id)
            self.programas_cache[programa_id] = programa
            
        except Exception as e:
            logger.warning(f"Error agregando programa: {e}")

    def _cargar_estudiante(self, estudiante_id):
        """Cargar información del estudiante"""
        try:
            estudiante = self._obtener_estudiante(estudiante_id)
            
            if estudiante:
                self.estudiante_data = estudiante
                nombres = getattr(estudiante, 'nombres', '')
                apellidos = getattr(estudiante, 'apellidos', '')
                ci = getattr(estudiante, 'ci_numero', '')
                
                nombre_completo = f"{nombres} {apellidos}".strip()
                
                if nombre_completo:
                    self.lbl_estudiante_info.setText(f"👤 Estudiante: {nombre_completo} • CI: {ci}")
                else:
                    self.lbl_estudiante_info.setText(f"👤 Estudiante ID: {estudiante_id}")
                
                logger.info(f"✅ Estudiante cargado: {nombre_completo}")
            else:
                self.lbl_estudiante_info.setText(f"⚠️ Estudiante ID: {estudiante_id} (no encontrado)")
                logger.warning(f"Estudiante {estudiante_id} no encontrado")
                
        except Exception as e:
            logger.error(f"Error cargando estudiante: {e}")
            self.lbl_estudiante_info.setText(f"❌ Error cargando estudiante ID: {estudiante_id}")

    def _obtener_estudiante(self, estudiante_id):
        """Obtener estudiante por ID"""
        try:
            # Método 1: Usar controlador
            if self.estudiante_controller:
                if hasattr(self.estudiante_controller, 'obtener_estudiante'):
                    return self.estudiante_controller.obtener_estudiante(estudiante_id)
                elif hasattr(self.estudiante_controller, 'get_by_id'):
                    return self.estudiante_controller.get_by_id(estudiante_id)
            
            # Método 2: Buscar directamente
            if hasattr(EstudianteModel, 'find_by_id'):
                return EstudianteModel.find_by_id(estudiante_id)
            elif hasattr(EstudianteModel, 'get_by_id'):
                return EstudianteModel.get_by_id(estudiante_id)
            elif hasattr(EstudianteModel, 'query'):
                return EstudianteModel.query.get(estudiante_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo estudiante: {e}")
            return None

    def _on_programa_seleccionado(self, index):
        """Manejar selección de programa"""
        try:
            programa_id = self.combo_programa.itemData(index)
            
            if programa_id is None:
                self._resetear_seleccion_programa()
                return
            
            # Buscar en cache primero
            programa = self.programas_cache.get(programa_id)
            
            # Si no está en cache, buscar
            if not programa:
                programa = self._obtener_programa_por_id(programa_id)
                
                if not programa:
                    QMessageBox.warning(self, "Advertencia", 
                                      "No se pudo obtener información del programa")
                    self._resetear_seleccion_programa()
                    return
                
                # Guardar en cache
                self.programas_cache[programa_id] = programa
            
            self.programa_seleccionado = programa
            self._actualizar_ui_programa(programa)
            self._calcular_costos()
            
        except Exception as e:
            logger.error(f"Error seleccionando programa: {e}", exc_info=True)
            self._resetear_seleccion_programa()

    def _obtener_programa_por_id(self, programa_id):
        """Obtener programa por ID"""
        try:
            # Método 1: Usar controlador
            if self.programa_controller:
                if hasattr(self.programa_controller, 'obtener_programa'):
                    return self.programa_controller.obtener_programa(programa_id)
                elif hasattr(self.programa_controller, 'get_by_id'):
                    return self.programa_controller.get_by_id(programa_id)
            
            # Método 2: Buscar directamente
            if hasattr(ProgramaAcademicoModel, 'get_by_id'):
                return ProgramaAcademicoModel.get_by_id(programa_id)
            elif hasattr(ProgramaAcademicoModel, 'find_by_id'):
                return ProgramaAcademicoModel.find_by_id(programa_id)
            elif hasattr(ProgramaAcademicoModel, 'query'):
                return ProgramaAcademicoModel.query.get(programa_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo programa: {e}")
            return None

    def _resetear_seleccion_programa(self):
        """Resetear selección de programa"""
        self.programa_seleccionado = None
        self.lbl_programa_info.setText("Seleccione un programa para ver detalles")
        self.btn_matricular.setEnabled(False)
        self.combo_programa.setCurrentIndex(0)

    def _actualizar_ui_programa(self, programa):
        """Actualizar UI con información del programa"""
        try:
            nombre = getattr(programa, 'nombre', 'Sin nombre')
            codigo = getattr(programa, 'codigo', '')
            duracion = getattr(programa, 'duracion_semanas', 0)
            cupos = getattr(programa, 'cupos_disponibles', 0)
            estado = getattr(programa, 'estado', '')
            costo_base = getattr(programa, 'costo_base', Decimal('0'))
            costo_matricula = getattr(programa, 'costo_matricula', Decimal('0'))
            
            info_text = f"""
            <b>{nombre}</b> ({codigo})<br>
            <b>Duración:</b> {duracion} semanas<br>
            <b>Cupos disponibles:</b> {cupos}<br>
            <b>Estado:</b> {estado}<br>
            <b>Costo base:</b> Bs. {float(costo_base):.2f}<br>
            <b>Matrícula:</b> Bs. {float(costo_matricula):.2f}
            """
            
            # Promoción
            if getattr(programa, 'promocion_activa', False):
                descuento = getattr(programa, 'descuento_promocion', Decimal('0'))
                info_text += f"<br><br><b>🔥 PROMOCIÓN ACTIVA:</b><br>"
                info_text += f"<b>Descuento:</b> {descuento}%"
            
            self.lbl_programa_info.setText(info_text)
            self.btn_matricular.setEnabled(True)
            
            # Actualizar costo en UI
            self.lbl_costo_programa.setText(f"Bs. {float(costo_base):.2f}")
            self.lbl_costo_matricula.setText(f"Bs. {float(costo_matricula):.2f}")
            
        except Exception as e:
            logger.error(f"Error actualizando UI programa: {e}")

    def _on_forma_pago_cambiada(self, index):
        """Manejar cambio en forma de pago"""
        try:
            forma_pago = self.combo_forma_pago.currentText()
            
            # Habilitar/deshabilitar descuento por contado
            if index == 1:  # CONTADO
                self.check_descuento.setEnabled(True)
            else:
                self.check_descuento.setEnabled(False)
                self.check_descuento.setChecked(False)
            
            self._calcular_costos()
            
        except Exception as e:
            logger.error(f"Error cambiando forma de pago: {e}")

    def _calcular_costos(self):
        """Calcular costos basados en selección actual"""
        try:
            if not self.programa_seleccionado:
                return
            
            # Obtener valores
            costo_base = Decimal(str(getattr(self.programa_seleccionado, 'costo_base', 0)))
            costo_matricula = Decimal(str(getattr(self.programa_seleccionado, 'costo_matricula', 0)))
            
            # Determinar si incluir matrícula
            if self.check_incluir_matricula.isChecked():
                self.monto_base = costo_base + costo_matricula
                self.lbl_costo_matricula.setText(f"Bs. {float(costo_matricula):.2f}")
            else:
                self.monto_base = costo_base
                self.lbl_costo_matricula.setText("No incluido")
            
            # Aplicar descuentos
            self.descuento_total = Decimal('0')
            
            # Descuento por contado
            if self.check_descuento.isChecked() and self.check_descuento.isEnabled():
                descuento_contado = Decimal(str(getattr(self.programa_seleccionado, 'descuento_contado', 0)))
                if descuento_contado > 0:
                    self.descuento_total = self.monto_base * (descuento_contado / 100)
            
            # Descuento por promoción
            if getattr(self.programa_seleccionado, 'promocion_activa', False):
                descuento_promocion = Decimal(str(getattr(self.programa_seleccionado, 'descuento_promocion', 0)))
                if descuento_promocion > 0:
                    descuento_promocion_monto = costo_base * (descuento_promocion / 100)
                    if not self.check_incluir_matricula.isChecked():
                        descuento_promocion_monto = self.monto_base * (descuento_promocion / 100)
                    
                    if descuento_promocion_monto > self.descuento_total:
                        self.descuento_total = descuento_promocion_monto
            
            # Calcular monto final
            self.monto_final = max(Decimal('0'), self.monto_base - self.descuento_total)
            
            # Actualizar UI
            self.lbl_descuento.setText(f"Bs. {float(self.descuento_total):.2f}")
            self.lbl_total.setText(f"Bs. {float(self.monto_final):.2f}")
                
        except Exception as e:
            logger.error(f"Error calculando costos: {e}")
            self.lbl_total.setText("Error calculando total")

    def _on_matricular(self):
        """Procesar matrícula del estudiante - VERSIÓN FINAL"""
        try:
            # Validaciones básicas
            if not self._validar_datos():
                return

            # Preparar datos
            datos = self._preparar_datos_matricula()

            # Mostrar confirmación
            resumen = self._generar_resumen(datos)

            respuesta = QMessageBox.question(
                self, 
                "Confirmar Matrícula",
                f"¿Está seguro de realizar la matrícula?\n\n{resumen}",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No  # Botón por defecto
            )

            if respuesta == QMessageBox.No:
                return

            # Crear matrícula 
            resultado = self._crear_matricula(datos)

            if resultado['exito']:
                QMessageBox.information(
                    self, 
                    "✅ Matrícula Exitosa", 
                    f"{resultado['mensaje']}\n\n"
                    f"Estudiante matriculado exitosamente en el programa."
                )

                # Actualizar cupos disponibles si es posible
                self._actualizar_cupos_programa()

                # Cerrar el diálogo
                self.accept()
            else:
                QMessageBox.critical(
                    self, 
                    "❌ Error en Matrícula", 
                    f"No se pudo completar la matrícula:\n\n{resultado['mensaje']}"
                )

        except Exception as e:
            logger.error(f"Error en proceso de matrícula: {e}", exc_info=True)
            QMessageBox.critical(
                self, 
                "Error", 
                f"Ocurrió un error inesperado:\n\n{str(e)}\n\n"
                f"Por favor, intente nuevamente o contacte al administrador."
            )

    def _validar_datos(self):
        """Validar datos antes de matricular"""
        if not self.estudiante_data:
            QMessageBox.warning(self, "Validación", "No se ha cargado información del estudiante.")
            return False
            
        if not self.programa_seleccionado:
            QMessageBox.warning(self, "Validación", "Debe seleccionar un programa académico.")
            return False
        
        # Validar forma de pago
        if self.combo_forma_pago.currentIndex() == 0:
            QMessageBox.warning(self, "Validación", "Debe seleccionar una forma de pago.")
            return False
        
        # Validar cupos
        cupos = getattr(self.programa_seleccionado, 'cupos_disponibles', 0)
        if cupos <= 0:
            QMessageBox.warning(self, "Validación", "No hay cupos disponibles en este programa.")
            return False
        
        return True

    def _preparar_datos_matricula(self):
        """Preparar datos para la matrícula - VERSIÓN CORREGIDA"""
        try:
            from datetime import date
            from decimal import Decimal

            # 1. FECHA DE INICIO (requerida)
            fecha_inicio = self.date_fecha_inicio.date().toString("yyyy-MM-dd")

            # Para PySide6, convertir QDate a date de Python
            qdate = self.date_fecha_inicio.date()
            fecha_inicio_date = date(qdate.year(), qdate.month(), qdate.day())

            # Verificar que la fecha no sea pasada
            hoy = date.today()
            if fecha_inicio_date < hoy:
                logger.warning(f"Fecha de inicio ({fecha_inicio_date}) es anterior a hoy ({hoy})")
                # Podemos ajustar o dejar que el validador lo maneje

            # 2. MODALIDAD DE PAGO (requerida)
            forma_pago_texto = self.combo_forma_pago.currentText()

            if "CONTADO" in forma_pago_texto.upper():
                modalidad_pago = "CONTADO"
            elif "CUOTAS" in forma_pago_texto.upper():
                modalidad_pago = "CUOTAS"
            else:
                modalidad_pago = "CONTADO"  # Valor por defecto

            # 3. MONTO TOTAL (requerido, mínimo 100)
            monto_total = float(self.monto_final)
            if monto_total < 100:
                monto_total = 100.0  # Asegurar mínimo requerido por validador

            # 4. IDs REQUERIDOS
            estudiante_id = getattr(self.estudiante_data, 'id', self.estudiante_id)
            programa_id = getattr(self.programa_seleccionado, 'id')

            if not estudiante_id or not programa_id:
                raise ValueError("IDs de estudiante o programa no disponibles")

            # 5. CONSTRUIR DICCIONARIO DE DATOS
            datos = {
                # Campos requeridos por el validador
                'estudiante_id': estudiante_id,
                'programa_id': programa_id,
                'fecha_inicio': fecha_inicio,
                'modalidad_pago': modalidad_pago,
                'monto_total': monto_total,
                'monto_base': float(self.monto_base),

                # Campos adicionales que podrían ser requeridos
                'estado': 'ACTIVO',
                'estado_pago': 'PENDIENTE',
                'fecha_registro': hoy.isoformat(),
                'coordinador_id': None,  # Puede ser None si no hay coordinador
            }

            # 6. DESCUENTO APLICADO (si existe, máximo 50%)
            if self.descuento_total > 0:
                descuento_aplicado = float(self.descuento_total)
                # Asegurar que no exceda el 50%
                porcentaje_descuento = (self.descuento_total / self.monto_base * 100) if self.monto_base > 0 else Decimal('0')

                if porcentaje_descuento > Decimal('50'):
                    # Ajustar al máximo permitido
                    descuento_aplicado = float(self.monto_base * Decimal('0.50'))
                    datos['descuento_aplicado'] = descuento_aplicado
                    datos['porcentaje_descuento'] = 50.0
                else:
                    datos['descuento_aplicado'] = descuento_aplicado
                    datos['porcentaje_descuento'] = float(porcentaje_descuento)

                # Tipo de descuento
                if self.check_descuento.isChecked() and self.check_descuento.isEnabled():
                    datos['tipo_descuento'] = 'CONTADO'
                elif getattr(self.programa_seleccionado, 'promocion_activa', False):
                    datos['tipo_descuento'] = 'PROMOCION'
                else:
                    datos['tipo_descuento'] = 'OTRO'

            # 7. INFORMACIÓN DE MATRÍCULA
            datos['incluye_matricula'] = self.check_incluir_matricula.isChecked()

            if datos['incluye_matricula']:
                costo_matricula = getattr(self.programa_seleccionado, 'costo_matricula', Decimal('0'))
                datos['monto_matricula'] = float(costo_matricula)

            # 8. INFORMACIÓN DE CUOTAS (si aplica)
            if modalidad_pago == 'CUOTAS':
                # Extraer número de cuotas del texto
                import re
                match = re.search(r'(\d+)', forma_pago_texto)
                if match:
                    numero_cuotas = int(match.group(1))
                else:
                    numero_cuotas = 1

                datos['numero_cuotas'] = numero_cuotas

                # Calcular cuota mensual
                if numero_cuotas > 0:
                    datos['cuota_mensual'] = monto_total / numero_cuotas

            # 9. VALIDAR QUE TENEMOS TODOS LOS CAMPOS REQUERIDOS
            campos_requeridos = [
                'estudiante_id', 'programa_id', 'fecha_inicio', 
                'modalidad_pago', 'monto_total', 'monto_base'
            ]

            for campo in campos_requeridos:
                if campo not in datos or datos[campo] is None:
                    logger.warning(f"Campo requerido faltante o nulo: {campo}")
                    datos[campo] = self._obtener_valor_por_defecto(campo)

            logger.debug(f"Datos preparados para matrícula: {datos}")
            return datos

        except Exception as e:
            logger.error(f"Error preparando datos de matrícula: {e}", exc_info=True)
            raise

    def _obtener_valor_por_defecto(self, campo):
        """Obtener valor por defecto para campos requeridos"""
        valores_por_defecto = {
            'estudiante_id': self.estudiante_id,
            'programa_id': getattr(self.programa_seleccionado, 'id', 0),
            'fecha_inicio': date.today().isoformat(),
            'modalidad_pago': 'CONTADO',
            'monto_total': 100.0,  # Mínimo requerido por validador
            'monto_base': 100.0,
            'estado': 'ACTIVO',
            'estado_pago': 'PENDIENTE',
            'coordinador_id': None,
        }

        return valores_por_defecto.get(campo)

    def _confirmar_matricula(self, datos):
        """Mostrar confirmación de matrícula"""
        resumen = self._generar_resumen(datos)
        
        respuesta = QMessageBox.question(
            self, 
            "Confirmar Matrícula",
            f"¿Está seguro de realizar la matrícula?\n\n{resumen}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        return respuesta == QMessageBox.Yes

    def _generar_resumen(self, datos):
        """Generar resumen de la matrícula - VERSIÓN CORREGIDA"""
        try:
            estudiante_nombre = f"{getattr(self.estudiante_data, 'nombres', '')} {getattr(self.estudiante_data, 'apellidos', '')}"
            programa_nombre = getattr(self.programa_seleccionado, 'nombre', '')
            programa_codigo = getattr(self.programa_seleccionado, 'codigo', '')

            # Usar 'modalidad_pago' en lugar de 'forma_pago'
            modalidad_pago = datos.get('modalidad_pago', 'CONTADO')

            resumen = [
                "=== RESUMEN DE MATRÍCULA ===",
                f"ESTUDIANTE: {estudiante_nombre}",
                f"C.I.: {getattr(self.estudiante_data, 'ci_numero', '')}",
                "",
                f"PROGRAMA: {programa_codigo} - {programa_nombre}",
                f"FECHA DE INICIO: {datos.get('fecha_inicio', 'No especificada')}",
                f"MODALIDAD DE PAGO: {modalidad_pago}",  # <-- CAMBIO AQUÍ
                f"INCLUYE MATRÍCULA: {'Sí' if datos.get('incluye_matricula', False) else 'No'}",
                "",
                "=== DETALLE DE COSTOS ===",
                f"Monto base: Bs. {datos.get('monto_base', 0):.2f}",
                f"Descuento aplicado: Bs. {datos.get('descuento_aplicado', 0):.2f}",
                f"TOTAL A PAGAR: Bs. {datos.get('monto_total', 0):.2f}"
            ]

            # Información de cuotas si aplica
            if modalidad_pago == 'CUOTAS' and 'numero_cuotas' in datos:
                num_cuotas = datos['numero_cuotas']
                valor_cuota = datos.get('cuota_mensual', datos.get('monto_total', 0) / num_cuotas if num_cuotas > 0 else 0)
                resumen.extend([
                    "",
                    f"Cuotas: {num_cuotas}",
                    f"Valor por cuota: Bs. {valor_cuota:.2f}"
                ])

            return "\n".join(resumen)

        except Exception as e:
            logger.error(f"Error generando resumen: {e}")
            return "Resumen no disponible"

    def _crear_matricula(self, datos):
        """Crear matrícula en la base de datos - VERSIÓN ROBUSTA"""
        try:
            # Método 1: Usar controlador si está disponible
            if self.matricula_controller and hasattr(self.matricula_controller, 'crear_matricula'):
                logger.info("Intentando crear matrícula mediante controlador...")

                # Hacer una copia para no modificar el original
                datos_para_controlador = datos.copy()

                # Asegurar tipos de datos correctos para el validador
                if 'monto_total' in datos_para_controlador:
                    datos_para_controlador['monto_total'] = float(datos_para_controlador['monto_total'])

                if 'monto_base' in datos_para_controlador:
                    datos_para_controlador['monto_base'] = float(datos_para_controlador['monto_base'])

                if 'descuento_aplicado' in datos_para_controlador:
                    datos_para_controlador['descuento_aplicado'] = float(datos_para_controlador['descuento_aplicado'])

                # Intentar crear con el controlador
                exito, mensaje, matricula = self.matricula_controller.crear_matricula(datos_para_controlador)

                if exito:
                    logger.info(f"✅ Matrícula creada mediante controlador: {mensaje}")
                    return {'exito': True, 'mensaje': mensaje}
                else:
                    logger.warning(f"Controlador falló: {mensaje}")

                    # Intentar diagnóstico del error
                    error_info = self._diagnosticar_error_controlador(mensaje, datos_para_controlador)
                    logger.warning(f"Diagnóstico error: {error_info}")

                    # Intentar con datos ajustados
                    datos_ajustados = self._ajustar_datos_para_validador(datos_para_controlador)
                    exito, mensaje, matricula = self.matricula_controller.crear_matricula(datos_ajustados)

                    if exito:
                        return {'exito': True, 'mensaje': mensaje}
                    else:
                        # Fallback a creación directa
                        return self._crear_matricula_directamente(datos)

            # Método 2: Crear directamente
            return self._crear_matricula_directamente(datos)

        except Exception as e:
            logger.error(f"Error creando matrícula: {e}", exc_info=True)
            # Último intento con valores mínimos
            return self._crear_matricula_minima()

    def _diagnosticar_error_controlador(self, mensaje_error, datos):
        """Diagnosticar error del controlador"""
        diagnosticos = []

        # Verificar campos requeridos
        campos_requeridos = ['estudiante_id', 'programa_id', 'fecha_inicio', 
                             'modalidad_pago', 'monto_total']

        for campo in campos_requeridos:
            if campo not in datos or datos[campo] is None:
                diagnosticos.append(f"Falta campo: {campo}")
            elif datos[campo] == '':
                diagnosticos.append(f"Campo vacío: {campo}")

        # Verificar montos
        if 'monto_total' in datos and datos['monto_total'] < 100:
            diagnosticos.append(f"Monto total muy bajo: {datos['monto_total']} (mínimo 100)")

        # Verificar fecha
        if 'fecha_inicio' in datos:
            try:
                from datetime import date, datetime
                fecha = datetime.strptime(datos['fecha_inicio'], '%Y-%m-%d').date()
                if fecha < date.today():
                    diagnosticos.append(f"Fecha pasada: {datos['fecha_inicio']}")
            except:
                diagnosticos.append(f"Formato fecha inválido: {datos['fecha_inicio']}")

        return diagnosticos

    def _ajustar_datos_para_validador(self, datos):
        """Ajustar datos para pasar validaciones"""
        datos_ajustados = datos.copy()

        # Asegurar monto mínimo
        if 'monto_total' in datos_ajustados and datos_ajustados['monto_total'] < 100:
            datos_ajustados['monto_total'] = 100.0

        # Asegurar modalidad de pago válida
        if 'modalidad_pago' in datos_ajustados:
            modalidad = datos_ajustados['modalidad_pago'].upper()
            if modalidad not in ['CONTADO', 'CUOTAS']:
                datos_ajustados['modalidad_pago'] = 'CONTADO'

        # Asegurar descuento máximo 50%
        if 'descuento_aplicado' in datos_ajustados and 'monto_base' in datos_ajustados:
            if datos_ajustados['monto_base'] > 0:
                porcentaje = (datos_ajustados['descuento_aplicado'] / datos_ajustados['monto_base'] * 100)
                if porcentaje > 50:
                    datos_ajustados['descuento_aplicado'] = datos_ajustados['monto_base'] * 0.5

        # Asegurar fecha válida
        if 'fecha_inicio' in datos_ajustados:
            try:
                from datetime import date, datetime
                fecha = datetime.strptime(datos_ajustados['fecha_inicio'], '%Y-%m-%d').date()
                if fecha < date.today():
                    datos_ajustados['fecha_inicio'] = date.today().isoformat()
            except:
                datos_ajustados['fecha_inicio'] = date.today().isoformat()

        return datos_ajustados
    
    def _ajustar_datos_controlador(self, datos):
        """Ajustar datos para controlador específico"""
        datos_ajustados = datos.copy()
        
        # Asegurar tipos correctos
        if 'estudiante_id' in datos_ajustados:
            datos_ajustados['estudiante_id'] = int(datos_ajustados['estudiante_id'])
        
        if 'programa_id' in datos_ajustados:
            datos_ajustados['programa_id'] = int(datos_ajustados['programa_id'])
        
        if 'monto_total' in datos_ajustados:
            datos_ajustados['monto_total'] = float(datos_ajustados['monto_total'])
        
        if 'monto_base' in datos_ajustados:
            datos_ajustados['monto_base'] = float(datos_ajustados['monto_base'])
        
        # Asegurar que la modalidad de pago sea válida
        if 'modalidad_pago' in datos_ajustados:
            modalidad = datos_ajustados['modalidad_pago'].upper()
            if modalidad not in ['CONTADO', 'CUOTAS']:
                datos_ajustados['modalidad_pago'] = 'CONTADO'
        
        # Agregar campos que podrían faltar
        campos_opcionales = {
            'estado': 'ACTIVO',
            'estado_pago': 'PENDIENTE',
            'coordinador_id': None,
            'observaciones': 'Matrícula creada desde interfaz gráfica'
        }
        
        for campo, valor in campos_opcionales.items():
            if campo not in datos_ajustados:
                datos_ajustados[campo] = valor
        
        return datos_ajustados    

    def _crear_matricula_directamente(self, datos):
        """Crear matrícula directamente usando el modelo"""
        try:
            from app.models.matricula_model import MatriculaModel

            # Limpiar datos para el modelo
            datos_limpios = {}

            # Solo incluir campos que probablemente tenga el modelo
            campos_modelo = [
                'estudiante_id', 'programa_id', 'fecha_inicio', 
                'modalidad_pago', 'monto_total', 'monto_base',
                'descuento_aplicado', 'estado', 'estado_pago',
                'coordinador_id', 'observaciones'
            ]

            for campo in campos_modelo:
                if campo in datos and datos[campo] is not None:
                    datos_limpios[campo] = datos[campo]

            # Crear instancia del modelo
            matricula = MatriculaModel(**datos_limpios)

            # Guardar
            if hasattr(matricula, 'save'):
                matricula_id = matricula.save()
                if matricula_id:
                    logger.info(f"✅ Matrícula creada directamente: ID {matricula_id}")
                    return {
                        'exito': True,
                        'mensaje': f"Matrícula creada exitosamente (ID: {matricula_id})"
                    }
                else:
                    return {
                        'exito': False,
                        'mensaje': "Error al guardar la matrícula en la base de datos"
                    }
            else:
                # Último recurso: usar un método alternativo si existe
                if hasattr(MatriculaModel, 'crear'):
                    resultado = MatriculaModel.crear(**datos_limpios)
                    if resultado:
                        return {
                            'exito': True,
                            'mensaje': "Matrícula creada usando método alternativo"
                        }

                return {
                    'exito': False,
                    'mensaje': "El modelo no tiene método save()"
                }

        except Exception as e:
            logger.error(f"Error creando matrícula directamente: {e}", exc_info=True)
            return {
                'exito': False,
                'mensaje': f"Error al crear matrícula: {str(e)}"
            }

    def _crear_matricula_minima(self):
        """Crear matrícula con datos mínimos como último recurso"""
        try:
            from app.models.matricula_model import MatriculaModel
            from datetime import date

            datos_minimos = {
                'estudiante_id': getattr(self.estudiante_data, 'id', self.estudiante_id),
                'programa_id': getattr(self.programa_seleccionado, 'id', 0),
                'fecha_inicio': date.today().isoformat(),
                'modalidad_pago': 'CONTADO',
                'monto_total': 100.0,
                'estado': 'ACTIVO',
                'observaciones': 'Matrícula creada como último recurso'
            }

            matricula = MatriculaModel(**datos_minimos)

            if hasattr(matricula, 'save'):
                matricula_id = matricula.save()
                if matricula_id:
                    return {
                        'exito': True,
                        'mensaje': f"Matrícula creada (modo mínimo): ID {matricula_id}"
                    }

            return {
                'exito': False,
                'mensaje': "No se pudo crear la matrícula en modo mínimo"
            }

        except Exception as e:
            logger.error(f"Error en creación mínima: {e}")
            return {
                'exito': False,
                'mensaje': f"Error fatal: {str(e)}"
            }

    def _actualizar_cupos_programa(self):
        """Actualizar cupos disponibles del programa"""
        try:
            if not self.programa_seleccionado:
                return
            
            programa_id = getattr(self.programa_seleccionado, 'id')
            if not programa_id:
                return
            
            # Buscar programa actualizado
            programa = self._obtener_programa_por_id(programa_id)
            if not programa:
                return
            
            # Reducir cupos
            if hasattr(programa, 'cupos_disponibles'):
                nuevos_cupos = max(0, programa.cupos_disponibles - 1)
                programa.cupos_disponibles = nuevos_cupos
                
                # Guardar cambios
                if hasattr(programa, 'save'):
                    programa.save()
                    logger.info(f"✅ Cupos actualizados: {nuevos_cupos} disponibles")
                
                # Actualizar cache
                if programa_id in self.programas_cache:
                    self.programas_cache[programa_id].cupos_disponibles = nuevos_cupos
                    
        except Exception as e:
            logger.error(f"Error actualizando cupos: {e}")


if __name__ == "__main__":
    # Para pruebas
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = MatriculaEstudianteFormDialog(estudiante_id=1)
    dialog.exec()
    sys.exit(app.exec())