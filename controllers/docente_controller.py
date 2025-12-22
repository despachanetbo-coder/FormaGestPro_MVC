# app/controllers/docente_controller.py
"""
Controlador para la gestión de docentes - VERSIÓN COMPLETA
"""
import sys
import os
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QMessageBox, QTableWidget, QTableWidgetItem, QPushButton,
    QHBoxLayout, QVBoxLayout, QWidget, QHeaderView, QLabel, QLineEdit,
    QComboBox, QDateEdit, QCheckBox, QGroupBox, QFormLayout, QTextEdit,
    QTabWidget, QGridLayout, QFrame, QApplication, QProgressDialog,
    QDialogButtonBox, QFileDialog, QInputDialog, QProgressBar,
    QDoubleSpinBox
)
from PySide6.QtCore import Qt, QDate, Signal, Slot, QTimer, QSize
from PySide6.QtGui import QColor, QFont, QIcon

try:
    from app.views.generated.dialogs.ui_docente_dialog import Ui_DocenteDialog # type: ignore
    from app.views.generated.dialogs.ui_docente_form_dialog import Ui_DocenteFormDialog
except ImportError as e:
    print(f"❌ Error importando interfaces UI: {e}")
    print("💡 Ejecuta: pyside6-uic app/views/ui/dialogs/docente_dialog.ui -o app/views/generated/dialogs/ui_docente_dialog.py")
    print("💡 Ejecuta: pyside6-uic app/views/ui/dialogs/docente_form_dialog.ui -o app/views/generated/dialogs/ui_docente_form_dialog.py")

from app.models.docente_model import DocenteModel
from database.database import db

# ==================== CLASES DEL CONTROLADOR ====================

