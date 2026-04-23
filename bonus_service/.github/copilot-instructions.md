# Bonus Service — Copilot Agent Instructions

**Project:** bonus_service  
**Architecture:** Hexagonal + Clean Architecture  
**Stack:** FastAPI, SQLAlchemy async, Celery, Redis, PostgreSQL  
**Security Level:** Confidential (LFPDPPP compliance)  
**Date:** April 2026

---

## Quick Start Commands

```bash
# Setup
docker compose up -d --build
docker compose exec bonus_api alembic upgrade head

# Testing
pytest tests/unit/ -v                  # Pure domain (no DB)
pytest tests/integration/ -v           # With test DB  
pytest tests/e2e/ -v                   # Full HTTP endpoints

# Development
docker compose logs -f bonus_api       # Watch API logs
http://localhost:8002/docs             # Swagger UI with JWT auth

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head

# Celery batch processing
celery -A app.workers.celery_app worker --loglevel=info
```

---

## Architecture Layers & Dependencies

```
DOMAIN (Pure business logic — NO framework imports)
├─ calculator.py          ← Vectorized fiancial formulas (NumPy/Pandas)
├─ entities.py            ← Immutable BonusCalculation dataclass
└─ exceptions.py          ← Business exceptions only

APPLICATION (Orchestration layer — NO FastAPI/DB imports)
├─ use_cases/
│  ├─ calculate_bonus.py  ← Bonus calculation choreography
│  └─ get_bonus_report.py ← Report aggregation
└─ ports/                 ← Abstract interfaces for:
   ├─ input.py            ← InputPort (command contracts)
   └─ output.py           ← OutputPort (repository, publisher)

INFRASTRUCTURE (Concrete implementations — ALL framework deps here)
├─ api/
│  ├─ routers.py          ← FastAPI endpoints + RBAC decorators
│  ├─ schemas.py          ← Pydantic models for request/response
│  └─ middleware/         ← Rate limiting, security headers
├─ database/
│  ├─ models.py           ← SQLAlchemy ORM models
│  ├─ repository.py       ← Async repository with encryption/decryption
│  └─ database.py         ← Connection management
└─ messaging/
   └─ publisher.py        ← Redis event publishing
```

**Key Principle:** Domain never imports from Application or Infrastructure. Application never imports framework-specific code. Infrastructure depends on both.

---

## Critical Patterns & Rules

### 1. **Encryption at Rest (LFPDPPP Art. 18-19)**
- **ENCRYPTED** fields: `salario_base_snapshot`, `monto_final_bono`
- **ENCRYPTION METHOD:** Fernet AES-256 (via `cryptography` package)
- **WHERE:** Encryption/decryption happens ONLY in `repository.py` layer
- **NEVER:** Store encrypted data in domain entities; decrypt before passing to use case

```python
# ✗ WRONG: Storing encrypted in entity
bonus = BonusCalculation(..., salario_base=encrypted_value)

# ✓ CORRECT: Decrypt in repository, pass plaintext to use case
salario_plaintext = self._decrypt_decimal(db_bonus.salario_base_encrypted)
bonus = BonusCalculation(..., salario_base=salario_plaintext)
```

### 2. **JWT Role-Based Access Control (Secure-by-Design)**
- Uses RS256 (public key) — Django-generated, inject via dependency
- Roles: `admin`, `finanzas`, `sistemas`
- ALL endpoints require `@Depends(verify_token)` + `@Depends(require_role(...))`

```python
# Every endpoint must validate:
@router.post("/api/v1/bonus/calculate")
async def calculate_bonus(
    payload: CalculateRequest,
    user: CurrentUserDep = Depends(verify_token),
    _: None = Depends(require_role("admin", "finanzas")),
):
    # Use user.user_id for audit trail (calculado_por)
```

### 3. **Idempotency & Audit Trail**
- Every bonus write must include `calculado_por: str` (user_id from JWT)
- Check existence before calculation to prevent double-bonuses
- Events published to Redis after successful writes

### 4. **Async/Await Discipline**
- ALL I/O operations MUST be `await`ed
- Repository methods are `async def`
- Database sessions are context-managed with `async with`
- No blocking calls in async context (e.g., no `time.sleep`)

### 5. **Batch Processing (Vectorized)**
- Use NumPy/Pandas in `calculator.py` for large datasets
- Celery tasks wrap calculator calls with `task_eager_mode=False` (production)
- Add retries: `@celery_app.task(max_retries=3, default_retry_delay=60)`

### 6. **Immutable Domain Entities**
- `BonusCalculation` is a frozen dataclass — cannot be modified
- Create new instance if value changes:

```python
# ✗ WRONG
bonus.monto = new_value

# ✓ CORRECT
bonus = BonusCalculation(..., monto=new_value)
```

### 7. **Error Handling (Layered)**
```python
# Domain raises domain exceptions
raise InvalidEBITDAException(f"EBITDA must be 0-100, got {value}")

# Infrastructure maps to HTTP via exception handler
@app.add_exception_handler(InvalidEBITDAException, ...)
# → returns {"detail": "...", "code": "INVALID_EBITDA"}
```

---

## Naming Conventions

