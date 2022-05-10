"""
APP TO EXECUTE THE SEARCH
"""
import os
import re
import sys
import time
import threading
from time import perf_counter
from urllib import parse
from colorama import Style, Fore
import requests as req
from lib import card as dl
from lib import settings as cfg
os.system("")


class Download:
	def __init__(self):
		self.thr = []
		self.basics = []
		self.list = cfg.cardlist
		self.time = perf_counter()

	def start(self):
		"""
		Open cards.txt, for each card initiate a download
		"""
		with open(self.list, 'r', encoding="utf-8") as cards:
			# For each card create new thread
			for i, card in enumerate(cards):
				# Detailed card including set?
				if "--" or " (" in card:
					self.thr.append(threading.Thread(
						target=self.download_detailed,
						args=(card,))
					)
				else:
					self.thr.append(threading.Thread(
						target=self.download_normal,
						args=(card,))
					)

				# Start thread, then sleep to manage thread overload
				self.thr[i].start()
				time.sleep(float(1/cfg.threads_per_second))

			# Ensure each thread completes
			for t in self.thr:
				t.join()
			# Check for basics encountered
			for b in self.basics:
				self.download_basic(b)

			# Output completion time
			self.complete(int(perf_counter()) - self.time)

	def download_normal(self, card):
		"""
		Download a card with no defined set code.
		:param card: Card name
		"""
		# Remove line break
		card = card.replace("\n", "")

		# Basic land?
		if card in cfg.basic_lands:
			self.basics.append(card)
			return None
		try:
			# Retrieve scryfall data
			r = req.get(
				f"https://api.scryfall.com/cards/search?q=!\"{parse.quote(card)}\""
				f"&unique={cfg.unique}"
				f"&include_extras={cfg.include_extras}"
				"&order=released"
			).json()

			# Remove full art entries
			# Add our numbered sets
			prepared = []
			special = {}
			for kind in cfg.special_sets:
				special[kind] = []
			for t in r['data']:
				# No fullart to exclude?
				if not cfg.exclude_fullart or t['full_art'] is False:
					# No numbered set to separate?
					t['accounted'] = False
					for kind in special:
						if t['set'] in cfg.special_sets[kind]:
							special[kind].append(t)
							t['accounted'] = True
					if not t['accounted']: prepared.append(t)

			# Loop through prints of this card
			for c in prepared:
				card_class = dl.get_card_class(c)
				result = card_class(c).download()
				# If we're not downloading all, break
				if not cfg.download_all and result:
					return None

			# Loop through numbered sets
			self.download_special(special)

		except Exception:
			# Try named lookup
			try:
				c = req.get(f"https://api.scryfall.com/cards/named?fuzzy={parse.quote(card)}").json()
				card_class = dl.get_card_class(c)
				card_class(c).download()
			except Exception:
				print(f"{card} not found!")

	@staticmethod
	def download_detailed(item):
		"""
		Download card with defined set code.
		:param item: Card name -- set code
		"""
		# Setup card detailed
		if " (" in item:
			reg = r"(.*) \((.*)\)"
			card = re.match(reg, item)
			name = card[1]
			set_code = card[2]
		else:
			card = item.split("--")
			set_code = card[0]
			name = card[1]

		# Try to find the card
		try:
			# Lookup card
			c = req.get(
				f"https://api.scryfall.com/cards/named?"
				f"fuzzy={parse.quote(name)}"
				f"&set={parse.quote(set_code.lower())}"
			).json()
			card_class = dl.get_card_class(c)
			card_class(c).download()
		except Exception:
			print(f"{name} not found!")

	@staticmethod
	def download_basic(card):
		"""
		Prompt user for set info for basic land, then download.
		:param card: Basic land name
		:return: Always returns None
		"""
		# Have user choose the set, then download
		land_set = input(f"'{card}' basic land found! What set should I pull from? Ex: VOW, C21, ELD\n")
		while True:
			if len(land_set) >= 3:
				try:
					c = req.get(
						f"https://api.scryfall.com/cards/named?fuzzy={parse.quote(card)}"
						f"&set={parse.quote(land_set)}").json()
					dl.Land(c).download()
					break
				except Exception: print("Scryfall couldn't find this set. Try again!")
			else: print("Error! Illegitimate set. Try again!")

	@staticmethod
	def download_special(special):
		"""
		Download cards from sets with special requirements
		:param special: {Set code : [list of cards]}
		"""
		for s, cards in special.items():
			# Promo sets with numbered items
			if s in ('secret lair', "mystical archive"):
				num = 1
				if len(cards) == 1:
					# One card
					for c in cards:
						c['list_order'] = 0
						card_class = dl.get_card_class(c)
						result = card_class(c).download()
						if not cfg.download_all and result:
							return None
				else:
					# A list of cards
					for c in sorted(cards, key=lambda i: i['collector_number']):
						c['list_order'] = 0
						c['name'] = f"{c['name']} {str(num)}"
						card_class = dl.get_card_class(c)
						result = card_class(c).download()
						if not cfg.download_all and result:
							return None
						num += 1
			# Judge promos
			if s == 'judge promo':
				for i, c in enumerate(cards):
					c['list_order'] = i
					card_class = dl.get_card_class(c)
					result = card_class(c).download()
					if not cfg.download_all and result:
						return None
			if s == "misc promo":
				for i, c in enumerate(cards):
					c['list_order'] = i
					card_class = dl.get_card_class(c)
					result = card_class(c).download()
					if not cfg.download_all and result:
						return None


	@staticmethod
	def complete(elapsed):
		"""
		Tell the user the download process is complete.
		:param elapsed: Time to complete downloads (seconds)
		"""
		print(f"Downloads finished in {elapsed} seconds!")
		input("\nAll available files downloaded.\n"
		"See failed.txt for images that couldn't be located.\n"
		"Press enter to exit :)")
		sys.exit()


