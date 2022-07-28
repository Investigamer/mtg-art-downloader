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
import requests as req
from lib import card as dl
from lib import settings as cfg
from lib import core
from lib.constants import console
from colorama import Style, Fore

os.system("")


class Download:
    def __init__(self, command=None, card_list=None):
        self.thr = []
        self.fails = []
        self.basics = []
        if not card_list:
            self.list = cfg.cardlist
        else:
            self.list = card_list
        self.time = perf_counter()
        self.command = command

    def start_command(self, dry_run=False):
        """
        Initiate download procedure based on the command.
        """
        # Valid command received?
        if ":" in self.command:
            self.list = core.get_list_from_scryfall(self.command)
        elif self.command:
            self.command = core.get_command(self.command)
            if self.command:
                self.list = core.get_list_from_link(self.command)
        else:
            self.command = None
        self.start(dry_run)

    def start(self, dry_run=False):
        """
        Open card list, for each card initiate a download
        """
        if isinstance(self.list, str):
            with open(self.list, "r", encoding="utf-8") as cards:
                # Remove blank lines, print total cards
                cards = cards.readlines()
                try:
                    cards.remove("")
                except ValueError:
                    pass
                try:
                    cards.remove(" ")
                except ValueError:
                    pass
        elif isinstance(self.list, list):
            cards = self.list
        else:
            print(f"{Fore.RED}---- NO CARD LIST FOUND! ----{Style.RESET_ALL}")
            return None

        # Alert the user
        if not dry_run:
            print(
                f"{Fore.GREEN}---- Downloading {len(cards)} cards! ----{Style.RESET_ALL}"
            )

        # For each card create new thread
        for i, card in enumerate(cards):
            # Detailed card including set?
            if "--" in card or " (" in card:
                self.thr.append(
                    threading.Thread(target=self.download_detailed, args=(card,))
                )
            else:
                self.thr.append(
                    threading.Thread(target=self.download_normal, args=(card,))
                )

            # Start thread, then sleep to manage thread overload
            self.thr[i].start()
            time.sleep(float(1 / cfg.threads_per_second))

        # Ensure each thread completes
        for t in self.thr:
            t.join()
        # Check for basics encountered
        for b in self.basics:
            self.download_basic(b)

        # Output completion time
        if not dry_run:
            self.complete(int(perf_counter()) - self.time)

    def download_normal(self, card, disable_all=False):
        """
        Download a card with no defined set code.
        :param card: Card name
        :param disable_all: Disable download all
        """
        # Remove line break
        card = card.replace("\n", "")
        results = []
        fail = True

        # Basic land?
        if card in cfg.basic_lands:
            self.basics.append(card)
            return True
        try:
            # Retrieve scryfall data
            r = req.get(
                f'https://api.scryfall.com/cards/search?q=!"{parse.quote(card)}"'
                f"&unique={cfg.unique}"
                f"&include_extras={cfg.include_extras}"
                "&order=released"
            ).json()

            # Remove full art entries
            # Add our numbered sets
            prepared = []
            for t in r["data"]:
                # No fullart to exclude?
                if not cfg.exclude_fullart or t["full_art"] is False:
                    prepared.append(t)

            # Loop through prints of this card
            for c in prepared:
                card_class = dl.get_card_class(c)
                result = card_class(c).download()
                # If we're not downloading all, break
                if (not cfg.download_all or disable_all) and result:
                    results = [True]
                    break
                results.append(result)

        except Exception:
            # Try named lookup
            try:
                c = req.get(
                    f"https://api.scryfall.com/cards/named?fuzzy={parse.quote(card)}"
                ).json()
                card_class = dl.get_card_class(c)
                result = card_class(c).download()
            except Exception:
                console.out.append(f"{card} not found!")
                result = False
            results.append(result)
        if sum(results) == 0:
            self.fails.append(card)
        return results

    def download_detailed(self, item):
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
            result = card_class(c).download()
        except Exception:
            console.out.append(f"{name} not found!")
            result = False
        if not result:
            self.fails.append(item)
        return result

    @staticmethod
    def download_basic(card):
        """
        Prompt user for set info for basic land, then download.
        :param card: Basic land name
        :return: Always returns None
        """
        # Have user choose the set, then download
        land_set = input(
            f"'{card}' basic land found! What set should I pull from? Ex: VOW, C21, ELD\n"
        )
        while True:
            if len(land_set) >= 3:
                try:
                    c = req.get(
                        f"https://api.scryfall.com/cards/named?fuzzy={parse.quote(card)}"
                        f"&set={parse.quote(land_set)}"
                    ).json()
                    dl.Land(c).download()
                    break
                except Exception:
                    console.out.append("Scryfall couldn't find this set. Try again!")
            else:
                console.out.append("Error! Illegitimate set. Try again!")

    @staticmethod
    def complete(elapsed):
        """
        Tell the user the download process is complete.
        :param elapsed: Time to complete downloads (seconds)
        """
        time.sleep(1)
        console.out.append(f"Downloads finished in {elapsed} seconds!")
        time.sleep(0.02)
        console.out.append(
            "\nAll available files downloaded.\n"
            "See failed.txt for images that couldn't be located.\n"
            "Press enter to exit :)"
        )
        input()
        sys.exit()


if __name__ == "__main__":
    __VER__ = "1.1.6"
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
    print(f"{Fore.CYAN}{Style.BRIGHT}MTG Art Downloader by Mr Teferi v{__VER__}")
    print("Additional thanks to Trix are for Scoot + Gikkman")
    print(f"http://mpcfill.com --- Support great MTG Proxies!{Style.RESET_ALL}\n")

    # Does the user want to use Google Sheet queries or cards from txt file?
    choice = input(
        "Please view the README for detailed instructions.\n"
        "Cards in cards.txt can either be listed as 'Name' or 'SET--Name'\n"
        "Full Github and README available at: mprox.link/art-downloader\n"
    )

    # If the command is valid, download based on that, otherwise cards.txt
    if choice != "":
        print()  # Add newline gap
    Download(choice).start_command()
