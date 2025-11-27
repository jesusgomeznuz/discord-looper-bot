from discord.ext import commands
import discord

async def setup(bot):

    @bot.command()
    async def stop(ctx):
        vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if vc:
            await ctx.send("⏹ Loop detenido.")
            await vc.disconnect()
        else:
            await ctx.send("❌ No hay nada reproduciéndose.")
