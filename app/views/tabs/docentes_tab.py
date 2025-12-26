# app/views/tabs/docentes_tab.py
"""
Pestaña de gestión de docentes - Implementación completa con flujo mejorado
"""

import logging
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QLineEdit,
    QLabel,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QGridLayout,
    QFrame,
    QMenu,
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon, QFont

from app.models.docente_model import DocenteModel

logger = logging.getLogger(__name__)


class DocentesTab(QWidget):
    """Pestaña para gestión de docentes con flujo completo edición/lectura"""

    # Señales para comunicación con MainWindow
    docente_seleccionado = Signal(dict)
    necesita_actualizar = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.docentes_data = []
        self.docentes_paginados = []
        self.docentes_filtrados_actuales = []  # ¡AGREGA ESTA LÍNEA!
        self.current_filter = "todos"
        self.current_page = 1
        self.records_per_page = 10
        self.total_pages = 1

        self.setup_ui()
        self.setup_connections()
        self.cargar_docentes()

    def setup_ui(self):
        """Configurar la interfaz de usuario de la pestaña"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # ============ ENCABEZADO ============
        header_frame = QFrame()
        header_frame.setStyleSheet(
            """
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 15px;
            }
        """
        )

        header_layout = QHBoxLayout(header_frame)

        # Título
        title_label = QLabel("👨‍🏫 Gestión de Docentes")
        title_label.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
            }
        """
        )
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Botón Nuevo Docente
        self.btn_nuevo_docente = QPushButton("➕ Nuevo Docente")
        self.btn_nuevo_docente.setFixedHeight(40)
        self.btn_nuevo_docente.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """
        )
        self.btn_nuevo_docente.setToolTip("Agregar un nuevo docente al sistema")
        header_layout.addWidget(self.btn_nuevo_docente)

        layout.addWidget(header_frame)

        # ============ FILTROS ============
        filter_frame = QFrame()
        filter_frame.setStyleSheet(
            """
            QFrame {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """
        )

        filter_layout = QHBoxLayout(filter_frame)

        # Etiqueta de filtro
        filter_label = QLabel("Filtrar por estado:")
        filter_label.setStyleSheet("font-weight: bold; color: #495057;")
        filter_layout.addWidget(filter_label)

        # Combo box para filtro
        self.combo_filtro = QComboBox()
        self.combo_filtro.addItems(["Todos", "Activos", "Inactivos"])
        self.combo_filtro.setFixedHeight(36)
        self.combo_filtro.setFixedWidth(150)
        self.combo_filtro.setStyleSheet(
            """
            QComboBox {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
                color: black;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
        """
        )
        filter_layout.addWidget(self.combo_filtro)

        # Buscador
        search_label = QLabel("Buscar:")
        search_label.setStyleSheet(
            "font-weight: bold; color: #495057; margin-left: 20px;"
        )
        filter_layout.addWidget(search_label)

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Nombre, CI o especialidad...")
        self.txt_buscar.setFixedHeight(36)
        self.txt_buscar.setMinimumWidth(250)
        self.txt_buscar.setStyleSheet(
            """
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """
        )
        filter_layout.addWidget(self.txt_buscar)

        # Botón Buscar
        self.btn_buscar = QPushButton("🔍 Buscar")
        self.btn_buscar.setFixedHeight(36)
        self.btn_buscar.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
        """
        )
        filter_layout.addWidget(self.btn_buscar)

        # Botón Limpiar
        self.btn_limpiar = QPushButton("🗑️ Limpiar")
        self.btn_limpiar.setFixedHeight(36)
        self.btn_limpiar.setStyleSheet(
            """
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #616a6b;
            }
        """
        )
        filter_layout.addWidget(self.btn_limpiar)

        filter_layout.addStretch()
        layout.addWidget(filter_frame)

        # ============ TABLA DE DOCENTES ============
        self.tabla_docentes = QTableWidget()
        self.tabla_docentes.setStyleSheet(
            """
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                gridline-color: #dee2e6;
                color: black;
            }
            QTableWidget::item {
                padding: 3px;
                border-bottom: 1px solid #dee2e6;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
        """
        )

        self.tabla_docentes.setAlternatingRowColors(True)
        self.tabla_docentes.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_docentes.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla_docentes.verticalHeader().setVisible(
            False
        )  # Ocultar números de fila
        self.tabla_docentes.verticalHeader().setDefaultSectionSize(
            40
        )  # Altura uniforme de filas

        layout.addWidget(self.tabla_docentes, 1)

        # ============ CONTROLES DE PAGINACIÓN ============
        pagination_frame = QFrame()
        pagination_frame.setStyleSheet(
            """
            QFrame {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """
        )

        pagination_layout = QHBoxLayout(pagination_frame)
        pagination_layout.setContentsMargins(20, 5, 20, 5)

        # Botón Primera Página
        self.btn_primera = QPushButton("⏮️ Primera")
        self.btn_primera.setFixedHeight(35)
        self.btn_primera.setStyleSheet(
            """
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #727b84;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )
        pagination_layout.addWidget(self.btn_primera)

        # Botón Anterior
        self.btn_anterior = QPushButton("◀️ Anterior")
        self.btn_anterior.setFixedHeight(35)
        self.btn_anterior.setStyleSheet(
            """
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )
        pagination_layout.addWidget(self.btn_anterior)

        # Información de página
        pagination_layout.addStretch()

        self.lbl_info_pagina = QLabel("Página 1 de 1")
        self.lbl_info_pagina.setStyleSheet(
            """
            QLabel {
                font-weight: bold;
                color: #2c3e50;
                font-size: 13px;
            }
        """
        )
        pagination_layout.addWidget(self.lbl_info_pagina)

        # Contador de registros
        self.lbl_contador = QLabel("Mostrando 0 de 0 registros")
        self.lbl_contador.setStyleSheet(
            """
            QLabel {
                color: #7f8c8d;
                font-size: 12px;
                font-style: italic;
            }
        """
        )
        pagination_layout.addWidget(self.lbl_contador)

        pagination_layout.addStretch()

        # Botón Siguiente
        self.btn_siguiente = QPushButton("Siguiente ▶️")
        self.btn_siguiente.setFixedHeight(35)
        self.btn_siguiente.setStyleSheet(
            """
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )
        pagination_layout.addWidget(self.btn_siguiente)

        # Botón Última Página
        self.btn_ultima = QPushButton("Última ⏭️")
        self.btn_ultima.setFixedHeight(35)
        self.btn_ultima.setStyleSheet(
            """
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #727b84;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )
        pagination_layout.addWidget(self.btn_ultima)

        layout.addWidget(pagination_frame)

        # ============ ESTADO ============
        self.lbl_estado = QLabel("Cargando docentes...")
        self.lbl_estado.setStyleSheet("color: #7f8c8d; font-style: italic;")
        self.lbl_estado.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_estado)

    def setup_connections(self):
        """Conectar señales y slots"""
        # Botones
        self.btn_nuevo_docente.clicked.connect(self.agregar_nuevo_docente)
        self.btn_buscar.clicked.connect(self.buscar_docentes)
        self.btn_limpiar.clicked.connect(self.limpiar_busqueda)

        # Filtros
        self.combo_filtro.currentTextChanged.connect(
            lambda text: self.filtrar_docentes(desde_paginacion=False)
        )
        self.txt_buscar.returnPressed.connect(self.buscar_docentes)

        # Paginación
        self.btn_primera.clicked.connect(lambda: self.cambiar_pagina(1))
        self.btn_anterior.clicked.connect(
            lambda: self.cambiar_pagina(self.current_page - 1)
        )
        self.btn_siguiente.clicked.connect(
            lambda: self.cambiar_pagina(self.current_page + 1)
        )
        self.btn_ultima.clicked.connect(lambda: self.cambiar_pagina(self.total_pages))

    def cargar_docentes(self, filtro="todos"):
        """Cargar docentes desde la base de datos"""
        try:
            self.lbl_estado.setText("Cargando docentes...")

            # Obtener todos los docentes
            self.docentes_data = DocenteModel().get_all()

            # Resetear paginación
            self.current_page = 1

            # Aplicar filtro inicial
            self.current_filter = filtro
            self.filtrar_docentes(desde_paginacion=False)  # Cambio aquí

            if self.docentes_data:
                self.lbl_estado.setText(
                    f"✅ {len(self.docentes_data)} docentes cargados"
                )
            else:
                self.lbl_estado.setText("📭 No hay docentes registrados")

        except Exception as e:
            logger.error(f"Error al cargar docentes: {e}")
            self.lbl_estado.setText("❌ Error al cargar docentes")
            QMessageBox.critical(self, "Error", f"Error al cargar docentes: {str(e)}")

    def filtrar_docentes(self, desde_paginacion=False):
        """Filtrar docentes según el estado seleccionado y aplicar paginación"""
        try:
            # Obtener valores actuales
            filtro_texto = self.combo_filtro.currentText().lower()
            texto_busqueda = self.txt_buscar.text().strip().lower()

            print("metodo filtrar_docentes")

            # Filtrar docentes
            docentes_filtrados = []
            for docente in self.docentes_data:
                # Filtrar por estado
                if filtro_texto == "activos" and docente.activo != 1:
                    continue
                elif filtro_texto == "inactivos" and docente.activo != 0:
                    continue
                print(f"Módulo filtrar_docentes filtro_texto={filtro_texto}")

                # Filtrar por búsqueda si hay texto
                if texto_busqueda:
                    campos = [
                        str(docente.nombres or ""),
                        str(docente.apellidos or ""),
                        str(docente.ci_numero or ""),
                        str(getattr(docente, "especialidad", "") or ""),
                        str(getattr(docente, "grado_academico", "") or ""),
                    ]

                    if not any(texto_busqueda in campo.lower() for campo in campos):
                        continue

                docentes_filtrados.append(docente)

            # Actualizar la lista filtrada
            self.docentes_filtrados_actuales = docentes_filtrados
            print(
                f"Método filtrar_docente docentes_filtrados_actuales={self.docentes_filtrados_actuales}"
            )

            # Resetear a página 1 solo si no viene desde paginación y hubo cambio real
            if not desde_paginacion:
                self.current_page = 1

            # Actualizar la paginación
            self.actualizar_paginacion()

        except Exception as e:
            logger.error(f"Error al filtrar docentes: {e}")
            import traceback

            traceback.print_exc()

    def buscar_docentes(self):
        """Buscar docentes según el texto ingresado"""
        self.current_page = 1
        self.filtrar_docentes(desde_paginacion=False)  # Simplificado

    def limpiar_busqueda(self):
        """Limpiar el campo de búsqueda, resetear paginación y mostrar todos"""
        self.txt_buscar.clear()
        self.current_page = 1
        self.filtrar_docentes(desde_paginacion=False)

    def mostrar_docentes_en_tabla(self, docentes):
        """Mostrar docentes en la tabla con las nuevas especificaciones"""
        try:
            self.tabla_docentes.clear()

            # Configurar columnas NUEVAS
            columnas = [
                "ID",
                "# Carnet",
                "Nombre Docente",
                "Especialidad",
                "Email",
                "Teléfono",
                "CV",
                "Estado",
                "Acciones",
            ]

            self.tabla_docentes.setColumnCount(len(columnas))
            self.tabla_docentes.setHorizontalHeaderLabels(columnas)
            self.tabla_docentes.setRowCount(len(docentes))

            # Llenar datos
            for fila, docente in enumerate(docentes):
                # Configurar altura de fila uniforme
                self.tabla_docentes.setRowHeight(fila, 40)

                # 1. ID
                item_id = QTableWidgetItem(str(docente.id))
                item_id.setTextAlignment(Qt.AlignCenter)
                self.tabla_docentes.setItem(fila, 0, item_id)

                # 2. Carnet (CI)
                ci_completo = f"{docente.ci_numero}-{docente.ci_expedicion}"
                item_ci = QTableWidgetItem(ci_completo)
                item_ci.setTextAlignment(Qt.AlignCenter)
                self.tabla_docentes.setItem(fila, 1, item_ci)

                # 3. Nombre Docente (Grado + Nombres + Apellidos)
                grado = getattr(docente, "grado_academico", "") or ""
                nombres = str(docente.nombres) if docente.nombres else ""
                apellidos = str(docente.apellidos) if docente.apellidos else ""

                # Formato: "Grado Acad. Nombres Apellidos"
                nombre_completo = ""
                if grado:
                    nombre_completo += f"{grado} "
                nombre_completo += f"{nombres} {apellidos}".strip()

                item_nombre = QTableWidgetItem(nombre_completo.strip())
                self.tabla_docentes.setItem(fila, 2, item_nombre)

                # 4. Especialidad
                especialidad = getattr(docente, "especialidad", "") or ""
                item_especialidad = QTableWidgetItem(especialidad)
                self.tabla_docentes.setItem(fila, 3, item_especialidad)

                # 5. Email
                email = getattr(docente, "email", "") or ""
                item_email = QTableWidgetItem(email)
                self.tabla_docentes.setItem(fila, 4, item_email)

                # 6. Teléfono
                telefono = getattr(docente, "telefono", "") or ""
                item_telefono = QTableWidgetItem(telefono)
                self.tabla_docentes.setItem(fila, 5, item_telefono)

                # 7. CV
                tiene_cv = "✅" if getattr(docente, "curriculum_path", None) else "❌"
                item_cv = QTableWidgetItem(tiene_cv)
                item_cv.setTextAlignment(Qt.AlignCenter)
                self.tabla_docentes.setItem(fila, 6, item_cv)

                # 8. Estado
                estado = "✅ Activo" if docente.activo == 1 else "❌ Inactivo"
                item_estado = QTableWidgetItem(estado)
                item_estado.setTextAlignment(Qt.AlignCenter)

                # Color según estado
                if docente.activo == 1:
                    item_estado.setForeground(Qt.darkGreen)
                else:
                    item_estado.setForeground(Qt.darkRed)

                self.tabla_docentes.setItem(fila, 7, item_estado)

                # 9. Acciones (5 botones con tamaño fijo)
                widget_acciones = QWidget()
                layout_acciones = QHBoxLayout(widget_acciones)
                layout_acciones.setContentsMargins(3, 3, 3, 3)
                layout_acciones.setSpacing(3)

                # Botón 1: Ver Detalles
                btn_detalles = QPushButton("👁️")
                btn_detalles.setFixedSize(40, 28)
                btn_detalles.setToolTip("Ver detalles del docente")
                btn_detalles.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border-radius: 4px;
                        font-size: 11px;
                        border: none;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                    QPushButton:pressed {
                        background-color: #1f618d;
                    }
                """
                )
                btn_detalles.clicked.connect(
                    lambda checked, d=docente: self.ver_detalles_docente(d)
                )

                # Botón 2: Editar
                btn_editar = QPushButton("✏️")
                btn_editar.setFixedSize(40, 28)
                btn_editar.setToolTip("Editar docente")
                btn_editar.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #f39c12;
                        color: white;
                        border-radius: 4px;
                        font-size: 11px;
                        border: none;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #e67e22;
                    }
                    QPushButton:pressed {
                        background-color: #d35400;
                    }
                """
                )
                btn_editar.clicked.connect(
                    lambda checked, d=docente: self.editar_docente(d.id)
                )

                # Botón 3: PDF (Ver CV)
                btn_pdf = QPushButton("📄")
                btn_pdf.setFixedSize(40, 28)
                btn_pdf.setToolTip("Ver/Descargar CV")
                btn_pdf.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #9b59b6;
                        color: white;
                        border-radius: 4px;
                        font-size: 11px;
                        border: none;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #8e44ad;
                    }
                    QPushButton:pressed {
                        background-color: #7d3c98;
                    }
                    QPushButton:disabled {
                        background-color: #bdc3c7;
                        color: #7f8c8d;
                    }
                """
                )
                # Solo habilitar si tiene CV
                if not getattr(docente, "curriculum_path", None):
                    btn_pdf.setEnabled(False)
                btn_pdf.clicked.connect(
                    lambda checked, d=docente: self.ver_cv_docente(d)
                )

                # Botón 4: Activar/Desactivar
                if docente.activo == 1:
                    btn_estado = QPushButton("⏸️")
                    btn_estado.setToolTip("Desactivar docente")
                    btn_estado.setStyleSheet(
                        """
                        QPushButton {
                            background-color: #e74c3c;
                            color: white;
                            border-radius: 4px;
                            font-size: 11px;
                            border: none;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #c0392b;
                        }
                        QPushButton:pressed {
                            background-color: #a93226;
                        }
                    """
                    )
                else:
                    btn_estado = QPushButton("▶️")
                    btn_estado.setToolTip("Activar docente")
                    btn_estado.setStyleSheet(
                        """
                        QPushButton {
                            background-color: #2ecc71;
                            color: white;
                            border-radius: 4px;
                            font-size: 11px;
                            border: none;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #27ae60;
                        }
                        QPushButton:pressed {
                            background-color: #219653;
                        }
                    """
                    )
                btn_estado.setFixedSize(40, 28)
                btn_estado.clicked.connect(
                    lambda checked, d=docente: self.toggle_estado_docente(d)
                )

                # Botón 5: Eliminar
                btn_eliminar = QPushButton("🗑️")
                btn_eliminar.setFixedSize(40, 28)
                btn_eliminar.setToolTip("Eliminar docente")
                btn_eliminar.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #34495e;
                        color: white;
                        border-radius: 4px;
                        font-size: 11px;
                        border: none;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #2c3e50;
                    }
                    QPushButton:pressed {
                        background-color: #1a252f;
                    }
                """
                )
                btn_eliminar.clicked.connect(
                    lambda checked, d=docente: self.eliminar_docente(d)
                )

                # Agregar los 5 botones al layout
                layout_acciones.addWidget(btn_detalles)
                layout_acciones.addWidget(btn_editar)
                layout_acciones.addWidget(btn_pdf)
                layout_acciones.addWidget(btn_estado)
                layout_acciones.addWidget(btn_eliminar)

                # Sin stretch para que los botones se alineen a la izquierda
                # layout_acciones.addStretch()  # REMOVEMOS ESTO para que ocupen todo el ancho

                self.tabla_docentes.setCellWidget(fila, 8, widget_acciones)

            # Ajustar anchos de columnas
            self.tabla_docentes.horizontalHeader().setStretchLastSection(False)

            # Anchos específicos
            self.tabla_docentes.setColumnWidth(0, 50)  # ID (más pequeño)
            self.tabla_docentes.setColumnWidth(1, 100)  # # Carnet
            self.tabla_docentes.setColumnWidth(
                2, 250
            )  # Nombre Docente (ancho suficiente para grado + nombres)
            self.tabla_docentes.setColumnWidth(3, 150)  # Especialidad
            self.tabla_docentes.setColumnWidth(4, 200)  # Email
            self.tabla_docentes.setColumnWidth(5, 120)  # Teléfono
            self.tabla_docentes.setColumnWidth(6, 50)  # CV (icono)
            self.tabla_docentes.setColumnWidth(7, 100)  # Estado

            # Acciones: 5 botones de 40px + 5 espacios de 5px = 225px
            self.tabla_docentes.setColumnWidth(
                8, 225
            )  # Acciones (espacio para 5 botones)

            # Hacer que algunas columnas sean expansibles
            self.tabla_docentes.horizontalHeader().setSectionResizeMode(
                2, QHeaderView.Stretch
            )  # Nombre Docente
            self.tabla_docentes.horizontalHeader().setSectionResizeMode(
                3, QHeaderView.Stretch
            )  # Especialidad
            self.tabla_docentes.horizontalHeader().setSectionResizeMode(
                4, QHeaderView.Stretch
            )  # Email

        except Exception as e:
            logger.error(f"Error al mostrar docentes en tabla: {e}")
            self.lbl_estado.setText("❌ Error al mostrar docentes")

    # ============================================================================
    # MÉTODOS PRINCIPALES DE GESTIÓN
    # ============================================================================

    def agregar_nuevo_docente(self):
        """Abrir diálogo para nuevo docente"""
        try:
            from app.views.dialogs.docente_form_dialog import DocenteFormDialog

            # Abrir diálogo para nuevo docente
            dialog = DocenteFormDialog(docente_id=None, modo_lectura=False, parent=self)

            # Conectar señal para mostrar después de guardar
            dialog.docente_editar.connect(
                lambda data: self.mostrar_docente_en_modo_lectura(data["id"])
            )

            if dialog.exec():
                print(f"DEBUG: Nuevo docente creado")
                self.cargar_docentes(self.current_filter)

        except Exception as e:
            logger.error(f"Error al crear docente: {e}")
            QMessageBox.critical(self, "Error", f"Error al crear docente: {str(e)}")

    def ver_detalles_docente(self, docente):
        """Mostrar diálogo con detalles del docente (solo lectura)"""
        try:
            print(
                f"DEBUG ver_detalles_docente: Abriendo diálogo para docente ID {docente.id}"
            )

            from app.views.dialogs.docente_form_dialog import DocenteFormDialog

            # Crear diccionario con datos del docente
            docente_data = {
                "id": docente.id,
                "ci_numero": docente.ci_numero,
                "ci_expedicion": docente.ci_expedicion,
                "nombres": docente.nombres,
                "apellidos": docente.apellidos,
                "especialidad": getattr(docente, "especialidad", ""),
                "grado_academico": getattr(docente, "grado_academico", ""),
                "telefono": getattr(docente, "telefono", ""),
                "email": getattr(docente, "email", ""),
                "curriculum_path": getattr(docente, "curriculum_path", None),
                "activo": getattr(docente, "activo", 1),
            }

            # Abrir diálogo en modo lectura
            dialog = DocenteFormDialog(
                docente_data=docente_data, modo_lectura=True, parent=self
            )

            # Conectar señales para acciones desde modo lectura
            dialog.docente_editar.connect(lambda data: self.editar_docente(data["id"]))

            dialog.docente_inscribir.connect(self.on_inscribir_desde_detalles)
            dialog.docente_borrar.connect(self.on_borrar_desde_detalles)

            dialog.exec()

        except Exception as e:
            print(f"ERROR en ver_detalles_docente: {e}")
            logger.error(f"Error en ver_detalles_docente: {e}")
            QMessageBox.critical(self, "Error", f"Error al mostrar detalles: {str(e)}")

    def editar_docente(self, docente_id):
        """Abrir diálogo para editar un docente"""
        try:
            print(f"DEBUG editar_docente: Abriendo diálogo para ID {docente_id}")

            from app.views.dialogs.docente_form_dialog import DocenteFormDialog

            # Abrir diálogo en modo edición
            dialog = DocenteFormDialog(
                docente_id=docente_id, modo_lectura=False, parent=self
            )

            # Conectar señal para mostrar después de guardar
            dialog.docente_editar.connect(
                lambda data: self.mostrar_docente_en_modo_lectura(data["id"])
            )

            if dialog.exec():
                print(f"DEBUG editar_docente - Diálogo cerrado")
                self.cargar_docentes(self.current_filter)

        except Exception as e:
            logger.error(f"Error al editar docente: {e}")
            QMessageBox.critical(self, "Error", f"Error al editar docente: {str(e)}")

    def mostrar_docente_en_modo_lectura(self, docente_id):
        """Mostrar docente en modo lectura después de guardar"""
        try:
            print(f"DEBUG mostrar_docente_en_modo_lectura: ID {docente_id}")

            from app.models.docente_model import DocenteModel

            docente = DocenteModel.find_by_id(docente_id)

            if docente:
                self.ver_detalles_docente(docente)
            else:
                print(f"ERROR: Docente {docente_id} no encontrado")

        except Exception as e:
            print(f"ERROR mostrando docente en modo lectura: {e}")
            logger.error(f"Error mostrando docente en modo lectura: {e}")

    def ver_cv_docente(self, docente):
        """Abrir el CV del docente"""
        try:
            cv_path = getattr(docente, "curriculum_path", None)
            if cv_path:
                from pathlib import Path
                import os
                import platform

                ruta = Path(cv_path)
                if ruta.exists():
                    sistema = platform.system()

                    if sistema == "Windows":
                        os.startfile(str(ruta))
                    elif sistema == "Darwin":  # macOS
                        os.system(f'open "{ruta}"')
                    else:  # Linux
                        os.system(f'xdg-open "{ruta}"')
                else:
                    QMessageBox.warning(
                        self,
                        "Archivo no encontrado",
                        f"El archivo CV no existe:\n{cv_path}",
                    )
            else:
                QMessageBox.information(
                    self, "Sin CV", "Este docente no tiene un CV cargado."
                )

        except Exception as e:
            logger.error(f"Error al abrir CV: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo abrir el CV: {str(e)}")

    def toggle_estado_docente(self, docente):
        """Activar/Desactivar docente"""
        try:
            nuevo_estado = 0 if docente.activo == 1 else 1
            estado_texto = "desactivar" if docente.activo == 1 else "activar"

            respuesta = QMessageBox.question(
                self,
                "Confirmar Cambio",
                f"¿Está seguro de {estado_texto} al docente?\n\n"
                f"Docente: {docente.nombres} {docente.apellidos}\n"
                f"CI: {docente.ci_numero}",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if respuesta == QMessageBox.Yes:
                # Actualizar en la base de datos
                docente.activo = nuevo_estado
                docente.update()

                # Actualizar tabla
                self.cargar_docentes(self.current_filter)

                estado_final = "activado" if nuevo_estado == 1 else "desactivado"
                QMessageBox.information(
                    self, "✅ Éxito", f"Docente {estado_final} correctamente"
                )

        except Exception as e:
            logger.error(f"Error al cambiar estado del docente: {e}")
            QMessageBox.critical(self, "Error", f"Error al cambiar estado: {str(e)}")

    def eliminar_docente(self, docente):
        """Eliminar docente"""
        try:
            respuesta = QMessageBox.question(
                self,
                "Confirmar Eliminación",
                f"¿Está seguro de eliminar este docente?\n\n"
                f"Docente: {docente.nombres} {docente.apellidos}\n"
                f"CI: {docente.ci_numero}\n\n"
                f"⚠️ Esta acción no se puede deshacer.",
                QMessageBox.Yes | QMenu.No,
                QMessageBox.No,
            )

            if respuesta == QMessageBox.Yes:
                # Eliminar archivo CV si existe
                cv_path = getattr(docente, "curriculum_path", None)
                if cv_path:
                    try:
                        from pathlib import Path

                        cv_file = Path(cv_path)
                        if cv_file.exists():
                            cv_file.unlink()
                    except Exception as e:
                        logger.warning(f"No se pudo eliminar CV: {e}")

                # Eliminar de la base de datos
                docente.delete()

                # Actualizar tabla
                self.cargar_docentes(self.current_filter)

                QMessageBox.information(
                    self, "✅ Éxito", "Docente eliminado correctamente"
                )

        except Exception as e:
            logger.error(f"Error al eliminar docente: {e}")
            QMessageBox.critical(self, "Error", f"Error al eliminar docente: {str(e)}")

    # ============================================================================
    # MANEJADORES DE SEÑALES DESDE DIÁLOGO
    # ============================================================================

    def on_inscribir_desde_detalles(self, datos_docente):
        """Manejador para inscribir docente desde modo lectura"""
        try:
            docente_id = datos_docente.get("id")
            if docente_id:
                print(f"DEBUG: Asignando cursos a docente ID {docente_id}")
                # Aquí puedes implementar la lógica para asignar cursos
                # Por ahora solo mostramos un mensaje
                QMessageBox.information(
                    self,
                    "Asignar Cursos",
                    f"Funcionalidad para asignar cursos al docente {docente_id}\n"
                    f"(Por implementar)",
                )
        except Exception as e:
            logger.error(f"Error al inscribir desde detalles: {e}")

    def on_borrar_desde_detalles(self, datos_docente):
        """Manejador para borrar docente desde modo lectura"""
        try:
            docente_id = datos_docente.get("id")
            if docente_id:
                respuesta = QMessageBox.question(
                    self,
                    "Confirmar Eliminación",
                    f"¿Está seguro de eliminar este docente?\n\n"
                    f"Esta acción eliminará permanentemente al docente del sistema.\n"
                    f"ID: {docente_id}",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )

                if respuesta == QMessageBox.Yes:
                    print(f"DEBUG: Eliminando docente ID {docente_id}")

                    # Buscar y eliminar el docente
                    docente = DocenteModel.find_by_id(docente_id)
                    if docente:
                        # Eliminar archivo CV si existe
                        if (
                            hasattr(docente, "curriculum_path")
                            and docente.curriculum_path
                        ):
                            try:
                                cv_path = Path(docente.curriculum_path)
                                if cv_path.exists():
                                    cv_path.unlink()
                            except Exception as e:
                                print(f"Advertencia: No se pudo eliminar CV: {e}")

                        # Eliminar de la base de datos
                        docente.delete()

                        # Actualizar tabla
                        self.cargar_docentes(self.current_filter)

                        QMessageBox.information(
                            self, "✅ Éxito", "Docente eliminado correctamente"
                        )
                    else:
                        QMessageBox.warning(self, "Error", "Docente no encontrado")

        except Exception as e:
            logger.error(f"Error al borrar desde detalles: {e}")
            QMessageBox.critical(self, "Error", f"Error al eliminar docente: {str(e)}")

    # ============================================================================
    # MÉTODOS AUXILIARES
    # ============================================================================

    def actualizar_interfaz(self):
        """Actualizar la interfaz después de cambios"""
        self.cargar_docentes(self.current_filter)

    def obtener_docente_por_id(self, docente_id):
        """Obtener docente por ID desde los datos cargados"""
        for docente in self.docentes_data:
            if docente.id == docente_id:
                return docente
        return None

    # ============================================================================
    # MÉTODOS DE PAGINACIÓN
    # ============================================================================

    def calcular_paginacion(self, docentes_filtrados):
        """Calcular paginación basada en docentes filtrados"""
        total_docentes = len(docentes_filtrados)
        self.total_pages = max(
            1, (total_docentes + self.records_per_page - 1) // self.records_per_page
        )

        # Ajustar página actual si es necesario
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages

        # Calcular índices para la página actual
        start_idx = (self.current_page - 1) * self.records_per_page
        end_idx = min(start_idx + self.records_per_page, total_docentes)

        # Obtener docentes para la página actual
        self.docentes_paginados = docentes_filtrados[start_idx:end_idx]

        return total_docentes, start_idx, end_idx

    def cambiar_pagina(self, nueva_pagina):
        """Cambiar a una nueva página"""
        if 1 <= nueva_pagina <= self.total_pages and nueva_pagina != self.current_page:
            self.current_page = nueva_pagina
            self.actualizar_paginacion()

    def filtrar_docentes(self, desde_paginacion=False):
        """Filtrar docentes según el estado seleccionado y aplicar paginación"""
        try:
            # Obtener valores actuales
            filtro_texto = self.combo_filtro.currentText().lower()
            texto_busqueda = self.txt_buscar.text().strip().lower()

            # Filtrar docentes
            docentes_filtrados = []
            for docente in self.docentes_data:
                # Filtrar por estado
                if filtro_texto == "activos" and docente.activo != 1:
                    continue
                elif filtro_texto == "inactivos" and docente.activo != 0:
                    continue

                # Filtrar por búsqueda si hay texto
                if texto_busqueda:
                    campos = [
                        str(docente.nombres or ""),
                        str(docente.apellidos or ""),
                        str(docente.ci_numero or ""),
                        str(getattr(docente, "especialidad", "") or ""),
                        str(getattr(docente, "grado_academico", "") or ""),
                    ]

                    if not any(texto_busqueda in campo.lower() for campo in campos):
                        continue

                docentes_filtrados.append(docente)

            # Actualizar la lista filtrada
            self.docentes_filtrados_actuales = docentes_filtrados

            # Resetear a página 1 solo si no viene desde paginación
            if not desde_paginacion:
                self.current_page = 1

            # Actualizar la paginación
            self.actualizar_paginacion()

        except Exception as e:
            logger.error(f"Error al filtrar docentes: {e}")
            import traceback

            traceback.print_exc()

    def mostrar_pagina_actual(self):
        """Mostrar la página actual de docentes"""
        total_docentes, start_idx, end_idx = self.calcular_paginacion(
            self.docentes_filtrados_actuales
        )

        # Mostrar docentes de la página actual
        self.mostrar_docentes_en_tabla(self.docentes_paginados)

        # Actualizar contador
        mostrar_texto = (
            f"Mostrando {len(self.docentes_paginados)} de {total_docentes} registros"
        )
        if total_docentes > 0:
            mostrar_texto += f" ({start_idx + 1}-{end_idx})"
        self.lbl_contador.setText(mostrar_texto)

    def actualizar_paginacion(self):
        """Actualizar controles de paginación y mostrar página actual"""
        # Calcular paginación
        total_docentes = len(self.docentes_filtrados_actuales)
        self.total_pages = max(
            1, (total_docentes + self.records_per_page - 1) // self.records_per_page
        )

        # Ajustar página actual si es necesario
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages

        # Calcular índices para la página actual
        start_idx = (self.current_page - 1) * self.records_per_page
        end_idx = min(start_idx + self.records_per_page, total_docentes)

        # Obtener docentes para la página actual
        self.docentes_paginados = self.docentes_filtrados_actuales[start_idx:end_idx]

        # Actualizar botones
        self.btn_primera.setEnabled(self.current_page > 1)
        self.btn_anterior.setEnabled(self.current_page > 1)
        self.btn_siguiente.setEnabled(self.current_page < self.total_pages)
        self.btn_ultima.setEnabled(self.current_page < self.total_pages)

        # Actualizar información
        self.lbl_info_pagina.setText(
            f"Página {self.current_page} de {self.total_pages}"
        )

        # Mostrar docentes de la página actual
        self.mostrar_docentes_en_tabla(self.docentes_paginados)

        # Actualizar contador
        mostrar_texto = (
            f"Mostrando {len(self.docentes_paginados)} de {total_docentes} registros"
        )
        if total_docentes > 0:
            mostrar_texto += f" ({start_idx + 1}-{end_idx})"
        self.lbl_contador.setText(mostrar_texto)
