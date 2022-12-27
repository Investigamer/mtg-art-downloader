"""
CARD CLASSES
"""
import os
from functools import cached_property
from urllib.error import HTTPError, ContentTooShortError
from pathvalidate import sanitize_filename
import requests
from pathlib import Path
from urllib import request
from bs4 import BeautifulSoup
from colorama import Style, Fore
from unidecode import unidecode
from lib import settings as cfg
from lib.constants import console
from lib import core

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
        if self.path_back != "":
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
        return self.c["set"]

    @property
    def name(self) -> str:
        return self.c["name"]

    @property
    def artist(self) -> str:
        return unidecode(self.c["artist"])

    @property
    def number(self) -> str:
        return self.c["collector_number"]

    @property
    def set_name(self) -> str:
        return self.c["set_name"]

    @property
    def set_type(self) -> str:
        return self.c["set_type"]

    @property
    def scrylink(self) -> str:
        return self.c["image_uris"]["art_crop"]

    @property
    def promo(self) -> bool:
        return self._promo

    @promo.setter
    def promo(self, value):
        self._promo = value

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
    def filename(self) -> str:
        # Filename to save front face image
        front_name = self.naming_convention(self.name, self.artist, self.set.upper())
        return f"{self.path}{front_name}.jpg"

    @cached_property
    def filename_back(self) -> str:
        # Filename to save back face image
        if self.path_back != "":
            back_name = self.naming_convention(
                self.name_back, self.artist, self.set.upper()
            )
            return f"{self.path_back}{back_name}.jpg"

    """
    METHODS
    """

    def download(self, log_failed: bool = True) -> bool:
        """
        Download just one version of this card.
        """
        # Download only scryfall?
        if cfg.only_scryfall:
            if not self.download_scryfall(self.name, self.filename, self.scrylink):
                return False
            return True

        # Try downloading MTGP
        if not self.download_mtgp(self.name, self.filename, self.mtgp_code):
            if cfg.download_scryfall:
                self.download_scryfall(self.name, self.filename, self.scrylink)
            if log_failed:
                core.log(self.name, self.set)
            return False
        return True

    def download_mtgp(self, name: str, path: str, mtgp_code: str, back: bool = False):
        """
        Download image from MTG Pics
        :param name: Name of card to use for console output
        :param path: Image save path
        :param mtgp_code: MTGP linkage
        :param back: Is this the back side?
        :return:
        """
        img_link = ""
        path = f"{cfg.mtgp}/{path}"
        try:
            # Crawl the mtgpics site to find correct link
            r = requests.get("https://www.mtgpics.com/card?ref=" + mtgp_code)
            soup = BeautifulSoup(r.content, "html.parser")
            soup_img = soup.find_all(
                "img", {"style": "display:block;border:4px black solid;cursor:pointer;"}
            )

            # Is this the back face?
            img_link = core.get_card_face(soup_img, back)

            # Check path for overwrites
            if not cfg.overwrite:
                path = self.check_path(path)

            # Try to download from MTG Pics
            request.urlretrieve(img_link, path)
            console.out.append(
                f"{Fore.GREEN}MTGP:{Style.RESET_ALL} {name} [{self.set.upper()}]"
            )
        except ContentTooShortError:
            # Retry download
            try:
                request.urlretrieve(img_link, path)
                console.out.append(
                    f"{Fore.GREEN}MTGP:{Style.RESET_ALL} {name} [{self.set.upper()}]"
                )
            except (TypeError, AttributeError, HTTPError, ContentTooShortError):
                return False
        except (TypeError, AttributeError, HTTPError):
            return False
        return True

    def download_scryfall(self, name: str, path: str, scrylink: str):
        """
        Download scryfall art crop
        :param name: Name of card to use in console output
        :param path: Image save path
        :param scrylink: Art crop scryfall URI
        :return:
        """
        try:
            request.urlretrieve(scrylink, f"{cfg.scry}/{path}")
            console.out.append(
                f"{Fore.YELLOW}SCRYFALL:{Style.RESET_ALL} {name} [{self.set.upper()}]"
            )
            return True
        except (TypeError, AttributeError, HTTPError):
            return False

    """
    STATIC METHODS
    """

    @staticmethod
    def check_path(path):
        """
        Check if path needs to be numbered to prevent overwrite.
        """
        # Front face
        i = 0
        current_path = path
        while Path(current_path).is_file():
            i += 1
            current_path = path.replace(".jpg", f" ({str(i)}).jpg")
        return current_path

    @staticmethod
    def naming_convention(name: str, artist: str, setcode: str):
        """
        Generates filename using config naming convention.
        :param name: Name of card
        :param artist: Card artist
        :param setcode: Set card was printed in
        :return: Correct filename
        """
        result = cfg.naming.replace("NAME", name)
        result = result.replace("ARTIST", artist).replace("SET", setcode)
        result = sanitize_filename(result)
        return result


