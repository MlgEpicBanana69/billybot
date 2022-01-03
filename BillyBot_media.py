import random
import re
from typing import final
import requests
import mimetypes
from requests.api import request
mimetypes.init()

import validators
from youtube_dl import YoutubeDL
import discord
from discord.utils import get

class Media:
    _name = None
    _content = None
    _source = None
    _route_type = None

    def __init__(self, source):
        self._source = source
        self.source_route()
        assert self._route_type is not None

    def __str__(self):
        return self._name

    def __repr__(self):
        return "Media<{0}>".format(self._name)

    def __call__(self):
        return self.get_content()

    def get_name(self):
        return self._name

    def get_content(self):
       return self._content

    def get_source(self):
        return self._source

    @staticmethod
    def query_youtube(query_str):
        """Query youtube using a query and returns a list of the """
        prefix = "https://www.youtube.com/results?search_query="
        blacklisted_characters = r"@#$%^&+=|\][}{';:?/,`><" + '"'
        search = query_str
        search = ''.join([c for c in search if ord(c) >= 32])
        search = ''.join([f"%{hex(ord(c))[2::].upper()}" if c in blacklisted_characters else c for c in search])
        search = search.replace(' ', '+')
        search = prefix + search

        resp = requests.get(search)
        videos_found = [tag[-11::] for tag in re.findall('{"videoId":"[\d\w]{11}', resp.content.decode('utf-8'))]
        SIZE = 10
        video_prefix = "https://www.youtube.com/watch?v="
        final_recommandations = []
        for i in range(len(videos_found)):
            if len(final_recommandations) == SIZE:
                break
            if video_prefix + videos_found[i] not in final_recommandations:
                final_recommandations.append(video_prefix + videos_found[i])
        return final_recommandations

    def source_route(self):
        """Sets the Media's _route_type variable"""

        route = None
        if validators.url(self._source):
            if self._source.startswith("https://www.youtube.com/watch?v="):
                route = "youtube_media"
            elif '.' in self._source and '/' in self._source:
                mimestart = mimetypes.guess_type(self._source.split('/')[-1])[0]
                if mimestart is not None:
                    if mimestart.split('/')[0] in ['video', 'audio', 'image']:
                        route = "generic_" + mimestart.split('/')[0]
        self._route_type = route

    def fetch_file(self, url):
        # 100MB
        size_limit = 104857600

        # The url is to a file
        if self.source_route(url) == "generic_streamable_media":
            resp = requests.get(self._source, stream=True)
            resp.raise_for_status()

            if len(resp.content) > size_limit:
                raise ValueError('respose too large')

            contents = bytes()
            # 8MB
            curr_size = 0
            for chunk in resp.iter_content(size_limit):
                curr_size += len(chunk)
                if curr_size > size_limit:
                    raise ValueError("response too large")
                contents += chunk
            return contents

class Streamable(Media):
    def __init__(self, source):
        super().__init__(source)
        self.generate_content()

    def get_content(self):
        if self._content is None:
            self.generate_content()
        # Streamable content is one time use and is desposed of
        temp = self._content
        self._content = None
        return temp

    def generate_content(self, no_video=True):
        """Generates the streamables attributes for a Streamable object.
           sets self._name and self._content. This function returns nothing"""

        # Options that seem to work perfectly (?)
        # ydl_options = {'format': 'bestaudio', 'noplaylist':'True'}
        # ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        ydl_options = {'format': 'worseaudio/bestaudio',
                    'noplaylist':'True',
                    'youtube_include_dash_manifest': False}
        ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                        'options': '-vn'}

        # That source is a youtube link
        if self._route_type == "youtube_media":
            with YoutubeDL(ydl_options) as ydl:
                info = ydl.extract_info(self._source, download=False)
                url = info['formats'][0]['url']

                self._name = info['title']
                if no_video:
                    self._content = discord.FFmpegPCMAudio(url, **ffmpeg_options)

        # The source is a link to a file TODO: Implement properly
        elif self._route_type in ["generic_video", "generic_audio"]:
            self._name = self._source.split('/')[-1]
            if no_video:
                self._content = discord.FFmpegPCMAudio(self._source, **ffmpeg_options)

class Static(Media):
    def __init__(self, source):
        super().__init__(source)
        self.generate_content()

    def get_content(self):
        return self._content

    def generate_content(self):
        if self.source_route() != "youtube_media":
            self._content = self.fetch_file(self._source)

# Need to improve on queue editing, design
# add youtube query
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
            temp = self._queue.pop(0)
            random.shuffle(self._queue)
            self._queue.insert(0, temp)

    def toggle_loop(self):
        """Toggles loop"""
        self._loop = not self._loop
        return self._loop

    def next(self):
        """Skips to the next song in the queue"""

        voice = get(self._bot.voice_clients, guild=self._guild)
        if voice is not None:
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

    async def play(self, media:Streamable):
        """Adds a Media object to the queue"""

        voice = get(self._bot.voice_clients, guild=self._guild)

        assert media is not None
        # Adds to queue if media is not None
        self._queue.append(media)

        # Plays now if nothing is playing
        if self._queue[0] == media:
            voice.play(media(), after=lambda e: self.next())

    async def stop(self):
        """Stops and clears the queue"""
        self._queue = []
        voice = get(self._bot.voice_clients, guild=self._guild)
        if voice is not None:
            get(self._bot.voice_clients, guild=self._guild).stop()

    async def pause(self):
        """Pauses play"""
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

    async def wipe(self):
        """Stops playing and wipes the player back into default settings"""
        await self.stop()

        self._loop = False
        self._queue = []

    def get_bot(self):
        return self._bot