# Sistema ISA - Backend Django

## Resumen del Proyecto
**Contexto actualizado (abril 2026)**
- El proyecto está basado en Supabase (PostgreSQL) con **`managed = False`**; las tablas ya existen.
- `inspectdb` muestra el modelo real de la tabla **`usuarios`**: incluye `password`, `nombre_completo`, `id_presona_empleado` (typo) y campos `id_area_siare`, `id_puesto_siare`.
- El DBA solicitó que el modelo Django herede de `AbstractBaseUser` y mapee los campos exactos, incluido `db_column='id_presona_empleado'`.
- Falta la columna `last_login`; se propondrá agregarla o usar `models.Model` con manejo manual de contraseñas.
- Próximo objetivo: JIT Provisioning vía el API .NET (AD) y creación de un mock FastAPI para pruebas.

El **Sistema ISA** es una plataforma backend para digitalizar el proceso de evaluación de desempeño discrecional de ISA Corporativo. Reemplaza el flujo físico (Excel + papel) por una plataforma digital con:

- Captura digital de evaluaciones de desempeño
- Workflow de aprobación automatizado con máquina de estados (django-fsm)
- Firma electrónica simple (Base64 Canvas)
- Cálculo automático de bonos basado en desempeño y EBITDA
- Trazabilidad y auditoría completa

---

## Stack Tecnológico

| Tecnología | Propósito | Versión |
|------------|-----------|---------|
| **Django 5.0.4** | Framework web principal | 5.0.4 |
| **Django REST Framework** | APIs REST | 3.15.x |
| **SimpleJWT** | Autenticación stateless JWT | 5.3.x |
| **django-cors-headers** | CORS para Frontend | 4.3.x |
| **django-environ** | Variables de entorno | 0.11.x |
| **PostgreSQL (Supabase)** | Base de datos | 16 |
| **Docker + Docker Compose** | Contenedores | Latest |

---

## Estado del Proyecto: EN DESARROLLO

### ✅ Fase 1 Completada

| # | Componente | Estado | Endpoint |
|---|------------|--------|----------|
| 1.1 | Login JWT con CustomTokenObtainPairSerializer | ✅ Completado | `/api/v1/auth/login/` |
| 1.2 | Refresh Token | ✅ Completado | `/api/v1/auth/refresh/` |
| 1.3 | API de Roles (ReadOnly) | ✅ Completado | `/api/v1/catalogs/roles/` |
| 1.4 | API de Departamentos (ReadOnly) | ✅ Completado | `/api/v1/catalogs/departamentos/` |
| 1.5 | API de Periodos (ReadOnly) | ✅ Completado | `/api/v1/catalogs/periodos/` |
| 1.6 | API de Competencias (ReadOnly) | ✅ Completado | `/api/v1/catalogs/competencias/` |
| 1.7 | CRUD de Usuarios | ✅ Completado | `/api/v1/users/` |
| 1.8 | Permisos RBAC | ✅ Completado | IsAdminOrContraloria |
| 1.9 | Django Admin | ✅ Completado | `/admin/` |

### ✅ Fase 2 Completada: Evaluation Core Service

| # | Componente | Estado | Archivo |
|---|------------|--------|---------|
| 2.1 | Permisos a nivel de objeto | ✅ Completado | `apps/evaluations/permissions.py` |
| 2.2 | Lógica de negocio (State Machine) | ✅ Completado | `apps/evaluations/services.py` |
| 2.3 | Serializers (lectura/escritura) | ✅ Completado | `apps/evaluations/serializers.py` |
| 2.4 | Vistas (ViewSet + acciones) | ✅ Completado | `apps/evaluations/views.py` |
| 2.5 | Rutas API | ✅ Completado | `apps/evaluations/urls.py` |
| 2.6 | Tests unitarios | ✅ Completado | `apps/evaluations/tests.py` |

