# app/views/windows/main_window_tabs.py
"""
app/views/windows/main_window_tabs.py
Ventana principal del sistema con sistema de pestañas
Versión 2.0 - Interfaz profesional
"""
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QMessageBox,
    QStatusBar, QToolBar, QMenuBar, QMenu, QGroupBox,
    QGridLayout, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon, QFont

from app.views.tabs.dashboard_tab import DashboardTab
from app.views.tabs.estudiantes_tab import EstudiantesTab
from app.views.tabs.docentes_tab import DocentesTab
from app.views.tabs.programas_tab import ProgramasTab
from app.views.tabs.financiero_tab import FinancieroTab
from app.views.tabs.ayuda_tab import AyudaTab

class MainWindowTabs(QMainWindow):
    """Ventana principal con sistema de pestañas profesionales"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        print("🔧 Inicializando MainWindowTabs...")
        
        self.setup_window()
        self.create_ui()
        self.setup_connections()
        self.setup_style()
        
        print("✅ MainWindowTabs inicializada correctamente")
    
    def setup_window(self):
        """Configurar propiedades de la ventana"""
        # Configuración básica
        self.setWindowTitle("FormaGestPro - Sistema de Gestión Académica")
        self.setGeometry(100, 100, 1400, 900)  # x, y, width, height
        self.setMinimumSize(1200, 700)
        
        # Establecer icono (si existe)
        # self.setWindowIcon(QIcon("resources/icons/app_icon.png"))
    
    def create_ui(self):
        """Crear todos los elementos de la interfaz"""
        # 1. Crear barra de menú
        self.create_menu_bar()
        
        # 2. Crear barra de herramientas
        self.create_toolbar()
        
        # 3. Crear widget central con pestañas
        self.create_central_widget()
        
        # 4. Crear barra de estado
        self.create_status_bar()
    
    def create_menu_bar(self):
        """Crear barra de menú"""
        menubar = self.menuBar()
        
        # Menú Archivo
        menu_archivo = menubar.addMenu("&Archivo")
        
        action_salir = QAction("&Salir", self)
        action_salir.setShortcut("Ctrl+Q")
        action_salir.triggered.connect(self.close)
        menu_archivo.addAction(action_salir)
        
        # Menú Gestión
        menu_gestion = menubar.addMenu("&Gestión")
        
        action_estudiantes = QAction("&Estudiantes", self)
        action_estudiantes.setShortcut("Ctrl+E")
        action_estudiantes.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        menu_gestion.addAction(action_estudiantes)
        
        action_docentes = QAction("&Docentes/Tutores", self)
        action_docentes.setShortcut("Ctrl+D")
        action_docentes.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        menu_gestion.addAction(action_docentes)
        
        action_programas = QAction("&Programas Académicos", self)
        action_programas.setShortcut("Ctrl+P")
        action_programas.triggered.connect(lambda: self.tab_widget.setCurrentIndex(3))
        menu_gestion.addAction(action_programas)
        
        action_financiero = QAction("&Financiero", self)
        action_financiero.setShortcut("Ctrl+F")
        action_financiero.triggered.connect(lambda: self.tab_widget.setCurrentIndex(4))
        menu_gestion.addAction(action_financiero)
        
        # Menú Ayuda
        menu_ayuda = menubar.addMenu("&Ayuda")
        
        action_acerca = QAction("&Acerca de...", self)
        action_acerca.triggered.connect(self.show_about)
        menu_ayuda.addAction(action_acerca)
        
        action_manual = QAction("&Manual de usuario", self)
        action_manual.triggered.connect(self.show_manual)
        menu_ayuda.addAction(action_manual)
    
    def create_toolbar(self):
        """Crear barra de herramientas"""
        toolbar = QToolBar("Barra de herramientas principal")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Botón Dashboard
        btn_dashboard = QAction("🏠 Dashboard", self)
        btn_dashboard.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        toolbar.addAction(btn_dashboard)
        
        toolbar.addSeparator()
        
        # Botón Estudiantes
        btn_estudiantes = QAction("👤 Estudiantes", self)
        btn_estudiantes.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        toolbar.addAction(btn_estudiantes)
        
        # Botón Docentes
        btn_docentes = QAction("👨‍🏫 Docentes", self)
        btn_docentes.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        toolbar.addAction(btn_docentes)
        
        # Botón Programas
        btn_programas = QAction("📚 Programas", self)
        btn_programas.triggered.connect(lambda: self.tab_widget.setCurrentIndex(3))
        toolbar.addAction(btn_programas)
        
        toolbar.addSeparator()
        
        # Botón Actualizar
        btn_actualizar = QAction("🔄 Actualizar", self)
        btn_actualizar.triggered.connect(self.update_status)
        toolbar.addAction(btn_actualizar)
    
    def create_central_widget(self):
        """Crear widget central con pestañas"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Crear widget de pestañas
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setMovable(True)
        
        # Crear pestañas
        self.create_tabs()
        
        layout.addWidget(self.tab_widget)
    
    def create_tabs(self):
        """Crear todas las pestañas del sistema"""
        # 1. Dashboard
        self.tab_dashboard = self.create_dashboard_tab()
        self.tab_widget.addTab(self.tab_dashboard, "🏠 Dashboard")
        
        # 2. Estudiantes
        self.tab_estudiantes = EstudiantesTab()
        self.tab_widget.addTab(self.tab_estudiantes, "👤 Estudiantes")
        
        # 3. Docentes
        try:
            from app.views.tabs.docentes_tab import DocentesTab
            self.tab_docentes = DocentesTab()
            self.tab_widget.addTab(self.tab_docentes, "👨‍🏫 Docentes/Tutores")
            print("✅ Pestaña de docentes cargada correctamente")
        except ImportError as e:
            print(f"⚠️  Error cargando docentes_tab: {e}")
            print("💡 Usando placeholder temporal")
            self.tab_docentes = self.create_module_tab(
                "👨‍🏫 Docentes/Tutores", 
                "#9b59b6", 
                "Gestión de docentes y tutores"
            )
        
        # 4. Programas
        self.tab_programas = self.create_module_tab(
            "📚 Programas Académicos", 
            "#2ecc71", 
            "Gestión de programas y cursos"
        )
        self.tab_widget.addTab(self.tab_programas, "📚 Programas")
        
        # 5. Financiero
        self.tab_financiero = self.create_module_tab(
            "💰 Gestión Financiera", 
            "#e74c3c", 
            "Control financiero y contable"
        )
        self.tab_widget.addTab(self.tab_financiero, "💰 Financiero")
        
        # 6. Ayuda
        self.tab_ayuda = self.create_help_tab()
        self.tab_widget.addTab(self.tab_ayuda, "🔧 Ayuda")
    
    def create_dashboard_tab(self):
        """Crear pestaña de Dashboard/Inicio"""
        from app.views.tabs.dashboard_tab import DashboardTab
        
        try:
            # Intentar cargar el dashboard real
            dashboard = DashboardTab()
            return dashboard
        except ImportError:
            print("⚠️  DashboardTab no disponible, usando placeholder")
            return self.create_module_tab("🏠 Dashboard", "#3498db", "Panel de control principal", True)
    
    def create_module_tab(self, title, color, description, show_stats=False):
        """Crear pestaña para un módulo"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Encabezado
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color}15;
                border-radius: 15px;
                padding: 20px;
            }}
        """)
        
        header_layout = QVBoxLayout(header_frame)
        
        # Título
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 32px;
                font-weight: bold;
                color: {color};
                padding: 10px;
            }}
        """)
        header_layout.addWidget(title_label)
        
        # Descripción
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #7f8c8d;
                padding: 5px;
            }
        """)
        header_layout.addWidget(desc_label)
        
        layout.addWidget(header_frame)
        
        if show_stats:
            # Estadísticas rápidas
            stats_frame = QFrame()
            stats_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 2px solid #ecf0f1;
                    border-radius: 10px;
                    padding: 20px;
                }
            """)
            
            stats_layout = QGridLayout(stats_frame)
            
            stats_data = [
                ("📊 Total Estudiantes", "24", "#3498db"),
                ("👨‍🏫 Docentes Activos", "8", "#9b59b6"),
                ("📚 Programas Activos", "6", "#2ecc71"),
                ("💰 Ingresos del Mes", "Bs. 15,240", "#e74c3c"),
            ]
            
            for i, (label_text, value_text, stat_color) in enumerate(stats_data):
                stat_widget = self.create_stat_widget(label_text, value_text, stat_color)
                stats_layout.addWidget(stat_widget, i // 2, i % 2)
            
            layout.addWidget(stats_frame)
        
        # Contenido principal
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #ecf0f1;
                border-radius: 10px;
                padding: 30px;
            }
        """)
        
        content_layout = QVBoxLayout(content_frame)
        
        # Mensaje de desarrollo
        dev_label = QLabel(
            f"<div style='text-align: center; padding: 40px;'>"
            f"<h2 style='color: #f39c12;'>🚧 Módulo en Desarrollo</h2>"
            f"<p style='color: #7f8c8d; font-size: 16px;'>"
            f"El módulo <strong>{title}</strong> se encuentra actualmente en desarrollo.<br>"
            f"Próximamente estará disponible con todas sus funcionalidades."
            f"</p>"
            f"<p style='color: #95a5a6; font-size: 14px; margin-top: 20px;'>"
            f"<strong>FormaGestPro v2.0</strong> - Sistema de Gestión Académica"
            f"</p>"
            f"</div>"
        )
        dev_label.setAlignment(Qt.AlignCenter)
        dev_label.setTextFormat(Qt.RichText)
        content_layout.addWidget(dev_label)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        btn_quick_access = QPushButton(f"🚀 Acceder a {title.split()[0]}")
        btn_quick_access.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                min-width: 200px;
            }}
            QPushButton:hover {{
                background-color: #2c3e50;
            }}
        """)
        btn_quick_access.clicked.connect(lambda: self.show_module_message(title))
        
        button_layout.addWidget(btn_quick_access)
        button_layout.addStretch()
        
        content_layout.addLayout(button_layout)
        layout.addWidget(content_frame)
        
        layout.addStretch()
        
        return widget
    
    def create_stat_widget(self, label, value, color):
        """Crear widget de estadística"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                border-left: 5px solid {color};
                background-color: white;
                padding: 15px;
                border-radius: 5px;
            }}
        """)
        
        layout = QVBoxLayout(widget)
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #7f8c8d;
            }
        """)
        layout.addWidget(label_widget)
        
        value_widget = QLabel(value)
        value_widget.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {color};
            }}
        """)
        layout.addWidget(value_widget)
        
        return widget
    
    def create_help_tab(self):
        """Crear pestaña de Ayuda"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Título
        title_label = QLabel("🔧 Ayuda y Soporte")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: #f39c12;
                padding: 20px;
            }
        """)
        layout.addWidget(title_label)
        
        # Contenedor de ayuda
        help_container = QFrame()
        help_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #fdf2e9;
                border-radius: 15px;
                padding: 30px;
            }
        """)
        
        help_layout = QVBoxLayout(help_container)
        
        # Secciones de ayuda
        help_sections = [
            ("📖 Manual de Usuario", 
             "Documentación completa del sistema con ejemplos y guías paso a paso."),
            ("🎥 Video Tutoriales", 
             "Videos instructivos para aprender a usar cada módulo del sistema."),
            ("❓ Preguntas Frecuentes", 
             "Respuestas a las dudas más comunes de los usuarios."),
            ("📞 Soporte Técnico", 
             "Contacto para asistencia técnica y resolución de problemas."),
            ("🔄 Actualizaciones", 
             "Información sobre las últimas actualizaciones y nuevas funcionalidades."),
        ]
        
        for section_title, section_desc in help_sections:
            section_widget = self.create_help_section(section_title, section_desc)
            help_layout.addWidget(section_widget)
        
        layout.addWidget(help_container)
        layout.addStretch()
        
        return widget
    
    def create_help_section(self, title, description):
        """Crear sección de ayuda"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border-radius: 10px;
                padding: 20px;
                margin: 10px 0;
            }
            QFrame:hover {
                background-color: #f0f0f0;
            }
        """)
        
        layout = QHBoxLayout(widget)
        
        # Contenido
        content_layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        content_layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                padding-top: 5px;
            }
        """)
        desc_label.setWordWrap(True)
        content_layout.addWidget(desc_label)
        
        layout.addLayout(content_layout)
        
        # Botón
        btn = QPushButton("➔")
        btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
                min-width: 30px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        btn.clicked.connect(lambda: self.show_help_message(title))
        
        layout.addWidget(btn)
        
        return widget
    
    def create_status_bar(self):
        """Crear barra de estado"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # Mensaje inicial
        status_bar.showMessage("✅ Sistema listo - Bienvenido a FormaGestPro", 5000)
        
        # Widgets adicionales en barra de estado
        status_bar.addPermanentWidget(QLabel("FormaGestPro v2.0"))
        status_bar.addPermanentWidget(QLabel(" | "))
        status_bar.addPermanentWidget(QLabel("© Formación Continua Consultora"))
    
    def setup_connections(self):
        """Configurar conexiones de señales"""
        # Conectar cambio de pestaña
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
    
    def setup_style(self):
        """Configurar estilos de la aplicación"""
        # Estilo para las pestañas
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #ddd;
                background-color: white;
                border-radius: 10px;
                margin-top: 5px;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                padding: 12px 25px;
                margin-right: 3px;
                border: 1px solid #ddd;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                color: #2c3e50;
                font-size: 13px;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
                border-color: #2980b9;
            }
            QTabBar::tab:hover:!selected {
                background-color: #ecf0f1;
            }
            QTabBar::tab:first {
                margin-left: 5px;
            }
        """)
        
        # Estilo general
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f7fa;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QLabel {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
    
    def on_tab_changed(self, index):
        """Manejar cambio de pestaña"""
        tab_names = ["Dashboard", "Estudiantes", "Docentes", "Programas", "Financiero", "Ayuda"]
        if 0 <= index < len(tab_names):
            self.statusBar().showMessage(f"📁 Módulo activo: {tab_names[index]}", 3000)
    
    def show_module_message(self, module_name):
        """Mostrar mensaje informativo del módulo"""
        QMessageBox.information(
            self,
            f"Acceso a {module_name}",
            f"<h3>Módulo: {module_name}</h3>"
            f"<p>Esta funcionalidad está actualmente en desarrollo.</p>"
            f"<p>Estará disponible en la próxima actualización del sistema FormaGestPro.</p>"
            f"<hr>"
            f"<p><small><i>Formación Continua Consultora</i></small></p>",
            QMessageBox.StandardButton.Ok
        )
    
    def show_help_message(self, help_topic):
        """Mostrar mensaje de ayuda"""
        QMessageBox.information(
            self,
            f"Ayuda: {help_topic}",
            f"<h3>{help_topic}</h3>"
            f"<p>Esta sección de ayuda está en desarrollo.</p>"
            f"<p>Próximamente estará disponible con información completa.</p>",
            QMessageBox.StandardButton.Ok
        )
    
    def show_about(self):
        """Mostrar información acerca del sistema"""
        QMessageBox.about(
            self,
            "Acerca de FormaGestPro",
            """<h2>FormaGestPro</h2>
            <h3>Sistema de Gestión Académica</h3>
            
            <p><b>Versión:</b> 2.0 (Interfaz con Pestañas)</p>
            <p><b>Desarrollado por:</b> Equipo de Desarrollo</p>
            <p><b>© 2024 Formación Continua Consultora</b></p>
            
            <hr>
            
            <h4>Características principales:</h4>
            <ul>
                <li>👤 Gestión integral de estudiantes</li>
                <li>👨‍🏫 Administración de docentes/tutores</li>
                <li>📚 Control de programas académicos</li>
                <li>💰 Sistema financiero y contable</li>
                <li>📊 Reportes y estadísticas</li>
                <li>🔧 Interfaz moderna e intuitiva</li>
            </ul>
            
            <p><i>Software desarrollado con PySide6 y Python</i></p>
            """
        )
    
    def show_manual(self):
        """Mostrar manual del usuario"""
        QMessageBox.information(
            self,
            "Manual de Usuario",
            "<h3>Manual de Usuario FormaGestPro</h3>"
            "<p>El manual completo está en desarrollo.</p>"
            "<p>Para asistencia inmediata:</p>"
            "<ul>"
            "<li>Use los menús y pestañas para navegar</li>"
            "<li>Cada módulo tiene instrucciones específicas</li>"
            "<li>Contacte al administrador del sistema</li>"
            "</ul>",
            QMessageBox.StandardButton.Ok
        )
    
    def update_status(self):
        """Actualizar estado del sistema"""
        self.statusBar().showMessage("🔄 Sistema actualizado - " + 
                                   "Todos los módulos están operativos", 3000)
    
    def closeEvent(self, event):
        """Manejar el cierre de la aplicación"""
        reply = QMessageBox.question(
            self,
            "Confirmar salida",
            "¿Está seguro de que desea salir del sistema FormaGestPro?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            print("👋 FormaGestPro cerrado correctamente")
            event.accept()
        else:
            event.ignore()

# Punto de entrada para pruebas directas
if __name__ == "__main__":
    print("🧪 Ejecutando MainWindowTabs en modo prueba...")
    
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindowTabs()
    window.show()
    
    print("✅ Prueba iniciada - Ventana mostrada")
    sys.exit(app.exec())