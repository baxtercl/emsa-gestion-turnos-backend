-- ============================================================
-- EMSA Gestion de Turnos - Datos Iniciales (Seed)
-- Version: 1.0
-- ============================================================

-- ============================================================
-- EMPRESAS
-- ============================================================

INSERT INTO empresas (nombre, rut, es_mandante, activo) VALUES
('EMSA (Exploraciones Mineras S.A.)', '76.100.200-K', TRUE, TRUE),
('Perforaciones Andinas SpA', '76.543.210-1', FALSE, TRUE),
('Servicios de Campamento Ltda', '77.888.999-2', FALSE, TRUE),
('Sondajes del Norte S.A.', '76.111.222-3', FALSE, TRUE),
('Logistica Minera SpA', '77.444.555-6', FALSE, TRUE);

-- ============================================================
-- USUARIOS (passwords hasheados con bcrypt - password = rol en minusculas)
-- En produccion usar passwords reales hasheados
-- Dominio EMSA: @em.codelco.cl | Contratistas: dominios independientes
-- ============================================================

-- Password 'admin' hasheado con bcrypt
INSERT INTO usuarios (id, username, email, password_hash, nombre_completo, rol, empresa_id, cargo, is_active) VALUES
(1, 'admin', 'admin@em.codelco.cl', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.JvR7n7G/1E1mGy', 'Administrador del Sistema', 'ADMIN', 1, 'Administrador', TRUE);

-- Password 'gestor' hasheado con bcrypt
INSERT INTO usuarios (id, username, email, password_hash, nombre_completo, rol, empresa_id, cargo, is_active) VALUES
(2, 'gestor', 'gestor@em.codelco.cl', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.JvR7n7G/1E1mGy', 'Maria Gonzalez', 'GESTOR_PROYECTOS', 1, 'Gestor de Proyectos', TRUE);

-- Password 'jefe' hasheado con bcrypt
INSERT INTO usuarios (id, username, email, password_hash, nombre_completo, rol, empresa_id, cargo, is_active) VALUES
(3, 'jefe', 'jefe@em.codelco.cl', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.JvR7n7G/1E1mGy', 'Carlos Rodriguez', 'JEFE_PROYECTO', 1, 'Jefe de Proyecto', TRUE);

-- Password 'contratista' hasheado con bcrypt (dominio independiente)
INSERT INTO usuarios (id, username, email, password_hash, nombre_completo, rol, empresa_id, cargo, is_active) VALUES
(4, 'contratista', 'contratista@perforaciones.cl', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.JvR7n7G/1E1mGy', 'Pedro Martinez', 'CONTRATISTA', 2, 'Administrador de Contrato', TRUE);

-- ============================================================
-- SERVICIOS
-- ============================================================

INSERT INTO servicios (nombre, descripcion, activo) VALUES
('Exploraciones', 'Exploraciones mineras y geologicas', TRUE),
('Perforacion y Sondajes', 'Sondajes diamantinos y RC', TRUE),
('Servicios de Campamento', 'Alimentacion, hospedaje y servicios generales', TRUE),
('Sondajes', 'Sondajes especializados', TRUE),
('Logistica y Transporte', 'Transporte de personal y materiales', TRUE),
('Mantenimiento', 'Mantenimiento de equipos y maquinaria', TRUE),
('Seguridad HSEC', 'Seguridad industrial y medio ambiente', TRUE);

-- ============================================================
-- PROYECTOS
-- ============================================================

INSERT INTO proyectos (nombre, descripcion, activo, fecha_inicio, fecha_fin) VALUES
('Proyecto Sierra Alta', 'Exploracion minera en zona norte', TRUE, '2024-01-01', '2025-12-31'),
('Proyecto Valle Verde', 'Exploracion en zona central', TRUE, '2024-03-01', '2025-06-30'),
('Proyecto Salar Blanco', 'Exploracion de litio', TRUE, '2024-06-01', '2026-12-31'),
('Proyecto Cerro Rojo', 'Proyecto finalizado', FALSE, '2023-01-01', '2024-12-31');

-- ============================================================
-- ASIGNACION DE JEFES DE PROYECTO
-- ============================================================

-- Asignar jefe (id=3) a proyectos 1 y 2
INSERT INTO usuarios_proyectos (usuario_id, proyecto_id) VALUES
(3, 1),
(3, 2);

-- ============================================================
-- CONTRATOS
-- ============================================================

-- Proyecto Sierra Alta
INSERT INTO contratos (proyecto_id, servicio_id, empresa_id, tipo_turnos, patron, activo, fecha_inicio) VALUES
(1, 2, 2, 'ABCD', '7x7', TRUE, '2024-01-01'),   -- Perforaciones Andinas - Perforacion
(1, 3, 3, 'ABCD', '7x7', TRUE, '2024-01-01'),   -- Servicios Campamento - Campamento
(1, 5, 5, 'AB', '5x2', TRUE, '2024-01-01');      -- Logistica Minera - Transporte

-- Proyecto Valle Verde
INSERT INTO contratos (proyecto_id, servicio_id, empresa_id, tipo_turnos, patron, activo, fecha_inicio) VALUES
(2, 2, 2, 'ABCD', '10x10', TRUE, '2024-03-01'), -- Perforaciones Andinas
(2, 4, 4, 'ABCD', '7x7', TRUE, '2024-03-01');    -- Sondajes del Norte

-- Proyecto Salar Blanco
INSERT INTO contratos (proyecto_id, servicio_id, empresa_id, tipo_turnos, patron, activo, fecha_inicio) VALUES
(3, 2, 2, 'ABCD', '14x14', TRUE, '2024-06-01'), -- Perforaciones Andinas
(3, 3, 3, 'ABCD', '14x14', TRUE, '2024-06-01'); -- Servicios Campamento

-- ============================================================
-- CARGOS
-- ============================================================

-- Cargos generales (jefaturas)
INSERT INTO cargos (nombre, proyecto_id, empresa_id, jefe_directo_id, nivel) VALUES
('Jefe de Faena', 1, 2, NULL, 'GERENCIA'),
('Administrador de Contrato', 1, 2, 1, 'JEFATURA'),
('Supervisor de Faena', 1, 2, 1, 'SUPERVISION'),
('Supervisor HSEC', 1, 2, 1, 'SUPERVISION');

-- Cargos operativos
INSERT INTO cargos (nombre, proyecto_id, empresa_id, jefe_directo_id, nivel) VALUES
('Perforista de Sondaje', 1, 2, 3, 'OPERATIVO'),
('Ayudante de Sondaje', 1, 2, 3, 'OPERATIVO'),
('Operador de Sondaje', 1, 2, 3, 'OPERATIVO'),
('Chofer de Sondaje', 1, 2, 3, 'OPERATIVO'),
('Mecanico', 1, 2, 3, 'OPERATIVO'),
('Prevencionista de Riesgos', 1, 2, 4, 'OPERATIVO');

-- Cargos de campamento
INSERT INTO cargos (nombre, proyecto_id, empresa_id, jefe_directo_id, nivel) VALUES
('Jefe de Campamento', 1, 3, NULL, 'JEFATURA'),
('Chef', 1, 3, 11, 'OPERATIVO'),
('Ayudante de Cocina', 1, 3, 11, 'OPERATIVO'),
('Campamentero', 1, 3, 11, 'OPERATIVO');

-- ============================================================
-- FIN DEL SCRIPT
-- ============================================================
