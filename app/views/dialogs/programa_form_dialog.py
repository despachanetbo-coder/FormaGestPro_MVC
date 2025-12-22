# app/views/tabs/programas/dialogs/programa_form_dialog.py
"""
Diálogo para crear/editar programas - Versión GUI
"""
import sys
from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QMessageBox, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QFormLayout, QLineEdit, QTextEdit,
    QSpinBox, QDoubleSpinBox, QComboBox, QDateEdit, QCheckBox,
    QTabWidget, QWidget, QDialogButtonBox
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont

try:
    from app.views.generated.modules.programas.ui_programa_form import Ui_ProgramaFormDialog
    print("✅ UI de programa_form cargada correctamente")
except ImportError as e:
    print(f"❌ Error cargando UI: {e}")
    # Crear UI básica como fallback
    class Ui_ProgramaFormDialog:
        def setupUi(self, ProgramaFormDialog):
            pass

from app.models.programa_academico_model import ProgramaModel
from app.models.docente_model import DocenteModel
from utils.calculos_financieros import (
    calcular_descuento_exacto,
    calcular_porcentaje_para_monto_final,
    formatear_moneda,
    redondear_a_entero_cercano
)

class ProgramaFormDialog(QDialog):
    """Diálogo para crear/editar programas académicos"""
    
    programa_guardado = Signal(dict)  # Señal cuando se guarda
    
    def __init__(self, programa_data=None, parent=None):
        super().__init__(parent)
        self.ui = Ui_ProgramaFormDialog()
        self.ui.setupUi(self)
        
        self.programa_data = programa_data
        self.modo_edicion = programa_data is not None
        
        self.setup_ui()
        self.setup_connections()
        self.cargar_docentes()
        
        if self.modo_edicion:
            self.cargar_datos()
            self.setWindowTitle(f"✏️ Editar Programa")
        else:
            self.setWindowTitle("➕ Nuevo Programa Académico")
            # Configurar fechas por defecto
            hoy = QDate.currentDate()
            self.ui.dateFechaInicio.setDate(hoy.addMonths(1))
            self.ui.dateFechaFin.setDate(hoy.addMonths(4))
    
    def setup_ui(self):
        """Configurar interfaz"""
        # Configurar validadores
        self.ui.txtCodigo.textChanged.connect(self.validar_codigo)
        
        # Configurar tooltips
        self.ui.txtCodigo.setToolTip("Ej: DIP-001, CUR-2024-01")
        self.ui.txtNombre.setToolTip("Nombre completo del programa académico")
        self.ui.spinCostoBase.setToolTip("Costo base de la colegiatura")
        self.ui.spinDescuentoContado.setToolTip("Descuento por pago al contado")
        self.ui.spinCuposTotales.setToolTip("Número total de cupos disponibles")
        
        # Configurar fechas
        self.ui.dateFechaInicio.setDate(QDate.currentDate().addMonths(1))
        self.ui.dateFechaFin.setDate(QDate.currentDate().addMonths(4))
        self.ui.dateFechaInicio.setMinimumDate(QDate.currentDate())
        self.ui.dateFechaFin.setMinimumDate(QDate.currentDate().addDays(1))
        
        # Conectar cambios para actualizar resumen
        self.ui.spinCostoInscripcion.valueChanged.connect(self.actualizar_resumen_costos)
        self.ui.spinCostoMatricula.valueChanged.connect(self.actualizar_resumen_costos)
        self.ui.spinCostoBase.valueChanged.connect(self.actualizar_resumen_costos)
        self.ui.spinDescuentoContado.valueChanged.connect(self.actualizar_resumen_costos)
        
        # Estado inicial del resumen
        self.actualizar_resumen_costos()
    
    def setup_connections(self):
        """Configurar conexiones de señales"""
        self.ui.buttonBox.accepted.connect(self.validar_y_guardar)
        self.ui.buttonBox.rejected.connect(self.reject)
        
        # Cuotas mensuales
        self.ui.checkCuotasMensuales.toggled.connect(
            lambda checked: self.ui.spinDiasEntreCuotas.setEnabled(not checked)
        )
    
    def cargar_docentes(self):
        """Cargar lista de docentes disponibles"""
        try:
            docentes = DocenteModel.buscar_activos()
            self.ui.comboTutor.clear()
            self.ui.comboTutor.addItem("-- Sin tutor asignado --", None)
            
            for docente in docentes:
                nombre_completo = docente.nombre_completo
                if docente.max_grado_academico:
                    nombre_completo = f"{docente.max_grado_academico} {nombre_completo}"
                self.ui.comboTutor.addItem(nombre_completo, docente.id)
        except Exception as e:
            print(f"⚠️ Error cargando docentes: {e}")
    
    def validar_codigo(self, texto):
        """Validar formato de código"""
        if texto:
            # Convertir a mayúsculas y eliminar espacios
            texto = texto.strip().upper()
            if self.ui.txtCodigo.text() != texto:
                self.ui.txtCodigo.setText(texto)
                self.ui.txtCodigo.setCursorPosition(len(texto))
    
    def cargar_datos(self):
        """Cargar datos del programa en el formulario"""
        if not self.programa_data:
            return
        
        # Campos básicos
        self.ui.txtCodigo.setText(self.programa_data.get('codigo', ''))
        self.ui.txtNombre.setText(self.programa_data.get('nombre', ''))
        
        if self.programa_data.get('descripcion'):
            self.ui.txtDescripcion.setText(self.programa_data.get('descripcion'))
        
        # Duraciones
        if self.programa_data.get('duracion_semanas'):
            meses = self.programa_data.get('duracion_semanas', 0) // 4
            self.ui.spinDuracionMeses.setValue(meses)
        
        if self.programa_data.get('horas_totales'):
            self.ui.spinHorasTotales.setValue(self.programa_data.get('horas_totales'))
        
        # Costos
        self.ui.spinCostoInscripcion.setValue(self.programa_data.get('costo_inscripcion', 0))
        self.ui.spinCostoMatricula.setValue(self.programa_data.get('costo_matricula', 0))
        self.ui.spinCostoBase.setValue(self.programa_data.get('costo_base', 0))
        self.ui.spinDescuentoContado.setValue(self.programa_data.get('descuento_contado', 0))
        
        # Cupos
        self.ui.spinCuposTotales.setValue(self.programa_data.get('cupos_totales', 25))
        
        # Estado
        estado = self.programa_data.get('estado', 'PLANIFICADO')
        index = self.ui.comboEstado.findText(estado)
        if index >= 0:
            self.ui.comboEstado.setCurrentIndex(index)
        
        # Fechas
        if self.programa_data.get('fecha_inicio_planificada'):
            try:
                qdate = QDate.fromString(self.programa_data['fecha_inicio_planificada'], 'yyyy-MM-dd')
                if qdate.isValid():
                    self.ui.dateFechaInicio.setDate(qdate)
            except:
                pass
        
        # Tutor
        tutor_id = self.programa_data.get('tutor_id')
        if tutor_id:
            for i in range(self.ui.comboTutor.count()):
                if self.ui.comboTutor.itemData(i) == tutor_id:
                    self.ui.comboTutor.setCurrentIndex(i)
                    break
        
        # Configuración de cuotas
        if 'cuotas_mensuales' in self.programa_data:
            self.ui.checkCuotasMensuales.setChecked(bool(self.programa_data['cuotas_mensuales']))
        
        if 'dias_entre_cuotas' in self.programa_data:
            self.ui.spinDiasEntreCuotas.setValue(self.programa_data['dias_entre_cuotas'])
    
    def actualizar_resumen_costos(self):
        """Actualizar resumen de costos en tiempo real"""
        costo_inscripcion = self.ui.spinCostoInscripcion.value()
        costo_matricula = self.ui.spinCostoMatricula.value()
        costo_base = self.ui.spinCostoBase.value()
        descuento_contado = self.ui.spinDescuentoContado.value()
        
        # Calcular total sin descuento
        total_sin_descuento = costo_inscripcion + costo_matricula + costo_base
        
        # Calcular con descuento contado
        if descuento_contado > 0:
            descuento_bs, colegiatura_con_descuento = calcular_descuento_exacto(
                costo_base, descuento_contado
            )
            total_con_descuento = costo_inscripcion + costo_matricula + colegiatura_con_descuento
            ahorro = total_sin_descuento - total_con_descuento
            
            resumen = f"""
            <div style='font-family: Arial; font-size: 11pt;'>
            <b>💰 RESUMEN DE COSTOS:</b><br>
            • Inscripción: <b>Bs. {costo_inscripcion:,.2f}</b><br>
            • Matrícula: <b>Bs. {costo_matricula:,.2f}</b><br>
            • Colegiatura: <b>Bs. {costo_base:,.2f}</b><br>
            • <span style='color: #27ae60;'>Descuento contado ({descuento_contado:.1f}%): Bs. {descuento_bs:,.2f}</span><br>
            <hr>
            • Total sin descuento: <b>Bs. {total_sin_descuento:,.2f}</b><br>
            • Total con descuento: <b>Bs. {total_con_descuento:,.2f}</b><br>
            • <span style='color: #e74c3c;'>Ahorro: Bs. {ahorro:,.2f}</span><br>
            </div>
            """
        else:
            resumen = f"""
            <div style='font-family: Arial; font-size: 11pt;'>
            <b>💰 RESUMEN DE COSTOS:</b><br>
            • Inscripción: <b>Bs. {costo_inscripcion:,.2f}</b><br>
            • Matrícula: <b>Bs. {costo_matricula:,.2f}</b><br>
            • Colegiatura: <b>Bs. {costo_base:,.2f}</b><br>
            <hr>
            • <b>TOTAL A PAGAR: Bs. {total_sin_descuento:,.2f}</b><br>
            </div>
            """
        
        self.ui.labelResumenCostos.setText(resumen)
    
    def obtener_datos_formulario(self):
        """Obtener y validar datos del formulario"""
        errores = []
        
        # Validar campos obligatorios
        codigo = self.ui.txtCodigo.text().strip()
        if not codigo:
            errores.append("El código del programa es obligatorio")
        
        nombre = self.ui.txtNombre.text().strip()
        if not nombre:
            errores.append("El nombre del programa es obligatorio")
        
        costo_base = self.ui.spinCostoBase.value()
        if costo_base <= 0:
            errores.append("La colegiatura debe ser mayor a 0")
        
        cupos_totales = self.ui.spinCuposTotales.value()
        if cupos_totales <= 0:
            errores.append("Los cupos totales deben ser mayor a 0")
        
        # Validar fechas
        fecha_inicio = self.ui.dateFechaInicio.date()
        fecha_fin = self.ui.dateFechaFin.date()
        if fecha_inicio >= fecha_fin:
            errores.append("La fecha de fin debe ser posterior a la de inicio")
        
        return errores, {
            'codigo': codigo,
            'nombre': nombre,
            'descripcion': self.ui.txtDescripcion.toPlainText().strip(),
            'duracion_semanas': self.ui.spinDuracionMeses.value() * 4,
            'horas_totales': self.ui.spinHorasTotales.value(),
            'costo_inscripcion': self.ui.spinCostoInscripcion.value(),
            'costo_matricula': self.ui.spinCostoMatricula.value(),
            'costo_base': costo_base,
            'descuento_contado': self.ui.spinDescuentoContado.value(),
            'cupos_totales': cupos_totales,
            'cupos_disponibles': cupos_totales,  # Al crear, todos están disponibles
            'estado': self.ui.comboEstado.currentText(),
            'fecha_inicio_planificada': fecha_inicio.toString('yyyy-MM-dd'),
            'tutor_id': self.ui.comboTutor.currentData(),
            'cuotas_mensuales': 1 if self.ui.checkCuotasMensuales.isChecked() else 0,
            'dias_entre_cuotas': self.ui.spinDiasEntreCuotas.value()
        }
    
    def validar_y_guardar(self):
        """Validar y guardar los datos"""
        errores, datos = self.obtener_datos_formulario()
        
        if errores:
            QMessageBox.warning(self, "Validación", "\n".join(errores))
            return
        
        # Si es nuevo, verificar que no exista el código
        if not self.modo_edicion:
            existente = ProgramaModel.buscar_por_codigo(datos['codigo'])
            if existente:
                QMessageBox.warning(
                    self, "Validación", 
                    f"Ya existe un programa con código {datos['codigo']}"
                )
                return
        
        # Emitir señal con los datos
        self.programa_guardado.emit(datos)
        self.accept()