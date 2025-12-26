# app/views/windows/main_window_tabs.py
"""
Ventana principal optimizada del sistema FormaGestPro.
Versión 3.0 - Hereda de BaseView, sin menús superiores, centrada en pestañas.

ESTRUCTURA PRINCIPAL:
1. Ventana principal que hereda de BaseView (no QMainWindow)
2. Sistema de pestañas profesional con estilos centralizados
3. Gestión eficiente de recursos y carga bajo demanda
4. Interfaz limpia y moderna sin elementos redundantes
"""

import sys
import logging
from typing import Optional
from pathlib import Path

# PySide6 imports
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QLabel,
    QFrame,
    QPushButton,
    QStatusBar,
    QSizePolicy,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal, Slot, QTimer
from PySide6.QtGui import QIcon, QFont, QColor, QPalette

# Importar clase base
from app.views.base_view import BaseView

# Importar pestañas del sistema
try:
    from app.views.tabs.dashboard_tab import DashboardTab
    from app.views.tabs.estudiantes_tab import EstudiantesTab
    from app.views.tabs.docentes_tab import DocentesTab
    from app.views.tabs.programas_tab import ProgramasTab
    from app.views.tabs.financiero_tab import FinancieroTab
    from app.views.tabs.ayuda_tab import AyudaTab

    TABS_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Algunas pestañas no están disponibles: {e}")
    TABS_AVAILABLE = False
    # Definir placeholders para evitar errores
    DashboardTab = EstudiantesTab = DocentesTab = ProgramasTab = FinancieroTab = (
        AyudaTab
    ) = QWidget

logger = logging.getLogger(__name__)


