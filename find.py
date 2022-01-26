# Requirements
import requests
import settings
from downloader import download_card, download_cards
from urllib import request, error, parse
from colorama import init
from colorama import Style, Fore, Back
from contextlib import suppress
from pathlib import Path
from bs4 import BeautifulSoup
import time
import sys
import os

# System call
os.system("")

# Create folders if they don't exist
Path(settings.f_name).mkdir(mode=511, parents=True, exist_ok=True)
Path(settings.f_mtgp).mkdir(mode=511, parents=True, exist_ok=True)
Path(settings.f_scry).mkdir(mode=511, parents=True, exist_ok=True)
Path(settings.f_mtgp_b).mkdir(mode=511, parents=True, exist_ok=True)
Path(settings.f_scry_b).mkdir(mode=511, parents=True, exist_ok=True)

def txt_downloader ():
	# Open the failed to find txt
	failed = open(settings.f_name+"/failed.txt","w+")

	with open(settings.cardlist, 'r') as cards:
		for card in cards:
			# Remove line break
			card = card.replace("\n","")
			if card in settings.basic_lands:
				z = 0
				while z == 0:
					print("Basic land found! What set should I pull the art from? ex: vow, m21, eld\n")
					land_set = input()
					if len(land_set) >= 3:
						z = 1
						r = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={parse.quote(card)}&set={parse.quote(land_set)}").json()

						# Borderless card?
						if r['border_color'] == "borderless": alternate = True
						else: alternate = False

						download_card(failed, r['set'], r['collector_number'], r['name'], r['artist'], r['image_uris']['art_crop'], "", r['layout'], r['set_type'], alternate)
					else: print("Error! Illegitimate set. Try again!\n")
			else:
				if settings.download_all:
					raw = requests.get(f"https://api.scryfall.com/cards/search?q=!\"{parse.quote(card)}\" is:hires&unique="+settings.unique+"&order=released").json()
					for r in raw['data']:
						set = r['set']
						card_num = r['collector_number']
						artist = r['artist']
						layout = r['layout']
						flipname = ""
						
						# Extra stuff for flip cards
						if "card_faces" in r:
							flipname = r['card_faces'][1]['name']
							art_crop = r['card_faces'][0]['image_uris']['art_crop']
							card_name = r['card_faces'][0]['name']
						else: 
							art_crop = r['image_uris']['art_crop']
							card_name = r['name']
						
						# Borderless card?
						if r['border_color'] == "borderless" or r['collector_number'][-1] == "s": alternate = True
						else: alternate = False
						
						if settings.exclude_fullart == True:
							if r['full_art'] == True: print("\nSkipping fullart image...\n")
							else: download_card(failed, set, card_num, card_name, artist, art_crop, flipname, layout, r['set_type'], alternate)
						else: download_card(failed, set, card_num, card_name, artist, art_crop, flipname, layout, r['set_type'], alternate)
				else:
					raw = requests.get(f"https://api.scryfall.com/cards/search?q=!\"{parse.quote(card)}\" is:hires&unique="+settings.unique+"&order=released").json()
					# Remove full art entries?
					prepared = []
					if settings.exclude_fullart == True:
						for foo in raw['data']:
							if foo['full_art'] == False: prepared.append(foo)
					else: prepared = raw['data']
					if prepared: download_cards(failed,prepared)
					else: print(card + " not found!")
	# Close the txt file
	failed.close()

	print("\nAll available files downloaded.\nSee failed.txt for images that couldn't be located.\nPress enter to exit :)")
	input()
	sys.exit()

def sheet_downloader ():
	# Open the failed to find txt
	failed = open(settings.f_name+"/failed.txt","w+")

	# Open the card list
	with open(settings.detailed_list, 'r') as cards:
		for item in cards:
			
			# Split the name and set
			card = item.split("--")
			set_code = card[0]
			name = card[1]

			# Lookup the card
			r = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={parse.quote(name)}&set={parse.quote(set_code)}").json()

			# Is this a flip card?
			flipname = ""
			if "card_faces" in r:
				flipname = r['card_faces'][1]['name']
				art_crop = r['card_faces'][0]['image_uris']['art_crop']
				card_name = r['card_faces'][0]['name']
			else: 
				art_crop = r['image_uris']['art_crop']
				card_name = r['name']

			# Borderless card?
			if r['border_color'] == "borderless" or r['collector_number'][-1] == "s": alternate = True
			else: alternate = False
			
			# Download the card
			download_card(failed, r['set'], r['collector_number'], card_name, r['artist'], art_crop, flipname, r['layout'], r['set_type'], alternate)

	# Close the txt file
	failed.close()

	print("\nAll available files downloaded.\nSee failed.txt for images that couldn't be located.\nPress enter to exit :)")
	input()
	sys.exit()

print(f"{Fore.YELLOW}{Style.BRIGHT}\n  ██████╗ ███████╗████████╗    ███╗   ███╗████████╗ ██████╗ ")
print(f" ██╔════╝ ██╔════╝╚══██╔══╝    ████╗ ████║╚══██╔══╝██╔════╝ ")
print(f" ██║  ███╗█████╗     ██║       ██╔████╔██║   ██║   ██║  ███╗")
print(f" ██║   ██║██╔══╝     ██║       ██║╚██╔╝██║   ██║   ██║   ██║")
print(f" ╚██████╔╝███████╗   ██║       ██║ ╚═╝ ██║   ██║   ╚██████╔╝")
print(f"  ╚═════╝ ╚══════╝   ╚═╝       ╚═╝     ╚═╝   ╚═╝    ╚═════╝ ")
print(f"  █████╗ ██████╗ ████████╗    ███╗   ██╗ ██████╗ ██╗    ██╗ ")
print(f" ██╔══██╗██╔══██╗╚══██╔══╝    ████╗  ██║██╔═══██╗██║    ██║ ")
print(f" ███████║██████╔╝   ██║       ██╔██╗ ██║██║   ██║██║ █╗ ██║ ")
print(f" ██╔══██║██╔══██╗   ██║       ██║╚██╗██║██║   ██║██║███╗██║ ")
print(f" ██║  ██║██║  ██║   ██║       ██║ ╚████║╚██████╔╝╚███╔███╔╝ ")
print(f" ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝       ╚═╝  ╚═══╝ ╚═════╝  ╚══╝╚══╝  {Style.RESET_ALL}\n")
print(f"{Fore.CYAN}{Style.BRIGHT}MTG Art Downloader by Mr Teferi")
print(f"Additional credit to Trix are for Scoot + Gikkman")
print(f"http://mpcfill.com --- Support great MTG Proxies!{Style.RESET_ALL}\n")
z = 0
while z == 0:
	# Does the user want to use Google Sheet queeries or cards from txt file?
	print("Enter 1 to download arts from cardname list in cards.txt.\nEnter 2 to download images from \"set--name\" list in detailed.txt.\nFor help using this app, visit: tinyurl.com/mtg-art-dl")
	choice = input()
	
	# Import our Google Sheets generated queeries
	if choice == "1":
		z = 1
		print("\nCan do! Grab yourself a beer, we might be here a minute..")
		txt_downloader()
	elif choice == "2":
		z = 1
		print("\nCan do! Grab yourself a beer, we might be here a minute..")
		sheet_downloader()
	else: print("\nDo you think this is a game? Try again.\n")