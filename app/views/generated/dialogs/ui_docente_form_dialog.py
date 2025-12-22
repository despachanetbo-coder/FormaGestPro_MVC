# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'docente_form_dialog.ui'
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
    QFormLayout, QLabel, QLineEdit, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_DocenteFormDialog(object):
    def setupUi(self, DocenteFormDialog):
        if not DocenteFormDialog.objectName():
            DocenteFormDialog.setObjectName(u"DocenteFormDialog")
        DocenteFormDialog.resize(500, 489)
        self.verticalLayout = QVBoxLayout(DocenteFormDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.labelCINumero = QLabel(DocenteFormDialog)
        self.labelCINumero.setObjectName(u"labelCINumero")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelCINumero)

        self.txtCINumero = QLineEdit(DocenteFormDialog)
        self.txtCINumero.setObjectName(u"txtCINumero")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.txtCINumero)

        self.labelExpedicion = QLabel(DocenteFormDialog)
        self.labelExpedicion.setObjectName(u"labelExpedicion")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelExpedicion)

        self.comboExpedicion = QComboBox(DocenteFormDialog)
        self.comboExpedicion.addItem("")
        self.comboExpedicion.addItem("")
        self.comboExpedicion.addItem("")
        self.comboExpedicion.addItem("")
        self.comboExpedicion.addItem("")
        self.comboExpedicion.addItem("")
        self.comboExpedicion.addItem("")
        self.comboExpedicion.addItem("")
        self.comboExpedicion.addItem("")
        self.comboExpedicion.addItem("")
        self.comboExpedicion.setObjectName(u"comboExpedicion")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.comboExpedicion)

        self.labelNombres = QLabel(DocenteFormDialog)
        self.labelNombres.setObjectName(u"labelNombres")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelNombres)

        self.txtNombres = QLineEdit(DocenteFormDialog)
        self.txtNombres.setObjectName(u"txtNombres")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.txtNombres)

        self.labelApellidos = QLabel(DocenteFormDialog)
        self.labelApellidos.setObjectName(u"labelApellidos")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelApellidos)

        self.txtApellidos = QLineEdit(DocenteFormDialog)
        self.txtApellidos.setObjectName(u"txtApellidos")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.txtApellidos)

        self.labelFechaNacimiento = QLabel(DocenteFormDialog)
        self.labelFechaNacimiento.setObjectName(u"labelFechaNacimiento")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.labelFechaNacimiento)

        self.dateFechaNacimiento = QDateEdit(DocenteFormDialog)
        self.dateFechaNacimiento.setObjectName(u"dateFechaNacimiento")
        self.dateFechaNacimiento.setCalendarPopup(True)

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.dateFechaNacimiento)

        self.labelGradoAcademico = QLabel(DocenteFormDialog)
        self.labelGradoAcademico.setObjectName(u"labelGradoAcademico")

        self.formLayout.setWidget(5, QFormLayout.ItemRole.LabelRole, self.labelGradoAcademico)

        self.comboGradoAcademico = QComboBox(DocenteFormDialog)
        self.comboGradoAcademico.addItem("")
        self.comboGradoAcademico.addItem("")
        self.comboGradoAcademico.addItem("")
        self.comboGradoAcademico.addItem("")
        self.comboGradoAcademico.addItem("")
        self.comboGradoAcademico.addItem("")
        self.comboGradoAcademico.addItem("")
        self.comboGradoAcademico.addItem("")
        self.comboGradoAcademico.addItem("")
        self.comboGradoAcademico.addItem("")
        self.comboGradoAcademico.setObjectName(u"comboGradoAcademico")

        self.formLayout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.comboGradoAcademico)

        self.labelTelefono = QLabel(DocenteFormDialog)
        self.labelTelefono.setObjectName(u"labelTelefono")

        self.formLayout.setWidget(6, QFormLayout.ItemRole.LabelRole, self.labelTelefono)

        self.txtTelefono = QLineEdit(DocenteFormDialog)
        self.txtTelefono.setObjectName(u"txtTelefono")

        self.formLayout.setWidget(6, QFormLayout.ItemRole.FieldRole, self.txtTelefono)

        self.labelEmail = QLabel(DocenteFormDialog)
        self.labelEmail.setObjectName(u"labelEmail")

        self.formLayout.setWidget(7, QFormLayout.ItemRole.LabelRole, self.labelEmail)

        self.txtEmail = QLineEdit(DocenteFormDialog)
        self.txtEmail.setObjectName(u"txtEmail")

        self.formLayout.setWidget(7, QFormLayout.ItemRole.FieldRole, self.txtEmail)

        self.labelEspecialidad = QLabel(DocenteFormDialog)
        self.labelEspecialidad.setObjectName(u"labelEspecialidad")

        self.formLayout.setWidget(8, QFormLayout.ItemRole.LabelRole, self.labelEspecialidad)

        self.txtEspecialidad = QLineEdit(DocenteFormDialog)
        self.txtEspecialidad.setObjectName(u"txtEspecialidad")

        self.formLayout.setWidget(8, QFormLayout.ItemRole.FieldRole, self.txtEspecialidad)

        self.labelHonorario = QLabel(DocenteFormDialog)
        self.labelHonorario.setObjectName(u"labelHonorario")

        self.formLayout.setWidget(9, QFormLayout.ItemRole.LabelRole, self.labelHonorario)

        self.spinHonorarioHora = QDoubleSpinBox(DocenteFormDialog)
        self.spinHonorarioHora.setObjectName(u"spinHonorarioHora")
        self.spinHonorarioHora.setDecimals(2)
        self.spinHonorarioHora.setMaximum(10000.000000000000000)

        self.formLayout.setWidget(9, QFormLayout.ItemRole.FieldRole, self.spinHonorarioHora)

        self.checkActivo = QCheckBox(DocenteFormDialog)
        self.checkActivo.setObjectName(u"checkActivo")
        self.checkActivo.setChecked(True)

        self.formLayout.setWidget(10, QFormLayout.ItemRole.FieldRole, self.checkActivo)


        self.verticalLayout.addLayout(self.formLayout)

        self.buttonBox = QDialogButtonBox(DocenteFormDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(DocenteFormDialog)

        QMetaObject.connectSlotsByName(DocenteFormDialog)
    # setupUi

    def retranslateUi(self, DocenteFormDialog):
        DocenteFormDialog.setWindowTitle(QCoreApplication.translate("DocenteFormDialog", u"Formulario de Docente/Tutor", None))
        self.labelCINumero.setText(QCoreApplication.translate("DocenteFormDialog", u"CI N\u00famero:", None))
        self.labelExpedicion.setText(QCoreApplication.translate("DocenteFormDialog", u"Expedici\u00f3n:", None))
        self.comboExpedicion.setItemText(0, QCoreApplication.translate("DocenteFormDialog", u"BE", None))
        self.comboExpedicion.setItemText(1, QCoreApplication.translate("DocenteFormDialog", u"CH", None))
        self.comboExpedicion.setItemText(2, QCoreApplication.translate("DocenteFormDialog", u"CB", None))
        self.comboExpedicion.setItemText(3, QCoreApplication.translate("DocenteFormDialog", u"LP", None))
        self.comboExpedicion.setItemText(4, QCoreApplication.translate("DocenteFormDialog", u"OR", None))
        self.comboExpedicion.setItemText(5, QCoreApplication.translate("DocenteFormDialog", u"PD", None))
        self.comboExpedicion.setItemText(6, QCoreApplication.translate("DocenteFormDialog", u"PT", None))
        self.comboExpedicion.setItemText(7, QCoreApplication.translate("DocenteFormDialog", u"SC", None))
        self.comboExpedicion.setItemText(8, QCoreApplication.translate("DocenteFormDialog", u"TJ", None))
        self.comboExpedicion.setItemText(9, QCoreApplication.translate("DocenteFormDialog", u"EX", None))

        self.labelNombres.setText(QCoreApplication.translate("DocenteFormDialog", u"Nombres:", None))
        self.labelApellidos.setText(QCoreApplication.translate("DocenteFormDialog", u"Apellidos:", None))
        self.labelFechaNacimiento.setText(QCoreApplication.translate("DocenteFormDialog", u"Fecha Nacimiento:", None))
        self.labelGradoAcademico.setText(QCoreApplication.translate("DocenteFormDialog", u"M\u00e1ximo Grado:", None))
        self.comboGradoAcademico.setItemText(0, QCoreApplication.translate("DocenteFormDialog", u"Seleccione...", None))
        self.comboGradoAcademico.setItemText(1, QCoreApplication.translate("DocenteFormDialog", u"Mtr.", None))
        self.comboGradoAcademico.setItemText(2, QCoreApplication.translate("DocenteFormDialog", u"Mgtr.", None))
        self.comboGradoAcademico.setItemText(3, QCoreApplication.translate("DocenteFormDialog", u"Mag.", None))
        self.comboGradoAcademico.setItemText(4, QCoreApplication.translate("DocenteFormDialog", u"MBA", None))
        self.comboGradoAcademico.setItemText(5, QCoreApplication.translate("DocenteFormDialog", u"MSc", None))
        self.comboGradoAcademico.setItemText(6, QCoreApplication.translate("DocenteFormDialog", u"M.Sc.", None))
        self.comboGradoAcademico.setItemText(7, QCoreApplication.translate("DocenteFormDialog", u"PhD.", None))
        self.comboGradoAcademico.setItemText(8, QCoreApplication.translate("DocenteFormDialog", u"Dr.", None))
        self.comboGradoAcademico.setItemText(9, QCoreApplication.translate("DocenteFormDialog", u"Dra.", None))

        self.labelTelefono.setText(QCoreApplication.translate("DocenteFormDialog", u"Tel\u00e9fono:", None))
        self.labelEmail.setText(QCoreApplication.translate("DocenteFormDialog", u"Email:", None))
        self.labelEspecialidad.setText(QCoreApplication.translate("DocenteFormDialog", u"Especialidad:", None))
        self.labelHonorario.setText(QCoreApplication.translate("DocenteFormDialog", u"Honorario/Hora (Bs.):", None))
        self.spinHonorarioHora.setPrefix(QCoreApplication.translate("DocenteFormDialog", u"Bs. ", None))
        self.checkActivo.setText(QCoreApplication.translate("DocenteFormDialog", u"Activo", None))
    # retranslateUi

