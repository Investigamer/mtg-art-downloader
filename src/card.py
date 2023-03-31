"""
CARD CLASSES
"""
import os
from functools import cached_property
from typing import Optional

from pathvalidate import sanitize_filename
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from unidecode import unidecode
from src import settings as cfg
from src import core
from src.core import log_failed, log_mtgp, log_scryfall
from src.fetch import get_scryfall_image, get_mtgp_image, get_mtgp_page
from src.types import DownloadResult

cwd = os.getcwd()


"""
CARD CLASSES
"""


class Card:
    """
    Base class to extend all cards to.
    """

    path = ""
    path_back = ""

    def __init__(self, c: dict) -> None:
        # Store all card info
        self.c = c
        self._promo = False

        # Create download folders if needed
        Path(os.path.join(cfg.mtgp, self.path)).mkdir(
            mode=511, parents=True, exist_ok=True
        )
        Path(os.path.join(cfg.scry, self.path)).mkdir(
            mode=511, parents=True, exist_ok=True
        )

        # Setup backs folder if needed
        if self.path_back:
            Path(os.path.join(cfg.mtgp, self.path_back)).mkdir(
                mode=511, parents=True, exist_ok=True
            )
            Path(os.path.join(cfg.scry, self.path_back)).mkdir(
                mode=511, parents=True, exist_ok=True
            )

    """
    PROPERTIES
    """

    @property
    def set(self) -> str:
        return self.c.get("set", "")

    @property
    def name(self) -> str:
        return self.c.get("name", "")

    @property
    def artist(self) -> str:
        return unidecode(self.c.get("artist", ""))

    @property
    def number(self) -> str:
        return self.c.get("collector_number", "")

    @property
    def set_name(self) -> str:
        return self.c.get("set_name", "")

    @property
    def set_type(self) -> str:
        return self.c.get("set_type", "")

    @property
    def label(self) -> str:
        return f"{self.name} ({self.set.upper()}) {self.number}"

    @property
    def mtgp_name(self) -> str:
        return self.name

    @cached_property
    def mtgp_code(self) -> str:
        """
        Get the correct mtgp URL code
        """
        # Possible promo set
        if self.mtgp_set and self.promo:
            if code := core.get_mtgp_code_pmo(
                self.mtgp_name, self.artist, self.set_name, self.mtgp_set
            ):
                return code

        # Try looking for the card under its collector number
        if code := core.get_mtgp_code(self.mtgp_set, self.number, self.mtgp_name):
            return code
        return self.set + self.number

    @cached_property
    def mtgp_set(self) -> str:
        # Acquire MTGP appropriate set code
        mtgp_set = self.set
        if mtgp_set in cfg.replace_sets:
            mtgp_set = cfg.replace_sets[self.set]

        # Check for promo set
        set_types = ["funny", "promo"]
        if mtgp_set == "pre":
            self.promo = True
        if "Alchemy" in self.set_name:
            self.promo = True
            return "a22"
        if "Judge Gift" in self.set_name or mtgp_set == "dci":
            self.promo = True
            return "dci"
        if self.set_name in ("Legacy Championship", "Vintage Championship"):
            self.promo = True
            return "uni"
        if self.set_type in set_types:
            self.promo = True
            return "pmo"
        return mtgp_set

    @cached_property
    def mtgp_url(self) -> Optional[str]:
        # Acquire best download link for MTGP image
        html = get_mtgp_page(f"https://www.mtgpics.com/card?ref={self.mtgp_code}")
        soup = BeautifulSoup(html, "html.parser")
        soup_img = soup.find_all(
            "img", {"style": "display:block;border:4px black solid;cursor:pointer;"}
        )
        return core.get_card_face(soup_img, False)

    @cached_property
    def mtgp_path(self) -> str:
        # Path to save MTGP image download
        path = os.path.join(cfg.mtgp, self.path) if self.path else cfg.mtgp
        return self.generate_path(path, self.name, self.artist)

    @property
    def scry_url(self) -> str:
        # Download link for Scryfall art crop
        return self.c.get("image_uris", {}).get("art_crop", "")

    @cached_property
    def scry_path(self) -> str:
        # Path to save Scryfall art crop download
        path = os.path.join(cfg.scry, self.path) if self.path else cfg.scry
        return self.generate_path(path, self.name, self.artist)

    """
    SETTABLE PROPERTIES
    """

    @property
    def promo(self) -> bool:
        return self._promo

    @promo.setter
    def promo(self, value):
        self._promo = value

    """
    METHODS
    """

    def generate_path(self, path: str, name: str, artist: str):
        """
        Generate a valid path using given card details.
        @param path: Main path to prepend with.
        @param name: Name of the card.
        @param artist: Artist of the card.
        @return: Valid path to save a file.
        """
        filename = self.naming_convention(name, artist, self.set.upper(), self.number)
        path = os.path.join(path, f"{filename}.jpg")
        if not cfg.overwrite:
            path = self.check_path(path)
        return path

    def download(self, logging: bool = True) -> DownloadResult:
        """
        Initiate download of the card image.
        @param logging: Log failed downloads if True.
        @return: List of tuple results containing success state, and card label.
        """
        # Download only scryfall?
        if cfg.only_scryfall:
            if self.download_scryfall(self.scry_url, self.scry_path, self.label):
                return [(True, self.label)]
            log_failed(self.label, action="SCRY")
            return [(False, self.label)]

        # Try downloading MTGP
        if not self.download_mtgp(self.mtgp_url, self.mtgp_path, self.label):
            if (
                cfg.download_scryfall
                and self.download_scryfall(self.scry_url, self.scry_path, self.label)
                and logging
            ):
                log_failed(self.label, print_out=False)
            elif logging:
                log_failed(self.label)
            return [(False, self.label)]
        return [(True, self.label)]

    """
    STATIC METHODS
    """

    @staticmethod
    def download_mtgp(
        url: Optional[str], path: Optional[str], label: Optional[str]
    ) -> bool:
        """
        Download MTG art from URL.
        @param url: URL to download image from.
        @param path: Path to save the image.
        @param label: Display label for card being downloaded.
        @return: True if successful, otherwise False.
        """
        if url and path:
            if get_mtgp_image(url, path):
                log_mtgp(label)
                return True
        return False

    @staticmethod
    def download_scryfall(
        url: Optional[str], path: Optional[str], label: Optional[str]
    ) -> bool:
        """
        Download scryfall art crop from URL.
        @param url: URL to download image from.
        @param path: Path to save the image.
        @param label: Display label for card being downloaded.
        @return: True if successful, otherwise False.
        """
        if url and path:
            if get_scryfall_image(url, path):
                log_scryfall(label)
                return True
        return False

    @staticmethod
    def check_path(path):
        """
        Check if path needs to be numbered to prevent overwrite.
        """
        i = 0
        current_path = path
        while os.path.isfile(current_path):
            i += 1
            current_path = path.replace(".jpg", f" ({str(i)}).jpg")
        return current_path

    @staticmethod
    def naming_convention(
        card_name: str, card_artist: str, card_set: str, card_number: str
    ) -> str:
        """
        Generates filename using config naming convention.
        @param card_name: Name of the card.
        @param card_artist: Artist of the card.
        @param card_set: Set code of the card.
        @param card_number: Collector number of the card.
        @return: Correct filename
        """
        result = (
            cfg.naming.replace("NAME", card_name)
            .replace("ARTIST", card_artist)
            .replace("SET", card_set)
            .replace("NUMBER", card_number)
        )
        return str(sanitize_filename(result))