class DocenteFormDialog(QDialog):
    """Diálogo para crear/editar docentes - VERSIÓN COMPLETA"""
    
    docente_guardado = Signal(dict)
    
    def __init__(self, docente_data=None, parent=None):
        super().__init__(parent)
        self.ui = Ui_DocenteFormDialog()
        self.ui.setupUi(self)
        
        self.docente_data = docente_data
        self.modo_edicion = docente_data is not None
        
        self.setup_ui()
        self.setup_connections()
        
        if self.modo_edicion:
            self.cargar_datos()
        else:
            # Configurar fecha por defecto (30 años atrás)
            fecha_default = QDate.currentDate().addYears(-30)
            self.ui.dateFechaNacimiento.setDate(fecha_default)
            # Configurar honorario por defecto
            self.ui.spinHonorarioHora.setValue(0.0)
    
    def setup_ui(self):
        """Configurar interfaz"""
        if self.modo_edicion:
            self.setWindowTitle(f"✏️ Editar Docente/Tutor")
            self.ui.txtCINumero.setEnabled(False)
            self.ui.comboExpedicion.setEnabled(False)
        else:
            self.setWindowTitle("➕ Nuevo Docente/Tutor")
        
        # Configurar spinbox de honorario
        self.ui.spinHonorarioHora.setRange(0, 10000)
        self.ui.spinHonorarioHora.setDecimals(2)
        self.ui.spinHonorarioHora.setSingleStep(10.0)
        
        # Configurar validadores
        self.ui.txtCINumero.textChanged.connect(self.validar_ci)
        self.ui.txtEmail.textChanged.connect(self.validar_email)
        
        # Configurar tooltips
        self.ui.txtCINumero.setToolTip("Solo números, sin puntos ni guiones")
        self.ui.txtEmail.setToolTip("ejemplo@dominio.com")
        self.ui.txtTelefono.setToolTip("Ej: 77712345")
        self.ui.spinHonorarioHora.setToolTip("Honorario por hora en Bolivianos")
        self.ui.txtEspecialidad.setToolTip("Área de especialización o experiencia")
    
    def setup_connections(self):
        """Conectar señales"""
        self.ui.buttonBox.accepted.connect(self.validar_y_guardar)
        self.ui.buttonBox.rejected.connect(self.reject)
        
        # Calcular edad automáticamente
        self.ui.dateFechaNacimiento.dateChanged.connect(self.calcular_edad)
    
    def calcular_edad(self):
        """Calcular y mostrar edad"""
        fecha_nac = self.ui.dateFechaNacimiento.date()
        hoy = QDate.currentDate()
        
        edad = hoy.year() - fecha_nac.year()
        if (hoy.month(), hoy.day()) < (fecha_nac.month(), fecha_nac.day()):
            edad -= 1
        
        self.ui.dateFechaNacimiento.setToolTip(f"Edad: {edad} años")
    
    def validar_ci(self, texto):
        """Validar formato de CI"""
        if texto and not texto.isdigit():
            # Remover caracteres no numéricos
            limpio = ''.join(filter(str.isdigit, texto))
            self.ui.txtCINumero.setText(limpio)
            self.ui.txtCINumero.setCursorPosition(len(limpio))
    
    def validar_email(self, texto):
        """Validar formato de email"""
        if texto and ('@' not in texto or '.' not in texto.split('@')[-1]):
            self.ui.txtEmail.setStyleSheet("border: 1px solid #e74c3c;")
        else:
            self.ui.txtEmail.setStyleSheet("")
    
    def cargar_datos(self):
        """Cargar datos del docente en el formulario"""
        if not self.docente_data:
            return
        
        # Campos obligatorios
        self.ui.txtCINumero.setText(str(self.docente_data.get('ci_numero', '')))
        
        expedicion = self.docente_data.get('ci_expedicion', 'BE')
        index = self.ui.comboExpedicion.findText(expedicion)
        if index >= 0:
            self.ui.comboExpedicion.setCurrentIndex(index)
        
        self.ui.txtNombres.setText(self.docente_data.get('nombres', ''))
        self.ui.txtApellidos.setText(self.docente_data.get('apellidos', ''))
        
        # Fecha de nacimiento
        fecha_nac = self.docente_data.get('fecha_nacimiento')
        if fecha_nac:
            try:
                qdate = QDate.fromString(fecha_nac, 'yyyy-MM-dd')
                if qdate.isValid():
                    self.ui.dateFechaNacimiento.setDate(qdate)
            except:
                pass
        
        # Otros campos
        campos = {
            'telefono': self.ui.txtTelefono,
            'email': self.ui.txtEmail,
            'especialidad': self.ui.txtEspecialidad
        }
        
        for campo_db, widget in campos.items():
            valor = self.docente_data.get(campo_db, '')
            if valor:
                widget.setText(str(valor))
        
        # Grado académico
        grado = self.docente_data.get('max_grado_academico')
        if grado:
            index = self.ui.comboGradoAcademico.findText(grado)
            if index >= 0:
                self.ui.comboGradoAcademico.setCurrentIndex(index)
        
        # Honorario por hora
        honorario = self.docente_data.get('honorario_hora', 0.0)
        self.ui.spinHonorarioHora.setValue(float(honorario))
        
        # Estado activo
        activo = self.docente_data.get('activo', 1)
        self.ui.checkActivo.setChecked(bool(activo))
    
    def obtener_datos_formulario(self):
        """Obtener y validar datos del formulario"""
        # Validar campos obligatorios
        errores = []
        
        ci_numero = self.ui.txtCINumero.text().strip()
        if not ci_numero:
            errores.append("El número de CI es obligatorio")
        elif not ci_numero.isdigit():
            errores.append("El CI debe contener solo números")
        
        ci_expedicion = self.ui.comboExpedicion.currentText()
        nombres = self.ui.txtNombres.text().strip()
        apellidos = self.ui.txtApellidos.text().strip()
        
        if not nombres:
            errores.append("Los nombres son obligatorios")
        
        if not apellidos:
            errores.append("Los apellidos son obligatorios")
        
        # Validar email si se ingresó
        email = self.ui.txtEmail.text().strip()
        if email and ('@' not in email or '.' not in email.split('@')[-1]):
            errores.append("Formato de email inválido")
        
        return errores, {
            'ci_numero': ci_numero,
            'ci_expedicion': ci_expedicion,
            'nombres': nombres,
            'apellidos': apellidos,
            'activo': 1 if self.ui.checkActivo.isChecked() else 0
        }
    
    def validar_y_guardar(self):
        """Validar y guardar los datos"""
        errores, datos = self.obtener_datos_formulario()
        
        if errores:
            QMessageBox.warning(self, "Validación", "\n".join(errores))
            return
        
        # Agregar campos opcionales
        fecha_nac = self.ui.dateFechaNacimiento.date()
        if fecha_nac.isValid():
            datos['fecha_nacimiento'] = fecha_nac.toString('yyyy-MM-dd')
        
        telefono = self.ui.txtTelefono.text().strip()
        if telefono:
            datos['telefono'] = telefono
        
        email = self.ui.txtEmail.text().strip()
        if email:
            datos['email'] = email
        
        especialidad = self.ui.txtEspecialidad.text().strip()
        if especialidad:
            datos['especialidad'] = especialidad
        
        # Grado académico
        grado = self.ui.comboGradoAcademico.currentText()
        if grado and grado != "Seleccione...":
            datos['max_grado_academico'] = grado
        
        # Honorario por hora
        honorario = self.ui.spinHonorarioHora.value()
        if honorario > 0:
            datos['honorario_hora'] = honorario
        
        # Si es nuevo, verificar que no exista el CI
        if not self.modo_edicion:
            existente = DocenteModel.buscar_por_ci(
                datos['ci_numero'], 
                datos['ci_expedicion']
            )
            if existente:
                QMessageBox.warning(
                    self, "Validación", 
                    f"Ya existe un docente con CI {datos['ci_numero']}-{datos['ci_expedicion']}"
                )
                return
        
        # Emitir señal con los datos
        self.docente_guardado.emit(datos)
        self.accept()


