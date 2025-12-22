# app/controllers/estudiante_controller.py
"""
Controlador para la gestión de estudiantes - VERSIÓN FUNCIONAL
"""
import sys
import os
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QMessageBox, QTableWidget, QTableWidgetItem, QPushButton,
    QHBoxLayout, QVBoxLayout, QWidget, QHeaderView, QLabel, QLineEdit,
    QComboBox, QDateEdit, QCheckBox, QGroupBox, QFormLayout, QTextEdit,
    QTabWidget, QGridLayout, QFrame, QApplication, QProgressDialog,
    QDialogButtonBox, QFileDialog, QInputDialog, QProgressBar
)
from PySide6.QtCore import Qt, QDate, Signal, Slot, QTimer, QSize
from PySide6.QtGui import QColor, QFont, QIcon

from app.views.generated.dialogs.ui_estudiante_dialog import Ui_EstudianteDialog
from app.views.generated.dialogs.ui_estudiante_form_dialog import Ui_EstudianteFormDialog
from app.models.estudiante_model import EstudianteModel
from database.database import db

# ==================== CLASES DEL CONTROLADOR ====================

class EstudianteFormDialog(QDialog):
    """Diálogo para crear/editar estudiantes - VERSIÓN COMPLETA"""
    
    estudiante_guardado = Signal(dict)
    
    def __init__(self, estudiante_data=None, parent=None):
        super().__init__(parent)
        self.ui = Ui_EstudianteFormDialog()
        self.ui.setupUi(self)
        
        self.estudiante_data = estudiante_data
        self.modo_edicion = estudiante_data is not None
        
        self.setup_ui()
        self.setup_connections()
        
        if self.modo_edicion:
            self.cargar_datos()
        else:
            # Configurar fecha por defecto (18 años atrás)
            fecha_default = QDate.currentDate().addYears(-18)
            self.ui.dateFechaNacimiento.setDate(fecha_default)
    
    def setup_ui(self):
        """Configurar interfaz"""
        if self.modo_edicion:
            self.setWindowTitle(f"✏️ Editar Estudiante")
            self.ui.txtCINumero.setEnabled(False)
            self.ui.comboExpedicion.setEnabled(False)
        else:
            self.setWindowTitle("➕ Nuevo Estudiante")
        
        # Configurar validadores
        self.ui.txtCINumero.textChanged.connect(self.validar_ci)
        self.ui.txtEmail.textChanged.connect(self.validar_email)
        
        # Configurar tooltips
        self.ui.txtCINumero.setToolTip("Solo números, sin puntos ni guiones")
        self.ui.txtEmail.setToolTip("ejemplo@dominio.com")
        self.ui.txtTelefono.setToolTip("Ej: 77712345")
    
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
        """Cargar datos del estudiante en el formulario"""
        if not self.estudiante_data:
            return
        
        # Campos obligatorios
        self.ui.txtCINumero.setText(str(self.estudiante_data.get('ci_numero', '')))
        
        expedicion = self.estudiante_data.get('ci_expedicion', 'BE')
        index = self.ui.comboExpedicion.findText(expedicion)
        if index >= 0:
            self.ui.comboExpedicion.setCurrentIndex(index)
        
        self.ui.txtNombres.setText(self.estudiante_data.get('nombres', ''))
        self.ui.txtApellidos.setText(self.estudiante_data.get('apellidos', ''))
        
        # Fecha de nacimiento
        fecha_nac = self.estudiante_data.get('fecha_nacimiento')
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
            'universidad_egreso': self.ui.txtUniversidad,
            'profesion': self.ui.txtProfesion
        }
        
        for campo_db, widget in campos.items():
            valor = self.estudiante_data.get(campo_db, '')
            if valor:
                widget.setText(str(valor))
        
        # Estado activo
        activo = self.estudiante_data.get('activo', 1)
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
        
        universidad = self.ui.txtUniversidad.text().strip()
        if universidad:
            datos['universidad_egreso'] = universidad
        
        profesion = self.ui.txtProfesion.text().strip()
        if profesion:
            datos['profesion'] = profesion
        
        # Si es nuevo, verificar que no exista el CI
        if not self.modo_edicion:
            existente = EstudianteModel.buscar_por_ci(
                datos['ci_numero'], 
                datos['ci_expedicion']
            )
            if existente:
                QMessageBox.warning(
                    self, "Validación", 
                    f"Ya existe un estudiante con CI {datos['ci_numero']}-{datos['ci_expedicion']}"
                )
                return
        
        # Emitir señal con los datos
        self.estudiante_guardado.emit(datos)
        self.accept()

