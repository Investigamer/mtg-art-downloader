# MTG Art Downloader
Mass download MTG card arts using MTGPics with Scryfall as a backup source, downloaded images are named according to their card name with the artist in parenthesis, set code in brackets. Arts from mtgpics are put in one folder, scryfall art crops in another folder. If any cards couldn't be found from either source a "failed.txt" is populated with names of the missing cards so you can manually look for them. For additional help using this app, join our discord server (click the discord button below), we have a #downloader channel and can help with any questions.

<p align="center">
  <a href="http://mprox.link/discord">
    <img alt="Discord" src="https://img.shields.io/discord/889831317066358815?label=Discord&style=plastic">
  </a>
  <img alt="Maintenance" src="https://img.shields.io/badge/Maintained%3F-yes-brightgreen?style=plastic">
  <img alt="Passing" src="https://img.shields.io/github/actions/workflow/status/MrTeferi/MTG-Art-Downloader/py-test.yml?style=plastic">
  <img alt="GitHub" src="https://img.shields.io/github/license/MrTeferi/MTG-Art-Downloader?color=1082C2&style=plastic">
  <a href="https://github.com/MrTeferi/MTG-Art-Downloader/releases">
    <img alt="GitHub all releases" src="https://img.shields.io/github/downloads/MrTeferi/MTG-Art-Downloader/total?style=plastic">
  </a>
  <img alt="Python" src="https://img.shields.io/badge/python-3.6%2B-yellow?style=plastic">
</p>

# Setup - Executable Release
- Download the latest release
- **Option 1**: Paste a list of cards into the cards.txt file. For best results, I recommend exporting a list from your favorite deck editor (I use Moxfield)
using the mode that displays each card like so: `Damnation (TSR) 106`. It's okay if this is preceded by a number value, MTG Art Downloader will correct
for this. Start the app and hit Enter. The app will begin downloading art images for these cards!
- **Option 2**: Alternatively you can use Scryfall notation if you're looking for something specific, like all Legendary creatures within Modern Horizons 2, or
even every card in Modern Horizons 2! Scroll down to the section on Scryfall commands.

# Setup - Python Version
We now use [poetry](https://python-poetry.org/docs/) for dependency management:
- Have or Install Python 3.8+
- Have or Install poetry, you can use one of the following commands or [check out this install guide](https://python-poetry.org/docs/):
```shell
# WINDOWS (Powershell/Terminal)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# WINDOWS (if you have Scoop)
scoop install poetry

# LINUX/MACOS (Or Windows if you have WSL)
curl -sSL https://install.python-poetry.org | python3 -
```
- Download or clone this repository somewhere on your machine:
```shell
git clone https://github.com/MrTeferi/MTG-Art-Downloader
```
- Next open a powershell/terminal in the MTG Art Downloader folder, enter `poetry install` to install our dependencies.
- You can run MTG Art Downloader with one of the following commands:
```shell
# Run with poetry
poetry run python main.py

# Enter poetry environment, then run with Python
poetry shell
py main.py
```
- Alternatively you can get PyCharm which has native support for Poetry and can automatically start the app for you!

# How to use with a Decklist
- Paste a decklist into the cards.txt file in the working directory of MTG Art Downloader
- Run the downloader, hit Enter. You're good to go!
- Remember that you will get best results with clearly defined cards: `Card Name (SET) Number`
- I recommend avoiding random promo sets, and definitely avoid the Pre-release/Promo versions of existing sets. For example if looking for Midnight Hunt
cards make sure to use MID and not PMID!

# How to use with Scryfall commands?
- After running the app, you can enter commands like so:
`set:mh2, power>:3, type:creature`
- This example will download images for all MH2 creatures with power greater than or equal to 3. Separate arguments with a comma, separate the key and value of the argument with a colon. Refer to the scryfall API documentation for more use cases.

# How to use with Google Sheet Script
- "Make a copy" of this [Google Sheet](https://docs.google.com/spreadsheets/d/1QnVoQ1gvz1N4TKnkJJ44_FHomy0gNoxZlaPSkua4Rmk), this can use Scryfall to create a specialized list of cards based on parameters.
- Open up your copy of the "MTG Art Downloader Script" google sheet.
- In the FX for box A2 you can customize arguments for what cards you want to pull using the first string parameter, for example choose a given set, a given rarity (or range of rarities). Don't change the other parameters, those govern the columns that are generated.
- You can read more about arguments for this scryfall script here: https://github.com/scryfall/google-sheets
- Once your comfortable with the scryfall arguments, press enter and watch it populate. Copy the right most column.
- Paste those rows into the cards.txt file in the working directory, hit save.
- Run the downloader

# Config.ini
- You can choose the download folder and cards.txt naming conventions.
- You can choose whether to download all available arts or only one art.
- You can choose whether to only download unique art or all art even when duplicats are present.
- You can choose whether to ignore fullarts (supported only when download all is enabled)
- You can choose whether to download scryfall arts as a fallback
- You can choose whether to download ONLY scryfall arts.
- You can choose whether to include extras in the search, this includes un-sets and special championship cards.
- You can increase or decrease threads added per second depending on the speed of your internet.
- You can choose the naming convention for saving the downloaded images.

# Contributing
If you wish to contribute to this project:
- Before doing a PR always make sure to run `pre-commit run` to ensure your code is standardized
- Only commit with commitizen, add your changed files with `git add .` then `cz commit` and follow the prompts
- You can test the app for consistency with:
```shell
pytest src/tests.py
```
- You can run a mypy typechecking test with:
```shell
mypy main.py build.py src
```

[1]: https://python-poetry.org/docs/basic-usage/
