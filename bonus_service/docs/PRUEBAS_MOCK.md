# 🧪 Guía de Pruebas - Bonus Service (Modo Desarrollo)

## ⚠️ MODALIDAD DE PRUEBAS SIN BASE DE DATOS

Este documento explica cómo probar el `bonus_service` **sin necesidad de tener la base de datos configurada**.

---

## 🎯 ENDPOINTS MOCKEADOS DISPONIBLES

### 1. **Obtener Token JWT Mockeado**

**Endpoint:** `POST /api/v1/auth/mock-login`  
**Requisitos:** `DEBUG_MODE=true`  
**Base de datos:** NO requerida

```bash
curl -X POST http://localhost:8002/api/v1/auth/mock-login \
  -H "Content-Type: application/json" \
  -d '{"username": "cualquier-valor", "password": "cualquier-valor"}'
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "roles": ["admin", "finanzas"]
}
```

**Nota:** Este endpoint **NO valida credenciales**. Cualquier username/password genera un token válido con roles de admin.

---

### 2. **Calcular Bono SIN Base de Datos**

**Endpoint:** `POST /api/v1/auth/mock-calculate`  
**Requisitos:** `DEBUG_MODE=true`  
**Base de datos:** NO requerida  
**Autenticación:** NO requerida

```bash
curl -X POST http://localhost:8002/api/v1/auth/mock-calculate \
  -H "Content-Type: application/json" \
  -d '{
    "evaluacion_id": "550e8400-e29b-41d4-a716-446655440000",
    "calificacion_global": 4.0
  }'
```

**Respuesta:**
```json
{
  "evaluacion_id": "550e8400-e29b-41d4-a716-446655440000",
  "calificacion_global": 4.0,
  "porcentaje_logro": 80.0,
  "fecha_calculo": "2026-06-02T14:25:43.683424"
}
```

**Fórmula:** `porcentaje_logro = calificacion_global × 20`

---

### 3. **Generar Token desde Script CLI**

**Ubicación:** `scripts/generate_test_token.py`  
**Requisitos:** Python 3.9+

```bash
# Generar token por defecto
python3 scripts/generate_test_token.py

# Especificar usuario y roles
python3 scripts/generate_test_token.py --user admin --roles admin,finanzas

# Token que expira en 48 horas
python3 scripts/generate_test_token.py --expires 48

# Modo silencioso (solo el token)
python3 scripts/generate_test_token.py --quiet
```

**Ejemplo de uso:**
```bash
# Generar token y usarlo inmediatamente
TOKEN=$(python3 scripts/generate_test_token.py --quiet)

curl -X POST http://localhost:8002/api/v1/bonus/calculate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"evaluacion_id": "uuid", "calificacion_global": 4.0}'
```

---

## 📋 EJEMPLOS COMPLETOS DE PRUEBAS

### Ejemplo 1: Calificación 4.0 → 80% de logro

```bash
curl -X POST http://localhost:8002/api/v1/auth/mock-calculate \
  -H "Content-Type: application/json" \
  -d '{"evaluacion_id": "uuid-1", "calificacion_global": 4.0}'
```

**Respuesta esperada:**
```json
{
  "evaluacion_id": "uuid-1",
  "calificacion_global": 4.0,
  "porcentaje_logro": 80.0,
  "fecha_calculo": "2026-06-02T14:25:43.683424"
}
```

---

### Ejemplo 2: Calificación 5.0 → 100% de logro

```bash
curl -X POST http://localhost:8002/api/v1/auth/mock-calculate \
  -H "Content-Type: application/json" \
  -d '{"evaluacion_id": "uuid-2", "calificacion_global": 5.0}'
```

**Respuesta esperada:**
```json
{
  "evaluacion_id": "uuid-2",
  "calificacion_global": 5.0,
  "porcentaje_logro": 100.0,
  "fecha_calculo": "2026-06-02T14:25:43.683424"
}
```

---

### Ejemplo 3: Calificación inválida (0.5) → Error

```bash
curl -X POST http://localhost:8002/api/v1/auth/mock-calculate \
  -H "Content-Type: application/json" \
  -d '{"evaluacion_id": "uuid-3", "calificacion_global": 0.5}'
```

**Respuesta esperada:**
```json
{
  "detail": [
    {
      "type": "greater_than_equal",
      "loc": ["body", "calificacion_global"],
      "msg": "Input should be greater than or equal to 1",
      "ctx": {"ge": 1.0}
    }
  ]
}
```

