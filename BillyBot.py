"""BillyBot is a general purpose discord bot that barely works"""

import io
import os
import random
from urllib.parse import urlparse

import aiohttp
import discord
from discord.ext import commands
from discord.utils import get

import cv2
import numpy as np
import validators

import BillyBot_utils as bb_utils
import BillyBot_games as bb_games
import BillyBot_media as bb_media

# Ideas:
#   osu statistics display
#   ghost ping logging
#   server managment commands
#   the ultimate shitpost database
#   Trade with TamaCrypto (Based!!)

# https://discord.com/api/oauth2/authorize?client_id=757490339425550336&permissions=8&scope=applications.commands%20bot

intents = discord.Intents.default()
intents.members = True
BillyBot = discord.Bot(intents=intents)

# Every auto list contains a two dimension tuple containing the member id and guild id
# (id, guild_id)
auto_say_members = []

#region Bot events
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
            await message.channel.send(message)

@BillyBot.event
async def on_guild_join(guild):
    bb_media.Player(guild, BillyBot)
#endregion

#region Simple commands
@BillyBot.slash_command(name="say")
async def say(ctx, message):
    """Repeats a given message."""
    await ctx.respond(message)

@BillyBot.slash_command(name="roll")
async def roll(ctx, start : int, end=100):
    """ Rolls a number in the given range where both ends are inclusive """

    if start > end:
        await ctx.respond("Invalid range!")
        return

    await ctx.respond("I rolled: {0}!".format(random.randint(start, end)))

@roll.error
async def roll_error(ctx, error):
    """Handles errors on the roll command"""
    if isinstance(error, commands.BadArgument):
        await ctx.respond("Invalid arguments! Follow the command format of: roll {start} {end}")

@BillyBot.slash_command(name="squaretext")
async def squaretext(ctx, message):
    """why (Squares text)"""

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
        await ctx.respond(final_message)
    else:
        await ctx.respond(content="", file=discord.File(fp=io.StringIO(final_message), filename="squared_text.txt"))

