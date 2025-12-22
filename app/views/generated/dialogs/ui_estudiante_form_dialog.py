# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'estudiante_form_dialog.ui'
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
    QDateEdit, QDialog, QDialogButtonBox, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_EstudianteFormDialog(object):
    def setupUi(self, EstudianteFormDialog):
        if not EstudianteFormDialog.objectName():
            EstudianteFormDialog.setObjectName(u"EstudianteFormDialog")
        EstudianteFormDialog.resize(600, 500)
        EstudianteFormDialog.setMinimumSize(QSize(600, 500))
        self.verticalLayout = QVBoxLayout(EstudianteFormDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(EstudianteFormDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.txtCINumero = QLineEdit(self.groupBox)
        self.txtCINumero.setObjectName(u"txtCINumero")

        self.gridLayout.addWidget(self.txtCINumero, 0, 1, 1, 1)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 2, 1, 1)

        self.comboExpedicion = QComboBox(self.groupBox)
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

        self.gridLayout.addWidget(self.comboExpedicion, 0, 3, 1, 1)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)

        self.txtNombres = QLineEdit(self.groupBox)
        self.txtNombres.setObjectName(u"txtNombres")

        self.gridLayout.addWidget(self.txtNombres, 1, 1, 1, 3)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)

        self.txtApellidos = QLineEdit(self.groupBox)
        self.txtApellidos.setObjectName(u"txtApellidos")

        self.gridLayout.addWidget(self.txtApellidos, 2, 1, 1, 3)

        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)

        self.dateFechaNacimiento = QDateEdit(self.groupBox)
        self.dateFechaNacimiento.setObjectName(u"dateFechaNacimiento")
        self.dateFechaNacimiento.setCalendarPopup(True)

        self.gridLayout.addWidget(self.dateFechaNacimiento, 3, 1, 1, 3)

        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 4, 0, 1, 1)

        self.txtTelefono = QLineEdit(self.groupBox)
        self.txtTelefono.setObjectName(u"txtTelefono")

        self.gridLayout.addWidget(self.txtTelefono, 4, 1, 1, 3)

        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout.addWidget(self.label_7, 5, 0, 1, 1)

        self.txtEmail = QLineEdit(self.groupBox)
        self.txtEmail.setObjectName(u"txtEmail")

        self.gridLayout.addWidget(self.txtEmail, 5, 1, 1, 3)


        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(EstudianteFormDialog)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_2 = QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_8 = QLabel(self.groupBox_2)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_2.addWidget(self.label_8, 0, 0, 1, 1)

        self.txtUniversidad = QLineEdit(self.groupBox_2)
        self.txtUniversidad.setObjectName(u"txtUniversidad")

        self.gridLayout_2.addWidget(self.txtUniversidad, 0, 1, 1, 3)

        self.label_9 = QLabel(self.groupBox_2)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_2.addWidget(self.label_9, 1, 0, 1, 1)

        self.txtProfesion = QLineEdit(self.groupBox_2)
        self.txtProfesion.setObjectName(u"txtProfesion")

        self.gridLayout_2.addWidget(self.txtProfesion, 1, 1, 1, 3)


        self.verticalLayout.addWidget(self.groupBox_2)

        self.groupBox_3 = QGroupBox(EstudianteFormDialog)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.horizontalLayout = QHBoxLayout(self.groupBox_3)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.checkActivo = QCheckBox(self.groupBox_3)
        self.checkActivo.setObjectName(u"checkActivo")
        self.checkActivo.setChecked(True)

        self.horizontalLayout.addWidget(self.checkActivo)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addWidget(self.groupBox_3)

        self.buttonBox = QDialogButtonBox(EstudianteFormDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(EstudianteFormDialog)
        self.buttonBox.accepted.connect(EstudianteFormDialog.accept)
        self.buttonBox.rejected.connect(EstudianteFormDialog.reject)

        QMetaObject.connectSlotsByName(EstudianteFormDialog)
    # setupUi

    def retranslateUi(self, EstudianteFormDialog):
        EstudianteFormDialog.setWindowTitle(QCoreApplication.translate("EstudianteFormDialog", u"Formulario de Estudiante", None))
        self.groupBox.setTitle(QCoreApplication.translate("EstudianteFormDialog", u"Datos Personales", None))
        self.label.setText(QCoreApplication.translate("EstudianteFormDialog", u"CI N\u00famero:*", None))
        self.txtCINumero.setPlaceholderText(QCoreApplication.translate("EstudianteFormDialog", u"Ej: 1234567", None))
        self.label_2.setText(QCoreApplication.translate("EstudianteFormDialog", u"Expedici\u00f3n:*", None))
        self.comboExpedicion.setItemText(0, QCoreApplication.translate("EstudianteFormDialog", u"BE", None))
        self.comboExpedicion.setItemText(1, QCoreApplication.translate("EstudianteFormDialog", u"CH", None))
        self.comboExpedicion.setItemText(2, QCoreApplication.translate("EstudianteFormDialog", u"CB", None))
        self.comboExpedicion.setItemText(3, QCoreApplication.translate("EstudianteFormDialog", u"LP", None))
        self.comboExpedicion.setItemText(4, QCoreApplication.translate("EstudianteFormDialog", u"OR", None))
        self.comboExpedicion.setItemText(5, QCoreApplication.translate("EstudianteFormDialog", u"PD", None))
        self.comboExpedicion.setItemText(6, QCoreApplication.translate("EstudianteFormDialog", u"PT", None))
        self.comboExpedicion.setItemText(7, QCoreApplication.translate("EstudianteFormDialog", u"SC", None))
        self.comboExpedicion.setItemText(8, QCoreApplication.translate("EstudianteFormDialog", u"TJ", None))
        self.comboExpedicion.setItemText(9, QCoreApplication.translate("EstudianteFormDialog", u"EX", None))

        self.comboExpedicion.setCurrentText(QCoreApplication.translate("EstudianteFormDialog", u"SC", None))
        self.label_3.setText(QCoreApplication.translate("EstudianteFormDialog", u"Nombres:*", None))
        self.txtNombres.setPlaceholderText(QCoreApplication.translate("EstudianteFormDialog", u"Ej: Juan Carlos", None))
        self.label_4.setText(QCoreApplication.translate("EstudianteFormDialog", u"Apellidos:*", None))
        self.txtApellidos.setPlaceholderText(QCoreApplication.translate("EstudianteFormDialog", u"Ej: P\u00e9rez Gonz\u00e1lez", None))
        self.label_5.setText(QCoreApplication.translate("EstudianteFormDialog", u"Fecha de Nacimiento:", None))
        self.label_6.setText(QCoreApplication.translate("EstudianteFormDialog", u"Tel\u00e9fono:", None))
        self.txtTelefono.setPlaceholderText(QCoreApplication.translate("EstudianteFormDialog", u"Ej: 77654321", None))
        self.label_7.setText(QCoreApplication.translate("EstudianteFormDialog", u"Email:", None))
        self.txtEmail.setPlaceholderText(QCoreApplication.translate("EstudianteFormDialog", u"Ej: juan.perez@email.com", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("EstudianteFormDialog", u"Informaci\u00f3n Acad\u00e9mica y Profesional", None))
        self.label_8.setText(QCoreApplication.translate("EstudianteFormDialog", u"Universidad de Egreso:", None))
        self.txtUniversidad.setPlaceholderText(QCoreApplication.translate("EstudianteFormDialog", u"Ej: Universidad Mayor de San Andr\u00e9s", None))
        self.label_9.setText(QCoreApplication.translate("EstudianteFormDialog", u"Profesi\u00f3n:", None))
        self.txtProfesion.setPlaceholderText(QCoreApplication.translate("EstudianteFormDialog", u"Ej: Ingeniero de Sistemas", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("EstudianteFormDialog", u"Estado", None))
        self.checkActivo.setText(QCoreApplication.translate("EstudianteFormDialog", u"Estudiante Activo", None))
    # retranslateUi

