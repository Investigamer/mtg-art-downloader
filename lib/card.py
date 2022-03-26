"""
CARD CLASSES
"""
# pylint: disable=E0401, R0902, E1101
import os
from pathlib import Path
from urllib import request
from bs4 import BeautifulSoup
from colorama import Style, Fore
import requests
from lib import settings as cfg
from lib import core
cwd = os.getcwd()

# SINGLE IMAGE CARDS
class Card ():
	"""
	Base class to extend all cards to.
	"""

	def __init__ (self, c):

		# Inherited card info
		self.set = c['set']
		self.artist = c['artist']
		self.num = c['collector_number']
		self.mtgp_set = core.fix_mtgp_set(self.set)

		# Name if not defined
		try: self.name
		except: self.name = c['name']

		# Make sure card num is 3 digits
		if len(self.num) == 1: self.num = f"00{self.num}"
		elif len(self.num) == 2: self.num = f"0{self.num}"

		# Alternate version or promo card
		self.alt = bool(c['border_color'] == "borderless" or self.num[-1] == "s")
		self.promo = bool(c['set_type'] == "promo")

		# Get the correct mtgp URL code
		try:
			if self.alt: self.code = core.get_mtgp_code(self.mtgp_set, self.name, True)
			else: self.code = core.get_mtgp_code(self.mtgp_set, self.name)
		except:
			if self.promo:
				try:
					if self.alt: self.code = core.get_mtgp_code("pmo", self.name, True)
					else: self.code = core.get_mtgp_code("pmo", self.name)
				except: self.code = self.set+self.num
			else: self.code = self.set+self.num

	def download (self, log_failed=True):
		"""
		Download just one version of this card.
		"""
		try: self.download_mtgp (self.name, self.mtgp_path, self.code)
		except:
			if cfg.download_scryfall: self.download_scryfall (self.name, self.scry_path, self.scrylink)
			elif log_failed: core.log(self.name, self.set)
			return False
		return True

	def download_mtgp (self, name, path, mtgp_code, back=False):
		"""
		Download from MTG Pics
		"""
		# Crawl the mtgpics site to find correct link for mdfc card
		r = requests.get("https://www.mtgpics.com/card?ref="+mtgp_code)
		soup = BeautifulSoup(r.content, "html.parser")
		soup_img = soup.find_all("img", {"style": "display:block;border:4px black solid;cursor:pointer;"})

		# Is this the back face?
		img_link = core.get_card_face(soup_img, back)

		# Try to download from MTG Pics
		request.urlretrieve(img_link, path)
		print(f"{Fore.GREEN}SUCCESS: {Style.RESET_ALL}" + name)

	def download_scryfall (self, name, path, scrylink):
		"""
		Download scryfall art crop
		"""
		print(f"{Fore.YELLOW}MTGP FAILED: {name} downloaded Scryfall")
		request.urlretrieve(scrylink, path)

	def make_folders(self, name):
		"""
		Check that the folders exist
		"""
		Path(os.path.join(cfg.mtgp, name)).mkdir(mode=511, parents=True, exist_ok=True)
		Path(os.path.join(cfg.scry, name)).mkdir(mode=511, parents=True, exist_ok=True)

class Normal (Card):
	"""
	Normal frame card
	"""
	def __init__ (self, c):
		super().__init__(c)
		self.scrylink = c['image_uris']['art_crop']

		# Saved filepath
		self.mtgp_path = os.path.join(cwd,
			f"{cfg.mtgp}/{self.name} ({self.artist}) [{self.set.upper()}].jpg")
		self.scry_path = os.path.join(cwd,
			f"{cfg.scry}/{self.name} ({self.artist}) [{self.set.upper()}].jpg")

class Land (Normal):
	"""
	Basic land card
	"""
	def __init__ (self, c):
		super().__init__(c)

		# Saved filepath
		self.mtgp_path = os.path.join(cwd,
			f"{cfg.mtgp}/Land/{self.name} ({self.artist}) [{self.set.upper()}].jpg")
		self.scry_path = os.path.join(cwd,
			f"{cfg.scry}/Land/{self.name} ({self.artist}) [{self.set.upper()}].jpg")

		# Ensure save folder exists
		super().make_folders("Land")

