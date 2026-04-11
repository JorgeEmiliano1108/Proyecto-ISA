# Proyecto-ISA
Sistema de Evaluación Discrecional (SED) - ISA Corporativo
📌 Descripción del Proyecto
El SED es una solución web interna diseñada para modernizar el proceso anual de evaluación de desempeño de ISA Corporativo. Este sistema reemplaza el flujo tradicional basado en archivos Excel y firmas físicas por un Ecosistema Digital de Firmas, centralizando la captura de objetivos, el cálculo de bonos (EBITDA) y la trazabilidad operativa.

🚀 Tecnologías Principales
Backend as a Service (BaaS): Supabase

Base de Datos: PostgreSQL 15

Gestión de Datos: DBeaver

Firma Digital: Canvas API (Codificación Base64)

🏗️ Arquitectura de Datos
El sistema se basa en un modelo relacional de 12 tablas diseñado para la integridad y el no-repudio de la información:

Catálogos: cat_roles, cat_departamentos, cat_competencias, cat_periodos.

Seguridad: usuarios (con jerarquía recursiva manager_id).

Transaccional: evaluaciones, objetivos, calificaciones_competencias, aprobaciones.

Auditoría: historial_estados, logs_sistema.

Finanzas: bonos (implementando lógica de Snapshot financiero).

⚙️ Reglas de Negocio Clave
1. Máquina de Estados
El flujo de una evaluación es estricto y unidireccional (salvo rechazos):
DRAFT ➔ SUBMITTED ➔ PENDING_APPROVAL ➔ APPROVED ➔ CLOSED

2. Firma Electrónica Simple
Se captura el trazo del usuario mediante un Canvas y se almacena como una cadena Base64 directamente en la base de datos, vinculada a la IP y el Timestamp del servidor para garantizar la validez técnica.

3. Lógica de Bonos
Los cálculos financieros se protegen mediante un "Snapshot". Al momento de la aprobación, se congela el salario base y el impacto EBITDA logrados para evitar alteraciones por cambios salariales posteriores al cierre.

📁 Estructura del Repositorio de Datos
Bash
├── scripts/
│   ├── V1.0.0_crear_tablas_base.sql   # Definición de esquema (DDL)
│   ├── 01_insertar_catalogos.sql     # Datos maestros iniciales
│   └── 02_insertar_usuarios.sql      # Carga de jerarquía de prueba
├── docs/
│   ├── diagrama_er.png               # Diagrama Entidad-Relación
│   └── diccionario_datos.csv         # Especificación técnica de campos
└── README.md
🛠️ Instalación y Configuración
Crear un proyecto en Supabase.

Conectar vía DBeaver utilizando las credenciales proporcionadas en el Dashboard de Supabase.

Ejecutar el script scripts/V1.0.0_crear_tablas_base.sql.

Poblar el sistema ejecutando los archivos de seed en orden numérico.
