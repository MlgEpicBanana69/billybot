"""BillyBot is a general purpose discord bot that barely works"""

import io
import os
import random

import aiohttp
import discord
from discord.ext import commands
from discord.utils import get
import cv2
import numpy as np
import validators

import BillyBot_utils as bb_utils
import BillyBot_minesweeper as bb_minesweeper
import BillyBot_media as bb_media

# Ideas:
#   osu statistics display
#   ghost ping logging
#   server managment commands
#   the ultimate shitpost database
#   Trade with TamaCrypto (Based!!)

# https://discord.com/api/oauth2/authorize?client_id=757490339425550336&permissions=8&scope=bot

intents = discord.Intents.default()
intents.members = True
BillyBot = commands.Bot(command_prefix='~', intents=intents)

# Every auto list contains a two dimension tuple containing the member id and guild id
# (id, guild_id)
auto_cyber_members = []
auto_say_members = []

@BillyBot.event
async def on_ready():
    """Does the initial setup for BillyBot"""
    # Generates and binds a player for all of the guilds
    for guild in BillyBot.guilds:
        bb_media.Player(guild, BillyBot)
    await BillyBot.change_presence(status=discord.Status.online, activity=discord.Game("Pogging rn use ~ for stuff"))
    print("Logged on as {0}!".format(BillyBot.user))

@BillyBot.event
async def on_message(message):
    """Handles stuff that need to be handled on every message"""
    print("{0} on {1} -> #{2}: {3}".format(str(message.author), str(message.guild),
                                          str(message.channel), message.content))
    # auto-say
    if message.guild is not None:
        if (message.author.id, message.guild.id) in auto_say_members:
            await say(ctx=message, message=message.content)
    await BillyBot.process_commands(message)

@BillyBot.event
async def on_guild_join(guild):
    bb_media.Player(guild, BillyBot)

@BillyBot.command(aliases=["Mute", "mutee", "mut", "Mutee", "Mut"])
@commands.has_permissions(mute_members=True)
async def mute(ctx, member : discord.Member):
    """Mutes a member or everyone in your voice call with the argument all"""
    if member == "all" and ctx.voice is not None:
        for participant in ctx.voice.channel.members:
            await participant.edit(mute=True)
    else:
        await member.edit(mute=True)

@BillyBot.command(aliases=["UnMute", "unmutee", "unmut", "UnMutee", "UnMut", "Unmute", "ummute", "Ummute"])
@commands.has_permissions(mute_members=True)
async def unmute(ctx, member : discord.Member):
    """Unmutes a member or everyone in your voice call with the argument all"""
    if member == "all" and ctx.voice is not None:
        for participant in ctx.voice.channel.members:
            participant.edit(mute=False)
    else:
        await member.edit(mute=False)

@BillyBot.command()
async def getsource(ctx, source):
    """May or may not be illegal. Lawsuit may be pending..."""

    media = await bb_utils.download_media(source)
    await ctx.channel.send(media)

@BillyBot.command(aliases=["Play", "pla", "Pla", "p", "P"])
async def play(ctx, *, source=None):
    """Plays audio from an audio source"""

    # Builds the player incase the server aint got one
    if bb_media.Player.get_player(ctx.guild) is None:
        bb_media.Player(ctx.guild, BillyBot)
    await join(ctx)

    # Playing a 'source' goes by a these rules:
    # 1) An audio file is embeded, play that audio file
    # 2) A link is requested, depending on where that link leads, fetch the audio file and play it
    # 3) A query is requested, search that query on youtube and recommand multiple best results

    # Few key notes, a source cannot be theoretically invalid
    # also when multiple sources are given, BillyBot takes only the first one
    # further attachments are *completely* ignored.

    guild_player = bb_media.Player.get_player(ctx.guild)
    if len(ctx.message.attachments) > 0:
        attachment = ctx.message.attachments[0]
        await join(ctx)
        await guild_player.play(attachment.url)
        return
    elif validators.url(source):
        media = await bb_utils.get_media(source)
        if media is not None:
            await guild_player.play(media)
        else:
            # debug
            # might want to give feedback on why
            pass
    elif source is not None:
        raise NotImplementedError()
    else:
        ctx.message.channel.send("what")

