# app/controllers/estudiante_controller.py
"""
Controlador para la gestión de estudiantes en el sistema FormaGestPro_MVC
"""

import logging
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

from app.models.estudiante_model import EstudianteModel
from app.models.programa_academico_model import ProgramasAcademicosModel

logger = logging.getLogger(__name__)


class EstudianteController:
    """Controlador para la gestión de estudiantes"""

    def __init__(self, db_path: str = None):
        """
        Inicializar controlador de estudiantes

        Args:
            db_path: Ruta a la base de datos (opcional)
        """
        self.db_path = db_path

    # ==================== OPERACIONES CRUD ====================

    def crear_estudiante(
        self, datos: Dict[str, Any]
    ) -> Tuple[bool, str, Optional[EstudianteModel]]:
        """
        Crear un nuevo estudiante

        Args:
            datos: Diccionario con los datos del estudiante

        Returns:
            Tuple (éxito, mensaje, estudiante)
        """
        try:
            # Validar datos requeridos
            errores = self._validar_datos_estudiante(datos)
            if errores:
                return False, "Errores de validación: " + "; ".join(errores), None

            # Verificar si ya existe un estudiante con el mismo CI
            if "ci_numero" in datos and "ci_expedicion" in datos:
                existente = EstudianteModel.buscar_por_ci(
                    datos["ci_numero"], datos["ci_expedicion"]
                )
                if existente:
                    return (
                        False,
                        f"Ya existe un estudiante con CI {datos['ci_numero']}-{datos['ci_expedicion']}",
                        None,
                    )

            # Crear el estudiante
            estudiante = EstudianteModel(**datos)
            estudiante_id = estudiante.save()

            if estudiante_id:
                estudiante_creado = EstudianteModel.get_by_id(estudiante_id)
                mensaje = f"Estudiante creado exitosamente (ID: {estudiante_id})"
                return True, mensaje, estudiante_creado
            else:
                return False, "Error al guardar el estudiante en la base de datos", None

        except Exception as e:
            logger.error(f"Error al crear estudiante: {e}")
            return False, f"Error interno: {str(e)}", None

    def actualizar_estudiante(
        self, estudiante_id: int, datos: Dict[str, Any]
    ) -> Tuple[bool, str, Optional[EstudianteModel]]:
        """
        Actualizar un estudiante existente

        Args:
            estudiante_id: ID del estudiante a actualizar
            datos: Diccionario con los datos a actualizar

        Returns:
            Tuple (éxito, mensaje, estudiante)
        """
        try:
            # Buscar estudiante existente
            estudiante = EstudianteModel.get_by_id(estudiante_id)
            if not estudiante:
                return False, f"No se encontró estudiante con ID {estudiante_id}", None

            # Validar datos
            errores = self._validar_datos_estudiante(datos, es_actualizacion=True)
            if errores:
                return False, "Errores de validación: " + "; ".join(errores), None

            # Verificar duplicados de CI (si se está actualizando el CI)
            if "ci_numero" in datos or "ci_expedicion" in datos:
                ci_numero = datos.get("ci_numero", estudiante.ci_numero)
                ci_expedicion = datos.get("ci_expedicion", estudiante.ci_expedicion)

                # Buscar otros estudiantes con el mismo CI
                otros = EstudianteModel.buscar_por_ci(ci_numero, ci_expedicion)
                if otros and otros.id != estudiante_id:
                    return (
                        False,
                        f"Ya existe otro estudiante con CI {ci_numero}-{ci_expedicion}",
                        None,
                    )

            # Actualizar atributos del estudiante
            for key, value in datos.items():
                if hasattr(estudiante, key):
                    setattr(estudiante, key, value)

            # Guardar cambios
            if estudiante.save():
                mensaje = f"Estudiante actualizado exitosamente (ID: {estudiante_id})"
                return True, mensaje, estudiante
            else:
                return False, "Error al guardar los cambios", None

        except Exception as e:
            logger.error(f"Error al actualizar estudiante {estudiante_id}: {e}")
            return False, f"Error interno: {str(e)}", None

    def eliminar_estudiante(self, estudiante_id: int) -> Tuple[bool, str]:
        """
        Eliminar un estudiante (marcar como inactivo)

        Args:
            estudiante_id: ID del estudiante a eliminar

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            estudiante = EstudianteModel.get_by_id(estudiante_id)
            if not estudiante:
                return False, f"No se encontró estudiante con ID {estudiante_id}"

            # Cambiar estado a inactivo en lugar de eliminar físicamente
            estudiante.activo = 0
            if estudiante.save():
                return True, f"Estudiante marcado como inactivo (ID: {estudiante_id})"
            else:
                return False, "Error al marcar estudiante como inactivo"

        except Exception as e:
            logger.error(f"Error al eliminar estudiante {estudiante_id}: {e}")
            return False, f"Error interno: {str(e)}"

    def reactivar_estudiante(self, estudiante_id: int) -> Tuple[bool, str]:
        """
        Reactivar un estudiante previamente eliminado

        Args:
            estudiante_id: ID del estudiante a reactivar

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            estudiante = EstudianteModel.get_by_id(estudiante_id)
            if not estudiante:
                return False, f"No se encontró estudiante con ID {estudiante_id}"

            # Cambiar estado a activo
            estudiante.activo = 1
            if estudiante.save():
                return True, f"Estudiante reactivado exitosamente (ID: {estudiante_id})"
            else:
                return False, "Error al reactivar estudiante"

        except Exception as e:
            logger.error(f"Error al reactivar estudiante {estudiante_id}: {e}")
            return False, f"Error interno: {str(e)}"

    # ==================== CONSULTAS ====================

    def obtener_estudiante(self, estudiante_id: int) -> Optional[EstudianteModel]:
        """
        Obtener un estudiante por su ID

        Args:
            estudiante_id: ID del estudiante

        Returns:
            EstudianteModel o None si no se encuentra
        """
        try:
            return EstudianteModel.get_by_id(estudiante_id)
        except Exception as e:
            logger.error(f"Error al obtener estudiante {estudiante_id}: {e}")
            return None

    def obtener_estudiante_por_ci(
        self, ci_numero: str, ci_expedicion: str
    ) -> Optional[EstudianteModel]:
        """
        Obtener estudiante por CI

        Args:
            ci_numero: Número de CI
            ci_expedicion: Expedición del CI

        Returns:
            EstudianteModel o None si no se encuentra
        """
        try:
            return EstudianteModel.buscar_por_ci(ci_numero, ci_expedicion)
        except Exception as e:
            logger.error(
                f"Error al obtener estudiante por CI {ci_numero}-{ci_expedicion}: {e}"
            )
            return None

    def obtener_estudiantes(
        self,
        activos: bool = True,
        programa_id: Optional[int] = None,
        limite: int = 100,
        offset: int = 0,
        orden_por: str = "apellidos",
        orden_asc: bool = True,
    ) -> List[EstudianteModel]:
        """
        Obtener lista de estudiantes con filtros

        Args:
            activos: Si True, solo estudiantes activos
            programa_id: Filtrar por programa académico
            limite: Número máximo de resultados
            offset: Desplazamiento para paginación
            orden_por: Campo para ordenar ('apellidos', 'nombres', 'ci_numero', 'fecha_registro')
            orden_asc: Orden ascendente (True) o descendente (False)

        Returns:
            Lista de estudiantes
        """
        try:
            # Construir condiciones
            condiciones = []
            parametros = []

            if activos:
                condiciones.append("activo = ?")
                parametros.append(1)

            if programa_id:
                # Necesitaríamos un JOIN con matrículas para obtener el programa
                # Por ahora, si no hay campo programa_id en estudiantes, ignoramos
                pass

            # Convertir condiciones a string
            where_clause = ""
            if condiciones:
                where_clause = "WHERE " + " AND ".join(condiciones)

            # Validar campo de orden
            campos_validos = ["apellidos", "nombres", "ci_numero", "fecha_registro"]
            if orden_por not in campos_validos:
                orden_por = "apellidos"

            # Construir orden
            orden = f"{orden_por} {'ASC' if orden_asc else 'DESC'}"

            # Construir límite
            limit_clause = ""
            if limite > 0:
                limit_clause = f"LIMIT {limite} OFFSET {offset}"

            # Ejecutar consulta
            query = f"""
                SELECT * FROM estudiantes 
                {where_clause}
                ORDER BY {orden}
                {limit_clause}
            """

            estudiantes = (
                EstudianteModel.query(query, parametros)
                if parametros
                else EstudianteModel.query(query)
            )
            return (
                [EstudianteModel(**est) for est in estudiantes] if estudiantes else []
            )

        except Exception as e:
            logger.error(f"Error al obtener estudiantes: {e}")
            return []

    def buscar_estudiantes(
        self, criterio: str, valor: str, activos: bool = True
    ) -> List[EstudianteModel]:
        """
        Buscar estudiantes por criterio

        Args:
            criterio: 'ci', 'nombre', 'email', 'telefono', 'profesion', 'universidad'
            valor: Valor a buscar
            activos: Solo estudiantes activos

        Returns:
            Lista de estudiantes que coinciden
        """
        try:
            if not valor:
                return []

            # Construir condiciones de búsqueda
            condiciones = ["activo = ?"] if activos else []
            parametros = [1] if activos else []

            criterio_lower = criterio.lower()
            if criterio_lower == "ci":
                condiciones.append(
                    "(ci_numero LIKE ? OR ci_numero || '-' || ci_expedicion LIKE ?)"
                )
                parametros.extend([f"%{valor}%", f"%{valor}%"])
            elif criterio_lower == "nombre":
                condiciones.append(
                    "(nombres LIKE ? OR apellidos LIKE ? OR nombres || ' ' || apellidos LIKE ?)"
                )
                parametros.extend([f"%{valor}%", f"%{valor}%", f"%{valor}%"])
            elif criterio_lower == "email":
                condiciones.append("email LIKE ?")
                parametros.append(f"%{valor}%")
            elif criterio_lower == "telefono":
                condiciones.append("telefono LIKE ?")
                parametros.append(f"%{valor}%")
            elif criterio_lower == "profesion":
                condiciones.append("profesion LIKE ?")
                parametros.append(f"%{valor}%")
            elif criterio_lower == "universidad":
                condiciones.append("universidad_egreso LIKE ?")
                parametros.append(f"%{valor}%")
            else:
                # Búsqueda general en varios campos
                condiciones.append(
                    """
                    (nombres LIKE ? OR apellidos LIKE ? OR email LIKE ? 
                    OR telefono LIKE ? OR profesion LIKE ? OR universidad_egreso LIKE ?)
                """
                )
                parametros.extend([f"%{valor}%"] * 6)

            where_clause = "WHERE " + " AND ".join(condiciones)
            query = f"""
                SELECT * FROM estudiantes 
                {where_clause}
                ORDER BY apellidos, nombres
                LIMIT 100
            """

            estudiantes = EstudianteModel.query(query, parametros)
            return (
                [EstudianteModel(**est) for est in estudiantes] if estudiantes else []
            )

        except Exception as e:
            logger.error(f"Error al buscar estudiantes ({criterio}={valor}): {e}")
            return []

    def contar_estudiantes(self, activos: bool = True) -> int:
        """
        Contar número de estudiantes

        Args:
            activos: Si True, solo estudiantes activos

        Returns:
            Número de estudiantes
        """
        try:
            where_clause = "WHERE activo = 1" if activos else ""
            query = f"SELECT COUNT(*) as count FROM estudiantes {where_clause}"
            resultado = EstudianteModel.query(query)
            return resultado[0]["count"] if resultado else 0
        except Exception as e:
            logger.error(f"Error al contar estudiantes: {e}")
            return 0

    # ==================== OPERACIONES ESPECÍFICAS ====================

    def guardar_fotografia(
        self, estudiante_id: int, ruta_foto: str
    ) -> Tuple[bool, str]:
        """
        Guardar ruta de fotografía del estudiante

        Args:
            estudiante_id: ID del estudiante
            ruta_foto: Ruta del archivo de fotografía

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            estudiante = EstudianteModel.get_by_id(estudiante_id)
            if not estudiante:
                return False, f"No se encontró estudiante con ID {estudiante_id}"

            # Verificar que el archivo exista
            if not Path(ruta_foto).exists():
                return False, f"El archivo de fotografía no existe: {ruta_foto}"

            # Copiar archivo a directorio de fotos de estudiantes
            fotos_dir = Path("archivos/fotos_estudiantes")
            fotos_dir.mkdir(parents=True, exist_ok=True)

            # Generar nombre único
            ext = Path(ruta_foto).suffix
            nombre_archivo = f"estudiante_{estudiante_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
            destino = fotos_dir / nombre_archivo

            import shutil

            shutil.copy2(ruta_foto, destino)

            # Actualizar estudiante
            estudiante.fotografia_path = str(destino)
            if estudiante.save():
                return True, f"Fotografía guardada exitosamente: {nombre_archivo}"
            else:
                return False, "Error al guardar la ruta de la fotografía"

        except Exception as e:
            logger.error(
                f"Error al guardar fotografía del estudiante {estudiante_id}: {e}"
            )
            return False, f"Error interno: {str(e)}"

    def obtener_fotografia(self, estudiante_id: int) -> Optional[str]:
        """
        Obtener ruta de la fotografía del estudiante

        Args:
            estudiante_id: ID del estudiante

        Returns:
            Ruta de la fotografía o None si no existe
        """
        try:
            estudiante = EstudianteModel.get_by_id(estudiante_id)
            if not estudiante or not estudiante.fotografia_path:
                return None

            foto_path = Path(estudiante.fotografia_path)
            return str(foto_path) if foto_path.exists() else None

        except Exception as e:
            logger.error(
                f"Error al obtener fotografía del estudiante {estudiante_id}: {e}"
            )
            return None

    def obtener_edad_estudiante(self, estudiante_id: int) -> Optional[int]:
        """
        Calcular edad del estudiante

        Args:
            estudiante_id: ID del estudiante

        Returns:
            Edad en años o None si no se puede calcular
        """
        try:
            estudiante = EstudianteModel.get_by_id(estudiante_id)
            if not estudiante or not estudiante.fecha_nacimiento:
                return None

            # Convertir string a date
            if isinstance(estudiante.fecha_nacimiento, str):
                fecha_nac = datetime.strptime(
                    estudiante.fecha_nacimiento, "%Y-%m-%d"
                ).date()
            else:
                fecha_nac = estudiante.fecha_nacimiento

            # Calcular edad
            hoy = date.today()
            edad = hoy.year - fecha_nac.year

            # Ajustar si aún no ha cumplido años este año
            if (hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day):
                edad -= 1

            return edad

        except Exception as e:
            logger.error(f"Error al calcular edad del estudiante {estudiante_id}: {e}")
            return None

    # ==================== VALIDACIONES ====================

    def _validar_datos_estudiante(
        self, datos: Dict[str, Any], es_actualizacion: bool = False
    ) -> List[str]:
        """
        Validar datos del estudiante

        Args:
            datos: Diccionario con datos a validar
            es_actualizacion: Si es una actualización (algunos campos son opcionales)

        Returns:
            Lista de mensajes de error
        """
        errores = []

        # Validar campos requeridos (solo para creación)
        if not es_actualizacion:
            campos_requeridos = ["ci_numero", "ci_expedicion", "nombres", "apellidos"]
            for campo in campos_requeridos:
                if campo not in datos or not str(datos.get(campo, "")).strip():
                    errores.append(f"El campo '{campo}' es requerido")

        # Validar CI
        if "ci_numero" in datos and datos["ci_numero"]:
            ci_numero = str(datos["ci_numero"]).strip()
            if not ci_numero.isdigit():
                errores.append("El CI debe contener solo números")
            elif len(ci_numero) < 4 or len(ci_numero) > 10:
                errores.append("El CI debe tener entre 4 y 10 dígitos")

        # Validar expedición
        if "ci_expedicion" in datos and datos["ci_expedicion"]:
            expediciones_validas = [
                "BE",
                "CH",
                "CB",
                "LP",
                "OR",
                "PD",
                "PT",
                "SC",
                "TJ",
                "EX",
            ]
            if datos["ci_expedicion"] not in expediciones_validas:
                errores.append(
                    f"Expedición inválida. Válidas: {', '.join(expediciones_validas)}"
                )

        # Validar nombres y apellidos
        if "nombres" in datos and datos["nombres"]:
            nombres = str(datos["nombres"]).strip()
            if len(nombres) < 2:
                errores.append("Los nombres deben tener al menos 2 caracteres")
            if len(nombres) > 100:
                errores.append("Los nombres no pueden exceder 100 caracteres")

        if "apellidos" in datos and datos["apellidos"]:
            apellidos = str(datos["apellidos"]).strip()
            if len(apellidos) < 2:
                errores.append("Los apellidos deben tener al menos 2 caracteres")
            if len(apellidos) > 100:
                errores.append("Los apellidos no pueden exceder 100 caracteres")

        # Validar email si se proporciona
        if "email" in datos and datos["email"]:
            email = str(datos["email"]).strip()
            if email and ("@" not in email or "." not in email.split("@")[-1]):
                errores.append("Formato de email inválido")

        # Validar teléfono si se proporciona
        if "telefono" in datos and datos["telefono"]:
            telefono = str(datos["telefono"]).strip()
            if (
                telefono
                and not telefono.replace(" ", "")
                .replace("-", "")
                .replace("+", "")
                .isdigit()
            ):
                errores.append(
                    "El teléfono debe contener solo números y caracteres válidos (+ -)"
                )

        # Validar fecha de nacimiento si se proporciona
        if "fecha_nacimiento" in datos and datos["fecha_nacimiento"]:
            try:
                fecha_str = datos["fecha_nacimiento"]
                if isinstance(fecha_str, str):
                    fecha_nac = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                    # Verificar que sea una fecha razonable (no futuro y mayor de 12 años)
                    hoy = date.today()
                    if fecha_nac > hoy:
                        errores.append("La fecha de nacimiento no puede ser futura")
                    elif (hoy.year - fecha_nac.year) < 12:
                        errores.append("El estudiante debe tener al menos 12 años")
            except ValueError:
                errores.append("Fecha de nacimiento inválida. Formato: YYYY-MM-DD")

        # Validar universidad si se proporciona
        if "universidad_egreso" in datos and datos["universidad_egreso"]:
            universidad = str(datos["universidad_egreso"]).strip()
            if len(universidad) > 200:
                errores.append(
                    "El nombre de la universidad no puede exceder 200 caracteres"
                )

        # Validar profesión si se proporciona
        if "profesion" in datos and datos["profesion"]:
            profesion = str(datos["profesion"]).strip()
            if len(profesion) > 100:
                errores.append("La profesión no puede exceder 100 caracteres")

        return errores

    # ==================== ESTADÍSTICAS E INFORMES ====================

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de estudiantes

        Returns:
            Diccionario con estadísticas
        """
        try:
            # Contar estudiantes activos
            estudiantes_activos = self.contar_estudiantes(activos=True)

            # Contar estudiantes inactivos
            estudiantes_inactivos = self.contar_estudiantes(activos=False)

            # Total estudiantes
            total_estudiantes = estudiantes_activos + estudiantes_inactivos

            # Estudiantes por mes de registro (últimos 12 meses)
            hoy = date.today()
            estudiantes_por_mes = {}

            for i in range(12):
                mes = hoy.month - i
                año = hoy.year
                if mes <= 0:
                    mes += 12
                    año -= 1

                fecha_inicio = date(año, mes, 1)
                if mes == 12:
                    fecha_fin = date(año + 1, 1, 1)
                else:
                    fecha_fin = date(año, mes + 1, 1)

                query = """
                    SELECT COUNT(*) as count FROM estudiantes 
                    WHERE fecha_registro >= ? AND fecha_registro < ?
                """
                resultado = EstudianteModel.query(
                    query, [fecha_inicio.isoformat(), fecha_fin.isoformat()]
                )
                count = resultado[0]["count"] if resultado else 0

                mes_nombre = fecha_inicio.strftime("%b %Y")
                estudiantes_por_mes[mes_nombre] = count

            return {
                "total_estudiantes": total_estudiantes,
                "estudiantes_activos": estudiantes_activos,
                "estudiantes_inactivos": estudiantes_inactivos,
                "porcentaje_activos": (
                    (estudiantes_activos / total_estudiantes * 100)
                    if total_estudiantes > 0
                    else 0
                ),
                "estudiantes_por_mes": estudiantes_por_mes,
                "fecha_consulta": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

        except Exception as e:
            logger.error(f"Error al obtener estadísticas de estudiantes: {e}")
            return {
                "total_estudiantes": 0,
                "estudiantes_activos": 0,
                "estudiantes_inactivos": 0,
                "porcentaje_activos": 0,
                "estudiantes_por_mes": {},
                "fecha_consulta": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e),
            }

    def generar_informe_estudiantes(
        self, formato: str = "texto", activos: bool = True
    ) -> str:
        """
        Generar informe de estudiantes

        Args:
            formato: 'texto' o 'html'
            activos: Si True, solo estudiantes activos

        Returns:
            Informe formateado
        """
        try:
            estudiantes = self.obtener_estudiantes(
                activos=activos, limite=0  # Sin límite
            )

            if formato.lower() == "html":
                return self._generar_informe_html(estudiantes, activos)
            else:
                return self._generar_informe_texto(estudiantes, activos)

        except Exception as e:
            logger.error(f"Error al generar informe de estudiantes: {e}")
            return f"Error al generar informe: {str(e)}"

    def _generar_informe_texto(
        self, estudiantes: List[EstudianteModel], activos: bool
    ) -> str:
        """Generar informe en formato texto"""
        titulo = "INFORME DE ESTUDIANTES"
        if activos:
            titulo += " ACTIVOS"
        else:
            titulo += " (TODOS)"

        informe = []
        informe.append("=" * 80)
        informe.append(titulo.center(80))
        informe.append("=" * 80)
        informe.append(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        informe.append(f"Total de estudiantes: {len(estudiantes)}")
        informe.append("-" * 80)

        for i, estudiante in enumerate(estudiantes, 1):
            # Calcular edad si es posible
            edad_info = ""
            if estudiante.fecha_nacimiento:
                try:
                    if isinstance(estudiante.fecha_nacimiento, str):
                        fecha_nac = datetime.strptime(
                            estudiante.fecha_nacimiento, "%Y-%m-%d"
                        ).date()
                    else:
                        fecha_nac = estudiante.fecha_nacimiento

                    hoy = date.today()
                    edad = hoy.year - fecha_nac.year
                    if (hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day):
                        edad -= 1
                    edad_info = f" ({edad} años)"
                except:
                    pass

            informe.append(f"{i:3d}. {estudiante.nombre_completo}{edad_info}")
            informe.append(
                f"     CI: {estudiante.ci_numero}-{estudiante.ci_expedicion}"
            )

            if estudiante.email:
                informe.append(f"     Email: {estudiante.email}")
            if estudiante.telefono:
                informe.append(f"     Teléfono: {estudiante.telefono}")
            if estudiante.profesion:
                informe.append(f"     Profesión: {estudiante.profesion}")
            if estudiante.universidad_egreso:
                informe.append(f"     Universidad: {estudiante.universidad_egreso}")

            estado = "Activo" if estudiante.activo else "Inactivo"
            informe.append(f"     Estado: {estado}")
            informe.append("")

        informe.append("=" * 80)

        return "\n".join(informe)

    def _generar_informe_html(
        self, estudiantes: List[EstudianteModel], activos: bool
    ) -> str:
        """Generar informe en formato HTML"""
        titulo = "Informe de Estudiantes"
        if activos:
            titulo += " Activos"
        else:
            titulo += " (Todos)"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{titulo}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                .header {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .estudiante {{ border: 1px solid #ddd; padding: 15px; margin-bottom: 10px; border-radius: 5px; }}
                .estudiante:nth-child(even) {{ background-color: #f9f9f9; }}
                .ci {{ color: #7f8c8d; font-weight: bold; }}
                .estado-activo {{ color: #27ae60; font-weight: bold; }}
                .estado-inactivo {{ color: #e74c3c; font-weight: bold; }}
                .total {{ font-weight: bold; color: #9b59b6; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #34495e; color: white; }}
                tr:hover {{ background-color: #f5f5f5; }}
            </style>
        </head>
        <body>
            <h1>{titulo}</h1>
            <div class="header">
                <p><strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                <p><strong>Total de estudiantes:</strong> <span class="total">{len(estudiantes)}</span></p>
            </div>
        """

        if estudiantes:
            html += """
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Nombre Completo</th>
                        <th>CI</th>
                        <th>Email</th>
                        <th>Teléfono</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
            """

            for i, estudiante in enumerate(estudiantes, 1):
                estado_clase = (
                    "estado-activo" if estudiante.activo else "estado-inactivo"
                )
                estado_texto = "Activo" if estudiante.activo else "Inactivo"

                html += f"""
                <tr>
                    <td>{i}</td>
                    <td>{estudiante.nombre_completo}</td>
                    <td class="ci">{estudiante.ci_numero}-{estudiante.ci_expedicion}</td>
                    <td>{estudiante.email or '-'}</td>
                    <td>{estudiante.telefono or '-'}</td>
                    <td><span class="{estado_clase}">{estado_texto}</span></td>
                </tr>
                """

            html += """
                </tbody>
            </table>
            """
        else:
            html += "<p>No hay estudiantes para mostrar.</p>"

        html += """
            <hr>
            <p><em>Generado por FormaGestPro_MVC - Módulo de Estudiantes</em></p>
        </body>
        </html>
        """

        return html

    def exportar_estudiantes_a_csv(
        self, activos: bool = True, archivo_salida: Optional[str] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Exportar estudiantes a archivo CSV

        Args:
            activos: Si True, solo estudiantes activos
            archivo_salida: Ruta del archivo de salida

        Returns:
            Tuple (éxito, mensaje, ruta_archivo)
        """
        try:
            # Obtener estudiantes
            estudiantes = self.obtener_estudiantes(activos=activos, limite=0)

            if not estudiantes:
                return False, "No hay estudiantes para exportar", None

            # Generar nombre de archivo si no se proporciona
            if not archivo_salida:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                estado = "activos" if activos else "todos"
                archivo_salida = f"estudiantes_{estado}_{timestamp}.csv"

            # Asegurar extensión .csv
            if not archivo_salida.lower().endswith(".csv"):
                archivo_salida += ".csv"

            # Crear directorio si no existe
            archivo_path = Path(archivo_salida)
            archivo_path.parent.mkdir(parents=True, exist_ok=True)

            # Escribir CSV
            with open(archivo_path, "w", encoding="utf-8") as f:
                # Encabezados
                encabezados = [
                    "ID",
                    "CI",
                    "Nombres",
                    "Apellidos",
                    "Fecha Nacimiento",
                    "Teléfono",
                    "Email",
                    "Universidad Egreso",
                    "Profesión",
                    "Fecha Registro",
                    "Estado",
                ]
                f.write(";".join(encabezados) + "\n")

                # Datos
                for estudiante in estudiantes:
                    # Formatear fecha de nacimiento
                    fecha_nac = ""
                    if estudiante.fecha_nacimiento:
                        if isinstance(estudiante.fecha_nacimiento, str):
                            fecha_nac = estudiante.fecha_nacimiento
                        else:
                            fecha_nac = estudiante.fecha_nacimiento.isoformat()

                    # Formatear fecha de registro
                    fecha_reg = ""
                    if (
                        hasattr(estudiante, "fecha_registro")
                        and estudiante.fecha_registro
                    ):
                        if isinstance(estudiante.fecha_registro, str):
                            fecha_reg = estudiante.fecha_registro
                        else:
                            fecha_reg = estudiante.fecha_registro.isoformat()

                    fila = [
                        str(estudiante.id),
                        f"{estudiante.ci_numero}-{estudiante.ci_expedicion}",
                        estudiante.nombres,
                        estudiante.apellidos,
                        fecha_nac,
                        estudiante.telefono or "",
                        estudiante.email or "",
                        estudiante.universidad_egreso or "",
                        estudiante.profesion or "",
                        fecha_reg,
                        "Activo" if estudiante.activo else "Inactivo",
                    ]
                    f.write(";".join(fila) + "\n")

            mensaje = f"Exportados {len(estudiantes)} estudiantes a {archivo_path}"
            return True, mensaje, str(archivo_path)

        except Exception as e:
            logger.error(f"Error al exportar estudiantes a CSV: {e}")
            return False, f"Error al exportar: {str(e)}", None
