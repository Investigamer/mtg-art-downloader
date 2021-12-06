# Requirements
import urllib.request
import urllib.error
import requests
import settings
from colorama import Fore
from colorama import Style
from contextlib import suppress
from pathlib import Path
from bs4 import BeautifulSoup
import os

# System call
os.system("")

# Create folders if they don't exist
Path(settings.f_name).mkdir(mode=511, parents=True, exist_ok=True)
Path(settings.f_mtgp).mkdir(mode=511, parents=True, exist_ok=True)
Path(settings.f_scry).mkdir(mode=511, parents=True, exist_ok=True)
Path(settings.f_mtgp_b).mkdir(mode=511, parents=True, exist_ok=True)
Path(settings.f_scry_b).mkdir(mode=511, parents=True, exist_ok=True)

z = 0
while z == 0:
	# Does the user want to use Google Sheet queeries or cards from txt file?
	print("Enter 1 to download images from Google Sheet query.\nEnter 2 to download images from cards.txt list.")
	choice = input()
	
	# Import our Google Sheets generated queeries
	if choice == "1":
		z = 1
		print("Can do! Grab yourself a beer, we might be here a minute..")
		import sheet_generated
	elif choice == "2":
		z = "Loading decklist! Grab yourself a beer, we might be here a minute..")
		import txt_downloader
	else: print("Do you think this is a game? Try again.\n")