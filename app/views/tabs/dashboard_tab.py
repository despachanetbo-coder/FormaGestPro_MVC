# app/views/tabs/dashboard_tab.py
"""
Dashboard principal del sistema FormaGestPro - Versión optimizada con herencia BaseTab
Versión 4.0 - Totalmente integrada con BaseView/BaseTab, con exportación a PDF

CARACTERÍSTICAS:
1. Hereda de BaseTab para estilos y funcionalidades comunes
2. Usa estilos centralizados de BaseView (COLORS, FONTS, SIZES, STYLES)
3. Integra DashboardController para obtener datos
4. Implementa gráficos QtCharts con temas consistentes
5. Incluye funcionalidad de exportación a PDF
"""

import logging
import tempfile
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from io import BytesIO

# PySide6 imports
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
    QPushButton,
    QSizePolicy,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QFileDialog,
    QProgressDialog,
    QApplication,
)
from PySide6.QtCore import (
    Qt,
    QTimer,
    QDate,
    QDateTime,
    Signal,
    Slot,
    QPropertyAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
)
from PySide6.QtGui import (
    QPainter,
    QColor,
    QFont,
    QIcon,
    QLinearGradient,
    QTextDocument,
    QBrush,
    QCursor,
    QPen,
    QPixmap,
    QImage,
    QPageSize,
)
from PySide6.QtCharts import (
    QChart,
    QChartView,
    QPieSeries,
    QPieSlice,
    QBarSeries,
    QBarSet,
    QBarCategoryAxis,
    QValueAxis,
    QLineSeries,
)

# Importar clases base
from app.views.tabs.base_tab import BaseTab
from app.controllers.dashboard_controller import DashboardController

# Para exportación a PDF
try:
    from PySide6.QtPrintSupport import QPrinter
    from PySide6.QtGui import QTextDocument
    from reportlab.lib import pagesizes
    from reportlab.lib.pagesizes import letter, A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        Image,
        PageBreak,
    )
    from reportlab.pdfgen import canvas
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    logger = logging.getLogger(__name__)
    logger.warning("QPrinter no disponible - funcionalidad PDF desactivada")

logger = logging.getLogger(__name__)


# ============================================================================
# CLASES AUXILIARES (OPTIMIZADAS PARA USAR ESTILOS BASEVIEW)
# ============================================================================


