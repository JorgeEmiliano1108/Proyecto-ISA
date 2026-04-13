FROM python:3.12-slim
FROM python:3.12-slim

WORKDIR /app

# Instalamos librerías necesarias para SQL y Analítica
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*
RUN pip install fastapi uvicorn sqlalchemy psycopg2-binary pandas

COPY . .

# Exponemos el puerto interno
EXPOSE 8000

# Ejecutamos el archivo que acabas de renombrar a main.py
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Reutilizamos el concepto de requerimientos
RUN pip install fastapi uvicorn sqlalchemy psycopg2-binary pandas

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]