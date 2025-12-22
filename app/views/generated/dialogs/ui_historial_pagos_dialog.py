# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'historial_pagos_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QHeaderView, QLabel, QSizePolicy, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_HistorialPagosDialog(object):
    def setupUi(self, HistorialPagosDialog):
        if not HistorialPagosDialog.objectName():
            HistorialPagosDialog.setObjectName(u"HistorialPagosDialog")
        HistorialPagosDialog.resize(800, 600)
        self.verticalLayout = QVBoxLayout(HistorialPagosDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.lblInfoEstudiante = QLabel(HistorialPagosDialog)
        self.lblInfoEstudiante.setObjectName(u"lblInfoEstudiante")
        self.lblInfoEstudiante.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.lblInfoEstudiante)

        self.tablePagos = QTableWidget(HistorialPagosDialog)
        if (self.tablePagos.columnCount() < 5):
            self.tablePagos.setColumnCount(5)
        __qtablewidgetitem = QTableWidgetItem()
        self.tablePagos.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tablePagos.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tablePagos.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tablePagos.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tablePagos.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        self.tablePagos.setObjectName(u"tablePagos")
        self.tablePagos.setColumnCount(5)
        self.tablePagos.horizontalHeader().setVisible(True)
        self.tablePagos.horizontalHeader().setCascadingSectionResizes(False)
        self.tablePagos.horizontalHeader().setHighlightSections(True)
        self.tablePagos.horizontalHeader().setStretchLastSection(False)
        self.tablePagos.verticalHeader().setVisible(False)

        self.verticalLayout.addWidget(self.tablePagos)

        self.buttonBox = QDialogButtonBox(HistorialPagosDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(HistorialPagosDialog)
        self.buttonBox.rejected.connect(HistorialPagosDialog.reject)

        QMetaObject.connectSlotsByName(HistorialPagosDialog)
    # setupUi

    def retranslateUi(self, HistorialPagosDialog):
        HistorialPagosDialog.setWindowTitle(QCoreApplication.translate("HistorialPagosDialog", u"Historial de Pagos", None))
        self.lblInfoEstudiante.setText(QCoreApplication.translate("HistorialPagosDialog", u"Informaci\u00f3n del estudiante", None))
        ___qtablewidgetitem = self.tablePagos.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("HistorialPagosDialog", u"ID", None));
        ___qtablewidgetitem1 = self.tablePagos.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("HistorialPagosDialog", u"Programa", None));
        ___qtablewidgetitem2 = self.tablePagos.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("HistorialPagosDialog", u"Monto", None));
        ___qtablewidgetitem3 = self.tablePagos.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("HistorialPagosDialog", u"Fecha", None));
        ___qtablewidgetitem4 = self.tablePagos.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("HistorialPagosDialog", u"Estado", None));
    # retranslateUi

