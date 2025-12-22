# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window_tabs.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QMainWindow, QMenu, QMenuBar,
    QSizePolicy, QStatusBar, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1200, 800)
        self.actionSalir = QAction(MainWindow)
        self.actionSalir.setObjectName(u"actionSalir")
        self.actionEstudiantes = QAction(MainWindow)
        self.actionEstudiantes.setObjectName(u"actionEstudiantes")
        self.actionDocentes = QAction(MainWindow)
        self.actionDocentes.setObjectName(u"actionDocentes")
        self.actionProgramas = QAction(MainWindow)
        self.actionProgramas.setObjectName(u"actionProgramas")
        self.actionFinanciero = QAction(MainWindow)
        self.actionFinanciero.setObjectName(u"actionFinanciero")
        self.actionAcerca_de = QAction(MainWindow)
        self.actionAcerca_de.setObjectName(u"actionAcerca_de")
        self.actionManual = QAction(MainWindow)
        self.actionManual.setObjectName(u"actionManual")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabDashboard = QWidget()
        self.tabDashboard.setObjectName(u"tabDashboard")
        self.tabWidget.addTab(self.tabDashboard, "")
        self.tabEstudiantes = QWidget()
        self.tabEstudiantes.setObjectName(u"tabEstudiantes")
        self.tabWidget.addTab(self.tabEstudiantes, "")
        self.tabDocentes = QWidget()
        self.tabDocentes.setObjectName(u"tabDocentes")
        self.tabWidget.addTab(self.tabDocentes, "")
        self.tabProgramas = QWidget()
        self.tabProgramas.setObjectName(u"tabProgramas")
        self.tabWidget.addTab(self.tabProgramas, "")
        self.tabFinanciero = QWidget()
        self.tabFinanciero.setObjectName(u"tabFinanciero")
        self.tabWidget.addTab(self.tabFinanciero, "")
        self.tabAyuda = QWidget()
        self.tabAyuda.setObjectName(u"tabAyuda")
        self.tabWidget.addTab(self.tabAyuda, "")

        self.verticalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1200, 22))
        self.menuArchivo = QMenu(self.menubar)
        self.menuArchivo.setObjectName(u"menuArchivo")
        self.menuGestion = QMenu(self.menubar)
        self.menuGestion.setObjectName(u"menuGestion")
        self.menuAyuda = QMenu(self.menubar)
        self.menuAyuda.setObjectName(u"menuAyuda")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuArchivo.menuAction())
        self.menubar.addAction(self.menuGestion.menuAction())
        self.menubar.addAction(self.menuAyuda.menuAction())
        self.menuArchivo.addAction(self.actionSalir)
        self.menuGestion.addAction(self.actionEstudiantes)
        self.menuGestion.addAction(self.actionDocentes)
        self.menuGestion.addAction(self.actionProgramas)
        self.menuGestion.addAction(self.actionFinanciero)
        self.menuAyuda.addAction(self.actionAcerca_de)
        self.menuAyuda.addAction(self.actionManual)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(5)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"FormaGestPro - Sistema de Gesti\u00f3n Acad\u00e9mica", None))
        self.actionSalir.setText(QCoreApplication.translate("MainWindow", u"&Salir", None))
#if QT_CONFIG(shortcut)
        self.actionSalir.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Q", None))
#endif // QT_CONFIG(shortcut)
        self.actionEstudiantes.setText(QCoreApplication.translate("MainWindow", u"&Estudiantes", None))
#if QT_CONFIG(shortcut)
        self.actionEstudiantes.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+E", None))
#endif // QT_CONFIG(shortcut)
        self.actionDocentes.setText(QCoreApplication.translate("MainWindow", u"&Docentes/Tutores", None))
#if QT_CONFIG(shortcut)
        self.actionDocentes.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+D", None))
#endif // QT_CONFIG(shortcut)
        self.actionProgramas.setText(QCoreApplication.translate("MainWindow", u"&Programas Acad\u00e9micos", None))
#if QT_CONFIG(shortcut)
        self.actionProgramas.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+P", None))
#endif // QT_CONFIG(shortcut)
        self.actionFinanciero.setText(QCoreApplication.translate("MainWindow", u"&Financiero", None))
#if QT_CONFIG(shortcut)
        self.actionFinanciero.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+F", None))
#endif // QT_CONFIG(shortcut)
        self.actionAcerca_de.setText(QCoreApplication.translate("MainWindow", u"&Acerca de", None))
        self.actionManual.setText(QCoreApplication.translate("MainWindow", u"&Manual de usuario", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabDashboard), QCoreApplication.translate("MainWindow", u"\U0001f3e0 Inicio", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabEstudiantes), QCoreApplication.translate("MainWindow", u"\U0001f464 Estudiantes", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabDocentes), QCoreApplication.translate("MainWindow", u"\U0001f468\U0000200d\U0001f3eb Docentes", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabProgramas), QCoreApplication.translate("MainWindow", u"\U0001f4da Programas", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabFinanciero), QCoreApplication.translate("MainWindow", u"\U0001f4b0 Financiero", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAyuda), QCoreApplication.translate("MainWindow", u"\U0001f527 Ayuda", None))
        self.menuArchivo.setTitle(QCoreApplication.translate("MainWindow", u"&Archivo", None))
        self.menuGestion.setTitle(QCoreApplication.translate("MainWindow", u"&Gesti\u00f3n", None))
        self.menuAyuda.setTitle(QCoreApplication.translate("MainWindow", u"&Ayuda", None))
    # retranslateUi

