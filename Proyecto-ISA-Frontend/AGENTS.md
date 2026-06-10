# AGENTS — ISA Frontend (Static MPA)

## Estructura del proyecto

```
Proyecto-ISA/
├── AGENTS.md
├── README.md
├── requisitos.txt                  # Requisitos funcionales y no funcionales
├── .gitignore
└── frontend/
    ├── index.html                  # Login (único entrypoint)
    ├── css/
    │   └── styles.css              # Variables CSS globales y clases base
    └── src/
        ├── components/
        │   ├── layout/
        │   │   ├── layout.js       # Sidebar + topbar + auth guard
        │   │   ├── layout.css      # Estilos del layout completo
        │   │   ├── layout.html     # Template (no usado en producción)
        │   │   ├── modal-perfil.js # Modal de perfil de usuario
        │   │   ├── modal-notificaciones.js  # Sistema de notificaciones
        │   │   └── modal-consulta.js        # Sistema de consultas/ayuda
        │   └── grilla-evaluacion/
        │       ├── grilla-evaluacion.js     # Clases GrillaISA y GrillaSupervisor (Handsontable)
        │       └── grilla-evaluacion.css    # Estilos de la grilla
        └── pages/
            ├── login/
            │   ├── login.js        # Lógica de autenticación simulada
            │   └── login.css       # Estilos del login
            ├── admin/              # Páginas para rol admin
            │   ├── dashboard/      # Dashboard con KPI cards
            │   ├── usuarios/       # CRUD de usuarios con tabla y modal
            │   ├── catalogos/      # Gestión de catálogos y menú de navegación
            │   ├── evaluaciones/   # Diseño de evaluaciones + supervisión
            │   ├── aprobaciones/   # Solicitudes pendientes (evaluaciones, bonos, accesos)
            │   ├── reportes/       # Analítica con gráficas (Chart.js), KPI y tabla
            │   ├── bonos/          # Arquitectura de incentivos con programas y asignación
            │   └── consultas/      # Aclaraciones: responde consultas, envía notificaciones
            └── usuario/            # Páginas para rol usuario
                ├── dashboard/      # Resumen personal con KPI y tabla de evaluaciones
                ├── evaluaciones/   # Mis evaluaciones pendientes + historial + grilla interactiva
                ├── bonos/          # Incentivos, metas vinculadas e historial de pagos
                └── reportes/       # Reportes con gráficas de tendencia y competencias
```

## Visión general

Aplicación **Multi-Page Application (MPA)** estática hecha con **Vanilla JS**, **Bootstrap 5** (CDN) y datos simulados en `localStorage`. No hay backend real — todos los `fetch()` están comentados. El proyecto está diseñado como frontend puro listo para integrarse con una API REST en el futuro.

## Ejecución local

Servir la carpeta `frontend` con cualquier servidor HTTP estático. NO abrir `index.html` directamente (las rutas relativas se rompen).

```bash
python -m http.server 8000 -d frontend
# O con Node: npx serve frontend
# O con PHP: php -S localhost:8000 -t frontend
```

## Sistema de autenticación (simulado)

- El entrypoint es `frontend/index.html` → carga `login.js`
- `login.js` guarda en `localStorage` bajo la clave `userData`:
  ```json
  { "nombre": "admin", "rol": "admin" }
  ```
- El rol es `'admin'` solo si el usuario ingresa exactamente `admin`. Cualquier otro nombre de usuario asigna `'usuario'`.
- El campo de contraseña es **decorativo**: solo se valida el nombre de usuario.
- Tras el login, redirige a:
  - `admin/dashboard/dashboard.html` si es admin
  - `usuario/dashboard/dashboard.html` si es usuario
- Cerrar sesión: `localStorage.removeItem('userData')` y redirige al login.

## Navegación y layout (`layout.js`)

- Todas las páginas (excepto login) incluyen `<div id="layout-container"></div>` donde `layout.js` inyecta el sidebar + topbar.
- `layout.js` verifica que exista `userData` en `localStorage`; si no, redirige al login.
- El sidebar muestra enlaces según el rol del usuario:
  - **Admin**: Dashboard, Usuarios, Catálogos, Evaluaciones, Aprobaciones, Reportes, Bonos, Aclaraciones
  - **Usuario**: Mi Resumen, Mis Evaluaciones, Mis Bonos, Mis Reportes
- Sidebar colapsado por defecto (solo íconos), se expande al hacer hover.
- El enlace activo se marca comparando `window.location.pathname`.
- Incluye dropdown de usuario con opción "Mi Perfil" y "Cerrar Sesión".
- El tema de color se lee de `localStorage` (`isaThemeColor`) y se aplica al CSS var `--primary-color`.

## Sistema de datos (simulado con `localStorage`)

