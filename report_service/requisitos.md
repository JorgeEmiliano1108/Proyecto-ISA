# Especificación de Requisitos - Reports Service (ISA Corporativo)

> **Versión:** 1.0 | **Fecha:** 2026-04-14 | **Servicio:** `reports_service` (Puerto 8003)

---

## 1. REQUISITOS FUNCIONALES (RF)

### 1.1 Generación de Reportes

| ID | Descripción | Criterio de Aceptación |
|----|-------------|------------------------|
| RF-01 | Encolar generación de reporte PDF | `POST /generate` retorna `202 Accepted` con `job_id` en <500ms |
| RF-02 | Consultar estado del job | `GET /status/{job_id}` retorna `QUEUED\|STARTED\|SUCCESS\|FAILED` |
| RF-03 | Generar PDF asíncrono via Celery | Tarea `generate_report_task` completa en <300s (soft_limit=600s) |
| RF-04 | Renderizar PDF con WeasyPrint | HTML convertido a bytes binarios sin tocar disco local |
| RF-05 | Subir PDF a S3/MinIO | `S3Adapter.upload_pdf()` persiste archivo en bucket `reports` |
| RF-06 | Generar URL pre-firmada | `generate_presigned_url()` con expiración de 300s (5 min) |

### 1.2 Seguridad y Cumplimiento (LFPDPPP)

| ID | Descripción | Criterio de Aceptación |
|----|-------------|------------------------|
| RF-07 | Prevenir IDOR en consultas SQL | Repository filtra por `requester_id` y `requester_role` en WHERE clause |
| RF-08 | Enmascarar PII antes de IA | `DataSanitizer.mask_name()` → "J*** P****", `mask_email()` → "j****@domain.com" |
| RF-09 | Autodestrucción asíncrona de archivos | Worker `delete_ephemeral_report` ejecuta `S3Adapter.delete_pdf()` a los 300s |
| RF-10 | Auditoría inmutable de reportes | Tabla `isa_reports_audit` persiste `job_id`, `status`, `result_url` |

### 1.3 Inteligencia Artificial y RAG

| ID | Descripción | Criterio de Aceptación |
|----|-------------|------------------------|
| RF-11 | Generar layout con Phi-3 | Ollama retorna JSON estructurado (`ReportLayoutSchema`) |
| RF-12 | Retrieval de reglas corporativas | Qdrant busca por embedding en colección `isa_reports_styles` |
| RF-13 | Upsert de reglas PDF → Vector DB | `POST /rules/upload` extrae texto y persiste en Qdrant |
| RF-14 | Delete de reglas por perfil | `DELETE /rules/{profile_name}` elimina vectors filtrados |
| RF-15 | Modo contingencia IA | Si LLM falla, retorna layout genérico con mensaje de error |

### 1.4 Gestión de Activos

| ID | Descripción | Criterio de Aceptación |
|----|-------------|------------------------|
| RF-16 | Subir logos institucionales | `POST /assets/logos/{institution_id}` acepta PNG/JPEG |
| RF-17 | Eliminar logos | `DELETE /assets/logos/{institution_id}` elimina archivo local |
| RF-18 | Validación de tipos MIME | Solo `image/png` y `image/jpeg` aceptados en uploads |

### 1.5 Autenticación

| ID | Descripción | Criterio de Aceptación |
|----|-------------|------------------------|
| RF-19 | Validación JWT Bearer | Todos los endpoints protegidos con `verify_token()` |
| RF-20 | Refresh de tokens | Retorna `401` con header `WWW-Authenticate` en token expirado |

---

## 2. REQUISITOS NO FUNCIONALES (RNF)

### 2.1 Rendimiento

| ID | Atributo | Requisito | Métrica |
|----|----------|-----------|---------|
| RNF-01 | Latencia API | p99 endpoint síncronos | < 500ms |
| RNF-02 | Throughput | Jobs simultáneos | ≥ 10 concurrentes sin degradación |
| RNF-03 | LLM Timeout | Tiempo máximo espera Ollama | 120s por request |
| RNF-04 | Worker Soft Limit | Tiempo máximo tarea Celery | 600s (configurable) |

