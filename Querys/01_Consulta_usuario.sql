SELECT 
    e.username AS empleado, 
    r.nombre AS rol, 
    d.nombre AS departamento,
    j.username AS jefe_inmediato
FROM usuarios e
JOIN cat_roles r ON e.rol_id = r.id
JOIN cat_departamentos d ON e.departamento_id = d.id
LEFT JOIN usuarios j ON e.manager_id = j.id;

select * from usuarios;
select * from evaluaciones;
