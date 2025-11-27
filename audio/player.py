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
