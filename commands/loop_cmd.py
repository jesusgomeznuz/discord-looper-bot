import asyncio

import discord
from discord.ext import commands

from audio.player import play_gapless
from storage.discord_loops import ensure_loop_file

VOICE_CONNECT_TIMEOUT = 15

async def setup(bot):
    @bot.command()
    async def loop(ctx, *, loop_name: str):
        file_path = await ensure_loop_file(loop_name, ctx.guild)

        if file_path is None:
            await ctx.send(f"Could not find '{loop_name}'.")
            return

        try:
            channel = ctx.author.voice.channel
        except:
            await ctx.send("You must be in a voice channel.")
            return

        vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)

        try:
            if vc and vc.is_connected():
                if vc.channel != channel:
                    await vc.move_to(channel)
            else:
                vc = await channel.connect(timeout=VOICE_CONNECT_TIMEOUT, reconnect=True)
        except asyncio.TimeoutError:
            await ctx.send("Connection to the voice channel timed out, please try again.")
            return
        except discord.ClientException as exc:
            await ctx.send(f"Could not connect to voice: {exc}")
            return

        if vc.is_playing():
            vc.stop()

        play_gapless(vc, file_path)

        await ctx.send(f"Looping (gapless): {loop_name}")
