# MTG Art Downloader
Mass download MTG card arts using MTGPics with Scryfall as a backup source, downloaded images are named according to their card name with the artist in parenthesis, set code in brackets. Arts from mtgpics are put in one folder, scryfall art crops in another folder. If any cards couldn't be found from either source a "failed.txt" is populated with names of the missing cards so you can manually look for them.

<p align="center">
  <a href="https://discord.gg/3kXw2qQwRH">
    <img alt="Discord" src="https://img.shields.io/discord/889831317066358815?label=Discord&style=plastic">
  </a>
  <img alt="GitHub" src="https://img.shields.io/github/license/MrTeferi/MTG-Art-Downloader?color=1082C2&style=plastic">
  <a href="https://github.com/MrTeferi/MTG-Art-Downloader/releases">
    <img alt="GitHub all releases" src="https://img.shields.io/github/downloads/MrTeferi/MTG-Art-Downloader/total?style=plastic">
  </a>
  <img alt="Python" src="https://img.shields.io/badge/python-3.5%2B-yellow?style=plastic">
</p>

# Setup - Executable Release
- Download the latest release
- Make a copy of this google sheet document on your account: https://docs.google.com/spreadsheets/d/1QnVoQ1gvz1N4TKnkJJ44_FHomy0gNoxZlaPSkua4Rmk (optional)

# Setup - Python Version
- Python 3
- pip install -r requirements.txt (python dependencies)
- Make a copy of this google sheet document on your account: https://docs.google.com/spreadsheets/d/1Gss4pwJZL_WzjNVFx6uDAviu1gpJdfN1fQUHbwNJl2o (optional)
- "python app.py" to run

# How to use with a Decklist
- Paste a decklist into the cards.txt file in the working directory of MTG Art Downloader
- Runt he downloader

# How to use with Google Sheet Script
- Open up your copy of the "MTG Art Downloader Script" google sheet
- In the FX for box A2 you can customize arguments for what cards you want to pull using the first variable, for example choose a given set, a given rarity (or range of rarities). Don't change the second variable, those are the columns that are generated. You can read more about arguments for this scryfall script here: https://github.com/scryfall/google-sheets
- Once your comfortable with the scryfall arguments, press enter and watch it populate. Copy the right most column.
- Paste those rows into the cards.txt file in the working directory, hit save.
- Run the downloader

# Config.ini
- You can choose whether to download all available arts or only one art
- You can choose whether to ignore fullarts (supported only when download all is enabled)
- You can choose whether to download scryfall arts as a fallback
