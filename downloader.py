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

# Function to download image
def download_image (txt,set,code,name,artist,scrylink,flipname):
	
	# Make sure numeric code is 3 digits
	if len(code) == 1: code = "00"+code
	elif len(code) == 2: code = "0"+code
	
	# Some sets aren't represented accurately on mtgpics, lets fix it
	mtgp_set = fix_set_mtgp(set)
	
	baselink = "https://mtgpics.com/pics/art/"+mtgp_set+"/"
	flipscry = scrylink.replace("front","back")
	
	try:
		try:
			# Crawl the mtgpics site to find correct link for mdfc card
			r = requests.get("https://www.mtgpics.com/card?ref="+mtgp_set+code)
			soup = BeautifulSoup(r.content, "html.parser")
			thiscard = soup.find_all(id="CardScan")
			tcimage = thiscard[0].find("img")
			tcsrc = tcimage['src']
			mtgp_link = baselink+tcsrc[-7:]
		except:
			mtgp_link = "https://mtgpics.com/pics/art/"+mtgp_set+"/"+code+".jpg"
		
		# Try to download from MTG Pics
		urllib.request.urlretrieve(mtgp_link, settings.f_mtgp + "/" + name + " (" + artist + ") [" + set.upper() + "].jpg")
		print(f"{Fore.GREEN}SUCCESS MTGP: {Style.RESET_ALL}" + name)
	except:
		# Failed so download from scryfall art crop
		print(f"{Fore.RED}MTGP is missing " + name + ", checking Scryfall...")
		try: 
			urllib.request.urlretrieve(scrylink, settings.f_scry + "/" + name + " (" + artist + ") [" + set.upper() + "].jpg")
			print(f"{Fore.GREEN}SUCCESS SCRY: {Style.RESET_ALL}" + name)
		except:
			txt.write(name+'\n')
			print(f"{Fore.RED}FAILED ALL: {Style.RESET_ALL}" + name)
	
	# Do flip card images
	if flipname != "":
		print(f"{Fore.GREEN}FLIP card found: {Style.RESET_ALL}" + flipname)
		try:
			# Crawl the mtgpics site to find correct link for mdfc card
			r = requests.get("https://www.mtgpics.com/card?ref="+mtgp_set+code)
			soup = BeautifulSoup(r.content, "html.parser")
			cardback = soup.find_all(id="CardScanBack")
			cbimage = cardback[0].find("img")
			cbsrc = cbimage['src']
			mtgp_link = baselink+cbsrc[-7:]
			
			# Try to download flip from MTG Pics
			urllib.request.urlretrieve(mtgp_link, settings.f_mtgp_b + "/" + flipname + " (" + artist + ") [" + set.upper() + "].jpg")
			print(f"{Fore.GREEN}SUCCESS MTGP: {Style.RESET_ALL}" + flipname)
		except:
			# Failed so download from scryfall art crop
			print(f"{Fore.RED}MTGP is missing " + flipname + ", checking Scryfall...")
			try: 
				urllib.request.urlretrieve(flipscry, settings.f_scry_b + "/" + flipname + " (" + artist + ") [" + set.upper() + "].jpg")
				print(f"{Fore.GREEN}SUCCESS SCRY: {Style.RESET_ALL}" + flipname)
			except:
				txt.write(flipname+'\n')
				print(f"{Fore.RED}FAILED ALL: {Style.RESET_ALL}" + flipname)

