# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ayuda_tab.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QSizePolicy, QSpacerItem,
    QTabWidget, QTextBrowser, QVBoxLayout, QWidget)

class Ui_AyudaTab(object):
    def setupUi(self, AyudaTab):
        if not AyudaTab.objectName():
            AyudaTab.setObjectName(u"AyudaTab")
        AyudaTab.resize(800, 600)
        self.verticalLayout = QVBoxLayout(AyudaTab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.labelTitulo = QLabel(AyudaTab)
        self.labelTitulo.setObjectName(u"labelTitulo")
        self.labelTitulo.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.labelTitulo)

        self.tabWidget = QTabWidget(AyudaTab)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabManual = QWidget()
        self.tabManual.setObjectName(u"tabManual")
        self.verticalLayout_2 = QVBoxLayout(self.tabManual)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.textBrowserManual = QTextBrowser(self.tabManual)
        self.textBrowserManual.setObjectName(u"textBrowserManual")

        self.verticalLayout_2.addWidget(self.textBrowserManual)

        self.tabWidget.addTab(self.tabManual, "")
        self.tabAcercaDe = QWidget()
        self.tabAcercaDe.setObjectName(u"tabAcercaDe")
        self.verticalLayout_3 = QVBoxLayout(self.tabAcercaDe)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.labelLogo = QLabel(self.tabAcercaDe)
        self.labelLogo.setObjectName(u"labelLogo")
        self.labelLogo.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.labelLogo)

        self.labelNombreApp = QLabel(self.tabAcercaDe)
        self.labelNombreApp.setObjectName(u"labelNombreApp")
        self.labelNombreApp.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.labelNombreApp)

        self.labelDescripcion = QLabel(self.tabAcercaDe)
        self.labelDescripcion.setObjectName(u"labelDescripcion")
        self.labelDescripcion.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.labelDescripcion)

        self.labelVersion = QLabel(self.tabAcercaDe)
        self.labelVersion.setObjectName(u"labelVersion")
        self.labelVersion.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.labelVersion)

        self.labelDesarrollado = QLabel(self.tabAcercaDe)
        self.labelDesarrollado.setObjectName(u"labelDesarrollado")
        self.labelDesarrollado.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.labelDesarrollado)

        self.labelCopyright = QLabel(self.tabAcercaDe)
        self.labelCopyright.setObjectName(u"labelCopyright")
        self.labelCopyright.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.labelCopyright)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.tabWidget.addTab(self.tabAcercaDe, "")
        self.tabSoporte = QWidget()
        self.tabSoporte.setObjectName(u"tabSoporte")
        self.verticalLayout_4 = QVBoxLayout(self.tabSoporte)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_3 = QLabel(self.tabSoporte)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignCenter)

        self.verticalLayout_4.addWidget(self.label_3)

        self.tabWidget.addTab(self.tabSoporte, "")

        self.verticalLayout.addWidget(self.tabWidget)


        self.retranslateUi(AyudaTab)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(AyudaTab)
    # setupUi

    def retranslateUi(self, AyudaTab):
        AyudaTab.setWindowTitle(QCoreApplication.translate("AyudaTab", u"Ayuda", None))
        self.labelTitulo.setText(QCoreApplication.translate("AyudaTab", u"<html><head/><body><p align=\"center\"><span style=\" font-size:24pt; font-weight:700; color:#f39c12;\">\U0001f527 AYUDA Y UTILIDADES</span></p></body></html>", None))
        self.textBrowserManual.setHtml(QCoreApplication.translate("AyudaTab", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<h1 align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:18pt; font-weight:700;\">Manual de Usuario</span></h1>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:18pt; font-weight:700;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">Bienvenido al Sistema de Gesti\U000000f3n Acad\U000000e9mica FormaGestPro.</span></p>\n"
"<p style=\""
                        "-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">\U0001f3e0 Dashboard</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\U00002022 Visualice estad\U000000edsticas generales del sistema</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\U00002022 Acceda r\U000000e1pidamente a m\U000000f3dulos principales</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" fon"
                        "t-weight:700;\">\U0001f464 Estudiantes</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\U00002022 Gesti\U000000f3n completa de estudiantes</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\U00002022 Registro, edici\U000000f3n y eliminaci\U000000f3n</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\U00002022 Visualizaci\U000000f3n de matr\U000000edculas activas</p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabManual), QCoreApplication.translate("AyudaTab", u"\U0001f4d6 Manual", None))
        self.labelLogo.setText(QCoreApplication.translate("AyudaTab", u"<html><head/><body><p align=\"center\"><span style=\" font-size:36pt;\">\U0001f3e2</span></p></body></html>", None))
        self.labelNombreApp.setText(QCoreApplication.translate("AyudaTab", u"<html><head/><body><p align=\"center\"><span style=\" font-size:18pt; font-weight:700;\">FormaGestPro</span></p></body></html>", None))
        self.labelDescripcion.setText(QCoreApplication.translate("AyudaTab", u"<html><head/><body><p align=\"center\"><span style=\" font-size:11pt;\">Sistema de Gesti\u00f3n Acad\u00e9mica</span></p></body></html>", None))
        self.labelVersion.setText(QCoreApplication.translate("AyudaTab", u"<html><head/><body><p align=\"center\"><span style=\" font-size:10pt;\">Versi\u00f3n 2.0 (GUI con pesta\u00f1as)</span></p></body></html>", None))
        self.labelDesarrollado.setText(QCoreApplication.translate("AyudaTab", u"<html><head/><body><p align=\"center\"><span style=\" font-size:10pt;\">Desarrollado por: Tu equipo de desarrollo</span></p></body></html>", None))
        self.labelCopyright.setText(QCoreApplication.translate("AyudaTab", u"<html><head/><body><p align=\"center\"><span style=\" font-size:10pt;\">\u00a9 2024 Formaci\u00f3n Continua Consultora</span></p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAcercaDe), QCoreApplication.translate("AyudaTab", u"\u2139\ufe0f Acerca de", None))
        self.label_3.setText(QCoreApplication.translate("AyudaTab", u"<html><head/><body><p align=\"center\"><span style=\" font-size:16pt;\">\U0001f6a7 M\U000000f3dulo en desarrollo \U0001f6a7</span></p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSoporte), QCoreApplication.translate("AyudaTab", u"\U0001f6e0\U0000fe0f Soporte", None))
    # retranslateUi

