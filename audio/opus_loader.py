import discord

def load_opus():
    if discord.opus.is_loaded():
        return

    possible_paths = [
        "/usr/lib/libopus.so.0",
        "/usr/local/lib/libopus.0.dylib",
        "/opt/homebrew/lib/libopus.0.dylib"
    ]

    for path in possible_paths:
        try:
            discord.opus.load_opus(path)
            print(f"[OK] Opus loaded from {path}")
            return
        except:
            pass

    raise RuntimeError("❌ No se pudo cargar OPUS.")
