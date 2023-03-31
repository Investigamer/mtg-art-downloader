"""
BASIC PYTEST MODULE
"""
import os
import sys
from pathlib import Path

# Add cwd to path
sys.path.append(str(Path(os.getcwd())))
os.chdir(str(Path(os.getcwd()).resolve()))
import main as app
import core


def test_normal_cards():
    dl = app.Download(testing=True)
    assert all(
        [result for result, name in dl.download_normal("As Foretold", True)]
    )  # Normal card
    assert all(
        [result for result, name in dl.download_normal("Faithbound Judge", True)]
    )  # TF card
    assert all(
        [result for result, name in dl.download_normal("Darkbore Pathway", True)]
    )  # MDFC card
    assert all(
        [result for result, name in dl.download_normal("Fire // Ice", True)]
    )  # Split card
    assert all(
        [result for result, name in dl.download_normal("Geyadrone Dihada", True)]
    )  # Planeswalker


def test_detailed_cards():
    dl = app.Download(testing=True)
    assert dl.download_detailed("As Foretold (2x2)")[0]  # Normal card
    assert dl.download_detailed("Faithbound Judge (vow)")[0]  # TF card
    assert dl.download_detailed("Darkbore Pathway (khm)")[0]  # MDFC card
    assert dl.download_detailed("Fire // Ice (mh2)")[0]  # Split card
    assert dl.download_detailed("Geyadrone Dihada (mh2)")[0]  # Planeswalker


def test_scryfall_command():
    dl = app.Download("set:2x2, power>=15, color:g", testing=True)
    assert all([result for result, name in dl.start()])


def test_mtgp_image_determination():
    longer_string_test = [
        {"src": "pics/art_th/mh2/030b.jpg"},
        {"src": "pics/art_th/mh2/030.jpg"},
    ]
    bigger_number_test = [
        {"src": "pics/art_th/mh2/051.jpg"},
        {"src": "pics/art_th/mh2/050.jpg"},
    ]
    underscore_letter_test = [
        {"src": "pics/art_th/mh2/030_b.jpg"},
        {"src": "pics/art_th/mh2/030_a.jpg"},
    ]
    underscore_number_test = [
        {"src": "pics/art_th/mh2/030_2.jpg"},
        {"src": "pics/art_th/mh2/030_1.jpg"},
    ]

    longer_string_test = [
        os.path.basename(core.get_card_face(longer_string_test)),
        os.path.basename(core.get_card_face(longer_string_test, True)),
    ]
    underscore_letter_test = [
        os.path.basename(core.get_card_face(underscore_letter_test)),
        os.path.basename(core.get_card_face(underscore_letter_test, True)),
    ]
    underscore_number_test = [
        os.path.basename(core.get_card_face(underscore_number_test)),
        os.path.basename(core.get_card_face(underscore_number_test, True)),
    ]
    bigger_number_test = [
        os.path.basename(core.get_card_face(bigger_number_test)),
        os.path.basename(core.get_card_face(bigger_number_test, True)),
    ]

    assert longer_string_test == ["030.jpg", "030b.jpg"]
    assert bigger_number_test == ["050.jpg", "051.jpg"]
    assert underscore_letter_test == ["030_a.jpg", "030_b.jpg"]
    assert underscore_number_test == ["030_1.jpg", "030_2.jpg"]
