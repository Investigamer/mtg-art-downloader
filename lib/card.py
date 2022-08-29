"""
CARD CLASSES
"""
import os
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


# SINGLE IMAGE CARDS
class Card:
    """
    Base class to extend all cards to.
    """

    path = ""
    path_back = ""

    def __init__(self, c: dict) -> None:
        # Inherited card info
        self.set = c["set"]
        self.artist = unidecode(c["artist"])
        self.num = c["collector_number"]
        self.set_name = c["set_name"]
        self.set_type = c["set_type"]

        # Scrylink
        if not hasattr(self, "scrylink"):
            self.scrylink = c["image_uris"]["art_crop"]

        # Fix mtgp setcode
        if self.set in cfg.replace_sets:
            self.mtgp_set = cfg.replace_sets[self.set]
        else:
            self.mtgp_set = self.set

        # Name if not defined
        if not hasattr(self, "name"):
            self.name = c["name"]

        # Possible promo card?
        self.promo = self.check_for_promo()

        # Get the MTGP code
        self.code = self.get_mtgp_code(self.name)

        # Make folders, setup path
        if self.path:
            self.make_folders()
        self.make_path()

    def get_mtgp_code(self, name: str) -> str:
        """
        Get the correct mtgp URL code
        """
        # Possible promo set
        if self.promo or self.mtgp_set == "pmo":
            code = core.get_mtgp_code_pmo(
                name, self.artist, self.set_name, self.mtgp_set
            )
            if code:
                return code

        # Try looking for the card under its collector number
        code = core.get_mtgp_code(self.mtgp_set, self.num, name)
        if code:
            return code
        else:
            return self.set + self.num

    def download(self, log_failed: bool = True) -> bool:
        """
        Download just one version of this card.
        """
        # Download only scryfall?
        if cfg.only_scryfall:
            if not self.download_scryfall(self.name, self.filename, self.scrylink):
                return False

        # Try downloading MTGP
        if not self.download_mtgp(self.name, self.filename, self.code):
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

    def make_folders(self):
        """
        Check that the folders exist
        """
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

    def make_path(self):
        """
        Define save paths for this card
        """
        # Front image path
        front_name = self.naming_convention(self.name, self.artist, self.set.upper())
        self.filename = f"{self.path}{front_name}.jpg"

        # Setup back path if exists
        if self.path_back != "":
            back_name = self.naming_convention(
                self.name_back, self.artist, self.set.upper()
            )
            self.filename_back = f"{self.path_back}{back_name}.jpg"

    @staticmethod
    def check_path(path):
        """
        Check if path needs to be numbered to prevent overwrite.
        """
        # Front face
        if Path(path).is_file():
            i = 1
            path = path.replace(".jpg", f" ({str(i)}).jpg")
            while True:
                i += 1
                if Path(path).is_file():
                    path = path.replace(f"({str(i-1)})", f"({str(i)})")
                else:
                    break
        return path

    def check_for_promo(self):
        """
        Check if this is a promo card
        """
        set_types = ["funny", "promo"]
        if self.mtgp_set == "pre":
            return True
        if "Alchemy" in self.set_name:
            self.mtgp_set = "a22"
            return True
        if "Judge Gift" in self.set_name or self.mtgp_set == "dci":
            self.mtgp_set = "dci"
            return True
        if self.set_name in ("Legacy Championship", "Vintage Championship"):
            self.mtgp_set = "uni"
            return True
        if self.set_type in set_types:
            self.mtgp_set = "pmo"
            return True
        return False

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


class Adventure(Card):
    """
    Adventure card
    """

    path = "Adventure/"

    def __init__(self, c):
        self.savename = c["card_faces"][0]["name"]
        super().__init__(c)

    def get_mtgp_code(self, name: str):
        """
        Override this method because flip names are displayed differently.
        :param name: Card name to reformat
        :return: The MTGP code linkage
        """
        name = self.name.replace("//", "/")
        return super().get_mtgp_code(name)

    def make_path(self):
        """
        Override this method because // isn't valid in filenames
        """
        front_name = self.naming_convention(
            self.savename, self.artist, self.set.upper()
        )
        self.filename = f"{self.path}{front_name}.jpg"


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


class Flip(Card):
    """
    Flip card
    """

    path = "Flip/"

    def __init__(self, c):
        self.savename = c["card_faces"][0]["name"]
        super().__init__(c)

    def get_mtgp_code(self, name: str):
        """
        Override this method because flip names are displayed differently.
        :param name: Card name to reformat
        :return: The MTGP code linkage
        """
        name = self.name.replace("//", "/")
        return super().get_mtgp_code(name)

    def make_path(self):
        """
        Override this method because // isn't valid in filenames
        """
        front_name = self.naming_convention(
            self.savename, self.artist, self.set.upper()
        )
        self.filename = f"{self.path}{front_name}.jpg"


class Planar(Card):
    """
    Planar card
    """

    path = "Planar/"


# MULTIPLE IMAGE CARDS
class MDFC(Card):
    """
    Double faced card
    """

    path = "MDFC Front/"
    path_back = "MDFC Back/"

    def __init__(self, c):

        # Face variables
        self.name = c["card_faces"][0]["name"]
        self.name_back = c["card_faces"][1]["name"]
        if not hasattr(self, "scrylink"):
            self.scrylink = c["card_faces"][0]["image_uris"]["art_crop"]
            self.scrylink_back = c["card_faces"][1]["image_uris"]["art_crop"]
        super().__init__(c)

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
                f"{self.name_back} (Back)", self.filename_back, self.code, True
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


class Transform(MDFC):
    """
    Transform card
    """

    path = "TF Front/"
    path_back = "TF Back/"


class Split(MDFC):
    """
    Split card
    """

    path = "Split/"
    path_back = "Split/"

    def __init__(self, c: dict):
        self.fullname = c["name"]
        self.scrylink = c["image_uris"]["art_crop"]
        super().__init__(c)

    def get_mtgp_code(self, name: str):
        """
        Override this method because split names are displayed differently.
        :param name: Card name to reformat
        :return: The MTGP code linkage
        """
        name = self.fullname.replace("//", "/")
        return super().get_mtgp_code(name)


class Meld(Card):
    """
    Meld card
    TODO: Revisit
    """

    path = "Meld/"


class Token(Card):
    """
    Token card
    """

    path = "Token/"


class Reversible(MDFC):
    """
    Reversible card, see "Heads I Win, Tails You Lose"
    """

    path = "Reversible/"


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
