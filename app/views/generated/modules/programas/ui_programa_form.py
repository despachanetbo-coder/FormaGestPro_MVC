# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'programa_form.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDateEdit, QDialog, QDialogButtonBox, QDoubleSpinBox,
    QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QSizePolicy, QSpacerItem, QSpinBox,
    QTabWidget, QTextEdit, QVBoxLayout, QWidget)

class Ui_ProgramaFormDialog(object):
    def setupUi(self, ProgramaFormDialog):
        if not ProgramaFormDialog.objectName():
            ProgramaFormDialog.setObjectName(u"ProgramaFormDialog")
        ProgramaFormDialog.resize(700, 850)
        self.verticalLayout = QVBoxLayout(ProgramaFormDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(ProgramaFormDialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabInfoBasica = QWidget()
        self.tabInfoBasica.setObjectName(u"tabInfoBasica")
        self.verticalLayout_2 = QVBoxLayout(self.tabInfoBasica)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox = QGroupBox(self.tabInfoBasica)
        self.groupBox.setObjectName(u"groupBox")
        self.formLayout = QFormLayout(self.groupBox)
        self.formLayout.setObjectName(u"formLayout")
        self.labelCodigo = QLabel(self.groupBox)
        self.labelCodigo.setObjectName(u"labelCodigo")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelCodigo)

        self.txtCodigo = QLineEdit(self.groupBox)
        self.txtCodigo.setObjectName(u"txtCodigo")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.txtCodigo)

        self.labelNombre = QLabel(self.groupBox)
        self.labelNombre.setObjectName(u"labelNombre")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelNombre)

        self.txtNombre = QLineEdit(self.groupBox)
        self.txtNombre.setObjectName(u"txtNombre")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.txtNombre)

        self.labelDescripcion = QLabel(self.groupBox)
        self.labelDescripcion.setObjectName(u"labelDescripcion")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelDescripcion)

        self.txtDescripcion = QTextEdit(self.groupBox)
        self.txtDescripcion.setObjectName(u"txtDescripcion")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.txtDescripcion)

        self.labelDuracion = QLabel(self.groupBox)
        self.labelDuracion.setObjectName(u"labelDuracion")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelDuracion)

        self.spinDuracionMeses = QSpinBox(self.groupBox)
        self.spinDuracionMeses.setObjectName(u"spinDuracionMeses")
        self.spinDuracionMeses.setMinimum(1)
        self.spinDuracionMeses.setMaximum(36)
        self.spinDuracionMeses.setValue(3)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.spinDuracionMeses)

        self.labelHoras = QLabel(self.groupBox)
        self.labelHoras.setObjectName(u"labelHoras")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.labelHoras)

        self.spinHorasTotales = QSpinBox(self.groupBox)
        self.spinHorasTotales.setObjectName(u"spinHorasTotales")
        self.spinHorasTotales.setMinimum(0)
        self.spinHorasTotales.setMaximum(500)
        self.spinHorasTotales.setValue(40)

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.spinHorasTotales)

        self.labelCupos = QLabel(self.groupBox)
        self.labelCupos.setObjectName(u"labelCupos")

        self.formLayout.setWidget(5, QFormLayout.ItemRole.LabelRole, self.labelCupos)

        self.spinCuposTotales = QSpinBox(self.groupBox)
        self.spinCuposTotales.setObjectName(u"spinCuposTotales")
        self.spinCuposTotales.setMinimum(1)
        self.spinCuposTotales.setMaximum(200)
        self.spinCuposTotales.setValue(25)

        self.formLayout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.spinCuposTotales)


        self.verticalLayout_2.addWidget(self.groupBox)

        self.tabWidget.addTab(self.tabInfoBasica, "")
        self.tabCostos = QWidget()
        self.tabCostos.setObjectName(u"tabCostos")
        self.verticalLayout_3 = QVBoxLayout(self.tabCostos)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupBox_2 = QGroupBox(self.tabCostos)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.formLayout_2 = QFormLayout(self.groupBox_2)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.labelCostoInscripcion = QLabel(self.groupBox_2)
        self.labelCostoInscripcion.setObjectName(u"labelCostoInscripcion")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelCostoInscripcion)

        self.spinCostoInscripcion = QDoubleSpinBox(self.groupBox_2)
        self.spinCostoInscripcion.setObjectName(u"spinCostoInscripcion")
        self.spinCostoInscripcion.setDecimals(2)
        self.spinCostoInscripcion.setMaximum(10000)

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinCostoInscripcion)

        self.labelCostoMatricula = QLabel(self.groupBox_2)
        self.labelCostoMatricula.setObjectName(u"labelCostoMatricula")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelCostoMatricula)

        self.spinCostoMatricula = QDoubleSpinBox(self.groupBox_2)
        self.spinCostoMatricula.setObjectName(u"spinCostoMatricula")
        self.spinCostoMatricula.setDecimals(2)
        self.spinCostoMatricula.setMaximum(10000)

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinCostoMatricula)

        self.labelCostoColegiatura = QLabel(self.groupBox_2)
        self.labelCostoColegiatura.setObjectName(u"labelCostoColegiatura")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelCostoColegiatura)

        self.spinCostoBase = QDoubleSpinBox(self.groupBox_2)
        self.spinCostoBase.setObjectName(u"spinCostoBase")
        self.spinCostoBase.setDecimals(2)
        self.spinCostoBase.setMinimum(100)
        self.spinCostoBase.setMaximum(50000)
        self.spinCostoBase.setValue(2500)

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinCostoBase)

        self.labelDescuentoContado = QLabel(self.groupBox_2)
        self.labelDescuentoContado.setObjectName(u"labelDescuentoContado")

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelDescuentoContado)

        self.spinDescuentoContado = QDoubleSpinBox(self.groupBox_2)
        self.spinDescuentoContado.setObjectName(u"spinDescuentoContado")
        self.spinDescuentoContado.setDecimals(2)
        self.spinDescuentoContado.setMinimum(0)
        self.spinDescuentoContado.setMaximum(50)

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.FieldRole, self.spinDescuentoContado)


        self.verticalLayout_3.addWidget(self.groupBox_2)

        self.labelResumenCostos = QLabel(self.tabCostos)
        self.labelResumenCostos.setObjectName(u"labelResumenCostos")
        self.labelResumenCostos.setAlignment(Qt.AlignCenter)
        self.labelResumenCostos.setWordWrap(True)
        self.labelResumenCostos.setStyleSheet(u"QLabel {\n"
"    background-color: #f8f9fa;\n"
"    padding: 15px;\n"
"    border-radius: 5px;\n"
"    border: 1px solid #ddd;\n"
"}")

        self.verticalLayout_3.addWidget(self.labelResumenCostos)

        self.tabWidget.addTab(self.tabCostos, "")
        self.tabConfiguracion = QWidget()
        self.tabConfiguracion.setObjectName(u"tabConfiguracion")
        self.verticalLayout_4 = QVBoxLayout(self.tabConfiguracion)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.groupBox_3 = QGroupBox(self.tabConfiguracion)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.formLayout_3 = QFormLayout(self.groupBox_3)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.labelEstado = QLabel(self.groupBox_3)
        self.labelEstado.setObjectName(u"labelEstado")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelEstado)

        self.comboEstado = QComboBox(self.groupBox_3)
        self.comboEstado.addItem("")
        self.comboEstado.addItem("")
        self.comboEstado.addItem("")
        self.comboEstado.addItem("")
        self.comboEstado.setObjectName(u"comboEstado")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.FieldRole, self.comboEstado)

        self.labelFechas = QLabel(self.groupBox_3)
        self.labelFechas.setObjectName(u"labelFechas")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelFechas)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.labelFechaInicio = QLabel(self.groupBox_3)
        self.labelFechaInicio.setObjectName(u"labelFechaInicio")

        self.horizontalLayout.addWidget(self.labelFechaInicio)

        self.dateFechaInicio = QDateEdit(self.groupBox_3)
        self.dateFechaInicio.setObjectName(u"dateFechaInicio")

        self.horizontalLayout.addWidget(self.dateFechaInicio)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.labelFechaFin = QLabel(self.groupBox_3)
        self.labelFechaFin.setObjectName(u"labelFechaFin")

        self.horizontalLayout.addWidget(self.labelFechaFin)

        self.dateFechaFin = QDateEdit(self.groupBox_3)
        self.dateFechaFin.setObjectName(u"dateFechaFin")

        self.horizontalLayout.addWidget(self.dateFechaFin)


        self.formLayout_3.setLayout(1, QFormLayout.ItemRole.FieldRole, self.horizontalLayout)

        self.labelCuotas = QLabel(self.groupBox_3)
        self.labelCuotas.setObjectName(u"labelCuotas")

        self.formLayout_3.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelCuotas)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.checkCuotasMensuales = QCheckBox(self.groupBox_3)
        self.checkCuotasMensuales.setObjectName(u"checkCuotasMensuales")
        self.checkCuotasMensuales.setChecked(True)

        self.horizontalLayout_2.addWidget(self.checkCuotasMensuales)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.labelDiasEntreCuotas = QLabel(self.groupBox_3)
        self.labelDiasEntreCuotas.setObjectName(u"labelDiasEntreCuotas")

        self.horizontalLayout_2.addWidget(self.labelDiasEntreCuotas)

        self.spinDiasEntreCuotas = QSpinBox(self.groupBox_3)
        self.spinDiasEntreCuotas.setObjectName(u"spinDiasEntreCuotas")
        self.spinDiasEntreCuotas.setMinimum(1)
        self.spinDiasEntreCuotas.setMaximum(90)
        self.spinDiasEntreCuotas.setValue(30)
        self.spinDiasEntreCuotas.setEnabled(False)

        self.horizontalLayout_2.addWidget(self.spinDiasEntreCuotas)


        self.formLayout_3.setLayout(2, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_2)


        self.verticalLayout_4.addWidget(self.groupBox_3)

        self.tabWidget.addTab(self.tabConfiguracion, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.buttonBox = QDialogButtonBox(ProgramaFormDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Save)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(ProgramaFormDialog)
        self.checkCuotasMensuales.toggled.connect(self.spinDiasEntreCuotas.setDisabled)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(ProgramaFormDialog)
    # setupUi

    def retranslateUi(self, ProgramaFormDialog):
        ProgramaFormDialog.setWindowTitle(QCoreApplication.translate("ProgramaFormDialog", u"Formulario de Programa", None))
        self.groupBox.setTitle(QCoreApplication.translate("ProgramaFormDialog", u"Datos del Programa", None))
        self.labelCodigo.setText(QCoreApplication.translate("ProgramaFormDialog", u"C\u00f3digo*:", None))
        self.txtCodigo.setPlaceholderText(QCoreApplication.translate("ProgramaFormDialog", u"Ej: DIP-001, CUR-2024", None))
        self.labelNombre.setText(QCoreApplication.translate("ProgramaFormDialog", u"Nombre*:", None))
        self.txtNombre.setPlaceholderText(QCoreApplication.translate("ProgramaFormDialog", u"Nombre completo del programa", None))
        self.labelDescripcion.setText(QCoreApplication.translate("ProgramaFormDialog", u"Descripci\u00f3n:", None))
        self.labelDuracion.setText(QCoreApplication.translate("ProgramaFormDialog", u"Duraci\u00f3n (meses):", None))
        self.labelHoras.setText(QCoreApplication.translate("ProgramaFormDialog", u"Horas totales:", None))
        self.labelCupos.setText(QCoreApplication.translate("ProgramaFormDialog", u"Cupos totales*:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabInfoBasica), QCoreApplication.translate("ProgramaFormDialog", u"\U0001f4cb Informaci\U000000f3n B\U000000e1sica", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("ProgramaFormDialog", u"Estructura de Costos", None))
        self.labelCostoInscripcion.setText(QCoreApplication.translate("ProgramaFormDialog", u"Inscripci\u00f3n (Bs.):", None))
        self.spinCostoInscripcion.setPrefix(QCoreApplication.translate("ProgramaFormDialog", u"Bs. ", None))
        self.labelCostoMatricula.setText(QCoreApplication.translate("ProgramaFormDialog", u"Matr\u00edcula (Bs.):", None))
        self.spinCostoMatricula.setPrefix(QCoreApplication.translate("ProgramaFormDialog", u"Bs. ", None))
        self.labelCostoColegiatura.setText(QCoreApplication.translate("ProgramaFormDialog", u"Colegiatura (Bs.)*:", None))
        self.spinCostoBase.setPrefix(QCoreApplication.translate("ProgramaFormDialog", u"Bs. ", None))
        self.labelDescuentoContado.setText(QCoreApplication.translate("ProgramaFormDialog", u"Descuento contado (%):", None))
        self.spinDescuentoContado.setSuffix(QCoreApplication.translate("ProgramaFormDialog", u" %", None))
        self.labelResumenCostos.setText(QCoreApplication.translate("ProgramaFormDialog", u"Resumen de costos aparecer\u00e1 aqu\u00ed...", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabCostos), QCoreApplication.translate("ProgramaFormDialog", u"\U0001f4b0 Costos", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("ProgramaFormDialog", u"Configuraci\u00f3n Adicional", None))
        self.labelEstado.setText(QCoreApplication.translate("ProgramaFormDialog", u"Estado:", None))
        self.comboEstado.setItemText(0, QCoreApplication.translate("ProgramaFormDialog", u"PLANIFICADO", None))
        self.comboEstado.setItemText(1, QCoreApplication.translate("ProgramaFormDialog", u"INICIADO", None))
        self.comboEstado.setItemText(2, QCoreApplication.translate("ProgramaFormDialog", u"CONCLUIDO", None))
        self.comboEstado.setItemText(3, QCoreApplication.translate("ProgramaFormDialog", u"CANCELADO", None))

        self.labelFechas.setText(QCoreApplication.translate("ProgramaFormDialog", u"Fechas:", None))
        self.labelFechaInicio.setText(QCoreApplication.translate("ProgramaFormDialog", u"Inicio:", None))
        self.labelFechaFin.setText(QCoreApplication.translate("ProgramaFormDialog", u"Fin:", None))
        self.labelCuotas.setText(QCoreApplication.translate("ProgramaFormDialog", u"Cuotas:", None))
        self.checkCuotasMensuales.setText(QCoreApplication.translate("ProgramaFormDialog", u"Mensuales", None))
        self.labelDiasEntreCuotas.setText(QCoreApplication.translate("ProgramaFormDialog", u"D\u00edas entre cuotas:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabConfiguracion), QCoreApplication.translate("ProgramaFormDialog", u"\u2699\ufe0f Configuraci\u00f3n", None))
    # retranslateUi

