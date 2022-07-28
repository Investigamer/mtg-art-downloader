"""
BASIC PYTEST MODULE
"""
import os
import sys
from pathlib import Path
sys.path.append(str(Path(os.getcwd())))
import main as app


def test_normal_cards():
    dl = app.Download()
    assert all(dl.download_normal("As Foretold"))  # Normal card
    assert all(dl.download_normal("Faithbound Judge", True))  # TF card
    assert all(dl.download_normal("Darkbore Pathway", True))  # MDFC card
    assert all(dl.download_normal("Fire // Ice", True))  # Split card
    assert all(dl.download_normal("Geyadrone Dihada", True))  # Planeswalker


def test_detailed_cards():
    dl = app.Download()
    assert dl.download_detailed("2x2--As Foretold")  # Normal card
    assert dl.download_detailed("vow--Faithbound Judge")  # TF card
    assert dl.download_detailed("khm--Darkbore Pathway")  # MDFC card
    assert dl.download_detailed("mh2--Fire // Ice")  # Split card
    assert dl.download_detailed("mh2--Geyadrone Dihada")  # Planeswalker


def test_scryfall_command():
    dl = app.Download("set:mh2, power>:15, color:C")
    dl.start(dry_run=True)
    assert len(dl.fails) == 0
