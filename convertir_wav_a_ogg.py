import os
import subprocess

LOOPS_DIR = "loops"

def convertir_wav_a_ogg():
    for archivo in os.listdir(LOOPS_DIR):
        ruta = os.path.join(LOOPS_DIR, archivo)

        # 1. Borrar archivos .asd
        if archivo.lower().endswith(".asd"):
            print(f"Deleting Ableton sidecar file: {archivo}")
            os.remove(ruta)
            continue

        # 2. Convertir WAV → OGG
        if archivo.lower().endswith(".wav"):
            ruta_ogg = os.path.join(LOOPS_DIR, archivo[:-4] + ".ogg")

            print(f"Converting {archivo} -> {os.path.basename(ruta_ogg)}")

            comando = [
                "ffmpeg",
                "-y",
                "-i", ruta,
                "-codec:a", "libopus",
                "-b:a", "128k",
                ruta_ogg
            ]

            subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            os.remove(ruta)
            print(f"Deleted original: {archivo}")

    print("\nDone!")

if __name__ == "__main__":
    convertir_wav_a_ogg()
