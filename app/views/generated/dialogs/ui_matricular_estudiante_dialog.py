# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'matricular_estudiante_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDateEdit, QDialog,
    QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QSpinBox, QTableWidget, QTableWidgetItem, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_MatricularEstudianteDialog(object):
    def setupUi(self, MatricularEstudianteDialog):
        if not MatricularEstudianteDialog.objectName():
            MatricularEstudianteDialog.setObjectName(u"MatricularEstudianteDialog")
        MatricularEstudianteDialog.resize(800, 650)
        self.verticalLayout = QVBoxLayout(MatricularEstudianteDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.lblEstudiante = QLabel(MatricularEstudianteDialog)
        self.lblEstudiante.setObjectName(u"lblEstudiante")
        self.lblEstudiante.setAlignment(Qt.AlignCenter)
        self.lblEstudiante.setWordWrap(True)
        self.lblEstudiante.setStyleSheet(u"font-weight: bold; background-color: #e3f2fd; padding: 10px; border-radius: 5px;")

        self.verticalLayout.addWidget(self.lblEstudiante)

        self.groupBoxPrograma = QGroupBox(MatricularEstudianteDialog)
        self.groupBoxPrograma.setObjectName(u"groupBoxPrograma")
        self.gridLayoutPrograma = QGridLayout(self.groupBoxPrograma)
        self.gridLayoutPrograma.setObjectName(u"gridLayoutPrograma")
        self.lblPrograma = QLabel(self.groupBoxPrograma)
        self.lblPrograma.setObjectName(u"lblPrograma")

        self.gridLayoutPrograma.addWidget(self.lblPrograma, 0, 0, 1, 1)

        self.comboPrograma = QComboBox(self.groupBoxPrograma)
        self.comboPrograma.setObjectName(u"comboPrograma")

        self.gridLayoutPrograma.addWidget(self.comboPrograma, 0, 1, 1, 3)

        self.lblModalidad = QLabel(self.groupBoxPrograma)
        self.lblModalidad.setObjectName(u"lblModalidad")

        self.gridLayoutPrograma.addWidget(self.lblModalidad, 1, 0, 1, 1)

        self.comboModalidadPago = QComboBox(self.groupBoxPrograma)
        self.comboModalidadPago.addItem("")
        self.comboModalidadPago.addItem("")
        self.comboModalidadPago.addItem("")
        self.comboModalidadPago.addItem("")
        self.comboModalidadPago.addItem("")
        self.comboModalidadPago.addItem("")
        self.comboModalidadPago.setObjectName(u"comboModalidadPago")

        self.gridLayoutPrograma.addWidget(self.comboModalidadPago, 1, 1, 1, 1)

        self.lblFechaInicio = QLabel(self.groupBoxPrograma)
        self.lblFechaInicio.setObjectName(u"lblFechaInicio")

        self.gridLayoutPrograma.addWidget(self.lblFechaInicio, 2, 0, 1, 1)

        self.dateFechaInicio = QDateEdit(self.groupBoxPrograma)
        self.dateFechaInicio.setObjectName(u"dateFechaInicio")
        self.dateFechaInicio.setCalendarPopup(True)
        self.dateFechaInicio.setDate(QDate(2024, 1, 15))

        self.gridLayoutPrograma.addWidget(self.dateFechaInicio, 2, 1, 1, 1)


        self.verticalLayout.addWidget(self.groupBoxPrograma)

        self.groupBoxDetalles = QGroupBox(MatricularEstudianteDialog)
        self.groupBoxDetalles.setObjectName(u"groupBoxDetalles")
        self.groupBoxDetalles.setEnabled(False)
        self.verticalLayoutDetalles = QVBoxLayout(self.groupBoxDetalles)
        self.verticalLayoutDetalles.setObjectName(u"verticalLayoutDetalles")
        self.lblDetallesPrograma = QLabel(self.groupBoxDetalles)
        self.lblDetallesPrograma.setObjectName(u"lblDetallesPrograma")
        self.lblDetallesPrograma.setAlignment(Qt.AlignCenter)
        self.lblDetallesPrograma.setWordWrap(True)

        self.verticalLayoutDetalles.addWidget(self.lblDetallesPrograma)


        self.verticalLayout.addWidget(self.groupBoxDetalles)

        self.groupBoxCuotas = QGroupBox(MatricularEstudianteDialog)
        self.groupBoxCuotas.setObjectName(u"groupBoxCuotas")
        self.groupBoxCuotas.setVisible(False)
        self.gridLayoutCuotas = QGridLayout(self.groupBoxCuotas)
        self.gridLayoutCuotas.setObjectName(u"gridLayoutCuotas")
        self.lblNumCuotas = QLabel(self.groupBoxCuotas)
        self.lblNumCuotas.setObjectName(u"lblNumCuotas")

        self.gridLayoutCuotas.addWidget(self.lblNumCuotas, 0, 0, 1, 1)

        self.spinNumCuotas = QSpinBox(self.groupBoxCuotas)
        self.spinNumCuotas.setObjectName(u"spinNumCuotas")
        self.spinNumCuotas.setMinimum(2)
        self.spinNumCuotas.setMaximum(12)
        self.spinNumCuotas.setValue(3)

        self.gridLayoutCuotas.addWidget(self.spinNumCuotas, 0, 1, 1, 1)

        self.lblMontoCuota = QLabel(self.groupBoxCuotas)
        self.lblMontoCuota.setObjectName(u"lblMontoCuota")

        self.gridLayoutCuotas.addWidget(self.lblMontoCuota, 1, 0, 1, 1)

        self.lblMontoCuotaValor = QLabel(self.groupBoxCuotas)
        self.lblMontoCuotaValor.setObjectName(u"lblMontoCuotaValor")
        self.lblMontoCuotaValor.setStyleSheet(u"font-weight: bold; color: #2c3e50;")

        self.gridLayoutCuotas.addWidget(self.lblMontoCuotaValor, 1, 1, 1, 1)

        self.btnGenerarCalendario = QPushButton(self.groupBoxCuotas)
        self.btnGenerarCalendario.setObjectName(u"btnGenerarCalendario")

        self.gridLayoutCuotas.addWidget(self.btnGenerarCalendario, 2, 0, 1, 2)


        self.verticalLayout.addWidget(self.groupBoxCuotas)

        self.groupBoxResumen = QGroupBox(MatricularEstudianteDialog)
        self.groupBoxResumen.setObjectName(u"groupBoxResumen")
        self.gridLayoutResumen = QGridLayout(self.groupBoxResumen)
        self.gridLayoutResumen.setObjectName(u"gridLayoutResumen")
        self.lblCostoBase = QLabel(self.groupBoxResumen)
        self.lblCostoBase.setObjectName(u"lblCostoBase")

        self.gridLayoutResumen.addWidget(self.lblCostoBase, 0, 0, 1, 1)

        self.lblCostoBaseValor = QLabel(self.groupBoxResumen)
        self.lblCostoBaseValor.setObjectName(u"lblCostoBaseValor")

        self.gridLayoutResumen.addWidget(self.lblCostoBaseValor, 0, 1, 1, 1)

        self.lblDescuento = QLabel(self.groupBoxResumen)
        self.lblDescuento.setObjectName(u"lblDescuento")

        self.gridLayoutResumen.addWidget(self.lblDescuento, 1, 0, 1, 1)

        self.lblDescuentoValor = QLabel(self.groupBoxResumen)
        self.lblDescuentoValor.setObjectName(u"lblDescuentoValor")
        self.lblDescuentoValor.setStyleSheet(u"color: #27ae60;")

        self.gridLayoutResumen.addWidget(self.lblDescuentoValor, 1, 1, 1, 1)

        self.lblTotalPagar = QLabel(self.groupBoxResumen)
        self.lblTotalPagar.setObjectName(u"lblTotalPagar")
        self.lblTotalPagar.setStyleSheet(u"font-weight: bold;")

        self.gridLayoutResumen.addWidget(self.lblTotalPagar, 2, 0, 1, 1)

        self.lblTotalPagarValor = QLabel(self.groupBoxResumen)
        self.lblTotalPagarValor.setObjectName(u"lblTotalPagarValor")
        self.lblTotalPagarValor.setStyleSheet(u"font-weight: bold; color: #e74c3c; font-size: 14px;")

        self.gridLayoutResumen.addWidget(self.lblTotalPagarValor, 2, 1, 1, 1)

        self.lblPagoInicial = QLabel(self.groupBoxResumen)
        self.lblPagoInicial.setObjectName(u"lblPagoInicial")

        self.gridLayoutResumen.addWidget(self.lblPagoInicial, 3, 0, 1, 1)

        self.lblPagoInicialValor = QLabel(self.groupBoxResumen)
        self.lblPagoInicialValor.setObjectName(u"lblPagoInicialValor")
        self.lblPagoInicialValor.setStyleSheet(u"font-weight: bold; color: #3498db;")

        self.gridLayoutResumen.addWidget(self.lblPagoInicialValor, 3, 1, 1, 1)


        self.verticalLayout.addWidget(self.groupBoxResumen)

        self.groupBoxCalendario = QGroupBox(MatricularEstudianteDialog)
        self.groupBoxCalendario.setObjectName(u"groupBoxCalendario")
        self.groupBoxCalendario.setVisible(False)
        self.verticalLayoutCalendario = QVBoxLayout(self.groupBoxCalendario)
        self.verticalLayoutCalendario.setObjectName(u"verticalLayoutCalendario")
        self.tableCuotas = QTableWidget(self.groupBoxCalendario)
        if (self.tableCuotas.columnCount() < 4):
            self.tableCuotas.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableCuotas.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableCuotas.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableCuotas.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableCuotas.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.tableCuotas.setObjectName(u"tableCuotas")
        self.tableCuotas.setRowCount(0)
        self.tableCuotas.setColumnCount(4)

        self.verticalLayoutCalendario.addWidget(self.tableCuotas)


        self.verticalLayout.addWidget(self.groupBoxCalendario)

        self.groupBoxObservaciones = QGroupBox(MatricularEstudianteDialog)
        self.groupBoxObservaciones.setObjectName(u"groupBoxObservaciones")
        self.verticalLayoutObservaciones = QVBoxLayout(self.groupBoxObservaciones)
        self.verticalLayoutObservaciones.setObjectName(u"verticalLayoutObservaciones")
        self.txtObservaciones = QTextEdit(self.groupBoxObservaciones)
        self.txtObservaciones.setObjectName(u"txtObservaciones")
        self.txtObservaciones.setMaximumHeight(80)

        self.verticalLayoutObservaciones.addWidget(self.txtObservaciones)


        self.verticalLayout.addWidget(self.groupBoxObservaciones)

        self.horizontalLayoutBotones = QHBoxLayout()
        self.horizontalLayoutBotones.setObjectName(u"horizontalLayoutBotones")
        self.btnCalcular = QPushButton(MatricularEstudianteDialog)
        self.btnCalcular.setObjectName(u"btnCalcular")
        self.btnCalcular.setStyleSheet(u"QPushButton {\n"
"    background-color: #3498db;\n"
"    color: white;\n"
"    padding: 10px 20px;\n"
"    border-radius: 5px;\n"
"    font-weight: bold;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #2980b9;\n"
"}")

        self.horizontalLayoutBotones.addWidget(self.btnCalcular)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutBotones.addItem(self.horizontalSpacer)

        self.btnImprimir = QPushButton(MatricularEstudianteDialog)
        self.btnImprimir.setObjectName(u"btnImprimir")
        self.btnImprimir.setEnabled(False)
        self.btnImprimir.setStyleSheet(u"QPushButton {\n"
"    background-color: #95a5a6;\n"
"    color: white;\n"
"    padding: 10px 20px;\n"
"    border-radius: 5px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #7f8c8d;\n"
"}")

        self.horizontalLayoutBotones.addWidget(self.btnImprimir)

        self.btnMatricular = QPushButton(MatricularEstudianteDialog)
        self.btnMatricular.setObjectName(u"btnMatricular")
        self.btnMatricular.setEnabled(False)
        self.btnMatricular.setStyleSheet(u"QPushButton {\n"
"    background-color: #27ae60;\n"
"    color: white;\n"
"    padding: 10px 30px;\n"
"    border-radius: 5px;\n"
"    font-weight: bold;\n"
"    font-size: 14px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #219653;\n"
"}\n"
"QPushButton:disabled {\n"
"    background-color: #95a5a6;\n"
"}")

        self.horizontalLayoutBotones.addWidget(self.btnMatricular)

        self.btnCancelar = QPushButton(MatricularEstudianteDialog)
        self.btnCancelar.setObjectName(u"btnCancelar")
        self.btnCancelar.setStyleSheet(u"QPushButton {\n"
"    background-color: #e74c3c;\n"
"    color: white;\n"
"    padding: 10px 20px;\n"
"    border-radius: 5px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #c0392b;\n"
"}")

        self.horizontalLayoutBotones.addWidget(self.btnCancelar)


        self.verticalLayout.addLayout(self.horizontalLayoutBotones)


        self.retranslateUi(MatricularEstudianteDialog)

        QMetaObject.connectSlotsByName(MatricularEstudianteDialog)
    # setupUi

    def retranslateUi(self, MatricularEstudianteDialog):
        MatricularEstudianteDialog.setWindowTitle(QCoreApplication.translate("MatricularEstudianteDialog", u"\U0001f393 Matricular Estudiante", None))
        self.lblEstudiante.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"Estudiante: [Nombre]", None))
        self.groupBoxPrograma.setTitle(QCoreApplication.translate("MatricularEstudianteDialog", u"\U0001f4da Programa Acad\U000000e9mico", None))
        self.lblPrograma.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"Programa:*", None))
        self.comboPrograma.setPlaceholderText(QCoreApplication.translate("MatricularEstudianteDialog", u"Seleccione un programa...", None))
        self.lblModalidad.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"Modalidad de Pago:*", None))
        self.comboModalidadPago.setItemText(0, QCoreApplication.translate("MatricularEstudianteDialog", u"Seleccione...", None))
        self.comboModalidadPago.setItemText(1, QCoreApplication.translate("MatricularEstudianteDialog", u"Contado", None))
        self.comboModalidadPago.setItemText(2, QCoreApplication.translate("MatricularEstudianteDialog", u"Cuotas (2 meses)", None))
        self.comboModalidadPago.setItemText(3, QCoreApplication.translate("MatricularEstudianteDialog", u"Cuotas (3 meses)", None))
        self.comboModalidadPago.setItemText(4, QCoreApplication.translate("MatricularEstudianteDialog", u"Cuotas (4 meses)", None))
        self.comboModalidadPago.setItemText(5, QCoreApplication.translate("MatricularEstudianteDialog", u"Cuotas (6 meses)", None))

        self.lblFechaInicio.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"Fecha de Inicio:*", None))
        self.groupBoxDetalles.setTitle(QCoreApplication.translate("MatricularEstudianteDialog", u"\U0001f4ca Detalles del Programa", None))
        self.lblDetallesPrograma.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"Seleccione un programa para ver detalles", None))
        self.groupBoxCuotas.setTitle(QCoreApplication.translate("MatricularEstudianteDialog", u"\U0001f4b0 Configuraci\U000000f3n de Cuotas", None))
        self.lblNumCuotas.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"N\u00famero de Cuotas:", None))
        self.lblMontoCuota.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"Monto por Cuota:", None))
        self.lblMontoCuotaValor.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"$0.00", None))
        self.btnGenerarCalendario.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"\U0001f4c5 Generar Calendario de Pagos", None))
        self.groupBoxResumen.setTitle(QCoreApplication.translate("MatricularEstudianteDialog", u"\U0001f9ee Resumen de la Matr\U000000edcula", None))
        self.lblCostoBase.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"Costo Base:", None))
        self.lblCostoBaseValor.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"$0.00", None))
        self.lblDescuento.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"Descuento:", None))
        self.lblDescuentoValor.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"$0.00 (0%)", None))
        self.lblTotalPagar.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"Total a Pagar:", None))
        self.lblTotalPagarValor.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"$0.00", None))
        self.lblPagoInicial.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"Pago Inicial:", None))
        self.lblPagoInicialValor.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"$0.00", None))
        self.groupBoxCalendario.setTitle(QCoreApplication.translate("MatricularEstudianteDialog", u"\U0001f4c5 Calendario de Pagos", None))
        ___qtablewidgetitem = self.tableCuotas.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"#", None));
        ___qtablewidgetitem1 = self.tableCuotas.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"Fecha Vencimiento", None));
        ___qtablewidgetitem2 = self.tableCuotas.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"Monto", None));
        ___qtablewidgetitem3 = self.tableCuotas.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"Estado", None));
        self.groupBoxObservaciones.setTitle(QCoreApplication.translate("MatricularEstudianteDialog", u"\U0001f4dd Observaciones", None))
        self.txtObservaciones.setPlaceholderText(QCoreApplication.translate("MatricularEstudianteDialog", u"Ingrese observaciones adicionales si es necesario...", None))
        self.btnCalcular.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"\U0001f9ee Calcular", None))
        self.btnImprimir.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"\U0001f5a8\U0000fe0f Imprimir", None))
        self.btnMatricular.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"\U0001f393 Matricular", None))
        self.btnCancelar.setText(QCoreApplication.translate("MatricularEstudianteDialog", u"\u274c Cancelar", None))
    # retranslateUi

