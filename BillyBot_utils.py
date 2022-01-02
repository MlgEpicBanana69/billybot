import numpy as np
import validators
from youtube_dl import YoutubeDL
from discord import FFmpegPCMAudio
import asyncio

class Media:
    _name = None
    _playable = None
    _source = None

    def __init__(self, name, playable, source):
        self._name = name
        self._playable = playable
        self._source = source

    def __str__(self):
        return self._name

    def __repr__(self):
        return "Media<{0}>".format(self._name)

    def __call__(self):
        return self.get_playable()

    def get_name(self):
        return self._name

    def get_playable(self):
        return self._playable

    def get_source(self):
        return self._source



# https://en.wikipedia.org/wiki/Alpha_compositing
def merge_pixels(foreground, background):
    """Merges the values of two pixels to create a new one"""
    foreground_alpha = foreground[3] / 255
    background_alpha = background[3] / 255

    if foreground_alpha == 0.0:
        return background
    elif foreground_alpha == 1.0:
        return foreground

    merged_alpha = (foreground_alpha + background_alpha * (1 - foreground_alpha))

    foreground_red = foreground[0] / 255
    foreground_green = foreground[1] / 255
    foreground_blue = foreground[2] / 255

    background_red = background[0] / 255
    background_green = background[1] / 255
    background_blue = background[2] / 255

    merged_red   = (foreground_red * foreground_alpha+ background_red
                    * background_alpha * (1 - foreground_alpha)) / merged_alpha
    merged_green = (foreground_green * foreground_alpha + background_green
                    * background_alpha * (1 - foreground_alpha)) / merged_alpha
    merged_blue  = (foreground_blue * foreground_alpha + background_blue
                    * background_alpha * (1 - foreground_alpha)) / merged_alpha
    return np.array([int(merged_red * 255), int(merged_green * 255),
                     int(merged_blue * 255), int(merged_alpha * 255)])

async def get_media(source):
    """Gets a link and returns its ffmpeg object to be used for streaming purposes"""
    # Options that seem to work perfectly (?)
    # ydl_options = {'format': 'bestaudio', 'noplaylist':'True'}
    # ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    ydl_options = {'format': 'worseaudio/bestaudio',
                   'noplaylist':'True',
                   'youtube_include_dash_manifest': False}
    ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                      'options': '-vn'}

    # Some online audio source was given
    if source is not None:
        # That source is a youtube link
        if validators.url(source) and source.startswith("https://www.youtube.com/watch?v="):
            with YoutubeDL(ydl_options) as ydl:
                info = ydl.extract_info(source, download=False)
                url = info['formats'][0]['url']
                return Media(info['title'], FFmpegPCMAudio(url, **ffmpeg_options), source)
        # The source is a link to a file DEBUG
        elif validators.url(source):
            return Media('debug', FFmpegPCMAudio(url, **ffmpeg_options), source)
        # Treat source as a youtube query
        else:
            pass
    return None

async def download_media(source):
    """Downloads a media from file url on the web"""
    # Options that seem to work perfectly (?)
    # ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    raise NotImplementedError()