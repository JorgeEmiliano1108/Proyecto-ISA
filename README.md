# Sistema ISA - Backend Django

## Resumen del Proyecto

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

### ⏳ Fase 2 Pendiente

- Máquina de estados con django-fsm (DRAFT → SUBMITTED → PENDING_APPROVAL → APPROVED → CLOSED)
- APIs de evaluaciones con transiciones de estado
- Snapshot financiero (captura salary_base al aprobar)
- APIs de bonos

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
│   │   └── authentication.py          # CustomJWTAuthentication (pendiente)
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
│   ├── evaluations/                   # 📍 DOMINIO: Evaluaciones (Pendiente)
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py                  # Evaluaciones, CompetenciasDetalle, Objetivos
│   │   ├── serializers.py             # [POR CREAR]
│   │   ├── views.py                   # [POR CREAR] ViewSets con FSM
│   │   ├── services.py                # [POR CREAR] Lógica de State Machine
│   │   ├── selectors.py               # [POR CREAR] Queries optimizadas
│   │   └── urls.py                    # [POR CREAR]
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

## Máquina de Estados (FSM) - Pendiente

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

## Variables de Entorno (.env)

```env
SECRET_KEY=django-insecure-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://postgres.pkihspbkksoggvvwcbam:admin_database2026@aws-1-us-west-2.pooler.supabase.com:6543/postgres
JWT_SECRET_KEY=tu-jwt-secret-key-aqui
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

## Estado: Fase 1 Completada ✅

El proyecto tiene la Fase 1 completamente funcional:
- ✅ Login JWT funcionando
- ✅ Catálogos API (ReadOnly) funcionando
- ✅ CRUD de Usuarios con permisos RBAC
- ✅ Django Admin configurado

**Próximo paso**: Fase 2 - Máquina de Estados con django-fsm para evaluaciones