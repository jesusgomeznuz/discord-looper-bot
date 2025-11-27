# Imagen base ligera con Python 3.11
FROM python:3.11-slim

# Instalar dependencias del sistema necesarias para discord.py + opus + ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libopus0 \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Exponer algún puerto (Fly requiere uno, aunque no lo uses)
EXPOSE 8080

# Comando de ejecución
CMD ["python", "bot.py"]