if __name__ == "__main__":

	print(f"{Fore.YELLOW}{Style.BRIGHT}\n")
	print("  ██████╗ ███████╗████████╗   ███╗   ███╗████████╗ ██████╗ ")
	print(" ██╔════╝ ██╔════╝╚══██╔══╝   ████╗ ████║╚══██╔══╝██╔════╝ ")
	print(" ██║  ███╗█████╗     ██║      ██╔████╔██║   ██║   ██║  ███╗")
	print(" ██║   ██║██╔══╝     ██║      ██║╚██╔╝██║   ██║   ██║   ██║")
	print(" ╚██████╔╝███████╗   ██║      ██║ ╚═╝ ██║   ██║   ╚██████╔╝")
	print("  ╚═════╝ ╚══════╝   ╚═╝      ╚═╝     ╚═╝   ╚═╝    ╚═════╝ ")
	print("  █████╗ ██████╗ ████████╗    ███╗   ██╗ ██████╗ ██╗    ██╗ ")
	print(" ██╔══██╗██╔══██╗╚══██╔══╝    ████╗  ██║██╔═══██╗██║    ██║ ")
	print(" ███████║██████╔╝   ██║       ██╔██╗ ██║██║   ██║██║ █╗ ██║ ")
	print(" ██╔══██║██╔══██╗   ██║       ██║╚██╗██║██║   ██║██║███╗██║ ")
	print(" ██║  ██║██║  ██║   ██║       ██║ ╚████║╚██████╔╝╚███╔███╔╝ ")
	print(" ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝       ╚═╝  ╚═══╝ ╚═════╝  ╚══╝╚══╝  ")
	print(f"{Fore.CYAN}{Style.BRIGHT}MTG Art Downloader by Mr Teferi v1.1.4")
	print("Additional thanks to Trix are for Scoot + Gikkman")
	print(f"http://mpcfill.com --- Support great MTG Proxies!{Style.RESET_ALL}\n")

	# Does the user want to use Google Sheet queries or cards from txt file?
	input("Please view the README for detailed instructions.\n"
	"Cards in cards.txt can either be listed as 'Name' or 'SET--Name'\n"
	"Full Github and README available at: mprox.link/art-downloader\n")

	# Start the download operation
	Download().start()