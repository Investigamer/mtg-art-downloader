"""
CORE FUNCTIONS
"""
import json
import os
from typing import Optional, Union

import requests
from difflib import SequenceMatcher
from pathlib import Path
from colorama import Style, Fore
from bs4 import BeautifulSoup
from requests import RequestException
from unidecode import unidecode
from src import settings as cfg
from src.constants import console
from src.fetch import get_cards_paged, get_mtgp_page

cwd = os.getcwd()


"""
PRE-PROCESS DATA
"""


def normalize_card_list(cards: list[Union[str, dict]]) -> list[Union[str, dict]]:
    """
    Normalizes a list of cards, correcting for inconsistencies.
    @param cards: List of card names, with optional tags.
    @return: Normalized list of card names.
    """
    result: list[Union[str, dict]] = []

    # Remove empty lines
    if "" in cards:
        cards.remove("")
    if " " in cards:
        cards.remove(" ")

    # Format each card
    for c in cards:
        # Analyze string card
        if isinstance(c, str):
            # Trim extra spaces and newline
            c = c.strip().replace("\n", "")

            # Remove inappropriate leading number
            terms = c.split(" ")
            if len(terms[0]) < 4 and terms[0].isdigit():
                c = " ".join(terms[1:])
        result.append(c)
    return result


"""
COMMANDS
"""


def get_command(command: str) -> Optional[dict]:
    """
    See if the command is listed in links.json
    @param command: String representing a pre-programmed command from links.json.
    @return: The appropriate link, None if nothing matches
    """
    for k, v in cfg.links.items():
        if command in v:
            return v[command]
    return None


def get_list_from_link(command: dict) -> list[dict]:
    """
    Webscrape to create list of cards to download from a given list.
    @param command: Command array including name, and url
    @return: Filename of the newly created list
    """
    try:
        # Grab the card list from JSON supported API
        cards = requests.get(command["url"]).json()
    except (RequestException, json.JSONDecodeError):
        # Invalid data or bad request
        return []
    # Navigate to list using keys defined by command
    for k in command.get("keys", []):
        cards = cards.get(k, {})
    return cards if isinstance(cards, list) else []


def get_list_from_scryfall(command: str) -> Optional[list]:
    """
    Use Scryfall API compliant query to return a list.
    @param command: Command string containing scryfall arguments.
    @return: Return path to the list file
    """
    query = "https://api.scryfall.com/cards/search"
    commands = [com.strip() for com in command.split(",")]

    # Recognized parameters
    params = {
        "unique": cfg.unique,
        "include_extras": cfg.include_extras,
        "q": " ".join(commands),
    }

    # Query paged results
    return get_cards_paged(query, params=params, keys=["data"])


"""
MTGP Functions
"""


def get_mtgp_code(set_code: str, num: str, name: str) -> Optional[str]:
    """
    Webscrape to find the correct MTG Pics code for the card.
    @param set_code: Set code of this card, ex: MH2
    @param num: Collector number of this card, ex: 220
    @param name: Name of this card, ex: Damnation
    @return: Accurate mtgp linkage for this card.
    """
    try:

        # Crawl the mtgpics site to find correct set code
        r = get_mtgp_page(f"https://www.mtgpics.com/card?ref={set_code}001")
        soup = BeautifulSoup(r, "html.parser")
        soup_td = soup.find("td", {"width": "170", "align": "center"})
        replaced = soup_td.find("a").get("href", "").replace("set?", "set_checklist?")
        mtgp_link = f"https://mtgpics.com/{replaced}"

        # Crawl the set page to find the correct link
        r = get_mtgp_page(mtgp_link)
        soup = BeautifulSoup(r, "html.parser")
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
        pass
    return None


def get_mtgp_code_pmo(
    name: str, artist: str, set_name: str, promo: str = "pmo"
) -> Optional[str]:
    """
    Webscrape to find the correct MTG Pics code for a promo card.
    @param name: Name of the card.
    @param artist: Artist of the card.
    @param set_name: Name of the card set.
    @param promo: Type of promo set.
    @return: Accurate mtgp linkage for this card.
    """
    try:
        # Track matches
        matches = []

        # Which promo set?
        if promo == "dci":
            url = "https://mtgpics.com/set_checklist?set=18"
        elif promo == "a22":
            url = "https://mtgpics.com/set_checklist?set=375"
        elif promo == "uni":
            url = "https://mtgpics.com/set_checklist?set=201"
        else:
            url = "https://mtgpics.com/set_checklist?set=72"

        # Crawl the set page to find the correct link
        r = get_mtgp_page(url)
        soup = BeautifulSoup(r, "html.parser")
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
                        "code": cols[2]
                        .find("a")
                        .get("href", "")
                        .replace("card?ref=", ""),
                        "match": SequenceMatcher(
                            a=cols[2].text.replace(name, ""), b=set_name
                        ).ratio(),
                    }
                )
        return sorted(matches, key=lambda i: i["match"], reverse=True)[0]["code"]
    except (KeyError, TypeError, IndexError, AttributeError):
        pass
    return None


def get_card_face(entries: list[dict], back: bool = False) -> Optional[str]:
    """
    Determine which image URL is most likely correct on MTGP.
    @param entries: Image URLs available for this card on MTGP.
    @param back: True if this is the back face of a card, False if front face.
    @return: Our best guess which image is correct to download, None if zero found.
    """

    # Return none if entry list empty
    if len(entries) == 0:
        return None

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
            # Only one image, assume back is missing
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

    # Finally, couldn't match anything
    return None


"""
LOGGING
"""


def log_mtgp(label: str) -> None:
    """
    Log card that was successfully downloaded from MTGP.
    """
    console.print(f"{Fore.GREEN}MTGP DONE:{Style.RESET_ALL} {label}")


def log_scryfall(label: str) -> None:
    """
    Log card that was successfully downloaded from Scryfall.
    """
    console.print(f"{Fore.YELLOW}SCRYFALL:{Style.RESET_ALL} {label}")


def log_failed(
    label: str,
    print_out: bool = True,
    write_log: bool = True,
    filename: str = "failed",
    action: str = "MTGP",
) -> None:
    """
    Log card that couldn't be found.
    @param label: MTG card name and other details.
    @param print_out: Whether to print the failure.
    @param write_log: Whether to write failure to log file.
    @param filename: Name of the log file.
    @param action: The particular action that failed (MTGP or SCRY)
    """
    if write_log:
        Path(os.path.join(cwd, "logs")).mkdir(mode=511, parents=True, exist_ok=True)
        with open(
            os.path.join(cwd, f"logs/{filename}.txt"), "a", encoding="utf-8"
        ) as f:
            f.write(f"{label}\n")
    if print_out:
        console.print(f"{Fore.RED}{action} FAILED:{Style.RESET_ALL} {label}")