# Might use this function in the future, needs work
def download_cards (txt, json):
	
	mtgp = 0
	mtgp_b = 0
	
	for card in json:
		
		# Base variables
		set = card['set']
		card_num = card['collector_number']
		artist = card['artist']
		flipname = ""
		mtgp_set = fix_set_mtgp(set)
		
		# Is this mdfc?
		if 'card_faces' in card:
			flipname = card['card_faces'][1]['name']
			art_crop = card['card_faces'][0]['image_uris']['art_crop']
			card_name = card['card_faces'][0]['name']
		else:
			art_crop = card['image_uris']['art_crop']
			card_name = card['name']
			mtgp_b = 1
		
		baselink = "https://mtgpics.com/pics/art/"+mtgp_set+"/"
		
		# Has MTGPic art been found yet?
		if mtgp != 1:
			try:
				try:
					# Crawl the mtgpics site to find correct link for mdfc card
					r = requests.get("https://www.mtgpics.com/card?ref="+mtgp_set+card_num)
					soup = BeautifulSoup(r.content, "html.parser")
					thiscard = soup.find_all(id="CardScan")
					tcimage = thiscard[0].find("img")
					tcsrc = tcimage['src']
					mtgp_link = baselink+tcsrc[-7:]
				except:
					mtgp_link = "https://mtgpics.com/pics/art/"+mtgp_set+"/"+card_num+".jpg"
				# Try to download from MTG Pics
				urllib.request.urlretrieve(mtgp_link, settings.f_mtgp + "/" + card_name + " (" + artist + ").jpg")
				print(f"{Fore.GREEN}SUCCESS MTGP: {Style.RESET_ALL}" + card_name)
				mtgp = 1
			except: mtgp = 0
		
		# Has MTGPic art been found for back?
		if mtgp_b != 1:
			try:
				# Crawl the mtgpics site to find correct link for mdfc card
				r = requests.get("https://www.mtgpics.com/card?ref="+mtgp_set+card_num)
				soup = BeautifulSoup(r.content, "html.parser")
				cardback = soup.find_all(id="CardScanBack")
				cbimage = cardback[0].find("img")
				cbsrc = cbimage['src']
				mtgp_link = baselink+cbsrc[-7:]
				
				# Try to download flip from MTG Pics
				urllib.request.urlretrieve(mtgp_link, settings.f_mtgp_b + "/" + flipname + " (" + artist + ").jpg")
				print(f"{Fore.GREEN}SUCCESS MTGP: {Style.RESET_ALL}" + flipname + " (Back)")
				mtgp_b = 1
			except: mtgp_b = 0
	
	card = json[0]
	
	# Base variables
	set = card['set']
	card_num = card['collector_number']
	artist = card['artist']
	flipname = ""
	
	# Is this mdfc?
	if 'card_faces' in card:
		flipname = card['card_faces'][1]['name']
		art_crop = card['card_faces'][0]['image_uris']['art_crop']
		card_name = card['card_faces'][0]['name']
		flipscry = json[0]['card_faces'][1]['image_uris']['art_crop']
	else:
		art_crop = card['image_uris']['art_crop']
		card_name = card['name']
		mtgp_b = 1
	
	# Did MTGP fail all?
	if mtgp == 0:
		print(f"{Fore.RED}FAILED MTGP: {Style.RESET_ALL}" + card_name + ", trying scryfall...")
		try: 
			urllib.request.urlretrieve(art_crop, settings.f_scry + "/" + card_name + " (" + artist + ").jpg")
			print(f"{Fore.GREEN}SUCCESS SCRY: {Style.RESET_ALL}" + card_name)
		except:
			txt.write(name+'\n')
			print(f"{Fore.RED}FAILED ALL: {Style.RESET_ALL}" + card_name)
	
	# Did MTGP fail all backs?
	if mtgp_b == 0:
		print(f"{Fore.RED}FAILED MTGP: {Style.RESET_ALL}" + flipname + " (Back), trying scryfall...")
		try: 
			urllib.request.urlretrieve(flipscry, settings.f_scry_b + "/" + flipname + " (" + artist + ").jpg")
			print(f"{Fore.GREEN}SUCCESS SCRY: {Style.RESET_ALL}" + flipname + " (Back)")
		except:
			txt.write(flipname+'\n')
			print(f"{Fore.RED}FAILED ALL: {Style.RESET_ALL}" + flipname + " (Back)")

def fix_set_mtgp (set):
	if set == "m10": return("10m")
	else: return(set)