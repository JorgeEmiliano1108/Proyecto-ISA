# ISA Corporativo — Sistema de Gestión Empresarial

Sistema frontend de gestión empresarial para **ISA Corporativo**, desarrollado como una **Multi-Page Application (MPA)** estática con **JavaScript Vanilla**, **Bootstrap 5** y datos simulados. Permite administrar evaluaciones de desempeño, bonos, usuarios, reportes, aprobaciones y más, con una arquitectura preparada para consumir una API REST.

---

## Requisitos del sistema

- Servidor HTTP estático (Python, Node, PHP, etc.)
- Navegador moderno con soporte para ES6+
- Conexión a internet (para librerías CDN)

> **NO** abrir `index.html` directamente en el navegador. Las rutas relativas se rompen. Usar siempre un servidor HTTP.

```bash
python -m http.server 8000 -d frontend
npx serve frontend
php -S localhost:8000 -t frontend
```

---

## Estructura del proyecto

```
Proyecto-ISA/
├── AGENTS.md                          # Documentación técnica para asistentes IA
├── Evaluacion Discrecional 2025.xlsx  # Plantilla de evaluación de desempeño (referencia)
├── README.md                          # Este archivo
├── requisitos.txt                     # Requisitos funcionales y no funcionales
└── frontend/
    ├── index.html                     # Entrypoint — pantalla de login
    ├── css/
    │   └── styles.css                 # Variables CSS globales y clases base
    └── src/
        ├── components/
        │   ├── grilla-evaluacion/
        │   │   ├── grilla-evaluacion.css   # Estilos de la grilla de evaluación
        │   │   └── grilla-evaluacion.js    # GrillaISA (editable) y GrillaSupervisor (solo lectura) con Handsontable
        │   └── layout/
        │       ├── layout.css              # Sidebar colapsable + topbar + contenido dinámico
        │       ├── layout.html             # Template HTML (no usado en producción)
        │       ├── layout.js               # Inyección del layout, auth guard, navegación por rol
        │       ├── modal-consulta.js        # Sistema de consultas/ayuda del usuario
        │       ├── modal-notificaciones.js  # Sistema de notificaciones (tareas y comunicados)
        │       └── modal-perfil.js          # Modal de perfil de usuario
        ├── pages/
        │   ├── login/
        │   │   ├── login.css               # Estilos del login con split-card y animaciones
        │   │   └── login.js                # Autenticación JWT, color picker, redirección por rol
        │   ├── admin/                      # Páginas para rol Administrador
        │   │   ├── aprobaciones/           # Solicitudes pendientes (evaluaciones, bonos, accesos)
        │   │   ├── bonos/                  # Programas de incentivos y asignación a empleados
        │   │   ├── catalogos/              # Categorías maestras y estructura del menú
        │   │   ├── configuracion/          # Personalización del color primario del sistema
        │   │   ├── consultas/              # Aclaraciones: responder consultas y enviar notificaciones
        │   │   ├── dashboard/              # Panel con KPIs, actividad reciente y tareas
        │   │   ├── evaluaciones/           # Constructor de evaluaciones + supervisión con grilla
        │   │   ├── reportes/               # Analítica con gráficas (Chart.js) y tabla de registros
        │   │   └── usuarios/               # CRUD de usuarios con tabla y modal
        │   └── usuario/                    # Páginas para rol Usuario
        │       ├── bonos/                  # Mis incentivos, metas vinculadas e historial de pagos
        │       ├── dashboard/              # Resumen personal con KPIs y tabla de evaluaciones
        │       ├── evaluaciones/           # Evaluaciones pendientes + historial + grilla interactiva
        │       └── reportes/               # Gráficas de tendencia y competencias (Chart.js)
        └── services/
            └── microsoft-graph.js          # Integración con Microsoft Graph API (MSAL) para Excel
```

---

## Descripción por módulo

### Login (`index.html` + `login.js` + `login.css`)
Pantalla de inicio de sesión con split-card: lado izquierdo con la marca "ISA CORPORATIVO" sobre fondo degradado, lado derecho con formulario de usuario/contraseña. Incluye un selector de color que persiste en `localStorage` y se aplica en vivo al tema completo. La autenticación se realiza contra `POST /auth/login/`, decodifica el JWT para extraer el rol y redirige al dashboard correspondiente.

