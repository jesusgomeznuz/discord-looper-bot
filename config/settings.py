import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Carpeta donde estarán los loops
LOOPS_FOLDER = "loops"

def buscar_archivo(nombre):
    """
    Devuelve ruta del .ogg o .wav si existe.
    """
    for ext in ["ogg", "wav", "mp3"]:
        archivo = f"{LOOPS_FOLDER}/{nombre}.{ext}"
        if os.path.exists(archivo):
            return archivo
    return None
