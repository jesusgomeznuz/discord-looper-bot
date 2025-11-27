# Imagen base con Python y FFmpeg
FROM python:3.11-slim

# Instalar FFmpeg y libopus
RUN apt-get update && \
    apt-get install -y ffmpeg libopus0 && \
    apt-get clean

# Crear carpeta de la app
WORKDIR /app

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar resto del proyecto
COPY . .

CMD ["python", "bot.py"]
