# app/views/tabs/estudiantes_tab.py
"""
Pestaña de Estudiantes - Versión completa con búsqueda, tabla paginada y funcionalidades CRUD
"""
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QProgressDialog,
    QToolButton, QFrame, QSizePolicy, QSpacerItem, QTextEdit, 
    QDialog, QFormLayout
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QSize
from PySide6.QtGui import QColor, QFont, QIcon

# Importa solo los modelos necesarios
from app.models.estudiante_model import EstudianteModel
from app.models.matricula_model import MatriculaModel
from app.models.programa_academico_model import ProgramaAcademicoModel
from app.models.pago_model import PagoModel
from database import db, Database
from datetime import datetime
import os
import sys
from pathlib import Path

try:
    from app.views.dialogs.estudiante_form_dialog import EstudianteFormDialog
except ImportError as e:
    print(f"⚠️ Error importando EstudianteFormDialog: {e}")
    # Definir placeholder si no existe
    class EstudianteFormDialog:
        estudiante_guardado = None
        estudiante_inscribir = None
        estudiante_borrar = None
        
        def __init__(self, *args, **kwargs):
            pass

try:
    from app.views.generated.dialogs.ui_matricular_estudiante_dialog import Ui_MatricularEstudianteDialog
except ImportError as e:
    print(f"⚠️ Advertencia: No se pudo importar diálogos: {e}")
    # Definir placeholders
    class Ui_MatricularEstudianteDialog:
        pass
    EstudianteFormDialog = None

logger = logging.getLogger(__name__)

# Agregar el directorio raíz al path de Python
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

