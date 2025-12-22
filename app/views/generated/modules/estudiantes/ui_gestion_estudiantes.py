# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gestion_estudiantes.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QSizePolicy, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_GestionEstudiantesWidget(object):
    def setupUi(self, GestionEstudiantesWidget):
        if not GestionEstudiantesWidget.objectName():
            GestionEstudiantesWidget.setObjectName(u"GestionEstudiantesWidget")
        self.verticalLayout = QVBoxLayout(GestionEstudiantesWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.labelTitulo = QLabel(GestionEstudiantesWidget)
        self.labelTitulo.setObjectName(u"labelTitulo")
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(18)
        font.setBold(True)
        self.labelTitulo.setFont(font)
        self.labelTitulo.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.labelTitulo)

        self.tabWidget = QTabWidget(GestionEstudiantesWidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabRegistrar = QWidget()
        self.tabRegistrar.setObjectName(u"tabRegistrar")
        self.tabWidget.addTab(self.tabRegistrar, "")
        self.tabListar = QWidget()
        self.tabListar.setObjectName(u"tabListar")
        self.tabWidget.addTab(self.tabListar, "")
        self.tabBuscarCI = QWidget()
        self.tabBuscarCI.setObjectName(u"tabBuscarCI")
        self.tabWidget.addTab(self.tabBuscarCI, "")
        self.tabBuscarNombre = QWidget()
        self.tabBuscarNombre.setObjectName(u"tabBuscarNombre")
        self.tabWidget.addTab(self.tabBuscarNombre, "")
        self.tabEstadisticas = QWidget()
        self.tabEstadisticas.setObjectName(u"tabEstadisticas")
        self.tabWidget.addTab(self.tabEstadisticas, "")

        self.verticalLayout.addWidget(self.tabWidget)


        self.retranslateUi(GestionEstudiantesWidget)

        QMetaObject.connectSlotsByName(GestionEstudiantesWidget)
    # setupUi

    def retranslateUi(self, GestionEstudiantesWidget):
        self.labelTitulo.setText(QCoreApplication.translate("GestionEstudiantesWidget", u"\U0001f464 GESTI\U000000d3N DE ESTUDIANTES", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabRegistrar), QCoreApplication.translate("GestionEstudiantesWidget", u"\u2795 Registrar", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabListar), QCoreApplication.translate("GestionEstudiantesWidget", u"\U0001f4cb Listar", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabBuscarCI), QCoreApplication.translate("GestionEstudiantesWidget", u"\U0001f50d Buscar por CI", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabBuscarNombre), QCoreApplication.translate("GestionEstudiantesWidget", u"\U0001f464 Buscar por Nombre", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabEstadisticas), QCoreApplication.translate("GestionEstudiantesWidget", u"\U0001f4ca Estad\U000000edsticas", None))
        pass
    # retranslateUi

