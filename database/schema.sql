-- ============================================
-- ESQUEMA COMPLETO FORMA_GEST_PRO
-- archivo: database/schema.sql
-- ============================================
-- Basado en los requisitos del negocio
-- ============================================

-- Tabla de configuración de empresa
CREATE TABLE IF NOT EXISTS empresa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL DEFAULT "Formación Continua Consultora",
    nit TEXT UNIQUE NOT NULL DEFAULT "1234567012",
    direccion TEXT,
    telefono TEXT,
    email TEXT,
    logo_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de estudiantes
CREATE TABLE IF NOT EXISTS estudiantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ci_numero TEXT UNIQUE NOT NULL,
    ci_expedicion TEXT CHECK(ci_expedicion IN ('BE', 'CH', 'CB', 'LP', 'OR', 'PD', 'PT', 'SC', 'TJ', 'EX')),
    nombres TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    fecha_nacimiento DATE,
    telefono TEXT,
    email TEXT,
    universidad_egreso TEXT,
    profesion TEXT,
    fotografia_path TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT 1
);

-- Tabla de docentes/tutores
CREATE TABLE IF NOT EXISTS docentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ci_numero TEXT UNIQUE NOT NULL,
    ci_expedicion TEXT CHECK(ci_expedicion IN ('BE', 'CH', 'CB', 'LP', 'OR', 'PD', 'PT', 'SC', 'TJ', 'EX')),
    nombres TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    fecha_nacimiento DATE,
    max_grado_academico TEXT CHECK(max_grado_academico IN ('Mtr.', 'Mgtr.', 'Mag.', 'MBA', 'MSc', 'M.Sc.', 'PhD.', 'Dr.', 'Dra.')),
    telefono TEXT,
    email TEXT,
    curriculum_path TEXT,
    especialidad TEXT,
    honorario_hora DECIMAL(10,2),
    activo BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de programas académicos
CREATE TABLE "programas_academicos" (
	"id"	INTEGER,
	"codigo"	TEXT NOT NULL UNIQUE,
	"nombre"	TEXT NOT NULL,
	"descripcion"	TEXT,
	"duracion_semanas"	INTEGER,
	"horas_totales"	BLOB,
	"costo_base"	DECIMAL(10, 2) NOT NULL,
	"descuento_contado"	DECIMAL(5, 2) DEFAULT 0,
	"cupos_totales"	INTEGER NOT NULL,
	"cupos_disponibles"	INTEGER,
	"estado"	TEXT DEFAULT 'PLANIFICADO' CHECK("estado" IN ('PLANIFICADO', 'INICIADO', 'CONCLUIDO', 'CANCELADO')),
	"fecha_inicio_planificada"	DATE,
	"fecha_inicio_real"	DATE,
	"fecha_fin_real"	DATE,
	"tutor_id"	INTEGER,
	"promocion_activa"	BOOLEAN DEFAULT 0,
	"descripcion_promocion"	TEXT,
	"descuento_promocion"	DECIMAL(5, 2) DEFAULT 0,
	"created_at"	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	"updated_at"	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	"costo_inscripcion"	DECIMAL(10, 2) DEFAULT 0,
	"costo_matricula"	DECIMAL(10, 2) DEFAULT 0,
	"promocion_fecha_limite"	DATE,
	"cuotas_mensuales"	REAL DEFAULT 1,
	"dias_entre_cuotas"	INTEGER DEFAULT 30,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("tutor_id") REFERENCES "docentes"("id"),
	CHECK("cupos_disponibles" BETWEEN 0 AND "cupos_totales")
);

-- Tabla de planes de pago (para cuotas)
CREATE TABLE IF NOT EXISTS planes_pago (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    programa_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    nro_cuotas INTEGER NOT NULL CHECK (nro_cuotas > 0),
    intervalo_dias INTEGER NOT NULL CHECK (intervalo_dias > 0),
    descripcion TEXT,
    activo BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (programa_id) REFERENCES programas_academicos(id),
    UNIQUE(programa_id, nombre)
);

-- Tabla de matrículas
CREATE TABLE IF NOT EXISTS matriculas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estudiante_id INTEGER NOT NULL,
    programa_id INTEGER NOT NULL,
    
    -- Modalidad de pago
    modalidad_pago TEXT CHECK(modalidad_pago IN ('CONTADO', 'CUOTAS')) NOT NULL,
    plan_pago_id INTEGER,
    
    -- Montos
    monto_total DECIMAL(10,2) NOT NULL,
    descuento_aplicado DECIMAL(10,2) DEFAULT 0,
    monto_final DECIMAL(10,2) NOT NULL,
    
    -- Estado financiero
    monto_pagado DECIMAL(10,2) DEFAULT 0,
    estado_pago TEXT CHECK(estado_pago IN ('PENDIENTE', 'PARCIAL', 'PAGADO', 'MORA')) DEFAULT 'PENDIENTE',
    
    -- Estado académico
    estado_academico TEXT CHECK(estado_academico IN ('PREINSCRITO', 'INSCRITO', 'EN_CURSO', 'CONCLUIDO', 'RETIRADO')) DEFAULT 'PREINSCRITO',
    
    -- Fechas
    fecha_matricula TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_inicio DATE,
    fecha_conclusion DATE,
    
    -- Auditoría
    coordinador_id INTEGER,
    observaciones TEXT,
    
    UNIQUE(estudiante_id, programa_id),
    FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id),
    FOREIGN KEY (programa_id) REFERENCES programas_academicos(id),
    FOREIGN KEY (plan_pago_id) REFERENCES planes_pago(id),
    
    CHECK (monto_final = monto_total - descuento_aplicado),
    CHECK ((modalidad_pago = 'CUOTAS' AND plan_pago_id IS NOT NULL) OR 
           (modalidad_pago = 'CONTADO' AND plan_pago_id IS NULL))
);

