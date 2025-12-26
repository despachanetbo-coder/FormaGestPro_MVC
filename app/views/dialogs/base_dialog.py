# app/views/dialogs/base_dialog.py

"""
BaseDialog - Clase base especializada para diálogos/formularios del sistema.
Hereda de BaseView para reutilizar estilos y funcionalidades comunes.

OBJETIVOS:

    Proporcionar una base consistente para todos los diálogos del sistema

    Centralizar la lógica común de formularios (validación, guardado, cancelación)

    Implementar estilos uniformes usando la configuración de BaseView

    Simplificar la creación de nuevos diálogos mediante herencia
"""

import logging
from typing import Dict, Any, Optional, List, Callable, Union, Tuple
from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFormLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QTextEdit,
    QDateEdit,
    QTimeEdit,
    QDateTimeEdit,
    QGroupBox,
    QFrame,
    QScrollArea,
    QMessageBox,
    QProgressBar,
    QListWidget,
    QTreeWidget,
    QTableWidget,
    QTabWidget,
    QToolButton,
    QRadioButton,
    QButtonGroup,
    QSlider,
    QProgressDialog,
    QDialogButtonBox,
    QSizePolicy,
    QSpacerItem,
    QFileDialog,
    QInputDialog,
    QFontComboBox,
    QCalendarWidget,
)
from PySide6.QtCore import (
    Qt,
    Signal,
    Slot,
    QDate,
    QTime,
    QDateTime,
    QSize,
    QTimer,
    QEvent,
    QPropertyAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
)
from PySide6.QtGui import (
    QFont,
    QPalette,
    QColor,
    QIcon,
    QPixmap,
    QBrush,
    QPen,
    QKeyEvent,
    QMouseEvent,
    QFocusEvent,
    QValidator,
    QIntValidator,
    QDoubleValidator,
    QRegularExpressionValidator,
)

# Importar la clase base

from app.views.base_view import BaseView

logger = logging.getLogger(name)


