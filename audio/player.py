import asyncio

import discord


def play_gapless(vc, path):
    """
    Reproduce un archivo en loop sin delay usando el loop interno de FFmpeg.
    """
    ffmpeg_options = {
        'before_options': '-stream_loop -1 -re',
        'options': '-vn'
    }

    source = discord.FFmpegPCMAudio(path, **ffmpeg_options)
    vc.play(source)


def play_once(bot, vc, path, disconnect_after=True):
    """
    Reproduce un archivo una sola vez y opcionalmente desconecta al bot al terminar.
    """
    source = discord.FFmpegPCMAudio(path)

    def _after(error):
        if disconnect_after:
            asyncio.run_coroutine_threadsafe(vc.disconnect(), bot.loop)

    vc.play(source, after=_after)
