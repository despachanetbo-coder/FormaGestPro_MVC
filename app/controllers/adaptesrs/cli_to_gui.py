# app/controllers/adapters/cli_to_gui.py
"""
Adaptador para convertir lógica CLI a GUI
"""
class CLItoGUIAdapter:
    def __init__(self, cli_functions):
        # CLI functions: dict con todas las funciones del cli.py
        self.cli_functions = cli_functions
    
    def crear_tab_programas(self):
        """Convertir funciones CLI de programas a GUI"""
        # Reutilizar la lógica de:
        # - crear_programa()
        # - listar_programas()
        # - buscar_programa_codigo()
        # etc.