# Requirements
import requests
import settings
import urllib.request
import urllib.error
import re
from colorama import init
from colorama import Style, Fore, Back
from contextlib import suppress
from pathlib import Path
from bs4 import BeautifulSoup

def download_card (txt,set_code,code,name,artist,scrylink,name2,layout,set_type,alternate):

	# Make sure numeric code is 3 digits
	if len(code) == 1: code = "00"+code
	elif len(code) == 2: code = "0"+code
	
	# Set up the filename
	filename = "/" + name + " (" + artist + ") [" + set_code.upper() + "].jpg"

	# Some sets aren't represented accurately on mtgpics, lets fix it
	set = fix_set_mtgp(set_code)

	# Get correct mtgp code
	mtgp_code = get_mtgp_code (set, name, alternate)
	if mtgp_code == "missing":
		if set_type == "promo": 
			mtgp_code = get_mtgp_code ("pmo", name, alternate)
			if mtgp_code == "missing": mtg_code = set+code
		else: mtgp_code = set+code

	# Which type of card?
	if layout == "transform" or layout == "modal_dfc" or layout == "split":

		# Try downloading from mtgp
		success = download_mtgp (name,settings.f_mtgp+filename,mtgp_code,False)

		# If failed, download scryfall art
		if success == False: download_scryfall (name,scrylink,settings.f_scry+filename,False)

		# Filename for back
		filename2 = "/" + name2 + " (" + artist + ") [" + set_code.upper() + "].jpg"

		# Try downloading back from mtgp
		if success: success = download_mtgp (name2,settings.f_mtgp_b+filename2,mtgp_code,True)

		# If failed, download scryfall art
		if success == False: download_scryfall (name2,scrylink.replace("front","back"),settings.f_scry_b+filename2,True)

	else:
		# Try downloading from mtgp
		success = download_mtgp (name,settings.f_mtgp+filename,mtgp_code,False)

		# If failed, download scryfall art
		if success == False: download_scryfall (name,scrylink,settings.f_scry+filename,False)

def download_mtgp (name,filename,mtgp_code,back):
	try:
		# Crawl the mtgpics site to find correct link for mdfc card
		r = requests.get("https://www.mtgpics.com/card?ref="+mtgp_code)
		soup = BeautifulSoup(r.content, "html.parser")
		soup_img = soup.find_all("img", {"style": "display:block;border:4px black solid;cursor:pointer;"})
		
		# Is this the back face?
		if back: 
			img_src = soup_img[1]['src']
			name = name + " (Back)"
		else: img_src = soup_img[0]['src']
		
		# Final mtgp IMG link
		img_link = img_src.replace("pics/art_th/","https://mtgpics.com/pics/art/")
		
		# Try to download from MTG Pics
		urllib.request.urlretrieve(img_link, filename)
		print(f"{Fore.GREEN}SUCCESS MTGP: {Style.RESET_ALL}" + name)
		return(True)
	except: return(False)

def download_scryfall (name,scrylink,filename,back):
	# Is downloading scryfall enabled?
	if settings.download_scryfall:
		# Is this a card back?
		if back: name = name + " (BACK)"
		print(f"{Fore.RED}MTGP is missing " + name + ", checking Scryfall...")
		try: 
			urllib.request.urlretrieve(scrylink, filename)
			print(f"{Fore.GREEN}SUCCESS SCRY: {Style.RESET_ALL}" + name)
			return(True)
		except:
			txt.write(name+" (https://www.mtgpics.com/card?ref="+mtgp_code+")\n")
			print(f"{Fore.RED}FAILED ALL: {Style.RESET_ALL}" + name)
			return(False)
	else:
		print(f"{Fore.RED}MTGP is missing " + name + f"{Style.RESET_ALL}") 
		return(False)

def get_mtgp_code (set, name, alternate):
	try:
		# Crawl the mtgpics site to find correct set code
		r = requests.get("https://www.mtgpics.com/card?ref="+set+"001")
		soup = BeautifulSoup(r.content, "html.parser")
		soup_td = soup.find("td", {"width": "170", "align": "center"})
		soup_a = soup_td.find('a')
		src_link = soup_a['href']
		mtgp_link = "https://mtgpics.com/"+src_link

		# Crawl the set page to find the correct link
		r = requests.get(mtgp_link)
		soup = BeautifulSoup(r.content, "html.parser")
		soup_i = soup.find_all("img", attrs={"alt": re.compile('^'+name+'.*')})
		if alternate: soup_src = soup_i[1]['src']
		else: soup_src = soup_i[0]['src']
		mtgp_code = soup_src.replace("../pics/reg/","")
		mtgp_code = mtgp_code.replace("/","")
		return(mtgp_code.replace(".jpg",""))
	except: return("missing")

