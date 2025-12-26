-- ============================================================
-- SCRIPT DE CREACIÓN DE BASE DE DATOS - FORMA GEST PRO
-- PostgreSQL 18
-- Versión: 1.0.0
-- Autor: Sistema de Gestión Educativa
-- Fecha: 2025-12-25
-- ============================================================
-- 1. CREACIÓN DE LA BASE DE DATOS
-- ============================================================
-- Comentario: Crear la base de datos si no existe
-- Nota: Ejecutar este comando desde una conexión a la base de datos 'postgres'
-- DROP DATABASE IF EXISTS formagestpro_db;
-- CREATE DATABASE formagestpro_db
--     WITH 
--     OWNER = postgres
--     ENCODING = 'UTF8'
--     LC_COLLATE = 'Spanish_Spain.1252'
--     LC_CTYPE = 'Spanish_Spain.1252'
--     TABLESPACE = pg_default
--     CONNECTION LIMIT = -1
--     IS_TEMPLATE = False;

-- \c formagestpro_db;  -- Conectarse a la base de datos creada

SELECT datname FROM pg_database WHERE datistemplate = false;
SELECT current_database();

-- ============================================================
-- 2. CREACIÓN DE DOMINIOS (TYPES) PARA VALIDACIÓN
-- ============================================================
CREATE DOMAIN d_expedicion_ci AS TEXT 
    CHECK (VALUE IN ('BE', 'CH', 'CB', 'LP', 'OR', 'PD', 'PT', 'SC', 'TJ', 'EX'));

CREATE DOMAIN d_grado_academico AS TEXT 
    CHECK (VALUE IN ('Mtr.', 'Mgtr.', 'Mag.', 'MBA', 'MSc', 'M.Sc.', 'PhD.', 'Dr.', 'Dra.'));

CREATE DOMAIN d_estado_programa AS TEXT 
    CHECK (VALUE IN ('PLANIFICADO', 'INICIADO', 'CONCLUIDO', 'CANCELADO'));

CREATE DOMAIN d_modalidad_pago AS TEXT 
    CHECK (VALUE IN ('CONTADO', 'CUOTAS'));

CREATE DOMAIN d_estado_pago AS TEXT 
    CHECK (VALUE IN ('PENDIENTE', 'PARCIAL', 'PAGADO', 'MORA'));

CREATE DOMAIN d_estado_academico AS TEXT 
    CHECK (VALUE IN ('PREINSCRITO', 'INSCRITO', 'EN_CURSO', 'CONCLUIDO', 'RETIRADO'));

CREATE DOMAIN d_forma_pago AS TEXT 
    CHECK (VALUE IN ('EFECTIVO', 'TRANSFERENCIA', 'TARJETA', 'CHEQUE', 'DEPOSITO', 'QR'));

CREATE DOMAIN d_estado_transaccion AS TEXT 
    CHECK (VALUE IN ('REGISTRADO', 'CONFIRMADO', 'ANULADO'));

CREATE DOMAIN d_tipo_ingreso AS TEXT 
    CHECK (VALUE IN ('MATRICULA_CUOTA', 'MATRICULA_CONTADO', 'OTRO_INGRESO'));

CREATE DOMAIN d_tipo_documento AS TEXT 
    CHECK (VALUE IN ('VOUCHER', 'RECIBO_TALONARIO', 'DEPOSITO_BANCARIO', 'QR_CAPTURA', 'FACTURA', 'RESOLUCION_ADMIN'));

CREATE DOMAIN d_extension_archivo AS TEXT 
    CHECK (VALUE IN ('jpg', 'jpeg', 'png', 'pdf', 'txt'));

CREATE DOMAIN d_tipo_movimiento AS TEXT 
    CHECK (VALUE IN ('INGRESO', 'EGRESO'));

CREATE DOMAIN d_rol_usuario AS TEXT 
    CHECK (VALUE IN ('COORDINADOR', 'CAJERO', 'ADMINISTRADOR'));

-- ============================================================
-- 3. CREACIÓN DE SECUENCIAS PARA IDs AUTOINCREMENTALES
-- ============================================================
-- Comentario: En PostgreSQL, las secuencias permiten un mejor control
-- sobre los valores autoincrementales y su reutilización.