"""
CARDS WITH TWO NAMES, ONE FACE
"""


class Adventure(Card):
    """
    Adventure card
    """

    path = "Adventure"

    @property
    def name_saved(self) -> str:
        return self.c["card_faces"][0]["name"]

    @cached_property
    def mtgp_path(self) -> str:
        # Path to save MTGP image download
        return self.generate_path(
            os.path.join(cfg.mtgp, self.path), self.name_saved, self.artist
        )

    @cached_property
    def scry_path(self) -> str:
        # Path to save Scryfall art crop download
        return self.generate_path(
            os.path.join(cfg.scry, self.path), self.name_saved, self.artist
        )

    @property
    def mtgp_name(self) -> str:
        # MTGP only displays one forward slash
        return self.name.replace("//", "/")


class Flip(Card):
    """
    Flip card
    """

    path = "Flip"

    @property
    def name_saved(self) -> str:
        return self.c["card_faces"][0]["name"]

    @cached_property
    def mtgp_path(self) -> str:
        # Path to save MTGP image download
        return self.generate_path(
            os.path.join(cfg.mtgp, self.path), self.name_saved, self.artist
        )

    @cached_property
    def scry_path(self) -> str:
        # Path to save Scryfall art crop download
        return self.generate_path(
            os.path.join(cfg.scry, self.path), self.name_saved, self.artist
        )

    @property
    def mtgp_name(self) -> str:
        return self.name.replace("//", "/")


"""
CARDS WITH CARD_FACES ARRAY
"""


