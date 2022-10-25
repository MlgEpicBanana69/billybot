import random
import re
import requests
import mimetypes
import validators
from youtube_dl import YoutubeDL
from urllib.parse import urlparse
import discord
from discord.utils import get

mimetypes.init()

class Media:
    GENERIC_IMAGE = "generic_image"
    GENERIC_VIDEO = "generic_video"
    GENERIC_AUDIO = "generic_audio"
    GENERIC_FILE  = "generic_file"

    # Options that seem to work perfectly (?)
    # ydl_options = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': ''}
    FFMPEG_OPTIONS_NO_VIDEO = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    DISCORD_FILE_LIMITERS = (8388608,)

    def __init__(self, source, *, force_audio_stream_options=False):
        self._name = None
        self._content = None
        self._route_type = None
        self._stream = None
        self._info = {}
        self._extension = None
        self.force_audio_stream_options = force_audio_stream_options

        self._source = source
        self.source_route()
        assert self._route_type is not None

    def __call__(self):
        return self.get_content()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "BBMedia<{0}>".format(self._name)

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

        if self.force_audio_stream_options:
            ydl_options = {'format': 'bestaudio',
                        'noplaylist':'True',
                        'youtube_include_dash_manifest': False}
        else:
            ydl_options = {'format': 'bestvideo+bestaudio/bestaudio/bestvideo[ext=gif]/best',
                        'noplaylist':'True',
                        'youtube_include_dash_manifest': False}

        route = None
        extension = None
        name = None
        info = {}
        force_raw_source = False
        if validators.url(self._source):
            is_media = self.is_web_media()
            if is_media:
                with YoutubeDL({}) as ydl:
                    info = ydl.extract_info(self._source, download=False)
                    if 'entries' in info:
                        raise AssertionError
                        #info = info['entries'][0]
                        #force_raw_source = True
                        #self._source = info['url']
                    else:
                        if 'formats' in info:
                            pass # self._source = info['formats'][-1]['url']
                        elif 'thumbnails' in info:
                            self._source = info['thumbnails'][-1]['url']
                        else:
                            raise AssertionError("osuHOW") # NOTE shouldn't occur
                        mimestart = mimetypes.guess_type(f"{info['id']}.{info['ext']}")[0]
                    name = info["title"]
            if (not is_media and ('.' in self._source and '/' in self._source)) or force_raw_source:
                mimestart = mimetypes.guess_type(urlparse(self._source).path.split('/')[-1])[0]
                name = urlparse(self._source).path.split('/')[-1]
                info = {"url": self._source, "id": ".".join(name.split('.')[:-1]), "ext": name.split('.')[-1]}

            if mimestart is not None:
                if mimestart.split('/')[0] in ['video', 'audio', 'image']:
                    route = "generic_" + mimestart.split('/')[0]
                    extension = mimestart.split('/')[1]
            elif len(urlparse(self._source).path.split('/')[-1].split('.')) == 2:
                route = Media.GENERIC_FILE
        self._route_type = route
        self._name = name
        self._extension = extension
        self._info = info

    def fetch_file(self, size_limit:int=104857600):
        # 100MB
        resp = requests.get(self._source, stream=True)
        resp.raise_for_status()

        contents = bytes()
        # 4MB (4194304)
        curr_size = 0
        for chunk in resp.iter_content(4194304):
            curr_size += len(chunk)
            if curr_size > size_limit:
                resp.close()
                raise ValueError("response too large")
            contents += chunk
        self._content = contents

    def generate_stream(self, no_video:bool=True):
        """Generates the streamables attributes for a Streamable object.
           :sets: self._stream
           :returns: None"""

        assert self.is_streamable()

        if no_video:
            ydl_options = {'format': 'worseaudio/bestaudio',
                        'noplaylist':'True',
                        'youtube_include_dash_manifest': False}
        else:
            ydl_options = {'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
                    'noplaylist':'True',
                    'youtube_include_dash_manifest': False}

        #ydl_options = {'format': "bestvideo[filesize<8MiB][ext=mp4]+bestaudio/best",
        #            'noplaylist':'True',
        #            'youtube_include_dash_manifest': False}

        if no_video:
            ffmpeg_options = Media.FFMPEG_OPTIONS_NO_VIDEO
        else:
            ffmpeg_options = Media.FFMPEG_OPTIONS

        format_change_required = (no_video or self._route_type == Media.GENERIC_VIDEO)
        premade_audio_stream   = (no_video or self.force_audio_stream_options)
        different_source = (format_change_required and not premade_audio_stream)
        is_web_media = self.is_web_media()

        if (len(self._info) <= 1 or different_source) and is_web_media:
            with YoutubeDL(ydl_options) as ydl:
                info = ydl.extract_info(self._source, download=False)
                url = Media.choose_best_format(info, no_video)
                self._stream = discord.FFmpegPCMAudio(url, **ffmpeg_options)
        elif is_web_media and len(self._info) > 1:
            url = Media.choose_best_format(self._info, no_video)
            self._stream = discord.FFmpegPCMAudio(url, **ffmpeg_options)
        else:
            self._stream = discord.FFmpegPCMAudio(self._source, **ffmpeg_options)

    def get_name(self):
        return self._name

    def get_route_type(self):
       return self._route_type

    def get_stream(self):
        if self._stream is None:
            self.generate_stream()
        # stream is one time use and is disposed of
        temp = self._stream
        self._stream = None
        return temp

    def get_extension(self):
        return self._extension

    def get_content(self):
        return self._content

    def get_source(self):
        return self._source

    def get_filename(self):
        return f"{self._info['id']}.{self._info['ext']}"

    def is_streamable(self):
        return self._route_type in (Media.GENERIC_AUDIO, Media.GENERIC_VIDEO)

    def is_web_media(self) -> bool:
        """
        Returns true if the media needs to be web proccessed on demand
        Returns false if the media is to a raw source
        Also returns false if the media is of web type but the proccesing can be done immediately.
        This function will silently perform the immediate proccessing.
        """
        if validators.url(self._source):
            if self._source.startswith("https://www.youtube.com/watch?v=") or self._source.startswith("https://youtu.be/"):
                return True
            elif self._source.startswith("https://www.reddit.com/"):
                return True
            elif self._source.startswith("https://tenor.com/view/"):
                tenor_resp = requests.get(self._source)
                matches = re.search("https:\/\/media\.tenor\.com\/.+?\/.+?\.gif", tenor_resp.text)
                self._source = matches.group(0)
                return False
            elif self._source.startswith("https://twitter.com/") and (not "/photo/" in self._source):
                return True
        return False

    @staticmethod
    def choose_best_format(info:dict, no_video:bool, max_filesize:int=None) -> str:
        i = 0
        if not no_video:
            i = len(info['formats'])
            for fr in info['formats'][::-1]:
                if fr['ext'] == "mp4" and fr['fps'] != None and fr['format_note'] != "tiny":
                    if fr['filesize'] != None:
                        if max_filesize is None:
                            break
                        elif fr['filesize'] < max_filesize:
                            break
                i -= 1
                if i == 0:
                    raise AssertionError("No suitable format found, probably too large")
        url = info['formats'][i]['url']
        return url

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
                next_song = self.get_queue()[0]
                print("Playing {0} on guild {1}".format(next_song.get_name(), self.get_guild().name))
                strm = next_song.get_stream()
                voice.play(strm, after=lambda e: self.next())

    def current_song(self):
        """Returns the name of the current song"""
        return self.get_queue()[0].get_name()

    async def play(self, media):
        """Adds a Media object to the queue"""

        voice = get(self._bot.voice_clients, guild=self._guild)

        assert media is not None
        # Adds to queue if media is not None
        self._queue.append(media)

        # Plays now if nothing is playing
        if self._queue[0] == media:
            strm = media.get_stream()
            voice.play(strm, after=lambda e: self.next())

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
