import mimetypes
import os
import random
import re
import tempfile
import threading
import time
from urllib.parse import urlparse

import discord
import nest_asyncio
import ffmpeg
import requests
import validators
import asyncio
from discord.utils import get
from youtube_dl import YoutubeDL

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
        self._local = None
        self._thumbnail = None

        self.force_audio_only = force_audio_only
        self.speed = speed

        self._source = source
        self.source_route()
        assert self._route_type is not None

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
        for tag in re.findall('{"videoId":".{11}",', resp.content.decode('utf-8')):
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
            ydl_options = {'noplaylist': True,
                        'youtube_include_dash_manifest': False}
            #ydl_options = {'format': 'bestvideo+bestaudio/bestaudio/bestvideo[ext=gif]/best',
            #            'noplaylist':'True',
            #            'youtube_include_dash_manifest': False}

        route = None
        extension = None
        name = None
        info = {}
        force_raw_source = False
        local = None
        thumbnail = None
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
                        if len(info["thumbnails"]):
                            thumbnail = info["thumbnails"][-1]["url"]
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
        elif self._source.startswith("shitpost"):
            _, shitpost_id = self._source.split("shitpost")
            shitpost_id = int(shitpost_id)

            for filename in os.listdir("resources/dynamic/shitposts/"):
                if filename.startswith(f"shitpost{shitpost_id}"):
                    name = f"shitpost{shitpost_id}"
                    info = {"id": name, "ext": filename.split('.')[-1]}
                    extension = info["ext"]

                    mimestart = mimetypes.guess_type(filename)[0]
                    route = "generic_" + mimestart.split('/')[0]
                    local = f"resources/dynamic/shitposts/{filename}"
                    break

        self._route_type = route
        self._name = name
        self._extension = extension
        self._info = info
        self._local = local
        self._thumbnail = thumbnail

    def fetch_file(self, size_limit:int=104857600):
        if self._local is None:
            # 100MB
            no_video = self.force_audio_only
            ultimate_sources = self.get_ultimate_sources(no_video=no_video, sizelimit=size_limit)
            def download_source(source:str):
                resp = requests.get(source, stream=True)
                if resp.status_code != 200:
                    print(f"STATUS CODE {resp.status_code} ERROR IN FETCH_FILE")
                    return None
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
                audio_contents = False
                video_contents = False
                if len(ultimate_sources['audio']) > 0:
                    audio_contents = download_source(ultimate_sources['audio'][0])
                if len(ultimate_sources['video']) > 0:
                    video_contents = download_source(ultimate_sources['video'][0])

                if audio_contents and video_contents:
                    try:
                        Media.TEMPFILE_LOCK.acquire()
                        audio_tempfile_fd, audio_tempfile_name   = tempfile.mkstemp()
                        video_tempfile_fd, video_tempfile_name   = tempfile.mkstemp()
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
                elif video_contents:
                    output_data = video_contents
                else:
                    self._content = None
                    return None
            self._content = output_data
        else:
            with open(self._local, "rb") as local_file:
                self._content = local_file.read()
        return self._content

    def generate_stream(self) -> bool:
        """Generates the audio stream for the media object
           :sets: self._stream
           :returns: bool of the function's success"""

        assert self.is_streamable()

        no_video = True
        if self._local is None:
            ffmpeg_options = Media.STREAM_FFMPEG_OPTIONS.copy()
        else:
            ffmpeg_options = {'options': ""}
        if self.speed != 1.0:
            ffmpeg_options['options'] += f' -filter:a "atempo={self.speed}" '
        if no_video:
            ffmpeg_options['options'] += ' -vn '

        if self._local is None:
            ultimate_sources = self.get_ultimate_sources(no_video=no_video)
            if ultimate_sources['audio'] is not None:
                self._stream = discord.FFmpegPCMAudio(ultimate_sources['audio'][0], **ffmpeg_options)
                return True
        else:
            self._stream = discord.FFmpegPCMAudio(os.path.join(os.path.curdir, self._local), **ffmpeg_options)
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

        def filter_formats() -> dict:
            details = {'quality': -1, 'format_note': "", 'filesize': None}
            for fr in self._info['formats']:
                for detail in details:
                    if detail not in fr:
                        fr[detail] = details[detail]
                if 'fragment_base_url' in fr:
                    if fr['url'].startswith("https://manifest.googlevideo.com/api/manifest/"):
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
                            # assert x['acodec'] == 'none'
                            pass
                    if 'vcodec' in x:
                        if is_video:
                            assert x['vcodec'] != 'none'
                        else:
                            assert x['vcodec'] == 'none'

                    assert '.m3u8' not in x['url']

                    return True
                except AssertionError:
                    return False

            # info['formats'][-1]['url']
            audio_suggestion = [x['url'] for x in arr if format_condition(x, ('mp4', 'm4a', 'webm'), is_video=False)][::-1]
            if not no_video:
                video_suggestion = [x['url'] for x in arr if format_condition(x, ('mp4', 'm3u8', 'webm'), is_video=True)][::-1]
            else:
                video_suggestion = []
                # video_suggestions = [x['url'] for x in arr if format_condition(x, ("mp4",))]
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
            if no_video:
                return {'video': [], 'audio': [self._source,]}
            else:
                return {'video': [self._source,], 'audio': []}
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

    def get_file_extension(self):
        return f"{self._info['ext']}"

    def get_thumbnail(self):
        return self._thumbnail

    def is_streamable(self):
        return self._route_type in (Media.GENERIC_AUDIO, Media.GENERIC_VIDEO)

    def is_web_media(self) -> bool:
        """
        Returns True if the media needs to be web proccessed on demand
        Returns False if the media is to a raw source
        Also returns False if the media is of web type but the proccesing can be done immediately.
        This function will silently perform the immediate proccessing.
        """
        if validators.url(self._source):
            if self._source.startswith("https://www.youtube.com/shorts/"):
                self._source = "https://www.youtube.com/watch?v=" + self._source.split("https://www.youtube.com/shorts/")[-1]

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

