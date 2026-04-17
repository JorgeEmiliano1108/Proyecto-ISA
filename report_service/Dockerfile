# Dockerfile para Report Service (ISA Corporativo)
FROM python:3.11-slim

# INYECCIÓN CLAVE: Zona horaria predeterminada
ENV TZ="America/Mexico_City"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/srv/report_service/app:/srv/report_service"

WORKDIR /srv/report_service

# Instalar dependencias del sistema requeridas por WeasyPrint + tzdata
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-xlib-2.0-0 \
    libffi-dev \
    pkg-config \
    shared-mime-info \
    build-essential \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Hardening: Crear usuario no-root y asegurar permisos de las carpetas dinámicas
RUN useradd --create-home --shell /bin/bash appuser \
    && mkdir -p /srv/report_service/static/reports \
    && mkdir -p /srv/report_service/data \
    && chown -R appuser:appuser /srv/report_service

USER appuser

EXPOSE 8003

STOPSIGNAL SIGTERM

# Comando de inicio por defecto (FastAPI) usando la notación exec (corchetes)
# Esto asegura que uvicorn sea el PID 1 y reciba el SIGTERM directamente.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]