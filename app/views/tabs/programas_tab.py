# app/views/tabs/programas_tab.py
"""
Pestaña de Programas - Versión completa con paginación
"""

import logging
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QLineEdit, QLabel,
    QComboBox, QFormLayout, QGroupBox, QGridLayout, QFrame, QMenu
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon, QFont, QColor

from app.models.programa_academico_model import ProgramaAcademicoModel

logger = logging.getLogger(__name__)

class ProgramasTab(QWidget):
    """Pestaña para gestión de programas académicos con paginación"""
    
    # Señales para comunicación con MainWindow
    programa_seleccionado = Signal(dict)
    necesita_actualizar = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.programas_data = []
        self.programas_paginados = []
        self.programas_filtrados_actuales = []
        self.current_filter = 'todos'
        self.current_page = 1
        self.records_per_page = 10  # Mostrar 10 registros por página
        self.total_pages = 1
        
        self.setup_ui()
        self.setup_connections()
        self.cargar_programas()
    
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
        title_label = QLabel("📚 Gestión de Programas")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Botón Nuevo Programa
        self.btn_nuevo_programa = QPushButton("➕ Nuevo Programa")
        self.btn_nuevo_programa.setFixedHeight(40)
        self.btn_nuevo_programa.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
        """)
        self.btn_nuevo_programa.setToolTip("Agregar un nuevo programa académico")
        header_layout.addWidget(self.btn_nuevo_programa)
        
        layout.addWidget(header_frame)
        
        # ============ FILTROS ============
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        filter_layout = QHBoxLayout(filter_frame)
        
        # Etiqueta de filtro
        filter_label = QLabel("Filtrar por estado:")
        filter_label.setStyleSheet("font-weight: bold; color: #495057;")
        filter_layout.addWidget(filter_label)
        
        # Combo box para filtro
        self.combo_filtro = QComboBox()
        self.combo_filtro.addItems(['Todos', 'Activos', 'Inactivos', 'Planificados', 'Finalizados'])
        self.combo_filtro.setFixedHeight(36)
        self.combo_filtro.setFixedWidth(150)
        self.combo_filtro.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
                color: black;
            }
            QComboBox:focus {
                border: 2px solid #2ecc71;
            }
        """)
        filter_layout.addWidget(self.combo_filtro)
        
        # Buscador
        search_label = QLabel("Buscar:")
        search_label.setStyleSheet("font-weight: bold; color: #495057; margin-left: 20px;")
        filter_layout.addWidget(search_label)
        
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Código, nombre o carrera...")
        self.txt_buscar.setFixedHeight(36)
        self.txt_buscar.setMinimumWidth(250)
        self.txt_buscar.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #2ecc71;
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
        
        # ============ TABLA DE PROGRAMAS ============
        self.tabla_programas = QTableWidget()
        self.tabla_programas.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                gridline-color: #dee2e6;
                color: black;
            }
            QTableWidget::item {
                padding: 3px;
                border-bottom: 1px solid #dee2e6;
            }
            QTableWidget::item:selected {
                background-color: #2ecc71;
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
        
        self.tabla_programas.setAlternatingRowColors(True)
        self.tabla_programas.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_programas.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla_programas.verticalHeader().setVisible(False)
        self.tabla_programas.verticalHeader().setDefaultSectionSize(40)
        
        layout.addWidget(self.tabla_programas, 1)
        
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
        self.lbl_estado = QLabel("Cargando programas...")
        self.lbl_estado.setStyleSheet("color: #7f8c8d; font-style: italic;")
        self.lbl_estado.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_estado)
    
    def setup_connections(self):
        """Conectar señales y slots"""
        # Botones
        self.btn_nuevo_programa.clicked.connect(self.agregar_nuevo_programa)
        self.btn_buscar.clicked.connect(self.buscar_programas)
        self.btn_limpiar.clicked.connect(self.limpiar_busqueda)
        
        # Filtros
        self.combo_filtro.currentTextChanged.connect(
            lambda: self.filtrar_programas(desde_paginacion=False)
        )
        self.txt_buscar.returnPressed.connect(self.buscar_programas)
        
        # Paginación
        self.btn_primera.clicked.connect(lambda: self.cambiar_pagina(1))
        self.btn_anterior.clicked.connect(lambda: self.cambiar_pagina(self.current_page - 1))
        self.btn_siguiente.clicked.connect(lambda: self.cambiar_pagina(self.current_page + 1))
        self.btn_ultima.clicked.connect(lambda: self.cambiar_pagina(self.total_pages))
    
    def cargar_programas(self, filtro='todos'):
        """Cargar programas desde la base de datos"""
        try:
            self.lbl_estado.setText("Cargando programas...")
            
            # Obtener todos los programas
            self.programas_data = ProgramaAcademicoModel.get_all()
            
            # Resetear paginación
            self.current_page = 1
            
            # Aplicar filtro inicial
            self.current_filter = filtro
            self.filtrar_programas(desde_paginacion=False)
            
            if self.programas_data:
                self.lbl_estado.setText(f"✅ {len(self.programas_data)} programas cargados")
            else:
                self.lbl_estado.setText("📭 No hay programas registrados")
                
        except Exception as e:
            logger.error(f"Error al cargar programas: {e}")
            self.lbl_estado.setText("❌ Error al cargar programas")
            QMessageBox.critical(self, "Error", f"Error al cargar programas: {str(e)}")
    
    def filtrar_programas(self, desde_paginacion=False):
        """Filtrar programas según el estado seleccionado y aplicar paginación"""
        try:
            # Obtener valores actuales
            filtro_texto = self.combo_filtro.currentText().lower()
            texto_busqueda = self.txt_buscar.text().strip().lower()
            
            # Filtrar programas
            programas_filtrados = []
            for programa in self.programas_data:
                # Filtrar por estado
                estado = getattr(programa, 'estado', '').lower()
                if filtro_texto == 'activos' and estado != 'activo':
                    continue
                elif filtro_texto == 'inactivos' and estado != 'inactivo':
                    continue
                elif filtro_texto == 'planificados' and estado != 'planificado':
                    continue
                elif filtro_texto == 'finalizados' and estado != 'finalizado':
                    continue
                
                # Filtrar por búsqueda si hay texto
                if texto_busqueda:
                    campos = [
                        str(getattr(programa, 'codigo', '') or ''),
                        str(getattr(programa, 'nombre', '') or ''),
                        str(getattr(programa, 'descripcion', '') or ''),
                        str(getattr(programa, 'carrera', '') or '')
                    ]
                    
                    if not any(texto_busqueda in campo.lower() for campo in campos):
                        continue
                
                programas_filtrados.append(programa)
            
            # Actualizar la lista filtrada
            self.programas_filtrados_actuales = programas_filtrados
            
            # Resetear a página 1 solo si no viene desde paginación
            if not desde_paginacion:
                self.current_page = 1
            
            # Actualizar la paginación
            self.actualizar_paginacion()
            
        except Exception as e:
            logger.error(f"Error al filtrar programas: {e}")
            import traceback
            traceback.print_exc()
    
    def buscar_programas(self):
        """Buscar programas según el texto ingresado"""
        self.current_page = 1
        self.filtrar_programas(desde_paginacion=False)
    
    def limpiar_busqueda(self):
        """Limpiar el campo de búsqueda, resetear paginación y mostrar todos"""
        self.txt_buscar.clear()
        self.current_page = 1
        self.filtrar_programas(desde_paginacion=False)
    
    def mostrar_programas_en_tabla(self, programas):
        """Mostrar programas en la tabla"""
        try:
            self.tabla_programas.clear()
            
            # Configurar columnas
            columnas = [
                "ID", "Código", "Nombre", "Carrera", "Duración", 
                "Costo", "Cupos", "Estado", "Acciones"
            ]
            
            self.tabla_programas.setColumnCount(len(columnas))
            self.tabla_programas.setHorizontalHeaderLabels(columnas)
            self.tabla_programas.setRowCount(len(programas))
            
            # Llenar datos
            for fila, programa in enumerate(programas):
                # Configurar altura de fila uniforme
                self.tabla_programas.setRowHeight(fila, 40)
                
                # ID
                item_id = QTableWidgetItem(str(programa.id))
                item_id.setTextAlignment(Qt.AlignCenter)
                self.tabla_programas.setItem(fila, 0, item_id)
                
                # Código
                codigo = getattr(programa, 'codigo', '') or ''
                item_codigo = QTableWidgetItem(codigo)
                item_codigo.setTextAlignment(Qt.AlignCenter)
                self.tabla_programas.setItem(fila, 1, item_codigo)
                
                # Nombre
                nombre = getattr(programa, 'nombre', '') or ''
                item_nombre = QTableWidgetItem(nombre)
                self.tabla_programas.setItem(fila, 2, item_nombre)
                
                # Carrera
                carrera = getattr(programa, 'carrera', '') or ''
                item_carrera = QTableWidgetItem(carrera)
                self.tabla_programas.setItem(fila, 3, item_carrera)
                
                # Duración
                duracion = getattr(programa, 'duracion_meses', '') or ''
                if duracion:
                    duracion_text = f"{duracion} meses"
                else:
                    duracion_text = getattr(programa, 'duracion', '') or ''
                item_duracion = QTableWidgetItem(duracion_text)
                self.tabla_programas.setItem(fila, 4, item_duracion)
                
                # Costo
                costo = getattr(programa, 'costo_base', 0) or getattr(programa, 'costo', 0) or 0
                item_costo = QTableWidgetItem(f"Bs. {float(costo):.2f}")
                self.tabla_programas.setItem(fila, 5, item_costo)
                
                # Cupos
                cupos_totales = getattr(programa, 'cupos_totales', 0) or 0
                cupos_disponibles = getattr(programa, 'cupos_disponibles', 0) or 0
                cupos_text = f"{cupos_disponibles}/{cupos_totales}"
                item_cupos = QTableWidgetItem(cupos_text)
                item_cupos.setTextAlignment(Qt.AlignCenter)
                self.tabla_programas.setItem(fila, 6, item_cupos)
                
                # Estado
                estado = getattr(programa, 'estado', '') or ''
                if not estado:
                    estado = "Activo" if getattr(programa, 'activo', 1) == 1 else "Inactivo"
                
                item_estado = QTableWidgetItem(estado.capitalize())
                item_estado.setTextAlignment(Qt.AlignCenter)
                
                # Color según estado
                estado_lower = estado.lower()
                if estado_lower == 'activo' or estado_lower == 'iniciado':
                    item_estado.setForeground(Qt.darkGreen)
                elif estado_lower == 'planificado':
                    item_estado.setForeground(QColor("#f39c12"))  # Naranja
                elif estado_lower == 'finalizado':
                    item_estado.setForeground(Qt.darkRed)
                elif estado_lower == 'inactivo':
                    item_estado.setForeground(Qt.darkGray)
                else:
                    item_estado.setForeground(Qt.black)
                    
                self.tabla_programas.setItem(fila, 7, item_estado)
                
                # Acciones (botones)
                widget_acciones = self.crear_widget_acciones(programa)
                self.tabla_programas.setCellWidget(fila, 8, widget_acciones)
            
            # Ajustar columnas
            self.tabla_programas.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # Nombre
            self.tabla_programas.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # Carrera
            
            # Columnas fijas
            self.tabla_programas.setColumnWidth(0, 50)   # ID
            self.tabla_programas.setColumnWidth(1, 100)  # Código
            self.tabla_programas.setColumnWidth(4, 80)   # Duración
            self.tabla_programas.setColumnWidth(5, 100)  # Costo
            self.tabla_programas.setColumnWidth(6, 80)   # Cupos
            self.tabla_programas.setColumnWidth(7, 100)  # Estado
            
            # Acciones: 6 botones de 40px + 6 espacios de 3px = ~258px
            self.tabla_programas.setColumnWidth(8, 258)  # Acciones
            
        except Exception as e:
            logger.error(f"Error al mostrar programas en tabla: {e}")
            self.lbl_estado.setText("❌ Error al mostrar programas")
    
    def crear_widget_acciones(self, programa):
        """Crear widget con botones de acciones completas"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        # Botón 1: Ver Detalles
        btn_detalles = QPushButton("👁️")
        btn_detalles.setToolTip("Ver detalles del programa")
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
        btn_detalles.clicked.connect(lambda: self.ver_detalles_programa(programa))

        # Botón 2: Editar
        btn_editar = QPushButton("✏️")
        btn_editar.setToolTip("Editar programa")
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
        btn_editar.clicked.connect(lambda: self.editar_programa(programa))

        # Botón 3: Estudiantes inscritos
        btn_estudiantes = QPushButton("👥")
        btn_estudiantes.setToolTip("Ver estudiantes inscritos")
        btn_estudiantes.setFixedSize(40, 28)
        btn_estudiantes.setStyleSheet("""
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
        btn_estudiantes.clicked.connect(lambda: self.ver_estudiantes_programa(programa))

        # Botón 4: Docentes asignados
        btn_docentes = QPushButton("👨‍🏫")
        btn_docentes.setToolTip("Ver docentes asignados")
        btn_docentes.setFixedSize(40, 28)
        btn_docentes.setStyleSheet("""
            QPushButton {
                background-color: #1abc9c;
                color: white;
                border-radius: 3px;
                border: none;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #16a085;
            }
            QPushButton:pressed {
                background-color: #138d75;
            }
        """)
        btn_docentes.clicked.connect(lambda: self.ver_docentes_programa(programa))

        # Botón 5: Promoción/Descuento
        btn_promocion = QPushButton("🎁")
        btn_promocion.setToolTip("Configurar promoción/descuento")
        btn_promocion.setFixedSize(40, 28)
        btn_promocion.setStyleSheet("""
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
        btn_promocion.clicked.connect(lambda: self.configurar_promocion(programa))

        # Botón 6: Eliminar
        btn_eliminar = QPushButton("🗑️")
        btn_eliminar.setToolTip("Eliminar programa")
        btn_eliminar.setFixedSize(40, 28)
        btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                border-radius: 3px;
                border: none;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
            QPushButton:pressed {
                background-color: #1a252f;
            }
        """)
        btn_eliminar.clicked.connect(lambda: self.eliminar_programa(programa))

        # Agregar todos los botones al layout
        layout.addWidget(btn_detalles)
        layout.addWidget(btn_editar)
        layout.addWidget(btn_estudiantes)
        layout.addWidget(btn_docentes)
        layout.addWidget(btn_promocion)
        layout.addWidget(btn_eliminar)
        layout.addStretch()

        return widget
    
    # ============================================================================
    # MÉTODOS DE PAGINACIÓN
    # ============================================================================
    
    def actualizar_paginacion(self):
        """Actualizar controles de paginación y mostrar página actual"""
        # Calcular paginación
        total_programas = len(self.programas_filtrados_actuales)
        self.total_pages = max(1, (total_programas + self.records_per_page - 1) // self.records_per_page)
        
        # Ajustar página actual si es necesario
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        
        # Calcular índices para la página actual
        start_idx = (self.current_page - 1) * self.records_per_page
        end_idx = min(start_idx + self.records_per_page, total_programas)
        
        # Obtener programas para la página actual
        self.programas_paginados = self.programas_filtrados_actuales[start_idx:end_idx]
        
        # Actualizar botones
        self.btn_primera.setEnabled(self.current_page > 1)
        self.btn_anterior.setEnabled(self.current_page > 1)
        self.btn_siguiente.setEnabled(self.current_page < self.total_pages)
        self.btn_ultima.setEnabled(self.current_page < self.total_pages)
        
        # Actualizar información
        self.lbl_info_pagina.setText(f"Página {self.current_page} de {self.total_pages}")
        
        # Mostrar programas de la página actual
        self.mostrar_programas_en_tabla(self.programas_paginados)
        
        # Actualizar contador
        mostrar_texto = f"Mostrando {len(self.programas_paginados)} de {total_programas} registros"
        if total_programas > 0:
            mostrar_texto += f" ({start_idx + 1}-{end_idx})"
        self.lbl_contador.setText(mostrar_texto)
    
    def cambiar_pagina(self, nueva_pagina):
        """Cambiar a una nueva página"""
        if 1 <= nueva_pagina <= self.total_pages and nueva_pagina != self.current_page:
            self.current_page = nueva_pagina
            self.actualizar_paginacion()
    
    # ============================================================================
    # MÉTODOS PRINCIPALES DE GESTIÓN
    # ============================================================================
    
    def agregar_nuevo_programa(self):
        """Abrir diálogo para nuevo programa"""
        try:
            from app.views.dialogs.programa_form_dialog import ProgramaFormDialog
            
            dialog = ProgramaFormDialog(
                programa_id=None,
                modo_lectura=False,
                parent=self
            )
            
            if dialog.exec():
                self.cargar_programas(self.current_filter)
                
        except ImportError:
            QMessageBox.information(
                self, 
                "Funcionalidad no implementada", 
                "El formulario de programa aún no está implementado"
            )
        except Exception as e:
            logger.error(f"Error al crear programa: {e}")
            QMessageBox.critical(self, "Error", f"Error al crear programa: {str(e)}")
    
    def ver_detalles_programa(self, programa):
        """Mostrar diálogo con detalles del programa"""
        try:
            from app.views.dialogs.programa_form_dialog import ProgramaFormDialog
            
            programa_data = {
                'id': programa.id,
                'codigo': getattr(programa, 'codigo', ''),
                'nombre': getattr(programa, 'nombre', ''),
                'descripcion': getattr(programa, 'descripcion', ''),
                'carrera': getattr(programa, 'carrera', ''),
                'duracion': getattr(programa, 'duracion_meses', '') or getattr(programa, 'duracion', ''),
                'costo_base': getattr(programa, 'costo_base', 0) or getattr(programa, 'costo', 0),
                'cupos_totales': getattr(programa, 'cupos_totales', 0),
                'cupos_disponibles': getattr(programa, 'cupos_disponibles', 0),
                'estado': getattr(programa, 'estado', ''),
                'activo': getattr(programa, 'activo', 1)
            }
            
            dialog = ProgramaFormDialog(
                programa_data=programa_data,
                modo_lectura=True,
                parent=self
            )
            
            dialog.exec()
            
        except ImportError:
            QMessageBox.information(
                self, 
                "Funcionalidad no implementada", 
                f"Vista de detalles para programa ID {programa.id}\n"
                f"(Por implementar)"
            )
        except Exception as e:
            logger.error(f"Error al mostrar detalles: {e}")
            QMessageBox.critical(self, "Error", f"Error al mostrar detalles: {str(e)}")
    
    def editar_programa(self, programa):
        """Abrir diálogo para editar un programa"""
        try:
            from app.views.dialogs.programa_form_dialog import ProgramaFormDialog
            
            dialog = ProgramaFormDialog(
                programa_id=programa.id,
                modo_lectura=False,
                parent=self
            )
            
            if dialog.exec():
                self.cargar_programas(self.current_filter)
        
        except ImportError:
            QMessageBox.information(
                self, 
                "Funcionalidad no implementada", 
                f"Edición para programa ID {programa.id}\n"
                f"(Por implementar)"
            )
        except Exception as e:
            logger.error(f"Error al editar programa: {e}")
            QMessageBox.critical(self, "Error", f"Error al editar programa: {str(e)}")
    
    def ver_estudiantes_programa(self, programa):
        """Mostrar estudiantes inscritos en el programa"""
        try:
            QMessageBox.information(
                self, 
                "Estudiantes Inscritos", 
                f"Mostrando estudiantes inscritos en {getattr(programa, 'nombre', 'Programa')}\n"
                f"(Funcionalidad por implementar)"
            )
        except Exception as e:
            logger.error(f"Error al ver estudiantes: {e}")
            QMessageBox.critical(self, "Error", f"Error al ver estudiantes: {str(e)}")
    
    def ver_docentes_programa(self, programa):
        """Mostrar docentes asignados al programa"""
        try:
            QMessageBox.information(
                self, 
                "Docentes Asignados", 
                f"Mostrando docentes asignados a {getattr(programa, 'nombre', 'Programa')}\n"
                f"(Funcionalidad por implementar)"
            )
        except Exception as e:
            logger.error(f"Error al ver docentes: {e}")
            QMessageBox.critical(self, "Error", f"Error al ver docentes: {str(e)}")
    
    def configurar_promocion(self, programa):
        """Configurar promoción/descuento para el programa"""
        try:
            QMessageBox.information(
                self, 
                "Configurar Promoción", 
                f"Configurando promoción para {getattr(programa, 'nombre', 'Programa')}\n"
                f"(Funcionalidad por implementar)"
            )
        except Exception as e:
            logger.error(f"Error al configurar promoción: {e}")
            QMessageBox.critical(self, "Error", f"Error al configurar promoción: {str(e)}")
    
    def eliminar_programa(self, programa):
        """Eliminar programa del sistema"""
        try:
            respuesta = QMessageBox.question(
                self,
                "Confirmar Eliminación",
                f"¿Está seguro de eliminar este programa?\n\n"
                f"Programa: {getattr(programa, 'nombre', 'N/A')}\n"
                f"Código: {getattr(programa, 'codigo', 'N/A')}\n\n"
                f"⚠️ Esta acción no se puede deshacer.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if respuesta == QMessageBox.Yes:
                # Eliminar de la base de datos
                programa.delete()
                
                # Actualizar tabla
                self.cargar_programas(self.current_filter)
                
                QMessageBox.information(self, "✅ Éxito", "Programa eliminado correctamente")
                
        except Exception as e:
            logger.error(f"Error al eliminar programa: {e}")
            QMessageBox.critical(self, "Error", f"Error al eliminar programa: {str(e)}")
    
    # ============================================================================
    # MÉTODOS AUXILIARES
    # ============================================================================
    
    def actualizar_interfaz(self):
        """Actualizar la interfaz después de cambios"""
        self.cargar_programas(self.current_filter)
    
    def obtener_programa_por_id(self, programa_id):
        """Obtener programa por ID desde los datos cargados"""
        for programa in self.programas_data:
            if programa.id == programa_id:
                return programa
        return None