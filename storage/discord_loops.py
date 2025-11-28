import re
import shutil
from pathlib import Path
from typing import Iterable, Optional

import discord

from config.settings import LOOPS_CACHE_DIR, LOOP_EXTENSIONS, buscar_archivo

# Número de mensajes por canal que se inspeccionarán al buscar attachments
HISTORY_LIMIT = 200
BASE_SUFFIX = "_base"


def prepare_cache_dir(clean: bool = True) -> None:
    """
    Prepara el directorio de caché al iniciar el bot.
    """
    if clean and LOOPS_CACHE_DIR.exists():
        shutil.rmtree(LOOPS_CACHE_DIR)
    LOOPS_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def normalize_loop_name(raw: str) -> str:
    """
    Convierte input humano ("Demo 1 completa") en la convención interna demo1_completa.
    """
    cleaned = re.sub(r"[^a-z0-9]+", "_", raw.lower())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned


def _normalize_channel_name(name: str) -> str:
    ascii_name = name.encode("ascii", errors="ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "", ascii_name)


def _channels_by_normalized_name(guild: discord.Guild, desired: str) -> Iterable[discord.TextChannel]:
    target = _normalize_channel_name(desired)
    for channel in guild.text_channels:
        if _normalize_channel_name(channel.name) == target:
            yield channel


def _loop_channels(guild: discord.Guild) -> Iterable[discord.TextChannel]:
    return _channels_by_normalized_name(guild, "loops")


def _base_channels(guild: discord.Guild) -> Iterable[discord.TextChannel]:
    return _channels_by_normalized_name(guild, "base")


def _attachment_matches(attachment: discord.Attachment, loop_name: str) -> bool:
    file_path = Path(attachment.filename)
    return (
        file_path.stem.lower() == loop_name.lower()
        and file_path.suffix.lower().lstrip(".") in LOOP_EXTENSIONS
    )


async def _find_attachment(loop_name: str, channels: Iterable[discord.TextChannel]) -> Optional[discord.Attachment]:
    for channel in channels:
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


async def _download_attachment(loop_name: str, attachment: discord.Attachment, guild_id: int) -> str:
    cache_path = _cache_path_for(guild_id, loop_name, attachment.filename)
    await attachment.save(cache_path)
    return str(cache_path)


async def ensure_loop_file(raw_loop_name: str, guild: discord.Guild) -> Optional[str]:
    """
    Busca el loop solicitado: primero local, luego #loops y, si termina en "_base",
    intenta con el archivo raíz alojado en #base.
    """
    normalized_name = normalize_loop_name(raw_loop_name)

    if not normalized_name:
        return None

    local = buscar_archivo(normalized_name)
    if local:
        return local

    if guild is None:
        return None

    attachment = await _find_attachment(normalized_name, _loop_channels(guild))
    if attachment:
        return await _download_attachment(normalized_name, attachment, guild.id)

    if normalized_name.endswith(BASE_SUFFIX):
        base_name = normalized_name[: -len(BASE_SUFFIX)]
        if not base_name:
            return None

        local_base = buscar_archivo(base_name)
        if local_base:
            return local_base

        attachment = await _find_attachment(base_name, _base_channels(guild))
        if attachment:
            return await _download_attachment(base_name, attachment, guild.id)

    return None