-- Tabla de pagos
CREATE TABLE IF NOT EXISTS pagos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matricula_id INTEGER NOT NULL,
    nro_cuota INTEGER,
    monto DECIMAL(10,2) NOT NULL,
    fecha_pago DATE NOT NULL,
    forma_pago TEXT CHECK(forma_pago IN ('EFECTIVO', 'TRANSFERENCIA', 'TARJETA', 'CHEQUE', 'DEPOSITO', 'PAGOS QR')),
    estado TEXT CHECK(estado IN ('REGISTRADO', 'CONFIRMADO', 'ANULADO')) DEFAULT 'REGISTRADO',
    nro_comprobante TEXT UNIQUE,
    nro_transaccion TEXT,
    observaciones TEXT,
    registrado_por INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (matricula_id) REFERENCES matriculas(id),
    CHECK (nro_cuota IS NULL OR nro_cuota > 0)
);

-- Tabla de cuotas programadas
CREATE TABLE IF NOT EXISTS cuotas_programadas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matricula_id INTEGER NOT NULL,
    nro_cuota INTEGER NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    estado TEXT CHECK(estado IN ('PENDIENTE', 'PAGADA', 'VENCIDA', 'CANCELADA')) DEFAULT 'PENDIENTE',
    fecha_pago DATE,
    pago_id INTEGER,
    interes_mora DECIMAL(10,2) DEFAULT 0,
    dias_mora INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (matricula_id) REFERENCES matriculas(id),
    FOREIGN KEY (pago_id) REFERENCES pagos(id),
    
    UNIQUE(matricula_id, nro_cuota)
);

-- Tabla de gastos operativos
CREATE TABLE IF NOT EXISTS gastos_operativos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha DATE NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    categoria TEXT NOT NULL,
    subcategoria TEXT,
    descripcion TEXT,
    proveedor TEXT,
    nro_factura TEXT,
    forma_pago TEXT CHECK(forma_pago IN ('EFECTIVO', 'TRANSFERENCIA', 'TARJETA', 'CHEQUE', 'DEPOSITO', 'PAGOS QR')),
    comprobante_nro TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de movimientos de caja
CREATE TABLE IF NOT EXISTS movimientos_caja (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo TEXT CHECK(tipo IN ('INGRESO', 'EGRESO')) NOT NULL,
    monto DECIMAL(12,2) NOT NULL,
    descripcion TEXT,
    referencia_tipo TEXT,
    referencia_id INTEGER
);

-- Tabla de facturas (solo registro, no generación)
CREATE TABLE IF NOT EXISTS facturas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nro_factura TEXT UNIQUE NOT NULL,
    fecha_emision DATE NOT NULL,
    tipo_documento TEXT CHECK(tipo_documento IN ('NIT', 'CI', 'CONSUMIDOR_FINAL')),
    nit_ci TEXT,
    razon_social TEXT NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL,
    iva DECIMAL(12,2) NOT NULL,
    it DECIMAL(12,2) NOT NULL,
    total DECIMAL(12,2) NOT NULL,
    concepto TEXT,
    estado TEXT DEFAULT 'EMITIDA',
    exportada_siat BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de usuarios del sistema
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    nombre_completo TEXT NOT NULL,
    email TEXT,
    rol TEXT CHECK(rol IN ('COORDINADOR', 'CAJERO', 'ADMINISTRADOR')) DEFAULT 'COORDINADOR',
    activo BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Tabla de configuraciones del sistema
CREATE TABLE IF NOT EXISTS configuraciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clave TEXT UNIQUE NOT NULL,
    valor TEXT,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de ingresos genéricos (no asociados a matrículas)
CREATE TABLE IF NOT EXISTS ingresos_genericos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha DATE NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    concepto TEXT NOT NULL,
    descripcion TEXT,
    forma_pago TEXT CHECK(forma_pago IN ('EFECTIVO', 'TRANSFERENCIA', 'TARJETA', 'CHEQUE', 'DEPOSITO', 'PAGOS QR')),
    comprobante_nro TEXT,
    registrado_por INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);