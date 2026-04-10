# audit_service/Dockerfile

# Base (Configuración común)

# Usamos Debian Bookworm Slim: Excelente equilibrio entre tamaño y compatibilidad.
FROM python:3.12-slim-bookworm AS base

# Evitar que Python escriba archivos .pyc y forzar logs sin buffer
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

# Builder (Compilación de dependencias)

FROM base AS builder

# Instalar dependencias del sistema necesarias para compilar paquetes C (ej. asyncpg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear un entorno virtual para encapsular las dependencias
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar solo el archivo de dependencias primero (Layer Caching)
# Suponiendo que tienes un requirements.txt. Si usas poetry: poetry export -f requirements.txt > requirements.txt
COPY requirements.txt .

# Instalar dependencias en el venv (sin guardar cache)
RUN pip install --no-cache-dir -r requirements.txt


# Development (Target para docker-compose)

FROM base AS development

# Copiar el entorno virtual compilado del builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Herramientas extra para dev (pytest, etc.) podrían ir aquí

# El código se montará vía volumen en docker-compose, no lo copiamos
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


# STAGE 4: Production (Imagen final ligera)

FROM base AS production

# Crear un usuario no root por seguridad (OWASP)
RUN addgroup --system appgroup && adduser --system --group appuser

# Copiar el entorno virtual ya compilado desde el builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar el código de la aplicación
COPY ./app /app/app
COPY ./alembic /app/alembic
COPY alembic.ini /app/alembic.ini

# Cambiar permisos y usar usuario no root
RUN chown -R appuser:appgroup /app
USER appuser

# Healthcheck interno (Opcional, pero buena práctica)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Comando de producción sin --reload y con workers
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]