# backend/Dockerfile
FROM python:3.12-slim

# Evita que Python escriba .pyc y que bufferee stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del container

WORKDIR /app

# Instala dependencias del sistema que necesitan algunas libs de Python
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependencias Python primero
# (separado del código para aprovechar cache de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


    # Copia el código
COPY . .

# Puerto que expone el container
EXPOSE 8000