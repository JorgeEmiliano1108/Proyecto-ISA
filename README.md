# Sistema ISA - Backend Django

## ¿Qué es este proyecto?

El **Sistema ISA** es una plataforma backend para digitalizar el proceso de evaluación de desempeño discrecional de ISA Corporativo. Reemplaza el flujo físico (Excel + papel) por una plataforma digital con:

- Captura digital de evaluaciones de desempeño
- Workflow de aprobación automatizado con máquina de estados
- Firma electrónica simple (Base64 Canvas)
- Cálculo automático de bonos basado en desempeño y EBITDA
- Trazabilidad y auditoría completa

---

## Stack Tecnológico

| Tecnología | Propósito |
|-------------|-----------|
| **Django 5.0.4** | Framework web principal |
| **Django REST Framework 3.15.1** | APIs REST |
| **SimpleJWT 5.3.0** | Autenticación stateless con JWT |
| **django-fsm 2.8.1** | Máquina de estados |
| **PostgreSQL (Supabase)** | Base de datos |
| **Docker + Docker Compose** | Contenedores |

---

## Estado del Proyecto: EN DESARROLLO

### ✅ Lo que ya está implementado

- **Estructura de múltiples apps Django** (`apps/users`, `apps/catalogs`, `apps/evaluations`)
- **Modelos con `managed = False`** apuntando a 12 tablas de Supabase
- **Conexión a Supabase** configurada en variables de entorno
- **sys.path configurado** para importar las apps

### ❌ Pendiente por implementar

#### Fase 1: User & Catalog Service
- [ ] Autenticación JWT con SimpleJWT
- [ ] Endpoint `/api/v1/auth/login/` (serializer customizado para modelo Supabase)
- [ ] APIs de catálogos (roles, departamentos, periodos, competencias)
- [ ] CRUD de usuarios

#### Fase 2: Evaluation Core Service
- [ ] Máquina de estados con django-fsm (DRAFT → SUBMITTED → PENDING_APPROVAL → APPROVED → CLOSED)
- [ ] APIs de evaluaciones con transiciones de estado
- [ ] Snapshot financiero (captura salary_base al aprobar)
- [ ] APIs de bonos

#### Fase 3: Extras
- [ ] Firmas digitales (Base64)
- [ ] Notificaciones (recordatorios cada 3 días)
- [ ] Auditoría completa

---

## Árbol de Archivos y Carpetas

```
Proyecto-ISA/
│
├── apps/                          # Aplicaciones Django modulares
│   ├── __init__.py
│   │
│   ├── users/                     # Gestión de Usuarios y Autenticación
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py              # Modelo: Usuarios (con jerarquía manager_id)
│   │   ├── serializers.py         # [POR CREAR] Custom JWT Serializer
│   │   ├── views.py               # [POR CREAR] Vistas de API
│   │   ├── services.py            # [POR CREAR] Lógica de negocio
│   │   ├── selectors.py           # [POR CREAR] Queries optimizadas
│   │   └── urls.py                # [POR CREAR] Rutas /api/v1/users/
│   │
│   ├── catalogs/                  # Catálogos del Sistema
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py              # Modelos: CatRoles, CatDepartamentos, CatPeriodos, CatCompetencias
│   │   ├── serializers.py         # [POR CREAR]
│   │   ├── views.py               # [POR CREAR] ReadOnlyModelViewSet
│   │   ├── services.py            # [POR CREAR]
│   │   ├── selectors.py          # [POR CREAR]
│   │   └── urls.py                # [POR CREAR] Rutas /api/v1/catalogs/
│   │
│   └── evaluations/               # Evaluaciones y Auditoría
│       ├── __init__.py
│       ├── apps.py
│       ├── models.py              # Modelos: Evaluaciones, CompetenciasDetalle, Objetivos
│       ├── auditoria.py           # Modelos: HistorialEstados, Aprobaciones, LogsSistema
│       ├── serializers.py         # [POR CREAR]
│       ├── views.py               # [POR CREAR] ViewSets con transiciones FSM
│       ├── services.py            # [POR CREAR] Lógica de State Machine
│       ├── selectors.py           # [POR CREAR]
│       └── urls.py                # [POR CREAR] Rutas /api/v1/evaluations/
│
├── core/                          # Configuración del Proyecto Django
│   ├── __init__.py
│   ├── settings.py                # Configuración completa (DB, JWT, DRF, CORS)
│   ├── urls.py                    # Rutas principales
│   ├── wsgi.py                    # Entrypoint WSGI
│   └── asgi.py                    # Entrypoint ASGI
│
├── sistema_isa/                    # App legacy (modelos originales)
│   ├── __init__.py
│   ├── apps.py
│   ├── admin.py                   # Admin customizado ISA
│   ├── views.py
│   ├── tests.py
│   ├── models/                    # Modelos originales (referencia)
│   │   ├── __init__.py
│   │   ├── seguridad.py           # Modelo: Usuarios
│   │   ├── catalogos.py           # Modelos de catálogos
│   │   ├── transaccional.py       # Evaluaciones, competencias, objetivos
│   │   ├── auditoria.py          # Historial, aprobaciones, logs
│   │   └── finanzas.py            # Bonos
│   └── migrations/
│
├── manage.py                      # Django management script
├── requirements.txt               # Dependencias Python
├── Dockerfile                     # Imagen Docker
├── docker-compose.yml             # Orquestación Docker
├── .env                          # Variables de entorno (NO commitear)
├── .env.example                  # Template de variables
├── PLAN_IMPLEMENTACION.txt        # Plan detallado del proyecto
└── README.md                     # Este archivo
```