### 2.2 Escalabilidad

| ID | Atributo | Requisito | Implementación |
|----|----------|-----------|----------------|
| RNF-05 | Workers horizontales | N réplicas Celery | Cola dedicada `reports_queue` |
| RNF-06 | Prefetch rate | Control de concurrencia | `worker_prefetch_multiplier=1` |
| RNF-07 | Aislamiento de colas | No colisionar con Django | Cola explícita en `task_default_queue` |

### 2.3 Seguridad

| ID | Atributo | Requisito | Evidencia |
|----|----------|-----------|-----------|
| RNF-08 | Algoritmo JWT | RS256 (o HS256 con secret ≥256b) | `settings.ALGORITHM` |
| RNF-09 | Rate Limiting | Por usuario | **NO IMPLEMENTADO** (Gap) |
| RNF-10 | Encryption at Rest | Datos PostgreSQL | **NO IMPLEMENTADO** (Gap) |
| RNF-11 | TLS en tránsito | Ollama ↔ API | Redes Docker bridge (dev) |

### 2.4 Resiliencia

| ID | Atributo | Requisito | Implementación |
|----|----------|-----------|----------------|
| RNF-12 | Retry de tareas | Max reintentos | `max_retries=2`, `retry_backoff=True` |
| RNF-13 | Jitter en retry | Evitar thundering herd | `retry_jitter=True` |
| RNF-14 | Ack tardío | Procesar solo si completa | `task_acks_late=True` |
| RNF-15 | Fallback S3 lifecycle | Red de seguridad borrado | **NO IMPLEMENTADO** (Gap crítico) |
| RNF-16 | Dead Letter Queue | Mensajes fallidos | **NO CONFIGURADO** (Gap) |

### 2.5 Observabilidad

| ID | Atributo | Requisito | Implementación |
|----|----------|-----------|----------------|
| RNF-17 | Logging estructurado | JSON logs con job_id | `logging.getLogger("ms_reports.*")` |
| RNF-18 | Trazas distribuidas | OpenTelemetry | **NO IMPLEMENTADO** (Gap) |
| RNF-19 | Métricas Prometheus | Key metrics | **NO IMPLEMENTADO** (Gap) |
| RNF-20 | Alerting | Umbrales de SLA | **NO IMPLEMENTADO** (Gap) |

### 2.6 Disponibilidad

| ID | Atributo | Requisito | Métrica |
|----|----------|-----------|---------|
| RNF-21 | SLO API | Uptime mensual | ≥ 99.5% |
| RNF-22 | Healthcheck | Readiness probes | Docker healthcheck configurado |
| RNF-23 | Graceful shutdown | Finalizar tareas en curso | **NO DOCUMENTADO** (Gap) |

### 2.7 Compliance (LFPDPPP)

| ID | Atributo | Requisito | Evidencia |
|----|----------|-----------|-----------|
| RNF-24 | Principio de minimización | Solo datos necesarios | `DataSanitizer` elimina PII |
| RNF-25 | Retención cero en IA | No PII a modelos externos | Ollama on-prem, no cloud |
| RNF-26 | Ejercicio de derechos ARCO | Endpoints de eliminación | **NO IMPLEMENTADO** (Gap) |

### 2.8 Infraestructura (12-Factor)

