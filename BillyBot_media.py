import random
import re
import requests
import mimetypes
import validators
from youtube_dl import YoutubeDL
from urllib.parse import urlparse
import discord
from discord.utils import get
import ffmpeg
import os
import tempfile
import threading

mimetypes.init()

class Media:
    GENERIC_IMAGE = "generic_image"
    GENERIC_VIDEO = "generic_video"
    GENERIC_AUDIO = "generic_audio"
    GENERIC_FILE  = "generic_file"
    TEMPFILE_LOCK = threading.Lock()

    # Options that seem to work perfectly (?)
    # ydl_options = {'format': 'bestaudio', 'noplaylist':'True'}
    STREAM_FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': ''}

    DISCORD_FILE_LIMITERS = (8388608,)

    def __init__(self, source:str, *, speed:float=1.0, force_audio_only:bool=False):
        assert speed >= 0.5 and speed <= 20.0

        self._name = None
        self._content = None
        self._route_type = None
        self._stream = None
        self._info = {}
        self._extension = None

        self.force_audio_only = force_audio_only
        self.speed = speed

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

        if self.force_audio_only:
            ydl_options = {'format': 'bestaudio/best',
                        'noplaylist': True,
                        'youtube_include_dash_manifest': False}
        else:
            ydl_options = {}
            #ydl_options = {'format': 'bestvideo+bestaudio/bestaudio/bestvideo[ext=gif]/best',
            #            'noplaylist':'True',
            #            'youtube_include_dash_manifest': False}

        route = None
        extension = None
        name = None
        info = {}
        force_raw_source = False
        if validators.url(self._source):
            is_media = self.is_web_media()
            if is_media:
                with YoutubeDL(ydl_options) as ydl:
                    info = ydl.extract_info(self._source, download=False)
                    if 'entries' in info:
                        raise AssertionError("Entries in info")
                        #info = info['entries'][0]
                        #force_raw_source = True
                        #self._source = info['url']
                    else:
                        if 'formats' in info:
                            mimestart = f'video/{info["ext"]}'
                        elif 'thumbnails' in info:
                            self._source = info['thumbnails'][-1]['url']
                            mimestart = mimetypes.guess_type(f"{info['id']}.{info['ext']}")[0]
                        else:
                            raise AssertionError("osuHOW") # NOTE shouldn't occur
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
        no_video = self.force_audio_only
        ultimate_sources = self.get_ultimate_sources(no_video=no_video, sizelimit=size_limit)
        def download_source(source:str):
            resp = requests.get(source, stream=True)
            resp.raise_for_status()
            contents = bytes()
            # 4MB (4194304)
            curr_size = 0
            for chunk in resp.iter_content(65536):
                curr_size += len(chunk)
                if curr_size > size_limit:
                    resp.close()
                    return None
                contents += chunk
            return contents

        # TODO: add error handling in case fetching file fails
        # TODO: Change ultimate sources interaction
        if no_video:
            output_data = download_source(ultimate_sources['audio'][0])
        else:
            # DO SOME PROCCESSING
            audio_contents = download_source(ultimate_sources['audio'][0])
            video_contents = download_source(ultimate_sources['video'][-1])

            try:
                Media.TEMPFILE_LOCK.acquire()
                audio_tempfile_fd, audio_tempfile_name   = tempfile.mkstemp(suffix=".m4a")
                video_tempfile_fd, video_tempfile_name   = tempfile.mkstemp(suffix=".mp4")
                merged_tempfile_fd, merged_tempfile_name = tempfile.mkstemp(suffix=".mp4")

                os.write(audio_tempfile_fd, audio_contents)
                os.write(video_tempfile_fd, video_contents)

                input_audio = ffmpeg.input(audio_tempfile_name)
                input_video = ffmpeg.input(video_tempfile_name)

                ffmpeg.concat(input_video, input_audio, v=1, a=1).output(merged_tempfile_name, loglevel="quiet").run(overwrite_output=True, )

                with open(merged_tempfile_name, "rb") as tfile:
                    output_data = tfile.read()
            finally:
                os.close(audio_tempfile_fd)
                os.close(video_tempfile_fd)
                os.close(merged_tempfile_fd)
                os.remove(audio_tempfile_name)
                os.remove(video_tempfile_name)
                os.remove(merged_tempfile_name)
                Media.TEMPFILE_LOCK.release()
        self._content = output_data
        return True

    def generate_stream(self) -> bool:
        """Generates the audio stream for the media object
           :sets: self._stream
           :returns: bool of the function's success"""

        assert self.is_streamable()

        no_video = True
        ffmpeg_options = Media.STREAM_FFMPEG_OPTIONS.copy()
        if self.speed != 1.0:
            ffmpeg_options['options'] += f' -filter:a "atempo={self.speed}" '
        if no_video:
            ffmpeg_options['options'] += ' -vn '

        ultimate_sources = self.get_ultimate_sources(no_video=no_video)
        if ultimate_sources['audio'] is not None:
            self._stream = discord.FFmpegPCMAudio(ultimate_sources['audio'][0], **ffmpeg_options)
            return True
        return False

    def get_ultimate_sources(self, *, no_video:bool, sizelimit:int=104857600) -> dict:
        if no_video:
            ydl_options = {'format': 'worseaudio/bestaudio',
                        'noplaylist':True,
                        'youtube_include_dash_manifest': False}
        else:
            ydl_options = {'format': 'bestvideo[ext=mp4]+bestaudio/bestvideo+bestaudio',
                    'noplaylist':True,
                    'youtube_include_dash_manifest': False}

        #ydl_options = {'format': "bestvideo[filesize<8MiB][ext=mp4]+bestaudio/best",
        #            'noplaylist':'True',
        #            'youtube_include_dash_manifest': False}

        def filter_formats() -> str:
            details = {'quality': -1, 'format_note': "", 'filesize': None}
            for fr in self._info['formats']:
                for detail in details:
                    if detail not in fr:
                        fr[detail] = details[detail]
                if 'fragment_base_url' in fr:
                    if fr['url'] != fr['fragment_base_url']:
                        fr['url'] = fr['fragment_base_url']

            arr = self._info['formats']
            arr = sorted(self._info['formats'], key=lambda i: i['quality'], reverse=False)
            def format_condition(x, exts, is_video) -> bool:
                try:
                    assert x['ext'] in exts or len(exts) == 0
                    # assert 'DASH' not in x['format_note']
                    assert x['filesize'] == None or x['filesize'] < sizelimit
                    if 'acodec' in x:
                        if not is_video:
                            assert x['acodec'] != 'none'
                        else:
                            assert x['acodec'] == 'none'
                    if 'vcodec' in x:
                        if is_video:
                            assert x['vcodec'] != 'none'
                        else:
                            assert x['vcodec'] == 'none'

                    return True
                except AssertionError:
                    return False

            # info['formats'][-1]['url']
            audio_suggestion = [x['url'] for x in arr if format_condition(x, ('mp4', 'm4a'), is_video=False)]
            if not no_video:
                video_suggestion = [x['url'] for x in arr if format_condition(x, ('mp4', 'm3u8'), is_video=True)]
            else:
                video_suggestion = []
                # video_suggestions = [x['url'] for x in arr if format_condition(x, ("mp4",))]
            if len(video_suggestion) == 0:
                video_suggestion = None
            if len(audio_suggestion) == 0:
                audio_suggestion = None
            return {'video': video_suggestion, 'audio': audio_suggestion}

        format_change_required = (no_video and self._route_type == Media.GENERIC_VIDEO) or (not no_video and self._route_type == Media.GENERIC_AUDIO)
        premade_audio_stream   = (no_video or self.force_audio_only)
        different_source = (format_change_required and not premade_audio_stream)
        is_web_media = self.is_web_media()

        ultimate_sources = None
        if ((len(self._info) <= 1 or different_source) and is_web_media):
            with YoutubeDL(ydl_options) as ydl:
                self._info = ydl.extract_info(self._source, download=False)
                urls = filter_formats()
                ultimate_sources = urls
        elif is_web_media and len(self._info) > 1:
            urls = filter_formats()
            ultimate_sources = urls
        else:
            ultimate_sources = (self._source,)
        return ultimate_sources

    def get_name(self):
        base = self._name + " "
        if self.speed != 1.0:
            base += f"({self.speed}x) "
        base = base[:-1:]

        return base

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