class Player:
    """BillyBot's unique player"""

    _players = []  # static variable containing ALL player objects
    PLAYER_EMBED_COLOR = 16711680

    STOPPED = 0
    PAUSED  = 1
    PLAYING = 2

    class PlayerView(discord.ui.View):
        def __init__(self, player):
            super().__init__()
            self.player = player

        @discord.ui.button(label="Refresh", style=discord.ButtonStyle.secondary, emoji="🔄")
        async def refresh_callback(self, button:discord.ui.Button, interaction:discord.interactions.Interaction):
            await interaction.response.edit_message(embed=self.player.make_embed(), view=self)

        @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, emoji="⏹️", disabled=True)
        async def stop_callback(self, button:discord.ui.Button, interaction:discord.interactions.Interaction):
            if button.label == "Stop":
                await self.player.stop()
                #button.label = "Remove"
                #button.emoji = ""
                #await interaction.response.edit_message(embed=self.player.make_embed, view=self)
            if button.label == "Remove":
                await self.player.wipe_and_remove()
                # embed = discord.Embed(title="BillyBot Music Player", description=f"Player was stopped by {interaction.user}")
                # await interaction.response.edit_message(view=None, embed=embed, delete_after=300)
            await interaction.response.edit_message()

        @discord.ui.button(label="Pause", style=discord.ButtonStyle.success, emoji="⏸️")
        async def pause_resume_callback(self, button:discord.ui.Button, interaction:discord.interactions.Interaction):
            if button.label == "Resume":
                button.emoji = "⏸️"
                button.label = "Pause"
                button.view.children[0].disabled = True
                await self.player.resume()
            elif button.label == "Pause":
                button.emoji = "▶️"
                button.label = "Resume"
                button.view.children[0].disabled = False
                await self.player.pause()
            await interaction.response.edit_message()

        @discord.ui.button(label="Skip", style=discord.ButtonStyle.primary, emoji="⏩")
        async def skip_callback(self, button:discord.ui.Button, interaction:discord.interactions.Interaction):
            await interaction.response.edit_message()
            await self.player.next()

        @discord.ui.button(label="Loop", style=discord.ButtonStyle.secondary, emoji="🔂")
        async def loop_callback(self, button:discord.ui.Button, interaction:discord.interactions.Interaction):
            await self.player.toggle_loop()
            await interaction.response.edit_message()

        @discord.ui.button(label="Shuffle", style=discord.ButtonStyle.secondary, emoji="🔀")
        async def shuffle_callback(self, button:discord.ui.Button, interaction:discord.interactions.Interaction):
            await self.player.shuffle()
            await interaction.response.edit_message()

    def __init__(self, guild, bot):
        self._players.append(self)

        self._guild = guild  # The guild that the player is binded to
        self._bot = bot

        self.state = Player.STOPPED

        self._loop = False # Is the player in loop state
        self._queue = [] # The queue of songs in order
        self.binding = None
        self._skip_flag = False

        self.view = Player.PlayerView(self)
        self.embed = None

    def current_song(self):
        """Returns the name of the current song"""
        return self._queue[0].get_name()

    #region player control
    async def _next(self):
        if self._skip_flag:
            self._skip_flag = False
        else:
            self._skip_flag = True
            await self.next()

    async def next(self):
        """Skips to the next song in the queue"""

        self._skip_flag = not self._skip_flag
        voice = get(self._bot.voice_clients, guild=self._guild)
        if voice is not None:
            if voice.is_playing():
                voice.stop()

            if len(self._queue) > 0:
                if self._loop:
                    self._queue.append(self._queue.pop(0))
                else:
                    self._queue.pop(0)

            if len(self._queue) > 0:
                next_song = self._queue[0]
                print("Playing {0} on guild {1}".format(next_song.get_name(), self.get_guild().name))
                strm = next_song.get_stream()
                voice.play(strm, after=lambda e: asyncio.run(self._next()))
                self._set_state(Player.PLAYING)
            else:
                self._set_state(Player.STOPPED)
        else:
            print("hmm test this one") # TODO: DEBUG

        try:
            if self.binding:
                await self.binding.edit(view=self.view, embed=self.make_embed())
        except Exception as e:
            pass

    async def play(self, media):
        """Adds a Media object to the queue"""

        voice = get(self._bot.voice_clients, guild=self._guild)

        assert media is not None
        # Adds to queue if media is not None
        self._queue.append(media)

        # Plays now if nothing is playing
        if self._queue[0] == media:
            strm = media.get_stream()
            voice.play(strm, after=lambda e: asyncio.run(self._next()))
            self._set_state(Player.PLAYING)

        if self.binding:
            await self.binding.edit(view=self.view, embed=self.make_embed())

    async def stop(self):
        """Stops and clears the queue"""
        self._queue = []
        voice = get(self._bot.voice_clients, guild=self._guild)
        if voice is not None:
            get(self._bot.voice_clients, guild=self._guild).stop()
        self._set_state(Player.STOPPED)

        if self.binding:
            await self.binding.edit(view=self.view, embed=self.make_embed())

    async def pause(self):
        """Pauses play"""
        if self.state == Player.PLAYING:
            self._set_state(Player.PAUSED)
            get(self._bot.voice_clients, guild=self._guild).pause()

        if self.binding:
            await self.binding.edit(view=self.view, embed=self.make_embed())

    async def resume(self):
        """Resumes to playing the queue"""
        if self.state == Player.PAUSED:
            self._set_state(Player.PLAYING)
            get(self._bot.voice_clients, guild=self._guild).resume()

        if self.binding:
            await self.binding.edit(view=self.view, embed=self.make_embed())

    async def wipe_and_remove(self, issuer=None):
        """Stops playing and wipes the player back into default settings"""
        self._queue = []
        voice = get(self._bot.voice_clients, guild=self._guild)
        if voice is not None:
            get(self._bot.voice_clients, guild=self._guild).stop()
        self._set_state(Player.STOPPED)

        self._loop = False

        Player._players.remove(self)

        if self.binding:
            embed = discord.Embed(title="BillyBot Music Player", description=f"Player was stopped by {issuer}")
            await self.binding.edit(view=None, embed=embed, delete_after=300)

    async def toggle_loop(self):
        """Toggles loop"""
        self._loop = not self._loop

        if self.binding:
            await self.binding.edit(view=self.view, embed=self.make_embed())

        return self._loop

    async def shuffle(self):
        """Shuffles the queue"""
        if len(self._queue) > 0:
            temp = self._queue.pop(0)
            random.shuffle(self._queue)
            self._queue.insert(0, temp)

        if self.binding:
            await self.binding.edit(view=self.view, embed=self.make_embed())
    #endregion

    def get_guild(self):
        """Returns the guild this player is attached to"""
        return self._guild

    async def bind_player_to_ctx(self, ctx):
        if self.binding is not None:
            raise AssertionError("Cannot bind player that is already bound!")
        await ctx.respond("", embed=self.make_embed(), view=self.view)
        self.binding = ctx

    @staticmethod
    def get_player(guild):
        for player in Player._players:
            if player.get_guild() == guild:
                return player
        return None

    def get_queue(self):
        """Returns the player's queue"""
        return self._queue

    def get_bot(self):
        return self._bot

    def make_embed(self) -> discord.Embed:
        thumbnail = None

        embed_field_list = []
        queue_len = len(self._queue)
        if queue_len:
            embed_field_list.append(
                discord.EmbedField(
                    name="Currently Playing",
                    value=self._queue[0].get_name()
                    )
                )
            thumbnail = self._queue[0].get_thumbnail()
            if queue_len > 1:
                embed_field_list.append(
                    discord.EmbedField(
                        name = "Playing Next",
                        value=self._queue[1].get_name()
                    )
                )
        if len(embed_field_list) == 0:
            embed_field_list = None

        output = discord.Embed(
            title="BillyBot Music Player",
            description=f"Queue size: {queue_len}",
            color=Player.PLAYER_EMBED_COLOR,
            fields=embed_field_list,
        )
        if thumbnail:
            output.set_thumbnail(url=thumbnail)
        if queue_len > 2:
            output.set_footer(text=", ".join(media.get_name() for media in self._queue[2::]))

        return output

    def _set_state(self, new_state):
        match new_state:
            case Player.PAUSED:
                pass
            case Player.STOPPED:
                pass
            case Player.PLAYING:
                pass

        self.state = new_state