# Beta feature, needs additional work
def download_cards (txt, json):
	
	# Used to track whether mtgp downloaded for both sides
	mtgp = False
	mtgp_b = False
	
	for card in json:
		
		# Base variables
		set_code = card['set']
		card_num = card['collector_number']
		artist = card['artist']
		set = fix_set_mtgp(set_code)
		
		# Is this double faced?
		if 'card_faces' in card:
			flipname = card['card_faces'][1]['name']
			art_crop = card['card_faces'][0]['image_uris']['art_crop']
			card_name = card['card_faces'][0]['name']
			filename = "/" + card_name + " (" + artist + ") [" + set_code.upper() + "].jpg"
			filename2 = "/" + flipname + " (" + artist + ") [" + set_code.upper() + "].jpg"
		else:
			art_crop = card['image_uris']['art_crop']
			card_name = card['name']
			filename = "/" + card_name + " (" + artist + ") [" + set_code.upper() + "].jpg"
			mtgp_b = True

		# Borderless card?
		if card['border_color'] == "borderless": alternate = True
		else: alternate = False
		
		# Get correct mtgp code
		mtgp_code = get_mtgp_code(set, card_name, alternate)
		if mtgp_code == "missing": 
			if card['set_type'] == "promo": 
				mtgp_code = get_mtgp_code("pmo", card_name, alternate)
				if mtgp_code == "missing": mtgp_code = set+card_num
			else: mtgp_code = set+card_num

		# Has MTGPic art been found yet?
		if mtgp == False: mtgp = download_mtgp (card_name,settings.f_mtgp+filename,mtgp_code,False)
		
		# Has MTGPic art been found for back?
		if mtgp_b == False: mtgp_b = download_mtgp (flipname,settings.f_mtgp_b+filename2,mtgp_code,True)
	
	card = json[0]
	
	# Base variables
	set_code = card['set']
	card_num = card['collector_number']
	artist = card['artist']
	
	# Is this mdfc?
	if 'card_faces' in card:
		flipname = card['card_faces'][1]['name']
		card_name = card['card_faces'][0]['name']
		scrylink = card['card_faces'][0]['image_uris']['art_crop']
		filename = "/" + card_name + " (" + artist + ") [" + set_code.upper() + "].jpg"
		filename2 = "/" + flipname + " (" + artist + ") [" + set_code.upper() + "].jpg"
	else:
		scrylink = card['image_uris']['art_crop']
		card_name = card['name']
		filename = "/" + card_name + " (" + artist + ") [" + set_code.upper() + "].jpg"
	
	# Did MTGP fail all?
	if mtgp == False: download_scryfall (card_name,scrylink,settings.f_scry+filename,False)
	
	# Did MTGP fail all backs?
	if mtgp_b == False: download_scryfall (flipname,scrylink.replace("front","back"),settings.f_scry_b+filename2,True)

def fix_set_mtgp (set):
	if set == "arb": return("alr")
	if set == "mp2": return("aki")
	if set == "atq": return("ant")
	if set == "apc": return("apo")
	if set == "arn": return("ara")
	if set == "e01": return("anb")
	if set == "anb": return("an2")
	if set == "bok": return("bek")
	if set == "csp": return("col")
	if set == "c13": return("13c")
	if set == "c14": return("14c")
	if set == "c15": return("15c")
	if set == "c16": return("16c")
	if set == "c17": return("17c")
	if set == "cn2": return("2cn")
	if set == "dst": return("drs")
	if set == "dpa": return("dop")
	if set == "e02": return("dop")
	if set == "fem": return("fal")
	if set == "5dn": return("fda")
	if set == "v17": return("ftr")
	if set == "gpt": return("gui")
	if set == "hml": return("hom")
	if set == "mps": return("kli")
	if set == "lgn": return("lgi")
	if set == "lrw": return("lor")
	if set == "m10": return("10m")
	if set == "m11": return("11m")
	if set == "m12": return("12m")
	if set == "m13": return("13m")
	if set == "m14": return("14m")
	if set == "m15": return("15m")
	if set == "a25": return("25m")
	if set == "mmq": return("mer")
	if set == "mm2": return("mmb")
	if set == "mm3": return("mmc")
	if set == "hop": return("pch")
	if set == "pc2": return("2pc")
	if set == "pls": return("pla")
	if set == "p02": return("psa")
	if set == "pd2": return("fir")
	if set == "pd3": return("gra")
	if set == "pcy": return("pro")
	if set == "3ed": return("rev")
	if set == "sok": return("sak")
	if set == "scg": return("sco")
	if set == "shm": return("sha")
	if set == "ala": return("soa")
	if set == "sta": return("stm")
	if set == "sth": return("str")
	if set == "tmp": return("tem")
	if set == "drk": return("dar")
	if set == "puma": return("uma")
	if set == "uma": return("ulm")
	if set == "ugl": return("ung")
	if set == "wth": return("wea")
	if set == "exp": return("zex")
	if set == "10e": return("xth")
	if set == "9ed": return("9th")
	if set == "8ed": return("8th")
	if set == "7ed": return("7th")
	if set == "6ed": return("6th")
	if set == "5ed": return("5th")
	if set == "4ed": return("4th")
	if set == "pnat": return("pmo")
	if set == "pvow": return("vow")
	if set == "pmid": return("mid")
	else: return(set)