### Endpoints de Evaluaciones

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/evaluations/` | Listar evaluaciones |
| POST | `/api/v1/evaluations/` | Crear evaluación |
| GET | `/api/v1/evaluations/{id}/` | Ver evaluación |
| PUT/PATCH | `/api/v1/evaluations/{id}/` | Actualizar evaluación |
| POST | `/api/v1/evaluations/{id}/submit/` | Enviar (DRAFT → SUBMITTED) |
| POST | `/api/v1/evaluations/{id}/approve/` | Aprobar → APPROVED |
| POST | `/api/v1/evaluations/{id}/reject/` | Rechazar → DRAFT |
| GET | `/api/v1/evaluations/transitions/?estado=DRAFT` | Ver transiciones disponibles |

### Tests de Evaluación

| Test | Descripción |
|------|-------------|
| `test_empleado_puede_ver_su_propia_evaluacion` | Verifica acceso propio |
| `test_empleado_no_puede_acceder_evaluacion_ajena` | Verifica permisos |
| `test_manager_puede_ver_evaluacion_de_subordinado` | Verifica jerarquía |
| `test_submit_exitoso` | Happy path: DRAFT → SUBMITTED |
| `test_estado_protegido_no_editable_via_put` | Estado inmutable por API |
| `test_reject_sin_comentario_falla` | Validación: comentario requerido |
| `test_reject_comentario_corto_falla` | Validación: min 10 caracteres |
| `test_reject_con_comentario_valido_exitoso` | Rechazo válido |
| `test_flujo_completo_happy_path` | DRAFT → SUBMITTED → APPROVED |

### ⏳ Fase 3 Pendiente: Firmas Electrónicas

- Implementación de firmas digitales (Base64 Canvas)
- Generación de documentos PDF
- Integración con flujo de aprobación

---

## Arquitectura del Proyecto

```
Proyecto-ISA/
│
├── apps/                              # Aplicaciones Django (Domain-Driven Design)
│   ├── __init__.py
│   │
│   ├── users/                        # 📍 DOMINIO: Usuarios y Autenticación
│   │   ├── __init__.py
│   │   ├── apps.py                   # Configuración de la app
│   │   ├── models.py                  # Modelo: Usuarios (jerarquía con manager_id)
│   │   ├── serializers.py             # CustomTokenObtainPairSerializer, UsuarioSerializer
│   │   ├── views.py                  # CustomTokenObtainPairView, UsuarioViewSet, IsAdminOrContraloria
│   │   ├── urls.py                    # Rutas: /auth/login/, /auth/refresh/, /users/
│   │   ├── admin.py                   # Admin con auto-encriptación de password
│   │   └── authentication.py          # ✅ CustomJWTAuthentication
│   │
│   ├── catalogs/                      # 📍 DOMINIO: Catálogos del Sistema
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py                  # CatRoles, CatDepartamentos, CatPeriodos, CatCompetencias
│   │   ├── serializers.py             # CatRolesSerializer, etc.
│   │   ├── views.py                  # ReadOnlyModelViewSets para cada catálogo
│   │   ├── urls.py                    # Rutas con DefaultRouter
│   │   └── admin.py                  # Admin para catálogos
│   │
│   ├── evaluations/                   # 📍 DOMINIO: Evaluaciones (COMPLETO)
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py                  # Evaluaciones, CompetenciasDetalle, Objetivos
│   │   ├── serializers.py             # ✅ EvaluacionSerializer, Create, Update, Transition
│   │   ├── views.py                   # ✅ EvaluacionViewSet con acciones
│   │   ├── services.py               # ✅ EvaluationService (State Machine)
│   │   ├── permissions.py            # ✅ IsManagerOrContraloriaOrSelf
│   │   ├── urls.py                   # ✅ Rutas API
│   │   └── tests.py                   # ✅ Tests unitarios
│   │
│   ├── finances/                      # 📍 DOMINIO: Finanzas y Bonos (Pendiente)
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   └── models.py                  # Bonos (snapshot financiero)
│   │
│   └── audit/                          # 📍 DOMINIO: Auditoría (Pendiente)
│       ├── __init__.py
│       ├── apps.py
│       └── models.py                  # HistorialEstados, Aprobaciones, LogsSistema
│
├── core/                              # Configuración Centralizada
│   ├── __init__.py
│   ├── settings.py                    # ⚙️ Configuración completa (DB, JWT, DRF, CORS)
│   ├── urls.py                        # Routing principal
│   ├── wsgi.py                        # WSGI entrypoint
│   └── asgi.py                        # ASGI entrypoint
│
├── manage.py                          # Django management script
├── requirements.txt                   # Dependencias Python
├── Dockerfile                         # Imagen Docker
├── docker-compose.yml                 # Orquestación Docker
├── .env                              # Variables de entorno (NO commitear)
├── .env.example                      # Template de variables
├── PLAN_IMPLEMENTACION.txt           # Plan detallado del proyecto
└── README.md                         # Este archivo
```

---

## Modelo de Datos (12 Tablas en Supabase)

### Catálogos
| Tabla | Descripción | App Django |
|-------|-------------|------------|
| `cat_roles` | Roles (Administrador, Director, Gerente, Coordinador, Contraloria) con nivel_aprobacion | `apps.catalogs` |
| `cat_departamentos` | Áreas organizacionales (Sistemas, Finanzas, Operaciones) | `apps.catalogs` |
| `cat_periodos` | Ciclos de evaluación (Anual 2025) | `apps.catalogs` |
| `cat_competencias` | Competencias a evaluar (6 competencias) | `apps.catalogs` |

### Transaccional
| Tabla | Descripción | App Django |
|-------|-------------|------------|
| `usuarios` | Usuarios con jerarquía (manager_id self-join) y password_hash PBKDF2 | `apps.users` |
| `evaluaciones` | Evaluaciones con campo estado (DRAFT, SUBMITTED, PENDING_APPROVAL, APPROVED, CLOSED) | `apps.evaluations` |
| `competencias_detalle` | Calificación por competencia (1-5) | `apps.evaluations` |
| `objetivos` | Objetivos del evaluado | `apps.evaluations` |

### Auditoría
| Tabla | Descripción | App Django |
|-------|-------------|------------|
| `historial_estados` | Trazabilidad de cambios de estado | `apps.audit` |
| `aprobaciones` | Firmas digitales (Base64) | `apps.audit` |
| `logs_sistema` | Logs de acciones | `apps.audit` |

### Finanzas
| Tabla | Descripción | App Django |
|-------|-------------|------------|
| `bonos` | Snapshot financiero (salario_base, impacto_ebitda, monto_final) | `apps.finances` |

---

## Flujo de Autenticación JWT

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FLUJO DE AUTHENTICATION                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. FRONTEND                                                                │
│     POST /api/v1/auth/login/                                               │
│     { "username": "admin", "password": "admin123" }                        │
│                           │                                                  │
│                           ▼                                                  │
│  2. CustomTokenObtainPairSerializer.validate()                             │
│     ├── Busca usuario en Supabase por username                            │
│     ├── Valida password_hash con check_password() (PBKDF2)               │
│     └── Genera tokens JWT con claims personalizados                        │
│                           │                                                  │
│                           ▼                                                  │
│  3. RESPUESTA                                                              │
│     {                                                                       │
│       "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",                 │
│       "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."                  │
│     }                                                                       │
│                           │                                                  │
│                           ▼                                                  │
│  4. CLAIMS EN EL TOKEN                                                      │
│     {                                                                       │
│       "user_id": "71323b56-e279-43e4-9603-8485dd1fecf9",                  │
│       "username": "admin",                                                  │
│       "nombre_completo": "Jorge Yael Padua Nava",                          │
│       "puesto": "DBA",                                                     │
│       "rol_id": 1,                                                         │
│       "departamento_id": 1                                                  │
│     }                                                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Endpoints Activos

### Autenticación
| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/auth/login/` | Login JWT | ❌ Público |
| POST | `/api/v1/auth/refresh/` | Refresh token | ❌ Público |

