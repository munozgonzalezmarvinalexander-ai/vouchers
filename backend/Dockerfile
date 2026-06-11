# Imagen del backend (FastAPI + WeasyPrint).
# Se usa para desplegar en Render/Fly/Railway. Incluye las librerías del
# sistema que WeasyPrint necesita para generar el PDF; así el botón
# "Descargar PDF" funciona en el servidor sin pasos extra.

FROM python:3.12-slim

# Librerías del sistema para WeasyPrint (Pango/Cairo/etc.) y fuentes base.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b \
    libgdk-pixbuf-2.0-0 libcairo2 libffi-dev libjpeg62-turbo \
    fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala primero las dependencias (mejor cache de capas).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del backend.
COPY . .

# El proveedor (Render, etc.) inyecta el puerto en la variable PORT.
ENV PORT=8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