CREATE SEQUENCE seq_empresa_id START 1;
CREATE SEQUENCE seq_estudiantes_id START 1;
CREATE SEQUENCE seq_docentes_id START 1;
CREATE SEQUENCE seq_programas_academicos_id START 1;
CREATE SEQUENCE seq_planes_pago_id START 1;
CREATE SEQUENCE seq_matriculas_id START 1;
CREATE SEQUENCE seq_ingresos_id START 1;
CREATE SEQUENCE seq_gastos_id START 1;
CREATE SEQUENCE seq_comprobantes_adjuntos_id START 1;
CREATE SEQUENCE seq_movimientos_caja_id START 1;
CREATE SEQUENCE seq_facturas_id START 1;
CREATE SEQUENCE seq_usuarios_id START 1;
CREATE SEQUENCE seq_configuraciones_id START 1;
CREATE SEQUENCE seq_auditoria_transacciones_id START 1;

-- ============================================================
-- 4. CREACIÓN DE TABLAS PRINCIPALES
-- ============================================================

-- 4.1 TABLA: empresa
-- Comentario: Almacena la información de la empresa o institución
CREATE TABLE empresa (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_empresa_id'),
    nombre TEXT NOT NULL DEFAULT 'Formación Continua Consultora',
    nit TEXT UNIQUE NOT NULL DEFAULT '1234567012',
    direccion TEXT,
    telefono TEXT,
    email TEXT,
    logo_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Índices para búsquedas frecuentes
    CONSTRAINT uk_empresa_nit UNIQUE (nit)
);

