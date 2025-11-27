from discord.ext import commands
import discord
from config.settings import buscar_archivo
from audio.player import play_gapless

async def setup(bot):
    @bot.command()
    async def loop(ctx, loop_name: str):
        file_path = buscar_archivo(loop_name)

        if file_path is None:
            await ctx.send(f"Could not find '{loop_name}'.")
            return

        try:
            channel = ctx.author.voice.channel
        except:
            await ctx.send("You must be in a voice channel.")
            return

        vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)

        if vc and vc.is_connected():
            await vc.move_to(channel)
        else:
            vc = await channel.connect()

        play_gapless(vc, file_path)

        await ctx.send(f"Looping (gapless): {loop_name}")