class EstudianteDialog(QDialog):
    """Diálogo principal de gestión de estudiantes - VERSIÓN COMPLETA"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_EstudianteDialog()
        self.ui.setupUi(self)
        
        # Configuración inicial
        self.current_page = 1
        self.records_per_page = 25
        self.total_records = 0
        self.total_pages = 1
        self.current_filter = None
        self.estudiantes_cache = []
        
        self.setup_ui()
        self.setup_connections()
        self.cargar_estudiantes_inicial()
        
        # Ajustar tamaño para que sea igual al de docentes
        self.resize(1200, 700)  # Mismo tamaño que docentes
        print("✅ Diálogo de estudiantes inicializado (versión completa)")
    
    def setup_ui(self):
        """Configurar interfaz inicial"""
        # Configurar tabla
        header = self.ui.tableEstudiantes.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # CI
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Nombre
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Email
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Teléfono
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Universidad
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Profesión
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Estado
        header.setSectionResizeMode(8, QHeaderView.Fixed)             # Acciones
        self.ui.tableEstudiantes.setColumnWidth(8, 120)
        
        # Configurar estilo de la tabla
        self.ui.tableEstudiantes.setAlternatingRowColors(True)
        self.ui.tableEstudiantes.setStyleSheet("""
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
        self.ui.statusbar.showMessage("Sistema de gestión de estudiantes listo", 3000)
    
    def setup_connections(self):
        """Conectar todas las señales"""
        # Botones de búsqueda
        self.ui.btnBuscarCI.clicked.connect(self.buscar_por_ci)
        self.ui.btnBuscarNombre.clicked.connect(self.buscar_por_nombre)
        self.ui.btnMostrarTodos.clicked.connect(self.mostrar_todos)
        self.ui.btnNuevoEstudiante.clicked.connect(self.nuevo_estudiante)
        
        # Paginación
        self.ui.btnPrimeraPagina.clicked.connect(lambda: self.cambiar_pagina(1))
        self.ui.btnPaginaAnterior.clicked.connect(self.pagina_anterior)
        self.ui.btnPaginaSiguiente.clicked.connect(self.pagina_siguiente)
        self.ui.btnUltimaPagina.clicked.connect(self.ultima_pagina)
        self.ui.comboRegistrosPagina.currentTextChanged.connect(self.cambiar_registros_pagina)
        
        # Buscar con Enter
        self.ui.txtBuscarCINumero.returnPressed.connect(self.buscar_por_ci)
        self.ui.txtBuscarNombre.returnPressed.connect(self.buscar_por_nombre)
        
        # Doble click en tabla para editar
        self.ui.tableEstudiantes.doubleClicked.connect(self.editar_estudiante_click)

        self.finished.connect(self.cleanup_on_close)
    
    def cargar_estudiantes_inicial(self):
        """Cargar estudiantes al iniciar"""
        QTimer.singleShot(100, self.mostrar_todos)
    
    # ==================== MÉTODOS DE CARGA Y PAGINACIÓN ====================
    
    def cargar_estudiantes(self, filtro=None):
        """Cargar estudiantes con paginación"""
        progress = None
        try:
            # Mostrar progreso
            progress = QProgressDialog("Cargando estudiantes...", "Cancelar", 0, 100, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setValue(10)
            progress.setAutoClose(True)
            progress.setAutoReset(True)
            QApplication.processEvents()
            
            # Limpiar tabla
            self.ui.tableEstudiantes.setRowCount(0)
            progress.setValue(30)
            
            # Obtener estudiantes
            offset = (self.current_page - 1) * self.records_per_page
            self.estudiantes_cache = self.obtener_estudiantes_paginados(filtro, offset)
            progress.setValue(60)
            
            if not self.estudiantes_cache:
                self.ui.tableEstudiantes.setRowCount(1)
                item = QTableWidgetItem("No se encontraron estudiantes")
                item.setTextAlignment(Qt.AlignCenter)
                item.setForeground(QColor("#7f8c8d"))
                self.ui.tableEstudiantes.setItem(0, 0, item)
                self.ui.tableEstudiantes.setSpan(0, 0, 1, 9)
                self.total_records = 0
            else:
                # Llenar tabla
                for i, estudiante in enumerate(self.estudiantes_cache):
                    self.agregar_fila_tabla(i, estudiante)
                
                # Obtener total de registros
                self.total_records = self.contar_estudiantes(filtro)  # Asegurar nombre correcto
            
            progress.setValue(90)
            
            # Actualizar controles
            self.actualizar_controles_paginacion()
            self.actualizar_contador()
            
            progress.setValue(100)
            self.ui.statusbar.showMessage(f"Cargados {len(self.estudiantes_cache)} estudiantes", 3000)
            
        except Exception as e:
            self.ui.statusbar.showMessage(f"Error: {str(e)}", 5000)
            QMessageBox.critical(self, "Error", f"Error cargando estudiantes: {str(e)}")
            print(f"❌ Error en cargar_estudiantes: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if progress:
                progress.close()
    
    def agregar_fila_tabla(self, fila, estudiante):
        """Agregar una fila a la tabla"""
        self.ui.tableEstudiantes.insertRow(fila)
        
        # ID
        self.ui.tableEstudiantes.setItem(fila, 0, 
            QTableWidgetItem(str(estudiante.id)))
        
        # CI completo
        ci_completo = f"{estudiante.ci_numero}-{estudiante.ci_expedicion}"
        item_ci = QTableWidgetItem(ci_completo)
        item_ci.setToolTip(f"CI: {ci_completo}")
        self.ui.tableEstudiantes.setItem(fila, 1, item_ci)
        
        # Nombre completo
        item_nombre = QTableWidgetItem(estudiante.nombre_completo)
        item_nombre.setToolTip(f"Nombre: {estudiante.nombre_completo}")
        self.ui.tableEstudiantes.setItem(fila, 2, item_nombre)
        
        # Email
        email = estudiante.email if estudiante.email else ""
        item_email = QTableWidgetItem(email)
        if email:
            item_email.setForeground(QColor("#3498db"))
            item_email.setToolTip(f"Email: {email}")
        self.ui.tableEstudiantes.setItem(fila, 3, item_email)
        
        # Teléfono
        telefono = estudiante.telefono if estudiante.telefono else ""
        item_telefono = QTableWidgetItem(telefono)
        self.ui.tableEstudiantes.setItem(fila, 4, item_telefono)
        
        # Universidad
        universidad = estudiante.universidad_egreso if estudiante.universidad_egreso else ""
        item_universidad = QTableWidgetItem(universidad)
        self.ui.tableEstudiantes.setItem(fila, 5, item_universidad)
        
        # Profesión
        profesion = estudiante.profesion if estudiante.profesion else ""
        item_profesion = QTableWidgetItem(profesion)
        self.ui.tableEstudiantes.setItem(fila, 6, item_profesion)
        
        # Estado
        if estudiante.activo:
            estado_texto = "✅ Activo"
            color = QColor("#27ae60")
        else:
            estado_texto = "❌ Inactivo"
            color = QColor("#e74c3c")
        
        item_estado = QTableWidgetItem(estado_texto)
        item_estado.setForeground(color)
        item_estado.setTextAlignment(Qt.AlignCenter)
        item_estado.setToolTip("Activo" if estudiante.activo else "Inactivo")
        self.ui.tableEstudiantes.setItem(fila, 7, item_estado)
        
        # Acciones
        acciones_widget = self.crear_widget_acciones(estudiante)
        self.ui.tableEstudiantes.setCellWidget(fila, 8, acciones_widget)
    
    def crear_widget_acciones(self, estudiante):
        """Crear widget con botones de acciones"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(3)
        
        # Botón Editar
        btn_editar = QPushButton("✏️")
        btn_editar.setToolTip("Editar estudiante")
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
        btn_editar.clicked.connect(lambda: self.editar_estudiante(estudiante))
        
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
        btn_detalles.clicked.connect(lambda: self.ver_detalles_completos(estudiante))
        
        # Botón Eliminar
        btn_eliminar = QPushButton("🗑️")
        btn_eliminar.setToolTip("Eliminar estudiante")
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
        btn_eliminar.clicked.connect(lambda: self.eliminar_estudiante(estudiante))
        
        layout.addWidget(btn_editar)
        layout.addWidget(btn_detalles)
        layout.addWidget(btn_eliminar)
        layout.addStretch()
        
        return widget
    
    def obtener_estudiantes_paginados(self, filtro=None, offset=0):
        """Obtener estudiantes con paginación"""
        query = "SELECT * FROM estudiantes"
        params = []
        
        # CORREGIDO: Manejo correcto de parámetros
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
            return [EstudianteModel(**row) for row in rows]
        except Exception as e:
            print(f"❌ Error en obtener_estudiantes_paginados: {e}")
            print(f"   Query: {query}")
            print(f"   Params: {params}")
            return []
    
    def contar_estudiantes(self, filtro=None):
        """Contar total de estudiantes"""
        query = "SELECT COUNT(*) as total FROM estudiantes"
        params = []
        
        if filtro:
            query += f" WHERE {filtro['condicion']}"
            params = filtro['params']
        
        resultado = db.fetch_one(query, tuple(params))
        return resultado['total'] if resultado else 0
    
    # ==================== MÉTODOS DE BÚSQUEDA ====================
    
    def buscar_por_ci(self):
        """Buscar estudiante por CI"""
        ci_numero = self.ui.txtBuscarCINumero.text().strip()
        expedicion = self.ui.comboBuscarExpedicion.currentText()
        
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
            self.cargar_estudiantes(filtro)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en búsqueda: {str(e)}")
            self.ui.statusbar.showMessage(f"Error en búsqueda: {str(e)}", 5000)
            return

        if self.total_records == 0:
            self.ui.statusbar.showMessage(f"No se encontraron estudiantes", 3000)
            QMessageBox.information(self, "Búsqueda", 
                f"No se encontraron estudiantes con CI: {ci_numero}")
        else:
            self.ui.statusbar.showMessage(
                f"Encontrados {self.total_records} estudiantes - {mensaje}", 3000)
    
    def buscar_por_nombre(self):
        """Buscar estudiante por nombre o apellido"""
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
        self.cargar_estudiantes(filtro)
        
        if self.total_records == 0:
            self.ui.statusbar.showMessage(f"No se encontraron estudiantes con: {nombre}", 3000)
            QMessageBox.information(self, "Búsqueda", 
                f"No se encontraron estudiantes con: {nombre}")
        else:
            self.ui.statusbar.showMessage(
                f"Encontrados {self.total_records} estudiantes para: {nombre}", 3000)
    
    def mostrar_todos(self):
        """Mostrar todos los estudiantes"""
        self.current_filter = None
        self.current_page = 1
        self.ui.txtBuscarCINumero.clear()
        self.ui.txtBuscarNombre.clear()
        self.ui.comboBuscarExpedicion.setCurrentIndex(0)
        self.cargar_estudiantes()
        self.ui.statusbar.showMessage("Mostrando todos los estudiantes", 3000)
    
    # ==================== MÉTODOS CRUD COMPLETOS ====================
    
    def nuevo_estudiante(self):
        """Abrir diálogo para nuevo estudiante"""
        dialog = EstudianteFormDialog(parent=self)
        
        def on_estudiante_guardado(datos):
            try:
                estudiante = EstudianteModel.crear_estudiante(datos)
                
                # Mostrar mensaje de éxito con detalles
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("✅ Estudiante Creado")
                msg.setText(f"Estudiante creado exitosamente!")
                msg.setInformativeText(
                    f"ID: {estudiante.id}\n"
                    f"Nombre: {estudiante.nombre_completo}\n"
                    f"CI: {estudiante.ci_numero}-{estudiante.ci_expedicion}"
                )
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                
                # Recargar estudiantes
                self.cargar_estudiantes(self.current_filter)
                
            except ValueError as e:
                QMessageBox.warning(self, "Error de Validación", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al crear estudiante: {str(e)}")
        
        dialog.estudiante_guardado.connect(on_estudiante_guardado)
        dialog.exec()
    
    def editar_estudiante_click(self, index):
        """Editar estudiante al hacer doble click"""
        if index.column() != 8:  # No es la columna de acciones
            row = index.row()
            if row < len(self.estudiantes_cache):
                self.editar_estudiante(self.estudiantes_cache[row])
    
    def editar_estudiante(self, estudiante):
        """Editar estudiante existente"""
        # Preparar datos para el formulario
        estudiante_data = {
            'id': estudiante.id,
            'ci_numero': estudiante.ci_numero,
            'ci_expedicion': estudiante.ci_expedicion,
            'nombres': estudiante.nombres,
            'apellidos': estudiante.apellidos,
            'fecha_nacimiento': estudiante.fecha_nacimiento,
            'telefono': estudiante.telefono,
            'email': estudiante.email,
            'universidad_egreso': estudiante.universidad_egreso,
            'profesion': estudiante.profesion,
            'activo': estudiante.activo
        }
        
        dialog = EstudianteFormDialog(estudiante_data=estudiante_data, parent=self)
        
        def on_estudiante_guardado(datos):
            try:
                # Actualizar estudiante
                estudiante.nombres = datos['nombres']
                estudiante.apellidos = datos['apellidos']
                estudiante.fecha_nacimiento = datos.get('fecha_nacimiento')
                estudiante.telefono = datos.get('telefono')
                estudiante.email = datos.get('email')
                estudiante.universidad_egreso = datos.get('universidad_egreso')
                estudiante.profesion = datos.get('profesion')
                estudiante.activo = datos['activo']
                
                estudiante.save()
                
                # Mostrar mensaje de éxito
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("✅ Estudiante Actualizado")
                msg.setText(f"Estudiante actualizado exitosamente!")
                msg.setInformativeText(
                    f"Nombre: {estudiante.nombre_completo}\n"
                    f"CI: {estudiante.ci_numero}-{estudiante.ci_expedicion}\n"
                    f"Estado: {'Activo' if estudiante.activo else 'Inactivo'}"
                )
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                
                # Recargar estudiantes
                self.cargar_estudiantes(self.current_filter)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al actualizar estudiante: {str(e)}")
        
        dialog.estudiante_guardado.connect(on_estudiante_guardado)
        dialog.exec()
    
    def ver_detalles_completos(self, estudiante):
        """Ver detalles completos del estudiante"""
        from PySide6.QtWidgets import QTextEdit, QDialog, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"📋 Detalles del Estudiante")
        dialog.setModal(True)
        dialog.resize(500, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Crear texto con los detalles
        edad_text = f" ({estudiante.edad} años)" if estudiante.edad else ""
        
        texto = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif;">
            <h2 style="color: #2c3e50; text-align: center;">📋 DETALLES DEL ESTUDIANTE</h2>
            <hr style="border: 1px solid #ddd; margin: 10px 0;">
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <h3 style="color: #3498db; margin-top: 0;">👤 Información Personal</h3>
                <p><strong>ID:</strong> {estudiante.id}</p>
                <p><strong>Nombre completo:</strong> {estudiante.nombre_completo}</p>
                <p><strong>CI:</strong> {estudiante.ci_numero}-{estudiante.ci_expedicion}</p>
        """
        
        if estudiante.fecha_nacimiento:
            texto += f"<p><strong>Fecha nacimiento:</strong> {estudiante.fecha_nacimiento}{edad_text}</p>"
        
        texto += f"""
                <p><strong>Fecha registro:</strong> {estudiante.fecha_registro[:10] if estudiante.fecha_registro else 'N/A'}</p>
                <p><strong>Estado:</strong> <span style="color: {'#27ae60' if estudiante.activo else '#e74c3c'}">
                    {'✅ Activo' if estudiante.activo else '❌ Inactivo'}</span></p>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <h3 style="color: #3498db;">📞 Contacto</h3>
        """
        
        if estudiante.telefono:
            texto += f"<p><strong>Teléfono:</strong> {estudiante.telefono}</p>"
        
        if estudiante.email:
            texto += f"<p><strong>Email:</strong> <a href='mailto:{estudiante.email}' style='color: #3498db;'>{estudiante.email}</a></p>"
        
        texto += """
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px;">
                <h3 style="color: #3498db;">🎓 Información Académica</h3>
        """
        
        if estudiante.universidad_egreso:
            texto += f"<p><strong>Universidad de egreso:</strong> {estudiante.universidad_egreso}</p>"
        
        if estudiante.profesion:
            texto += f"<p><strong>Profesión:</strong> {estudiante.profesion}</p>"
        
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
        
        btn_editar.clicked.connect(lambda: [dialog.accept(), self.editar_estudiante(estudiante)])
        btn_cerrar.clicked.connect(dialog.reject)
        
        layout.addWidget(button_box)
        
        dialog.exec()
    
    def eliminar_estudiante(self, estudiante):
        """Eliminar estudiante con confirmación"""
        respuesta = QMessageBox.question(
            self,
            "🗑️ Confirmar Eliminación",
            f"¿Está seguro de eliminar al estudiante?\n\n"
            f"<b>Nombre:</b> {estudiante.nombre_completo}<br>"
            f"<b>CI:</b> {estudiante.ci_numero}-{estudiante.ci_expedicion}<br><br>"
            f"<span style='color: #e74c3c;'>⚠️ Esta acción no se puede deshacer.</span>",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                # Verificar que no tenga matrículas
                query = "SELECT COUNT(*) as count FROM matriculas WHERE estudiante_id = ?"
                resultado = db.fetch_one(query, (estudiante.id,))
                
                if resultado and resultado['count'] > 0:
                    QMessageBox.warning(
                        self, "No se puede eliminar", 
                        "El estudiante tiene matrículas registradas.\n\n"
                        "Recomendación: Desactive al estudiante en lugar de eliminarlo."
                    )
                    return
                
                # Eliminar estudiante
                estudiante.delete()
                
                # Mostrar mensaje de éxito
                QMessageBox.information(
                    self, "✅ Estudiante Eliminado", 
                    f"Estudiante {estudiante.nombre_completo} eliminado exitosamente."
                )
                
                # Recargar estudiantes
                self.cargar_estudiantes(self.current_filter)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar estudiante: {str(e)}")
    
    # ==================== PAGINACIÓN ====================
    
    def actualizar_controles_paginacion(self):
        """Actualizar estado de controles de paginación"""
        self.total_pages = max(1, (self.total_records + self.records_per_page - 1) // self.records_per_page)
        
        # Actualizar botones
        self.ui.btnPrimeraPagina.setEnabled(self.current_page > 1)
        self.ui.btnPaginaAnterior.setEnabled(self.current_page > 1)
        self.ui.btnPaginaSiguiente.setEnabled(self.current_page < self.total_pages)
        self.ui.btnUltimaPagina.setEnabled(self.current_page < self.total_pages)

# ==================== MÉTODOS NECESARIOS PARA INTEGRACIÓN ====================

    def cambiar_pagina(self, pagina):
        """Cambiar a página específica"""
        if 1 <= pagina <= self.total_pages:
            self.current_page = pagina
            self.cargar_estudiantes(self.current_filter)
    
    def pagina_anterior(self):
        """Ir a página anterior"""
        if self.current_page > 1:
            self.current_page -= 1
            self.cargar_estudiantes(self.current_filter)
    
    def pagina_siguiente(self):
        """Ir a página siguiente"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.cargar_estudiantes(self.current_filter)
    
    def ultima_pagina(self):
        """Ir a última página"""
        if self.total_pages > 0:
            self.current_page = self.total_pages
            self.cargar_estudiantes(self.current_filter)
    
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
        self.cargar_estudiantes(self.current_filter)
    
    def actualizar_contador(self):
        """Actualizar contador de registros"""
        if self.total_records == 0:
            self.ui.labelContador.setText("No hay estudiantes")
            self.ui.labelPaginaActual.setText("Página 0 de 0")
            return
        
        inicio = (self.current_page - 1) * self.records_per_page + 1
        fin = min(self.current_page * self.records_per_page, self.total_records)
        
        self.ui.labelContador.setText(f"Mostrando {inicio}-{fin} de {self.total_records} estudiantes")
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
        print("🔄 Limpiando diálogo de estudiantes...")
    
    # MODIFICA el método setup_connections existente para agregar:
    # (Busca el método setup_connections y agrega esta línea al final)
    # self.finished.connect(self.cleanup_on_close)