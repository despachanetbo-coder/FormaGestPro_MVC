# app/views/tabs/programas_tab.py
"""
Pestaña de Programas - Versión GUI de las funciones CLI
"""
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QLineEdit, QComboBox, QMessageBox, QTabWidget, QFormLayout,
    QDoubleSpinBox, QSpinBox, QDateEdit, QTextEdit, QGroupBox,
    QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor

from app.views.tabs.base_tab import BaseTab
from app.models.programa_academico_model import ProgramaAcademicoModel
from views.dialogs.programa_form_dialog import ProgramaFormDialog

class ProgramasTab(BaseTab):
    """Pestaña de gestión de programas"""
    
    def __init__(self):
        super().__init__("📚 Gestión de Programas")
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz"""
        layout = QVBoxLayout(self)
        
        # Header
        layout.addWidget(self.create_header("📚 GESTIÓN DE PROGRAMAS ACADÉMICOS"))
        
        # Panel de botones principales
        btn_panel = QWidget()
        btn_layout = QHBoxLayout(btn_panel)
        
        # Botones principales
        buttons = [
            ("➕ Crear Programa", self.crear_programa, "success"),
            ("📋 Listar Programas", self.listar_programas, "primary"),
            ("🔍 Buscar por Código", self.buscar_programa, "warning"),
            ("✏️ Editar Programa", self.editar_programa, "primary"),
            ("🎁 Configurar Promoción", self.configurar_promocion, "warning"),
            ("📊 Estadísticas", self.ver_estadisticas, "primary")
        ]
        
        for text, callback, style in buttons:
            btn = self.create_button(text, callback, style)
            btn_layout.addWidget(btn)
        
        btn_layout.addStretch()
        layout.addWidget(btn_panel)
        
        # Tabla para mostrar resultados
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Código", "Nombre", "Costo", "Cupos", 
            "Estado", "Promoción", "Acciones"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Nombre
        
        layout.addWidget(self.table)
        
        # Estatus bar
        self.status_label = QLabel("Listo")
        self.status_label.setStyleSheet("color: #7f8c8d; padding: 5px;")
        layout.addWidget(self.status_label)
    
    def crear_programa(self):
        """Diálogo para crear nuevo programa (basado en CLI)"""
        dialog = ProgramaFormDialog(self)
        if dialog.exec():
            # Obtener datos del formulario
            datos = dialog.get_datos()
            
            try:
                # Llamar a la función CLI existente
                from cli import crear_programa
                
                # Adaptar para GUI
                programa = ProgramaAcademicoModel.crear_programa(datos)
                
                QMessageBox.information(
                    self, "✅ Programa Creado",
                    f"Programa {programa.codigo} creado exitosamente!\n\n"
                    f"Nombre: {programa.nombre}\n"
                    f"Costo: Bs. {programa.costo_base:.2f}\n"
                    f"Cupos: {programa.cupos_disponibles}/{programa.cupos_totales}"
                )
                
                # Actualizar tabla
                self.listar_programas()
                
            except Exception as e:
                QMessageBox.critical(self, "❌ Error", f"Error al crear programa: {str(e)}")
    
    def listar_programas(self):
        """Listar todos los programas (basado en CLI)"""
        try:
            programas = ProgramaAcademicoModel.all()
            self.table.setRowCount(len(programas))
            
            for i, programa in enumerate(programas):
                self.table.setItem(i, 0, QTableWidgetItem(str(programa.id)))
                self.table.setItem(i, 1, QTableWidgetItem(programa.codigo))
                self.table.setItem(i, 2, QTableWidgetItem(programa.nombre))
                self.table.setItem(i, 3, QTableWidgetItem(f"Bs. {programa.costo_base:.2f}"))
                self.table.setItem(i, 4, QTableWidgetItem(
                    f"{programa.cupos_disponibles}/{programa.cupos_totales}"
                ))
                
                # Estado con color
                estado_item = QTableWidgetItem(programa.estado)
                if programa.estado == 'INICIADO':
                    estado_item.setForeground(QColor("#27ae60"))
                elif programa.estado == 'PLANIFICADO':
                    estado_item.setForeground(QColor("#f39c12"))
                self.table.setItem(i, 5, estado_item)
                
                # Promoción
                promocion_text = "✅" if programa.promocion_activa else "❌"
                self.table.setItem(i, 6, QTableWidgetItem(promocion_text))
                
                # Botón de acciones
                acciones_widget = self.create_acciones_widget(programa)
                self.table.setCellWidget(i, 7, acciones_widget)
            
            self.status_label.setText(f"Mostrando {len(programas)} programas")
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"Error al listar programas: {str(e)}")

    def crear_programa_gui(datos):
        """Versión GUI de crear programa"""
        from app.models.programa_academico_model import ProgramaAcademicoModel
        return ProgramaAcademicoModel.crear_estudiante(datos)  # Ajusta según tu modelo

    def listar_programas_gui():
        """Versión GUI de listar programas"""
        from app.models.programa_academico_model import ProgramaAcademicoModel
        return ProgramaAcademicoModel.buscar_activos()

    def buscar_programa_codigo_gui(codigo):
        """Versión GUI de buscar programa"""
        from app.models.programa_academico_model import ProgramaAcademicoModel
        return ProgramaAcademicoModel.buscar_por_codigo(codigo)