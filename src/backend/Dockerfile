# Dockerfile para Django en backend usando Python completo
FROM python:3.11

# Variables de entorno para Django
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# --- NUEVA SECCIÓN: Dependencias del sistema para MySQL ---
# Instalamos las librerías necesarias para que mysqlclient funcione
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*
# ---------------------------------------------------------

# Actualizamos pip
RUN pip install --upgrade pip

# Copiamos requirements.txt y los instalamos
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código Django
COPY app/ /app/

# Aplicar migraciones
# RUN python manage.py migrate

 # Cargar fixtures initial_data.json
# RUN python manage.py loaddata initial_data.json

# Exponer puerto Django
EXPOSE 8000

# Comando por defecto para desarrollo
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]