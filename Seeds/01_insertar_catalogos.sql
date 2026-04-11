-- ==========================================
-- SEED: CATÁLOGOS BASE
-- ==========================================

-- 1. Insertar Roles (Los 4 definidos en el Backlog)
INSERT INTO cat_roles (id, nombre, nivel_aprobacion) VALUES
(1, 'Coordinador', 0),
(2, 'Gerente', 1),
(3, 'Director', 2),
(4, 'Contraloría', 99);

-- 2. Insertar Departamentos
INSERT INTO cat_departamentos (id, nombre) VALUES
(1, 'Sistemas'),
(2, 'Finanzas'),
(3, 'Operaciones');

-- 3. Insertar las 6 Competencias exactas del formato Excel
INSERT INTO cat_competencias (id, nombre, descripcion) VALUES
(1, 'Orientación al cliente', 'Disponibilidad y Flexibilidad'),
(2, 'Enfoque a resultados', 'Identificar las prioridades'),
(3, 'Confiabilidad', 'Capacidad para adaptarse y Disponibilidad'),
(4, 'Trabajo en equipo', 'Apoyo a compañeros y Flexibilidad para tomar nuevas tareas'),
(5, 'Innovación y desarrollo', 'Propuestas de mejoras'),
(6, 'Liderazgo', 'Capacidad de llevar adelante proyectos e iniciativas y motivar a su equipo');