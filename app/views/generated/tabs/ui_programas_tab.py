# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'programas_tab.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QFormLayout,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QSizePolicy, QSpacerItem, QTableWidget,
    QTableWidgetItem, QToolBar, QVBoxLayout, QWidget)

class Ui_ProgramasTab(object):
    def setupUi(self, ProgramasTab):
        if not ProgramasTab.objectName():
            ProgramasTab.setObjectName(u"ProgramasTab")
        ProgramasTab.resize(800, 600)
        self.verticalLayout = QVBoxLayout(ProgramasTab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.toolBar = QToolBar(ProgramasTab)
        self.toolBar.setObjectName(u"toolBar")
        self.toolBar.setMovable(False)

        self.verticalLayout.addWidget(self.toolBar)

        self.groupBoxFiltros = QGroupBox(ProgramasTab)
        self.groupBoxFiltros.setObjectName(u"groupBoxFiltros")
        self.horizontalLayout = QHBoxLayout(self.groupBoxFiltros)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.comboEstado = QComboBox(self.groupBoxFiltros)
        self.comboEstado.addItem("")
        self.comboEstado.addItem("")
        self.comboEstado.addItem("")
        self.comboEstado.addItem("")
        self.comboEstado.setObjectName(u"comboEstado")

        self.horizontalLayout.addWidget(self.comboEstado)

        self.txtBuscar = QLineEdit(self.groupBoxFiltros)
        self.txtBuscar.setObjectName(u"txtBuscar")

        self.horizontalLayout.addWidget(self.txtBuscar)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addWidget(self.groupBoxFiltros)

        self.tablaProgramas = QTableWidget(ProgramasTab)
        if (self.tablaProgramas.columnCount() < 5):
            self.tablaProgramas.setColumnCount(5)
        __qtablewidgetitem = QTableWidgetItem()
        self.tablaProgramas.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tablaProgramas.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tablaProgramas.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tablaProgramas.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tablaProgramas.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        self.tablaProgramas.setObjectName(u"tablaProgramas")
        self.tablaProgramas.setAlternatingRowColors(True)
        self.tablaProgramas.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tablaProgramas.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.verticalLayout.addWidget(self.tablaProgramas)

        self.groupBoxDetalles = QGroupBox(ProgramasTab)
        self.groupBoxDetalles.setObjectName(u"groupBoxDetalles")
        self.formLayout = QFormLayout(self.groupBoxDetalles)
        self.formLayout.setObjectName(u"formLayout")
        self.labelCodigo = QLabel(self.groupBoxDetalles)
        self.labelCodigo.setObjectName(u"labelCodigo")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelCodigo)

        self.lblCodigo = QLabel(self.groupBoxDetalles)
        self.lblCodigo.setObjectName(u"lblCodigo")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lblCodigo)

        self.labelNombre = QLabel(self.groupBoxDetalles)
        self.labelNombre.setObjectName(u"labelNombre")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelNombre)

        self.lblNombre = QLabel(self.groupBoxDetalles)
        self.lblNombre.setObjectName(u"lblNombre")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lblNombre)


        self.verticalLayout.addWidget(self.groupBoxDetalles)


        self.retranslateUi(ProgramasTab)

        QMetaObject.connectSlotsByName(ProgramasTab)
    # setupUi

    def retranslateUi(self, ProgramasTab):
        ProgramasTab.setWindowTitle(QCoreApplication.translate("ProgramasTab", u"Programas", None))
        self.groupBoxFiltros.setTitle(QCoreApplication.translate("ProgramasTab", u"Filtros", None))
        self.comboEstado.setItemText(0, QCoreApplication.translate("ProgramasTab", u"Todos", None))
        self.comboEstado.setItemText(1, QCoreApplication.translate("ProgramasTab", u"PLANIFICADO", None))
        self.comboEstado.setItemText(2, QCoreApplication.translate("ProgramasTab", u"INICIADO", None))
        self.comboEstado.setItemText(3, QCoreApplication.translate("ProgramasTab", u"CONCLUIDO", None))

        self.txtBuscar.setPlaceholderText(QCoreApplication.translate("ProgramasTab", u"Buscar...", None))
        ___qtablewidgetitem = self.tablaProgramas.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("ProgramasTab", u"C\u00f3digo", None));
        ___qtablewidgetitem1 = self.tablaProgramas.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("ProgramasTab", u"Nombre", None));
        ___qtablewidgetitem2 = self.tablaProgramas.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("ProgramasTab", u"Estado", None));
        ___qtablewidgetitem3 = self.tablaProgramas.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("ProgramasTab", u"Inicio", None));
        ___qtablewidgetitem4 = self.tablaProgramas.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("ProgramasTab", u"Cupos", None));
        self.groupBoxDetalles.setTitle(QCoreApplication.translate("ProgramasTab", u"Detalles", None))
        self.labelCodigo.setText(QCoreApplication.translate("ProgramasTab", u"C\u00f3digo:", None))
        self.lblCodigo.setText(QCoreApplication.translate("ProgramasTab", u"-", None))
        self.labelNombre.setText(QCoreApplication.translate("ProgramasTab", u"Nombre:", None))
        self.lblNombre.setText(QCoreApplication.translate("ProgramasTab", u"-", None))
    # retranslateUi

