# Imagen base
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para mysqlclient
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt /app/

# Instalar dependencias python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar proyecto
COPY . /app/

# Exponer puerto
EXPOSE 8000

# Ejecutar Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]