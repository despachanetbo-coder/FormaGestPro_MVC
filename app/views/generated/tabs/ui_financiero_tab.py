# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'financiero_tab.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QStatusBar,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class Ui_FinancieroTab(object):
    def setupUi(self, FinancieroTab):
        if not FinancieroTab.objectName():
            FinancieroTab.setObjectName("FinancieroTab")
        FinancieroTab.resize(800, 600)
        self.verticalLayout = QVBoxLayout(FinancieroTab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QTabWidget(FinancieroTab)
        self.tabWidget.setObjectName("tabWidget")
        self.tabCaja = QWidget()
        self.tabCaja.setObjectName("tabCaja")
        self.verticalLayout_2 = QVBoxLayout(self.tabCaja)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBoxResumen = QGroupBox(self.tabCaja)
        self.groupBoxResumen.setObjectName("groupBoxResumen")
        self.gridLayout = QGridLayout(self.groupBoxResumen)
        self.gridLayout.setObjectName("gridLayout")
        self.labelSaldo = QLabel(self.groupBoxResumen)
        self.labelSaldo.setObjectName("labelSaldo")
        font = QFont()
        font.setBold(True)
        self.labelSaldo.setFont(font)

        self.gridLayout.addWidget(self.labelSaldo, 0, 0, 1, 1)

        self.lblSaldo = QLabel(self.groupBoxResumen)
        self.lblSaldo.setObjectName("lblSaldo")
        font1 = QFont()
        font1.setPointSize(14)
        font1.setBold(True)
        self.lblSaldo.setFont(font1)

        self.gridLayout.addWidget(self.lblSaldo, 0, 1, 1, 1)

        self.labelIngresosHoy = QLabel(self.groupBoxResumen)
        self.labelIngresosHoy.setObjectName("labelIngresosHoy")

        self.gridLayout.addWidget(self.labelIngresosHoy, 1, 0, 1, 1)

        self.lblIngresosHoy = QLabel(self.groupBoxResumen)
        self.lblIngresosHoy.setObjectName("lblIngresosHoy")

        self.gridLayout.addWidget(self.lblIngresosHoy, 1, 1, 1, 1)

        self.labelEgresosHoy = QLabel(self.groupBoxResumen)
        self.labelEgresosHoy.setObjectName("labelEgresosHoy")

        self.gridLayout.addWidget(self.labelEgresosHoy, 2, 0, 1, 1)

        self.lblEgresosHoy = QLabel(self.groupBoxResumen)
        self.lblEgresosHoy.setObjectName("lblEgresosHoy")

        self.gridLayout.addWidget(self.lblEgresosHoy, 2, 1, 1, 1)

        self.labelMovimientos = QLabel(self.groupBoxResumen)
        self.labelMovimientos.setObjectName("labelMovimientos")

        self.gridLayout.addWidget(self.labelMovimientos, 3, 0, 1, 1)

        self.lblMovimientos = QLabel(self.groupBoxResumen)
        self.lblMovimientos.setObjectName("lblMovimientos")

        self.gridLayout.addWidget(self.lblMovimientos, 3, 1, 1, 1)

        self.verticalLayout_2.addWidget(self.groupBoxResumen)

        self.groupBoxMovimientos = QGroupBox(self.tabCaja)
        self.groupBoxMovimientos.setObjectName("groupBoxMovimientos")
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxMovimientos)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.tablaMovimientos = QTableWidget(self.groupBoxMovimientos)
        if self.tablaMovimientos.columnCount() < 4:
            self.tablaMovimientos.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.tablaMovimientos.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tablaMovimientos.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tablaMovimientos.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tablaMovimientos.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.tablaMovimientos.setObjectName("tablaMovimientos")
        self.tablaMovimientos.setAlternatingRowColors(True)
        self.tablaMovimientos.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout_3.addWidget(self.tablaMovimientos)

        self.verticalLayout_2.addWidget(self.groupBoxMovimientos)

        self.tabWidget.addTab(self.tabCaja, "")
        self.tabPagos = QWidget()
        self.tabPagos.setObjectName("tabPagos")
        self.verticalLayout_4 = QVBoxLayout(self.tabPagos)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.groupBoxFiltrosPagos = QGroupBox(self.tabPagos)
        self.groupBoxFiltrosPagos.setObjectName("groupBoxFiltrosPagos")
        self.horizontalLayout = QHBoxLayout(self.groupBoxFiltrosPagos)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.comboEstadoPago = QComboBox(self.groupBoxFiltrosPagos)
        self.comboEstadoPago.addItem("")
        self.comboEstadoPago.addItem("")
        self.comboEstadoPago.addItem("")
        self.comboEstadoPago.addItem("")
        self.comboEstadoPago.setObjectName("comboEstadoPago")

        self.horizontalLayout.addWidget(self.comboEstadoPago)

        self.dateDesde = QDateEdit(self.groupBoxFiltrosPagos)
        self.dateDesde.setObjectName("dateDesde")

        self.horizontalLayout.addWidget(self.dateDesde)

        self.label = QLabel(self.groupBoxFiltrosPagos)
        self.label.setObjectName("label")

        self.horizontalLayout.addWidget(self.label)

        self.dateHasta = QDateEdit(self.groupBoxFiltrosPagos)
        self.dateHasta.setObjectName("dateHasta")

        self.horizontalLayout.addWidget(self.dateHasta)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.verticalLayout_4.addWidget(self.groupBoxFiltrosPagos)

        self.tablaPagos = QTableWidget(self.tabPagos)
        if self.tablaPagos.columnCount() < 5:
            self.tablaPagos.setColumnCount(5)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tablaPagos.setHorizontalHeaderItem(0, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tablaPagos.setHorizontalHeaderItem(1, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tablaPagos.setHorizontalHeaderItem(2, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tablaPagos.setHorizontalHeaderItem(3, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tablaPagos.setHorizontalHeaderItem(4, __qtablewidgetitem8)
        self.tablaPagos.setObjectName("tablaPagos")
        self.tablaPagos.setAlternatingRowColors(True)
        self.tablaPagos.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout_4.addWidget(self.tablaPagos)

        self.tabWidget.addTab(self.tabPagos, "")
        self.tabReportes = QWidget()
        self.tabReportes.setObjectName("tabReportes")
        self.verticalLayout_5 = QVBoxLayout(self.tabReportes)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_2 = QLabel(self.tabReportes)
        self.label_2.setObjectName("label_2")
        self.label_2.setAlignment(Qt.AlignCenter)

        self.verticalLayout_5.addWidget(self.label_2)

        self.tabWidget.addTab(self.tabReportes, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.statusBar = QStatusBar(FinancieroTab)
        self.statusBar.setObjectName("statusBar")

        self.verticalLayout.addWidget(self.statusBar)

        self.retranslateUi(FinancieroTab)

        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(FinancieroTab)

    # setupUi

    def retranslateUi(self, FinancieroTab):
        FinancieroTab.setWindowTitle(
            QCoreApplication.translate("FinancieroTab", "Financiero", None)
        )
        self.groupBoxResumen.setTitle(
            QCoreApplication.translate(
                "FinancieroTab", "\U0001f4b5 Resumen de Caja", None
            )
        )
        self.labelSaldo.setText(
            QCoreApplication.translate("FinancieroTab", "Saldo Actual:", None)
        )
        self.lblSaldo.setText(
            QCoreApplication.translate("FinancieroTab", "Bs. 0.00", None)
        )
        self.labelIngresosHoy.setText(
            QCoreApplication.translate("FinancieroTab", "Ingresos hoy:", None)
        )
        self.lblIngresosHoy.setText(
            QCoreApplication.translate("FinancieroTab", "Bs. 0.00", None)
        )
        self.labelEgresosHoy.setText(
            QCoreApplication.translate("FinancieroTab", "Egresos hoy:", None)
        )
        self.lblEgresosHoy.setText(
            QCoreApplication.translate("FinancieroTab", "Bs. 0.00", None)
        )
        self.labelMovimientos.setText(
            QCoreApplication.translate("FinancieroTab", "Movimientos hoy:", None)
        )
        self.lblMovimientos.setText(
            QCoreApplication.translate("FinancieroTab", "0", None)
        )
        self.groupBoxMovimientos.setTitle(
            QCoreApplication.translate(
                "FinancieroTab", "\U0001f4dd \U000000daltimos Movimientos", None
            )
        )
        ___qtablewidgetitem = self.tablaMovimientos.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(
            QCoreApplication.translate("FinancieroTab", "Fecha", None)
        )
        ___qtablewidgetitem1 = self.tablaMovimientos.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(
            QCoreApplication.translate("FinancieroTab", "Tipo", None)
        )
        ___qtablewidgetitem2 = self.tablaMovimientos.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(
            QCoreApplication.translate("FinancieroTab", "Descripci\u00f3n", None)
        )
        ___qtablewidgetitem3 = self.tablaMovimientos.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(
            QCoreApplication.translate("FinancieroTab", "Monto", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabCaja),
            QCoreApplication.translate("FinancieroTab", "\U0001f4b0 Caja", None),
        )
        self.groupBoxFiltrosPagos.setTitle(
            QCoreApplication.translate("FinancieroTab", "\U0001f50d Filtros", None)
        )
        self.comboEstadoPago.setItemText(
            0, QCoreApplication.translate("FinancieroTab", "Todos", None)
        )
        self.comboEstadoPago.setItemText(
            1, QCoreApplication.translate("FinancieroTab", "REGISTRADO", None)
        )
        self.comboEstadoPago.setItemText(
            2, QCoreApplication.translate("FinancieroTab", "CONFIRMADO", None)
        )
        self.comboEstadoPago.setItemText(
            3, QCoreApplication.translate("FinancieroTab", "ANULADO", None)
        )

        self.label.setText(QCoreApplication.translate("FinancieroTab", "a", None))
        ___qtablewidgetitem4 = self.tablaPagos.horizontalHeaderItem(0)
        ___qtablewidgetitem4.setText(
            QCoreApplication.translate("FinancieroTab", "Fecha", None)
        )
        ___qtablewidgetitem5 = self.tablaPagos.horizontalHeaderItem(1)
        ___qtablewidgetitem5.setText(
            QCoreApplication.translate("FinancieroTab", "Estudiante", None)
        )
        ___qtablewidgetitem6 = self.tablaPagos.horizontalHeaderItem(2)
        ___qtablewidgetitem6.setText(
            QCoreApplication.translate("FinancieroTab", "Concepto", None)
        )
        ___qtablewidgetitem7 = self.tablaPagos.horizontalHeaderItem(3)
        ___qtablewidgetitem7.setText(
            QCoreApplication.translate("FinancieroTab", "Monto", None)
        )
        ___qtablewidgetitem8 = self.tablaPagos.horizontalHeaderItem(4)
        ___qtablewidgetitem8.setText(
            QCoreApplication.translate("FinancieroTab", "Estado", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabPagos),
            QCoreApplication.translate("FinancieroTab", "\U0001f4b3 Pagos", None),
        )
        self.label_2.setText(
            QCoreApplication.translate(
                "FinancieroTab",
                '<html><head/><body><p align="center"><span style=" font-size:16pt;">\U0001f6a7 M\U000000f3dulo en desarrollo \U0001f6a7</span></p></body></html>',
                None,
            )
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabReportes),
            QCoreApplication.translate("FinancieroTab", "\U0001f4ca Reportes", None),
        )

    # retranslateUi
