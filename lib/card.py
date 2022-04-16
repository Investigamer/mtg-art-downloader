"""
CARD CLASSES
"""
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
		# Defined for later use
		self.code = None

		# Inherited card info
		self.set = c['set']
		self.artist = c['artist']
		self.num = c['collector_number']

		# Fix mtgp setcode
		if self.set in cfg.replace_sets:
			self.mtgp_set = cfg.replace_sets[self.set]
		else: self.mtgp_set = self.set

		# Name if not defined
		if not hasattr(self, 'name'):
			self.name = c['name']

		# Make sure card num is 3 digits
		if len(self.num) == 1: self.num = f"00{self.num}"
		elif len(self.num) == 2: self.num = f"0{self.num}"

		# Alternate version or promo card
		self.alt = self.check_for_alternate(c)
		self.promo = self.check_for_promo(c['set_type'])

		# Get the MTGP code
		self.get_mtgp_code()

		# Make folders, setup path
		if hasattr(self, 'path'): self.make_folders()
		self.make_path()

	def check_for_alternate(self, c):
		"""
		Checks if this is an alternate art card
		:param c: Card info
		:return: bool
		"""
		if 'list_order' in c: return c['list_order']
		if (c['border_color'] == "borderless"
			and c['set'] not in cfg.special_sets
		):
			return True
		if self.num[-1] == "s": return True
		return False

	def check_for_promo(self, set_type):
		"""
		Check if this is a promo card
		"""
		set_types = ['funny', 'promo']
		if set_type in set_types: return True
		return False

	def get_mtgp_code(self):
		"""
		Get the correct mtgp URL code
		"""
		try: self.code = core.get_mtgp_code(self.mtgp_set, self.name, self.alt)
		except Exception:
			if self.promo:
				try: self.code = core.get_mtgp_code("pmo", self.name, self.alt)
				except Exception: self.code = self.set+self.num
			else: self.code = self.set+self.num

	def download (self, log_failed=True):
		"""
		Download just one version of this card.
		"""
		# Download only scryfall?
		if cfg.only_scryfall:
			self.download_scryfall (self.name, self.scry_path, self.scrylink)
			return True

		# Try downloading MTGP
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
		print(f"{Fore.GREEN}MTGP:{Style.RESET_ALL} {name} [{self.set.upper()}]")

	def download_scryfall (self, name, path, scrylink):
		"""
		Download scryfall art crop
		"""
		print(f"{Fore.YELLOW}SCRYFALL: {name}{Style.RESET_ALL}")
		request.urlretrieve(scrylink, path)

	def make_folders(self):
		"""
		Check that the folders exist
		"""
		if self.path != "":
			Path(os.path.join(cfg.mtgp, self.path)).mkdir(mode=511, parents=True, exist_ok=True)
			Path(os.path.join(cfg.scry, self.path)).mkdir(mode=511, parents=True, exist_ok=True)

		# Setup backs folder if exists
		if hasattr(self, 'path_back'):
			Path(os.path.join(cfg.mtgp, self.path_back)).mkdir(mode=511, parents=True, exist_ok=True)
			Path(os.path.join(cfg.scry, self.path_back)).mkdir(mode=511, parents=True, exist_ok=True)

	def make_path(self):
		"""
		Define save paths for this card
		"""
		self.mtgp_path = os.path.join(cwd,
			f"{cfg.mtgp}/{self.path}{self.name} ({self.artist}) [{self.set.upper()}].jpg")
		self.scry_path = os.path.join(cwd,
			f"{cfg.scry}/{self.path}{self.name} ({self.artist}) [{self.set.upper()}].jpg")

		# Setup back path if exists
		if hasattr(self, 'path_back'):
			self.mtgp_path_back = os.path.join(cwd,
				f"{cfg.mtgp}/{self.path_back}{self.name_back} ({self.artist}) [{self.set.upper()}].jpg")
			self.scry_path_back = os.path.join(cwd,
				f"{cfg.scry}/{self.path_back}{self.name_back} ({self.artist}) [{self.set.upper()}].jpg")

class Normal (Card):
	"""
	Normal frame card
	"""
	def __init__ (self, c):
		# Create empty path if no path is set
		if hasattr(self, 'path'): pass
		else: self.path = ""
		super().__init__(c)
		self.scrylink = c['image_uris']['art_crop']

class Land (Normal):
	"""
	Basic land card
	"""
	def __init__ (self, c):
		self.path = "Land/"
		super().__init__(c)

class Saga (Normal):
	"""
	Saga card
	"""
	def __init__ (self, c):
		self.path = "Saga/"
		super().__init__(c)

class Adventure (Normal):
	"""
	Adventure card
	"""
	def __init__ (self, c):
		self.path = "Adventure/"
		super().__init__(c)

