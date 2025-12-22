# app/views/tabs/docentes_tab.py
"""
Pestaña de gestión de docentes - Implementación completa con flujo mejorado
"""

import logging
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QLineEdit, QLabel,
    QComboBox, QFormLayout, QGroupBox, QGridLayout, QFrame
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon, QFont

from app.models.docente_model import DocenteModel

logger = logging.getLogger(__name__)

class DocentesTab(QWidget):
    """Pestaña para gestión de docentes con flujo completo edición/lectura"""
    
    # Señales para comunicación con MainWindow
    docente_seleccionado = Signal(dict)
    necesita_actualizar = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.docentes_data = []
        self.current_filter = 'todos'
        
        self.setup_ui()
        self.setup_connections()
        self.cargar_docentes()
    
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
        title_label = QLabel("👨‍🏫 Gestión de Docentes")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Botón Nuevo Docente
        self.btn_nuevo_docente = QPushButton("➕ Nuevo Docente")
        self.btn_nuevo_docente.setFixedHeight(40)
        self.btn_nuevo_docente.setStyleSheet("""
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
        self.btn_nuevo_docente.setToolTip("Agregar un nuevo docente al sistema")
        header_layout.addWidget(self.btn_nuevo_docente)
        
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
        self.combo_filtro.addItems(['Todos', 'Activos', 'Inactivos'])
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
                border: 2px solid #3498db;
            }
        """)
        filter_layout.addWidget(self.combo_filtro)
        
        # Buscador
        search_label = QLabel("Buscar:")
        search_label.setStyleSheet("font-weight: bold; color: #495057; margin-left: 20px;")
        filter_layout.addWidget(search_label)
        
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Nombre, CI o especialidad...")
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
                border: 2px solid #3498db;
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
        
        # ============ TABLA DE DOCENTES ============
        self.tabla_docentes = QTableWidget()
        self.tabla_docentes.setStyleSheet("""
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
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        
        self.tabla_docentes.setAlternatingRowColors(True)
        self.tabla_docentes.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_docentes.setSelectionMode(QTableWidget.SingleSelection)
        
        layout.addWidget(self.tabla_docentes, 1)
        
        # ============ ESTADO ============
        self.lbl_estado = QLabel("Cargando docentes...")
        self.lbl_estado.setStyleSheet("color: #7f8c8d; font-style: italic;")
        self.lbl_estado.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_estado)
    
    def setup_connections(self):
        """Conectar señales y slots"""
        # Botones
        self.btn_nuevo_docente.clicked.connect(self.agregar_nuevo_docente)
        self.btn_buscar.clicked.connect(self.buscar_docentes)
        self.btn_limpiar.clicked.connect(self.limpiar_busqueda)
        
        # Filtros
        self.combo_filtro.currentTextChanged.connect(self.filtrar_docentes)
        self.txt_buscar.returnPressed.connect(self.buscar_docentes)
    
    def cargar_docentes(self, filtro='todos'):
        """Cargar docentes desde la base de datos"""
        try:
            self.lbl_estado.setText("Cargando docentes...")
            
            # Obtener todos los docentes
            self.docentes_data = DocenteModel.get_all()
            
            # Aplicar filtro inicial
            self.current_filter = filtro
            self.filtrar_docentes()
            
            if self.docentes_data:
                self.lbl_estado.setText(f"✅ {len(self.docentes_data)} docentes cargados")
            else:
                self.lbl_estado.setText("📭 No hay docentes registrados")
                
        except Exception as e:
            logger.error(f"Error al cargar docentes: {e}")
            self.lbl_estado.setText("❌ Error al cargar docentes")
            QMessageBox.critical(self, "Error", f"Error al cargar docentes: {str(e)}")
    
    def filtrar_docentes(self):
        """Filtrar docentes según el estado seleccionado"""
        try:
            filtro = self.combo_filtro.currentText().lower()
            
            docentes_filtrados = []
            for docente in self.docentes_data:
                if filtro == 'todos':
                    docentes_filtrados.append(docente)
                elif filtro == 'activos' and docente.activo == 1:
                    docentes_filtrados.append(docente)
                elif filtro == 'inactivos' and docente.activo == 0:
                    docentes_filtrados.append(docente)
            
            self.mostrar_docentes_en_tabla(docentes_filtrados)
            
        except Exception as e:
            logger.error(f"Error al filtrar docentes: {e}")
    
    def buscar_docentes(self):
        """Buscar docentes según el texto ingresado"""
        try:
            texto = self.txt_buscar.text().strip().lower()
            
            if not texto:
                self.filtrar_docentes()
                return
            
            docentes_filtrados = []
            for docente in self.docentes_data:
                # Buscar en múltiples campos
                campos = [
                    str(docente.nombres or ''),
                    str(docente.apellidos or ''),
                    str(docente.ci_numero or ''),
                    str(getattr(docente, 'especialidad', '') or ''),
                    str(getattr(docente, 'grado_academico', '') or '')
                ]
                
                if any(texto in campo.lower() for campo in campos):
                    docentes_filtrados.append(docente)
            
            self.mostrar_docentes_en_tabla(docentes_filtrados)
            
            if docentes_filtrados:
                self.lbl_estado.setText(f"🔍 {len(docentes_filtrados)} docentes encontrados")
            else:
                self.lbl_estado.setText("🔍 No se encontraron docentes")
                
        except Exception as e:
            logger.error(f"Error al buscar docentes: {e}")
    
    def limpiar_busqueda(self):
        """Limpiar el campo de búsqueda y mostrar todos"""
        self.txt_buscar.clear()
        self.filtrar_docentes()
    
    def mostrar_docentes_en_tabla(self, docentes):
        """Mostrar docentes en la tabla"""
        try:
            self.tabla_docentes.clear()
            
            # Configurar columnas
            columnas = [
                "ID", "CI", "Nombres", "Apellidos", "Especialidad",
                "Grado Académico", "Email", "Teléfono", "CV", "Estado", "Acciones"
            ]
            
            self.tabla_docentes.setColumnCount(len(columnas))
            self.tabla_docentes.setHorizontalHeaderLabels(columnas)
            self.tabla_docentes.setRowCount(len(docentes))
            
            # Llenar datos
            for fila, docente in enumerate(docentes):
                # ID
                item_id = QTableWidgetItem(str(docente.id))
                item_id.setTextAlignment(Qt.AlignCenter)
                self.tabla_docentes.setItem(fila, 0, item_id)
                
                # CI
                ci_completo = f"{docente.ci_numero}-{docente.ci_expedicion}"
                item_ci = QTableWidgetItem(ci_completo)
                item_ci.setTextAlignment(Qt.AlignCenter)
                self.tabla_docentes.setItem(fila, 1, item_ci)
                
                # Nombres
                item_nombres = QTableWidgetItem(str(docente.nombres))
                self.tabla_docentes.setItem(fila, 2, item_nombres)
                
                # Apellidos
                item_apellidos = QTableWidgetItem(str(docente.apellidos))
                self.tabla_docentes.setItem(fila, 3, item_apellidos)
                
                # Especialidad
                especialidad = getattr(docente, 'especialidad', '') or ''
                item_especialidad = QTableWidgetItem(especialidad)
                self.tabla_docentes.setItem(fila, 4, item_especialidad)
                
                # Grado Académico
                grado = getattr(docente, 'grado_academico', '') or ''
                item_grado = QTableWidgetItem(grado)
                self.tabla_docentes.setItem(fila, 5, item_grado)
                
                # Email
                email = getattr(docente, 'email', '') or ''
                item_email = QTableWidgetItem(email)
                self.tabla_docentes.setItem(fila, 6, item_email)
                
                # Teléfono
                telefono = getattr(docente, 'telefono', '') or ''
                item_telefono = QTableWidgetItem(telefono)
                self.tabla_docentes.setItem(fila, 7, item_telefono)
                
                # CV
                tiene_cv = "✅" if getattr(docente, 'curriculum_path', None) else "❌"
                item_cv = QTableWidgetItem(tiene_cv)
                item_cv.setTextAlignment(Qt.AlignCenter)
                self.tabla_docentes.setItem(fila, 8, item_cv)
                
                # Estado
                estado = "✅ Activo" if docente.activo == 1 else "❌ Inactivo"
                item_estado = QTableWidgetItem(estado)
                item_estado.setTextAlignment(Qt.AlignCenter)
                
                # Color según estado
                if docente.activo == 1:
                    item_estado.setForeground(Qt.darkGreen)
                else:
                    item_estado.setForeground(Qt.darkRed)
                    
                self.tabla_docentes.setItem(fila, 9, item_estado)
                
                # Acciones (botones)
                widget_acciones = QWidget()
                layout_acciones = QHBoxLayout(widget_acciones)
                layout_acciones.setContentsMargins(5, 2, 5, 2)
                layout_acciones.setSpacing(5)
                
                # Botón Ver Detalles
                btn_detalles = QPushButton("👁️ Ver")
                btn_detalles.setFixedHeight(28)
                btn_detalles.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-size: 11px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                    QPushButton:pressed {
                        background-color: #1f618d;
                    }
                """)
                btn_detalles.clicked.connect(lambda checked, d=docente: self.ver_detalles_docente(d))
                
                # Botón Editar
                btn_editar = QPushButton("✏️ Editar")
                btn_editar.setFixedHeight(28)
                btn_editar.setStyleSheet("""
                    QPushButton {
                        background-color: #f39c12;
                        color: white;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-size: 11px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #e67e22;
                    }
                    QPushButton:pressed {
                        background-color: #d35400;
                    }
                """)
                btn_editar.clicked.connect(lambda checked, d=docente: self.editar_docente(d.id))
                
                layout_acciones.addWidget(btn_detalles)
                layout_acciones.addWidget(btn_editar)
                layout_acciones.addStretch()
                
                self.tabla_docentes.setCellWidget(fila, 10, widget_acciones)
            
            # Ajustar columnas
            self.tabla_docentes.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # Nombres
            self.tabla_docentes.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # Apellidos
            self.tabla_docentes.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)  # Especialidad
            
            # Columnas fijas
            self.tabla_docentes.setColumnWidth(0, 50)   # ID
            self.tabla_docentes.setColumnWidth(1, 100)  # CI
            self.tabla_docentes.setColumnWidth(5, 120)  # Grado
            self.tabla_docentes.setColumnWidth(6, 180)  # Email
            self.tabla_docentes.setColumnWidth(7, 100)  # Teléfono
            self.tabla_docentes.setColumnWidth(8, 50)   # CV
            self.tabla_docentes.setColumnWidth(9, 100)  # Estado
            self.tabla_docentes.setColumnWidth(10, 150) # Acciones
            
        except Exception as e:
            logger.error(f"Error al mostrar docentes en tabla: {e}")
            self.lbl_estado.setText("❌ Error al mostrar docentes")
    
    # ============================================================================
    # MÉTODOS PRINCIPALES DE GESTIÓN
    # ============================================================================
    
    def agregar_nuevo_docente(self):
        """Abrir diálogo para nuevo docente"""
        try:
            from app.views.dialogs.docente_form_dialog import DocenteFormDialog
            
            # Abrir diálogo para nuevo docente
            dialog = DocenteFormDialog(
                docente_id=None,
                modo_lectura=False,
                parent=self
            )
            
            # Conectar señal para mostrar después de guardar
            dialog.docente_editar.connect(
                lambda data: self.mostrar_docente_en_modo_lectura(data['id'])
            )
            
            if dialog.exec():
                print(f"DEBUG: Nuevo docente creado")
                self.cargar_docentes(self.current_filter)
                
        except Exception as e:
            logger.error(f"Error al crear docente: {e}")
            QMessageBox.critical(self, "Error", f"Error al crear docente: {str(e)}")
    
    def ver_detalles_docente(self, docente):
        """Mostrar diálogo con detalles del docente (solo lectura)"""
        try:
            print(f"DEBUG ver_detalles_docente: Abriendo diálogo para docente ID {docente.id}")
            
            from app.views.dialogs.docente_form_dialog import DocenteFormDialog
            
            # Crear diccionario con datos del docente
            docente_data = {
                'id': docente.id,
                'ci_numero': docente.ci_numero,
                'ci_expedicion': docente.ci_expedicion,
                'nombres': docente.nombres,
                'apellidos': docente.apellidos,
                'especialidad': getattr(docente, 'especialidad', ''),
                'grado_academico': getattr(docente, 'grado_academico', ''),
                'telefono': getattr(docente, 'telefono', ''),
                'email': getattr(docente, 'email', ''),
                'curriculum_path': getattr(docente, 'curriculum_path', None),
                'activo': getattr(docente, 'activo', 1)
            }
            
            # Abrir diálogo en modo lectura
            dialog = DocenteFormDialog(
                docente_data=docente_data,
                modo_lectura=True,
                parent=self
            )
            
            # Conectar señales para acciones desde modo lectura
            dialog.docente_editar.connect(
                lambda data: self.editar_docente(data['id'])
            )
            
            dialog.docente_inscribir.connect(self.on_inscribir_desde_detalles)
            dialog.docente_borrar.connect(self.on_borrar_desde_detalles)
            
            dialog.exec()
            
        except Exception as e:
            print(f"ERROR en ver_detalles_docente: {e}")
            logger.error(f"Error en ver_detalles_docente: {e}")
            QMessageBox.critical(self, "Error", f"Error al mostrar detalles: {str(e)}")
    
    def editar_docente(self, docente_id):
        """Abrir diálogo para editar un docente"""
        try:
            print(f"DEBUG editar_docente: Abriendo diálogo para ID {docente_id}")
            
            from app.views.dialogs.docente_form_dialog import DocenteFormDialog
            
            # Abrir diálogo en modo edición
            dialog = DocenteFormDialog(
                docente_id=docente_id,
                modo_lectura=False,
                parent=self
            )
            
            # Conectar señal para mostrar después de guardar
            dialog.docente_editar.connect(
                lambda data: self.mostrar_docente_en_modo_lectura(data['id'])
            )
            
            if dialog.exec():
                print(f"DEBUG editar_docente - Diálogo cerrado")
                self.cargar_docentes(self.current_filter)
        
        except Exception as e:
            logger.error(f"Error al editar docente: {e}")
            QMessageBox.critical(self, "Error", f"Error al editar docente: {str(e)}")
    
    def mostrar_docente_en_modo_lectura(self, docente_id):
        """Mostrar docente en modo lectura después de guardar"""
        try:
            print(f"DEBUG mostrar_docente_en_modo_lectura: ID {docente_id}")
            
            from app.models.docente_model import DocenteModel
            docente = DocenteModel.find_by_id(docente_id)
            
            if docente:
                self.ver_detalles_docente(docente)
            else:
                print(f"ERROR: Docente {docente_id} no encontrado")
                
        except Exception as e:
            print(f"ERROR mostrando docente en modo lectura: {e}")
            logger.error(f"Error mostrando docente en modo lectura: {e}")
    
    # ============================================================================
    # MANEJADORES DE SEÑALES DESDE DIÁLOGO
    # ============================================================================
    
    def on_inscribir_desde_detalles(self, datos_docente):
        """Manejador para inscribir docente desde modo lectura"""
        try:
            docente_id = datos_docente.get('id')
            if docente_id:
                print(f"DEBUG: Asignando cursos a docente ID {docente_id}")
                # Aquí puedes implementar la lógica para asignar cursos
                # Por ahora solo mostramos un mensaje
                QMessageBox.information(
                    self, 
                    "Asignar Cursos", 
                    f"Funcionalidad para asignar cursos al docente {docente_id}\n"
                    f"(Por implementar)"
                )
        except Exception as e:
            logger.error(f"Error al inscribir desde detalles: {e}")
    
    def on_borrar_desde_detalles(self, datos_docente):
        """Manejador para borrar docente desde modo lectura"""
        try:
            docente_id = datos_docente.get('id')
            if docente_id:
                respuesta = QMessageBox.question(
                    self,
                    "Confirmar Eliminación",
                    f"¿Está seguro de eliminar este docente?\n\n"
                    f"Esta acción eliminará permanentemente al docente del sistema.\n"
                    f"ID: {docente_id}",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if respuesta == QMessageBox.Yes:
                    print(f"DEBUG: Eliminando docente ID {docente_id}")
                    
                    # Buscar y eliminar el docente
                    docente = DocenteModel.find_by_id(docente_id)
                    if docente:
                        # Eliminar archivo CV si existe
                        if hasattr(docente, 'curriculum_path') and docente.curriculum_path:
                            try:
                                cv_path = Path(docente.curriculum_path)
                                if cv_path.exists():
                                    cv_path.unlink()
                            except Exception as e:
                                print(f"Advertencia: No se pudo eliminar CV: {e}")
                        
                        # Eliminar de la base de datos
                        docente.delete()
                        
                        # Actualizar tabla
                        self.cargar_docentes(self.current_filter)
                        
                        QMessageBox.information(self, "✅ Éxito", "Docente eliminado correctamente")
                    else:
                        QMessageBox.warning(self, "Error", "Docente no encontrado")
                        
        except Exception as e:
            logger.error(f"Error al borrar desde detalles: {e}")
            QMessageBox.critical(self, "Error", f"Error al eliminar docente: {str(e)}")
    
    # ============================================================================
    # MÉTODOS AUXILIARES
    # ============================================================================
    
    def actualizar_interfaz(self):
        """Actualizar la interfaz después de cambios"""
        self.cargar_docentes(self.current_filter)
    
    def obtener_docente_por_id(self, docente_id):
        """Obtener docente por ID desde los datos cargados"""
        for docente in self.docentes_data:
            if docente.id == docente_id:
                return docente
        return None