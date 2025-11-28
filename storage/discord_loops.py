import re
import shutil
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import discord

from config.settings import LOOPS_CACHE_DIR, LOOP_EXTENSIONS, buscar_archivo

# Número de mensajes por canal que se inspeccionarán al buscar attachments
HISTORY_LIMIT = 200
BASE_SUFFIX = "_base"
BASE_INDEX_PATTERN = re.compile(rf"^(?P<name>.+){BASE_SUFFIX}_(?P<index>\d+)$")


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


async def _find_all_base_variants(base_name: str, guild: discord.Guild) -> List[discord.Attachment]:
    """
    Devuelve todos los attachments disponibles para la base (base, base_1, base_2...) en #base.
    """
    matches = []
    for channel in _base_channels(guild):
        async for message in channel.history(limit=HISTORY_LIMIT, oldest_first=False):
            for attachment in message.attachments:
                if attachment.filename.endswith(tuple(f".{ext}" for ext in LOOP_EXTENSIONS)):
                    stem = Path(attachment.filename).stem.lower()
                    if stem == base_name.lower() or stem.startswith(f"{base_name.lower()}_"):
                        matches.append(attachment)
    return matches


class BaseSelectionError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


async def _resolve_base_attachment(
    normalized_name: str, guild: discord.Guild
) -> Tuple[Optional[str], Optional[str]]:
    """
    Maneja la lógica de bases simples y múltiples. Devuelve (ruta, mensaje_error_opcional).
    """
    match = BASE_INDEX_PATTERN.match(normalized_name)
    if match:
        base_name = match.group("name")
        base_index = match.group("index")
        normalized_variant = f"{base_name}{BASE_SUFFIX}_{base_index}"

        local_variant = buscar_archivo(normalized_variant)
        if local_variant:
            return local_variant, None

        attachment = await _find_attachment(normalized_variant, _base_channels(guild))
        if attachment:
            return await _download_attachment(normalized_variant, attachment, guild.id), None

        return None, (
            f"No encontré '{base_name} base {base_index}'. "
            f"Asegúrate de que el archivo exista como {base_name}_{base_index}.ext"
        )

    base_name = normalized_name[: -len(BASE_SUFFIX)]
    if not base_name:
        return None, "Especifica qué base necesitas."

    # Single base local
    local_base = buscar_archivo(base_name)
    if local_base:
        return local_base, None

    # Check attachments
    attachments = await _find_all_base_variants(base_name, guild)

    if not attachments:
        attachment = await _find_attachment(base_name, _base_channels(guild))
        if attachment:
            return await _download_attachment(base_name, attachment, guild.id), None
        return None, f"No encontré archivos base para '{base_name}'."

    # Determine if there are multiple variants with numeric suffixes
    variants = [att for att in attachments if att.filename.lower().startswith(f"{base_name.lower()}_")]
    if variants and len(variants) > 1:
        return None, f"Hay varias bases para '{base_name}'. Intenta con '{base_name} base 1'."

    # Only base without suffix
    attachment = await _find_attachment(base_name, _base_channels(guild))
    if attachment:
        return await _download_attachment(base_name, attachment, guild.id), None

    return None, f"No encontré archivos base para '{base_name}'."


async def ensure_loop_file(raw_loop_name: str, guild: discord.Guild) -> Tuple[Optional[str], Optional[str]]:
    """
    Busca el loop solicitado: primero local, luego #loops y, si termina en "_base",
    intenta con el archivo raíz alojado en #base.
    """
    normalized_name = normalize_loop_name(raw_loop_name)

    if not normalized_name:
        return None, "No se proporcionó un nombre válido."

    local = buscar_archivo(normalized_name)
    if local:
        return local, None

    if guild is None:
        return None, "Este comando sólo funciona dentro de un servidor."

    attachment = await _find_attachment(normalized_name, _loop_channels(guild))
    if attachment:
        return await _download_attachment(normalized_name, attachment, guild.id), None

    if normalized_name.endswith(BASE_SUFFIX) or BASE_INDEX_PATTERN.match(normalized_name):
        return await _resolve_base_attachment(normalized_name, guild)

    return None, f"No pude encontrar '{raw_loop_name}'."