# MULTIPLE IMAGE CARDS
class MDFC(Card):
    """
    Double faced card
    """

    path = "MDFC Front"
    path_back = "MDFC Back"

    @property
    def name(self) -> str:
        return self.c["card_faces"][0]["name"]

    @property
    def name_back(self) -> str:
        return self.c["card_faces"][1]["name"]

    @property
    def artist(self) -> str:
        return self.c["card_faces"][0]["artist"]

    @property
    def artist_back(self) -> str:
        return self.c["card_faces"][1]["artist"]

    @property
    def scry_urls(self) -> list[Optional[str]]:
        return [
            self.c["card_faces"][0]["image_uris"]["art_crop"],
            self.c["card_faces"][1]["image_uris"]["art_crop"],
        ]

    @cached_property
    def mtgp_urls(self) -> list[Optional[str]]:
        # Acquire best download link for MTGP image
        r = requests.get("https://www.mtgpics.com/card?ref=" + self.mtgp_code)
        soup = BeautifulSoup(r.content, "html.parser")
        soup_img = soup.find_all(
            "img", {"style": "display:block;border:4px black solid;cursor:pointer;"}
        )
        return [core.get_card_face(soup_img, False), core.get_card_face(soup_img, True)]

    @cached_property
    def mtgp_paths(self) -> list[str]:
        # Path to save MTGP image download
        return [
            self.generate_path(
                os.path.join(cfg.mtgp, self.path), self.name, self.artist
            ),
            self.generate_path(
                os.path.join(cfg.mtgp, self.path_back), self.name_back, self.artist_back
            ),
        ]

    @cached_property
    def scry_paths(self) -> list[str]:
        # Path to save Scryfall art crop download
        return [
            self.generate_path(
                os.path.join(cfg.scry, self.path), self.name, self.artist
            ),
            self.generate_path(
                os.path.join(cfg.scry, self.path_back), self.name_back, self.artist_back
            ),
        ]

    @cached_property
    def labels(self) -> list[str]:
        return [
            f"{self.name} ({self.set.upper()}) {self.number}",
            f"{self.name_back} ({self.set.upper()}) {self.number}",
        ]

    def download(self, logging: bool = True):
        """
        Download each card side.
        @param logging: Whether to log failed download attempts.
        @return:
        """
        # Track download results
        results = []

        # Download only scryfall?
        if cfg.only_scryfall:
            for i, scry_url in enumerate(self.scry_urls):
                result = self.download_scryfall(
                    scry_url, self.scry_paths[i], self.labels[i]
                )
                results.append((result, self.labels[i]))
                if not result and logging:
                    log_failed(self.labels[i], action="SCRY")
            return results

        # Try to download MTGP
        for i, scry_url in enumerate(self.scry_urls):
            result = self.download_mtgp(
                self.mtgp_urls[i], self.mtgp_paths[i], self.labels[i]
            )
            if not result:
                # Download Scryfall as a backup?
                if cfg.download_scryfall and self.download_scryfall(
                    scry_url, self.scry_paths[i], self.labels[i]
                ):
                    log_failed(self.labels[i], print_out=False)
                elif logging:
                    log_failed(self.labels[i])
            results.append((result, self.labels[i]))
        return results


class Split(MDFC):
    """
    Split card
    """

    path = "Split"
    path_back = "Split"

    @property
    def scry_urls(self) -> list[Optional[str]]:
        return [self.c["image_uris"]["art_crop"], self.c["image_uris"]["art_crop"]]

    @property
    def mtgp_name(self) -> str:
        return self.name.replace("//", "/")


class Transform(MDFC):
    """
    Transform card
    """

    path = "TF Front"
    path_back = "TF Back"


class Reversible(MDFC):
    """
    Reversible card, see "Heads I Win, Tails You Lose"
    """

    path = "Reversible Front"
    path_back = "Reversible Back"


"""
SIMPLE ARCHETYPES
"""


class Land(Card):
    """
    Basic land card
    """

    path = "Land"


class Saga(Card):
    """
    Saga card
    """

    path = "Saga"


class Leveler(Card):
    """
    Leveler card
    """

    path = "Leveler"


class Mutate(Card):
    """
    Mutate card
    """

    path = "Mutate"


class Planeswalker(Card):
    """
    Planeswalker card
    """

    path = "Planeswalker"


class Class(Card):
    """
    Class card
    """

    path = "Class"


class Token(Card):
    """
    Token card
    """

    path = "Token"


class Planar(Card):
    """
    Planar card
    """

    path = "Planar"


class Meld(Card):
    """
    Meld card
    Todo: Revisit to treat as Transform.
    """

    path = "Meld"


"""
UTILITY FUNCTIONS
"""


def get_card_class(c: dict):
    """
    Return the card class
    @param c: Card json data.
    @return: The correct card class to use.
    """
    class_map = {
        "normal": Card,
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
        "token": Token,
        "reversible_card": Reversible,
    }

    # Planeswalker, saga, or land? (non mdfc)
    if not isinstance(c, dict):
        print("C VALUE: ", c)
    if "Planeswalker" in c.get("type_line", "") and "card_faces" not in c:
        return Planeswalker
    if "Saga" in c.get("type_line", "") and "card_faces" not in c:
        return Saga
    if "Mutate" in c.get("keywords", ""):
        return Mutate
    if "Land" in c.get("type_line", "") and "card_faces" not in c:
        return Land
    return class_map.get(c.get("layout", "normal"), Card)
