# Microservicios — ISA Corporativo

Conjunto de 4 microservicios independientes para el Sistema de Evaluación Discrecional. Cada uno tiene su propio `docker-compose.yml` y se despliega por separado.

## Servicios

| Servicio | Puerto | Propósito | Estado |
|----------|--------|-----------|--------|
| **appwo_service** | `:8001` | Flujo de aprobaciones multinivel con firmas digitales | Activo |
| **audit_service** | `:8002` | Auditoría de eventos + detección de anomalías con IA | Activo |
| **bonus_service** | `:8004` | Cálculo matemático de bonos y porcentajes de logro | Pospuesto |
| **report_service** | `:8003` | Generación de PDF con WeasyPrint + RAG (Qdrant + Ollama) | Activo |

## Red compartida

Todos los servicios usan `isa_network` como red externa. Crear antes de levantar:

```bash
docker network create isa_network
```

## Despliegue unificado

Los 4 servicios también se pueden levantar desde el `docker-compose.yml` unificado en `backend/` usando profiles:

```bash
cd backend
docker compose --profile all up -d
```

Ver `backend/AGENTS.md` para el detalle de profiles y puertos.

