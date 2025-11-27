from discord.ext import commands
import discord
from config.settings import buscar_archivo
from audio.player import play_gapless

async def setup(bot):
    @bot.command()
    async def loop(ctx, nombre_loop: str):
        archivo = buscar_archivo(nombre_loop)

        if archivo is None:
            await ctx.send(f"❌ No encontré `{nombre_loop}`.")
            return

        try:
            channel = ctx.author.voice.channel
        except:
            await ctx.send("❌ Debes estar en un canal de voz.")
            return

        vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)

        if vc and vc.is_connected():
            await vc.move_to(channel)
        else:
            vc = await channel.connect()

        play_gapless(vc, archivo)

        await ctx.send(f"🔁 Loop (gapless): **{nombre_loop}**")