"""
CARDS WITH TWO NAMES, ONE FACE
"""


class Adventure(Card):
    """
    Adventure card
    """

    path = "Adventure/"

    @property
    def savename(self) -> str:
        return self.c["card_faces"][0]["name"]

    @cached_property
    def filename(self):
        """
        Override this method because // isn't valid in filenames
        """
        front_name = self.naming_convention(
            self.savename, self.artist, self.set.upper()
        )
        return f"{self.path}{front_name}.jpg"

    @property
    def mtgp_name(self) -> str:
        return self.name.replace("//", "/")


class Flip(Card):
    """
    Flip card
    """

    path = "Flip/"

    @property
    def savename(self) -> str:
        return self.c["card_faces"][0]["name"]

    @cached_property
    def filename(self) -> str:
        """
        Override this because // isn't valid in filenames
        """
        front_name = self.naming_convention(
            self.savename, self.artist, self.set.upper()
        )
        return f"{self.path}{front_name}.jpg"

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

    path = "MDFC Front/"
    path_back = "MDFC Back/"

    @property
    def name(self) -> str:
        return self.c["card_faces"][0]["name"]

    @property
    def name_back(self) -> str:
        return self.c["card_faces"][1]["name"]

    @property
    def scrylink(self) -> str:
        return self.c["card_faces"][0]["image_uris"]["art_crop"]

    @property
    def scrylink_back(self) -> str:
        return self.c["card_faces"][1]["image_uris"]["art_crop"]

    def download(self, log_failed: bool = True):
        """
        Download each card side.
        :param log_failed: Whether to log failed download attempts.
        :return:
        """
        # Call super to download the front
        front = super().download()
        back = False

        # Download the back.
        if cfg.only_scryfall:
            if self.download_scryfall(
                self.name_back, self.filename_back, self.scrylink_back
            ):
                back = True
        else:
            if not self.download_mtgp(
                f"{self.name_back} (Back)", self.filename_back, self.mtgp_code, True
            ):
                if cfg.download_scryfall:
                    self.download_scryfall(
                        self.name_back, self.filename_back, self.scrylink_back
                    )
            else:
                back = True

        # Log any failures
        if log_failed:
            if not front and not back:
                core.log(self.name, self.set)
                return False
            elif not front:
                core.log(self.name, self.set, "failed_front")
            elif not back:
                core.log(self.name_back, self.set, "failed_back")
        return True


class Split(MDFC):
    """
    Split card
    """

    path = "Split/"
    path_back = "Split/"

    @property
    def scrylink(self) -> str:
        return self.c["image_uris"]["art_crop"]

    @property
    def mtgp_name(self) -> str:
        return self.name.replace("//", "/")


class Transform(MDFC):
    """
    Transform card
    """

    path = "TF Front/"
    path_back = "TF Back/"


class Reversible(MDFC):
    """
    Reversible card, see "Heads I Win, Tails You Lose"
    """

    path = "Reversible/"


"""
SIMPLE ARCHETYPES
"""


class Land(Card):
    """
    Basic land card
    """

    path = "Land/"


class Saga(Card):
    """
    Saga card
    """

    path = "Saga/"


class Leveler(Card):
    """
    Leveler card
    """

    path = "Leveler/"


class Mutate(Card):
    """
    Mutate card
    """

    path = "Mutate/"


class Planeswalker(Card):
    """
    Planeswalker card
    """

    path = "Planeswalker/"


class Class(Card):
    """
    Class card
    """

    path = "Class/"


class Token(Card):
    """
    Token card
    """

    path = "Token/"


class Planar(Card):
    """
    Planar card
    """

    path = "Planar/"


class Meld(Card):
    """
    Meld card
    TODO: Revisit
    """

    path = "Meld/"


"""
UTILITY FUNCTIONS
"""


def get_card_class(c: dict):
    """
    Return the card class
    :param c: Card json data.
    :return: The correct card class to use.
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
    if "type_line" in c and "Planeswalker" in c["type_line"] and "card_faces" not in c:
        return Planeswalker
    if "type_line" in c and "Saga" in c["type_line"] and "card_faces" not in c:
        return Saga
    if "keywords" in c and "Mutate" in c["keywords"]:
        return Mutate
    if "type_line" in c and "Land" in c["type_line"] and "card_faces" not in c:
        return Land
    return class_map[c["layout"]]
