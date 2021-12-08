# Import download image function
import settings
import requests
import time
from urllib import parse
from downloader import download_image, download_cards

# Open the failed to find txt
failed = open(settings.f_name+"/failed.txt","w+")

with open(settings.cardlist, 'r') as cards:
	for card in cards:
		if card in settings.basic_lands:
			z = 0
			while z == 0:
				print("Basic land found! What set should I pull the art from? ex: vow, m21, eld\n")
				land_set = input()
				if len(land_set) >= 3:
					z = 1
					r = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={parse.quote(card)}&set={parse.quote(land_set)}").json()
					set = r['set']
					card_num = r['collector_number']
					artist = r['artist']
					flipname = ""
					download_image(failed, set, card_num, card_name, artist, art_crop, flipname)
				else: print("Error! Illegitimate set. Try again!\n")
		else:
			if settings.download_all:
				raw = requests.get(f"https://api.scryfall.com/cards/search?q=!{parse.quote(card)} is:hires&unique=art&order=released").json()
				for r in raw['data']:
					set = r['set']
					card_num = r['collector_number']
					artist = r['artist']
					flipname = ""
					
					# Extra stuff for flip cards
					if "card_faces" in r:
						flipname = r['card_faces'][1]['name']
						art_crop = r['card_faces'][0]['image_uris']['art_crop']
						card_name = r['card_faces'][0]['name']
					else: 
						art_crop = r['image_uris']['art_crop']
						card_name = r['name']
					
					if settings.exclude_fullart == True:
						if r['full_art']: print("\nSkipping fullart image...\n")
						else: download_image(failed, set, card_num, card_name, artist, art_crop, flipname)
					else: download_image(failed, set, card_num, card_name, artist, art_crop, flipname)
			else:
				raw = requests.get(f"https://api.scryfall.com/cards/search?q={parse.quote(card)} is:hires&unique=art&order=released").json()
				download_cards(failed,raw['data'])
# Close the txt file
failed.close()

print("\nAll available files downloaded.\nSee failed.txt for images that couldn't be located.\n")