# app/views/tabs/estudiantes_tab.py
"""
Pestaña de gestión de estudiantes - Implementación completa con paginación
"""

import logging
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QLineEdit, QLabel,
    QComboBox, QFormLayout, QGroupBox, QGridLayout, QFrame, QMenu
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon, QFont

from app.models.estudiante_model import EstudianteModel

logger = logging.getLogger(__name__)

class EstudiantesTab(QWidget):
    """Pestaña para gestión de estudiantes con flujo completo edición/lectura y paginación"""
    
    # Señales para comunicación con MainWindow
    estudiante_seleccionado = Signal(dict)
    necesita_actualizar = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.estudiantes_data = []
        self.estudiantes_paginados = []
        self.estudiantes_filtrados_actuales = []
        self.current_filter = 'todos'
        self.current_page = 1
        self.records_per_page = 10  # Mostrar 10 registros por página
        self.total_pages = 1
        
        self.setup_ui()
        self.setup_connections()
        self.cargar_estudiantes()
    
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
        title_label = QLabel("👨‍🎓 Gestión de Estudiantes")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Botón Nuevo Estudiante
        self.btn_nuevo_estudiante = QPushButton("➕ Nuevo Estudiante")
        self.btn_nuevo_estudiante.setFixedHeight(40)
        self.btn_nuevo_estudiante.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:pressed {
                background-color: #7d3c98;
            }
        """)
        self.btn_nuevo_estudiante.setToolTip("Agregar un nuevo estudiante al sistema")
        header_layout.addWidget(self.btn_nuevo_estudiante)
        
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
        self.combo_filtro.addItems(['Todos', 'Activos', 'Inactivos', 'Graduados'])
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
                border: 2px solid #9b59b6;
            }
        """)
        filter_layout.addWidget(self.combo_filtro)
        
        # Buscador
        search_label = QLabel("Buscar:")
        search_label.setStyleSheet("font-weight: bold; color: #495057; margin-left: 20px;")
        filter_layout.addWidget(search_label)
        
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Nombre, CI, matrícula o carrera...")
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
                border: 2px solid #9b59b6;
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
        
        # ============ TABLA DE ESTUDIANTES ============
        self.tabla_estudiantes = QTableWidget()
        self.tabla_estudiantes.setStyleSheet("""
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
                background-color: #9b59b6;
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
        
        self.tabla_estudiantes.setAlternatingRowColors(True)
        self.tabla_estudiantes.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_estudiantes.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla_estudiantes.verticalHeader().setVisible(False)
        self.tabla_estudiantes.verticalHeader().setDefaultSectionSize(40)
        
        layout.addWidget(self.tabla_estudiantes, 1)
        
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
        self.lbl_estado = QLabel("Cargando estudiantes...")
        self.lbl_estado.setStyleSheet("color: #7f8c8d; font-style: italic;")
        self.lbl_estado.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_estado)
    
    def setup_connections(self):
        """Conectar señales y slots"""
        # Botones
        self.btn_nuevo_estudiante.clicked.connect(self.agregar_nuevo_estudiante)
        self.btn_buscar.clicked.connect(self.buscar_estudiantes)
        self.btn_limpiar.clicked.connect(self.limpiar_busqueda)
        
        # Filtros
        self.combo_filtro.currentTextChanged.connect(
            lambda: self.filtrar_estudiantes(desde_paginacion=False)
        )
        self.txt_buscar.returnPressed.connect(self.buscar_estudiantes)
        
        # Paginación
        self.btn_primera.clicked.connect(lambda: self.cambiar_pagina(1))
        self.btn_anterior.clicked.connect(lambda: self.cambiar_pagina(self.current_page - 1))
        self.btn_siguiente.clicked.connect(lambda: self.cambiar_pagina(self.current_page + 1))
        self.btn_ultima.clicked.connect(lambda: self.cambiar_pagina(self.total_pages))
    
    def cargar_estudiantes(self, filtro='todos'):
        """Cargar estudiantes desde la base de datos"""
        try:
            self.lbl_estado.setText("Cargando estudiantes...")
            
            # Obtener todos los estudiantes
            self.estudiantes_data = EstudianteModel.get_all()
            
            # Resetear paginación
            self.current_page = 1
            
            # Aplicar filtro inicial
            self.current_filter = filtro
            self.filtrar_estudiantes(desde_paginacion=False)
            
            if self.estudiantes_data:
                self.lbl_estado.setText(f"✅ {len(self.estudiantes_data)} estudiantes cargados")
            else:
                self.lbl_estado.setText("📭 No hay estudiantes registrados")
                
        except Exception as e:
            logger.error(f"Error al cargar estudiantes: {e}")
            self.lbl_estado.setText("❌ Error al cargar estudiantes")
            QMessageBox.critical(self, "Error", f"Error al cargar estudiantes: {str(e)}")
    
    def filtrar_estudiantes(self, desde_paginacion=False):
        """Filtrar estudiantes según el estado seleccionado y aplicar paginación"""
        try:
            # Obtener valores actuales
            filtro_texto = self.combo_filtro.currentText().lower()
            texto_busqueda = self.txt_buscar.text().strip().lower()
            
            # Filtrar estudiantes
            estudiantes_filtrados = []
            for estudiante in self.estudiantes_data:
                # Filtrar por estado
                if filtro_texto == 'activos' and estudiante.activo != 1:
                    continue
                elif filtro_texto == 'inactivos' and estudiante.activo != 0:
                    continue
                elif filtro_texto == 'graduados':
                    # Asumiendo que hay un atributo 'graduado' en el modelo
                    if not getattr(estudiante, 'graduado', False):
                        continue
                
                # Filtrar por búsqueda si hay texto
                if texto_busqueda:
                    campos = [
                        str(estudiante.nombres or ''),
                        str(estudiante.apellidos or ''),
                        str(getattr(estudiante, 'ci_numero', '') or ''),
                        str(getattr(estudiante, 'matricula', '') or ''),
                        str(getattr(estudiante, 'carrera', '') or '')
                    ]
                    
                    if not any(texto_busqueda in campo.lower() for campo in campos):
                        continue
                
                estudiantes_filtrados.append(estudiante)
            
            # Actualizar la lista filtrada
            self.estudiantes_filtrados_actuales = estudiantes_filtrados
            
            # Resetear a página 1 solo si no viene desde paginación
            if not desde_paginacion:
                self.current_page = 1
            
            # Actualizar la paginación
            self.actualizar_paginacion()
            
        except Exception as e:
            logger.error(f"Error al filtrar estudiantes: {e}")
            import traceback
            traceback.print_exc()
    
    def buscar_estudiantes(self):
        """Buscar estudiantes según el texto ingresado"""
        self.current_page = 1
        self.filtrar_estudiantes(desde_paginacion=False)
    
    def limpiar_busqueda(self):
        """Limpiar el campo de búsqueda, resetear paginación y mostrar todos"""
        self.txt_buscar.clear()
        self.current_page = 1
        self.filtrar_estudiantes(desde_paginacion=False)
    
    def mostrar_estudiantes_en_tabla(self, estudiantes):
        """Mostrar estudiantes en la tabla con botones completos"""
        try:
            self.tabla_estudiantes.clear()

            # Configurar columnas (ajusta según tu modelo de estudiante)
            columnas = [
                "ID", "Matrícula", "CI", "Nombres", "Apellidos", 
                "Carrera", "Email", "Teléfono", "Estado", "Acciones"
            ]

            self.tabla_estudiantes.setColumnCount(len(columnas))
            self.tabla_estudiantes.setHorizontalHeaderLabels(columnas)
            self.tabla_estudiantes.setRowCount(len(estudiantes))

            # Llenar datos
            for fila, estudiante in enumerate(estudiantes):
                # Configurar altura de fila uniforme
                self.tabla_estudiantes.setRowHeight(fila, 40)

                # ID
                item_id = QTableWidgetItem(str(estudiante.id))
                item_id.setTextAlignment(Qt.AlignCenter)
                self.tabla_estudiantes.setItem(fila, 0, item_id)

                # Matrícula
                matricula = getattr(estudiante, 'matricula', '') or ''
                item_matricula = QTableWidgetItem(matricula)
                item_matricula.setTextAlignment(Qt.AlignCenter)
                self.tabla_estudiantes.setItem(fila, 1, item_matricula)

                # CI
                ci_numero = getattr(estudiante, 'ci_numero', '') or ''
                ci_expedicion = getattr(estudiante, 'ci_expedicion', '') or ''
                ci_completo = f"{ci_numero}-{ci_expedicion}" if ci_expedicion else ci_numero
                item_ci = QTableWidgetItem(ci_completo)
                self.tabla_estudiantes.setItem(fila, 2, item_ci)

                # Nombres
                item_nombres = QTableWidgetItem(str(estudiante.nombres))
                self.tabla_estudiantes.setItem(fila, 3, item_nombres)

                # Apellidos
                item_apellidos = QTableWidgetItem(str(estudiante.apellidos))
                self.tabla_estudiantes.setItem(fila, 4, item_apellidos)

                # Carrera
                carrera = getattr(estudiante, 'carrera', '') or ''
                item_carrera = QTableWidgetItem(carrera)
                self.tabla_estudiantes.setItem(fila, 5, item_carrera)

                # Email
                email = getattr(estudiante, 'email', '') or ''
                item_email = QTableWidgetItem(email)
                self.tabla_estudiantes.setItem(fila, 6, item_email)

                # Teléfono
                telefono = getattr(estudiante, 'telefono', '') or ''
                item_telefono = QTableWidgetItem(telefono)
                self.tabla_estudiantes.setItem(fila, 7, item_telefono)

                # Estado
                estado = "✅ Activo" if estudiante.activo == 1 else "❌ Inactivo"
                item_estado = QTableWidgetItem(estado)
                item_estado.setTextAlignment(Qt.AlignCenter)

                # Color según estado
                if estudiante.activo == 1:
                    item_estado.setForeground(Qt.darkGreen)
                else:
                    item_estado.setForeground(Qt.darkRed)

                self.tabla_estudiantes.setItem(fila, 8, item_estado)

                # Acciones (6 botones con tamaño fijo)
                widget_acciones = self.crear_widget_acciones(estudiante)
                self.tabla_estudiantes.setCellWidget(fila, 9, widget_acciones)

            # Ajustar columnas
            self.tabla_estudiantes.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # Nombres
            self.tabla_estudiantes.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)  # Apellidos
            self.tabla_estudiantes.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)  # Carrera

            # Columnas fijas
            self.tabla_estudiantes.setColumnWidth(0, 50)   # ID
            self.tabla_estudiantes.setColumnWidth(1, 100)  # Matrícula
            self.tabla_estudiantes.setColumnWidth(2, 100)  # CI
            self.tabla_estudiantes.setColumnWidth(6, 180)  # Email
            self.tabla_estudiantes.setColumnWidth(7, 100)  # Teléfono
            self.tabla_estudiantes.setColumnWidth(8, 100)  # Estado

            # Acciones: 6 botones de 40px + 6 espacios de 3px + stretch = ~258px
            self.tabla_estudiantes.setColumnWidth(9, 258)  # Acciones (espacio para 6 botones)

        except Exception as e:
            logger.error(f"Error al mostrar estudiantes en tabla: {e}")
            self.lbl_estado.setText("❌ Error al mostrar estudiantes")

    def crear_widget_acciones(self, estudiante):
        """Crear widget con botones de acciones completas"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)
    
        # Botón 1: Ver Detalles (solo lectura)
        btn_detalles = QPushButton("👁️")
        btn_detalles.setToolTip("Ver detalles del estudiante (solo lectura)")
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
        btn_detalles.clicked.connect(lambda: self.ver_detalles_estudiante(estudiante))
    
        # Botón 2: Editar
        btn_editar = QPushButton("✏️")
        btn_editar.setToolTip("Editar estudiante")
        btn_editar.setFixedSize(40, 28)
        btn_editar.setStyleSheet("""
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
        btn_editar.clicked.connect(lambda: self.editar_estudiante(estudiante))
    
        # Botón 3: Matricular en programa
        btn_matricular = QPushButton("🎓")
        btn_matricular.setToolTip("Matricular en programa académico")
        btn_matricular.setFixedSize(40, 28)
        btn_matricular.setStyleSheet("""
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
        btn_matricular.clicked.connect(lambda: self.matricular_estudiante(estudiante))
    
        # Botón 4: Historial de programas
        btn_programas = QPushButton("📚")
        btn_programas.setToolTip("Ver historial de programas académicos")
        btn_programas.setFixedSize(40, 28)
        btn_programas.setStyleSheet("""
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
        btn_programas.clicked.connect(lambda: self.ver_programas_academicos(estudiante))
    
        # Botón 5: Seguimiento de pagos
        btn_pagos = QPushButton("💰")
        btn_pagos.setToolTip("Seguimiento de pagos y cuotas")
        btn_pagos.setFixedSize(40, 28)
        btn_pagos.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 3px;
                border: none;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
        """)
        btn_pagos.clicked.connect(lambda: self.seguimiento_pagos(estudiante))
    
        # Botón 6: Eliminar
        btn_eliminar = QPushButton("🗑️")
        btn_eliminar.setToolTip("Eliminar estudiante")
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
        btn_eliminar.clicked.connect(lambda: self.eliminar_estudiante(estudiante))
    
        # Agregar todos los botones al layout
        layout.addWidget(btn_detalles)
        layout.addWidget(btn_editar)
        layout.addWidget(btn_matricular)
        layout.addWidget(btn_programas)
        layout.addWidget(btn_pagos)
        layout.addWidget(btn_eliminar)
        layout.addStretch()
    
        return widget
    
    # Métodos que deben existir para los botones
    def matricular_estudiante(self, estudiante):
        """Matricular estudiante en programa académico"""
        try:
            QMessageBox.information(
                self, 
                "Matricular Estudiante", 
                f"Matriculando a {estudiante.nombres} {estudiante.apellidos} en programa académico\n"
                f"(Funcionalidad por implementar)"
            )
        except Exception as e:
            logger.error(f"Error al matricular estudiante: {e}")
            QMessageBox.critical(self, "Error", f"Error al matricular estudiante: {str(e)}")
    
    def ver_programas_academicos(self, estudiante):
        """Ver historial de programas académicos del estudiante"""
        try:
            QMessageBox.information(
                self, 
                "Historial de Programas", 
                f"Mostrando historial de programas para {estudiante.nombres} {estudiante.apellidos}\n"
                f"(Funcionalidad por implementar)"
            )
        except Exception as e:
            logger.error(f"Error al ver programas académicos: {e}")
            QMessageBox.critical(self, "Error", f"Error al ver programas académicos: {str(e)}")
    
    def seguimiento_pagos(self, estudiante):
        """Seguimiento de pagos y cuotas del estudiante"""
        try:
            QMessageBox.information(
                self, 
                "Seguimiento de Pagos", 
                f"Mostrando seguimiento de pagos para {estudiante.nombres} {estudiante.apellidos}\n"
                f"(Funcionalidad por implementar)"
            )
        except Exception as e:
            logger.error(f"Error al ver seguimiento de pagos: {e}")
            QMessageBox.critical(self, "Error", f"Error al ver seguimiento de pagos: {str(e)}")
    
    def eliminar_estudiante(self, estudiante):
        """Eliminar estudiante del sistema"""
        try:
            respuesta = QMessageBox.question(
                self,
                "Confirmar Eliminación",
                f"¿Está seguro de eliminar este estudiante?\n\n"
                f"Estudiante: {estudiante.nombres} {estudiante.apellidos}\n"
                f"Matrícula: {getattr(estudiante, 'matricula', 'N/A')}\n\n"
                f"⚠️ Esta acción no se puede deshacer.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if respuesta == QMessageBox.Yes:
                # Eliminar de la base de datos
                estudiante.delete()
                
                # Actualizar tabla
                self.cargar_estudiantes(self.current_filter)
                
                QMessageBox.information(self, "✅ Éxito", "Estudiante eliminado correctamente")
                
        except Exception as e:
            logger.error(f"Error al eliminar estudiante: {e}")
            QMessageBox.critical(self, "Error", f"Error al eliminar estudiante: {str(e)}")
    
    # ============================================================================
    # MÉTODOS DE PAGINACIÓN
    # ============================================================================
    
    def actualizar_paginacion(self):
        """Actualizar controles de paginación y mostrar página actual"""
        # Calcular paginación
        total_estudiantes = len(self.estudiantes_filtrados_actuales)
        self.total_pages = max(1, (total_estudiantes + self.records_per_page - 1) // self.records_per_page)
        
        # Ajustar página actual si es necesario
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        
        # Calcular índices para la página actual
        start_idx = (self.current_page - 1) * self.records_per_page
        end_idx = min(start_idx + self.records_per_page, total_estudiantes)
        
        # Obtener estudiantes para la página actual
        self.estudiantes_paginados = self.estudiantes_filtrados_actuales[start_idx:end_idx]
        
        # Actualizar botones
        self.btn_primera.setEnabled(self.current_page > 1)
        self.btn_anterior.setEnabled(self.current_page > 1)
        self.btn_siguiente.setEnabled(self.current_page < self.total_pages)
        self.btn_ultima.setEnabled(self.current_page < self.total_pages)
        
        # Actualizar información
        self.lbl_info_pagina.setText(f"Página {self.current_page} de {self.total_pages}")
        
        # Mostrar estudiantes de la página actual
        self.mostrar_estudiantes_en_tabla(self.estudiantes_paginados)
        
        # Actualizar contador
        mostrar_texto = f"Mostrando {len(self.estudiantes_paginados)} de {total_estudiantes} registros"
        if total_estudiantes > 0:
            mostrar_texto += f" ({start_idx + 1}-{end_idx})"
        self.lbl_contador.setText(mostrar_texto)
    
    def cambiar_pagina(self, nueva_pagina):
        """Cambiar a una nueva página"""
        if 1 <= nueva_pagina <= self.total_pages and nueva_pagina != self.current_page:
            self.current_page = nueva_pagina
            self.actualizar_paginacion()
    
    # ============================================================================
    # MÉTODOS PRINCIPALES DE GESTIÓN (ESQUELETO - IMPLEMENTAR SEGÚN NECESIDAD)
    # ============================================================================
    
    def agregar_nuevo_estudiante(self):
        """Abrir diálogo para nuevo estudiante"""
        try:
            # Importar aquí para evitar importación circular
            from app.views.dialogs.estudiante_form_dialog import EstudianteFormDialog
            
            dialog = EstudianteFormDialog(
                estudiante_id=None,
                modo_lectura=False,
                parent=self
            )
            
            if dialog.exec():
                self.cargar_estudiantes(self.current_filter)
                
        except ImportError:
            QMessageBox.information(
                self, 
                "Funcionalidad no implementada", 
                "El formulario de estudiante aún no está implementado"
            )
        except Exception as e:
            logger.error(f"Error al crear estudiante: {e}")
            QMessageBox.critical(self, "Error", f"Error al crear estudiante: {str(e)}")
    
    def ver_detalles_estudiante(self, estudiante):
        """Mostrar diálogo con detalles del estudiante"""
        try:
            from app.views.dialogs.estudiante_form_dialog import EstudianteFormDialog
            
            estudiante_data = {
                'id': estudiante.id,
                'nombres': estudiante.nombres,
                'apellidos': estudiante.apellidos,
                'ci_numero': getattr(estudiante, 'ci_numero', ''),
                'ci_expedicion': getattr(estudiante, 'ci_expedicion', ''),
                'matricula': getattr(estudiante, 'matricula', ''),
                'carrera': getattr(estudiante, 'carrera', ''),
                'telefono': getattr(estudiante, 'telefono', ''),
                'email': getattr(estudiante, 'email', ''),
                'activo': getattr(estudiante, 'activo', 1)
            }
            
            dialog = EstudianteFormDialog(
                estudiante_data=estudiante_data,
                modo_lectura=True,
                parent=self
            )
            
            dialog.exec()
            
        except ImportError:
            QMessageBox.information(
                self, 
                "Funcionalidad no implementada", 
                f"Vista de detalles para estudiante ID {estudiante.id}\n"
                f"(Por implementar)"
            )
        except Exception as e:
            logger.error(f"Error al mostrar detalles: {e}")
            QMessageBox.critical(self, "Error", f"Error al mostrar detalles: {str(e)}")
    
    def editar_estudiante(self, estudiante_id):
        """Abrir diálogo para editar un estudiante"""
        try:
            from app.views.dialogs.estudiante_form_dialog import EstudianteFormDialog
            
            dialog = EstudianteFormDialog(
                estudiante_id=estudiante_id,
                modo_lectura=False,
                parent=self
            )
            
            if dialog.exec():
                self.cargar_estudiantes(self.current_filter)
        
        except ImportError:
            QMessageBox.information(
                self, 
                "Funcionalidad no implementada", 
                f"Edición para estudiante ID {estudiante_id}\n"
                f"(Por implementar)"
            )
        except Exception as e:
            logger.error(f"Error al editar estudiante: {e}")
            QMessageBox.critical(self, "Error", f"Error al editar estudiante: {str(e)}")
    
    # ============================================================================
    # MÉTODOS AUXILIARES
    # ============================================================================
    
    def actualizar_interfaz(self):
        """Actualizar la interfaz después de cambios"""
        self.cargar_estudiantes(self.current_filter)
    
    def obtener_estudiante_por_id(self, estudiante_id):
        """Obtener estudiante por ID desde los datos cargados"""
        for estudiante in self.estudiantes_data:
            if estudiante.id == estudiante_id:
                return estudiante
        return None