#################################
# PESTAÑA PRINCIPAL ESTUDIANTES #
#################################
class EstudiantesTab(QWidget):
    """Pestaña principal de gestión de estudiantes - Versión simplificada usando controlador"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configuración inicial
        self.current_page = 1
        self.records_per_page = 25
        self.total_records = 0
        self.total_pages = 1
        self.current_filter = None
        self.estudiantes_cache = []
        
        # Referencia al controlador de estudiantes
        self.estudiante_controller = None
        
        self.setup_ui()
        self.setup_connections()
        self.cargar_estudiantes_inicial()
    
    def setup_ui(self):
        """Configurar interfaz - Versión simplificada"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # ==================== SECCIÓN DE BÚSQUEDA ====================
        search_group = QGroupBox("🔍 Buscar Estudiantes")
        search_group.setStyleSheet("""
            QGroupBox {
               color: #2c3e50;
            }
        """)
        search_layout = QGridLayout()
        
        # Búsqueda por CI
        label_ci = QLabel("Buscar por CI:")
        label_ci.setStyleSheet("color: black; font-weight: bold;")
        search_layout.addWidget(label_ci, 0, 0)
        self.txtBuscarCI = QLineEdit()
        self.txtBuscarCI.setPlaceholderText("Ingrese número de CI")
        self.txtBuscarCI.setStyleSheet("color: #212121; background-color: #FFFFFF;")
        search_layout.addWidget(self.txtBuscarCI, 0, 1)
        
        self.comboExpedicion = QComboBox()
        self.comboExpedicion.addItems(["Todas", "BE", "CH", "CB", "LP", "OR", "PD", "PT", "SC", "TJ", "EX"])
        search_layout.addWidget(self.comboExpedicion, 0, 2)
        
        self.btnBuscarCI = QPushButton("🔍 Buscar por CI")
        self.btnBuscarCI.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        search_layout.addWidget(self.btnBuscarCI, 0, 3)
        
        # Búsqueda por nombre
        label_nombres_o_apellidos = QLabel("Buscar por Nombres o Apellidos:")
        label_nombres_o_apellidos.setStyleSheet("color: black; font-weight: bold;")
        search_layout.addWidget(label_nombres_o_apellidos, 1, 0)
        self.txtBuscarNombre = QLineEdit()
        self.txtBuscarNombre.setStyleSheet("color: #212121; background-color: #FFFFFF;")
        self.txtBuscarNombre.setPlaceholderText("Ingrese nombre o apellido")
        search_layout.addWidget(self.txtBuscarNombre, 1, 1, 1, 2)
        
        self.btnBuscarNombre = QPushButton("👤 Buscar por nombre")
        self.btnBuscarNombre.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        search_layout.addWidget(self.btnBuscarNombre, 1, 3)
        
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)
        
        # ==================== BOTONES DE ACCIÓN ====================
        action_layout = QHBoxLayout()
        
        self.btnNuevo = QPushButton("➕ Nuevo Estudiante")
        self.btnNuevo.setIcon(QIcon(":/icons/add.png") if hasattr(QIcon, "fromTheme") else QIcon())
        self.btnNuevo.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        
        #self.btnMostrarTodos = QPushButton("📋 Mostrar Todos")
        #self.btnMostrarTodos.setStyleSheet("""
        #    QPushButton {
        #        background-color: #7f8c8d;
        #        color: white;
        #        padding: 8px 15px;
        #        border-radius: 4px;
        #    }
        #    QPushButton:hover {
        #        background-color: #95a5a6;
        #    }
        #""")
        #
        #self.btnAbrirGestorCompleto = QPushButton("📊 Abrir Gestor Completo")
        #self.btnAbrirGestorCompleto.setStyleSheet("""
        #    QPushButton {
        #        background-color: #9b59b6;
        #        color: white;
        #        padding: 8px 15px;
        #        border-radius: 4px;
        #    }
        #    QPushButton:hover {
        #        background-color: #8e44ad;
        #    }
        #""")
        
        action_layout.addWidget(self.btnNuevo)
        #action_layout.addWidget(self.btnMostrarTodos)
        #action_layout.addWidget(self.btnAbrirGestorCompleto)
        action_layout.addStretch()
        
        main_layout.addLayout(action_layout)
        
        # ==================== TABLA DE ESTUDIANTES ====================
        self.tableEstudiantes = QTableWidget()
        self.tableEstudiantes.setColumnCount(9)  # Reducido a 9 columnas
        self.tableEstudiantes.setHorizontalHeaderLabels([
            "ID", "CI", "Nombre Completo", "Email", "Teléfono", 
            "Universidad", "Profesión", "Estado", "Acciones"
        ])
        
        # Configurar tabla
        header = self.tableEstudiantes.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # CI
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Nombre
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Email
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Teléfono
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Universidad
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Profesión
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Estado
        header.setSectionResizeMode(8, QHeaderView.Stretch)           # Acciones
        self.tableEstudiantes.setColumnWidth(10, 300)  # Más pequeño
        
        # Estilo de la tabla
        self.tableEstudiantes.setAlternatingRowColors(True)
        self.tableEstudiantes.setStyleSheet("""
            QTableWidget {
                background-color: #fbfbfb;
                color: #212121;
                border-color: #E0E0E0;
                alternate-background-color: #F8F8F8;
                selection-background-color: #1976D2;
                selection-color: #FFFFFF;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        main_layout.addWidget(self.tableEstudiantes)
        
        # ==================== PAGINACIÓN ====================
        pagination_layout = QHBoxLayout()
        
        # Controles de registros por página
        pagination_layout.addWidget(QLabel("Mostrar:"))
        self.comboRegistrosPagina = QComboBox()
        self.comboRegistrosPagina.addItems(["10", "25", "50", "100", "Todos"])
        self.comboRegistrosPagina.setCurrentText("25")
        pagination_layout.addWidget(self.comboRegistrosPagina)
        
        pagination_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Botones de paginación
        self.btnPrimera = QPushButton("⏮️ Primera")
        self.btnAnterior = QPushButton("◀️ Anterior")
        self.btnSiguiente = QPushButton("Siguiente ▶️")
        self.btnUltima = QPushButton("Última ⏭️")
        
        for btn in [self.btnPrimera, self.btnAnterior, self.btnSiguiente, self.btnUltima]:
            btn.setFixedSize(100, 30)
            pagination_layout.addWidget(btn)
        
        # Etiquetas de paginación
        self.lblPaginaInfo = QLabel("Página 0 de 0")
        self.lblContador = QLabel("Mostrando 0-0 de 0 estudiantes")
        pagination_layout.addWidget(self.lblPaginaInfo)
        pagination_layout.addWidget(self.lblContador)
        
        main_layout.addLayout(pagination_layout)
        
        # ==================== BARRA DE ESTADO ====================
        self.statusBar = QLabel("Sistema de gestión de estudiantes listo")
        self.statusBar.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")
        main_layout.addWidget(self.statusBar)
    
    def setup_connections(self):
        """Conectar todas las señales usando métodos del controlador"""
        # Botones de búsqueda
        self.btnBuscarCI.clicked.connect(self.buscar_por_ci_simple)
        self.btnBuscarNombre.clicked.connect(self.buscar_por_nombre_simple)
        #self.btnMostrarTodos.clicked.connect(self.mostrar_todos)
        self.btnNuevo.clicked.connect(self.nuevo_estudiante)
        #self.btnAbrirGestorCompleto.clicked.connect(self.abrir_gestor_completo)
        
        # Buscar con Enter
        self.txtBuscarCI.returnPressed.connect(self.buscar_por_ci_simple)
        self.txtBuscarNombre.returnPressed.connect(self.buscar_por_nombre_simple)
        
        # Paginación
        self.btnPrimera.clicked.connect(lambda: self.cambiar_pagina(1))
        self.btnAnterior.clicked.connect(self.pagina_anterior)
        self.btnSiguiente.clicked.connect(self.pagina_siguiente)
        self.btnUltima.clicked.connect(self.ultima_pagina)
        self.comboRegistrosPagina.currentTextChanged.connect(self.cambiar_registros_pagina)
        
        # Doble click en tabla para abrir detalles
        self.tableEstudiantes.doubleClicked.connect(self.on_doble_click_tabla)
    
    def abrir_gestor_completo(self):
        """Abrir gestor completo de estudiantes"""
        try:
            from app.views.dialogs.estudiante_form_dialog import EstudianteFormDialog

            dialog = EstudianteFormDialog(parent=self)
            dialog.estudiante_guardado.connect(self.cargar_estudiantes)
            dialog.exec()

        except ImportError as e:
            print(f'Error importando EstudianteFormDialog: {e}')
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, 'Error', f'No se pudo abrir el gestor: {e}')
        except Exception as e:
            print(f'Error abriendo gestor completo: {e}')
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, 'Error', f'Error al abrir gestor: {e}')

    # ==================== MÉTODOS SIMPLIFICADOS QUE USAN EL CONTROLADOR ====================
    
    def cargar_estudiantes_inicial(self):
        """Cargar estudiantes al iniciar"""
        QTimer.singleShot(100, self.mostrar_todos)
    
    def cargar_estudiantes(self, filtro=None):
        """Cargar estudiantes con paginación - Versión corregida"""
        try:
            # Limpiar tabla
            self.tableEstudiantes.setRowCount(0)
            
            # Obtener estudiantes según filtro
            estudiantes = []
            
            if filtro is None:
                # Mostrar todos los activos
                estudiantes = EstudianteModel.buscar_activos()
            elif 'ci_numero' in filtro:
                # Buscar por CI
                expedicion = filtro.get('ci_expedicion', 'Todas')
                if expedicion != 'Todas':
                    # Buscar por CI específico
                    estudiante = EstudianteModel.buscar_por_ci(
                        filtro['ci_numero'], 
                        expedicion
                    )
                    if estudiante:
                        estudiantes = [estudiante]
                else:
                    # Buscar solo por número de CI
                    # Necesitarías un método buscar_por_ci_numero
                    # Por ahora, filtrar de todos
                    todos = EstudianteModel.buscar_activos()
                    estudiantes = [
                        e for e in todos 
                        if filtro['ci_numero'] in e.ci_numero
                    ]
            elif 'nombre' in filtro:
                # Buscar por nombre
                estudiantes = EstudianteModel.buscar_por_nombre(filtro['nombre'])
            
            self.estudiantes_cache = estudiantes
            self.total_records = len(estudiantes)
            
            if not estudiantes:
                # Mostrar mensaje de "sin datos"
                self.tableEstudiantes.setRowCount(1)
                item = QTableWidgetItem("No se encontraron estudiantes")
                item.setTextAlignment(Qt.AlignCenter)
                item.setForeground(QColor("#7f8c8d"))
                self.tableEstudiantes.setItem(0, 0, item)
                self.tableEstudiantes.setSpan(0, 0, 1, 9)
            else:
                # Llenar tabla
                for i, estudiante in enumerate(estudiantes):
                    self.tableEstudiantes.insertRow(i)
                    self.tableEstudiantes.setRowHeight(i, 40)
                    
                    # Datos básicos
                    self.tableEstudiantes.setItem(i, 0, QTableWidgetItem(str(estudiante.id)))
                    self.tableEstudiantes.setItem(i, 1, QTableWidgetItem(
                        f"{estudiante.ci_numero}-{estudiante.ci_expedicion}"))
                    self.tableEstudiantes.setItem(i, 2, QTableWidgetItem(estudiante.nombre_completo))
                    self.tableEstudiantes.setItem(i, 3, QTableWidgetItem(estudiante.email or ""))
                    self.tableEstudiantes.setItem(i, 4, QTableWidgetItem(estudiante.telefono or ""))
                    self.tableEstudiantes.setItem(i, 5, QTableWidgetItem(estudiante.universidad_egreso or ""))
                    self.tableEstudiantes.setItem(i, 6, QTableWidgetItem(estudiante.profesion or ""))
                    
                    # Estado
                    estado = QTableWidgetItem("✅ Activo" if estudiante.activo else "❌ Inactivo")
                    estado.setForeground(QColor("#27ae60") if estudiante.activo else QColor("#e74c3c"))
                    estado.setTextAlignment(Qt.AlignCenter)
                    self.tableEstudiantes.setItem(i, 7, estado)
                    
                    # Acciones
                    acciones_widget = self.crear_widget_acciones(estudiante)
                    self.tableEstudiantes.setCellWidget(i, 8, acciones_widget)
            
            # Actualizar controles
            self.actualizar_controles_paginacion()
            self.actualizar_contador()
            
            self.statusBar.setText(f"Cargados {len(estudiantes)} estudiantes")
            
        except Exception as e:
            self.statusBar.setText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error cargando estudiantes: {str(e)}")
            logger.error(f"Error en cargar_estudiantes: {e}")
    
    def crear_widget_acciones(self, estudiante):
        """Crear widget con botones de acciones completas"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        # Botón 1: Ver Detalles (solo lectura)
        btn_detalles = QPushButton("👁️")
        btn_detalles.setIconSize(QSize(28, 28))
        btn_detalles.setToolTip("Ver detalles del estudiante (solo lectura)")
        btn_detalles.setFixedSize(40, 28)
        btn_detalles.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 3px;
                border: none;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
        """)
        btn_detalles.clicked.connect(lambda: self.ver_detalles_estudiante(estudiante))

        # Botón 2: Editar
        btn_editar = QPushButton("✏️")
        btn_editar.setToolTip("Editar estudiante")
        btn_editar.setFixedSize(40, 28)
        btn_editar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 3px;
                border: none;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        btn_editar.clicked.connect(lambda: self.editar_estudiante(estudiante))

        # Botón 3: Matricular en programa
        btn_matricular = QPushButton("🎓")
        btn_matricular.setToolTip("Matricular en programa académico")
        btn_matricular.setFixedSize(40, 28)
        btn_matricular.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border-radius: 3px;
                border: none;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:pressed {
                background-color: #7d3c98;
            }
        """)
        btn_matricular.clicked.connect(lambda: self.matricular_estudiante(estudiante))

        # Botón 4: Historial de programas
        btn_programas = QPushButton("📚")
        btn_programas.setToolTip("Ver historial de programas académicos")
        btn_programas.setFixedSize(40, 28)
        btn_programas.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border-radius: 3px;
                border: none;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #d35400;
            }
        """)
        btn_programas.clicked.connect(lambda: self.ver_programas_academicos(estudiante))

        # Botón 5: Seguimiento de pagos
        btn_pagos = QPushButton("💰")
        btn_pagos.setToolTip("Seguimiento de pagos y cuotas")
        btn_pagos.setFixedSize(40, 28)
        btn_pagos.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 3px;
                border: none;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
        """)
        btn_pagos.clicked.connect(lambda: self.seguimiento_pagos(estudiante))

        # Botón 6: Eliminar
        btn_eliminar = QPushButton("🗑️")
        btn_eliminar.setToolTip("Eliminar estudiante")
        btn_eliminar.setFixedSize(40, 28)
        btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 3px;
                border: none;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        btn_eliminar.clicked.connect(lambda: self.eliminar_estudiante(estudiante))

        # Agregar todos los botones al layout
        layout.addWidget(btn_detalles)
        layout.addWidget(btn_editar)
        layout.addWidget(btn_matricular)
        layout.addWidget(btn_programas)
        layout.addWidget(btn_pagos)
        layout.addWidget(btn_eliminar)
        layout.addStretch()

        return widget
    
    # ==================== MÉTODOS DE BÚSQUEDA SIMPLIFICADOS ====================
    
    def buscar_por_ci_simple(self):
        """Buscar estudiante por CI - Versión simplificada"""
        ci_numero = self.txtBuscarCI.text().strip()
        expedicion = self.comboExpedicion.currentText()
        
        if not ci_numero:
            QMessageBox.warning(self, "Advertencia", "Ingrese un número de CI para buscar")
            return
        
        self.current_filter = {'ci_numero': ci_numero}
        if expedicion != "Todas":
            self.current_filter['ci_expedicion'] = expedicion
        
        self.current_page = 1
        self.cargar_estudiantes(self.current_filter)
        self.statusBar.setText(f"Búsqueda por CI: {ci_numero}-{expedicion}")
    
    def buscar_por_nombre_simple(self):
        """Buscar estudiante por nombre - Versión simplificada"""
        texto = self.txtBuscarNombre.text().strip()
        
        if not texto:
            QMessageBox.warning(self, "Advertencia", "Ingrese un nombre o apellido para buscar")
            return
        
        self.current_filter = {'nombre': texto}
        self.current_page = 1
        self.cargar_estudiantes(self.current_filter)
        self.statusBar.setText(f"Búsqueda por nombre: {texto}")
    
    def mostrar_todos(self):
        """Mostrar todos los estudiantes"""
        self.txtBuscarCI.clear()
        self.txtBuscarNombre.clear()
        self.comboExpedicion.setCurrentIndex(0)
        
        self.current_filter = None
        self.current_page = 1
        self.cargar_estudiantes()
        self.statusBar.setText("Mostrando todos los estudiantes")
    
    # ==================== MÉTODOS CRUD QUE USAN EL CONTROLADOR ====================
    
    def nuevo_estudiante(self):
        """Abrir formulario para nuevo estudiante usando el controlador"""
        dialog = EstudianteFormDialog(parent=self)
        dialog.estudiante_guardado.connect(self.on_estudiante_guardado)
        dialog.exec()
    
    def ver_detalles_estudiante(self, estudiante):
        """Mostrar diálogo con detalles del estudiante (solo lectura)"""
        try:
            print(f"DEBUG ver_detalles_estudiante: Abriendo diálogo para estudiante")
            
            # Obtener ID del estudiante
            if hasattr(estudiante, 'id'):
                estudiante_id = estudiante.id
            else:
                estudiante_id = estudiante
            
            print(f"DEBUG: Usando ID {estudiante_id}")
            
            from app.views.dialogs.estudiante_form_dialog import EstudianteFormDialog
            from app.models.estudiante_model import EstudianteModel
            
            # Obtener datos frescos desde BD
            estudiante_bd = EstudianteModel.find_by_id(estudiante_id)
            if not estudiante_bd:
                QMessageBox.warning(self, "Error", "Estudiante no encontrado")
                return
            
            # Crear diccionario con datos
            estudiante_data = {
                'id': estudiante_bd.id,
                'ci_numero': estudiante_bd.ci_numero,
                'ci_expedicion': estudiante_bd.ci_expedicion,
                'nombres': estudiante_bd.nombres,
                'apellidos': estudiante_bd.apellidos,
                'fecha_nacimiento': estudiante_bd.fecha_nacimiento,
                'telefono': getattr(estudiante_bd, 'telefono', ''),
                'email': getattr(estudiante_bd, 'email', ''),
                'universidad_egreso': getattr(estudiante_bd, 'universidad_egreso', ''),
                'profesion': getattr(estudiante_bd, 'profesion', ''),
                'fotografia_path': getattr(estudiante_bd, 'fotografia_path', None),
                'activo': getattr(estudiante_bd, 'activo', 1)
            }
            
            # Abrir diálogo en modo lectura
            dialog = EstudianteFormDialog(
                estudiante_data=estudiante_data,
                modo_lectura=True,
                parent=self
            )
            
            # Conectar señales
            dialog.estudiante_editar.connect(lambda data: self.editar_estudiante(data['id']))
            dialog.estudiante_inscribir.connect(self.on_inscribir_desde_detalles)
            dialog.estudiante_borrar.connect(self.on_borrar_desde_detalles)
            
            dialog.exec()
            
        except Exception as e:
            print(f"ERROR en ver_detalles_estudiante: {e}")
            logger.error(f"Error en ver_detalles_estudiante: {e}")
            QMessageBox.critical(self, "Error", f"Error al mostrar detalles: {str(e)}")
            print(f"ERROR en ver_detalles_estudiante: {e}")
            logger.error(f"Error en ver_detalles_estudiante: {e}")
            QMessageBox.critical(self, "Error", f"Error al mostrar detalles: {str(e)}")

    def editar_estudiante(self, estudiante):
        """Abrir diálogo para editar un estudiante"""
        try:
            print(f"DEBUG editar_estudiante: Abriendo diálogo para estudiante")

            # Asegurarnos de que tenemos el ID
            if hasattr(estudiante, 'id'):
                estudiante_id = estudiante.id
            elif isinstance(estudiante, dict) and 'id' in estudiante:
                estudiante_id = estudiante['id']
            else:
                estudiante_id = estudiante  # Asumir que ya es un ID

            print(f"DEBUG: Usando ID {estudiante_id}")

            from app.views.dialogs.estudiante_form_dialog import EstudianteFormDialog

            # Abrir diálogo en modo edición
            dialog = EstudianteFormDialog(
                estudiante_id=estudiante_id,  # Solo pasamos el ID
                modo_lectura=False,           # Modo edición
                parent=self
            )

            # Conectar señales
            dialog.estudiante_mostrar_detalles.connect(self.mostrar_estudiante_en_modo_lectura)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                print(f"DEBUG editar_estudiante - Diálogo cerrado")
                self.cargar_estudiantes()

        except Exception as e:
            logger.error(f"Error al editar estudiante: {e}")
            print(f"ERROR detallado: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Error al editar estudiante: {str(e)}")
    
    def on_doble_click_tabla(self, index):
        """Manejar doble click en la tabla"""
        row = index.row()
        if row < len(self.estudiantes_cache):
            self.editar_estudiante(self.estudiantes_cache[row])
    
    def on_estudiante_guardado(self, datos):
        """Manejador cuando se guarda un estudiante - Abre diálogo de detalles"""
        try:
            # Determinar si es creación o edición
            es_nuevo = 'id' not in datos
            
            print(f"DEBUG on_estudiante_guardado:")
            print(f"  - Es nuevo: {es_nuevo}")
            print(f"  - Datos recibidos: {datos}")
            print(f"  - fotografia_path en datos: {datos.get('fotografia_path')}")
            
            try:
                if es_nuevo:
                    # CREAR NUEVO ESTUDIANTE
                    from app.models.estudiante_model import EstudianteModel
                    
                    # Asegurar que fotografia_path esté incluido
                    datos_creacion = datos.copy()
                    
                    # Si no hay fotografia_path, establecer como None explícitamente
                    if 'fotografia_path' not in datos_creacion:
                        datos_creacion['fotografia_path'] = None
                    
                    print(f"  - Creando estudiante con datos: {datos_creacion}")
                    
                    estudiante_creado = EstudianteModel.crear_estudiante(datos_creacion)
                    
                    # Guardar el ID en los datos
                    datos['id'] = estudiante_creado.id
                    
                    # Obtener el objeto completo del estudiante creado
                    estudiante = estudiante_creado
                    mensaje_titulo = "✅ Estudiante Creado"
                    mensaje_texto = "Estudiante creado exitosamente"
                    
                    print(f"  - ✅ Estudiante creado ID: {estudiante.id}")
                    print(f"  - fotografia_path guardado: {getattr(estudiante, 'fotografia_path', 'No tiene')}")
                    
                else:
                    # ACTUALIZAR ESTUDIANTE EXISTENTE
                    from app.models.estudiante_model import EstudianteModel
                    estudiante = EstudianteModel.find_by_id(datos['id'])
                    
                    if estudiante:
                        print(f"  - Estudiante encontrado ID: {estudiante.id}")
                        print(f"  - fotografia_path actual: {getattr(estudiante, 'fotografia_path', 'No tiene')}")
                        print(f"  - fotografia_path nuevo: {datos.get('fotografia_path')}")
                        
                        # Actualizar TODOS los campos que vienen en datos
                        for campo, valor in datos.items():
                            if campo != 'id':  # No actualizar el ID
                                if hasattr(estudiante, campo):
                                    print(f"  - Actualizando campo '{campo}': {valor}")
                                    setattr(estudiante, campo, valor)
                                else:
                                    print(f"  - ADVERTENCIA: El modelo no tiene campo '{campo}'")
                        
                        print(f"  - Guardando estudiante...")
                        estudiante.save()
                        print(f"  - ✅ Estudiante actualizado")
                        
                        # Verificar que se guardó
                        estudiante_verificado = EstudianteModel.find_by_id(datos['id'])
                        if estudiante_verificado:
                            print(f"  - Verificación - fotografia_path después de guardar: {getattr(estudiante_verificado, 'fotografia_path', 'No tiene')}")
                    
                    mensaje_titulo = "✅ Estudiante Actualizado"
                    mensaje_texto = "Estudiante actualizado exitosamente"
                
                # Recargar la tabla
                self.cargar_estudiantes(self.current_filter)
                
                # Cerrar el diálogo de edición/creación actual
                # (Esto se hace automáticamente cuando se emite la señal y se llama a accept())
                
                # Mostrar diálogo de detalles en modo lectura
                self.mostrar_detalles_despues_de_guardar(estudiante, mensaje_titulo, mensaje_texto)
                
            except ValueError as e:
                print(f"  - ❌ Error de validación: {e}")
                QMessageBox.warning(self, "Error de Validación", str(e))
                return
            except Exception as e:
                print(f"  - ❌ Error: {e}")
                import traceback
                traceback.print_exc()
                QMessageBox.critical(self, "Error", f"Error al guardar estudiante: {str(e)}")
                return
                
        except Exception as e:
            print(f"  - ❌ Error inesperado: {e}")
            QMessageBox.critical(self, "Error", f"Error inesperado: {str(e)}")
            logger.error(f"Error en on_estudiante_guardado: {e}")    
    
    def mostrar_detalles_despues_de_guardar(self, estudiante, titulo, mensaje):
        """Mostrar diálogo de detalles después de guardar"""
        try:
            # Preparar datos para el diálogo de detalles
            estudiante_data = {
                'id': estudiante.id,
                'ci_numero': estudiante.ci_numero,
                'ci_expedicion': estudiante.ci_expedicion,
                'nombres': estudiante.nombres,
                'apellidos': estudiante.apellidos,
                'fecha_nacimiento': estudiante.fecha_nacimiento,
                'telefono': estudiante.telefono,
                'email': estudiante.email,
                'universidad_egreso': estudiante.universidad_egreso,
                'profesion': estudiante.profesion,
                'activo': estudiante.activo
            }
            
            # Crear diálogo en modo lectura
            dialog = EstudianteFormDialog(
                estudiante_data=estudiante_data, 
                modo_lectura=True, 
                parent=self
            )
            
            # Conectar las señales para los botones especiales
            dialog.estudiante_inscribir.connect(self.on_inscribir_estudiante)
            dialog.estudiante_borrar.connect(self.on_borrar_estudiante_desde_dialog)
            
            # Mostrar un breve mensaje antes de abrir los detalles
            QTimer.singleShot(100, lambda: dialog.exec())
            
        except Exception as e:
            logger.error(f"Error al mostrar detalles después de guardar: {e}")
            # Si falla, mostrar mensaje tradicional
            QMessageBox.information(self, titulo, mensaje)
    
    def eliminar_estudiante(self, estudiante):
        """Eliminar estudiante con confirmación"""
        respuesta = QMessageBox.question(
            self, "🗑️ Confirmar Eliminación",
            f"¿Está seguro de eliminar al estudiante?\n\n"
            f"Nombre: {estudiante.nombre_completo}\n"
            f"CI: {estudiante.ci_numero}-{estudiante.ci_expedicion}\n\n"
            f"⚠️ Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            try:
                # Eliminar usando el modelo
                success = EstudianteModel.delete(estudiante.id)
                if success:
                    QMessageBox.information(self, "✅ Éxito", "Estudiante eliminado correctamente")
                    self.cargar_estudiantes(self.current_filter)
                else:
                    QMessageBox.warning(self, "Error", "No se pudo eliminar el estudiante")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar: {str(e)}")
    
    # ==================== MÉTODOS DE PAGINACIÓN SIMPLIFICADOS ====================
    
    def actualizar_controles_paginacion(self):
        """Actualizar controles de paginación - Versión simplificada"""
        if self.records_per_page == 0:
            self.total_pages = 1
        else:
            self.total_pages = max(1, (self.total_records + self.records_per_page - 1) // self.records_per_page)
        
        self.lblPaginaInfo.setText(f"Página {self.current_page} de {self.total_pages}")
        
        # Habilitar/deshabilitar botones
        self.btnPrimera.setEnabled(self.current_page > 1)
        self.btnAnterior.setEnabled(self.current_page > 1)
        self.btnSiguiente.setEnabled(self.current_page < self.total_pages)
        self.btnUltima.setEnabled(self.current_page < self.total_pages)
    
    def actualizar_contador(self):
        """Actualizar contador de registros"""
        if self.total_records == 0:
            self.lblContador.setText("No hay estudiantes")
        else:
            if self.records_per_page == 0:
                inicio = 1
                fin = self.total_records
            else:
                inicio = (self.current_page - 1) * self.records_per_page + 1
                fin = min(self.current_page * self.records_per_page, self.total_records)
            
            self.lblContador.setText(f"Mostrando {inicio}-{fin} de {self.total_records} estudiantes")
    
    def cambiar_pagina(self, pagina):
        """Cambiar a página específica"""
        if 1 <= pagina <= self.total_pages:
            self.current_page = pagina
            self.cargar_estudiantes(self.current_filter)
    
    def pagina_anterior(self):
        """Ir a página anterior"""
        if self.current_page > 1:
            self.current_page -= 1
            self.cargar_estudiantes(self.current_filter)
    
    def pagina_siguiente(self):
        """Ir a página siguiente"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.cargar_estudiantes(self.current_filter)
    
    def ultima_pagina(self):
        """Ir a última página"""
        self.cambiar_pagina(self.total_pages)
    
    def cambiar_registros_pagina(self, texto):
        """Cambiar registros por página"""
        if texto == "Todos":
            self.records_per_page = 0
        else:
            try:
                self.records_per_page = int(texto)
            except:
                self.records_per_page = 25
        
        self.current_page = 1
        self.cargar_estudiantes(self.current_filter)

    # ================= Métodos manejadores en EstudiantesTab =================

    def on_inscribir_estudiante(self, estudiante_data):
        """Manejador para inscribir estudiante desde diálogo de detalles"""
        try:
            # Obtener el objeto estudiante completo
            from app.models.estudiante_model import EstudianteModel
            estudiante = EstudianteModel.find_by_id(estudiante_data['id'])

            if estudiante:
                # Usar el método matricular_estudiante que YA funciona
                # Este método usa la clase MatricularEstudianteDialog que SÍ existe
                self.matricular_estudiante(estudiante)

        except Exception as e:
            logger.error(f"Error al inscribir estudiante desde diálogo: {e}")
            QMessageBox.critical(self, "Error", f"Error al inscribir estudiante: {str(e)}")

    def on_borrar_estudiante_desde_dialog(self, estudiante_data):
        """Manejador para borrar estudiante desde diálogo de detalles"""
        try:
            # Obtener el objeto estudiante completo
            estudiante = EstudianteModel.find_by_id(estudiante_data['id'])
            if estudiante:
                # Llamar al método existente de eliminación
                self.eliminar_estudiante(estudiante)
        except Exception as e:
            logger.error(f"Error al borrar estudiante desde diálogo: {e}")
            QMessageBox.critical(self, "Error", f"Error al borrar estudiante: {str(e)}")

    def on_editar_desde_modo_lectura(self, datos_estudiante):
        """
        Manejador cuando se presiona "Editar" desde el modo lectura

        Args:
            datos_estudiante: Diccionario con datos del estudiante
        """
        try:
            print(f"DEBUG on_editar_desde_modo_lectura:")
            print(f"  - Datos recibidos: {datos_estudiante}")

            estudiante_id = datos_estudiante.get('id')
            if not estudiante_id:
                print(f"  - ERROR: No hay ID en los datos")
                return

            # Cerrar el diálogo de lectura actual
            # (Se cerrará automáticamente cuando se emita la señal)

            # Abrir diálogo de edición
            self.editar_estudiante(estudiante_id)

        except Exception as e:
            print(f"ERROR en on_editar_desde_modo_lectura: {e}")
            logger.error(f"Error en on_editar_desde_modo_lectura: {e}")
            QMessageBox.critical(self, "Error", f"Error al editar estudiante: {str(e)}")

    def matricular_estudiante(self, estudiante):
        """Abrir diálogo mejorado de matrícula"""
        try:
            # Verificar si el estudiante puede matricularse
            if not estudiante.activo:
                QMessageBox.warning(self, "Advertencia", 
                    "El estudiante está inactivo y no puede matricularse")
                return

            # Abrir diálogo de matrícula
            dialog = Ui_MatricularEstudianteDialog(estudiante.id, parent=self)
            dialog.matricula_realizada.connect(self.on_matricula_realizada)
            dialog.exec()

        except Exception as e:
            logger.error(f"Error al abrir matrícula: {e}")
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")

    def on_matricula_realizada(self, datos):
        """Manejador cuando se completa una matrícula"""
        matricula_id = datos.get('matricula_id')
        QMessageBox.information(self, "✅ Éxito", 
            f"Matrícula registrada exitosamente\nID: {matricula_id}")

        # Opcional: Recargar datos
        self.cargar_estudiantes(self.current_filter)

    def on_inscribir_desde_detalles(self, datos_estudiante):
        """Manejador para inscribir estudiante desde modo lectura"""
        try:
            estudiante_id = datos_estudiante.get('id')
            if estudiante_id:
                print(f"DEBUG: Inscribiendo estudiante ID {estudiante_id}")
                # Aquí puedes llamar a tu método para abrir diálogo de inscripción
                # self.abrir_dialogo_inscripcion(estudiante_id)
        except Exception as e:
            logger.error(f"Error al inscribir desde detalles: {e}")

    def on_borrar_desde_detalles(self, datos_estudiante):
        """Manejador para borrar estudiante desde modo lectura"""
        try:
            estudiante_id = datos_estudiante.get('id')
            if estudiante_id:
                print(f"DEBUG: Borrando estudiante ID {estudiante_id}")
                # Aquí puedes llamar a tu método para borrar estudiante
                # self.borrar_estudiante(estudiante_id)
        except Exception as e:
            logger.error(f"Error al borrar desde detalles: {e}")

    def mostrar_estudiante_en_modo_lectura(self, estudiante_id):
        """Mostrar estudiante en modo lectura después de guardar"""
        try:
            print(f"DEBUG mostrar_estudiante_en_modo_lectura: ID {estudiante_id}")

            from app.views.dialogs.estudiante_form_dialog import EstudianteFormDialog
            from app.models.estudiante_model import EstudianteModel

            # Obtener datos frescos desde BD
            estudiante = EstudianteModel.find_by_id(estudiante_id)
            if not estudiante:
                print(f"ERROR: Estudiante {estudiante_id} no encontrado")
                return

            # Crear diccionario con datos
            estudiante_data = {
                'id': estudiante.id,
                'ci_numero': estudiante.ci_numero,
                'ci_expedicion': estudiante.ci_expedicion,
                'nombres': estudiante.nombres,
                'apellidos': estudiante.apellidos,
                'fecha_nacimiento': estudiante.fecha_nacimiento,
                'telefono': getattr(estudiante, 'telefono', ''),
                'email': getattr(estudiante, 'email', ''),
                'universidad_egreso': getattr(estudiante, 'universidad_egreso', ''),
                'profesion': getattr(estudiante, 'profesion', ''),
                'fotografia_path': getattr(estudiante, 'fotografia_path', None),
                'activo': getattr(estudiante, 'activo', 1)
            }

            # Abrir diálogo en modo lectura
            dialog = EstudianteFormDialog(
                estudiante_data=estudiante_data,
                modo_lectura=True,
                parent=self
            )

            # Conectar señales
            dialog.estudiante_editar.connect(lambda data: self.editar_estudiante(data['id']))
            dialog.estudiante_inscribir.connect(self.on_inscribir_desde_detalles)
            dialog.estudiante_borrar.connect(self.on_borrar_desde_detalles)

            dialog.exec()

        except Exception as e:
            print(f"ERROR mostrando estudiante en modo lectura: {e}")
            logger.error(f"Error mostrando estudiante en modo lectura: {e}")