class StatCard(QFrame):
    """Tarjeta de estadística optimizada usando estilos BaseView"""

    def __init__(
        self,
        title: str,
        value: str,
        icon: str = "",
        color_key: str = "secondary",
        change_text: str = "",
        change_positive: bool = True,
        colors: Optional[Dict[str, str]] = None,
        sizes: Optional[Dict[str, int]] = None,
        parent=None,
    ):
        """
        Inicializa una tarjeta de estadística

        Args:
            title: Título de la tarjeta
            value: Valor principal a mostrar
            icon: Ícono/emoji (opcional)
            color_key: Clave de color de BaseView.COLORS
            change_text: Texto de cambio/tendencia
            change_positive: Si el cambio es positivo
            colors: Diccionario de colores (opcional, usa BaseView.COLORS por defecto)
            sizes: Diccionario de tamaños (opcional, usa BaseView.SIZES por defecto)
        """
        super().__init__(parent)

        self.title = title
        self.value = value
        self.icon = icon
        self.color_key = color_key
        self.change_text = change_text
        self.change_positive = change_positive

        # Usar colores y tamaños proporcionados o los de BaseView
        self.colors = colors or self._get_default_colors()
        self.sizes = sizes or self._get_default_sizes()

        self._setup_ui()

    def _get_default_colors(self) -> Dict[str, str]:
        """Obtiene los colores por defecto de BaseView"""
        try:
            # Intentar importar BaseView para obtener los colores por defecto
            from app.views.base_view import BaseView

            return BaseView.COLORS
        except ImportError:
            # Si no se puede importar, usar valores por defecto
            return {
                "secondary": "#3498DB",
                "success": "#27AE60",
                "warning": "#F39C12",
                "danger": "#E74C3C",
                "info": "#17A2B8",
                "gray": "#95A5A6",
                "card_background": "#FFFFFF",
                "border": "#D1D5DB",
                "light": "#ECF0F1",
            }

    def _get_default_sizes(self) -> Dict[str, int]:
        """Obtiene los tamaños por defecto de BaseView"""
        try:
            from app.views.base_view import BaseView

            return BaseView.SIZES
        except ImportError:
            return {"border_radius": 4}

    def _setup_ui(self):
        """Configura la interfaz usando estilos BaseView"""
        self.setObjectName("StatCard")

        # Configurar dimensiones
        self.setMinimumHeight(140)
        self.setMaximumHeight(160)
        self.setMinimumWidth(180)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        # Fila superior: Icono y título
        top_layout = QHBoxLayout()

        # Icono (si se proporciona)
        if self.icon:
            icon_label = QLabel(self.icon)
            icon_label.setStyleSheet(
                f"""
                QLabel {{
                    font-size: 24px;
                    color: {self.colors.get(self.color_key, self.colors['secondary'])};
                }}
            """
            )
            top_layout.addWidget(icon_label)

        top_layout.addStretch()

        # Título
        title_label = QLabel(self.title)
        title_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 12px;
                color: {self.colors['gray']};
                font-weight: bold;
            }}
        """
        )
        title_label.setWordWrap(True)
        top_layout.addWidget(title_label)

        layout.addLayout(top_layout)

        # Valor principal
        value_label = QLabel(self.value)
        value_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                color: {self.colors.get(self.color_key, self.colors['secondary'])};
                padding: 8px 0;
            }}
        """
        )
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)

        # Cambio/tendencia (si se proporciona)
        if self.change_text:
            change_color = (
                self.colors["success"]
                if self.change_positive
                else self.colors["danger"]
            )
            change_icon = "▲" if self.change_positive else "▼"

            change_label = QLabel(f"{change_icon} {self.change_text}")
            change_label.setStyleSheet(
                f"""
                QLabel {{
                    font-size: 11px;
                    color: {change_color};
                    font-weight: bold;
                    padding: 3px 8px;
                    background-color: {change_color}15;
                    border-radius: 10px;
                    margin-top: 4px;
                }}
            """
            )
            change_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(change_label)

        layout.addStretch()

        # Estilo de la tarjeta usando estilos BaseView
        border_radius = self.sizes.get("border_radius", 4)

        self.setStyleSheet(
            f"""
            #StatCard {{
                background-color: {self.colors['card_background']};
                border-radius: {border_radius * 2}px;
                border: 1px solid {self.colors['border']};
            }}
            #StatCard:hover {{
                border: 2px solid {self.colors.get(self.color_key, self.colors['secondary'])}60;
                background-color: {self.colors['light']};
            }}
        """
        )


# ============================================================================
# CLASE PRINCIPAL: DASHBOARDTAB
# ============================================================================