| Entity Type | Pattern | Example |
|------------|---------|---------|
| Function | `verbo_*()`  snake_case | `calcular_bono()`, `obtener_reporte()` |
| Class | `XxxModel`, `XxxRepository` | `BonusCalculation`, `BonusRepository` |
| Constant | `UPPER_SNAKE_CASE` | `PESO_DESEMPENIO = 0.60` |
| Private | `_función_privada()` | `_decrypt_decimal()` |
| Boolean param | `es_*`, `puede_*` | `es_retrocálculo`, `puede_editar` |
| Import | Relative within package, absolute across | `from .calculator import ...` / `from app.domain.calculator import ...` |

**NEVER use wildcard imports**: ❌ `from app.domain import *` → ✓ Explicit imports

---

## Common Pitfalls ⚠️

| ❌ Problem | 🔧 Solution | 📍 Where |
|-----------|-----------|---------|
| Domain imports FastAPI in calculator | Raise domain exception, handle in API layer | `calculator.py` + `routers.py` |
| Missing `await` on async repo call | Add `await` before repository calls | `use_cases/` |
| Modifying frozen dataclass | Recreate with new value | `domain/entities.py` |
| Forgetting to encrypt salary data | Call `_encrypt_decimal()` before DB write | `infrastructure/database/repository.py` |
| No CASCADE delete on FK | Add `ondelete="CASCADE"` to Column/ForeignKey | `infrastructure/database/models.py` |
| Forgetting audit user ID | Always capture `user_id` from JWT context | `routers.py` |
| No retry logic in Celery tasks | Add `max_retries=3, default_retry_delay=60` | `workers/tasks.py` |
| Rate limiting missing from endpoint | Wrap with rate_limit_middleware | `infrastructure/api/routers.py` |
| Hardcoded config values | Load from `.env` or Docker Secrets | `app/core/config.py` |
| Computing with encrypted values | Decrypt first, compute second | `repository.py` then `use_case` |

---

## File Reference Guide

| Purpose | File | Key Patterns |
|---------|------|--------------|
| **Bonus Calculation Formula** | [app/domain/calculator.py](app/domain/calculator.py) | NumPy vectorization, 0-1 normalization |
| **Domain Entity** | [app/domain/entities.py](app/domain/entities.py) | Frozen dataclass, immutable |
| **Use Case Orchestration** | [app/application/use_cases/calculate_bonus.py](app/application/use_cases/calculate_bonus.py) | Choreography, ports |
| **API Endpoints** | [app/infrastructure/api/routers.py](app/infrastructure/api/routers.py) | JWT, RBAC, rate-limit, OpenAPI docs |
| **Database Models** | [app/infrastructure/database/models.py](app/infrastructure/database/models.py) | Encrypted columns, audit fields |
| **Encryption/Decryption** | [app/infrastructure/database/repository.py](app/infrastructure/database/repository.py) | Fernet, async queries, Depends |
| **Configuration** | [app/core/config.py](app/core/config.py) | Pydantic-settings, .env validation |
| **JWT Security** | [app/core/security.py](app/core/security.py) | verify_token, require_role, RS256 |
| **Unit Tests** | [tests/unit/test_calculator.py](tests/unit/test_calculator.py) | No DB, pure functions |
| **Integration Tests** | [tests/integration/](tests/integration/) | Test container, async fixtures |
| **E2E Tests** | [tests/e2e/test_bonus_endpoints.py](tests/e2e/test_bonus_endpoints.py) | Full HTTP flow with JWT |
| **Security Policy** | [docs/POLITICA_SEGURIDAD.md](docs/POLITICA_SEGURIDAD.md) | LFPDPPP compliance, data classes |

---

## Security Checklist

Before every commit:

- [ ] No domain layer imports FastAPI, SQLAlchemy, or Redis
- [ ] All encrypted fields use `_encrypt_decimal()` / `_decrypt_decimal()` in repository
- [ ] All endpoints have `@Depends(verify_token)` + role check
- [ ] Audit trail: `calculado_por` populated from JWT `user.user_id`
- [ ] No hardcoded secrets — load from `.env` or Docker Secrets
- [ ] Async I/O all use `await`
- [ ] Tests don't import infrastructure directly (use mocks)
- [ ] Error messages don't expose internal implementation
- [ ] Rate limiting middleware present on public endpoints
- [ ] Frozen dataclasses not mutated with direct assignment

---

## Development Workflow

1. **Start environment:** `docker compose up -d --build`
2. **Run migrations:** `docker compose exec bonus_api alembic upgrade head`
3. **Write domain logic first** (pure functions, no I/O)
4. **Add unit tests** (`pytest tests/unit/`)
5. **Implement use case** (orchestration in application layer)
6. **Add integration tests** (`pytest tests/integration/`)
7. **Expose via API** (routers in infrastructure)
8. **Add e2e tests** (`pytest tests/e2e/`)
9. **Security review:** Encryption, RBAC, audit trail
10. **Deploy:** `docker compose up -d` (with updated images)

---

## When to Ask for Clarification

Ask the user if these are ambiguous:
- Which role should access a new endpoint?
- Is this new data sensitive (encrypt) or corporate metric (clear)?
- Should batch processing be async (Celery) or sync?
- Is this a breaking API change that needs versioning?

---

## Related Documentation

- **Technical README:** [README.md](README.md)
- **Security Policy:** [docs/POLITICA_SEGURIDAD.md](docs/POLITICA_SEGURIDAD.md)
- **Database Migrations:** [alembic/env.py](alembic/env.py)
- **Architecture Details:** See `Architecture Layers & Dependencies` section above

---

**Version:** 1.0.0 | **Last Updated:** April 2026  
**Maintained by:** Copilot Agent  
**Feedback:** If you find patterns missing or rules unclear, update this file.