class Saga (Normal):
	"""
	Saga card
	"""
	def __init__ (self, c):
		super().__init__(c)

		# Saved filepath
		self.mtgp_path = os.path.join(cwd,
			f"{cfg.mtgp}/Saga/{self.name} ({self.artist}) [{self.set.upper()}].jpg")
		self.scry_path = os.path.join(cwd,
			f"{cfg.scry}/Saga/{self.name} ({self.artist}) [{self.set.upper()}].jpg")

		# Ensure save folder exists
		super().make_folders("Saga")

class Adventure (Normal):
	"""
	Adventure card
	"""
	def __init__ (self, c):
		super().__init__(c)

		# Saved filepath
		self.mtgp_path = os.path.join(cwd,
			f"{cfg.mtgp}/Adventure/{self.name} ({self.artist}) [{self.set.upper()}].jpg")
		self.scry_path = os.path.join(cwd,
			f"{cfg.scry}/Adventure/{self.name} ({self.artist}) [{self.set.upper()}].jpg")

		# Ensure save folder exists
		super().make_folders("Adventure")

class Leveler (Normal):
	"""
	Leveler card
	"""
	def __init__ (self, c):
		super().__init__(c)

		# Saved filepath
		self.mtgp_path = os.path.join(cwd,
			f"{cfg.mtgp}/Leveler/{self.name} ({self.artist}) [{self.set.upper()}].jpg")
		self.scry_path = os.path.join(cwd,
			f"{cfg.scry}/Leveler/{self.name} ({self.artist}) [{self.set.upper()}].jpg")

		# Ensure save folder exists
		super().make_folders("Leveler")

class Planeswalker (Normal):
	"""
	Planeswalker card
	"""
	def __init__ (self, c):
		super().__init__(c)

		# Saved filepath
		self.mtgp_path = os.path.join(cwd,
			f"{cfg.mtgp}/Planeswalker/{self.name} ({self.artist}) [{self.set.upper()}].jpg")
		self.scry_path = os.path.join(cwd,
			f"{cfg.scry}/Planeswalker/{self.name} ({self.artist}) [{self.set.upper()}].jpg")

		# Ensure save folder exists
		super().make_folders("Planeswalker")

class Class (Normal):
	"""
	Class card
	"""
	def __init__ (self, c):
		super().__init__(c)

		# Saved filepath
		self.mtgp_path = os.path.join(cwd,
			f"{cfg.mtgp}/Class/{self.name} ({self.artist}) [{self.set.upper()}].jpg")
		self.scry_path = os.path.join(cwd,
			f"{cfg.scry}/Class/{self.name} ({self.artist}) [{self.set.upper()}].jpg")

		# Ensure save folder exists
		super().make_folders("Class")

class Flip (Normal):
	"""
	Flip card
	"""
	def __init__ (self, c):
		super().__init__(c)

		# Saved filepath
		self.mtgp_path = os.path.join(cwd,
			f"{cfg.mtgp}/Flip/{self.name} ({self.artist}) [{self.set.upper()}].jpg")
		self.scry_path = os.path.join(cwd,
			f"{cfg.scry}/Flip/{self.name} ({self.artist}) [{self.set.upper()}].jpg")

		# Ensure save folder exists
		super().make_folders("Flip")

class Split (Normal):
	"""
	Split card
	"""
	def __init__ (self, c):
		super().__init__(c)

		# Saved filepath
		self.mtgp_path = os.path.join(cwd,
			f"{cfg.mtgp}/Split/{self.name} ({self.artist}) [{self.set.upper()}].jpg")
		self.scry_path = os.path.join(cwd,
			f"{cfg.scry}/Split/{self.name} ({self.artist}) [{self.set.upper()}].jpg")

		# Ensure save folder exists
		super().make_folders("Split")

