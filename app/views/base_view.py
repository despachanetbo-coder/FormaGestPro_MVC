# app/views/base_view.py
"""
Clase base para vistas con estilos consistentes en PySide6.
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QHeaderView,
    QMessageBox,
    QDialog,
    QFormLayout,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QScrollArea,
    QSizePolicy,
    QToolBar,
    QStatusBar,
    QApplication,
    QStyle,
)
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QFontDatabase
import sys

logger = logging.getLogger(__name__)


class BaseView(QWidget):
    """Clase base para todas las vistas/páginas del sistema en PySide6"""

    # ============ SEÑALES ============
    data_changed = Signal()
    view_refreshed = Signal()

    # ============ CONFIGURACIÓN CENTRALIZADA ============

    # Paleta de colores del sistema (Qt)
    COLORS = {
        # Colores primarios (azules)
        "primary": "#2C3E50",
        "primary_light": "#34495E",
        "primary_dark": "#1A252F",
        # Colores secundarios
        "secondary": "#3498DB",
        "success": "#27AE60",
        "warning": "#F39C12",
        "danger": "#E74C3C",
        "info": "#17A2B8",
        # Colores neutros
        "light": "#ECF0F1",
        "dark": "#2C3E50",
        "gray": "#95A5A6",
        "gray_light": "#BDC3C7",
        "white": "#FFFFFF",
        "black": "#000000",
        # Estados
        "hover": "#2980B9",
        "pressed": "#21618C",
        "disabled": "#BDC3C7",
        # Componentes específicos
        "background": "#F5F7FA",
        "card_background": "#FFFFFF",
        "border": "#D1D5DB",
        "tree_odd": "#F8F9F9",
        "tree_even": "#FFFFFF",
        "selection": "#3498DB",
    }

    # Configuración de fuentes
    # Configuración de fuentes CORREGIDA
    FONTS = {
        "title": ("Segoe UI", 16, QFont.Weight.Bold),
        "subtitle": ("Segoe UI", 14, QFont.Weight.Bold),
        "header": ("Segoe UI", 12, QFont.Weight.Bold),
        "normal": ("Segoe UI", 10, QFont.Weight.Normal),
        "small": ("Segoe UI", 9, QFont.Weight.Normal),
        "monospace": ("Consolas", 10, QFont.Weight.Normal),
    }

    # Tamaños y dimensiones
    SIZES = {
        "button_min_width": 100,
        "button_min_height": 32,
        "input_height": 32,
        "tree_row_height": 28,
        "icon_size": 20,
        "padding_small": 4,
        "padding_medium": 8,
        "padding_large": 16,
        "spacing_small": 4,
        "spacing_medium": 8,
        "spacing_large": 16,
        "border_radius": 4,
    }

    # Estilos CSS para Qt
    STYLES = {
        "QWidget": f"""
            background-color: {COLORS["background"]};
            color: {COLORS["dark"]};
        """,
        "QPushButton": f"""
            QPushButton {{
                background-color: {COLORS["secondary"]};
                color: {COLORS["white"]};
                border: none;
                border-radius: {SIZES["border_radius"]}px;
                padding: 6px 12px;
                font-weight: 500;
                min-height: {SIZES["button_min_height"]}px;
                min-width: {SIZES["button_min_width"]}px;
            }}
            QPushButton:hover {{
                background-color: {COLORS["hover"]};
            }}
            QPushButton:pressed {{
                background-color: {COLORS["pressed"]};
            }}
            QPushButton:disabled {{
                background-color: {COLORS["disabled"]};
                color: {COLORS["gray"]};
            }}
        """,
        "QPushButton.primary": f"""
            QPushButton {{
                background-color: {COLORS["primary"]};
                color: {COLORS["white"]};
            }}
        """,
        "QPushButton.success": f"""
            QPushButton {{
                background-color: {COLORS["success"]};
                color: {COLORS["white"]};
            }}
        """,
        "QPushButton.danger": f"""
            QPushButton {{
                background-color: {COLORS["danger"]};
                color: {COLORS["white"]};
            }}
        """,
        "QLineEdit": f"""
            QLineEdit {{
                background-color: {COLORS["white"]};
                border: 1px solid {COLORS["border"]};
                border-radius: {SIZES["border_radius"]}px;
                padding: 4px 8px;
                min-height: {SIZES["input_height"]}px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS["secondary"]};
                padding: 3px 7px;
            }}
        """,
        "QTreeWidget": f"""
            QTreeWidget {{
                background-color: {COLORS["white"]};
                border: 1px solid {COLORS["border"]};
                border-radius: {SIZES["border_radius"]}px;
                outline: 0;
            }}
            QTreeWidget::item {{
                height: {SIZES["tree_row_height"]}px;
                padding: 2px;
            }}
            QTreeWidget::item:selected {{
                background-color: {COLORS["selection"]};
                color: {COLORS["white"]};
            }}
            QTreeWidget::item:hover:!selected {{
                background-color: {COLORS["light"]};
            }}
            QHeaderView::section {{
                background-color: {COLORS["primary"]};
                color: {COLORS["white"]};
                padding: 6px;
                border: none;
                font-weight: bold;
            }}
        """,
        "QComboBox": f"""
            QComboBox {{
                background-color: {COLORS["white"]};
                border: 1px solid {COLORS["border"]};
                border-radius: {SIZES["border_radius"]}px;
                padding: 4px 8px;
                min-height: {SIZES["input_height"]}px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {COLORS["dark"]};
            }}
        """,
    }

    def __init__(self, parent: Optional[QWidget] = None, title: str = ""):
        """
        Inicializa la vista base

        Args:
            parent: Widget padre
            title: Título de la vista
        """
        super().__init__(parent)

        # No asignar self.parent - ya está definido por QWidget
        self.view_title = title  # Usar un nombre diferente para el título

        # Configurar estilos
        self._setup_styles()

        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(
            self.SIZES["padding_large"],
            self.SIZES["padding_large"],
            self.SIZES["padding_large"],
            self.SIZES["padding_large"],
        )
        self.main_layout.setSpacing(self.SIZES["spacing_medium"])

        # Diccionario para widgets
        self.widgets = {}

        # Configurar fuente
        self._setup_fonts()

        logger.debug(f"BaseView PySide6 inicializada: {title}")

    # ============ CONFIGURACIÓN INICIAL ============
    def _setup_styles(self):
        """Configura los estilos CSS para la aplicación"""
        # Aplicar estilos globales
        for widget_type, style in self.STYLES.items():
            self.setStyleSheet(style)

    def _setup_fonts(self):
        """Configura las fuentes del sistema"""
        # Intentar cargar fuentes si existen
        font_db = QFontDatabase()
        available_families = font_db.families()
        # Verificar si tenemos las fuentes preferidas
        preferred_fonts = ["Segoe UI", "Arial", "Helvetica", "Verdana"]
        for font in preferred_fonts:
            if font in available_families:
                app_font = QFont(font, 10)
                QApplication.setFont(app_font)
                break

    # ============ MÉTODOS DE CONSTRUCCIÓN DE UI ============

    def create_header(self, text: str, icon: Optional[str] = None) -> QLabel:
        """
        Crea un encabezado para la vista

        Args:
            text: Texto del encabezado
            icon: Ruta al ícono (opcional)

        Returns:
            QLabel: Label del encabezado
        """
        header = QLabel(text)

        # Configurar fuente CORREGIDA
        font_family, font_size, font_weight = self.FONTS["title"]
        font = QFont(font_family, font_size)
        font.setWeight(font_weight)
        header.setFont(font)

        # Configurar color CORREGIDO
        palette = header.palette()
        palette.setColor(
            QPalette.ColorRole.WindowText, QColor(self.COLORS["primary"])
        )  # ¡Corregido!
        header.setPalette(palette)

        # Añadir al layout
        self.main_layout.addWidget(header)

        # Guardar referencia
        self.widgets["header"] = header

        return header

    def create_toolbar(self, buttons_config: List[Dict]) -> QWidget:
        """
        Crea una barra de herramientas

        Args:
            buttons_config: Configuración de botones

        Returns:
            QWidget: Widget de toolbar
        """
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(self.SIZES["spacing_small"])

        for config in buttons_config:
            text = config.get("text", "")
            icon_path = config.get("icon", "")
            command = config.get("command")
            style = config.get("style", "default")

            btn = QPushButton(text)

            # Configurar ícono si existe
            if icon_path:
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(QSize(self.SIZES["icon_size"], self.SIZES["icon_size"]))

            # Configurar estilo
            if style != "default":
                btn.setProperty("class", style)
                btn.style().polish(btn)

            # Conectar señal
            if command:
                btn.clicked.connect(command)

            # Tamaño mínimo
            btn.setMinimumSize(
                self.SIZES["button_min_width"], self.SIZES["button_min_height"]
            )

            toolbar_layout.addWidget(btn)

            # Guardar referencia
            key = f"btn_{text.lower().replace(' ', '_')}"
            self.widgets[key] = btn

        # Añadir stretch al final
        toolbar_layout.addStretch()

        # Añadir al layout principal
        self.main_layout.addWidget(toolbar)

        return toolbar

    def create_search_bar(self, callback: Callable) -> QWidget:
        """
        Crea una barra de búsqueda

        Args:
            callback: Función a llamar al buscar

        Returns:
            QWidget: Widget de búsqueda
        """
        search_widget = QWidget()
        search_layout = QHBoxLayout(search_widget)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(self.SIZES["spacing_small"])

        # Etiqueta
        label = QLabel("Buscar:")
        search_layout.addWidget(label)

        # Campo de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ingrese texto para buscar...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.returnPressed.connect(callback)
        search_layout.addWidget(self.search_input)

        # Botón buscar
        search_btn = QPushButton("Buscar")
        search_btn.clicked.connect(callback)
        search_layout.addWidget(search_btn)

        # Botón limpiar
        clear_btn = QPushButton("Limpiar")
        clear_btn.clicked.connect(self._clear_search)
        search_layout.addWidget(clear_btn)

        # Guardar referencias
        self.widgets["search_widget"] = search_widget
        self.widgets["search_input"] = self.search_input

        # Añadir al layout principal
        self.main_layout.addWidget(search_widget)

        return search_widget

    def _clear_search(self):
        """Limpia la búsqueda"""
        self.search_input.clear()
        if hasattr(self, "on_clear_search"):
            self.on_clear_search()

    def create_treeview(
        self, headers: List[str], column_widths: Optional[List[int]] = None
    ) -> QTreeWidget:
        """
        Crea un QTreeWidget configurado

        Args:
            headers: Lista de encabezados
            column_widths: Anchos de columnas (opcional)

        Returns:
            QTreeWidget: Tree widget configurado
        """
        tree = QTreeWidget()

        # Configurar encabezados
        tree.setHeaderLabels(headers)

        # Configurar anchos de columnas
        if column_widths:
            for i, width in enumerate(column_widths):
                tree.setColumnWidth(i, width)

        # Configurar propiedades
        tree.setAlternatingRowColors(True)
        tree.setSelectionBehavior(QTreeWidget.SelectionBehavior.SelectRows)
        tree.setSortingEnabled(True)

        # Ajustar encabezados
        header = tree.header()
        header.setStretchLastSection(True)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)

        # Configurar altura de filas
        tree.setStyleSheet(
            f"""
            QTreeWidget::item {{
                height: {self.SIZES["tree_row_height"]}px;
            }}
        """
        )

        # Añadir al layout con stretch
        self.main_layout.addWidget(tree, 1)  # Factor de estiramiento 1

        # Guardar referencia
        self.widgets["treeview"] = tree

        return tree

    def create_form_dialog(
        self,
        title: str,
        fields: List[Dict],
        on_save: Callable,
        on_cancel: Optional[Callable] = None,
    ) -> QDialog:
        """
        Crea un diálogo de formulario

        Args:
            title: Título del diálogo
            fields: Campos del formulario
            on_save: Función para guardar
            on_cancel: Función para cancelar

        Returns:
            QDialog: Diálogo de formulario
        """
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setModal(True)

        # Layout principal
        layout = QVBoxLayout(dialog)
        layout.setSpacing(self.SIZES["spacing_medium"])

        # Frame para formulario
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(self.SIZES["spacing_medium"])

        # Variables para almacenar widgets
        form_fields = {}

        # Crear campos
        for field in fields:
            label = field.get("label", "")
            field_type = field.get("type", "text")
            field_key = field.get("key", label.lower())
            default = field.get("default", "")

            # Crear widget según tipo
            if field_type == "text":
                widget = QLineEdit()
                widget.setText(str(default))

            elif field_type == "number":
                widget = QSpinBox()
                widget.setRange(field.get("min", 0), field.get("max", 100))
                widget.setValue(int(default) if default else 0)

            elif field_type == "combo":
                widget = QComboBox()
                widget.addItems(field.get("items", []))
                if default in field.get("items", []):
                    widget.setCurrentText(default)

            elif field_type == "checkbox":
                widget = QCheckBox(field.get("text", ""))
                widget.setChecked(bool(default))

            elif field_type == "date":
                # Para fecha podríamos usar QDateEdit
                widget = QLineEdit()
                widget.setText(str(default))

            # Añadir al formulario
            form_layout.addRow(label, widget)
            form_fields[field_key] = widget

        layout.addWidget(form_widget)

        # Botones
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setSpacing(self.SIZES["spacing_small"])

        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(
            lambda: self._handle_form_save(dialog, form_fields, on_save)
        )

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(lambda: self._handle_form_cancel(dialog, on_cancel))

        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addWidget(button_widget)

        # Ajustar tamaño
        dialog.adjustSize()

        return dialog

    def _handle_form_save(self, dialog: QDialog, fields: Dict, on_save: Callable):
        """Maneja el guardado del formulario"""
        try:
            # Recoger datos
            data = {}
            for key, widget in fields.items():
                if isinstance(widget, QLineEdit):
                    data[key] = widget.text()
                elif isinstance(widget, QSpinBox):
                    data[key] = widget.value()
                elif isinstance(widget, QComboBox):
                    data[key] = widget.currentText()
                elif isinstance(widget, QCheckBox):
                    data[key] = widget.isChecked()

            # Llamar función de guardado
            success = on_save(data)

            if success:
                dialog.accept()
                self.show_success("Datos guardados correctamente")
            else:
                self.show_error("Error al guardar los datos")

        except Exception as e:
            logger.error(f"Error en formulario: {e}")
            self.show_error(f"Error: {str(e)}")

    def _handle_form_cancel(self, dialog: QDialog, on_cancel: Optional[Callable]):
        """Maneja la cancelación del formulario"""
        if on_cancel:
            on_cancel()
        dialog.reject()

    # ============ MÉTODOS DE UTILIDAD ============

    def show_message(
        self,
        title: str,
        message: str,
        message_type: QMessageBox.Icon = QMessageBox.Icon.Information,  # CORREGIDO
    ) -> bool:
        """
        Muestra un mensaje al usuario

        Args:
            title: Título del mensaje
            message: Contenido del mensaje
            message_type: Tipo de mensaje

        Returns:
            bool: Resultado si es pregunta
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(message_type)

        # Configurar botones según tipo
        if message_type == QMessageBox.Icon.Question:  # CORREGIDO
            # Botones personalizados en español
            msg_box.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            # Traducir textos de botones
            msg_box.setButtonText(QMessageBox.StandardButton.Yes, "Sí")
            msg_box.setButtonText(QMessageBox.StandardButton.No, "No")

            return msg_box.exec() == QMessageBox.StandardButton.Yes
        else:
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)  # CORREGIDO
            msg_box.setButtonText(QMessageBox.StandardButton.Ok, "Aceptar")
            msg_box.exec()
            return True

    def show_error(self, message: str):
        """Muestra un mensaje de error"""
        self.show_message("Error", message, QMessageBox.Icon.Critical)  # CORREGIDO

    def show_success(self, message: str):
        """Muestra un mensaje de éxito"""
        self.show_message("Éxito", message, QMessageBox.Icon.Information)  # CORREGIDO

    def show_warning(self, message: str):
        """Muestra un mensaje de advertencia"""
        self.show_message("Advertencia", message, QMessageBox.Icon.Warning)  # CORREGIDO

    def ask_confirmation(self, message: str) -> bool:
        """Pide confirmación al usuario"""
        return self.show_message(
            "Confirmar", message, QMessageBox.Icon.Question
        )  # CORREGIDO

    def center_on_screen(self):
        """Centra la ventana en la pantalla"""
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()

        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)

        self.move(window_geometry.topLeft())

    # ============ MÉTODOS PARA SOBRESCRIBIR ============

    def load_data(self):
        """Carga los datos de la vista (debe ser implementado)"""
        raise NotImplementedError("Método load_data debe ser implementado")

    def refresh(self):
        """Refresca la vista"""
        self.load_data()
        self.view_refreshed.emit()

    def on_clear_search(self):
        """Manejador para limpiar búsqueda (opcional sobrescribir)"""
        pass

    def cleanup(self):
        """Limpia recursos antes de cerrar (opcional)"""
        pass


