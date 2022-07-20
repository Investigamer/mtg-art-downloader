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


def get_command(com):
	"""
	See if the command is listed in links.json
	:param com: String given by the user
	:return: The appropriate link, None if nothing matches
	"""
	for k, v in cfg.links.items():
		if com in v:
			return v[com]
	return None


def get_list(com):
	"""
	Webscrape to create list of cards to download from a given list.
	:param com: Command array including name, and url
	:return: Filename of the newly created list
	"""
	Path(os.path.join(cwd, "lists")).mkdir(mode=511, parents=True, exist_ok=True)
	cards = requests.get(com["url"]).json()
	with open(os.path.join(cwd, f"lists/{com['name']}.txt"), "w", encoding="utf-8") as f:
		# Clear out the txt file if used before
		f.truncate(0)

		# Get our card list
		for k in com['keys']:
			cards = cards[k]

		# Loop through cards adding them to the txt list
		for card in cards:
			f.write(f"{card['name']}\n")
	return os.path.join(cwd, f"lists/{com['name']}.txt")


def get_mtgp_code(set_code, name, alternate=False):
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
	soup_i = soup.find_all("img", attrs={"alt": re.compile(f"^({name})(.)*")})
	if isinstance(alternate, int): soup_src = soup_i[alternate]['src']
	elif alternate: soup_src = soup_i[1]['src']
	else: soup_src = soup_i[0]['src']
	return soup_src.replace("../pics/reg/","").replace("/","").replace(".jpg","")


def log(name, set_code=None, txt="failed"):
	"""
	Log card that couldn't be found.
	"""
	Path(os.path.join(cwd, "logs")).mkdir(mode=511, parents=True, exist_ok=True)
	with open(os.path.join(cwd, f"logs/{txt}.txt"), "a", encoding="utf-8") as l:
		if set_code: l.write(f"{set_code}--{name}\n")
		else: l.write(f"{name}\n")
	print(f"{Fore.RED}FAILED: {Style.RESET_ALL}{name} [{set_code.upper()}]")


def handle(error):
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