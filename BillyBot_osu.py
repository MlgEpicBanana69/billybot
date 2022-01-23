import os
import json
import requests
import browser_cookie3
import re
from winreg import HKEY_CURRENT_USER, OpenKey, QueryValueEx

SELF_PATH = os.path.dirname(os.path.realpath(__file__))
COMMON_OSU_PATHS = ["C:\\Program Files\\osu!", "D:\\Program Files\\osu!", "O:\\Program Files\\osu!"]
api_key = None

OSU_URL = "https://osu.ppy.sh/home"
OSU_SESSION_URL = "https://osu.ppy.sh/session"
OSU_SEARCH_URL = "https://osu.ppy.sh/beatmapsets/search"
OSU_BEATMAPSET_URL = "https://osu.ppy.sh/beatmapsets"

browser_reg_path = r'Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice'

def get_browser_cookies():
    with OpenKey(HKEY_CURRENT_USER, browser_reg_path) as key:
        browser_key = QueryValueEx(key, "ProgId")[0]

    # Chrome
    if browser_key == "ChromeHTML":
        return browser_cookie3.chrome()
    # Firefox
    elif browser_key == "FirefoxURL-308046B0AF4A39CB":
        return browser_cookie3.firefox()
    # Edge (who uses edge?)
    elif browser_key == "MSEdgeHTM":
        return browser_cookie3.edge()
    else:
        print("Your default browser isn't recognized so you will have to input your")
        print("account credentials in order to download beatmaps (the osu! site requires this).")
        raise NotImplementedError

# returns api key put in a file at this scripts same directory.
# File should be named api.txt and should contain nothing but the api key
def get_api_key():
    global api_key

    with open("api.txt", "r", encoding="utf-8") as api_file:
        api_key = api_file.read()

    return api_key

def forge_beatmap_dirname(beatmap_data):
    beatmap_dirname = f"{beatmap_data['beatmapset_id']} {beatmap_data['artist']} - {beatmap_data['title']}"

    blacklisted_chars = ['<', '>', '"', '/', '\\', '|', '?', '*', '.']
    for c in blacklisted_chars:
        beatmap_dirname = beatmap_dirname.replace(c, '')

    beatmap_dirname = beatmap_dirname.replace(':', '-')
    beatmap_dirname += ".osz"

    return beatmap_dirname

def initiate_authored_session():
    headers = {"referer": OSU_URL}
    cookies = get_browser_cookies()
    osu_cookies = cookies._cookies['.ppy.sh']['/']
    session = requests.Session()


    session.get(OSU_URL)

    hu_tao = session.post(OSU_SESSION_URL, headers=headers, cookies=get_browser_cookies())

    if hu_tao.status_code != requests.codes.ok:
        raise Exception("Failed to initiate authorized session with osu.ppy.sh!")

    return session

 #   return response.content
def get_token(session):
       # access the osu! homepage
       homepage = session.get(OSU_URL)
       # extract the CSRF token sitting in one of the <meta> tags
       regex = re.compile(r".*?csrf-token.*?content=\"(.*?)\">", re.DOTALL)
       match = regex.match(homepage.text)
       csrf_token = match.group(1)
       return csrf_token

def validate_osu_directoy(path):
    required_files = ["collection.db", "osu!.exe", "osu!.cfg", "osu!.db"]
    required_directories = ["Songs"]

    flag = True
    for file in required_files:
        flag = os.path.isfile(path + "\\" + file)
    for dir in required_directories:
        flag = os.path.isdir(path + "\\" + dir)

    return flag

# Gets: beatmap hashcode
# Returns: Beatmap data
def seek_beatmap(hash):
    resp = requests.get(f"https://osu.ppy.sh/api/get_beatmaps?k={api_key}&h={hash}")
    contents = json.loads(resp.text)

    if type(contents) == dict:
        return None
    elif len(contents) == 0:
        return None

    contents = contents[0]
    contents["hash"] = hash
    return contents

def rigorous_beatmap_name(details):
    beatmap_id = purify(details['beatmap_id'])
    artist = purify(details['artist'])
    title = purify(details['title'])
    return f"{beatmap_id} {artist} - {title}"

def rigorous_beatmapset_name(details):
    beatmapset_id = purify(details['beatmapset_id'])
    artist = purify(details['artist'])
    title = purify(details['title'])
    return f"{beatmapset_id} {artist} - {title}"

# Removes invalid characters that may be found in beatmap names
def purify(term):
    blacklisted_chars = ['<', '>', '"', '/', '\\', '|', '?', '*', '.']
    for c in blacklisted_chars:
        term = term.replace(c, '')

    term = term.replace(':', '-')

    return term


def read_collection_file(db_file):
    """Reads the osu collection.db file and returns a neatly formated datatype
       Takes either a path to a collection.db file or its binary contents (bytes)"""

    output = {}

    if os.path.isfile(db_file):
        with open(db_file, "rb") as collection:
            contents = collection.read().decode('unicode_escape')
    else:
        contents = db_file

    # Header of collection file (contains file version and
    # number of collections that can be found but I simply do not care)
    contents = contents[10::]
    for i in range(len(contents)-1):
        if contents[i] == "\x0B" and (ord(contents[i+1]) < 32 and contents[i+1] != "\x00"):
            contents = contents.replace(contents[i] + contents[i+1], "\x0B\x03")
    raw_collections = contents.split("\x0B\x03")
    for coll in raw_collections:
        curr_coll_split = coll.split("\x00\x00\x00\x0b ")
        if len(curr_coll_split) > 1:
            title, contents = curr_coll_split

            title = title[:-1:]
            contents = contents.replace("\x0B", "").split()
            output[title] = contents
        else:
            del coll

    return output




if __name__ == '__main__':
    input("This is a module that contains cool helpful ultility functions for using and minipulating the osu api to do various cool tasks!")
