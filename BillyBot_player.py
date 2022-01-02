import random
from discord.utils import get
import BillyBot_utils as bb_utils

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
        if self not in self._players:
            self._players.append(self)

            self._guild = guild
            self._bot = bot
            self._loop = False
            self._queue = []
        else:
            # I need to know when a player gets duped
            del self
            raise Exception()

    def shuffle(self):
        """Shuffles the queue"""
        random.shuffle(self._queue)

    def toggle_loop(self):
        """Toggles loop"""
        #self._loop = not self._loop
        return self._loop

    def next(self):
        """Skips to the next song in the queue"""

        voice = get(self._bot.voice_clients, guild=self._guild)
        if voice.is_playing():
            voice.stop()
            return

        if self._loop:
            self.get_queue().append(self.get_queue().pop(0))
        else:
            self.get_queue().pop(0)

        if len(self.get_queue()) > 0:
            print("Playing {0} on guild {1}".format(self.get_queue()[0].get_name(), self.get_guild.__name__))
            voice.play(self.get_queue()[0].get_playable(), after=lambda e: self.next())

    def current_song(self):
        """Returns the name of the current song"""
        return self.get_queue()[0].get_name()

    async def play(self, source:bb_utils.Media):
        """Adds a to the queue

            assumes source is valid"""

        # Adds to queue if media is not None
        self._queue.append(source)

        # Plays now if nothing is playing
        voice = get(self._bot.voice_clients, guild=self._guild)
        if self._queue[0] == source:
            voice.play(source.get_playable(), after=lambda e: self.next())

    async def stop(self):
        """Stops and clears the queue"""
        get(self._bot.voice_clients, guild=self._guild).stop()
        self._queue = []

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
        """Wipes the player back into default settings"""
        self._loop = False
        self._queue = []

    def get_bot(self):
        return self._bot