class MainWindowTabs(BaseView):
    """
    Ventana principal optimizada del sistema FormaGestPro.

    Características principales:
    1. Hereda de BaseView para estilos y utilidades centralizadas
    2. Sin barra de menú ni barra de herramientas superiores
    3. Sistema de pestañas como navegación principal
    4. Carga de pestañas bajo demanda para mejor rendimiento
    5. Estilos consistentes usando la configuración de BaseView
    """

    # Señales específicas de la ventana principal
    tab_changed = Signal(int, str)  # Índice de pestaña, título de pestaña
    window_ready = Signal()
    refresh_all_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None, title: str = "FormaGestPro"):
        """
        Inicializa la ventana principal del sistema.

        Args:
            parent: Widget padre (opcional)
            title: Título de la ventana
        """
        super().__init__(parent, title)

        logger.info("🚀 Inicializando MainWindowTabs (versión BaseView)...")

        # Configuración específica de ventana principal
        self._window_initialized = False
        self._tabs_loaded = False

        # Diccionario para almacenar instancias de pestañas
        self.tab_instances = {}

        # Configurar ventana
        self._setup_window()

        # Configurar interfaz de usuario
        self._setup_ui()

        # Configurar conexiones
        self._setup_connections()

        # Cargar pestañas iniciales
        self._load_initial_tabs()

        self._window_initialized = True
        self.window_ready.emit()

        logger.info("✅ MainWindowTabs inicializada correctamente")

    # ============================================================================
    # MÉTODOS DE CONFIGURACIÓN
    # ============================================================================

    def _setup_window(self):
        """Configura las propiedades básicas de la ventana"""
        # Establecer título de ventana
        self.setWindowTitle(f"{self.view_title} - Sistema de Gestión Académica")

        # Establecer tamaño mínimo y preferido
        self.setMinimumSize(1200, 700)

        # Configurar política de tamaño
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def _setup_ui(self):
        """Configura toda la interfaz de usuario"""
        # Limpiar layout base heredado
        self._clear_layout(self.main_layout)

        # Ajustar márgenes para ventana principal
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Crear barra de título personalizada
        self._create_title_bar()

        # 2. Crear sistema de pestañas
        self._create_tab_system()

        # 3. Crear barra de estado
        self._create_status_bar()

    def _create_title_bar(self):
        """Crea una barra de título personalizada (opcional, sin menú)"""
        title_frame = QFrame()
        title_frame.setObjectName("TitleBar")
        title_frame.setMaximumHeight(60)
        title_frame.setMinimumHeight(50)

        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(
            self.SIZES["padding_large"],
            self.SIZES["padding_medium"],
            self.SIZES["padding_large"],
            self.SIZES["padding_medium"],
        )

        # Logo/Título de la aplicación
        app_title = QLabel(f"🏛️ {self.view_title}")
        app_title.setObjectName("AppTitle")

        # Configurar fuente del título usando BaseView
        font_family, font_size, font_weight = self.FONTS["title"]
        title_font = QFont(font_family, font_size + 4)  # Un poco más grande
        title_font.setWeight(font_weight)
        app_title.setFont(title_font)

        # Configurar color del título
        title_palette = app_title.palette()
        title_palette.setColor(
            app_title.foregroundRole(), QColor(self.COLORS["primary_dark"])
        )
        app_title.setPalette(title_palette)

        title_layout.addWidget(app_title)
        title_layout.addStretch()

        # Botones de control de ventana (minimizar, maximizar, cerrar)
        control_layout = QHBoxLayout()
        control_layout.setSpacing(self.SIZES["spacing_small"])

        # Botón de actualización global
        self.btn_refresh_all = QPushButton("🔄 Actualizar Todo")
        self.btn_refresh_all.setToolTip("Actualizar todas las pestañas")
        self.btn_refresh_all.setMinimumHeight(32)
        self.btn_refresh_all.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self.COLORS["info"]};
                color: {self.COLORS["white"]};
                border-radius: {self.SIZES["border_radius"]}px;
                padding: 6px 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {self.COLORS["secondary"]};
            }}
        """
        )
        control_layout.addWidget(self.btn_refresh_all)

        title_layout.addLayout(control_layout)

        # Añadir barra de título al layout principal
        self.main_layout.addWidget(title_frame)

        # Guardar referencia
        self.widgets["title_bar"] = title_frame
        self.widgets["btn_refresh_all"] = self.btn_refresh_all

    def _create_tab_system(self):
        """Crea el sistema de pestañas principal"""
        # Frame contenedor para las pestañas
        tab_frame = QFrame()
        tab_frame.setObjectName("TabFrame")

        tab_layout = QVBoxLayout(tab_frame)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)

        # Crear widget de pestañas
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("MainTabWidget")
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.setTabsClosable(False)  # No cerrables por el usuario

        # Configurar estilo de las pestañas usando BaseView
        self.tab_widget.setStyleSheet(
            f"""
            QTabWidget::pane {{
                border: 1px solid {self.COLORS["border"]};
                border-top: none;
                background-color: {self.COLORS["background"]};
            }}
            QTabBar::tab {{
                background-color: {self.COLORS["light"]};
                color: {self.COLORS["dark"]};
                padding: {self.SIZES["padding_medium"]}px {self.SIZES["padding_large"]}px;
                margin-right: {self.SIZES["padding_small"]}px;
                border: 1px solid {self.COLORS["border"]};
                border-bottom: none;
                border-top-left-radius: {self.SIZES["border_radius"]}px;
                border-top-right-radius: {self.SIZES["border_radius"]}px;
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                background-color: {self.COLORS["white"]};
                color: {self.COLORS["primary"]};
                border-bottom: 2px solid {self.COLORS["primary"]};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {self.COLORS["gray_light"]};
            }}
        """
        )

        tab_layout.addWidget(self.tab_widget)
        self.main_layout.addWidget(tab_frame, 1)  # Factor de stretch 1

        # Guardar referencia
        self.widgets["tab_frame"] = tab_frame
        self.widgets["tab_widget"] = self.tab_widget

    def _create_status_bar(self):
        """Crea una barra de estado simplificada"""
        status_frame = QFrame()
        status_frame.setObjectName("StatusBar")
        status_frame.setMaximumHeight(30)
        status_frame.setMinimumHeight(25)

        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(
            self.SIZES["padding_medium"],
            self.SIZES["padding_small"],
            self.SIZES["padding_medium"],
            self.SIZES["padding_small"],
        )

        # Estado del sistema
        self.lbl_system_status = QLabel("✅ Sistema listo")
        self.lbl_system_status.setFont(self._create_font("small"))
        status_layout.addWidget(self.lbl_system_status)

        status_layout.addStretch()

        # Información de pestaña actual
        self.lbl_tab_info = QLabel("")
        self.lbl_tab_info.setFont(self._create_font("small"))
        self.lbl_tab_info.setStyleSheet(f"color: {self.COLORS['gray']};")
        status_layout.addWidget(self.lbl_tab_info)

        self.main_layout.addWidget(status_frame)

        # Guardar referencias
        self.widgets["status_bar"] = status_frame
        self.widgets["lbl_system_status"] = self.lbl_system_status
        self.widgets["lbl_tab_info"] = self.lbl_tab_info

    def _setup_connections(self):
        """Configura todas las conexiones de señales y slots"""
        # Conectar cambio de pestaña
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        # Conectar botón de actualización
        self.btn_refresh_all.clicked.connect(self._refresh_all_tabs)

        # Conectar señal de cierre
        # (Si necesitas manejar cierre de ventana, puedes añadirlo aquí)

    # ============================================================================
    # MÉTODOS DE CARGA DE PESTAÑAS
    # ============================================================================

    def _load_initial_tabs(self):
        """Carga las pestañas iniciales del sistema"""
        if not TABS_AVAILABLE:
            self._show_error_tabs()
            return

        logger.info("📂 Cargando pestañas del sistema...")

        try:
            # Lista de pestañas a cargar (ícono, clase, título)
            tabs_to_load = [
                ("🏠", DashboardTab, "Dashboard"),
                ("👤", EstudiantesTab, "Estudiantes"),
                ("👨‍🏫", DocentesTab, "Docentes"),
                ("📚", ProgramasTab, "Programas"),
                ("💰", FinancieroTab, "Financiero"),
                ("⚙️", AyudaTab, "Configuración"),  # Renombrado de Ayuda a Configuración
            ]

            for icon, tab_class, title in tabs_to_load:
                self._add_tab(tab_class, f"{icon} {title}")

            self._tabs_loaded = True
            logger.info(f"✅ {len(tabs_to_load)} pestañas cargadas correctamente")

        except Exception as e:
            logger.error(f"❌ Error cargando pestañas: {e}")
            self._show_error_tabs()

    def _add_tab(self, tab_class, tab_title):
        """
        Añade una pestaña al sistema.

        Args:
            tab_class: Clase de la pestaña a instanciar
            tab_title: Título de la pestaña (con ícono)
        """
        try:
            # Crear instancia de la pestaña
            tab_instance = tab_class(parent=self)

            # Almacenar referencia
            tab_index = self.tab_widget.count()
            self.tab_instances[tab_index] = {
                "instance": tab_instance,
                "title": tab_title,
                "class": tab_class.__name__,
            }

            # Añadir al widget de pestañas
            self.tab_widget.addTab(tab_instance, tab_title)

            logger.debug(f"  ✅ Pestaña '{tab_title}' cargada correctamente")

        except Exception as e:
            logger.error(f"  ⚠️ Error cargando pestaña '{tab_title}': {e}")

            # Crear pestaña de fallback
            fallback_widget = self._create_fallback_tab(tab_title)
            tab_index = self.tab_widget.count()

            self.tab_instances[tab_index] = {
                "instance": fallback_widget,
                "title": tab_title,
                "class": "FallbackTab",
                "is_fallback": True,
            }

            self.tab_widget.addTab(fallback_widget, tab_title)

    def _create_fallback_tab(self, title):
        """
        Crea una pestaña de respaldo cuando falla la carga de una pestaña.

        Args:
            title: Título de la pestaña

        Returns:
            QWidget: Widget de pestaña de respaldo
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(self.SIZES["spacing_large"])
        layout.setContentsMargins(
            self.SIZES["padding_large"] * 2,
            self.SIZES["padding_large"] * 2,
            self.SIZES["padding_large"] * 2,
            self.SIZES["padding_large"] * 2,
        )

        # Ícono de error/advertencia
        icon_label = QLabel("⚠️")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 64px;
                color: {self.COLORS["warning"]};
            }}
        """
        )
        layout.addWidget(icon_label)

        # Título
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(self._create_font("title"))
        title_palette = title_label.palette()
        title_palette.setColor(
            title_label.foregroundRole(), QColor(self.COLORS["dark"])
        )
        title_label.setPalette(title_palette)
        layout.addWidget(title_label)

        # Mensaje
        message_label = QLabel(
            f"<div style='text-align: center;'>"
            f"<p style='color: {self.COLORS['gray']}; font-size: 14px;'>"
            f"El módulo <strong>{title}</strong> no está disponible temporalmente."
            f"</p>"
            f"<p style='color: {self.COLORS['gray_light']}; font-size: 12px; margin-top: 20px;'>"
            f"Esto puede deberse a:<br>"
            f"• Dependencias faltantes<br>"
            f"• Errores en la configuración<br>"
            f"• El módulo está en mantenimiento"
            f"</p>"
            f"</div>"
        )
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        layout.addStretch()

        return widget

    def _show_error_tabs(self):
        """Muestra un mensaje de error cuando no se pueden cargar las pestañas"""
        error_widget = QWidget()
        layout = QVBoxLayout(error_widget)
        layout.setSpacing(self.SIZES["spacing_large"])
        layout.setContentsMargins(50, 50, 50, 50)

        error_label = QLabel(
            f"<div style='text-align: center;'>"
            f"<h1 style='color: {self.COLORS['danger']};'>❌ Error de Carga</h1>"
            f"<p style='color: {self.COLORS['gray']};'>"
            f"No se pudieron cargar las pestañas del sistema.<br>"
            f"Por favor, verifica las dependencias y la configuración."
            f"</p>"
            f"</div>"
        )
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(error_label)

        self.tab_widget.addTab(error_widget, "⚠️ Error")

    # ============================================================================
    # MÉTODOS DE EVENTOS
    # ============================================================================

    @Slot(int)
    def _on_tab_changed(self, index):
        """
        Maneja el cambio de pestaña.

        Args:
            index: Índice de la nueva pestaña seleccionada
        """
        if index < 0 or index >= self.tab_widget.count():
            return

        # Obtener información de la pestaña
        tab_info = self.tab_instances.get(index, {})
        tab_title = tab_info.get("title", "Desconocido")

        # Actualizar barra de estado
        self.lbl_tab_info.setText(f"{tab_title}")

        # Emitir señal
        self.tab_changed.emit(index, tab_title)

        logger.debug(f"📌 Cambiado a pestaña: {tab_title} (índice: {index})")

    @Slot()
    def _refresh_all_tabs(self):
        """Actualiza todas las pestañas cargadas"""
        logger.info("🔄 Actualizando todas las pestañas...")

        self.lbl_system_status.setText("⏳ Actualizando...")

        try:
            # Actualizar cada pestaña
            for index, tab_info in self.tab_instances.items():
                tab_instance = tab_info.get("instance")

                # Si la pestaña tiene método refresh, llamarlo
                if hasattr(tab_instance, "refresh"):
                    try:
                        tab_instance.refresh()
                        logger.debug(f"  ✅ Pestaña {index} actualizada")
                    except Exception as e:
                        logger.warning(f"  ⚠️ Error actualizando pestaña {index}: {e}")

            self.lbl_system_status.setText("✅ Actualización completada")
            self.refresh_all_requested.emit()

            # Restaurar mensaje después de 3 segundos
            QTimer.singleShot(
                3000, lambda: self.lbl_system_status.setText("✅ Sistema listo")
            )

        except Exception as e:
            logger.error(f"❌ Error durante actualización: {e}")
            self.lbl_system_status.setText("❌ Error en actualización")

    # ============================================================================
    # MÉTODOS PÚBLICOS
    # ============================================================================

    def get_current_tab(self):
        """
        Obtiene la pestaña actualmente seleccionada.

        Returns:
            tuple: (índice, instancia, título) o (None, None, None) si no hay selección
        """
        current_index = self.tab_widget.currentIndex()

        if current_index < 0:
            return None, None, None

        tab_info = self.tab_instances.get(current_index, {})
        return current_index, tab_info.get("instance"), tab_info.get("title")

    def switch_to_tab(self, tab_index):
        """
        Cambia a una pestaña específica.

        Args:
            tab_index: Índice de la pestaña a la que cambiar

        Returns:
            bool: True si el cambio fue exitoso, False en caso contrario
        """
        if 0 <= tab_index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(tab_index)
            return True
        return False

    def switch_to_tab_by_name(self, tab_name):
        """
        Cambia a una pestaña por su nombre.

        Args:
            tab_name: Nombre de la pestaña (sin ícono)

        Returns:
            bool: True si el cambio fue exitoso, False en caso contrario
        """
        for index, tab_info in self.tab_instances.items():
            if tab_name.lower() in tab_info.get("title", "").lower():
                return self.switch_to_tab(index)
        return False

    def add_custom_tab(self, widget, title, icon="📋"):
        """
        Añade una pestaña personalizada al sistema.

        Args:
            widget: Widget a añadir como pestaña
            title: Título de la pestaña
            icon: Ícono de la pestaña (opcional)

        Returns:
            int: Índice de la nueva pestaña, o -1 en caso de error
        """
        try:
            full_title = f"{icon} {title}" if icon else title

            # Añadir pestaña
            tab_index = self.tab_widget.count()
            self.tab_widget.addTab(widget, full_title)

            # Almacenar información
            self.tab_instances[tab_index] = {
                "instance": widget,
                "title": full_title,
                "class": widget.__class__.__name__,
                "is_custom": True,
            }

            logger.info(f"📋 Pestaña personalizada '{title}' añadida")
            return tab_index

        except Exception as e:
            logger.error(f"❌ Error añadiendo pestaña personalizada: {e}")
            return -1

    # ============================================================================
    # MÉTODOS DE UTILIDAD (HEREDADOS/EXTENDIDOS)
    # ============================================================================

    def _create_font(self, font_type: str = "normal") -> QFont:
        """
        Crea una fuente QFont según la configuración de BaseView.

        Args:
            font_type: Tipo de fuente (title, subtitle, header, normal, small, monospace)

        Returns:
            QFont: Fuente configurada
        """
        if font_type not in self.FONTS:
            logger.warning(
                f"Tipo de fuente '{font_type}' no encontrado. Usando 'normal'."
            )
            font_type = "normal"

        try:
            font_family, font_size, font_weight = self.FONTS[font_type]
            font = QFont(font_family, font_size)
            font.setWeight(font_weight)
            return font
        except Exception as e:
            logger.error(f"Error creando fuente '{font_type}': {e}")
            return QFont()

    def _clear_layout(self, layout):
        """
        Limpia todos los widgets de un layout de manera segura.

        Args:
            layout: Layout a limpiar
        """
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
                item.layout().deleteLater()

    def show_message(
        self, title: str, message: str, message_type: str = "info"
    ) -> bool:
        """
        Muestra un mensaje al usuario usando los estilos de BaseView.

        Args:
            title: Título del mensaje
            message: Contenido del mensaje
            message_type: Tipo de mensaje (info, warning, error, question)

        Returns:
            bool: Resultado si es pregunta
        """
        try:
            # Mapeo de strings a QMessageBox.Icon
            icon_map = {
                "info": QMessageBox.Icon.Information,
                "information": QMessageBox.Icon.Information,
                "warning": QMessageBox.Icon.Warning,
                "error": QMessageBox.Icon.Critical,
                "critical": QMessageBox.Icon.Critical,
                "question": QMessageBox.Icon.Question,
            }

            # Normalizar el tipo de mensaje
            normalized_type = message_type.lower().strip()

            # Obtener el icono correspondiente
            if normalized_type in icon_map:
                icon = icon_map[normalized_type]
            else:
                logger.warning(
                    f"Tipo de mensaje '{message_type}' no reconocido. Usando 'info'."
                )
                icon = QMessageBox.Icon.Information

            # Llamar al método de la clase padre
            return super().show_message(title, message, icon)

        except Exception as e:
            logger.error(f"Error mostrando mensaje: {e}")
            # Implementación de respaldo local
            return self._show_message_backup(title, message, message_type)

    def _show_message_backup(
        self, title: str, message: str, message_type: str = "info"
    ) -> bool:
        """
        Implementación de respaldo para mostrar mensajes.

        Args:
            title: Título del mensaje
            message: Contenido del mensaje
            message_type: Tipo de mensaje

        Returns:
            bool: Resultado si es pregunta
        """
        try:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)

            # Configurar icono según tipo
            if message_type == "info":
                msg_box.setIcon(QMessageBox.Icon.Information)
            elif message_type == "warning":
                msg_box.setIcon(QMessageBox.Icon.Warning)
            elif message_type == "error":
                msg_box.setIcon(QMessageBox.Icon.Critical)
            elif message_type == "question":
                msg_box.setIcon(QMessageBox.Icon.Question)
                msg_box.setStandardButtons(
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                # Traducir botones al español
                msg_box.setButtonText(QMessageBox.StandardButton.Yes, "Sí")
                msg_box.setButtonText(QMessageBox.StandardButton.No, "No")
                return msg_box.exec() == QMessageBox.StandardButton.Yes
            else:
                msg_box.setIcon(QMessageBox.Icon.Information)

            # Para mensajes no de pregunta
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setButtonText(QMessageBox.StandardButton.Ok, "Aceptar")
            msg_box.exec()
            return True

        except Exception as e:
            logger.error(f"Error crítico en backup de show_message: {e}")
            # Último recurso: mostrar en consola
            print(f"[{title.upper()}] {message}")
            return False


# ============================================================================
# FUNCIÓN DE INICIALIZACIÓN
# ============================================================================


def create_main_window():
    """
    Función para crear y configurar la ventana principal.

    Returns:
        MainWindowTabs: Instancia configurada de la ventana principal
    """
    try:
        window = MainWindowTabs(title="FormaGestPro")

        # Centrar ventana en la pantalla
        screen_geometry = window.screen().availableGeometry()
        window_geometry = window.frameGeometry()

        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        window.move(window_geometry.topLeft())

        return window

    except Exception as e:
        logger.error(f"❌ Error crítico creando ventana principal: {e}")

        # Crear ventana de emergencia
        emergency_window = QWidget()
        emergency_window.setWindowTitle("FormaGestPro - Error")
        emergency_window.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout(emergency_window)
        error_label = QLabel(
            f"<h1 style='color: #e74c3c;'>❌ Error Crítico</h1>"
            f"<p>No se pudo crear la ventana principal:</p>"
            f"<pre>{str(e)}</pre>"
            f"<p>Por favor, contacte al administrador del sistema.</p>"
        )
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(error_label)

        return emergency_window


# ============================================================================
# PUNTO DE ENTRADA PARA PRUEBAS
# ============================================================================

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Crear aplicación
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Crear y mostrar ventana principal
    window = create_main_window()
    window.show()

    # Ejecutar aplicación
    sys.exit(app.exec())
