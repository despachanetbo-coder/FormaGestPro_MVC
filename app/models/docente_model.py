# app/models/docente_model.py
"""
Modelo para gestión de docentes en el sistema FormaGestPro.
Maneja todas las operaciones de base de datos relacionadas con docentes
usando la arquitectura centralizada de conexión.
"""

from datetime import datetime
from app.models.base_model import BaseModel
from sqlalchemy import text


class DocenteModel(BaseModel):
    """
    Modelo para operaciones de base de datos de docentes.

    Hereda de BaseModel para usar la conexión centralizada a la base de datos.
    Implementa todas las funcionalidades del repositorio original.
    """

    def __init__(self):
        """
        Inicializa el modelo de docentes.

        Configura el nombre de la tabla y cualquier atributo específico necesario.
        """
        super().__init__()
        self.table_name = "docentes"

    # ============================================================================
    # MÉTODOS DE CONSULTA Y OBTENCIÓN DE DATOS
    # ============================================================================

    def get_all(self, solo_activos=False):
        """
        Obtiene todos los docentes registrados en el sistema.

        Args:
            solo_activos (bool, optional): Si es True, solo devuelve docentes activos.
                Default es False (devuelve todos).

        Returns:
            list: Lista de diccionarios con los datos de los docentes.
                Retorna lista vacía si ocurre un error o no hay datos.

        Examples:
            >>> docente_model = DocenteModel()
            >>> todos_docentes = docente_model.get_all()
            >>> docentes_activos = docente_model.get_all(solo_activos=True)
        """
        try:
            with self.engine.connect() as conn:
                # Construir consulta base
                if solo_activos:
                    query = text(
                        f"""
                        SELECT * FROM {self.table_name} 
                        WHERE estado = 'Activo'
                        ORDER BY apellido, nombre
                    """
                    )
                else:
                    query = text(
                        f"""
                        SELECT * FROM {self.table_name} 
                        ORDER BY apellido, nombre
                    """
                    )

                # Ejecutar consulta
                result = conn.execute(query)
                docentes = result.fetchall()

                # Convertir resultados a diccionarios
                return [dict(docente) for docente in docentes]

        except Exception as error:
            self._log_error(f"Error al obtener todos los docentes: {error}")
            return []

    def get_by_id(self, docente_id):
        """
        Obtiene un docente específico por su ID.

        Args:
            docente_id (int): ID único del docente a consultar.

        Returns:
            dict or None: Diccionario con los datos del docente si existe,
                None si no se encuentra o ocurre un error.

        Examples:
            >>> docente = docente_model.get_by_id(1)
            >>> if docente:
            >>>     print(f"Docente: {docente['nombre']} {docente['apellido']}")
        """
        try:
            with self.engine.connect() as conn:
                query = text(
                    f"""
                    SELECT * FROM {self.table_name} 
                    WHERE id = :docente_id
                """
                )

                result = conn.execute(query, {"docente_id": docente_id})
                docente = result.fetchone()

                return dict(docente) if docente else None

        except Exception as error:
            self._log_error(f"Error al obtener docente por ID {docente_id}: {error}")
            return None

    def get_by_email(self, email):
        """
        Obtiene un docente por su dirección de email.

        Args:
            email (str): Email del docente a buscar.

        Returns:
            dict or None: Datos del docente si existe, None en caso contrario.

        Examples:
            >>> docente = docente_model.get_by_email("profesor@ejemplo.com")
        """
        try:
            with self.engine.connect() as conn:
                query = text(
                    f"""
                    SELECT * FROM {self.table_name} 
                    WHERE email = :email
                """
                )

                result = conn.execute(query, {"email": email})
                docente = result.fetchone()

                return dict(docente) if docente else None

        except Exception as error:
            self._log_error(f"Error al obtener docente por email {email}: {error}")
            return None

    def get_by_identificacion(self, identificacion):
        """
        Obtiene un docente por su número de identificación.

        Args:
            identificacion (str): Número de identificación del docente.

        Returns:
            dict or None: Datos del docente si existe, None en caso contrario.

        Examples:
            >>> docente = docente_model.get_by_identificacion("12345678")
        """
        try:
            with self.engine.connect() as conn:
                query = text(
                    f"""
                    SELECT * FROM {self.table_name} 
                    WHERE identificacion = :identificacion
                """
                )

                result = conn.execute(query, {"identificacion": identificacion})
                docente = result.fetchone()

                return dict(docente) if docente else None

        except Exception as error:
            self._log_error(
                f"Error al obtener docente por identificación {identificacion}: {error}"
            )
            return None

    # ============================================================================
    # MÉTODOS DE CREACIÓN Y REGISTRO
    # ============================================================================

    def create(self, docente_data):
        """
        Crea un nuevo registro de docente en la base de datos.

        Args:
            docente_data (dict): Diccionario con los datos del docente.
                Debe incluir al menos: nombre, apellido, email, identificacion.

        Returns:
            int or None: ID del docente creado si es exitoso, None si falla.

        Raises:
            ValueError: Si faltan datos requeridos.

        Examples:
            >>> nuevo_docente = {
            >>>     'nombre': 'Juan',
            >>>     'apellido': 'Pérez',
            >>>     'email': 'juan.perez@ejemplo.com',
            >>>     'identificacion': '12345678',
            >>>     'especialidad': 'Matemáticas',
            >>>     'telefono': '3001234567'
            >>> }
            >>> docente_id = docente_model.create(nuevo_docente)
        """
        try:
            # Validar datos requeridos
            campos_requeridos = ["nombre", "apellido", "email", "identificacion"]
            for campo in campos_requeridos:
                if campo not in docente_data or not docente_data[campo]:
                    raise ValueError(f"Campo requerido faltante: {campo}")

            # Verificar duplicados
            if self.get_by_email(docente_data["email"]):
                raise ValueError("Ya existe un docente con este email")

            if self.get_by_identificacion(docente_data["identificacion"]):
                raise ValueError("Ya existe un docente con esta identificación")

            # Preparar datos con valores por defecto
            datos_completos = self._preparar_datos_creacion(docente_data)

            with self.engine.connect() as conn:
                # Construir consulta de inserción
                columnas = ", ".join(datos_completos.keys())
                marcadores = ", ".join([f":{key}" for key in datos_completos.keys()])

                query = text(
                    f"""
                    INSERT INTO {self.table_name} ({columnas})
                    VALUES ({marcadores})
                """
                )

                # Ejecutar inserción
                result = conn.execute(query, datos_completos)
                conn.commit()

                docente_id = result.lastrowid

                self._log_info(f"Docente creado exitosamente - ID: {docente_id}")
                return docente_id

        except ValueError as ve:
            self._log_error(f"Error de validación al crear docente: {ve}")
            raise
        except Exception as error:
            self._log_error(f"Error al crear docente: {error}")
            return None

    # ============================================================================
    # MÉTODOS DE ACTUALIZACIÓN
    # ============================================================================

    def update(self, docente_id, update_data):
        """
        Actualiza los datos de un docente existente.

        Args:
            docente_id (int): ID del docente a actualizar.
            update_data (dict): Diccionario con los campos a actualizar.

        Returns:
            bool: True si la actualización fue exitosa, False en caso contrario.

        Examples:
            >>> datos_actualizacion = {
            >>>     'telefono': '3109876543',
            >>>     'especialidad': 'Física Avanzada'
            >>> }
            >>> exito = docente_model.update(1, datos_actualizacion)
        """
        try:
            # Verificar que el docente existe
            docente = self.get_by_id(docente_id)
            if not docente:
                self._log_error(
                    f"No se puede actualizar - Docente ID {docente_id} no encontrado"
                )
                return False

            # Validar unicidad de email si se está actualizando
            if "email" in update_data and update_data["email"] != docente["email"]:
                if self.get_by_email(update_data["email"]):
                    raise ValueError("Ya existe otro docente con este email")

            # Validar unicidad de identificación si se está actualizando
            if (
                "identificacion" in update_data
                and update_data["identificacion"] != docente["identificacion"]
            ):
                if self.get_by_identificacion(update_data["identificacion"]):
                    raise ValueError("Ya existe otro docente con esta identificación")

            # Preparar datos de actualización
            datos_actualizados = self._preparar_datos_actualizacion(update_data)

            if not datos_actualizados:
                self._log_info("No hay datos válidos para actualizar")
                return False

            with self.engine.connect() as conn:
                # Construir consulta de actualización
                set_clause = ", ".join(
                    [f"{key} = :{key}" for key in datos_actualizados.keys()]
                )

                query = text(
                    f"""
                    UPDATE {self.table_name}
                    SET {set_clause}
                    WHERE id = :docente_id
                """
                )

                # Agregar ID a los parámetros
                datos_actualizados["docente_id"] = docente_id

                # Ejecutar actualización
                result = conn.execute(query, datos_actualizados)
                conn.commit()

                actualizado = result.rowcount > 0

                if actualizado:
                    self._log_info(f"Docente ID {docente_id} actualizado exitosamente")
                else:
                    self._log_warning(f"No se actualizó el docente ID {docente_id}")

                return actualizado

        except ValueError as ve:
            self._log_error(f"Error de validación al actualizar docente: {ve}")
            return False
        except Exception as error:
            self._log_error(f"Error al actualizar docente ID {docente_id}: {error}")
            return False

    # ============================================================================
    # MÉTODOS DE ELIMINACIÓN Y CAMBIO DE ESTADO
    # ============================================================================

    def delete(self, docente_id):
        """
        Elimina (desactiva) un docente del sistema.

        Nota: En lugar de eliminación física, se cambia el estado a 'Inactivo'.

        Args:
            docente_id (int): ID del docente a desactivar.

        Returns:
            bool: True si la desactivación fue exitosa, False en caso contrario.

        Examples:
            >>> exito = docente_model.delete(1)
        """
        try:
            return self.update(docente_id, {"estado": "Inactivo"})
        except Exception as error:
            self._log_error(f"Error al eliminar docente ID {docente_id}: {error}")
            return False

    def activar(self, docente_id):
        """
        Activa un docente previamente inactivo.

        Args:
            docente_id (int): ID del docente a activar.

        Returns:
            bool: True si la activación fue exitosa, False en caso contrario.

        Examples:
            >>> exito = docente_model.activar(1)
        """
        try:
            return self.update(docente_id, {"estado": "Activo"})
        except Exception as error:
            self._log_error(f"Error al activar docente ID {docente_id}: {error}")
            return False

    # ============================================================================
    # MÉTODOS DE BÚSQUEDA Y FILTRADO
    # ============================================================================

    def search(self, criterio, valor, solo_activos=False):
        """
        Busca docentes según diferentes criterios.

        Args:
            criterio (str): Criterio de búsqueda. Puede ser:
                - 'nombre': Busca por nombre o apellido
                - 'especialidad': Busca por especialidad
                - 'email': Busca por email
                - 'identificacion': Busca por identificación
                - 'telefono': Busca por teléfono
                - 'todos': Búsqueda general en varios campos
            valor (str): Valor a buscar.
            solo_activos (bool, optional): Filtrar solo docentes activos.

        Returns:
            list: Lista de docentes que coinciden con la búsqueda.

        Examples:
            >>> # Buscar por nombre
            >>> resultados = docente_model.search('nombre', 'Juan')
            >>>
            >>> # Buscar por especialidad
            >>> resultados = docente_model.search('especialidad', 'Matemáticas')
            >>>
            >>> # Búsqueda general
            >>> resultados = docente_model.search('todos', 'física')
        """
        try:
            with self.engine.connect() as conn:
                # Construir WHERE clause según criterio
                where_clause = self._construir_where_busqueda(criterio, valor)

                # Agregar filtro de estado si es necesario
                if solo_activos:
                    if "WHERE" in where_clause:
                        where_clause += " AND estado = 'Activo'"
                    else:
                        where_clause = "WHERE estado = 'Activo'"

                query = text(
                    f"""
                    SELECT * FROM {self.table_name}
                    {where_clause}
                    ORDER BY apellido, nombre
                """
                )

                # Preparar parámetros
                if criterio in [
                    "nombre",
                    "especialidad",
                    "email",
                    "identificacion",
                    "telefono",
                ]:
                    params = {"valor": f"%{valor}%"}
                else:
                    params = {}

                # Ejecutar consulta
                result = conn.execute(query, params)
                docentes = result.fetchall()

                return [dict(docente) for docente in docentes]

        except Exception as error:
            self._log_error(
                f"Error en búsqueda de docentes (criterio: {criterio}, valor: {valor}): {error}"
            )
            return []

    def search_by_especialidad(self, especialidad, solo_activos=False):
        """
        Busca docentes por especialidad específica.

        Args:
            especialidad (str): Especialidad a buscar.
            solo_activos (bool, optional): Filtrar solo docentes activos.

        Returns:
            list: Docentes con la especialidad especificada.

        Examples:
            >>> matematicos = docente_model.search_by_especialidad('Matemáticas')
        """
        try:
            with self.engine.connect() as conn:
                query = f"""
                    SELECT * FROM {self.table_name}
                    WHERE especialidad LIKE :especialidad
                """

                if solo_activos:
                    query += " AND estado = 'Activo'"

                query += " ORDER BY apellido, nombre"

                result = conn.execute(
                    text(query), {"especialidad": f"%{especialidad}%"}
                )
                docentes = result.fetchall()

                return [dict(docente) for docente in docentes]

        except Exception as error:
            self._log_error(
                f"Error al buscar docentes por especialidad '{especialidad}': {error}"
            )
            return []

    # ============================================================================
    # MÉTODOS DE CONSULTA ESPECIALIZADA
    # ============================================================================

    def get_docentes_con_cursos(self, solo_activos=True):
        """
        Obtiene docentes con información de los cursos que imparten.

        Args:
            solo_activos (bool, optional): Filtrar solo docentes activos.

        Returns:
            list: Docentes con datos de sus cursos.

        Examples:
            >>> docentes_con_cursos = docente_model.get_docentes_con_cursos()
        """
        try:
            with self.engine.connect() as conn:
                # Consulta que obtiene docentes con información de cursos
                query = text(
                    """
                    SELECT 
                        d.*,
                        COUNT(c.id) as total_cursos,
                        GROUP_CONCAT(c.nombre, ', ') as cursos_nombres,
                        SUM(CASE WHEN c.estado = 'Activo' THEN 1 ELSE 0 END) as cursos_activos
                    FROM docentes d
                    LEFT JOIN cursos c ON d.id = c.docente_id
                    WHERE 1=1
                """
                )

                if solo_activos:
                    query = text(str(query) + " AND d.estado = 'Activo'")

                query = text(
                    str(query)
                    + """
                    GROUP BY d.id
                    ORDER BY d.apellido, d.nombre
                """
                )

                result = conn.execute(query)
                docentes = result.fetchall()

                return [dict(docente) for docente in docentes]

        except Exception as error:
            self._log_error(f"Error al obtener docentes con cursos: {error}")
            return []

    def get_docentes_disponibles(self):
        """
        Obtiene docentes disponibles (activos) sin sobrecarga de cursos.

        Returns:
            list: Docentes disponibles para asignar nuevos cursos.

        Examples:
            >>> docentes_disponibles = docente_model.get_docentes_disponibles()
        """
        try:
            with self.engine.connect() as conn:
                # Consulta que obtiene docentes con carga de trabajo
                query = text(
                    """
                    SELECT 
                        d.*,
                        COUNT(c.id) as cursos_asignados
                    FROM docentes d
                    LEFT JOIN cursos c ON d.id = c.docente_id AND c.estado = 'Activo'
                    WHERE d.estado = 'Activo'
                    GROUP BY d.id
                    HAVING cursos_asignados < 5  -- Límite de cursos por docente
                    ORDER BY cursos_asignados ASC, d.apellido, d.nombre
                """
                )

                result = conn.execute(query)
                docentes = result.fetchall()

                return [dict(docente) for docente in docentes]

        except Exception as error:
            self._log_error(f"Error al obtener docentes disponibles: {error}")
            return []

    def get_estadisticas(self):
        """
        Obtiene estadísticas generales de los docentes.

        Returns:
            dict: Diccionario con estadísticas de docentes.

        Examples:
            >>> estadisticas = docente_model.get_estadisticas()
            >>> print(f"Total docentes: {estadisticas['total']}")
            >>> print(f"Docentes activos: {estadisticas['activos']}")
        """
        try:
            with self.engine.connect() as conn:
                query = text(
                    f"""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN estado = 'Activo' THEN 1 ELSE 0 END) as activos,
                        SUM(CASE WHEN estado = 'Inactivo' THEN 1 ELSE 0 END) as inactivos,
                        COUNT(DISTINCT especialidad) as especialidades_distintas
                    FROM {self.table_name}
                """
                )

                result = conn.execute(query)
                row = result.fetchone()

                if row:
                    return {
                        "total": row[0],
                        "activos": row[1],
                        "inactivos": row[2],
                        "especialidades_distintas": row[3],
                    }
                else:
                    return {
                        "total": 0,
                        "activos": 0,
                        "inactivos": 0,
                        "especialidades_distintas": 0,
                    }

        except Exception as error:
            self._log_error(f"Error al obtener estadísticas de docentes: {error}")
            return {
                "total": 0,
                "activos": 0,
                "inactivos": 0,
                "especialidades_distintas": 0,
            }

    # ============================================================================
    # MÉTODOS AUXILIARES PRIVADOS
    # ============================================================================

    def _preparar_datos_creacion(self, datos):
        """
        Prepara los datos para la creación de un nuevo docente.

        Args:
            datos (dict): Datos crudos del docente.

        Returns:
            dict: Datos preparados con valores por defecto.
        """
        datos_preparados = datos.copy()

        # Establecer valores por defecto si no están presentes
        defaults = {
            "estado": "Activo",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        for key, value in defaults.items():
            if key not in datos_preparados or not datos_preparados[key]:
                datos_preparados[key] = value

        return datos_preparados

    def _preparar_datos_actualizacion(self, datos):
        """
        Prepara los datos para la actualización de un docente.

        Args:
            datos (dict): Datos a actualizar.

        Returns:
            dict: Datos preparados para actualización.
        """
        # Filtrar campos que no deben actualizarse directamente
        campos_excluidos = ["id", "created_at"]
        datos_preparados = {
            key: value
            for key, value in datos.items()
            if key not in campos_excluidos and value is not None
        }

        # Siempre actualizar el timestamp
        datos_preparados["updated_at"] = datetime.now()

        return datos_preparados

    def _construir_where_busqueda(self, criterio, valor):
        """
        Construye la cláusula WHERE para búsquedas.

        Args:
            criterio (str): Tipo de búsqueda.
            valor (str): Valor a buscar.

        Returns:
            str: Cláusula WHERE SQL.
        """
        if not valor:
            return ""

        criterios = {
            "nombre": f"WHERE nombre LIKE '%{valor}%' OR apellido LIKE '%{valor}%'",
            "especialidad": f"WHERE especialidad LIKE '%{valor}%'",
            "email": f"WHERE email LIKE '%{valor}%'",
            "identificacion": f"WHERE identificacion LIKE '%{valor}%'",
            "telefono": f"WHERE telefono LIKE '%{valor}%'",
            "todos": f"""
                WHERE nombre LIKE '%{valor}%' 
                OR apellido LIKE '%{valor}%'
                OR email LIKE '%{valor}%'
                OR identificacion LIKE '%{valor}%'
                OR especialidad LIKE '%{valor}%'
                OR telefono LIKE '%{valor}%'
            """,
        }

        return criterios.get(
            criterio, f"WHERE nombre LIKE '%{valor}%' OR apellido LIKE '%{valor}%'"
        )

    def _log_info(self, mensaje):
        """
        Registra mensajes informativos.

        Args:
            mensaje (str): Mensaje a registrar.
        """
        print(f"📝 [DocenteModel] INFO: {mensaje}")

    def _log_error(self, mensaje):
        """
        Registra mensajes de error.

        Args:
            mensaje (str): Mensaje de error a registrar.
        """
        print(f"❌ [DocenteModel] ERROR: {mensaje}")

    def _log_warning(self, mensaje):
        """
        Registra mensajes de advertencia.

        Args:
            mensaje (str): Mensaje de advertencia a registrar.
        """
        print(f"⚠️ [DocenteModel] WARNING: {mensaje}")
