"""
CORE FUNCTIONS
"""
import os
from typing import Optional
from urllib.parse import quote_plus
import requests
from difflib import SequenceMatcher
from pathlib import Path
from colorama import Style, Fore
from bs4 import BeautifulSoup
from unidecode import unidecode
from lib import settings as cfg

cwd = os.getcwd()
# Add necessary directories
Path(cfg.folder).mkdir(mode=511, parents=True, exist_ok=True)
Path(cfg.mtgp).mkdir(mode=511, parents=True, exist_ok=True)
Path(cfg.scry).mkdir(mode=511, parents=True, exist_ok=True)
Path(os.path.join(cwd, "logs")).mkdir(mode=511, parents=True, exist_ok=True)
Path(os.path.join(cwd, "lists")).mkdir(mode=511, parents=True, exist_ok=True)


def get_command(command: str) -> Optional[dict]:
    """
    See if the command is listed in links.json
    :param command: String representing a pre-programmed command from links.json.
    :return: The appropriate link, None if nothing matches
    """
    for k, v in cfg.links.items():
        if command in v:
            return v[command]
    return None


def get_list_from_link(command: dict) -> str:
    """
    Webscrape to create list of cards to download from a given list.
    :param command: Command array including name, and url
    :return: Filename of the newly created list
    """
    cards = requests.get(command["url"]).json()
    with open(
        os.path.join(cwd, f"lists/{command['name']}.txt"), "w", encoding="utf-8"
    ) as f:
        # Get our card list
        for k in command["keys"]:
            cards = cards[k]

        # Clear file then write card list
        f.truncate(0)
        for card in cards:
            f.write(f"{card['name']}\n")
    return os.path.join(cwd, f"lists/{command['name']}.txt")


def get_list_from_scryfall(com: str) -> Optional[list]:
    """
    Use Scryfall API compliant query to return a list.
    :param com: Command string containing scryfall arguments.
    :return: Return path to the list file
    """
    command = {}
    query = "https://api.scryfall.com/cards/search?q="

    # Split command by argument
    com_arr = com.split(",")
    for c in com_arr:
        # Obtain key and value for argument
        arg = c.split(":")

        # Get the correct separator
        ops = ["!", "<", ">"]
        param = "".join(["" if c in ops else c for c in arg[0]])
        if param in cfg.scry_args:
            sep = cfg.scry_args[param]
        else:
            sep = "="

        # Add to commands
        try:
            if arg[0][0] == " ":
                arg[0] = arg[0][1:]
            if arg[1][0] == " ":
                arg[1] = arg[1][1:]
        except (KeyError, TypeError):
            pass
        command.update({arg[0] + sep: arg[1]})
        if "set:" in command and "is:" not in command:
            if get_mtg_set(command["set:"])["set_type"] == "expansion":
                command.update({"is:": "booster"})

    # Add each argument to scryfall search
    for k, v in command.items():
        query += quote_plus(f" {k}{v}")
    query += "&unique=art"

    # Query scryfall
    res = requests.get(query).json()

    # Add additional pages if any exist
    cards = []
    try:
        while True:
            cards.extend(res["data"])
            if res["has_more"]:
                res = requests.get(res["next_page"]).json()
            else:
                break
    except KeyError:
        return None

    # Write the list
    return cards


def get_mtgp_code(set_code: str, num: str, name: str):
    """
    Webscrape to find the correct MTG Pics code for the card.
    :param set_code: Set code of this card, ex: mh2
    :param num: Collector number of this card, ex: 220
    :return: Accurate mtgp linkage for this card
    """
    try:

        # Crawl the mtgpics site to find correct set code
        r = requests.get("https://www.mtgpics.com/card?ref=" + set_code + "001")
        soup = BeautifulSoup(r.content, "html.parser")
        soup_td = soup.find("td", {"width": "170", "align": "center"})
        replaced = soup_td.find("a")["href"].replace("set?", "set_checklist?")
        mtgp_link = f"https://mtgpics.com/{replaced}"

        # Crawl the set page to find the correct link
        r = requests.get(mtgp_link)
        soup = BeautifulSoup(r.content, "html.parser")
        rows = soup.find_all(
            "div",
            {
                "style": "display:block;margin:0px 2px 0px 2px;border-top:1px #cccccc dotted;"
            },
        )

        # Look for collector number and name match
        for row in rows:
            cols = row.find_all("td")
            if cols[0].text == num and name in cols[2].text:
                return cols[2].find("a")["href"].replace("card?ref=", "")

        # Collector number doesn't match, look only for the name
        for row in rows:
            cols = row.find_all("td")
            if name in cols[2].text:
                return cols[2].find("a")["href"].replace("card?ref=", "")

    except (KeyError, TypeError, IndexError, AttributeError):
        return None
    return None