| ID | Factor | Cumplimiento | Evidencia |
|----|--------|--------------|-----------|
| RNF-27 | Codebase | ✅ Monorepo | 3 servicios en un repo |
| RNF-28 | Dependencies | ✅ Explícitas | `pyproject.toml` |
| RNF-29 | Config | ✅ Environment | `pydantic-settings` + `.env` |
| RNF-30 | Backing services | ✅ Treat as attached | PostgreSQL, Redis, S3 |
| RNF-31 | Build/Release/Run | ⚠️ Parcial | Dockerfile, sin CI/CD stages |
| RNF-32 | Processes | ✅ Stateless | Redis para estado |
| RNF-33 | Port binding | ✅ | Puerto 8003 |
| RNF-34 | Concurrency | ✅ | Celery workers |
| RNF-35 | Disposability | ⚠️ Gap | Sin graceful shutdown |
| RNF-36 | Dev/Prod parity | ⚠️ Parcial | MinIO local vs S3 prod |
| RNF-37 | Logs | ✅ | stdout/stderr + audit table |
| RNF-38 | Admin processes | ⚠️ Gap | Sin migration scripts versionados |

---

## 3. ARQUITECTURA HEXAGONAL - MAPA DE COMPONENTES

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CAPA DE ENTRADA (INPUT)                        │
│  ┌──────────────────┐  ┌──────────────────────┐  ┌──────────────────┐  │
│  │ routers.py       │  │ tasks.py (Celery)    │  │ input.py         │  │
│  │ POST /generate   │  │ generate_report_task │  │ InputPorts       │  │
│  │ GET /status      │  │ delete_ephemeral...  │  │                  │  │
│  └────────┬─────────┘  └──────────┬───────────┘  └──────────────────┘  │
└───────────┼────────────────────────┼────────────────────────────────────┘
            │                        │
            ▼                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           CASOS DE USO (DOMINIO)                         │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ generate_evaluation_report.py                                      │ │
│  │ 1. get_evaluation_full_data()  ← IDOR validation                  │ │
│  │ 2. DataSanitizer.sanitize()   ← PII mask (LFPDPPP)               │ │
│  │ 3. qdrant.get_style_rules()    ← RAG retrieval                    │ │
│  │ 4. llm.generate_layout()       ← Phi-3 structured JSON            │ │
│  │ 5. pdf_gen.build_html()        ← Jinja2 template                  │ │
│  │ 6. cloud_storage.upload()      ← S3 ephemeral                    │ │
│  │ 7. delete_ephemeral_report()   ← 300s countdown                   │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
            │                        │
            ▼                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           CAPA DE SALIDA (OUTPUT)                        │
│  ┌─────────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐  │
│  │ ISARepositoryPort│ │ CloudStorage │ │ VectorDBPort │ │ LLMPort    │  │
│  │ (PostgreSQL)     │ │ (S3/MinIO)   │ │ (Qdrant)     │ │ (Ollama)   │  │
│  └─────────────────┘ └──────────────┘ └──────────────┘ └────────────┘  │
│  ┌─────────────────┐ ┌──────────────┐ ┌──────────────────────────────┐│
│  │ JobStorePort    │ │ PDFGenerator │ │ output.py                     ││
│  │ (Redis)         │ │ (WeasyPrint) │ │ OutputPorts contracts         ││
│  └─────────────────┘ └──────────────┘ └──────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. FLUJO DE DATOS - CICLO DE VIDA EFÍMERO

