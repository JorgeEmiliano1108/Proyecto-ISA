-- ==========================================
-- SEED: USUARIOS DE PRUEBA (JERARQUÍA COMPLETA)
-- ==========================================

/*
-- 1. DIRECTOR (Nivel más alto, no tiene jefe en este flujo)
INSERT INTO usuarios (id, username, rol_id, departamento_id, manager_id) 
VALUES ('d1111111-1111-1111-1111-111111111111', 'director.sistemas', 3, 1, NULL);
*/
-- 2. GERENTE (Su jefe es el Director 'd1111111...')
-- (Cambiamos la 'g' por 'b' para que sea un Hexadecimal válido)
INSERT INTO usuarios (id, username, rol_id, departamento_id, manager_id) 
VALUES ('b2222222-2222-2222-2222-222222222222', 'gerente.sistemas', 2, 1, 'd1111111-1111-1111-1111-111111111111');

-- 3. COORDINADOR A (Su jefe es el Gerente 'b2222222...')
INSERT INTO usuarios (id, username, rol_id, departamento_id, manager_id) 
VALUES ('c3333333-3333-3333-3333-333333333333', 'coordinador.dev', 1, 1, 'b2222222-2222-2222-2222-222222222222');

-- 4. COORDINADOR B (Su jefe también es el Gerente 'b2222222...')
INSERT INTO usuarios (id, username, rol_id, departamento_id, manager_id) 
VALUES ('c4444444-4444-4444-4444-444444444444', 'coordinador.soporte', 1, 1, 'b2222222-2222-2222-2222-222222222222');
/*
-- 5. CONTRALORÍA (Auditor global, pertenece a Finanzas, no se evalúa en este flujo)
INSERT INTO usuarios (id, username, rol_id, departamento_id, manager_id) 
VALUES ('a5555555-5555-5555-5555-555555555555', 'admin.contraloria', 4, 2, NULL);
*/

-- 1. Insertar el Rol de Administrador
INSERT INTO cat_roles (nombre, nivel_aprobacion, activo) 
VALUES ('Administrador', 1, true)
ON CONFLICT DO NOTHING;

-- 2. Insertar el Departamento de Sistemas
INSERT INTO cat_departamentos (nombre, activo) 
VALUES ('Sistemas', true)
ON CONFLICT DO NOTHING;

-- 3. Insertar el Usuario Administrador
-- Nota: El hash corresponde a la contraseña "admin123" 
-- compatible con el algoritmo PBKDF2 de Django.
INSERT INTO usuarios (
    username, 
    password_hash, 
    nombres, 
    apellido_paterno, 
    apellido_materno, 
    puesto, 
    rol_id, 
    departamento_id, 
    activo, 
    fecha_registro
) 
VALUES (
    'admin', 
    'pbkdf2_sha256$720000$vY8v7Y6qZ9X8$E3p5hR4tY2u1I9o8P7a6S5d4F3g2H1j0K9l8M7n6B5v4=', 
    'Admin', 
    'Sistema', 
    'ISA', 
    'Gerente de TI', 
    (SELECT id FROM cat_roles WHERE nombre = 'Administrador' LIMIT 1), 
    (SELECT id FROM cat_departamentos WHERE nombre = 'Sistemas' LIMIT 1), 
    true, 
    NOW()
)
ON CONFLICT (username) DO NOTHING;