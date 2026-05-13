INSERT INTO cat_roles (id, nombre, nivel_aprobacion, activo) VALUES (1, 'RRHH', 1, true) ON CONFLICT (id) DO NOTHING;
INSERT INTO cat_departamentos (id, nombre, activo) VALUES (1, 'Recursos Humanos', true) ON CONFLICT (id) DO NOTHING;

INSERT INTO usuarios (id, username, rol_id, departamento_id) 
VALUES ('11111111-1111-1111-1111-111111111111', 'user_99', 1, 1) ON CONFLICT (id) DO NOTHING;
INSERT INTO usuarios (id, username, rol_id, departamento_id) 
VALUES ('22222222-2222-2222-2222-222222222222', 'evaluador', 1, 1) ON CONFLICT (id) DO NOTHING;

INSERT INTO evaluaciones (id, evaluado_id, evaluador_id, periodo_id, estado)
VALUES ('c6a84c56-6a56-4b56-8a56-06a56a56a56a', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', 1, 'DRAFT')
ON CONFLICT (id) DO NOTHING;