Todos los servicios (`*Service.js`) usan datos mock hardcodeados. Las claves de `localStorage` usadas son:

| Clave | Uso | Módulo |
|---|---|---|
| `userData` | Datos del usuario autenticado | login.js, layout.js |
| `isaThemeColor` | Color primario personalizado | login.js, layout.js |
| `isa_perfil` | Perfil del usuario (nombre, email, teléfono, etc.) | modal-perfil.js |
| `isa_notificaciones` | Notificaciones (tareas, comunicados) | modal-notificaciones.js |
| `isa_consultas` | Consultas de usuarios | modal-consulta.js, consultas.js |
| `isa_evaluacion_<periodo>` | Datos de grilla de evaluación | grilla-evaluacion.js |

## Páginas de administración

### Dashboard (`admin/dashboard/`)
- 4 tarjetas KPI: Total Usuarios, Evaluaciones, Pendientes, Bonos
- Lista de actividad reciente y próximas tareas
- Todos los datos son simulados en `DashboardService`

### Usuarios (`admin/usuarios/`)
- CRUD de usuarios con tabla paginada y filtro en tiempo real por nombre/email
- Modal para crear/editar usuario (nombre, email, rol, departamento)
- KPI cards: total de personal, activos, seguridad del sistema
- Exportar (simulado) y eliminar (confirmación + filtrado local)

### Catálogos (`admin/catalogos/`)
- Gestión de categorías maestras y estructura del menú de navegación
- Renderizado de árbol de menú con subitems
- Gráfica de uso de navegación con **Chart.js**
- Registro de actividad de cambios

### Evaluaciones (`admin/evaluaciones/`)
- Constructor de evaluaciones: título, descripción, audiencia
- Añade criterios de forma dinámica: Opción Múltiple, Escala Lineal, Texto Largo
- Publica evaluación (simulado, imprime en consola)
- **Supervisión**: modal con grilla Handsontable en modo solo lectura (`GrillaSupervisor`), con filtros por estado y búsqueda

### Aprobaciones (`admin/aprobaciones/`)
- Lista de solicitudes pendientes (Evaluaciones, Bonos, Actualización de Accesos)
- Filtros por categoría
- Panel lateral de "Revisión Rápida" con detalle al seleccionar
- Botones Confirmar Aprobación / Rechazar Solicitud (con confirmación y simulación)
- Historial de aprobaciones con estado Aprobado/Rechazado

### Reportes (`admin/reportes/`)
- KPIs: Total Evaluaciones, Puntuación Promedio, Tasa de Finalización
- Selector de temporalidad: 30 días / Trimestral / Anual
- **Chart.js**: gráfica de líneas (tendencias) y barras (departamentos)
- Tabla de registros detallados con puntuación y estado

### Bonos (`admin/bonos/`)
- Cards de programas: Multiplicador de Desempeño, Hito de Retención
- Modal con detalle del programa (participantes, utilización, progreso)
- Tabla de asignación de empleados con barra de progreso y pago potencial
- Modal para crear nuevo programa de incentivos

### Consultas / Aclaraciones (`admin/consultas/`)
- Doble pestaña: Consultas (pendientes y respondidas) + Notificaciones
- Responder consultas mediante modal
- Exportar consultas a CSV (genera Blob + descarga)
- Enviar notificaciones (tarea o comunicado) con fecha límite opcional
- Historial de notificaciones enviadas
- Estadísticas: pendientes, respondidas, notificaciones enviadas

## Páginas de usuario

### Dashboard (`usuario/dashboard/`)
- KPIs personales: Mi Promedio, Evaluaciones Pendientes, Bono Acumulado
- Tabla con mis últimas evaluaciones
- Lista de próximos pasos (tareas con prioridad)

### Evaluaciones (`usuario/evaluaciones/`)
- Pendientes por completar (cards con categoría y fecha límite)
- Historial de evaluaciones (tabla con puntuación)
- **Grilla de Evaluación**: modal con Handsontable (`GrillaISA`) — edita competencias (Liderazgo, Comunicación, Proactividad, Colaboración, Adaptabilidad, Orient. Resultados), calcula promedios automáticamente, auto-guarda cada 2s en `localStorage`, leyenda de colores 1-5

### Bonos (`usuario/bonos/`)
- Progreso del ciclo actual con barra animada y monto proyectado
- Metas vinculadas con indicador meta vs actual
- Historial de pagos

### Reportes (`usuario/reportes/`)
- **Chart.js**: gráfica de líneas (tendencia personal) y radar (competencias)
- Tabla de reportes generados con descarga de PDF (simulada)

## Componentes compartidos

