# Imagen base con Python y FFmpeg
FROM python:3.11-slim

# Instalar FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# Crear carpeta de la app
WORKDIR /app

# Copiar archivos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Comando de arranque
CMD ["python", "bot.py"]
