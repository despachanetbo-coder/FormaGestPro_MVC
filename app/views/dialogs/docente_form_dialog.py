# app/views/dialogs/docente_form_dialog.py
"""
Diálogo para formulario de docentes en FormaGestPro_MVC
"""

import os
from datetime import datetime, date
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QDateEdit,
    QTextEdit, QMessageBox, QFileDialog, QCheckBox,
    QGroupBox, QWidget, QSpacerItem, QSizePolicy,
    QDialogButtonBox, QTabWidget, QScrollArea, QGridLayout
)
from PySide6.QtCore import Qt, QDate, Signal, Slot
from PySide6.QtGui import QFont, QPixmap, QIcon

from app.controllers.docente_form_controller import DocenteFormController
from app.models.docente_model import DocenteModel


class DocenteFormDialog(QDialog):
    """Diálogo para crear/editar docentes"""
    
    docente_guardado = Signal(dict)
    docente_actualizado = Signal(int, dict)
    
    def __init__(self, docente_data=None, modo_lectura=False, parent=None, controller=None):
        super().__init__(parent)
        
        self.docente_data = docente_data or {}
        self.modo_lectura = modo_lectura
        self.docente_id = docente_data.get('id') if docente_data else None
        
        # Inicializar controlador
        self.controller = controller or DocenteFormController()
        
        # Configurar ventana
        if modo_lectura:
            self.setWindowTitle("👨‍🏫 Detalles del Docente")
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        elif docente_data:
            self.setWindowTitle("✏️ Editar Docente")
        else:
            self.setWindowTitle("➕ Nuevo Docente")
        
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        
        self.setup_ui()
        
        if self.docente_data:
            self.cargar_datos()
        
        if self.modo_lectura:
            self.set_readonly_mode(True)
    
    def setup_ui(self):
        """Configurar interfaz del diálogo"""
        main_layout = QVBoxLayout(self)
        
        # Crear pestañas para organizar el formulario
        tab_widget = QTabWidget()
        
        # Pestaña 1: Información Personal
        personal_tab = QWidget()
        self.setup_personal_tab(personal_tab)
        tab_widget.addTab(personal_tab, "📝 Información Personal")
        
        # Pestaña 2: Información Profesional
        profesional_tab = QWidget()
        self.setup_profesional_tab(profesional_tab)
        tab_widget.addTab(profesional_tab, "🎓 Información Profesional")
        
        main_layout.addWidget(tab_widget)
        
        # Sección de botones
        button_layout = QHBoxLayout()
        
        if not self.modo_lectura:
            self.btn_guardar = QPushButton("💾 Guardar")
            self.btn_guardar.clicked.connect(self.guardar_docente)
            self.btn_guardar.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    font-weight: bold;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            button_layout.addWidget(self.btn_guardar)
        
        self.btn_cancelar = QPushButton("❌ Cancelar")
        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        button_layout.addWidget(self.btn_cancelar)
        
        if self.modo_lectura:
            self.btn_cerrar = QPushButton("👋 Cerrar")
            self.btn_cerrar.clicked.connect(self.accept)
            self.btn_cerrar.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    font-weight: bold;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #0b7dda;
                }
            """)
            button_layout.addWidget(self.btn_cerrar)
        
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
    
    def setup_personal_tab(self, parent):
        """Configurar pestaña de información personal"""
        layout = QVBoxLayout(parent)
        
        # Scroll area para formulario largo
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Grupo: Datos de Identificación
        identificacion_group = QGroupBox("🆔 Datos de Identificación")
        identificacion_layout = QFormLayout()
        
        # CI Número
        self.txt_ci_numero = QLineEdit()
        self.txt_ci_numero.setPlaceholderText("Ej: 1234567")
        self.txt_ci_numero.setMaximumWidth(200)
        identificacion_layout.addRow("CI Número:", self.txt_ci_numero)
        
        # CI Expedición
        self.cmb_ci_expedicion = QComboBox()
        self.cmb_ci_expedicion.addItems(['', 'BE', 'CH', 'CB', 'LP', 'OR', 'PD', 'PT', 'SC', 'TJ', 'EX'])
        self.cmb_ci_expedicion.setMaximumWidth(100)
        identificacion_layout.addRow("Expedición:", self.cmb_ci_expedicion)
        
        identificacion_group.setLayout(identificacion_layout)
        scroll_layout.addWidget(identificacion_group)
        
        # Grupo: Datos Personales
        personal_group = QGroupBox("👤 Datos Personales")
        personal_layout = QFormLayout()
        
        # Nombres
        self.txt_nombres = QLineEdit()
        self.txt_nombres.setPlaceholderText("Ej: Juan Carlos")
        personal_layout.addRow("Nombres:*", self.txt_nombres)
        
        # Apellidos
        self.txt_apellidos = QLineEdit()
        self.txt_apellidos.setPlaceholderText("Ej: Pérez Gómez")
        personal_layout.addRow("Apellidos:*", self.txt_apellidos)
        
        # Fecha de Nacimiento
        self.date_fecha_nacimiento = QDateEdit()
        self.date_fecha_nacimiento.setCalendarPopup(True)
        self.date_fecha_nacimiento.setDate(QDate.currentDate().addYears(-30))
        self.date_fecha_nacimiento.setMaximumDate(QDate.currentDate())
        self.date_fecha_nacimiento.setDisplayFormat("dd/MM/yyyy")
        personal_layout.addRow("Fecha Nacimiento:", self.date_fecha_nacimiento)
        
        personal_group.setLayout(personal_layout)
        scroll_layout.addWidget(personal_group)
        
        # Grupo: Contacto
        contacto_group = QGroupBox("📞 Información de Contacto")
        contacto_layout = QFormLayout()
        
        # Teléfono
        self.txt_telefono = QLineEdit()
        self.txt_telefono.setPlaceholderText("Ej: 77712345")
        contacto_layout.addRow("Teléfono:", self.txt_telefono)
        
        # Email
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("Ej: juan.perez@email.com")
        contacto_layout.addRow("Email:", self.txt_email)
        
        contacto_group.setLayout(contacto_layout)
        scroll_layout.addWidget(contacto_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
    
    def setup_profesional_tab(self, parent):
        """Configurar pestaña de información profesional"""
        layout = QVBoxLayout(parent)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Grupo: Formación Académica
        formacion_group = QGroupBox("🎓 Formación Académica")
        formacion_layout = QFormLayout()
        
        # Grado Académico
        self.cmb_grado_academico = QComboBox()
        self.cmb_grado_academico.addItems(['', 'TÉCNICO', 'LICENCIATURA', 'MAESTRÍA', 'DOCTORADO', 'POST-DOCTORADO'])
        formacion_layout.addRow("Grado Académico:", self.cmb_grado_academico)
        
        # Especialidad
        self.txt_especialidad = QLineEdit()
        self.txt_especialidad.setPlaceholderText("Ej: Ingeniería de Sistemas")
        formacion_layout.addRow("Especialidad:", self.txt_especialidad)
        
        formacion_group.setLayout(formacion_layout)
        scroll_layout.addWidget(formacion_group)
        
        # Grupo: Información Laboral
        laboral_group = QGroupBox("💼 Información Laboral")
        laboral_layout = QFormLayout()
        
        # Honorario por Hora
        self.txt_honorario_hora = QLineEdit()
        self.txt_honorario_hora.setPlaceholderText("Ej: 50.00")
        self.txt_honorario_hora.setMaximumWidth(150)
        laboral_layout.addRow("Honorario/Hora (Bs.):", self.txt_honorario_hora)
        
        laboral_group.setLayout(laboral_layout)
        scroll_layout.addWidget(laboral_group)
        
        # Grupo: Documentación
        documentacion_group = QGroupBox("📄 Documentación")
        documentacion_layout = QVBoxLayout()
        
        # Curriculum
        curriculum_layout = QHBoxLayout()
        self.txt_curriculum_path = QLineEdit()
        self.txt_curriculum_path.setReadOnly(True)
        self.txt_curriculum_path.setPlaceholderText("Ruta del currículum...")
        
        self.btn_buscar_curriculum = QPushButton("📁 Buscar...")
        self.btn_buscar_curriculum.clicked.connect(self.buscar_curriculum)
        
        curriculum_layout.addWidget(QLabel("Currículum:"))
        curriculum_layout.addWidget(self.txt_curriculum_path)
        curriculum_layout.addWidget(self.btn_buscar_curriculum)
        
        documentacion_layout.addLayout(curriculum_layout)
        
        # Observaciones
        self.txt_observaciones = QTextEdit()
        self.txt_observaciones.setPlaceholderText("Observaciones adicionales...")
        self.txt_observaciones.setMaximumHeight(100)
        documentacion_layout.addWidget(QLabel("Observaciones:"))
        documentacion_layout.addWidget(self.txt_observaciones)
        
        documentacion_group.setLayout(documentacion_layout)
        scroll_layout.addWidget(documentacion_group)
        
        # Estado (solo para edición)
        if self.docente_id:
            estado_group = QGroupBox("⚙️ Estado del Registro")
            estado_layout = QFormLayout()
            
            self.chk_activo = QCheckBox("Activo")
            self.chk_activo.setChecked(True)
            estado_layout.addRow("Estado:", self.chk_activo)
            
            estado_group.setLayout(estado_layout)
            scroll_layout.addWidget(estado_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
    
    def set_readonly_mode(self, readonly):
        """Establecer todos los campos en modo lectura"""
        widgets = [
            self.txt_ci_numero, self.cmb_ci_expedicion,
            self.txt_nombres, self.txt_apellidos,
            self.date_fecha_nacimiento, self.txt_telefono,
            self.txt_email, self.cmb_grado_academico,
            self.txt_especialidad, self.txt_honorario_hora,
            self.txt_curriculum_path, self.txt_observaciones
        ]
        
        for widget in widgets:
            if hasattr(widget, 'setReadOnly'):
                widget.setReadOnly(readonly)
            elif hasattr(widget, 'setEnabled'):
                widget.setEnabled(not readonly)
        
        if hasattr(self, 'chk_activo'):
            self.chk_activo.setEnabled(not readonly)
        
        if hasattr(self, 'btn_buscar_curriculum'):
            self.btn_buscar_curriculum.setEnabled(not readonly)
        
        if hasattr(self, 'btn_guardar'):
            self.btn_guardar.setEnabled(not readonly)
    
    def cargar_datos(self):
        """Cargar datos del docente en el formulario"""
        if not self.docente_data:
            return
        
        try:
            # Datos de identificación
            self.txt_ci_numero.setText(str(self.docente_data.get('ci_numero', '')))
            
            expedicion = self.docente_data.get('ci_expedicion', '')
            index = self.cmb_ci_expedicion.findText(expedicion)
            if index >= 0:
                self.cmb_ci_expedicion.setCurrentIndex(index)
            
            # Datos personales
            self.txt_nombres.setText(self.docente_data.get('nombres', ''))
            self.txt_apellidos.setText(self.docente_data.get('apellidos', ''))
            
            # Fecha de nacimiento
            fecha_nac = self.docente_data.get('fecha_nacimiento')
            if fecha_nac:
                if isinstance(fecha_nac, str):
                    qdate = QDate.fromString(fecha_nac, Qt.ISODate)
                else:
                    qdate = QDate(fecha_nac.year, fecha_nac.month, fecha_nac.day)
                if qdate.isValid():
                    self.date_fecha_nacimiento.setDate(qdate)
            
            # Contacto
            self.txt_telefono.setText(self.docente_data.get('telefono', ''))
            self.txt_email.setText(self.docente_data.get('email', ''))
            
            # Información profesional
            grado = self.docente_data.get('max_grado_academico', '')
            index = self.cmb_grado_academico.findText(grado.upper() if grado else '')
            if index >= 0:
                self.cmb_grado_academico.setCurrentIndex(index)
            
            self.txt_especialidad.setText(self.docente_data.get('especialidad', ''))
            
            # Honorario
            honorario = self.docente_data.get('honorario_hora', '')
            if honorario:
                self.txt_honorario_hora.setText(str(float(honorario)))
            
            # Documentación
            self.txt_curriculum_path.setText(self.docente_data.get('curriculum_path', ''))
            self.txt_observaciones.setPlainText(self.docente_data.get('observaciones', ''))
            
            # Estado
            if hasattr(self, 'chk_activo'):
                activo = self.docente_data.get('activo', True)
                self.chk_activo.setChecked(bool(activo))
        
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar datos: {str(e)}")
    
    def buscar_curriculum(self):
        """Abrir diálogo para buscar archivo de currículum"""
        file_filter = "Documentos PDF (*.pdf);;Documentos Word (*.doc *.docx);;Todos los archivos (*.*)"
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Currículum",
            "",
            file_filter
        )
        
        if file_path:
            self.txt_curriculum_path.setText(file_path)
    
    def obtener_datos_formulario(self):
        """Obtener datos del formulario como diccionario"""
        datos = {
            'ci_numero': self.txt_ci_numero.text().strip(),
            'ci_expedicion': self.cmb_ci_expedicion.currentText(),
            'nombres': self.txt_nombres.text().strip(),
            'apellidos': self.txt_apellidos.text().strip(),
            'telefono': self.txt_telefono.text().strip(),
            'email': self.txt_email.text().strip().lower(),
            'max_grado_academico': self.cmb_grado_academico.currentText(),
            'especialidad': self.txt_especialidad.text().strip(),
            'observaciones': self.txt_observaciones.toPlainText().strip(),
            'curriculum_path': self.txt_curriculum_path.text().strip()
        }
        
        # Fecha de nacimiento
        qdate = self.date_fecha_nacimiento.date()
        if qdate.isValid():
            datos['fecha_nacimiento'] = qdate.toString(Qt.ISODate)
        
        # Honorario por hora
        honorario_text = self.txt_honorario_hora.text().strip()
        if honorario_text:
            try:
                datos['honorario_hora'] = float(honorario_text)
            except ValueError:
                datos['honorario_hora'] = 0.0
        else:
            datos['honorario_hora'] = 0.0
        
        # Estado (solo para actualización)
        if hasattr(self, 'chk_activo'):
            datos['activo'] = 1 if self.chk_activo.isChecked() else 0
        
        return datos
    
    def validar_formulario(self):
        """Validar datos del formulario"""
        errores = []
        
        # Validar campos requeridos
        if not self.txt_ci_numero.text().strip():
            errores.append("El número de CI es requerido")
        elif not self.txt_ci_numero.text().strip().isdigit():
            errores.append("El CI debe contener solo números")
        
        if not self.txt_nombres.text().strip():
            errores.append("Los nombres son requeridos")
        
        if not self.txt_apellidos.text().strip():
            errores.append("Los apellidos son requeridos")
        
        # Validar email
        email = self.txt_email.text().strip()
        if email and ('@' not in email or '.' not in email.split('@')[-1]):
            errores.append("Formato de email inválido")
        
        # Validar teléfono
        telefono = self.txt_telefono.text().strip()
        if telefono and not telefono.replace('+', '').replace(' ', '').isdigit():
            errores.append("El teléfono debe contener solo números")
        
        # Validar honorario
        honorario_text = self.txt_honorario_hora.text().strip()
        if honorario_text:
            try:
                honorario = float(honorario_text)
                if honorario < 0:
                    errores.append("El honorario no puede ser negativo")
                if honorario > 10000:  # Límite razonable
                    errores.append("El honorario es demasiado alto")
            except ValueError:
                errores.append("Honorario inválido. Debe ser un número")
        
        return errores
    
    @Slot()
    def guardar_docente(self):
        """Guardar o actualizar docente"""
        # Validar formulario
        errores = self.validar_formulario()
        if errores:
            QMessageBox.warning(self, "Errores de validación", "\n".join(errores))
            return
        
        datos = self.obtener_datos_formulario()
        
        try:
            if self.docente_id:
                # Actualizar docente existente
                success, message, docente = self.controller.actualizar_docente(
                    self.docente_id, datos
                )
                
                if success:
                    QMessageBox.information(self, "✅ Éxito", message)
                    self.docente_actualizado.emit(self.docente_id, datos)
                    self.accept()
                else:
                    QMessageBox.critical(self, "❌ Error", message)
            else:
                # Crear nuevo docente
                success, message, docente = self.controller.crear_docente(datos)
                
                if success:
                    QMessageBox.information(self, "✅ Éxito", message)
                    datos['id'] = docente.id
                    self.docente_guardado.emit(datos)
                    self.accept()
                else:
                    QMessageBox.critical(self, "❌ Error", message)
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ Error del sistema",
                f"Error inesperado: {str(e)}"
            )


class DocenteInfoDialog(QDialog):
    """Diálogo simplificado para mostrar información del docente"""
    
    def __init__(self, docente_id, parent=None, controller=None):
        super().__init__(parent)
        
        self.docente_id = docente_id
        self.controller = controller or DocenteFormController()
        
        self.setWindowTitle("👨‍🏫 Información del Docente")
        self.setMinimumWidth(500)
        
        self.setup_ui()
        self.cargar_informacion()
    
    def setup_ui(self):
        """Configurar interfaz del diálogo"""
        layout = QVBoxLayout(self)
        
        # Área de scroll para contenido largo
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Información personal
        personal_group = QGroupBox("Información Personal")
        personal_layout = QFormLayout()
        
        self.lbl_nombre = QLabel()
        self.lbl_nombre.setStyleSheet("font-weight: bold; font-size: 14px;")
        personal_layout.addRow("Nombre:", self.lbl_nombre)
        
        self.lbl_ci = QLabel()
        personal_layout.addRow("CI:", self.lbl_ci)
        
        self.lbl_fecha_nac = QLabel()
        personal_layout.addRow("Fecha Nacimiento:", self.lbl_fecha_nac)
        
        self.lbl_edad = QLabel()
        personal_layout.addRow("Edad:", self.lbl_edad)
        
        self.lbl_telefono = QLabel()
        personal_layout.addRow("Teléfono:", self.lbl_telefono)
        
        self.lbl_email = QLabel()
        personal_layout.addRow("Email:", self.lbl_email)
        
        personal_group.setLayout(personal_layout)
        content_layout.addWidget(personal_group)
        
        # Información profesional
        profesional_group = QGroupBox("Información Profesional")
        profesional_layout = QFormLayout()
        
        self.lbl_grado = QLabel()
        profesional_layout.addRow("Grado Académico:", self.lbl_grado)
        
        self.lbl_especialidad = QLabel()
        profesional_layout.addRow("Especialidad:", self.lbl_especialidad)
        
        self.lbl_honorario = QLabel()
        profesional_layout.addRow("Honorario/Hora:", self.lbl_honorario)
        
        self.lbl_curriculum = QLabel()
        self.lbl_curriculum.setWordWrap(True)
        profesional_layout.addRow("Curriculum:", self.lbl_curriculum)
        
        profesional_group.setLayout(profesional_layout)
        content_layout.addWidget(profesional_group)
        
        # Estado
        estado_group = QGroupBox("Estado")
        estado_layout = QFormLayout()
        
        self.lbl_estado = QLabel()
        estado_layout.addRow("Estado:", self.lbl_estado)
        
        self.lbl_fecha_registro = QLabel()
        estado_layout.addRow("Fecha Registro:", self.lbl_fecha_registro)
        
        estado_group.setLayout(estado_layout)
        content_layout.addWidget(estado_group)
        
        content_layout.addStretch()
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.accept)
        button_layout.addWidget(btn_cerrar)
        
        layout.addLayout(button_layout)
    
    def cargar_informacion(self):
        """Cargar información del docente"""
        try:
            docente = self.controller.obtener_docente(self.docente_id)
            
            if not docente:
                QMessageBox.warning(self, "Error", "No se encontró el docente")
                self.reject()
                return
            
            # Información personal
            self.lbl_nombre.setText(f"{docente.nombres} {docente.apellidos}")
            
            ci_completo = docente.ci_numero or ""
            if docente.ci_expedicion:
                ci_completo += f" {docente.ci_expedicion}"
            self.lbl_ci.setText(ci_completo)
            
            if docente.fecha_nacimiento:
                self.lbl_fecha_nac.setText(str(docente.fecha_nacimiento))
                
                # Calcular edad
                if isinstance(docente.fecha_nacimiento, str):
                    birth_date = datetime.strptime(docente.fecha_nacimiento, '%Y-%m-%d').date()
                else:
                    birth_date = docente.fecha_nacimiento
                
                today = date.today()
                edad = today.year - birth_date.year - (
                    (today.month, today.day) < (birth_date.month, birth_date.day)
                )
                self.lbl_edad.setText(f"{edad} años")
            
            self.lbl_telefono.setText(docente.telefono or "No especificado")
            self.lbl_email.setText(docente.email or "No especificado")
            
            # Información profesional
            self.lbl_grado.setText(docente.max_grado_academico or "No especificado")
            self.lbl_especialidad.setText(docente.especialidad or "No especificado")
            
            if docente.honorario_hora:
                self.lbl_honorario.setText(f"Bs. {float(docente.honorario_hora):,.2f}")
            else:
                self.lbl_honorario.setText("No especificado")
            
            self.lbl_curriculum.setText(docente.curriculum_path or "No cargado")
            
            # Estado
            estado = "✅ Activo" if docente.activo else "❌ Inactivo"
            self.lbl_estado.setText(estado)
            
            if docente.created_at:
                self.lbl_fecha_registro.setText(str(docente.created_at))
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar información: {str(e)}")