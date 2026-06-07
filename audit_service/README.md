# audit_service — Auditoría y Detección de Anomalías

Microservicio de auditoría para el Sistema de Evaluación Discrecional ISA. Escucha eventos vía Redis Pub/Sub, registra trazabilidad y detecta anomalías usando IA local (Ollama).

## Stack

- **FastAPI** — API REST para consulta de logs de auditoría
- **PostgreSQL** — Tabla propia: `audit_logs`, `ai_anomaly_reports`
- **Redis** — Consumo de eventos (canal `audit_events`) + Pub/Sub
- **Ollama (Phi-3)** — Detección de anomalías en worker async
- **JWT RS256** — Validación de tokens emitidos por el backend Django

## Eventos que consume

| Evento | Origen | Descripción |
|--------|--------|-------------|
| `EVALUATION_SUBMITTED` | Backend Django | Evaluación enviada por empleado |
| `EVALUATION_APPROVED_N1` | Backend Django | Aprobación nivel 1 (evaluador) |
| `EVALUATION_APPROVED_N2` | Backend Django | Aprobación nivel 2 (manager) |
| `EVALUATION_REJECTED` | Backend Django | Evaluación rechazada |
| `REPORT_GENERATED` | Report Service | PDF generado |
| `BONUS_CALCULATED` | Bonus Service | Cálculo de logro |

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/audit/` | Registrar evento de auditoría |
| GET | `/api/v1/audit/resource/{resource_id}` | Consultar historial por recurso |
| GET | `/health` | Health check |

## Workers

- **anomaly_detector** — Worker que consume eventos de Redis y ejecuta IA local (Ollama Phi-3) para detectar patrones anómalos en las transiciones de estado.

## Inicio rápido

```bash
docker compose up --build
# API en: http://localhost:8002
# Docs:  http://localhost:8002/docs
```
