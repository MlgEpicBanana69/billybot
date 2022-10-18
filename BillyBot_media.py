import random
import re
import requests
import mimetypes
mimetypes.init()
import validators
from youtube_dl import YoutubeDL
from urllib.parse import urlparse
import discord
from discord.utils import get

class Media:
    GENERIC_IMAGE = "generic_image"
    GENERIC_VIDEO = "generic_video"
    GENERIC_AUDIO = "generic_audio"
    GENERIC_FILE  = "generic_file"

    def __init__(self, source):
        self._name = None
        self._content = None
        self._route_type = None
        self._source = source
        self.source_route()
        assert self._route_type is not None

    def __call__(self):
        return self.get_content()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Media<{0}>".format(self._name)

    def get_name(self):
        return self._name

    def get_content(self):
       return self._content

    def get_source(self):
        return self._source

    @staticmethod
    def query_youtube(query_str, SIZE=10):
        """Query youtube using a query and returns a list of the """
        prefix = "https://www.youtube.com/results?search_query="
        blacklisted_characters = r"@#$%^&+=|\][}{';:?/,`><" + '"'
        search = query_str
        search = ''.join([c for c in search if ord(c) >= 32])
        search = ''.join([f"%{hex(ord(c))[2::].upper()}" if c in blacklisted_characters else c for c in search])
        search = search.replace(' ', '+')
        search = prefix + search

        resp = requests.get(search)
        video_prefix = "https://www.youtube.com/watch?v="

        video_ids = []
        for tag in re.findall('{"videoId":"[\d\w]{11}",', resp.content.decode('utf-8')):
            if video_prefix + tag[12:-2:] not in video_ids:
                video_ids.append(video_prefix + tag[12:-2:])
        video_titles = [tag[26:-3:] for tag in re.findall('"title":\{"runs":\[\{"text":".+?"\}\]', resp.content.decode('utf-8'))[:-10:]]
        videos_found = list(zip(video_ids, video_titles))[:SIZE:]

        final_recommandations = []
        for video in videos_found:
            if video[0] not in final_recommandations:
                final_recommandations.append(video)
        return final_recommandations

    def source_route(self):
        """Sets the Media's _route_type variable"""

        ydl_options = {'format': 'bestvideo[filesize<8MiB][ext=mp4]+bestaudio[ext=m4a]/bestvideo[filesize<8MiB]+bestaudio/best[filesize<8MiB]',
                    'noplaylist':'True',
                    'youtube_include_dash_manifest': False}

        route = None
        extension = None
        if validators.url(self._source):
            if Media.is_web_media(self._source):
                with YoutubeDL(ydl_options) as ydl:
                    info = ydl.extract_info(self._source, download=False)
                    mimestart = mimetypes.guess_type("a." + info['ext'])[0]
                    if 'formats' in info:
                        self._source = info['formats'][-1]['url']
                    elif 'thumbnails' in info:
                        self._source = info['thumbnails'][-1]['url']
                    else:
                        raise AssertionError("osuHOW")
            elif '.' in self._source and '/' in self._source:
                mimestart = mimetypes.guess_type(urlparse(self._source).path.split('/')[-1])[0]

            if mimestart is not None:
                if mimestart.split('/')[0] in ['video', 'audio', 'image']:
                    route = "generic_" + mimestart.split('/')[0]
                    extension = mimestart.split('/')[1]
            elif len(urlparse(self._source).path.split('/')[-1].split('.')) == 2:
                route = Media.GENERIC_FILE
        self._route_type = route
        self.extension = extension

    def fetch_file(self, size_limit:int=104857600):
        # 100MB
        resp = requests.get(self._source, stream=True)
        resp.raise_for_status()

        contents = bytes()
        # 8MB (8388608)
        curr_size = 0
        for chunk in resp.iter_content(8388608):
            curr_size += len(chunk)
            if curr_size > size_limit:
                resp.close()
                raise ValueError("response too large")
            contents += chunk
        self._content = contents

    def get_route_type(self):
        return self._route_type

    @staticmethod
    def is_web_media(src:str):
        """
        Returns true if media source is a web url to a proccessable website media
        """
        if validators.url(src):
            if src.startswith("https://www.youtube.com/watch?v=") or src.startswith("https://youtu.be/"):
                return True
            elif src.startswith("https://www.reddit.com/"):
                return True
            elif src.startswith("https://tenor.com/view/"):
                return True
        return False

class Streamable(Media):
    def __init__(self, source, gen_stream=True):
        super().__init__(source)
        # One time use discord streamable stream object
        self._stream = None
        self._web_src = None
        assert self._route_type in ['generic_video', 'generic_audio', 'youtube_media']
        if gen_stream:
            self.generate_stream()

    def __call__(self):
        return self.get_stream()

    def get_stream(self):
        if self._stream is None:
            self.generate_stream()
        # stream is one time use and is disposed of
        temp = self._stream
        self._stream = None
        return temp

    def generate_content(self):
        self.fetch_file()

    def get_content(self):
        if self._content is None:
            self.generate_content()
        return self._content

    def generate_stream(self, no_video=True):
        """Generates the streamables attributes for a Streamable object.
           sets self._name and self._stream. This function returns nothing"""

        # Options that seem to work perfectly (?)
        # ydl_options = {'format': 'bestaudio', 'noplaylist':'True'}
        # ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                        'options': '-vn'}
        if no_video:
            ydl_options = {'format': 'worseaudio/bestaudio',
                        'noplaylist':'True',
                        'youtube_include_dash_manifest': False}
        else:
            ydl_options = {'format': "bestvideo[filesize<8MiB][ext=mp4]+bestaudio/best",
                        'noplaylist':'True',
                        'youtube_include_dash_manifest': False}
        # That source is a youtube link
        if self._route_type == Media.GENERIC_AUDIO:
            with YoutubeDL(ydl_options) as ydl:
                info = ydl.extract_info(self._source, download=False)
                i = 0
                if not no_video:
                    i = len(info['formats'])
                    for fr in info['formats'][::-1]:
                        if fr['ext'] == "mp4" and fr['fps'] != None and fr['format_note'] != "tiny":
                            if fr['filesize'] != None and fr['filesize'] < 8388608:
                                break
                        i -= 1
                        if i == 0:
                            raise AssertionError("No suitable format found, too large")
                url = info['formats'][i]['url']
                self.youtube_src = url

                self._name = info['title']
                self._stream = discord.FFmpegPCMAudio(url, **ffmpeg_options)

        # The source is a link to a file TODO: Implement properly
        elif self._route_type in ["generic_video", "generic_audio"]:
            self._name = self._source.split('/')[-1]
            if no_video:
                self._stream = discord.FFmpegPCMAudio(self._source, **ffmpeg_options)

    def __repr__(self):
        "streamableMedia<{0}>".format(self._name)

class Static(Media):
    def __init__(self, source, gen_content=True):
        super().__init__(source)
        if gen_content:
            self.generate_content()

    def get_content(self):
        return self._content

    def __repr__(self):
        "staticMedia<{0}>".format(self._name)

    def generate_content(self):
        self.fetch_file()

# Need to improve on queue editing, design
# add youtube query
class Player:
    """BillyBot's unique player"""

    _players = []  # static variable containing ALL player objects

    def __init__(self, guild, bot):
        self._players.append(self)

        self._guild = guild  # The guild that the player is binded to
        self._bot = bot

        self._loop = False # Is the player in loop state
        self._queue = [] # The queue of songs in order

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
            voice.play(media.get_stream(), after=lambda e: self.next())

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