### Catálogos (ReadOnly)
| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/catalogs/roles/` | Listar roles | ✅ JWT |
| GET | `/api/v1/catalogs/departamentos/` | Listar departamentos | ✅ JWT |
| GET | `/api/v1/catalogs/periodos/` | Listar periodos | ✅ JWT |
| GET | `/api/v1/catalogs/competencias/` | Listar competencias | ✅ JWT |

### Usuarios (CRUD)
| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/users/` | Listar usuarios | ✅ JWT |
| POST | `/api/v1/users/` | Crear usuario | ✅ JWT (Solo Admin/Contraloría) |
| GET | `/api/v1/users/{id}/` | Ver usuario | ✅ JWT |
| PUT/PATCH | `/api/v1/users/{id}/` | Actualizar usuario | ✅ JWT (Solo Admin/Contraloría) |
| DELETE | `/api/v1/users/{id}/` | Eliminar usuario | ✅ JWT (Solo Admin/Contraloría) |

---

## Permisos RBAC Implementados

```python
class IsAdminOrContraloria(BasePermission):
    """
    Permite acceso total solo a Administradores y Contraloría.
    Los demás usuarios solo pueden consultar (GET).
    """
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        user_rol = getattr(request.user.rol, 'nombre', '').lower()
        return user_rol in ['administrador', 'contraloria']
```

