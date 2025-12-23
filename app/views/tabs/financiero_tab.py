# app/views/tabs/financiero_tab.py
"""
Pestaña de Gestión Financiera - Versión completa con paginación
"""

import logging
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QLineEdit, QLabel,
    QComboBox, QFormLayout, QGroupBox, QGridLayout, QFrame, QMenu,
    QDateEdit, QDoubleSpinBox, QSpinBox, QDialog, QTextEdit
)
from PySide6.QtCore import Qt, Signal, Slot, QDate
from PySide6.QtGui import QIcon, QFont, QColor, QAction

from app.models.pago_model import PagoModel
from app.models.cuota_model import CuotaModel
from app.models.estudiante_model import EstudianteModel
from app.models.programa_academico_model import ProgramaAcademicoModel

logger = logging.getLogger(__name__)

class FinancieroTab(QWidget):
    """Pestaña para gestión financiera con paginación"""
    
    # Señales para comunicación con MainWindow
    pago_seleccionado = Signal(dict)
    necesita_actualizar = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.pagos_data = []
        self.pagos_paginados = []
        self.pagos_filtrados_actuales = []
        self.current_filter = 'todos'
        self.current_page = 1
        self.records_per_page = 10  # Mostrar 10 registros por página
        self.total_pages = 1
        
        self.setup_ui()
        self.setup_connections()
        self.cargar_pagos()
    
    def setup_ui(self):
        """Configurar la interfaz de usuario de la pestaña"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # ============ ENCABEZADO ============
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 15px;
            }
        """)

        header_layout = QHBoxLayout(header_frame)

        # Título
        title_label = QLabel("💰 Gestión Financiera")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Botón Nuevo Pago
        self.btn_nuevo_pago = QPushButton("💳 Nuevo Pago")
        self.btn_nuevo_pago.setFixedHeight(40)
        self.btn_nuevo_pago.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.btn_nuevo_pago.setToolTip("Registrar un nuevo pago")
        header_layout.addWidget(self.btn_nuevo_pago)

        layout.addWidget(header_frame)

        # ============ FILTROS ============
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                color: black;
            }
        """)

        filter_layout = QHBoxLayout(filter_frame)

        # Etiqueta de filtro
        filter_label = QLabel("Filtrar por estado:")
        filter_label.setStyleSheet("font-weight: bold; color: #495057;")
        filter_layout.addWidget(filter_label)

        # Combo box para filtro
        self.combo_filtro = QComboBox()
        self.combo_filtro.addItems(['Todos', 'Pendientes', 'Completados', 'Atrasados', 'Cancelados'])
        self.combo_filtro.setFixedHeight(36)
        self.combo_filtro.setFixedWidth(150)
        self.combo_filtro.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
            }
            QComboBox:focus {
                border: 2px solid #27ae60;
            }
        """)
        filter_layout.addWidget(self.combo_filtro)

        # Filtro por fecha
        date_label = QLabel("Fecha:")
        date_label.setStyleSheet("font-weight: bold; color: #495057; margin-left: 20px;")
        filter_layout.addWidget(date_label)

        self.date_desde = QDateEdit()
        self.date_desde.setDate(QDate.currentDate().addMonths(-1))
        self.date_desde.setCalendarPopup(True)
        self.date_desde.setFixedHeight(36)
        self.date_desde.setFixedWidth(120)
        self.date_desde.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        filter_layout.addWidget(self.date_desde)

        sep_label = QLabel("a")
        sep_label.setStyleSheet("margin: 0 5px;")
        filter_layout.addWidget(sep_label)

        self.date_hasta = QDateEdit()
        self.date_hasta.setDate(QDate.currentDate())
        self.date_hasta.setCalendarPopup(True)
        self.date_hasta.setFixedHeight(36)
        self.date_hasta.setFixedWidth(120)
        self.date_hasta.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        filter_layout.addWidget(self.date_hasta)

        # Buscador
        search_label = QLabel("Buscar:")
        search_label.setStyleSheet("font-weight: bold; color: #495057; margin-left: 20px;")
        filter_layout.addWidget(search_label)

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Estudiante, código o concepto...")
        self.txt_buscar.setFixedHeight(36)
        self.txt_buscar.setMinimumWidth(200)
        self.txt_buscar.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #27ae60;
            }
        """)
        filter_layout.addWidget(self.txt_buscar)

        # Botón Buscar
        self.btn_buscar = QPushButton("🔍 Buscar")
        self.btn_buscar.setFixedHeight(36)
        self.btn_buscar.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
        """)
        filter_layout.addWidget(self.btn_buscar)

        # Botón Limpiar
        self.btn_limpiar = QPushButton("🗑️ Limpiar")
        self.btn_limpiar.setFixedHeight(36)
        self.btn_limpiar.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #616a6b;
            }
        """)
        filter_layout.addWidget(self.btn_limpiar)

        filter_layout.addStretch()
        layout.addWidget(filter_frame)

        # ============ TABLA DE PAGOS ============
        self.tabla_pagos = QTableWidget()
        self.tabla_pagos.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                gridline-color: #dee2e6;
                color: black;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #dee2e6;
            }
            QTableWidget::item:selected {
                background-color: #27ae60;
                color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
        """)

        self.tabla_pagos.setAlternatingRowColors(True)
        self.tabla_pagos.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_pagos.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla_pagos.verticalHeader().setVisible(False)
        self.tabla_pagos.verticalHeader().setDefaultSectionSize(40)

        layout.addWidget(self.tabla_pagos, 1)

        # ============ CONTROLES DE PAGINACIÓN ============
        pagination_frame = QFrame()
        pagination_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)

        pagination_layout = QHBoxLayout(pagination_frame)
        pagination_layout.setContentsMargins(20, 5, 20, 5)

        # Botón Primera Página
        self.btn_primera = QPushButton("⏮️ Primera")
        self.btn_primera.setFixedHeight(35)
        self.btn_primera.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #727b84;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        pagination_layout.addWidget(self.btn_primera)

        # Botón Anterior
        self.btn_anterior = QPushButton("◀️ Anterior")
        self.btn_anterior.setFixedHeight(35)
        self.btn_anterior.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        pagination_layout.addWidget(self.btn_anterior)

        # Información de página
        pagination_layout.addStretch()

        self.lbl_info_pagina = QLabel("Página 1 de 1")
        self.lbl_info_pagina.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #2c3e50;
                font-size: 13px;
            }
        """)
        pagination_layout.addWidget(self.lbl_info_pagina)

        # Contador de registros
        self.lbl_contador = QLabel("Mostrando 0 de 0 registros")
        self.lbl_contador.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 12px;
                font-style: italic;
            }
        """)
        pagination_layout.addWidget(self.lbl_contador)

        pagination_layout.addStretch()

        # Botón Siguiente
        self.btn_siguiente = QPushButton("Siguiente ▶️")
        self.btn_siguiente.setFixedHeight(35)
        self.btn_siguiente.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        pagination_layout.addWidget(self.btn_siguiente)

        # Botón Última Página
        self.btn_ultima = QPushButton("Última ⏭️")
        self.btn_ultima.setFixedHeight(35)
        self.btn_ultima.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #727b84;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        pagination_layout.addWidget(self.btn_ultima)

        layout.addWidget(pagination_frame)

        # ============ ESTADO ============
        self.lbl_estado = QLabel("Cargando pagos...")
        self.lbl_estado.setStyleSheet("color: #7f8c8d; font-style: italic;")
        self.lbl_estado.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_estado)
    
    def create_summary_widget(self, title, value, color):
        """Crear widget de resumen financiero"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                border-left: 4px solid {color};
                background-color: white;
                padding: 15px;
                border-radius: 6px;
            }}
        """)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #7f8c8d;
                font-weight: bold;
            }
        """)
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 22px;
                font-weight: bold;
                color: {color};
            }}
        """)
        layout.addWidget(value_label)
        
        return widget
    
    def setup_connections(self):
        """Conectar señales y slots"""
        # Botones
        self.btn_nuevo_pago.clicked.connect(self.agregar_nuevo_pago)
        #self.btn_reporte.clicked.connect(self.generar_reporte)
        self.btn_buscar.clicked.connect(self.buscar_pagos)
        self.btn_limpiar.clicked.connect(self.limpiar_busqueda)
        
        # Filtros
        self.combo_filtro.currentTextChanged.connect(
            lambda: self.filtrar_pagos(desde_paginacion=False)
        )
        self.date_desde.dateChanged.connect(
            lambda: self.filtrar_pagos(desde_paginacion=False)
        )
        self.date_hasta.dateChanged.connect(
            lambda: self.filtrar_pagos(desde_paginacion=False)
        )
        self.txt_buscar.returnPressed.connect(self.buscar_pagos)
        
        # Paginación
        self.btn_primera.clicked.connect(lambda: self.cambiar_pagina(1))
        self.btn_anterior.clicked.connect(lambda: self.cambiar_pagina(self.current_page - 1))
        self.btn_siguiente.clicked.connect(lambda: self.cambiar_pagina(self.current_page + 1))
        self.btn_ultima.clicked.connect(lambda: self.cambiar_pagina(self.total_pages))
    
    def cargar_pagos(self, filtro='todos'):
        """Cargar pagos desde la base de datos"""
        try:
            self.lbl_estado.setText("Cargando pagos...")
            
            # Obtener todos los pagos
            self.pagos_data = PagoModel.get_all()
            
            # Resetear paginación
            self.current_page = 1
            
            # Aplicar filtro inicial
            self.current_filter = filtro
            self.filtrar_pagos(desde_paginacion=False)
            
            # Actualizar resumen
            self.actualizar_resumen()
            
            if self.pagos_data:
                self.lbl_estado.setText(f"✅ {len(self.pagos_data)} pagos cargados")
            else:
                self.lbl_estado.setText("📭 No hay pagos registrados")
                
        except Exception as e:
            logger.error(f"Error al cargar pagos: {e}")
            self.lbl_estado.setText("❌ Error al cargar pagos")
            QMessageBox.critical(self, "Error", f"Error al cargar pagos: {str(e)}")
    
    def actualizar_resumen(self):
        """Actualizar el resumen financiero"""
        
    
    def filtrar_pagos(self, desde_paginacion=False):
        """Filtrar pagos según los criterios seleccionados y aplicar paginación"""
        try:
            # Obtener valores actuales
            filtro_texto = self.combo_filtro.currentText().lower()
            texto_busqueda = self.txt_buscar.text().strip().lower()
            fecha_desde = self.date_desde.date()
            fecha_hasta = self.date_hasta.date()
            
            # Filtrar pagos
            pagos_filtrados = []
            for pago in self.pagos_data:
                # Filtrar por estado
                estado = getattr(pago, 'estado', '').lower()
                if filtro_texto == 'pendientes' and estado != 'pendiente':
                    continue
                elif filtro_texto == 'completados' and estado != 'completado':
                    continue
                elif filtro_texto == 'atrasados' and estado != 'atrasado':
                    continue
                elif filtro_texto == 'cancelados' and estado != 'cancelado':
                    continue
                
                # Filtrar por fecha
                fecha_pago = getattr(pago, 'fecha_pago', None)
                if fecha_pago:
                    fecha_pago_date = QDate.fromString(fecha_pago, "yyyy-MM-dd")
                    if fecha_pago_date < fecha_desde or fecha_pago_date > fecha_hasta:
                        continue
                
                # Filtrar por búsqueda si hay texto
                if texto_busqueda:
                    campos = [
                        str(getattr(pago, 'codigo_pago', '') or ''),
                        str(getattr(pago, 'concepto', '') or ''),
                        str(getattr(pago, 'estudiante_nombre', '') or ''),
                        str(getattr(pago, 'programa_nombre', '') or '')
                    ]
                    
                    if not any(texto_busqueda in campo.lower() for campo in campos):
                        continue
                
                pagos_filtrados.append(pago)
            
            # Actualizar la lista filtrada
            self.pagos_filtrados_actuales = pagos_filtrados
            
            # Resetear a página 1 solo si no viene desde paginación
            if not desde_paginacion:
                self.current_page = 1
            
            # Actualizar la paginación
            self.actualizar_paginacion()
            
        except Exception as e:
            logger.error(f"Error al filtrar pagos: {e}")
            import traceback
            traceback.print_exc()
    
    def buscar_pagos(self):
        """Buscar pagos según el texto ingresado"""
        self.current_page = 1
        self.filtrar_pagos(desde_paginacion=False)
    
    def limpiar_busqueda(self):
        """Limpiar todos los filtros y mostrar todos"""
        self.txt_buscar.clear()
        self.combo_filtro.setCurrentIndex(0)
        self.date_desde.setDate(QDate.currentDate().addMonths(-1))
        self.date_hasta.setDate(QDate.currentDate())
        self.current_page = 1
        self.filtrar_pagos(desde_paginacion=False)
    
    def mostrar_pagos_en_tabla(self, pagos):
        """Mostrar pagos en la tabla"""
        try:
            self.tabla_pagos.clear()
            
            # Configurar columnas
            columnas = [
                "ID", "Código", "Fecha", "Estudiante", "Concepto", 
                "Monto", "Método", "Estado", "Acciones"
            ]
            
            self.tabla_pagos.setColumnCount(len(columnas))
            self.tabla_pagos.setHorizontalHeaderLabels(columnas)
            self.tabla_pagos.setRowCount(len(pagos))
            
            # Llenar datos
            for fila, pago in enumerate(pagos):
                # Configurar altura de fila uniforme
                self.tabla_pagos.setRowHeight(fila, 40)
                
                # ID
                item_id = QTableWidgetItem(str(pago.id))
                item_id.setTextAlignment(Qt.AlignCenter)
                self.tabla_pagos.setItem(fila, 0, item_id)
                
                # Código
                codigo = getattr(pago, 'codigo_pago', '') or getattr(pago, 'codigo', '') or ''
                item_codigo = QTableWidgetItem(codigo)
                item_codigo.setTextAlignment(Qt.AlignCenter)
                self.tabla_pagos.setItem(fila, 1, item_codigo)
                
                # Fecha
                fecha = getattr(pago, 'fecha_pago', '') or getattr(pago, 'fecha', '') or ''
                item_fecha = QTableWidgetItem(fecha)
                self.tabla_pagos.setItem(fila, 2, item_fecha)
                
                # Estudiante
                estudiante = getattr(pago, 'estudiante_nombre', '') or 'Estudiante'
                item_estudiante = QTableWidgetItem(estudiante)
                self.tabla_pagos.setItem(fila, 3, item_estudiante)
                
                # Concepto
                concepto = getattr(pago, 'concepto', '') or ''
                item_concepto = QTableWidgetItem(concepto)
                self.tabla_pagos.setItem(fila, 4, item_concepto)
                
                # Monto
                monto = float(getattr(pago, 'monto', 0) or 0)
                item_monto = QTableWidgetItem(f"Bs. {monto:.2f}")
                item_monto.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tabla_pagos.setItem(fila, 5, item_monto)
                
                # Método de pago
                metodo = getattr(pago, 'metodo_pago', '') or getattr(pago, 'metodo', '') or ''
                item_metodo = QTableWidgetItem(metodo.capitalize())
                self.tabla_pagos.setItem(fila, 6, item_metodo)
                
                # Estado
                estado = getattr(pago, 'estado', '') or ''
                if not estado:
                    estado = "Pendiente" if getattr(pago, 'pendiente', 1) == 1 else "Completado"
                
                item_estado = QTableWidgetItem(estado.capitalize())
                item_estado.setTextAlignment(Qt.AlignCenter)
                
                # Color según estado
                estado_lower = estado.lower()
                if estado_lower == 'completado' or estado_lower == 'pagado':
                    item_estado.setForeground(Qt.darkGreen)
                elif estado_lower == 'pendiente':
                    item_estado.setForeground(QColor("#f39c12"))  # Naranja
                elif estado_lower == 'atrasado':
                    item_estado.setForeground(Qt.darkRed)
                elif estado_lower == 'cancelado':
                    item_estado.setForeground(Qt.darkGray)
                else:
                    item_estado.setForeground(Qt.black)
                    
                self.tabla_pagos.setItem(fila, 7, item_estado)
                
                # Acciones (botones)
                widget_acciones = self.crear_widget_acciones(pago)
                self.tabla_pagos.setCellWidget(fila, 8, widget_acciones)
            
            # Ajustar columnas
            self.tabla_pagos.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # Estudiante
            self.tabla_pagos.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)  # Concepto
            
            # Columnas fijas
            self.tabla_pagos.setColumnWidth(0, 50)   # ID
            self.tabla_pagos.setColumnWidth(1, 100)  # Código
            self.tabla_pagos.setColumnWidth(2, 100)  # Fecha
            self.tabla_pagos.setColumnWidth(5, 100)  # Monto
            self.tabla_pagos.setColumnWidth(6, 100)  # Método
            self.tabla_pagos.setColumnWidth(7, 100)  # Estado
            
            # Acciones: 5 botones de 40px + 5 espacios de 3px = ~215px
            self.tabla_pagos.setColumnWidth(8, 215)  # Acciones
            
        except Exception as e:
            logger.error(f"Error al mostrar pagos en tabla: {e}")
            self.lbl_estado.setText("❌ Error al mostrar pagos")
    
    def crear_widget_acciones(self, pago):
        """Crear widget con botones de acciones"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        # Botón 1: Ver Detalles
        btn_detalles = QPushButton("👁️")
        btn_detalles.setToolTip("Ver detalles del pago")
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
        btn_detalles.clicked.connect(lambda: self.ver_detalles_pago(pago))

        # Botón 2: Editar
        btn_editar = QPushButton("✏️")
        btn_editar.setToolTip("Editar pago")
        btn_editar.setFixedSize(40, 28)
        btn_editar.setStyleSheet("""
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
        btn_editar.clicked.connect(lambda: self.editar_pago(pago))

        # Botón 3: Marcar como Pagado
        estado = getattr(pago, 'estado', '').lower()
        if estado == 'pendiente' or estado == 'atrasado':
            btn_pagar = QPushButton("💰")
            btn_pagar.setToolTip("Marcar como pagado")
            btn_pagar.setFixedSize(40, 28)
            btn_pagar.setStyleSheet("""
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
            btn_pagar.clicked.connect(lambda: self.marcar_como_pagado(pago))
            layout.addWidget(btn_pagar)

        # Botón 4: Comprobante
        btn_comprobante = QPushButton("🧾")
        btn_comprobante.setToolTip("Generar comprobante")
        btn_comprobante.setFixedSize(40, 28)
        btn_comprobante.setStyleSheet("""
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
        btn_comprobante.clicked.connect(lambda: self.generar_comprobante(pago))
        layout.addWidget(btn_comprobante)

        # Botón 5: Eliminar
        btn_eliminar = QPushButton("🗑️")
        btn_eliminar.setToolTip("Eliminar pago")
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
        btn_eliminar.clicked.connect(lambda: self.eliminar_pago(pago))
        layout.addWidget(btn_eliminar)

        # Agregar botones comunes
        layout.addWidget(btn_detalles)
        layout.addWidget(btn_editar)
        layout.addStretch()

        return widget
    
    # ============================================================================
    # MÉTODOS DE PAGINACIÓN
    # ============================================================================
    
    def actualizar_paginacion(self):
        """Actualizar controles de paginación y mostrar página actual"""
        try:
            # Calcular paginación
            total_pagos = len(self.pagos_filtrados_actuales)
            self.total_pages = max(1, (total_pagos + self.records_per_page - 1) // self.records_per_page)
            
            # Ajustar página actual si es necesario
            if self.current_page > self.total_pages:
                self.current_page = self.total_pages
            
            # Calcular índices para la página actual
            start_idx = (self.current_page - 1) * self.records_per_page
            end_idx = min(start_idx + self.records_per_page, total_pagos)
            
            # Obtener pagos para la página actual
            self.pagos_paginados = self.pagos_filtrados_actuales[start_idx:end_idx]
            
            # Actualizar botones
            self.btn_primera.setEnabled(self.current_page > 1)
            self.btn_anterior.setEnabled(self.current_page > 1)
            self.btn_siguiente.setEnabled(self.current_page < self.total_pages)
            self.btn_ultima.setEnabled(self.current_page < self.total_pages)
            
            # Actualizar información
            self.lbl_info_pagina.setText(f"Página {self.current_page} de {self.total_pages}")
            
            # Actualizar contador de registros
            if total_pagos > 0:
                self.lbl_contador.setText(f"Mostrando {start_idx + 1}-{end_idx} de {total_pagos} registros")
            else:
                self.lbl_contador.setText("Mostrando 0 de 0 registros")
            
            # Mostrar pagos de la página actual
            self.mostrar_pagos_en_tabla(self.pagos_paginados)
            
        except Exception as e:
            logger.error(f"Error al actualizar paginación: {e}")
    
    def cambiar_pagina(self, nueva_pagina):
        """Cambiar a una nueva página"""
        if 1 <= nueva_pagina <= self.total_pages and nueva_pagina != self.current_page:
            self.current_page = nueva_pagina
            self.actualizar_paginacion()
    
    # ============================================================================
    # MÉTODOS DE ACCIONES (A IMPLEMENTAR COMPLETAMENTE)
    # ============================================================================
    
    def agregar_nuevo_pago(self):
        """Abrir diálogo para agregar nuevo pago"""
        try:
            # Crear diálogo simple para ejemplo
            dialog = QDialog(self)
            dialog.setWindowTitle("Nuevo Pago")
            dialog.setModal(True)
            dialog.resize(500, 400)
            
            layout = QVBoxLayout(dialog)
            
            # Título
            titulo = QLabel("💳 Registrar Nuevo Pago")
            titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
            titulo.setAlignment(Qt.AlignCenter)
            layout.addWidget(titulo)
            
            # Formulario simple
            form_group = QGroupBox("Información del Pago")
            form_layout = QFormLayout(form_group)
            
            # Campos del formulario
            txt_codigo = QLineEdit()
            txt_codigo.setPlaceholderText("PAGO-001")
            
            date_fecha = QDateEdit()
            date_fecha.setDate(QDate.currentDate())
            date_fecha.setCalendarPopup(True)
            
            txt_estudiante = QLineEdit()
            txt_estudiante.setPlaceholderText("Nombre del estudiante")
            
            txt_concepto = QLineEdit()
            txt_concepto.setPlaceholderText("Matrícula, mensualidad, etc.")
            
            spin_monto = QDoubleSpinBox()
            spin_monto.setRange(0, 10000)
            spin_monto.setValue(0)
            spin_monto.setPrefix("Bs. ")
            spin_monto.setDecimals(2)
            
            combo_metodo = QComboBox()
            combo_metodo.addItems(["Efectivo", "Transferencia", "Tarjeta", "Cheque"])
            
            combo_estado = QComboBox()
            combo_estado.addItems(["Pendiente", "Completado", "Atrasado", "Cancelado"])
            
            # Agregar campos al formulario
            form_layout.addRow("Código:", txt_codigo)
            form_layout.addRow("Fecha:", date_fecha)
            form_layout.addRow("Estudiante:", txt_estudiante)
            form_layout.addRow("Concepto:", txt_concepto)
            form_layout.addRow("Monto:", spin_monto)
            form_layout.addRow("Método:", combo_metodo)
            form_layout.addRow("Estado:", combo_estado)
            
            layout.addWidget(form_group)
            
            # Botones
            btn_layout = QHBoxLayout()
            
            btn_cancelar = QPushButton("❌ Cancelar")
            btn_cancelar.clicked.connect(dialog.reject)
            
            btn_guardar = QPushButton("💾 Guardar Pago")
            btn_guardar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
            
            btn_guardar.clicked.connect(lambda: self.guardar_nuevo_pago(
                txt_codigo.text(),
                date_fecha.date().toString("yyyy-MM-dd"),
                txt_estudiante.text(),
                txt_concepto.text(),
                spin_monto.value(),
                combo_metodo.currentText(),
                combo_estado.currentText(),
                dialog
            ))
            
            btn_layout.addWidget(btn_cancelar)
            btn_layout.addWidget(btn_guardar)
            
            layout.addLayout(btn_layout)
            
            # Mostrar diálogo
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Error al abrir diálogo nuevo pago: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo abrir el formulario: {str(e)}")
    
    def guardar_nuevo_pago(self, codigo, fecha, estudiante, concepto, monto, metodo, estado, dialog):
        """Guardar nuevo pago en la base de datos"""
        try:
            if not codigo or not estudiante:
                QMessageBox.warning(self, "Advertencia", "Código y Estudiante son obligatorios")
                return
            
            # Crear objeto pago
            pago_data = {
                'codigo_pago': codigo,
                'fecha_pago': fecha,
                'estudiante_nombre': estudiante,
                'concepto': concepto,
                'monto': monto,
                'metodo_pago': metodo,
                'estado': estado.lower(),
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Guardar en la base de datos
            nuevo_pago = PagoModel.create(**pago_data)
            
            if nuevo_pago:
                QMessageBox.information(self, "Éxito", "Pago registrado correctamente")
                
                # Recargar pagos
                self.cargar_pagos()
                
                # Cerrar diálogo
                dialog.accept()
                
                # Emitir señal de actualización
                self.necesita_actualizar.emit()
            else:
                QMessageBox.critical(self, "Error", "No se pudo registrar el pago")
                
        except Exception as e:
            logger.error(f"Error al guardar nuevo pago: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo guardar el pago: {str(e)}")
    
    def ver_detalles_pago(self, pago):
        """Mostrar detalles del pago seleccionado"""
        try:
            # Crear diálogo de detalles
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Detalles del Pago - {getattr(pago, 'codigo_pago', '')}")
            dialog.setModal(True)
            dialog.resize(500, 400)
            
            layout = QVBoxLayout(dialog)
            
            # Título
            titulo = QLabel("📋 Detalles del Pago")
            titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
            titulo.setAlignment(Qt.AlignCenter)
            layout.addWidget(titulo)
            
            # Área de texto para mostrar detalles
            text_area = QTextEdit()
            text_area.setReadOnly(True)
            text_area.setStyleSheet("""
                QTextEdit {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    padding: 10px;
                    font-family: monospace;
                }
            """)
            
            # Formatear detalles
            detalles = f"""
            ╔═══════════════════════════════════════════╗
            ║           DETALLES DEL PAGO              ║
            ╠═══════════════════════════════════════════╣
            ║  Código:       {getattr(pago, 'codigo_pago', 'N/A')}
            ║  Fecha:        {getattr(pago, 'fecha_pago', 'N/A')}
            ║  Estudiante:   {getattr(pago, 'estudiante_nombre', 'N/A')}
            ║  Programa:     {getattr(pago, 'programa_nombre', 'N/A')}
            ╠═══════════════════════════════════════════╣
            ║  Concepto:     {getattr(pago, 'concepto', 'N/A')}
            ║  Monto:        Bs. {float(getattr(pago, 'monto', 0) or 0):.2f}
            ║  Método:       {getattr(pago, 'metodo_pago', 'N/A').capitalize()}
            ║  Estado:       {getattr(pago, 'estado', 'N/A').capitalize()}
            ╠═══════════════════════════════════════════╣
            ║  Fecha Creación: {getattr(pago, 'created_at', 'N/A')}
            ║  Última Actualización: {getattr(pago, 'updated_at', 'N/A')}
            ╚═══════════════════════════════════════════╝
            """
            
            text_area.setText(detalles)
            layout.addWidget(text_area)
            
            # Botón Cerrar
            btn_cerrar = QPushButton("❌ Cerrar")
            btn_cerrar.clicked.connect(dialog.accept)
            btn_cerrar.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    font-weight: bold;
                    padding: 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)
            layout.addWidget(btn_cerrar)
            
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Error al mostrar detalles: {e}")
            QMessageBox.warning(self, "Error", f"No se pudieron mostrar los detalles: {str(e)}")
    
    def editar_pago(self, pago):
        """Abrir diálogo para editar pago"""
        QMessageBox.information(self, "Editar Pago", 
            f"Funcionalidad de edición para el pago {getattr(pago, 'codigo_pago', '')}\n\nEsta función se implementará completamente en la siguiente versión.")
    
    def marcar_como_pagado(self, pago):
        """Marcar un pago como pagado"""
        try:
            respuesta = QMessageBox.question(
                self, 
                "Confirmar Pago",
                f"¿Está seguro de marcar el pago {getattr(pago, 'codigo_pago', '')} como PAGADO?\n\nEstudiante: {getattr(pago, 'estudiante_nombre', '')}\nMonto: Bs. {float(getattr(pago, 'monto', 0) or 0):.2f}",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if respuesta == QMessageBox.Yes:
                # Actualizar estado
                pago.estado = 'completado'
                if hasattr(pago, 'save'):
                    pago.save()
                
                # Mostrar mensaje de éxito
                QMessageBox.information(self, "Éxito", "Pago marcado como completado")
                
                # Recargar datos
                self.cargar_pagos()
                
        except Exception as e:
            logger.error(f"Error al marcar como pagado: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el pago: {str(e)}")
    
    def generar_comprobante(self, pago):
        """Generar comprobante de pago"""
        QMessageBox.information(self, "Generar Comprobante", 
            f"Generando comprobante para el pago {getattr(pago, 'codigo_pago', '')}\n\nEsta función se implementará completamente en la siguiente versión.")
    
    def eliminar_pago(self, pago):
        """Eliminar un pago"""
        try:
            respuesta = QMessageBox.warning(
                self, 
                "Confirmar Eliminación",
                f"¿Está seguro de ELIMINAR el pago {getattr(pago, 'codigo_pago', '')}?\n\n⚠️ Esta acción no se puede deshacer.\n\nEstudiante: {getattr(pago, 'estudiante_nombre', '')}\nMonto: Bs. {float(getattr(pago, 'monto', 0) or 0):.2f}",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if respuesta == QMessageBox.Yes:
                # Eliminar pago
                if hasattr(pago, 'delete'):
                    resultado = pago.delete()
                else:
                    resultado = False
                
                if resultado:
                    QMessageBox.information(self, "Éxito", "Pago eliminado correctamente")
                    
                    # Recargar datos
                    self.cargar_pagos()
                    
                    # Emitir señal de actualización
                    self.necesita_actualizar.emit()
                else:
                    QMessageBox.critical(self, "Error", "No se pudo eliminar el pago")
                
        except Exception as e:
            logger.error(f"Error al eliminar pago: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo eliminar el pago: {str(e)}")
    
    def generar_reporte(self):
        """Generar reporte financiero"""
        try:
            # Diálogo simple de reporte
            dialog = QDialog(self)
            dialog.setWindowTitle("📊 Generar Reporte Financiero")
            dialog.setModal(True)
            dialog.resize(400, 300)
            
            layout = QVBoxLayout(dialog)
            
            # Título
            titulo = QLabel("Generar Reporte Financiero")
            titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
            titulo.setAlignment(Qt.AlignCenter)
            layout.addWidget(titulo)
            
            # Opciones de reporte
            group_opciones = QGroupBox("Opciones de Reporte")
            group_layout = QVBoxLayout(group_opciones)
            
            radio_mensual = QPushButton("📅 Reporte Mensual")
            radio_trimestral = QPushButton("📊 Reporte Trimestral")
            radio_anual = QPushButton("📈 Reporte Anual")
            radio_pendientes = QPushButton("⚠️ Reporte de Pendientes")
            
            for btn in [radio_mensual, radio_trimestral, radio_anual, radio_pendientes]:
                btn.setFixedHeight(40)
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding-left: 20px;
                        background-color: #f8f9fa;
                        border: 1px solid #dee2e6;
                        border-radius: 5px;
                        margin: 2px;
                    }
                    QPushButton:hover {
                        background-color: #e9ecef;
                        border-color: #3498db;
                    }
                """)
                group_layout.addWidget(btn)
            
            layout.addWidget(group_opciones)
            
            # Conectar botones
            radio_mensual.clicked.connect(lambda: self.generar_reporte_tipo("mensual", dialog))
            radio_trimestral.clicked.connect(lambda: self.generar_reporte_tipo("trimestral", dialog))
            radio_anual.clicked.connect(lambda: self.generar_reporte_tipo("anual", dialog))
            radio_pendientes.clicked.connect(lambda: self.generar_reporte_tipo("pendientes", dialog))
            
            # Botón Cancelar
            btn_cancelar = QPushButton("❌ Cancelar")
            btn_cancelar.clicked.connect(dialog.reject)
            layout.addWidget(btn_cancelar)
            
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Error al generar reporte: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo generar el reporte: {str(e)}")
    
    def generar_reporte_tipo(self, tipo, dialog):
        """Generar reporte según tipo seleccionado"""
        try:
            # Cerrar diálogo
            dialog.accept()
            
            # Generar reporte simple
            fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            # Calcular estadísticas básicas
            total_pagos = len(self.pagos_data)
            completados = sum(1 for p in self.pagos_data if getattr(p, 'estado', '').lower() in ['completado', 'pagado'])
            pendientes = sum(1 for p in self.pagos_data if getattr(p, 'estado', '').lower() == 'pendiente')
            total_ingresos = sum(float(getattr(p, 'monto', 0) or 0) for p in self.pagos_data if getattr(p, 'estado', '').lower() in ['completado', 'pagado'])
            
            # Mostrar reporte en un diálogo
            reporte_dialog = QDialog(self)
            reporte_dialog.setWindowTitle(f"Reporte {tipo.capitalize()}")
            reporte_dialog.setModal(True)
            reporte_dialog.resize(600, 500)
            
            layout = QVBoxLayout(reporte_dialog)
            
            # Título
            titulo = QLabel(f"📊 REPORTE {tipo.upper()} - {fecha_actual}")
            titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
            titulo.setAlignment(Qt.AlignCenter)
            layout.addWidget(titulo)
            
            # Área de texto para el reporte
            text_area = QTextEdit()
            text_area.setReadOnly(True)
            text_area.setStyleSheet("""
                QTextEdit {
                    background-color: white;
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    padding: 15px;
                    font-family: 'Courier New', monospace;
                    font-size: 12px;
                }
            """)
            
            # Generar contenido del reporte
            contenido = f"""
            {'='*60}
            FORMA GESTPRO - REPORTE FINANCIERO {tipo.upper()}
            {'='*60}
            Fecha de generación: {fecha_actual}
            {'-'*60}
            
            📈 RESUMEN GENERAL:
            {'─'*40}
            • Total de pagos registrados: {total_pagos}
            • Pagos completados: {completados}
            • Pagos pendientes: {pendientes}
            • Ingresos totales: Bs. {total_ingresos:.2f}
            {'-'*60}
            
            📅 DESGLOSE POR MÉTODO DE PAGO:
            {'─'*40}
            """
            
            # Agregar métodos de pago
            metodos = {}
            for pago in self.pagos_data:
                metodo = getattr(pago, 'metodo_pago', 'No especificado') or 'No especificado'
                metodos[metodo] = metodos.get(metodo, 0) + 1
            
            for metodo, cantidad in metodos.items():
                porcentaje = (cantidad / total_pagos * 100) if total_pagos > 0 else 0
                contenido += f"• {metodo}: {cantidad} ({porcentaje:.1f}%)\n"
            
            contenido += f"""
            {'-'*60}
            
            ⚠️  PAGOS PENDIENTES:
            {'─'*40}
            """
            
            # Listar primeros 10 pagos pendientes
            pendientes_lista = [p for p in self.pagos_data if getattr(p, 'estado', '').lower() == 'pendiente'][:10]
            for i, pago in enumerate(pendientes_lista, 1):
                contenido += f"{i}. {getattr(pago, 'estudiante_nombre', 'N/A')}: Bs. {float(getattr(pago, 'monto', 0) or 0):.2f}\n"
            
            if len(pendientes_lista) < len([p for p in self.pagos_data if getattr(p, 'estado', '').lower() == 'pendiente']):
                contenido += f"... y {len([p for p in self.pagos_data if getattr(p, 'estado', '').lower() == 'pendiente']) - 10} más\n"
            
            contenido += f"""
            {'='*60}
            Fin del Reporte
            {'='*60}
            """
            
            text_area.setText(contenido)
            layout.addWidget(text_area)
            
            # Botones
            btn_layout = QHBoxLayout()
            
            btn_imprimir = QPushButton("🖨️ Imprimir")
            btn_exportar = QPushButton("📥 Exportar PDF")
            btn_cerrar = QPushButton("❌ Cerrar")
            
            for btn in [btn_imprimir, btn_exportar, btn_cerrar]:
                btn.setFixedHeight(35)
                btn_layout.addWidget(btn)
            
            btn_cerrar.clicked.connect(reporte_dialog.accept)
            
            layout.addLayout(btn_layout)
            
            reporte_dialog.exec()
            
        except Exception as e:
            logger.error(f"Error al generar reporte {tipo}: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo generar el reporte: {str(e)}")
    
    def actualizar_datos(self):
        """Actualizar datos desde la base de datos"""
        self.cargar_pagos()