class Leveler (Normal):
	"""
	Leveler card
	"""
	def __init__ (self, c):
		self.path = "Leveler/"
		super().__init__(c)

class Planeswalker (Normal):
	"""
	Planeswalker card
	"""
	def __init__ (self, c):
		self.path = "Planeswalker/"
		super().__init__(c)

class Class (Normal):
	"""
	Class card
	"""
	def __init__ (self, c):
		self.path = "Class/"
		super().__init__(c)

class Flip (Normal):
	"""
	Flip card
	"""
	def __init__ (self, c):
		self.path = "Flip/"
		self.savename = c['card_faces'][0]['name']
		super().__init__(c)

	def get_mtgp_code(self):
		# Override this method because flip names are different
		name = self.name.replace("//","/")
		try:
			if self.alt: self.code = core.get_mtgp_code(self.mtgp_set, name, True)
			else: self.code = core.get_mtgp_code(self.mtgp_set, name)
		except:
			if self.promo:
				try:
					if self.alt: self.code = core.get_mtgp_code("pmo", name, True)
					else: self.code = core.get_mtgp_code("pmo", name)
				except: self.code = self.set+self.num
			else: self.code = self.set+self.num

	def make_path(self):
		# Override this method because // isn't valid in filenames
		self.mtgp_path = os.path.join(cwd,
			f"{cfg.mtgp}/{self.path}{self.savename} ({self.artist}) [{self.set.upper()}].jpg")
		self.scry_path = os.path.join(cwd,
			f"{cfg.scry}/{self.path}{self.savename} ({self.artist}) [{self.set.upper()}].jpg")

class Planar (Normal):
	"""
	Planar card
	"""
	def __init__ (self, c):
		self.path = "Planar/"
		super().__init__(c)

# MULTIPLE IMAGE CARDS
class MDFC (Card):
	"""
	Double faced card
	"""
	def __init__(self, c):

		# Face variables
		self.name = c['card_faces'][0]['name']
		self.name_back = c['card_faces'][1]['name']
		if not hasattr(self, 'scrylink'):
			self.scrylink = c['card_faces'][0]['image_uris']['art_crop']
			self.scrylink_back = c['card_faces'][1]['image_uris']['art_crop']
		if not hasattr(self, 'path'):
			self.path = "MDFC Front/"
			self.path_back = "MDFC Back/"
		super().__init__(c)

	def download (self, log_failed=True):
		"""
		Download each card
		"""
		# Default success value, change on failure
		front = True
		back = True

		# Download only scryfall?
		if cfg.only_scryfall:
			try: self.download_scryfall (self.name, self.scry_path, self.scrylink)
			except: front = False
			try: self.download_scryfall (self.name_back, self.scry_path_back, self.scrylink_back)
			except: back = True

			# Log any failures
			if log_failed:
				if not front and not back:
					core.log(self.name, self.set)
					return False
				if not front: core.log(self.name, self.set, "failed_front")
				elif not back: core.log(self.name_back, self.set, "failed_back")
			return True

		# Download Front
		try: self.download_mtgp (self.name, self.mtgp_path, self.code)
		except:
			if cfg.download_scryfall:
				try: self.download_scryfall (self.name, self.scry_path, self.scrylink)
				except: front = False
			else: front = False

		# Download back
		try: self.download_mtgp (f"{self.name_back} (Back)", self.mtgp_path_back, self.code, True)
		except:
			if cfg.download_scryfall:
				try: self.download_scryfall (self.name_back, self.scry_path_back, self.scrylink_back)
				except: back = False
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
		self.nopath = True
		self.path = "TF Front/"
		self.path_back = "TF Back/"
		super().__init__(c)

class Split (MDFC):
	"""
	Split card
	"""
	def __init__ (self, c):
		self.fullname = c['name']
		self.nopath = True
		self.path = "Split/"
		self.path_back = "Split/"
		self.scrylink = c['image_uris']['art_crop']
		super().__init__(c)

	def get_mtgp_code(self):
		# Override this method because split names are different
		name = self.fullname.replace("//","/")
		try:
			if self.alt: self.code = core.get_mtgp_code(self.mtgp_set, name, True)
			else: self.code = core.get_mtgp_code(self.mtgp_set, name)
		except:
			if self.promo:
				try:
					if self.alt: self.code = core.get_mtgp_code("pmo", name, True)
					else: self.code = core.get_mtgp_code("pmo", name)
				except: self.code = self.set+self.num
			else: self.code = self.set+self.num

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

	# Planeswalker, saga, or land? (non mdfc)
	if "Planeswalker" in c['type_line'] and "card_faces" not in c:
		return Planeswalker
	if "Saga" in c['type_line'] and "card_faces" not in c:
		return Saga
	if "Land" in c['type_line'] and "card_faces" not in c:
		return Land
	return class_map[c['layout']]