### Layout (`layout.js` + `layout.css`)
Inyecta sidebar + topbar en todas las páginas protegidas. Verifica la existencia de `userData` y tokens JWT en `localStorage`; si expiraron, intenta refrescarlos automáticamente. El sidebar se muestra colapsado (80px) y se expande (260px) al hacer hover. Los enlaces cambian según el rol: **admin** ve 9 secciones, **usuario** ve 4. Incluye dropdown de usuario con "Mi Perfil" y "Cerrar Sesión", notificaciones y centro de ayuda.

### Grilla de Evaluación (`grilla-evaluacion.js` + `grilla-evaluacion.css`)
Componente central para las evaluaciones de desempeño. Contiene dos clases:
- **`GrillaISA`** — Formulario interactivo con datos del colaborador/evaluador/jefe, 6 competencias evaluadas con radios del 1 al 5 (cada nivel con un color distinto), campos de texto para resultados y compromisos, evaluación global, comentarios y firmas. Se integra con Microsoft Graph API para leer y escribir directamente en un archivo Excel de OneDrive.
- **`GrillaSupervisor`** — Tabla de solo lectura implementada con **Handsontable** que lista a todos los usuarios con sus puntuaciones, promedios, estado (Borrador/En Proceso/Completado) y acciones. Incluye filtros y búsqueda.

### Sistema de Notificaciones (`modal-notificaciones.js`)
CRUD completo en `localStorage` bajo la clave `isa_notificaciones`. Las notificaciones pueden ser de tipo **tarea** o **comunicado**, con fecha límite opcional. Se muestran en un dropdown desde el topbar con badge de conteo de no leídas. El administrador puede crear notificaciones desde la página de Aclaraciones.

### Sistema de Consultas (`modal-consulta.js`)
Permite a los usuarios enviar dudas al administrador y consultar las respuestas. Persiste en `localStorage` clave `isa_consultas`. El administrador ve un badge con el conteo de pendientes y puede responder desde la página de Aclaraciones.

### Perfil de Usuario (`modal-perfil.js`)
Modal para editar nombre, email (solo lectura), teléfono, departamento y puesto. Guarda en `localStorage` clave `isa_perfil` y mantiene sincronizado `userData.nombre`.

### Dashboard Admin (`admin/dashboard/`)
Panel con 4 indicadores clave (Total Usuarios, Evaluaciones, Pendientes, Bonos), lista de actividad reciente y próximas tareas. Los datos son simulados pero la estructura está lista para consumir una API.

### Usuarios Admin (`admin/usuarios/`)
CRUD completo con tabla paginada, filtro en tiempo real por nombre/email y modal para crear o editar usuarios (nombre, email, rol, departamento). Incluye KPIs de personal, exportación simulada y eliminación con confirmación.

### Catálogos Admin (`admin/catalogos/`)
Gestión de categorías maestras y estructura del menú de navegación. Renderiza un árbol con items y subitems, cada uno con su estado (VISIBLE/BLOQUEADO/OCULTO). Incluye gráfica de uso de navegación con Chart.js y registro de actividad.

### Evaluaciones Admin (`admin/evaluaciones/`)
Constructor de evaluaciones con definición (título, descripción, audiencia) y criterios dinámicos de tres tipos: Opción Múltiple, Escala Lineal y Texto Largo. Incluye un modal de supervisión que usa `GrillaSupervisor` para visualizar todas las evaluaciones en una tabla interactiva con filtros.

### Aprobaciones Admin (`admin/aprobaciones/`)
Listado unificado de solicitudes pendientes clasificadas por tipo (Evaluación, Bono, Actualización de Acceso). Panel lateral de "Revisión Rápida" con detalle de la solicitud seleccionada, botones para aprobar o rechazar (con confirmación y simulación de red), y tabla de historial con estado Aprobado/Rechazado.

### Reportes Admin (`admin/reportes/`)
Panel de analítica con KPIs, selector de temporalidad (30 días / Trimestral / Anual), gráfica de tendencias (líneas), gráfica de eficiencia por departamento (barras) y tabla de registros detallados. Todo implementado con Chart.js.

### Bonos Admin (`admin/bonos/`)
Gestión de programas de incentivos con cards de resumen (Multiplicador de Desempeño, Hito de Retención), flujo de caja, tabla de asignación de empleados con barra de progreso y pago potencial. Incluye modal de detalle del programa y modal para crear nuevos programas.

### Consultas/Aclaraciones Admin (`admin/consultas/`)
Doble pestaña: **Consultas** (con sub-pestañas Pendientes y Respondidas) y **Notificaciones** (formulario de envío + historial). Permite responder consultas, exportar a CSV, eliminar, y enviar notificaciones tipo tarea o comunicado con fecha límite.

