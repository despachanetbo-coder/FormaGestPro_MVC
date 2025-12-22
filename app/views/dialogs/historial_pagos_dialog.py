import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QProgressDialog,
    QToolButton, QFrame, QSizePolicy, QSpacerItem, QTextEdit, 
    QDialog, QFormLayout
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QSize
from PySide6.QtGui import QColor, QFont, QIcon

from app.models import EstudianteModel, MatriculaModel, PagoModel, ProgramaAcademicoModel
from app.views.generated.dialogs import Ui_HistorialPagosDialog
import logging

logger = logging.getLogger(__name__)

class HistorialPagosDialog(QDialog):
    """Diálogo para mostrar historial de pagos de un estudiante"""
    
    def __init__(self, estudiante_id, parent=None):
        super().__init__(parent)
        self.ui = Ui_HistorialPagosDialog()
        self.ui.setupUi(self)
        
        self.estudiante_id = estudiante_id
        self.setup_ui()
        self.cargar_datos()
    
    def setup_ui(self):
        """Configurar interfaz"""
        self.setWindowTitle("💰 Historial de Pagos")
        
        # Configurar tabla
        header = self.ui.tablePagos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Programa
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Monto
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Fecha
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Estado
    
    def cargar_datos(self):
        """Cargar historial de pagos del estudiante"""
        try:
            # Obtener estudiante
            estudiante = EstudianteModel.find_by_id(self.estudiante_id)
            if not estudiante:
                QMessageBox.warning(self, "Error", "Estudiante no encontrado")
                self.reject()
                return
            
            # Obtener matrículas del estudiante
            matriculas = MatriculaModel.buscar_por_estudiante(self.estudiante_id)
            
            self.ui.tablePagos.setRowCount(0)
            
            for matricula in matriculas:
                # Obtener pagos de cada matrícula
                pagos = PagoModel.buscar_por_matricula(matricula.id)
                
                for pago in pagos:
                    row = self.ui.tablePagos.rowCount()
                    self.ui.tablePagos.insertRow(row)
                    
                    # Obtener programa
                    programa = ProgramaAcademicoModel.find_by_id(matricula.programa_id)
                    programa_nombre = programa.nombre if programa else "Programa desconocido"
                    
                    self.ui.tablePagos.setItem(row, 0, QTableWidgetItem(str(pago.id)))
                    self.ui.tablePagos.setItem(row, 1, QTableWidgetItem(programa_nombre))
                    self.ui.tablePagos.setItem(row, 2, QTableWidgetItem(f"${pago.monto:.2f}"))
                    self.ui.tablePagos.setItem(row, 3, QTableWidgetItem(pago.fecha_pago))
                    
                    estado_item = QTableWidgetItem(pago.estado)
                    if pago.estado == 'CONFIRMADO':
                        estado_item.setForeground(QColor("#27ae60"))
                    elif pago.estado == 'ANULADO':
                        estado_item.setForeground(QColor("#e74c3c"))
                    self.ui.tablePagos.setItem(row, 4, estado_item)
            
            # Actualizar información del estudiante
            total_pagos = sum(p.monto for mat in matriculas for p in PagoModel.buscar_por_matricula(mat.id))
            total_matriculas = len(matriculas)
            
            self.ui.lblInfoEstudiante.setText(
                f"<b>Estudiante:</b> {estudiante.nombre_completo}<br>"
                f"<b>CI:</b> {estudiante.ci_numero}-{estudiante.ci_expedicion}<br>"
                f"<b>Total matrículas:</b> {total_matriculas}<br>"
                f"<b>Total pagos registrados:</b> ${total_pagos:.2f}"
            )
            
        except Exception as e:
            logger.error(f"Error al cargar historial de pagos: {e}")
            QMessageBox.critical(self, "Error", f"Error al cargar datos: {str(e)}")
