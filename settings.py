# Requirements
import configparser

# Import our config file
config = configparser.ConfigParser()
config.read("config.ini")

# Folder names
f_name = config['FILES']['Download.Folder'] # Parent folder of all imgs
f_scry = f_name+"/"+config['FILES']['Scryfall.Art.Folder'] # Scryfall images sub
f_mtgp = f_name+"/"+config['FILES']['MTGPics.Art.Folder'] # MTGPics images sub
f_scry_b = f_scry+"/"+config['FILES']['Scryfall.Backs.Folder'] # Scryfall BACKS sub
f_mtgp_b = f_mtgp+"/"+config['FILES']['MTGPics.Backs.Folder'] # MTGPics BACKS sub
cardlist = config['FILES']['Card.List'] # Card list txt file
detailed_list = config['FILES']['Card.Detailed.List'] # Card list including set

# Basic lands
basic_lands = ["Plains", "Island", "Swamp", "Mountain", "Forest"]

# Exclude full arts?
exclude_fullart = config['SETTINGS'].getboolean('Exclude.Fullart')

# Download all images available or just most recent?
download_all = config['SETTINGS'].getboolean('Download.All')

# Refer to this for generating detailed list
# https://docs.google.com/spreadsheets/d/1QnVoQ1gvz1N4TKnkJJ44_FHomy0gNoxZlaPSkua4Rmk/edit?usp=sharing