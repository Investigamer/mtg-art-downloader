"""
ESTABLISH USER SETTINGS
"""
import os
import configparser
import hjson
import json

cwd = os.getcwd()
with open("config.ini", "r", encoding="utf-8") as f:
    config = configparser.ConfigParser()
    config.read_file(f)


"""
CONSTANTS
"""
with open(os.path.join(cwd, "src/codes.hjson"), "r", encoding="utf-8") as js:
    replace_sets = hjson.load(js)
with open(os.path.join(cwd, "src/links.json"), "r", encoding="utf-8") as js:
    links = json.load(js)

"""
FILES AND FOLDERS
"""

# Card list text file
cardlist = os.path.join(cwd, config.get("FILES", "Card.List", fallback="cards.txt"))

# Parent folder of all images
folder = os.path.join(
    cwd, config.get("FILES", "Download.Folder", fallback="downloaded")
)

# Scryfall sub folder
scry = os.path.join(
    cwd, folder + "/" + config.get("FILES", "Scryfall.Art.Folder", fallback="scryfall")
)

# MTG Pics sub folder
mtgp = os.path.join(
    cwd, folder + "/" + config.get("FILES", "MTGPics.Art.Folder", fallback="mtgpics")
)

# Output naming convention
naming = config.get(
    "FILES", "Naming.Convention", fallback="NAME (ARTIST) [SET] {NUMBER}"
)

"""
APP SETTINGS
"""

# Download full card image from Scryfall?
download_scryfall_full = config.getboolean(
    "SETTINGS", "Download.Scryfall.Full", fallback=False
)

# Download scryfall if MTGPics missing?
download_scryfall = config.getboolean(
    "SETTINGS", "If.Missing.Download.Scryfall", fallback=True
)

# ONLY download scryfall?
only_scryfall = config.getboolean("SETTINGS", "Only.Download.Scryfall", fallback=False)

# Overwrite previous files
overwrite = config.getboolean("SETTINGS", "Overwrite.Same.Name", fallback=True)

# Download all images available or just most recent?
download_all = config.getboolean("SETTINGS", "Download.All", fallback=False)

"""
SEARCH SETTINGS
"""

# Exclude full arts?
exclude_fullart = config.getboolean("SEARCH", "Exclude.Fullart", fallback=False)

# Download unique or ALL?
unique = (
    "art"
    if config.getboolean("SEARCH", "Only.Search.Unique.Art", fallback=True)
    else "prints"
)

# Include extras in search
include_extras = str(config.getboolean("SEARCH", "Include.Extras", fallback=True))