| Rol | GET (listar/ver) | POST/PUT/DELETE |
|-----|-----------------|------------------|
| Administrador | ✅ | ✅ |
| Contraloria | ✅ | ✅ |
| Director | ✅ | ❌ |
| Gerente | ✅ | ❌ |
| Coordinador | ✅ | ❌ |

---

## Máquina de Estados (FSM) - ✅ Completada

```
    ┌──────────────────────────────────────────────────────────┐
    │                                                          │
    │    ┌───────┐                                           │
    │    │ DRAFT │ ← Estado inicial                          │
    │    └───┬───┘   El evaluado puede editar                │
    │        │                                               │
    │        │ submit_evaluation()                           │
    │        ▼                                               │
    │    ┌───────────┐                                       │
    │    │ SUBMITTED │ Ya no es editable por evaluado        │
    │    └─────┬─────┘                                       │
    │          │                                             │
    │          │ approve_by_coordinator()                    │
    │          ▼                                             │
    │    ┌────────────────────┐                              │
    │    │ PENDING_APPROVAL  │ ← En espera de firmas        │
    │    └─────────┬──────────┘                              │
    │              │                                         │
    │     ┌────────┴────────┐                                │
    │     ▼                 ▼                                │
    │  ┌─────────┐   ┌───────────┐                         │
    │  │ APPROVED│   │ REJECTED  │ ← Requiere comentario    │
    │  └────┬────┘   └─────┬────┘                         │
    │       │              │                                 │
    │       ▼              ▼                                 │
    │  ┌─────────┐    (regresa a DRAFT)                      │
    │  │ CLOSED  │ ← Estado final, inmutable                  │
    │  └─────────┘                                            │
    │                                                          │
    └──────────────────────────────────────────────────────────┘
```

---

## Arquitectura: Defense in Depth

