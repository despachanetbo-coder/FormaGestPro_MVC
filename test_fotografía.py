# Ejecuta esto en la consola de Python
import os
ruta = r"D:\FormaGestPro_MVC\archivos\fotos_estudiantes\f_e_7142618.jpg"
print(f"¿Existe?: {os.path.exists(ruta)}")
print(f"Tamaño: {os.path.getsize(ruta) if os.path.exists(ruta) else 'No existe'} bytes")
