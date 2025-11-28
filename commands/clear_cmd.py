import re

from discord.ext import commands

TARGET_CHANNEL = "commands"
PURGE_BATCH_SIZE = 100


def _normalize_channel_name(name: str) -> str:
    ascii_name = name.encode("ascii", errors="ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "", ascii_name)


async def setup(bot):
    @bot.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(ctx):
        """
        Limpia todos los mensajes del canal #commands.
        """
        if _normalize_channel_name(ctx.channel.name) != TARGET_CHANNEL:
            await ctx.send("This command can only be used inside #commands.")
            return

        deleted_total = 0
        while True:
            deleted = await ctx.channel.purge(limit=PURGE_BATCH_SIZE, bulk=True)
            deleted_total += len(deleted)
            if len(deleted) < PURGE_BATCH_SIZE:
                break

        confirmation = await ctx.send(f"Cleared {deleted_total} messages.")
        await confirmation.delete(delay=5)