-- 4.2 TABLA: estudiantes
-- Comentario: Información personal y académica de los estudiantes
CREATE TABLE estudiantes (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_estudiantes_id'),
    ci_numero TEXT NOT NULL,
    ci_expedicion d_expedicion_ci,
    nombres TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    fecha_nacimiento DATE,
    telefono TEXT,
    email TEXT,
    universidad_egreso TEXT,
    profesion TEXT,
    fotografia_path TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    
    -- Restricciones de integridad
    CONSTRAINT uk_estudiante_ci UNIQUE (ci_numero),
    CONSTRAINT ck_email_valido CHECK (email IS NULL OR email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    
    -- Índices para optimización
    CONSTRAINT idx_estudiante_nombre_apellido UNIQUE (nombres, apellidos)
);

-- 4.3 TABLA: docentes
-- Comentario: Información de los docentes/tutores del sistema
CREATE TABLE docentes (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_docentes_id'),
    ci_numero TEXT NOT NULL,
    ci_expedicion d_expedicion_ci,
    nombres TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    fecha_nacimiento DATE,
    max_grado_academico d_grado_academico,
    telefono TEXT,
    email TEXT,
    curriculum_path TEXT,
    especialidad TEXT,
    honorario_hora DECIMAL(10,2),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Restricciones
    CONSTRAINT uk_docente_ci UNIQUE (ci_numero),
    CONSTRAINT ck_email_docente_valido CHECK (email IS NULL OR email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT ck_honorario_positivo CHECK (honorario_hora >= 0)
);

-- 4.4 TABLA: programas_academicos
-- Comentario: Catálogo de programas académicos disponibles
CREATE TABLE programas_academicos (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_programas_academicos_id'),
    codigo TEXT NOT NULL,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    duracion_semanas INTEGER,
    horas_totales INTEGER,
    costo_base DECIMAL(10,2) NOT NULL,
    descuento_contado DECIMAL(5,2) DEFAULT 0,
    cupos_totales INTEGER NOT NULL,
    cupos_disponibles INTEGER,
    estado d_estado_programa DEFAULT 'PLANIFICADO',
    fecha_inicio_planificada DATE,
    fecha_inicio_real DATE,
    fecha_fin_real DATE,
    tutor_id INTEGER,
    promocion_activa BOOLEAN DEFAULT FALSE,
    descripcion_promocion TEXT,
    descuento_promocion DECIMAL(5,2) DEFAULT 0,
    costo_inscripcion DECIMAL(10,2) DEFAULT 0,
    costo_matricula DECIMAL(10,2) DEFAULT 0,
    promocion_fecha_limite DATE,
    cuotas_mensuales INTEGER DEFAULT 1,
    dias_entre_cuotas INTEGER DEFAULT 30,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Claves foráneas
    CONSTRAINT fk_programa_tutor 
        FOREIGN KEY (tutor_id) 
        REFERENCES docentes(id) 
        ON DELETE SET NULL,
    
    -- Restricciones de integridad
    CONSTRAINT uk_programa_codigo UNIQUE (codigo),
    CONSTRAINT ck_cupos_validos 
        CHECK (cupos_disponibles BETWEEN 0 AND cupos_totales),
    CONSTRAINT ck_descuentos_validos 
        CHECK (descuento_contado BETWEEN 0 AND 100 AND descuento_promocion BETWEEN 0 AND 100),
    CONSTRAINT ck_fechas_validas 
        CHECK (fecha_inicio_planificada IS NULL OR fecha_fin_real IS NULL OR fecha_fin_real >= fecha_inicio_planificada),
    
    -- Índices para optimización
    CONSTRAINT idx_programa_estado UNIQUE (estado, id)
);

-- 4.5 TABLA: planes_pago
-- Comentario: Configuración de planes de pago para programas
CREATE TABLE planes_pago (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_planes_pago_id'),
    programa_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    nro_cuotas INTEGER NOT NULL,
    intervalo_dias INTEGER NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Claves foráneas
    CONSTRAINT fk_plan_programa 
        FOREIGN KEY (programa_id) 
        REFERENCES programas_academicos(id) 
        ON DELETE CASCADE,
    
    -- Restricciones
    CONSTRAINT ck_cuotas_positivas CHECK (nro_cuotas > 0),
    CONSTRAINT ck_intervalo_positivo CHECK (intervalo_dias > 0),
    CONSTRAINT uk_plan_programa_nombre UNIQUE (programa_id, nombre)
);

-- 4.6 TABLA: matriculas
-- Comentario: Registro de matrículas de estudiantes en programas
CREATE TABLE matriculas (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_matriculas_id'),
    estudiante_id INTEGER NOT NULL,
    programa_id INTEGER NOT NULL,
    modalidad_pago d_modalidad_pago NOT NULL,
    plan_pago_id INTEGER,
    monto_total DECIMAL(10,2) NOT NULL,
    descuento_aplicado DECIMAL(10,2) DEFAULT 0,
    monto_final DECIMAL(10,2) NOT NULL,
    monto_pagado DECIMAL(10,2) DEFAULT 0,
    estado_pago d_estado_pago DEFAULT 'PENDIENTE',
    estado_academico d_estado_academico DEFAULT 'PREINSCRITO',
    fecha_matricula TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_inicio DATE,
    fecha_conclusion DATE,
    coordinador_id INTEGER,
    observaciones TEXT,
    
    -- Claves foráneas
    CONSTRAINT fk_matricula_estudiante 
        FOREIGN KEY (estudiante_id) 
        REFERENCES estudiantes(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_matricula_programa 
        FOREIGN KEY (programa_id) 
        REFERENCES programas_academicos(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_matricula_plan_pago 
        FOREIGN KEY (plan_pago_id) 
        REFERENCES planes_pago(id) 
        ON DELETE SET NULL,
    
    -- Restricciones de integridad
    CONSTRAINT uk_matricula_unica UNIQUE (estudiante_id, programa_id),
    CONSTRAINT ck_montos_validos 
        CHECK (monto_total >= 0 AND descuento_aplicado >= 0 AND monto_final >= 0 AND monto_pagado >= 0),
    CONSTRAINT ck_monto_final_correcto 
        CHECK (monto_final = monto_total - descuento_aplicado),
    CONSTRAINT ck_plan_pago_consistente 
        CHECK ((modalidad_pago = 'CUOTAS' AND plan_pago_id IS NOT NULL) OR 
               (modalidad_pago = 'CONTADO' AND plan_pago_id IS NULL)),
    CONSTRAINT ck_monto_pagado_no_excede 
        CHECK (monto_pagado <= monto_final),
    
    -- Índices para consultas frecuentes
    CONSTRAINT idx_matricula_estado UNIQUE (estado_pago, estado_academico)
);

-- 4.12 TABLA: usuarios
-- Comentario: Usuarios del sistema con roles y autenticación
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_usuarios_id'),
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    nombre_completo TEXT NOT NULL,
    email TEXT,
    rol d_rol_usuario DEFAULT 'COORDINADOR',
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    
    -- Restricciones
    CONSTRAINT ck_usuario_email_valido 
        CHECK (email IS NULL OR email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    
    -- Índices
    CONSTRAINT idx_usuario_rol UNIQUE (rol, username)
);

-- 4.7 TABLA: ingresos (TABLA UNIFICADA)
-- Comentario: Registro unificado de todos los ingresos del sistema
CREATE TABLE ingresos (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_ingresos_id'),
    tipo_ingreso d_tipo_ingreso NOT NULL,
    matricula_id INTEGER,
    nro_cuota INTEGER,
    fecha DATE NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    concepto TEXT NOT NULL,
    descripcion TEXT,
    forma_pago d_forma_pago,
    estado d_estado_transaccion DEFAULT 'REGISTRADO',
    nro_comprobante TEXT UNIQUE,
    nro_transaccion TEXT,
    registrado_por INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Claves foráneas
    CONSTRAINT fk_ingreso_matricula 
        FOREIGN KEY (matricula_id) 
        REFERENCES matriculas(id) 
        ON DELETE SET NULL,
    CONSTRAINT fk_ingreso_registrado_por 
        FOREIGN KEY (registrado_por) 
        REFERENCES usuarios(id) 
        ON DELETE SET NULL,
    
    -- Restricciones de integridad
    CONSTRAINT ck_monto_positivo CHECK (monto > 0),
    CONSTRAINT ck_tipo_matricula_consistente 
        CHECK ((tipo_ingreso IN ('MATRICULA_CUOTA', 'MATRICULA_CONTADO') AND matricula_id IS NOT NULL) OR
               (tipo_ingreso = 'OTRO_INGRESO' AND matricula_id IS NULL)),
    CONSTRAINT ck_nro_cuota_valido 
        CHECK (nro_cuota IS NULL OR nro_cuota > 0),
    
    -- Índices
    CONSTRAINT idx_ingreso_fecha UNIQUE (fecha, id),
    CONSTRAINT idx_ingreso_matricula UNIQUE (matricula_id, tipo_ingreso)
);

-- 4.8 TABLA: gastos
-- Comentario: Registro de gastos operativos del sistema
CREATE TABLE gastos (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_gastos_id'),
    fecha DATE NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    categoria TEXT NOT NULL,
    subcategoria TEXT,
    descripcion TEXT,
    proveedor TEXT,
    nro_factura TEXT,
    forma_pago d_forma_pago,
    comprobante_nro TEXT,
    registrado_por INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Claves foráneas
    CONSTRAINT fk_gasto_registrado_por 
        FOREIGN KEY (registrado_por) 
        REFERENCES usuarios(id) 
        ON DELETE SET NULL,
    
    -- Restricciones
    CONSTRAINT ck_gasto_monto_positivo CHECK (monto > 0),
    
    -- Índices
    CONSTRAINT idx_gasto_categoria UNIQUE (categoria, fecha)
);

-- 4.9 TABLA: comprobantes_adjuntos (VERSIÓN CORREGIDA)
-- Comentario: Archivos adjuntos de comprobantes (unificada para ingresos y gastos)
CREATE TABLE comprobantes_adjuntos (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_comprobantes_adjuntos_id'),
    origen_tipo TEXT NOT NULL CHECK (origen_tipo IN ('INGRESO', 'GASTO')),
    origen_id INTEGER NOT NULL,
    tipo_documento d_tipo_documento NOT NULL,
    ruta_archivo TEXT NOT NULL,
    nombre_original TEXT,
    extension d_extension_archivo,
    subido_por INTEGER,
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Claves foráneas
    CONSTRAINT fk_comprobante_subido_por 
        FOREIGN KEY (subido_por) 
        REFERENCES usuarios(id) 
        ON DELETE SET NULL,
    
    -- Restricciones de integridad
    CONSTRAINT uk_comprobante_origen UNIQUE (origen_tipo, origen_id, tipo_documento),
    
    -- Índices
    CONSTRAINT idx_comprobante_tipo UNIQUE (tipo_documento, origen_tipo)
);

-- FUNCIÓN PARA VALIDAR EL ORIGEN (REEMPLAZA EL CHECK CONSTRAINT)
CREATE OR REPLACE FUNCTION fn_validar_origen_comprobante()
RETURNS TRIGGER AS $$
BEGIN
    -- Validar que el origen_id exista en la tabla correspondiente
    IF NEW.origen_tipo = 'INGRESO' THEN
        IF NOT EXISTS (SELECT 1 FROM ingresos WHERE id = NEW.origen_id) THEN
            RAISE EXCEPTION 'El origen_id % no existe en la tabla ingresos', NEW.origen_id;
        END IF;
    ELSIF NEW.origen_tipo = 'GASTO' THEN
        IF NOT EXISTS (SELECT 1 FROM gastos WHERE id = NEW.origen_id) THEN
            RAISE EXCEPTION 'El origen_id % no existe en la tabla gastos', NEW.origen_id;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- TRIGGER PARA VALIDAR ANTES DE INSERTAR/ACTUALIZAR
CREATE TRIGGER tr_validar_origen_comprobante
    BEFORE INSERT OR UPDATE ON comprobantes_adjuntos
    FOR EACH ROW
    EXECUTE FUNCTION fn_validar_origen_comprobante();

-- 4.10 TABLA: movimientos_caja
-- Comentario: Movimientos simplificados de caja para reportes rápidos
CREATE TABLE movimientos_caja (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_movimientos_caja_id'),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    tipo d_tipo_movimiento NOT NULL,
    monto DECIMAL(12,2) NOT NULL,
    origen_tipo TEXT CHECK (origen_tipo IN ('INGRESO', 'GASTO')),
    origen_id INTEGER,
    descripcion TEXT NOT NULL,
    registrado_por INTEGER,
    
    -- Claves foráneas
    CONSTRAINT fk_movimiento_registrado_por 
        FOREIGN KEY (registrado_por) 
        REFERENCES usuarios(id) 
        ON DELETE SET NULL,
    
    -- Restricciones
    CONSTRAINT ck_movimiento_monto_positivo CHECK (monto > 0),
    CONSTRAINT uk_movimiento_origen UNIQUE (origen_tipo, origen_id),
    
    -- Índices para consultas de caja
    CONSTRAINT idx_movimiento_fecha_tipo UNIQUE (fecha, tipo)
);

-- 4.11 TABLA: facturas
-- Comentario: Registro de facturas emitidas (solo registro, no generación)
CREATE TABLE facturas (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_facturas_id'),
    nro_factura TEXT UNIQUE NOT NULL,
    fecha_emision DATE NOT NULL,
    tipo_documento TEXT CHECK (tipo_documento IN ('NIT', 'CI', 'CONSUMIDOR_FINAL')),
    nit_ci TEXT,
    razon_social TEXT NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL,
    iva DECIMAL(12,2) NOT NULL,
    it DECIMAL(12,2) NOT NULL,
    total DECIMAL(12,2) NOT NULL,
    concepto TEXT,
    estado TEXT DEFAULT 'EMITIDA',
    exportada_siat BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Restricciones
    CONSTRAINT ck_montos_factura CHECK (total = subtotal + iva + it),
    
    -- Índices
    CONSTRAINT idx_factura_fecha UNIQUE (fecha_emision, nro_factura)
);

-- 4.13 TABLA: configuraciones
-- Comentario: Configuraciones del sistema (clave-valor)
CREATE TABLE configuraciones (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_configuraciones_id'),
    clave TEXT UNIQUE NOT NULL,
    valor TEXT,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Índices
    CONSTRAINT idx_configuracion_clave UNIQUE (clave)
);

-- 4.14 TABLA: auditoria_transacciones
-- Comentario: Auditoría de todas las transacciones (ingresos y gastos)
CREATE TABLE auditoria_transacciones (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_auditoria_transacciones_id'),
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INTEGER NOT NULL,
    origen_tipo TEXT NOT NULL CHECK (origen_tipo IN ('INGRESO', 'GASTO')),
    origen_id INTEGER NOT NULL,
    accion TEXT NOT NULL CHECK (accion IN ('CREACION', 'MODIFICACION', 'ELIMINACION', 'ANULACION')),
    motivo TEXT NOT NULL,
    responsable_autoriza TEXT,
    ruta_resolucion TEXT,
    datos_anteriores TEXT,
    datos_nuevos TEXT,
    
    -- Claves foráneas
    CONSTRAINT fk_auditoria_usuario 
        FOREIGN KEY (usuario_id) 
        REFERENCES usuarios(id) 
        ON DELETE CASCADE,
    
    -- Índices para consultas de auditoría
    CONSTRAINT idx_auditoria_fecha_accion UNIQUE (fecha_hora, accion),
    CONSTRAINT idx_auditoria_origen UNIQUE (origen_tipo, origen_id, accion)
);

-- ============================================================
-- 5. CREACIÓN DE FUNCIONES Y TRIGGERS
-- ============================================================

-- 5.1 FUNCIÓN: Actualizar monto_pagado en matrículas
-- Comentario: Actualiza automáticamente el monto pagado cuando se registra un ingreso
CREATE OR REPLACE FUNCTION fn_actualizar_monto_pagado_matricula()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' AND NEW.tipo_ingreso IN ('MATRICULA_CUOTA', 'MATRICULA_CONTADO') THEN
        UPDATE matriculas 
        SET monto_pagado = monto_pagado + NEW.monto,
            estado_pago = CASE 
                WHEN (monto_pagado + NEW.monto) >= monto_final THEN 'PAGADO'::d_estado_pago
                WHEN (monto_pagado + NEW.monto) > 0 THEN 'PARCIAL'::d_estado_pago
                ELSE 'PENDIENTE'::d_estado_pago
            END
        WHERE id = NEW.matricula_id;
        
        -- Registrar movimiento de caja automático
        INSERT INTO movimientos_caja (tipo, monto, origen_tipo, origen_id, descripcion, registrado_por)
        VALUES ('INGRESO', NEW.monto, 'INGRESO', NEW.id, 
                CONCAT('Ingreso por matrícula: ', NEW.concepto), NEW.registrado_por);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 5.2 TRIGGER para actualizar monto_pagado
CREATE TRIGGER tr_actualizar_monto_pagado
    AFTER INSERT ON ingresos
    FOR EACH ROW
    EXECUTE FUNCTION fn_actualizar_monto_pagado_matricula();

-- 5.3 FUNCIÓN: Registrar movimiento de caja para gastos
CREATE OR REPLACE FUNCTION fn_registrar_movimiento_caja_gasto()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO movimientos_caja (tipo, monto, origen_tipo, origen_id, descripcion, registrado_por)
        VALUES ('EGRESO', NEW.monto, 'GASTO', NEW.id, 
                CONCAT('Gasto: ', NEW.categoria, ' - ', NEW.descripcion), NEW.registrado_por);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 5.4 TRIGGER para movimientos de caja de gastos
CREATE TRIGGER tr_registrar_movimiento_gasto
    AFTER INSERT ON gastos
    FOR EACH ROW
    EXECUTE FUNCTION fn_registrar_movimiento_caja_gasto();

-- 5.5 FUNCIÓN: Actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION fn_actualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 5.6 TRIGGER para updated_at en programas_academicos
CREATE TRIGGER tr_actualizar_timestamp_programa
    BEFORE UPDATE ON programas_academicos
    FOR EACH ROW
    EXECUTE FUNCTION fn_actualizar_timestamp();

-- 5.7 TRIGGER para updated_at en configuraciones
CREATE TRIGGER tr_actualizar_timestamp_configuracion
    BEFORE UPDATE ON configuraciones
    FOR EACH ROW
    EXECUTE FUNCTION fn_actualizar_timestamp();

-- 5.8 FUNCIÓN: Validar cupos disponibles
CREATE OR REPLACE FUNCTION fn_validar_cupos_matricula()
RETURNS TRIGGER AS $$
DECLARE
    cupos_disponibles INTEGER;
BEGIN
    SELECT cupos_disponibles INTO cupos_disponibles
    FROM programas_academicos
    WHERE id = NEW.programa_id;
    
    IF cupos_disponibles <= 0 THEN
        RAISE EXCEPTION 'No hay cupos disponibles para este programa';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 5.9 TRIGGER para validar cupos antes de matricular
CREATE TRIGGER tr_validar_cupos_matricula
    BEFORE INSERT ON matriculas
    FOR EACH ROW
    EXECUTE FUNCTION fn_validar_cupos_matricula();

-- 5.10 FUNCIÓN: Actualizar cupos disponibles
CREATE OR REPLACE FUNCTION fn_actualizar_cupos_matricula()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE programas_academicos
        SET cupos_disponibles = cupos_disponibles - 1
        WHERE id = NEW.programa_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE programas_academicos
        SET cupos_disponibles = cupos_disponibles + 1
        WHERE id = OLD.programa_id;
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- 5.11 TRIGGER para actualizar cupos después de matrícula
CREATE TRIGGER tr_actualizar_cupos_matricula
    AFTER INSERT OR DELETE ON matriculas
    FOR EACH ROW
    EXECUTE FUNCTION fn_actualizar_cupos_matricula();

-- ============================================================
-- 6. CREACIÓN DE VISTAS PARA REPORTES
-- ============================================================

-- 6.1 VISTA: Resumen financiero por programa
CREATE OR REPLACE VIEW vw_resumen_financiero_programa AS
SELECT 
    p.id AS programa_id,
    p.codigo,
    p.nombre AS programa_nombre,
    COUNT(m.id) AS total_matriculas,
    SUM(m.monto_total) AS ingresos_potenciales,
    SUM(m.monto_pagado) AS ingresos_reales,
    SUM(m.monto_final - m.monto_pagado) AS saldo_pendiente,
    AVG(m.monto_pagado / m.monto_final * 100) AS porcentaje_pago_promedio
FROM programas_academicos p
LEFT JOIN matriculas m ON p.id = m.programa_id
GROUP BY p.id, p.codigo, p.nombre;

-- 6.2 VISTA: Estado de pagos por estudiante
CREATE OR REPLACE VIEW vw_estado_pagos_estudiante AS
SELECT 
    e.id AS estudiante_id,
    e.nombres || ' ' || e.apellidos AS estudiante_nombre,
    e.ci_numero,
    COUNT(DISTINCT m.id) AS total_programas,
    SUM(m.monto_final) AS total_debe,
    SUM(m.monto_pagado) AS total_pagado,
    SUM(m.monto_final - m.monto_pagado) AS total_saldo,
    STRING_AGG(p.nombre, ', ') AS programas_inscritos
FROM estudiantes e
JOIN matriculas m ON e.id = m.estudiante_id
JOIN programas_academicos p ON m.programa_id = p.id
GROUP BY e.id, e.nombres, e.apellidos, e.ci_numero;

-- 6.3 VISTA: Movimientos de caja diarios
CREATE OR REPLACE VIEW vw_movimientos_caja_diarios AS
SELECT 
    DATE(fecha) AS fecha_dia,
    tipo,
    COUNT(*) AS cantidad_movimientos,
    SUM(monto) AS total_monto,
    STRING_AGG(descripcion, '; ') AS descripciones
FROM movimientos_caja
GROUP BY DATE(fecha), tipo
ORDER BY fecha_dia DESC;

-- 6.4 VISTA: Ingresos detallados por tipo
CREATE OR REPLACE VIEW vw_ingresos_detallados AS
SELECT 
    i.id,
    i.tipo_ingreso,
    i.fecha,
    i.monto,
    i.concepto,
    i.forma_pago,
    i.estado,
    e.nombres || ' ' || e.apellidos AS estudiante_nombre,
    p.nombre AS programa_nombre,
    u.nombre_completo AS registrado_por
FROM ingresos i
LEFT JOIN matriculas m ON i.matricula_id = m.id
LEFT JOIN estudiantes e ON m.estudiante_id = e.id
LEFT JOIN programas_academicos p ON m.programa_id = p.id
LEFT JOIN usuarios u ON i.registrado_por = u.id
ORDER BY i.fecha DESC;

-- ============================================================
-- 7. INSERCIÓN DE DATOS INICIALES
-- ============================================================

-- 7.1 Insertar empresa por defecto
INSERT INTO empresa (nombre, nit, direccion, telefono, email) 
VALUES ('CONSULTORA FORMACION CONTINUA S.R.L.', '194810025', 'Calle Calama Nro 104 piso 1', '+591 67935343', 'info@formacioncontinua.bo')
ON CONFLICT (nit) DO NOTHING;

-- 7.2 Insertar usuario administrador por defecto
-- Contraseña: "admin123" (debe ser hasheada en la aplicación real)
INSERT INTO usuarios (username, password_hash, nombre_completo, email, rol) 
VALUES ('admin', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Administrador del Sistema', 'admin@formacioncontinua.bo', 'ADMINISTRADOR')
ON CONFLICT (username) DO NOTHING;

-- 7.3 Insertar configuraciones iniciales
INSERT INTO configuraciones (clave, valor, descripcion) VALUES
('EMPRESA_NOMBRE', 'Formación Continua Consultora', 'CONSULTORA FORMACION CONTINUA S.R.L.'),
('EMPRESA_NIT', '194810025', 'NIT de la empresa'),
('EMPRESA_DIRECCION', 'Calle Calama Nro 104 piso 1', 'Dirección de la empresa'),
('EMPRESA_TELEFONO', '+591 67935343', 'Teléfono de la empresa'),
('EMPRESA_EMAIL', 'info@formacioncontinua.bo', 'Email de la empresa'),
('SISTEMA_VERSION', '1.0.0', 'Versión del sistema'),
('IMPUESTO_IVA', '13', 'Porcentaje de IVA aplicable'),
('IMPUESTO_IT', '3', 'Porcentaje de IT aplicable'),
('RUTA_COMPROBANTES', 'archivos/comprobantes/', 'Ruta base para comprobantes'),
('RUTA_FOTOS_ESTUDIANTES', 'archivos/fotos_estudiantes/', 'Ruta para fotos de estudiantes'),
('RUTA_CURRICULUM_DOCENTES', 'archivos/cv_docentes/', 'Ruta para CV de docentes')
ON CONFLICT (clave) DO UPDATE SET valor = EXCLUDED.valor;

-- ============================================================
-- 8. CREACIÓN DE ÍNDICES ADICIONALES PARA OPTIMIZACIÓN
-- ============================================================

-- Índices para búsquedas por fecha
CREATE INDEX idx_ingresos_fecha ON ingresos(fecha DESC);
CREATE INDEX idx_gastos_fecha ON gastos(fecha DESC);
CREATE INDEX idx_matriculas_fecha ON matriculas(fecha_matricula DESC);

-- Índices para búsquedas por estado
CREATE INDEX idx_matriculas_estado_pago ON matriculas(estado_pago);
CREATE INDEX idx_matriculas_estado_academico ON matriculas(estado_academico);
CREATE INDEX idx_ingresos_estado ON ingresos(estado);
CREATE INDEX idx_programas_estado ON programas_academicos(estado);

-- Índices para búsquedas por relaciones
CREATE INDEX idx_matriculas_estudiante ON matriculas(estudiante_id);
CREATE INDEX idx_matriculas_programa ON matriculas(programa_id);
CREATE INDEX idx_ingresos_matricula ON ingresos(matricula_id);
CREATE INDEX idx_planes_pago_programa ON planes_pago(programa_id);

-- Índices para textos frecuentes
CREATE INDEX idx_estudiantes_nombre_apellido ON estudiantes(nombres, apellidos);
CREATE INDEX idx_docentes_nombre_apellido ON docentes(nombres, apellidos);
CREATE INDEX idx_programas_nombre ON programas_academicos(nombre);

-- ============================================================
-- 9. COMENTARIOS DE DOCUMENTACIÓN
-- ============================================================

COMMENT ON DATABASE formagestpro_db IS 'Base de datos del sistema FormaGestPro - Gestión Educativa';
COMMENT ON TABLE empresa IS 'Información de la empresa o institución educativa';
COMMENT ON TABLE estudiantes IS 'Registro de estudiantes del sistema';
COMMENT ON TABLE docentes IS 'Registro de docentes y tutores';
COMMENT ON TABLE programas_academicos IS 'Catálogo de programas académicos ofertados';
COMMENT ON TABLE planes_pago IS 'Planes de pago configurados para los programas';
COMMENT ON TABLE matriculas IS 'Matrículas de estudiantes en programas académicos';
COMMENT ON TABLE ingresos IS 'Ingresos unificados del sistema (matrículas y otros)';
COMMENT ON TABLE gastos IS 'Gastos operativos del sistema';
COMMENT ON TABLE comprobantes_adjuntos IS 'Archivos adjuntos de comprobantes (ingresos y gastos)';
COMMENT ON TABLE movimientos_caja IS 'Movimientos simplificados de caja para reportes';
COMMENT ON TABLE facturas IS 'Registro de facturas emitidas';
COMMENT ON TABLE usuarios IS 'Usuarios del sistema con autenticación';
COMMENT ON TABLE configuraciones IS 'Configuraciones del sistema en formato clave-valor';
COMMENT ON TABLE auditoria_transacciones IS 'Auditoría de transacciones del sistema';

-- ============================================================
-- 10. SENTENCIAS DE VERIFICACIÓN
-- ============================================================

-- Verificar que las tablas se crearon correctamente
DO $$
BEGIN
    RAISE NOTICE '=========================================';
    RAISE NOTICE 'BASE DE DATOS CREADA EXITOSAMENTE';
    RAISE NOTICE '=========================================';
    RAISE NOTICE 'Tablas creadas: %', (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public');
    RAISE NOTICE 'Vistas creadas: %', (SELECT COUNT(*) FROM information_schema.views WHERE table_schema = 'public');
    RAISE NOTICE 'Funciones creadas: %', (SELECT COUNT(*) FROM information_schema.routines WHERE routine_schema = 'public');
    RAISE NOTICE 'Triggers creados: %', (SELECT COUNT(*) FROM information_schema.triggers WHERE trigger_schema = 'public');
    RAISE NOTICE '=========================================';
END $$;

-- Mostrar resumen de tablas
SELECT 
    table_name AS "Tabla",
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) AS "Columnas",
    (SELECT COUNT(*) FROM information_schema.table_constraints WHERE table_name = t.table_name AND constraint_type = 'FOREIGN KEY') AS "FKs",
    (SELECT COUNT(*) FROM information_schema.table_constraints WHERE table_name = t.table_name AND constraint_type = 'PRIMARY KEY') AS "PKs"
FROM information_schema.tables t
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY table_name;