FROM python:3.11-bookworm

ENV TZ=Europe/Madrid

WORKDIR /app

# Dependencias del sistema (si las necesitas)
RUN apt update && apt install -y nano cron && apt clean

COPY . .

RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiar todo el código

# Exponer puerto (opcional pero recomendado)
EXPOSE 8200

# 🚀 Producción con Gunicorn (RECOMENDADO)
# CMD ["gunicorn", "-b", "0.0.0.0:8200", "app:app"]