"""
APP TO EXECUTE THE SEARCH
"""
# pylint: disable=R0912, R1702, R0915
import os
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
				if "--" in card:
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

			# Remove full art entries?
			prepared = []
			sld = []
			for t in r['data']:
				# No fullart to exclude?
				if not cfg.exclude_fullart or t['full_art'] is False:
					# No secret lair to exclude
					if t['set'] != "sld":
						prepared.append(t)
					else:
						sld.append(t)

			# Loop through prints of this card
			done = False
			sl_num = 1
			repeat = False
			for c in prepared:
				card_class = dl.get_card_class(c)
				result = card_class(c).download()
				if not cfg.download_all and result:
					done = True
					break
			for c in sorted(sld, key=lambda i: i['collector_number']):
				if done or cfg.exclude_secret_lair: break
				if repeat: c['name'] = c['name'] + " " + str(sl_num)
				sl_num += 1
				repeat = True
				card_class = dl.get_card_class(c)
				card_class(c).download()

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
		card = item.split("--")
		set_code = card[0]
		name = card[1]

		# Try to find the card
		try:
			# Lookup card
			c = req.get(
				f"https://api.scryfall.com/cards/named?fuzzy={parse.quote(name)}&set={parse.quote(set_code)}").json()
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
	print(f"{Fore.CYAN}{Style.BRIGHT}MTG Art Downloader by Mr Teferi")
	print("Additional thanks to Trix are for Scoot + Gikkman")
	print(f"http://mpcfill.com --- Support great MTG Proxies!{Style.RESET_ALL}\n")

	# Does the user want to use Google Sheet queries or cards from txt file?
	input("Please view the README for detailed instructions.\n"
	"Cards in cards.txt can either be listed as 'Name' or 'SET--Name'\n"
	"Full Github and README available at: mprox.link/art-downloader\n")

	# Start the download operation
	Download().start()