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