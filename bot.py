import os
import discord
from discord.ext import commands
from config.settings import DISCORD_TOKEN

# Load opus
if not discord.opus.is_loaded():
    discord.opus.load_opus('libopus.so.0')  # Linux

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

EXTENSIONS = [
    "commands.loop_cmd",
    "commands.stop_cmd",
]

@bot.event
async def on_ready():
    print(f"🔥 Bot conectado como {bot.user}")

    # Cargar extensiones async
    for ext in EXTENSIONS:
        await bot.load_extension(ext)
        print(f"[OK] Cargado: {ext}")

bot.run(DISCORD_TOKEN)