---

## Modelo de Datos (12 Tablas en Supabase)

### Catálogos
| Tabla | Descripción |
|-------|-------------|
| `cat_roles` | Roles (Coordinador, Gerente, Director, Contraloría) con nivel_aprobacion |
| `cat_departamentos` | Áreas organizacionales |
| `cat_periodos` | Ciclos de evaluación |
| `cat_competencias` | Competencias a evaluar |

### Transaccional
| Tabla | Descripción |
|-------|-------------|
| `usuarios` | Usuarios con jerarquía (manager_id self-join) y password_hash |
| `evaluaciones` | Evaluaciones con campo `estado` |
| `competencias_detalle` | Calificación por competencia |
| `objetivos` | Objetivos del evaluado |

### Auditoría
| Tabla | Descripción |
|-------|-------------|
| `historial_estados` | Trazabilidad de cambios de estado |
| `aprobaciones` | Firmas digitales (Base64) |
| `logs_sistema` | Logs de acciones |

### Finanzas
| Tabla | Descripción |
|-------|-------------|
| `bonos` | Snapshot financiero (salario_base, impacto_ebitda, monto_final) |

---

## Máquina de Estados (FSM)

```
   DRAFT ──submit()──▶ SUBMITTED ──approve()──▶ PENDING_APPROVAL
                                                          │
                        ┌──────────────┬───────────────────┤
                        ▼              ▼                   ▼
                   APPROVED       REJECTED           (escalation)
                        │
                        ▼
                    CLOSED
```

### Transiciones
| Estado | Acción | Siguiente | Condición |
|--------|--------|-----------|-----------|
| DRAFT | submit() | SUBMITTED | Todas las competencias llenas |
| SUBMITTED | approve() | PENDING_APPROVAL | Evaluador es Coordinador |
| PENDING_APPROVAL | approve() | APPROVED | Si no requiere gerente |
| PENDING_APPROVAL | reject() | DRAFT | Comentario obligatorio |
| APPROVED | close() | CLOSED | Solo Director |

---

## Endpoints Planificados

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/auth/login/` | Login JWT |
| POST | `/api/v1/auth/refresh/` | Refresh token |
| GET | `/api/v1/catalogs/roles/` | Listar roles |
| GET | `/api/v1/catalogs/departamentos/` | Listar departamentos |
| GET | `/api/v1/catalogs/periodos/` | Listar periodos |
| GET/POST | `/api/v1/users/` | CRUD usuarios |
| GET/POST/PATCH | `/api/v1/evaluations/` | Evaluaciones |
| POST | `/api/v1/evaluations/{id}/submit/` | Enviar evaluación |
| POST | `/api/v1/evaluations/{id}/approve/` | Aprobar |
| POST | `/api/v1/evaluations/{id}/reject/` | Rechazar (con comentario) |

---

## Arquitectura: Defense in Depth

```
┌─────────────────────────────────────┐
│         views.py (APIs)             │  ← Capa de TRANSPORTE
│  - Valida JWT, permisos, esquemas   │
│  - Delega a services               │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│         services.py                 │  ← Capa de NEGOCIO
│  - Lógica de estado (FSM)          │
│  - Cálculo de bonos                │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│         selectors.py                │  ← Capa de LECTURA
│  - Queries optimizados             │
│  - select_related, prefetch_related │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│         models.py                   │  ← Capa de DATOS
│  - managed = False (Supabase)       │
└─────────────────────────────────────┘
```

**Regla**: views → services → selectors → models (nunca en sentido contrario)

---

## Cómo iniciar el proyecto

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Verificar conexión
python manage.py check

# 3. Ejecutar migraciones (tablas internas de Django)
python manage.py migrate

# 4. Iniciar servidor
python manage.py runserver

# 5. Acceder a http://localhost:8000/admin/
```

---

## Variables de Entorno (.env)

```env
SECRET_KEY=django-insecure-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_URL=postgresql://postgres.pkihspbkksoggvvwcbam:admin_database2026@aws-1-us-west-2.pooler.supabase.com:6543/postgres

CORS_ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080

JWT_SECRET_KEY=jwt-super-secret-key-change-in-production
```

---

## Ramas del Repositorio

| Rama | Descripción |
|------|-------------|
| `main` | Rama estable |
| `backend` | Desarrollo del backend Django (esta rama) |
| `frontend` | Frontend (separate repo) |
| `database` | Migraciones y scripts SQL |

---

## Contributing

Para contribuir a esta rama:

1. Crear branch desde `backend`: `git checkout -b feature/nueva功能`
2. Implementar cambios siguiendo la arquitectura Defense in Depth
3. Crear tests si aplica
4. Commit y push: `git commit -m "feat: descripción"` → `git push origin backend`
5. Crear Pull Request

---

## Estado: LISTO PARA FASE 1

El proyecto tiene la estructura base creada. El siguiente paso es implementar:
1. Instalar DRF, SimpleJWT, CORS, django-fsm
2. Configurar JWT en settings.py
3. Crear endpoint de login customizado
4. Crear APIs de catálogos