```
┌────────┐     ┌─────────┐     ┌──────────┐     ┌────────┐     ┌────────┐
│ CLIENT │────▶│ JWT验证  │────▶│ Celery   │────▶│ Worker │────▶│Redis   │
│ (API)  │     │verify   │     │ Enqueue  │     │        │     │ Job    │
└────────┘     └─────────┘     └──────────┘     └────────┘     │Store   │
   ▲                                           │                └────────┘
   │                                           ▼                     │
   │              ┌──────────────────────────────────────┐           │
   │              │          WORKER TASK FLOW             │           │
   │              │                                      │           │
   │              │  1. get_evaluation_full_data()        │           │
   │              │     ↑ IDOR validation (requester)    │           │
   │              │                                      │           │
   │              │  2. DataSanitizer.sanitize()         │           │
   │              │     ↑ PII masked (names, emails)     │           │
   │              │                                      │           │
   │              │  3. Qdrant.get_style_rules()         │           │
   │              │     ↑ RAG context retrieval          │           │
   │              │                                      │           │
   │              │  4. Ollama.generate_layout()          │           │
   │              │     ↑ Phi-3 JSON (no PII)           │           │
   │              │                                      │           │
   │              │  5. WeasyPrint.generate_pdf()         │           │
   │              │     ↑ PDF in-memory bytes            │           │
   │              │                                      │           │
   │              │  6. S3Adapter.upload_pdf()           │           │
   │              │     ↑ Object stored in bucket        │           │
   │              │                                      │           │
   │              │  7. generate_presigned_url(300s)     │           │
   │              │     ↑ Temporary download link        │           │
   │              │                                      │           │
   │              │  8. delete_ephemeral_report(300s)    │           │
   │              │     ↑ Scheduled destruction          │           │
   │              └──────────────────────────────────────┘           │
   │                                           │                       │
   └───────────────────────────────────────────┘                       │
                                                                       │
                         ┌──────────────────────────────────────┐      │
                         │         S3 LIFECYCLE                │      │
                         │                                      │      │
                         │  T=0:    [report_uuid.pdf] CREATED  │      │
                         │                                      │      │
                         │  T=300s: Celery deletes from S3     │◀─────┘
                         │          + PostgreSQL status=DONE    │
                         │                                      │
                         │  T>300: If worker fails:             │
                         │          S3 Lifecycle Policy         │
                         │          acts as fallback           │
                         │          (NOT IMPLEMENTED)          │
                         └──────────────────────────────────────┘
```

---

## 5. GAPS CONOCIDOS

| Prioridad | Gap | Impacto | Referencia |
|-----------|-----|---------|------------|
| 🔴 CRÍTICO | `s3_adapter.py` no existe | No se pueden subir/eliminar PDFs | `tasks.py:19,80` |
| 🔴 CRÍTICO | Sin S3 Lifecycle Policy | Archivos huérfanos si worker falla | `delete_ephemeral_report` |
| 🟡 ALTA | Sin rate limiting | DDoS/DoS vulnerability | OWASP API Security |
| 🟡 ALTA | Sin encryption-at-rest PG | Datos sensibles en disco | LFPDPPP Art. 17 |
| 🟡 ALTA | Sin Prometheus metrics | No visibilidad de SLAs | RNF-19 |
| 🟡 ALTA | Sin OpenTelemetry | Sin trazas distribuidas | RNF-18 |
| 🟡 ALTA | Sin RBAC centralizado | Roles hardcoded en SQL | `repository.py:84-88` |
| 🟡 ALTA | JWT usa HS256 en config | Potencial weakness | `config.py:17` |
| 🟠 MEDIA | Sin graceful shutdown | Tareas interrumpidas | RNF-35 |
| 🟠 MEDIA | Sin Dead Letter Queue | Mensajes perdidos | RNF-16 |
| 🟠 MEDIA | Sin migration scripts | Alembic no usado | RNF-38 |
| 🟠 MEDIA | Sin alerting | No notificaciones de SLA | RNF-20 |
| 🟠 MEDIA | Sin logout/revocación JWT | Sesiones persistentes | OWASP Session Mgmt |
| 🟡 MEDIA | Texto libre no sanitizado | PII en comentarios | `sanitizer.py:46-48` |
| 🟡 MEDIA | Sin ABAC | Solo RBAC simple | OWASP DS-06 |

---

## 6. MATRIZ DE DEPENDENCIAS EXTERNAS

| Servicio | Host (Docker) | Puerto | Tipo | Criticidad |
|----------|---------------|--------|------|------------|
| reports_db | reports_db | 5432 | PostgreSQL 16 | CRÍTICA |
| reports_redis | reports_redis | 6379 | Redis 7 | CRÍTICA |
| ollama_reports | ollama_reports | 11434 | Ollama | CRÍTICA |
| reports_qdrant | reports_qdrant | 6333 | Qdrant | MEDIA |
| minio | minio | 9000 | MinIO/S3 | CRÍTICA |
