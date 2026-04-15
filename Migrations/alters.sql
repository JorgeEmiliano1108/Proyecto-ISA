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