def get_mtgp_code_pmo(name: str, artist: str, set_name: str, promo: str = "pmo"):
    """
    Webscrape to find the correct MTG Pics code for the card.
    """
    try:
        # Track matches
        matches = []

        # Which promo set?
        if promo == "dci":
            req = "https://mtgpics.com/set_checklist?set=18"
        elif promo == "a22":
            req = "https://mtgpics.com/set_checklist?set=375"
        elif promo == "uni":
            req = "https://mtgpics.com/set_checklist?set=201"
        else:
            req = "https://mtgpics.com/set_checklist?set=72"

        # Crawl the set page to find the correct link
        r = requests.get(req)
        soup = BeautifulSoup(r.content, "html.parser")
        rows = soup.find_all(
            "div",
            {
                "style": "display:block;margin:0px 2px 0px 2px;border-top:1px #cccccc dotted;"
            },
        )
        for row in rows:
            cols = row.find_all("td")
            if (
                artist in unidecode(cols[6].text)
                and name.lower() in cols[2].text.lower()
            ):
                matches.append(
                    {
                        "code": cols[2].find("a")["href"].replace("card?ref=", ""),
                        "match": SequenceMatcher(
                            a=cols[2].text.replace(name, ""), b=set_name
                        ).ratio(),
                    }
                )
        return sorted(matches, key=lambda i: i["match"], reverse=True)[0]["code"]
    except (KeyError, TypeError, IndexError, AttributeError):
        return None


def log(name: str, set_code: str, txt: str = "failed"):
    """
    Log card that couldn't be found.
    """
    Path(os.path.join(cwd, "logs")).mkdir(mode=511, parents=True, exist_ok=True)
    with open(os.path.join(cwd, f"logs/{txt}.txt"), "a", encoding="utf-8") as f:
        f.write(f"{set_code}--{name}\n") if set_code else f.write(f"{name}\n")
    print(f"{Fore.RED}FAILED: {Style.RESET_ALL}{name} [{set_code.upper()}]")


def get_card_face(entries: list, back: bool = False):
    """
    Determine which image should be downloaded when multiple are present.
    """

    # Return none if entry list empty
    if len(entries) == 0:
        return

    # Format the image path
    arr = []
    path = f"https://mtgpics.com/{os.path.dirname(entries[0]['src'])}"
    path = path.replace("art_th", "art")

    # Isolate the image code
    for e in entries:
        arr.append(os.path.basename(e["src"]).replace(".jpg", ""))

    # Strategy based on number of entries
    if len(arr) == 1:
        if back:
            return None
        return f"{path}/{arr[0]}.jpg"
    if len(arr) == 2:
        if back:
            return f"{path}/{sorted(arr)[1]}.jpg"
        return f"{path}/{sorted(arr)[0]}.jpg"
    if len(arr) > 2:

        # Separate into string array and int array, sorted
        img_i = []
        img_s = []
        arr.sort()

        for i in arr:
            if len(i) == 3:
                img_i.append(i)
            elif len(i) > 3:
                img_s.append(i)

        # Try comparing ints
        if len(img_i) > 1:
            if back:
                return f"{path}/{img_i[1]}.jpg"
            return f"{path}/{img_i[0]}.jpg"

        # Try comparing strings
        if len(img_s) > 1:
            if back:
                return f"{path}/{img_s[1]}.jpg"
            return f"{path}/{img_s[0]}.jpg"

        # Or just go in order
        if back:
            return f"{path}/{img_i[0]}.jpg"
        return f"{path}/{img_s[0]}.jpg"


"""
SCRYFALL FUNCTIONS
"""


def get_mtg_set(code):
    """
    Return json data for MTG Set.
    :param code: Set code
    :return: Dict of set data
    """
    try:
        return requests.get(f"https://api.scryfall.com/sets/{code}").json()
    except requests.exceptions.BaseHTTPError:
        return None
