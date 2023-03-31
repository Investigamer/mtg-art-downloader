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
cardlist = os.path.join(cwd, config["FILES"]["Card.List"])
# Parent folder of all images
folder = os.path.join(cwd, config["FILES"]["Download.Folder"])
# Scryfall sub folder
scry = os.path.join(cwd, folder + "/" + config["FILES"]["Scryfall.Art.Folder"])
# MTG Pics sub folder
mtgp = os.path.join(cwd, folder + "/" + config["FILES"]["MTGPics.Art.Folder"])
# Output naming convention
naming = config["FILES"]["Naming.Convention"]


"""
APP SETTINGS
"""
# Download all images available or just most recent?
download_all = config["SETTINGS"].getboolean("Download.All")
# Download scryfall if MTGPics missing?
try:
    download_scryfall = config["SETTINGS"].getboolean("If.Missing.Download.Scryfall")
except ValueError:
    download_scryfall = True
# ONLY download scryfall?
try:
    only_scryfall = config["SETTINGS"].getboolean("Only.Download.Scryfall")
except ValueError:
    only_scryfall = False
# Overwrite previous files
try:
    overwrite = config["SETTINGS"].getboolean("Overwrite.Same.Name")
except ValueError:
    only_scryfall = True


"""
SEARCH SETTINGS
"""
# Exclude full arts?
try:
    exclude_fullart = config["SEARCH"].getboolean("Exclude.Fullart")
except ValueError:
    exclude_fullart = False
# Download unique or ALL?
try:
    if config["SEARCH"].getboolean("Only.Search.Unique.Art"):
        unique = "art"
    else:
        unique = "prints"
except ValueError:
    unique = "art"
# Include extras in search
try:
    include_extras = str(bool(config["SEARCH"].getboolean("Include.Extras")))
except ValueError:
    include_extras = "false"
