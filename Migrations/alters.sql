-- Añadir la columna password_hash a la tabla de usuarios existente
ALTER TABLE usuarios 
ADD COLUMN password_hash TEXT NOT NULL DEFAULT 'remplazar_por_hash_real';

-- Una vez añadida, se recomienda quitar el valor por defecto para futuros registros
ALTER TABLE usuarios 
ALTER COLUMN password_hash DROP DEFAULT;

-- Limpiar los valores por defecto para futuros registros
ALTER TABLE usuarios ALTER COLUMN nombres DROP DEFAULT;
ALTER TABLE usuarios ALTER COLUMN apellido_paterno DROP DEFAULT;
ALTER TABLE usuarios 
ADD COLUMN puesto VARCHAR(100);

-- 1. Ajuste del campo de contraseña para compatibilidad nativa con Django
ALTER TABLE usuarios RENAME COLUMN password_hash TO password;
ALTER TABLE usuarios ALTER COLUMN password TYPE VARCHAR(128);
ALTER TABLE usuarios ALTER COLUMN password DROP NOT NULL; -- Para permitir el JIT Provisioning sin choques

-- 2. Agregar las columnas espejo del sistema SIARE (Active Directory)
ALTER TABLE usuarios ADD COLUMN id_siare INT UNIQUE;         -- Mapea: idPersonaEmpleado
ALTER TABLE usuarios ADD COLUMN id_area_siare INT;           -- Mapea: idArea
ALTER TABLE usuarios ADD COLUMN id_puesto_siare INT;         -- Mapea: idPuesto

-- 3. (Opcional pero recomendado) Revertir la separación de nombres para coincidir con la API
ALTER TABLE usuarios DROP COLUMN nombres;
ALTER TABLE usuarios DROP COLUMN apellido_paterno;
ALTER TABLE usuarios DROP COLUMN apellido_materno;
ALTER TABLE usuarios ADD COLUMN nombre_completo VARCHAR(255);

--4

alter table usuarios rename column id_siare to id_presona_empleado;