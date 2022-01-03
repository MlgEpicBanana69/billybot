import numpy as np
import validators
from youtube_dl import YoutubeDL

import discord
from discord.utils import get

import asyncio
import random

class Media:
    _name = None
    _playable = None
    _source = None

    def __init__(self, source):
        self._source = source
        self.generate_streamables()

    def __str__(self):
        return self._name

    def __repr__(self):
        return "Media<{0}>".format(self._name)

    def __call__(self):
        return self.get_playable()

    def get_name(self):
        return self._name

    def get_playable(self):
        if self._playable is None:
            self.generate_streamables()

        temp = self._playable
        self._playable = None
        return temp

    def get_source(self):
        return self._source

    def generate_streamables(self):
        """Generates the streamables attributes for the current Media object.
           sets self._name and self._playable. This function returns nothing"""

        # Options that seem to work perfectly (?)
        # ydl_options = {'format': 'bestaudio', 'noplaylist':'True'}
        # ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        ydl_options = {'format': 'worseaudio/bestaudio',
                    'noplaylist':'True',
                    'youtube_include_dash_manifest': False}
        ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                        'options': '-vn'}

        # That source is a youtube link
        if validators.url(self._source) and self._source.startswith("https://www.youtube.com/watch?v="):
            with YoutubeDL(ydl_options) as ydl:
                info = ydl.extract_info(self._source, download=False)
                url = info['formats'][0]['url']

                self._name = info['title']
                self._playable = discord.FFmpegPCMAudio(url, **ffmpeg_options)

        # The source is a link to a file TODO: Implement properly
        elif validators.url(self._source):
            self._name = "bruh??"
            self._playable = discord.FFmpegPCMAudio(self._source, **ffmpeg_options)


        # Treat source as a youtube query
        else:
            return None

# Need to improve on queue editing, design
# add dynamic youtube search and lastly optimize streaming quality (somehow)
class Player:
    """BillyBot's unique player"""

    _players = []  # static variable containing ALL player objects

    _guild = None  # The guild that the player is binded to
    _bot = None
    _loop = None   # Is the player in loop state
    _queue = None    # The queue of songs in order

    def __init__(self, guild, bot):
        self._players.append(self)

        self._guild = guild
        self._bot = bot

        self._loop = False
        self._queue = []

    async def shuffle(self):
        """Shuffles the queue"""
        if len(self._queue) > 0:
            random.shuffle(self._queue)
            temp = self._queue
            self._queue = []
            await self.stop()
            await self.play(temp[0])
            self._queue += temp[1::]



    def toggle_loop(self):
        """Toggles loop"""
        self._loop = not self._loop
        return self._loop

    def next(self):
        """Skips to the next song in the queue"""

        voice = get(self._bot.voice_clients, guild=self._guild)
        if voice.is_playing():
            voice.stop()
            return

        if len(self.get_queue()) > 0:
            if self._loop:
                self.get_queue().append(self.get_queue().pop(0))
            else:
                self.get_queue().pop(0)

        if len(self.get_queue()) > 0:
            print("Playing {0} on guild {1}".format(self.get_queue()[0].get_name(), self.get_guild().name))
            voice.play(self.get_queue()[0](), after=lambda e: self.next())

    def current_song(self):
        """Returns the name of the current song"""
        return self.get_queue()[0].get_name()

    async def play(self, media:Media):
        """Adds a Media object to the queue"""

        voice = get(self._bot.voice_clients, guild=self._guild)
        #while voice.is_playing() and len(self._queue) == 0:
        #    pass

        # Adds to queue if media is not None
        self._queue.append(media)

        # Plays now if nothing is playing
        if self._queue[0] == media:
            voice.play(media(), after=lambda e: self.next())

    async def stop(self):
        """Stops and clears the queue"""
        self._queue = []
        get(self._bot.voice_clients, guild=self._guild).stop()

    async def pause(self):
        """Pauses playing the queue"""
        get(self._bot.voice_clients, guild=self._guild).pause()

    async def resume(self):
        """Resumes to playing the queue"""
        get(self._bot.voice_clients, guild=self._guild).resume()

    def get_guild(self):
        """Returns the guild this player is attached to"""
        return self._guild

    @staticmethod
    def get_player(guild):
        for player in Player._players:
            if player.get_guild() == guild:
                return player
        return None

    def get_queue(self):
        """Returns the player's queue"""
        return self._queue

    def wipe(self):
        """Stops playing and wipes the player back into default settings"""
        self.stop()

        self._loop = False
        self._queue = []

    def get_bot(self):
        return self._bot