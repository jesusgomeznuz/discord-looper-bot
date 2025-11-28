import asyncio

import discord
from discord.ext import commands

from audio.player import play_once
from storage.discord_loops import ensure_loop_file

VOICE_CONNECT_TIMEOUT = 15


async def setup(bot):
    @bot.command()
    async def start(ctx, *, loop_name: str):
        file_path = await ensure_loop_file(loop_name, ctx.guild)

        if file_path is None:
            await ctx.send(f"No pude encontrar '{loop_name}'❌")
            return

        try:
            channel = ctx.author.voice.channel
        except:
            await ctx.send("Necesitas estar en un canal de voz🎙️")
            return

        vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)

        if vc and vc.is_playing():
            await ctx.send("Ya hay algo reproduciéndose, detén el loop antes de usar !start🔁")
            return

        try:
            if vc and vc.is_connected():
                if vc.channel != channel:
                    await vc.move_to(channel)
            else:
                vc = await channel.connect(timeout=VOICE_CONNECT_TIMEOUT, reconnect=True)
        except asyncio.TimeoutError:
            await ctx.send("La conexión al canal de voz se tardó demasiado⏳")
            return
        except discord.ClientException as exc:
            await ctx.send(f"No pude conectarme al canal: {exc}⚠️")
            return

        play_once(bot, vc, file_path, disconnect_after=True)
        await ctx.send(f"Reproduciendo una sola vez: {loop_name}🎚️")
