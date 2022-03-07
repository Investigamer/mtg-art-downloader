# MTG Art Downloader
This tool is intended to mass download arts for MTG Cards using MTGPics with Scryfall as a backup source, images are automaticalled named according to their card name with the artist in parenthesis, set code in brackets. Arts from mtgpics are put in one folder, scryfall art crops in another folder. If any cards couldn't be found from either source a "failed.txt" is populated with names of the missing cards so you can manually look for them.

<img alt="Discord" src="https://img.shields.io/discord/889831317066358815?label=discord&style=plastic">

# Setup - Executable Release
- Download the latest release
- Make a copy of this google sheet document on your account: https://docs.google.com/spreadsheets/d/1QnVoQ1gvz1N4TKnkJJ44_FHomy0gNoxZlaPSkua4Rmk (optional)

# Setup - Python Version
- Python 3
- pip install -r requirements.txt (python dependencies)
- Make a copy of this google sheet document on your account: https://docs.google.com/spreadsheets/d/1Gss4pwJZL_WzjNVFx6uDAviu1gpJdfN1fQUHbwNJl2o (optional)
- "python find.py" to run

# How to use with a Decklist
- Paste a decklist into the cards.txt file in the working directory of MTG Art Downloader
- Run the downloader, choose option 1

# How to use with Google Sheet Script
- Open up your copy of the "MTG Art Downloader Script" google sheet
- In the FX for box A2 you can customize arguments for what cards you want to pull using the first variable, for example choose a given set, a given rarity (or range of rarities). Don't change the second variable, those are the columns that are generated. You can read more about arguments for this scryfall script here: https://github.com/scryfall/google-sheets
- Once your comfortable with the scryfall arguments, press enter and watch it populate. Copy the right most column.
- Paste those rows into the "detailed.txt" file in the MTG Art Downloader directory, hit save.
- Run the downloader, choose option 2. 

# Config.ini
- You can rename the download folders
- You can choose whether to download all available arts or only one art
- You can choose whether to ignore fullarts (supported only when download all is enabled)
- You can choose whether to download scryfall arts as a fallback
