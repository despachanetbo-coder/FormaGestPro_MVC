# app/views/tabs/base_tab.py
"""
BaseTab - Clase base especializada para pestañas/tabs del sistema
Hereda de BaseView para reutilizar estilos y funcionalidades comunes
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLineEdit,
    QComboBox,
    QFrame,
    QMessageBox,
    QDialog,
    QFormLayout,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QDateEdit,
    QTextEdit,
    QGroupBox,
    QMenu,
    QScrollArea,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, Slot, QDate
from PySide6.QtGui import QIcon, QFont, QColor, QAction

from app.views.base_view import BaseView, ViewUtils

logger = logging.getLogger(__name__)


class BaseTab(BaseView):
    """
    Clase base para todas las pestañas del sistema

    Proporciona:
    1. Funcionalidades de paginación
    2. Configuración de tablas estandarizadas
    3. Sistema de filtros unificado
    4. Señales comunes para comunicación
    """

    # ============ SEÑALES ESPECÍFICAS PARA TABS ============
    tab_initialized = Signal()  # Tab inicializado
    data_filtered = Signal(list)  # Datos filtrados
    page_changed = Signal(int, int)  # Página actual, total páginas
    item_selected = Signal(dict)  # Item seleccionado en tabla
    needs_refresh = Signal()  # Necesita actualizar datos

    def __init__(self, parent: Optional[QWidget] = None, title: str = ""):
        """
        Inicializa la pestaña base

        Args:
            parent: Widget padre
            title: Título de la pestaña
        """
        super().__init__(parent, title)

        # Configuración específica de pestañas
        self.widgets.clear()  # Limpiar widgets heredados para reconfigurar

        # Variables de paginación
        self.current_data = []  # Datos completos
        self.filtered_data = []  # Datos filtrados
        self.paginated_data = []  # Datos paginados actuales
        self.current_filter = "todos"  # Filtro actual
        self.current_page = 1  # Página actual
        self.records_per_page = 10  # Registros por página
        self.total_pages = 1  # Total de páginas

        # Configurar UI base para pestañas
        self._setup_tab_ui()

        logger.debug(f"BaseTab inicializada: {title}")

    def _setup_tab_ui(self):
        """Configura la UI base para todas las pestañas"""
        # Limpiar layout heredado de manera segura
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item and item.widget():
                widget = item.widget()
                if widget:
                    widget.deleteLater()

        # Configurar márgenes específicos para pestañas
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(self.SIZES["spacing_medium"])

    # ============ MÉTODOS DE UI PARA TABS ============

    def create_tab_header(self, icon: str = "", subtitle: str = "") -> QLabel:
        """
        Crea un encabezado específico para pestañas

        Args:
            icon: Ícono/emoji para el encabezado
            subtitle: Subtítulo opcional

        Returns:
            QLabel: Encabezado configurado
        """
        header_text = f"{icon} {self.view_title}" if icon else self.view_title

        # Usar el método heredado de BaseView
        header = self.create_header(header_text)

        # Estilo específico para pestañas
        header.setStyleSheet(
            f"""
            {header.styleSheet()}
            QLabel {{
                border-bottom: 2px solid {self.COLORS["secondary"]};
                margin-bottom: {self.SIZES["spacing_medium"]}px;
            }}
        """
        )

        # Añadir subtítulo si se especifica
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setFont(self._create_font("small"))
            palette = subtitle_label.palette()
            palette.setColor(
                subtitle_label.foregroundRole(), QColor(self.COLORS["gray"])
            )
            subtitle_label.setPalette(palette)
            self.main_layout.addWidget(subtitle_label)

        return header

    def create_filter_bar(
        self, filter_options: List[str], search_placeholder: str = "Buscar..."
    ) -> QFrame:
        """
        Crea una barra de filtros estandarizada para pestañas

        Args:
            filter_options: Opciones para el combo de filtro
            search_placeholder: Placeholder para el campo de búsqueda

        Returns:
            QFrame: Frame con los controles de filtro
        """
        filter_frame = QFrame()
        filter_frame.setObjectName("FilterFrame")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(
            self.SIZES["padding_medium"],
            self.SIZES["padding_medium"],
            self.SIZES["padding_medium"],
            self.SIZES["padding_medium"],
        )
        filter_layout.setSpacing(self.SIZES["spacing_medium"])

        # Estilo del frame
        filter_frame.setStyleSheet(
            f"""
            #FilterFrame {{
                background-color: {self.COLORS["white"]};
                border: 1px solid {self.COLORS["border"]};
                border-radius: {self.SIZES["border_radius"]}px;
            }}
        """
        )

        # Label de filtro
        filter_label = QLabel("Filtrar:")
        filter_label.setFont(self._create_font("small"))
        filter_label.setStyleSheet(f"font-weight: bold; color: {self.COLORS['dark']};")
        filter_layout.addWidget(filter_label)

        # ComboBox de filtro
        self.combo_filtro = QComboBox()
        self.combo_filtro.addItems(filter_options)
        self.combo_filtro.setMinimumWidth(120)
        self.combo_filtro.setFont(self._create_font("small"))
        self.combo_filtro.setStyleSheet(self.STYLES["QComboBox"])
        filter_layout.addWidget(self.combo_filtro)

        # Campo de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(search_placeholder)
        self.search_input.setMinimumWidth(200)
        self.search_input.setFont(self._create_font("small"))
        self.search_input.setStyleSheet(self.STYLES["QLineEdit"])
        filter_layout.addWidget(self.search_input)

        # Botón de búsqueda
        self.btn_search = QPushButton("🔍 Buscar")
        self.btn_search.setFont(self._create_font("small"))
        self.btn_search.setStyleSheet(self.STYLES["QPushButton"])
        filter_layout.addWidget(self.btn_search)

        # Botón de limpiar
        self.btn_clear = QPushButton("🗑️ Limpiar")
        self.btn_clear.setFont(self._create_font("small"))
        self.btn_clear.setStyleSheet(
            f"""
            {self.STYLES["QPushButton"]}
            QPushButton {{
                background-color: {self.COLORS["gray"]};
            }}
            QPushButton:hover {{
                background-color: {self.COLORS["gray_light"]};
            }}
        """
        )
        filter_layout.addWidget(self.btn_clear)

        # Espacio flexible
        filter_layout.addStretch()

        # Guardar referencias
        self.widgets["filter_frame"] = filter_frame
        self.widgets["combo_filtro"] = self.combo_filtro
        self.widgets["search_input"] = self.search_input
        self.widgets["btn_search"] = self.btn_search
        self.widgets["btn_clear"] = self.btn_clear

        # Añadir al layout principal
        self.main_layout.addWidget(filter_frame)

        return filter_frame

    def create_data_table(
        self, headers: List[str], column_widths: Optional[List[int]] = None
    ) -> QTableWidget:
        """
        Crea una tabla de datos estandarizada con paginación

        Args:
            headers: Encabezados de las columnas
            column_widths: Anchos opcionales de columnas

        Returns:
            QTableWidget: Tabla configurada
        """
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

        # Configurar propiedades de la tabla
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(self.SIZES["tree_row_height"])

        # Configurar encabezados
        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)

        # Establecer anchos de columna si se proporcionan
        if column_widths:
            for i, width in enumerate(column_widths):
                if i < len(headers):
                    table.setColumnWidth(i, width)

        # Aplicar estilos
        table.setStyleSheet(
            f"""
            QTableWidget {{
                background-color: {self.COLORS["white"]};
                alternate-background-color: {self.COLORS["light"]};
                border: 1px solid {self.COLORS["border"]};
                border-radius: {self.SIZES["border_radius"]}px;
                gridline-color: {self.COLORS["border"]};
                color: {self.COLORS["dark"]};
                font-size: {self.SIZES["padding_medium"]}px;
            }}
            QTableWidget::item {{
                padding: {self.SIZES["padding_small"]}px;
                border-bottom: 1px solid {self.COLORS["border"]};
            }}
            QTableWidget::item:selected {{
                background-color: {self.COLORS["selection"]};
                color: {self.COLORS["white"]};
            }}
            QHeaderView::section {{
                background-color: {self.COLORS["primary"]};
                color: {self.COLORS["white"]};
                padding: {self.SIZES["padding_small"]}px {self.SIZES["padding_medium"]}px;
                border: none;
                font-weight: bold;
                font-size: {self.SIZES["padding_medium"]}px;
            }}
        """
        )

        # Añadir al layout
        self.main_layout.addWidget(table, 1)  # Factor de stretch 1

        # Guardar referencia
        self.widgets["data_table"] = table

        return table

    def create_pagination_controls(self) -> QFrame:
        """
        Crea controles de paginación estandarizados

        Returns:
            QFrame: Frame con controles de paginación
        """
        pagination_frame = QFrame()
        pagination_frame.setObjectName("PaginationFrame")
        pagination_layout = QHBoxLayout(pagination_frame)
        pagination_layout.setContentsMargins(
            self.SIZES["padding_medium"],
            self.SIZES["padding_small"],
            self.SIZES["padding_medium"],
            self.SIZES["padding_small"],
        )
        pagination_layout.setSpacing(self.SIZES["spacing_small"])

        # Estilo del frame
        pagination_frame.setStyleSheet(
            f"""
            #PaginationFrame {{
                background-color: {self.COLORS["white"]};
                border: 1px solid {self.COLORS["border"]};
                border-radius: {self.SIZES["border_radius"]}px;
            }}
        """
        )

        # Botón Primera Página
        self.btn_first = QPushButton("⏮️ Primera")
        self.btn_first.setMinimumWidth(80)
        self.btn_first.setFont(self._create_font("small"))
        self._style_pagination_button(self.btn_first, "gray")
        pagination_layout.addWidget(self.btn_first)

        # Botón Página Anterior
        self.btn_prev = QPushButton("◀️ Anterior")
        self.btn_prev.setMinimumWidth(80)
        self.btn_prev.setFont(self._create_font("small"))
        self._style_pagination_button(self.btn_prev, "gray_light")
        pagination_layout.addWidget(self.btn_prev)

        # Espacio
        pagination_layout.addStretch()

        # Información de página
        self.lbl_page_info = QLabel("Página 1 de 1")
        self.lbl_page_info.setFont(self._create_font("small"))
        self.lbl_page_info.setStyleSheet(
            f"font-weight: bold; color: {self.COLORS['dark']};"
        )
        pagination_layout.addWidget(self.lbl_page_info)

        # Contador de registros
        self.lbl_record_count = QLabel("Mostrando 0 de 0 registros")
        self.lbl_record_count.setFont(self._create_font("small"))
        self.lbl_record_count.setStyleSheet(
            f"color: {self.COLORS['gray']}; font-style: italic;"
        )
        pagination_layout.addWidget(self.lbl_record_count)

        # Espacio
        pagination_layout.addStretch()

        # Botón Página Siguiente
        self.btn_next = QPushButton("Siguiente ▶️")
        self.btn_next.setMinimumWidth(80)
        self.btn_next.setFont(self._create_font("small"))
        self._style_pagination_button(self.btn_next, "gray_light")
        pagination_layout.addWidget(self.btn_next)

        # Botón Última Página
        self.btn_last = QPushButton("Última ⏭️")
        self.btn_last.setMinimumWidth(80)
        self.btn_last.setFont(self._create_font("small"))
        self._style_pagination_button(self.btn_last, "gray")
        pagination_layout.addWidget(self.btn_last)

        # Guardar referencias
        self.widgets.update(
            {
                "pagination_frame": pagination_frame,
                "btn_first": self.btn_first,
                "btn_prev": self.btn_prev,
                "btn_next": self.btn_next,
                "btn_last": self.btn_last,
                "lbl_page_info": self.lbl_page_info,
                "lbl_record_count": self.lbl_record_count,
            }
        )

        # Añadir al layout principal
        self.main_layout.addWidget(pagination_frame)

        return pagination_frame

    def _style_pagination_button(self, button: QPushButton, color_key: str):
        """
        Aplica estilo a botones de paginación

        Args:
            button: Botón a estilizar
            color_key: Clave de color en self.COLORS
        """
        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self.COLORS[color_key]};
                color: {self.COLORS["white"]};
                font-weight: bold;
                border-radius: {self.SIZES["border_radius"] - 2}px;
                padding: {self.SIZES["padding_small"]}px {self.SIZES["padding_medium"]}px;
                border: none;
                min-height: {self.SIZES["button_min_height"] - 4}px;
            }}
            QPushButton:hover {{
                background-color: {self.COLORS["hover"] if color_key == "gray_light" else self.COLORS["gray"]};
            }}
            QPushButton:pressed {{
                background-color: {self.COLORS["pressed"]};
            }}
            QPushButton:disabled {{
                background-color: {self.COLORS["disabled"]};
                color: {self.COLORS["gray"]};
            }}
        """
        )

    # ============ MÉTODOS DE PAGINACIÓN ============

    def apply_pagination(self, data: List[Any]) -> List[Any]:
        """
        Aplica paginación a los datos

        Args:
            data: Lista de datos a paginar

        Returns:
            List[Any]: Sublista de datos para la página actual
        """
        if not data:
            self.total_pages = 1
            self.current_page = 1
            return []

        # Calcular total de páginas
        total_records = len(data)
        self.total_pages = max(
            1, (total_records + self.records_per_page - 1) // self.records_per_page
        )

        # Asegurar que current_page esté en rango válido
        self.current_page = max(1, min(self.current_page, self.total_pages))

        # Calcular índices
        start_idx = (self.current_page - 1) * self.records_per_page
        end_idx = min(start_idx + self.records_per_page, total_records)

        # Obtener datos para la página actual
        paginated = data[start_idx:end_idx]

        # Actualizar controles de paginación
        self._update_pagination_controls(total_records)

        return paginated

    def _update_pagination_controls(self, total_records: int):
        """
        Actualiza los controles de paginación

        Args:
            total_records: Total de registros
        """
        if not hasattr(self, "lbl_page_info") or not hasattr(self, "lbl_record_count"):
            return

        # Actualizar etiquetas
        self.lbl_page_info.setText(f"Página {self.current_page} de {self.total_pages}")

        start_idx = (self.current_page - 1) * self.records_per_page + 1
        end_idx = min(start_idx + self.records_per_page - 1, total_records)

        if total_records == 0:
            self.lbl_record_count.setText("Mostrando 0 de 0 registros")
        else:
            self.lbl_record_count.setText(
                f"Mostrando {start_idx}-{end_idx} de {total_records} registros"
            )

        # Actualizar estado de botones
        self.btn_first.setEnabled(self.current_page > 1)
        self.btn_prev.setEnabled(self.current_page > 1)
        self.btn_next.setEnabled(self.current_page < self.total_pages)
        self.btn_last.setEnabled(self.current_page < self.total_pages)

    def change_page(self, page: int):
        """
        Cambia a una página específica

        Args:
            page: Número de página
        """
        if 1 <= page <= self.total_pages and page != self.current_page:
            self.current_page = page
            self.load_page_data()
            self.page_changed.emit(self.current_page, self.total_pages)

    # ============ MÉTODOS PARA SOBRESCRIBIR ============

    def setup_ui(self):
        """
        Configura la interfaz de usuario específica de la pestaña

        DEBE ser implementado por las subclases
        """
        raise NotImplementedError("Las subclases deben implementar setup_ui()")

    def load_data(self):
        """
        Carga los datos iniciales de la pestaña

        DEBE ser implementado por las subclases
        """
        raise NotImplementedError("Las subclases deben implementar load_data()")

    def load_page_data(self):
        """
        Carga los datos de la página actual

        DEBE ser implementado por las subclases
        """
        raise NotImplementedError("Las subclases deben implementar load_page_data()")

    def apply_filters(self):
        """
        Aplica los filtros actuales a los datos

        DEBE ser implementado por las subclases
        """
        raise NotImplementedError("Las subclases deben implementar apply_filters()")

    def setup_connections(self):
        """
        Configura las conexiones de señales y slots

        Opcional: Las subclases pueden sobrescribir para añadir conexiones específicas
        """
        # Conectar controles de paginación
        if hasattr(self, "btn_first"):
            self.btn_first.clicked.connect(lambda: self.change_page(1))
        if hasattr(self, "btn_prev"):
            self.btn_prev.clicked.connect(
                lambda: self.change_page(self.current_page - 1)
            )
        if hasattr(self, "btn_next"):
            self.btn_next.clicked.connect(
                lambda: self.change_page(self.current_page + 1)
            )
        if hasattr(self, "btn_last"):
            self.btn_last.clicked.connect(lambda: self.change_page(self.total_pages))

        # Conectar controles de filtro
        if hasattr(self, "btn_search"):
            self.btn_search.clicked.connect(self.apply_filters)
        if hasattr(self, "btn_clear"):
            self.btn_clear.clicked.connect(self.clear_filters)
        if hasattr(self, "search_input"):
            self.search_input.returnPressed.connect(self.apply_filters)
        if hasattr(self, "combo_filtro"):
            self.combo_filtro.currentTextChanged.connect(self.apply_filters)

    def clear_filters(self):
        """
        Limpia todos los filtros

        Las subclases pueden sobrescribir para comportamiento específico
        """
        if hasattr(self, "search_input"):
            self.search_input.clear()
        if hasattr(self, "combo_filtro"):
            self.combo_filtro.setCurrentIndex(0)

        self.apply_filters()

    # ============ MÉTODOS DE UTILIDAD ============

    def _create_font(self, font_type: str = "normal") -> QFont:
        """
        Crea una fuente QFont según la configuración

        Args:
            font_type: Tipo de fuente (title, subtitle, header, normal, small, monospace)

        Returns:
            QFont: Fuente configurada

        Raises:
            ValueError: Si el tipo de fuente no existe
        """
        # Verificar si el tipo de fuente existe
        if font_type not in self.FONTS:
            logger.warning(
                f"Tipo de fuente '{font_type}' no encontrado. Usando 'normal'."
            )
            font_type = "normal"

        try:
            font_family, font_size, font_weight = self.FONTS[font_type]

            # Crear fuente
            font = QFont()

            # Configurar familia
            if font_family:
                font.setFamily(font_family)

            # Configurar tamaño
            if font_size:
                font.setPointSize(font_size)

            # Configurar peso
            if font_weight:
                font.setWeight(font_weight)

            return font

        except Exception as e:
            logger.error(f"Error creando fuente '{font_type}': {e}")
            # Retornar fuente por defecto
            return QFont()

    def refresh(self):
        """Refresca la pestaña completamente"""
        self.load_data()
        self.apply_filters()
        self.load_page_data()
        self.needs_refresh.emit()

    def get_selected_item(self) -> Optional[Dict]:
        """
        Obtiene el item seleccionado en la tabla

        Returns:
            Optional[Dict]: Diccionario con datos del item o None
        """
        table = self.widgets.get("data_table")
        if not table or table.selectedItems():
            return None

        # Implementación básica - las subclases deben sobrescribir
        selected_row = table.currentRow()
        if selected_row >= 0 and selected_row < len(self.paginated_data):
            return self.paginated_data[selected_row]

        return None