# Clase de utilidades estáticas
class ViewUtils:
    """Utilidades estáticas para vistas"""

    @staticmethod
    def apply_style(widget: QWidget, style_name: str):
        """Aplica un estilo CSS a un widget"""
        if style_name in BaseView.STYLES:
            widget.setStyleSheet(BaseView.STYLES[style_name])

    @staticmethod
    def create_icon_button(
        text: str, icon_path: str = "", tooltip: str = ""
    ) -> QPushButton:
        """Crea un botón con ícono"""
        btn = QPushButton(text)

        if icon_path:
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(
                QSize(BaseView.SIZES["icon_size"], BaseView.SIZES["icon_size"])
            )

        if tooltip:
            btn.setToolTip(tooltip)

        return btn

    @staticmethod
    def create_separator(
        horizontal: bool = True,
        shadow_type: QFrame.Shadow = QFrame.Shadow.Sunken,
        line_width: int = 1,
        mid_line_width: int = 0,
    ) -> QFrame:
        """
        Crea un separador con opciones personalizadas

        Args:
            horizontal: True para horizontal, False para vertical
            shadow_type: Tipo de sombra (Sunken, Raised, Plain)
            line_width: Ancho de la línea
            mid_line_width: Ancho de la línea media (para algunos estilos)

        Returns:
            QFrame: Separador configurado
        """
        separator = QFrame()

        # Configurar forma
        if horizontal:
            separator.setFrameShape(QFrame.Shape.HLine)
        else:
            separator.setFrameShape(QFrame.Shape.VLine)

        # Configurar sombra
        separator.setFrameShadow(shadow_type)

        # Configurar anchos
        separator.setLineWidth(line_width)
        separator.setMidLineWidth(mid_line_width)

        # Estilo mínimo para separadores verticales
        if not horizontal:
            separator.setMinimumHeight(1)
            separator.setMaximumHeight(16777215)  # Qt máximo

        return separator


