-- ============================================================
-- EMSA Gestion de Turnos - Esquema de Base de Datos
-- Version: 1.0
-- Base de datos: PostgreSQL 14+
-- ============================================================

-- Eliminar tablas existentes (en orden inverso por dependencias)
DROP TABLE IF EXISTS asignaciones CASCADE;
DROP TABLE IF EXISTS requerimientos CASCADE;
DROP TABLE IF EXISTS ciclos CASCADE;
DROP TABLE IF EXISTS trabajadores CASCADE;
DROP TABLE IF EXISTS cargos CASCADE;
DROP TABLE IF EXISTS contratos CASCADE;
DROP TABLE IF EXISTS servicios CASCADE;
DROP TABLE IF EXISTS usuarios_proyectos CASCADE;
DROP TABLE IF EXISTS proyectos CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;
DROP TABLE IF EXISTS empresas CASCADE;
DROP TYPE IF EXISTS rol_usuario CASCADE;
DROP TYPE IF EXISTS estado_ciclo CASCADE;
DROP TYPE IF EXISTS tipo_turnos CASCADE;

-- ============================================================
-- TIPOS ENUM
-- ============================================================

-- Roles de usuario del sistema
CREATE TYPE rol_usuario AS ENUM (
    'ADMIN',
    'GESTOR_PROYECTOS',
    'JEFE_PROYECTO',
    'CONTRATISTA'
);

-- Estados de ciclo
CREATE TYPE estado_ciclo AS ENUM (
    'NO_DEFINIDO',
    'INCOMPLETO',
    'COMPLETO'
);

-- Tipos de turnos
CREATE TYPE tipo_turnos AS ENUM (
    'AB',
    'ABCD'
);

-- ============================================================
-- TABLAS
-- ============================================================

-- Empresas (Mandante y Contratistas)
CREATE TABLE empresas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    rut VARCHAR(12) UNIQUE NOT NULL,
    es_mandante BOOLEAN DEFAULT FALSE,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Usuarios del sistema
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(200),
    rol rol_usuario NOT NULL DEFAULT 'CONTRATISTA',
    empresa_id INTEGER REFERENCES empresas(id) ON DELETE SET NULL,
    cargo VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Proyectos
CREATE TABLE proyectos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Asignacion de Jefes de Proyecto
CREATE TABLE usuarios_proyectos (
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    proyecto_id INTEGER REFERENCES proyectos(id) ON DELETE CASCADE,
    fecha_asignacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (usuario_id, proyecto_id)
);

-- Servicios
CREATE TABLE servicios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Contratos
CREATE TABLE contratos (
    id SERIAL PRIMARY KEY,
    proyecto_id INTEGER NOT NULL REFERENCES proyectos(id) ON DELETE CASCADE,
    servicio_id INTEGER NOT NULL REFERENCES servicios(id) ON DELETE RESTRICT,
    empresa_id INTEGER NOT NULL REFERENCES empresas(id) ON DELETE RESTRICT,
    tipo_turnos tipo_turnos NOT NULL DEFAULT 'ABCD',
    patron VARCHAR(10) NOT NULL DEFAULT '7x7',
    activo BOOLEAN DEFAULT TRUE,
    fecha_inicio DATE,
    fecha_fin DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_contrato UNIQUE (proyecto_id, servicio_id, empresa_id)
);

-- Cargos
CREATE TABLE cargos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    proyecto_id INTEGER REFERENCES proyectos(id) ON DELETE CASCADE,
    empresa_id INTEGER REFERENCES empresas(id) ON DELETE CASCADE,
    jefe_directo_id INTEGER REFERENCES cargos(id) ON DELETE SET NULL,
    nivel VARCHAR(20) DEFAULT 'OPERATIVO',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Trabajadores
