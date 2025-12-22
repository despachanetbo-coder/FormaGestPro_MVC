# app/views/tabs/docentes_tab.py
"""
Pestaña de Docentes - Versión completa similar a estudiantes_tab.py
"""
import logging
import os
import sys
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QProgressDialog,
    QToolButton, QFrame, QSizePolicy, QSpacerItem, QTextEdit, 
    QDialog, QFormLayout, QDateEdit, QDoubleSpinBox, QCheckBox,
    QFileDialog
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QSize
from PySide6.QtGui import QColor, QFont, QIcon, QDesktopServices
from PySide6.QtCore import QUrl

# Importar modelos
from app.models.docente_model import DocenteModel
from app.models.gasto_operativo_model import GastoOperativoModel

# Importar diálogos
from app.views.dialogs.docente_form_dialog import DocenteFormDialog, DocenteInfoDialog

logger = logging.getLogger(__name__)

# Agregar el directorio raíz al path de Python
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

###########################
# DIÁLOGOS DE DOCENTES #
###########################
class GastoOperativoDialog(QDialog):
    """Diálogo para registrar/ver gastos operativos - Doble uso"""
    
    gasto_guardado = Signal(dict)
    constancia_emitida = Signal(dict)
    
    def __init__(self, datos_predefinidos=None, modo_lectura=False, parent=None):
        super().__init__(parent)
        
        self.datos_predefinidos = datos_predefinidos or {}
        self.modo_lectura = modo_lectura
        self.es_pago_honorarios = 'descripcion' in self.datos_predefinidos
        
        self.setup_ui()
        self.setup_connections()
        
        if self.datos_predefinidos:
            self.cargar_datos_predefinidos()
        
        if self.modo_lectura:
            self.set_readonly_mode(True)
            self.configurar_botones_modo_lectura()
    
    def setup_ui(self):
        """Configurar interfaz del diálogo de gastos"""
        if self.modo_lectura:
            self.setWindowTitle("📄 Constancia de Egreso")
        elif self.es_pago_honorarios:
            self.setWindowTitle("💰 Pago de Honorarios")
        else:
            self.setWindowTitle("📝 Registrar Gasto Operativo")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # ============ INFORMACIÓN DEL GASTO ============
        group_gasto = QGroupBox("📋 Información del Gasto" if not self.modo_lectura else "📋 Detalles del Egreso")
        form_gasto = QGridLayout()
        form_gasto.setSpacing(10)
        
        # Fila 0: Fecha
        form_gasto.addWidget(QLabel("Fecha:*"), 0, 0)
        self.date_fecha = QDateEdit()
        self.date_fecha.setDate(datetime.now().date())
        self.date_fecha.setCalendarPopup(True)
        form_gasto.addWidget(self.date_fecha, 0, 1)
        
        # Fila 0: Monto
        form_gasto.addWidget(QLabel("Monto (Bs.):*"), 0, 2)
        self.spin_monto = QDoubleSpinBox()
        self.spin_monto.setRange(0, 100000)
        self.spin_monto.setDecimals(2)
        self.spin_monto.setPrefix("Bs. ")
        form_gasto.addWidget(self.spin_monto, 0, 3)
        
        # Fila 1: Categoría
        form_gasto.addWidget(QLabel("Categoría:*"), 1, 0)
        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems(GastoOperativoModel.CATEGORIAS)
        form_gasto.addWidget(self.combo_categoria, 1, 1)
        
        # Fila 1: Subcategoría
        form_gasto.addWidget(QLabel("Subcategoría:"), 1, 2)
        self.combo_subcategoria = QComboBox()
        form_gasto.addWidget(self.combo_subcategoria, 1, 3)
        
        # Conectar cambio de categoría para actualizar subcategorías
        self.combo_categoria.currentTextChanged.connect(self.actualizar_subcategorias)
        
        # Fila 2: Descripción
        form_gasto.addWidget(QLabel("Descripción:*"), 2, 0)
        self.txt_descripcion = QTextEdit()
        self.txt_descripcion.setMaximumHeight(60)
        form_gasto.addWidget(self.txt_descripcion, 2, 1, 1, 3)
        
        # Fila 3: Proveedor
        form_gasto.addWidget(QLabel("Proveedor:"), 3, 0)
        self.txt_proveedor = QLineEdit()
        form_gasto.addWidget(self.txt_proveedor, 3, 1)
        
        # Fila 3: N° Factura
        form_gasto.addWidget(QLabel("N° Factura:"), 3, 2)
        self.txt_nro_factura = QLineEdit()
        form_gasto.addWidget(self.txt_nro_factura, 3, 3)
        
        # Fila 4: Forma de Pago
        form_gasto.addWidget(QLabel("Forma de Pago:*"), 4, 0)
        self.combo_forma_pago = QComboBox()
        self.combo_forma_pago.addItems(GastoOperativoModel.FORMAS_PAGO)
        form_gasto.addWidget(self.combo_forma_pago, 4, 1)
        
        # Fila 4: N° Comprobante
        form_gasto.addWidget(QLabel("N° Comprobante:"), 4, 2)
        self.txt_comprobante = QLineEdit()
        form_gasto.addWidget(self.txt_comprobante, 4, 3)
        
        group_gasto.setLayout(form_gasto)
        layout.addWidget(group_gasto)
        
        # ============ BOTONES ============
        if not self.modo_lectura:
            # Botones para modo registro/edición
            hbox_botones = QHBoxLayout()
            
            self.btn_guardar = QPushButton("💾 Registrar Egreso" if not self.es_pago_honorarios else "💰 Registrar Pago")
            self.btn_guardar.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    padding: 10px 30px;
                    font-weight: bold;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #219653;
                }
            """)
            self.btn_guardar.clicked.connect(self.validar_y_guardar)
            
            self.btn_cancelar = QPushButton("❌ Salir")
            self.btn_cancelar.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    padding: 10px 30px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            self.btn_cancelar.clicked.connect(self.reject)
            
            hbox_botones.addStretch()
            hbox_botones.addWidget(self.btn_guardar)
            hbox_botones.addWidget(self.btn_cancelar)
            layout.addLayout(hbox_botones)
        
        # Actualizar subcategorías iniciales
        self.actualizar_subcategorias(self.combo_categoria.currentText())
    
    def configurar_botones_modo_lectura(self):
        """Configurar botones especiales para modo lectura"""
        # Obtener el layout principal
        main_layout = self.layout()
        
        # Crear layout de botones
        button_layout = QHBoxLayout()
        
        # Botón Emitir Constancia
        self.btn_emitir_constancia = QPushButton("📄 Emitir Constancia de Egreso")
        self.btn_emitir_constancia.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #2980b9;
                border: 2px solid #1f618d;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
        """)
        self.btn_emitir_constancia.setToolTip("Generar e imprimir constancia de egreso")
        
        # Botón Salir
        self.btn_salir = QPushButton("✖️ Salir")
        self.btn_salir.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                padding: 10px 30px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #95a5a6;
                border: 2px solid #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #7f8c8d;
            }
        """)
        self.btn_salir.setToolTip("Cerrar esta ventana")
        
        # Agregar botones al layout
        button_layout.addStretch()
        button_layout.addWidget(self.btn_emitir_constancia)
        button_layout.addWidget(self.btn_salir)
        
        # Agregar el layout de botones al layout principal
        main_layout.addLayout(button_layout)
    
    def set_readonly_mode(self, readonly=True):
        """Establecer todos los campos en modo solo lectura"""
        widgets = [
            self.date_fecha, self.spin_monto, self.combo_categoria,
            self.combo_subcategoria, self.txt_descripcion, self.txt_proveedor,
            self.txt_nro_factura, self.combo_forma_pago, self.txt_comprobante
        ]
        
        for widget in widgets:
            if hasattr(widget, 'setReadOnly'):
                widget.setReadOnly(readonly)
            if hasattr(widget, 'setEnabled'):
                widget.setEnabled(not readonly)
        
        # Estilos para modo lectura
        if readonly:
            style = """
                QLineEdit:read-only, QComboBox:disabled, QDateEdit:read-only, 
                QDoubleSpinBox:disabled, QTextEdit:read-only {
                    background-color: #f5f5f5;
                    color: #666666;
                    border: 1px solid #dddddd;
                }
            """
            for widget in widgets:
                widget.setStyleSheet(style)
    
    def setup_connections(self):
        """Conectar señales"""
        if self.modo_lectura:
            self.btn_emitir_constancia.clicked.connect(self.on_emitir_constancia_clicked)
            self.btn_salir.clicked.connect(self.reject)
    
    def actualizar_subcategorias(self, categoria):
        """Actualizar las subcategorías según la categoría seleccionada"""
        self.combo_subcategoria.clear()
        self.combo_subcategoria.addItem("")  # Opción vacía
        
        if categoria in GastoOperativoModel.SUBCATEGORIAS:
            self.combo_subcategoria.addItems(GastoOperativoModel.SUBCATEGORIAS[categoria])
    
    def cargar_datos_predefinidos(self):
        """Cargar datos predefinidos (para pago de honorarios)"""
        if 'descripcion' in self.datos_predefinidos:
            self.txt_descripcion.setPlainText(self.datos_predefinidos['descripcion'])
        
        if 'monto' in self.datos_predefinidos:
            self.spin_monto.setValue(self.datos_predefinidos['monto'])
        
        if 'categoria' in self.datos_predefinidos:
            index = self.combo_categoria.findText(self.datos_predefinidos['categoria'])
            if index >= 0:
                self.combo_categoria.setCurrentIndex(index)
    
    def cargar_datos_docente(self, docente_data):
        """Carga los datos del docente en los campos del formulario"""
        try:
            # Información personal
            self.txt_ci_numero.setText(docente_data.get('ci_numero', ''))
            self.combo_expedicion.setCurrentText(docente_data.get('expedicion', 'BE'))
            self.txt_nombres.setText(docente_data.get('nombres', ''))
            self.txt_apellidos.setText(docente_data.get('apellidos', ''))

            # Fecha de nacimiento
            fecha_nac = docente_data.get('fecha_nacimiento')
            if fecha_nac:
                self.date_fecha_nacimiento.setDate(fecha_nac)

            # Grado académico
            self.combo_grado_academico.setCurrentText(docente_data.get('grado_academico', ''))

            # Información de contacto
            self.txt_telefono.setText(docente_data.get('telefono', ''))
            self.txt_email.setText(docente_data.get('email', ''))

            # Información profesional
            self.txt_especialidad.setText(docente_data.get('especialidad', ''))
            self.spin_honorario_hora.setValue(docente_data.get('honorario_hora', 50.0))

            # CV
            ruta_cv = docente_data.get('ruta_cv')
            if ruta_cv and os.path.exists(ruta_cv):
                self.ruta_cv = ruta_cv
                nombre_archivo = os.path.basename(ruta_cv)

                # Formatear la información para mostrar
                info_texto = nombre_archivo
                if len(info_texto) > 30:
                    info_texto = info_texto[:27] + "..."

                self.lbl_cv_info.setText(info_texto)
                self.btn_ver_cv.setEnabled(True)

            # Estado
            self.check_activo.setChecked(docente_data.get('activo', True))

        except Exception as e:
            print(f"Error al cargar datos del docente: {e}")

    def obtener_datos_formulario(self):
        """Obtener y validar datos del formulario"""
        errores = []
        
        # Validar monto
        monto = self.spin_monto.value()
        if monto <= 0:
            errores.append("El monto debe ser mayor a 0")
        
        # Validar categoría
        categoria = self.combo_categoria.currentText()
        if not categoria:
            errores.append("La categoría es obligatoria")
        
        # Validar descripción
        descripcion = self.txt_descripcion.toPlainText().strip()
        if not descripcion:
            errores.append("La descripción es obligatoria")
        
        # Validar forma de pago
        forma_pago = self.combo_forma_pago.currentText()
        if not forma_pago:
            errores.append("La forma de pago es obligatoria")
        
        return errores, {
            'fecha': self.date_fecha.date().toString('yyyy-MM-dd'),
            'monto': monto,
            'categoria': categoria,
            'subcategoria': self.combo_subcategoria.currentText() or None,
            'descripcion': descripcion,
            'proveedor': self.txt_proveedor.text().strip() or None,
            'nro_factura': self.txt_nro_factura.text().strip() or None,
            'forma_pago': forma_pago,
            'comprobante_nro': self.txt_comprobante.text().strip() or None
        }
    
    def validar_y_guardar(self):
        """Validar y guardar los datos del gasto"""
        errores, datos = self.obtener_datos_formulario()
        
        if errores:
            QMessageBox.warning(self, "Validación", "\n".join(errores))
            return
        
        try:
            # Crear y guardar gasto
            gasto = GastoOperativoModel(**datos)
            gasto_id = gasto.save()
            
            # Mostrar mensaje de éxito
            if self.es_pago_honorarios:
                mensaje = f"Pago de honorarios registrado exitosamente\nID: {gasto_id}"
            else:
                mensaje = f"Gasto operativo registrado exitosamente\nID: {gasto_id}"
            
            QMessageBox.information(self, "✅ Éxito", mensaje)
            
            # Emitir señal con datos del gasto guardado
            datos['id'] = gasto_id
            self.gasto_guardado.emit(datos)
            
            # Cerrar diálogo actual y abrir en modo lectura
            self.close()
            
            # Abrir diálogo en modo lectura
            dialog_lectura = GastoOperativoDialog(
                datos_predefinidos=datos,
                modo_lectura=True,
                parent=self.parent()
            )
            dialog_lectura.constancia_emitida.connect(self.constancia_emitida)
            dialog_lectura.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar gasto: {str(e)}")
            logger.error(f"Error al guardar gasto operativo: {e}")
    
    def on_emitir_constancia_clicked(self):
        """Manejador para botón Emitir Constancia"""
        try:
            # Obtener datos del formulario
            datos = {
                'fecha': self.date_fecha.date().toString('dd/MM/yyyy'),
                'monto': self.spin_monto.value(),
                'descripcion': self.txt_descripcion.toPlainText(),
                'categoria': self.combo_categoria.currentText(),
                'forma_pago': self.combo_forma_pago.currentText(),
                'comprobante': self.txt_comprobante.text() or 'N/A'
            }
            
            # Emitir señal
            self.constancia_emitida.emit(datos)
            
            QMessageBox.information(
                self, 
                "📄 Constancia Generada",
                "Constancia de egreso generada exitosamente.\n\n"
                "Se ha guardado en la carpeta de documentos."
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al emitir constancia: {str(e)}")


#################################
# PESTAÑA PRINCIPAL DOCENTES #
#################################
class DocentesTab(QWidget):
    """Pestaña principal de gestión de docentes - Versión similar a estudiantes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configuración inicial
        self.current_page = 1
        self.records_per_page = 25
        self.total_records = 0
        self.total_pages = 1
        self.current_filter = None
        self.docentes_cache = []
        
        self.setup_ui()
        self.setup_connections()
        self.cargar_docentes_inicial()
    
    def setup_ui(self):
        """Configurar interfaz - Versión similar a estudiantes"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # ==================== SECCIÓN DE BÚSQUEDA ====================
        search_group = QGroupBox("🔍 Buscar Docentes")
        search_group.setStyleSheet("""
            QGroupBox {
               color: #2c3e50;
            }
        """)
        search_layout = QGridLayout()
        
        # Búsqueda por CI
        label_ci = QLabel("Buscar por CI:")
        label_ci.setStyleSheet("color: black; font-weight: bold;")
        search_layout.addWidget(label_ci, 0, 0)
        self.txt_buscar_ci = QLineEdit()
        self.txt_buscar_ci.setPlaceholderText("Ingrese número de CI")
        self.txt_buscar_ci.setStyleSheet("color: #212121; background-color: #FFFFFF;")
        search_layout.addWidget(self.txt_buscar_ci, 0, 1)
        
        self.combo_expedicion = QComboBox()
        self.combo_expedicion.addItems(["Todas", "BE", "CH", "CB", "LP", "OR", "PD", "PT", "SC", "TJ", "EX"])
        search_layout.addWidget(self.combo_expedicion, 0, 2)
        
        self.btn_buscar_ci = QPushButton("🔍 Buscar por CI")
        self.btn_buscar_ci.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        search_layout.addWidget(self.btn_buscar_ci, 0, 3)
        
        # Búsqueda por nombre
        label_nombre = QLabel("Buscar por Nombre o Apellido:")
        label_nombre.setStyleSheet("color: black; font-weight: bold;")
        search_layout.addWidget(label_nombre, 1, 0)
        self.txt_buscar_nombre = QLineEdit()
        self.txt_buscar_nombre.setStyleSheet("color: #212121; background-color: #FFFFFF;")
        self.txt_buscar_nombre.setPlaceholderText("Ingrese nombre o apellido")
        search_layout.addWidget(self.txt_buscar_nombre, 1, 1, 1, 2)
        
        self.btn_buscar_nombre = QPushButton("👤 Buscar por nombre")
        self.btn_buscar_nombre.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        search_layout.addWidget(self.btn_buscar_nombre, 1, 3)
        
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)
        
        # ==================== BOTONES DE ACCIÓN ====================
        action_layout = QHBoxLayout()
        
        self.btn_nuevo = QPushButton("➕ Nuevo Docente")
        self.btn_nuevo.setIcon(QIcon(":/icons/add.png") if hasattr(QIcon, "fromTheme") else QIcon())
        self.btn_nuevo.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        
        self.btn_mostrar_todos = QPushButton("📋 Mostrar Todos")
        self.btn_mostrar_todos.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
        """)
        
        action_layout.addWidget(self.btn_nuevo)
        action_layout.addWidget(self.btn_mostrar_todos)
        action_layout.addStretch()
        
        main_layout.addLayout(action_layout)
        
        # ==================== TABLA DE DOCENTES ====================
        self.table_docentes = QTableWidget()
        self.table_docentes.setColumnCount(5)  # 5 columnas
        self.table_docentes.setHorizontalHeaderLabels([
            "CI", "Nombre Completo", "Especialidad", "Estado", "Acciones"
        ])
        
        # Configurar tabla
        header = self.table_docentes.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # CI
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Nombre
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Especialidad
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Estado
        header.setSectionResizeMode(4, QHeaderView.Fixed)             # Acciones
        self.table_docentes.setColumnWidth(4, 200)
        
        # Estilo de la tabla
        self.table_docentes.setAlternatingRowColors(True)
        self.table_docentes.setStyleSheet("""
            QTableWidget {
                background-color: #fbfbfb;
                color: #212121;
                border-color: #E0E0E0;
                alternate-background-color: #F8F8F8;
                selection-background-color: #9b59b6;
                selection-color: #FFFFFF;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #9b59b6;
                color: white;
            }
        """)
        
        main_layout.addWidget(self.table_docentes)
        
        # ==================== PAGINACIÓN ====================
        pagination_layout = QHBoxLayout()
        
        # Controles de registros por página
        pagination_layout.addWidget(QLabel("Mostrar:"))
        self.combo_registros_pagina = QComboBox()
        self.combo_registros_pagina.addItems(["10", "25", "50", "100", "Todos"])
        self.combo_registros_pagina.setCurrentText("25")
        pagination_layout.addWidget(self.combo_registros_pagina)
        
        pagination_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Botones de paginación
        self.btn_primera = QPushButton("⏮️ Primera")
        self.btn_anterior = QPushButton("◀️ Anterior")
        self.btn_siguiente = QPushButton("Siguiente ▶️")
        self.btn_ultima = QPushButton("Última ⏭️")
        
        for btn in [self.btn_primera, self.btn_anterior, self.btn_siguiente, self.btn_ultima]:
            btn.setFixedSize(100, 30)
            pagination_layout.addWidget(btn)
        
        # Etiquetas de paginación
        self.lbl_pagina_info = QLabel("Página 0 de 0")
        self.lbl_contador = QLabel("Mostrando 0-0 de 0 docentes")
        pagination_layout.addWidget(self.lbl_pagina_info)
        pagination_layout.addWidget(self.lbl_contador)
        
        main_layout.addLayout(pagination_layout)
        
        # ==================== BARRA DE ESTADO ====================
        self.status_bar = QLabel("Sistema de gestión de docentes listo")
        self.status_bar.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")
        main_layout.addWidget(self.status_bar)
    
    def setup_connections(self):
        """Conectar todas las señales"""
        # Botones de búsqueda
        self.btn_buscar_ci.clicked.connect(self.buscar_por_ci)
        self.btn_buscar_nombre.clicked.connect(self.buscar_por_nombre)
        self.btn_mostrar_todos.clicked.connect(self.mostrar_todos)
        self.btn_nuevo.clicked.connect(self.nuevo_docente)
        
        # Buscar con Enter
        self.txt_buscar_ci.returnPressed.connect(self.buscar_por_ci)
        self.txt_buscar_nombre.returnPressed.connect(self.buscar_por_nombre)
        
        # Paginación
        self.btn_primera.clicked.connect(lambda: self.cambiar_pagina(1))
        self.btn_anterior.clicked.connect(self.pagina_anterior)
        self.btn_siguiente.clicked.connect(self.pagina_siguiente)
        self.btn_ultima.clicked.connect(self.ultima_pagina)
        self.combo_registros_pagina.currentTextChanged.connect(self.cambiar_registros_pagina)
        
        # Doble click en tabla para abrir detalles
        self.table_docentes.doubleClicked.connect(self.on_doble_click_tabla)
    
    # ==================== MÉTODOS DE CARGA ====================
    
    def cargar_docentes_inicial(self):
        """Cargar docentes al iniciar"""
        QTimer.singleShot(100, self.mostrar_todos)
    
    def cargar_docentes(self, filtro=None):
        """Cargar docentes con paginación"""
        try:
            # Limpiar tabla
            self.table_docentes.setRowCount(0)
            
            # Obtener docentes según filtro
            docentes = []
            
            if filtro is None:
                # Mostrar todos los activos
                docentes = DocenteModel.buscar_activos()
            elif 'ci_numero' in filtro:
                # Buscar por CI
                expedicion = filtro.get('ci_expedicion', 'Todas')
                if expedicion != 'Todas':
                    # Buscar por CI específico
                    docente = DocenteModel.buscar_por_ci(
                        filtro['ci_numero'], 
                        expedicion
                    )
                    if docente:
                        docentes = [docente]
                else:
                    # Buscar solo por número de CI
                    todos = DocenteModel.buscar_activos()
                    docentes = [
                        d for d in todos 
                        if filtro['ci_numero'] in d.ci_numero
                    ]
            elif 'nombre' in filtro:
                # Buscar por nombre - Necesitaríamos implementar este método
                # Por ahora, usar búsqueda manual
                todos = DocenteModel.buscar_activos()
                texto_busqueda = filtro['nombre'].lower()
                docentes = [
                    d for d in todos 
                    if texto_busqueda in d.nombres.lower() or 
                       texto_busqueda in d.apellidos.lower() or
                       texto_busqueda in d.nombre_completo.lower()
                ]
            
            self.docentes_cache = docentes
            self.total_records = len(docentes)
            
            if not docentes:
                # Mostrar mensaje de "sin datos"
                self.table_docentes.setRowCount(1)
                item = QTableWidgetItem("No se encontraron docentes")
                item.setTextAlignment(Qt.AlignCenter)
                item.setForeground(QColor("#7f8c8d"))
                self.table_docentes.setItem(0, 0, item)
                self.table_docentes.setSpan(0, 0, 1, 5)
            else:
                # Llenar tabla
                for i, docente in enumerate(docentes):
                    self.table_docentes.insertRow(i)
                    self.table_docentes.setRowHeight(i, 40)
                    
                    # CI
                    self.table_docentes.setItem(i, 0, QTableWidgetItem(
                        f"{docente.ci_numero}-{docente.ci_expedicion}"))
                    
                    # Nombre completo con grado
                    nombre_completo = docente.nombre_completo
                    if docente.max_grado_academico:
                        nombre_completo = f"{docente.max_grado_academico} {nombre_completo}"
                    self.table_docentes.setItem(i, 1, QTableWidgetItem(nombre_completo))
                    
                    # Especialidad
                    self.table_docentes.setItem(i, 2, QTableWidgetItem(docente.especialidad or ""))
                    
                    # Estado
                    estado = QTableWidgetItem("✅ Activo" if docente.activo else "❌ Inactivo")
                    estado.setForeground(QColor("#27ae60") if docente.activo else QColor("#e74c3c"))
                    estado.setTextAlignment(Qt.AlignCenter)
                    self.table_docentes.setItem(i, 3, estado)
                    
                    # Acciones
                    acciones_widget = self.crear_widget_acciones(docente)
                    self.table_docentes.setCellWidget(i, 4, acciones_widget)
            
            # Actualizar controles
            self.actualizar_controles_paginacion()
            self.actualizar_contador()
            
            self.status_bar.setText(f"Cargados {len(docentes)} docentes")
            
        except Exception as e:
            self.status_bar.setText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error cargando docentes: {str(e)}")
            logger.error(f"Error en cargar_docentes: {e}")
    
    def crear_widget_acciones(self, docente):
        """Crear widget con botones de acciones"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        # Botón 1: Ver Detalles (solo lectura)
        btn_detalles = QPushButton("👁️")
        btn_detalles.setIconSize(QSize(28, 28))
        btn_detalles.setToolTip("Ver detalles del docente (solo lectura)")
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
        btn_detalles.clicked.connect(lambda: self.ver_detalles_docente(docente))

        # Botón 2: Editar
        btn_editar = QPushButton("✏️")
        btn_editar.setToolTip("Editar docente")
        btn_editar.setFixedSize(40, 28)
        btn_editar.setStyleSheet("""
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
        btn_editar.clicked.connect(lambda: self.editar_docente(docente))

        # Botón 3: Pago de Honorarios
        btn_pago_honorarios = QPushButton("💰")
        btn_pago_honorarios.setToolTip("Registrar pago de honorarios")
        btn_pago_honorarios.setFixedSize(40, 28)
        btn_pago_honorarios.setStyleSheet("""
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
        btn_pago_honorarios.clicked.connect(lambda: self.pago_honorarios_docente(docente))

        # Botón 4: Ver CV (solo si existe)
        btn_ver_cv = QPushButton("📄")
        btn_ver_cv.setToolTip("Ver currículum vitae")
        btn_ver_cv.setFixedSize(40, 28)
        btn_ver_cv.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        
        # Habilitar solo si hay CV
        if docente.curriculum_path:
            btn_ver_cv.clicked.connect(lambda: self.abrir_cv_docente(docente))
        else:
            btn_ver_cv.setEnabled(False)
            btn_ver_cv.setToolTip("No hay CV disponible")

        # Botón 5: Eliminar
        btn_eliminar = QPushButton("🗑️")
        btn_eliminar.setToolTip("Eliminar docente")
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
        btn_eliminar.clicked.connect(lambda: self.eliminar_docente(docente))

        # Agregar todos los botones al layout
        layout.addWidget(btn_detalles)
        layout.addWidget(btn_editar)
        layout.addWidget(btn_pago_honorarios)
        layout.addWidget(btn_ver_cv)
        layout.addWidget(btn_eliminar)
        layout.addStretch()

        return widget
    
    # ==================== MÉTODOS DE BÚSQUEDA ====================
    
    def buscar_por_ci(self):
        """Buscar docente por CI"""
        ci_numero = self.txt_buscar_ci.text().strip()
        expedicion = self.combo_expedicion.currentText()
        
        if not ci_numero:
            QMessageBox.warning(self, "Advertencia", "Ingrese un número de CI para buscar")
            return
        
        self.current_filter = {'ci_numero': ci_numero}
        if expedicion != "Todas":
            self.current_filter['ci_expedicion'] = expedicion
        
        self.current_page = 1
        self.cargar_docentes(self.current_filter)
        self.status_bar.setText(f"Búsqueda por CI: {ci_numero}-{expedicion}")
    
    def buscar_por_nombre(self):
        """Buscar docente por nombre"""
        texto = self.txt_buscar_nombre.text().strip()
        
        if not texto:
            QMessageBox.warning(self, "Advertencia", "Ingrese un nombre o apellido para buscar")
            return
        
        self.current_filter = {'nombre': texto}
        self.current_page = 1
        self.cargar_docentes(self.current_filter)
        self.status_bar.setText(f"Búsqueda por nombre: {texto}")
    
    def mostrar_todos(self):
        """Mostrar todos los docentes"""
        self.txt_buscar_ci.clear()
        self.txt_buscar_nombre.clear()
        self.combo_expedicion.setCurrentIndex(0)
        
        self.current_filter = None
        self.current_page = 1
        self.cargar_docentes()
        self.status_bar.setText("Mostrando todos los docentes")
    
    # ==================== MÉTODOS CRUD ====================
    
    def nuevo_docente(self):
        """Abrir formulario para nuevo docente"""
        dialog = DocenteFormDialog(parent=self)
        dialog.docente_guardado.connect(self.on_docente_guardado)
        dialog.exec()
    
    def ver_detalles_docente(self, docente):
        """Mostrar diálogo con detalles del docente (solo lectura)"""
        docente_data = {
            'id': docente.id,
            'ci_numero': docente.ci_numero,
            'ci_expedicion': docente.ci_expedicion,
            'nombres': docente.nombres,
            'apellidos': docente.apellidos,
            'fecha_nacimiento': docente.fecha_nacimiento,
            'max_grado_academico': docente.max_grado_academico,
            'telefono': docente.telefono,
            'email': docente.email,
            'curriculum_path': docente.curriculum_path,
            'especialidad': docente.especialidad,
            'honorario_hora': docente.honorario_hora,
            'activo': docente.activo
        }

        dialog = DocenteInfoDialog(docente_id=docente_data[id], parent=self)

        # Conectar señales
        dialog.docente_pago_honorarios.connect(self.on_pago_honorarios_docente)
        dialog.docente_borrar.connect(self.on_borrar_docente_desde_dialog)

        dialog.exec()
    
    def editar_docente(self, docente):
        """Editar docente"""
        docente_data = {
            'id': docente.id,
            'ci_numero': docente.ci_numero,
            'ci_expedicion': docente.ci_expedicion,
            'nombres': docente.nombres,
            'apellidos': docente.apellidos,
            'fecha_nacimiento': docente.fecha_nacimiento,
            'max_grado_academico': docente.max_grado_academico,
            'telefono': docente.telefono,
            'email': docente.email,
            'curriculum_path': docente.curriculum_path,
            'especialidad': docente.especialidad,
            'honorario_hora': docente.honorario_hora,
            'activo': docente.activo
        }
        
        dialog = DocenteFormDialog(docente_data=docente_data, parent=self)
        dialog.docente_actualizado.connect(self.on_docente_actualizado)
        dialog.exec()
    
    def on_doble_click_tabla(self, index):
        """Manejar doble click en la tabla"""
        row = index.row()
        if row < len(self.docentes_cache):
            self.editar_docente(self.docentes_cache[row])
    
    def on_docente_guardado(self, datos):
        """Manejador cuando se guarda un docente"""
        try:
            # Determinar si es creación o edición
            es_nuevo = 'id' not in datos
            
            if es_nuevo:
                # CREAR NUEVO DOCENTE
                docente_creado = DocenteModel.crear_docente(datos)
                datos['id'] = docente_creado.id
                docente = docente_creado
                mensaje_titulo = "✅ Docente Creado"
            else:
                # ACTUALIZAR DOCENTE EXISTENTE
                docente = DocenteModel.find_by_id(datos['id'])
                if docente:
                    # Actualizar campos
                    for key, value in datos.items():
                        if hasattr(docente, key) and key != 'id':
                            setattr(docente, key, value)
                    docente.save()
                mensaje_titulo = "✅ Docente Actualizado"
            
            # Recargar la tabla
            self.cargar_docentes(self.current_filter)
            
            # Mostrar diálogo de detalles en modo lectura
            QTimer.singleShot(100, lambda: self.mostrar_detalles_despues_de_guardar(docente, mensaje_titulo))
            
        except ValueError as e:
            QMessageBox.warning(self, "Error de Validación", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar docente: {str(e)}")
            logger.error(f"Error en on_docente_guardado: {e}")
    
    def mostrar_detalles_despues_de_guardar(self, docente, titulo):
        """Mostrar diálogo de detalles después de guardar"""
        try:
            # Preparar datos para el diálogo de detalles
            docente_data = {
                'id': docente.id,
                'ci_numero': docente.ci_numero,
                'ci_expedicion': docente.ci_expedicion,
                'nombres': docente.nombres,
                'apellidos': docente.apellidos,
                'fecha_nacimiento': docente.fecha_nacimiento,
                'max_grado_academico': docente.max_grado_academico,
                'telefono': docente.telefono,
                'email': docente.email,
                'curriculum_path': docente.curriculum_path,
                'especialidad': docente.especialidad,
                'honorario_hora': docente.honorario_hora,
                'activo': docente.activo
            }
            
            # Crear diálogo en modo lectura
            dialog = DocenteFormDialog(
                docente_data=docente_data, 
                modo_lectura=True, 
                parent=self
            )
            
            # Conectar las señales para los botones especiales
            dialog.docente_pago_honorarios.connect(self.on_pago_honorarios_docente)
            dialog.docente_borrar.connect(self.on_borrar_docente_desde_dialog)
            
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Error al mostrar detalles después de guardar: {e}")
            # Si falla, mostrar mensaje tradicional
            QMessageBox.information(self, titulo, "Docente guardado exitosamente")
    
    def pago_honorarios_docente(self, docente):
        """Abrir diálogo de pago de honorarios para docente"""
        try:
            # Preparar descripción predefinida
            descripcion = f"PAGO POR HONORARIOS - {docente.nombre_completo}"
            if docente.ci_numero:
                descripcion += f" - CI: {docente.ci_numero}"
            
            datos_predefinidos = {
                'descripcion': descripcion,
                'categoria': 'PAGO_DOCENTE',
                'monto': docente.honorario_hora * 8  # Sugerir 8 horas por defecto
            }
            
            # Abrir diálogo de gasto operativo con datos predefinidos
            dialog = GastoOperativoDialog(
                datos_predefinidos=datos_predefinidos,
                parent=self
            )
            dialog.gasto_guardado.connect(self.on_gasto_guardado)
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Error al abrir pago de honorarios: {e}")
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def on_pago_honorarios_docente(self, docente_data):
        """Manejador para pago de honorarios desde diálogo de detalles"""
        try:
            docente = DocenteModel.find_by_id(docente_data['id'])
            if docente:
                self.pago_honorarios_docente(docente)
                
        except Exception as e:
            logger.error(f"Error en on_pago_honorarios_docente: {e}")
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def abrir_cv_docente(self, docente):
        """Abrir CV del docente en visor PDF"""
        try:
            if docente.curriculum_path and os.path.exists(docente.curriculum_path):
                url = QUrl.fromLocalFile(docente.curriculum_path)
                QDesktopServices.openUrl(url)
            else:
                QMessageBox.information(self, "Información", "No hay currículum vitae disponible para este docente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo PDF: {str(e)}")
    
    def eliminar_docente(self, docente):
        """Eliminar docente con confirmación"""
        respuesta = QMessageBox.question(
            self, "🗑️ Confirmar Eliminación",
            f"¿Está seguro de eliminar al docente?\n\n"
            f"Nombre: {docente.nombre_completo}\n"
            f"CI: {docente.ci_numero}-{docente.ci_expedicion}\n\n"
            f"⚠️ Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            try:
                # Eliminar usando el modelo
                success = DocenteModel.delete(docente.id)
                if success:
                    QMessageBox.information(self, "✅ Éxito", "Docente eliminado correctamente")
                    self.cargar_docentes(self.current_filter)
                else:
                    QMessageBox.warning(self, "Error", "No se pudo eliminar el docente")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar: {str(e)}")
    
    def on_borrar_docente_desde_dialog(self, docente_data):
        """Manejador para borrar docente desde diálogo de detalles"""
        try:
            docente = DocenteModel.find_by_id(docente_data['id'])
            if docente:
                self.eliminar_docente(docente)
        except Exception as e:
            logger.error(f"Error al borrar docente desde diálogo: {e}")
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def on_gasto_guardado(self, datos_gasto):
        """Manejador cuando se guarda un gasto"""
        self.status_bar.setText(f"Gasto registrado exitosamente - ID: {datos_gasto.get('id', 'N/A')}")
    
    # ==================== MÉTODOS DE PAGINACIÓN ====================
    
    def actualizar_controles_paginacion(self):
        """Actualizar controles de paginación"""
        if self.records_per_page == 0:
            self.total_pages = 1
        else:
            self.total_pages = max(1, (self.total_records + self.records_per_page - 1) // self.records_per_page)
        
        self.lbl_pagina_info.setText(f"Página {self.current_page} de {self.total_pages}")
        
        # Habilitar/deshabilitar botones
        self.btn_primera.setEnabled(self.current_page > 1)
        self.btn_anterior.setEnabled(self.current_page > 1)
        self.btn_siguiente.setEnabled(self.current_page < self.total_pages)
        self.btn_ultima.setEnabled(self.current_page < self.total_pages)
    
    def actualizar_contador(self):
        """Actualizar contador de registros"""
        if self.total_records == 0:
            self.lbl_contador.setText("No hay docentes")
        else:
            if self.records_per_page == 0:
                inicio = 1
                fin = self.total_records
            else:
                inicio = (self.current_page - 1) * self.records_per_page + 1
                fin = min(self.current_page * self.records_per_page, self.total_records)
            
            self.lbl_contador.setText(f"Mostrando {inicio}-{fin} de {self.total_records} docentes")
    
    def cambiar_pagina(self, pagina):
        """Cambiar a página específica"""
        if 1 <= pagina <= self.total_pages:
            self.current_page = pagina
            self.cargar_docentes(self.current_filter)
    
    def pagina_anterior(self):
        """Ir a página anterior"""
        if self.current_page > 1:
            self.current_page -= 1
            self.cargar_docentes(self.current_filter)
    
    def pagina_siguiente(self):
        """Ir a página siguiente"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.cargar_docentes(self.current_filter)
    
    def ultima_pagina(self):
        """Ir a última página"""
        self.cambiar_pagina(self.total_pages)
    
    def cambiar_registros_pagina(self, texto):
        """Cambiar registros por página"""
        if texto == "Todos":
            self.records_per_page = 0
        else:
            try:
                self.records_per_page = int(texto)
            except:
                self.records_per_page = 25
        
        self.current_page = 1
        self.cargar_docentes(self.current_filter)