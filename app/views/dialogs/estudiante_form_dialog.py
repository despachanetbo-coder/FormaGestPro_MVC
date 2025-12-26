# app/views/dialogs/estudiante_form_dialog.py
"""
Diálogo para formulario de estudiantes - Diseño limpio con tarjeta de foto
"""

import logging
import shutil
from datetime import datetime, date
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QDateEdit,
    QTextEdit,
    QMessageBox,
    QFileDialog,
    QCheckBox,
    QGroupBox,
    QRadioButton,
    QButtonGroup,
    QSpinBox,
    QDoubleSpinBox,
    QSizePolicy,
    QFrame,
    QWidget,
    QScrollArea,
)
from PySide6.QtCore import Qt, QDate, Signal, Slot, QSize
from PySide6.QtGui import QIcon, QPixmap, QFont, QPainter, QPen, QBrush, QColor

from app.models.estudiante_model import EstudianteModel
from app.views.base_view import BaseView

logger = logging.getLogger(__name__)


class EstudianteFormDialog(QDialog):
    """Diálogo para crear/editar estudiantes con diseño limpio y tarjeta de foto"""

    # Señales
    estudiante_guardado = Signal(dict)  # Para creación
    estudiante_actualizado = Signal(int, dict)  # Para edición (id, datos)
    estudiante_inscribir = Signal(dict)  # Para botón "Inscribir en Programa"
    estudiante_borrar = Signal(dict)  # Para botón "Eliminar"
    estudiante_editar = Signal(dict)  # Para botón "Editar" en modo lectura
    estudiante_mostrar_detalles = Signal(int)  # Solo necesita el ID

    def __init__(
        self, estudiante_id=None, estudiante_data=None, modo_lectura=False, parent=None
    ):
        """
        Inicializar diálogo de estudiante

        Args:
            estudiante_id: ID del estudiante (para edición/lectura). None para nuevo.
            estudiante_data: Diccionario con datos (opcional, para compatibilidad)
            modo_lectura: Si True, muestra en modo solo lectura
            parent: Widget padre
        """
        super().__init__(parent)

        # Inicialización de variables
        self._inicializar_variables(estudiante_id, estudiante_data, modo_lectura)

        # Configuración de la ventana
        self._configurar_ventana()

        # Configuración de la interfaz
        self.setup_ui()
        self.setup_connections()

        # Cargar datos si es necesario
        self._cargar_datos_iniciales()

    def _inicializar_variables(self, estudiante_id, estudiante_data, modo_lectura):
        """Inicializar variables internas del diálogo"""
        # Determinar ID y datos
        if estudiante_data and "id" in estudiante_data:
            self.estudiante_id = estudiante_data["id"]
            self.estudiante_data = estudiante_data
        else:
            self.estudiante_id = estudiante_id
            self.estudiante_data = {}

        self.modo_lectura = modo_lectura
        self.es_edicion = self.estudiante_id is not None

        # Variables para manejo de fotos
        self.ruta_foto_original = None
        self.ruta_foto_temp = None
        self.foto_modificada = False

        # Directorio para fotos
        self.directorio_fotos = Path("archivos/fotos_estudiantes")
        self.directorio_fotos.mkdir(parents=True, exist_ok=True)

    def _configurar_ventana(self):
        """Configurar propiedades de la ventana"""
        # Determinar título según modo
        if self.modo_lectura:
            self.setWindowTitle("👤 Detalles del Estudiante")
        elif self.es_edicion:
            self.setWindowTitle("✏️ Editar Estudiante")
        else:
            self.setWindowTitle("➕ Nuevo Estudiante")

        # Tamaño mínimo
        self.setMinimumWidth(900)
        self.setMinimumHeight(750)

    def _cargar_datos_iniciales(self):
        """Cargar datos iniciales según el modo"""
        # Cargar desde BD si es edición/lectura
        if self.es_edicion:
            self.cargar_datos_desde_bd()

        # Establecer modo lectura si corresponde
        if self.modo_lectura:
            self.set_readonly_mode(True)

    def setup_ui(self):
        """Configurar interfaz del diálogo con diseño limpio"""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Panel izquierdo - Formulario (70%)
        left_panel = self._crear_panel_formulario()

        # Panel derecho - Tarjeta de foto (30%)
        right_panel = self._crear_panel_foto()

        # Agregar paneles al layout principal
        main_layout.addWidget(left_panel, 7)  # 70% del espacio
        main_layout.addWidget(right_panel, 3)  # 30% del espacio

    def _crear_panel_formulario(self):
        """Crear panel izquierdo con el formulario de datos"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Título
        title_label = QLabel("📝 Información del Estudiante")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Si quieres centrarlo
        title_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {BaseView.COLORS["primary"]};
                padding: 8px 0;
                border-bottom: 2px solid {BaseView.COLORS["border"]};
                margin-bottom: 10px;
            }}
        """
        )
        layout.addWidget(title_label)

        # Área de scroll para el formulario
        form_scroll = QScrollArea()
        form_scroll.setWidgetResizable(True)
        form_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        form_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Estilo para la scroll area
        form_scroll.setStyleSheet(
            f"""
            QScrollArea {{
                border: 1px solid {BaseView.COLORS["border"]};
                border-radius: 5px;
                background-color: {BaseView.COLORS["white"]};
            }}
            QScrollBar:vertical {{
                border: none;
                background: {BaseView.COLORS["light"]};
                width: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {BaseView.COLORS["gray"]};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {BaseView.COLORS["gray_light"]};
            }}
        """
        )

        # Widget contenedor del formulario
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(15, 15, 15, 15)
        form_layout.setSpacing(20)  # Más espacio entre secciones

        # Agregar secciones del formulario
        form_layout.addWidget(self._crear_seccion_datos_personales())
        form_layout.addWidget(self._crear_seccion_contacto())
        form_layout.addWidget(self._crear_seccion_academica())

        # Agregar sección de estado si es edición/lectura
        if self.es_edicion or self.modo_lectura:
            form_layout.addWidget(self._crear_seccion_estado())

        form_layout.addStretch()

        # Configurar scroll area
        form_scroll.setWidget(form_widget)
        layout.addWidget(form_scroll)

        return panel

    def _crear_seccion_datos_personales(self):
        """Crear sección de datos personales"""
        group = QGroupBox("👤 Datos Personales")
        group.setStyleSheet(
            """
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
        """
        )

        form = QFormLayout()
        form.setSpacing(12)
        form.setContentsMargins(15, 20, 15, 20)

        # CI (Número + Expedición)
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

        # Fecha de nacimiento
        fecha_label = QLabel("Fecha de Nacimiento:")
        fecha_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.date_nacimiento = self._crear_date_edit()
        form.addRow(fecha_label, self.date_nacimiento)

        group.setLayout(form)
        return group

    def _crear_seccion_contacto(self):
        """Crear sección de información de contacto"""
        group = QGroupBox("📞 Información de Contacto")
        group.setStyleSheet(
            """
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
        """
        )

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

    def _crear_seccion_academica(self):
        """Crear sección de información académica"""
        group = QGroupBox("🎓 Información Académica")
        group.setStyleSheet(
            """
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
        """
        )

        form = QFormLayout()
        form.setSpacing(12)
        form.setContentsMargins(15, 20, 15, 20)

        # Universidad
        universidad_label = QLabel("Universidad de Egreso:")
        universidad_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.txt_universidad = self._crear_line_edit("Universidad Nacional Siglo XX")
        form.addRow(universidad_label, self.txt_universidad)

        # Profesión
        profesion_label = QLabel("Profesión/Ocupación:")
        profesion_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.txt_profesion = self._crear_line_edit("Ingeniero de Sistemas")
        form.addRow(profesion_label, self.txt_profesion)

        group.setLayout(form)
        return group

    def _crear_seccion_estado(self):
        """Crear sección de estado del estudiante"""
        # Determinar estado actual
        esta_activo = (
            self.estudiante_data.get("activo", 1) if self.estudiante_data else 1
        )

        # Definir colores según estado
        if esta_activo:
            color_borde = "#27ae60"  # Verde
            color_titulo = "#27ae60"
            texto_estado = "✅ ESTADO: ACTIVO"
        else:
            color_borde = "#e74c3c"  # Rojo
            color_titulo = "#e74c3c"
            texto_estado = "❌ ESTADO: INACTIVO"

        group = QGroupBox("📊 Estado del Estudiante")
        group.setStyleSheet(
            f"""
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
                color: {color_titulo};
            }}
        """
        )

        layout = QHBoxLayout()
        layout.setContentsMargins(15, 20, 15, 20)

        # Modo lectura: solo mostrar texto
        if self.modo_lectura:
            lbl_estado = QLabel(texto_estado)
            lbl_estado.setStyleSheet(
                f"""
                QLabel {{
                    font-size: 13px;
                    font-weight: bold;
                    padding: 10px 15px;
                    color: {color_titulo};
                    background-color: white;
                    border-radius: 6px;
                    border: 1px solid {color_borde};
                }}
            """
            )
            lbl_estado.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl_estado)

        # Modo edición: mostrar checkbox
        else:
            self.chk_activo = QCheckBox("Estudiante activo")
            self.chk_activo.setChecked(bool(esta_activo))
            self.chk_activo.setStyleSheet(
                """
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
                QCheckBox:hover {
                    background-color: #f8f9fa;
                    border-radius: 4px;
                }
            """
            )

            # Conectar señal para cambiar colores dinámicamente
            self.chk_activo.toggled.connect(self.actualizar_color_estado)
            layout.addWidget(self.chk_activo)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _crear_panel_foto(self):
        """Crear panel derecho con la tarjeta de foto"""
        panel = QWidget()
        panel.setFixedWidth(320)
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignTop)

        # Título
        card_title = QLabel("📸 Fotografía del Estudiante")
        card_title.setStyleSheet(
            """
            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px 0;
                text-align: center;
            }
        """
        )
        layout.addWidget(card_title)

        # Contenedor de la tarjeta
        card_container = QFrame()
        card_container.setMinimumHeight(380)
        card_container.setStyleSheet(
            """
            QFrame {
                border: 2px solid #dee2e6;
                border-radius: 10px;
                padding: 20px;
            }
        """
        )
        card_container.setFrameStyle(QFrame.Box | QFrame.Raised)

        card_layout = QVBoxLayout(card_container)
        card_layout.setSpacing(20)
        card_layout.setAlignment(Qt.AlignCenter)

        # Marco para la foto
        photo_frame = QFrame()
        photo_frame.setFixedSize(240, 240)
        photo_frame.setStyleSheet(
            """
            QFrame {
                background-color: #ffffff;
                border: 3px solid #2c3e50;
                border-radius: 10px;
                padding: 10px;
            }
        """
        )

        photo_layout = QVBoxLayout(photo_frame)
        photo_layout.setContentsMargins(5, 5, 5, 5)

        self.lbl_foto = QLabel()
        self.lbl_foto.setFixedSize(200, 200)
        self.lbl_foto.setStyleSheet(
            """
            QLabel {
                background-color: #ffffff;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """
        )
        self.lbl_foto.setAlignment(Qt.AlignCenter)
        self.lbl_foto.setText("FOTO\nDEL\nESTUDIANTE")
        self.lbl_foto.setWordWrap(True)

        photo_layout.addWidget(self.lbl_foto, alignment=Qt.AlignCenter)
        card_layout.addWidget(photo_frame, alignment=Qt.AlignCenter)

        # Botones para gestión de foto (solo en modo edición/creación)
        if not self.modo_lectura:
            self._agregar_botones_foto(card_layout)

        layout.addWidget(card_container)
        layout.addStretch()

        # Área de botones (inferior)
        layout.addWidget(self._crear_area_botones())

        return panel

    def _agregar_botones_foto(self, layout):
        """Agregar botones para gestión de fotos"""
        button_frame = QWidget()
        button_layout = QVBoxLayout(button_frame)
        button_layout.setSpacing(10)

        # Botón seleccionar foto
        self.btn_seleccionar_foto = QPushButton("📁 Seleccionar Foto")
        self.btn_seleccionar_foto.setFixedHeight(40)
        self.btn_seleccionar_foto.setStyleSheet(
            """
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
        """
        )
        self.btn_seleccionar_foto.setToolTip(
            "Seleccionar imagen JPG/JPEG del estudiante"
        )

        # Botón eliminar foto
        self.btn_eliminar_foto = QPushButton("🗑️ Eliminar Foto")
        self.btn_eliminar_foto.setFixedHeight(40)
        self.btn_eliminar_foto.setStyleSheet(
            """
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
        """
        )
        self.btn_eliminar_foto.setEnabled(False)
        self.btn_eliminar_foto.setToolTip("Eliminar la foto seleccionada")

        button_layout.addWidget(self.btn_seleccionar_foto)
        button_layout.addWidget(self.btn_eliminar_foto)

        layout.addWidget(button_frame)

        # Información de la foto
        info_label = QLabel("Formato: JPG/JPEG\nTamaño recomendado: 300x300 px")
        info_label.setStyleSheet(
            """
            QLabel {
                color: #7f8c8d;
                font-size: 11px;
                text-align: center;
                padding: 8px;
                background-color: #ffffff;
                border-radius: 4px;
                border: 1px dashed #bdc3c7;
            }
        """
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)

        layout.addWidget(info_label)
        layout.addStretch()

    def _crear_area_botones(self):
        """Crear área de botones según el modo"""
        area = QFrame()
        area.setStyleSheet(
            """
            QFrame {
                border: 2px solid #dee2e6;
                border-radius: 10px;
                padding: 15px 0;
            }
        """
        )

        layout = QVBoxLayout(area)
        layout.setSpacing(10)

        # Botones para modo edición/creación
        if not self.modo_lectura:
            self.btn_guardar = self._crear_boton(
                "💾 Guardar", "#f39c12", "#e67e22", "#d35400"
            )
            self.btn_cancelar = self._crear_boton(
                "❌ Cancelar", "#e74c3c", "#c0392b", "#a93226", es_principal=True
            )

            layout.addWidget(self.btn_guardar)
            layout.addWidget(self.btn_cancelar)

        # Botones para modo lectura
        else:
            self.btn_inscribir = self._crear_boton(
                "🎓 Inscribir", "#9b59b6", "#8e44ad", "#7d3c98"
            )
            self.btn_editar = self._crear_boton(
                "✏️ Editar", "#27ae60", "#219653", "#1e8449"
            )
            self.btn_borrar = self._crear_boton(
                "🗑️ Eliminar Estudiante",
                "#e74c3c",
                "#c0392b",
                "#a93226",
                es_principal=True,
            )
            self.btn_cerrar = self._crear_boton(
                "✖️ Cerrar Vista", "#e74c3c", "#c0392b", "#a93226", es_principal=True
            )

            self.btn_inscribir.setToolTip(
                "Matricular este estudiante en un programa académico"
            )
            self.btn_editar.setToolTip("Editar los datos de este estudiante")
            self.btn_borrar.setToolTip("Eliminar este estudiante del sistema")
            self.btn_cerrar.setToolTip("Cerrar esta ventana")

            layout.addWidget(self.btn_inscribir)
            layout.addWidget(self.btn_editar)
            layout.addWidget(self.btn_borrar)
            layout.addWidget(self.btn_cerrar)

        return area

    def _crear_line_edit(self, placeholder, max_width=400):
        """Crear QLineEdit con estilo consistente"""
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        if max_width:
            line_edit.setMaximumWidth(max_width)
        line_edit.setFixedHeight(36)
        line_edit.setStyleSheet(
            """
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """
        )
        return line_edit

    def _crear_combo_expedicion(self):
        """Crear combo box para expedición de CI"""
        combo = QComboBox()
        combo.addItems(["BE", "CH", "CB", "LP", "OR", "PD", "PT", "SC", "TJ", "EX"])
        combo.setFixedHeight(36)
        combo.setFixedWidth(80)
        combo.setStyleSheet(
            """
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 13px;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
        """
        )
        return combo

    def _crear_date_edit(self):
        """Crear QDateEdit con estilo consistente"""
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate(1990, 1, 1))
        date_edit.setMaximumDate(QDate.currentDate())
        date_edit.setMaximumWidth(400)
        date_edit.setFixedHeight(36)
        date_edit.setStyleSheet(
            """
            QDateEdit {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 13px;
            }
            QDateEdit:focus {
                border: 2px solid #3498db;
            }
        """
        )
        return date_edit

    def _crear_boton(
        self, texto, color_normal, color_hover, color_pressed, es_principal=False
    ):
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
        # Conexiones según modo
        if not self.modo_lectura:
            if hasattr(self, "btn_guardar"):
                self.btn_guardar.clicked.connect(self.validar_y_guardar)

            if hasattr(self, "btn_cancelar"):
                self.btn_cancelar.clicked.connect(self.reject)

            # Conexiones para fotografía
            if hasattr(self, "btn_seleccionar_foto"):
                self.btn_seleccionar_foto.clicked.connect(self.seleccionar_foto)

            if hasattr(self, "btn_eliminar_foto"):
                self.btn_eliminar_foto.clicked.connect(self.eliminar_foto)

        else:
            # MODO LECTURA - CORREGIDO: sin paréntesis
            if hasattr(self, "btn_inscribir"):
                self.btn_inscribir.clicked.connect(
                    self.on_inscribir_clicked
                )  # <-- SIN ()

            if hasattr(self, "btn_editar"):
                self.btn_editar.clicked.connect(self.on_editar_clicked)

            if hasattr(self, "btn_borrar"):
                self.btn_borrar.clicked.connect(self.on_borrar_clicked)

            if hasattr(self, "btn_cerrar"):
                self.btn_cerrar.clicked.connect(self.accept)

    # ============================================================================
    # MÉTODOS PARA MANEJO DE DATOS
    # ============================================================================

    def cargar_datos_desde_bd(self):
        """Cargar datos del estudiante directamente desde la base de datos"""
        try:
            if not self.estudiante_id:
                return

            from app.models.estudiante_model import EstudianteModel

            estudiante = EstudianteModel.find_by_id(self.estudiante_id)
            if not estudiante:
                QMessageBox.critical(self, "Error", "Estudiante no encontrado")
                self.reject()
                return

            # Convertir a diccionario con todos los campos
            self.estudiante_data = {
                "id": estudiante.id,
                "ci_numero": estudiante.ci_numero,
                "ci_expedicion": estudiante.ci_expedicion,
                "nombres": estudiante.nombres,
                "apellidos": estudiante.apellidos,
                "fecha_nacimiento": estudiante.fecha_nacimiento,
                "telefono": getattr(estudiante, "telefono", ""),
                "email": getattr(estudiante, "email", ""),
                "universidad_egreso": getattr(estudiante, "universidad_egreso", ""),
                "profesion": getattr(estudiante, "profesion", ""),
                "fotografia_path": getattr(estudiante, "fotografia_path", None),
                "activo": getattr(estudiante, "activo", 1),
            }

            # Guardar ruta original de la foto
            self.ruta_foto_original = self.estudiante_data["fotografia_path"]

            # Cargar datos en la UI
            self.cargar_datos()

        except Exception as e:
            logger.error(f"Error al cargar datos del estudiante desde BD: {e}")
            QMessageBox.critical(self, "Error", f"Error al cargar datos: {str(e)}")
            self.reject()

    def cargar_datos(self):
        """Cargar datos del estudiante en los campos del formulario"""
        try:
            if not self.estudiante_data:
                return

            # Información personal
            self.txt_ci_numero.setText(str(self.estudiante_data.get("ci_numero", "")))

            expedicion = self.estudiante_data.get("ci_expedicion", "BE")
            index = self.combo_expedicion.findText(expedicion)
            if index >= 0:
                self.combo_expedicion.setCurrentIndex(index)

            self.txt_nombres.setText(str(self.estudiante_data.get("nombres", "")))
            self.txt_apellidos.setText(str(self.estudiante_data.get("apellidos", "")))

            # Fecha de nacimiento
            fecha_nac = self.estudiante_data.get("fecha_nacimiento")
            if fecha_nac:
                if isinstance(fecha_nac, str):
                    try:
                        fecha_date = datetime.strptime(fecha_nac, "%Y-%m-%d").date()
                        qdate = QDate(fecha_date.year, fecha_date.month, fecha_date.day)
                        self.date_nacimiento.setDate(qdate)
                    except Exception as e:
                        logger.warning(f"Error parseando fecha: {e}")
                elif isinstance(fecha_nac, date):
                    qdate = QDate(fecha_nac.year, fecha_nac.month, fecha_nac.day)
                    self.date_nacimiento.setDate(qdate)

            # Información de contacto
            self.txt_telefono.setText(str(self.estudiante_data.get("telefono", "")))
            self.txt_email.setText(str(self.estudiante_data.get("email", "")))

            # Información académica
            self.txt_universidad.setText(
                str(self.estudiante_data.get("universidad_egreso", ""))
            )
            self.txt_profesion.setText(str(self.estudiante_data.get("profesion", "")))

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
            datos["ci_numero"] = ci_numero

        datos["ci_expedicion"] = self.combo_expedicion.currentText()

        nombres = self.txt_nombres.text().strip()
        if not nombres:
            errores.append("Los nombres son obligatorios")
        elif len(nombres) < 2:
            errores.append("Los nombres deben tener al menos 2 caracteres")
        else:
            datos["nombres"] = nombres

        apellidos = self.txt_apellidos.text().strip()
        if not apellidos:
            errores.append("Los apellidos son obligatorios")
        elif len(apellidos) < 2:
            errores.append("Los apellidos deben tener al menos 2 caracteres")
        else:
            datos["apellidos"] = apellidos

        # Fecha de nacimiento
        fecha_nac = self.date_nacimiento.date()
        if fecha_nac.isValid():
            datos["fecha_nacimiento"] = fecha_nac.toString("yyyy-MM-dd")

        # Contacto
        telefono = self.txt_telefono.text().strip()
        if telefono:
            datos["telefono"] = telefono

        email = self.txt_email.text().strip()
        if email:
            if "@" not in email or "." not in email.split("@")[-1]:
                errores.append("Formato de email inválido")
            else:
                datos["email"] = email.lower()

        # Información académica
        universidad = self.txt_universidad.text().strip()
        if universidad:
            datos["universidad_egreso"] = universidad

        profesion = self.txt_profesion.text().strip()
        if profesion:
            datos["profesion"] = profesion

        # Estado
        if hasattr(self, "chk_activo"):
            datos["activo"] = 1 if self.chk_activo.isChecked() else 0

        # Procesar foto
        if ci_numero:
            if self.foto_modificada:
                if self.ruta_foto_temp:
                    ruta_foto = self.procesar_foto(ci_numero)
                    if ruta_foto:
                        datos["fotografia_path"] = ruta_foto
                    else:
                        errores.append("No se pudo guardar la fotografía")
                else:
                    datos["fotografia_path"] = None
            elif self.ruta_foto_original:
                datos["fotografia_path"] = self.ruta_foto_original

        # Incluir ID si es edición
        if self.es_edicion and self.estudiante_id:
            datos["id"] = self.estudiante_id

        return errores, datos

    def validar_y_guardar(self):
        """Validar y guardar los datos del estudiante directamente en la BD"""
        errores, datos = self.obtener_datos_formulario()

        if errores:
            QMessageBox.warning(self, "Validación", "\n".join(errores))
            return

        try:
            from app.models.estudiante_model import EstudianteModel

            if self.es_edicion:
                # ACTUALIZAR
                estudiante = EstudianteModel.find_by_id(datos["id"])
                if estudiante:
                    # Actualizar todos los campos
                    for campo, valor in datos.items():
                        if campo != "id" and hasattr(estudiante, campo):
                            setattr(estudiante, campo, valor)
                    estudiante.save()
                    mensaje = "✅ Estudiante actualizado correctamente"
                else:
                    QMessageBox.warning(self, "Error", "Estudiante no encontrado")
                    return
            else:
                # CREAR
                estudiante = EstudianteModel(**datos)
                estudiante.save()
                datos["id"] = estudiante.id
                mensaje = "✅ Estudiante creado correctamente"

            # Mostrar mensaje
            QMessageBox.information(self, "Éxito", mensaje)

            # Cerrar este diálogo
            self.accept()

            # Notificar al padre para que actualice la tabla
            # (Si el diálogo fue abierto desde EstudiantesTab)
            if hasattr(self.parent(), "cargar_estudiantes"):
                self.parent().cargar_estudiantes()

            # Abrir nuevo diálogo en modo lectura
            self._abrir_modo_lectura(datos["id"])

        except Exception as e:
            logger.error(f"Error al guardar estudiante: {e}")
            QMessageBox.critical(
                self, "Error", f"Error al guardar estudiante: {str(e)}"
            )

    def _abrir_modo_lectura(self, estudiante_id):
        """Abrir diálogo en modo lectura"""
        try:
            from app.models.estudiante_model import EstudianteModel
            from app.views.dialogs.estudiante_form_dialog import EstudianteFormDialog

            estudiante = EstudianteModel.find_by_id(estudiante_id)
            if estudiante:
                datos = {
                    "id": estudiante.id,
                    "ci_numero": estudiante.ci_numero,
                    "ci_expedicion": estudiante.ci_expedicion,
                    "nombres": estudiante.nombres,
                    "apellidos": estudiante.apellidos,
                    "fecha_nacimiento": estudiante.fecha_nacimiento,
                    "telefono": getattr(estudiante, "telefono", ""),
                    "email": getattr(estudiante, "email", ""),
                    "universidad_egreso": getattr(estudiante, "universidad_egreso", ""),
                    "profesion": getattr(estudiante, "profesion", ""),
                    "fotografia_path": getattr(estudiante, "fotografia_path", None),
                    "activo": getattr(estudiante, "activo", 1),
                }

                dialog = EstudianteFormDialog(
                    estudiante_data=datos, modo_lectura=True, parent=self.parent()
                )

                # Conectar señal de editar
                if hasattr(self.parent(), "on_editar_desde_modo_lectura"):
                    dialog.estudiante_editar.connect(
                        self.parent().on_editar_desde_modo_lectura
                    )

                dialog.exec()

        except Exception as e:
            logger.error(f"Error al abrir en modo lectura: {e}")

    # ============================================================================
    # MÉTODOS PARA MANEJO DE FOTOGRAFÍAS
    # ============================================================================

    def cargar_foto(self, ruta):
        """Cargar y mostrar fotografía en la tarjeta"""
        try:
            if not ruta:
                self.lbl_foto.setText("Sin\nfoto")
                return

            ruta_path = Path(ruta)
            if not ruta_path.exists():
                # Intentar buscar en el directorio de fotos
                nombre_archivo = ruta_path.name
                ruta_alternativa = self.directorio_fotos / nombre_archivo
                if ruta_alternativa.exists():
                    self.cargar_foto(str(ruta_alternativa))
                    return
                else:
                    self.lbl_foto.setText("Sin\nfoto")
                    return

            pixmap = QPixmap(str(ruta_path))
            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.lbl_foto.setPixmap(pixmap)
                self.lbl_foto.setText("")
                self.ruta_foto_temp = str(ruta_path)
            else:
                self.lbl_foto.setText("Imagen\nno válida")

        except Exception as e:
            logger.error(f"Error al cargar foto: {e}")
            self.lbl_foto.setText("Error\ncargando")

    def seleccionar_foto(self):
        """Seleccionar archivo de fotografía JPG"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Seleccionar Fotografía del Estudiante")
        file_dialog.setNameFilter("Imágenes JPG (*.jpg *.jpeg)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec():
            archivos = file_dialog.selectedFiles()
            if archivos:
                ruta_origen = archivos[0]

                if not ruta_origen.lower().endswith((".jpg", ".jpeg")):
                    QMessageBox.warning(
                        self,
                        "Formato no válido",
                        "Por favor, seleccione una imagen en formato JPG o JPEG.",
                    )
                    return

                self.cargar_foto(ruta_origen)
                self.foto_modificada = True
                self.ruta_foto_temp = ruta_origen
                self.btn_eliminar_foto.setEnabled(True)

                logger.info(f"Foto seleccionada: {ruta_origen}")

    def eliminar_foto(self):
        """Eliminar fotografía seleccionada y el archivo físico si existe"""
        try:
            respuesta = QMessageBox.question(
                self,
                "Eliminar Foto",
                "¿Eliminar la fotografía del estudiante?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if respuesta != QMessageBox.Yes:
                return

            # Eliminar archivo físico si existe
            if self.ruta_foto_original:
                ruta_path = Path(self.ruta_foto_original)
                if (
                    ruta_path.exists()
                    and ruta_path.is_file()
                    and self.directorio_fotos in ruta_path.parents
                ):
                    try:
                        ruta_path.unlink()
                    except Exception as e:
                        logger.warning(f"No se pudo eliminar archivo físico: {e}")

            # Resetear variables
            self.ruta_foto_temp = None
            self.ruta_foto_original = None
            self.foto_modificada = True

            # Actualizar UI
            self.lbl_foto.clear()
            self.lbl_foto.setText("FOTO\nDEL\nESTUDIANTE")
            self.btn_eliminar_foto.setEnabled(False)

            QMessageBox.information(self, "Éxito", "Foto eliminada correctamente")

        except Exception as e:
            logger.error(f"Error al eliminar foto: {e}")
            QMessageBox.warning(self, "Error", f"Error al eliminar foto: {str(e)}")

    def procesar_foto(self, ci_numero):
        """
        Procesar la foto: copiarla al directorio de fotos con nombre generado

        Args:
            ci_numero: Número de CI para nombrar el archivo

        Returns:
            Ruta absoluta del archivo generado o None si no hay foto
        """
        if not self.ruta_foto_temp:
            return None

        try:
            # Generar nombre de archivo
            nombre_archivo = f"f_e_{ci_numero}.jpg"
            ruta_destino = self.directorio_fotos / nombre_archivo

            # Eliminar foto anterior si existe
            if self.ruta_foto_original:
                ruta_anterior = Path(self.ruta_foto_original)
                if (
                    ruta_anterior.exists()
                    and ruta_anterior != ruta_destino
                    and self.directorio_fotos in ruta_anterior.parents
                ):
                    try:
                        ruta_anterior.unlink()
                    except Exception as e:
                        logger.warning(f"No se pudo eliminar foto anterior: {e}")

            # Si el archivo ya existe, sobrescribirlo
            if ruta_destino.exists():
                ruta_destino.unlink()

            # Copiar la foto
            shutil.copy2(self.ruta_foto_temp, ruta_destino)

            logger.info(f"Foto guardada en: {ruta_destino}")
            return str(ruta_destino.absolute())

        except Exception as e:
            logger.error(f"Error al guardar foto: {e}")
            QMessageBox.warning(self, "Error", f"No se pudo guardar la foto: {str(e)}")
            return None

    # ============================================================================
    # MÉTODOS PARA MANEJO DE EVENTOS Y UI
    # ============================================================================

    def showEvent(self, event):
        """Evento que se ejecuta cuando el diálogo se muestra"""
        super().showEvent(event)

        # Cargar la foto después de que la UI esté completamente configurada
        if self.estudiante_data:
            self.cargar_foto_despues_de_ui()

    def cargar_foto_despues_de_ui(self):
        """Cargar la foto después de que la UI esté configurada"""
        try:
            ruta_foto = self.estudiante_data.get("fotografia_path")
            if ruta_foto:
                self.ruta_foto_original = ruta_foto
                self.ruta_foto_temp = ruta_foto
                self.cargar_foto(ruta_foto)

                # Solo habilitar btn_eliminar_foto si existe (en modo edición)
                if hasattr(self, "btn_eliminar_foto"):
                    self.btn_eliminar_foto.setEnabled(True)
            else:
                self.lbl_foto.setText("Sin\nfoto")

        except Exception as e:
            logger.error(f"Error cargando foto después de UI: {e}")

    def set_readonly_mode(self, readonly=True):
        """Establecer todos los campos en modo solo lectura"""
        widgets = [
            self.txt_ci_numero,
            self.combo_expedicion,
            self.txt_nombres,
            self.txt_apellidos,
            self.date_nacimiento,
            self.txt_telefono,
            self.txt_email,
            self.txt_universidad,
            self.txt_profesion,
        ]

        for widget in widgets:
            if hasattr(widget, "setReadOnly"):
                widget.setReadOnly(readonly)
            if hasattr(widget, "setEnabled"):
                widget.setEnabled(not readonly)

        # Deshabilitar botones de foto en modo lectura
        if hasattr(self, "btn_seleccionar_foto"):
            self.btn_seleccionar_foto.setEnabled(not readonly)

        if hasattr(self, "btn_eliminar_foto"):
            tiene_foto = bool(self.ruta_foto_temp) or bool(self.ruta_foto_original)
            self.btn_eliminar_foto.setEnabled(not readonly and tiene_foto)

    def actualizar_color_estado(self, checked):
        """Actualizar color del grupo estado cuando cambia el checkbox"""
        if not hasattr(self, "chk_activo"):
            return

        for widget in self.findChildren(QGroupBox):
            if widget.title() == "📊 Estado del Estudiante":
                if checked:
                    color_borde = "#27ae60"
                    color_titulo = "#27ae60"
                else:
                    color_borde = "#e74c3c"
                    color_titulo = "#e74c3c"

                widget.setStyleSheet(
                    f"""
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
                        color: {color_titulo};
                    }}
                """
                )
                break

    # ============================================================================
    # MANEJADORES DE BOTONES (MODO LECTURA)
    # ============================================================================

    def on_inscribir_clicked(self):
        """Abrir diálogo para inscribir al estudiante - VERSIÓN ROBUSTA"""
        try:
            # Intentar obtener el ID del estudiante de múltiples formas
            estudiante_id = None

            # 1. Intentar desde self.estudiante si existe
            if (
                hasattr(self, "estudiante")
                and self.estudiante
                and hasattr(self.estudiante, "id")
            ):
                estudiante_id = self.estudiante.id
                logger.debug(f"ID obtenido de self.estudiante: {estudiante_id}")

            # 2. Si no, intentar desde self.estudiante_data
            elif hasattr(self, "estudiante_data") and self.estudiante_data:
                estudiante_id = self.estudiante_data.get("id")
                logger.debug(f"ID obtenido de self.estudiante_data: {estudiante_id}")

            # 3. Si no, intentar desde self.estudiante_id
            elif hasattr(self, "estudiante_id") and self.estudiante_id:
                estudiante_id = self.estudiante_id
                logger.debug(f"ID obtenido de self.estudiante_id: {estudiante_id}")

            # Verificar que tenemos un ID válido
            if not estudiante_id:
                logger.error("No se pudo obtener ID del estudiante")
                QMessageBox.warning(
                    self, "Error", "No se pudo identificar al estudiante."
                )
                return

            logger.info(f"Iniciando matrícula para estudiante ID: {estudiante_id}")

            # Importar diálogo de matrícula
            try:
                from app.views.dialogs.matricula_estudiante_form_dialog import (
                    MatriculaEstudianteFormDialog,
                )
            except ImportError as e:
                logger.error(f"Error importando MatriculaEstudianteFormDialog: {e}")
                QMessageBox.critical(
                    self,
                    "Error del Sistema",
                    f"No se pudo cargar el módulo de matrícula.\n\nError: {str(e)}",
                )
                return

            # Crear y mostrar diálogo
            dialog = MatriculaEstudianteFormDialog(
                estudiante_id=estudiante_id, parent=self
            )

            # Intentar obtener nombre para personalizar título
            nombre_estudiante = ""
            if hasattr(self, "estudiante") and self.estudiante:
                if hasattr(self.estudiante, "nombres") and hasattr(
                    self.estudiante, "apellidos"
                ):
                    nombre_estudiante = (
                        f"{self.estudiante.nombres} {self.estudiante.apellidos}"
                    )
            elif hasattr(self, "estudiante_data") and self.estudiante_data:
                nombres = self.estudiante_data.get("nombres", "")
                apellidos = self.estudiante_data.get("apellidos", "")
                nombre_estudiante = f"{nombres} {apellidos}"

            if nombre_estudiante.strip():
                dialog.setWindowTitle(f"Matricular a: {nombre_estudiante.strip()}")

            # Ejecutar diálogo
            result = dialog.exec()

            if result == QDialog.DialogCode.Accepted:
                QMessageBox.information(
                    self,
                    "✅ Matrícula Exitosa",
                    "El estudiante ha sido matriculado correctamente.",
                )

        except Exception as e:
            logger.error(f"Error abriendo diálogo de matrícula: {e}", exc_info=True)
            QMessageBox.critical(
                self, "Error", f"No se pudo abrir el diálogo de matrícula:\n\n{str(e)}"
            )

    def on_editar_clicked(self):
        """Manejador para botón Editar"""
        try:
            self.estudiante_editar.emit(self.estudiante_data)
            self.accept()
        except Exception as e:
            logger.error(f"Error al procesar edición: {e}")
            QMessageBox.critical(self, "Error", f"Error al editar estudiante: {str(e)}")

    def on_borrar_clicked(self):
        """Manejador para botón Eliminar"""
        respuesta = QMessageBox.question(
            self,
            "🗑️ Confirmar Eliminación",
            f"¿Está seguro de eliminar al estudiante?\n\n"
            f"Nombre: {self.estudiante_data.get('nombres', '')} {self.estudiante_data.get('apellidos', '')}\n"
            f"CI: {self.estudiante_data.get('ci_numero', '')}-{self.estudiante_data.get('ci_expedicion', '')}\n\n"
            f"⚠️ Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Nover,
        )

        if respuesta == QMessageBox.Yes:
            try:
                self.estudiante_borrar.emit(self.estudiante_data)
                self.accept()
            except Exception as e:
                logger.error(f"Error al eliminar estudiante: {e}")
                QMessageBox.critical(
                    self, "Error", f"Error al eliminar estudiante: {str(e)}"
                )
