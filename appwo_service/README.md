# appwo_service — Approval Workflow Service

Microservicio de aprobaciones multinivel para el Sistema de Evaluación Discrecional ISA. Gestiona el flujo de firmas electrónicas y transiciones de estado de las evaluaciones.

## Stack

- **FastAPI** — API REST asíncrona
- **Celery** — Tareas en segundo plano (notificaciones, recordatorios)
- **PostgreSQL** — Tablas propias: `evaluation_workflows`, `approval_signatures`
- **Redis** — Broker de Celery + caché
- **JWT RS256** — Validación de tokens emitidos por el backend Django

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/evaluations/{id}/approve` | Aprobar evaluación con firma digital |
| POST | `/api/v1/evaluations/{id}/reject` | Rechazar evaluación con justificación |
| POST | `/api/v1/evaluations/{id}/review` | Marcar en revisión |

## Arquitectura

```
HTTP Request → FastAPI → Application (use cases) → Domain (entities + state machine)
                                                        ↓
                                              Infrastructure:
                                                ├── Database (PostgreSQL)
                                                ├── Redis (Celery + caché)
                                                └── HTTP Client (User Service → Django backend)
```

## Inicio rápido

```bash
docker compose up --build
# API en: http://localhost:8001
# Docs:  http://localhost:8001/docs
```