@BillyBot.command(aliases=["Stop", "Stoop", "stoop", "Sto", "sto", "stopp", "Stopp", "Clear", "clear"])
async def stop(ctx):
    """Stops the music and clears the queue"""
    await bb_media.Player.get_player(ctx.guild).stop()

@BillyBot.command(aliases=["Pause"])
async def pause(ctx):
    """Pauses the current song"""
    if ctx.guild.me.voice.channel == ctx.author.voice.channel and ctx.guild.me.voice is not None:
        await ctx.channel.send("Now paused.")
        await bb_media.Player.get_player(ctx.guild).pause()

@BillyBot.command(aliases=["Resume"])
async def resume(ctx):
    """Pauses the current song"""
    if ctx.guild.me.voice.channel == ctx.author.voice.channel and ctx.guild.me.voice is not None:
        await ctx.channel.send("Resumed.")
        await bb_media.Player.get_player(ctx.guild).resume()

@BillyBot.command(aliases=["Next", "next", "skip", "Skip"])
async def next_song(ctx):
    """Skips to the next song in queue"""
    bb_media.Player.get_player(ctx.guild).next()

@BillyBot.command(aliases=["Shuffle"])
async def shuffle(ctx):
    """Shuffles the queue"""
    bb_media.Player.get_player(ctx.guild).shuffle()

@BillyBot.command(aliases=["Loop", "loop"])
async def toggle_loop(ctx):
    """Toggles playlist loop on/off"""
    loop_state = bb_media.Player.get_player(ctx.guild).toggle_loop()
    loop_state = "ON" if loop_state else "OFF"
    await ctx.channel.send("Loop state is now {0}".format(loop_state))

@BillyBot.command(aliases=["Goto", "GoTo"])
async def goto(ctx, position : int):
    """Skips to a position in queue"""
    await bb_media.Player.get_player(ctx.guild).goto(position)

@BillyBot.command(aliases=["Ban"])
@commands.has_permissions(administrator=True)
async def ban(ctx, member:discord.User, reason=""):
    await ctx.guild.ban(member, reason=reason)
    ctx.channel.send(f"{member} got fucked")

@BillyBot.command(aliases=["current"])
async def current_song(ctx):
    """Shows the current song that is playing"""
    guild_player = bb_media.Player.get_player(ctx.guild)
    if len(guild_player.get_sourcenames()) > 0:
        await ctx.channel.send("Currently playing {0} at position: {1}".format(guild_player.current_song()[0], guild_player.current_song()[1]))
    else:
        await ctx.channel.send("I am currently not playing anything!")

@BillyBot.command(aliases=["Queue", "queue", "q", "Q"])
async def song_queue(ctx):
    """Displays the current queue"""
    guild_player = bb_media.Player.get_player(ctx.guild)
    queue_string = "\n".join([media.get_name() for media in guild_player.get_queue()])
    if queue_string != "":
        await ctx.channel.send(queue_string)
    else:
        await ctx.channel.send("I am not playing anything right now!")

@BillyBot.command(aliases=["Join"])
async def join(ctx):
    """Joins into your voice channel."""
    if ctx.author.voice is None:
        await ctx.channel.send("You're not in any voice channel.")
        return
    elif ctx.guild.voice_client is None:
        await ctx.author.voice.channel.connect()
        get(BillyBot.voice_clients, guild=ctx.guild).stop()
    elif ctx.guild.voice_client.channel != ctx.author.voice.channel:
        await ctx.guild.me.move_to(ctx.author.voice.channel)

    try:
        await ctx.guild.me.edit(deafen=True)
    except discord.errors.Forbidden:
        pass # Silent permission error because the self deafen is purely cosmetic kekW

@BillyBot.command(aliases=["Leave", "leav", "Leav", "fuckoff"])
async def leave(ctx):
    """Leaves voice channel."""
    if ctx.guild is None:
        await ctx.channel.send("What")
    if ctx.guild.voice_client is not None:
        await ctx.guild.voice_client.disconnect()
        bb_media.Player.get_player(ctx.guild).wipe()
    else:
        await ctx.message.channel.send("I'm not in a voice channel! Use {0}join to make me join one.".format(BillyBot.command_prefix))

