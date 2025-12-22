# scripts/project_status_v2.py
"""
Script de estado del proyecto - Versión 2 (considerando CLI completo)
"""
import os
import json
from datetime import datetime
#from cli import *

class EnhancedProjectStatus:
    def __init__(self, project_root="."):
        self.project_root = project_root
        self.status = {
            "timestamp": datetime.now().isoformat(),
            "modules": {}
        }
    
    def analyze(self):
        """Analizar estado completo"""
        self.analyze_cli_functions()
        self.analyze_gui_components()
        self.analyze_database()
        self.generate_migration_plan()
        
        return self.status
    
    def analyze_cli_functions(self):
        """Analizar funciones implementadas en CLI"""
        from cli import (
            registrar_estudiante, listar_estudiantes, buscar_estudiante_ci,
            buscar_estudiante_nombre, ver_estadisticas_estudiantes,
            registrar_docente, listar_docentes, buscar_docente_ci,
            buscar_docente_especialidad, ver_estadisticas_docentes,
            crear_programa, listar_programas, buscar_programa_codigo,
            editar_programa_menu, configurar_promocion,
            buscar_programas_cupos, ver_estadisticas_programas,
            registrar_matricula, registrar_pago_cuota, ver_estado_pagos_estudiante,
            gestionar_planes_pago, ver_movimientos_caja,
            gestionar_gastos_operativos, gestionar_comprobantes,
            gestionar_ingresos_genericos,
            verificar_sistema, inicializar_base_datos
        )  # Importar todas las funciones CLI
        
        cli_functions = {
            "estudiantes": [
                registrar_estudiante, listar_estudiantes, buscar_estudiante_ci,
                buscar_estudiante_nombre, ver_estadisticas_estudiantes
            ],
            "docentes": [
                registrar_docente, listar_docentes, buscar_docente_ci,
                buscar_docente_especialidad, ver_estadisticas_docentes
            ],
            "programas": [
                crear_programa, listar_programas, buscar_programa_codigo,
                editar_programa_menu, configurar_promocion,
                buscar_programas_cupos, ver_estadisticas_programas
            ],
            "financiero": [
                registrar_matricula, registrar_pago_cuota, ver_estado_pagos_estudiante,
                gestionar_planes_pago, ver_movimientos_caja,
                gestionar_gastos_operativos, gestionar_comprobantes,
                gestionar_ingresos_genericos
            ],
            "utilidades": [
                verificar_sistema, inicializar_base_datos
            ]
        }
        
        self.status["modules"]["cli"] = {
            module: {"count": len(funcs), "complete": True}
            for module, funcs in cli_functions.items()
        }