---

### Ejemplo 4: Usar token mockeado con endpoint protegido

```bash
# Paso 1: Obtener token
TOKEN=$(curl -s -X POST http://localhost:8002/api/v1/auth/mock-login \
  -H "Content-Type: application/json" \
  -d '{"username": "test-user", "password": "test"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Paso 2: Usar token en endpoint protegido (aún requiere BD configurada)
curl -X POST http://localhost:8002/api/v1/bonus/calculate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"evaluacion_id": "uuid-4", "calificacion_global": 4.0}'
```

---

## 🎯 RANGO DE CALIFICACIONES VÁLIDAS

| Calificación | Porcentaje de Logro | Estado |
|--------------|---------------------|--------|
| 1.0 | 20% | ✅ Válido (mínimo) |
| 2.0 | 40% | ✅ Válido |
| 3.0 | 60% | ✅ Válido |
| 4.0 | 80% | ✅ Válido |
| 5.0 | 100% | ✅ Válido (máximo) |
| 0.5 | - | ❌ Inválido (< 1.0) |
| 5.5 | - | ❌ Inválido (> 5.0) |
| -1.0 | - | ❌ Inválido (< 1.0) |

---

## 🔧 CONFIGURACIÓN REQUERIDA

### 1. Activar modo DEBUG

Asegúrate de tener `DEBUG_MODE=true` en tu archivo `.env`:

```bash
# .env
DEBUG_MODE=true
SECRET_KEY=super-secret-placeholder-change-me-in-production-2026
ENCRYPTION_KEY=LAEVnqq4I8q0jiqok71vYri5GEwm9FlDhp_1FYfWJZM=
```

### 2. Levantar contenedores

```bash
docker compose up -d
```

### 3. Verificar que el servicio está corriendo

```bash
docker compose logs bonus_api --tail=10
```

Deberías ver:
```
INFO:     Uvicorn running on http://0.0.0.0:8002 (Press CTRL+C to quit)
```

---

## 🚀 FLUJO DE PRUEBAS RECOMENDADO

### Opción A: Más rápido (sin autenticación)

```bash
# Solo usar el endpoint /mock-calculate
curl -X POST http://localhost:8002/api/v1/auth/mock-calculate \
  -H "Content-Type: application/json" \
  -d '{"evaluacion_id": "uuid", "calificacion_global": 4.0}'
```

### Opción B: Con token mockeado

```bash
# 1. Obtener token
TOKEN=$(curl -s -X POST http://localhost:8002/api/v1/auth/mock-login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 2. Usar token
curl -X POST http://localhost:8002/api/v1/bonus/calculate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"evaluacion_id": "uuid", "calificacion_global": 4.0}'
```

### Opción C: Con script CLI

```bash
# 1. Generar token
python3 scripts/generate_test_token.py --user admin

# 2. Copiar el token y usarlo en tus pruebas
```

---

## ⚠️ NOTAS IMPORTANTES

1. **Endpoints mockeados SOLO funcionan con `DEBUG_MODE=true`**
2. **No guardan datos en la base de datos** - Solo calculan y devuelven resultados
3. **Para producción:** Eliminar los endpoints `/mock-login` y `/mock-calculate` del código
4. **Los tokens mockeados expiran en 24 horas**

---

## 📞 ¿PROBLEMAS?

### Error: "DEBUG_MODE no está activado"

**Solución:** Agrega `DEBUG_MODE=true` a tu `.env` y reinicia los contenedores:

```bash
docker compose down && docker compose up -d
```

### Error: "password authentication failed"

**Solución:** Este error significa que el servicio está intentando conectarse a la BD. Usa los endpoints `/mock-calculate` que NO requieren BD.

### Error: "Fernet key must be 32 url-safe base64-encoded bytes"

**Solución:** Genera una nueva clave Fernet válida:

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Actualiza `ENCRYPTION_KEY` en tu `.env` con la nueva clave.

---

## 📚 PRÓXIMOS PASOS

1. ✅ **Probar la fórmula matemática** con los endpoints mockeados
2. ⏳ **Configurar la base de datos** cuando tengas las credenciales
3. ⏳ **Probar los endpoints reales** (`/bonus/calculate`) con persistencia
4. ⏳ **Eliminar endpoints mockeados** antes de ir a producción

---

**Última actualización:** 2026-06-02  
**Versión:** 1.0.0