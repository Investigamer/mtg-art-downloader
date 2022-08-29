"""
APP TO EXECUTE THE SEARCH
"""
import os
import re
import sys
import time
import threading
from typing import Union, Optional
from time import perf_counter
from urllib import parse
import requests as req
from lib import card as dl
from lib import settings as cfg
from lib import core
from lib.constants import console
from colorama import Style, Fore

cwd = os.getcwd()
__VER__ = "1.1.9"
os.system("")


class Download:
    def __init__(self, command: str = None, card_list: Union[str, list] = None):
        self.thr: list = []
        self.fails: list = []
        self.basics: list = []
        if not card_list:
            self.list = cfg.cardlist
        else:
            self.list = card_list
        self.time: float = perf_counter()
        self.command: Optional[str] = command

    def start_command(self, dry_run: bool = False) -> list:
        """
        Initiate download procedure based on the command.
        """
        # Valid command received?
        if isinstance(self.command, str):
            if ":" in self.command:
                self.list = core.get_list_from_scryfall(self.command)
            else:
                link = core.get_command(self.command)
                if link:
                    self.list = core.get_list_from_link(link)

        self.start(dry_run)
        return self.fails

    def start(self, dry_run: bool = False) -> None:
        """
        Open card list, for each card initiate a download
        """
        if isinstance(self.list, str):
            with open(self.list, "r", encoding="utf-8") as f:
                # Remove blank lines, print total cards
                cards = f.readlines()
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
            if isinstance(card, dict):
                self.thr.append(
                    threading.Thread(target=self.download_dict, args=(card,))
                )
            elif "--" in card or " (" in card:
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
            self.complete(int(perf_counter() - self.time))

    def download_normal(self, card: str, disable_all: bool = False) -> list:
        """
        Download a card with no defined set code.
        :param card: Card name
        :param disable_all: Disable download all
        """
        # Remove line break
        card = card.replace("\n", "")
        results = []

        # Basic land?
        if card in cfg.basic_lands:
            self.basics.append(card)
            return [True]
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

    def download_detailed(self, item: str) -> bool:
        """
        Download card with defined set code.
        :param item: Card name -- set code
        """
        # Setup card detailed
        if " (" in item:
            reg = r"(.*) \((.*)\)"
            card = re.findall(reg, item)[0]
            name = card[0]
            set_code = card[1]
        else:
            card = item.split("--")
            set_code = card[0]
            name = card[1]
        name = name.replace("\n", "")

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

    def download_dict(self, card: dict):
        """
        Downloads a card with previously fetched scryfall data.
        :param card: Dict of card data
        :return: True if succeeded, False if not
        """
        # Try to download the card
        try:
            card_class = dl.get_card_class(card)
            result = card_class(card).download()
        except Exception:
            console.out.append(f"{card['name']} not found!")
            result = False
        if not result:
            self.fails.append(card["name"])
        return result

    @staticmethod
    def download_basic(card: str):
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
    def complete(elapsed: int):
        """
        Tell the user the download process is complete.
        :param elapsed: Time to complete downloads (seconds)
        """
        console.out.append(f"Downloads finished in {elapsed} seconds!")
        console.out.append(
            "\nAll available files downloaded.\n"
            "See failed.txt for images that couldn't be located.\n"
            "Press enter to exit :)"
        )
        console.flush()
        input()
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
