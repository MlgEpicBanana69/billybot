import asyncio
import hashlib
import io
import os
import random

import cv2
import datetime
import discord
from discord.commands.context import ApplicationContext
import mysql.connector
import numpy as np
import requests
import validators
from bs4 import BeautifulSoup
from discord.ext import commands
from dotenv import load_dotenv

import BillyBot_games as bb_games
import BillyBot_media as bb_media
import BillyBot_utils as bb_utils
from BillyBot_osu import BillyBot_osu

# Ideas:
#   osu statistics display
#   ghost ping logging
#   server managment commands
#   the ultimate shitpost database

# needs to update pycord

# Couple of helpful links
# ------------------------
# Discord developer portal
# https://discord.com/developers/applications/757490339425550336/information
#
# BillyBot invite url
# https://discord.com/api/oauth2/authorize?client_id=757490339425550336&permissions=8&scope=applications.commands%20bot
#
# Discord API Documantation
# https://discord.com/developers/docs/intro
#
# Pycord Documantation
# https://docs.pycord.dev/en/stable/
#
# Autocode Embed Builder
# https://autocode.com/tools/discord/embed-builder/

load_dotenv()

intents = discord.Intents.all()
BillyBot = discord.Bot(intents=intents)

BOT_DISCORD_FILE_LIMIT = bb_media.Media.DISCORD_FILE_LIMITERS[0]
DISCORD_MESSAGE_SIZE_LIMITS = (2000,)
BOT_DISCORD_MESSAGE_SIZE_LIMIT = DISCORD_MESSAGE_SIZE_LIMITS[0]

# Every auto list contains a two dimensional tuple containing the member id and guild id
# (id, guild_id)
auto_say_members = []

discord_token = os.environ.get("discord_token")
osu_token = os.environ.get("osu_token")
sql_pw = os.environ.get("sql_pw")
bb_osu = BillyBot_osu(osu_token)

# Connect to the shitposting database
sql_connection = mysql.connector.connect(user="light", password=sql_pw, host="127.0.0.1", database="billybot_db")
sql_cursor = sql_connection.cursor()

#region Bot events
@BillyBot.event
async def on_ready():
    """Does the initial setup for BillyBot"""

    # Log and wait for bot to be online
    await BillyBot.change_presence(status=discord.Status.online)
    print("Logged on as {0}!".format(BillyBot.user))

@BillyBot.event
async def on_message(message):
    """Handles stuff that need to be handled on every message"""
    print("{0} on {1} -> #{2}: {3}".format(str(message.author), str(message.guild),
                                           str(message.channel), message.content))

    # auto-say
    if message.guild is not None:
        if (message.author.id, message.guild.id) in auto_say_members:
            await message.channel.send(message.content)

        if message.author != BillyBot.user:
            if message.content.startswith(BillyBot.user.mention) or message.content.endswith(BillyBot.user.mention):
                keyphrase = message.content.replace(BillyBot.user.mention, '').strip()
                keyphrase = "".join([c for c in keyphrase if c.isalpha() or c == ' '])

                cyber_response = await cyber_intimidation(message, keyphrase)
                respond_table = [cyber_response]
                for val in respond_table:
                    if val is not None:
                        await message.channel.send(val)
                        break

@BillyBot.event
async def on_command_error(ctx:ApplicationContext, error):
    await ctx.defer()
    match error:
        case isinstance(error, commands.errors.MissingPermissions):
            await ctx.respond("You do not have the required permission to run this command.")
        case _:
            await ctx.respond("Command failed to to unknown error")
            raise

@BillyBot.event
async def on_guild_join(guild):
    pass

@BillyBot.event
async def on_guild_remove(guild):
    guild_player = bb_media.Player.get_player(guild)
    if guild_player is not None:
        await guild_player.wipe_and_remove()
# endregion

#region Simple commands
@BillyBot.slash_command(name="ping")
async def ping(ctx:ApplicationContext):
    """Checks that the bot is online"""
    await ctx.respond("pong! :ping_pong:")

@BillyBot.slash_command(name="say")
async def say(ctx:ApplicationContext, message):
    """Repeats a given message."""
    await ctx.respond(message)

@BillyBot.slash_command(name="roll")
async def roll(ctx:ApplicationContext, end:int=100, start:int=1):
    """ Rolls a number in the given range where both ends are inclusive """

    if start > end:
        await ctx.respond("Invalid range!")
    else:
        await ctx.respond("I rolled: {0}!".format(random.randint(start, end)))

