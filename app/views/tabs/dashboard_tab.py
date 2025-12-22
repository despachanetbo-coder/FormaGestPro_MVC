"""
app/views/tabs/dashboard_tab.py
Dashboard completo con gráficos y estadísticas en tiempo real
Versión: 3.0 - Optimizada, sin código innecesario, usa controlador

ESTRUCTURA:
1. Imports
2. Clases auxiliares (AnimatedCard, StatCard)
3. Clase principal DashboardTab:
   - Constructor y métodos básicos
   - Métodos de UI (setup_ui, create_header, etc.)
   - Métodos de gráficos (create_students_chart, create_financial_chart)
   - Métodos de eventos/interacción
   - Métodos de exportación
   - Métodos auxiliares de UI
"""

import sys
from datetime import datetime
from typing import Dict, List, Any

# PySide6 imports
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QPushButton, QGroupBox,
    QSizePolicy, QScrollArea, QProgressBar,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QSplitter, QMessageBox, QComboBox,
    QToolTip, QFileDialog
)
from PySide6.QtCore import (
    Qt, QTimer, QDate, QDateTime,
    Signal, Slot, QPropertyAnimation,
    QEasingCurve, QParallelAnimationGroup
)
from PySide6.QtGui import (
    QPainter, QLinearGradient,
    QBrush, QColor, QIcon, QCursor
)
from PySide6.QtCharts import (
    QChart, QChartView, QPieSeries, QPieSlice,
    QBarSeries, QBarSet, QBarCategoryAxis,
    QValueAxis, QLineSeries, QSplineSeries,
    QDateTimeAxis, QAreaSeries, QLegend
)
from PySide6.QtGui import QPen

# Importar controlador
from app.controllers.dashboard_controller import DashboardController

# ============================================================================
# CLASES AUXILIARES
# ============================================================================

class AnimatedCard(QFrame):
    """Tarjeta con animación al pasar el mouse"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_animations()
    
    def setup_animations(self):
        """Configurar animaciones"""
        self.enter_animation = QPropertyAnimation(self, b"geometry")
        self.enter_animation.setDuration(200)
        self.enter_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.exit_animation = QPropertyAnimation(self, b"geometry")
        self.exit_animation.setDuration(200)
        self.exit_animation.setEasingCurve(QEasingCurve.InCubic)
    
    def enterEvent(self, event):
        """Animación al entrar"""
        geom = self.geometry()
        self.enter_animation.setStartValue(geom)
        self.enter_animation.setEndValue(geom.adjusted(-2, -2, 2, 2))
        self.enter_animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Animación al salir"""
        geom = self.geometry()
        self.exit_animation.setStartValue(geom)
        self.exit_animation.setEndValue(geom.adjusted(2, 2, -2, -2))
        self.exit_animation.start()
        super().leaveEvent(event)