```
┌─────────────────────────────────────────────┐
│              views.py (APIs)                 │  ← Capa de TRANSPORTE
│  - Valida JWT, permisos, esquemas            │
│  - Delega a services                         │
│  - PROHIBIDO: lógica de negocio             │
└─────────────────┬───────────────────────────┘
                  ▼
┌─────────────────────────────────────────────┐
│              services.py                     │  ← Capa de NEGOCIO
│  - Lógica de estado (FSM)                   │
│  - Cálculo de bonos                         │
│  - Validaciones complejas                   │
│  - PROHIBIDO: Queries directas a BD        │
└─────────────────┬───────────────────────────┘
                  ▼
┌─────────────────────────────────────────────┐
│             selectors.py                     │  ← Capa de LECTURA
│  - Queries optimizados                      │
│  - select_related, prefetch_related        │
│  - NO modifica datos                        │
└─────────────────┬───────────────────────────┘
                  ▼
┌─────────────────────────────────────────────┐
│              models.py                       │  ← Capa de DATOS
│  - managed = False (Supabase)               │
│  - Define estructuras de tablas            │
└─────────────────────────────────────────────┘
```

**Regla de oro**: views → services → selectors → models (nunca en sentido contrario)

---

## Configuración de Django (core/settings.py)

```python
# ============================================
# DJANGO REST FRAMEWORK
# ============================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apps.users.authentication.CustomJWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# ============================================
# SIMPLE JWT CONFIGURATION
# ============================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': os.environ.get('JWT_SECRET_KEY', 'jwt-default-key'),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# ============================================
# CORS HEADERS
# ============================================
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
```

---

## Cómo iniciar el proyecto

```bash
# 1. Construir y levantar Docker
docker compose up --build

# 2. El servidor estará disponible en
http://localhost:8000

# 3. Panel de administración
http://localhost:8000/admin/
```


---

## Ramas del Repositorio

| Rama | Descripción |
|------|-------------|
| `main` | Rama estable |
| `backend` | Desarrollo del backend Django (esta rama) |
| `frontend` | Frontend (repo separado) |
| `database` | Migraciones y scripts SQL |

---

## Contributing

Para contribuir a esta rama:

1. Crear branch desde `backend`: `git checkout -b feature/nueva-funcionalidad`
2. Implementar cambios siguiendo la arquitectura **Defense in Depth**
3. Los modelos deben tener `managed = False` (no modificar esquema de Supabase)
4. Crear serializers separados para lectura y escritura
5. Implementar permisos RBAC en ViewSets
6. Commit y push
7. Crear Pull Request

---

## Estado: Fases 1 y 2 Completadas ✅

### Próximos pasos
- Actualizar `apps/users/models.py` para usar los campos exactos del esquema del DBA (incluyendo `id_presona_empleado` con `db_column='id_presona_empleado'`).
- Decidir entre `AbstractBaseUser` (requiere `last_login`) o `models.Model` con manejo manual de contraseñas.
- Implementar Mock FastAPI que exponga los endpoints `/api/auth/token`, `/api/active-directory/validar-acceso` y `/api/personas-siare/consultar-por-usuario-ad`.
- Crear cliente HTTP en Django (`apps/users/ad_client.py`) que consuma el Mock y habilite JIT Provisioning.

## Árbol del proyecto
.
├── Dockerfile
├── PLAN_IMPLEMENTACION.txt
├── README.md
├── api_ISA
│   └── README.md
├── apps
│   ├── __init__.py
│   ├── audit
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   └── __init__.py
│   │   └── models.py
│   ├── catalogs
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── evaluations
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── services.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── finances
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   └── __init__.py
│   │   └── models.py
│   └── users
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── authentication.py
│       ├── models.py
│       ├── serializers.py
│       ├── urls.py
│       └── views.py
├── core
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── docker-compose.yml
├── manage.py
└── requirements.txt

11 directories, 47 files

El proyecto tiene las siguientes fases funcionales:
- ✅ Fase 1: Login JWT, Catálogos API (ReadOnly), CRUD Usuarios, Permisos RBAC, Django Admin
- ✅ Fase 2: Evaluación Core Service con State Machine, Permisos a nivel de objeto, Tests unitarios

**Próximo paso**: Fase 3 - Firmas Electrónicas y Bonos