### Configuración Admin (`admin/configuracion/`)
Selector de color primario que se aplica en vivo a toda la plataforma y persiste en `localStorage` clave `isaThemeColor`.

### Dashboard Usuario (`usuario/dashboard/`)
Resumen personal con KPIs (Mi Promedio, Evaluaciones Pendientes, Bono Acumulado), tabla de las últimas evaluaciones y lista de próximas tareas con prioridad.

### Evaluaciones Usuario (`usuario/evaluaciones/`)
Evaluaciones pendientes por completar (cards con categoría y fecha límite), historial de evaluaciones anteriores, y botón para abrir la **Evaluación Discrecional 2025** en un modal que carga `GrillaISA` con conexión a OneDrive mediante Microsoft Graph API.

### Bonos Usuario (`usuario/bonos/`)
Progreso del ciclo actual con barra animada, monto proyectado, metas vinculadas con indicador meta vs actual, e historial de pagos recibidos.

### Reportes Usuario (`usuario/reportes/`)
Dos gráficas con Chart.js: línea de tendencia personal (evolución de puntuación en el tiempo) y radar de competencias (Técnica, Cultura, Liderazgo, Soft Skills, Puntualidad). Tabla de reportes generados con botón de descarga PDF (simulada).

### Microsoft Graph Service (`services/microsoft-graph.js`)
Servicio de integración con **Microsoft Graph API** usando MSAL.js. Permite autenticación mediante popup de Microsoft, obtener token de acceso, y leer/escribir rangos en archivos Excel almacenados en OneDrive. Es utilizado por `GrillaISA` para persistir las evaluaciones de desempeño directamente en un libro de Excel.

---

## Roles del sistema

| Rol | Rutas disponibles |
|-----|-------------------|
| **admin** | Dashboard, Usuarios, Catálogos, Evaluaciones, Aprobaciones, Reportes, Bonos, Configuración, Aclaraciones |
| **usuario** | Mi Resumen, Mis Evaluaciones, Mis Bonos, Mis Reportes |

---

## Stack tecnológico

| Tecnología | Versión | Uso |
|------------|---------|-----|
| Bootstrap 5 | 5.3.0 | UI framework (CSS + JS bundle) |
| Bootstrap Icons | 1.11.3 | Iconos vectoriales |
| Google Fonts (Inter) | - | Tipografía del login |
| Handsontable | última | Grilla de supervisión de evaluaciones |
| Chart.js | última | Gráficas en reportes y catálogos |
| MSAL.js | 3.0.0 | Autenticación Microsoft Graph |
| JavaScript Vanilla | ES6+ | Lógica de negocio (patrón MVC ligero) |

No hay `package.json`, ni npm, ni paso de compilación. Todo se sirve como archivos estáticos.

---

## Arquitectura de datos

Actualmente el sistema usa datos simulados (mock) almacenados directamente en los archivos JavaScript de cada módulo. Todos los `fetch()` están comentados y listos para ser reemplazados por llamadas reales a `http://localhost:8000/api/v1`.

### Persistencia en `localStorage`

| Clave | Contenido | Módulo |
|-------|-----------|--------|
| `userData` | Usuario autenticado (nombre, rol, username, user_id) | login.js, layout.js |
| `access_token` | Token JWT de acceso | login.js, layout.js |
| `refresh_token` | Token JWT de refresco | login.js, layout.js |
| `isaThemeColor` | Color primario personalizado | login.js, configuracion.js |
| `isa_perfil` | Perfil del usuario (nombre, email, teléfono, etc.) | modal-perfil.js |
| `isa_notificaciones` | Notificaciones del sistema | modal-notificaciones.js |
| `isa_consultas` | Consultas de usuarios | modal-consulta.js, consultas.js |
| `isa_evaluacion_*` | Datos de grilla de evaluación | grilla-evaluacion.js |

---

## Convenciones de código

- Patrón **MVC ligero**: cada página tiene un Service (modelo), funciones `render*()` (vista) y un `DOMContentLoaded` (controlador)
- Variables CSS para personalización de tema (`--primary-color`)
- Sidebar colapsado por defecto que se expande al hover mediante CSS puro (`body:has()`)
- Bootstrap 5 para layout responsivo
- Funciones globales expuestas en `window` para componentes compartidos
- Datos mock con comentarios indicando la llamada API futura

---

## Primeros pasos

1. Iniciar sesión con cualquier usuario (admin/admin para rol administrador)
2. Explorar el sidebar según el rol asignado
3. Para limpiar datos de prueba: `localStorage.clear()` en consola y recargar
