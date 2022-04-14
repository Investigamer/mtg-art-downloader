"""
CORE FUNCTIONS
"""
import os
import re
import sys
from pathlib import Path
from colorama import Style, Fore
import requests
from bs4 import BeautifulSoup
from lib import settings as cfg
cwd = os.getcwd()

# Create folders if they don't exist
Path(cfg.folder).mkdir(mode=511, parents=True, exist_ok=True)
Path(cfg.mtgp).mkdir(mode=511, parents=True, exist_ok=True)
Path(cfg.scry).mkdir(mode=511, parents=True, exist_ok=True)
Path(os.path.join(cwd, "logs")).mkdir(mode=511, parents=True, exist_ok=True)

def get_mtgp_code (set_code, name, alternate=False):
	"""
	Webscrape to find the correct MTG Pics code for the card.
	"""
	# Crawl the mtgpics site to find correct set code
	r = requests.get("https://www.mtgpics.com/card?ref="+set_code+"001")
	soup = BeautifulSoup(r.content, "html.parser")
	soup_td = soup.find("td", {"width": "170", "align": "center"})
	mtgp_link = f"https://mtgpics.com/{soup_td.find('a')['href']}"

	# Crawl the set page to find the correct link
	r = requests.get(mtgp_link)
	soup = BeautifulSoup(r.content, "html.parser")
	soup_i = soup.find_all("img", attrs={"alt": re.compile('^'+name+'.*')})
	if alternate: soup_src = soup_i[1]['src']
	else: soup_src = soup_i[0]['src']
	return soup_src.replace("../pics/reg/","").replace("/","").replace(".jpg","")

def log (name, set_code=None, txt="failed"):
	"""
	Log card that couldn't be found.
	"""
	Path(os.path.join(cwd, "logs")).mkdir(mode=511, parents=True, exist_ok=True)
	with open(os.path.join(cwd, f"logs/{txt}.txt"), "a", encoding="utf-8") as l:
		if set_code: l.write(f"{set_code}--{name}\n")
		else: l.write(f"{name}\n")
	print(f"{Fore.RED}FAILED: {Style.RESET_ALL}" + name)

def handle (error):
	"""
	Handle error messages
	"""
	print(f"{error}\nPress enter to exit...")
	sys.exit()

def get_card_face(entries, back):
	"""
	Determine which images are back and front
	"""
	arr = []
	path = f"https://mtgpics.com/{os.path.dirname(entries[0]['src'])}"
	path = path.replace("art_th","art")

	for i in entries:
		arr.append(os.path.basename(i['src']).replace(".jpg",""))
	if len(arr) == 1:
		if back: return None
		return f"{path}/{arr[0]}.jpg"
	if len(arr) == 2:
		# Two sides exist
		try:
			# Bigger number usually the back
			if int(arr[0]) > int(arr[1]):
				if back: return f"{path}/{arr[0]}.jpg"
				return f"{path}/{arr[1]}.jpg"
			if int(arr[1]) > int(arr[0]):
				if back: return f"{path}/{arr[1]}.jpg"
				return f"{path}/{arr[0]}.jpg"
		except:
			try:
				# In some cases backs have longer string
				if len(arr[0]) > len(arr[1]):
					if back: return f"{path}/{arr[0]}.jpg"
					return f"{path}/{arr[1]}.jpg"
				if len(arr[1]) > len(arr[0]):
					if back: return f"{path}/{arr[1]}.jpg"
					return f"{path}/{arr[0]}.jpg"
			except: pass
		# All other cases just go in order
		if back: return f"{path}/{arr[1]}.jpg"
		return f"{path}/{arr[0]}.jpg"
	if len(arr) > 2:
		img_i = []
		img_s = []
		# Separate into string array and int array, sorted
		arr.sort()
		for i in arr:
			if len(i) == 3: img_i.append(i)
			elif len(i) > 3: img_s.append(i)

		# Try comparing ints
		if len(img_i) > 1:
			if back: return f"{path}/{img_i[1]}.jpg"
			return f"{path}/{img_i[0]}.jpg"
		# Try comparing strings
		if len(img_s) > 1:
			if back: return f"{path}/{img_s[1]}.jpg"
			return f"{path}/{img_s[0]}.jpg"
		# Or just go in order
		if back: return f"{path}/{img_i[0]}.jpg"
		return f"{path}/{img_s[0]}.jpg"

	# All else failed go in order
	if back: return f"{path}/{arr[1]}.jpg"
	return f"{path}/{arr[0]}.jpg"


def fix_mtgp_set (set_code):
	"""
	Replace the real set code with MTGP's weird code
	"""
	if set_code == "arb": return "alr"
	if set_code == "mp2": return "aki"
	if set_code == "atq": return "ant"
	if set_code == "apc": return "apo"
	if set_code == "arn": return "ara"
	if set_code == "e01": return "anb"
	if set_code == "anb": return "an2"
	if set_code == "bok": return "bek"
	if set_code == "csp": return "col"
	if set_code == "c13": return "13c"
	if set_code == "c14": return "14c"
	if set_code == "c15": return "15c"
	if set_code == "c16": return "16c"
	if set_code == "c17": return "17c"
	if set_code == "cn2": return "2cn"
	if set_code == "dst": return "drs"
	if set_code == "dpa": return "dop"
	if set_code == "e02": return "dop"
	if set_code == "fem": return "fal"
	if set_code == "5dn": return "fda"
	if set_code == "v17": return "ftr"
	if set_code == "gpt": return "gui"
	if set_code == "hml": return "hom"
	if set_code == "mps": return "kli"
	if set_code == "lgn": return "lgi"
	if set_code == "lrw": return "lor"
	if set_code == "m10": return "10m"
	if set_code == "m11": return "11m"
	if set_code == "m12": return "12m"
	if set_code == "m13": return "13m"
	if set_code == "m14": return "14m"
	if set_code == "m15": return "15m"
	if set_code == "a25": return "25m"
	if set_code == "mmq": return "mer"
	if set_code == "mm2": return "mmb"
	if set_code == "mm3": return "mmc"
	if set_code == "hop": return "pch"
	if set_code == "pc2": return "2pc"
	if set_code == "pls": return "pla"
	if set_code == "p02": return "psa"
	if set_code == "pd2": return "fir"
	if set_code == "pd3": return "gra"
	if set_code == "pcy": return "pro"
	if set_code == "3ed": return "rev"
	if set_code == "sok": return "sak"
	if set_code == "scg": return "sco"
	if set_code == "shm": return "sha"
	if set_code == "ala": return "soa"
	if set_code == "sta": return "stm"
	if set_code == "sth": return "str"
	if set_code == "tmp": return "tem"
	if set_code == "drk": return "dar"
	if set_code == "puma": return "uma"
	if set_code == "uma": return "ulm"
	if set_code == "ugl": return "ung"
	if set_code == "wth": return "wea"
	if set_code == "exp": return "zex"
	if set_code == "10e": return "xth"
	if set_code == "9ed": return "9th"
	if set_code == "8ed": return "8th"
	if set_code == "7ed": return "7th"
	if set_code == "6ed": return "6th"
	if set_code == "5ed": return "5th"
	if set_code == "4ed": return "4th"
	if set_code == "pnat": return "pmo"
	if set_code == "pvow": return "vow"
	if set_code == "pmid": return "mid"
	if set_code == "me3": return "3me"
	if set_code == "me2": return "2me"
	if set_code == "me1": return "1me"
	if set_code == "cma": return "can"
	if set_code == "ulg": return "url"
	if set_code == "ddo": return "evk"
	return set_code
