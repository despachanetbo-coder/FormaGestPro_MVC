# app/views/dialogs/docente_form_dialog.py
"""
Diálogo para formulario de docentes - Basado en estudiantes pero con manejo de CV PDF
"""

import logging
import shutil
import fitz
from PIL import Image
import io
from datetime import datetime, date
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QDateEdit,
    QMessageBox, QFileDialog, QCheckBox,
    QGroupBox, QFrame, QWidget, QScrollArea
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QPixmap, QImage

from app.models.docente_model import DocenteModel

logger = logging.getLogger(__name__)

class DocenteFormDialog(QDialog):
    """Diálogo para crear/editar docentes con manejo de CV PDF"""
    
    # Señales
    docente_guardado = Signal(dict)          # Para creación
    docente_actualizado = Signal(int, dict)  # Para edición (id, datos)
    docente_inscribir = Signal(dict)         # Para futuras funcionalidades
    docente_borrar = Signal(dict)            # Para botón "Eliminar"
    docente_editar = Signal(dict)            # Para botón "Editar" en modo lectura
    
    def __init__(self, docente_id=None, docente_data=None, modo_lectura=False, parent=None):
        """
        Inicializar diálogo de docente
        
        Args:
            docente_id: ID del docente (para edición/lectura). None para nuevo.
            docente_data: Diccionario con datos (opcional, para compatibilidad)
            modo_lectura: Si True, muestra en modo solo lectura
            parent: Widget padre
        """
        super().__init__(parent)
        
        # Determinar ID y datos
        if docente_data and 'id' in docente_data:
            self.docente_id = docente_data['id']
            self.docente_data = docente_data
        else:
            self.docente_id = docente_id
            self.docente_data = {}
        
        self.modo_lectura = modo_lectura
        self.es_edicion = self.docente_id is not None
        
        # Variables para manejo de CV
        self.ruta_cv_original = None
        self.ruta_cv_temp = None
        self.cv_modificado = False
        
        # Directorio para CVs
        self.directorio_cvs = Path("archivos/cv_docentes")
        self.directorio_cvs.mkdir(parents=True, exist_ok=True)
        
        # Configurar ventana
        self._configurar_ventana()
        self.setup_ui()
        self.setup_connections()
        
        # Cargar datos si es necesario
        self._cargar_datos_iniciales()
    
    def _configurar_ventana(self):
        """Configurar propiedades de la ventana"""
        if self.modo_lectura:
            self.setWindowTitle("👨‍🏫 Detalles del Docente")
        elif self.es_edicion:
            self.setWindowTitle("✏️ Editar Docente")
        else:
            self.setWindowTitle("➕ Nuevo Docente")
        
        self.setMinimumWidth(850)
        self.setMinimumHeight(700)
    
    def _cargar_datos_iniciales(self):
        """Cargar datos iniciales según el modo"""
        if self.es_edicion:
            self.cargar_datos_desde_bd()
        
        if self.modo_lectura:
            self.set_readonly_mode(True)
    
    def setup_ui(self):
        """Configurar interfaz del diálogo"""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Panel izquierdo - Formulario
        left_panel = self._crear_panel_formulario()
        
        # Panel derecho - Información de CV
        right_panel = self._crear_panel_cv()
        
        main_layout.addWidget(left_panel, 7)
        main_layout.addWidget(right_panel, 3)
    
    def _crear_panel_formulario(self):
        """Crear panel izquierdo con el formulario de datos"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Título
        title_label = QLabel("📝 Información del Docente")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 8px 0;
            }
        """)
        layout.addWidget(title_label)
        
        # Área de scroll
        form_scroll = QScrollArea()
        form_scroll.setWidgetResizable(True)
        
        # Widget contenedor
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(15)
        
        # Secciones del formulario
        form_layout.addWidget(self._crear_seccion_datos_personales())
        form_layout.addWidget(self._crear_seccion_profesional())
        form_layout.addWidget(self._crear_seccion_contacto())
        
        # Sección de estado si es edición/lectura
        if self.es_edicion or self.modo_lectura:
            form_layout.addWidget(self._crear_seccion_estado())
        
        form_layout.addStretch()
        form_scroll.setWidget(form_widget)
        layout.addWidget(form_scroll)
        
        return panel
    
    def _crear_seccion_datos_personales(self):
        """Crear sección de datos personales"""
        group = QGroupBox("👤 Datos Personales")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #3498db;
            }
        """)
        
        form = QFormLayout()
        form.setSpacing(12)
        form.setContentsMargins(15, 20, 15, 20)
        
        # CI
        hbox_ci = QHBoxLayout()
        hbox_ci.setSpacing(10)
        
        ci_label = QLabel("Carnet de Identidad:*")
        ci_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        
        self.txt_ci_numero = self._crear_line_edit("1234567")
        self.combo_expedicion = self._crear_combo_expedicion()
        
        hbox_ci.addWidget(self.txt_ci_numero)
        hbox_ci.addWidget(QLabel("-"))
        hbox_ci.addWidget(self.combo_expedicion)
        hbox_ci.addStretch()
        
        form.addRow(ci_label, hbox_ci)
        
        # Nombres
        nombres_label = QLabel("Nombres:*")
        nombres_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.txt_nombres = self._crear_line_edit("Juan Carlos")
        form.addRow(nombres_label, self.txt_nombres)
        
        # Apellidos
        apellidos_label = QLabel("Apellidos:*")
        apellidos_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.txt_apellidos = self._crear_line_edit("Pérez López")
        form.addRow(apellidos_label, self.txt_apellidos)
        
        group.setLayout(form)
        return group
    
    def _crear_seccion_profesional(self):
        """Crear sección de información profesional"""
        group = QGroupBox("🎓 Información Profesional")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #9b59b6;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #9b59b6;
            }
        """)
        
        form = QFormLayout()
        form.setSpacing(12)
        form.setContentsMargins(15, 20, 15, 20)
        
        # Especialidad
        especialidad_label = QLabel("Especialidad:*")
        especialidad_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.txt_especialidad = self._crear_line_edit("Ingeniería de Sistemas")
        form.addRow(especialidad_label, self.txt_especialidad)
        
        # Grado Académico
        grado_label = QLabel("Grado Académico:")
        grado_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.txt_grado_academico = self._crear_line_edit("Magister")
        form.addRow(grado_label, self.txt_grado_academico)
        
        group.setLayout(form)
        return group
    
    def _crear_seccion_contacto(self):
        """Crear sección de información de contacto"""
        group = QGroupBox("📞 Información de Contacto")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #2ecc71;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #2ecc71;
            }
        """)
        
        form = QFormLayout()
        form.setSpacing(12)
        form.setContentsMargins(15, 20, 15, 20)
        
        # Teléfono
        telefono_label = QLabel("Teléfono/Celular:")
        telefono_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.txt_telefono = self._crear_line_edit("77712345")
        form.addRow(telefono_label, self.txt_telefono)
        
        # Email
        email_label = QLabel("Correo Electrónico:")
        email_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.txt_email = self._crear_line_edit("juan.perez@email.com")
        form.addRow(email_label, self.txt_email)
        
        group.setLayout(form)
        return group
    
    def _crear_seccion_estado(self):
        """Crear sección de estado del docente"""
        esta_activo = self.docente_data.get('activo', 1) if self.docente_data else 1
        
        if esta_activo:
            color_borde = "#27ae60"
            texto_estado = "✅ ESTADO: ACTIVO"
        else:
            color_borde = "#e74c3c"
            texto_estado = "❌ ESTADO: INACTIVO"
        
        group = QGroupBox("📊 Estado del Docente")
        group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 13px;
                border: 2px solid {color_borde};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 8px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: {color_borde};
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 20, 15, 20)
        
        if self.modo_lectura:
            lbl_estado = QLabel(texto_estado)
            lbl_estado.setStyleSheet(f"""
                QLabel {{
                    font-size: 13px;
                    font-weight: bold;
                    padding: 10px 15px;
                    color: {color_borde};
                    background-color: white;
                    border-radius: 6px;
                    border: 1px solid {color_borde};
                }}
            """)
            lbl_estado.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl_estado)
        else:
            self.chk_activo = QCheckBox("Docente activo")
            self.chk_activo.setChecked(bool(esta_activo))
            self.chk_activo.setStyleSheet("""
                QCheckBox {
                    font-size: 13px;
                    font-weight: bold;
                    padding: 10px;
                    color: #2c3e50;
                }
                QCheckBox::indicator {
                    width: 22px;
                    height: 22px;
                    border-radius: 4px;
                    border: 2px solid #95a5a6;
                }
                QCheckBox::indicator:checked {
                    background-color: #27ae60;
                    border: 2px solid #219653;
                }
                QCheckBox::indicator:unchecked {
                    background-color: #e74c3c;
                    border: 2px solid #c0392b;
                }
            """)
            layout.addWidget(self.chk_activo)
        
        layout.addStretch()
        group.setLayout(layout)
        return group
    
    def _crear_panel_cv(self):
        """Crear panel derecho para manejo y vista previa de CV con scroll"""
        panel = QWidget()
        panel.setFixedWidth(350)  # Un poco más ancho para mejor visualización
        
        # Layout principal con scroll
        main_layout = QVBoxLayout(panel)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Título
        card_title = QLabel("📄 Currículum Vitae")
        card_title.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px 0;
                text-align: center;
                background-color: #f8f9fa;
                border-radius: 8px;
                margin-bottom: 5px;
            }
        """)
        main_layout.addWidget(card_title)
        
        # Crear área de scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Solo scroll vertical
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f8f9fa;
                width: 10px;
                border-radius: 5px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #adb5bd;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #6c757d;
            }
            QScrollBar::add-line:vertical, 
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar:left-arrow:vertical, 
            QScrollBar::right-arrow:vertical {
                background: none;
            }
        """)
        
        # Widget contenedor para el scroll
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: transparent;")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)
        scroll_layout.setContentsMargins(5, 5, 15, 5)  # Margen derecho para el scroll
        
        # Contenedor principal (card)
        card_container = QFrame()
        card_container.setMinimumHeight(480)  # Más alto para acomodar la vista previa proporcional
        card_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        card_layout = QVBoxLayout(card_container)
        card_layout.setSpacing(15)
        card_layout.setAlignment(Qt.AlignCenter)
        
        # Marco para la vista previa del PDF con proporción carta (A4: 1:1.414)
        # Ancho: 200px, Alto: 200 * 1.414 ≈ 283px
        preview_width = 200
        preview_height = int(preview_width * 1.414)  # Ratio A4 estándar
        
        preview_frame = QFrame()
        preview_frame.setFixedSize(preview_width + 20, preview_height + 20)  # +20 para el padding/borde
        preview_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #2c3e50;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setAlignment(Qt.AlignCenter)
        
        # Label para mostrar la vista previa - tamaño proporcional carta
        self.lbl_preview_pdf = QLabel()
        self.lbl_preview_pdf.setFixedSize(preview_width, preview_height)
        self.lbl_preview_pdf.setStyleSheet("""
            QLabel {
                background-color: #ffffff;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                qproperty-alignment: 'AlignCenter';
            }
        """)
        self.lbl_preview_pdf.setAlignment(Qt.AlignCenter)
        self.lbl_preview_pdf.setText("Vista previa\nPDF")
        self.lbl_preview_pdf.setWordWrap(True)
        
        preview_layout.addWidget(self.lbl_preview_pdf)
        card_layout.addWidget(preview_frame, alignment=Qt.AlignCenter)
        
        # Información del archivo (con scroll interno si es necesario)
        info_container = QFrame()
        info_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        
        info_layout = QVBoxLayout(info_container)
        info_layout.setSpacing(5)
        
        self.lbl_info_cv = QLabel("No hay CV cargado")
        self.lbl_info_cv.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 12px;
                text-align: center;
                padding: 12px;
                background-color: #f8f9fa;
                border-radius: 6px;
                border: 1px dashed #bdc3c7;
            }
        """)
        self.lbl_info_cv.setAlignment(Qt.AlignCenter)
        self.lbl_info_cv.setWordWrap(True)
        self.lbl_info_cv.setTextInteractionFlags(Qt.TextSelectableByMouse)  # Permite seleccionar texto
        
        info_layout.addWidget(self.lbl_info_cv)
        card_layout.addWidget(info_container)
        
        # Botones para CV (solo en modo edición/creación)
        if not self.modo_lectura:
            self._agregar_botones_cv(card_layout)
        
        scroll_layout.addWidget(card_container)
        scroll_layout.addStretch()
        
        # Configurar el scroll area
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area, 1)  # El 1 hace que el scroll area se expanda
        
        # Área de botones (fuera del scroll)
        main_layout.addWidget(self._crear_area_botones())
        
        return panel
    
    def _agregar_botones_cv(self, layout):
        """Agregar botones para gestión de CV"""
        button_frame = QWidget()
        button_layout = QVBoxLayout(button_frame)
        button_layout.setSpacing(10)
        
        # Botón seleccionar CV
        self.btn_seleccionar_cv = QPushButton("📁 Seleccionar CV")
        self.btn_seleccionar_cv.setFixedHeight(40)
        self.btn_seleccionar_cv.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                font-size: 13px;
                border-radius: 6px;
                border: 2px solid #2980b9;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #2980b9;
                border: 2px solid #1f618d;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
        """)
        self.btn_seleccionar_cv.setToolTip("Seleccionar archivo PDF del currículum")
        
        # Botón eliminar CV
        self.btn_eliminar_cv = QPushButton("🗑️ Eliminar CV")
        self.btn_eliminar_cv.setFixedHeight(40)
        self.btn_eliminar_cv.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                font-size: 13px;
                border-radius: 6px;
                border: 2px solid #c0392b;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #c0392b;
                border: 2px solid #a93226;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                border: 1px solid #95a5a6;
            }
        """)
        self.btn_eliminar_cv.setEnabled(False)
        self.btn_eliminar_cv.setToolTip("Eliminar el currículum seleccionado")
        
        # Botón Ver CV Completo
        self.btn_abrir_cv = QPushButton("👁️ Ver Completo")
        self.btn_abrir_cv.setFixedHeight(40)
        self.btn_abrir_cv.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                font-weight: bold;
                font-size: 13px;
                border-radius: 6px;
                border: 2px solid #8e44ad;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
                border: 2px solid #7d3c98;
            }
            QPushButton:pressed {
                background-color: #7d3c98;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                border: 1px solid #95a5a6;
            }
        """)
        self.btn_abrir_cv.setEnabled(False)
        self.btn_abrir_cv.setToolTip("Abrir el PDF completo con el visor predeterminado")
        self.btn_abrir_cv.clicked.connect(self.abrir_cv_completo)

        button_layout.addWidget(self.btn_seleccionar_cv)
        button_layout.addWidget(self.btn_eliminar_cv)
        button_layout.addWidget(self.btn_abrir_cv)  # Agregar este
        
        layout.addWidget(button_frame)
        
        # Información del CV
        info_label = QLabel("Formato: PDF\nTamaño máximo: 5MB")
        info_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 11px;
                text-align: center;
                padding: 8px;
                background-color: #ffffff;
                border-radius: 4px;
                border: 1px dashed #bdc3c7;
            }
        """)
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        
        layout.addWidget(info_label)
        layout.addStretch()
    
    def _crear_area_botones(self):
        """Crear área de botones según el modo"""
        area = QFrame()
        area.setStyleSheet("""
            QFrame {
                border: 2px solid #dee2e6;
                border-radius: 10px;
                padding: 15px 0;
            }
        """)
        
        layout = QVBoxLayout(area)
        layout.setSpacing(10)
        
        if not self.modo_lectura:
            self.btn_guardar = self._crear_boton("💾 Guardar", "#f39c12", "#e67e22", "#d35400")
            self.btn_cancelar = self._crear_boton("❌ Cancelar", "#e74c3c", "#c0392b", "#a93226", es_principal=True)
            
            layout.addWidget(self.btn_guardar)
            layout.addWidget(self.btn_cancelar)
        else:
            self.btn_inscribir = self._crear_boton("📚 Asignar Cursos", "#9b59b6", "#8e44ad", "#7d3c98")
            self.btn_editar = self._crear_boton("✏️ Editar", "#27ae60", "#219653", "#1e8449")
            self.btn_borrar = self._crear_boton("🗑️ Eliminar Docente", "#e74c3c", "#c0392b", "#a93226", es_principal=True)
            self.btn_cerrar = self._crear_boton("✖️ Cerrar Vista", "#e74c3c", "#c0392b", "#a93226", es_principal=True)
            
            self.btn_inscribir.setToolTip("Asignar cursos a este docente")
            self.btn_editar.setToolTip("Editar los datos de este docente")
            self.btn_borrar.setToolTip("Eliminar este docente del sistema")
            self.btn_cerrar.setToolTip("Cerrar esta ventana")
            
            layout.addWidget(self.btn_inscribir)
            layout.addWidget(self.btn_editar)
            layout.addWidget(self.btn_borrar)
            layout.addWidget(self.btn_cerrar)
        
        return area
    
    def _crear_line_edit(self, placeholder):
        """Crear QLineEdit con estilo consistente"""
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setMaximumWidth(400)
        line_edit.setFixedHeight(36)
        line_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        return line_edit
    
    def _crear_combo_expedicion(self):
        """Crear combo box para expedición de CI"""
        combo = QComboBox()
        combo.addItems(['BE', 'CH', 'CB', 'LP', 'OR', 'PD', 'PT', 'SC', 'TJ', 'EX'])
        combo.setFixedHeight(36)
        combo.setFixedWidth(80)
        combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 13px;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
        """)
        return combo
    
    def _crear_boton(self, texto, color_normal, color_hover, color_pressed, es_principal=False):
        """Crear QPushButton con estilo consistente"""
        boton = QPushButton(texto)
        boton.setFixedHeight(45)
        
        if es_principal:
            estilo = f"""
                QPushButton {{
                    background-color: {color_normal};
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    border-radius: 8px;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: {color_hover};
                }}
                QPushButton:pressed {{
                    background-color: {color_pressed};
                }}
            """
        else:
            estilo = f"""
                QPushButton {{
                    background-color: {color_normal};
                    color: white;
                    border-radius: 3px;
                    border: none;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: {color_hover};
                }}
                QPushButton:pressed {{
                    background-color: {color_pressed};
                }}
            """
        
        boton.setStyleSheet(estilo)
        return boton
    
    def setup_connections(self):
        """Conectar señales y slots"""
        if not self.modo_lectura:
            self.btn_guardar.clicked.connect(self.validar_y_guardar)
            self.btn_cancelar.clicked.connect(self.reject)
            
            self.btn_seleccionar_cv.clicked.connect(self.seleccionar_cv)
            self.btn_eliminar_cv.clicked.connect(self.eliminar_cv)
        else:
            self.btn_inscribir.clicked.connect(self.on_inscribir_clicked)
            self.btn_editar.clicked.connect(self.on_editar_clicked)
            self.btn_borrar.clicked.connect(self.on_borrar_clicked)
            self.btn_cerrar.clicked.connect(self.accept)
    
    # ============================================================================
    # MÉTODOS PARA MANEJO DE DATOS
    # ============================================================================
    
    def cargar_datos_desde_bd(self):
        """Cargar datos del docente directamente desde la base de datos"""
        try:
            if not self.docente_id:
                return
            
            docente = DocenteModel.find_by_id(self.docente_id)
            if not docente:
                QMessageBox.critical(self, "Error", "Docente no encontrado")
                self.reject()
                return
            
            # Convertir a diccionario
            self.docente_data = {
                'id': docente.id,
                'ci_numero': docente.ci_numero,
                'ci_expedicion': docente.ci_expedicion,
                'nombres': docente.nombres,
                'apellidos': docente.apellidos,
                'especialidad': getattr(docente, 'especialidad', ''),
                'grado_academico': getattr(docente, 'grado_academico', ''),
                'telefono': getattr(docente, 'telefono', ''),
                'email': getattr(docente, 'email', ''),
                'curriculum_path': getattr(docente, 'curriculum_path', None),
                'activo': getattr(docente, 'activo', 1)
            }
            
            # Guardar ruta original del CV
            self.ruta_cv_original = self.docente_data['curriculum_path']
            
            # Cargar datos en la UI
            self.cargar_datos()
            
        except Exception as e:
            logger.error(f"Error al cargar datos del docente desde BD: {e}")
            QMessageBox.critical(self, "Error", f"Error al cargar datos: {str(e)}")
            self.reject()
    
    def cargar_datos(self):
        """Cargar datos del docente en los campos del formulario"""
        try:
            if not self.docente_data:
                return
            
            # Información personal
            self.txt_ci_numero.setText(str(self.docente_data.get('ci_numero', '')))
            
            expedicion = self.docente_data.get('ci_expedicion', 'BE')
            index = self.combo_expedicion.findText(expedicion)
            if index >= 0:
                self.combo_expedicion.setCurrentIndex(index)
            
            self.txt_nombres.setText(str(self.docente_data.get('nombres', '')))
            self.txt_apellidos.setText(str(self.docente_data.get('apellidos', '')))
            
            # Información profesional
            self.txt_especialidad.setText(str(self.docente_data.get('especialidad', '')))
            self.txt_grado_academico.setText(str(self.docente_data.get('grado_academico', '')))
            
            # Información de contacto
            self.txt_telefono.setText(str(self.docente_data.get('telefono', '')))
            self.txt_email.setText(str(self.docente_data.get('email', '')))
            
        except Exception as e:
            logger.error(f"Error al cargar datos en UI: {e}")
            QMessageBox.warning(self, "Error", f"Error al cargar datos: {str(e)}")
    
    def obtener_datos_formulario(self):
        """Obtener y validar datos del formulario"""
        errores = []
        datos = {}
        
        # Validar campos obligatorios
        ci_numero = self.txt_ci_numero.text().strip()
        if not ci_numero:
            errores.append("El número de CI es obligatorio")
        elif not ci_numero.isdigit():
            errores.append("El CI debe contener solo números")
        elif len(ci_numero) < 4 or len(ci_numero) > 10:
            errores.append("El CI debe tener entre 4 y 10 dígitos")
        else:
            datos['ci_numero'] = ci_numero
        
        datos['ci_expedicion'] = self.combo_expedicion.currentText()
        
        nombres = self.txt_nombres.text().strip()
        if not nombres:
            errores.append("Los nombres son obligatorios")
        elif len(nombres) < 2:
            errores.append("Los nombres deben tener al menos 2 caracteres")
        else:
            datos['nombres'] = nombres
        
        apellidos = self.txt_apellidos.text().strip()
        if not apellidos:
            errores.append("Los apellidos son obligatorios")
        elif len(apellidos) < 2:
            errores.append("Los apellidos deben tener al menos 2 caracteres")
        else:
            datos['apellidos'] = apellidos
        
        # Información profesional
        especialidad = self.txt_especialidad.text().strip()
        if not especialidad:
            errores.append("La especialidad es obligatoria")
        else:
            datos['especialidad'] = especialidad
        
        grado_academico = self.txt_grado_academico.text().strip()
        if grado_academico:
            datos['grado_academico'] = grado_academico
        
        # Contacto
        telefono = self.txt_telefono.text().strip()
        if telefono:
            datos['telefono'] = telefono
        
        email = self.txt_email.text().strip()
        if email:
            if '@' not in email or '.' not in email.split('@')[-1]:
                errores.append("Formato de email inválido")
            else:
                datos['email'] = email.lower()
        
        # Estado
        if hasattr(self, 'chk_activo'):
            datos['activo'] = 1 if self.chk_activo.isChecked() else 0
        
        # Procesar CV
        if ci_numero:
            if self.cv_modificado:
                if self.ruta_cv_temp:
                    ruta_cv = self.procesar_cv(ci_numero)
                    if ruta_cv:
                        datos['curriculum_path'] = ruta_cv
                    else:
                        errores.append("No se pudo guardar el currículum")
                else:
                    datos['curriculum_path'] = None
            elif self.ruta_cv_original:
                datos['curriculum_path'] = self.ruta_cv_original
        
        # Incluir ID si es edición
        if self.es_edicion and self.docente_id:
            datos['id'] = self.docente_id
        
        return errores, datos
    
    def validar_y_guardar(self):
        """Validar y guardar los datos del docente directamente en la BD"""
        errores, datos = self.obtener_datos_formulario()
        
        if errores:
            QMessageBox.warning(self, "Validación", "\n".join(errores))
            return
        
        try:
            from app.models.docente_model import DocenteModel
            
            if self.es_edicion:
                # ACTUALIZAR
                docente = DocenteModel.find_by_id(datos['id'])
                if docente:
                    # Actualizar todos los campos
                    for campo, valor in datos.items():
                        if campo != 'id' and hasattr(docente, campo):
                            setattr(docente, campo, valor)
                    docente.save()
                    mensaje = "✅ Docente actualizado correctamente"
                else:
                    QMessageBox.warning(self, "Error", "Docente no encontrado")
                    return
            else:
                # CREAR
                docente = DocenteModel(**datos)
                docente.save()
                datos['id'] = docente.id
                mensaje = "✅ Docente creado correctamente"
            
            # Mostrar mensaje
            QMessageBox.information(self, "Éxito", mensaje)
            
            # Cerrar este diálogo
            self.accept()
            
            # Notificar al padre para que actualice la tabla
            if hasattr(self.parent(), 'cargar_docentes'):
                self.parent().cargar_docentes()
            
            # Abrir nuevo diálogo en modo lectura
            self._abrir_modo_lectura(datos['id'])
            
        except Exception as e:
            logger.error(f"Error al guardar docente: {e}")
            QMessageBox.critical(self, "Error", f"Error al guardar docente: {str(e)}")
    
    def _abrir_modo_lectura(self, docente_id):
        """Abrir diálogo en modo lectura"""
        try:
            from app.models.docente_model import DocenteModel
            from app.views.dialogs.docente_form_dialog import DocenteFormDialog
            
            docente = DocenteModel.find_by_id(docente_id)
            if docente:
                datos = {
                    'id': docente.id,
                    'ci_numero': docente.ci_numero,
                    'ci_expedicion': docente.ci_expedicion,
                    'nombres': docente.nombres,
                    'apellidos': docente.apellidos,
                    'especialidad': getattr(docente, 'especialidad', ''),
                    'grado_academico': getattr(docente, 'grado_academico', ''),
                    'telefono': getattr(docente, 'telefono', ''),
                    'email': getattr(docente, 'email', ''),
                    'curriculum_path': getattr(docente, 'curriculum_path', None),
                    'activo': getattr(docente, 'activo', 1)
                }
                
                dialog = DocenteFormDialog(
                    docente_data=datos,
                    modo_lectura=True,
                    parent=self.parent()
                )
                dialog.exec()
                
        except Exception as e:
            logger.error(f"Error al abrir en modo lectura: {e}")
    
    # ============================================================================
    # MÉTODOS PARA MANEJO DE CURRÍCULUM
    # ============================================================================
    
    def cargar_cv(self, ruta):
        """Cargar y mostrar vista previa del CV PDF"""
        try:
            if not ruta:
                self.lbl_preview_pdf.setText("Sin\nCV")
                self.lbl_preview_pdf.setStyleSheet("""
                    QLabel {
                        background-color: #ffffff;
                        border: 1px solid #bdc3c7;
                        border-radius: 4px;
                        font-size: 14px;
                        color: #7f8c8d;
                    }
                """)
                self.lbl_info_cv.setText("No hay CV cargado")
                return

            ruta_path = Path(ruta)

            # Verificar si el archivo existe
            if not ruta_path.exists():
                # Intentar buscar en el directorio de CVs
                nombre_archivo = ruta_path.name
                ruta_alternativa = self.directorio_cvs / nombre_archivo
                if ruta_alternativa.exists():
                    self.cargar_cv(str(ruta_alternativa))
                    return
                else:
                    self.lbl_preview_pdf.setText("Archivo\nno encontrado")
                    self.lbl_info_cv.setText(f"Archivo no encontrado: {nombre_archivo}")
                    return

            # Verificar que sea PDF
            if not ruta.lower().endswith('.pdf'):
                self.lbl_preview_pdf.setText("No es\nPDF")
                self.lbl_info_cv.setText(f"El archivo no es PDF: {ruta_path.name}")
                return

            try:
                # Generar vista previa de la primera página
                self.generar_vista_previa_pdf(ruta_path)

                # Actualizar información del archivo
                tamaño_kb = ruta_path.stat().st_size / 1024
                paginas = self.obtener_numero_paginas_pdf(ruta_path)

                info_texto = f"📄 {ruta_path.name}\n"
                info_texto += f"📏 Tamaño: {tamaño_kb:.1f} KB\n"
                info_texto += f"📑 Páginas: {paginas}"

                self.lbl_info_cv.setText(info_texto)
                self.ruta_cv_temp = str(ruta_path)

                if hasattr(self, 'btn_abrir_cv'):
                    self.btn_abrir_cv.setEnabled(True)

            except Exception as e:
                print(f"Error generando vista previa: {e}")
                # Mostrar información básica si falla la vista previa
                tamaño_kb = ruta_path.stat().st_size / 1024
                self.lbl_preview_pdf.setText("📄\nPDF")
                self.lbl_info_cv.setText(f"{ruta_path.name}\nTamaño: {tamaño_kb:.1f} KB")
                self.ruta_cv_temp = str(ruta_path)

        except Exception as e:
            logger.error(f"Error al cargar CV: {e}")
            self.lbl_preview_pdf.setText("Error\ncargando")
            self.lbl_info_cv.setText("Error al cargar el archivo")
    
    def seleccionar_cv(self):
        """Seleccionar archivo de currículum PDF"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Seleccionar Currículum Vitae (PDF)")
        file_dialog.setNameFilter("Archivos PDF (*.pdf)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        
        if file_dialog.exec():
            archivos = file_dialog.selectedFiles()
            if archivos:
                ruta_origen = archivos[0]
                
                if not ruta_origen.lower().endswith('.pdf'):
                    QMessageBox.warning(self, "Formato no válido", 
                                       "Por favor, seleccione un archivo en formato PDF.")
                    return
                
                # Verificar tamaño (5MB máximo)
                tamaño = Path(ruta_origen).stat().st_size
                if tamaño > 5 * 1024 * 1024:  # 5MB
                    QMessageBox.warning(self, "Archivo muy grande",
                                       "El archivo excede el tamaño máximo de 5MB.")
                    return
                
                self.cargar_cv(ruta_origen)
                self.cv_modificado = True
                self.ruta_cv_temp = ruta_origen
                self.btn_eliminar_cv.setEnabled(True)
                
                logger.info(f"CV seleccionado: {ruta_origen}")
    
    def eliminar_cv(self):
        """Eliminar currículum seleccionado"""
        try:
            respuesta = QMessageBox.question(
                self,
                "Eliminar CV",
                "¿Eliminar el currículum vitae del docente?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if respuesta != QMessageBox.Yes:
                return

            # Eliminar archivo físico si existe
            if self.ruta_cv_original:
                ruta_path = Path(self.ruta_cv_original)
                if (ruta_path.exists() and 
                    ruta_path.is_file() and 
                    self.directorio_cvs in ruta_path.parents):
                    try:
                        ruta_path.unlink()
                    except Exception as e:
                        logger.warning(f"No se pudo eliminar archivo físico: {e}")

            # Resetear variables
            self.ruta_cv_temp = None
            self.ruta_cv_original = None
            self.cv_modificado = True

            # Limpiar vista previa y mostrar estado
            self.lbl_preview_pdf.clear()
            self.lbl_preview_pdf.setText("Sin\nCV")
            self.lbl_preview_pdf.setStyleSheet("""
                QLabel {
                    background-color: #ffffff;
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                    font-size: 14px;
                    color: #7f8c8d;
                }
            """)

            self.lbl_info_cv.setText("No hay CV cargado")
            self.btn_eliminar_cv.setEnabled(False)

            if hasattr(self, 'btn_abrir_cv'):
                self.btn_abrir_cv.setEnabled(False)

            QMessageBox.information(self, "Éxito", "CV eliminado correctamente")

        except Exception as e:
            logger.error(f"Error al eliminar CV: {e}")
            QMessageBox.warning(self, "Error", f"Error al eliminar CV: {str(e)}")
    
    def procesar_cv(self, ci_numero):
        """
        Procesar el CV: copiarlo al directorio de CVs con nombre generado
        
        Args:
            ci_numero: Número de CI para nombrar el archivo
            
        Returns:
            Ruta absoluta del archivo generado o None si no hay CV
        """
        if not self.ruta_cv_temp:
            return None
        
        try:
            # Generar nombre de archivo
            nombre_archivo = f"cv_d_{ci_numero}.pdf"
            ruta_destino = self.directorio_cvs / nombre_archivo
            
            # Eliminar CV anterior si existe
            if self.ruta_cv_original:
                ruta_anterior = Path(self.ruta_cv_original)
                if (ruta_anterior.exists() and 
                    ruta_anterior != ruta_destino and
                    self.directorio_cvs in ruta_anterior.parents):
                    try:
                        ruta_anterior.unlink()
                    except Exception as e:
                        logger.warning(f"No se pudo eliminar CV anterior: {e}")
            
            # Si el archivo ya existe, sobrescribirlo
            if ruta_destino.exists():
                ruta_destino.unlink()
            
            # Copiar el CV
            shutil.copy2(self.ruta_cv_temp, ruta_destino)
            
            logger.info(f"CV guardado en: {ruta_destino}")
            return str(ruta_destino.absolute())
            
        except Exception as e:
            logger.error(f"Error al guardar CV: {e}")
            QMessageBox.warning(self, "Error", f"No se pudo guardar el CV: {str(e)}")
            return None
    
    # ============================================================================
    # MÉTODOS PARA MANEJO DE EVENTOS Y UI
    # ============================================================================
    
    def showEvent(self, event):
        """Evento que se ejecuta cuando el diálogo se muestra"""
        super().showEvent(event)
        
        # Cargar el CV después de que la UI esté completamente configurada
        if self.docente_data:
            self.cargar_cv_despues_de_ui()
    
    def cargar_cv_despues_de_ui(self):
        """Cargar el CV después de que la UI esté configurada"""
        try:
            ruta_cv = self.docente_data.get('curriculum_path')
            if ruta_cv:
                self.ruta_cv_original = ruta_cv
                self.ruta_cv_temp = ruta_cv
                self.cargar_cv(ruta_cv)
                self.btn_eliminar_cv.setEnabled(True)
            else:
                self.lbl_preview_pdf.setText("Sin\nCV")
                self.lbl_preview_pdf.setStyleSheet("""
                    QLabel {
                        background-color: #ffffff;
                        border: 1px solid #bdc3c7;
                        border-radius: 4px;
                        font-size: 14px;
                        color: #7f8c8d;
                    }
                """)
                self.lbl_info_cv.setText("No hay CV cargado")

        except Exception as e:
            logger.error(f"Error cargando CV después de UI: {e}")
    
    def set_readonly_mode(self, readonly=True):
        """Establecer todos los campos en modo solo lectura"""
        widgets = [
            self.txt_ci_numero, self.combo_expedicion, self.txt_nombres,
            self.txt_apellidos, self.txt_especialidad, self.txt_grado_academico,
            self.txt_telefono, self.txt_email
        ]
        
        for widget in widgets:
            if hasattr(widget, 'setReadOnly'):
                widget.setReadOnly(readonly)
            if hasattr(widget, 'setEnabled'):
                widget.setEnabled(not readonly)
        
        # Deshabilitar botones de CV en modo lectura
        if hasattr(self, 'btn_seleccionar_cv'):
            self.btn_seleccionar_cv.setEnabled(not readonly)
        
        if hasattr(self, 'btn_eliminar_cv'):
            tiene_cv = bool(self.ruta_cv_temp) or bool(self.ruta_cv_original)
            self.btn_eliminar_cv.setEnabled(not readonly and tiene_cv)
    
    # ============================================================================
    # MANEJADORES DE BOTONES (MODO LECTURA)
    # ============================================================================
    
    def on_inscribir_clicked(self):
        """Manejador para botón Asignar Cursos"""
        try:
            print(f"DEBUG: Botón Asignar Cursos clickeado para docente ID {self.docente_data.get('id')}")
            # Emitir señal para que DocentesTab maneje la asignación
            self.docente_inscribir.emit(self.docente_data)
            # Cerrar el diálogo actual
            self.accept()
        except Exception as e:
            print(f"ERROR en on_inscribir_clicked: {e}")
            logger.error(f"Error en on_inscribir_clicked: {e}")
            QMessageBox.warning(self, "Error", f"Error al procesar asignación: {str(e)}")
    
    def on_editar_clicked(self):
        """Manejador para botón Editar"""
        try:
            print(f"DEBUG: Botón Editar clickeado para docente ID {self.docente_data.get('id')}")
            # Emitir señal para que DocentesTab abra el diálogo en modo edición
            self.docente_editar.emit(self.docente_data)
            # Cerrar el diálogo actual
            self.accept()
        except Exception as e:
            print(f"ERROR en on_editar_clicked: {e}")
            logger.error(f"Error al procesar edición: {e}")
            QMessageBox.critical(self, "Error", f"Error al editar docente: {str(e)}")
    
    def on_borrar_clicked(self):
        """Manejador para botón Eliminar"""
        try:
            respuesta = QMessageBox.question(
                self, 
                "🗑️ Confirmar Eliminación",
                f"¿Está seguro de eliminar al docente?\n\n"
                f"Nombre: {self.docente_data.get('nombres', '')} {self.docente_data.get('apellidos', '')}\n"
                f"Especialidad: {self.docente_data.get('especialidad', '')}\n"
                f"CI: {self.docente_data.get('ci_numero', '')}-{self.docente_data.get('ci_expedicion', '')}\n\n"
                f"⚠️ Esta acción no se puede deshacer.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if respuesta == QMessageBox.Yes:
                print(f"DEBUG: Confirmada eliminación de docente ID {self.docente_data.get('id')}")
                # Emitir señal para que DocentesTab maneje la eliminación
                self.docente_borrar.emit(self.docente_data)
                # Cerrar el diálogo actual
                self.accept()
                
        except Exception as e:
            print(f"ERROR en on_borrar_clicked: {e}")
            logger.error(f"Error al eliminar docente: {e}")
            QMessageBox.critical(self, "Error", f"Error al eliminar docente: {str(e)}")
    
    # ============================================================================
    # MÉTODOS PARA MANEJAR PDF
    # ============================================================================
    
    def generar_vista_previa_pdf(self, ruta_pdf):
        """Generar y mostrar vista previa de la primera página del PDF"""
        try:
            # Abrir el PDF
            pdf_document = fitz.open(str(ruta_pdf))

            # Obtener la primera página
            primera_pagina = pdf_document[0]

            # Renderizar la página como imagen (300 DPI para buena calidad)
            pix = primera_pagina.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))  # Escala 2x

            # Convertir a QImage
            img_data = pix.tobytes("ppm")
            qimage = QImage()
            qimage.loadFromData(img_data)

            # Escalar manteniendo proporción para caber en el label
            qimage_escalada = qimage.scaled(
                240, 240,  # Un poco más pequeño que el label
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            # Convertir a QPixmap y mostrar
            pixmap = QPixmap.fromImage(qimage_escalada)
            self.lbl_preview_pdf.setPixmap(pixmap)

            # Cerrar el documento
            pdf_document.close()

        except Exception as e:
            print(f"Error generando vista previa: {e}")
            # Mostrar icono de PDF si hay error
            self.lbl_preview_pdf.setText("📄\nPDF")
            raise

    def obtener_numero_paginas_pdf(self, ruta_pdf):
        """Obtener número de páginas del PDF"""
        try:
            pdf_document = fitz.open(str(ruta_pdf))
            num_paginas = len(pdf_document)
            pdf_document.close()
            return num_paginas
        except:
            return "?"

    def abrir_cv_completo(self):
        """Abrir el PDF completo con el visor predeterminado del sistema"""
        try:
            if self.ruta_cv_temp:
                import os
                import platform

                ruta = Path(self.ruta_cv_temp)
                if ruta.exists():
                    sistema = platform.system()

                    if sistema == 'Windows':
                        os.startfile(str(ruta))
                    elif sistema == 'Darwin':  # macOS
                        os.system(f'open "{ruta}"')
                    else:  # Linux
                        os.system(f'xdg-open "{ruta}"')
                else:
                    QMessageBox.warning(self, "Error", "El archivo PDF no existe")
            else:
                QMessageBox.warning(self, "Error", "No hay CV para abrir")

        except Exception as e:
            logger.error(f"Error al abrir PDF: {e}")
            QMessageBox.warning(self, "Error", f"No se pudo abrir el PDF: {str(e)}")