@BillyBot.command(aliases=["why", "Why", "Squaretext", "SquareText", "square", "Square", "wwhy", "Wwhy"])
async def squaretext(ctx, *, message):
    """Squares text. Example: pog -> p\npo\npog\npo\np"""

    final_message = ""
    build_up = []
    message_by_lines = []
    penelty = 0
    for i in range(len(message)):
        build_up.append(i)
        new_line = ""
        for num in build_up:
            new_line += message[num]
        if new_line[-1] == ' ':
            new_line = new_line[:-1]
        if new_line not in message_by_lines:
            message_by_lines.append(new_line)
            final_message += message_by_lines[i - penelty]
            final_message += "\n"
        else:
            penelty += 1
    penelty = 0
    message_by_lines = []
    for i in range(len(message) - 1):
        del build_up[-1]
        new_line = ""
        for num in build_up:
            new_line += message[num]
        if new_line[-1] == ' ':
            new_line = new_line[:-1]
        if new_line not in message_by_lines:
            message_by_lines.append(new_line)
            final_message += message_by_lines[i - penelty]
            final_message += "\n"
        else:
            penelty += 1
    if len(final_message) <= 2000:
        await ctx.message.channel.send(final_message)
    elif len(final_message) <= 20000:
        splitted_message = ""
        splitted_final_message = []
        for line in final_message.split("\n"):
            if len(splitted_message + line + "\n") <= 2000:
                splitted_message += line + "\n"
            else:
                splitted_final_message.append(splitted_message)
                splitted_message = ""
        if splitted_message != "":
            splitted_final_message.append(splitted_message)

        for part in splitted_final_message:
            await ctx.message.channel.send(part)
    else:
        await ctx.channel.send(content="", file=discord.File(fp=io.StringIO(final_message), filename="squared_text.txt"))

@BillyBot.command(aliases=["Cyber", "CYBER", "cybee", "Cybee"])
async def cyber(ctx, *args):
    """Overlays the text סייבר on a given image."""
    img_objects = []
    if ctx.message.attachments != []:
        for attachment in ctx.message.attachments:
            if attachment.height is not None:
                attachment_bytestring = await attachment.read()
                img_object = cv2.imdecode(np.frombuffer(attachment_bytestring, np.uint8), cv2.IMREAD_UNCHANGED)
                if len(img_object[0, 0]) == 3:
                    img_object = cv2.cvtColor(img_object, cv2.COLOR_RGB2RGBA)
                img_objects.append(img_object)
    if len(args) > 0:
        for img_link in args:
            if validators.url(img_link):
                async with aiohttp.ClientSession() as session:
                    async with session.get(img_link) as resp:
                        if resp.status == 200:
                            img_bytestring = await resp.read()
                            img_object = cv2.imdecode(np.frombuffer(img_bytestring, np.uint8), cv2.IMREAD_UNCHANGED)
                            if img_object is None:
                                continue
                            if len(img_object[0, 0]) == 3:
                                img_object = cv2.cvtColor(img_object, cv2.COLOR_RGB2RGBA)
                            img_objects.append(img_object)
            else:
                continue
    if (ctx.message.attachments == [] and len(args) == 0):
        await ctx.channel.send("You must attach an image file or pass a link as the last argument to the command message!")
        return
    # processing and final sending goes here!
    for img_object in img_objects:
        current_img = img_object
        #C:\Users\MlgEp\My Drive\HOME\Python\Projects\Self\anime_cyber\Discord bot
        #C:\\Users\\MlgEp\\Google Drive\\HOME\\Python\\Projects\\Self\\anime_cyber\\Discord bot\\foreground.png
        foreground_image = cv2.imread("resources\\foreground.png", cv2.IMREAD_UNCHANGED)
        foreground_img_ratio = foreground_image.shape[1] / foreground_image.shape[0]
        if current_img.shape[1] >= current_img.shape[0]:
            foreground_image = cv2.resize(foreground_image, (int(foreground_img_ratio * current_img.shape[0]), current_img.shape[0]), interpolation=cv2.INTER_AREA)
        else:
            foreground_image = cv2.resize(foreground_image, (current_img.shape[1], int(foreground_img_ratio ** -1 * current_img.shape[1])), interpolation=cv2.INTER_AREA)
        for row in range(foreground_image.shape[0]):
            for col in range(foreground_image.shape[1]):
                try:
                    row_offset = current_img.shape[0] - foreground_image.shape[0]
                    col_offset = (current_img.shape[1] - foreground_image.shape[1]) // 2
                    if (foreground_image[row, col][3] == 255):
                        current_img[row + row_offset, col + col_offset] = foreground_image[row, col]
                    elif (foreground_image[row, col][3] == 0):
                        pass
                    else:
                        current_img[row + row_offset, col + col_offset] = bb_utils.merge_pixels(foreground_image[row, col], current_img[row + row_offset, col + col_offset])
                except IndexError:
                    pass
        await ctx.channel.send(content="", file=discord.File(fp=io.BytesIO(cv2.imencode(".png", current_img)[1].tobytes()), filename="outputImage.png"))