@BillyBot.slash_command(name="doomsday")
async def doomsday(ctx, day:int, month:int, year:int):
    """Tells you what day a given date is using the doomsday algorithm"""
    days_of_the_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    centuary_anchors = [5, 3, 2, 0]
    anchor_day = centuary_anchors[(year // 100 - 18) % 4]

    calc1 = (year - year // 100 * 100) // 12
    calc2 = abs((calc1 * 12) - (year - year // 100 * 100))
    calc3 = 6 // 4
    calc4 = anchor_day
    calc5 = calc1 + calc2 + calc3 + calc4
    calc6 = calc5 % 7
    await ctx.respond(f"{day}/{month}/{year} is a {days_of_the_week[calc6]}")
#endregion

#region Chat toggles
@BillyBot.slash_command(name="saytoggle")
async def saytoggle(ctx):
    """Toggles on/off the auto echo function."""

    if (ctx.author.id, ctx.guild.id) not in auto_say_members:
        auto_say_members.append((ctx.author.id, ctx.guild.id))
        await ctx.respond("✅ Now ON")
    else:
        auto_say_members.remove((ctx.author.id, ctx.guild.id))
        await ctx.respond("✅ Now OFF")
#endregion

#region Player commands
@BillyBot.slash_command(name="play")
async def play(ctx, source):
    """Plays audio from an audio source

    # Playing a 'source' goes by a these rules:
    # 1) An audio file is embeded, play that audio file
    # 2) A link is requested, depending on where that link leads, fetch the audio file and play it
    # 3) A query is requested, search that query on youtube and recommand multiple best results

    # also when multiple sources are given, BillyBot takes only the first one
    # further attachments are *completely* ignored."""

    if ctx.author.voice is not None:
        await join(ctx)
        guild_player = bb_media.Player.get_player(ctx.guild)

        # Source is attachment
        #if len(ctx.message.attachments) > 0:
        #    attachment = ctx.message.attachments[0]
        #    media = bb_media.Streamable(attachment.url)
        #    await guild_player.play(media)#

        await ctx.defer()
        # Source is message content
        if validators.url(source):
            media = bb_media.Streamable(source)
            await guild_player.play(media)
            await ctx.respond(media.get_name())

        # Source is youtube query
        else:
            results = bb_media.Media.query_youtube(source)
            await ctx.channel.send("\n".join([entry[1] for entry in results]))

            # TODO: Reactive video choosing
            chosen_result = results[0]

            media = bb_media.Streamable(chosen_result[0])
            await guild_player.play(media)
            await ctx.respond(f"{chosen_result[1]} added to queue!")
    else:
        ctx.respond("You're not in any voice channel.")

@BillyBot.slash_command(name="stop")
async def stop(ctx):
    """Stops the music and clears the queue"""
    await bb_media.Player.get_player(ctx.guild).stop()

@BillyBot.slash_command(name="pause")
async def pause(ctx):
    """Pauses the current song"""
    if ctx.guild.me.voice.channel == ctx.author.voice.channel and ctx.guild.me.voice is not None:
        await ctx.respond("Now paused.")
        await bb_media.Player.get_player(ctx.guild).pause()

@BillyBot.slash_command(name="resume")
async def resume(ctx):
    """Pauses the current song"""
    if ctx.guild.me.voice.channel == ctx.author.voice.channel and ctx.guild.me.voice is not None:
        await ctx.respond("Resumed.")
        await bb_media.Player.get_player(ctx.guild).resume()

@BillyBot.slash_command(name="skip")
async def skip(ctx):
    """Skips to the next song in queue"""
    bb_media.Player.get_player(ctx.guild).next()

@BillyBot.slash_command(name="shuffle")
async def shuffle(ctx):
    """Shuffles the queue"""
    await bb_media.Player.get_player(ctx.guild).shuffle()

@BillyBot.slash_command(name="loop")
async def loop(ctx):
    """Toggles playlist loop on/off"""
    loop_state = bb_media.Player.get_player(ctx.guild).toggle_loop()
    loop_state = "ON" if loop_state else "OFF"
    await ctx.respond("Loop is now {0}".format(loop_state))

@BillyBot.slash_command(name="skipto")
async def skipto(ctx, position:int):
    """Skips to a position in queue"""
    await bb_media.Player.get_player(ctx.guild).goto(position)

@BillyBot.slash_command(name="queue")
async def queue(ctx):
    """Displays the current queue"""
    guild_player = bb_media.Player.get_player(ctx.guild)
    queue_string = "\n".join([f"{i+1}. " + media.get_name() for i, media in enumerate(guild_player.get_queue())])
    if queue_string != "":
        await ctx.respond(queue_string)
    else:
        await ctx.respond("I am not playing anything right now!")
#endregion

#region Voice commands
@BillyBot.slash_command(name="join")
async def join(ctx):
    """Joins into your voice channel."""
    if ctx.author.voice is None:
        await ctx.respond("You're not in any voice channel.")
        return
    elif ctx.guild.voice_client is None:
        await ctx.author.voice.channel.connect()
    elif ctx.guild.voice_client.channel != ctx.author.voice.channel:
        await ctx.guild.me.move_to(ctx.author.voice.channel)
    try:
        await ctx.guild.me.edit(deafen=True)
    except discord.errors.Forbidden:
        raise # Silent permission error because the self deafen is purely cosmetic kekW

@BillyBot.slash_command(name="leave")
async def leave(ctx):
    """Leaves voice channel."""
    if ctx.guild is None:
        await ctx.respond("What")
    if ctx.guild.voice_client is not None:
        await ctx.guild.voice_client.disconnect()
        await bb_media.Player.get_player(ctx.guild).wipe()
    else:
        await ctx.respond("I'm not in a voice channel! Use /join to make me join one.")
#endregion

#region Processing commands
@BillyBot.slash_command(name="cyber")
async def cyber(ctx, args=""):
    """Overlays the text סייבר on a given image."""

    await ctx.defer()
    message_sources = _all_ctx_sources(ctx, args)
    img_objects = []
    for i, source in enumerate(message_sources):
        image_obj = bb_media.Static(source)
        if image_obj is not None:
            if image_obj.get_route_type() == "generic_image":
                nparr = np.frombuffer(image_obj(), np.uint8)
                cv2_img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
                if len(cv2_img[0][0]) < 4:
                    cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_RGB2RGBA)
                img_objects.append(cv2_img)
            else:
                # Discard unsupported static media formats
                message_sources.pop(i)
    if (len(message_sources) == 0):
        await ctx.respond("You must attach an image file or pass a link as the last argument to the command message!")
        return

    # processing and final sending goes here!
    for current_img in img_objects:
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
        await ctx.respond(content="", file=discord.File(fp=io.BytesIO(cv2.imencode(".png", current_img)[1].tobytes()), filename="outputImage.png"))

@BillyBot.slash_command(name="bibi")
async def bibi(ctx):
    """Sends a picture of Israel's **EX** prime minister Benjamin Netanyahu."""
    bb_images = os.listdir("resources\\bibi\\")
    with open("resources\\bibi\\" + random.choice(bb_images), "rb") as bb_pick:
        await ctx.respond(file=discord.File(fp=bb_pick, filename="bb.png"))
#endregion

#region Personal management
@BillyBot.slash_command(name="remindme")
async def remindme(ctx, reminder:str, seconds:int):
    """Not implemented"""
    raise NotImplementedError
#endregion

#region gaming
@BillyBot.slash_command(name="minesweeper")
async def minesweeper(ctx, width:int, height:int, mines:int):
    """Play minesweeper, powered by BillyBot™"""

    # Criterias for a valid game
    try:
        width = int(width)
        height = int(height)
        mines = int(mines)

        valid_game = not(width * height > 100 or width >= 38 or width <= 3 or height <= 3 or mines <= 0 or width * height - 9 <= mines)
    except ValueError:
        valid_game = False

    if not valid_game:
        await ctx.respond("Invalid paramenters!")
        return

    minesweeper_game = bb_games.Minesweeper(width, height, mines)
    minesweeper_game.generate()
    minesweeper_message = str(minesweeper_game)

    if len(minesweeper_message) <= 2000:
        await ctx.respond(minesweeper_message)
    else:
        await ctx.respond("Board contents too long (more than 2000 characters)! Try making a smaller board...")
#endregion

#region Tag user commands
@BillyBot.user_command(name="sus")
async def sus(ctx, user):
    """amogus"""
    await ctx.respond(f"{ctx.author.mention} susses out {user.mention}")

@BillyBot.user_command(name="love")
async def love(ctx, user):
    """Tag someone you like"""
    await ctx.respond(f"{ctx.author.mention} ❤️ {user.mention} 🥰")
#endregion

#region Helper functions
def _all_ctx_sources(ctx, args):
    "Returns a of all file sources from given ctx + args"
    output = []
    #if ctx.message.attachments != []:
    #    for attachment in ctx.message.attachments:
    #         output.append(attachment.url)
    for arg in args.split():
        if validators.url(arg):
            output.append(arg)
    return output
#endregion

with open("token.txt", "r", encoding="UTF-8") as token_f:
    BillyBot.run(token_f.read())
