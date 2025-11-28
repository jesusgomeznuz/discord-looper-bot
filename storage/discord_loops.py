import re
import shutil
from pathlib import Path
from typing import Iterable, Optional

import discord

from config.settings import LOOPS_CACHE_DIR, LOOP_EXTENSIONS, buscar_archivo

# Número de mensajes por canal que se inspeccionarán al buscar attachments
HISTORY_LIMIT = 200


def prepare_cache_dir(clean: bool = True) -> None:
    """
    Prepara el directorio de caché al iniciar el bot.
    """
    if clean and LOOPS_CACHE_DIR.exists():
        shutil.rmtree(LOOPS_CACHE_DIR)
    LOOPS_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _normalize_channel_name(name: str) -> str:
    ascii_name = name.encode("ascii", errors="ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "", ascii_name)


def _loop_channels(guild: discord.Guild) -> Iterable[discord.TextChannel]:
    for channel in guild.text_channels:
        if _normalize_channel_name(channel.name) == "loops":
            yield channel


def _attachment_matches(attachment: discord.Attachment, loop_name: str) -> bool:
    file_path = Path(attachment.filename)
    return (
        file_path.stem.lower() == loop_name.lower()
        and file_path.suffix.lower().lstrip(".") in LOOP_EXTENSIONS
    )


async def _find_attachment(loop_name: str, guild: discord.Guild) -> Optional[discord.Attachment]:
    for channel in _loop_channels(guild):
        async for message in channel.history(limit=HISTORY_LIMIT, oldest_first=False):
            for attachment in message.attachments:
                if _attachment_matches(attachment, loop_name):
                    return attachment
    return None


def _cache_path_for(guild_id: int, loop_name: str, filename: str) -> Path:
    file_extension = Path(filename).suffix.lower() or ".ogg"
    cache_dir = LOOPS_CACHE_DIR / str(guild_id)
    cache_dir.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^a-z0-9_-]+", "", loop_name.lower())
    return cache_dir / f"{safe_name}{file_extension}"


async def ensure_loop_file(loop_name: str, guild: discord.Guild) -> Optional[str]:
    """
    Busca un loop local y, si no existe, intenta descargarlo desde los canales #loops.
    """
    local = buscar_archivo(loop_name)
    if local:
        return local

    if guild is None:
        return None

    attachment = await _find_attachment(loop_name, guild)
    if not attachment:
        return None

    cache_path = _cache_path_for(guild.id, loop_name, attachment.filename)
    await attachment.save(cache_path)
    return str(cache_path)
