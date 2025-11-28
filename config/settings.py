import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Carpeta con loops locales disponibles sin descargar desde Discord
LOOPS_FOLDER = Path(os.getenv("LOOPS_FOLDER", "loops"))

# Extensiones soportadas al buscar loops
LOOP_EXTENSIONS = ("ogg", "wav", "mp3")

# Carpeta usada para cachear loops descargados desde Discord
LOOPS_CACHE_DIR = Path(os.getenv("LOOPS_CACHE_DIR", "/tmp/looper-cache"))


def buscar_archivo(nombre: str) -> Optional[str]:
    """
    Devuelve ruta del loop local si existe.
    """
    for ext in LOOP_EXTENSIONS:
        archivo = LOOPS_FOLDER / f"{nombre}.{ext}"
        if archivo.exists():
            return str(archivo)
    return None