class DashboardTab(BaseTab):
    """Dashboard principal del sistema FormaGestPro"""

    # Señales específicas del dashboard
    dashboard_updated = Signal(dict)
    export_completed = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        """Inicializar dashboard"""
        super().__init__(parent, "Dashboard")

        # Definir todos los atributos
        self.status_label = None
        self.charts_grid: QGridLayout = QGridLayout()
        self.metrics_grid: QGridLayout = QGridLayout()
        self.dashboard_data: dict = {}
        self.stat_cards: dict = {}

        logger.info("🚀 Inicializando DashboardTab (versión BaseTab)...")

        # Inicializar controlador
        self.controller = DashboardController()

        # Variables para gráficos
        self.charts = {}
        self.stat_cards = {}

        # Configurar UI específica del dashboard
        self.setup_ui()
        self.setup_connections()
        self.setup_timers()

        # Cargar datos iniciales
        self.load_data()

        logger.info("✅ DashboardTab inicializado correctamente")

    # ============================================================================
    # MÉTODOS DE CONFIGURACIÓN
    # ============================================================================

    def setup_ui(self):
        """Configura la interfaz de usuario del dashboard"""
        # Limpiar UI base
        self._clear_layout(self.main_layout)

        # Ajustar márgenes
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Crear área de scroll para contenido
        scroll_area = self._create_scroll_area()

        # 2. Crear widget de contenido
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setSpacing(self.SIZES["spacing_large"])
        self.content_layout.setContentsMargins(
            self.SIZES["padding_large"],
            self.SIZES["padding_large"],
            self.SIZES["padding_large"],
            self.SIZES["padding_large"] * 2,
        )

        # 2.1 Encabezado del dashboard
        self._create_dashboard_header()

        # 2.2 Barra de herramientas
        self._create_toolbar()

        # 2.3 Tarjetas de métricas principales
        self._create_metrics_cards()

        # 2.4 Sección de gráficos
        self._create_charts_section()

        # 2.5 Sección inferior (tablas/información detallada)
        self._create_bottom_section()

        scroll_area.setWidget(content_widget)
        self.main_layout.addWidget(scroll_area)

    def _create_scroll_area(self) -> QScrollArea:
        """Crea un área de scroll para el dashboard"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Aplicar estilos usando BaseView
        scroll_area.setStyleSheet(
            f"""
            QScrollArea {{
                border: none;
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
        """
        )

        return scroll_area

    def _create_dashboard_header(self):
        """Crea el encabezado del dashboard"""
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, self.SIZES["spacing_medium"])
        header_layout.setSpacing(self.SIZES["spacing_small"])

        # Título principal usando create_tab_header de BaseTab
        title_label = self.create_tab_header(
            "🏠", "Panel de Control y Análisis en Tiempo Real"
        )
        header_layout.addWidget(title_label)

        # Información de fecha/hora
        time_widget = QWidget()
        time_layout = QHBoxLayout(time_widget)
        time_layout.setContentsMargins(0, 0, 0, 0)

        self.date_label = QLabel()
        self.date_label.setFont(self._create_font("small"))
        self.date_label.setStyleSheet(f"color: {self.COLORS['gray']};")

        self.time_label = QLabel()
        self.time_label.setFont(self._create_font("small"))
        self.time_label.setStyleSheet(
            f"""
            color: {self.COLORS['primary']};
            font-weight: bold;
            padding: 4px 8px;
            background-color: {self.COLORS['primary']}10;
            border-radius: {self.SIZES['border_radius']}px;
        """
        )

        time_layout.addWidget(self.date_label)
        time_layout.addStretch()
        time_layout.addWidget(self.time_label)

        header_layout.addWidget(time_widget)
        self.content_layout.addWidget(header_widget)

        # Guardar referencias
        self.widgets["date_label"] = self.date_label
        self.widgets["time_label"] = self.time_label

    def _create_toolbar(self):
        """Crea la barra de herramientas del dashboard"""
        toolbar_buttons = [
            {
                "text": "🔄 Actualizar",
                "command": self.refresh_dashboard,
                "style": "primary",
            },
            {
                "text": "📊 Exportar PDF",
                "command": self.export_to_pdf,
                "style": "success",
            },
            {"text": "⚙️ Configurar", "command": self.show_settings, "style": "default"},
        ]

        toolbar = self.create_toolbar(toolbar_buttons)
        self.content_layout.addWidget(toolbar)

    def _create_metrics_cards(self):
        """Crea las tarjetas de métricas principales"""
        metrics_frame = QFrame()
        metrics_layout = QGridLayout(metrics_frame)
        metrics_layout.setSpacing(self.SIZES["spacing_medium"])
        metrics_layout.setContentsMargins(0, 0, 0, 0)

        # Configurar 4 columnas para las tarjetas
        self.metrics_grid = metrics_layout
        self.content_layout.addWidget(metrics_frame)

        # Las tarjetas se crearán dinámicamente cuando se carguen los datos
        self.widgets["metrics_frame"] = metrics_frame

    def _create_charts_section(self):
        """Crea la sección de gráficos"""
        charts_container = QWidget()
        charts_layout = QVBoxLayout(charts_container)
        charts_layout.setSpacing(self.SIZES["spacing_large"])

        # Título de la sección
        charts_title = QLabel("📈 Análisis Visual")
        charts_title.setFont(self._create_font("header"))
        charts_title.setStyleSheet(
            f"""
            QLabel {{
                color: {self.COLORS['primary']};
                border-bottom: 1px solid {self.COLORS['border']};
                padding-bottom: {self.SIZES['padding_small']}px;
            }}
        """
        )
        charts_layout.addWidget(charts_title)

        # Contenedor para gráficos (2 columnas)
        self.charts_widget = QWidget()
        self.charts_grid = QGridLayout(self.charts_widget)
        self.charts_grid.setSpacing(self.SIZES["spacing_medium"])
        self.charts_grid.setContentsMargins(0, 0, 0, 0)

        charts_layout.addWidget(self.charts_widget)
        self.content_layout.addWidget(charts_container)

        self.widgets["charts_container"] = charts_container

    def _create_bottom_section(self):
        """Crea la sección inferior con información detallada"""
        bottom_container = QWidget()
        bottom_layout = QVBoxLayout(bottom_container)
        bottom_layout.setSpacing(self.SIZES["spacing_large"])

        # Título de la sección
        bottom_title = QLabel("📋 Información Detallada")
        bottom_title.setFont(self._create_font("header"))
        bottom_title.setStyleSheet(
            f"""
            QLabel {{
                color: {self.COLORS['primary']};
                border-bottom: 1px solid {self.COLORS['border']};
                padding-bottom: {self.SIZES['padding_small']}px;
            }}
        """
        )
        bottom_layout.addWidget(bottom_title)

        # Tabla para información detallada
        self.detail_table = self.create_data_table(
            headers=["Categoría", "Valor", "Cambio", "Tendencia"],
            column_widths=[200, 100, 100, 100],
        )
        bottom_layout.addWidget(self.detail_table)

        self.content_layout.addWidget(bottom_container)
        self.widgets["detail_table"] = self.detail_table

    def setup_connections(self):
        """Configura las conexiones de señales"""
        super().setup_connections()

        # Conectar señal de actualización del dashboard
        self.dashboard_updated.connect(self.update_display)

        # Conectar señal de exportación completada
        self.export_completed.connect(self._on_export_completed)

    def setup_timers(self):
        """Configura los temporizadores"""
        # Temporizador para actualizar hora
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time_display)
        self.time_timer.start(1000)  # Actualizar cada segundo

        # Temporizador para actualizar datos (cada 30 segundos)
        self.data_timer = QTimer()
        self.data_timer.timeout.connect(self.refresh_data)
        self.data_timer.start(30000)

        # Actualizar inmediatamente
        self.update_time_display()

    # ============================================================================
    # MÉTODOS DE DATOS
    # ============================================================================

    def load_data(self):
        """Carga los datos del dashboard"""
        logger.info("📊 Cargando datos del dashboard...")

        try:
            # Obtener datos del controlador
            self.dashboard_data = self.controller.get_estadisticas_resumen()

            # Actualizar visualización
            self.update_display()

            logger.info("✅ Datos del dashboard cargados correctamente")

        except Exception as e:
            logger.error(f"❌ Error cargando datos: {e}")
            self.show_error(f"Error al cargar datos: {str(e)}")

            # Usar datos de ejemplo
            self._load_sample_data()

    def _load_sample_data(self):
        """Carga datos de ejemplo para fallback"""
        self.dashboard_data = {
            "resumen": {
                "total_estudiantes": 0,
                "total_docentes": 0,
                "cursos_activos": 0,
                "total_cursos": 0,
            },
            "distribuciones": {
                "estudiantes_genero": [],
                "docentes_genero": [],
                "estudiantes_programa": [],
                "docentes_departamento": [],
            },
        }

    def refresh_data(self):
        """Actualiza los datos del dashboard"""
        logger.debug("🔄 Actualizando datos del dashboard...")

        try:
            # Forzar actualización de cache
            new_data = self.controller.actualizar_datos()
            self.dashboard_data = new_data

            # Actualizar visualización
            self.update_display()

            # Emitir señal
            self.dashboard_updated.emit(new_data)

            logger.debug("✅ Datos actualizados correctamente")

        except Exception as e:
            logger.error(f"❌ Error actualizando datos: {e}")

    # ============================================================================
    # MÉTODOS DE VISUALIZACIÓN
    # ============================================================================

    def update_display(self):
        """Actualiza toda la visualización del dashboard"""
        if not hasattr(self, "dashboard_data"):
            return

        # 1. Actualizar tarjetas de métricas
        self._update_metrics_cards()

        # 2. Actualizar gráficos
        self._update_charts()

        # 3. Actualizar tabla de detalles
        self._update_detail_table()

        # 4. Actualizar estado
        self._update_status()

    def _update_metrics_cards(self):
        """Actualiza las tarjetas de métricas"""
        if not hasattr(self, "metrics_grid"):
            return

        # Limpiar tarjetas existentes
        while self.metrics_grid.count():
            item = self.metrics_grid.takeAt(0)  # Toma el primer item
            if item and item.widget():
                item.widget().deleteLater()  # type: ignore
            # El item se elimina automáticamente cuando se usa takeAt()

        # Definir métricas a mostrar
        metrics = [
            {
                "title": "Estudiantes",
                "key": "total_estudiantes",
                "icon": "👨‍🎓",
                "color": "secondary",
                "change": "+3 este mes",
            },
            {
                "title": "Docentes",
                "key": "total_docentes",
                "icon": "👨‍🏫",
                "color": "success",
                "change": "+1 este mes",
            },
            {
                "title": "Cursos Activos",
                "key": "cursos_activos",
                "icon": "📚",
                "color": "warning",
                "change": "3 activos",
            },
            {
                "title": "Total Cursos",
                "key": "total_cursos",
                "icon": "🏫",
                "color": "info",
                "change": "+2 este año",
            },
        ]

        # Crear tarjetas
        resumen = self.dashboard_data.get("resumen", {})

        for i, metric in enumerate(metrics):
            value = resumen.get(metric["key"], 0)

            card = StatCard(
                title=metric["title"],
                value=str(value),
                icon=metric["icon"],
                color_key=metric["color"],
                change_text=metric.get("change", ""),
                change_positive=True,
                parent=self,
            )

            self.metrics_grid.addWidget(card, 0, i)
            self.stat_cards[metric["key"]] = card

    def _update_charts(self):
        """Actualiza los gráficos del dashboard"""
        if not hasattr(self, "charts_grid"):
            return

        # Limpiar gráficos existentes
        while self.charts_grid.count():
            item = self.charts_grid.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()

        # Crear gráficos
        distribuciones = self.dashboard_data.get("distribuciones", {})

        # Gráfico 1: Estudiantes por género
        if "estudiantes_genero" in distribuciones:
            chart1 = self._create_pie_chart(
                data=distribuciones["estudiantes_genero"],
                title="Estudiantes por Género",
                colors=[
                    self.COLORS["secondary"],
                    self.COLORS["info"],
                    self.COLORS["warning"],
                ],
            )
            self.charts_grid.addWidget(chart1, 0, 0)

        # Gráfico 2: Docentes por género
        if "docentes_genero" in distribuciones:
            chart2 = self._create_pie_chart(
                data=distribuciones["docentes_genero"],
                title="Docentes por Género",
                colors=[
                    self.COLORS["success"],
                    self.COLORS["info"],
                    self.COLORS["warning"],
                ],
            )
            self.charts_grid.addWidget(chart2, 0, 1)

        # Gráfico 3: Estudiantes por programa (Top 5)
        if "estudiantes_programa" in distribuciones:
            chart3 = self._create_bar_chart(
                data=distribuciones["estudiantes_programa"],
                title="Top Programas (Estudiantes)",
                color=self.COLORS["secondary"],
            )
            self.charts_grid.addWidget(chart3, 1, 0)

        # Gráfico 4: Docentes por departamento (Top 5)
        if "docentes_departamento" in distribuciones:
            chart4 = self._create_bar_chart(
                data=distribuciones["docentes_departamento"],
                title="Top Departamentos (Docentes)",
                color=self.COLORS["success"],
            )
            self.charts_grid.addWidget(chart4, 1, 1)

    def _create_pie_chart(
        self, data: List[Dict], title: str, colors: List[str]
    ) -> QChartView:
        """Crea un gráfico de pastel"""
        series = QPieSeries()
        series.setHoleSize(0.3)  # Para gráfico de dona

        # Añadir datos
        for i, item in enumerate(data):
            nombre = item.get("genero", item.get("nombre", f"Item {i}"))
            valor = item.get("cantidad", 0)

            if valor > 0:
                slice = QPieSlice(f"{nombre}: {valor}", valor)
                slice.setColor(QColor(colors[i % len(colors)]))
                slice.setLabelVisible(True)
                series.append(slice)

        # Crear chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(title)
        chart.setTitleFont(self._create_font("subtitle"))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        # Crear vista
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setMinimumHeight(300)

        # Aplicar estilos
        chart_view.setStyleSheet(
            f"""
            QChartView {{
                background-color: {self.COLORS["white"]};
                border: 1px solid {self.COLORS["border"]};
                border-radius: {self.SIZES["border_radius"]}px;
            }}
        """
        )

        return chart_view

    def _create_bar_chart(self, data: List[Dict], title: str, color: str) -> QChartView:
        """Crea un gráfico de barras"""
        series = QBarSeries()
        bar_set = QBarSet("")

        labels = []
        values = []

        # Preparar datos
        for item in data[:5]:  # Limitar a top 5
            nombre = item.get(
                "programa", item.get("departamento", item.get("nombre", ""))
            )
            valor = item.get("cantidad", 0)

            if nombre and valor > 0:
                labels.append(nombre[:15] + "..." if len(nombre) > 15 else nombre)
                values.append(valor)
                bar_set.append(valor)

        # Configurar color de barras
        bar_set.setColor(QColor(color))
        bar_set.setBorderColor(QColor(color))

        series.append(bar_set)

        # Crear chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(title)
        chart.setTitleFont(self._create_font("subtitle"))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        # Configurar ejes
        axis_x = QBarCategoryAxis()
        axis_x.append(labels)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setRange(0, max(values) * 1.2 if values else 10)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        # Crear vista
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setMinimumHeight(300)

        # Aplicar estilos
        chart_view.setStyleSheet(
            f"""
            QChartView {{
                background-color: {self.COLORS["white"]};
                border: 1px solid {self.COLORS["border"]};
                border-radius: {self.SIZES["border_radius"]}px;
            }}
        """
        )

        return chart_view

    def _update_detail_table(self):
        """Actualiza la tabla de detalles"""
        if not hasattr(self, "detail_table"):
            return

        table = self.detail_table
        table.setRowCount(0)

        # Añadir datos a la tabla
        resumen = self.dashboard_data.get("resumen", {})

        rows = [
            [
                "Estudiantes Totales",
                str(resumen.get("total_estudiantes", 0)),
                "+3",
                "↗️",
            ],
            ["Docentes Totales", str(resumen.get("total_docentes", 0)), "+1", "↗️"],
            ["Cursos Activos", str(resumen.get("cursos_activos", 0)), "0", "➡️"],
            ["Total Cursos", str(resumen.get("total_cursos", 0)), "+2", "↗️"],
            ["Inscripciones Activas", "24", "+2", "↗️"],
            ["Ocupación Promedio", "85%", "+5%", "↗️"],
        ]

        table.setRowCount(len(rows))

        for i, row in enumerate(rows):
            for j, cell in enumerate(row):
                item = QTableWidgetItem(cell)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Estilizar según el tipo de dato
                if j == 0:  # Categoría
                    item.setFont(self._create_font("small"))
                elif j == 3:  # Tendencia
                    item.setFont(QFont("Segoe UI Emoji", 10))

                table.setItem(i, j, item)

    def _update_status(self):
        """Actualiza el estado del dashboard"""
        total_estudiantes = self.dashboard_data.get("resumen", {}).get(
            "total_estudiantes", 0
        )
        total_docentes = self.dashboard_data.get("resumen", {}).get("total_docentes", 0)

        status_text = f"✅ Sistema activo | Estudiantes: {total_estudiantes} | Docentes: {total_docentes}"

        # Podrías actualizar una barra de estado si tienes una
        if hasattr(self, "status_label"):
            self.status_label.setText(status_text)  # type: ignore

    # ============================================================================
    # MÉTODOS DE INTERACCIÓN
    # ============================================================================

    @Slot()
    def refresh_dashboard(self):
        """Actualiza manualmente el dashboard"""
        logger.info("🔄 Actualización manual del dashboard solicitada")

        # Mostrar indicador de carga
        self.show_message("Actualizando", "Cargando datos más recientes...", "info")  # type: ignore

        # Actualizar datos
        self.refresh_data()

        # Mostrar confirmación
        self.show_success("Dashboard actualizado correctamente")

    @Slot()
    def export_to_pdf(self):
        """Exporta el dashboard a PDF"""
        if not PDF_SUPPORT:
            self.show_error("La funcionalidad de exportación a PDF no está disponible")
            return

        logger.info("📄 Exportando dashboard a PDF...")

        # Solicitar ubicación para guardar
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Dashboard a PDF",
            f"dashboard_{QDateTime.currentDateTime().toString('yyyyMMdd_HHmmss')}.pdf",
            "PDF Files (*.pdf)",
        )

        if not file_path:
            return  # Usuario canceló

        try:
            # Crear documento HTML para el PDF
            html_content = self._generate_pdf_html()

            # Crear documento y configurar impresora
            document = QTextDocument()
            document.setHtml(html_content)

            # En PyQt6, QPrinter está en QtPrintSupport
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_path)

            # Configurar tamaño de página (PyQt6)
            printer.setPageSize(letter)  # type: ignore
            printer.setPageOrientation(
                QPrinter.PaQPrinter.setPageSizegeOrientation.Portrait  # type: ignore
            )

            # Imprimir - en PyQt6 se usa print() en lugar de print_()
            # Alternativamente, puedes usar QPainter
            document.print_(printer)  # Nota: en PyQt6 se llama print_() con guión bajo

            # Emitir señal
            self.export_completed.emit(file_path)

            logger.info(f"✅ Dashboard exportado a: {file_path}")
            self.show_success(f"Dashboard exportado correctamente a:\n{file_path}")

        except Exception as e:
            logger.error(f"❌ Error exportando a PDF: {e}")
            self.show_error(f"Error al exportar PDF: {str(e)}")

    def _generate_pdf_html(self) -> str:
        """Genera contenido HTML para el PDF"""
        resumen = self.dashboard_data.get("resumen", {})

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Dashboard FormaGestPro</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .title {{ font-size: 24px; font-weight: bold; color: #2C3E50; }}
                .subtitle {{ font-size: 14px; color: #7F8C8D; margin-top: 5px; }}
                .date {{ font-size: 12px; color: #95A5A6; margin-top: 10px; }}
                .metrics {{ display: flex; justify-content: space-between; margin: 20px 0; }}
                .metric-card {{ 
                    border: 1px solid #ECF0F1; 
                    border-radius: 8px; 
                    padding: 15px; 
                    text-align: center;
                    flex: 1;
                    margin: 0 10px;
                }}
                .metric-value {{ font-size: 28px; font-weight: bold; margin: 10px 0; }}
                .metric-title {{ font-size: 14px; color: #7F8C8D; }}
                .section {{ margin-top: 30px; }}
                .section-title {{ 
                    font-size: 18px; 
                    font-weight: bold; 
                    color: #2C3E50;
                    border-bottom: 2px solid #3498DB;
                    padding-bottom: 5px;
                    margin-bottom: 15px;
                }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th {{ background-color: #2C3E50; color: white; padding: 10px; text-align: left; }}
                td {{ padding: 8px; border-bottom: 1px solid #ECF0F1; }}
                tr:nth-child(even) {{ background-color: #F8F9F9; }}
                .footer {{ margin-top: 40px; text-align: center; font-size: 12px; color: #95A5A6; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">🏠 Dashboard FormaGestPro</div>
                <div class="subtitle">Panel de Control y Análisis del Sistema</div>
                <div class="date">Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>
            </div>
            
            <div class="section">
                <div class="section-title">📊 Métricas Principales</div>
                <div class="metrics">
                    <div class="metric-card">
                        <div class="metric-title">Estudiantes</div>
                        <div class="metric-value" style="color: #3498DB;">{resumen.get('total_estudiantes', 0)}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Docentes</div>
                        <div class="metric-value" style="color: #27AE60;">{resumen.get('total_docentes', 0)}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Cursos Activos</div>
                        <div class="metric-value" style="color: #E67E22;">{resumen.get('cursos_activos', 0)}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Total Cursos</div>
                        <div class="metric-value" style="color: #9B59B6;">{resumen.get('total_cursos', 0)}</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">📋 Información Detallada</div>
                <table>
                    <tr>
                        <th>Categoría</th>
                        <th>Valor</th>
                        <th>Cambio</th>
                        <th>Tendencia</th>
                    </tr>
                    <tr>
                        <td>Estudiantes Totales</td>
                        <td>{resumen.get('total_estudiantes', 0)}</td>
                        <td>+3</td>
                        <td>↗️</td>
                    </tr>
                    <tr>
                        <td>Docentes Totales</td>
                        <td>{resumen.get('total_docentes', 0)}</td>
                        <td>+1</td>
                        <td>↗️</td>
                    </tr>
                    <tr>
                        <td>Cursos Activos</td>
                        <td>{resumen.get('cursos_activos', 0)}</td>
                        <td>0</td>
                        <td>➡️</td>
                    </tr>
                    <tr>
                        <td>Total Cursos</td>
                        <td>{resumen.get('total_cursos', 0)}</td>
                        <td>+2</td>
                        <td>↗️</td>
                    </tr>
                    <tr>
                        <td>Inscripciones Activas</td>
                        <td>24</td>
                        <td>+2</td>
                        <td>↗️</td>
                    </tr>
                    <tr>
                        <td>Ocupación Promedio</td>
                        <td>85%</td>
                        <td>+5%</td>
                        <td>↗️</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <div class="section-title">📈 Distribuciones</div>
                <p><strong>Estudiantes por Programa (Top 5):</strong></p>
                <ul>
        """

        # Añadir programas top
        distribuciones = self.dashboard_data.get("distribuciones", {})
        estudiantes_programa = distribuciones.get("estudiantes_programa", [])[:5]

        for programa in estudiantes_programa:
            nombre = programa.get("programa", programa.get("nombre", "Desconocido"))
            cantidad = programa.get("cantidad", 0)
            html += f"<li>{nombre}: {cantidad} estudiantes</li>"

        html += """
                </ul>
                
                <p><strong>Docentes por Departamento (Top 5):</strong></p>
                <ul>
        """

        # Añadir departamentos top
        docentes_departamento = distribuciones.get("docentes_departamento", [])[:5]

        for depto in docentes_departamento:
            nombre = depto.get("departamento", depto.get("nombre", "Desconocido"))
            cantidad = depto.get("cantidad", 0)
            html += f"<li>{nombre}: {cantidad} docentes</li>"

        html += f"""
                </ul>
            </div>
            
            <div class="footer">
                <p>FormaGestPro - Sistema de Gestión Académica</p>
                <p>Documento generado automáticamente. Para más información, consulte el sistema.</p>
            </div>
        </body>
        </html>
        """

        return html

    def _on_export_completed(self, file_path: str):
        """Maneja la finalización de la exportación"""
        logger.debug(f"Exportación completada: {file_path}")
        # Podrías agregar más lógica aquí, como abrir el archivo, etc.

    @Slot()
    def show_settings(self):
        """Muestra la configuración del dashboard"""
        self.show_message(
            "Configuración del Dashboard",
            "Aquí puedes configurar:\n"
            "• Intervalo de actualización\n"
            "• Métricas a mostrar\n"
            "• Estilos del dashboard\n"
            "• Opciones de exportación",
            QMessageBox.Icon.Information,  # Usar el enum correcto
        )

    # ============================================================================
    # MÉTODOS DE UTILIDAD
    # ============================================================================

    @Slot()
    def update_time_display(self):
        """Actualiza la visualización de fecha y hora"""
        now = datetime.now()

        if hasattr(self, "date_label"):
            self.date_label.setText(now.strftime("%A, %d de %B de %Y"))

        if hasattr(self, "time_label"):
            self.time_label.setText(now.strftime("%H:%M:%S"))

    def _clear_layout(self, layout):
        """Limpia un layout de manera segura"""
        if not layout:
            return

        while layout.count():
            item = layout.takeAt(0)
            if item is None:
                continue

            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    # ============================================================================
    # MÉTODOS HEREDADOS DE BASETAB (SOBRESCRITOS)
    # ============================================================================

    def load_page_data(self):
        """Carga los datos de la página actual (requerido por BaseTab)"""
        # Para el dashboard, no usamos paginación
        self.load_data()

    def apply_filters(self):
        """Aplica filtros (requerido por BaseTab)"""
        # El dashboard no tiene filtros tradicionales
        pass

    def clear_filters(self):
        """Limpia filtros (requerido por BaseTab)"""
        # El dashboard no tiene filtros tradicionales
        pass


# ============================================================================
# PUNTO DE ENTRADA PARA PRUEBAS
# ============================================================================

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Crear aplicación de prueba
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    # Crear dashboard
    dashboard = DashboardTab()
    dashboard.resize(1200, 800)
    dashboard.show()

    # Ejecutar aplicación
    sys.exit(app.exec())