# ============================================================================
# EJEMPLO DE USO PARA LAS SUBCLASES
# ============================================================================

"""
Ejemplo de cómo debería verse una pestaña que herede de BaseTab:

class MiPestaña(BaseTab):
    def __init__(self, parent=None):
        super().__init__(parent, "Título de Mi Pestaña")
        
        # Configurar UI específica
        self.setup_ui()
        self.setup_connections()
        
        # Cargar datos iniciales
        self.load_data()
        self.apply_filters()
        self.load_page_data()
        
        self.tab_initialized.emit()
    
    def setup_ui(self):
        # 1. Crear encabezado
        self.create_tab_header("📚", "Gestión de recursos educativos")
        
        # 2. Crear barra de filtros
        self.create_filter_bar(
            filter_options=['Todos', 'Activos', 'Inactivos'],
            search_placeholder="Buscar por nombre..."
        )
        
        # 3. Crear tabla
        self.create_data_table(
            headers=['ID', 'Nombre', 'Estado', 'Fecha'],
            column_widths=[80, 200, 100, 120]
        )
        
        # 4. Crear controles de paginación
        self.create_pagination_controls()
    
    def load_data(self):
        # Cargar datos desde el modelo
        self.current_data = MiModelo.get_all()
        self.filtered_data = self.current_data.copy()
    
    def load_page_data(self):
        # Aplicar paginación y mostrar en tabla
        self.paginated_data = self.apply_pagination(self.filtered_data)
        self.display_data_in_table(self.paginated_data)
    
    def apply_filters(self):
        # Aplicar filtros basados en combo_filtro y search_input
        filter_text = self.combo_filtro.currentText().lower()
        search_text = self.search_input.text().lower()
        
        filtered = self.current_data
        
        # Aplicar filtro de estado
        if filter_text != 'todos':
            filtered = [item for item in filtered if item['estado'] == filter_text]
        
        # Aplicar búsqueda
        if search_text:
            filtered = [item for item in filtered 
                       if search_text in item['nombre'].lower()]
        
        self.filtered_data = filtered
        self.current_page = 1  # Volver a primera página
        self.load_page_data()
        self.data_filtered.emit(self.filtered_data)
    
    def display_data_in_table(self, data):
        # Mostrar datos en la tabla
        table = self.widgets.get("data_table")
        if not table:
            return
        
        table.setRowCount(len(data))
        for row, item in enumerate(data):
            # Llenar celdas según estructura de datos
            table.setItem(row, 0, QTableWidgetItem(str(item.get('id', ''))))
            table.setItem(row, 1, QTableWidgetItem(item.get('nombre', '')))
            # ... más columnas
"""
