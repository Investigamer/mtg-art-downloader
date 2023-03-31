"""
SCRIPT TO BUILD PROXYSHOP AS EXE RELEASE
"""
import os
import sys
import zipfile
from glob import glob
from pathlib import Path
from shutil import copy2, rmtree, move
import PyInstaller.__main__

# Folder definitions
CWD = os.getcwd()
DIST = os.path.join(CWD, "dist")
SRC = os.path.join(os.getcwd(), "src")
DIST_SRC = os.path.join(os.getcwd(), "dist/src")

# All individual files that need to be copied upon pyinstaller completion
files = [
    # --- WORKING DIRECTORY
    {"src": os.path.join(CWD, "LICENSE"), "dst": os.path.join(DIST, "LICENSE")},
    {"src": os.path.join(CWD, "README.md"), "dst": os.path.join(DIST, "README.md")},
    {"src": os.path.join(CWD, "cards.txt"), "dst": os.path.join(DIST, "cards.txt")},
    {"src": os.path.join(CWD, "config.ini"), "dst": os.path.join(DIST, "config.ini")},
    # --- SOURCE DIRECTORY
    {
        "src": os.path.join(SRC, "codes.hjson"),
        "dst": os.path.join(DIST_SRC, "codes.hjson"),
    },
    {
        "src": os.path.join(SRC, "links.json"),
        "dst": os.path.join(DIST_SRC, "links.json"),
    },
]


def clear_build_files(clear_dist: bool = True):
    """
    Clean out all PYCACHE files and Pyinstaller files
    """
    os.system("pyclean -v .")
    os.system("pyclean -v .venv")
    try:
        rmtree(os.path.join(os.getcwd(), "build"))
    except Exception as e:
        print(e)
    if clear_dist:
        try:
            rmtree(os.path.join(os.getcwd(), "dist"))
        except Exception as e:
            print(e)


def make_dirs():
    """
    Make sure necessary directories exist.
    """
    # Ensure folders exist
    Path(DIST).mkdir(mode=511, parents=True, exist_ok=True)
    Path(DIST_SRC).mkdir(mode=511, parents=True, exist_ok=True)


def move_data():
    """
    Move our data files into the release.
    """
    # Transfer our necessary files
    print("Transferring data files...")
    for f in files:
        copy2(f["src"], f["dst"])


def build_zip(version: str):
    """
    Create a zip of this release.
    """
    print("Building ZIP...")
    ZIP = os.path.join(CWD, "mtg-art-downloader.{}.zip".format(version))
    ZIP_DIST = os.path.join(DIST, "mtg-art-downloader.{}.zip".format(version))
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as zipf:
        for fp in glob(os.path.join(DIST, "**/*"), recursive=True):
            base = os.path.commonpath([DIST, fp])
            zipf.write(fp, arcname=fp.replace(base, ""))
    move(ZIP, ZIP_DIST)


if __name__ == "__main__":

    # Pre-build steps
    clear_build_files()
    make_dirs()

    # Run pyinstaller
    print("Starting PyInstaller...")
    PyInstaller.__main__.run(["main.spec", "--clean"])

    # Post-build steps
    move_data()

    # Produce a zip if argument is provided
    if len(sys.argv) > 1:
        build_zip(sys.argv[1])

    # Clear build files
    clear_build_files(False)
