# app/views/tabs/programas/programas_tab.py
"""
Diálogo para configurar promoción de programa - Versión GUI
"""
from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QDoubleSpinBox, QDateEdit, QGroupBox, QFormLayout,
    QRadioButton, QButtonGroup, QMessageBox, QTextEdit
)
from PySide6.QtCore import Qt, QDate, Signal, QTimer

from utils.calculos_financieros import (
    calcular_descuento_exacto,
    calcular_porcentaje_para_monto_final,
    formatear_moneda,
    redondear_a_entero_cercano
)

class ProgramaPromocionDialog(QDialog):
    """Diálogo para configurar promoción de programa"""
    
    promocion_configurada = Signal()  # Señal cuando se configura la promoción
    
    def __init__(self, programa, parent=None):
        super().__init__(parent)
        self.programa = programa
        
        self.setWindowTitle(f"🎁 Configurar Promoción - {programa.codigo}")
        self.setMinimumWidth(500)
        
        self.setup_ui()
        self.setup_connections()
        
        # Cargar datos existentes si hay promoción
        self.cargar_datos_existentes()
    
    def setup_ui(self):
        """Configurar interfaz"""
        layout = QVBoxLayout(self)
        
        # Información del programa
        info_group = QGroupBox("📋 Información del Programa")
        info_layout = QFormLayout(info_group)
        
        info_layout.addRow("Código:", QLabel(self.programa.codigo))
        info_layout.addRow("Nombre:", QLabel(self.programa.nombre))
        
        costo_text = f"Bs. {self.programa.costo_base:,.2f}"
        if self.programa.descuento_contado > 0:
            descuento_bs, costo_con_descuento = calcular_descuento_exacto(
                self.programa.costo_base, self.programa.descuento_contado
            )
            costo_text += f" (Bs. {costo_con_descuento:,.2f} con descuento contado)"
        
        info_layout.addRow("Colegiatura:", QLabel(costo_text))
        
        layout.addWidget(info_group)
        
        # Método de configuración
        metodo_group = QGroupBox("📊 Método de Configuración")
        metodo_layout = QVBoxLayout(metodo_group)
        
        self.radio_porcentaje = QRadioButton("Porcentaje de descuento")
        self.radio_monto_final = QRadioButton("Monto final deseado")
        self.radio_porcentaje.setChecked(True)
        
        metodo_layout.addWidget(self.radio_porcentaje)
        metodo_layout.addWidget(self.radio_monto_final)
        
        layout.addWidget(metodo_group)
        
        # Campos de entrada
        entrada_group = QGroupBox("🎯 Configuración de Promoción")
        entrada_layout = QFormLayout(entrada_group)
        
        self.label_entrada = QLabel("Porcentaje de descuento (%):")
        self.input_entrada = QDoubleSpinBox()
        self.input_entrada.setDecimals(2)
        self.input_entrada.setRange(0, 100)
        self.input_entrada.setValue(10)
        self.input_entrada.setSingleStep(0.5)
        
        entrada_layout.addRow(self.label_entrada, self.input_entrada)
        
        # Descripción
        self.input_descripcion = QLineEdit()
        self.input_descripcion.setPlaceholderText("Ej: Inscripción temprana, Descuento por grupo, etc.")
        entrada_layout.addRow("Descripción:", self.input_descripcion)
        
        # Fecha límite
        self.input_fecha_limite = QDateEdit()
        self.input_fecha_limite.setDate(QDate.currentDate().addMonths(1))
        self.input_fecha_limite.setCalendarPopup(True)
        entrada_layout.addRow("Fecha límite:", self.input_fecha_limite)
        
        layout.addWidget(entrada_group)
        
        # Resultado
        self.label_resultado = QLabel()
        self.label_resultado.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                border: 1px solid #ddd;
                font-family: monospace;
            }
        """)
        self.label_resultado.setWordWrap(True)
        layout.addWidget(self.label_resultado)
        
        # Botones
        button_layout = QHBoxLayout()
        
        self.btn_calcular = QPushButton("🧮 Calcular")
        self.btn_calcular.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btn_calcular.clicked.connect(self.calcular_promocion)
        
        self.btn_aplicar = QPushButton("✅ Aplicar Promoción")
        self.btn_aplicar.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.btn_aplicar.clicked.connect(self.aplicar_promocion)
        
        btn_cancelar = QPushButton("❌ Cancelar")
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_cancelar.clicked.connect(self.reject)
        
        button_layout.addWidget(self.btn_calcular)
        button_layout.addWidget(self.btn_aplicar)
        button_layout.addWidget(btn_cancelar)
        
        layout.addLayout(button_layout)
    
    def setup_connections(self):
        """Configurar conexiones"""
        self.radio_porcentaje.toggled.connect(self.cambiar_metodo)
        self.input_entrada.valueChanged.connect(self.calcular_promocion)
        
        # Calcular al inicio
        QTimer.singleShot(100, self.calcular_promocion)
    
    def cambiar_metodo(self, checked):
        """Cambiar método de configuración"""
        if checked:
            self.label_entrada.setText("Porcentaje de descuento (%):")
            self.input_entrada.setRange(0, 100)
            self.input_entrada.setDecimals(2)
            self.input_entrada.setSuffix(" %")
        else:
            self.label_entrada.setText("Monto final deseado (Bs.):")
            self.input_entrada.setRange(1, self.programa.costo_base)
            self.input_entrada.setDecimals(2)
            self.input_entrada.setPrefix("Bs. ")
            self.input_entrada.setSuffix("")
        
        self.calcular_promocion()
    
    def cargar_datos_existentes(self):
        """Cargar datos de promoción existente"""
        if self.programa.promocion_activa:
            # Usar método por porcentaje por defecto
            self.radio_porcentaje.setChecked(True)
            self.input_entrada.setValue(self.programa.descuento_promocion)
            self.input_descripcion.setText(self.programa.descripcion_promocion)
            
            if self.programa.promocion_fecha_limite:
                try:
                    qdate = QDate.fromString(self.programa.promocion_fecha_limite, 'yyyy-MM-dd')
                    if qdate.isValid():
                        self.input_fecha_limite.setDate(qdate)
                except:
                    pass
    
    def calcular_promocion(self):
        """Calcular y mostrar resultados de la promoción"""
        try:
            if self.radio_porcentaje.isChecked():
                # Método por porcentaje
                porcentaje = self.input_entrada.value()
                
                if porcentaje <= 0:
                    self.label_resultado.setText("Ingrese un porcentaje mayor a 0")
                    return
                
                descuento_bs, monto_final = calcular_descuento_exacto(
                    self.programa.costo_base, porcentaje
                )
                
                resultado = f"""
                <b>📊 CÁLCULO CON {porcentaje:.2f}% DE DESCUENTO:</b><br>
                • Colegiatura original: <b>Bs. {formatear_moneda(self.programa.costo_base)}</b><br>
                • Descuento: <b>Bs. {formatear_moneda(descuento_bs)}</b><br>
                • Colegiatura con promoción: <b>Bs. {formatear_moneda(monto_final)}</b><br>
                """
                
                # Mostrar redondeo a entero si es cercano
                if abs(monto_final - redondear_a_entero_cercano(monto_final)) < 0.01:
                    resultado += f"• Colegiatura (entero): <b>Bs. {redondear_a_entero_cercano(monto_final):.0f}</b><br>"
                
            else:
                # Método por monto final
                monto_final_deseado = self.input_entrada.value()
                
                if monto_final_deseado >= self.programa.costo_base:
                    self.label_resultado.setText("El monto final debe ser menor al costo base")
                    return
                
                porcentaje_necesario = calcular_porcentaje_para_monto_final(
                    self.programa.costo_base, monto_final_deseado
                )
                
                # Verificar cálculo exacto
                descuento_calculado, monto_final_calculado = calcular_descuento_exacto(
                    self.programa.costo_base, porcentaje_necesario
                )
                
                resultado = f"""
                <b>📊 CÁLCULO PARA MONTO FINAL DE Bs. {formatear_moneda(monto_final_deseado)}:</b><br>
                • Colegiatura original: <b>Bs. {formatear_moneda(self.programa.costo_base)}</b><br>
                • Porcentaje necesario: <b>{porcentaje_necesario:.6f}%</b><br>
                • Descuento: <b>Bs. {formatear_moneda(descuento_calculado)}</b><br>
                • Colegiatura calculada: <b>Bs. {formatear_moneda(monto_final_calculado)}</b><br>
                """
                
                if abs(monto_final_calculado - monto_final_deseado) > 0.01:
                    resultado += f"• ⚠️  Diferencia por redondeo: <b>Bs. {formatear_moneda(abs(monto_final_calculado - monto_final_deseado))}</b><br>"
            
            # Agregar total con costos adicionales
            costo_inscripcion = getattr(self.programa, 'costo_inscripcion', 0)
            costo_matricula = getattr(self.programa, 'costo_matricula', 0)
            
            if costo_inscripcion > 0 or costo_matricula > 0:
                resultado += f"<br><b>💵 TOTAL COMPLETO CON COSTOS ADICIONALES:</b><br>"
                if costo_inscripcion > 0:
                    resultado += f"• Inscripción: <b>Bs. {formatear_moneda(costo_inscripcion)}</b><br>"
                if costo_matricula > 0:
                    resultado += f"• Matrícula: <b>Bs. {formatear_moneda(costo_matricula)}</b><br>"
                
                total_con_promocion = costo_inscripcion + costo_matricula + monto_final
                resultado += f"• <b>TOTAL CON PROMOCIÓN: Bs. {formatear_moneda(total_con_promocion)}</b>"
            
            self.label_resultado.setText(resultado)
            
        except Exception as e:
            self.label_resultado.setText(f"❌ Error en cálculo: {str(e)}")
    
    def aplicar_promocion(self):
        """Aplicar la promoción al programa"""
        try:
            # Validar
            if not self.input_descripcion.text().strip():
                QMessageBox.warning(self, "Validación", "La descripción de la promoción es obligatoria")
                return
            
            # Calcular porcentaje final
            if self.radio_porcentaje.isChecked():
                descuento_porcentaje = self.input_entrada.value()
            else:
                monto_final = self.input_entrada.value()
                descuento_porcentaje = calcular_porcentaje_para_monto_final(
                    self.programa.costo_base, monto_final
                )
            
            # Actualizar programa
            from app.models.programa_academico_model import ProgramaModel
            from datetime import datetime
            
            datos_actualizacion = {
                'promocion_activa': 1,
                'descripcion_promocion': self.input_descripcion.text().strip(),
                'descuento_promocion': round(descuento_porcentaje, 6),
                'promocion_fecha_limite': self.input_fecha_limite.date().toString('yyyy-MM-dd'),
                'updated_at': datetime.now().isoformat()
            }
            
            if ProgramaModel.update_by_id(self.programa.id, datos_actualizacion):
                QMessageBox.information(
                    self, "✅ Promoción Aplicada",
                    f"Promoción configurada exitosamente para {self.programa.codigo}\n\n"
                    f"Descuento: {descuento_porcentaje:.2f}%\n"
                    f"Válido hasta: {self.input_fecha_limite.date().toString('yyyy-MM-dd')}"
                )
                
                # Emitir señal
                self.promocion_configurada.emit()
                self.accept()
            else:
                QMessageBox.critical(self, "❌ Error", "No se pudo actualizar la promoción")
        
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"Error al aplicar promoción: {str(e)}")