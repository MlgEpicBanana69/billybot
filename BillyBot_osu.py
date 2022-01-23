try:
    import os
    import json
    import requests
    import browser_cookie3
    import re
    from winreg import HKEY_CURRENT_USER, OpenKey, QueryValueEx
except ModuleNotFoundError as err:
    print("Import error has occoured, please contact me :(")
    print(err)
    input("<Press any key to continue...>")
    raise err

class BillyBot_osu:
    api_key = None

    def __init__(self, api_key:str):
        self.OSU_URL = "https://osu.ppy.sh/home"
        self.OSU_SESSION_URL = "https://osu.ppy.sh/session"
        self.OSU_SEARCH_URL = "https://osu.ppy.sh/beatmapsets/search"
        self.OSU_BEATMAPSET_URL = "https://osu.ppy.sh/beatmapsets"

        self.api_key = api_key

    def scorepost(self, score_url):
        pass

    #region collection management
    def merge_collections(self, *collections):
        """merges n collections together"""
        if len(collections) == 1:
            return collections[0]
        collection_A = collections.pop()
        collection_B = collections.pop()
        final_collection = {}
        title_sum = list(set(collection_A + collection_B))
        title_sum.sort()
        for title in title_sum:
            final_collection[title] = []
            if title in collection_A.keys():
                final_collection[title] += collection_A[title]
            if title in collection_B.keys():
                final_collection[title] += collection_B[title]
            final_collection[title].sort()
        collections.append(final_collection)
        return self.merge_collections(collections)

    def dump_collection(self, collection):
        """Converts json collection to binary collection file contents"""
        collections_count = len(collection)-1
        encode_number = lambda n: b"".join([chr((n // 255**i) % 255).encode() for i in range(4)])
        version = collection['']
        output = version.encode()
        output += encode_number(collections_count)
        output += b"\x0b"
        for i, title in enumerate(filter(len, collection.keys())):
            output += chr(len(title)).encode()
            output += title.encode()
            output += encode_number(len(collection[title]))
            for beatmap in collection[title]:
                output += b"\x0b "
                output += beatmap.encode()
            if i < len(collection.keys())-2:
                output += b"\x0b"
        return output

    def read_collection(self, collection_db):
        """Parses a collection.db file formatted binaries to json"""
        output = {}
        version = collection_db[:4:]
        collections_count = 0
        collections_count_binary = collection_db[4:8:]
        for i, v in enumerate(collections_count_binary[::-1]):
            collections_count += 256 ** (len(collections_count_binary)-i-1) * v
        collection_db = collection_db[9::]
        index = 0
        for collection in range(collections_count):
            title = collection_db[index+1:collection_db[index]+index+1].decode()
            collection_size = 0
            collection_size_binary = collection_db[index+len(title)+1:index+len(title)+5:]
            for i, v in enumerate(collection_size_binary[::-1]):
                collection_size += 256 ** (len(collection_size_binary)-i-1) * v
            output[title] = []
            index += 1 + len(title) + 5
            for beatmap in range(collection_size):
                output[title].append(collection_db[index+1:index+33].lstrip().decode())
                index += 33+1
        output[''] = version.decode()
        return output
    #endregion

    def get_browser_cookies(self):
        browser_reg_path = r'Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice'
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

    def forge_beatmap_dirname(self, beatmap_data):
        beatmap_dirname = f"{beatmap_data['beatmapset_id']} {beatmap_data['artist']} - {beatmap_data['title']}"

        blacklisted_chars = ['<', '>', '"', '/', '\\', '|', '?', '*', '.']
        for c in blacklisted_chars:
            beatmap_dirname = beatmap_dirname.replace(c, '')

        beatmap_dirname = beatmap_dirname.replace(':', '-')
        beatmap_dirname += ".osz"

        return beatmap_dirname

    def initiate_authored_session(self):
        headers = {"referer": self.OSU_URL}
        cookies = self.get_browser_cookies()
        osu_cookies = cookies._cookies['.ppy.sh']['/']
        session = requests.Session()


        session.get(self.OSU_URL)

        hu_tao = session.post(self.OSU_SESSION_URL, headers=headers, cookies=self.get_browser_cookies())

        if hu_tao.status_code != requests.codes.ok:
            raise Exception("Failed to initiate authorized session with osu.ppy.sh!")

        return session

    def get_token(self, session):
        # access the osu! homepage
        homepage = session.get(self.OSU_URL)
        # extract the CSRF token sitting in one of the <meta> tags
        regex = re.compile(r".*?csrf-token.*?content=\"(.*?)\">", re.DOTALL)
        match = regex.match(homepage.text)
        csrf_token = match.group(1)
        return csrf_token

    def validate_osu_directoy(self, path):
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
    def seek_beatmap(self, hash):
        resp = requests.get(f"https://osu.ppy.sh/api/get_beatmaps?k={self.api_key}&h={hash}")
        collection_db = json.loads(resp.text)

        if type(collection_db) == dict:
            return None
        elif len(collection_db) == 0:
            return None

        collection_db = collection_db[0]
        collection_db["hash"] = hash
        return collection_db

    def rigorous_beatmap_name(self, details):
        beatmap_id = self.purify(details['beatmap_id'])
        artist = self.purify(details['artist'])
        title = self.purify(details['title'])
        return f"{beatmap_id} {artist} - {title}"

    def rigorous_beatmapset_name(self, details):
        beatmapset_id = self.purify(details['beatmapset_id'])
        artist = self.purify(details['artist'])
        title = self.purify(details['title'])
        return f"{beatmapset_id} {artist} - {title}"

    # Removes invalid characters that may be found in beatmap names
    def purify(self, term):
        blacklisted_chars = ['<', '>', '"', '/', '\\', '|', '?', '*', '.']
        for c in blacklisted_chars:
            term = term.replace(c, '')

        term = term.replace(':', '-')

        return term