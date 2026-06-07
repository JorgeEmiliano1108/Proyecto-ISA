# report_service — Generación de Reportes y Analítica

Microservicio que genera PDFs de evaluaciones de desempeño bajo demanda. Usa WeasyPrint para renderizado, Ollama + Qdrant para aumento con RAG (reglas de negocio), y MinIO (S3) para almacenamiento.

## Stack

- **FastAPI** — API REST asíncrona
- **Celery** — Cola de generación (`reports_queue`)
- **Redis** — Broker + Job Store temporal
- **WeasyPrint** — HTML → PDF con estilos corporativos (Jinja2)
- **Qdrant** — Base vectorial para búsqueda semántica (RAG)
- **Ollama (Phi-3 + nomic-embed-text)** — LLM local para resúmenes inteligentes
- **MinIO (S3-compatible)** — Almacenamiento persistente de PDFs
- **Prometheus + Alertmanager** — Métricas y alertas
- **JWT RS256** — Validación de tokens emitidos por el backend Django

## Arquitectura

Sigue **Arquitectura Hexagonal**:

```
HTTP Request → FastAPI → Application (use cases: generate, status)
                            ↓
                      Domain (entities, ports)
                            ↓
                Infrastructure:
                  ├── HTTP Repository (consume evaluaciones vía Django API)
                  ├── S3 Adapter (MinIO)
                  ├── PDF Adapter (WeasyPrint + Jinja2)
                  ├── RAG Adapter (Qdrant + Ollama)
                  ├── Job Store (Redis)
                  ├── Sanitizer (LFPDPPP)
                  └── Monitoring (Prometheus metrics)
```

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/generate` | Encolar generación de PDF |
| GET | `/api/v1/status/{job_id}` | Consultar estado + URL de descarga |
| POST | `/api/v1/rules/upload` | Subir PDF de reglas de negocio (RAG) |
| DELETE | `/api/v1/rules/{profile_name}` | Eliminar perfil de reglas |
| POST | `/api/v1/assets/logos/{institution_id}` | Subir logo institucional |
| DELETE | `/api/v1/assets/logos/{institution_id}` | Eliminar logo |
| GET | `/metrics` | Métricas Prometheus |

## Flujo de generación

1. `POST /generate` → encola tarea en Celery, retorna `job_id`
2. Worker Celery:
   a. Fetch datos de evaluación vía HTTP al backend Django
   b. Sanitiza datos personales (LFPDPPP)
   c. Consulta reglas de negocio en Qdrant (RAG)
   d. Genera resumen con Ollama Phi-3
   e. Renderiza HTML con Jinja2
   f. Convierte a PDF con WeasyPrint
   g. Sube a MinIO (S3)
   h. Guarda resultado en Redis Job Store
3. `GET /status/{job_id}` → polling hasta `SUCCESS`, retorna `download_url` firmado

## Inicio rápido

```bash
docker compose up --build
# API en: http://localhost:8003
# Docs:  http://localhost:8003/docs
# MinIO: http://localhost:9003
# Qdrant: http://localhost:6334
```

> Requiere el backend Django corriendo (`:8000`) para obtener datos de evaluaciones.
