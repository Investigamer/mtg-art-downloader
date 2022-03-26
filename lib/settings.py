"""
MODULES
"""
import os
import configparser
cwd = os.getcwd()

# Import our config file
config = configparser.ConfigParser()
config.read("config.ini")

# Lists
cardlist = os.path.join(cwd, "cards.txt")
detailed = os.path.join(cwd, "detailed.txt")

# Folder names
folder = os.path.join(cwd, config['FILES']['Download.Folder']) # Parent folder of all imgs
scry = os.path.join(cwd, folder+"/"+config['FILES']['Scryfall.Art.Folder']) # Scryfall sub
mtgp = os.path.join(cwd, folder+"/"+config['FILES']['MTGPics.Art.Folder']) # MTG Pics sub

# Basic lands
basic_lands = ["Plains", "Island", "Swamp", "Mountain", "Forest"]

# Exclude full arts?
exclude_fullart = config['SETTINGS'].getboolean('Exclude.Fullart')

# Exclude secret lair
exclude_secret_lair = config['SETTINGS'].getboolean('Exclude.Secret.Lair')

# Download all images available or just most recent?
download_all = config['SETTINGS'].getboolean('Download.All')

# Download unique or ALL?
if config['SETTINGS'].getboolean('Only.Search.Unique.Art'): unique = "art"
else: unique = "prints"

# Download scryfall if mtgpics missing?
download_scryfall = config['SETTINGS'].getboolean('If.Missing.Download.Scryfall')
