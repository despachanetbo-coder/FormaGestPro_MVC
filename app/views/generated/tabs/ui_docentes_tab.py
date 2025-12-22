# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'docentes_tab.ui'
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
    QGroupBox, QHeaderView, QLabel, QLineEdit,
    QSizePolicy, QSpacerItem, QSplitter, QStatusBar,
    QTableWidget, QTableWidgetItem, QToolBar, QVBoxLayout,
    QWidget)

class Ui_DocentesTab(object):
    def setupUi(self, DocentesTab):
        if not DocentesTab.objectName():
            DocentesTab.setObjectName(u"DocentesTab")
        DocentesTab.resize(800, 600)
        self.verticalLayout = QVBoxLayout(DocentesTab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.toolBar = QToolBar(DocentesTab)
        self.toolBar.setObjectName(u"toolBar")
        self.toolBar.setMovable(False)
        self.toolBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.verticalLayout.addWidget(self.toolBar)

        self.splitter = QSplitter(DocentesTab)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.widgetLista = QWidget(self.splitter)
        self.widgetLista.setObjectName(u"widgetLista")
        self.verticalLayout_2 = QVBoxLayout(self.widgetLista)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.groupBoxFiltros = QGroupBox(self.widgetLista)
        self.groupBoxFiltros.setObjectName(u"groupBoxFiltros")
        self.formLayout = QFormLayout(self.groupBoxFiltros)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(self.groupBoxFiltros)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.comboEstado = QComboBox(self.groupBoxFiltros)
        self.comboEstado.addItem("")
        self.comboEstado.addItem("")
        self.comboEstado.addItem("")
        self.comboEstado.setObjectName(u"comboEstado")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.comboEstado)

        self.label_2 = QLabel(self.groupBoxFiltros)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.comboEspecialidad = QComboBox(self.groupBoxFiltros)
        self.comboEspecialidad.addItem("")
        self.comboEspecialidad.setObjectName(u"comboEspecialidad")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.comboEspecialidad)

        self.label_3 = QLabel(self.groupBoxFiltros)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.txtBuscar = QLineEdit(self.groupBoxFiltros)
        self.txtBuscar.setObjectName(u"txtBuscar")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.txtBuscar)


        self.verticalLayout_2.addWidget(self.groupBoxFiltros)

        self.tablaDocentes = QTableWidget(self.widgetLista)
        if (self.tablaDocentes.columnCount() < 5):
            self.tablaDocentes.setColumnCount(5)
        __qtablewidgetitem = QTableWidgetItem()
        self.tablaDocentes.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tablaDocentes.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tablaDocentes.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tablaDocentes.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tablaDocentes.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        self.tablaDocentes.setObjectName(u"tablaDocentes")
        self.tablaDocentes.setAlternatingRowColors(True)
        self.tablaDocentes.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tablaDocentes.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablaDocentes.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout_2.addWidget(self.tablaDocentes)

        self.splitter.addWidget(self.widgetLista)
        self.widgetDetalles = QWidget(self.splitter)
        self.widgetDetalles.setObjectName(u"widgetDetalles")
        self.verticalLayout_3 = QVBoxLayout(self.widgetDetalles)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.groupBoxDetalles = QGroupBox(self.widgetDetalles)
        self.groupBoxDetalles.setObjectName(u"groupBoxDetalles")
        self.formLayout_2 = QFormLayout(self.groupBoxDetalles)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.labelCI = QLabel(self.groupBoxDetalles)
        self.labelCI.setObjectName(u"labelCI")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelCI)

        self.lblCI = QLabel(self.groupBoxDetalles)
        self.lblCI.setObjectName(u"lblCI")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lblCI)

        self.labelNombre = QLabel(self.groupBoxDetalles)
        self.labelNombre.setObjectName(u"labelNombre")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelNombre)

        self.lblNombre = QLabel(self.groupBoxDetalles)
        self.lblNombre.setObjectName(u"lblNombre")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lblNombre)

        self.labelGrado = QLabel(self.groupBoxDetalles)
        self.labelGrado.setObjectName(u"labelGrado")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelGrado)

        self.lblGrado = QLabel(self.groupBoxDetalles)
        self.lblGrado.setObjectName(u"lblGrado")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lblGrado)

        self.labelEspecialidad = QLabel(self.groupBoxDetalles)
        self.labelEspecialidad.setObjectName(u"labelEspecialidad")

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelEspecialidad)

        self.lblEspecialidad = QLabel(self.groupBoxDetalles)
        self.lblEspecialidad.setObjectName(u"lblEspecialidad")

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.FieldRole, self.lblEspecialidad)

        self.labelHonorario = QLabel(self.groupBoxDetalles)
        self.labelHonorario.setObjectName(u"labelHonorario")

        self.formLayout_2.setWidget(4, QFormLayout.ItemRole.LabelRole, self.labelHonorario)

        self.lblHonorario = QLabel(self.groupBoxDetalles)
        self.lblHonorario.setObjectName(u"lblHonorario")

        self.formLayout_2.setWidget(4, QFormLayout.ItemRole.FieldRole, self.lblHonorario)

        self.labelEmail = QLabel(self.groupBoxDetalles)
        self.labelEmail.setObjectName(u"labelEmail")

        self.formLayout_2.setWidget(5, QFormLayout.ItemRole.LabelRole, self.labelEmail)

        self.lblEmail = QLabel(self.groupBoxDetalles)
        self.lblEmail.setObjectName(u"lblEmail")

        self.formLayout_2.setWidget(5, QFormLayout.ItemRole.FieldRole, self.lblEmail)

        self.labelEstado = QLabel(self.groupBoxDetalles)
        self.labelEstado.setObjectName(u"labelEstado")

        self.formLayout_2.setWidget(6, QFormLayout.ItemRole.LabelRole, self.labelEstado)

        self.lblEstado = QLabel(self.groupBoxDetalles)
        self.lblEstado.setObjectName(u"lblEstado")

        self.formLayout_2.setWidget(6, QFormLayout.ItemRole.FieldRole, self.lblEstado)


        self.verticalLayout_3.addWidget(self.groupBoxDetalles)

        self.groupBoxProgramas = QGroupBox(self.widgetDetalles)
        self.groupBoxProgramas.setObjectName(u"groupBoxProgramas")
        self.verticalLayout_4 = QVBoxLayout(self.groupBoxProgramas)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.tablaProgramas = QTableWidget(self.groupBoxProgramas)
        if (self.tablaProgramas.columnCount() < 3):
            self.tablaProgramas.setColumnCount(3)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tablaProgramas.setHorizontalHeaderItem(0, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tablaProgramas.setHorizontalHeaderItem(1, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tablaProgramas.setHorizontalHeaderItem(2, __qtablewidgetitem7)
        self.tablaProgramas.setObjectName(u"tablaProgramas")
        self.tablaProgramas.setAlternatingRowColors(True)
        self.tablaProgramas.setSelectionMode(QAbstractItemView.NoSelection)
        self.tablaProgramas.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout_4.addWidget(self.tablaProgramas)


        self.verticalLayout_3.addWidget(self.groupBoxProgramas)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.splitter.addWidget(self.widgetDetalles)

        self.verticalLayout.addWidget(self.splitter)

        self.statusBar = QStatusBar(DocentesTab)
        self.statusBar.setObjectName(u"statusBar")

        self.verticalLayout.addWidget(self.statusBar)


        self.retranslateUi(DocentesTab)

        QMetaObject.connectSlotsByName(DocentesTab)
    # setupUi

    def retranslateUi(self, DocentesTab):
        DocentesTab.setWindowTitle(QCoreApplication.translate("DocentesTab", u"Docentes", None))
        self.groupBoxFiltros.setTitle(QCoreApplication.translate("DocentesTab", u"\U0001f50d Filtros de B\U000000fasqueda", None))
        self.label.setText(QCoreApplication.translate("DocentesTab", u"Estado:", None))
        self.comboEstado.setItemText(0, QCoreApplication.translate("DocentesTab", u"Todos", None))
        self.comboEstado.setItemText(1, QCoreApplication.translate("DocentesTab", u"Activo", None))
        self.comboEstado.setItemText(2, QCoreApplication.translate("DocentesTab", u"Inactivo", None))

        self.label_2.setText(QCoreApplication.translate("DocentesTab", u"Especialidad:", None))
        self.comboEspecialidad.setItemText(0, QCoreApplication.translate("DocentesTab", u"Todas", None))

        self.label_3.setText(QCoreApplication.translate("DocentesTab", u"Buscar:", None))
        self.txtBuscar.setPlaceholderText(QCoreApplication.translate("DocentesTab", u"Nombre, CI, email...", None))
        ___qtablewidgetitem = self.tablaDocentes.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("DocentesTab", u"CI", None));
        ___qtablewidgetitem1 = self.tablaDocentes.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("DocentesTab", u"Nombre Completo", None));
        ___qtablewidgetitem2 = self.tablaDocentes.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("DocentesTab", u"Especialidad", None));
        ___qtablewidgetitem3 = self.tablaDocentes.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("DocentesTab", u"Honorario/h", None));
        ___qtablewidgetitem4 = self.tablaDocentes.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("DocentesTab", u"Estado", None));
        self.groupBoxDetalles.setTitle(QCoreApplication.translate("DocentesTab", u"\U0001f468\U0000200d\U0001f3eb Detalles del Docente", None))
        self.labelCI.setText(QCoreApplication.translate("DocentesTab", u"CI:", None))
        self.lblCI.setText(QCoreApplication.translate("DocentesTab", u"-", None))
        self.labelNombre.setText(QCoreApplication.translate("DocentesTab", u"Nombre:", None))
        self.lblNombre.setText(QCoreApplication.translate("DocentesTab", u"-", None))
        self.labelGrado.setText(QCoreApplication.translate("DocentesTab", u"Grado Acad\u00e9mico:", None))
        self.lblGrado.setText(QCoreApplication.translate("DocentesTab", u"-", None))
        self.labelEspecialidad.setText(QCoreApplication.translate("DocentesTab", u"Especialidad:", None))
        self.lblEspecialidad.setText(QCoreApplication.translate("DocentesTab", u"-", None))
        self.labelHonorario.setText(QCoreApplication.translate("DocentesTab", u"Honorario/hora:", None))
        self.lblHonorario.setText(QCoreApplication.translate("DocentesTab", u"-", None))
        self.labelEmail.setText(QCoreApplication.translate("DocentesTab", u"Email:", None))
        self.lblEmail.setText(QCoreApplication.translate("DocentesTab", u"-", None))
        self.labelEstado.setText(QCoreApplication.translate("DocentesTab", u"Estado:", None))
        self.lblEstado.setText(QCoreApplication.translate("DocentesTab", u"-", None))
        self.groupBoxProgramas.setTitle(QCoreApplication.translate("DocentesTab", u"\U0001f4da Programas Asignados", None))
        ___qtablewidgetitem5 = self.tablaProgramas.horizontalHeaderItem(0)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("DocentesTab", u"Programa", None));
        ___qtablewidgetitem6 = self.tablaProgramas.horizontalHeaderItem(1)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("DocentesTab", u"Estado", None));
        ___qtablewidgetitem7 = self.tablaProgramas.horizontalHeaderItem(2)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("DocentesTab", u"Inicio", None));
    # retranslateUi

