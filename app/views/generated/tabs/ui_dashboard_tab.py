# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dashboard_tab.ui'
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

class Ui_EstudiantesTab(object):
    def setupUi(self, EstudiantesTab):
        if not EstudiantesTab.objectName():
            EstudiantesTab.setObjectName(u"EstudiantesTab")
        EstudiantesTab.resize(800, 600)
        self.verticalLayout = QVBoxLayout(EstudiantesTab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.toolBar = QToolBar(EstudiantesTab)
        self.toolBar.setObjectName(u"toolBar")
        self.toolBar.setMovable(False)
        self.toolBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.verticalLayout.addWidget(self.toolBar)

        self.splitter = QSplitter(EstudiantesTab)
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

        self.txtBuscar = QLineEdit(self.groupBoxFiltros)
        self.txtBuscar.setObjectName(u"txtBuscar")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.txtBuscar)


        self.verticalLayout_2.addWidget(self.groupBoxFiltros)

        self.tablaEstudiantes = QTableWidget(self.widgetLista)
        if (self.tablaEstudiantes.columnCount() < 5):
            self.tablaEstudiantes.setColumnCount(5)
        __qtablewidgetitem = QTableWidgetItem()
        self.tablaEstudiantes.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tablaEstudiantes.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tablaEstudiantes.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tablaEstudiantes.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tablaEstudiantes.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        self.tablaEstudiantes.setObjectName(u"tablaEstudiantes")
        self.tablaEstudiantes.setAlternatingRowColors(True)
        self.tablaEstudiantes.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tablaEstudiantes.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablaEstudiantes.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout_2.addWidget(self.tablaEstudiantes)

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

        self.labelEmail = QLabel(self.groupBoxDetalles)
        self.labelEmail.setObjectName(u"labelEmail")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelEmail)

        self.lblEmail = QLabel(self.groupBoxDetalles)
        self.lblEmail.setObjectName(u"lblEmail")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lblEmail)

        self.labelTelefono = QLabel(self.groupBoxDetalles)
        self.labelTelefono.setObjectName(u"labelTelefono")

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelTelefono)

        self.lblTelefono = QLabel(self.groupBoxDetalles)
        self.lblTelefono.setObjectName(u"lblTelefono")

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.FieldRole, self.lblTelefono)

        self.labelUniversidad = QLabel(self.groupBoxDetalles)
        self.labelUniversidad.setObjectName(u"labelUniversidad")

        self.formLayout_2.setWidget(4, QFormLayout.ItemRole.LabelRole, self.labelUniversidad)

        self.lblUniversidad = QLabel(self.groupBoxDetalles)
        self.lblUniversidad.setObjectName(u"lblUniversidad")

        self.formLayout_2.setWidget(4, QFormLayout.ItemRole.FieldRole, self.lblUniversidad)

        self.labelEstado = QLabel(self.groupBoxDetalles)
        self.labelEstado.setObjectName(u"labelEstado")

        self.formLayout_2.setWidget(5, QFormLayout.ItemRole.LabelRole, self.labelEstado)

        self.lblEstado = QLabel(self.groupBoxDetalles)
        self.lblEstado.setObjectName(u"lblEstado")

        self.formLayout_2.setWidget(5, QFormLayout.ItemRole.FieldRole, self.lblEstado)


        self.verticalLayout_3.addWidget(self.groupBoxDetalles)

        self.groupBoxMatriculas = QGroupBox(self.widgetDetalles)
        self.groupBoxMatriculas.setObjectName(u"groupBoxMatriculas")
        self.verticalLayout_4 = QVBoxLayout(self.groupBoxMatriculas)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.tablaMatriculas = QTableWidget(self.groupBoxMatriculas)
        if (self.tablaMatriculas.columnCount() < 3):
            self.tablaMatriculas.setColumnCount(3)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tablaMatriculas.setHorizontalHeaderItem(0, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tablaMatriculas.setHorizontalHeaderItem(1, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tablaMatriculas.setHorizontalHeaderItem(2, __qtablewidgetitem7)
        self.tablaMatriculas.setObjectName(u"tablaMatriculas")
        self.tablaMatriculas.setAlternatingRowColors(True)
        self.tablaMatriculas.setSelectionMode(QAbstractItemView.NoSelection)
        self.tablaMatriculas.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout_4.addWidget(self.tablaMatriculas)


        self.verticalLayout_3.addWidget(self.groupBoxMatriculas)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_2)

        self.splitter.addWidget(self.widgetDetalles)

        self.verticalLayout.addWidget(self.splitter)

        self.statusBar = QStatusBar(EstudiantesTab)
        self.statusBar.setObjectName(u"statusBar")

        self.verticalLayout.addWidget(self.statusBar)


        self.retranslateUi(EstudiantesTab)

        QMetaObject.connectSlotsByName(EstudiantesTab)
    # setupUi

    def retranslateUi(self, EstudiantesTab):
        EstudiantesTab.setWindowTitle(QCoreApplication.translate("EstudiantesTab", u"Estudiantes", None))
        self.groupBoxFiltros.setTitle(QCoreApplication.translate("EstudiantesTab", u"\U0001f50d Filtros de B\U000000fasqueda", None))
        self.label.setText(QCoreApplication.translate("EstudiantesTab", u"Estado:", None))
        self.comboEstado.setItemText(0, QCoreApplication.translate("EstudiantesTab", u"Todos", None))
        self.comboEstado.setItemText(1, QCoreApplication.translate("EstudiantesTab", u"Activo", None))
        self.comboEstado.setItemText(2, QCoreApplication.translate("EstudiantesTab", u"Inactivo", None))

        self.label_2.setText(QCoreApplication.translate("EstudiantesTab", u"Buscar:", None))
        self.txtBuscar.setPlaceholderText(QCoreApplication.translate("EstudiantesTab", u"Nombre, CI, email...", None))
        ___qtablewidgetitem = self.tablaEstudiantes.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("EstudiantesTab", u"CI", None));
        ___qtablewidgetitem1 = self.tablaEstudiantes.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("EstudiantesTab", u"Nombre Completo", None));
        ___qtablewidgetitem2 = self.tablaEstudiantes.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("EstudiantesTab", u"Tel\u00e9fono", None));
        ___qtablewidgetitem3 = self.tablaEstudiantes.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("EstudiantesTab", u"Email", None));
        ___qtablewidgetitem4 = self.tablaEstudiantes.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("EstudiantesTab", u"Estado", None));
        self.groupBoxDetalles.setTitle(QCoreApplication.translate("EstudiantesTab", u"\U0001f464 Detalles del Estudiante", None))
        self.labelCI.setText(QCoreApplication.translate("EstudiantesTab", u"CI:", None))
        self.lblCI.setText(QCoreApplication.translate("EstudiantesTab", u"-", None))
        self.labelNombre.setText(QCoreApplication.translate("EstudiantesTab", u"Nombre:", None))
        self.lblNombre.setText(QCoreApplication.translate("EstudiantesTab", u"-", None))
        self.labelEmail.setText(QCoreApplication.translate("EstudiantesTab", u"Email:", None))
        self.lblEmail.setText(QCoreApplication.translate("EstudiantesTab", u"-", None))
        self.labelTelefono.setText(QCoreApplication.translate("EstudiantesTab", u"Tel\u00e9fono:", None))
        self.lblTelefono.setText(QCoreApplication.translate("EstudiantesTab", u"-", None))
        self.labelUniversidad.setText(QCoreApplication.translate("EstudiantesTab", u"Universidad:", None))
        self.lblUniversidad.setText(QCoreApplication.translate("EstudiantesTab", u"-", None))
        self.labelEstado.setText(QCoreApplication.translate("EstudiantesTab", u"Estado:", None))
        self.lblEstado.setText(QCoreApplication.translate("EstudiantesTab", u"-", None))
        self.groupBoxMatriculas.setTitle(QCoreApplication.translate("EstudiantesTab", u"\U0001f4da Matr\U000000edculas Activas", None))
        ___qtablewidgetitem5 = self.tablaMatriculas.horizontalHeaderItem(0)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("EstudiantesTab", u"Programa", None));
        ___qtablewidgetitem6 = self.tablaMatriculas.horizontalHeaderItem(1)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("EstudiantesTab", u"Estado", None));
        ___qtablewidgetitem7 = self.tablaMatriculas.horizontalHeaderItem(2)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("EstudiantesTab", u"Fecha", None));
    # retranslateUi