# Ejemplo de uso rápido
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    class ExampleView(BaseView):
        def __init__(self):
            super().__init__(None, "Ejemplo PySide6")
            self.setup_ui()

        def setup_ui(self):
            # Header
            self.create_header("Sistema de Gestión")

            # Toolbar
            self.create_toolbar(
                [
                    {"text": "Nuevo", "command": self.on_new, "style": "primary"},
                    {"text": "Editar", "command": self.on_edit},
                    {"text": "Eliminar", "command": self.on_delete, "style": "danger"},
                ]
            )

            # Treeview
            tree = self.create_treeview(["ID", "Nombre", "Email"], [100, 200, 250])

            # Añadir datos de ejemplo
            for i in range(5):
                item = QTreeWidgetItem(tree)
                item.setText(0, str(i + 1))
                item.setText(1, f"Usuario {i+1}")
                item.setText(2, f"usuario{i+1}@ejemplo.com")

            self.center_on_screen()
            self.resize(800, 600)

        def on_new(self):
            self.show_success("Nuevo elemento")

        def on_edit(self):
            self.show_message("Editar", "Editando...")

        def on_delete(self):
            if self.ask_confirmation("¿Eliminar elemento?"):
                self.show_success("Eliminado")

    window = ExampleView()
    window.show()
    sys.exit(app.exec())