### `modal-perfil.js`
- Modal de Mi Perfil (nombre, email, teléfono, departamento, puesto)
- Guarda en `localStorage` clave `isa_perfil`
- Actualiza `userData.nombre` en `localStorage` si cambia el nombre

### `modal-notificaciones.js`
- Servicio `NotificacionesService` con CRUD completo en `localStorage`
- Renderiza dropdown de notificaciones (ícono de campana, badge con conteo, lista)
- Modal de detalle de notificación
- Modal para crear notificación (tipo, título, mensaje, fecha límite, destinatario)
- Funciones expuestas globalmente: `renderNotificacionesDropdown()`, `renderBotonAdminNotificaciones()`, etc.

### `modal-consulta.js`
- Servicio `ConsultasService` con CRUD en `localStorage`
- Dropdown de ayuda con botón "Nueva Consulta" y "Ver mis consultas"
- Modal para crear consulta y modal para listar consultas del usuario
- Admin puede ver pendientes desde el dropdown con badge de conteo
- Funciones expuestas globalmente: `renderDropdownAyuda()`, `renderBotonAdminConsultas()`, etc.

### `grilla-evaluacion.js`
- **Clase `GrillaISA`**: grilla de evaluación interactiva con Handsontable
  - Columnas: #, Nombre, Puesto, 6 competencias, Promedio (auto), Evaluación Global (auto), Estado
  - Renderizado condicional por puntuación (color: rojo → naranja → amarillo → verde → celeste)
  - Cálculo automático de promedios por fila y promedio general
  - Auto-guardado cada 2 segundos en `localStorage` con debounce
  - Funciones: agregarFila, guardar, cargar
- **Clase `GrillaSupervisor`**: grilla de solo lectura para que admin supervise evaluaciones
  - Mismos datos pero modo readOnly
  - Renderizado de estado con colores (Borrador gris, En Proceso amarillo, Completado verde)
- Expone `window.GrillaISA` y `window.GrillaSupervisor`

## Dependencias externas (CDN)

| Librería | Versión | Uso |
|---|---|---|
| Bootstrap 5 | 5.3.0 | UI framework (CSS + JS bundle) |
| Bootstrap Icons | 1.11.3 | Iconos vectoriales |
| Google Fonts (Inter) | - | Tipografía del login |
| Handsontable | (última) | Grilla de evaluación (licencia non-commercial) |
| Chart.js | (última) | Gráficas en Reportes y Catálogos |

No hay `package.json`, ni npm, ni paso de compilación.

## Convenciones de estilo

- **CSS Variables**: `--primary-color` controla el color principal en todo el sistema. Configurable por el usuario mediante el selector de color en el login.
- **Layout**: sidebar colapsado (80px) → expandido (260px) al hover. Topbar fija a la derecha del sidebar.
- **Transiciones**: `body:has(.sidebar:hover)` empuja el topbar y el contenido al expandirse.
- **Breakpoints**: Mobile-first con Bootstrap 5. El login se apila en vertical en <768px.
- **Clases utilitarias**: `card-stat` (sombra + hover lift), `hover-icon` (elevación al hover), `text-dark-blue` para títulos.

## Patrón de código

Cada página sigue una arquitectura MVC ligera:

1. **Model** → Servicio simulado (ej. `DashboardService`, `UsuariosService`)
2. **View** → Funciones `render*()` que manipulan el DOM
3. **Controller** → `DOMContentLoaded` dispara carga de datos y renderizado

## Pruebas y reseteo de estado

- No hay suite de pruebas automatizadas.
- Para empezar sesión limpia: `localStorage.clear()` en la consola y recargar el login.
- Claves individuales a limpiar: `userData`, `isaThemeColor`, `isa_perfil`, `isa_notificaciones`, `isa_consultas`, `isa_evaluacion_*`.

## Errores comunes

- **Abrir `index.html` directamente**: rompe las rutas relativas de layout.js (`../../../../index.html`). Usar servidor HTTP siempre.
- **Falta `userData` en localStorage**: layout.js redirige al login. Si estás depurando una página protegida, asegúrate de haber iniciado sesión primero.
- **Rol incorrecto**: Si el sidebar no muestra los enlaces esperados, verifica `localStorage.userData.rol` debe ser `'admin'` o `'usuario'`.
- **Handsontable no carga**: requiere conexión a CDN o redes corporativas pueden bloquearlo. La licencia es non-commercial.
- **El modal de perfil/notificaciones no se abre**: las funciones globales (ej. `abrirModalPerfil()`) se definen en los archivos de componente que deben estar incluidos como `<script>` en el HTML.
- **Gráficas no se ven**: Chart.js se carga desde CDN. Verifica conectividad.
- **Tema no persiste**: la clave `isaThemeColor` debe existir en localStorage. El color picker la escribe al cambiar.
