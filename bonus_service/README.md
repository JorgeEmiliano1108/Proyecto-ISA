# bonus_service — Documentación Técnica

**Versión:** 1.0.0 | **Autor:** Cruz Bravo Cruz Felipe | **Puerto:** `8002`

> Motor matemático del Sistema ISA. Calcula, persiste y audita bonificaciones corporativas con arquitectura hexagonal y procesamiento vectorizado.

---

## Estructura del Proyecto

```
bonus_service/
├── alembic/                        # Migraciones de BD (tabla bonos)
├── app/
│   ├── core/                       # Config, seguridad JWT, manejo de errores
│   ├── domain/                     # Núcleo matemático puro (NumPy/Pandas)
│   │   ├── calculator.py           # Fórmulas financieras vectorizadas
│   │   ├── entities.py             # Entidad inmutable BonusCalculation
│   │   └── exceptions.py           # Excepciones de negocio
│   ├── application/                # Casos de uso + contratos (puertos)
│   ├── infrastructure/
│   │   ├── api/                    # FastAPI: routers, schemas, dependencias
│   │   ├── database/               # SQLAlchemy async + repositorios
│   │   └── messaging/              # Publicador de eventos Redis
│   └── workers/                    # Celery: configuración + tareas batch
└── tests/
    ├── unit/                       # Tests del calculator.py (sin BD)
    ├── integration/                # Tests de repositorios
    └── e2e/                        # Tests de endpoints HTTP
```

---

## Fórmula Financiera

```
factor_desempeño   = calificacion_global / 5.0        (0.0 – 1.0)
factor_corporativo = impacto_ebitda                   (0.0 – 1.0)
multiplicador      = (factor_desempeño × 0.60) + (factor_corporativo × 0.40)
monto_bono         = salario_base_snapshot × multiplicador
```

---

## Instalación y Despliegue

### 1. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con los valores reales
```

### 2. Levantar el ecosistema completo
```bash
docker compose up -d --build
```

### 3. Ejecutar migraciones
```bash
docker compose exec bonus_api alembic upgrade head
```

### 4. Validar en Swagger UI
```
http://localhost:8002/docs
```
Hacer clic en **Authorize** → ingresar el JWT → probar endpoints.

### 5. Monitorear workers Celery
```bash
docker compose logs -f bonus_celery_worker
```

### 6. Apagar el servicio
```bash
docker compose down
```

---

## Endpoints Principales

| Método | Ruta | Descripción | Rol requerido |
|--------|------|-------------|---------------|
| `POST` | `/api/v1/bonus/calculate` | Cálculo individual | `admin`, `finanzas` |
| `POST` | `/api/v1/bonus/calculate/batch` | Cálculo masivo (async) | `admin`, `finanzas` |
| `GET`  | `/api/v1/bonus/report/{periodo}` | Reporte consolidado | `admin`, `finanzas`, `sistemas` |
| `GET`  | `/api/v1/bonus/health` | Health check | Público |

---

## Ejecutar Pruebas

```bash
# Instalar dependencias de desarrollo
pip install -r requirements.txt

# Correr todos los tests
pytest tests/ -v

# Solo unitarios (sin BD)
pytest tests/unit/ -v
```

---

## Arquitectura

```
HTTP Request
     │
     ▼
[API Layer - FastAPI]          ← Validación JWT + Pydantic
     │
     ▼
[Application Layer]            ← Orquestación (Casos de Uso)
     │
     ▼
[Domain Layer]                 ← Fórmulas puras (NumPy/Pandas)
     │
     ├──► [DB Write - PostgreSQL]    tabla: bonos
     ├──► [DB Read  - PostgreSQL]    tabla: evaluaciones (solo lectura)
     └──► [Redis]                    eventos → audit_service
```