@BillyBot.slash_command(name="squaretext")
async def squaretext(ctx:ApplicationContext, message):
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
async def doomsday(ctx:ApplicationContext, day: int, month: int, year: int):
    """Tells you what day a given date is using the doomsday algorithm"""
    await ctx.defer()
    days_of_the_week = ["Sunday", "Monday", "Tuesday",
                        "Wednesday", "Thursday", "Friday", "Saturday"]
    centuary_anchors = [5, 3, 2, 0]
    anchor_day = centuary_anchors[(year // 100 - 18) % 4]
    doomsdays = [3, 28, 7, 4, 9, 6, 11, 8, 5, 10, 7, 12]
    leap_doomsdays = [4, 29]
    is_leap_year = (year % 4 == 0 and year % 100 != 0) or (
        year % 100 == 0 and year % 400 == 0)

    calc1 = (year % 100) // 12
    calc2 = abs((year % 100) - calc1*12)
    calc3 = calc2 // 4
    calc4 = anchor_day
    calc5 = calc1 + calc2 + calc3 + calc4
    calc6 = calc5 % 7

    if not is_leap_year:
        closest_doomsday = doomsdays[month-1]
    else:
        closest_doomsday = leap_doomsdays[month-1]

    delta_shift = abs(day - closest_doomsday) % 7
    if closest_doomsday < day:
        output = (calc6 + delta_shift) % 7
    else:
        output = (calc6 - delta_shift) % 7
    await ctx.respond(f"{day}/{month}/{year} is a {days_of_the_week[output]}")

@BillyBot.slash_command(name="dolev")
async def dolev(ctx:ApplicationContext, equation):
    if equation.count("=") == 1:
        await ctx.defer()
        await asyncio.sleep(120)
        await ctx.respond("Dolev gave up")
    else:
        await ctx.respond("This is not a valid equation.")

@BillyBot.slash_command(name="bibi")
async def bibi(ctx:ApplicationContext):
    """Sends a picture of Israel's **EX** prime minister Benjamin Netanyahu."""
    bb_images = os.listdir("resources\\static\\bibi\\")
    with open("resources\\static\\bibi\\" + random.choice(bb_images), "rb") as bb_pick:
        await ctx.respond(file=discord.File(fp=bb_pick, filename="bb.png"))

@BillyBot.slash_command(name="ofekganor")
async def ofekganor(ctx:ApplicationContext):
    """Sends a picture of Lord Ofek Ganor in his full glory"""
    await ctx.defer()
    ofek_images = os.listdir("resources\\static\\ofekganor\\")
    with open("resources\\static\\ofekganor\\" + random.choice(ofek_images), "rb") as ofek_pick:
        await ctx.respond(file=discord.File(fp=ofek_pick, filename="ofek.png"))

@BillyBot.slash_command(name="aranara")
async def aranara(ctx:ApplicationContext):
    """Sends a picture of an aranara"""
    aranara_images = os.listdir("resources\\static\\aranara\\")
    aranara_choice_name = random.choice(aranara_images)
    with open("resources\\static\\aranara\\" + aranara_choice_name, "rb") as aranara_pick:
        await ctx.respond(file=discord.File(fp=aranara_pick, filename=aranara_choice_name))

@BillyBot.slash_command(name="fetch_file")
async def fetch_file(ctx:ApplicationContext, src:str, force_audio_only:bool=False):
    await ctx.defer()
    media = bb_media.Media(src, force_audio_only=force_audio_only)
    try:
        media.fetch_file(BOT_DISCORD_FILE_LIMIT)
        if media.get_content():
            await ctx.respond(media.get_name(), file=discord.File(fp=io.BytesIO(media.get_content()), filename=f"{media.get_filename()}"))
        else:
            await ctx.respond("File size exceeds allowed size")
    except:
        await ctx.respond("Error fetching file...")

@BillyBot.slash_command(name="weekly_torah_portion")
async def weekly_torah_portion(ctx:ApplicationContext):
    resp = requests.get("https://www.פרשת-שבוע.com")
    soup = BeautifulSoup(resp.text, 'html.parser')
    href = resp.text.split("post-title entry-title")[1].split("href=")[1].split(">")[0][1:-1:]
    output = resp.text.split("post-title entry-title")[1].split(">")[2][:-3:]
    embed = discord.Embed(title=output, url=href)
    await ctx.respond(embed=embed)
#endregion

#region Chat toggles
@BillyBot.slash_command(name="saytoggle")
async def saytoggle(ctx:ApplicationContext):
    """Toggles on/off the auto echo function."""

    if (ctx.author.id, ctx.guild.id) not in auto_say_members:
        auto_say_members.append((ctx.author.id, ctx.guild.id))
        await ctx.respond("✅ Now ON")
    else:
        auto_say_members.remove((ctx.author.id, ctx.guild.id))
        await ctx.respond("❌ Now OFF")
# endregion

#region Server managment commands
@BillyBot.slash_command(name="purge")
@commands.has_permissions(manage_messages=True)
async def purge(ctx:ApplicationContext, n:int=None, before:str=None):
    """Deletes n meesages from the current text channel"""
    await ctx.defer()
    if n is not None:
        await ctx.channel.purge(limit=n, after=ctx.message)
    elif before is not None:
        try:
            before = int(before)
            await ctx.channel.purge(limit=5, before=before, after=ctx.message)
        except TypeError:
            await ctx.channel.send("Invalid input for 'before'.")
    else:
        await ctx.channel.send("Invalid input. Only one input allowed.")

    # history = await ctx.channel.history(limit=n+1).flatten()
    # for msg in history[1::]:
    #     await msg.delete()
    # await ctx.respond(f"Deleted {len(history[1::])} messages.", delete_after=5)
    await ctx.respond(f"Deleted {n} messages.", delete_after=5)
# endregion

#region Player commands
@BillyBot.slash_command(name="play")
async def play(ctx:ApplicationContext, source:str=None, shitpost_id:int=None, speed:float=1.0):
    """Plays audio from an audio source

    # Playing a 'source' goes by these rules:
    # 1) A link is requested, depending on where that link leads, fetch the audio file and play it
    # 2) A query is requested, search that query on youtube and recommand multiple best results
    """
    await ctx.defer()
    if ctx.author.voice is not None:
        await bot_join(ctx)
        guild_player = bb_media.Player.get_player(ctx.guild)
        binded_player = False
        if guild_player is None:
            binded_player = True
            guild_player = bb_media.Player(ctx.guild, BillyBot)
            await guild_player.bind_player_to_ctx(ctx)
        ultimate_source = None

        if source is not None:
            # Source is message content
            if validators.url(source):
                ultimate_source = source
            # Source is youtube query
            else:
                results = bb_media.Media.query_youtube(source)

                class YoutubeQueryView(discord.ui.View):
                    @discord.ui.select(
                        placeholder = "Choose a result",
                        min_values = 1,
                        max_values = 1,
                        options = [discord.SelectOption(label=result[1], value=str(i), default=i==0) for i, result in enumerate(results)]
                    )
                    async def select_callback(self, select, interaction:discord.interactions.Interaction): # the function called when the user is done selecting options
                        index = int(select.values[0])
                        await interaction.response.edit_message(content=f"{results[index][1]} added to queue!", embed=None, view=None, delete_after=3)
                        media = bb_media.Media(results[index][0], force_audio_only=True, speed=speed)
                        await guild_player.play(media)

                    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
                    async def cancel_callback(self, button, interaction:discord.interactions.Interaction):
                        await interaction.response.edit_message(content="Canceled", embed=None, view=None, delete_after=3)

                    @discord.ui.button(label="Play", style=discord.ButtonStyle.success)
                    async def play_callback(self, button, interaction:discord.interactions.Interaction):
                        await interaction.response.edit_message(content=f"added to queue!", embed=None, view=None, delete_after=3)
                        media = bb_media.Media(results[0][0], force_audio_only=True, speed=speed)
                        await guild_player.play(media)

                view = YoutubeQueryView()
                results_embed = discord.Embed(title="Youtube Query Results:", color=bb_media.Player.PLAYER_EMBED_COLOR)

                if binded_player:
                    await ctx.channel.send("", embed=results_embed, view=view)
                else:
                    await ctx.respond("", embed=results_embed, view=view)
                return
        elif shitpost_id is not None:
            ultimate_source = f"shitpost{shitpost_id}"
        else:
            await ctx.respond("Invalid parameters to play.")
            return

        media = bb_media.Media(ultimate_source, force_audio_only=True, speed=speed)
        await guild_player.play(media)
        await ctx.respond(f"{media.get_name()} added to queue!")
    else:
        await ctx.respond("You're not in any voice channel.")

@BillyBot.slash_command(name="stop")
async def stop(ctx:ApplicationContext):
    """Stops the music and clears the queue"""
    await bb_media.Player.get_player(ctx.guild).stop(ctx.author)
    await ctx.respond("Player stopped.")

@BillyBot.slash_command(name="pause")
async def pause(ctx:ApplicationContext):
    """Pauses the current song"""
    if ctx.guild.me.voice.channel == ctx.author.voice.channel and ctx.guild.me.voice is not None:
        await ctx.respond("Now paused.")
        await bb_media.Player.get_player(ctx.guild).pause()

@BillyBot.slash_command(name="resume")
async def resume(ctx:ApplicationContext):
    """Pauses the current song"""
    if ctx.guild.me.voice.channel == ctx.author.voice.channel and ctx.guild.me.voice is not None:
        await ctx.respond("Resumed.")
        await bb_media.Player.get_player(ctx.guild).resume()

@BillyBot.slash_command(name="skip")
async def skip(ctx:ApplicationContext):
    """Skips to the next song in queue"""
    await ctx.respond("Skipped")
    guild_player = bb_media.Player.get_player(ctx.guild)
    guild_player.next()

@BillyBot.slash_command(name="shuffle")
async def shuffle(ctx:ApplicationContext):
    """Shuffles the queue"""
    await bb_media.Player.get_player(ctx.guild).shuffle()

@BillyBot.slash_command(name="loop")
async def loop(ctx:ApplicationContext):
    """Toggles playlist loop on/off"""
    await ctx.defer()
    loop_state = bb_media.Player.get_player(ctx.guild).toggle_loop()
    loop_state = "ON" if loop_state else "OFF"
    await ctx.respond("Loop is now {0}".format(loop_state))

@BillyBot.slash_command(name="skipto")
async def skipto(ctx:ApplicationContext, position: int):
    """Skips to a position in queue"""
    await bb_media.Player.get_player(ctx.guild).goto(position)

@BillyBot.slash_command(name="queue")
async def queue(ctx:ApplicationContext):
    """Displays the current queue"""
    guild_player = bb_media.Player.get_player(ctx.guild)
    queue_string = "\n".join([f"{i+1}. " + media.get_name()
                             for i, media in enumerate(guild_player.get_queue())])
    if queue_string != "":
        await ctx.respond(queue_string)
    else:
        await ctx.respond("I am not playing anything right now!")
# endregion

#region Voice commands
@BillyBot.slash_command(name="join")
async def join(ctx:ApplicationContext):
    """Joins into your voice channel."""
    await ctx.defer()
    await bot_join(ctx, True)

async def bot_join(ctx:ApplicationContext, respond_on_join=False):
    if ctx.author.voice is None:
        await ctx.respond("You're not in any voice channel.")
        return
    elif ctx.guild.voice_client is None:
        guild_player = bb_media.Player.get_player(ctx.guild)
        if guild_player is not None:
            await guild_player.wipe_and_remove()
        await ctx.author.voice.channel.connect()
    elif ctx.guild.voice_client.channel != ctx.author.voice.channel:
        await ctx.guild.me.move_to(ctx.author.voice.channel)
    try:
        await ctx.guild.me.edit(deafen=True)
    except discord.errors.Forbidden:
        raise  # Silent permission error because the self deafen is purely cosmetic kekW
    if respond_on_join:
        await ctx.respond("Joined your VC", delete_after=5)

@BillyBot.slash_command(name="leave")
async def leave(ctx:ApplicationContext):
    """Leaves voice channel."""
    if ctx.guild is None:
        await ctx.respond("What")
    if ctx.guild.voice_client is not None:
        await ctx.guild.voice_client.disconnect()
        guild_player = bb_media.Player.get_player(ctx.guild)
        if guild_player is not None:
            await guild_player.wipe_and_remove()
        await ctx.respond("Bye bye", delete_after=5)
    else:
        await ctx.respond("I'm not in a voice channel! Use /join to make me join one.")
# endregion

#region Processing commands
@BillyBot.slash_command(name="cyber")
async def cyber(ctx:ApplicationContext, args=""):
    """Overlays the text סייבר on a given image."""

    await ctx.defer()
    message_sources = [arg for arg in args.split(' ') if validators.url(arg)]
    img_objects = []
    for i, source in enumerate(message_sources):
        image_obj = bb_media.Media(source)
        if image_obj is not None:
            if image_obj.get_route_type() == bb_media.Media.GENERIC_IMAGE:
                image_obj.fetch_file(BOT_DISCORD_FILE_LIMIT)
                nparr = np.frombuffer(image_obj.get_content(), np.uint8)
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
        foreground_image = cv2.imread(
            "resources\\static\\foreground.png", cv2.IMREAD_UNCHANGED)
        foreground_img_ratio = foreground_image.shape[1] / \
            foreground_image.shape[0]
        if current_img.shape[1] >= current_img.shape[0]:
            foreground_image = cv2.resize(foreground_image, (int(
                foreground_img_ratio * current_img.shape[0]), current_img.shape[0]), interpolation=cv2.INTER_AREA)
        else:
            foreground_image = cv2.resize(foreground_image, (current_img.shape[1], int(
                foreground_img_ratio ** -1 * current_img.shape[1])), interpolation=cv2.INTER_AREA)
        for row in range(foreground_image.shape[0]):
            for col in range(foreground_image.shape[1]):
                try:
                    row_offset = current_img.shape[0] - \
                        foreground_image.shape[0]
                    col_offset = (
                        current_img.shape[1] - foreground_image.shape[1]) // 2
                    if (foreground_image[row, col][3] == 255):
                        current_img[row + row_offset, col +
                                    col_offset] = foreground_image[row, col]
                    elif (foreground_image[row, col][3] == 0):
                        pass
                    else:
                        current_img[row + row_offset, col + col_offset] = bb_utils.merge_pixels(
                            foreground_image[row, col], current_img[row + row_offset, col + col_offset])
                except IndexError:
                    pass
        await ctx.respond(content="", file=discord.File(fp=io.BytesIO(cv2.imencode(".png", current_img)[1].tobytes()), filename="outputImage.png"))
# endregion

#region Personal management
@BillyBot.slash_command(name="remindme")
async def remindme(ctx:ApplicationContext, reminder, seconds:int=0, minutes:int=0, hours:int=0, days:int=0, weeks:int=0, years:int=0):
    """Will remind you in <t> time
       years are defined as 365 days"""
    time = 60*(60*(24*(years*365 + weeks*7 + days) + hours) + minutes) + seconds

    await ctx.respond(f"BillyBot will remind you to {reminder} in {time}s")
    await asyncio.sleep(time)
    await ctx.channel.send(f"{ctx.author.mention} You asked me to remind you to: {reminder}")
# endregion

#region gaming
@BillyBot.slash_command(name="minesweeper")
async def minesweeper(ctx:ApplicationContext, width: int, height: int, mines: int):
    """Play minesweeper, powered by BillyBot™"""

    # Criterias for a valid game
    valid_game = True
    try:
        assert width * height <= 100 and width * height > 9
        assert width >= 3 and height >= 3
        assert mines >= 0
        assert mines <= width * height - 9
        assert width <= 20
    except AssertionError as err:
        print("Failed to generate minesweeper game: " + err.args[0])
        valid_game = False

    if not valid_game:
        await ctx.respond("Invalid paramenters!")
        return

    await ctx.defer()
    minesweeper_game = bb_games.Minesweeper(width, height, mines)
    minesweeper_game.generate()
    minesweeper_message = str(minesweeper_game)

    if len(minesweeper_message) <= 2000:
        await ctx.respond(minesweeper_message)
    else:
        await ctx.respond("Board contents too long (more than 2000 characters)! Try making a smaller board...")
# endregion

#region Tag user commands
@BillyBot.user_command(name="sus")
async def sus(ctx:ApplicationContext, user):
    """amogus"""
    await ctx.respond(f"{ctx.author.mention} susses out {user.mention}")

@BillyBot.user_command(name="love")
async def love(ctx:ApplicationContext, user):
    """Tag someone you like"""
    await ctx.respond(f"{ctx.author.mention} ❤️ {user.mention} 🥰")
# endregion

#region osu commands
@BillyBot.slash_command(name="mergecollections")
async def merge_collections(ctx:ApplicationContext, collections):
    """Merges the given osu collection.db files together"""
    await ctx.defer()
    collections = [bb_media.Media(collection).fetch_file() for collection in collections.split()]
    final_collection = bb_osu.merge_collections(*[bb_osu.read_collection(collection_db) for collection_db in collections])
    file_contents = bb_osu.dump_collection(final_collection)
    await ctx.respond(f"Merged {len(collections)} collections", file=discord.File(fp=io.BytesIO(file_contents), filename="collection.db"))

@BillyBot.slash_command(name="glorydays")
@discord.option(name="language",
                type=str,
                choices=["en", "he", "sp", "jp", "ru", "ge", "du"])
async def glory_days(ctx:ApplicationContext, language:str="en"):
    copypastas = {
                    "en": "To seek the Glory Days 🌅 We’ll fight the lion’s way 🦁 Then let the rain wash 🌧 All of our pride away 😇 So if this victory 🏆 Is our last odyssey 🚗 Then let the POWER within us decide! 💪",
                    "he": "לחפש אחרי ימי התהילה 🌅 נלחם בדרך האריה 🦁 ואז נתן לגשם לשטוף 🌧️ את כל גאוותנו 😇 אז אם הניצחון הזה 🏆 הוא המסע הקשה האחרון שלנו 🚗 אז תן לכוח שבתוכנו להחליט 💪",
                    "sp": "Para buscar los Gloriosos Días 🌅 Lucharemos como los leones 🦁 Y deja que la lluvia lave 🌧️ Todo nuestro orgullo 😇 Así que si está victoria 🏆 Es nuestra última odisea 🚗 Entonces deja que el PODER dentro de nosotros decida! 💪",
                    "jp": "栄光の日々を求めるために🌅 我々は獅子の道を戦います🦁 そして雨が洗い流します🌧 我々のプライドのすべてを洗い流します 😇 もしこの勝利が我々の最後のオデッセイであるなら 🚗 それなら我々の中にあるパワーに決めさせてください! 💪",
                    "ru": "Щоб шукати днів слави🌅 Ми будемо битися на шляху лева 🦁 Потім нехай дощ змиє🌧 Всю нашу гордість😇 Тож якщо ця перемога 🏆 наша остання одіссея 🚗 Тоді нехай СИЛА всередині нас вирішить!",
                    "ge": "Um die glorreichen Tage zu suchen 🌅 Wir werden auf dem Weg des Löwen kämpfen 🦁 Dann lassen wir den Regen wegspülen 🌧 All unser Stolz ist dahin 😇 Also, wenn dieser Sieg 🏆 unsere letzte Odyssee ist 🚗 Dann lass die KRAFT in uns entscheiden!",
                    "du": "Om de gloriedagen te zoeken 🌅 We zullen vechten op de manier van de leeuw 🦁 Laat de regen dan wegspoelen 🌧 Al onze trots weg 😇 Dus als deze overwinning 🏆 onze laatste odyssee is 🚗 Laat dan de KRACHT in ons beslissen!",
                 }
    await ctx.respond(copypastas[language])
#endregion

#region shitposting
def sp_has_permission(discord_user_id:str, *, owner:bool=None, administrator:bool=None,
                      submit:bool=None, remove:bool=None, rate:bool=None, query:bool=None):
    """Helper function that checks if a given discord user given by ID has the following permissions
       :returns: (bool: has_required_permission, bool: in_database)"""

    privilege_names = ("owner", "administrator", "submit", "remove", "rate", "query")
    requested_privileges = dict(zip(privilege_names, (owner, administrator, submit, remove, rate, query)))

    sql_cursor.execute("SELECT %s FROM sp_user_privileges_view WHERE discord_user_id=%s;", (', '.join(privilege_names), discord_user_id))
    user_privileges = list(sql_cursor)
    if len(user_privileges) == 0:
        return False, False
    user_privileges = user_privileges[0][0].split(', ')

    for privilege_name in privilege_names:
        if requested_privileges[privilege_name] is not None:
            # False value on owner is None (null)
            if privilege_name == "owner" and requested_privileges[privilege_name] == False:
                requested_privileges[privilege_name] = None
            if (privilege_name not in user_privileges) == bool(requested_privileges[privilege_name]):
                return False, True
    return True, True

def sp_valid_tag(tag:str) -> bool:
    for c in tag:
        if not(c.isalpha() or c == "_" or c.isdigit()):
            return False
    return True

def sp_add_shitpost_tags(shitpost_id: int, tags:list) -> bool:
    sql_cursor.execute("SELECT tag, id FROM sp_tags_tbl;")
    tag_list = list(sql_cursor)
    assert len(tag_list) > 0
    tag_list = dict(tag_list)

    for tag in tags:
        if tag not in tag_list:
            print("flag!")
        sql_cursor.execute("INSERT INTO sp_shitposts_tags_tbl (tag_id, shitpost_id) VALUES (%s, %s);", (tag_list[tag], shitpost_id))

def sp_remove_shitpost_tag(shitpost_id: int, tags:list) -> bool:
    sql_cursor.execute("SELECT tag, id FROM sp_tags_tbl;")
    tag_list = list(sql_cursor)
    assert len(tag_list) > 0
    tag_list = dict(tag_list)

    sql_cursor.execute("SELECT tag_id FROM sp_shitposts_tags_tbl WHERE shitpost_id=%s", (shitpost_id,))
    sp_tag_list = list(sql_cursor)
    assert len(sp_tag_list) > len(tags)

    for tag in tags:
        sql_cursor.execute("DELETE FROM sp_shitposts_tags_tbl WHERE shitpost_id=%s AND tag_id=%s", (shitpost_id, tag_list[tag]))

def sp_valid_description(description:str) -> bool:
    if len(description) < 16 or len(description) > 255:
        return False
    for c in description:
        if ord(c) < 32 or ord(c) > 126:
            return False
    return True

def sp_rating_avg(shitpost_id:int) -> int:
    """Returns the average rating of a shitpost.
    If the shitpost is not rated, returns None"""
    sql_cursor.execute("SELECT AVG(rating) as avg_rating from sp_rating_tbl where shitpost_id=%s group by shitpost_id", (shitpost_id,))
    result = list(sql_cursor)
    if result:
        return round(result[0][0])
    else:
        return None

def sp_shitpost_tags(shitpost_id:int) -> list:
    sql_cursor.execute("SELECT sp_tags_tbl.tag FROM sp_shitposts_tags_tbl INNER JOIN sp_tags_tbl ON sp_tags_tbl.id = sp_shitposts_tags_tbl.tag_id WHERE shitpost_id = %s", (shitpost_id,))
    return [item for sublist in sql_cursor for item in sublist]

async def sp_pull_by_id(ctx:ApplicationContext, id:int, *, get_details:bool=False):
    """Pulls a shitpost by its ID"""
    output_msg = ""
    sql_cursor.execute("SELECT * FROM shitposts_tbl WHERE id=%s", (id,))
    shitpost = [key for subl in list(sql_cursor) for key in subl]
    if len(shitpost) == 0:
        await ctx.send_followup("Shitpost with given ID not found.", ephemeral=True, delete_after=10)
        return
    shitpost_file_hash = shitpost.pop(1)
    shitpost_file_ext = shitpost.pop(1)
    sql_cursor.execute("SELECT extension FROM sp_file_extensions_tbl WHERE id=%s", (shitpost_file_ext,))
    shitpost_file_ext = list(sql_cursor)[0][0]

    shitpost_file = open(f"resources/dynamic/shitposts/shitpost{id}.{shitpost_file_ext}", "rb")

    if get_details:
        shitpost = dict(zip(("id", "submitter", "description", "upload date"), shitpost))
        shitpost["submitter"] = await BillyBot.fetch_user(int(shitpost["submitter"]))
        shitpost["rating"] = sp_rating_avg(shitpost["id"])
        for key, value in shitpost.items():
            output_msg += f"{key}: {value}\n"
        output_msg += f"tags: {' '.join(sp_shitpost_tags(id))}\n"
        output_msg += f"hash: {shitpost_file_hash}"
        await ctx.send_followup(output_msg, ephemeral=True)
    else:
        await ctx.channel.send("", file=discord.File(fp=shitpost_file, filename=f"shitpost{id}.{shitpost_file_ext}"))

    shitpost_file.close()

@BillyBot.slash_command(name="sp_modify_user")
async def sp_modify_user(ctx:ApplicationContext, discord_user:str, privilege_name:str):
    """
    Modifies the privilege of a given discord user.
    If the user is not in the database, adds it to the database with the given privilege
    Administrator privilege is required to use this command
    Owner privilege is required to deal with administrator or owner privileges
    """
    discord_user = str(discord_user)
    target_user = bb_utils.discord_mention_to_user_id(ctx, discord_user)

    author_has_owner = sp_has_permission(str(ctx.author.id), owner=True)
    target_has_owner = sp_has_permission(target_user, owner=True)
    author_has_administrator = sp_has_permission(str(ctx.author.id), administrator=True)
    target_has_administrator = sp_has_permission(target_user, administrator=True)

    target_high_level = target_has_owner[0] or target_has_administrator[0]
    if not author_has_owner[0]:
        if not author_has_administrator[0] or target_high_level:
            await ctx.respond("Insufficient user privilege")
            return

    sql_cursor.execute("SELECT name, id FROM sp_user_privileges_tbl;")
    privilege_dict = dict(list(sql_cursor))
    if privilege_name not in privilege_dict:
        await ctx.respond("Invalid privilege name. See list of valid permissions:\n\n" + "\n".join([str(x) for x in privilege_dict.keys()]))
        return
    if target_has_administrator[1] == False:
        sql_cursor.execute("INSERT INTO sp_users_tbl (discord_user_id, privilege_id) VALUES (%s, %s);", (target_user, privilege_dict[privilege_name]))
    else:
        sql_cursor.execute("UPDATE sp_users_tbl SET privilege_id=%s WHERE discord_user_id=%s", (privilege_dict[privilege_name], target_user))
    sql_connection.commit()
    await ctx.respond("Completed action")

@BillyBot.slash_command(name="sp_rate")
async def sp_rate(ctx:ApplicationContext, shitpost_id:int, rating:int):
    submitter_id = str(ctx.author.id)
    if not sp_has_permission(submitter_id, rate=True)[0]:
        await ctx.respond("Insufficient permissions.")
        return
    if (rating < 0 or rating > 100):
        await ctx.respond("Invalid rating.")
        return
    try:
        sql_cursor.execute("INSERT INTO sp_rating_tbl (rating, submitter_id, shitpost_id) VALUES (%s, %s, %s);", (rating, submitter_id, shitpost_id))
    except mysql.connector.errors.IntegrityError as err:
        if err.errno == 1452: # Undefined foreign key
            await ctx.respond(f"Shitpost of id {shitpost_id} doesn't exist")
            return
        elif err.errno == 1062: # Duplicate entry
            sql_cursor.execute("UPDATE sp_rating_tbl SET rating=%s WHERE submitter_id=%s AND shitpost_id=%s", (rating, submitter_id, shitpost_id))
        else:
            raise
    sql_connection.commit()
    reply = f"Shitpost {shitpost_id} was given a rating of {rating} points!\nShitpost {shitpost_id} is now rated at {sp_rating_avg(shitpost_id)}"
    await ctx.respond(reply)

@BillyBot.slash_command(name="sp_list_tags")
async def sp_list_tags(ctx:ApplicationContext, contains:str="", startswith:str=""):
    """Sends a list of legal tags that contains the given string"""
    await ctx.defer(ephemeral=True)
    author_has_permission = sp_has_permission(str(ctx.author.id), query=True)
    author_has_permission = author_has_permission[0] or not author_has_permission[1]

    contains = contains.upper()
    startswith = startswith.upper()
    # Returns table with every existing tag with the amount of times they tag a shitpost
    sql_query = """SELECT tag, CAST(SUM(NOT(ISNULL(shitpost_id))) AS UNSIGNED)
                FROM (select tag, id from sp_tags_tbl)
                AS epic LEFT JOIN sp_shitposts_tags_tbl
                ON sp_shitposts_tags_tbl.tag_id = id
                GROUP BY tag
                ORDER BY tag;"""
    sql_cursor.execute(sql_query)
    # NOTE: Try using fetchall
    query = list(sql_cursor)
    tag_list = "\n".join([f"{tag} ({count})" for tag, count in dict(query).items() if (contains in tag) and (tag.startswith(startswith))])
    if len(tag_list) > 0:
        if len(tag_list) <= BOT_DISCORD_MESSAGE_SIZE_LIMIT:
            await ctx.send_followup(tag_list, ephemeral=True)
        else:
            await ctx.send_followup("", file=discord.File(fp=io.StringIO(tag_list), filename="tags.txt"), ephemeral=True)
    else:
        await ctx.send_followup("No tags were found using the given filter.", ephemeral=True)

@BillyBot.slash_command(name="sp_add_tag")
async def sp_add_tag(ctx:ApplicationContext, tag:str):
    """Adds a tag to the legal list of tags. Please use resposibly."""
    if not sp_has_permission(str(ctx.author.id), submit=True)[0]:
        await ctx.respond("Insufficient privileges")
        return

    tag = tag.upper()
    for c in tag:
        if not (c.isalpha() or c.isdigit() or c == "_"):
            await ctx.respond("Illegal character in tag.")
            return
    try:
        sql_cursor.execute("INSERT INTO sp_tags_tbl (tag) VALUES (%s);", (tag,))
        sql_connection.commit()
        await ctx.respond(f"Added tag *{tag}* to database.")
    except mysql.connector.errors.IntegrityError:
        await ctx.respond(f"Failed to add *{tag}* to database, tag already exists!")

@BillyBot.slash_command(name="sp_delete_tag")
async def sp_delete_tag(ctx:ApplicationContext, tag:str):
    await ctx.defer()
    if not sp_has_permission(str(ctx.author.id), remove=True)[0]:
        await ctx.respond("Insufficient user privilege")
        return

    tag = tag.upper()
    if not sp_valid_tag(tag):
        await ctx.respond("Invalid tag")
        return

    sql_cursor.execute("DELETE FROM sp_tags_tbl WHERE tag=%s", (tag,))
    sql_connection.commit()
    await ctx.respond(f"Deleted tag *{tag}*")

@BillyBot.slash_command(name="sp_pull")
async def sp_pull(ctx:ApplicationContext, shitpost_id:int=None, keyphrase:str=None, tags:str=None,
        minimum_rating:int=0, maximum_rating:int=100, allow_unrated:bool=True,
        choose_limit:int=1, choose_random:bool=False, get_details:bool=False):
    """
    Pulls one or more shitposts based on matching tags or description and sends it in ctx

    Parameters
    ----------
    ctx : `ApplicationContext`
        Discord context
    shitpost_id : `int`
        Filter shitposts by id. Can only match one or more shitposts.
    keyphrase : `str`
        Filter shitposts by a keyphrase. This argument is used to match shitposts
        off their description value.
    tags : `str`
        A string of tags each seperated by a space. Filters shitposts to require *all* of the tags given
    minimum_rating : `int`
        the minimum shitpost rating allowed by the filter, inclusive.
    maximum_rating : `int`
        the maximum shitpost rating allowed by the filter, inclusive.
    allow_unrated : `bool`
        allows shitposts without a rating to bypass the rating filters.
    choose_limit : `int`
        Sets the limit of how many shitposts are allowed to be pulled.
        If there are more matches than the limit allows this function
        responds with an `ephemeral` `list` of all matches found
        without sending the media files themselves. If this argument
        is set to `0`, this function will not enforce any limit
    choose_random : `bool`
        Out of all matches found, only send one shitpost at random.
    get_details : `bool`
        Option to only get the metadata of the shitpost rather than the media file itself.
        When set to `True`, this function will not send the media file of matched shitpost/s
    """

    await ctx.defer(ephemeral=True)
    sufficient_privileges = sp_has_permission(str(ctx.author.id), query=True) # Check if user can query
    if not sufficient_privileges[0] and sufficient_privileges[1]:
        await ctx.send_followup("Insufficient privileges", ephemeral=True, delete_after=10)
        return

    if shitpost_id is None:
        sql_cursor.execute("SELECT id, description FROM shitposts_tbl;")
        shitpost_descriptions = dict(list(sql_cursor))
        shitpost_descriptions_filter = filter(lambda sp:
                                        sp_rating_avg(sp) >= minimum_rating and sp_rating_avg(sp) <= maximum_rating
                                        if sp_rating_avg(sp) is not None
                                        else allow_unrated,
                                        shitpost_descriptions)

        shitpost_descriptions = {key: shitpost_descriptions[key] for key in shitpost_descriptions_filter}

        def format_description(desc):
            output = ""
            for c in desc.lower():
                if c.isdigit() or c.isalpha() or c == ' ':
                    output += c
                elif c == '_':
                    output += " "
            return output

        keyword_filter = {}
        if keyphrase is not None:
            keyphrase = keyphrase.lower()
            for sp_id, sp_desc in shitpost_descriptions.items():
                if keyphrase in sp_desc.lower():
                    keyword_filter[sp_id] = len(keyphrase)
            if len(keyword_filter) == 0:
                with open("resources/static/conjuctions.txt", "r") as conjuction_file:
                    conjuction_words = conjuction_file.read().split('\n')
                for sp_id, sp_desc in shitpost_descriptions.items():
                    for part in keyphrase.split(' '):
                        part = format_description(part)
                        if part in format_description(sp_desc) and part not in conjuction_words and part != '':
                            if sp_id not in keyword_filter:
                                keyword_filter[sp_id] = len(part)
                            else:
                                keyword_filter[sp_id] += len(part)
            if len(keyword_filter) == 0:
                await ctx.send_followup("Could not find shitpost with given tags and keyphrase", ephemeral=True, delete_after=10)
                return

        output = set()
        sql_cursor.execute("SELECT tag, sp_shitposts_tags_tbl.shitpost_id FROM sp_tags_tbl INNER JOIN sp_shitposts_tags_tbl ON id = tag_id")
        shitposts_tags = list(sql_cursor)
        if tags is not None:
            tags = tags.upper()
            tags = tags.split(' ')
            for tag in tags:
                if not sp_valid_tag(tag):
                    await ctx.send_followup("One or more tags contain illegal characters", ephemeral=True, delete_after=10)
                    return

            tagged_shitposts = {}
            max_tagged = 0
            for tup in shitposts_tags:
                sp_tag, sp_id = tup
                if sp_tag in tags:
                    if sp_id not in tagged_shitposts.keys():
                        tagged_shitposts[sp_id] = 1
                    else:
                        tagged_shitposts[sp_id] += 1
                    if tagged_shitposts[sp_id] > max_tagged:
                        max_tagged = tagged_shitposts[sp_id]

            if sum(tagged_shitposts.values()) == 0:
                await ctx.send_followup("Could not find shitpost with given tags and keyphrase", ephemeral=True, delete_after=10)
                return
            for sp_id in set(tagged_shitposts.keys()).union(set(keyword_filter.keys())):
                if tagged_shitposts[sp_id] == max_tagged:
                    output.add(sp_id)
        else:
            output = set(keyword_filter.keys())

        if tags is None and keyphrase is None:
            output = set([tup[1] for tup in shitposts_tags])

        if choose_random:
            output = random.sample(output, 1)

        if choose_limit == 0:
            choose_limit = len(output)

        if len(output) > choose_limit:
            output_message = []
            for sp_id, sp_desc in shitpost_descriptions.items():
                if sp_id in output:
                    output_message.append((sp_id, f"id {sp_id}: {sp_desc}"))
            output_message = sorted(output_message, key=lambda x: x[0])
            output_message = "\n".join([part for _, part in output_message])
            await ctx.send_followup(output_message[:2000-8] + "\n**...**", ephemeral=True)
        else:
            for shitpost in list(output)[:choose_limit:]:
                await sp_pull_by_id(ctx, shitpost, get_details=get_details)
            if not get_details:
                await ctx.send_followup("Shitpost pulled succesfully.", ephemeral=True)
    else:
        await sp_pull_by_id(ctx, shitpost_id, get_details=get_details)
        await ctx.send_followup("Shitpost pulled succesfully.", ephemeral=True)

@BillyBot.slash_command(name="sp_add_tags_to_shitpost")
async def sp_add_tag_to_shitpost(ctx:ApplicationContext, shitpost_id:int, tags:str):
    sufficient_privileges = sp_has_permission(str(ctx.author.id), submit=True)
    if not sufficient_privileges[0]:
        await ctx.respond(f"Insufficient permissions")
        return

    tags = tags.split(' ')
    sp_add_shitpost_tags(shitpost_id, tags)
    sql_connection.commit()
    await ctx.respond(f"tags: {', '.join([f'*{tag}*' for tag in tags])} were successfully added to shitpost{shitpost_id}")

@BillyBot.slash_command(name="sp_remove_tags_from_shitpost")
async def sp_remove_tag_from_shitpost(ctx:ApplicationContext, shitpost_id:int, tags:str):
    sufficient_privileges = sp_has_permission(str(ctx.author.id), remove=True)
    if not sufficient_privileges[0]:
        await ctx.respond(f"Insufficient permissions")
        return

    tags = tags.split(' ')
    sp_remove_shitpost_tag(shitpost_id, tags)
    sql_connection.commit()
    await ctx.respond(f"tags: {', '.join([f'*{tag}*' for tag in tags])} were successfully removed from shitpost{shitpost_id}")

@BillyBot.slash_command(name="sp_delete_shitpost")
async def sp_delete_shitpost(ctx:ApplicationContext, id:int):
    await ctx.defer()
    if not sp_has_permission(str(ctx.author.id), remove=True)[0]:
        await ctx.respond("Insufficient user privilege")
        return

    sql_cursor.execute("DELETE FROM shitposts_tbl WHERE id=%s", (id,))

    for filename in os.listdir("resources\\dynamic\\shitposts\\"):
        if filename.startswith(f"shitpost{id}"):
            os.remove(f"resources\\dynamic\\shitposts\\{filename}")
            break
    else:
        raise AssertionError

    sql_connection.commit()
    await ctx.respond(f"Deleted shitpost {id}")

@BillyBot.slash_command(name="shitpost")
async def shitpost(ctx:ApplicationContext, src:str, tags:str, description:str):
    """
    Uploads a shitpost into the database.
    Requires submit privilege
    """
    await ctx.defer()
    tags = tags.upper().split(' ')

    if not sp_has_permission(str(ctx.author.id), submit=True)[0]:
        await ctx.respond("Insufficient user privilege")
        return

    media = bb_media.Media(src)
    if media.get_route_type() in (bb_media.Media.GENERIC_AUDIO, bb_media.Media.GENERIC_VIDEO, bb_media.Media.GENERIC_IMAGE):
        media.fetch_file(BOT_DISCORD_FILE_LIMIT)
        if media.get_content() is None:
            await ctx.respond(f"Source too large for discord (>~{BOT_DISCORD_FILE_LIMIT//1000000}MiB)")
            return
    else:
        await ctx.respond("Shitpost src must be a media compatible type")
        return

    try:
        sql_cursor.execute("SELECT tag, id FROM sp_tags_tbl;")
        tag_list = list(sql_cursor)
        assert len(tag_list) > 0
        tag_list = dict(tag_list)
        for tag in tags:
            assert sp_valid_tag(tag)
            assert tag in tag_list
    except AssertionError:
        await ctx.respond("Invalid tags")
        return

    if not sp_valid_description(description):
        await ctx.respond("Invalid description. Length must be in (16-255) inclusive")
        return

    sql_cursor.execute("SELECT extension, id FROM sp_file_extensions_tbl;")
    legal_file_extensions = dict(list(sql_cursor))
    media_extension = media.get_file_extension()
    try:
        assert len(legal_file_extensions) > 0
        assert media_extension in legal_file_extensions
    except AssertionError:
        await ctx.respond("Illegal file extension")
        return
    sql_insert_blob_query = """INSERT INTO shitposts_tbl
                          (file_hash, file_extension_id, submitter_id, description, upload_datetime) VALUES (%s,%s,%s,%s,%s);"""
    media_contents = media.get_content()
    media_hash = hashlib.sha256(media_contents).hexdigest()
    upload_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    insert_blob_tuple = (media_hash, legal_file_extensions[media_extension], ctx.author.id, description, upload_datetime)
    try:
        sql_cursor.execute(sql_insert_blob_query, insert_blob_tuple)
        shitpost_id = sql_cursor.lastrowid

        sp_add_shitpost_tags(shitpost_id, tags)

        with open(f"resources/dynamic/shitposts/shitpost{shitpost_id}.{media_extension}", "wb") as shitpost_file:
            shitpost_file.write(media_contents)

        sql_connection.commit()
        await ctx.respond(f"Shitpost uploaded succesfuly. (id: {shitpost_id})")
    except mysql.connector.errors.IntegrityError:
        await ctx.respond("Shitpost already exists within database!")

@BillyBot.slash_command(name="sp_macro")
@discord.option(name="option", type=str,
    choices=["bober"])
async def sp_macro(ctx:ApplicationContext, option:str):
    match option:
        case "bober":
            await sp_pull(ctx, shitpost_id=83)
#endregion

#region intimidation responses
async def cyber_intimidation(message, keyphrase):
    insults = None
    with open("resources/static/billy_insults.txt", mode="r", encoding='utf-8') as f:
        insults = f.read().split('\n')
    with open("resources/static/cyber_intimidation.txt", mode="r") as f:
        cyber_msg = f.read()
    rip_bozo_gif_url = "https://tenor.com/view/rip-bozo-gif-22294771"
    output_msg = f"{message.author.mention} this you?\n\n{cyber_msg}\n{repr(message)}\n\n{rip_bozo_gif_url}"

    for insult in insults:
        if insult in keyphrase:
            try:
                await message.author.timeout(until = discord.utils.utcnow() + datetime.timedelta(seconds=20), reason="RIP BOZO")
            except discord.errors.Forbidden:
                pass # We don't have permission to ban the caller
            return output_msg
    else:
        return None
# endregion

if __name__ == "__main__":
    BillyBot.run(discord_token)
