"""
APP TO EXECUTE THE SEARCH
"""

import os
import re
import sys
from functools import cached_property
from multiprocessing import cpu_count, freeze_support
from multiprocessing.pool import Pool
from pathlib import Path
from typing import Union, Optional
from time import perf_counter
from src import card as dl
from src import settings as cfg
from src.__version__ import version
from src.constants import console
from colorama import Style, Fore

from src.core import (
    normalize_card_list,
    get_list_from_link,
    get_list_from_scryfall,
    get_command,
)
from src.fetch import (
    get_scryfall_card_named,
    get_scryfall_card_numbered,
    get_scryfall_card_search,
)
from src.types import DownloadResult

# Core variables
detailed_reg = re.compile(r"(.*) \((.*)\) ?(.*)")
cwd = os.getcwd()
os.system("")


class Download:
    def __init__(
        self,
        command: str = None,
        card_list: Union[str, list] = None,
        testing: bool = False,
    ):
        self._testing: bool = testing
        self._time: float = perf_counter()
        self._list = cfg.cardlist if not card_list else card_list
        self._command: Optional[str] = command
        self.fails: list = []

        # Mute console output if in testing mode
        if self.is_test:
            console.waiting = False

    """
    PROPERTIES
    """

    @property
    def is_test(self):
        return self._testing

    @cached_property
    def cards(self) -> list[Union[dict, str]]:
        """
        Return a card list either from given command or text file.
        """
        if self.command and ":" in self.command:
            return get_list_from_scryfall(self.command)
        if self.command:
            if link := get_command(self.command):
                return normalize_card_list(get_list_from_link(link))
        if isinstance(self._list, list):
            return self._list
        if os.path.isfile(self._list):
            with open(self._list, "r", encoding="utf-8") as f:
                # Remove blank lines, print total cards
                return normalize_card_list(f.readlines())
        return []

    @cached_property
    def command(self) -> str:
        return self._command or ""

    @cached_property
    def time(self) -> float:
        return perf_counter() - self._time

    """
    METHODS
    """

    def start(self) -> list[tuple[bool, str]]:
        """
        Using our card list, generate a download for each card.
        @return: List of tuples, each containing success/fail state and name of the card.
        """
        # Do we have a valid card list?
        if not self.cards:
            print(f"{Fore.RED}---- NO CARD LIST FOUND! ----{Style.RESET_ALL}")
            return []
        if not self.is_test:
            print(
                f"{Fore.GREEN}---- Downloading {len(self.cards)} cards! ----{Style.RESET_ALL}"
            )

        # Create a pool to execute these downloads
        with Pool(processes=cpu_count()) as pool:
            downloads = pool.map(self.stage_download, self.cards)

        # Build results list
        results = []
        for res in list(downloads):
            results.extend(res)

        # Output completion time
        if not self.is_test:
            self.complete()
        return results

    def stage_download(self, card: Union[str, dict]) -> DownloadResult:
        """
        Choose the appropriate method to call to download this card, then call that method.
        @param card: Card details or name.
        @return: Tuple containing success/fail state and name of the card.
        """
        # Associate the proper download method
        if isinstance(card, dict):
            return self.download_dict(card)
        elif isinstance(card, str):
            return (
                self.download_detailed(card)
                if " (" in card
                else self.download_normal(card)
            )
        console.print(f"Unknown: {str(card)}")
        return [(False, str(card))]

    def complete(self):
        """
        Tell the user the download process is complete.
        """
        console.print(f"Downloads finished in {self.time} seconds!")
        console.print(
            "\nAll available files downloaded.\n"
            "See failed.txt for images that couldn't be located.\n"
            "Press enter to exit :)"
        )
        console.flush()
        input()
        sys.exit()

    """
    DOWNLOAD METHODS
    """

    def download_normal(self, card: str, disable_all: bool = False) -> DownloadResult:
        """
        Download a card with no defined set code.
        @param card: Card name
        @param disable_all: Disable download all
        """
        # Prepare our return data
        results: DownloadResult = []

        # Retrieve scryfall data
        res = get_scryfall_card_search(
            params={
                "unique": cfg.unique,
                "include_extras": cfg.include_extras,
                "order": "released",
                "q": f'!"{card}"',
            }
        )

        # Valid card data returned?
        if not res:
            return [(False, card)]

        # Remove full art entries if necessary
        cards = [c for c in res if not cfg.exclude_fullart or not c.get("full_art")]

        # Loop through prints of this card
        for c in cards:
            # Download the card
            result = self.download_dict(c)

            # Break if result is successful and we only need one
            if (not cfg.download_all or disable_all) and all(
                [res[0] for res in result]
            ):
                return result
            results.extend(result)
        return results

    def download_detailed(self, item: str) -> DownloadResult:
        """
        Download card with defined set code, possibly number.
        @param item: Card name (SET) number
        @return: True if successful, False if unsuccessful.
        """
        # Setup card details (Array destructuring)
        name, code, number = detailed_reg.findall(item)[0]

        # Was collector number given?
        card = (
            get_scryfall_card_numbered(code=code.lower(), number=number)
            if number
            else get_scryfall_card_named(name=name, code=code.lower())
        )

        # Valid card data found?
        if not card:
            return [(False, item)]

        # Try to download the card
        return self.download_dict(card)

    def download_dict(self, card: dict) -> DownloadResult:
        """
        Downloads a card using fetched scryfall data.
        @param card: Dict of card data
        @return: True if succeeded, False if not
        """
        # Ensure this is a real card
        if not card.get("name"):
            return [(False, "No Card Specified")]

        # Try to download the card
        card_class = dl.get_card_class(card)
        return card_class(card).download(not self.is_test)


if __name__ == "__main__":

    # Add necessary directories
    freeze_support()
    Path(cfg.folder).mkdir(mode=511, parents=True, exist_ok=True)
    Path(cfg.mtgp).mkdir(mode=511, parents=True, exist_ok=True)
    Path(cfg.scry).mkdir(mode=511, parents=True, exist_ok=True)
    Path(os.path.join(cwd, "logs")).mkdir(mode=511, parents=True, exist_ok=True)

    # Welcome page
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
    print(f"{Fore.CYAN}{Style.BRIGHT}MTG Art Downloader by Mr Teferi v{version}")
    print("Additional thanks to Trix are for Scoot, Chilli, and Gikkman")
    print(f"https://www.patreon.com/mpcfill --- Support our apps!{Style.RESET_ALL}\n")

    # Does the user want to use Google Sheet queries or cards from txt file?
    choice = input(
        "Please view the README for detailed instructions.\n"
        "Cards in cards.txt can either be listed as 'Name' or 'SET--Name'\n"
        "Full Github and README available at: mprox.link/art-downloader\n"
    )

    # If the command is valid, download based on that, otherwise cards.txt
    if choice != "":
        print()  # Add newline gap
    Download(choice).start()
