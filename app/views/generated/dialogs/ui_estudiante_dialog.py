# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'estudiante_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QDialog,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QStatusBar, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)

class Ui_EstudianteDialog(object):
    def setupUi(self, EstudianteDialog):
        if not EstudianteDialog.objectName():
            EstudianteDialog.setObjectName(u"EstudianteDialog")
        EstudianteDialog.resize(1000, 700)
        self.verticalLayout = QVBoxLayout(EstudianteDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.labelTitulo = QLabel(EstudianteDialog)
        self.labelTitulo.setObjectName(u"labelTitulo")
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(18)
        font.setBold(True)
        self.labelTitulo.setFont(font)
        self.labelTitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.labelTitulo)

        self.groupBoxBusqueda = QGroupBox(EstudianteDialog)
        self.groupBoxBusqueda.setObjectName(u"groupBoxBusqueda")
        self.horizontalLayout = QHBoxLayout(self.groupBoxBusqueda)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.widgetBuscarCI = QWidget(self.groupBoxBusqueda)
        self.widgetBuscarCI.setObjectName(u"widgetBuscarCI")
        self.horizontalLayout_2 = QHBoxLayout(self.widgetBuscarCI)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.labelBuscarCI = QLabel(self.widgetBuscarCI)
        self.labelBuscarCI.setObjectName(u"labelBuscarCI")

        self.horizontalLayout_2.addWidget(self.labelBuscarCI)

        self.txtBuscarCINumero = QLineEdit(self.widgetBuscarCI)
        self.txtBuscarCINumero.setObjectName(u"txtBuscarCINumero")
        self.txtBuscarCINumero.setMaxLength(15)

        self.horizontalLayout_2.addWidget(self.txtBuscarCINumero)

        self.comboBuscarExpedicion = QComboBox(self.widgetBuscarCI)
        self.comboBuscarExpedicion.addItem("")
        self.comboBuscarExpedicion.addItem("")
        self.comboBuscarExpedicion.addItem("")
        self.comboBuscarExpedicion.addItem("")
        self.comboBuscarExpedicion.addItem("")
        self.comboBuscarExpedicion.addItem("")
        self.comboBuscarExpedicion.addItem("")
        self.comboBuscarExpedicion.addItem("")
        self.comboBuscarExpedicion.addItem("")
        self.comboBuscarExpedicion.addItem("")
        self.comboBuscarExpedicion.addItem("")
        self.comboBuscarExpedicion.setObjectName(u"comboBuscarExpedicion")

        self.horizontalLayout_2.addWidget(self.comboBuscarExpedicion)

        self.btnBuscarCI = QPushButton(self.widgetBuscarCI)
        self.btnBuscarCI.setObjectName(u"btnBuscarCI")
        icon = QIcon()
        icon.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btnBuscarCI.setIcon(icon)

        self.horizontalLayout_2.addWidget(self.btnBuscarCI)


        self.horizontalLayout.addWidget(self.widgetBuscarCI)

        self.widgetBuscarNombre = QWidget(self.groupBoxBusqueda)
        self.widgetBuscarNombre.setObjectName(u"widgetBuscarNombre")
        self.horizontalLayout_3 = QHBoxLayout(self.widgetBuscarNombre)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.labelBuscarNombre = QLabel(self.widgetBuscarNombre)
        self.labelBuscarNombre.setObjectName(u"labelBuscarNombre")

        self.horizontalLayout_3.addWidget(self.labelBuscarNombre)

        self.txtBuscarNombre = QLineEdit(self.widgetBuscarNombre)
        self.txtBuscarNombre.setObjectName(u"txtBuscarNombre")

        self.horizontalLayout_3.addWidget(self.txtBuscarNombre)

        self.btnBuscarNombre = QPushButton(self.widgetBuscarNombre)
        self.btnBuscarNombre.setObjectName(u"btnBuscarNombre")

        self.horizontalLayout_3.addWidget(self.btnBuscarNombre)


        self.horizontalLayout.addWidget(self.widgetBuscarNombre)

        self.btnMostrarTodos = QPushButton(self.groupBoxBusqueda)
        self.btnMostrarTodos.setObjectName(u"btnMostrarTodos")

        self.horizontalLayout.addWidget(self.btnMostrarTodos)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.btnNuevoEstudiante = QPushButton(self.groupBoxBusqueda)
        self.btnNuevoEstudiante.setObjectName(u"btnNuevoEstudiante")
        self.btnNuevoEstudiante.setStyleSheet(u"background-color: #4CAF50; color: white; font-weight: bold; padding: 8px 16px;")

        self.horizontalLayout.addWidget(self.btnNuevoEstudiante)


        self.verticalLayout.addWidget(self.groupBoxBusqueda)

        self.tableEstudiantes = QTableWidget(EstudianteDialog)
        if (self.tableEstudiantes.columnCount() < 9):
            self.tableEstudiantes.setColumnCount(9)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableEstudiantes.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableEstudiantes.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableEstudiantes.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableEstudiantes.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableEstudiantes.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableEstudiantes.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tableEstudiantes.setHorizontalHeaderItem(6, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tableEstudiantes.setHorizontalHeaderItem(7, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tableEstudiantes.setHorizontalHeaderItem(8, __qtablewidgetitem8)
        self.tableEstudiantes.setObjectName(u"tableEstudiantes")
        self.tableEstudiantes.setAlternatingRowColors(True)
        self.tableEstudiantes.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableEstudiantes.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableEstudiantes.setShowGrid(True)
        self.tableEstudiantes.setGridStyle(Qt.PenStyle.SolidLine)
        self.tableEstudiantes.setWordWrap(False)
        self.tableEstudiantes.horizontalHeader().setVisible(True)
        self.tableEstudiantes.horizontalHeader().setStretchLastSection(True)
        self.tableEstudiantes.verticalHeader().setVisible(False)

        self.verticalLayout.addWidget(self.tableEstudiantes)

        self.widgetControles = QWidget(EstudianteDialog)
        self.widgetControles.setObjectName(u"widgetControles")
        self.horizontalLayout_4 = QHBoxLayout(self.widgetControles)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.labelContador = QLabel(self.widgetControles)
        self.labelContador.setObjectName(u"labelContador")

        self.horizontalLayout_4.addWidget(self.labelContador)

        self.widgetPaginacion = QWidget(self.widgetControles)
        self.widgetPaginacion.setObjectName(u"widgetPaginacion")
        self.horizontalLayout_5 = QHBoxLayout(self.widgetPaginacion)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.btnPrimeraPagina = QPushButton(self.widgetPaginacion)
        self.btnPrimeraPagina.setObjectName(u"btnPrimeraPagina")
        self.btnPrimeraPagina.setEnabled(False)

        self.horizontalLayout_5.addWidget(self.btnPrimeraPagina)

        self.btnPaginaAnterior = QPushButton(self.widgetPaginacion)
        self.btnPaginaAnterior.setObjectName(u"btnPaginaAnterior")
        self.btnPaginaAnterior.setEnabled(False)

        self.horizontalLayout_5.addWidget(self.btnPaginaAnterior)

        self.labelPaginaActual = QLabel(self.widgetPaginacion)
        self.labelPaginaActual.setObjectName(u"labelPaginaActual")

        self.horizontalLayout_5.addWidget(self.labelPaginaActual)

        self.btnPaginaSiguiente = QPushButton(self.widgetPaginacion)
        self.btnPaginaSiguiente.setObjectName(u"btnPaginaSiguiente")
        self.btnPaginaSiguiente.setEnabled(False)

        self.horizontalLayout_5.addWidget(self.btnPaginaSiguiente)

        self.btnUltimaPagina = QPushButton(self.widgetPaginacion)
        self.btnUltimaPagina.setObjectName(u"btnUltimaPagina")
        self.btnUltimaPagina.setEnabled(False)

        self.horizontalLayout_5.addWidget(self.btnUltimaPagina)


        self.horizontalLayout_4.addWidget(self.widgetPaginacion)

        self.widgetRegistrosPagina = QWidget(self.widgetControles)
        self.widgetRegistrosPagina.setObjectName(u"widgetRegistrosPagina")
        self.horizontalLayout_6 = QHBoxLayout(self.widgetRegistrosPagina)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.labelRegistrosPagina = QLabel(self.widgetRegistrosPagina)
        self.labelRegistrosPagina.setObjectName(u"labelRegistrosPagina")

        self.horizontalLayout_6.addWidget(self.labelRegistrosPagina)

        self.comboRegistrosPagina = QComboBox(self.widgetRegistrosPagina)
        self.comboRegistrosPagina.addItem("")
        self.comboRegistrosPagina.addItem("")
        self.comboRegistrosPagina.addItem("")
        self.comboRegistrosPagina.addItem("")
        self.comboRegistrosPagina.addItem("")
        self.comboRegistrosPagina.setObjectName(u"comboRegistrosPagina")

        self.horizontalLayout_6.addWidget(self.comboRegistrosPagina)


        self.horizontalLayout_4.addWidget(self.widgetRegistrosPagina)


        self.verticalLayout.addWidget(self.widgetControles)

        self.statusbar = QStatusBar(EstudianteDialog)
        self.statusbar.setObjectName(u"statusbar")

        self.verticalLayout.addWidget(self.statusbar)


        self.retranslateUi(EstudianteDialog)

        QMetaObject.connectSlotsByName(EstudianteDialog)
    # setupUi

    def retranslateUi(self, EstudianteDialog):
        EstudianteDialog.setWindowTitle(QCoreApplication.translate("EstudianteDialog", u"Gesti\u00f3n de Estudiantes", None))
        self.labelTitulo.setText(QCoreApplication.translate("EstudianteDialog", u"\U0001f464 GESTI\U000000d3N DE ESTUDIANTES", None))
        self.groupBoxBusqueda.setTitle(QCoreApplication.translate("EstudianteDialog", u"\U0001f50d Buscar Estudiantes", None))
        self.labelBuscarCI.setText(QCoreApplication.translate("EstudianteDialog", u"CI:", None))
        self.txtBuscarCINumero.setPlaceholderText(QCoreApplication.translate("EstudianteDialog", u"N\u00famero de CI", None))
        self.comboBuscarExpedicion.setItemText(0, QCoreApplication.translate("EstudianteDialog", u"Todas", None))
        self.comboBuscarExpedicion.setItemText(1, QCoreApplication.translate("EstudianteDialog", u"BE", None))
        self.comboBuscarExpedicion.setItemText(2, QCoreApplication.translate("EstudianteDialog", u"CH", None))
        self.comboBuscarExpedicion.setItemText(3, QCoreApplication.translate("EstudianteDialog", u"CB", None))
        self.comboBuscarExpedicion.setItemText(4, QCoreApplication.translate("EstudianteDialog", u"LP", None))
        self.comboBuscarExpedicion.setItemText(5, QCoreApplication.translate("EstudianteDialog", u"OR", None))
        self.comboBuscarExpedicion.setItemText(6, QCoreApplication.translate("EstudianteDialog", u"PD", None))
        self.comboBuscarExpedicion.setItemText(7, QCoreApplication.translate("EstudianteDialog", u"PT", None))
        self.comboBuscarExpedicion.setItemText(8, QCoreApplication.translate("EstudianteDialog", u"SC", None))
        self.comboBuscarExpedicion.setItemText(9, QCoreApplication.translate("EstudianteDialog", u"TJ", None))
        self.comboBuscarExpedicion.setItemText(10, QCoreApplication.translate("EstudianteDialog", u"EX", None))

        self.btnBuscarCI.setText(QCoreApplication.translate("EstudianteDialog", u"Buscar por CI", None))
        self.labelBuscarNombre.setText(QCoreApplication.translate("EstudianteDialog", u"Nombre:", None))
        self.txtBuscarNombre.setPlaceholderText(QCoreApplication.translate("EstudianteDialog", u"Nombre o apellido", None))
        self.btnBuscarNombre.setText(QCoreApplication.translate("EstudianteDialog", u"Buscar por Nombre", None))
        self.btnMostrarTodos.setText(QCoreApplication.translate("EstudianteDialog", u"Mostrar Todos", None))
        self.btnNuevoEstudiante.setText(QCoreApplication.translate("EstudianteDialog", u"\u2795 Nuevo Estudiante", None))
        ___qtablewidgetitem = self.tableEstudiantes.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("EstudianteDialog", u"ID", None));
        ___qtablewidgetitem1 = self.tableEstudiantes.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("EstudianteDialog", u"CI", None));
        ___qtablewidgetitem2 = self.tableEstudiantes.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("EstudianteDialog", u"Nombre Completo", None));
        ___qtablewidgetitem3 = self.tableEstudiantes.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("EstudianteDialog", u"Email", None));
        ___qtablewidgetitem4 = self.tableEstudiantes.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("EstudianteDialog", u"Tel\u00e9fono", None));
        ___qtablewidgetitem5 = self.tableEstudiantes.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("EstudianteDialog", u"Universidad", None));
        ___qtablewidgetitem6 = self.tableEstudiantes.horizontalHeaderItem(6)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("EstudianteDialog", u"Profesi\u00f3n", None));
        ___qtablewidgetitem7 = self.tableEstudiantes.horizontalHeaderItem(7)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("EstudianteDialog", u"Estado", None));
        ___qtablewidgetitem8 = self.tableEstudiantes.horizontalHeaderItem(8)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("EstudianteDialog", u"Acciones", None));
        self.labelContador.setText(QCoreApplication.translate("EstudianteDialog", u"Mostrando 0 de 0 estudiantes", None))
        self.btnPrimeraPagina.setText(QCoreApplication.translate("EstudianteDialog", u"\u00ab Primera", None))
        self.btnPaginaAnterior.setText(QCoreApplication.translate("EstudianteDialog", u"\u2039 Anterior", None))
        self.labelPaginaActual.setText(QCoreApplication.translate("EstudianteDialog", u"P\u00e1gina 1 de 1", None))
        self.btnPaginaSiguiente.setText(QCoreApplication.translate("EstudianteDialog", u"Siguiente \u203a", None))
        self.btnUltimaPagina.setText(QCoreApplication.translate("EstudianteDialog", u"\u00daltima \u00bb", None))
        self.labelRegistrosPagina.setText(QCoreApplication.translate("EstudianteDialog", u"Registros por p\u00e1gina:", None))
        self.comboRegistrosPagina.setItemText(0, QCoreApplication.translate("EstudianteDialog", u"10", None))
        self.comboRegistrosPagina.setItemText(1, QCoreApplication.translate("EstudianteDialog", u"25", None))
        self.comboRegistrosPagina.setItemText(2, QCoreApplication.translate("EstudianteDialog", u"50", None))
        self.comboRegistrosPagina.setItemText(3, QCoreApplication.translate("EstudianteDialog", u"100", None))
        self.comboRegistrosPagina.setItemText(4, QCoreApplication.translate("EstudianteDialog", u"Todos", None))

    # retranslateUi