class BaseDialog(BaseView, QDialog):
    """
    Clase base para todos los diálogos y formularios del sistema.
    Combina la funcionalidad de BaseView (estilos, utilidades) con QDialog
    para crear diálogos consistentes y fáciles de mantener.

    Características principales:
    1. Sistema de campos de formulario estandarizado
    2. Validación automática de datos
    3. Gestión de estado (nuevo/edición/lectura)
    4. Animaciones y transiciones suaves
    5. Manejo de errores unificado
    """

    # ============ SEÑALES ESPECÍFICAS PARA DIÁLOGOS ============
    dialog_accepted = Signal(dict)  # Diálogo aceptado con datos
    dialog_rejected = Signal()  # Diálogo cancelado
    form_validated = Signal(bool, dict)  # Validación de formulario (éxito, errores)
    field_changed = Signal(str, object)  # Campo específico cambiado

    # ============ CONFIGURACIÓN ESPECÍFICA PARA DIÁLOGOS ============
    DIALOG_SIZES = {
        "small": (400, 300),
        "medium": (600, 450),
        "large": (800, 600),
        "xlarge": (1000, 750),
    }

    # Estilos CSS específicos para diálogos
    DIALOG_STYLES = {
        "QDialog": """
            QDialog {
                background-color: palette(window);
                border: 1px solid palette(mid);
                border-radius: 8px;
            }
        """,
        "QGroupBox": """
            QGroupBox {
                font-weight: bold;
                border: 2px solid palette(mid);
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """,
        "FormSection": """
            QFrame#FormSection {
                background-color: palette(base);
                border: 1px solid palette(midlight);
                border-radius: 5px;
                padding: 10px;
            }
        """,
    }

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        title: str = "Diálogo",
        dialog_size: str = "medium",
        mode: str = "create",  # "create", "edit", "view"
        initial_data: Optional[Dict] = None,
    ):
        """
        Inicializa el diálogo base.

        Args:
            parent: Widget padre
            title: Título del diálogo
            dialog_size: Tamaño predefinido (small, medium, large, xlarge)
            mode: Modo de operación (create, edit, view)
            initial_data: Datos iniciales para formulario (para modo edit/view)
        """
        # Inicializar ambas clases base
        QDialog.__init__(self, parent)
        BaseView.__init__(self, self, title)  # Pasamos self como parent para BaseView

        # Configuración específica del diálogo
        self._mode = mode
        self._initial_data = initial_data or {}
        self._form_data = {}
        self._form_fields = {}
        self._validation_errors = {}
        self._is_modified = False

        # Configurar ventana de diálogo
        self._setup_dialog_window(dialog_size)

        # Configurar interfaz base
        self._setup_dialog_ui()

        # Configurar validadores
        self._setup_validators()

        # Configurar conexiones
        self._setup_dialog_connections()

        # Cargar datos iniciales si existen
        if self._initial_data:
            self._load_initial_data()

        logger.debug(f"BaseDialog inicializado: {title} (modo: {mode})")

    # ============ CONFIGURACIÓN INICIAL ============

    def _setup_dialog_window(self, dialog_size: str):
        """Configura las propiedades de la ventana de diálogo"""
        # Establecer título
        self.setWindowTitle(self.view_title)

        # Establecer tamaño basado en configuración
        if dialog_size in self.DIALOG_SIZES:
            width, height = self.DIALOG_SIZES[dialog_size]
            self.resize(width, height)
        else:
            self.resize(600, 450)  # Tamaño por defecto

        # Configurar modalidad (por defecto, los diálogos son modales)
        self.setModal(True)

        # Configurar flags de ventana
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowTitleHint
        )

    def _setup_dialog_ui(self):
        """Configura la interfaz base del diálogo"""
        # Limpiar layout heredado de BaseView
        self._clear_layout(self.main_layout)

        # Configurar layout principal para diálogo
        self.main_layout.setContentsMargins(
            self.SIZES["padding_large"],
            self.SIZES["padding_large"],
            self.SIZES["padding_large"],
            self.SIZES["padding_large"],
        )
        self.main_layout.setSpacing(self.SIZES["spacing_medium"])

        # Crear área de scroll si es necesario
        self._create_scroll_area()

        # Crear sección de formulario
        self._create_form_section()

        # Crear sección de botones
        self._create_button_section()

        # Aplicar estilos específicos de diálogo
        self._apply_dialog_styles()

    def _create_scroll_area(self):
        """Crea un área de scroll para formularios largos"""
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        # Widget contenedor del contenido
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(self.SIZES["spacing_medium"])

        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area, 1)  # Factor de estiramiento 1

    def _create_form_section(self):
        """Crea la sección principal del formulario"""
        # Frame para el formulario
        self.form_frame = QFrame()
        self.form_frame.setObjectName("FormFrame")

        self.form_layout = QVBoxLayout(self.form_frame)
        self.form_layout.setContentsMargins(
            self.SIZES["padding_medium"],
            self.SIZES["padding_medium"],
            self.SIZES["padding_medium"],
            self.SIZES["padding_medium"],
        )
        self.form_layout.setSpacing(self.SIZES["spacing_large"])

        # Título del formulario
        self._create_form_title()

        # Contenedor para campos del formulario
        self.fields_container = QWidget()
        self.fields_layout = QFormLayout(self.fields_container)
        self.fields_layout.setContentsMargins(0, 0, 0, 0)
        self.fields_layout.setSpacing(self.SIZES["spacing_medium"])
        self.fields_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.form_layout.addWidget(self.fields_container)
        self.form_layout.addStretch()

        self.scroll_layout.addWidget(self.form_frame)

    def _create_form_title(self):
        """Crea el título del formulario"""
        title_text = self.view_title
        if self._mode == "edit":
            title_text = f"✏️ Editar - {title_text}"
        elif self._mode == "view":
            title_text = f"👁️ Ver - {title_text}"

        title_label = QLabel(title_text)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Configurar fuente del título
        font_family, font_size, font_weight = self.FONTS["title"]
        title_font = QFont(font_family, font_size)
        title_font.setWeight(font_weight)
        title_label.setFont(title_font)

        # Configurar color
        palette = title_label.palette()
        palette.setColor(title_label.foregroundRole(), QColor(self.COLORS["primary"]))
        title_label.setPalette(palette)

        # Estilo adicional
        title_label.setStyleSheet(
            f"""
            QLabel {{
                border-bottom: 2px solid {self.COLORS["secondary"]};
                padding-bottom: {self.SIZES["padding_medium"]}px;
                margin-bottom: {self.SIZES["spacing_medium"]}px;
            }}
        """
        )

        self.form_layout.addWidget(title_label)

    def _create_button_section(self):
        """Crea la sección de botones del diálogo"""
        button_frame = QFrame()
        button_frame.setObjectName("ButtonFrame")

        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(self.SIZES["spacing_medium"])

        # Botones estándar
        self.btn_accept = QPushButton(self._get_accept_button_text())
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_help = QPushButton("Ayuda")

        # Configurar botones
        self._setup_dialog_buttons()

        # Añadir botones al layout
        button_layout.addStretch()
        button_layout.addWidget(self.btn_help)
        button_layout.addWidget(self.btn_cancel)
        button_layout.addWidget(self.btn_accept)

        self.main_layout.addWidget(button_frame)

        # Guardar referencias
        self.widgets.update(
            {
                "btn_accept": self.btn_accept,
                "btn_cancel": self.btn_cancel,
                "btn_help": self.btn_help,
                "button_frame": button_frame,
            }
        )

    def _setup_dialog_buttons(self):
        """Configura los botones del diálogo"""
        # Botón Aceptar/Guardar
        self.btn_accept.setMinimumWidth(self.SIZES["button_min_width"])
        self.btn_accept.setMinimumHeight(self.SIZES["button_min_height"])

        if self._mode == "view":
            self.btn_accept.setText("Cerrar")
            self.btn_accept.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {self.COLORS["gray"]};
                    color: {self.COLORS["white"]};
                }}
            """
            )
        else:
            self.btn_accept.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {self.COLORS["success"]};
                    color: {self.COLORS["white"]};
                }}
            """
            )

        # Botón Cancelar
        self.btn_cancel.setMinimumWidth(self.SIZES["button_min_width"])
        self.btn_cancel.setMinimumHeight(self.SIZES["button_min_height"])
        self.btn_cancel.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self.COLORS["danger"]};
                color: {self.COLORS["white"]};
            }}
        """
        )

        # Botón Ayuda
        self.btn_help.setMinimumWidth(self.SIZES["button_min_width"] - 20)
        self.btn_help.setMinimumHeight(self.SIZES["button_min_height"])
        self.btn_help.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self.COLORS["info"]};
                color: {self.COLORS["white"]};
            }}
        """
        )

    def _apply_dialog_styles(self):
        """Aplica estilos específicos para diálogos"""
        # Combinar estilos de BaseView con estilos específicos de diálogo
        dialog_stylesheet = f"""
            #FormFrame {{
                background-color: {self.COLORS["white"]};
                border: 1px solid {self.COLORS["border"]};
                border-radius: {self.SIZES["border_radius"]}px;
            }}

            #ButtonFrame {{
                border-top: 1px solid {self.COLORS["border"]};
                padding-top: {self.SIZES["padding_medium"]}px;
            }}

            QScrollArea {{
                border: 1px solid {self.COLORS["border"]};
                border-radius: {self.SIZES["border_radius"]}px;
                background-color: {self.COLORS["background"]};
            }}

            QScrollBar:vertical {{
                width: 10px;
                background: {self.COLORS["light"]};
            }}

            QScrollBar::handle:vertical {{
                background: {self.COLORS["gray"]};
                min-height: 20px;
                border-radius: 5px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: {self.COLORS["gray_light"]};
            }}
        """

        self.setStyleSheet(self.styleSheet() + dialog_stylesheet)

    def _setup_validators(self):
        """Configura validadores comunes"""
        self.validators = {
            "required": lambda value, field: (
                bool(str(value).strip()) if field.get("required", False) else True
            ),
            "email": lambda value, field: (
                "@" in str(value) if field.get("type") == "email" else True
            ),
            "number": lambda value, field: (
                str(value).replace(".", "", 1).isdigit()
                if field.get("type") in ["number", "float"]
                else True
            ),
            "min_length": lambda value, field: len(str(value))
            >= field.get("min_length", 0),
            "max_length": lambda value, field: len(str(value))
            <= field.get("max_length", 255),
            "regex": lambda value, field: (
                bool(field.get("pattern", "").match(str(value)))
                if field.get("pattern")
                else True
            ),
        }

    def _setup_dialog_connections(self):
        """Configura las conexiones de señales del diálogo"""
        # Botones principales
        self.btn_accept.clicked.connect(self._on_accept)
        self.btn_cancel.clicked.connect(self._on_cancel)
        self.btn_help.clicked.connect(self._on_help)

        # Teclas de acceso rápido
        self.btn_accept.setShortcut("Ctrl+Return")
        self.btn_cancel.setShortcut("Escape")

        # Detectar cambios en el formulario
        self.fields_container.installEventFilter(self)

    def _load_initial_data(self):
        """Carga datos iniciales en el formulario"""
        if not self._initial_data:
            return

        for field_name, field_widget in self._form_fields.items():
            if field_name in self._initial_data:
                value = self._initial_data[field_name]
                self._set_widget_value(field_widget, value)

        # Si es modo vista, deshabilitar campos editables
        if self._mode == "view":
            self._set_readonly_mode(True)

    # ============ MÉTODOS PARA CREACIÓN DE CAMPOS ============

    def add_field(
        self,
        name: str,
        label: str,
        field_type: str = "text",
        default_value: Any = None,
        required: bool = False,
        **kwargs,
    ) -> QWidget:
        """
        Añade un campo al formulario.

        Args:
            name: Nombre interno del campo
            label: Etiqueta visible para el usuario
            field_type: Tipo de campo (text, number, date, combo, etc.)
            default_value: Valor por defecto
            required: Si el campo es obligatorio
            **kwargs: Configuración adicional específica del tipo de campo

        Returns:
            QWidget: Widget del campo creado
        """
        # Crear etiqueta
        field_label = QLabel(label)
        if required:
            field_label.setText(f"{label} *")
            field_label.setStyleSheet(
                f"color: {self.COLORS['danger']}; font-weight: bold;"
            )

        # Crear widget según el tipo
        field_widget = self._create_field_widget(field_type, **kwargs)

        # Configurar valor por defecto
        if default_value is not None:
            self._set_widget_value(field_widget, default_value)

        # Configurar propiedades del campo
        field_info = {
            "name": name,
            "label": label,
            "type": field_type,
            "required": required,
            "widget": field_widget,
            "config": kwargs,
        }

        # Conectar señales para detectar cambios
        self._connect_field_signals(field_widget, name)

        # Añadir al layout
        row = self.fields_layout.rowCount()
        self.fields_layout.addRow(field_label, field_widget)

        # Almacenar referencia
        self._form_fields[name] = field_widget
        self._form_data[name] = self._get_widget_value(field_widget)

        # Aplicar estilos según tipo
        self._apply_field_styles(field_widget, field_type)

        return field_widget

    def _create_field_widget(self, field_type: str, **kwargs) -> QWidget:
        """Crea un widget según el tipo de campo especificado"""
        if field_type == "text":
            widget = QLineEdit()
            widget.setPlaceholderText(kwargs.get("placeholder", ""))
            widget.setMaxLength(kwargs.get("max_length", 255))

        elif field_type == "password":
            widget = QLineEdit()
            widget.setEchoMode(QLineEdit.EchoMode.Password)
            widget.setPlaceholderText(kwargs.get("placeholder", ""))

        elif field_type == "number":
            widget = QSpinBox()
            widget.setRange(kwargs.get("min", 0), kwargs.get("max", 999999))
            widget.setValue(kwargs.get("default", 0))

        elif field_type == "float":
            widget = QDoubleSpinBox()
            widget.setRange(kwargs.get("min", 0.0), kwargs.get("max", 999999.99))
            widget.setDecimals(kwargs.get("decimals", 2))
            widget.setValue(kwargs.get("default", 0.0))

        elif field_type == "combo":
            widget = QComboBox()
            items = kwargs.get("items", [])
            widget.addItems(items)
            widget.setEditable(kwargs.get("editable", False))

        elif field_type == "checkbox":
            widget = QCheckBox(kwargs.get("text", ""))

        elif field_type == "date":
            widget = QDateEdit()
            widget.setCalendarPopup(True)
            widget.setDate(kwargs.get("default", QDate.currentDate()))

        elif field_type == "datetime":
            widget = QDateTimeEdit()
            widget.setCalendarPopup(True)
            widget.setDateTime(kwargs.get("default", QDateTime.currentDateTime()))

        elif field_type == "time":
            widget = QTimeEdit()
            widget.setTime(kwargs.get("default", QTime.currentTime()))

        elif field_type == "textarea":
            widget = QTextEdit()
            widget.setMaximumHeight(100)
            widget.setPlaceholderText(kwargs.get("placeholder", ""))

        elif field_type == "email":
            widget = QLineEdit()
            widget.setPlaceholderText("ejemplo@correo.com")

        elif field_type == "phone":
            widget = QLineEdit()
            widget.setPlaceholderText("+591 12345678")
            widget.setInputMask("+999 99999999")

        elif field_type == "currency":
            widget = QDoubleSpinBox()
            widget.setPrefix("$ ")
            widget.setRange(0, 9999999.99)
            widget.setDecimals(2)

        else:
            # Por defecto, campo de texto
            widget = QLineEdit()

        # Configuración común
        widget.setMinimumHeight(self.SIZES["input_height"])

        # Aplicar estilo base
        if field_type not in ["checkbox", "radio"]:
            widget.setStyleSheet(self.STYLES.get(f"Q{widget.__class__.__name__}", ""))

        return widget

    def add_field_group(
        self, title: str, fields: List[Dict], columns: int = 1
    ) -> QGroupBox:
        """
        Añade un grupo de campos al formulario.

        Args:
            title: Título del grupo
            fields: Lista de definiciones de campos
            columns: Número de columnas para disposición en grid

        Returns:
            QGroupBox: Grupo creado
        """
        group_box = QGroupBox(title)
        group_box.setObjectName("FieldGroup")

        if columns > 1:
            layout = QGridLayout()
            layout.setSpacing(self.SIZES["spacing_medium"])
            current_row, current_col = 0, 0

            for field_def in fields:
                widget = self.add_field(**field_def)
                layout.addWidget(
                    QLabel(
                        field_def.get("label", "")
                        + (" *" if field_def.get("required", False) else "")
                    ),
                    current_row,
                    current_col * 2,
                )
                layout.addWidget(widget, current_row, current_col * 2 + 1)

                current_col += 1
                if current_col >= columns:
                    current_col = 0
                    current_row += 1
        else:
            layout = QVBoxLayout()
            layout.setSpacing(self.SIZES["spacing_medium"])

            for field_def in fields:
                self.add_field(**field_def)
                # Los campos ya se añaden automáticamente al fields_layout

        group_box.setLayout(layout)
        self.form_layout.insertWidget(
            self.form_layout.count() - 1, group_box
        )  # Antes del stretch

        return group_box

    def add_tabbed_fields(self, tabs: List[Dict[str, Any]]) -> QTabWidget:
        """
        Añade campos organizados en pestañas.

        Args:
            tabs: Lista de definiciones de pestañas
                Ejemplo: [{"title": "Datos Personales", "fields": [...]}, ...]

        Returns:
            QTabWidget: Widget de pestañas creado
        """
        tab_widget = QTabWidget()

        for tab_def in tabs:
            tab_title = tab_def.get("title", "Sin título")
            tab_fields = tab_def.get("fields", [])

            tab_content = QWidget()
            tab_layout = QVBoxLayout(tab_content)
            tab_layout.setSpacing(self.SIZES["spacing_medium"])

            # Crear formulario dentro de la pestaña
            for field_def in tab_fields:
                field_widget = self.add_field(**field_def)
                tab_layout.addWidget(
                    QLabel(
                        field_def.get("label", "")
                        + (" *" if field_def.get("required", False) else "")
                    )
                )
                tab_layout.addWidget(field_widget)

            tab_layout.addStretch()
            tab_widget.addTab(tab_content, tab_title)

        self.form_layout.insertWidget(self.form_layout.count() - 1, tab_widget)

        return tab_widget

    # ============ MÉTODOS DE VALIDACIÓN ============

    def validate_form(self) -> Tuple[bool, Dict[str, str]]:
        """
        Valida todos los campos del formulario.

        Returns:
            Tuple[bool, Dict]: (es_válido, errores_por_campo)
        """
        self._validation_errors.clear()
        is_valid = True

        for field_name, field_widget in self._form_fields.items():
            field_valid, error_message = self._validate_field(field_name, field_widget)

            if not field_valid:
                is_valid = False
                self._validation_errors[field_name] = error_message
                self._highlight_field_error(field_widget, error_message)
            else:
                self._clear_field_error(field_widget)

        # Emitir señal de validación
        self.form_validated.emit(is_valid, self._validation_errors.copy())

        return is_valid, self._validation_errors

    def _validate_field(self, field_name: str, widget: QWidget) -> Tuple[bool, str]:
        """Valida un campo individual"""
        # Obtener información del campo
        field_info = self._get_field_info(field_name)
        if not field_info:
            return True, ""  # Campo no registrado, no validar

        value = self._get_widget_value(widget)
        required = field_info.get("required", False)
        field_type = field_info.get("type", "text")

        # Validar campo requerido
        if required:
            if value is None or (isinstance(value, str) and not value.strip()):
                return False, "Este campo es obligatorio"

        # Validaciones específicas por tipo
        if field_type == "email" and value:
            if "@" not in str(value) or "." not in str(value):
                return False, "Ingrese un correo electrónico válido"

        elif field_type in ["number", "float"] and value:
            try:
                float(value)
            except ValueError:
                return False, "Ingrese un número válido"

        elif field_type == "phone" and value:
            # Validación simple de teléfono
            digits = "".join(filter(str.isdigit, str(value)))
            if len(digits) < 8:
                return False, "Ingrese un número de teléfono válido"

        # Validación de longitud mínima/máxima
        if field_info.get("min_length") and value:
            if len(str(value)) < field_info["min_length"]:
                return False, f"Mínimo {field_info['min_length']} caracteres"

        if field_info.get("max_length") and value:
            if len(str(value)) > field_info["max_length"]:
                return False, f"Máximo {field_info['max_length']} caracteres"

        return True, ""

    def _highlight_field_error(self, widget: QWidget, error_message: str):
        """Resalta un campo con error"""
        widget.setStyleSheet(
            f"""
            {widget.styleSheet()}
            border: 2px solid {self.COLORS['danger']};
            background-color: {self.COLORS['danger']}15;
        """
        )

        # Añadir tooltip con el error
        widget.setToolTip(f"❌ {error_message}")

        # Si el widget tiene un QLineEdit interno (como en QComboBox)
        if isinstance(widget, QComboBox):
            widget.lineEdit().setStyleSheet(
                f"border: 2px solid {self.COLORS['danger']};"
            )

    def _clear_field_error(self, widget: QWidget):
        """Limpia el resaltado de error de un campo"""
        # Restaurar estilo original
        widget_type = widget.__class__.__name__
        original_style = self.STYLES.get(f"Q{widget_type}", "")
        widget.setStyleSheet(original_style)
        widget.setToolTip("")

        if isinstance(widget, QComboBox) and widget.lineEdit():
            widget.lineEdit().setStyleSheet("")

    # ============ MÉTODOS DE MANEJO DE DATOS ============

    def get_form_data(self) -> Dict[str, Any]:
        """
        Obtiene todos los datos del formulario.

        Returns:
            Dict: Datos del formulario
        """
        data = {}
        for field_name, field_widget in self._form_fields.items():
            data[field_name] = self._get_widget_value(field_widget)

        return data

    def set_form_data(self, data: Dict[str, Any]):
        """
        Establece datos en el formulario.

        Args:
            data: Diccionario con datos a establecer
        """
        for field_name, value in data.items():
            if field_name in self._form_fields:
                self._set_widget_value(self._form_fields[field_name], value)

    def _get_widget_value(self, widget: QWidget) -> Any:
        """Obtiene el valor de un widget según su tipo"""
        if isinstance(widget, QLineEdit):
            return widget.text().strip()
        elif isinstance(widget, QTextEdit):
            return widget.toPlainText().strip()
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            return widget.value()
        elif isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QCheckBox):
            return widget.isChecked()
        elif isinstance(widget, QDateEdit):
            return widget.date().toString("yyyy-MM-dd")
        elif isinstance(widget, QDateTimeEdit):
            return widget.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        elif isinstance(widget, QTimeEdit):
            return widget.time().toString("HH:mm:ss")
        else:
            return None

    def _set_widget_value(self, widget: QWidget, value: Any):
        """Establece el valor de un widget según su tipo"""
        if isinstance(widget, QLineEdit):
            widget.setText(str(value))
        elif isinstance(widget, QTextEdit):
            widget.setText(str(value))
        elif isinstance(widget, QSpinBox):
            widget.setValue(int(value))
        elif isinstance(widget, QDoubleSpinBox):
            widget.setValue(float(value))
        elif isinstance(widget, QComboBox):
            index = widget.findText(str(value))
            if index >= 0:
                widget.setCurrentIndex(index)
            else:
                widget.setCurrentText(str(value))
        elif isinstance(widget, QCheckBox):
            widget.setChecked(bool(value))
        elif isinstance(widget, QDateEdit):
            if isinstance(value, QDate):
                widget.setDate(value)
            else:
                widget.setDate(QDate.fromString(str(value), "yyyy-MM-dd"))
        elif isinstance(widget, QDateTimeEdit):
            if isinstance(value, QDateTime):
                widget.setDateTime(value)
            else:
                widget.setDateTime(
                    QDateTime.fromString(str(value), "yyyy-MM-dd HH:mm:ss")
                )
        elif isinstance(widget, QTimeEdit):
            if isinstance(value, QTime):
                widget.setTime(value)
            else:
                widget.setTime(QTime.fromString(str(value), "HH:mm:ss"))

    # ============ MÉTODOS DE EVENTOS ============

    def _on_accept(self):
        """Maneja la aceptación del diálogo"""
        # Validar formulario
        is_valid, errors = self.validate_form()

        if not is_valid:
            self._show_validation_errors(errors)
            return

        # Obtener datos del formulario
        form_data = self.get_form_data()

        # Ejecutar validación personalizada si existe
        if hasattr(self, "before_accept"):
            try:
                if not self.before_accept(form_data):
                    return
            except Exception as e:
                logger.error(f"Error en before_accept: {e}")
                self.show_error(f"Error en validación: {str(e)}")
                return

        # Emitir señal con datos
        self.dialog_accepted.emit(form_data)

        # Cerrar diálogo con éxito
        self.accept()

    def _on_cancel(self):
        """Maneja la cancelación del diálogo"""
        # Verificar si hay cambios sin guardar
        if self._is_modified and self._mode != "view":
            response = self.ask_confirmation(
                "¿Está seguro?",
                "Hay cambios sin guardar. ¿Desea cancelar de todas formas?",
            )
            if not response:
                return

        # Emitir señal de rechazo
        self.dialog_rejected.emit()

        # Cerrar diálogo
        self.reject()

    def _on_help(self):
        """Muestra ayuda del diálogo"""
        help_text = self._get_help_text()
        self.show_message("Ayuda", help_text, "info")

    def _show_validation_errors(self, errors: Dict[str, str]):
        """Muestra los errores de validación"""
        if not errors:
            return

        error_list = "\n".join(
            [f"• {field}: {error}" for field, error in errors.items()]
        )
        error_message = f"Por favor, corrija los siguientes errores:\n\n{error_list}"

        self.show_error("Errores de Validación", error_message)

        # Enfocar el primer campo con error
        first_error_field = next(iter(errors.keys()))
        if first_error_field in self._form_fields:
            self._form_fields[first_error_field].setFocus()

    # ============ MÉTODOS PROTEGIDOS PARA SOBRESCRIBIR ============

    def _get_accept_button_text(self) -> str:
        """Obtiene el texto del botón de aceptar según el modo"""
        if self._mode == "create":
            return "Guardar"
        elif self._mode == "edit":
            return "Actualizar"
        elif self._mode == "view":
            return "Cerrar"
        return "Aceptar"

    def _get_help_text(self) -> str:
        """Obtiene el texto de ayuda para el diálogo (sobrescribir en subclases)"""
        return f"Diálogo: {self.view_title}\n\nComplete todos los campos obligatorios (*) y haga clic en Guardar."

    def _connect_field_signals(self, widget: QWidget, field_name: str):
        """Conecta señales para detectar cambios en el campo"""
        if isinstance(widget, QLineEdit):
            widget.textChanged.connect(
                lambda text: self._on_field_changed(field_name, text)
            )
        elif isinstance(widget, QTextEdit):
            widget.textChanged.connect(
                lambda: self._on_field_changed(field_name, widget.toPlainText())
            )
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            widget.valueChanged.connect(
                lambda value: self._on_field_changed(field_name, value)
            )
        elif isinstance(widget, QComboBox):
            widget.currentTextChanged.connect(
                lambda text: self._on_field_changed(field_name, text)
            )
        elif isinstance(widget, QCheckBox):
            widget.stateChanged.connect(
                lambda state: self._on_field_changed(field_name, bool(state))
            )
        elif isinstance(widget, (QDateEdit, QDateTimeEdit, QTimeEdit)):
            widget.dateTimeChanged.connect(
                lambda: self._on_field_changed(
                    field_name, self._get_widget_value(widget)
                )
            )

    def _on_field_changed(self, field_name: str, value: Any):
        """Maneja el cambio en un campo"""
        self._is_modified = True
        self._form_data[field_name] = value
        self.field_changed.emit(field_name, value)

    def _get_field_info(self, field_name: str) -> Optional[Dict]:
        """Obtiene información de un campo (debe ser implementado en subclases)"""
        # Las subclases deben mantener un registro de la configuración de campos
        return None

    def _set_readonly_mode(self, readonly: bool):
        """Establece el modo de solo lectura para todos los campos"""
        for field_widget in self._form_fields.values():
            field_widget.setEnabled(not readonly)

        if readonly:
            self.btn_accept.setText("Cerrar")
            self.btn_accept.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {self.COLORS["gray"]};
                    color: {self.COLORS["white"]};
                }}
            """
            )

    # ============ MÉTODOS DE UTILIDAD ============

    def show(self) -> int:
        """Muestra el diálogo y retorna el resultado"""
        return self.exec()

    def center_on_screen(self):
        """Centra el diálogo en la pantalla"""
        screen_geometry = self.screen().availableGeometry()
        dialog_geometry = self.frameGeometry()

        center_point = screen_geometry.center()
        dialog_geometry.moveCenter(center_point)

        self.move(dialog_geometry.topLeft())

    def set_field_visible(self, field_name: str, visible: bool):
        """Muestra u oculta un campo"""
        if field_name in self._form_fields:
            self._form_fields[field_name].setVisible(visible)
            # También ocultar la etiqueta si existe
            for i in range(self.fields_layout.rowCount()):
                item = self.fields_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
                if item and item.widget():
                    if field_name in item.widget().text():
                        item.widget().setVisible(visible)

    def set_field_enabled(self, field_name: str, enabled: bool):
        """Habilita o deshabilita un campo"""
        if field_name in self._form_fields:
            self._form_fields[field_name].setEnabled(enabled)

    def clear_form(self):
        """Limpia todos los campos del formulario"""
        for field_widget in self._form_fields.values():
            self._set_widget_value(field_widget, None)

        self._validation_errors.clear()
        self._is_modified = False

    # ============ SOBRECARGA DE MÉTODOS DE BASEWIEW ============

    def show_message(
        self, title: str, message: str, message_type: str = "info"
    ) -> bool:
        """Muestra un mensaje en el diálogo"""
        # Convertir string a QMessageBox.Icon para BaseView
        icon_map = {
            "info": QMessageBox.Icon.Information,
            "warning": QMessageBox.Icon.Warning,
            "error": QMessageBox.Icon.Critical,
            "question": QMessageBox.Icon.Question,
        }

        icon = icon_map.get(message_type.lower(), QMessageBox.Icon.Information)
        return super().show_message(title, message, icon)

    def show_error(self, message: str):
        """Muestra un mensaje de error"""
        self.show_message("Error", message, "error")

    def show_success(self, message: str):
        """Muestra un mensaje de éxito"""
        self.show_message("Éxito", message, "info")

    def ask_confirmation(self, title: str, message: str) -> bool:
        """Pide confirmación al usuario"""
        return self.show_message(title, message, "question")
