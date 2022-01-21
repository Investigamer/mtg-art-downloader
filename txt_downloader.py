# Import download image function
import settings
import requests
import time
from urllib import parse
from downloader import download_card, download_cards

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
					if r['set_type'] == "promo":
						set_name = "Misc. Promos"
						set = "pmo"
					download_card(failed, set, set_name, r['collector_number'], r['name'], r['artist'], r['image_uris']['art_crop'], "", r['layout'])
				else: print("Error! Illegitimate set. Try again!\n")
		else:
			if settings.download_all:
				raw = requests.get(f"https://api.scryfall.com/cards/search?q=!\"{parse.quote(card)}\" is:hires&unique=art&order=released").json()
				for r in raw['data']:
					set = r['set']
					set_name = r['set_name']
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

					if r['set_type'] == "promo":
						set_name = "Misc. Promos"
						set = "pmo"
					
					if settings.exclude_fullart == True:
						if r['full_art'] == True: print("\nSkipping fullart image...\n")
						else: download_card(failed, set, set_name, card_num, card_name, artist, art_crop, flipname, layout)
					else: download_card(failed, set, set_name, card_num, card_name, artist, art_crop, flipname, layout)
			else:
				raw = requests.get(f"https://api.scryfall.com/cards/search?q=!\"{parse.quote(card)}\" is:hires&unique=art&order=released").json()
				# Remove full art entries?
				prepared = []
				if settings.exclude_fullart == True:
					for foo in raw['data']:
						if foo['full_art'] == False: prepared.append(foo)
				if prepared:
					download_cards(failed,prepared)
				else: print(card + " not found!")
# Close the txt file
failed.close()

print("\nAll available files downloaded.\nSee failed.txt for images that couldn't be located.\n")