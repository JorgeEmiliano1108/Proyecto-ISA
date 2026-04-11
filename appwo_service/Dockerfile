
# Builder (Compilación)

FROM python:3.12-slim as builder
WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar asyncpg y otros
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear entorno virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Producción (Imagen Final)

FROM python:3.12-slim
WORKDIR /app

# Instalar solo las librerías en tiempo de ejecución necesarias para PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copiar el entorno virtual compilado de la etapa 1
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar el código fuente
COPY . .

# Seguridad OWASP: Crear un usuario no root para ejecutar la app
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Exponer puerto
EXPOSE 8000

# Comando por defecto (sobrescrito por docker-compose para dev)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]