@BillyBot.command(aliases=["Bibi", "BiBi", "BB", "Bb", "bb"])
async def bibi(ctx):
    """Sends a picture of Israel's **EX** prime minister Benjamin Netanyahu."""
    bb_images = os.listdir("resources\\bibi\\")
    with open("resources\\bibi\\" + random.choice(bb_images), "rb") as bb_pick:
        await ctx.message.channel.send(file=discord.File(fp=bb_pick, filename="bb.png"))

@BillyBot.command(aliases=["Echo", "echo", "Say"])
async def say(ctx, *, message):
    """Repeats a given message."""
    await ctx.channel.send(message)

@BillyBot.command(aliases=["SayState", "Saystate", "EchoState", "echostate", "Echostate"])
async def saystate(ctx, state):
    """Toggles on/off the auto echo function."""
    if state == "on":
        if (ctx.author.id, ctx.guild.id) not in auto_say_members:
            auto_say_members.append((ctx.author.id, ctx.guild.id))
    elif state == "off":
        if (ctx.author.id, ctx.guild.id) in auto_say_members:
            auto_say_members.remove((ctx.author.id, ctx.guild.id))
    else:
        return
    await ctx.message.add_reaction("✅")

@saystate.error
async def saystate_error(ctx, error):
    """Handles saystate function errors"""
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        response = ""
        if (ctx.author.id, ctx.guild.id) in auto_say_members:
            response = "on"
        else:
            response = "off"
        await ctx.channel.send("Say state is {0}".format(response))

@BillyBot.command(aliases=["Roll"])
async def roll(ctx, start : int, end : int):
    """ Rolls a number in the given range where both ends are inclusive """

    if start > end:
        await ctx.channel.send("Invalid range!")
        return

    await ctx.channel.send("I rolled: {0}!".format(random.randint(start, end)))

@roll.error
async def roll_error(ctx, error):
    """Handles errors on the roll command"""
    if isinstance(error, commands.BadArgument):
        await ctx.channel.send("Invalid arguments! Follow the command format of: roll {start} {end}")

@BillyBot.command(aliases=["RemindMe", "Remindme"])
async def remindme(ctx, reminder, seconds : int):
    """Not implemented"""
    raise NotImplementedError

@BillyBot.command(aliases=["Minesweeper"])
async def minesweeper(ctx, width, height, mines):
    """ Play minesweeper, powered by BillyBot """

    # Criterias for a valid game
    try:
        width = int(width)
        height = int(height)
        mines = int(mines)

        valid_game = not(width * height > 100 or width >= 38 or width <= 3 or height <= 3 or mines <= 0 or width * height - 9 <= mines)
    except ValueError:
        valid_game = False

    if not valid_game:
        await ctx.channel.send("Invalid paramenters!")
        return

    minesweeper_game = bb_minesweeper.Minesweeper(width, height, mines)
    minesweeper_game.generate()
    minesweeper_message = str(minesweeper_game)

    if len(minesweeper_message) <= 2000:
        await ctx.channel.send(minesweeper_message)
    else:
        await ctx.channel.send("Board contents too long (more than 2000 characters)! Try making a smaller board...")

with open("token.txt", "r", encoding="UTF-8") as token_f:
    BillyBot.run(token_f.read())