CREATE TABLE trabajadores (
    id SERIAL PRIMARY KEY,
    rut VARCHAR(12) UNIQUE NOT NULL,
    nombres VARCHAR(200) NOT NULL,
    apellidos VARCHAR(200) NOT NULL,
    email VARCHAR(200),
    telefono VARCHAR(20),
    proyecto_id INTEGER REFERENCES proyectos(id) ON DELETE SET NULL,
    empresa_id INTEGER NOT NULL REFERENCES empresas(id) ON DELETE RESTRICT,
    cargo_id INTEGER REFERENCES cargos(id) ON DELETE SET NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_ingreso DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Ciclos (Turnos)
CREATE TABLE ciclos (
    id SERIAL PRIMARY KEY,
    contrato_id INTEGER NOT NULL REFERENCES contratos(id) ON DELETE CASCADE,
    letra CHAR(1) NOT NULL CHECK (letra IN ('A', 'B', 'C', 'D')),
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    estado estado_ciclo DEFAULT 'NO_DEFINIDO',
    horario VARCHAR(10) DEFAULT 'DIA',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_fechas CHECK (fecha_fin >= fecha_inicio)
);

-- Requerimientos
CREATE TABLE requerimientos (
    id SERIAL PRIMARY KEY,
    ciclo_id INTEGER NOT NULL REFERENCES ciclos(id) ON DELETE CASCADE,
    cargo_id INTEGER NOT NULL REFERENCES cargos(id) ON DELETE CASCADE,
    cantidad_necesaria INTEGER NOT NULL DEFAULT 1 CHECK (cantidad_necesaria > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_requerimiento UNIQUE (ciclo_id, cargo_id)
);

-- Asignaciones
CREATE TABLE asignaciones (
    id SERIAL PRIMARY KEY,
    ciclo_id INTEGER NOT NULL REFERENCES ciclos(id) ON DELETE CASCADE,
    trabajador_id INTEGER NOT NULL REFERENCES trabajadores(id) ON DELETE CASCADE,
    fecha_asignacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_asignacion UNIQUE (ciclo_id, trabajador_id)
);

-- ============================================================
-- INDICES
-- ============================================================

-- Usuarios
CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_empresa ON usuarios(empresa_id);
CREATE INDEX idx_usuarios_rol ON usuarios(rol);
CREATE INDEX idx_usuarios_activo ON usuarios(is_active);

-- Proyectos
CREATE INDEX idx_proyectos_activo ON proyectos(activo);
CREATE INDEX idx_proyectos_fechas ON proyectos(fecha_inicio, fecha_fin);

-- Contratos
CREATE INDEX idx_contratos_proyecto ON contratos(proyecto_id);
CREATE INDEX idx_contratos_empresa ON contratos(empresa_id);
CREATE INDEX idx_contratos_activo ON contratos(activo);

-- Trabajadores
CREATE INDEX idx_trabajadores_rut ON trabajadores(rut);
CREATE INDEX idx_trabajadores_empresa ON trabajadores(empresa_id);
CREATE INDEX idx_trabajadores_proyecto ON trabajadores(proyecto_id);
CREATE INDEX idx_trabajadores_activo ON trabajadores(activo);

-- Ciclos
CREATE INDEX idx_ciclos_contrato ON ciclos(contrato_id);
CREATE INDEX idx_ciclos_fechas ON ciclos(fecha_inicio, fecha_fin);
CREATE INDEX idx_ciclos_estado ON ciclos(estado);

-- Asignaciones
CREATE INDEX idx_asignaciones_ciclo ON asignaciones(ciclo_id);
CREATE INDEX idx_asignaciones_trabajador ON asignaciones(trabajador_id);

-- ============================================================
-- FUNCIONES Y TRIGGERS
-- ============================================================

-- Funcion para actualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para updated_at
CREATE TRIGGER update_empresas_updated_at BEFORE UPDATE ON empresas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_proyectos_updated_at BEFORE UPDATE ON proyectos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contratos_updated_at BEFORE UPDATE ON contratos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cargos_updated_at BEFORE UPDATE ON cargos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_trabajadores_updated_at BEFORE UPDATE ON trabajadores
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ciclos_updated_at BEFORE UPDATE ON ciclos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_requerimientos_updated_at BEFORE UPDATE ON requerimientos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- VISTAS
-- ============================================================

-- Vista de cobertura de ciclos
CREATE OR REPLACE VIEW v_cobertura_ciclos AS
SELECT
    c.id AS ciclo_id,
    c.contrato_id,
    c.letra,
    c.fecha_inicio,
    c.fecha_fin,
    c.estado,
    COALESCE(SUM(r.cantidad_necesaria), 0) AS requeridos,
    COUNT(DISTINCT a.trabajador_id) AS asignados,
    CASE
        WHEN COALESCE(SUM(r.cantidad_necesaria), 0) = 0 THEN 0
        ELSE ROUND((COUNT(DISTINCT a.trabajador_id)::DECIMAL / SUM(r.cantidad_necesaria)) * 100, 2)
    END AS porcentaje_cobertura
FROM ciclos c
LEFT JOIN requerimientos r ON c.id = r.ciclo_id
LEFT JOIN asignaciones a ON c.id = a.ciclo_id
GROUP BY c.id, c.contrato_id, c.letra, c.fecha_inicio, c.fecha_fin, c.estado;

-- Vista de dotacion por proyecto
CREATE OR REPLACE VIEW v_dotacion_proyecto AS
SELECT
    p.id AS proyecto_id,
    p.nombre AS proyecto_nombre,
    e.id AS empresa_id,
    e.nombre AS empresa_nombre,
    COUNT(t.id) AS total_trabajadores,
    COUNT(CASE WHEN t.activo THEN 1 END) AS trabajadores_activos
FROM proyectos p
LEFT JOIN contratos c ON p.id = c.proyecto_id
LEFT JOIN empresas e ON c.empresa_id = e.id
LEFT JOIN trabajadores t ON t.empresa_id = e.id AND t.proyecto_id = p.id
GROUP BY p.id, p.nombre, e.id, e.nombre;

-- ============================================================
-- FIN DEL SCRIPT
-- ============================================================
