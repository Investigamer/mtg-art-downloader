"""
MODULES
"""
import os
import sys
from urllib import parse
from colorama import Style, Fore
import requests as req
from lib import card as dl
from lib import settings as cfg

# System call
os.system("")

def txt_downloader():
	"""
	Download basic names decklist
	"""

	# Loop through every card
	with open(cfg.cardlist, 'r', encoding="utf-8") as cards:
		for card in cards:

			# Remove line break
			card = card.replace("\n","")

			# Basic land?
			if card in cfg.basic_lands:
				while True:

					# Have user choose the set, then download
					land_set = input("Basic land found! What set should I pull the art from? ex: vow, m21, eld\n")
					if len(land_set) >= 3:
						c = req.get(f"https://api.scryfall.com/cards/named?fuzzy={parse.quote(card)}&set={parse.quote(land_set)}").json()
						dl.Basic(c).download()
						break
					print("Error! Illegitimate set. Try again!\n")

			elif cfg.download_all:

				# Retrieve scryfall data
				r = req.get(f"https://api.scryfall.com/cards/search?q=!\"{parse.quote(card)}\" is:hires&unique="+cfg.unique+"&order=released").json()

				# Loop through prints of this card
				for c in r:
					card_class = dl.get_card_class(c)
					card_class(c).download()

			else:

				# Retrieve scryfall data
				r = req.get(f"https://api.scryfall.com/cards/search?q=!\"{parse.quote(card)}\" is:hires&unique="+cfg.unique+"&order=released").json()

				# Remove full art entries?
				prepared = []
				if cfg.exclude_fullart:
					for t in r['data']:
						if t['full_art'] is False: prepared.append(t)
				else: prepared = r['data']

				# Loop through prints of this card
				for c in prepared:
					card_class = dl.get_card_class(c)
					card_class(c).download()

def sheet_downloader():
	"""
	Download given detailed.txt list
	"""

	# Open the card list
	with open(cfg.detailed, 'r', encoding="utf-8") as cards:
		for item in cards:

			# Split the name and set
			card = item.split("--")
			set_code = card[0]
			name = card[1]

			# Lookup card
			c = req.get(f"https://api.scryfall.com/cards/named?fuzzy={parse.quote(name)}&set={parse.quote(set_code)}").json()
			card_class = dl.get_card_class(c)
			card_class(c).download()

print(f"{Fore.YELLOW}{Style.BRIGHT}\n")
print("  ██████╗ ███████╗████████╗    ███╗   ███╗████████╗ ██████╗ ")
print(" ██╔════╝ ██╔════╝╚══██╔══╝    ████╗ ████║╚══██╔══╝██╔════╝ ")
print(" ██║  ███╗█████╗     ██║       ██╔████╔██║   ██║   ██║  ███╗")
print(" ██║   ██║██╔══╝     ██║       ██║╚██╔╝██║   ██║   ██║   ██║")
print(" ╚██████╔╝███████╗   ██║       ██║ ╚═╝ ██║   ██║   ╚██████╔╝")
print("  ╚═════╝ ╚══════╝   ╚═╝       ╚═╝     ╚═╝   ╚═╝    ╚═════╝ ")
print("  █████╗ ██████╗ ████████╗    ███╗   ██╗ ██████╗ ██╗    ██╗ ")
print(" ██╔══██╗██╔══██╗╚══██╔══╝    ████╗  ██║██╔═══██╗██║    ██║ ")
print(" ███████║██████╔╝   ██║       ██╔██╗ ██║██║   ██║██║ █╗ ██║ ")
print(" ██╔══██║██╔══██╗   ██║       ██║╚██╗██║██║   ██║██║███╗██║ ")
print(" ██║  ██║██║  ██║   ██║       ██║ ╚████║╚██████╔╝╚███╔███╔╝ ")
print(" ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝       ╚═╝  ╚═══╝ ╚═════╝  ╚══╝╚══╝  ")
print(f"{Fore.CYAN}{Style.BRIGHT}MTG Art Downloader by Mr Teferi")
print("Additional thanks to Trix are for Scoot + Gikkman")
print(f"http://mpcfill.com --- Support great MTG Proxies!{Style.RESET_ALL}\n")


# Does the user want to use Google Sheet queeries or cards from txt file?
choice = input("Enter 1 to download arts from cardname list in cards.txt.\nEnter 2 to download images from \"set--name\" list in detailed.txt.\nFor help using this app, visit: tinyurl.com/mtg-art-dl\n")

while True:
	# Import our Google Sheets generated queeries
	if choice == "1":
		print("\nCan do! Grab yourself a beer, we might be here a minute..")
		txt_downloader()
		break
	if choice == "2":
		print("\nCan do! Grab yourself a beer, we might be here a minute..")
		sheet_downloader()
		break
	choice = input("\nDo you think this is a game? Try again.\n")

print("\nAll available files downloaded.\nSee failed.txt for images that couldn't be located.\nPress enter to exit :)")
input()
sys.exit()