class StatCard(AnimatedCard):
    """Tarjeta de estadística con animación"""
    def __init__(self, title: str, value: str, icon: str, 
                 color: str, change: str = "", 
                 min_height: int = 160, max_height: int = 170,
                 parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color
        self.change = change
        self.min_height = min_height
        self.max_height = max_height
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interfaz de la tarjeta"""
        self.setObjectName("StatCard")
        
        # Control explícito de altura
        self.setMinimumHeight(self.min_height)
        self.setMaximumHeight(self.max_height)
        self.setMinimumWidth(180)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        # Fila superior: Icono y título
        top_layout = QHBoxLayout()
        
        # Icono
        icon_label = QLabel(self.icon)
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 32px;
                color: {self.color};
                font-family: 'Segoe UI Emoji';
            }}
        """)
        top_layout.addWidget(icon_label)
        top_layout.addStretch()
        
        # Título
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #7f8c8d;
                font-weight: bold;
            }
        """)
        title_label.setWordWrap(True)
        top_layout.addWidget(title_label)
        layout.addLayout(top_layout)
        
        # Valor principal
        value_label = QLabel(self.value)
        value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 20px;
                font-weight: bold;
                color: {self.color};
                padding: 10px 0;
            }}
        """)
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        # Cambio (si existe)
        if self.change:
            change_label = QLabel(self.change)
            
            # Determinar color basado en si es positivo/negativo
            if "+" in self.change:
                change_color = "#27ae60"
                change_text = f"▲ {self.change}"
            elif "-" in self.change:
                change_color = "#e74c3c"
                change_text = f"▼ {self.change}"
            else:
                change_color = "#f39c12"
                change_text = self.change
            
            change_label.setText(change_text)
            change_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 13px;
                    color: {change_color};
                    font-weight: bold;
                    padding: 4px 10px;
                    background-color: {change_color}15;
                    border-radius: 12px;
                    margin-top: 5px;
                }}
            """)
            change_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(change_label)
        
        layout.addStretch()
        
        # Estilo de la tarjeta
        self.setStyleSheet(f"""
            #StatCard {{
                background-color: white;
                border-radius: 12px;
                border: 2px solid #ecf0f1;
                padding: 5px;
            }}
            #StatCard:hover {{
                border: 3px solid {self.color}60;
                background-color: #f8f9fa;
            }}
        """)


# ============================================================================
# CLASE PRINCIPAL: DASHBOARDTAB
# ============================================================================

class DashboardTab(QWidget):
    """Dashboard principal del sistema FormaGestPro - Versión optimizada"""
    
    # Señales
    data_updated = Signal()
    refresh_requested = Signal()
    
    def __init__(self, parent=None):
        """Inicializar dashboard"""
        super().__init__(parent)
        print("🔧 Inicializando DashboardTab...")
        
        # Inicializar controlador
        self.controller = DashboardController()
        
        # Cargar datos iniciales
        self.load_data()
        
        # Configuración UI
        self.setup_ui()
        self.setup_connections()
        self.setup_animations()
        self.setup_timers()
        
        print("✅ DashboardTab inicializado correctamente")
    
    # ============================================================================
    # MÉTODOS DE CONFIGURACIÓN
    # ============================================================================
    
    def setup_ui(self):
        """Configurar interfaz de usuario completa"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 1. Encabezado con gradiente
        self.create_header(main_layout)
        
        # 2. Contenedor principal con scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f5f7fa;
            }
            QScrollArea > QWidget > QWidget {
                background-color: #f5f7fa;
            }
        """)
        
        # Widget contenido del scroll
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f5f7fa;")
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setSpacing(20)
        self.content_layout.setContentsMargins(20, 20, 20, 40)
        
        # 2.1 Estadísticas principales
        self.create_main_stats(self.content_layout)
        
        # 2.2 Gráficos y tablas
        self.create_charts_section(self.content_layout)
        
        # 2.3 Actividad reciente y programas
        self.create_bottom_section(self.content_layout)
        
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        # 3. Barra de herramientas inferior
        self.create_bottom_toolbar(main_layout)
    
    def setup_connections(self):
        """Configurar conexiones de señales"""
        self.data_updated.connect(self.update_display)
        self.refresh_requested.connect(self.refresh_dashboard)
    
    def setup_animations(self):
        """Configurar animaciones"""
        self.animation_group = QParallelAnimationGroup()
    
    def setup_timers(self):
        """Configurar temporizadores"""
        # Temporizador para la hora actual
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        
        # Temporizador para actualización de datos
        self.data_timer = QTimer()
        self.data_timer.timeout.connect(self.refresh_data)
        self.data_timer.start(30000)
        
        # Actualizar hora inmediatamente
        self.update_time()
    
    # ============================================================================
    # MÉTODOS DE DATOS
    # ============================================================================
    
    def load_data(self):
        """Cargar datos del dashboard usando el controlador"""
        print("📊 Cargando datos del dashboard...")
        try:
            self.dashboard_data = self.controller.obtener_datos_dashboard()
            print(f"✅ Datos cargados: {len(self.dashboard_data.get('programas_en_progreso', []))} programas")
        except Exception as e:
            print(f"⚠️  Error cargando datos: {e}")
            self.dashboard_data = self._get_sample_data()
    
    def _get_sample_data(self):
        """Datos de ejemplo para fallback"""
        año_actual = datetime.now().strftime('%Y')
        mes_actual = datetime.now().strftime('%B')
        
        return {
            'total_estudiantes': 24,
            'total_docentes': 8,
            'programas_activos': 6,
            'programas_registrados_2025': 10,
            'ingresos_mes_actual': 15240.0,
            'gastos_mes_actual': 5200.0,
            'estudiantes_por_programa': {},
            'programas_en_progreso': [],
            'datos_financieros': [],
            'año_actual': año_actual,
            'mes_actual_nombre': mes_actual,
            'estudiantes_cambio': '+3 este mes',
            'docentes_cambio': '+1 este mes',
            'programas_cambio': '3 activos',
            'programas_cambio_año': '+2 este año',
            'ingresos_cambio': '+12%',
            'gastos_cambio': '-8%',
            'programas_total': 6,
            'programas_año_actual': 8,
            'ingresos_mes': 15240.0,
            'gastos_mes': 5200.0,
            'total_programas_activos': 0,
            'ocupacion_promedio': 0,
            'total_estudiantes_matriculados': 0
        }
    
    # ============================================================================
    # MÉTODOS DE UI - SECCIÓN PRINCIPAL
    # ============================================================================
    
    def create_header(self, parent_layout):
        """Crear encabezado con gradiente"""
        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_frame.setMinimumHeight(120)
        header_frame.setMaximumHeight(130)
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(40, 20, 40, 30)
        
        # Fila superior: Título y hora
        top_row = QHBoxLayout()
        
        # Título
        title_label = QLabel("🏠 Panel de Control")
        title_label.setObjectName("DashboardTitle")
        title_label.setStyleSheet("""
            #DashboardTitle {
                font-size: 36px;
                font-weight: bold;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        top_row.addWidget(title_label)
        top_row.addStretch()
        
        # Hora actual
        self.time_label = QLabel()
        self.time_label.setObjectName("TimeLabel")
        self.time_label.setStyleSheet("""
            #TimeLabel {
                font-size: 14px;
                color: rgba(255, 255, 255, 0.9);
                font-weight: bold;
                padding: 8px 16px;
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }
        """)
        top_row.addWidget(self.time_label)
        header_layout.addLayout(top_row)
        
        # Subtítulo
        subtitle_label = QLabel("Panel de control y análisis en tiempo real del sistema")
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: rgba(255, 255, 255, 0.8);
                padding-top: 5px;
            }
        """)
        header_layout.addWidget(subtitle_label)
        header_layout.addStretch()
        
        # Estilo del encabezado con gradiente
        header_frame.setStyleSheet("""
            #HeaderFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db,
                    stop:0.5 #2980b9,
                    stop:1 #2c3e50
                );
                border-bottom: 3px solid #1a5276;
            }
        """)
        
        parent_layout.addWidget(header_frame)
    
    def create_main_stats(self, parent_layout):
        """Crear estadísticas principales"""
        # Crear grupo
        stats_group = QGroupBox("📊 MÉTRICAS DEL SISTEMA")
        stats_group.setMinimumHeight(380)
        stats_group.setMaximumHeight(450)
        
        # Layout de grid
        stats_layout = QGridLayout(stats_group)
        stats_layout.setSpacing(20)
        stats_layout.setContentsMargins(15, 40, 15, 25)
        
        # Obtener año y mes actual
        año_actual = self.dashboard_data.get('año_actual', datetime.now().strftime('%Y'))
        mes_actual = self.dashboard_data.get('mes_actual_nombre', 'el mes')
        
        # Configuración de tarjetas
        stats_config = [
            {
                'title': 'TOTAL ESTUDIANTES',
                'icon': '👤',
                'color': '#3498db',
                'value_key': 'total_estudiantes',
                'change_key': 'estudiantes_cambio',
                'prefix': '',
                'suffix': ''
            },
            {
                'title': 'DOCENTES ACTIVOS',
                'icon': '👨‍🏫',
                'color': '#9b59b6',
                'value_key': 'total_docentes',
                'change_key': 'docentes_cambio',
                'prefix': '',
                'suffix': ''
            },
            {
                'title': 'PROGRAMAS ACTIVOS',
                'icon': '📚',
                'color': '#2ecc71',
                'value_key': 'programas_activos',
                'change_key': 'programas_cambio',
                'prefix': '',
                'suffix': ''
            },
            {
                'title': f'PROGRAMAS EN {año_actual}',
                'icon': '📅',
                'color': '#1abc9c',
                'value_key': 'programas_año_actual',
                'change_key': 'programas_cambio_año',
                'prefix': '',
                'suffix': ''
            },
            {
                'title': f'INGRESOS EN {mes_actual.upper()}',
                'icon': '💰',
                'color': '#27ae60',
                'value_key': 'ingresos_mes',
                'change_key': 'ingresos_cambio',
                'prefix': 'Bs ',
                'suffix': ''
            },
            {
                'title': f'GASTOS EN {mes_actual.upper()}',
                'icon': '💸',
                'color': '#e74c3c',
                'value_key': 'gastos_mes',
                'change_key': 'gastos_cambio',
                'prefix': 'Bs ',
                'suffix': ''
            }
        ]
        
        # Crear tarjetas
        self.stat_cards = []
        
        for i, config in enumerate(stats_config):
            # Obtener valor
            value = self.dashboard_data.get(config['value_key'], 0)
            
            # Formatear valor
            if config['prefix'] == 'Bs ':
                value_str = f"Bs {value:,.2f}"
            else:
                value_str = str(value)
            
            # Obtener cambio
            change = self.dashboard_data.get(config['change_key'], "")
            
            # Crear tarjeta
            card = StatCard(
                title=config['title'],
                value=value_str,
                icon=config['icon'],
                color=config['color'],
                change=change,
                min_height=160,
                max_height=180
            )
            
            self.stat_cards.append(card)
            stats_layout.addWidget(card, i // 3, i % 3)
        
        parent_layout.addWidget(stats_group)
    
    def create_charts_section(self, parent_layout):
        """Crear sección de gráficos (2 columnas)"""
        # Contenedor para gráficos
        charts_container = QWidget()
        charts_layout = QHBoxLayout(charts_container)
        charts_layout.setSpacing(20)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        
        # Gráfico 1: Distribución de estudiantes
        chart1_widget = self.create_students_chart()
        charts_layout.addWidget(chart1_widget, 1)
        
        # Gráfico 2: Flujo financiero
        chart2_widget = self.create_financial_chart()
        charts_layout.addWidget(chart2_widget, 1)
        
        parent_layout.addWidget(charts_container)
    
    def create_bottom_section(self, parent_layout):
        """Crear sección inferior (actividad y estadísticas de programas)"""
        # Splitter horizontal
        bottom_splitter = QSplitter(Qt.Horizontal)
        bottom_splitter.setChildrenCollapsible(False)
        
        # Actividad reciente (izquierda)
        activity_widget = self.create_recent_activity()
        bottom_splitter.addWidget(activity_widget)
        
        # Resumen de programas (derecha)
        programs_summary_widget = self.create_programs_summary()
        bottom_splitter.addWidget(programs_summary_widget)
        
        # Ajustar proporciones
        bottom_splitter.setSizes([400, 400])
        parent_layout.addWidget(bottom_splitter)
    
    def create_bottom_toolbar(self, parent_layout):
        """Crear barra de herramientas inferior"""
        toolbar_frame = QFrame()
        toolbar_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-top: 1px solid #34495e;
                padding: 10px;
            }
        """)
        
        toolbar_layout = QHBoxLayout(toolbar_frame)
        
        # Información del sistema
        sys_info = QLabel(
            f"<span style='color: #ecf0f1;'>"
            f"FormaGestPro v3.0 • Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            f"</span>"
        )
        sys_info.setTextFormat(Qt.RichText)
        toolbar_layout.addWidget(sys_info)
        toolbar_layout.addStretch()
        
        # Botones de acción
        btn_refresh = QPushButton("🔄 Actualizar")
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                border: none;
                margin-right: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_refresh.clicked.connect(self.refresh_dashboard)
        
        btn_export = QPushButton("📊 Exportar Reporte")
        btn_export.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        btn_export.clicked.connect(self.export_report)
        
        toolbar_layout.addWidget(btn_refresh)
        toolbar_layout.addWidget(btn_export)
        
        parent_layout.addWidget(toolbar_frame)
    
    # ============================================================================
    # MÉTODOS DE GRÁFICOS
    # ============================================================================
    
    def create_students_chart(self):
        """Crear gráfico de distribución de estudiantes por programa"""
        group = QGroupBox("👥 DISTRIBUCIÓN DE ESTUDIANTES POR PROGRAMA")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
                border: 2px solid #ecf0f1;
                border-radius: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                background-color: white;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setContentsMargins(10, 30, 10, 20)
        
        try:
            # Obtener datos
            distribucion = self.dashboard_data.get('estudiantes_por_programa', {})
            
            if not distribucion:
                no_data_label = QLabel(
                    "<div style='text-align: center; padding: 40px;'>"
                    "<h3 style='color: #95a5a6;'>📭 Sin datos de estudiantes</h3>"
                    "<p>No hay estudiantes matriculados en programas.</p>"
                    "</div>"
                )
                no_data_label.setTextFormat(Qt.RichText)
                layout.addWidget(no_data_label)
                return group
            
            # Crear gráfico
            chart = QChart()
            chart.setTitle(f"Total estudiantes: {sum(distribucion.values())}")
            chart.setAnimationOptions(QChart.SeriesAnimations)
            chart.setTheme(QChart.ChartThemeLight)
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignBottom)
            chart.legend().setMarkerShape(QLegend.MarkerShapeCircle)
            
            # Crear serie de pastel (donut)
            series = QPieSeries()
            series.setHoleSize(0.35)  # Donut chart
            series.setPieSize(0.9)
            
            # Paleta de colores
            colors = [
                "#3498db", "#2ecc71", "#e74c3c", "#9b59b6", "#f39c12",
                "#1abc9c", "#34495e", "#e67e22", "#16a085", "#8e44ad",
                "#27ae60", "#d35400", "#c0392b", "#2980b9", "#f1c40f"
            ]
            
            # Agregar datos
            total_estudiantes = sum(distribucion.values())
            
            for i, (programa, cantidad) in enumerate(distribucion.items()):
                porcentaje = (cantidad / total_estudiantes * 100) if total_estudiantes > 0 else 0
                slice_label = f"{programa} ({cantidad})"
                slice_ = series.append(slice_label, cantidad)
                
                # Asignar color
                color_index = i % len(colors)
                slice_color = QColor(colors[color_index])
                slice_.setColor(slice_color)
                slice_.setBorderColor(QColor("#ffffff"))
                slice_.setBorderWidth(1)
                
                # Configurar etiqueta
                slice_.setLabelVisible(True)
                slice_.setLabelPosition(QPieSlice.LabelOutside)
                slice_.setLabel(f"{programa}\n{cantidad} estudiantes ({porcentaje:.1f}%)")
                
                # Conectar eventos
                slice_.hovered.connect(
                    lambda hovered, s=slice_, pn=programa, c=cantidad, pc=porcentaje: 
                    self.on_program_slice_hovered(hovered, s, pn, c, pc)
                )
                
                slice_.clicked.connect(
                    lambda checked, pn=programa: 
                    self.on_program_slice_clicked(pn)
                )
            
            # Agregar serie al chart
            chart.addSeries(series)
            
            # Crear vista del gráfico
            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart_view.setMinimumHeight(350)
            chart_view.setStyleSheet("""
                QChartView {
                    border-radius: 8px;
                    background-color: white;
                }
            """)
            
            layout.addWidget(chart_view)
            
            # Leyenda mejorada
            legend_frame = self.create_enhanced_legend(distribucion, colors)
            layout.addWidget(legend_frame)
            
            # Botones de acción
            action_frame = QFrame()
            action_layout = QHBoxLayout(action_frame)
            action_layout.setContentsMargins(0, 10, 0, 0)
            
            # Botón para ver detalle
            btn_detail = QPushButton("📋 Ver detalle por programa")
            btn_detail.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            btn_detail.clicked.connect(self.show_programs_detail)
            action_layout.addWidget(btn_detail)
            action_layout.addStretch()
            
            # Botón para actualizar
            btn_refresh = QPushButton("🔄 Actualizar")
            btn_refresh.setStyleSheet("""
                QPushButton {
                    background-color: #2c3e50;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #1a252f;
                }
            """)
            btn_refresh.clicked.connect(self.refresh_students_chart)
            action_layout.addWidget(btn_refresh)
            
            # Botón para exportar PDF
            btn_pdf = QPushButton("📄 Exportar PDF")
            btn_pdf.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            btn_pdf.clicked.connect(self.export_to_pdf)
            action_layout.addWidget(btn_pdf)
            
            layout.addWidget(action_frame)
            
        except Exception as e:
            print(f"⚠️  Error creando gráfico de estudiantes: {e}")
            error_label = QLabel(
                f"<div style='text-align: center; padding: 40px; color: #e74c3c;'>"
                f"<h3>⚠️ Error en gráfico</h3>"
                f"<p>Mostrando datos en tabla:</p>"
                f"</div>"
            )
            error_label.setTextFormat(Qt.RichText)
            layout.addWidget(error_label)
            
            table = self.create_students_backup_table()
            layout.addWidget(table)
        
        return group
    
    def create_financial_chart(self):
        """Crear gráfico de flujo financiero"""
        group = QGroupBox("📈 FLUJO FINANCIERO - ÚLTIMOS 6 MESES")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                border: 2px solid #ecf0f1;
                border-radius: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: white;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setContentsMargins(10, 25, 10, 15)
        
        try:
            # Obtener datos financieros
            datos_financieros = self.dashboard_data.get('datos_financieros', [])
            
            if not datos_financieros:
                no_data_label = QLabel(
                    "<div style='text-align: center; padding: 40px;'>"
                    "<h3 style='color: #95a5a6;'>📭 Sin datos financieros</h3>"
                    "<p>No hay registros de movimientos de caja.</p>"
                    "</div>"
                )
                no_data_label.setTextFormat(Qt.RichText)
                layout.addWidget(no_data_label)
                return group
            
            # Crear gráfico
            chart = QChart()
            chart.setTitle("Ingresos vs Gastos con Saldo Acumulado")
            chart.setAnimationOptions(QChart.SeriesAnimations)
            chart.setTheme(QChart.ChartThemeLight)
            
            # Crear series de barras
            series_ingresos = QBarSet("Ingresos")
            series_ingresos.setColor(QColor("#27ae60"))
            
            series_gastos = QBarSet("Gastos")
            series_gastos.setColor(QColor("#e74c3c"))
            
            # Crear serie de línea (saldo acumulado)
            series_saldo = QLineSeries()
            series_saldo.setName("Saldo Acumulado")
            series_saldo.setColor(QColor("#3498db"))
            series_saldo.setPen(QPen(QColor("#3498db"), 3))
            series_saldo.setPointsVisible(True)
            
            # Agregar datos
            meses_labels = []
            saldo_total = 0
            
            for i, mes_data in enumerate(datos_financieros):
                meses_labels.append(mes_data['mes'])
                series_ingresos.append(mes_data['ingresos'])
                series_gastos.append(mes_data['gastos'])
                
                saldo_total += (mes_data['ingresos'] - mes_data['gastos'])
                series_saldo.append(i, saldo_total)
            
            # Crear serie de barras agrupadas
            bar_series = QBarSeries()
            bar_series.append(series_ingresos)
            bar_series.append(series_gastos)
            bar_series.setLabelsVisible(True)
            bar_series.setLabelsFormat("@value Bs")
            bar_series.setLabelsPosition(QBarSeries.LabelsCenter)
            
            # Agregar series al gráfico
            chart.addSeries(bar_series)
            chart.addSeries(series_saldo)
            
            # Configurar ejes
            axis_x = QBarCategoryAxis()
            axis_x.append(meses_labels)
            axis_x.setTitleText("Meses")
            axis_x.setLabelsColor(QColor("#2c3e50"))
            chart.addAxis(axis_x, Qt.AlignBottom)
            
            axis_y_left = QValueAxis()
            axis_y_left.setTitleText("Monto (Bs)")
            axis_y_left.setLabelFormat("%d")
            axis_y_left.setLabelsColor(QColor("#2c3e50"))
            chart.addAxis(axis_y_left, Qt.AlignLeft)
            
            axis_y_right = QValueAxis()
            axis_y_right.setTitleText("Saldo Acumulado (Bs)")
            axis_y_right.setLabelFormat("%d")
            axis_y_right.setLabelsColor(QColor("#3498db"))
            chart.addAxis(axis_y_right, Qt.AlignRight)
            
            # Conectar series con ejes
            bar_series.attachAxis(axis_x)
            bar_series.attachAxis(axis_y_left)
            series_saldo.attachAxis(axis_x)
            series_saldo.attachAxis(axis_y_right)
            
            # Crear vista del gráfico
            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart_view.setMinimumHeight(300)
            chart_view.setMaximumHeight(400)
            
            layout.addWidget(chart_view)
            
            # Agregar estadísticas
            self.agregar_estadisticas_financieras(layout, datos_financieros)
            
        except Exception as e:
            print(f"⚠️  Error creando gráfico financiero: {e}")
            fallback_label = QLabel(
                "<div style='text-align: center; padding: 40px;'>"
                "<h3 style='color: #e74c3c;'>⚠️ Error en gráfico financiero</h3>"
                f"<p>{str(e)[:100]}...</p>"
                "</div>"
            )
            fallback_label.setTextFormat(Qt.RichText)
            layout.addWidget(fallback_label)
        
        return group
    
    # ============================================================================
    # MÉTODOS DE UI - SECCIONES ESPECÍFICAS
    # ============================================================================
    
    def create_recent_activity(self):
        """Crear tabla de actividad reciente"""
        group = QGroupBox("🔄 ACTIVIDAD RECIENTE DEL SISTEMA")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
                border: 2px solid #ecf0f1;
                border-radius: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                background-color: white;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setContentsMargins(15, 30, 15, 20)
        
        # Crear tabla
        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(4)
        self.activity_table.setHorizontalHeaderLabels([
            "Usuario", "Actividad", "Fecha/Hora", "Estado"
        ])
        
        # Configurar tabla
        self.activity_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.activity_table.verticalHeader().setVisible(False)
        self.activity_table.setAlternatingRowColors(True)
        self.activity_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.activity_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Estilo
        self.activity_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ecf0f1;
                border-radius: 8px;
                background-color: white;
                alternate-background-color: #f8f9fa;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 12px;
                font-weight: bold;
                border: none;
            }
        """)
        
        # Cargar datos
        self.load_activity_data()
        layout.addWidget(self.activity_table)
        
        # Botón para ver toda la actividad
        btn_container = QHBoxLayout()
        btn_container.addStretch()
        
        btn_view_all = QPushButton("📋 Ver toda la actividad")
        btn_view_all.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_view_all.clicked.connect(self.view_all_activity)
        btn_container.addWidget(btn_view_all)
        
        layout.addLayout(btn_container)
        
        return group
    
    def create_programs_summary(self):
        """Crear resumen ejecutivo de programas académicos"""
        group = QGroupBox("📊 RESUMEN DE PROGRAMAS ACADÉMICOS")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
                border: 2px solid #ecf0f1;
                border-radius: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                background-color: white;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setContentsMargins(15, 30, 15, 20)
        layout.setSpacing(15)
        
        # Obtener datos
        programas = self.dashboard_data.get('programas_en_progreso', [])
        
        if not programas:
            no_data_label = QLabel(
                "<div style='text-align: center; padding: 40px;'>"
                "<h3 style='color: #95a5a6;'>📭 Sin programas en gestión</h3>"
                "<p>No hay programas académicos activos en este momento.</p>"
                "</div>"
            )
            no_data_label.setTextFormat(Qt.RichText)
            layout.addWidget(no_data_label)
            return group
        
        # 1. ESTADÍSTICAS RÁPIDAS
        stats_frame = QFrame()
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(10)
        
        total_programas = len(programas)
        total_estudiantes = sum(p.get('estudiantes_matriculados', 0) for p in programas)
        iniciados = sum(1 for p in programas if p.get('estado') == 'INICIADO')
        planificados = sum(1 for p in programas if p.get('estado') == 'PLANIFICADO')
        ocupacion_promedio = self.dashboard_data.get('ocupacion_promedio', 0)
        
        stats_widgets = [
            self.create_mini_stat("📚 Total", str(total_programas), "#3498db"),
            self.create_mini_stat("👥 Estudiantes", str(total_estudiantes), "#27ae60"),
            self.create_mini_stat("🚀 En Curso", str(iniciados), "#f39c12"),
            self.create_mini_stat("📅 Planificados", str(planificados), "#9b59b6"),
            self.create_mini_stat("📊 Ocupación", f"{ocupacion_promedio}%", "#2c3e50")
        ]
        
        for widget in stats_widgets:
            stats_layout.addWidget(widget)
        
        stats_layout.addStretch()
        layout.addWidget(stats_frame)
        
        # 2. TABLA DE PROGRAMAS
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Código", "Nombre", "Estado", "Estudiantes", "Cupos", "Ocupación"
        ])
        
        table.setRowCount(min(8, len(programas)))
        
        for i, programa in enumerate(programas[:8]):
            # Código
            codigo_item = QTableWidgetItem(programa.get('codigo', 'N/A'))
            codigo_item.setTextAlignment(Qt.AlignCenter)
            
            # Nombre
            nombre = programa.get('nombre', '')
            if len(nombre) > 25:
                nombre = nombre[:22] + "..."
            nombre_item = QTableWidgetItem(nombre)
            
            # Estado
            estado_item = QTableWidgetItem(programa.get('estado_display', 'N/A'))
            estado_item.setTextAlignment(Qt.AlignCenter)
            if programa.get('estado') == 'INICIADO':
                estado_item.setForeground(QColor("#3498db"))
            else:
                estado_item.setForeground(QColor("#f39c12"))
            
            # Estudiantes
            estudiantes_item = QTableWidgetItem(str(programa.get('estudiantes_matriculados', 0)))
            estudiantes_item.setTextAlignment(Qt.AlignCenter)
            
            # Cupos
            cupos_text = f"{programa.get('cupos_ocupados', 0)}/{programa.get('cupos_totales', 0)}"
            cupos_item = QTableWidgetItem(cupos_text)
            cupos_item.setTextAlignment(Qt.AlignCenter)
            
            # Ocupación
            porcentaje = programa.get('porcentaje_ocupacion', 0)
            ocupacion_item = QTableWidgetItem(f"{porcentaje}%")
            ocupacion_item.setTextAlignment(Qt.AlignCenter)
            
            # Color según porcentaje
            if porcentaje >= 90:
                ocupacion_item.setForeground(QColor("#e74c3c"))
            elif porcentaje >= 70:
                ocupacion_item.setForeground(QColor("#f39c12"))
            else:
                ocupacion_item.setForeground(QColor("#27ae60"))
            
            table.setItem(i, 0, codigo_item)
            table.setItem(i, 1, nombre_item)
            table.setItem(i, 2, estado_item)
            table.setItem(i, 3, estudiantes_item)
            table.setItem(i, 4, cupos_item)
            table.setItem(i, 5, ocupacion_item)
        
        # Configurar tabla
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ecf0f1;
                border-radius: 8px;
                background-color: white;
                alternate-background-color: #f8f9fa;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)
        
        layout.addWidget(table)
        
        # 3. BOTÓN PARA VER TODOS LOS PROGRAMAS
        if len(programas) > 8:
            btn_frame = QFrame()
            btn_layout = QHBoxLayout(btn_frame)
            btn_layout.addStretch()
            
            btn_view_all = QPushButton(f"📋 Ver todos los programas ({len(programas)})")
            btn_view_all.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            btn_view_all.clicked.connect(self.view_all_programs)
            btn_layout.addWidget(btn_view_all)
            
            layout.addWidget(btn_frame)
        
        return group
    
    # ============================================================================
    # MÉTODOS AUXILIARES DE UI
    # ============================================================================
    
    def create_enhanced_legend(self, distribucion: Dict[str, int], colors: List[str]) -> QFrame:
        """Crear leyenda mejorada para el gráfico"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #f6f7f8;
                border: 1px solid #ecf0f1;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(8)
        
        # Título de leyenda
        title_label = QLabel("📊 Programas con estudiantes matriculados:")
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #2c3e50;
                font-size: 13px;
            }
        """)
        layout.addWidget(title_label)
        
        # Grid para los items
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(5)
        grid_layout.setContentsMargins(5, 5, 5, 5)
        
        total_estudiantes = sum(distribucion.values())
        programas = list(distribucion.items())
        
        # Dividir en 2 columnas si hay muchos programas
        col_count = 2 if len(programas) > 4 else 1
        
        for i, (programa, cantidad) in enumerate(programas):
            row = i // col_count
            col = i % col_count
            
            legend_item = self.create_legend_item(programa, cantidad, total_estudiantes, colors[i % len(colors)])
            grid_layout.addWidget(legend_item, row, col)
        
        layout.addWidget(grid_widget)
        
        # Resumen
        if total_estudiantes > 0:
            summary_label = QLabel(
                f"<div style='color: #2f8c8d; font-size: 12px; margin-top: 5px;'>"
                f"<strong>Total:</strong> {total_estudiantes} estudiantes en {len(programas)} programas • "
                f"<strong>Promedio:</strong> {total_estudiantes/len(programas):.1f} estudiantes/programa"
                f"</div>"
            )
            summary_label.setTextFormat(Qt.RichText)
            layout.addWidget(summary_label)
        
        return frame
    
    def create_legend_item(self, programa: str, cantidad: int, total: int, color: str) -> QFrame:
        """Crear item individual de leyenda"""
        widget = QFrame()
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 3, 5, 3)
        layout.setSpacing(8)
        
        # Círculo de color
        color_circle = QLabel()
        color_circle.setFixedSize(12, 12)
        color_circle.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                border-radius: 6px;
                border: 1px solid white;
            }}
        """)
        layout.addWidget(color_circle)
        
        # Información del programa
        porcentaje = (cantidad / total * 100) if total > 0 else 0
        
        info_label = QLabel(
            f"<div style='font-size: 11px; color: #2c3e50; min-width: 200px; max-width: 250px;'>"
            f"<strong>{programa}</strong><br>"
            f"<span style='color: #5498db;'>{cantidad} estudiantes</span> • "
            f"<span style='color: #7f8c8d;'>{porcentaje:.1f}%</span>"
            f"</div>"
        )
        info_label.setTextFormat(Qt.RichText)
        layout.addWidget(info_label)
        layout.addStretch()
        
        return widget
    
    def create_mini_stat(self, title: str, value: str, color: str):
        """Crear widget pequeño de estadística"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                border-left: 3px solid {color};
                padding: 10px;
                background-color: white;
                border-radius: 6px;
                min-width: 80px;
            }}
        """)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(4)
        
        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #7f8c8d;
            }
        """)
        layout.addWidget(title_label)
        
        # Valor
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {color};
            }}
        """)
        layout.addWidget(value_label)
        
        return widget
    
    def agregar_estadisticas_financieras(self, layout, datos_financieros):
        """Agregar estadísticas financieras debajo del gráfico"""
        try:
            if not datos_financieros:
                return
            
            # Calcular estadísticas
            total_ingresos = sum(mes['ingresos'] for mes in datos_financieros)
            total_gastos = sum(mes['gastos'] for mes in datos_financieros)
            saldo_final = datos_financieros[-1]['saldo_acumulado'] if datos_financieros else 0
            
            # Frame de estadísticas
            stats_frame = QFrame()
            stats_frame.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border: 1px solid #ecf0f1;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            
            stats_layout = QHBoxLayout(stats_frame)
            
            # Crear widgets de estadística
            stats_widgets = [
                self.crear_stat_financiera("💰 Ingresos Totales", f"Bs {total_ingresos:,.0f}", "#27ae60"),
                self.crear_stat_financiera("💸 Gastos Totales", f"Bs {total_gastos:,.0f}", "#e74c3c"),
                self.crear_stat_financiera("📊 Saldo Final", f"Bs {saldo_final:,.0f}", "#3498db"),
                self.crear_stat_financiera("📈 Rentabilidad", 
                                          f"{(total_ingresos-total_gastos)/total_ingresos*100:.1f}%" 
                                          if total_ingresos > 0 else "0%", 
                                          "#f39c12"),
            ]
            
            for widget in stats_widgets:
                stats_layout.addWidget(widget)
            
            stats_layout.addStretch()
            layout.addWidget(stats_frame)
            
        except Exception as e:
            print(f"⚠️  Error agregando estadísticas: {e}")
    
    def crear_stat_financiera(self, titulo, valor, color):
        """Crear widget de estadística financiera"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                border-left: 3px solid {color};
                padding: 10px;
                background-color: white;
                border-radius: 5px;
                margin-right: 10px;
            }}
        """)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)
        
        # Título
        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #7f8c8d;
                font-weight: bold;
            }
        """)
        layout.addWidget(titulo_label)
        
        # Valor
        valor_label = QLabel(valor)
        valor_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {color};
            }}
        """)
        layout.addWidget(valor_label)
        
        return widget
    
    def create_students_backup_table(self) -> QTableWidget:
        """Crear tabla de respaldo si falla el gráfico"""
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Programa", "Estudiantes", "Porcentaje"])
        
        distribucion = self.dashboard_data.get('estudiantes_por_programa', {})
        total = sum(distribucion.values())
        
        table.setRowCount(len(distribucion))
        
        for i, (programa, cantidad) in enumerate(distribucion.items()):
            porcentaje = (cantidad / total * 100) if total > 0 else 0
            
            table.setItem(i, 0, QTableWidgetItem(programa))
            table.setItem(i, 1, QTableWidgetItem(str(cantidad)))
            table.setItem(i, 2, QTableWidgetItem(f"{porcentaje:.1f}%"))
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ecf0f1;
                border-radius: 8px;
            }
        """)
        
        return table
    
    # ============================================================================
    # MÉTODOS DE EVENTOS E INTERACCIÓN
    # ============================================================================
    
    def on_program_slice_hovered(self, hovered: bool, slice_: QPieSlice, 
                                programa_nombre: str, cantidad: int, porcentaje: float):
        """Manejar hover en slice del gráfico"""
        if hovered:
            slice_.setExploded(True)
            slice_.setLabelVisible(True)
            
            tooltip_html = f"""
            <div style='
                background: white;
                border: 2px solid {slice_.color().name()};
                border-radius: 6px;
                padding: 12px;
                font-family: Arial;
                font-size: 12px;
                min-width: 200px;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            '>
                <div style='color: {slice_.color().name()}; font-weight: bold; margin-bottom: 5px;'>
                    📚 {programa_nombre}
                </div>
                <div><strong>{cantidad} estudiantes matriculados</strong></div>
                <div style='margin-top: 5px;'>
                    Representa el <span style='color: {slice_.color().name()}; font-weight: bold;'>{porcentaje:.1f}%</span> 
                    del total de estudiantes
                </div>
                <div style='margin-top: 8px; color: #7f8c8d; font-size: 11px;'>
                    Haz clic para ver detalles del programa
                </div>
            </div>
            """
            
            QToolTip.showText(QCursor.pos(), tooltip_html, msecShowTime=3000)
        else:
            slice_.setExploded(False)
    
    def on_program_slice_clicked(self, programa_nombre: str):
        """Manejar clic en slice del gráfico"""
        print(f"🎯 Clic en programa: {programa_nombre}")
        
        programas = self.dashboard_data.get('programas_en_progreso', [])
        programa_encontrado = None
        
        for programa in programas:
            if programa_nombre.startswith(programa.get('nombre', '')[:15]):
                programa_encontrado = programa
                break
            
        if programa_encontrado:
            info_text = f"""
            <div style='font-family: Arial; font-size: 12px;'>
                <h3 style='color: #2c3e50;'>{programa_encontrado.get('nombre', '')}</h3>
                <p><strong>Código:</strong> {programa_encontrado.get('codigo', '')}</p>
                <p><strong>Estado:</strong> {programa_encontrado.get('estado_display', '')}</p>
                <p><strong>Estudiantes matriculados:</strong> {programa_encontrado.get('estudiantes_matriculados', 0)}</p>
                <p><strong>Cupos:</strong> {programa_encontrado.get('cupos_ocupados', 0)}/{programa_encontrado.get('cupos_totales', 0)} 
                   ({programa_encontrado.get('porcentaje_ocupacion', 0)}%)</p>
                <p><strong>Tutor:</strong> {programa_encontrado.get('tutor_nombre', 'Sin asignar')}</p>
            </div>
            """
            
            QMessageBox.information(self, "📚 Detalles del Programa", info_text)
        else:
            QMessageBox.information(self, "Programa", f"Programa: {programa_nombre}")
    
    def show_programs_detail(self):
        """Mostrar detalle completo de programas"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
        
        dialog = QDialog(self)
        dialog.setWindowTitle("📊 Detalle de Programas y Estudiantes")
        dialog.resize(800, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Obtener datos
        distribucion = self.dashboard_data.get('estudiantes_por_programa', {})
        programas_detalle = self.dashboard_data.get('programas_en_progreso', [])
        
        # Crear tabla
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Programa", "Código", "Estudiantes", "Cupos Ocupados", "Cupos Totales", "Ocupación"
        ])
        
        table.setRowCount(len(distribucion))
        
        for i, (programa_nombre, estudiantes) in enumerate(distribucion.items()):
            # Buscar detalles adicionales
            programa_detalle = None
            for p in programas_detalle:
                if programa_nombre.startswith(p.get('nombre', '')[:15]):
                    programa_detalle = p
                    break
                
            # Programa (nombre completo)
            nombre_completo = programa_detalle.get('nombre', '') if programa_detalle else programa_nombre
            table.setItem(i, 0, QTableWidgetItem(nombre_completo))
            
            # Código
            codigo = programa_detalle.get('codigo', '') if programa_detalle else "N/A"
            table.setItem(i, 1, QTableWidgetItem(codigo))
            
            # Estudiantes
            estudiantes_item = QTableWidgetItem(str(estudiantes))
            estudiantes_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(i, 2, estudiantes_item)
            
            # Cupos ocupados
            if programa_detalle:
                cupos_ocupados = programa_detalle.get('cupos_ocupados', 0)
                cupos_item = QTableWidgetItem(str(cupos_ocupados))
            else:
                cupos_item = QTableWidgetItem(str(estudiantes))
            cupos_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(i, 3, cupos_item)
            
            # Cupos totales
            if programa_detalle:
                cupos_totales = programa_detalle.get('cupos_totales', 0)
                totales_item = QTableWidgetItem(str(cupos_totales))
            else:
                totales_item = QTableWidgetItem("N/A")
            totales_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(i, 4, totales_item)
            
            # Ocupación
            if programa_detalle:
                ocupacion = f"{programa_detalle.get('porcentaje_ocupacion', 0)}%"
                ocupacion_item = QTableWidgetItem(ocupacion)
                # Color según ocupación
                if programa_detalle.get('porcentaje_ocupacion', 0) >= 90:
                    ocupacion_item.setForeground(QColor("#e74c3c"))
                elif programa_detalle.get('porcentaje_ocupacion', 0) >= 70:
                    ocupacion_item.setForeground(QColor("#f39c12"))
                else:
                    ocupacion_item.setForeground(QColor("#27ae60"))
            else:
                ocupacion_item = QTableWidgetItem("N/A")
            ocupacion_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(i, 5, ocupacion_item)
        
        # Configurar tabla
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ecf0f1;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
            }
        """)
        
        layout.addWidget(table)
        dialog.exec()
    
    # ============================================================================
    # MÉTODOS DE ACTUALIZACIÓN
    # ============================================================================
    
    def update_time(self):
        """Actualizar la hora actual"""
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.time_label.setText(f"🕐 {current_time}")
    
    def update_display(self):
        """Actualizar la visualización con datos actuales"""
        print("🔄 Dashboard actualizado")
    
    def load_activity_data(self):
        """Cargar datos en la tabla de actividad"""
        if not hasattr(self, 'activity_table'):
            return
        
        # Datos de ejemplo (en producción, esto vendría del controlador)
        actividades = [
            ('María García', 'Nuevo estudiante registrado', 'Hace 2 horas', 'success'),
            ('Carlos Ruiz', 'Pago de matrícula realizado', 'Hace 4 horas', 'payment'),
            ('Ana López', 'Asignación de tutor completada', 'Ayer', 'assignment'),
            ('Pedro Martínez', 'Nuevo programa creado', 'Ayer', 'program'),
            ('Laura Torres', 'Certificado generado', 'Hace 3 días', 'certificate')
        ]
        
        self.activity_table.setRowCount(len(actividades))
        
        for i, (user, activity, time, status) in enumerate(actividades):
            # Usuario
            user_item = QTableWidgetItem(user)
            user_item.setTextAlignment(Qt.AlignCenter)
            
            # Actividad
            activity_item = QTableWidgetItem(activity)
            
            # Fecha/Hora
            time_item = QTableWidgetItem(time)
            time_item.setTextAlignment(Qt.AlignCenter)
            
            # Estado
            status_item = QTableWidgetItem()
            status_item.setTextAlignment(Qt.AlignCenter)
            
            # Configurar color según estado
            if status == 'success':
                status_item.setText("✅ Completado")
                status_item.setForeground(QColor("#27ae60"))
            elif status == 'payment':
                status_item.setText("💰 Pago")
                status_item.setForeground(QColor("#f39c12"))
            elif status == 'assignment':
                status_item.setText("👨‍🏫 Asignación")
                status_item.setForeground(QColor("#3498db"))
            elif status == 'program':
                status_item.setText("📚 Programa")
                status_item.setForeground(QColor("#9b59b6"))
            elif status == 'certificate':
                status_item.setText("📄 Certificado")
                status_item.setForeground(QColor("#2ecc71"))
            
            self.activity_table.setItem(i, 0, user_item)
            self.activity_table.setItem(i, 1, activity_item)
            self.activity_table.setItem(i, 2, time_item)
            self.activity_table.setItem(i, 3, status_item)
    
    def refresh_data(self):
        """Refrescar datos automáticamente"""
        print("🔄 Actualizando datos automáticamente...")
        self.load_data()
        
        # Mostrar notificación
        if self.parent():
            try:
                main_window = self.parent()
                while main_window and not hasattr(main_window, 'statusBar'):
                    main_window = main_window.parent()
                
                if main_window and hasattr(main_window, 'statusBar'):
                    main_window.statusBar().showMessage(
                        f"✅ Datos actualizados - {datetime.now().strftime('%H:%M:%S')}", 
                        3000
                    )
            except:
                pass
    
    def refresh_dashboard(self):
        """Refrescar dashboard manualmente"""
        print("🔃 Refrescando dashboard manualmente...")
        self.load_data()
        self.update_time()
        print("✅ Dashboard actualizado correctamente")
    
    def refresh_students_chart(self):
        """Actualizar gráfico de estudiantes"""
        print("🔄 Actualizando gráfico de estudiantes...")
        QMessageBox.information(self, "Actualizado", 
                              "Datos de estudiantes actualizados.\nRecarga la página para ver cambios.")
    
    # ============================================================================
    # MÉTODOS DE ACCIÓN
    # ============================================================================
    
    def view_all_activity(self):
        """Ver toda la actividad"""
        print("📋 Mostrando toda la actividad...")
        QMessageBox.information(self, "En desarrollo", "Vista completa de actividad en desarrollo")
    
    def view_all_programs(self):
        """Ver todos los programas"""
        programas = self.dashboard_data.get('programas_en_progreso', [])
        print(f"📋 Abriendo vista de todos los programas ({len(programas)} total)")
        QMessageBox.information(self, "En desarrollo", 
                              f"Vista completa de {len(programas)} programas en desarrollo")
    
    def export_report(self):
        """Exportar reporte del dashboard (placeholder)"""
        from PySide6.QtWidgets import QFileDialog
        from pathlib import Path
        
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Reporte del Dashboard",
            f"FormaGestPro_Reporte_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            "PDF Files (*.pdf);;Excel Files (*.xlsx);;All Files (*)"
        )
        
        if file_name:
            print(f"📄 Exportando reporte a: {file_name}")
            QMessageBox.information(self, "Exportación", 
                                  f"Reporte exportado: {Path(file_name).name}")
    
    def export_to_pdf(self):
        """Exportar el dashboard completo a PDF"""
        try:
            from datetime import datetime
            from PySide6.QtWidgets import QFileDialog, QMessageBox
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib.enums import TA_CENTER
            
            # 1. Obtener fecha actual
            fecha_actual = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            
            # 2. Diálogo para seleccionar ubicación
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Exportar Dashboard a PDF",
                f"FormaGestPro_Dashboard_{fecha_actual}.pdf",
                "Archivos PDF (*.pdf)"
            )
            
            if not file_path:
                return
            
            if not file_path.lower().endswith('.pdf'):
                file_path += '.pdf'
            
            # 3. Actualizar datos si es necesario
            if not hasattr(self, 'dashboard_data') or not self.dashboard_data:
                self.load_data()
            
            # 4. Crear documento PDF
            doc = SimpleDocTemplate(
                file_path,
                pagesize=A4,
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30
            )
            
            # 5. Contenido del PDF
            story = []
            styles = getSampleStyleSheet()
            
            # Título
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Title'],
                fontSize=18,
                spaceAfter=20,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#2c3e50')
            )
            
            title = Paragraph("FORMAGESTPRO - DASHBOARD DE GESTIÓN ACADÉMICA", title_style)
            story.append(title)
            
            # Fecha
            fecha_style = ParagraphStyle(
                'Fecha',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,
                textColor=colors.grey
            )
            fecha = Paragraph(f"Reporte generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", fecha_style)
            story.append(fecha)
            story.append(Spacer(1, 20))
            
            # SECCIÓN: MÉTRICAS PRINCIPALES
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=10,
                textColor=colors.HexColor('#3498db')
            )
            
            story.append(Paragraph("📊 MÉTRICAS PRINCIPALES", subtitle_style))
            
            # Datos de métricas
            metricas = [
                ["Estudiantes totales", str(self.dashboard_data.get('total_estudiantes', 0))],
                ["Programas activos", f"{self.dashboard_data.get('programas_activos', 0)}"],
                ["Docentes registrados", str(self.dashboard_data.get('total_docentes', 0))],
                ["Ingresos mensuales", f"Bs {self.dashboard_data.get('ingresos_mes_actual', 0):,.2f}"],
                ["Gastos mensuales", f"Bs {self.dashboard_data.get('gastos_mes_actual', 0):,.2f}"],
                ["Beneficio neto", f"Bs {self.dashboard_data.get('ingresos_mes_actual', 0) - self.dashboard_data.get('gastos_mes_actual', 0):,.2f}"]
            ]
            
            tabla_metricas = Table(metricas, colWidths=[3*inch, 2*inch])
            tabla_metricas.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                ('PADDING', (0, 0), (-1, -1), 8),
            ]))
            
            story.append(tabla_metricas)
            story.append(Spacer(1, 20))
            
            # SECCIÓN: DISTRIBUCIÓN DE ESTUDIANTES
            story.append(Paragraph("🎓 DISTRIBUCIÓN POR PROGRAMA", subtitle_style))
            
            distribucion = self.dashboard_data.get('estudiantes_por_programa', {})
            if distribucion:
                total = sum(distribucion.values())
                datos_dist = [["Programa", "Estudiantes", "Porcentaje"]]
                
                for programa, cantidad in distribucion.items():
                    porcentaje = (cantidad / total * 100) if total > 0 else 0
                    datos_dist.append([programa, str(cantidad), f"{porcentaje:.1f}%"])
                
                # Añadir total
                datos_dist.append(["TOTAL", str(total), "100.0%"])
                
                tabla_dist = Table(datos_dist, colWidths=[3.5*inch, 1.5*inch, 1*inch])
                tabla_dist.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#2c3e50')),
                    ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('FONTSIZE', (0, 1), (-1, -2), 10),
                    ('PADDING', (0, 0), (-1, -1), 6),
                ]))
                
                story.append(tabla_dist)
            else:
                story.append(Paragraph("No hay datos de distribución disponibles.", styles['Normal']))
            
            story.append(Spacer(1, 20))
            
            # SECCIÓN: PROGRAMAS EN PROGRESO
            story.append(Paragraph("📅 PROGRAMAS EN PROGRESO", subtitle_style))
            
            programas = self.dashboard_data.get('programas_en_progreso', [])
            if programas:
                datos_prog = [["Código", "Programa", "Estado", "Estudiantes"]]
                
                for programa in programas[:10]:
                    datos_prog.append([
                        programa.get('codigo', 'N/A'),
                        programa.get('nombre', '')[:40],
                        programa.get('estado_display', 'N/A'),
                        str(programa.get('estudiantes_matriculados', 0))
                    ])
                
                tabla_prog = Table(datos_prog, colWidths=[1.2*inch, 3*inch, 1.5*inch, 1*inch])
                tabla_prog.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('PADDING', (0, 0), (-1, -1), 5),
                ]))
                
                story.append(tabla_prog)
            else:
                story.append(Paragraph("No hay programas en progreso.", styles['Normal']))
            
            # PIE DE PÁGINA
            story.append(Spacer(1, 30))
            footer = Paragraph(
                "Sistema FormaGestPro - Reporte generado automáticamente",
                ParagraphStyle(
                    'Footer',
                    parent=styles['Normal'],
                    fontSize=8,
                    alignment=TA_CENTER,
                    textColor=colors.grey
                )
            )
            story.append(footer)
            
            # GENERAR PDF
            doc.build(story)
            
            # MOSTRAR ÉXITO
            QMessageBox.information(
                self,
                "✅ Exportación Exitosa",
                f"Dashboard exportado correctamente a:\n{file_path}",
                QMessageBox.Ok
            )
            
            print(f"✅ PDF exportado exitosamente: {file_path}")
            
        except Exception as e:
            print(f"❌ Error en export_to_pdf: {str(e)}")
            import traceback
            traceback.print_exc()
            
            QMessageBox.critical(
                self,
                "❌ Error",
                f"No se pudo generar el PDF:\n{str(e)}",
                QMessageBox.Ok
            )
    
    def get_logo_path(self):
        """Obtener ruta del logo para el PDF"""
        import os
        
        # Ruta del logo
        logo_paths = [
            "static/images/FORACON.png",
            "app/static/images/FORACON.png",
            "../static/images/FORACON.png",
            "FORACON.png"
        ]
        
        for path in logo_paths:
            if os.path.exists(path):
                print(f"✅ Logo encontrado en: {path}")
                return path
        
        print("⚠️ Logo no encontrado")
        return None


# ============================================================================
# PUNTO DE ENTRADA PARA PRUEBAS
# ============================================================================

if __name__ == "__main__":
    print("🧪 Ejecutando DashboardTab en modo prueba...")
    
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    dashboard = DashboardTab()
    dashboard.setWindowTitle("Dashboard - FormaGestPro v3.0")
    dashboard.resize(1400, 900)
    dashboard.show()
    
    print("✅ Dashboard iniciado en modo prueba")
    sys.exit(app.exec())