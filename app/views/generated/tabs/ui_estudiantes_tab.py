# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'estudiantes_tab.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QFrame,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)
import icons_rc # type: ignore

class Ui_EstudiantesTab(object):
    def setupUi(self, EstudiantesTab):
        if not EstudiantesTab.objectName():
            EstudiantesTab.setObjectName(u"EstudiantesTab")
        EstudiantesTab.resize(1200, 700)
        self.verticalLayout = QVBoxLayout(EstudiantesTab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBoxBusqueda = QGroupBox(EstudiantesTab)
        self.groupBoxBusqueda.setObjectName(u"groupBoxBusqueda")
        self.horizontalLayoutBusqueda = QHBoxLayout(self.groupBoxBusqueda)
        self.horizontalLayoutBusqueda.setObjectName(u"horizontalLayoutBusqueda")
        self.groupBoxBuscarCI = QGroupBox(self.groupBoxBusqueda)
        self.groupBoxBuscarCI.setObjectName(u"groupBoxBuscarCI")
        self.horizontalLayoutCI = QHBoxLayout(self.groupBoxBuscarCI)
        self.horizontalLayoutCI.setObjectName(u"horizontalLayoutCI")
        self.txtBuscarCINumero = QLineEdit(self.groupBoxBuscarCI)
        self.txtBuscarCINumero.setObjectName(u"txtBuscarCINumero")

        self.horizontalLayoutCI.addWidget(self.txtBuscarCINumero)

        self.comboBuscarExpedicion = QComboBox(self.groupBoxBuscarCI)
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

        self.horizontalLayoutCI.addWidget(self.comboBuscarExpedicion)

        self.btnBuscarCI = QPushButton(self.groupBoxBuscarCI)
        self.btnBuscarCI.setObjectName(u"btnBuscarCI")
        icon = QIcon()
        icon.addFile(u":/icons/search.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btnBuscarCI.setIcon(icon)

        self.horizontalLayoutCI.addWidget(self.btnBuscarCI)


        self.horizontalLayoutBusqueda.addWidget(self.groupBoxBuscarCI)

        self.groupBoxBuscarNombre = QGroupBox(self.groupBoxBusqueda)
        self.groupBoxBuscarNombre.setObjectName(u"groupBoxBuscarNombre")
        self.horizontalLayoutNombre = QHBoxLayout(self.groupBoxBuscarNombre)
        self.horizontalLayoutNombre.setObjectName(u"horizontalLayoutNombre")
        self.txtBuscarNombre = QLineEdit(self.groupBoxBuscarNombre)
        self.txtBuscarNombre.setObjectName(u"txtBuscarNombre")

        self.horizontalLayoutNombre.addWidget(self.txtBuscarNombre)

        self.btnBuscarNombre = QPushButton(self.groupBoxBuscarNombre)
        self.btnBuscarNombre.setObjectName(u"btnBuscarNombre")
        self.btnBuscarNombre.setIcon(icon)

        self.horizontalLayoutNombre.addWidget(self.btnBuscarNombre)


        self.horizontalLayoutBusqueda.addWidget(self.groupBoxBuscarNombre)

        self.horizontalSpacerBusqueda = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutBusqueda.addItem(self.horizontalSpacerBusqueda)

        self.btnNuevoEstudiante = QPushButton(self.groupBoxBusqueda)
        self.btnNuevoEstudiante.setObjectName(u"btnNuevoEstudiante")
        icon1 = QIcon()
        icon1.addFile(u":/icons/add.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btnNuevoEstudiante.setIcon(icon1)

        self.horizontalLayoutBusqueda.addWidget(self.btnNuevoEstudiante)

        self.btnMostrarTodos = QPushButton(self.groupBoxBusqueda)
        self.btnMostrarTodos.setObjectName(u"btnMostrarTodos")
        icon2 = QIcon()
        icon2.addFile(u":/icons/list.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btnMostrarTodos.setIcon(icon2)

        self.horizontalLayoutBusqueda.addWidget(self.btnMostrarTodos)


        self.verticalLayout.addWidget(self.groupBoxBusqueda)

        self.frameControles = QFrame(EstudiantesTab)
        self.frameControles.setObjectName(u"frameControles")
        self.frameControles.setFrameShape(QFrame.StyledPanel)
        self.frameControles.setFrameShadow(QFrame.Raised)
        self.horizontalLayoutControles = QHBoxLayout(self.frameControles)
        self.horizontalLayoutControles.setObjectName(u"horizontalLayoutControles")
        self.labelContador = QLabel(self.frameControles)
        self.labelContador.setObjectName(u"labelContador")

        self.horizontalLayoutControles.addWidget(self.labelContador)

        self.horizontalSpacerControles = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutControles.addItem(self.horizontalSpacerControles)

        self.labelRegistrosPagina = QLabel(self.frameControles)
        self.labelRegistrosPagina.setObjectName(u"labelRegistrosPagina")

        self.horizontalLayoutControles.addWidget(self.labelRegistrosPagina)

        self.comboRegistrosPagina = QComboBox(self.frameControles)
        self.comboRegistrosPagina.addItem("")
        self.comboRegistrosPagina.addItem("")
        self.comboRegistrosPagina.addItem("")
        self.comboRegistrosPagina.addItem("")
        self.comboRegistrosPagina.addItem("")
        self.comboRegistrosPagina.setObjectName(u"comboRegistrosPagina")

        self.horizontalLayoutControles.addWidget(self.comboRegistrosPagina)

        self.labelPaginaActual = QLabel(self.frameControles)
        self.labelPaginaActual.setObjectName(u"labelPaginaActual")

        self.horizontalLayoutControles.addWidget(self.labelPaginaActual)

        self.btnPrimeraPagina = QPushButton(self.frameControles)
        self.btnPrimeraPagina.setObjectName(u"btnPrimeraPagina")
        self.btnPrimeraPagina.setMaximumSize(QSize(40, 16777215))

        self.horizontalLayoutControles.addWidget(self.btnPrimeraPagina)

        self.btnPaginaAnterior = QPushButton(self.frameControles)
        self.btnPaginaAnterior.setObjectName(u"btnPaginaAnterior")
        self.btnPaginaAnterior.setMaximumSize(QSize(40, 16777215))

        self.horizontalLayoutControles.addWidget(self.btnPaginaAnterior)

        self.btnPaginaSiguiente = QPushButton(self.frameControles)
        self.btnPaginaSiguiente.setObjectName(u"btnPaginaSiguiente")
        self.btnPaginaSiguiente.setMaximumSize(QSize(40, 16777215))

        self.horizontalLayoutControles.addWidget(self.btnPaginaSiguiente)

        self.btnUltimaPagina = QPushButton(self.frameControles)
        self.btnUltimaPagina.setObjectName(u"btnUltimaPagina")
        self.btnUltimaPagina.setMaximumSize(QSize(40, 16777215))

        self.horizontalLayoutControles.addWidget(self.btnUltimaPagina)


        self.verticalLayout.addWidget(self.frameControles)

        self.tableEstudiantes = QTableWidget(EstudiantesTab)
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
        self.tableEstudiantes.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableEstudiantes.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableEstudiantes.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableEstudiantes.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout.addWidget(self.tableEstudiantes)

        self.frameAccionesRapidas = QFrame(EstudiantesTab)
        self.frameAccionesRapidas.setObjectName(u"frameAccionesRapidas")
        self.frameAccionesRapidas.setFrameShape(QFrame.StyledPanel)
        self.frameAccionesRapidas.setFrameShadow(QFrame.Raised)
        self.horizontalLayoutAcciones = QHBoxLayout(self.frameAccionesRapidas)
        self.horizontalLayoutAcciones.setObjectName(u"horizontalLayoutAcciones")
        self.labelEstadisticas = QLabel(self.frameAccionesRapidas)
        self.labelEstadisticas.setObjectName(u"labelEstadisticas")
        self.labelEstadisticas.setStyleSheet(u"font-weight: bold; color: #2c3e50;")

        self.horizontalLayoutAcciones.addWidget(self.labelEstadisticas)

        self.horizontalSpacerAcciones = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutAcciones.addItem(self.horizontalSpacerAcciones)

        self.btnExportarExcel = QPushButton(self.frameAccionesRapidas)
        self.btnExportarExcel.setObjectName(u"btnExportarExcel")
        icon3 = QIcon()
        icon3.addFile(u":/icons/excel.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btnExportarExcel.setIcon(icon3)

        self.horizontalLayoutAcciones.addWidget(self.btnExportarExcel)

        self.btnActualizar = QPushButton(self.frameAccionesRapidas)
        self.btnActualizar.setObjectName(u"btnActualizar")
        icon4 = QIcon()
        icon4.addFile(u":/icons/refresh.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btnActualizar.setIcon(icon4)

        self.horizontalLayoutAcciones.addWidget(self.btnActualizar)


        self.verticalLayout.addWidget(self.frameAccionesRapidas)


        self.retranslateUi(EstudiantesTab)

        QMetaObject.connectSlotsByName(EstudiantesTab)
    # setupUi

    def retranslateUi(self, EstudiantesTab):
        EstudiantesTab.setWindowTitle(QCoreApplication.translate("EstudiantesTab", u"Gesti\u00f3n de Estudiantes", None))
        self.groupBoxBusqueda.setTitle(QCoreApplication.translate("EstudiantesTab", u"\U0001f50d B\U000000fasqueda de Estudiantes", None))
        self.groupBoxBuscarCI.setTitle(QCoreApplication.translate("EstudiantesTab", u"Buscar por CI", None))
        self.txtBuscarCINumero.setPlaceholderText(QCoreApplication.translate("EstudiantesTab", u"N\u00famero de CI", None))
        self.comboBuscarExpedicion.setItemText(0, QCoreApplication.translate("EstudiantesTab", u"Todas", None))
        self.comboBuscarExpedicion.setItemText(1, QCoreApplication.translate("EstudiantesTab", u"BE", None))
        self.comboBuscarExpedicion.setItemText(2, QCoreApplication.translate("EstudiantesTab", u"CH", None))
        self.comboBuscarExpedicion.setItemText(3, QCoreApplication.translate("EstudiantesTab", u"CB", None))
        self.comboBuscarExpedicion.setItemText(4, QCoreApplication.translate("EstudiantesTab", u"LP", None))
        self.comboBuscarExpedicion.setItemText(5, QCoreApplication.translate("EstudiantesTab", u"OR", None))
        self.comboBuscarExpedicion.setItemText(6, QCoreApplication.translate("EstudiantesTab", u"PD", None))
        self.comboBuscarExpedicion.setItemText(7, QCoreApplication.translate("EstudiantesTab", u"PT", None))
        self.comboBuscarExpedicion.setItemText(8, QCoreApplication.translate("EstudiantesTab", u"SC", None))
        self.comboBuscarExpedicion.setItemText(9, QCoreApplication.translate("EstudiantesTab", u"TJ", None))
        self.comboBuscarExpedicion.setItemText(10, QCoreApplication.translate("EstudiantesTab", u"EX", None))

        self.btnBuscarCI.setText(QCoreApplication.translate("EstudiantesTab", u"Buscar por CI", None))
        self.groupBoxBuscarNombre.setTitle(QCoreApplication.translate("EstudiantesTab", u"Buscar por Nombre", None))
        self.txtBuscarNombre.setPlaceholderText(QCoreApplication.translate("EstudiantesTab", u"Nombre o apellido", None))
        self.btnBuscarNombre.setText(QCoreApplication.translate("EstudiantesTab", u"Buscar por Nombre", None))
        self.btnNuevoEstudiante.setText(QCoreApplication.translate("EstudiantesTab", u"\u2795 Nuevo Estudiante", None))
        self.btnMostrarTodos.setText(QCoreApplication.translate("EstudiantesTab", u"Mostrar Todos", None))
        self.labelContador.setText(QCoreApplication.translate("EstudiantesTab", u"Mostrando 0-0 de 0 estudiantes", None))
        self.labelRegistrosPagina.setText(QCoreApplication.translate("EstudiantesTab", u"Registros por p\u00e1gina:", None))
        self.comboRegistrosPagina.setItemText(0, QCoreApplication.translate("EstudiantesTab", u"10", None))
        self.comboRegistrosPagina.setItemText(1, QCoreApplication.translate("EstudiantesTab", u"25", None))
        self.comboRegistrosPagina.setItemText(2, QCoreApplication.translate("EstudiantesTab", u"50", None))
        self.comboRegistrosPagina.setItemText(3, QCoreApplication.translate("EstudiantesTab", u"100", None))
        self.comboRegistrosPagina.setItemText(4, QCoreApplication.translate("EstudiantesTab", u"Todos", None))

        self.labelPaginaActual.setText(QCoreApplication.translate("EstudiantesTab", u"P\u00e1gina 1 de 1", None))
        self.btnPrimeraPagina.setText(QCoreApplication.translate("EstudiantesTab", u"\u23ee\ufe0f", None))
#if QT_CONFIG(tooltip)
        self.btnPrimeraPagina.setToolTip(QCoreApplication.translate("EstudiantesTab", u"Primera p\u00e1gina", None))
#endif // QT_CONFIG(tooltip)
        self.btnPaginaAnterior.setText(QCoreApplication.translate("EstudiantesTab", u"\u25c0\ufe0f", None))
#if QT_CONFIG(tooltip)
        self.btnPaginaAnterior.setToolTip(QCoreApplication.translate("EstudiantesTab", u"P\u00e1gina anterior", None))
#endif // QT_CONFIG(tooltip)
        self.btnPaginaSiguiente.setText(QCoreApplication.translate("EstudiantesTab", u"\u25b6\ufe0f", None))
#if QT_CONFIG(tooltip)
        self.btnPaginaSiguiente.setToolTip(QCoreApplication.translate("EstudiantesTab", u"P\u00e1gina siguiente", None))
#endif // QT_CONFIG(tooltip)
        self.btnUltimaPagina.setText(QCoreApplication.translate("EstudiantesTab", u"\u23ed\ufe0f", None))
#if QT_CONFIG(tooltip)
        self.btnUltimaPagina.setToolTip(QCoreApplication.translate("EstudiantesTab", u"\u00daltima p\u00e1gina", None))
#endif // QT_CONFIG(tooltip)
        ___qtablewidgetitem = self.tableEstudiantes.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("EstudiantesTab", u"ID", None));
        ___qtablewidgetitem1 = self.tableEstudiantes.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("EstudiantesTab", u"CI", None));
        ___qtablewidgetitem2 = self.tableEstudiantes.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("EstudiantesTab", u"Nombre Completo", None));
        ___qtablewidgetitem3 = self.tableEstudiantes.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("EstudiantesTab", u"Email", None));
        ___qtablewidgetitem4 = self.tableEstudiantes.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("EstudiantesTab", u"Tel\u00e9fono", None));
        ___qtablewidgetitem5 = self.tableEstudiantes.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("EstudiantesTab", u"Universidad", None));
        ___qtablewidgetitem6 = self.tableEstudiantes.horizontalHeaderItem(6)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("EstudiantesTab", u"Profesi\u00f3n", None));
        ___qtablewidgetitem7 = self.tableEstudiantes.horizontalHeaderItem(7)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("EstudiantesTab", u"Estado", None));
        ___qtablewidgetitem8 = self.tableEstudiantes.horizontalHeaderItem(8)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("EstudiantesTab", u"Acciones", None));
        self.labelEstadisticas.setText(QCoreApplication.translate("EstudiantesTab", u"Total estudiantes: 0 | Activos: 0 | Inactivos: 0", None))
        self.btnExportarExcel.setText(QCoreApplication.translate("EstudiantesTab", u"\U0001f4ca Exportar Excel", None))
        self.btnActualizar.setText(QCoreApplication.translate("EstudiantesTab", u"\U0001f504 Actualizar", None))
    # retranslateUi

