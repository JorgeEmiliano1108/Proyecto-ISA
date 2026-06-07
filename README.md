# ISA Corporativo — Evaluación Discrecional

Plataforma corporativa de evaluación de desempeño por competencias y objetivos, con flujo de aprobaciones multinivel, cálculo de bonos y generación de reportes.

## Repositorio

Este proyecto usa **git worktrees**. Cada subdirectorio principal es un worktree independiente:

| Worktree | Propósito |
|----------|-----------|
| `backend/` | Django 5 + DRF + Supabase (managed=False) |
| `frontend/` | MPA estática (Vanilla JS + Bootstrap 5 + Handsontable + Chart.js) |
| `database/` | Migraciones SQL, seeds, diagrama ER |
| `microservicios/` | 4 microservicios FastAPI (appwo, audit, report) |

## Arquitectura general

```
Frontend (:3000) → Backend Django (:8000) → Supabase (PostgreSQL cloud)
                    ↓
           API externa ISA (SSO/AD/SIARE)
                    ↓
         Microservicios:
           ├── appwo_service (:8001) — Aprobaciones
           ├── audit_service (:8002) — Auditoría
           ├── report_service (:8003) — PDFs
           └── bonus_service (:8004) — Cálculo de logro
```

## Documentación por sección

- `backend/README.md` — API, FSM, RBAC, autenticación JWT RS256
- `frontend/README.md` — Páginas, componentes, localStorage
- `database/README.md` — Modelo de 12 tablas, migraciones, seeds
- `microservicios/README.md` — Visión general de microservicios
