# app/controllers/shared_controller.py
"""
Controlador compartido entre CLI y GUI
"""
from app.models.programa_academico_model import ProgramaAcademicoModel
from PySide6.QtWidgets import (QMessageBox)

class ProgramaController:
    def __init__(self, mode='GUI'):  # 'GUI' o 'CLI'
        self.mode = mode
        self.programa_model = ProgramaAcademicoModel
    
    def crear_programa(self, datos):
        """Crear programa (funciona en ambos modos)"""
        programa = self.programa_model.crear_programa(datos)
        
        if self.mode == 'GUI':
            # Mostrar mensaje en GUI
            QMessageBox.information(None, "Éxito", f"Programa creado: {programa.codigo}")
        else:
            # Mostrar en consola
            print(f"✅ Programa creado: {programa.codigo}")
        
        return programa