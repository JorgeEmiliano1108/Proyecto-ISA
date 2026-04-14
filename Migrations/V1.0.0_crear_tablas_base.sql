/*
PROYECTO: ISA CORPORATIVO - EVALUACIÓN DISCRECIONAL
MIGRACIÓN: V1.0.0__crear_tablas_base
*/

-- 1. CATÁLOGOS (No dependen de nadie)
CREATE TABLE cat_roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    nivel_aprobacion INT NOT NULL,
    activo BOOLEAN DEFAULT true
);

CREATE TABLE cat_departamentos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    activo BOOLEAN DEFAULT true
);

CREATE TABLE cat_competencias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT true
);

-- 2. SEGURIDAD (Depende de roles y departamentos)
CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL, 
    rol_id INT NOT NULL REFERENCES cat_roles(id),
    departamento_id INT NOT NULL REFERENCES cat_departamentos(id),
    manager_id UUID REFERENCES usuarios(id),
    fecha_registro TIMESTAMP DEFAULT now()
);

-- 3. TRANSACCIONAL - CABECERA (Depende de usuarios)
CREATE TABLE evaluaciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evaluado_id UUID NOT NULL REFERENCES usuarios(id),
    evaluador_id UUID NOT NULL REFERENCES usuarios(id),
    periodo_id INT NOT NULL,
    estado VARCHAR(50) DEFAULT 'DRAFT',
    logros_previos TEXT,
    comentarios_evaluador TEXT,
    comentarios_evaluado TEXT,
    fecha_creacion TIMESTAMP DEFAULT now(),
    fecha_actualizacion TIMESTAMP DEFAULT now(),
    fecha_ultimo_recordatorio TIMESTAMP
);

-- 4. TRANSACCIONAL - DETALLE (Depende de evaluaciones y competencias)
CREATE TABLE competencias_detalle (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evaluacion_id UUID NOT NULL REFERENCES evaluaciones(id) ON DELETE CASCADE,
    competencia_id INT NOT NULL REFERENCES cat_competencias(id),
    calificacion INT CHECK (calificacion BETWEEN 1 AND 5),
    comentario TEXT NOT NULL
);

CREATE TABLE objetivos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evaluacion_id UUID NOT NULL REFERENCES evaluaciones(id) ON DELETE CASCADE,
    descripcion TEXT NOT NULL
);

-- 5. AUDITORÍA Y FLUJO (Dependen de evaluaciones, usuarios y roles)
CREATE TABLE historial_estados (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evaluacion_id UUID NOT NULL REFERENCES evaluaciones(id) ON DELETE CASCADE,
    estado_anterior VARCHAR(50) NOT NULL,
    estado_nuevo VARCHAR(50) NOT NULL,
    usuario_id UUID NOT NULL REFERENCES usuarios(id),
    comentario TEXT,
    fecha TIMESTAMP DEFAULT now()
);

CREATE TABLE aprobaciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evaluacion_id UUID NOT NULL REFERENCES evaluaciones(id) ON DELETE CASCADE,
    rol_id INT NOT NULL REFERENCES cat_roles(id),
    usuario_id UUID NOT NULL REFERENCES usuarios(id),
    firma_digital_base64 TEXT NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    fecha_firma TIMESTAMP DEFAULT now()
);

CREATE TABLE logs_sistema (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuarios(id),
    accion VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    detalle TEXT,
    fecha TIMESTAMP DEFAULT now()
);

-- 6. FINANZAS (Depende de evaluaciones)
CREATE TABLE bonos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evaluacion_id UUID NOT NULL REFERENCES evaluaciones(id) ON DELETE CASCADE,
    salario_base_snapshot DECIMAL(12,2) NOT NULL,
    impacto_ebitda_logrado DECIMAL(5,2) NOT NULL,
    performance_index DECIMAL(5,2) NOT NULL,
    monto_final_bono DECIMAL(12,2) NOT NULL,
    fecha_calculo TIMESTAMP DEFAULT now()
);


-- Ajustes finales

-- 1. Crear tabla de Periodos (Faltante para Contraloría)
CREATE TABLE cat_periodos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL, -- Ej: 'Anual 2025'
    activo BOOLEAN DEFAULT true
);

-- 2. Ajustes en la tabla de Evaluaciones
ALTER TABLE evaluaciones 
-- Como periodo_id ya existe, solo le agregamos la restricción de llave foránea
ADD CONSTRAINT fk_evaluaciones_periodos FOREIGN KEY (periodo_id) REFERENCES cat_periodos(id),
-- Y agregamos la columna nueva
ADD COLUMN calificacion_global DECIMAL(3,2) CHECK (calificacion_global >= 1 AND calificacion_global <= 5);

-- 3. Insertar periodo inicial para pruebas
INSERT INTO cat_periodos (id, nombre) VALUES (1, 'Anual 2025');

-- 4. Vincular evaluaciones existentes al periodo recién creado (Por si ya tenías datos)
UPDATE evaluaciones SET periodo_id = 1;