class DocenteDialog(QDialog):
    """Diálogo principal de gestión de docentes - VERSIÓN COMPLETA"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_DocenteDialog()
        self.ui.setupUi(self)

        # Configuración inicial
        self.current_page = 1
        self.records_per_page = 25
        self.total_records = 0
        self.total_pages = 1
        self.current_filter = None
        self.docentes_cache = []

        print(f"📊 Records per page: {self.records_per_page}")
        print(f"📊 Current page: {self.current_page}")

        self.setup_ui()
        self.setup_connections()
        self.cargar_docentes_inicial()

        print("✅ Diálogo de docentes inicializado (versión completa)")
    
    def setup_ui(self):
        """Configurar interfaz inicial"""
        # Configurar tabla
        header = self.ui.tableDocentes.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # CI
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Nombre
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Grado
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Especialidad
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Honorario/H
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Email
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Teléfono
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Estado
        header.setSectionResizeMode(9, QHeaderView.Fixed)             # Acciones
        self.ui.tableDocentes.setColumnWidth(9, 120)
        
        # Configurar estilo de la tabla
        self.ui.tableDocentes.setAlternatingRowColors(True)
        self.ui.tableDocentes.setStyleSheet("""
            QTableWidget {
                gridline-color: #ddd;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        # Configurar combo de registros por página
        self.ui.comboRegistrosPagina.setCurrentText("25")
        
        # Configurar barra de estado
        self.ui.statusbar.showMessage("Sistema de gestión de docentes listo", 3000)
    
    def setup_connections(self):
        """Conectar todas las señales"""
        # Botones de búsqueda
        self.ui.btnBuscarCI.clicked.connect(self.buscar_por_ci)
        self.ui.btnBuscarNombre.clicked.connect(self.buscar_por_nombre)
        self.ui.btnBuscarEspecialidad.clicked.connect(self.buscar_por_especialidad)
        self.ui.btnMostrarTodos.clicked.connect(self.mostrar_todos)
        self.ui.btnSoloActivos.clicked.connect(self.mostrar_solo_activos)
        self.ui.btnVerEstadisticas.clicked.connect(self.ver_estadisticas)
        self.ui.btnNuevoDocente.clicked.connect(self.nuevo_docente)
        
        # Paginación
        self.ui.btnPrimeraPagina.clicked.connect(lambda: self.cambiar_pagina(1))
        self.ui.btnPaginaAnterior.clicked.connect(self.pagina_anterior)
        self.ui.btnPaginaSiguiente.clicked.connect(self.pagina_siguiente)
        self.ui.btnUltimaPagina.clicked.connect(self.ultima_pagina)
        self.ui.comboRegistrosPagina.currentTextChanged.connect(self.cambiar_registros_pagina)
        
        # Buscar con Enter
        self.ui.txtBuscarCINumero.returnPressed.connect(self.buscar_por_ci)
        self.ui.txtBuscarNombre.returnPressed.connect(self.buscar_por_nombre)
        self.ui.txtBuscarEspecialidad.returnPressed.connect(self.buscar_por_especialidad)
        
        # Doble click en tabla para editar
        self.ui.tableDocentes.doubleClicked.connect(self.editar_docente_click)

        self.finished.connect(self.cleanup_on_close)
    
    def cargar_docentes_inicial(self):
        """Cargar docentes al iniciar"""
        QTimer.singleShot(100, lambda: self.mostrar_todos_safe())

    def mostrar_todos_safe(self):
        """Versión segura de mostrar_todos para uso con timer"""
        try:
            self.mostrar_todos()
        except Exception as e:
            print(f"❌ Error en carga inicial: {e}")
            self.ui.statusbar.showMessage(f"Error inicial: {str(e)}", 5000)

    # ==================== MÉTODOS DE CARGA Y PAGINACIÓN ====================
    
    def cargar_docentes(self, filtro=None):
        """Cargar docentes con paginación"""
        progress = None  # Declarar fuera del try
        try:
            # Mostrar progreso
            progress = QProgressDialog("Cargando docentes...", "Cancelar", 0, 100, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setValue(10)
            progress.setAutoClose(True)
            progress.setAutoReset(True)
            QApplication.processEvents()

            # Limpiar tabla
            self.ui.tableDocentes.setRowCount(0)
            progress.setValue(30)

            # Obtener docentes
            offset = (self.current_page - 1) * self.records_per_page
            self.docentes_cache = self.obtener_docentes_paginados(filtro, offset)
            progress.setValue(60)

            if not self.docentes_cache:
                self.ui.tableDocentes.setRowCount(1)
                item = QTableWidgetItem("No se encontraron docentes")
                item.setTextAlignment(Qt.AlignCenter)
                item.setForeground(QColor("#7f8c8d"))
                self.ui.tableDocentes.setItem(0, 0, item)
                self.ui.tableDocentes.setSpan(0, 0, 1, 10)
                self.total_records = 0
            else:
                # Llenar tabla
                for i, docente in enumerate(self.docentes_cache):
                    self.agregar_fila_tabla(i, docente)

                # Obtener total de registros - CORRECCIÓN: usar contar_docentes
                self.total_records = self.contar_docentes(filtro)  # ¡¡¡CORREGIDO!!!

            progress.setValue(90)

            # Actualizar controles
            self.actualizar_controles_paginacion()
            self.actualizar_contador()

            progress.setValue(100)
            self.ui.statusbar.showMessage(f"Cargados {len(self.docentes_cache)} docentes", 3000)

        except Exception as e:
            self.ui.statusbar.showMessage(f"Error: {str(e)}", 5000)
            QMessageBox.critical(self, "Error", f"Error cargando docentes: {str(e)}")
            print(f"❌ Error en cargar_docentes: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Asegurar que el progress dialog se cierre
            if progress:
                progress.close()

    def contar_docentes(self, filtro=None):
        """Contar total de docentes"""
        try:
            query = "SELECT COUNT(*) as total FROM docentes"
            params = []

            if filtro:
                # Verificar que el filtro sea un diccionario válido
                if isinstance(filtro, dict):
                    if 'condicion' in filtro and 'params' in filtro:
                        query += f" WHERE {filtro['condicion']}"
                        params = filtro['params']
                    else:
                        print(f"⚠️  Filtro no tiene estructura válida: {filtro}")
                else:
                    print(f"⚠️  Filtro no es un diccionario: {type(filtro)}")

            print(f"🔍 Query contar_docentes: {query}")
            print(f"🔍 Params contar_docentes: {params}")

            if params:
                resultado = db.fetch_one(query, tuple(params))
            else:
                resultado = db.fetch_one(query)

            total = resultado['total'] if resultado else 0
            print(f"📊 Total docentes encontrados: {total}")

            return total

        except Exception as e:
            print(f"❌ Error en contar_docentes: {e}")
            print(f"   Query: {query}")
            print(f"   Params: {params}")
            return 0

    def agregar_fila_tabla(self, fila, docente):
        """Agregar una fila a la tabla"""
        self.ui.tableDocentes.insertRow(fila)
        
        # ID
        self.ui.tableDocentes.setItem(fila, 0, 
            QTableWidgetItem(str(docente.id)))
        
        # CI completo
        ci_completo = f"{docente.ci_numero}-{docente.ci_expedicion}"
        item_ci = QTableWidgetItem(ci_completo)
        item_ci.setToolTip(f"CI: {ci_completo}")
        self.ui.tableDocentes.setItem(fila, 1, item_ci)
        
        # Nombre completo
        item_nombre = QTableWidgetItem(docente.nombre_completo)
        item_nombre.setToolTip(f"Nombre: {docente.nombre_completo}")
        self.ui.tableDocentes.setItem(fila, 2, item_nombre)
        
        # Grado académico
        grado = docente.max_grado_academico if docente.max_grado_academico else ""
        item_grado = QTableWidgetItem(grado)
        if grado:
            item_grado.setForeground(QColor("#9b59b6"))
            item_grado.setToolTip(f"Grado: {grado}")
        self.ui.tableDocentes.setItem(fila, 3, item_grado)
        
        # Especialidad
        especialidad = docente.especialidad if docente.especialidad else ""
        item_especialidad = QTableWidgetItem(especialidad)
        if especialidad:
            item_especialidad.setToolTip(f"Especialidad: {especialidad}")
        self.ui.tableDocentes.setItem(fila, 4, item_especialidad)
        
        # Honorario/Hora
        honorario = docente.honorario_hora if hasattr(docente, 'honorario_hora') else 0.0
        item_honorario = QTableWidgetItem(f"Bs. {honorario:.2f}")
        if honorario > 0:
            item_honorario.setForeground(QColor("#27ae60"))
            item_honorario.setToolTip(f"Honorario por hora: Bs. {honorario:.2f}")
        self.ui.tableDocentes.setItem(fila, 5, item_honorario)
        
        # Email
        email = docente.email if docente.email else ""
        item_email = QTableWidgetItem(email)
        if email:
            item_email.setForeground(QColor("#3498db"))
            item_email.setToolTip(f"Email: {email}")
        self.ui.tableDocentes.setItem(fila, 6, item_email)
        
        # Teléfono
        telefono = docente.telefono if docente.telefono else ""
        item_telefono = QTableWidgetItem(telefono)
        self.ui.tableDocentes.setItem(fila, 7, item_telefono)
        
        # Estado
        if docente.activo:
            estado_texto = "✅ Activo"
            color = QColor("#27ae60")
        else:
            estado_texto = "❌ Inactivo"
            color = QColor("#e74c3c")
        
        item_estado = QTableWidgetItem(estado_texto)
        item_estado.setForeground(color)
        item_estado.setTextAlignment(Qt.AlignCenter)
        item_estado.setToolTip("Activo" if docente.activo else "Inactivo")
        self.ui.tableDocentes.setItem(fila, 8, item_estado)
        
        # Acciones
        acciones_widget = self.crear_widget_acciones(docente)
        self.ui.tableDocentes.setCellWidget(fila, 9, acciones_widget)
    
    def crear_widget_acciones(self, docente):
        """Crear widget con botones de acciones"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(3)
        
        # Botón Editar
        btn_editar = QPushButton("✏️")
        btn_editar.setToolTip("Editar docente")
        btn_editar.setFixedSize(28, 28)
        btn_editar.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_editar.clicked.connect(lambda: self.editar_docente(docente))
        
        # Botón Ver Detalles
        btn_detalles = QPushButton("👁️")
        btn_detalles.setToolTip("Ver detalles")
        btn_detalles.setFixedSize(28, 28)
        btn_detalles.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        btn_detalles.clicked.connect(lambda: self.ver_detalles_completos(docente))
        
        # Botón Eliminar
        btn_eliminar = QPushButton("🗑️")
        btn_eliminar.setToolTip("Eliminar docente")
        btn_eliminar.setFixedSize(28, 28)
        btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_eliminar.clicked.connect(lambda: self.eliminar_docente(docente))
        
        layout.addWidget(btn_editar)
        layout.addWidget(btn_detalles)
        layout.addWidget(btn_eliminar)
        layout.addStretch()
        
        return widget
    
    # Devuelve un número limitado de registros de docentes para ser mostrados por páginas a partir de offset
    def obtener_docentes_paginados(self, filtro=None, offset=0):
        """Obtener docentes con paginación"""
        query = "SELECT * FROM docentes"
        params = []
        
        if filtro:
            query += f" WHERE {filtro['condicion']}"
            params = filtro['params']
        
        # CORREGIDO: Solo añadir LIMIT y OFFSET si hay parámetros
        if params:
            query += " LIMIT ? OFFSET ?"
            params.extend([self.records_per_page, offset])
        else:
            query += f" LIMIT {self.records_per_page} OFFSET {offset}"

        try:
            if params:
                rows = db.fetch_all(query, tuple(params))
            else:
                rows = db.fetch_all(query)
            return [DocenteModel(**row) for row in rows]
        except Exception as e:
            print(f"❌ Error en obtener_docentes_paginados: {e}")
            print(f"   Query: {query}")
            print(f"   Params: {params}")
            return []
    
    # ==================== MÉTODOS DE BÚSQUEDA ====================
    
    # Método que busca docente por CI
    def buscar_por_ci(self):
        """Buscar docente por CI"""
        ci_numero = self.ui.txtBuscarCINumero.text().strip()
        expedicion = self.ui.comboBuscarExpedicion.currentText()
        
        if not ci_numero:
            QMessageBox.warning(self, "Búsqueda", "Ingrese un número de CI")
            self.ui.txtBuscarCINumero.setFocus()
            return
        
        # CORREGIDO: Manejo correcto de parámetros
        if expedicion == "Todas":
            filtro = {
                'condicion': "ci_numero LIKE ?",
                'params': [f"%{ci_numero}%"]
            }
            mensaje = f"Búsqueda por CI que contiene: {ci_numero}"
        else:
            filtro = {
                'condicion': "ci_numero = ? AND ci_expedicion = ?",
                'params': [ci_numero, expedicion]
            }
            mensaje = f"Búsqueda por CI exacto: {ci_numero}-{expedicion}"

        self.current_filter = filtro
        self.current_page = 1

        try:
            self.cargar_docentes(filtro)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en búsqueda: {str(e)}")
            self.ui.statusbar.showMessage(f"Error en búsqueda: {str(e)}", 5000)
            return

        if self.total_records == 0:
            self.ui.statusbar.showMessage(f"No se encontraron docentes", 3000)
            QMessageBox.information(self, "Búsqueda", 
                f"No se encontraron docentes con CI: {ci_numero}")
        else:
            self.ui.statusbar.showMessage(
                f"Encontrados {self.total_records} docentes - {mensaje}", 3000)
    
    def buscar_por_nombre(self):
        """Buscar docente por nombre o apellido"""
        nombre = self.ui.txtBuscarNombre.text().strip()
        
        if not nombre:
            QMessageBox.warning(self, "Búsqueda", "Ingrese un nombre o apellido")
            self.ui.txtBuscarNombre.setFocus()
            return
        
        filtro = {
            'condicion': "nombres LIKE ? OR apellidos LIKE ? OR nombres || ' ' || apellidos LIKE ?",
            'params': [f"%{nombre}%", f"%{nombre}%", f"%{nombre}%"]
        }
        
        self.current_filter = filtro
        self.current_page = 1
        self.cargar_docentes(filtro)
        
        if self.total_records == 0:
            self.ui.statusbar.showMessage(f"No se encontraron docentes con: {nombre}", 3000)
            QMessageBox.information(self, "Búsqueda", 
                f"No se encontraron docentes con: {nombre}")
        else:
            self.ui.statusbar.showMessage(
                f"Encontrados {self.total_records} docentes para: {nombre}", 3000)
    
    def buscar_por_especialidad(self):
        """Buscar docente por especialidad"""
        especialidad = self.ui.txtBuscarEspecialidad.text().strip()
        
        if not especialidad:
            QMessageBox.warning(self, "Búsqueda", "Ingrese una especialidad")
            self.ui.txtBuscarEspecialidad.setFocus()
            return
        
        filtro = {
            'condicion': "especialidad LIKE ?",
            'params': [f"%{especialidad}%"]
        }
        
        self.current_filter = filtro
        self.current_page = 1
        self.cargar_docentes(filtro)
        
        if self.total_records == 0:
            self.ui.statusbar.showMessage(f"No se encontraron docentes con especialidad: {especialidad}", 3000)
            QMessageBox.information(self, "Búsqueda", 
                f"No se encontraron docentes con especialidad: {especialidad}")
        else:
            self.ui.statusbar.showMessage(
                f"Encontrados {self.total_records} docentes con especialidad: {especialidad}", 3000)
    
    def mostrar_todos(self):
        """Mostrar todos los docentes"""
        self.current_filter = None
        self.current_page = 1
        self.ui.txtBuscarCINumero.clear()
        self.ui.txtBuscarNombre.clear()
        self.ui.txtBuscarEspecialidad.clear()
        self.ui.comboBuscarExpedicion.setCurrentIndex(0)

        try:
            self.cargar_docentes()  # Sin filtro
            self.ui.statusbar.showMessage("Mostrando todos los docentes", 3000)
        except Exception as e:
            self.ui.statusbar.showMessage(f"Error: {str(e)}", 5000)
            QMessageBox.critical(self, "Error", f"Error cargando docentes: {str(e)}")

    def mostrar_solo_activos(self):
        """Mostrar solo docentes activos"""
        filtro = {
            'condicion': "activo = 1",
            'params': []
        }
        
        self.current_filter = filtro
        self.current_page = 1
        self.ui.txtBuscarCINumero.clear()
        self.ui.txtBuscarNombre.clear()
        self.ui.txtBuscarEspecialidad.clear()
        self.cargar_docentes(filtro)
        self.ui.statusbar.showMessage("Mostrando solo docentes activos", 3000)
    
    # ==================== MÉTODOS CRUD COMPLETOS ====================
    
    def nuevo_docente(self):
        """Abrir diálogo para nuevo docente"""
        dialog = DocenteFormDialog(parent=self)
        
        def on_docente_guardado(datos):
            try:
                docente = DocenteModel.crear_docente(datos)
                
                # Mostrar mensaje de éxito con detalles
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("✅ Docente Creado")
                msg.setText(f"Docente creado exitosamente!")
                msg.setInformativeText(
                    f"ID: {docente.id}\n"
                    f"Nombre: {docente.nombre_completo}\n"
                    f"CI: {docente.ci_numero}-{docente.ci_expedicion}\n"
                    f"Grado: {docente.max_grado_academico if docente.max_grado_academico else 'No especificado'}"
                )
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                
                # Recargar docentes
                self.cargar_docentes(self.current_filter)
                
            except ValueError as e:
                QMessageBox.warning(self, "Error de Validación", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al crear docente: {str(e)}")
        
        dialog.docente_guardado.connect(on_docente_guardado)
        dialog.exec()
    
    def editar_docente_click(self, index):
        """Editar docente al hacer doble click"""
        if index.column() != 9:  # No es la columna de acciones
            row = index.row()
            if row < len(self.docentes_cache):
                self.editar_docente(self.docentes_cache[row])
    
    def editar_docente(self, docente):
        """Editar docente existente"""
        # Preparar datos para el formulario
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
            'especialidad': docente.especialidad,
            'honorario_hora': docente.honorario_hora if hasattr(docente, 'honorario_hora') else 0.0,
            'activo': docente.activo
        }
        
        dialog = DocenteFormDialog(docente_data=docente_data, parent=self)
        
        def on_docente_guardado(datos):
            try:
                # Actualizar docente
                docente.nombres = datos['nombres']
                docente.apellidos = datos['apellidos']
                docente.fecha_nacimiento = datos.get('fecha_nacimiento')
                docente.max_grado_academico = datos.get('max_grado_academico')
                docente.telefono = datos.get('telefono')
                docente.email = datos.get('email')
                docente.especialidad = datos.get('especialidad')
                docente.honorario_hora = datos.get('honorario_hora', 0.0)
                docente.activo = datos['activo']
                
                docente.save()
                
                # Mostrar mensaje de éxito
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("✅ Docente Actualizado")
                msg.setText(f"Docente actualizado exitosamente!")
                msg.setInformativeText(
                    f"Nombre: {docente.nombre_completo}\n"
                    f"CI: {docente.ci_numero}-{docente.ci_expedicion}\n"
                    f"Estado: {'Activo' if docente.activo else 'Inactivo'}"
                )
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                
                # Recargar docentes
                self.cargar_docentes(self.current_filter)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al actualizar docente: {str(e)}")
        
        dialog.docente_guardado.connect(on_docente_guardado)
        dialog.exec()
    
    def ver_detalles_completos(self, docente):
        """Ver detalles completos del docente"""
        from PySide6.QtWidgets import QTextEdit, QDialog, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"📋 Detalles del Docente/Tutor")
        dialog.setModal(True)
        dialog.resize(500, 550)
        
        layout = QVBoxLayout(dialog)
        
        # Crear texto con los detalles
        edad_text = f" ({docente.edad} años)" if docente.edad else ""
        
        texto = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif;">
            <h2 style="color: #2c3e50; text-align: center;">📋 DETALLES DEL DOCENTE/TUTOR</h2>
            <hr style="border: 1px solid #ddd; margin: 10px 0;">
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <h3 style="color: #3498db; margin-top: 0;">👨‍🏫 Información Personal</h3>
                <p><strong>ID:</strong> {docente.id}</p>
                <p><strong>Nombre completo:</strong> {docente.nombre_completo}</p>
                <p><strong>CI:</strong> {docente.ci_numero}-{docente.ci_expedicion}</p>
        """
        
        if docente.fecha_nacimiento:
            texto += f"<p><strong>Fecha nacimiento:</strong> {docente.fecha_nacimiento}{edad_text}</p>"
        
        if docente.max_grado_academico:
            texto += f"<p><strong>Grado académico:</strong> {docente.max_grado_academico}</p>"
        
        texto += f"""
                <p><strong>Fecha registro:</strong> {docente.created_at[:10] if docente.created_at else 'N/A'}</p>
                <p><strong>Estado:</strong> <span style="color: {'#27ae60' if docente.activo else '#e74c3c'}">
                    {'✅ Activo' if docente.activo else '❌ Inactivo'}</span></p>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <h3 style="color: #3498db;">📞 Contacto</h3>
        """
        
        if docente.telefono:
            texto += f"<p><strong>Teléfono:</strong> {docente.telefono}</p>"
        
        if docente.email:
            texto += f"<p><strong>Email:</strong> <a href='mailto:{docente.email}' style='color: #3498db;'>{docente.email}</a></p>"
        
        texto += """
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px;">
                <h3 style="color: #3498db;">🎓 Información Académica</h3>
        """
        
        if docente.especialidad:
            texto += f"<p><strong>Especialidad:</strong> {docente.especialidad}</p>"
        
        if hasattr(docente, 'honorario_hora') and docente.honorario_hora:
            texto += f"<p><strong>Honorario por hora:</strong> Bs. {docente.honorario_hora:.2f}</p>"
        
        texto += """
            </div>
        </div>
        """
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(texto)
        layout.addWidget(text_edit)
        
        # Botones
        button_box = QDialogButtonBox()
        btn_editar = button_box.addButton("✏️ Editar", QDialogButtonBox.ActionRole)
        btn_cerrar = button_box.addButton(QDialogButtonBox.Close)
        
        btn_editar.clicked.connect(lambda: [dialog.accept(), self.editar_docente(docente)])
        btn_cerrar.clicked.connect(dialog.reject)
        
        layout.addWidget(button_box)
        
        dialog.exec()
    
    def eliminar_docente(self, docente):
        """Eliminar docente con confirmación"""
        respuesta = QMessageBox.question(
            self,
            "🗑️ Confirmar Eliminación",
            f"¿Está seguro de eliminar al docente/tutor?\n\n"
            f"<b>Nombre:</b> {docente.nombre_completo}<br>"
            f"<b>CI:</b> {docente.ci_numero}-{docente.ci_expedicion}<br>"
            f"<b>Grado:</b> {docente.max_grado_academico if docente.max_grado_academico else 'No especificado'}<br><br>"
            f"<span style='color: #e74c3c;'>⚠️ Esta acción no se puede deshacer.</span>",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                # Verificar que no esté asignado a programas
                query = "SELECT COUNT(*) as count FROM programas_academicos WHERE tutor_id = ?"
                resultado = db.fetch_one(query, (docente.id,))
                
                if resultado and resultado['count'] > 0:
                    QMessageBox.warning(
                        self, "No se puede eliminar", 
                        "El docente está asignado a programas académicos.\n\n"
                        "Recomendación: Desactive al docente o reasigne los programas primero."
                    )
                    return
                
                # Eliminar docente
                docente.delete()
                
                # Mostrar mensaje de éxito
                QMessageBox.information(
                    self, "✅ Docente Eliminado", 
                    f"Docente {docente.nombre_completo} eliminado exitosamente."
                )
                
                # Recargar docentes
                self.cargar_docentes(self.current_filter)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar docente: {str(e)}")
    
    def ver_estadisticas(self):
        """Mostrar estadísticas de docentes"""
        try:
            estadisticas = DocenteModel.obtener_estadisticas()
            
            from PySide6.QtWidgets import QTextEdit, QDialog, QDialogButtonBox
            
            dialog = QDialog(self)
            dialog.setWindowTitle("📊 Estadísticas de Docentes")
            dialog.setModal(True)
            dialog.resize(500, 400)
            
            layout = QVBoxLayout(dialog)
            
            texto = f"""
            <div style="font-family: 'Segoe UI', Arial, sans-serif;">
                <h2 style="color: #2c3e50; text-align: center;">📊 ESTADÍSTICAS DE DOCENTES</h2>
                <hr style="border: 1px solid #ddd; margin: 10px 0;">
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <h3 style="color: #3498db; margin-top: 0;">📈 ESTADÍSTICAS GENERALES</h3>
                    <p><strong>• Total docentes:</strong> {estadisticas['total_docentes']}</p>
                    <p><strong>• Docentes activos:</strong> {estadisticas['docentes_activos']}</p>
                    <p><strong>• Docentes inactivos:</strong> {estadisticas['docentes_inactivos']}</p>
                </div>
            """
            
            if estadisticas['promedio_honorario_hora'] > 0:
                texto += f"""
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <h3 style="color: #3498db;">💰 ESTADÍSTICAS DE HONORARIOS</h3>
                    <p><strong>• Promedio por hora:</strong> Bs. {estadisticas['promedio_honorario_hora']:.2f}</p>
                    <p><strong>• Mínimo por hora:</strong> Bs. {estadisticas['minimo_honorario_hora']:.2f}</p>
                    <p><strong>• Máximo por hora:</strong> Bs. {estadisticas['maximo_honorario_hora']:.2f}</p>
                </div>
                """
            
            # Obtener información adicional
            from database.database import db
            query = "SELECT COUNT(DISTINCT especialidad) as especialidades FROM docentes WHERE especialidad IS NOT NULL"
            resultado = db.fetch_one(query)
            
            if resultado and resultado['especialidades']:
                texto += f"""
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px;">
                    <h3 style="color: #3498db;">🎓 INFORMACIÓN ADICIONAL</h3>
                    <p><strong>• Especialidades distintas:</strong> {resultado['especialidades']}</p>
                """
                
                query = "SELECT especialidad, COUNT(*) as cantidad FROM docentes WHERE especialidad IS NOT NULL GROUP BY especialidad ORDER BY cantidad DESC LIMIT 5"
                resultados = db.fetch_all(query)
                
                if resultados:
                    texto += "<p><strong>• Top especialidades:</strong></p><ul>"
                    for row in resultados:
                        texto += f"<li>{row['especialidad']}: {row['cantidad']} docentes</li>"
                    texto += "</ul>"
                
                texto += "</div>"
            
            texto += "</div>"
            
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setHtml(texto)
            layout.addWidget(text_edit)
            
            # Botón para cerrar
            button_box = QDialogButtonBox(QDialogButtonBox.Close)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al obtener estadísticas: {str(e)}")
    
    # ==================== PAGINACIÓN ====================
    
    def actualizar_controles_paginacion(self):
        """Actualizar estado de controles de paginación"""
        self.total_pages = max(1, (self.total_records + self.records_per_page - 1) // self.records_per_page)
        
        # Actualizar botones
        self.ui.btnPrimeraPagina.setEnabled(self.current_page > 1)
        self.ui.btnPaginaAnterior.setEnabled(self.current_page > 1)
        self.ui.btnPaginaSiguiente.setEnabled(self.current_page < self.total_pages)
        self.ui.btnUltimaPagina.setEnabled(self.current_page < self.total_pages)

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
        if self.total_pages > 0:
            self.current_page = self.total_pages
            self.cargar_docentes(self.current_filter)
    
    def cambiar_registros_pagina(self, texto):
        """Cambiar número de registros por página"""
        if texto == "Todos":
            # Para "Todos", usar un número grande pero manejable
            self.records_per_page = 10000  # En lugar de 1000
        else:
            try:
                self.records_per_page = int(texto)
            except ValueError:
                self.records_per_page = 25
        
        self.current_page = 1
        self.cargar_docentes(self.current_filter)
    
    def actualizar_contador(self):
        """Actualizar contador de registros"""
        if self.total_records == 0:
            self.ui.labelContador.setText("No hay docentes")
            self.ui.labelPaginaActual.setText("Página 0 de 0")
            return
        
        inicio = (self.current_page - 1) * self.records_per_page + 1
        fin = min(self.current_page * self.records_per_page, self.total_records)
        
        self.ui.labelContador.setText(f"Mostrando {inicio}-{fin} de {self.total_records} docentes")
        self.ui.labelPaginaActual.setText(f"Página {self.current_page} de {self.total_pages}")
    
    # ==================== MÉTODOS PARA TAMAÑO Y CIERRE ====================
    
    def sizeHint(self):
        """Sugerir tamaño apropiado para el diálogo"""
        return QSize(1200, 700)
    
    def minimumSizeHint(self):
        """Tamaño mínimo sugerido"""
        return QSize(900, 500)
    
    def cleanup_on_close(self):
        """Limpieza al cerrar el diálogo"""
        print("🔄 Limpiando diálogo de docentes...")