class Planar (Normal):
	"""
	Planar card
	"""
	def __init__ (self, c):
		super().__init__(c)

		# Saved filepath
		self.mtgp_path = os.path.join(cwd,
			f"{cfg.mtgp}/Planar/{self.name} ({self.artist}) [{self.set.upper()}].jpg")
		self.scry_path = os.path.join(cwd,
			f"{cfg.scry}/Planar/{self.name} ({self.artist}) [{self.set.upper()}].jpg")

		# Ensure save folder exists
		super().make_folders("Planar")

# MULTIPLE IMAGE CARDS
class MDFC (Card):
	"""
	Double faced card
	"""
	def __init__(self, c):

		# Face variables
		self.name = c['card_faces'][0]['name']
		self.name_back = c['card_faces'][1]['name']
		self.scrylink = c['card_faces'][0]['image_uris']['art_crop']
		self.scrylink_back = c['card_faces'][1]['image_uris']['art_crop']

		super().__init__(c)

		# Front filepath
		self.mtgp_path = os.path.join(cwd,
			f"{cfg.mtgp}/MDFC Front/{self.name} ({self.artist}) [{self.set.upper()}].jpg")
		self.scry_path = os.path.join(cwd,
			f"{cfg.scry}/MDFC Front/{self.name} ({self.artist}) [{self.set.upper()}].jpg")

		# Back filepath
		self.mtgp_path_back = os.path.join(cwd,
			f"{cfg.mtgp}/MDFC Back/{self.name_back} ({self.artist}) [{self.set.upper()}].jpg")
		self.scry_path_back = os.path.join(cwd,
			f"{cfg.scry}/MDFC Back/{self.name_back} ({self.artist}) [{self.set.upper()}].jpg")

		# Ensure save folders exist
		super().make_folders("MDFC Front")
		super().make_folders("MDFC Back")

	def download (self, log_failed=True):
		"""
		Download each card
		"""
		# Download Front
		front = True
		try: self.download_mtgp (self.name, self.mtgp_path, self.code)
		except:
			if cfg.download_scryfall: self.download_scryfall (self.name, self.scry_path, self.scrylink)
			else: front = False

		# Download back
		back = True
		try: self.download_mtgp (f"{self.name_back} (Back)", self.mtgp_path_back, self.code, True)
		except:
			if cfg.download_scryfall: super.download_scryfall (self.name_back, self.scry_path_back, self.scrylink_back)
			else: back = False

		# Log any failures
		if log_failed:
			if not front and not back:
				core.log(self.name, self.set)
				return False
			if not front: core.log(self.name, self.set, "failed_front")
			elif not back: core.log(self.name_back, self.set, "failed_back")
		return True

class Transform (MDFC):
	"""
	Transform card
	"""
	def __init__(self, c):
		super().__init__(c)

		# Front filepath
		self.mtgp_path = os.path.join(cwd,
			f"{cfg.mtgp}/TF Front/{self.name} ({self.artist}) [{self.set.upper()}].jpg")
		self.scry_path = os.path.join(cwd,
			f"{cfg.scry}/TF Front/{self.name} ({self.artist}) [{self.set.upper()}].jpg")

		# Back filepath
		self.mtgp_path_back = os.path.join(cwd,
			f"{cfg.mtgp}/TF Back/{self.name_back} ({self.artist}) [{self.set.upper()}].jpg")
		self.scry_path_back = os.path.join(cwd,
			f"{cfg.scry}/TF Back/{self.name_back} ({self.artist}) [{self.set.upper()}].jpg")

		# Ensure save folders exist
		super().make_folders("TF Front")
		super().make_folders("TF Back")

class Meld (Card):
	"""
	Meld card -- Will do later
	"""

def get_card_class(c):
	"""
	Return the card class
	"""
	class_map = {
		"normal": Normal,
	    "transform": Transform,
	    "modal_dfc": MDFC,
	    "adventure": Adventure,
	    "leveler": Leveler,
	    "saga": Saga,
	    "planar": Planar,
	    "meld": Meld,
	    "class": Class,
	    "split": Split,
	    "flip": Flip,
	}

	# Planeswalker?
	if "Planeswalker" in c['type_line'] and "card_faces" not in c:
		return Planeswalker
	if "Land" in c['type_line'] and "card_faces" not in c:
		return Land
	return class_map[c['layout']]
